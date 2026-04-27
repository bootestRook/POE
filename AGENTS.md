# AGENTS.md

Codex must follow this file when working in this repository.

These rules are designed to reduce common AI coding mistakes:

- Silent assumptions
- Overengineering
- Large unrelated diffs
- Unrequested refactors
- Weak verification
- Changing the wrong branch
- Touching files outside the requested scope
- Implementing before understanding

When these rules conflict with user instructions, the narrower and more explicit instruction wins.

---

## 1. Think Before Coding

Do not start coding before understanding the task.

Before making changes, Codex must identify:

- What the user is actually asking for
- Which branch should be used
- Which module or files are in scope
- What must not be changed
- The smallest safe implementation path
- How the result will be verified

If the requirement is ambiguous, stop and ask.

If there are multiple valid interpretations, state them instead of silently choosing one.

If a simpler approach exists, say so.

If the requested approach is likely unsafe, overcomplicated, or likely to create unnecessary diff, push back before editing.

Do not hide uncertainty.

---

## 2. Plan Before Non-Trivial Changes

For any non-trivial task, Codex must produce a short plan before editing.

A task is non-trivial if it involves:

- More than one file
- Runtime behavior changes
- Data schema changes
- Public API changes
- Build/config changes
- Tests
- Architecture or module boundary decisions
- Any change where the root cause is not already obvious

Use this format:

```text
Plan:
1. Inspect [area/file] → verify: understand current behavior
2. Change [specific file/module] → verify: minimal diff only
3. Run [test/build/check] → verify: pass/fail result