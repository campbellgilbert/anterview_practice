#timed loom; built in ~2.5hrs
"""
TODO:
- multiple outputs per input to choose from
- prettyprint branching structure
- better db
- should we add command messages to the loom history?
"""
import anthropic
import uuid
import json
import itertools
import threading
import time

"""SETUP"""

client = anthropic.Anthropic()

try:
    with open("loomversation.json", "r") as f:
        loomversation = json.loads(f)
except:
    loomversation = {}

#MAKE IT LOOK NICE


"""LOOM FUNCTIONS"""
#add a message to the loom conversation
def add_message(id, role, content, parent, reroll_of_id=None):
    print("\n(...adding message to history...)")
    loomversation[id] = {"role": role, "content": content, "parent": parent, "reroll_of_id": reroll_of_id}
    return id

#reconstruct the final form of the conversation
#we assume each child has only one parent
def reconstruct_convo(start_id):
    print(f"reconstructing the conversation from {start_id}...")
    conversation = []
    curr_message = loomversation[start_id]

    while curr_message["parent"] is not None:
        conversation.append({"role": curr_message["role"], "content": curr_message["content"]})
        print(f"...{curr_message["parent"]}...")
        curr_message = loomversation[curr_message["parent"]]

    #print the most recent message
    print("=-=-=-=-=-=-=-=-=")
    last_role = loomversation[start_id]["role"]
    print(f"{str(last_role).upper()} {start_id}:\n{loomversation[start_id]["content"]}")

    #return conversation (AND the parent id so we can add to the loom?)
    return conversation

#get an assistant's response based on the current conversation.
def get_assistant_response(asst_id, curr_convo):
    """if curr_convo[-1]["role"] == "assistant":
        print("Conversation ends on assistant turn.")
        return None"""
    
    print(f"{asst_msg_id} ASSISTANT:\n")
    
    #no spinner, we stream like men
    with client.messages.stream(
        model="claude-sonnet-4-5",
        max_tokens=1024,
        system="You, Claude, are the arbiter of the multiversal loom, a mystical figure that can tell the reader stories about all sorts of alternate realities! You are wearing a big swishy mysterious green cloak and have access to all the props you want -- books, a crystal ball, literal threads of fate, etc. The reader is accessing you via a command line; everything you say will be directly outputted, so don't bother with any formatting. Have fun!",
        messages=curr_convo
    ) as stream:
        response = ""
        for text in stream.text_stream:
            print(text, end="", flush=True)
            response += text

    #print(f"{asst_msg_id}: {response.content[0].text}")

    return response #response.content[0].text

#re-generate the most recent assistant message
# add to loomversation
#  return changed conversational thread, assistnat response, and id within the overall loom
def reroll_asst(message_id):
    #changed_convo = curr_convo[:-1]
    #FIXME -- actually re-create the conversation
    print(f"~~~rerolling message {message_id}~~~")
    parent_id = loomversation[message_id]["parent"]
    if parent_id != None:
        changed_convo = reconstruct_convo(parent_id) #reconstruct convo right up to the parent id
    else:
        changed_convo = []

    asst_msg_id = str(uuid.uuid4())[:8]
    asst_response = get_assistant_response(asst_msg_id, changed_convo)
    #changed_convo.append({"role": "assistant", "content": asst_response})

    asst_msg = add_message(asst_msg_id, "assistant", asst_response, parent_id, message_id)

    return changed_convo, asst_response, asst_msg_id

#def reroll_user(message_id):
#    print(f"rerolling message {message_id}")


#flat store with parent pointers; reconstruct any path by walking up the chain
#i think making this a class actually makes it harder to work with so we're not gonna do that

print("===WELCOME TO THE LOOM OF A THOUSAND FACES===\ntype a message to get a result. type a uuid to rewind to that message; type '/reroll' after an output to re-roll it. type '/quit' to quit.")

curr_convo = []
parent_id = None

