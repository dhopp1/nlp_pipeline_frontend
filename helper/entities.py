import os
import pandas as pd
import plotly.express as px
import streamlit as st
import sys

from helper.text_transformation import initialize_processor
from helper.progress_bar import Logger


# gen entity count csv
def gen_entities():
    st.markdown("### Top entities")
    st.markdown("Display the top n entities in the corpus.")

    st.session_state["n_top_entities"] = st.number_input(
        "Top n entities",
        min_value=1,
        value=50,
        help="How many top n entities to return",
    )

    st.session_state["top_entities_text_ids"] = st.text_input(
        "List of text ids to consider in the count",
        value="",
        help="A comma separated list of text ids to consider in the entity count. E.g., input `1,4,6` to get the top entity count for only these documents. Leave blank to calculate for all documents in the corpus.",
    )

    if "metadata" in st.session_state:
        with st.spinner("Loading corpus..."):
            processor = initialize_processor()

        st.session_state["top_entities_groups"] = st.selectbox(
            "Metadata column grouping to consider in the count",
            options=["NA"]
            + [
                x
                for x in st.session_state["metadata"].columns
                if x
                not in ["local_raw_filepath", "local_txt_filepath", "detected_language"]
            ],
            index=0,
            help="You can alternatively select a metadata column to group the top entities by. Leave as `NA` to not group.",
        )

        # selection of text ids
        if st.session_state["top_entities_text_ids"] == "":
            text_ids = list(processor.metadata.text_id.values)
        else:
            text_ids = eval("[" + st.session_state["top_entities_text_ids"] + "]")

            # group by column

        # run button
        st.session_state["run_top_entities_button"] = st.button(
            "Generate top entities",
            help="Generate top entities in the documents.",
        )

        if st.session_state["run_top_entities_button"]:
            # generate the CSV first with all text ids regardless
            with st.spinner("Calculating entities..."):
                # intialize progress bar in case necessary
                old_stdout = sys.stdout
                sys.stdout = Logger(st.progress(0), st.empty())

                # remove an existing word count file
                if os.path.exists(
                    f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/csv_outputs/transformed_entity_counts.csv"
                ):
                    os.remove(
                        f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/csv_outputs/transformed_entity_counts.csv"
                    )

                processor.gen_entity_count_csv(
                    text_ids=list(processor.metadata.text_id.values),
                )

            # generate the CSV
            # no grouping
            if st.session_state["top_entities_groups"] == "NA":
                p, df = processor.bar_plot_word_count(
                    text_ids=text_ids,
                    path_prefix="entity",
                    n_words=st.session_state["n_top_entities"],
                    title="",
                )
            # grouping
            else:
                groups = list(
                    st.session_state["metadata"][
                        st.session_state["top_entities_groups"]
                    ].unique()
                )
                for group in groups:
                    tmp_ids = list(
                        st.session_state["metadata"].loc[
                            lambda x: x[st.session_state["top_entities_groups"]]
                            == group,
                            "text_id",
                        ]
                    )
                    p, tmp_df = processor.bar_plot_word_count(
                        text_ids=tmp_ids,
                        path_prefix="entity",
                        n_words=st.session_state["n_top_entities"],
                        title="",
                    )
                    tmp_df[st.session_state["top_entities_groups"]] = group
                    tmp_df = tmp_df.loc[
                        :,
                        [st.session_state["top_entities_groups"]]
                        + [
                            x
                            for x in tmp_df.columns
                            if x != st.session_state["top_entities_groups"]
                        ],
                    ]
                    if group == groups[0]:
                        df = tmp_df.copy()
                    else:
                        df = pd.concat([df, tmp_df], ignore_index=True)

            st.info("Top entities successfully calculated!")

            # clear the progress bar
            try:
                sys.stdout = sys.stdout.clear()
                sys.stdout = old_stdout
            except:
                pass

            df.to_csv(
                f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/csv_outputs/top_entities.csv",
                index=False,
            )

        if os.path.exists(
            f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/csv_outputs/top_entities.csv"
        ):
            pd.read_csv(
                f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/csv_outputs/top_entities.csv"
            ).to_excel(
                f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/csv_outputs/top_entities.xlsx",
                index=False,
            )

            # download button
            with open(
                f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/csv_outputs/top_entities.xlsx",
                "rb",
            ) as template_file:
                template_byte = template_file.read()

            st.download_button(
                "Download top entities",
                template_byte,
                "top_entities.xlsx",
                "application/octet-stream",
                help="Download the top entities.",
            )

            # bar plot(s)
            plot_df = pd.read_csv(
                f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/csv_outputs/top_entities.csv",
                encoding="latin1",
            )
            # plot_df["word"] = plot_df["word"].astype(str)
            fig = px.bar(
                plot_df,
                x="word",
                y="count",
                color=plot_df.columns[0] if len(plot_df.columns) > 2 else None,
            )
            fig.update_layout(
                yaxis_title="Count",
                xaxis_title="",
                title=f"Top {st.session_state['n_top_entities']} entities",
                xaxis_type="category",
            )
            st.plotly_chart(fig, height=450, use_container_width=True)
