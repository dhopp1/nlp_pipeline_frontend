import pandas as pd
from streamlit_server_state import server_state, no_rerun
import streamlit as st


def ui_tab():
    "tab title and icon"
    st.set_page_config(
        page_title="NLP Pipeline",
        page_icon="https://www.svgrepo.com/show/398374/speaking-head.svg",
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

    # upload file
    st.session_state["uploaded_file"] = st.sidebar.file_uploader(
        "",
        type=[".zip", ".docx", ".doc", ".txt", ".pdf", ".csv"],
        help="Upload either a single `metadata.csv` file, with at least one column named `web_filepath` with the web addresses of the .html or .pdf documents, or upload a .zip file that contains a folder named `corpus` with the .csv, .doc, .docx, .txt, or .pdf files inside. You can optionally include a `metadata.csv` file in the zip file at the same level as the `corpus` folder, with at least a column named `filename` with the names of the files. If you want to only include certain page numbers of PDF files, in the metadata include a column called 'page_numbers', with the pages formatted as e.g., '1,6,9:12'.",
    )

    # set corpus name
    st.session_state["new_corpus_name"] = st.sidebar.text_input(
        "Uploaded corpus name",
        value=(
            "None"
            if "new_corpus_name" not in st.session_state
            else st.session_state["new_corpus_name"]
        ),
        help="The name of the new corpus you are processing. It must be only lower case, no special characters, no spaces. Use underscores.",
    )

    # process corpus button
    st.session_state["process_corpus_button"] = st.sidebar.button(
        "Convert to text",
        help="Click to convert the documents to text.",
    )


def ui_load_corpus():
    "load a corpus"
    pass
