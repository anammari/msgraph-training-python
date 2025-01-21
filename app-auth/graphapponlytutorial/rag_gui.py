# rag_gui.py
import streamlit as st
import json
import requests
from google import genai
from google.genai import types
from llama_index.core.base.llms.types import ChatMessage, MessageRole
from llama_index.core.prompts.base import ChatPromptTemplate
from llama_index.core import Settings
from llama_index.llms.gemini import Gemini
from dotenv import load_dotenv, find_dotenv
import os

# Load environment variables
_ = load_dotenv(find_dotenv())  # read local .env file

# Suppress logging warnings
os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GLOG_minloglevel"] = "2"

# Ensure the API key is set correctly
GOOGLE_API_KEY = os.getenv('GEMINI_API_KEY')
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
os.environ["GEMINI_API_KEY"] = GOOGLE_API_KEY

# Create a client
client = genai.Client(api_key=os.environ['GEMINI_API_KEY'])

# Initialize the Gemini models
gemini_1_5_flash = 'gemini-1.5-flash-8b'
Settings.llm = Gemini(model='models/gemini-2.0-flash-exp')

# Define the base URL for the Flask REST API
BASE_URL = "http://127.0.0.1:5000"

# Define the function declarations for the REST API interactions
display_access_token_declaration = types.FunctionDeclaration(
    name="display_access_token",
    description="Display the access token for the Microsoft Graph API",
    parameters={
        "type": "OBJECT",
        "properties": {
            "dummy": {
                "type": "STRING",
                "description": "Dummy parameter to satisfy the API requirements",
            },
        },
        "required": [],
    },
)

list_inbox_declaration = types.FunctionDeclaration(
    name="list_inbox",
    description="List the emails in the inbox",
    parameters={
        "type": "OBJECT",
        "properties": {
            "dummy": {
                "type": "STRING",
                "description": "Dummy parameter to satisfy the API requirements",
            },
        },
        "required": [],
    },
)

send_mail_declaration = types.FunctionDeclaration(
    name="send_mail",
    description="Send an email to the signed-in user",
    parameters={
        "type": "OBJECT",
        "properties": {
            "dummy": {
                "type": "STRING",
                "description": "Dummy parameter to satisfy the API requirements",
            },
        },
        "required": [],
    },
)

extract_email_metadata_declaration = types.FunctionDeclaration(
    name="extract_email_metadata",
    description="Extract metadata from emails",
    parameters={
        "type": "OBJECT",
        "properties": {
            "dummy": {
                "type": "STRING",
                "description": "Dummy parameter to satisfy the API requirements",
            },
        },
        "required": [],
    },
)

extract_calendar_events_declaration = types.FunctionDeclaration(
    name="extract_calendar_events",
    description="Extract calendar events",
    parameters={
        "type": "OBJECT",
        "properties": {
            "dummy": {
                "type": "STRING",
                "description": "Dummy parameter to satisfy the API requirements",
            },
        },
        "required": [],
    },
)

extract_contacts_declaration = types.FunctionDeclaration(
    name="extract_contacts",
    description="Extract contacts and network information",
    parameters={
        "type": "OBJECT",
        "properties": {
            "dummy": {
                "type": "STRING",
                "description": "Dummy parameter to satisfy the API requirements",
            },
        },
        "required": [],
    },
)

extract_sharepoint_usage_declaration = types.FunctionDeclaration(
    name="extract_sharepoint_usage",
    description="Extract SharePoint usage information",
    parameters={
        "type": "OBJECT",
        "properties": {
            "search_term": {
                "type": "STRING",
                "description": "Search term to filter SharePoint sites",
            },
        },
        "required": ["search_term"],
    },
)

# Define the tool
api_tool = types.Tool(
    function_declarations=[
        display_access_token_declaration,
        list_inbox_declaration,
        send_mail_declaration,
        extract_email_metadata_declaration,
        extract_calendar_events_declaration,
        extract_contacts_declaration,
        extract_sharepoint_usage_declaration,
    ],
)

# Define the functions to interact with the REST API
def display_access_token():
    url = f"{BASE_URL}/interact"
    payload = {"option": 1}
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to display access token: {response.status_code} - {response.text}")

def list_inbox():
    url = f"{BASE_URL}/interact"
    payload = {"option": 2}
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to list inbox: {response.status_code} - {response.text}")

def send_mail():
    url = f"{BASE_URL}/interact"
    payload = {"option": 3}
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to send mail: {response.status_code} - {response.text}")

def extract_email_metadata():
    url = f"{BASE_URL}/interact"
    payload = {"option": 4}
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to extract email metadata: {response.status_code} - {response.text}")

def extract_calendar_events():
    url = f"{BASE_URL}/interact"
    payload = {"option": 5}
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to extract calendar events: {response.status_code} - {response.text}")

def extract_contacts():
    url = f"{BASE_URL}/interact"
    payload = {"option": 6}
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to extract contacts: {response.status_code} - {response.text}")

def extract_sharepoint_usage(search_term):
    url = f"{BASE_URL}/interact"
    payload = {"option": 7, "search_term": search_term}
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to extract SharePoint usage: {response.status_code} - {response.text}")

# Define the functions dictionary
functions = {
    "display_access_token": display_access_token,
    "list_inbox": list_inbox,
    "send_mail": send_mail,
    "extract_email_metadata": extract_email_metadata,
    "extract_calendar_events": extract_calendar_events,
    "extract_contacts": extract_contacts,
    "extract_sharepoint_usage": extract_sharepoint_usage,
}

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

def determine_function_call(prompt):
    response = client.models.generate_content(
        model=gemini_1_5_flash,
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=[api_tool],
            temperature=0,
        ),
)
    if response.candidates and response.candidates[0].content.parts[0].function_call:
        function_call = response.candidates[0].content.parts[0].function_call
        return function_call.name, function_call.args
    return None, None

def generate_response(query_str, context_str):
    full_text = CHAT_TEXT_QA_PROMPT.format(context_str=json.dumps(context_str), query_str=query_str)
    resp = Settings.llm.complete(full_text)
    return resp.text

# Streamlit App
def main():
    st.title("Microsoft Graph API RAG Interface")
    st.write("Enter your query below to interact with the Microsoft Graph API.")

    # Input field for user query
    user_query = st.text_input("Enter your query:")

    if st.button("Submit"):
        if user_query:
            function_name, args = determine_function_call(user_query)
            
            if function_name and function_name in functions:
                try:
                    if function_name == "extract_sharepoint_usage":
                        result = functions[function_name](args["search_term"])
                    else:
                        result = functions[function_name]()
                    
                    if result:
                        response = generate_response(user_query, result)
                        st.write("Response:")
                        st.write(response)
                    else:
                        st.warning("No data found for the given query.")
                except Exception as e:
                    st.error(f"An error occurred: {e}")
            else:
                st.warning("The query cannot be served at this time.")
        else:
            st.warning("Please enter a query.")

if __name__ == "__main__":
    main()