from nlp_pipeline.nlp_pipeline import nlp_processor
import os
import pandas as pd
import streamlit as st

from helper.text_transformation import csv_expander, initialize_processor


def search_terms_inputs():
    "info and csv upload for search terms"
    st.markdown("### Search terms")
    st.markdown("Use this section to search for terms within the corpus.")

    # search terms
    csv_expander(
        expander_label="Search terms CSV",
        info="Use this list to search for the occurences of terms in the corpus.",
        session_state_file_name="search_terms",
        uploader_help="Upload your csv list of search terms to look for. It can have multiple columns ending in the most specific terms to search for. E.g., columns of `grouping`>`concept`>`permutation`. Only the term in the right-most column, `permutation`, will be searched for. The other columns are for groupings and aggregations.",
        uploader_button_name="search_terms_button",
        uploader_button_label="Upload search terms",
        uploader_button_help="Upload a CSV with search terms.",
        csv_name="search_terms.csv",
        finish_info="Search terms CSV successfully uploaded!",
        uploaded_info="Search terms CSV uploaded",
        uploaded_error="Search terms CSV not uploaded",
        download_button_name="Download search terms list",
        download_button_info="Download search terms list for verification.",
    )

    # other search term parameters
    with st.expander(label="Search parameters"):
        st.session_state["character_buffer"] = st.number_input(
            "Length of character buffer",
            min_value=3,
            value=100,
            help="The search will return the context of the found terms as well. This parameter is the number of characters on either side of the term occurrence. A bigger number returns a larger context.",
        )

        st.session_state["co_occurring_n_words"] = st.number_input(
            "Co-occurring n words limit",
            min_value=1,
            value=50,
            help="The search will also return the top n words that occur alongside each of the search terms.",
        )

    # second-level search terms
    csv_expander(
        expander_label="Second-level search terms CSV",
        info="Use this list to search terms that occur in the context of the search terms.",
        session_state_file_name="second_level_search_terms",
        uploader_help="Upload your csv list of second level search terms to look for. It should have the same structure as the search terms CSV. E.g., if `grouping`>`concept`>`permutation` was used there, this CSV should have `grouping`>`concept`>`permutation`>`second_level_term`. Then it will find the counts of `second_level_term` within the context of the `permutation` term.",
        uploader_button_name="second_Level_search_terms_button",
        uploader_button_label="Upload second level search terms",
        uploader_button_help="Upload a CSV with second level search terms.",
        csv_name="second_level_search_terms.csv",
        finish_info="Second level search terms CSV successfully uploaded!",
        uploaded_info="Second level search terms CSV uploaded",
        uploaded_error="Second level search terms CSV not uploaded",
        download_button_name="Download second level search terms list",
        download_button_info="Download second level search terms list for verification.",
    )

    # run search terms button
    if os.path.exists(
        f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/search_terms.csv"
    ):
        st.session_state["run_search_button"] = st.button(
            "Execute search",
            help="Search the corpus for terms in the uploaded search terms list.",
        )

        if st.session_state["run_search_button"]:
            with st.spinner("Searching corpus..."):
                processor = initialize_processor()

                # search terms
                processor.gen_search_terms(
                    group_name="all",
                    text_ids=list(processor.metadata.text_id.values),
                    search_terms_df=pd.read_csv(
                        f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/search_terms.csv",
                        encoding="latin1",
                    ),
                    path_prefix="transformed",
                    character_buffer=st.session_state["character_buffer"],
                )

                # co-occurring terms
                processor.gen_co_occurring_terms(
                    group_name="all",
                    co_occurrence_terms_df=pd.read_csv(
                        f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/search_terms.csv",
                        encoding="latin1",
                    ),
                    n_words=st.session_state["co_occurring_n_words"],
                )

                # second-level search terms
                if os.path.exists(
                    f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/second_level_search_terms.csv"
                ):
                    processor.gen_second_level_search_terms(
                        group_name="all",
                        second_level_search_terms_df=pd.read_csv(
                            f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/second_level_search_terms.csv",
                            encoding="latin1",
                        ),
                    )

            st.info("Corpus searched successfully!")

        # search term outputs
        if os.path.exists(
            f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/csv_outputs/search_terms_all_occurrences.csv"
        ):
            st.info(
                "The search has previously been run. Click the `Execute search` button above to override that output with a new search."
            )

            with st.expander(label="Outputs"):
                # download all occurrences
                st.download_button(
                    "Download context of all found search terms",
                    pd.read_csv(
                        f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/csv_outputs/search_terms_all_occurrences.csv",
                        encoding="latin1",
                    )
                    .to_csv(index=False)
                    .encode("latin1"),
                    "search_terms_all_occurrences.csv",
                    "text/csv",
                    help="Downloads a CSV with the context of all search term occurrences.",
                )

                # download all by groupings
                for col in pd.read_csv(
                    f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/search_terms.csv"
                ).columns:
                    st.download_button(
                        f"Download counts of all found search terms grouped by {col}",
                        pd.read_csv(
                            f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/csv_outputs/search_terms_all_counts_by_{col}.csv",
                            encoding="latin1",
                        )
                        .to_csv(index=False)
                        .encode("latin1"),
                        f"search_terms_all_counts_by_{col}.csv",
                        "text/csv",
                        help="Downloads a CSV with counts of all search terms.",
                    )

                # download co-occurrences
                st.download_button(
                    "Download count of co-occurring words",
                    pd.read_csv(
                        f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/csv_outputs/search_terms_all_co_occurrences.csv",
                        encoding="latin1",
                    )
                    .to_csv(index=False)
                    .encode("latin1"),
                    "search_terms_all_co_occurrences.csv",
                    "text/csv",
                    help="Downloads a CSV with the top n words that occur in the contexts of the different search terms.",
                )

                # second-level search terms
                if os.path.exists(
                    f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/csv_outputs/search_terms_all_second_level_counts.csv"
                ):
                    st.download_button(
                        "Download count of second-level search terms",
                        pd.read_csv(
                            f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/csv_outputs/search_terms_all_second_level_counts.csv",
                            encoding="latin1",
                        )
                        .to_csv(index=False)
                        .encode("latin1"),
                        "search_terms_all_second_level_counts.csv",
                        "text/csv",
                        help="Downloads a CSV with the count of words that occur in the context of previous search terms.",
                    )

    # search for a specific term
    with st.expander(label="Individual search term"):
        st.markdown(
            "Search through every document for occurrences of a specific search term."
        )

        st.session_state["search_individual_input"] = st.text_input(
            "Search term",
            value="",
            help="Get a breakdown of occurrences of a search in each document",
        )

        st.session_state["search_individual_button"] = st.button(
            "Execute individual term search",
            help="Search the corpus for an individual search term.",
        )

        if st.session_state["search_individual_button"]:
            with st.spinner("Performing search..."):
                # execute search
                count = []
                text_ids = []
                for text in os.listdir(
                    f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/transformed_txt_files/"
                ):
                    if ".txt" in text:
                        with open(
                            f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/transformed_txt_files/{text}",
                            "r",
                            encoding="latin1",
                        ) as f:
                            stringx = f.read()
                        text_ids.append(int(text.split("_")[1].split(".")[0]))
                        count.append(
                            stringx.count(
                                " " + st.session_state["search_individual_input"] + " "
                            )
                        )

                output = pd.DataFrame({"text_id": text_ids, "count": count})
                output["search_term"] = st.session_state["search_individual_input"]
                output = output.loc[:, ["text_id", "search_term", "count"]]
                output.to_csv(
                    f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/csv_outputs/individual_search_results.csv",
                    index=False,
                )
            st.info("Search completed!")

        if os.path.exists(
            f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/csv_outputs/individual_search_results.csv"
        ):
            st.download_button(
                "Download individual term search results",
                pd.read_csv(
                    f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/csv_outputs/individual_search_results.csv",
                    encoding="latin1",
                )
                .to_csv(index=False)
                .encode("latin1"),
                "individual_search_term_results.csv",
                "text/csv",
                help="Download result of individual term search.",
            )

            st.dataframe(
                data=pd.read_csv(
                    f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/csv_outputs/individual_search_results.csv",
                    encoding="latin1",
                ),
                hide_index=True,
            )
