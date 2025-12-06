import anthropic
import os
client = anthropic.Anthropic()

response = client.messages.create(
    model = "claude-sonnet-4-5",
    max_tokens=10,
    messages=[
        {
            "role": "user",
            "content": "Hi, Claude! I'm testing an app. Can you just say 'hello world'?"
        }
    ]
)
print(response.content)


#tool use test
response = client.messages.create(
    model = "claude-sonnet-4-5",
    max_tokens=1024,
    tools=[
        {
            "name": "get_weather",
            "description": "Get the current weather in a given location",
            "input_schema": {
                "type": "object", 
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City and state, e.g. Seattle, WA"
                    },
                    "unit": {
                        "type":"string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "The unit of temperature, either C or F"
                    }
                },
                "required": ["location"],
            }
        }
    ],
    messages = [ 
        {
            "role": "user",
            "content": "What's the weather like in San Francisco?"
        }
    ],
)

print(response)

response = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=1024,
    tools=[
        {
            "name": "get_weather",
            "description": "Get the current weather in a given location",
            "input_schema": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "The unit of temperature, either \"celsius\" or \"fahrenheit\""
                    }
                },
                "required": ["location"]
            }
        }
    ],
    messages=[{"role": "user", "content": "What is the weather like in San Francisco?"}]
)
print(response)