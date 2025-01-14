import os
import json
import requests
from google import genai
from google.genai import types

# Define the model ID
MODEL_ID = 'gemini-1.5-flash-8b'

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

# Create a client
client = genai.Client(api_key=os.environ['GEMINI_API_KEY'])

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

# Generate content based on the prompt
prompt = input("Enter a prompt: ")
response = client.models.generate_content(
    model=MODEL_ID,
    contents=prompt,
    config=types.GenerateContentConfig(
        tools=[api_tool],
        temperature=0,
    ),
)

# Print the function call
print("Model Response:")
function_call = response.candidates[0].content.parts[0].function_call
print(json.dumps({
    "function_name": function_call.name,
    "args": function_call.args
}, indent=4))

# Get the function name and args from the response
function_name = function_call.name
args = function_call.args

# Call the function
print("\nFunction Call Output:")
if function_name in functions:
    function = functions[function_name]
    if function_name == "extract_sharepoint_usage":
        result = function(args["search_term"])
    else:
        result = function()
    print(json.dumps({
        "function_name": function_name,
        "args": args,
        "result": result
    }, indent=4))
else:
    print(f"Function {function_name} not found")