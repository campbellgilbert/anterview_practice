import anthropic
import os
import time

#BARE MINIMUM
client = anthropic.Anthropic()

user_input = input(">")

response = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=1024,
    system="helpful assistant",
    messages = [
        {
            "role": "user",
            "content": user_input
        }
    ]
)
print(response.content[0].text)


#MEMORY, WITHIN FILE
client = anthropic.Anthropic()
conversation = []

while True:
    user_input = input()
    if user_input == "quit":
        break
    
    conversation.append({"role": "user", "content": user_input})

    response = client.messages.create(
        model = "claude-sonnet-4-5",
        max_tokens=1024,
        system="You are a friendly assistant.",
        messages=conversation
    )
    print(response.content[0].text)
    conversation.append({"role": "assistant", "content": response.content[0].text})


#MEMORY, PERSISTENT -- json file
import anthropic
import os
import json

client = anthropic.Anthropic()

with open("example.json", "r") as f:
    conversation = json.load(f)

while True:
    user_input = input()
    if user_input == "quit":
        break
    conversation.append({"role": "user", "content": user_input})

    response = client.messages.create(
        model="sonnet-4-5",
        max_tokens=1024,
        system="clod is hepful asistant",
        messages=conversation
    )
    reply = response.content[0].text
    print(reply)
    conversation.append({"role": "assistant", "content": reply})

with open("example.json", "r") as f:
    json.dump(conversation, f, indent=2)



#file use



#count tokens
from anthropic import Anthropic

client = Anthropic(
    api_key="my-anthropic-api-key",
)
beta_message_tokens_count = client.beta.messages.count_tokens(
    messages=[{
        "content": "string",
        "role": "user",
    }],
    model="claude-opus-4-5-20251101",
)
print(beta_message_tokens_count.context_management)