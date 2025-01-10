# nlp_pipeline_frontend
This repository offers a front end for the [nlp_pipeline](https://github.com/dhopp1/nlp_pipeline) library.

## Installation
- Make sure all required Python libraries in `requirements.txt` are installed. Pay special attention to `nlp_pipeline`, including installation of non-Python packages `poppler`, `tesseract`, and `antiword`.
- clone this repository
- set the password of your application by editing the file in `.streamlit/secrets.toml`
- add users by editing the `metadata/user_list.csv` file
- run the application by navigating to the directory in your terminal, then running `streamlit run app.py`
- additional information on use of the application can be found on the README tab of the application itself