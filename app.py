import os
import pandas as pd
import streamlit as st

from helper.text_setup import engage_process_corpus
from helper.ui import (
    import_styles,
    ui_delete_corpus,
    ui_download_txt_zip,
    ui_header,
    ui_load_corpus,
    ui_metadata_upload,
    ui_tab,
)
from helper.user_management import check_password, set_user_id, validate_corpora
from helper.text_transformation import text_transformation_inputs
from helper.search_terms import search_terms_inputs
from helper.entities import gen_entities
from helper.top_words import gen_top_words
from helper.sentiment import gen_sentiment
from helper.summary_statistics import gen_summary_statistics
from helper.similarity import gen_similarity

### page setup and authentication
ui_tab()  # icon and page title
ui_header()  # header

if not check_password():
    st.stop()

set_user_id()


### initialization
import_styles()


### clear out partial corpora
validate_corpora()


### sidebar
ui_metadata_upload()
engage_process_corpus()  # convert to text


# corpus name
ui_load_corpus()

# download raw text file button
ui_download_txt_zip()

# delete corpus button
ui_delete_corpus()

st.sidebar.markdown(
    """*For questions on how to use this application or its methodology, please write [Daniel Hopp](mailto:daniel.hopp@un.org)*""",
    unsafe_allow_html=True,
)


### tabs
tab_names = [
    "README",
    "Corpus metadata",
    "Text transformation",
    "Search terms",
    "Top words",
    "Top entities",
    "Sentiment",
    "Summary statistics",
    "Text similarity",
]

tabs = st.tabs(tab_names)

# README
with tabs[tab_names.index("README")]:
    st.markdown(
        """
### What is this tool?
"NLP" stands for "natural language processing". This tool allows you to analyze large corpora of written and spoken natural language to gain various data insights. This README will walk you through the basics of the tool's use, but there are additional tooltips for most elements. Hover over the small question marks in circles to get more information about a specific element. For any questions on how to use the tool, please contact [Daniel Hopp](mailto:daniel.hopp@un.org).

### Loading a corpus
To load a new corpus into the system for analysis, uncollapse the `Options` dropdown under the `Upload your metadata file or documents`. Upload either your zip file of documents or metadata file with URL links to the documents. If using links to e.g., PDFs, make sure the link is to the actual PDF itself, not a landing page. The system can handle the following formats for documents: `DOCX`, `DOC`, `TXT`, `PDF`, `MP3`, `MP4`. View the tooltip next to the upload box for more information on how to format your document upload.

Once the corpus is uploaded, choose a name for this corpus in the `Uploaded corpus name` text field. Note that if you choose a name that you have already used before, the corpus will be overwritten. Then hit the `Convert to text` button. This will convert the documents to raw text.

If you come back to the site having already uploaded a corpus before, you can load that corpus by selecting its name from the `Corpus name` dropdown on the sidebar. You can additionally click `Download documents converted to text` to get a .zip file of the corpus in raw text.

The next sections will explain each tab of the application in more detail.

### Corpus metadata
This table shows the documents alongside any additional metadata you've chosen to include. The `text_id` column is extremely important, it is the unique identifier for each document in the corpus. You can download this file for reference.

### Text transformation
Before you begin analyzing the corpus, you have the ability to perform various transformations on it first.

- `Replace prepunctuation`: you can specify terms you want to replace in the text that include punctuation. Do so in the `prepunctuation` tab of the `transformation_parameters.xlsx` file. For instance, you may want to replace "COVID-19" with "covid". The reason there is a prepunctuation adn postpunctuation replacement is that one of the subsequent transformations you can perform replaces punctuation with space. So "COVID-19" would be replaced with "COVID 19" and would no longer be considered one word.
- `Replace postpunctuation`: you can specify terms you want to replace in the text. Do so in the `postpunctuation` tab of the `transformation_parameters.xlsx` file. For instance, you could replace "the US" and "United States of America" with "usa". The replacement will occur after the option to `Perform lowercase` found in the `Other text transformation options` section, so if you choose that option, you can limit your replacement list to lower case only terms.
- `Exclude terms`: you can specify terms to exclude/remove common terms from the text, such as "good morning", etc., in case you don't want to count them in e.g., most common words. Do so in the `exclude` tab of the `transformation_parameters.xlsx` file.
- `Perform lowercase`: whether or not to convert all the documents to lower case.
- `Replace accented and unusual characters`: whether or not to replace accented characters with unaccented versions of them. E.g., "ä" will be replaced with "a".
- `Remove URLs`: whether or not to remove URLs from the text.
- `Remove headers and footers`: whether or not to remove repeated headers and footers from the text. For instance, if the document has a header on every page with "United Nations report on X", this will remove it from all but the very first page.
- `Replace periods`: this will replace full stops (".") with "|" for a consistent phrase ending character.
- `Remove numbers`: this will remove any numerals from the text.
- `Remove punctuation`: this will replace any punctuation in the text with spaces.
- `Remove stopwords`: this will remove common words from the text, such as "and", "with", etc.
- `Perform stemming`: this will convert words to their root. E.g., 'running', 'runs', 'ran' would all be converted to 'run'.

Once `transformation_parameters.xlsx` has been uploaded and transformations have been selected, click the `Transform text` button to perform the transformation. You can download the transformed text documents with the `Download transformed text documents` button for validation.

### Search terms
This section enable the searching of specific terms within the corpus, as well as returning the contexts where they appear. Upload the `search_terms.xlsx` file containing the desired search terms on the `search_terms` sheet. The sheet can have multiple columns for grouping the search terms, but only the rightmost columns' contents will be searched for.

Under `Search parameters`, `Length of character buffer` tells the number of characters in either direction of the found term to return as context of the term. `Co-occurring n words limit` stipulates how many top co-occurring words to return. E.g., if "trade" is the search term, a value of 50 here will let you see the top 50 words that occur in the contexts that contain the term "trade".

The `second_level_search_terms` sheet of the `search_terms.xlsx` file allows you to search for terms within the contexts of existing search terms. For instance, if you previously searched for "trade", you could then search for "tariff" and see how many times the word "tariff" occurs in the context where "trade" is mentioned.

Once the `search_terms.xlsx` file has been uploaded, click the `Execute search` button to perform the search. From the `Outputs` section, you can download the contexts of all the found search terms, the number of found terms, and the count of co-occurring words.

In the `Individual search term` section you can perform and visualize the results of searching for a single term. Enter the term in the `Search term` field, then hit `Execute individual term search` to perform the search. You can group the results by a column in the metadata.

### Top words
Here, you can see the top occurring words in the corpus.

- `Top n words`: how many top words to display.
- `List of text ids to consider in the count`: a comma-separated list of text ids to consider when calculating the top occurring words. E.g., if you want to only consider some documents, you can enter `1,4,6` in this field.
- `Metadata column groupiong to consider in teh count`: you can also select a metadata column to gropu the results by. Say `year` is a column in the metadata, you could view the top words for all documents from e.g., 2024 and 2023.
- `Generate top words`: push this button to run the calculation.
- `Download top words`: push this button to download the Excel file with the results.

Once you click `Generate top words`, you will see a bar plot and word cloud of the most commonly occurring words.

### Top entities
This section is the same as the top words section, but searchs for entities rather than words. Entities include things like geographic locations, cardinal numbers, organizations, etc.

### Sentiment
This section enables you to use the [VADER](https://pypi.org/project/vaderSentiment/) sentiment analysis tool. A phrase or sentence can have a score from -4 (most negative) to +4 (most positive). A score of 0 is a neutral sentence. The score for an individual document is calculated as the average of this number for all the sentences in the document. The sentiment scores generated here should be taken with a grain of salt, as the VADER algorithm is not perfect and you may find sentences whose sentiment scores you do not agree with.

- `Generate sentiment scores`: push this button to generate the sentiment scores. Depending on the length and number of your documents, this step can take a while.
- `Download sentiment scores`: push this button to download the sentiment score results. `avg_sentiment_w_neutral` shows the average sentiment of each document including neutral sentences.	`avg_sentiment_wo_neutral` shows the average sentiment excluding neutral sentences. `neutral_proportion` shows the proportion of the document that is neutral.
- `Which column to plot in the sentiment bar analysis`: select which of the three columns to display in the bar plot.
- `Metadata column to display on x axis`: which column from the metadata file to display on the x axis of the bar plot.

You can get a sentence by sentence breakdown of the sentiment for a particular text id or of an entirely new string/text pasted directly into the `Text ID or string for full sentiment report` field.

### Summary statistics
This section generates various summary statistics about the documents. Options are the same as on the `Sentiment` tab, and statistics generated are explained on the tab.

### Text similarity
This section calculates the similarity between the documents using the [TF-IDF](https://en.wikipedia.org/wiki/Tf%E2%80%93idf) algorithm. You can select which text ids to consider in the analysis and which metadata column to display on the axes and cluster plot.

The heat map shows a similarity matrix between every document. The cluster plot condenses the similarity matrix to two dimensions then plots them, letting you see visually how close or far different documents are to each other.
"""
    )

