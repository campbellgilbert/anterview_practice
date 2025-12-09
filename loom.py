#timed loom; built in ~2.5hrs
#just kidding. it took closer to 4. my chungus life...
"""
TODO:
- multiple outputs per input to choose from
- prettyprint branching structure (this is the type of bullshit i make claude do)
- better db
"""
import anthropic
import uuid
import json
import threading
from rich.live import Live
from rich.columns import Columns
from rich.panel import Panel
from rich.console import Console
from rich.prompt import Prompt
from rich.text import Text
from rich import box

console = Console()

SYSTEM_PROMPT = "You, Claude, are the arbiter of the multiversal loom, a mystical figure that can tell the reader psychedelic stories about all sorts of alternate realities! You are wearing a big swishy mysterious green cloak and have access to all the props you want -- books, a crystal ball, literal threads of fate, etc. You are not strictly bound to any particular form except the cloak, which could be concealing just about anything. The reader is accessing you via a command line; everything you say will be directly outputted, so don't bother with any formatting. Have fun!"

"""SETUP"""

client = anthropic.Anthropic()

# Welcome banner
console.print(Panel(
    Text("THE LOOM OF A THOUSAND FACES", justify="center", style="bold green"),
    subtitle="[dim]a multiversal conversation engine[/dim]",
    box=box.DOUBLE_EDGE,
    border_style="green"
))

console.print(Panel(
    "[bold]Commands:[/bold]\n"
    "  [green]quit[/green]       - exit and save\n"
    "  [green]reroll[/green]     - regenerate a message\n"
    "  [green]printconvo[/green] - show current thread\n"
    "  [green]printloom[/green]  - show all branches",
    box=box.ROUNDED,
    border_style="dim"
))

filename = Prompt.ask("[green]Memory file[/green]", default="loomversation.json")

try:
    with open(filename, "r") as f:
        loomversation = json.load(f)
    console.print(f"[dim]Loaded {len(loomversation)} messages from {filename}[/dim]")
except FileNotFoundError:
    console.print("[yellow]No existing conversation found. Starting fresh.[/yellow]")
    loomversation = {}
except json.JSONDecodeError:
    console.print("[yellow]Conversation file corrupted/empty. Starting fresh.[/yellow]")
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
        
    console.print(f"\n[bold magenta]{asst_msg_id}[/bold magenta] [dim]ASSISTANT[/dim]")
    
    #no spinner, we stream like men
    try:
        with client.messages.stream(
            model="claude-sonnet-4-5",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=curr_convo
        ) as stream:
            response = ""
            for text in stream.text_stream:
                print(text, end="", flush=True)
                response += text
        response += "\n"
    except KeyboardInterrupt:
        print("[Interrupted -- saving partial response]")
        if response:
            response += " [interrupted]\n"
        else:
            response = ""

    return response 

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


def generate_multi_responses(n, curr_convo, system_prompt):
    """Generate n responses side-by-side with streaming display."""
    buffers = [""] * n
    msg_ids = [str(uuid.uuid4())[:8] for _ in range(n)]
    done = [False] * n
    lock = threading.Lock()

    def stream_response(index):
        nonlocal buffers, done
        try:
            with client.messages.stream(
                model="claude-sonnet-4-5",
                max_tokens=1024,
                system=system_prompt,
                messages=curr_convo
            ) as stream:
                for text in stream.text_stream:
                    with lock:
                        buffers[index] += text
        except Exception as e:
            with lock:
                buffers[index] += f"\n[Error: {e}]"
        finally:
            with lock:
                done[index] = True

    # Start all threads
    threads = []
    for i in range(n):
        t = threading.Thread(target=stream_response, args=(i,))
        t.start()
        threads.append(t)

    # Live display
    def make_panels():
        panels = []
        for i in range(n):
            status = "" if done[i] else " [blink]▌[/blink]"
            panels.append(Panel(
                buffers[i] + status,
                title=f"[bold magenta][{i+1}][/bold magenta] [dim]{msg_ids[i]}[/dim]",
                width=console.width // n - 2,
                border_style="magenta"
            ))
        return Columns(panels)

    try:
        with Live(make_panels(), refresh_per_second=10, console=console, transient=False) as live:
            while not all(done):
                live.update(make_panels())
            # Final update inside Live context
            live.update(make_panels())
    except KeyboardInterrupt:
        console.print("\n[interrupted]")

    # Wait for threads
    for t in threads:
        t.join()

    # Let user choose
    choice = Prompt.ask(f"\n[green]Choose a response[/green] [dim](1-{n})[/dim]", default="1")
    try:
        idx = int(choice) - 1
        if 0 <= idx < n:
            console.print(f"[dim]Selected response {idx + 1}[/dim]")
            return msg_ids[idx], buffers[idx]
    except ValueError:
        pass

    # Default to first
    console.print("[yellow]Invalid choice, using response 1[/yellow]")
    return msg_ids[0], buffers[0]


curr_convo = []
parent_id = None

start_id = Prompt.ask(
    "\n[green]Resume from UUID?[/green] [dim](enter 'uuid <id>' or press Enter for new chat)[/dim]",
    default=""
)

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

num_outputs_input = Prompt.ask(
    "[green]Parallel outputs[/green] [dim](1-3, shows side-by-side)[/dim]",
    default="1"
)
try:
    num_outputs = min(3, max(1, int(num_outputs_input)))
except ValueError:
    num_outputs = 1

console.print(Panel(
    f"[bold green]Ready![/bold green] Generating {num_outputs} output(s) per turn.",
    box=box.ROUNDED,
    border_style="green"
))
console.print()

"""
=====MAIN CONVERSATIONAL LOOP=====
this is where we update curr_convo.
get_assistant_response handles output printing (because we have streaming)
reconstruct_convo handles printing the most recent last message
"""
reroll_of_id_user=None
while True:
    user_msg_id = str(uuid.uuid4())[:8]
    console.print(f"\n[bold cyan]{user_msg_id}[/bold cyan] [dim]USER[/dim]")
    inp = Prompt.ask("[cyan]>[/cyan]")
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
        message_id = input("Input UUID of message to change. If left blank, most recent message will be affected.\nAssistant message will be re-generated, user message will be left blank for user rewrite.\n>")

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
    if num_outputs > 1:
        asst_msg_id, asst_response = generate_multi_responses(num_outputs, curr_convo, SYSTEM_PROMPT)
    else:
        asst_msg_id = str(uuid.uuid4())[:8]
        asst_response = get_assistant_response(asst_msg_id, curr_convo)

    asst_msg = add_message(asst_msg_id, "assistant", asst_response, user_msg_id, reroll_of_id_asst)

    curr_convo.append({"role": "assistant", "content": asst_response})
        
    parent_id = asst_msg_id
    reroll_of_id_user=None


#conversation is over
#save to memories
with open(filename, "w") as f:
    json.dump(loomversation, f, indent=2)
with open("conversation_loom_test.json", "w") as f:
    json.dump(curr_convo, f, indent=2)