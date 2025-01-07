from io import StringIO
import os
import pandas as pd
import streamlit as st
from streamlit_server_state import server_state, server_state_lock, no_rerun
import zipfile


def create_zip_file(files, zip_path):
    "zip files together"
    zip_path = zip_path
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file in files:
            zipf.write(
                file, os.path.relpath(file, "/".join(file.split("/")[:-1]) + "/")
            )


def csv_expander(
    expander_label,
    info,
    session_state_file_name,
    uploader_help,
    uploader_button_name,
    uploader_button_label,
    uploader_button_help,
    csv_name,
    finish_info,
    uploaded_info,
    uploaded_error,
    download_button_name,
    download_button_info,
):
    with st.expander(label=expander_label):
        st.markdown(info)

        st.session_state[session_state_file_name] = st.file_uploader(
            "",
            type=[".csv"],
            help=uploader_help,
        )

        # upload the file
        st.session_state[uploader_button_name] = st.button(
            uploader_button_label,
            help=uploader_button_help,
        )

        # copy the file
        if st.session_state[uploader_button_name]:
            with open(
                f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/{csv_name}",
                "wb",
            ) as new_file:
                new_file.write(
                    st.session_state[session_state_file_name]
                    .getvalue()
                    .decode("latin1")
                    .encode("latin1")
                )
                new_file.close()

            st.info(finish_info)

        # show status of upload
        if os.path.exists(
            f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/{csv_name}"
        ):
            st.info(uploaded_info)
        else:
            st.error(uploaded_error)

        # download the file
        if os.path.exists(
            f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/{csv_name}"
        ):
            st.download_button(
                download_button_name,
                pd.read_csv(
                    f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/{csv_name}",
                    encoding="latin1",
                )
                .to_csv(index=False)
                .encode("latin1"),
                csv_name,
                "text/csv",
                help=download_button_info,
            )


def inputs():
    # prepunctuation
    csv_expander(
        expander_label="Replace prepunctuation",
        info="Use this list to replace words with punctuation in them, like `COVID-19` > `covid`. Punctuation can be replaced with spaces in subsequent steps, rendering 'COVID 19' no longer as one word. The CSV should have two columns, `term` and `replacement`.",
        session_state_file_name="prepunctuation_uploaded_file",
        uploader_help="Upload your csv list of terms to replace prepunctuation. It should have two columns: `term` and `replacement`",
        uploader_button_name="prepunctuation_button",
        uploader_button_label="Upload prepunctuation list",
        uploader_button_help="Upload a CSV with prepunctuation replacement terms.",
        csv_name="prepunctuation_list.csv",
        finish_info="Prepunctuation CSV successfully uploaded!",
        uploaded_info="Prepunctuation CSV uploaded",
        uploaded_error="Prepunctuation CSV not uploaded",
        download_button_name="Download prepunctuation list",
        download_button_info="Download prepunctuation list for verification.",
    )

    # postpunctuation
    csv_expander(
        expander_label="Replace postpunctuation",
        info="Use this list to replace words, like `United Nations` > `un`. The CSV should have two columns, `term` and `replacement`.",
        session_state_file_name="postpunctuation_uploaded_file",
        uploader_help="Upload your csv list of terms to replace postpunctuation. It should have two columns: `term` and `replacement`",
        uploader_button_name="postpunctuation_button",
        uploader_button_label="Upload postpunctuation list",
        uploader_button_help="Upload a CSV with postpunctuation replacement terms.",
        csv_name="postpunctuation_list.csv",
        finish_info="Postpunctuation CSV successfully uploaded!",
        uploaded_info="Postpunctuation CSV uploaded",
        uploaded_error="Postpunctuation CSV not uploaded",
        download_button_name="Download postpunctuation list",
        download_button_info="Download postpunctuation list for verification.",
    )

    # exclude words
    csv_expander(
        expander_label="Exclude terms",
        info="Use this list to exclude common terms from things like word count, like `good morning`, etc. The CSV should have one column, `term`.",
        session_state_file_name="exclude_uploaded_file",
        uploader_help="Upload your csv list of terms to replace exclude. It should have one column: `term`",
        uploader_button_name="exclude_button",
        uploader_button_label="Upload exclude list",
        uploader_button_help="Upload a CSV with exclusion terms.",
        csv_name="exclude_list.csv",
        finish_info="Exclude CSV successfully uploaded!",
        uploaded_info="Exclude CSV uploaded",
        uploaded_error="Exclude CSV not uploaded",
        download_button_name="Download exclude list",
        download_button_info="Download exclude list for verification.",
    )
