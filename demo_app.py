import os
import streamlit as st
from openai import OpenAI
from utils import (
    delete_files,
    delete_thread,
    EventHandler,
    moderation_endpoint,
    is_nsfw,
    render_custom_css,
    render_download_files,
    retrieve_messages_from_thread,
    retrieve_assistant_created_files
)

# Initialise the OpenAI client and retrieve the assistant
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
assistant = client.beta.assistants.retrieve(
  assistant_id=st.secrets["ASSISTANT_ID"],
  tool_resources={"file_search": {"vector_store_ids":st.secrets["FILE_ID"]}},
)

st.set_page_config(page_title="jiny", page_icon="🧐")

# Apply custom CSS
render_custom_css()

# Initialise session state variables
if "file_uploaded" not in st.session_state:
    st.session_state.file_uploaded = False

if "assistant_text" not in st.session_state:
    st.session_state.assistant_text = [""]

if "code_input" not in st.session_state:
    st.session_state.code_input = []

if "code_output" not in st.session_state:
    st.session_state.code_output = []

if "disabled" not in st.session_state:
    st.session_state.disabled = False

# UI
st.subheader("📖 jiny: Paper Study Engine")
st.markdown("This demo studied 20 papers of PFAS")
text_box = st.empty()
qn_btn = st.empty()

question = text_box.text_area("Ask a question", disabled=st.session_state.disabled)
if qn_btn.button("Ask jiny"):

    text_box.empty()
    qn_btn.empty()

    if moderation_endpoint(question):
        st.warning("Your question has been flagged. Refresh page to try again.")
        st.stop()

    # Create a new thread if not already created
    if "thread_id" not in st.session_state:
        thread = client.beta.threads.create()
        st.session_state.thread_id = thread.id
        print(st.session_state.thread_id)

    # Update the thread to attach the file
    client.beta.threads.update(
        thread_id=st.session_state.thread_id,
        tool_resources={"file_search": {"file_ids": [st.secrets["FILE_ID"]]}}
    )

    if "text_boxes" not in st.session_state:
        st.session_state.text_boxes = []

    client.beta.threads.messages.create(
        thread_id=st.session_state.thread_id,
        role="user",
        content=question
    )

    st.session_state.text_boxes.append(st.empty())
    st.session_state.text_boxes[-1].success(f"**> 🤔 User:** {question}")

    with client.beta.threads.runs.stream(
        thread_id=st.session_state.thread_id,
        assistant_id=assistant.id,
        tool_choice={"type": "file_search"},
        event_handler=EventHandler(),
        temperature=0
    ) as stream:
        stream.until_done()
        st.toast("jiny has finished searching the data", icon="🕵")

    # Prepare the files for download
    with st.spinner("Preparing the files for download..."):
        # Retrieve the messages by the Assistant from the thread
        assistant_messages = retrieve_messages_from_thread(st.session_state.thread_id)
        # For each assistant message, retrieve the file(s) created by the Assistant
        st.session_state.assistant_created_file_ids = retrieve_assistant_created_files(assistant_messages)
        # Download these files
        st.session_state.download_files, st.session_state.download_file_names = render_download_files(st.session_state.assistant_created_file_ids)

    # Clean-up
    # Delete the file(s) created by the Assistant
    delete_files(st.session_state.assistant_created_file_ids)
    # Delete the thread
    delete_thread(st.session_state.thread_id)
