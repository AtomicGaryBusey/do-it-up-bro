---
name: dub
description: Run the Do It Up, Bro orchestration workflow when the user explicitly invokes DUB, says Do it up, Bro, or asks for independent agents and rigorous verification.
---

# DUB for Codex

This is the short Codex alias for the sibling `do-it-up-bro` skill. Before acting, read and follow `../do-it-up-bro/SKILL.md` in full, then read the references it requires for the task. Use that bundle's `references/host-adapter.md` for Codex-specific capabilities. If the sibling skill is absent, tell the user that DUB needs to be installed; do not improvise a different protocol.

Treat the remainder of the user's prompt as the goal. Preserve its scope, permissions, budget, and stopping conditions. Use real native subagents when independent work is useful; verify and repair before reporting completion.
