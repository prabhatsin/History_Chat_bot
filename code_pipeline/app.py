import streamlit as st
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))  # NEW - if app.py is inside code_pipeline
from code_pipeline.query import load_model, load_collection, load_gemini, get_rag_response

st.set_page_config(page_title="History ChatBot", page_icon="🧠", layout="centered")
st.title("🧠 History ChatBot")
st.caption("Ask anything about your browsing history")

@st.cache_resource
def get_model():
    return load_model()

@st.cache_resource
def get_collection():
    return load_collection()

@st.cache_resource
def get_gemini():
    return load_gemini()

# CHANGED - load once, removed duplicate calls
with st.spinner("Loading models..."):
    model      = get_model()
    collection = get_collection()
    gemini     = get_gemini()

# REMOVED - the time tracking and second set of get_model/get_collection/get_gemini calls
# They were duplicates — @st.cache_resource already handles caching

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

query = st.chat_input("Ask about your browsing history...")

if query:
    with st.chat_message("user"):
        st.write(query)
    st.session_state.messages.append({"role": "user", "content": query})

    with st.chat_message("assistant"):
        response_text = st.write_stream(get_rag_response(query, model, collection, gemini))

    st.session_state.messages.append({"role": "assistant", "content": response_text})