import glob
import os
import types
import shutil
import sys

from nlp_pipeline.nlp_pipeline import nlp_processor
import pandas as pd
from zipfile import ZipFile
import streamlit as st

from helper.text_transformation import create_zip_file
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

        # only uploaded a metadata XLSX
        if uploaded_document.name.split(".")[-1].lower() == "xlsx":
            metadata = pd.read_excel(f"{temp_directory}tmp.xlsx")
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
            if "force_ocr" in processor.metadata.columns:
                ocr_text_ids = list(
                    processor.metadata.loc[
                        lambda x: x["force_ocr"] == 1, "text_id"
                    ].values
                )
                nonocr_text_ids = list(
                    processor.metadata.loc[
                        lambda x: x["force_ocr"] == 0, "text_id"
                    ].values
                )
                processor.convert_to_text(nonocr_text_ids)
                with st.spinner("Converting OCR PDFs, this may take a while..."):
                    processor.convert_to_text(ocr_text_ids, force_ocr=True)
            else:
                processor.convert_to_text(list(processor.metadata.text_id.values))

            # sync to the local metadata file
            processor.sync_local_metadata()

            # create an excel metadata file
            processor.metadata.to_excel(f"{temp_directory}metadata.xlsx", index=False)

        # uploaded a single .docx, .pdf, or .txt
        elif uploaded_document.name.split(".")[-1].lower() in [
            "pdf",
            "docx",
            "doc",
            "txt",
            "mp3",
            "mp4",
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

            # create an excel metadata file
            processor.metadata.to_excel(f"{temp_directory}metadata.xlsx", index=False)

        # uploaded a zip
        else:
            with ZipFile(f"{temp_directory}tmp.zip", "r") as zObject:
                zObject.extractall(path=temp_directory)

            # sync the object's metadata to the local file
            provided_metadata = any(
                [x.endswith("xlsx") for x in os.listdir(f"{temp_directory}")]
            )

            if provided_metadata:
                metadata = pd.read_excel(
                    f'{temp_directory}{[x for x, y in zip(os.listdir(temp_directory), [x.endswith("xlsx") for x in os.listdir(temp_directory)]) if y][0]}'
                )
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
                    if x.split(".")[-1] in ["txt", "docx", "doc", "pdf"]
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

            # download any files where only a url is provided
            if "web_filepath" in processor.metadata.columns:
                download_ids = list(
                    processor.metadata.loc[
                        lambda x: ~pd.isna(x.web_filepath), "text_id"
                    ].values
                )
                if len(download_ids) > 0:
                    processor.download_text_id(download_ids)

            # select out PDF pages if available
            if "page_numbers" in processor.metadata.columns:
                try:
                    processor.filter_pdf_pages(page_num_column="page_numbers")
                except:
                    pass

            # convert the files to text
            if "force_ocr" in processor.metadata.columns:
                ocr_text_ids = list(
                    processor.metadata.loc[
                        lambda x: x["force_ocr"] == 1, "text_id"
                    ].values
                )
                nonocr_text_ids = list(
                    processor.metadata.loc[
                        lambda x: x["force_ocr"] == 0, "text_id"
                    ].values
                )
                processor.convert_to_text(nonocr_text_ids)
                with st.spinner("Converting OCR PDFs, this may take a while..."):
                    processor.convert_to_text(ocr_text_ids, force_ocr=True)
            else:
                processor.convert_to_text(list(processor.metadata.text_id.values))

            # create an excel metadata file
            processor.metadata.to_excel(f"{temp_directory}metadata.xlsx", index=False)

        ### upload type independent actions

        # move the .txt files to the appropriate place for RAG
        if os.path.exists(f"corpora/{corpus_name}/"):
            shutil.rmtree(f"corpora/{corpus_name}/")
        shutil.copytree(f"{temp_directory}/", f"corpora/{corpus_name}/")

        # adding file-path for application
        processor.metadata["file_path"] = [
            os.path.abspath(f"corpora/{corpus_name}/txt_files/{x.split('/')[-1]}")
            for x in processor.metadata["local_txt_filepath"]
        ]
        processor.metadata.drop(
            ["is_csv", "local_raw_filepath", "local_txt_filepath", "detected_language"],
            axis=1,
            errors="ignore",
        ).to_excel(f"{temp_directory}metadata.xlsx", index=False)

        # move the metadata to the appropriate place for RAG
        processor.metadata.drop(
            ["is_csv", "local_raw_filepath", "local_txt_filepath", "detected_language"],
            axis=1,
            errors="ignore",
        ).to_excel(f"corpora/metadata_{corpus_name}.xlsx", index=False)

        # update the corpora list
        tmp_corpus = pd.DataFrame(
            {
                "name": corpus_name,
                "text_path": f"corpora/{corpus_name}/",
                "metadata_path": f"corpora/metadata_{corpus_name}.xlsx",
            },
            index=[0],
        )

        local_corpora_dict = pd.read_csv("metadata/corpora_list.csv", encoding="latin1")
        new_corpora_dict = pd.concat(
            [local_corpora_dict, tmp_corpus], ignore_index=True
        ).drop_duplicates()
        new_corpora_dict.to_csv("metadata/corpora_list.csv", index=False)

        # clear out the tmp_helper directory
        shutil.rmtree(temp_directory)

        # remove other superfluous documents
        if os.path.exists(f"corpora/{corpus_name}/__MACOSX/"):
            shutil.rmtree(f"corpora/{corpus_name}/__MACOSX/")
        if os.path.exists(f"corpora/{corpus_name}/corpus/"):
            shutil.rmtree(f"corpora/{corpus_name}/corpus/")
        for f in glob.glob(f"corpora/{corpus_name}/tmp.*"):
            os.remove(f)

    except Exception as error:
        shutil.rmtree(temp_directory)
        raise ValueError(
            f"The following error arose while trying to process the corpus: {repr(error)}"
        )

    return new_corpora_dict


def engage_process_corpus():
    "actually run the process corpus function"
    if st.session_state["new_corpus_name"] != "None":
        if st.session_state["process_corpus_button"]:
            # invalid name
            if (
                " " in st.session_state["new_corpus_name"]
                or any(char.isupper() for char in st.session_state["new_corpus_name"])
            ) and (st.session_state["new_corpus_name"] != "None"):
                st.error(
                    "The corpus name must be all lower case and using underscores instead of spaces"
                )
            else:
                # intialize progress bar in case necessary
                old_stdout = sys.stdout
                sys.stdout = Logger(st.progress(0), st.empty())

                with st.spinner("Processing corpus...", show_time=True):
                    st.warning(
                        "If this is taking a while, you may have OCR (scanned) documents in your corpus. These take significantly longer to convert to text. Be patient and don't reload or close the page until you see the message `Corpus successfully processed!` in blue below."
                    )

                    st.session_state["corpora_dict"] = process_corpus(
                        user_name=st.session_state["user_id"],
                        corpus_name=f'{st.session_state["user_id"]}_{st.session_state["new_corpus_name"]}',
                        uploaded_document=st.session_state["uploaded_file"],
                    )

                    st.session_state["selected_corpus"] = st.session_state[
                        "new_corpus_name"
                    ]

                st.session_state["metadata"] = pd.read_excel(
                    f"corpora/{st.session_state['user_id']}_{st.session_state['new_corpus_name']}/metadata.xlsx",
                )

                # create the zip file
                text_ids = list(st.session_state["metadata"].loc[:, "text_id"].values)

                # write a metadata without file_path
                metadata = st.session_state["metadata"].drop(
                    [
                        "local_raw_filepath",
                        "local_txt_filepath",
                        "detected_language",
                    ],
                    axis=1,
                    errors="ignore",
                )
                metadata = metadata[
                    ["text_id"] + [col for col in metadata.columns if col != "text_id"]
                ]
                metadata.to_excel(
                    f"corpora/{st.session_state['user_id']}_{st.session_state['new_corpus_name']}/metadata_clean.xlsx",
                    index=False,
                )
                files = [
                    f"corpora/{st.session_state['user_id']}_{st.session_state['new_corpus_name']}/txt_files/"
                    + str(x)
                    + ".txt"
                    for x in text_ids
                ] + [
                    f"corpora/{st.session_state['user_id']}_{st.session_state['new_corpus_name']}/metadata_clean.xlsx"
                ]

                create_zip_file(
                    files,
                    f"corpora/{st.session_state['user_id']}_{st.session_state['new_corpus_name']}/raw_text.zip",
                )

                # check if valid txt files
                valid_txts = False
                if (
                    len(
                        os.listdir(
                            f"corpora/{st.session_state['user_id']}_{st.session_state['new_corpus_name']}/txt_files/"
                        )
                    )
                    > 0
                ):
                    for filename in os.listdir(
                        f"corpora/{st.session_state['user_id']}_{st.session_state['new_corpus_name']}/txt_files/"
                    ):
                        filepath = os.path.join(
                            f"corpora/{st.session_state['user_id']}_{st.session_state['new_corpus_name']}/txt_files/",
                            filename,
                        )
                        if os.path.isfile(filepath) and filename.endswith(".txt"):
                            # Check if the file is not empty
                            if os.path.getsize(filepath) > 0:
                                valid_txts = True
                if valid_txts:
                    st.info("Corpus successfully processed!")
                else:
                    st.error(
                        "No valid text files were created. Check the URLs or formats of your documents. If using URLs, the provider may block automatic downloading and you need to download the files yourself and upload them as a .zip file."
                    )

                # clear the progress bar
                try:
                    sys.stdout = sys.stdout.clear()
                    sys.stdout = old_stdout
                except:
                    pass
