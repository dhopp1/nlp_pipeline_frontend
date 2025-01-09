import os
import pandas as pd
import plotly.express as px
import streamlit as st

from helper.text_transformation import initialize_processor


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
        processor = initialize_processor()

        # run button
        st.session_state["run_summary_button"] = st.button(
            "Generate summary statistics",
            help="Generate summary statistics about the corpus.",
        )

        if st.session_state["run_summary_button"]:
            # generate the CSV first with all text ids regardless
            with st.spinner("Generating summary statistics..."):
                processor.gen_summary_stats_csv(
                    text_ids=list(processor.metadata.text_id.values),
                    path_prefix="transformed",
                )
            st.info("Summary statistics successfully calculated!")

        if os.path.exists(
            f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/csv_outputs/transformed_summary_stats.csv"
        ):
            st.download_button(
                "Download summary statistics",
                pd.read_csv(
                    f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/csv_outputs/transformed_summary_stats.csv",
                    encoding="latin1",
                )
                .to_csv(index=False)
                .encode("latin1"),
                "summary_statistics.csv",
                "text/csv",
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
            fig = px.bar(
                plot_df,
                x="text_id",
                y=st.session_state["summary_stat_column"],
            )
            fig.update_layout(
                yaxis_title=st.session_state["summary_stat_column"],
                xaxis_title="Text ID",
                title=st.session_state["summary_stat_column"],
                xaxis_type="category",
            )
            st.plotly_chart(fig, height=450, use_container_width=True)
