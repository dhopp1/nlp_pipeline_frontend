from io import StringIO
import os
from nlp_pipeline.nlp_pipeline import nlp_processor
import pandas as pd
import streamlit as st
from streamlit_server_state import server_state, server_state_lock, no_rerun
import zipfile


def initialize_processor():
    "initialize the processor on the selected corpus name"
    metadata_addt_column_names = [
        x
        for x in st.session_state["metadata"].columns
        if x
        not in [
            "text_id",
            "local_raw_filepath",
            "local_txt_filepath",
            "detected_language",
        ]
    ]
    processor = nlp_processor(
        data_path=f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/",
        metadata_addt_column_names=metadata_addt_column_names,
        windows_tesseract_path=None,
        windows_poppler_path=None,
    )
    processor.refresh_object_metadata()
    processor.sync_local_metadata()

    return processor


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


def text_transformation_inputs():
    st.markdown("### Text transformation parameters")
    st.markdown(
        "Use this section to transform and clean up your texts, performing operations like converting to lower case, removing punctuation, etc."
    )

    # prepunctuation
    csv_expander(
        expander_label="Replace prepunctuation",
        info="Use this list to replace words with punctuation in them, like `COVID-19` > `covid`. Punctuation can be replaced with spaces in subsequent steps, rendering 'COVID 19' no longer as one word. The CSV should have two columns, `term` and `replacement`. If you select `Perform lowercase` in the checkbox iunder `Other text transformation options` below, you can limit the terms to lowercase terms only.",
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
        info="Use this list to replace words, like `United Nations` > `un`. The CSV should have two columns, `term` and `replacement`. If you select `Perform lowercase` in the checkbox under `Other text transformation options` below, you can limit the terms to lowercase terms only.",
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
        info="Use this list to exclude common terms from things like word count, like `good morning`, etc. The CSV should have one column, `term`. If you select `Perform lowercase` in the checkbox under `Other text transformation options` below, you can limit the terms to lowercase terms only.",
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

    # other text conversion options
    with st.expander(label="Other text transformation options"):
        # lower case
        st.session_state["perform_lower"] = st.checkbox(
            "Perform lowercase",
            help="Whether or not to convert the texts into all lowercase.",
        )

        # replace accented and unusual
        st.session_state["perform_accented"] = st.checkbox(
            "Replace accented and unusual characters",
            help="Whether or not to replace accented and unusual characters with non-accented equivalents.",
        )

        # remove urls
        st.session_state["remove_urls"] = st.checkbox(
            "Remove URLs", help="Whether or not to remove URLs from the text."
        )

        # remove headers and footers
        st.session_state["remove_headers"] = st.checkbox(
            "Remove headers and footers",
            help="Whether or not to remove headers/footers that may be repeated throughout a text.",
        )

        # replace periods
        st.session_state["replace_periods"] = st.checkbox(
            "Replace periods",
            help="Whether or not to replace periods (.) with |s for consistent word delimiters.",
        )

        # drop numbers
        st.session_state["remove_numbers"] = st.checkbox(
            "Remove numbers",
            help="Whether or not to remove any numerals (0-9) in the text.",
        )

        # remove punctuation
        st.session_state["remove_punctuation"] = st.checkbox(
            "Remove punctuation",
            help="Whether or not to replace any punctuation with spaces.",
        )

        # remove stopwords
        st.session_state["remove_stopwords"] = st.checkbox(
            "Remove stopwords",
            help="Whether or not to remove stopwords (common words like 'and', 'but', etc.).",
        )

        # pervform stemming
        st.session_state["perform_stemming"] = st.checkbox(
            "Perform stemming",
            help="Whether or not to stem the text. That is replacing words with their roots, e.g., 'running', 'runs', 'ran' are all converted to 'run'.",
        )

    # run transformation button
    st.session_state["text_transform_button"] = st.button(
        "Transform text",
        help="Run the stipulated text transformations",
    )

    if st.session_state["text_transform_button"]:
        with st.spinner("Transforming text..."):
            # clear out existing transformed text
            for file in os.listdir(
                f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/transformed_txt_files/"
            ):
                os.remove(
                    f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/transformed_txt_files/{file}"
                )

            processor = initialize_processor()

            processor.transform_text(
                text_ids=list(processor.metadata.text_id.values),
                path_prefix="transformed",
                perform_lower=st.session_state["perform_lower"],
                replace_accented_and_unusual_characters=st.session_state[
                    "perform_accented"
                ],
                perform_remove_urls=st.session_state["remove_urls"],
                perform_remove_multiple_header_and_footers=st.session_state[
                    "remove_headers"
                ],
                perform_replace_period=st.session_state["replace_periods"],
                drop_numbers=st.session_state["remove_numbers"],
                replace_words_with_punctuation_df=(
                    pd.read_csv(
                        f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/prepunctuation_list.csv",
                        encoding="latin1",
                    )
                    if os.path.exists(
                        f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/prepunctuation_list.csv"
                    )
                    else None
                ),
                perform_remove_punctuation=st.session_state["remove_punctuation"],
                replace_words_df=(
                    pd.read_csv(
                        f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/postpunctuation_list.csv",
                        encoding="latin1",
                    )
                    if os.path.exists(
                        f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/postpunctuation_list.csv"
                    )
                    else None
                ),
                exclude_words_df=(
                    pd.read_csv(
                        f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/exclude_list.csv",
                        encoding="latin1",
                    )
                    if os.path.exists(
                        f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/exclude_list.csv"
                    )
                    else None
                ),
                perform_remove_stopwords=st.session_state["remove_stopwords"],
                perform_stemming=st.session_state["perform_stemming"],
                stemmer="snowball",
            )

            # create zip file
            files = [
                f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/transformed_txt_files/transformed_"
                + str(x)
                + ".txt"
                for x in list(processor.metadata.text_id.values)
            ] + [
                f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/metadata_clean.csv"
            ]

            create_zip_file(
                files,
                f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/transformed_text.zip",
            )

            st.info("Text successfully transformed!")

    # download transformed text file
    if os.path.exists(
        f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/transformed_text.zip"
    ):
        st.info(
            "The text has previously been transformed. Click the `Transform text` button above to override that output with a new transformation."
        )
        with open(
            f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/transformed_text.zip",
            "rb",
        ) as file:
            st.download_button(
                "Download transformed text documents",
                file,
                "transformed_text.zip",
                "application/zip",
                help="Download transformed text files for verification.",
            )
