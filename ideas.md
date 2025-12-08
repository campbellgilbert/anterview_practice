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


    1. Streaming chat with graceful interrupts

  Handle streaming responses properly, let user ctrl+C mid-response without crashing, maintain clean state. Tests: generators, signal handling, terminal
   I/O.

  2. Parallel document processor

  Feed 10 documents to Claude concurrently, aggregate results. Tests: async/await or threading, rate limiting, error handling when some calls fail.

  3. Response → structured data parser

  Get Claude to output info, parse it into validated Python objects (not just JSON mode - handle messy outputs too). Tests: regex, parsing strategies,
  validation, error recovery.

  4. Retry/backoff wrapper

  Build a robust API client that handles rate limits, transient errors, timeouts with exponential backoff. Tests: decorators, exception handling,
  timing.

  5. Simple RAG from scratch

  Load text files, chunk them, do basic keyword/TF-IDF retrieval (no vector DB), augment prompts. Tests: file I/O, text processing, data structures.

  6. Conversation branching

  Save/load conversations, let user "fork" from any point to explore different paths. Tests: tree data structures, serialization, state management.

  