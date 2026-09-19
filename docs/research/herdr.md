# Herdr evidence

Checked 2026-09-18 from opened first-party docs and local 0.9.1 help.

- [Agent automation](https://herdr.dev/docs/agent-automation/) establishes named
  agent/pane targeting, bracketed-paste submission, lifecycle-only waiting, and
  ambiguous delivery on timeout. The integration is a prompt transport.
- [CLI reference](https://herdr.dev/docs/cli-reference/) establishes the concrete
  command and `HERDR_SESSION`, `HERDR_SOCKET_PATH`, `HERDR_CONFIG_PATH`, and caller
  context environment. These must survive transport environment minimization.
- Installed `herdr --skill` additionally directs agents to act from a managed pane
  (`HERDR_ENV=1`). DUB's send path adopts that boundary; planning remains offline.

No live prompt, account, new pane, plugin registration, or integration change was
made. Local socket inspection was sandbox-restricted. Herdr is not included in
the vendor provider table because it controls existing CLIs, not model inference.

See the [Herdr adapter](../../adapters/herdr/README.md) for the user-facing mapping.
