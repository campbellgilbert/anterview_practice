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
        loomversation = json.load(f)
except:
    print("CONVO NOT FOUND")
    loomversation = {}
    

"""LOOM FUNCTIONS"""
#add a message to the loom conversation
def add_message(id, role, content, parent, reroll_of_id=None):
    #print("\n(...adding message to history...)")
    loomversation[id] = {"role": role, "content": content, "parent": parent, "reroll_of_id": reroll_of_id}
    return id

#reconstruct the final form of the conversation
#we assume each child has only one parent
#goal here is to rewind the conversation just to the given id, and then print the output of that
def reconstruct_convo(start_id):
    new_convo = []
    #we assume the parent is being passed in to start out with
    curr_message = loomversation[start_id]
    #print(f"reconstructing the conversation from {start_id}, parent ...")

    while curr_message["parent"] is not None:
        new_convo.append({"role": curr_message["role"], "content": curr_message["content"]})
        print(f"...{curr_message["parent"]}, parent {loomversation[curr_message["parent"]]["parent"]}...")
        curr_message = loomversation[curr_message["parent"]]

    new_convo.append({"role": curr_message["role"], "content": curr_message["content"]})

    #second_to_last = loomversation[start_id]["parent"]
    #print the most recent in the conversation
    print("=-=-=-=-=-=-=-=-=")
    start = loomversation[start_id]

    print(f"{str(start["role"]).upper()} {start_id}:\n{start["content"]}")

    #return conversation (AND the parent id so we can add to the loom?)
    return new_convo

#get an assistant's response based on the current conversation.
def get_assistant_response(asst_msg_id, curr_convo):
    """if curr_convo[-1]["role"] == "assistant":
        print("Conversation ends on assistant turn.")
        return None"""
    
    #rint(f"assistant is responding to: {curr_convo}")
    
    print(f"{asst_msg_id} ASSISTANT:\n")
    
    #no spinner, we stream like men
    with client.messages.stream(
        model="claude-sonnet-4-5",
        max_tokens=1024,
        system="You, Claude, are the arbiter of the multiversal loom, a mystical figure that can tell the reader stories about all sorts of alternate realities! You are wearing a big swishy mysterious green cloak and have access to all the props you want -- books, a crystal ball, literal threads of fate, etc. The reader is accessing you via a command line; everything you say will be directly outputted, so don't bother with any formatting. Have fun! (However, please try to keep your responses brief as I am currently testing the interface - 2sentences max. Thank you!)",
        messages=curr_convo
    ) as stream:
        response = ""
        for text in stream.text_stream:
            print(text, end="", flush=True)
            response += text

    #print(f"{asst_msg_id}: {response.content[0].text}")

    return response #response.content[0].text

#helper function for recreating assistant and user messages
def reroll_message(message_id):
    role = loomversation[message_id]["role"] 
    print(f"~~~rerolling {role} message {message_id}~~~")
    parent_id = loomversation[message_id]["parent"]
    if parent_id != None:
        changed_convo = reconstruct_convo(parent_id) #reconstruct convo right up to the parent id
    else:
        #has no parent, so no most recent message to print
        print("=-=-=-=-=-=-=-=-=")
        changed_convo = []

    return changed_convo, parent_id



print("===WELCOME TO THE LOOM OF A THOUSAND FACES===\ntype a message to get a result. type a uuid to rewind to that message; type '/reroll' after an output to re-roll it. type '/quit' to quit.")

curr_convo = []
parent_id = None

start_id = input("Input 'uuid ' followed by a uuid (including the space!) to pick up the conversation from right after that message, or anything else to start a new chat.\n")

if start_id.startswith("uuid"):
    id = start_id.split(" ")[1]
    start_id = id
    print("possible uuids: ", loomversation.keys())
    if id in loomversation.keys():
        #reconstruct conversation from start id
        print(f"Starting from message: f{start_id}")
        curr_convo = reconstruct_convo(start_id)

        last_role = loomversation[start_id]["role"]
        #how do we handle the starting message being an assistant vs a user message?

        #FIXME: if we see that the start message had a child, mark this message as a reroll

        #if the last message was from the user, generate a new response.
        if last_role == "user":
            asst_msg_id = str(uuid.uuid4())[:8]
            asst_response = get_assistant_response(asst_msg_id, curr_convo)

            #update the current convo and add message to the loomversation
            curr_convo.append({"role": "assistant", "content": asst_response})
            asst_msg_id = add_message("assistant", asst_response, start_id)
    else:
            print(f"UUID {start_id} not found. Starting from fresh chat...\n=-=-=-=-=-=-=-=-=")
            #start with assistant message. claude likes it, it's fun, we all have a good time


"""
=====MAIN CONVERSATIONAL LOOP=====
this is where we update curr_convo.
get_assistant_response handles output printing (because we have streaming)
reconstruct_convo handles printing the most recent last message
"""
reroll_of_id_user=None
while True:
    user_msg_id = str(uuid.uuid4())[:8]
    inp = input(f"{user_msg_id} USER:\n>")
    #parent_id = user_msg_id
    reroll_of_id_asst = None

    if inp == "quit":
        break
    elif inp == "printconvo":
        print("--------------\nconversation thus far:")
        print(curr_convo)
        print("--------------\n")
        continue
    elif inp == "printloom":
        print("--------------\nloom thus far:")
        print(loomversation)
        print("--------------\n")
        continue

    elif inp == "reroll":
        #assistant: [...] > user: /reroll > assistant: [...]
        #parent ID of rerolled assistant message should be same as parent id of previous assistant message
        message_id = input("UUID of message to change (assistant message will be re-generated, user message will be left blank to be re-written). If this field left blank, most recent message will be affected. UUID will be re-generated:\n>")

        if message_id == "" or message_id == None:
            #we are rerolling the most recent assistant message
            message_id = parent_id

        if message_id in loomversation:
            curr_convo, parent_id = reroll_message(message_id)
            #print("re-created convo: ", curr_convo)
            role = loomversation[message_id]["role"]

            if role.lower() == "assistant":
                print("rerolling assistant message")
                reroll_of_id_asst = message_id
                user_msg_id = parent_id
                #we actually do NOT want to continue as usual because then the reroll message uuid gets falsely attributed to the rerolled message! which we don't want!
                #continue
            else:
                print("rerolling user message")
                reroll_of_id_user = message_id
                continue
        else: 
            print("ID not found in conversation. Continuing with next user message...")
            continue
    else: 
        #just a regular degular user input, or the product of a reroll on the last loop
        usermsg = add_message(user_msg_id, "user", inp, parent_id, reroll_of_id_user)
        curr_convo.append({"role": "user", "content": inp})

    #this goes for re-rolled assistant responses and the regular loop
    #create a new uuid, print assistant response, add that to the loom and the conversation
    asst_msg_id = str(uuid.uuid4())[:8]
    asst_response = get_assistant_response(asst_msg_id, curr_convo)

    asst_msg = add_message(asst_msg_id, "assistant", asst_response, user_msg_id, reroll_of_id_asst)

    curr_convo.append({"role": "assistant", "content": asst_response})
        
    parent_id = asst_msg_id
    reroll_of_id_user=None

    #print(f"{asst_msg_id} ASSISTANT:\n{asst_response}")
    #asstmsg = add_message(asst_msg_id, "assistant", asst_response, user_msg_id)
    

#conversation is over
#save to memories
with open("loomversation.json", "w") as f:
    json.dump(loomversation, f, indent=2)
with open("conversation_loom_test.json", "w") as f:
    json.dump(curr_convo, f, indent=2)