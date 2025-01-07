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
from helper.text_transformation import inputs

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
tabs = st.tabs(["Inputs", "Outputs", "README"])

with tabs[0]:
    inputs()

with tabs[2]:
    st.markdown(
        """
### placeholder
text
"""
    )
