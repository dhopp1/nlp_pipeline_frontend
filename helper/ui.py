import os
import shutil
import time
import pandas as pd
import streamlit as st


def ui_tab():
    "tab title and icon"
    st.set_page_config(
        page_title="NLP Pipeline",
        page_icon="https://www.svgrepo.com/show/398374/speaking-head.svg",
        layout="wide",
    )


def import_styles():
    "import styles sheet"
    with open("styles/style.css") as css:
        st.markdown(f"<style>{css.read()}</style>", unsafe_allow_html=True)


def ui_header():
    "UI header"
    st.title("NLP Pipeline")


def ui_metadata_upload():
    "UI section for uploading your own documents"

    # upload your own documents
    st.sidebar.markdown(
        "# Upload your metadata file or documents",
        help="Enter the name of your corpus in the `Corpus name` field.",
    )

    with st.sidebar.expander(label="Options"):
        # upload file
        st.session_state["uploaded_file"] = st.file_uploader(
            "",
            type=[".zip", ".docx", ".doc", ".txt", ".pdf", ".xlsx", ".mp3", ".mp4"],
            help="Upload either a single `metadata.xlsx` file, with at least one column named `web_filepath` with the web addresses of the .html or .pdf documents, or upload a .zip file that contains a folder named `corpus` with the files inside. You can optionally include a `metadata.xlsx` file in the zip file at the same level as the `corpus` folder, with at least a column named `filename` with the names of the files. If you want to only include certain page numbers of PDF files, in the metadata include a column called `page_numbers`, with the pages formatted as e.g., `1,6,9:12`. If upon inspection of your converted files, you find some pdfs did not convert to text properly, you can include a `force_ocr` column in your metadata. Set it to `1` to convert that document to text via OCR, and a `0` to not use OCR.",
        )

        # set corpus name
        st.session_state["new_corpus_name"] = st.text_input(
            "Uploaded corpus name",
            value=(
                "None"
                if "new_corpus_name" not in st.session_state
                else st.session_state["new_corpus_name"]
            ),
            help="The name of the new corpus you are processing. It must be only lower case, no special characters, no spaces. Use underscores.",
        )

        # process corpus button
        st.session_state["process_corpus_button"] = st.button(
            "Convert to text",
            help="Click to convert the documents to text.",
        )


def ui_load_corpus():
    "select a corpus"
    st.sidebar.markdown(
        "# Select a corpus",
        help="Once a corpus has been converted to text, select it here to work with it.",
    )

    # list of options
    st.session_state["corpora_list"] = pd.read_csv("metadata/corpora_list.csv")

    st.session_state["corpora_options"] = sorted(
        [
            x.replace(st.session_state["user_id"] + "_", "")
            for x in list(
                st.session_state["corpora_list"]
                .loc[lambda x: x.name.str.contains(st.session_state["user_id"]), "name"]
                .values
            )
        ]
    )

    st.session_state["selected_corpus"] = st.sidebar.selectbox(
        "Corpus name",
        options=["None"] + st.session_state["corpora_options"],
        index=(
            0
            if not st.session_state["process_corpus_button"]
            else (["None"] + st.session_state["corpora_options"]).index(
                st.session_state["new_corpus_name"]
            )
        ),
        help="Which corpus already converted to text to work with",
    )


def ui_download_txt_zip():
    "download text files and metadata in a zip file"
    if os.path.exists(
        f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/raw_text.zip"
    ):
        with open(
            f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/raw_text.zip",
            "rb",
        ) as file:
            st.sidebar.download_button(
                "Download documents converted to text",
                file,
                "raw_text.zip",
                "application/zip",
                help="Download raw converted text files for verification.",
            )


def ui_delete_corpus():
    "delete a corpus"
    if st.session_state["selected_corpus"] != "None":
        st.session_state["delete_button"] = st.sidebar.button("Delete selected corpus")

        if st.session_state["delete_button"]:
            # delete it from metadata corpora list
            cl = pd.read_csv("metadata/corpora_list.csv")
            cl = cl.loc[
                lambda x: x["name"]
                != f"{st.session_state['user_id']}_{st.session_state['selected_corpus']}",
                :,
            ].reset_index(drop=True)
            cl.to_csv("metadata/corpora_list.csv", index=False, encoding="latin1")

            # delete the metadata file
            try:
                os.remove(
                    f"corpora/metadata_{st.session_state['user_id']}_{st.session_state['selected_corpus']}.xlsx"
                )
            except:
                os.remove(
                    f"corpora/metadata_{st.session_state['user_id']}_{st.session_state['selected_corpus']}.csv"
                )

            # delete the directory
            shutil.rmtree(
                f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}"
            )
            st.sidebar.markdown(
                f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}"
            )

            st.sidebar.info("Corpus successfully deleted!")
            time.sleep(2)
