from nlp_pipeline.nlp_pipeline import nlp_processor
import os
import pandas as pd
import plotly.express as px
import streamlit as st
import sys

from helper.text_transformation import initialize_processor
from helper.progress_bar import Logger


def search_terms_inputs():
    "info and csv upload for search terms"
    st.markdown("## Search terms")
    st.markdown(
        """
Use this section to search for terms within the corpus. For the `Execute search` button to work properly, the `Replace periods` and `Remove punctuation` options must have been selected and run on the `Text transformation` tab. Download a template of the file to upload using the button below. The file has two tabs:
- `search_terms`: Search terms to look for. The sheet can have multiple columns ending in the most specific terms to search for. E.g., columns of `grouping`>`concept`>`permutation`. Only the term in the right-most column, `permutation`, will be searched for. The other columns are for groupings and aggregations.
- `second_level_search_terms: Searches for words within the context of the terms in the `search_terms` sheet. The sheet should have the same structure as the search terms sheet. E.g., if `grouping`>`concept`>`permutation` was used there, this CSV should have `grouping`>`concept`>`permutation`>`second_level_term`. Then it will find the counts of `second_level_term` within the context of the `permutation` term.
"""
    )

    st.warning(
        "**Note**: If you want to perform a search, you **MUST** have checked the `Replace periods` option on the `Text transformation` tab when you transformed your text."
    )

    # template
    with open(
        "metadata/search_terms_template.xlsx",
        "rb",
    ) as template_file:
        template_byte = template_file.read()

    st.download_button(
        "Download search terms template",
        template_byte,
        "search_terms.xlsx",
        "application/octet-stream",
        help="Download search terms template.",
    )

    # upload your file
    st.session_state["search_terms_upload"] = st.file_uploader(
        "Search terms",
        type=[".xlsx"],
        help="Upload your search terms file. It **MUST** be named `search_terms.xlsx`",
    )

    # upload the file
    st.session_state["search_terms_button"] = st.button(
        "Upload search terms",
        help="Upload your search terms file. It **MUST** be named `search_terms.xlsx`",
    )

    if os.path.exists(
        f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/search_terms.xlsx"
    ):
        st.info(
            "A search terms excel file has already been uploaded. You can reupload and overwrite it."
        )
        with open(
            f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/search_terms.xlsx",
            "rb",
        ) as template_file:
            template_byte = template_file.read()

        st.download_button(
            "Download existing search terms",
            template_byte,
            "search_terms.xlsx",
            "application/octet-stream",
            help="Download existing search terms.",
        )

    # copy the file
    if st.session_state["search_terms_button"]:
        with open(
            f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/search_terms.xlsx",
            "wb",
        ) as new_file:
            new_file.write(st.session_state["search_terms_upload"].getvalue())
            new_file.close()

        st.info("Search terms succesfully uploaded!")

    # match exclusion
    with st.expander("Exclude occurrences from search matches"):
        st.markdown("### Exclude occurrences from search matches")
        st.markdown(
            "You can run the search process, then go through and determine if you want to exclude any match occurrences from downstream metrics. For instance, if you have deemed some to be irrelevant or off-topic. To do so, upload here an excel with two columns, `permutation` and `sentence_context`. In the former, put the permutation/word/term that was being searched for where the occurrence was matched. In the latter, put the `sentence_context` exactly as it appears in the `search_terms_output.xlsx` workbook, `all_occurrences` sheet, `sentence_context` column. Once you have uploaded the file here, press the `Execute search` button again."
        )

        # template
        with open(
            "metadata/exclude_occurrences_template.xlsx",
            "rb",
        ) as template_file:
            template_byte = template_file.read()

        st.download_button(
            "Download exclude occurrences template",
            template_byte,
            "exclude_occurrences.xlsx",
            "application/octet-stream",
            help="Download exclude occurrences template.",
        )

        # upload your file
        st.session_state["exclude_occurrences_upload"] = st.file_uploader(
            "Exclude occurrences file",
            type=[".xlsx"],
            help="Upload your exclude occurrences file. It **MUST** be named `exclude_occurrences.xlsx`",
        )

        # upload the file
        st.session_state["exclude_occurrences_button"] = st.button(
            "Upload exclude occurrences file",
            help="Upload your exclude occurrences file. It **MUST** be named `exclude_occurrences.xlsx`",
        )

        if os.path.exists(
            f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/exclude_occurrences.xlsx"
        ):
            st.info(
                "An exclude occurrences excel file has already been uploaded. You can reupload and overwrite it."
            )
            with open(
                f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/exclude_occurrences.xlsx",
                "rb",
            ) as template_file:
                template_byte = template_file.read()

            st.download_button(
                "Download existing exclude occurrences file",
                template_byte,
                "exclude_occurrences.xlsx",
                "application/octet-stream",
                help="Download existing exclude occurrences file.",
            )

        # copy the file
        if st.session_state["exclude_occurrences_button"]:
            with open(
                f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/exclude_occurrences.xlsx",
                "wb",
            ) as new_file:
                new_file.write(
                    st.session_state["exclude_occurrences_upload"].getvalue()
                )
                new_file.close()

            st.session_state["exclude_occurrences"] = pd.read_excel(
                f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/exclude_occurrences.xlsx"
            )

            st.info("Exclude occurrences file succesfully uploaded!")

        if "exclude_occurrences" not in st.session_state:
            st.session_state["exclude_occurrences"] = None
        else:
            if os.path.exists(
                f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/exclude_occurrences.xlsx"
            ):
                st.session_state["exclude_occurrences"] = pd.read_excel(
                    f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/exclude_occurrences.xlsx"
                )

    # other search term parameters
    st.markdown("### Other search term parameters")
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

    # run search terms button
    if os.path.exists(
        f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/search_terms.xlsx"
    ):
        st.markdown("### Execute the search")
        st.session_state["run_search_button"] = st.button(
            "Execute search",
            help="Search the corpus for terms in the uploaded search terms list.",
        )

        if st.session_state["run_search_button"]:
            # intialize progress bar in case necessary
            old_stdout = sys.stdout
            sys.stdout = Logger(st.progress(0), st.empty())

            with st.spinner("Searching corpus..."):
                processor = initialize_processor()

                # search terms
                processor.gen_search_terms(
                    group_name="all",
                    text_ids=list(processor.metadata.text_id.values),
                    search_terms_df=pd.read_excel(
                        f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/search_terms.xlsx",
                        sheet_name="search_terms",
                    ),
                    path_prefix="transformed",
                    character_buffer=st.session_state["character_buffer"],
                    match_exclusion=st.session_state["exclude_occurrences"],
                )

                # search terms per document (for count per 1000, etc.)
                processor.gen_aggregated_search_terms(
                    group_names=list(processor.metadata.text_id.values),
                    text_ids=[[x] for x in list(processor.metadata.text_id.values)],
                    search_terms_df=pd.read_excel(
                        f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/search_terms.xlsx",
                        sheet_name="search_terms",
                    ),
                    path_prefix="transformed",
                    character_buffer=st.session_state["character_buffer"],
                )

                # co-occurring terms
                processor.gen_co_occurring_terms(
                    group_name="all",
                    co_occurrence_terms_df=pd.read_excel(
                        f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/search_terms.xlsx",
                        sheet_name="search_terms",
                    ),
                    n_words=st.session_state["co_occurring_n_words"],
                )

                # second-level search terms
                if (
                    len(
                        pd.read_excel(
                            f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/search_terms.xlsx",
                            sheet_name="second_level_search_terms",
                        )
                    )
                    > 0
                ):
                    processor.gen_second_level_search_terms(
                        group_name="all",
                        second_level_search_terms_df=pd.read_excel(
                            f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/search_terms.xlsx",
                            sheet_name="second_level_search_terms",
                        ),
                    )

                # delete existing excel of outputs
                if os.path.exists(
                    f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/csv_outputs/search_terms_output.xlsx"
                ):
                    os.remove(
                        f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/csv_outputs/search_terms_output.xlsx"
                    )

            st.info("Corpus searched successfully!")

            # clear the progress bar
            try:
                sys.stdout = sys.stdout.clear()
                sys.stdout = old_stdout
            except:
                pass

        # search term outputs
        if os.path.exists(
            f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/csv_outputs/search_terms_all_occurrences.csv"
        ):
            st.info(
                "The search has previously been run. Click the `Execute search` button above to overwrite that output with a new search."
            )

            # create excel version
            if not (
                os.path.exists(
                    f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/csv_outputs/search_terms_output.xlsx"
                )
            ):
                dfs = {}

                # all occurrences
                dfs["all_occurrences"] = pd.read_csv(
                    f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/csv_outputs/search_terms_all_occurrences.csv",
                    encoding="latin1",
                )

                # groupings
                for col in pd.read_excel(
                    f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/search_terms.xlsx",
                    sheet_name="search_terms",
                ).columns:
                    dfs[f"all_counts_by_{col}"] = pd.read_csv(
                        f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/csv_outputs/search_terms_all_counts_by_{col}.csv",
                        encoding="latin1",
                    )

                # co-occurrences
                dfs["co_occurrences"] = pd.read_csv(
                    f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/csv_outputs/search_terms_all_co_occurrences.csv",
                    encoding="latin1",
                )

                # second-level search terms
                if os.path.exists(
                    f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/csv_outputs/search_terms_all_second_level_counts.csv"
                ):
                    dfs["second_level_search"] = pd.read_csv(
                        f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/csv_outputs/search_terms_all_second_level_counts.csv",
                        encoding="latin1",
                    )

                # grouped by text id for everything on a per document level
                for col in pd.read_excel(
                    f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/search_terms.xlsx",
                    sheet_name="search_terms",
                ).columns:
                    dfs[f"text_id_by_{col}"] = pd.read_csv(
                        f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/csv_outputs/search_terms_grouped_by_{col}.csv",
                        encoding="latin1",
                    ).rename({"group": "text_id"}, axis=1)

                # create excel
                with pd.ExcelWriter(
                    f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/csv_outputs/search_terms_output.xlsx",
                    engine="xlsxwriter",
                ) as writer:
                    for key in dfs.keys():
                        dfs[key].to_excel(writer, sheet_name=key, index=False)

            # download the file
            with open(
                f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/csv_outputs/search_terms_output.xlsx",
                "rb",
            ) as template_file:
                template_byte = template_file.read()

            st.download_button(
                "Download search terms output",
                template_byte,
                "search_terms_output.xlsx",
                "application/octet-stream",
                help="Download search output.",
            )

    # excel sheet with occurrences and new search terms binary found
    st.markdown(
        "## Second-level search binary occurrence and grouping \nGenerate an excel file that shows occurrences by metadata group. It shows occurrences of second-level search terms within the context of other search terms and tells what percentage of a metadata group a term is found in. So if the term is mentioned multiple times in a document, it will only count as a binary 'yes' in the `grouped` tab of the excel output. You can search for 'ors' in the second-level search term CSV as well, separate terms with a `|`. So `shipping|trade` will mark the document as containing the term if either of those terms apperas. Uses the `second_level_search_terms` sheet as an input. "
    )

    if (
        os.path.exists(
            f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/search_terms.xlsx"
        )
        and os.path.exists(
            f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/csv_outputs/search_terms_all_occurrences.csv"
        )
        and len(
            pd.read_excel(
                f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/search_terms.xlsx",
                sheet_name="second_level_search_terms",
            )
        )
        > 0
    ):
        # selectbox with which column you want to put in the tabs of the excel sheet
        search_columns = list(
            pd.read_excel(
                f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/search_terms.xlsx"
            ).columns
        )
        st.session_state["excel_tab_column"] = st.selectbox(
            "Search CSV column",
            options=search_columns,
            index=0,
            help="Which column of the search terms CSV to split into individual excel tabs.",
        )

        st.session_state["excel_metadata_column"] = st.selectbox(
            "Which metadata column to aggregate by",
            options=st.session_state["metadata"]
            .drop(
                [
                    "web_filepath",
                    "local_raw_filepath",
                    "local_txt_filepath",
                    "detected_language",
                ],
                axis=1,
            )
            .columns,
            index=0,
            help="Which column of the metadata to group by for a binary count of a term appears in the grouping or not/the share of the group where it appears.",
        )

        # go through unique values in that grouping
        st.session_state["excel_button"] = st.button(
            "Generate excel file",
        )

        if st.session_state["excel_button"]:
            with st.spinner("Generating excel file..."):
                second_level_terms = pd.read_excel(
                    f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/search_terms.xlsx",
                    sheet_name="second_level_search_terms",
                )
                df = pd.read_csv(
                    f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/csv_outputs/search_terms_all_occurrences.csv"
                )
                context_dict = {}
                for value in df[st.session_state["excel_tab_column"]].unique():
                    short_val = value.lower().replace(" ", "_")[
                        :5
                    ]  # excel tab-friendly name
                    context_dict[short_val] = df.loc[
                        lambda x: x[st.session_state["excel_tab_column"]] == value,
                        ["text_id"] + search_columns + ["character_buffer_context"],
                    ].reset_index(drop=True)
                    # adding metadata columns
                    context_dict[short_val] = context_dict[short_val].merge(
                        st.session_state["metadata"].drop(
                            [
                                "web_filepath",
                                "local_raw_filepath",
                                "local_txt_filepath",
                                "detected_language",
                            ],
                            axis=1,
                        ),
                        how="left",
                        on="text_id",
                    )

                    # searching for second-level search terms
                    second_search_i = list(
                        second_level_terms.loc[
                            lambda x: x[st.session_state["excel_tab_column"]] == value,
                            :,
                        ]
                        .iloc[:, -1]
                        .values
                    )
                    for term in second_search_i:
                        context_dict[short_val][term] = 0
                        for i in range(len(context_dict[short_val])):
                            search_terms = [" " + x + " " for x in term.split("|")]
                            if any(
                                substring
                                in context_dict[short_val].loc[
                                    i, "character_buffer_context"
                                ]
                                for substring in search_terms
                            ):
                                context_dict[short_val].loc[i, term] = 1

                # aggregation by group
                context_dict["grouped"] = second_level_terms.copy()
                for metadata_value in st.session_state["metadata"][
                    st.session_state["excel_metadata_column"]
                ].unique():  # going through metadata value columns
                    context_dict["grouped"][metadata_value] = ""
                    for i in range(len(context_dict["grouped"])):  # going through rows
                        # which tab checking
                        short_val = (
                            context_dict["grouped"]
                            .loc[i, st.session_state["excel_tab_column"]]
                            .lower()
                            .replace(" ", "_")[:5]
                        )  # excel tab-friendly name

                        denominator = len(
                            st.session_state["metadata"].loc[
                                lambda x: x[st.session_state["excel_metadata_column"]]
                                == metadata_value,
                                :,
                            ]
                        )  # how many text ids in this group
                        numerator = len(
                            context_dict[short_val]
                            .loc[
                                lambda x: (
                                    x[st.session_state["excel_metadata_column"]]
                                    == metadata_value
                                )
                                & (x[second_level_terms.iloc[i, -1]] == 1),
                                "text_id",
                            ]
                            .unique()
                        )
                        ratio = numerator / denominator
                        context_dict["grouped"].loc[i, metadata_value] = ratio

                # write out excel file
                with pd.ExcelWriter(
                    f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/csv_outputs/excel_output.xlsx"
                ) as writer:
                    for key, value in context_dict.items():
                        value.to_excel(writer, sheet_name=key, index=False)

            st.info("Excel file successfully created!")

        # download the excel file
        if os.path.exists(
            f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/csv_outputs/excel_output.xlsx"
        ):
            st.info(
                "The second-level binary search has previously been run. You can run it again to overwrite the result."
            )
            with open(
                f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/csv_outputs/excel_output.xlsx",
                "rb",
            ) as template_file:
                template_byte = template_file.read()

            st.download_button(
                "Download excel file",
                template_byte,
                "excel_output.xlsx",
                "application/octet-stream",
                help="Download excel file.",
            )

    # search for a specific term
    st.markdown(
        "## Individual search term \nSearch through every document for occurrences of a specific search term."
    )

    st.session_state["search_individual_input"] = st.text_input(
        "Search term",
        value="",
        help="Get a breakdown of occurrences of a search in each document",
    )

    # dropdown of groups
    if "metadata" in st.session_state:
        st.session_state["individuaL_search_groups"] = st.selectbox(
            "Metadata column grouping to group search results",
            options=["NA"]
            + [
                x
                for x in st.session_state["metadata"].columns
                if x
                not in [
                    "local_raw_filepath",
                    "local_txt_filepath",
                    "detected_language",
                ]
            ],
            index=0,
            help="You can alternatively select a metadata column to group the results by. Leave as `NA` to not group.",
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

                # group by metadata columln if specified
                if st.session_state["individuaL_search_groups"] != "NA":
                    output = output.merge(
                        st.session_state["metadata"], how="left", on="text_id"
                    ).loc[
                        :,
                        [
                            st.session_state["individuaL_search_groups"],
                            "search_term",
                            "count",
                        ],
                    ]
                    output = (
                        output.groupby(st.session_state["individuaL_search_groups"])
                        .sum()
                        .reset_index()
                    )

                output = output.sort_values([output.columns[0]], axis=0).reset_index(
                    drop=True
                )

                output.to_excel(
                    f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/csv_outputs/individual_search_results.xlsx",
                    index=False,
                )
            st.info("Search completed!")

    if os.path.exists(
        f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/csv_outputs/individual_search_results.xlsx"
    ):
        with open(
            f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/csv_outputs/individual_search_results.xlsx",
            "rb",
        ) as template_file:
            template_byte = template_file.read()

        st.download_button(
            "Download individual term search results",
            template_byte,
            "individual_search_term_results.xlsx",
            "application/octet-stream",
            help="Download individual term search results.",
        )

        # bar plot
        try:
            plot_df = pd.read_excel(
                f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/csv_outputs/individual_search_results.xlsx"
            )
            fig = px.bar(
                plot_df,
                x=plot_df.columns[0],
                y="count",
            )
            fig.update_layout(
                yaxis_title="Count",
                xaxis_title="",
                title=f"Occurrence of '{plot_df.loc[0, 'search_term']}' in documents",
            )
            st.plotly_chart(fig, height=450, use_container_width=True)
        except:
            pass
