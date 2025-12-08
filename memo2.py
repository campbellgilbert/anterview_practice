import anthropic
import os
import json 

client = anthropic.Anthropic()

try:
    with open("conversation.json", "r") as f:
        conversation = json.load(f)
except:
    conversation = []

while True:
    ui = input()
    if ui == "q":
        break
    conversation.append({"role": "user", "content": ui})

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1024,
        system="you are a helpful assistant",
        messages=conversation
    )
    res = response.content[0].text
    conversation.append({"role": "assistant", "content": "res"})

with open("conversation.json", "r") as f:
    json.dump(conversation, f, indent=2)

with open("conversation.json", "r") as f:
    json.dump(conversation, f, indent=2)