import hmac

import pandas as pd
import streamlit as st
from streamlit_server_state import server_state, server_state_lock, no_rerun


def update_server_state(key, value):
    "update the server state variable"
    with no_rerun:
        with server_state_lock[key]:
            server_state[key] = value


def check_password():
    """Check if a user entered the password correctly"""
    # user list
    if "users_list" not in st.session_state:
        st.session_state["users_list"] = pd.read_csv("metadata/user_list.csv")

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    # Return True if the password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # show input for user name
    st.session_state["user_name"] = st.selectbox(
        "User",
        st.session_state["users_list"],
        index=None,
        placeholder="Select user...",
    )

    # Show input for password.
    st.text_input(
        "Password", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("Password incorrect")

    return False


def set_user_id():
    "get a user's id from their name"
    if "user_id" not in st.session_state:
        st.session_state["user_id"] = (
            st.session_state["user_name"].lower().replace(" ", "_")
        )