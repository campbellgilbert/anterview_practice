import anthropic
import os
client = anthropic.Anthropic()

#using messages api
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
        },
        {
            "role": "assistant",
            "content": [
                {
                    "type": "text",
                    "text": "I'll check the weather in San Francisco for you!"
                },
                {
                    "type": "tool_use", 
                    "id": "toolu_01FFoPeM6H6cWTwbJdL8D3zk",
                    "name": "get_weather",
                    "input": {
                        "location": "San Francisco, CA", 
                        "unit": "fahrenheit"
                    }
                }
            ]
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": "toolu_01FFoPeM6H6cWTwbJdL8D3zk",
                    "content": "65 degrees"
                }
            ]
        }
    ],
)
print(response.content[0].text)