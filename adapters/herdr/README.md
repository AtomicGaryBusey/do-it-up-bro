# Herdr transport

Checked 2026-09-18. Local `herdr --version`: **0.9.1**. This adapter uses the
[official CLI reference](https://herdr.dev/docs/cli-reference/) and
[agent automation guide](https://herdr.dev/docs/agent-automation/), plus installed
`herdr agent prompt --help`. No live prompt was sent during implementation.

Install DUB for the underlying CLI first. In a Herdr-managed pane:

```sh
herdr agent list
dub herdr --target reviewer --dry-run "Review my parser"
dub herdr --target reviewer "Review my parser"
dub herdr --target reviewer --campaign "Deliver the migration"
```

Use an actual live name or pane ID returned by Herdr, such as `w1:p2`. DUB requires
an explicit target and `HERDR_ENV=1` for sending. Preview works outside Herdr.
It preserves the documented session/socket/config and caller-context variables.
This transport does not use the federation run ledger or create new provider roots.

The generated command is:

```sh
herdr agent prompt reviewer 'Do it up, Bro: Review my parser' --wait --timeout 1800000
```

Herdr submits to a recognized agent and honors bracketed paste. A blocked agent
rejects submission. Waiting observes lifecycle, not a particular turn or verified
goal completion; an already-working agent may settle from its previous turn.
Inspect the target afterwards. A timeout or stalled result may follow delivery:
do not retry blindly. Stopping DUB's client does not stop the existing agent.

Herdr's native layout, worktrees, and `agent start` can organize independent host
agents, but v0.1 does not create these automatically. The selected host controls
models, effort, tools, billing, and native subagents. No Herdr skill path or model
API is invented. Do not install this transport as a model-provider skill or replace
Herdr's built-in `herdr --skill` instructions. Remote machine selection and plugin
actions are outside this adapter's scope.
