import hmac

import os
import pandas as pd
import shutil
import streamlit as st


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


def validate_corpora():
    corpora_list = pd.read_csv("metadata/corpora_list.csv")

    # delete orphaned directories
    for directory in [
        item
        for item in os.listdir("corpora/")
        if os.path.isdir(os.path.join("corpora/", item))
    ]:
        if directory not in corpora_list["name"].values:
            shutil.rmtree(f"corpora/{directory}")
            print(True)
        else:
            print(False)

    # delete incomplete corpora
    for corpus in corpora_list["name"]:
        valid_corpus = False
        valid_metadata = False
        valid_txts = False

        try:
            if os.path.exists(f"corpora/{corpus}/metadata_clean.xlsx"):
                valid_metadata = True

            if len(os.listdir(f"corpora/{corpus}/txt_files/")) > 0:
                for filename in os.listdir(f"corpora/{corpus}/txt_files/"):
                    filepath = os.path.join(f"corpora/{corpus}/txt_files/", filename)
                    if os.path.isfile(filepath) and filename.endswith(".txt"):
                        # Check if the file is not empty
                        if os.path.getsize(filepath) > 0:
                            valid_txts = True
        except:
            pass

        if valid_metadata and valid_txts:
            valid_corpus = True

        if not (valid_corpus):
            # delete from corpora_list
            corpora_list = (
                corpora_list.loc[lambda x: x["name"] != corpus, :]
                .sort_values(["name"], axis=0)
                .reset_index(drop=True)
            )
            corpora_list.to_csv("metadata/corpora_list.csv", index=False)

            # delete corpora directory
            try:
                shutil.rmtree(f"corpora/{corpus}/")
            except:
                pass

            # delete metadata file
            try:
                os.remove(f"corpora/metadata_{corpus}.xlsx")
            except:
                pass
