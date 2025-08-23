import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from src.schemas import tool_schemas
from src.core.prompts import (
    build_no_function_prompt,
    build_clothing_recommendation_prompt,
    build_location_prompt,
    build_weather_prompt,
    build_quote_prompt,
    build_capabilities_prompt,
)
import json

load_dotenv()


class FunctionRegistry:
    def __init__(self):
        self.functions = {
            "build_clothing_recommendation_prompt": build_clothing_recommendation_prompt,
            "build_location_prompt": build_location_prompt,
            "build_weather_prompt": build_weather_prompt,
            "build_quote_prompt": build_quote_prompt,
            "build_capabilities_prompt": build_capabilities_prompt,
        }

    def call_function(self, function_name: str, **kwargs):
        if function_name not in self.functions:
            raise ValueError(f"Unknown function: {function_name}")

        return self.functions[function_name](**kwargs)


function_registry = FunctionRegistry()
client = genai.Client()


def tool_call(user_prompt, history_summary=None):
    tools = types.Tool(function_declarations=tool_schemas)
    config = types.GenerateContentConfig(tools=[tools])

    if history_summary:
        user_prompt = f"Kullanıcının geçmişi: {history_summary}\n\nSoru: {user_prompt}"
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=user_prompt,
        config=config,
    )

    if response.candidates[0].content.parts[0].function_call:
        function_call = response.candidates[0].content.parts[0].function_call
        print(f"Function called: {function_call.name}")
        print(f"Arguments: {function_call.args}")

        function_result = function_registry.call_function(
            function_call.name, **function_call.args
        )
        print(f"Function result: {function_result}")
    else:
        print("No function call detected, using default response.")
        function_result = build_no_function_prompt()

    return function_result


def create_response(prompt):
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    return response.candidates[0].content.parts[0].text