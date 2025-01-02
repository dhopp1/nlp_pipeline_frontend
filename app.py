import streamlit as st
from streamlit_server_state import server_state

from helper.text_setup import engage_process_corpus
from helper.ui import (
    import_styles,
    ui_header,
    ui_load_corpus,
    ui_metadata_upload,
    ui_tab,
)
from helper.user_management import check_password, set_user_id

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

st.sidebar.divider()

engage_process_corpus()  # convert to text


# corpus name
ui_load_corpus()
