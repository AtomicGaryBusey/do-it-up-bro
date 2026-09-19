# Work orders and durable state

For each substantial delegated task, provide:

- Goal and acceptance criteria; required inputs and evidence sources.
- Distinct role, dependencies, and allowed files or isolated workspace.
- Whether writing is permitted, relevant permissions, and budget/time limit.
- Required output: conclusion, evidence, checks run, artifact paths, limitations.

Avoid forwarding the whole conversation. Give independent candidates the same problem and constraints, but not each other's proposals. Reviewers receive the finished candidate and raw evidence without being told what conclusion to reach.

Maintain a small state file in an agreed task artifact directory. Record the goal, mode, milestone criteria, task IDs and dependencies, owners, artifact locations, completed checks, decisions, failed hypotheses, unresolved objections, and next action. Record requested and observed model/effort separately; unknown observations stay unknown. Do not persist credentials or hidden reasoning.

## Campaign mode

Split long work into verifiable milestones. Checkpoint at each integration boundary and before context handoff. Reuse the host's supported resume/workflow facilities where present. Resume by reading state, inspecting current files and Git status, and checking whether prior evidence still applies. Re-run invalidated checks; do not blindly replay completed work or assume a process survived a session exit.

Bound retries and waves by user limits and progress. An external blocker should leave a resumable checkpoint and a precise description of missing access or information. A failed leaf task does not invalidate successful independent work.

## Isolation

Concurrent writers need disjoint ownership or separate worktrees/directories. Record each starting revision; ensure it includes intended prerequisite changes. One integration owner reviews and combines outputs, resolves conflicts, and runs combined checks. Do not assume a host's subagents automatically receive separate worktrees. Never discard the user's existing work as cleanup.
