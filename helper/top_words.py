import os
import pandas as pd
import plotly.express as px
import streamlit as st
import sys

from helper.text_transformation import initialize_processor
from helper.progress_bar import Logger


# gen word count excel
def gen_top_words():
    st.markdown("### Top words")
    st.markdown("Display the top n words in the corpus.")

    st.session_state["n_top_words"] = st.number_input(
        "Top n words",
        min_value=1,
        value=50,
        help="How many top n words to return",
    )

    st.session_state["top_words_text_ids"] = st.text_input(
        "List of text ids to consider in the count",
        value="",
        help="A comma separated list of text ids to consider in the word count. E.g., input `1,4,6` to get the top word count for only these documents. Leave blank to calculate for all documents in the corpus.",
    )

    if "metadata" in st.session_state:
        processor = initialize_processor()

        st.session_state["top_words_groups"] = st.selectbox(
            "Metadata column grouping to consider in the count",
            options=["NA"]
            + [
                x
                for x in st.session_state["metadata"].columns
                if x
                not in ["local_raw_filepath", "local_txt_filepath", "detected_language"]
            ],
            index=0,
            help="You can alternatively select a metadata column to group the top words by. Leave as `NA` to not group.",
        )

        # selection of text ids
        if st.session_state["top_words_text_ids"] == "":
            text_ids = list(processor.metadata.text_id.values)
        else:
            text_ids = eval("[" + st.session_state["top_words_text_ids"] + "]")

            # group by column

        # run button
        st.session_state["run_top_words_button"] = st.button(
            "Generate top words",
            help="Generate top words in the documents.",
        )

        if st.session_state["run_top_words_button"]:
            # generate the CSV first with all text ids regardless
            if (
                len(
                    pd.read_excel(
                        f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/transformation_parameters.xlsx",
                        sheet_name="exclude",
                    )
                )
                > 0
            ):
                exclude_words = list(
                    pd.read_excel(
                        f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/transformation_parameters.xlsx",
                        sheet_name="exclude",
                    )["term"]
                )
            else:
                exclude_words = []

            # remove an existing word count file
            if os.path.exists(
                f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/csv_outputs/transformed_word_counts.csv"
            ):
                os.remove(
                    f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/csv_outputs/transformed_word_counts.csv"
                )

            # intialize progress bar in case necessary
            old_stdout = sys.stdout
            sys.stdout = Logger(st.progress(0), st.empty())

            processor.gen_word_count_csv(
                text_ids=list(processor.metadata.text_id.values),
                path_prefix="transformed",
                exclude_words=exclude_words,
            )

            # generate the CSV
            # no grouping
            if st.session_state["top_words_groups"] == "NA":
                p, df = processor.bar_plot_word_count(
                    text_ids=text_ids,
                    path_prefix="transformed",
                    n_words=st.session_state["n_top_words"],
                    title="",
                )
            # grouping
            else:
                groups = list(
                    st.session_state["metadata"][
                        st.session_state["top_words_groups"]
                    ].unique()
                )
                for group in groups:
                    tmp_ids = list(
                        st.session_state["metadata"].loc[
                            lambda x: x[st.session_state["top_words_groups"]] == group,
                            "text_id",
                        ]
                    )
                    p, tmp_df = processor.bar_plot_word_count(
                        text_ids=tmp_ids,
                        path_prefix="transformed",
                        n_words=st.session_state["n_top_words"],
                        title="",
                    )
                    tmp_df[st.session_state["top_words_groups"]] = group
                    tmp_df = tmp_df.loc[
                        :,
                        [st.session_state["top_words_groups"]]
                        + [
                            x
                            for x in tmp_df.columns
                            if x != st.session_state["top_words_groups"]
                        ],
                    ]
                    if group == groups[0]:
                        df = tmp_df.copy()
                    else:
                        df = pd.concat([df, tmp_df], ignore_index=True)

            st.info("Top words successfully calculated!")

            # clear the progress bar
            try:
                sys.stdout = sys.stdout.clear()
                sys.stdout = old_stdout
            except:
                pass

            df.to_csv(
                f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/csv_outputs/top_words.csv",
                index=False,
            )

        if os.path.exists(
            f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/csv_outputs/top_words.csv"
        ):
            pd.read_csv(
                f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/csv_outputs/top_words.csv"
            ).to_excel(
                f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/csv_outputs/top_words.xlsx",
                index=False,
            )

            # download button
            with open(
                f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/csv_outputs/top_words.xlsx",
                "rb",
            ) as template_file:
                template_byte = template_file.read()

            st.download_button(
                "Download top words",
                template_byte,
                "top_words.xlsx",
                "application/octet-stream",
                help="Download the top words.",
            )

            # bar plot(s)
            plot_df = pd.read_csv(
                f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/csv_outputs/top_words.csv",
                encoding="latin1",
            )
            fig = px.bar(
                plot_df,
                x="word",
                y="count",
                color=plot_df.columns[0] if len(plot_df.columns) > 2 else None,
            )
            fig.update_layout(
                yaxis_title="Count",
                xaxis_title="",
                title=f"Top {st.session_state['n_top_words']} words",
            )
            st.plotly_chart(fig, height=450, use_container_width=True)

            if st.session_state["top_words_groups"] == "NA":
                st.markdown("### Word cloud")
                # wordcloud
                p, plot_df = processor.word_cloud(
                    text_ids=text_ids,
                    path_prefix="transformed",
                    n_words=st.session_state["n_top_words"],
                )

                st.pyplot(p)
            else:
                st.error(
                    "A word cloud can only be viewed if `Metadata column grouping to consider in the count` is set to `NA`."
                )
