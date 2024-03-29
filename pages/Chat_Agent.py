import os
import streamlit as st
from lyzr import ChatBot
from json import JSONDecodeError
import streamlit_analytics
import tempfile
import time
import re

# This is the path to the json file where you want to save the analytics
analytics_filepath = "analytics.json"

# start tracking analytics
try:
    print("Loading analytics from json file.")
    streamlit_analytics.start_tracking(load_from_json=analytics_filepath)
except (JSONDecodeError, FileNotFoundError):
    print("No analytics json file found. Starting new analytics.")
    streamlit_analytics.start_tracking()

st.set_page_config(
    page_title="ChatAgent",
    page_icon="🎤",
)
st.sidebar.title("Chat Agent")
st.image("lyzr-logo-oneColor-rgb-600-cropped.png", width=180)
st.title("Welcome to the Chat Agent")
with st.sidebar:
    openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
    "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"

st.sidebar.markdown(
    """<style>
    p .external-link {
        font-weight: bold;
        text-decoration: none;
        color: rgb(49, 51, 63);
    }
    p .external-link:after {
        content: "";
        background-image: url('https://www.svgrepo.com/show/374989/new-window.svg') !important;
        background-repeat: no-repeat;
        background-size: 12px;
        display: inline-block;
        width: 1em;
        height: 1em;
        margin-left: 3px;
    }
    </style>""",
    unsafe_allow_html=True,
)
st.sidebar.markdown(
    """
    <div style="bottom: 10px; position: fixed;">
    <p style='margin-bottom: 5px;'>
    <a class='external-link' href='https://lyzr.ai' target='_blank' rel='noopener noreferrer'>Homepage</a>
    </p>
    <p style='margin-bottom: 5px;'>
    <a class='external-link' href='https://docs.lyzr.ai' target='_blank' rel='noopener noreferrer'>Documentation</a>
    </p>
    <p style='margin-bottom: 5px;'>
    <a class='external-link' href='https://discord.gg/P6HCMQ9TRX' target='_blank' rel='noopener noreferrer'>Discord</a>
    </p>
    <p style='margin-bottom: 5px;'>
    <a class='external-link' href='https://join.slack.com/t/genaiforenterprise/shared_invite/zt-2a7fr38f7-_QDOY1W1WSlSiYNAEncLGw' target='_blank' rel='noopener noreferrer'>Slack</a>
    </p>
    </div>
    """,
    unsafe_allow_html=True,
)

def is_valid_api_key(api_key):
    """Check if the API key is valid. A valid API key in our case is a non-empty string of a certain length
    that consists of alphanumeric characters, optionally including hyphens and underscores."""
    return bool(re.match(r'^[a-zA-Z0-9\-_]{32,64}$', api_key))

def display_chat_interface():
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if "chatbot" in st.session_state:
        if prompt := st.chat_input("What is up?"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                response = st.session_state["chatbot"].chat(prompt)
                chat_response = response.response
                response = st.write(chat_response)
                st.session_state.messages.append(
                    {"role": "assistant", "content": chat_response}
            )
    else:
        st.warning("Please upload PDF files to continue.")

def pdf():
    uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

    if uploaded_file:
        # Reset chat history if new files are uploaded
        st.session_state.messages = []

        # Save the uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
            tmpfile.write(uploaded_file.getvalue())
            pdf_file_path = tmpfile.name

        # Use the single PDF file path for ChatBot processing
        unique_index_name = f"IndexName_{int(time.time())}"
        vector_store_params = {"index_name": unique_index_name}
        st.session_state["chatbot"] = ChatBot.pdf_chat(
            input_files=[pdf_file_path], vector_store_params=vector_store_params
        )

        # Inform the user that the file has been uploaded and processed
        st.success("PDF uploaded and processed. You can now interact with the chatbot.")

    display_chat_interface()
#Check if OpenAI API key is valid
if openai_api_key:
    if is_valid_api_key(openai_api_key):
        os.environ['OPENAI_API_KEY'] = openai_api_key
    else:
        st.warning("Please enter the correct API key.")
        st.stop()
elif openai_api_key is None or openai_api_key == "":
    st.info("Please add your OpenAI API key to continue.")
    st.stop()
else:
    st.warning("Invalid API key format!")
    st.stop()


pdf()

# stop tracking analytics and save to json file
# IMPORTANT: You must add an environment variable ANALYTICS_PASSWORD to ~/.streamlit/secrets.toml
streamlit_analytics.stop_tracking(
    save_to_json=analytics_filepath, unsafe_password=os.environ["ANALYTICS_PASSWORD"]
)
