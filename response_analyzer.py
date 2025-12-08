"""
YES. Finally! Let's DO this.

Alright, here's the plan we mapped out on Friday:

**API RESPONSE ANALYZER - THE BUILD PLAN**

**PHASE 1: BASIC STRUCTURE (TODAY, RIGHT NOW)**
Create a CLI tool that:
- Takes a prompt from the user
- Sends it to Claude API
- Captures the FULL response object (not just the text)
- Extracts and displays key metrics:
  * Input tokens used
  * Output tokens used
  * Model used
  * Stop reason
  * Response time (you'll measure this with Python's time module)

**PHASE 2: THE GOOD STUFF (Tomorrow/Monday)**
- Save each response to a JSON log file
- Compare multiple responses side-by-side
- Calculate cost estimates based on token usage
- Track patterns over time (avg tokens, response times, etc)

**YOUR IMMEDIATE STEPS:**
1. Create a file called `api_analyzer.py`
2. Import: anthropic, time, json
3. Write a function that sends a message and returns the full Message object
4. Parse `response.usage` to get token counts
5. Print it all in a nice readable format

The key insight: The anthropic library returns a Message object with a `.usage` attribute that has `.input_tokens` and `.output_tokens`. You want to grab those.

Ready to start coding? What's your first question?

"""
import anthropic
import os
import time
import json
client = anthropic.Anthropic()

input = input()

start = time.time()

response = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=1024,
    system="You are a helpful assistant.",
    messages=[
        {
            "role": "user",
            "content": input
        }
    ]
)
end = time.time()
print(response.content[0].text)
#output input tokens uised, output tokens uised
print(f"input tokens: {response.usage.input_tokens}")
print(f"output tokens: {response.usage.output_tokens}")
print(f"model : {response.model}")
print(f"stop reason : {response.stop_reason}")
print(f"response time: {end - start}")


"""Message(id='msg_01TC29ZGpmUku5nYqRmy8yDs', 
    content=[TextBlock(citations=None, 
    text='I hear your frustration! Here are some practical strategies to break the procrastination cycle:\n\n## Quick wins:\n- **Start tiny** - Just 2 minutes. Tell yourself you\'ll work for *only* 2 minutes. Usually, starting is the hardest part.\n- **Remove friction** - Close unrelated tabs, put phone in another room, make the task easier to start than to avoid.\n- **Use the "eat the frog" method** - Do the worst task first thing, before your brain can negotiate.\n\n## Deeper strategies:\n- **Figure out WHY** - Are you procrastinating because the task is:\n  - Unclear? → Break it into specific steps\n  - Boring? → Add a reward or timer challenge\n  - Scary/overwhelming? → Make it smaller\n  - Perfectionism? → Aim for "done" not "perfect"\n\n- **Time-box it** - Pomodoro technique (25 min work, 5 min break) works wonders\n\n- **Forgive yourself** - Self-criticism actually increases procrastination. Just redirect and start.\n\n## Right now:\nPick ONE small concrete action you can do in the next 5 minutes. What would that be?\n\nThe fact that you\'re asking means you\'re ready to change. You\'ve got this! 💪', 
    type='text')], 
    model='claude-sonnet-4-5-20250929', 
    role='assistant', 
    stop_reason='end_turn', 
    stop_sequence=None, 
    type='message', 
    usage=Usage(
        cache_creation=CacheCreation(
            ephemeral_1h_input_tokens=0, ephemeral_5m_input_tokens=0
        ), 
        cache_creation_input_tokens=0, 
        cache_read_input_tokens=0, 
        input_tokens=24, 
        output_tokens=299, 
        server_tool_use=None, 
        service_tier='standard'
    )
)
    """