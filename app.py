import os
import pandas as pd
import streamlit as st
from streamlit_server_state import server_state

from helper.text_setup import engage_process_corpus
from helper.ui import (
    import_styles,
    ui_download_txt_zip,
    ui_header,
    ui_load_corpus,
    ui_metadata_upload,
    ui_tab,
)
from helper.user_management import check_password, set_user_id
from helper.text_transformation import text_transformation_inputs

### page setup and authentication
ui_tab()  # icon and page title
ui_header()  # header

if not check_password():
    st.stop()

set_user_id()


### initialization
import_styles()


### sidebar
ui_metadata_upload()
engage_process_corpus()  # convert to text


# corpus name
ui_load_corpus()

# download raw text file button
ui_download_txt_zip()


### tabs
tabs = st.tabs(["Corpus metadata", "Inputs", "Outputs", "README"])

with tabs[0]:
    if os.path.exists(
        f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/metadata.csv"
    ):
        st.download_button(
            "Download metadata",
            pd.read_csv(
                f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/metadata.csv",
                encoding="latin1",
            )
            .to_csv(index=False)
            .encode("latin1"),
            "metadata.csv",
            "text/csv",
            help="Download metadata file.",
        )

        st.dataframe(
            pd.read_csv(
                f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/metadata_clean.csv"
            ),
            hide_index=True,
            height=800,
        )
    else:
        st.error(
            "Upload your metadata file or corpus under the `Options` dropdown on the sidebar, then hit `Convert to text`. If you have already processed a corpus, select its name under the `Corpus name` dropdown on the sidebar."
        )

with tabs[1]:
    text_transformation_inputs()

with tabs[3]:
    st.markdown(
        """
### placeholder
text
"""
    )