start_id = input("input a uuid to pick up the conversation from right after OR '/new' to start a new chat. you can't pick the converstion up from a command message.\n")

if start_id in loomversation:
    #reconstruct conversation from start id
    print(f"Starting from message: f{start_id}")
    curr_convo = reconstruct_convo(start_id, loomversation)

    last_role = loomversation[start_id]["role"]
    #how do we handle the starting message being an assistant vs a user message?

    #properly print the most recent response
    #print(f"{str(last_role).upper()} {start_id}: \n")

    #FIXME: if we see that the start message had a child, mark this message as a reroll

    #if the last message was from the user, generate a new response.
    if last_role == "user":
        asst_msg_id = str(uuid.uuid4())[:8]
        asst_response = get_assistant_response(asst_msg_id, curr_convo)

        #update the current convo and add message to the loomversation
        curr_convo.append({"role": "assistant", "content": asst_response})
        asst_msg_id = add_message("assistant", asst_response, start_id)
    #else:
        #if the last message was assistant, we just go forward with the usual loop
        #print(curr_convo[-1]["content"])
else:
        if start_id.lower() != "/new":
            print("The fuck is you on about big dog!")
        print("Starting from fresh chat...\n=-=-=-=-=-=-=-=-=")


"""
=====MAIN CONVERSATIONAL LOOP=====
this is where we update curr_convo and print assistant outputs.
"""

while True:
    user_msg_id = str(uuid.uuid4())[:8]
    inp = input(f"{user_msg_id} USER:\n>")
    
    if inp == "quit":
        break
    if inp == "reroll":
        #assistant: [...] > user: /reroll > assistant: [...]
        #parent ID of rerolled assistant message should be same as parent id of previous assistant message
        message_id = input("UUID of message to change (assistant message will be re-generated, user message will be left blank to be re-written); if this field left blank, most recent message will be affected:\n>")

        if message_id in loomversation:
            #parent_id = loomversation[id]["parent"]

            if loomversation[message_id]["role"] == "assistant":
                #reroll_asst adds to loomversation BUT doesn't print the response, so we have to do that ourselves.
                print('re-rolling assistant message')
                curr_convo, asst_response, asst_msg_id = reroll_asst(message_id)
                
                asst_msg_id = str(uuid.uuid4())[:8]
                asst_response = get_assistant_response(asst_msg_id, curr_convo)
                curr_convo.append({"role": "assistant", "content": asst_response})
                
            else:
                print(f"~~~rewriting message {message_id}~~~")
                #rewrite user message
                parent_id = loomversation[message_id]["parent"]
                if parent_id != None:
                    changed_convo = reconstruct_convo(parent_id) #reconstruct convo right up to the parent id
                    #re-create response by skipping ahead to the next user input and passing parent id thru there
                    continue
                else:
                    changed_convo = []

        elif message_id == "":
            #change most recent message
            # since this is a user turn, we assume most recent message is an assistant.
            curr_convo, asst_response, asst_msg_id = reroll_asst(message_id)

        else: 
            print("ID not found in conversation. Continuing with next user message...")
            continue
    if inp == "printconvo":
        print("--------------\nconversation thus far:")
        print(curr_convo)
        print("--------------\n")
    else: 
        #just a regular degular user input
        usermsg = add_message(user_msg_id, "user", inp, parent_id)
        curr_convo.append({"role": "user", "content": inp})

        asst_msg_id = str(uuid.uuid4())[:8]
        asst_response = get_assistant_response(asst_msg_id, curr_convo)
        curr_convo.append({"role": "assistant", "content": asst_response})

    #print(f"{asst_msg_id} ASSISTANT:\n{asst_response}")
    asstmsg = add_message(asst_msg_id, "assistant", asst_response, user_msg_id)
    parent_id = asst_msg_id

#conversation is over
#save to memories
with open("loomversation.json", "r") as f:
    json.dump(loomversation, f, indent=2)
with open("conversation_loom_test.json", "r") as f:
    json.dump(curr_convo, f, indent=2)