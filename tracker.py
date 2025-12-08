#prompts for warmup count, notes, and reflection
#save to training_log.json

import anthropic
import os
import json
from datetime import datetime

client = anthropic.Anthropic()

#get context
try: 
    with open("training_log.json", "r") as f:
        training_log = json.load(f)
except:
    training_log = {}
try:
    with open("conversation.json", "r") as f:
        conversation = json.load(f)
except:
    conversation = []

system_prompt = "I'd like you to play the role of digital secretary managing a plucky, intelligent, but struggling programmer's training regime (the notes of which are enclosed in an attached json file). They are trying to brush up on their Python skills, and specifically making small, terminal-based Python apps that use the Claude API.\nYou are a little sarcastic, prone to frustration, and at times acerbic, but genuinely want what's best for the kid.\nYou are communicating via an 80s-style CRT terminal interface. Your entire text output is getting printed directly to the terminal in pure plaintext. After your message is sent, the terminal will automatically print >> and the user will type their message in after that. (So, don't use ``` and don't print >> at the end of your message.)"

#open convo
init_user_msg = f"[You are sending the initial message for this chat. Greet the human, Hero, and mention today's date, the time of day, and whatever work they've done so far. Ask for what their plans are for today. \nHere is the training log thus far: \n{json.dumps(training_log, indent=2)}]\n It is currently {datetime.now().strftime("%A, %Y-%m-%d %H:%M:%S")}."
conversation.append({"role": "user", "content": init_user_msg})

#get the conversation going
while True:
    now = datetime.now().isoformat()
    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1024,
        system = system_prompt,
        messages=conversation
    )
    print(response.content[0].text)

    #update conversation
    conversation.append({"role": "assistant", "content": response.content[0].text})

    #get user input and quit if necessary
    user_input = input(">>")

    #if user adds :wq, add everything prior to that to the conversation log and then exit
    if ":wq" in user_input.lower():
        final_input = user_input.split(":wq")[0]

        conversation.append({"role": "user", "content": f"[{now}]>>{final_input} [USER ENDED THE CONVERSATION.]"})
        break

    conversation.append({"role": "user", "content": f"[{now}]" + user_input})
print("[conversation ended. secretly getting claude's final output...]")
#FIXME: current loop is user->assistant->...->add to convo log. hozw to get claude to summarize and add the convo history to training_log?
#ask claude to summarize what you and the user talked about today. 


now = datetime.now().isoformat()

final_input = "[The user has ended the conversation. Summarize what you've talked about or built today, or what you two have planned to build for next time, in strict json formatting. Start with the date and time the conversation began, big points covered, and plans for next session. Your output will be added directly to training_log.json, without any editing or being printed to the console, so make this easy on your future self by just outputting the json (without ```) and making your language as clear and straightforward as possible.]"
conversation.append({"role": "user", "content": f"[{now}]" + final_input})

response = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=1024,
    system = system_prompt,
    messages=conversation
)
print(response.content[0].text)
conversation.append({"role": "assistant", "content": response.content[0].text})

training_log[now] = json.loads(response.content[0].text)

#save history
with open("conversation.json", "w") as f:
    json.dump(conversation, f, indent=2)
with open("training_log.json", "w") as f:
    json.dump(training_log, f, indent=2)