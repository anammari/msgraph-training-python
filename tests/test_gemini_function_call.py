import os
import json
from google import genai
from google.genai import types

# Define the model ID
MODEL_ID = 'gemini-1.5-flash-8b'

# Define the set light function
def set_light_values(brightness, color_temp):
    """Set the brightness and color temperature of a room light. (mock API).

    Args:
        brightness: Light level from 0 to 100. Zero is off and 100 is full brightness
        color_temp: Color temperature of the light fixture, which can be `daylight`, `cool` or `warm`.

    Returns:
        A dictionary containing the set brightness and color temperature.
    """
    return {
        "brightness": brightness,
        "colorTemperature": color_temp
    }

# Define the function to turn on/off the light
def turn_on_light(on):
    """Turn on or off the room light.

    Args:
        on: A boolean indicating whether to turn on or off the light.

    Returns:
        A message indicating the result of the action.
    """
    if on:
        return "Light turned on"
    else:
        return "Light turned off"

# Define the function declarations
set_light_values_declaration = types.FunctionDeclaration(
    name="set_light_values",
    description="Set the brightness and color temperature of a room light",
    parameters={
        "type": "OBJECT",
        "properties": {
            "brightness": {
                "type": "INTEGER",
                "description": "Light level from 0 to 100. Zero is off and 100 is full brightness",
                "minimum": 0,
                "maximum": 100,
            },
            "color_temp": {
                "type": "STRING",
                "description": "Color temperature of the light fixture, which can be `daylight`, `cool` or `warm`",
                "enum": ["daylight", "cool", "warm"],
            },
        },
        "required": ["brightness", "color_temp"],
    },
)

turn_on_light_declaration = types.FunctionDeclaration(
    name="turn_on_light",
    description="Turn on or off the room light",
    parameters={
        "type": "OBJECT",
        "properties": {
            "on": {
                "type": "BOOLEAN",
                "description": "Whether to turn on or off the light",
            },
        },
        "required": ["on"],
    },
)

# Define the tool
light_tool = types.Tool(
    function_declarations=[set_light_values_declaration, turn_on_light_declaration],
)

# Create a client
client = genai.Client(api_key=os.environ['GEMINI_API_KEY'])

# Generate content
prompt = input("Enter a prompt: ")
response = client.models.generate_content(
    model=MODEL_ID,
    contents=prompt,
    config=types.GenerateContentConfig(
        tools=[light_tool],
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

# Define the functions
functions = {
    "set_light_values": set_light_values,
    "turn_on_light": turn_on_light,
}

# Call the function
print("\nFunction Call Output:")
if function_name in functions:
    function = functions[function_name]
    if function_name == "set_light_values":
        result = function(args["brightness"], args["color_temp"])
    elif function_name == "turn_on_light":
        result = function(args["on"])
    print(json.dumps({
        "function_name": function_name,
        "args": args,
        "result": result
    }, indent=4))
else:
    print(f"Function {function_name} not found")
