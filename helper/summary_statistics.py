import os
import pandas as pd
import plotly.express as px
import streamlit as st
import sys

from helper.text_transformation import initialize_processor
from helper.progress_bar import Logger


# gen summary statistics csv
def gen_summary_statistics():
    st.markdown("### Summary statistics")
    st.markdown(
        """Generate various summary statistics about the corpus. Column explanations:
- `n_words`: how many words are in the document
- `n_unique_words`: how many unique words are in the document
- `n_sentences`: how many sentences are in the document
- `n_pages`: how many pages are in the document
- `avg_word_length`: how many letters is the average word in the document
- `avg_word_incidence`: how common/rare is the average word in the document, expressed in terms of Zipf value. A word with Zipf value 6 appears once per thousand words and a word with Zipf value 3 appears once per million words.
- `num_chars_numeric`: how many numeric characters appear in the document (i.e., numbers or data).
- `num_chars_alpha`: how many alpha characters appear in the document.
- `numeric_proportion`: ratio between number of numeric and alpha characters. A higher figure implies a more data/figure-heavy document.
"""
    )

    if "metadata" in st.session_state:
        with st.spinner("Loading corpus..."):
            processor = initialize_processor()

        # run button
        st.session_state["run_summary_button"] = st.button(
            "Generate summary statistics",
            help="Generate summary statistics about the corpus.",
        )

        if st.session_state["run_summary_button"]:
            # generate the CSV first with all text ids regardless
            with st.spinner("Generating summary statistics..."):
                # intialize progress bar in case necessary
                old_stdout = sys.stdout
                sys.stdout = Logger(st.progress(0), st.empty())

                processor.gen_summary_stats_csv(
                    text_ids=list(processor.metadata.text_id.values),
                    path_prefix="transformed",
                )
            st.info("Summary statistics successfully calculated!")

            # clear the progress bar
            try:
                sys.stdout = sys.stdout.clear()
                sys.stdout = old_stdout
            except:
                pass

        if os.path.exists(
            f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/csv_outputs/transformed_summary_stats.csv"
        ):
            pd.read_csv(
                f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/csv_outputs/transformed_summary_stats.csv"
            ).to_excel(
                f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/csv_outputs/transformed_summary_stats.xlsx",
                index=False,
            )

            # download button
            with open(
                f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/csv_outputs/transformed_summary_stats.xlsx",
                "rb",
            ) as template_file:
                template_byte = template_file.read()

            st.download_button(
                "Download summary statistics",
                template_byte,
                "summary_statistics.xlsx",
                "application/octet-stream",
                help="Download summary statistics.",
            )

            # bar plot
            # desired column
            st.session_state["summary_stat_column"] = st.selectbox(
                "Which column to plot in the summary statistic bar plot",
                options=[
                    "n_words",
                    "n_unique_words",
                    "n_sentences",
                    "n_pages",
                    "avg_word_length",
                    "avg_word_incidence",
                    "num_chars_numeric",
                    "num_chars_alpha",
                    "numeric_proportion",
                ],
                index=0,
                help="",
            )

            # which metadata column to use for x axis labels
            st.session_state["summary_x_label"] = st.selectbox(
                "Metadata column to display on x axis for summary stats",
                options=[
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
                help="Select which metadata column you want to use for labelling the x axis.",
            )

            plot_df = (
                pd.read_csv(
                    f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/csv_outputs/transformed_summary_stats.csv",
                    encoding="latin1",
                )
                .sort_values(
                    [st.session_state["summary_stat_column"]], axis=0, ascending=False
                )
                .reset_index(drop=True)
            )

            # if a column other than text_id is chosen for the x-axis labels
            if st.session_state["summary_x_label"] != "text_id":
                plot_df = plot_df.merge(
                    st.session_state["metadata"], how="left", on="text_id"
                ).loc[
                    :,
                    [
                        st.session_state["summary_x_label"],
                        "n_words",
                        "n_unique_words",
                        "n_sentences",
                        "n_pages",
                        "avg_word_length",
                        "avg_word_incidence",
                        "num_chars_numeric",
                        "num_chars_alpha",
                        "numeric_proportion",
                    ],
                ]

            fig = px.bar(
                plot_df,
                x=st.session_state["summary_x_label"],
                y=st.session_state["summary_stat_column"],
            )
            fig.update_layout(
                yaxis_title=st.session_state["summary_stat_column"],
                xaxis_title=st.session_state["summary_x_label"],
                title=st.session_state["summary_stat_column"],
                xaxis_type="category",
            )
            st.plotly_chart(fig, height=450, use_container_width=True)