# metadata
with tabs[tab_names.index("Corpus metadata")]:
    if os.path.exists(
        f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/metadata.xlsx"
    ):
        if "metadata" not in st.session_state:
            st.session_state["metadata"] = pd.read_excel(
                f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/metadata.xlsx"
            )

        with open(
            f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/metadata_clean.xlsx",
            "rb",
        ) as template_file:
            template_byte = template_file.read()

        st.download_button(
            "Download metadata",
            template_byte,
            "metadata.xlsx",
            "application/octet-stream",
            help="Download metadata file.",
        )

        st.dataframe(
            pd.read_excel(
                f"corpora/{st.session_state['user_id']}_{st.session_state['selected_corpus']}/metadata_clean.xlsx"
            ),
            hide_index=True,
            height=800,
        )
    else:
        st.error(
            "Upload your metadata file or corpus under the `Options` dropdown on the sidebar, then hit `Convert to text`. If you have already processed a corpus, select its name under the `Corpus name` dropdown on the sidebar."
        )

# text transformation
with tabs[tab_names.index("Text transformation")]:
    text_transformation_inputs()

# search terms
with tabs[tab_names.index("Search terms")]:
    search_terms_inputs()

# word counts
with tabs[tab_names.index("Top words")]:
    gen_top_words()

# entity counts
with tabs[tab_names.index("Top entities")]:
    gen_entities()


# sentiment
with tabs[tab_names.index("Sentiment")]:
    gen_sentiment()

# summary statistics
with tabs[tab_names.index("Summary statistics")]:
    gen_summary_statistics()

# text similarity
with tabs[tab_names.index("Text similarity")]:
    gen_similarity()
