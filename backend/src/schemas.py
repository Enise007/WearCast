clothing_recommendation_schema = {
    "name": "build_clothing_recommendation_prompt",
    "description": "Provides personalized clothing recommendations based on current weather conditions. If the user specifies a location/city, use it as a parameter to get location-specific weather data and tailored clothing suggestions. If no location is provided, give general clothing advice without the city parameter.",
    "parameters": {
        "type": "object",
        "properties": {
            "city":{
            "type": "string",
            "description": "The name of the city/province to get the weather and clothing suggestions for. Only provide the main city or province name, not district names."
            }
        },
    }
}

weather_schema = {
    "name": "build_weather_prompt",
    "description": "If the user specifies a location/city, use it as a parameter to get location-specific weather data. If no location is provided, call the function without the city parameter.",
    "parameters": {
        "type": "object",
        "properties": {
            "city":{
            "type": "string",
            "description": "The name of the city/province to get the weather. Only provide the main city or province name, not district names."
            }
        },
    }
}

location_schema = {
    "name": "build_location_prompt",
    "description": "Returns the user's location information such as city and country.",
    "parameters": {
        "type": "object",
        "properties": {}
    }
}

quote_schema = {
    "name": "build_quote_prompt",
    "description": "Sends a motivational quote to the user.",
    "parameters": {
        "type": "object",
        "properties": {}
    }
}

capabilities_schema = {
    "name": "build_capabilities_prompt",
    "description": "Use this when the user asks about the bot's identity, capabilities, purpose, or what it can do. Triggers on questions like: 'who are you?', 'what can you do?', 'what are your functions?', 'senin görevin ne?', 'fonksiyonların neler?', 'özelliklerin neler?'.",
    "parameters": {
        "type": "object",
        "properties": {}
    }
}

tool_schemas = [clothing_recommendation_schema, weather_schema, location_schema, quote_schema, capabilities_schema]