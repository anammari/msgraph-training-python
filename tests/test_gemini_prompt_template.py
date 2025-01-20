import os
import json
import requests
import google.generativeai as genai
from llama_index.core.base.llms.types import ChatMessage, MessageRole
from llama_index.core.prompts.base import ChatPromptTemplate
from llama_index.core import Settings
from llama_index.llms.gemini import Gemini
from dotenv import load_dotenv, find_dotenv

# Load environment variables
_ = load_dotenv(find_dotenv())  # read local .env file

# Suppress logging warnings
os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GLOG_minloglevel"] = "2"

# Ensure the API key is set correctly
GOOGLE_API_KEY = os.getenv('GEMINI_API_KEY')
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
os.environ["GEMINI_API_KEY"] = GOOGLE_API_KEY

# Initialize the Gemini model
Settings.llm = Gemini(model='models/gemini-2.0-flash-exp')

# text qa prompt
TEXT_QA_SYSTEM_PROMPT = ChatMessage(
    content=(
        "You are an expert Q&A system that is trusted around the world.\n"
        "Always answer the query using the provided context information, "
        "and not prior knowledge.\n"
        "Some rules to follow:\n"
        "1. Never directly reference the given context in your answer.\n"
        "2. Avoid statements like 'Based on the context, ...' or "
        "'The context information ...' or anything along "
        "those lines."
    ),
    role=MessageRole.SYSTEM,
)

TEXT_QA_PROMPT_TMPL_MSGS = [
    TEXT_QA_SYSTEM_PROMPT,
    ChatMessage(
        content=(
            "Context information is below.\n"
            "---------------------\n"
            "{context_str}\n"
            "---------------------\n"
            "Given the context information and not prior knowledge, "
            "answer the query.\n"
            "Query: {query_str}\n"
            "Answer: "
        ),
        role=MessageRole.USER,
    ),
]

CHAT_TEXT_QA_PROMPT = ChatPromptTemplate(message_templates=TEXT_QA_PROMPT_TMPL_MSGS)

# Define the base URL for the Flask REST API
BASE_URL = "http://127.0.0.1:5000"

def list_inbox():
    url = f"{BASE_URL}/interact"
    payload = {"option": 2}
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to list inbox: {response.status_code} - {response.text}")

result = list_inbox()

full_text = CHAT_TEXT_QA_PROMPT.format(context_str=json.dumps(result), query_str="What are the subjects of my received emails?")

def chat():
    resp = Settings.llm.complete(full_text)
    print(resp)

if __name__ == "__main__":
    chat()

