from io import StringIO
import os
import pandas as pd
import streamlit as st
from streamlit_server_state import server_state, server_state_lock, no_rerun


def inputs():

    with st.expander(label="Replace prepunctuation"):
        st.markdown(
            "Use this list to replace words with punctuation in them, like `COVID-19` > `covid`. Punctuation can be replaced with spaces in subsequent steps, rendering 'COVID 19' no longer as one word. The CSV should have two columns, `term` and `replacement`."
        )

        st.session_state["prepunctuation_uploaded_file"] = st.file_uploader(
            "",
            type=[".csv"],
            help="Upload your csv list of terms to replace prepunctuation. It should have two columns: `term` and `replacement`",
        )

        # upload the file
        st.session_state["prepunctuation_button"] = st.button(
            "Upload prepunctuation list",
            help="Upload a CSV with prepunctuation replacement terms.",
        )

        # copy the file
        if st.session_state["prepunctuation_button"]:
            with open(
                f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/prepunctuation_list.csv",
                "wb",
            ) as new_file:
                new_file.write(
                    st.session_state["prepunctuation_uploaded_file"]
                    .getvalue()
                    .decode("latin1")
                    .encode("latin1")
                )
                new_file.close()

            st.info("Prepunctuation CSV successfully uploaded!")

        # download the file
        if os.path.exists(
            f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/prepunctuation_list.csv"
        ):
            st.download_button(
                "Download prepunctuation list",
                pd.read_csv(
                    f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/prepunctuation_list.csv",
                    encoding="latin1",
                )
                .to_csv(index=False)
                .encode("latin1"),
                "prepunctuation_list.csv",
                "text/csv",
                help="Download prepunctuation list for verification.",
            )
