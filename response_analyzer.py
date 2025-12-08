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