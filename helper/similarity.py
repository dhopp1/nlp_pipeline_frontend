import os
import pandas as pd
import pickle
import plotly.express as px
import streamlit as st

from helper.text_transformation import initialize_processor


# gen entity count csv
def gen_similarity():
    st.markdown("### Text similarity")
    st.markdown(
        "Display the similarity between documents according to the [TF-IDF](https://en.wikipedia.org/wiki/Tf%E2%80%93idf) measure."
    )

    # which text_ids
    st.session_state["similarity_text_ids"] = st.text_input(
        "List of text ids to consider in for text similarity",
        value="",
        help="A comma separated list of text ids to consider in the word count. E.g., input `1,4,6` to get similarity for only these documents. Leave blank to calculate for all documents in the corpus.",
    )

    if "metadata" in st.session_state:
        processor = initialize_processor()

        if st.session_state["similarity_text_ids"] == "":
            text_ids = list(processor.metadata.text_id.values)
        else:
            text_ids = eval("[" + st.session_state["similarity_text_ids"] + "]")

        # which metadata column to use for x axis labels
        st.session_state["similarity_label"] = st.selectbox(
            "Metadata column to display on x and y axes",
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
            help="Select which metadata column you want to use for labelling the axes.",
        )

        # run button
        st.session_state["run_text_similarity_button"] = st.button(
            "Generate generate text similarity",
            help="Generate text similarity.",
        )

        # generate data
        if st.session_state["run_text_similarity_button"]:
            with st.spinner("Generating text similarity data..."):
                p, plot_df, xaxis_labels = processor.plot_text_similarity(
                    text_ids, label_column=st.session_state["similarity_label"]
                )

                # pickle the plot
                with open(
                    f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/csv_outputs/similarity_heatmap.pkl",
                    "wb",
                ) as f:
                    pickle.dump(p, f)

                # edit column names if different metadata column selected
                plot_df.columns = list(
                    st.session_state["metadata"][
                        st.session_state["similarity_label"]
                    ].values
                )
                plot_df[st.session_state["similarity_label"]] = list(
                    st.session_state["metadata"][
                        st.session_state["similarity_label"]
                    ].values
                )
                plot_df = plot_df.loc[
                    :,
                    [st.session_state["similarity_label"]]
                    + [
                        x
                        for x in plot_df.columns
                        if x != st.session_state["similarity_label"]
                    ],
                ]
                plot_df.to_csv(
                    f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/csv_outputs/text_similarity.csv",
                    index=False,
                )
            st.info("Text similarity data succcessfully generated!")

        if os.path.exists(
            f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/csv_outputs/text_similarity.csv"
        ):

            st.download_button(
                "Download text similarity data",
                pd.read_csv(
                    f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/csv_outputs/text_similarity.csv",
                    encoding="latin1",
                )
                .to_csv(index=False)
                .encode("latin1"),
                "text_similarity.csv",
                "text/csv",
                help="Download text similarity data.",
            )

            # display heatmap
            if os.path.exists(
                f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/csv_outputs/similarity_heatmap.pkl"
            ):
                st.markdown("### Heat map of similarity between text")
                st.markdown(
                    "Each grid is the comparision between two documents. A value close to 1 means the documents are very similar, a value of 0 means they are completely different."
                )
                with open(
                    f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/csv_outputs/similarity_heatmap.pkl",
                    "rb",
                ) as f:
                    p = pickle.load(f)
                st.pyplot(p)
