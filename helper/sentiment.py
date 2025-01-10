import os
import pandas as pd
import plotly.express as px
import streamlit as st
import sys

from helper.text_transformation import initialize_processor
from helper.progress_bar import Logger


# gen sentiment csv
def gen_sentiment():
    st.markdown("### Sentiment")
    st.markdown(
        "View the sentiment of the documents according to the [VADER](https://pypi.org/project/vaderSentiment/) sentiment analysis tool. A score of -4 is the most negative a sentence/document can be, +4 is the most positive. 0 = a neutral sentence."
    )

    if "metadata" in st.session_state:
        processor = initialize_processor()

        # run button
        st.session_state["run_sentiment_button"] = st.button(
            "Generate sentiment scores",
            help="Generate sentiment scores.",
        )

        if st.session_state["run_sentiment_button"]:
            # generate the CSV first with all text ids regardless
            with st.spinner("Generating sentiment scores..."):
                # intialize progress bar in case necessary
                old_stdout = sys.stdout
                sys.stdout = Logger(st.progress(0), st.empty())

                processor.gen_sentiment_csv(
                    text_ids=list(processor.metadata.text_id.values),
                    path_prefix="transformed",
                )
            st.info("Sentiment scores successfully generated!")

            # clear the progress bar
            try:
                sys.stdout = sys.stdout.clear()
                sys.stdout = old_stdout
            except:
                pass

        # download button
        if os.path.exists(
            f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/csv_outputs/transformed_sentiments.csv"
        ):
            st.download_button(
                "Download sentiment scores",
                pd.read_csv(
                    f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/csv_outputs/transformed_sentiments.csv",
                    encoding="latin1",
                )
                .to_csv(index=False)
                .encode("latin1"),
                "sentiment.csv",
                "text/csv",
                help="Download the sentiment scores. `avg_sentiment_w_neutral` shows the average VADER sentiment score of the document including neutral sentences. `neutral_proportion` tells the percentage of the sentences in the document that have a neutral sentiment score.",
            )

            # bar plot
            # desired column
            st.session_state["sentiment_column"] = st.selectbox(
                "Which column to plot in the sentiment bar plot",
                options=[
                    "Average sentiment without neutral sentences",
                    "Average sentiment with neutral sentences",
                    "Proportion of neutral sentences",
                ],
                index=0,
                help="",
            )
            if (
                st.session_state["sentiment_column"]
                == "Average sentiment without neutral sentences"
            ):
                col_name = "avg_sentiment_wo_neutral"
            elif (
                st.session_state["sentiment_column"]
                == "Average sentiment with neutral sentences"
            ):
                col_name = "avg_sentiment_w_neutral"
            elif (
                st.session_state["sentiment_column"]
                == "Proportion of neutral sentences"
            ):
                col_name = "neutral_proportion"

            # which metadata column to use for x axis labels
            st.session_state["sentiment_x_label"] = st.selectbox(
                "Metadata column to display on x axis",
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

            # plot data
            plot_df = (
                pd.read_csv(
                    f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/csv_outputs/transformed_sentiments.csv",
                    encoding="latin1",
                )
                .sort_values([col_name], axis=0, ascending=False)
                .reset_index(drop=True)
            )

            # if a column other than text_id is chosen for the x-axis labels
            if st.session_state["sentiment_x_label"] != "text_id":
                plot_df = plot_df.merge(
                    st.session_state["metadata"], how="left", on="text_id"
                ).loc[
                    :,
                    [
                        st.session_state["sentiment_x_label"],
                        "avg_sentiment_w_neutral",
                        "avg_sentiment_wo_neutral",
                        "neutral_proportion",
                    ],
                ]

            fig = px.bar(
                plot_df,
                x=st.session_state["sentiment_x_label"],
                y=col_name,
            )
            fig.update_layout(
                yaxis_title=st.session_state["sentiment_column"],
                xaxis_title=st.session_state["sentiment_x_label"],
                title=st.session_state["sentiment_column"],
                xaxis_type="category",
            )
            st.plotly_chart(fig, height=450, use_container_width=True)

            # sentiment of an individual string or text id
            st.markdown(
                "### Get sentence-by-sentence sentiment scores for an individual text ID or new text"
            )

            st.session_state["sentiment_string"] = st.text_input(
                "Text ID or string for full sentiment report",
                value="",
                help="Enter either a single text id to get a sentence by sentence breakdown of sentiment, or directly paste in a whole new string/text to get a sentiment report of that new text.",
            )

            # run sentiment report button
            st.session_state["run_sentiment_report_button"] = st.button(
                "Generate sentiment report",
                help="Generate sentiment scores.",
            )

            if st.session_state["run_sentiment_report_button"]:
                with st.spinner("Running sentiment report..."):
                    try:
                        stringx = int(st.session_state["sentiment_string"])
                    except:
                        stringx = st.session_state["sentiment_string"]

                    if type(stringx) == int:
                        sentiment_report = processor.gen_sentiment_report(
                            text_id=stringx
                        )
                    else:
                        sentiment_report = processor.gen_sentiment_report(
                            stringx=stringx
                        )

                    sentiment_report.to_csv(
                        f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/csv_outputs/sentiment_report.csv",
                        index=False,
                    )
                st.info("Sentiment report successfully completed!")

            if os.path.exists(
                f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/csv_outputs/sentiment_report.csv"
            ):
                st.download_button(
                    "Download sentiment report",
                    pd.read_csv(
                        f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/csv_outputs/sentiment_report.csv",
                        encoding="latin1",
                    )
                    .to_csv(index=False)
                    .encode("latin1"),
                    "sentiment_report.csv",
                    "text/csv",
                    help="Download the sentence by sentence sentiment report.",
                )

                # plot the sentiment report
                plot_df = pd.read_csv(
                    f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/csv_outputs/sentiment_report.csv",
                    encoding="latin1",
                )

                fig = px.line(
                    plot_df,
                    x="sentence_number",
                    y="sentiment",
                )
                fig.update_layout(
                    yaxis_title="Sentiment",
                    xaxis_title="Sentence number",
                    title="Sentence-by-sentence sentiment score",
                    xaxis_type="category",
                )
                st.plotly_chart(fig, height=450, use_container_width=True)
