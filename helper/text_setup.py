import os
import types
import shutil
import sys

from nlp_pipeline.nlp_pipeline import nlp_processor
import pandas as pd
from zipfile import ZipFile
import streamlit as st
from streamlit_server_state import server_state

from helper.user_management import update_server_state
from helper.progress_bar import Logger


def process_corpus(user_name, corpus_name, uploaded_document):
    "process an uploaded corpus"
    temp_directory = f"corpora/tmp_helper_{user_name}/"

    # make temporary directory to handle files
    if not os.path.exists(f"{temp_directory}"):
        os.makedirs(f"{temp_directory}")

    try:
        # copy the file
        with open(
            f"{temp_directory}tmp.{uploaded_document.name.split('.')[-1]}", "wb"
        ) as new_file:
            new_file.write(uploaded_document.getbuffer())
            new_file.close()

        # only uploaded a metadata CSV
        if uploaded_document.name == "metadata.csv":
            metadata = pd.read_csv(f"{temp_directory}tmp.csv")
            if "text_id" not in list(metadata.columns):
                metadata["text_id"] = list(range(1, len(metadata) + 1))
            metadata_addt_column_names = list(
                metadata.columns[
                    ~metadata.columns.isin(
                        [
                            "text_id",
                            "web_filepath",
                            "local_raw_filepath",
                            "local_txt_filepath",
                            "detected_language",
                        ]
                    )
                ]
            )

            # write metadata out
            processor = nlp_processor(
                data_path=temp_directory,
                metadata_addt_column_names=metadata_addt_column_names,
                windows_tesseract_path=None,
                windows_poppler_path=None,
            )

            # sync the object's metadata to the local file
            for col in metadata.columns:
                processor.metadata[col] = metadata[col]

            # download the files
            processor.download_text_id(list(processor.metadata.text_id.values))

            # select out PDF pages if available
            if "page_numbers" in processor.metadata.columns:
                try:
                    processor.filter_pdf_pages(page_num_column="page_numbers")
                except:
                    pass

            # convert the files to text
            processor.convert_to_text(list(processor.metadata.text_id.values))

            # sync to the local metadata file
            processor.sync_local_metadata()

        # uploaded a single .docx, .pdf, or .txt
        elif uploaded_document.name.split(".")[-1] in [
            "csv",
            "pdf",
            "docx",
            "doc",
            "txt",
        ]:
            # write metadata out
            processor = nlp_processor(
                data_path=temp_directory,
                metadata_addt_column_names=[],
                windows_tesseract_path=None,
                windows_poppler_path=None,
            )

            # create metadata
            metadata = pd.DataFrame(
                {
                    "text_id": 1,
                    "local_raw_filepath": f"{temp_directory}tmp.{uploaded_document.name.split('.')[-1]}",
                },
                index=[0],
            )

            # sync the object's metadata to the local file
            for col in metadata.columns:
                processor.metadata[col] = metadata[col]

            # convert the files to text
            processor.convert_to_text(list(processor.metadata.text_id.values))

            # handle a CSV
            if "csv" in f"{temp_directory}tmp.{uploaded_document.name.split('.')[-1]}":
                old_name = f"{temp_directory}txt_files/1.txt"
                os.remove(old_name)
                new_name = f"{temp_directory}txt_files/1.csv"
                shutil.copyfile(
                    f"{temp_directory}tmp.{uploaded_document.name.split('.')[-1]}",
                    new_name,
                )
                # update the metadata
                processor.metadata.loc[0, "local_txt_filepath"] = new_name

        # uploaded a zip
        else:
            with ZipFile(f"{temp_directory}tmp.zip", "r") as zObject:
                zObject.extractall(path=temp_directory)

            # sync the object's metadata to the local file
            provided_metadata = os.path.exists(f"{temp_directory}metadata.csv")

            if provided_metadata:
                metadata = pd.read_csv(f"{temp_directory}metadata.csv")
                metadata_addt_column_names = list(
                    metadata.columns[
                        ~metadata.columns.isin(
                            [
                                "text_id",
                                "web_filepath",
                                "local_raw_filepath",
                                "local_txt_filepath",
                                "detected_language",
                            ]
                        )
                    ]
                )
                if "text_id" not in list(metadata.columns):
                    metadata["text_id"] = list(range(1, len(metadata) + 1))
            else:
                file_list = [
                    x
                    for x in os.listdir(f"{temp_directory}corpus/")
                    if x.split(".")[-1] in ["csv", "txt", "docx", "doc", "pdf"]
                ]

                metadata = pd.DataFrame(
                    {
                        "text_id": list(range(1, len(file_list) + 1)),
                        "filename": file_list,
                    }
                )
                metadata_addt_column_names = []

            processor = nlp_processor(
                data_path=temp_directory,
                metadata_addt_column_names=metadata_addt_column_names,
                windows_tesseract_path=None,
                windows_poppler_path=None,
            )

            for col in metadata.columns:
                processor.metadata[col] = metadata[col]

            # put the files in the right place and update the metadata
            shutil.rmtree(f"{temp_directory}raw_files/")
            shutil.copytree(f"{temp_directory}corpus/", f"{temp_directory}raw_files/")

            for file in os.listdir(f"{temp_directory}raw_files/"):
                processor.metadata.loc[
                    lambda x: x.filename == file, "local_raw_filepath"
                ] = os.path.abspath(f"{temp_directory}raw_files/{file}")

            # select out PDF pages if available
            if "page_numbers" in processor.metadata.columns:
                try:
                    processor.filter_pdf_pages(page_num_column="page_numbers")
                except:
                    pass

            # convert the files to text
            processor.convert_to_text(list(processor.metadata.text_id.values))

            # handle a CSV
            for file in os.listdir(f"{temp_directory}raw_files/"):
                if "csv" in file:
                    text_id = processor.metadata.loc[
                        lambda x: x.filename == file, "text_id"
                    ].values[0]
                    old_name = f"{temp_directory}txt_files/{text_id}.txt"
                    os.remove(old_name)
                    new_name = f"{temp_directory}txt_files/{text_id}.csv"
                    shutil.copyfile(f"{temp_directory}raw_files/{file}", new_name)
                    # update the metadata
                    processor.metadata.loc[
                        lambda x: x.filename == file, "local_txt_filepath"
                    ] = new_name

        ### upload type independent actions

        # move the .txt files to the appropriate place for RAG
        if os.path.exists(f"corpora/{corpus_name}/"):
            shutil.rmtree(f"corpora/{corpus_name}/")
        shutil.copytree(f"{temp_directory}txt_files/", f"corpora/{corpus_name}/")

        # adding file-path for application
        processor.metadata["file_path"] = [
            os.path.abspath(f"corpora/{corpus_name}/{x.split('/')[-1]}")
            for x in processor.metadata["local_txt_filepath"]
        ]
        processor.metadata.drop(
            ["is_csv", "local_raw_filepath", "local_txt_filepath", "detected_language"],
            axis=1,
            errors="ignore",
        ).to_csv(f"{temp_directory}metadata.csv", index=False)

        # move the metadata to the appropriate place for RAG
        processor.metadata.drop(
            ["is_csv", "local_raw_filepath", "local_txt_filepath", "detected_language"],
            axis=1,
            errors="ignore",
        ).to_csv(f"corpora/metadata_{corpus_name}.csv", index=False)

        # update the corpora list
        tmp_corpus = pd.DataFrame(
            {
                "name": corpus_name,
                "text_path": f"corpora/{corpus_name}/",
                "metadata_path": f"corpora/metadata_{corpus_name}.csv",
            },
            index=[0],
        )

        local_corpora_dict = pd.read_csv("metadata/corpora_list.csv")
        new_corpora_dict = pd.concat(
            [local_corpora_dict, tmp_corpus], ignore_index=True
        ).drop_duplicates()
        new_corpora_dict.to_csv("metadata/corpora_list.csv", index=False)

        # clear out the tmp_helper directory
        shutil.rmtree(temp_directory)
    except Exception as error:
        shutil.rmtree(temp_directory)
        raise ValueError(
            f"The following error arose while trying to process the corpus: {repr(error)}"
        )

    return new_corpora_dict


def engage_process_corpus():
    "actually run the process corpus function"
    if st.session_state["process_corpus_button"]:
        # intialize progress bar in case necessary
        old_stdout = sys.stdout
        sys.stdout = Logger(st.progress(0), st.empty())

        with st.spinner("Processing corpus..."):
            st.session_state["corpora_dict"] = process_corpus(
                user_name=st.session_state["user_id"],
                corpus_name=f'{st.session_state["user_id"]}_{st.session_state["new_corpus_name"]}',
                uploaded_document=st.session_state["uploaded_file"],
            )

            update_server_state(
                f'{st.session_state["user_name"]}_selected_corpus',
                st.session_state["new_corpus_name"],
            )

        # clear the progress bar
        try:
            sys.stdout = sys.stdout.clear()
            sys.stdout = old_stdout
        except:
            pass
