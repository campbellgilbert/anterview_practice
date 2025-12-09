# Interview Prep Notes - Failure Modes & Gotchas

## Claude API

**Tool use is multi-turn**
- `stop_reason='tool_use'` means Claude wants YOU to execute the tool
- Extract tool name + input → run your logic → send result back as `tool_result`
- Claude doesn't always include explanatory text before tool calls (docs example is the chatty version)

**Conversation history**
- `messages=` IS the conversation history - don't serialize it into a single message
- Don't embed `json.dumps(conversation)` inside messages that get appended to conversation (recursive explosion)
- `system=` prompt is separate, sent every call, not part of messages array

## Python

**sum() with custom classes**
```python
sum([Value(1), Value(2)])  # fails: 0 + Value doesn't work
```
Fix: add `__radd__` to your class:
```python
def __radd__(self, other):
    return self + other
```

**File modes**
- `"r"` = read, `"w"` = write - mixing these up gives `io.UnsupportedOperation: not writable`
- Empty file (0 bytes) is not valid JSON - `json.load()` will throw `JSONDecodeError`

**Bare except: hides problems**
```python
# BAD - hides what actually went wrong
except:
    print("something broke")

# GOOD - tells you the real issue
except FileNotFoundError:
    print("file missing")
except json.JSONDecodeError:
    print("file corrupted/empty")
```

**Data structure types**
- `{}` is a dict, `[]` is a list
- `.append()` is for lists only
- Initialize JSON files with `[]` if you want a list, `{}` if you want a dict

## Git / SSH

**Branch names**
- Check your actual branch: commit output shows `[master (root-commit) ...]`
- `git push -u origin main` fails if your local branch is `master`
- Fix: `git branch -M main` to rename, or push to correct name

**SSH key selection**
- SSH agent offers keys in order; GitHub accepts first valid one (might be wrong account)
- `ssh-add -l` shows what's loaded in agent
- Fix in `~/.ssh/config`:
```
Host github.com-personal
    HostName github.com
    User git
    IdentitiesOnly yes          # ignore agent, use only specified key
    IdentityFile ~/.ssh/my_key
```
- Then use: `git remote set-url origin git@github.com-personal:user/repo.git`

## Debugging approach

1. Read the actual error message (not just "it broke")
2. Check file contents when I/O fails (`cat`, `ls -la` for size)
3. Print intermediate state (`printconvo`, `printloom` commands were smart)
4. Catch specific exceptions to surface real issues
