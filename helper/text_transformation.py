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


def text_transformation_inputs():
    st.markdown("### Text transformation parameters")
    st.markdown(
        """
Use this section to transform and clean up your texts, performing operations like converting to lower case, removing punctuation, etc. Use the button below to download a template. The template has three tabs:
- `prepunctuation`: Use this list to replace words with punctuation in them, like `COVID-19` > `covid`. Punctuation can be replaced with spaces in subsequent steps, rendering 'COVID 19' no longer as one word. The CSV should have two columns, `term` and `replacement`. If you select `Perform lowercase` in the checkbox iunder `Other text transformation options` below, you can limit the terms to lowercase terms only.
- `postpunctuation`: Use this list to replace words, like `United Nations` > `un`. The CSV should have two columns, `term` and `replacement`. If you select `Perform lowercase` in the checkbox under `Other text transformation options` below, you can limit the terms to lowercase terms only.
- `exclude`: Use this list to exclude common terms from things like word count, like `good morning`, etc. The CSV should have one column, `term`. If you select `Perform lowercase` in the checkbox under `Other text transformation options` below, you can limit the terms to lowercase terms only. **Note** this list will not delete words from the corpus, just rather supress them from being shown in word counts. If you want to delete a term, use the `postpunctuation` tab and simply leave the `replacement` column blank.

If you don't want to use one of the tabs, just leave its entries blank when uploading.
"""
    )
    # template
    with open(
        "metadata/transformation_parameters_template.xlsx",
        "rb",
    ) as template_file:
        template_byte = template_file.read()

    st.download_button(
        "Download transformation parameters template",
        template_byte,
        "transformation_parameters.xlsx",
        "application/octet-stream",
        help="Download transformation parameters template.",
    )

    st.markdown("### Upload your transformation parameters")

    # upload your file
    st.session_state["transformation_parameters_upload"] = st.file_uploader(
        "Transformation parameters",
        type=[".xlsx"],
        help="Upload your transformation parameters file. It **MUST** be named `transformation_parameters.xlsx`",
    )

    # upload the file
    st.session_state["transformation_parameters_button"] = st.button(
        "Upload transformation parameters",
        help="Upload your transformation parameters file. It **MUST** be named `transformation_parameters.xlsx`",
    )

    if os.path.exists(
        f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/transformation_parameters.xlsx"
    ):
        st.info(
            "A transformation parameters excel file has already been uploaded. You can reupload and overwrite it."
        )
        with open(
            f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/transformation_parameters.xlsx",
            "rb",
        ) as template_file:
            template_byte = template_file.read()

        st.download_button(
            "Download existing transformation parameters",
            template_byte,
            "transformation_parameters.xlsx",
            "application/octet-stream",
            help="Download existing transformation parameters.",
        )

    # copy the file
    if st.session_state["transformation_parameters_button"]:
        with open(
            f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/transformation_parameters.xlsx",
            "wb",
        ) as new_file:
            new_file.write(
                st.session_state["transformation_parameters_upload"].getvalue()
            )
            new_file.close()

        st.info("Transformation parameters succesfully uploaded!")

    # other text conversion options
    st.markdown("### Other text conversion options")
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

    # perform stemming
    st.session_state["perform_stemming"] = st.checkbox(
        "Perform stemming",
        help="Whether or not to stem the text. That is replacing words with their roots, e.g., 'running', 'runs', 'ran' are all converted to 'run'.",
    )

    # run transformation button
    st.markdown("### Run the transformation")

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
                    pd.read_excel(
                        f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/transformation_parameters.xlsx",
                        sheet_name="prepunctuation",
                    )
                    if os.path.exists(
                        f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/transformation_parameters.xlsx"
                    )
                    else None
                ),
                perform_remove_punctuation=st.session_state["remove_punctuation"],
                replace_words_df=(
                    pd.read_excel(
                        f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/transformation_parameters.xlsx",
                        sheet_name="postpunctuation",
                    )
                    if os.path.exists(
                        f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/transformation_parameters.xlsx"
                    )
                    else None
                ),
                exclude_words_df=(
                    pd.read_excel(
                        f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/transformation_parameters.xlsx",
                        sheet_name="exclude",
                    )
                    if os.path.exists(
                        f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/transformation_parameters.xlsx"
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
                f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/metadata_clean.xlsx"
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
