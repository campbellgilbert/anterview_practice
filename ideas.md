tldr.py -- take in a filename, gives varying levels of length (short/medium/long), claude summarizes the file

  1. Self-correcting code agent (medium)

  Claude writes code, runs it, sees errors, and iterates until it works. Requires:
  - Tool use loop (execute code, return results)
  - Multi-turn reasoning
  - Knowing when to give up

  2. Debate agent (medium-hard)

  Two Claude instances argue opposite sides of a topic, then a third judges. Shows you
  understand:
  - Managing multiple conversation contexts
  - How framing/system prompts shape behavior
  - Token/cost awareness

  3. Memory-augmented assistant (hard)

  Claude that maintains long-term memory across sessions using embeddings + retrieval. When
  context gets long, it summarizes and stores to a vector DB, retrieves relevant memories for
   new queries.

  4. Constitutional AI demo (very relevant for Anthropic)

  Build a simple critique-revision loop: Claude generates a response, then critiques it
  against principles you define, then revises. This is literally how Anthropic trains models.