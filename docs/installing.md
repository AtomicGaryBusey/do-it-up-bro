# Installation

Use Python 3.11+ and install with `python -m pip install .` in a virtual environment,
or `pipx install .`. The wheel includes the canonical skill and all runtime assets;
it works without the source checkout. For development use `pip install -e '.[dev]'`.

```sh
dub doctor
dub install --dry-run
dub install --provider claude --dry-run
dub install --provider claude
dub install --provider google --project /absolute/path/to/project --dry-run
```

Default `--provider all` selects detected executables. Explicit selection allows
installation even when the CLI is not installed. DUB does not install vendor CLIs,
authenticate accounts, enable host experiments, or modify host configuration.

| Provider | Personal skill base | Project skill base |
| --- | --- | --- |
| Codex | `~/.agents/skills` | `.agents/skills` |
| Claude | `~/.claude/skills` | `.claude/skills` |
| Gemini | `~/.gemini/skills` | `.gemini/skills` |
| Grok | `~/.grok/skills` | `.grok/skills` |
| Kimi | `~/.kimi-code/skills` or `$KIMI_CODE_HOME/skills` | `.kimi-code/skills` |

Each destination is `BASE/do-it-up-bro`. `--dry-run` makes no directories or
provider calls. Each result lists its destination and files. Existing entries
produce `action=conflict` and exit 1. Explicit `--force` first moves the old entry
under the host's `dub-backups/` directory **outside** the scanned `skills/` tree,
then publishes the staged replacement. The returned `backup` is the exact recovery
path; restore it to the original destination after moving the replacement aside.
Symlink ancestors are refused; a symlink destination itself can be backed up as
an entry without following it. Copies are supported; symlink installation is not
implemented in v0.1. Keep install operations sequential for a given destination.

Configuration defaults to `./DUB.toml`; use `dub --config /path/DUB.toml ...` to
select another. Relative run and executable paths resolve beside that config.
`command` is one executable or path, not a shell command. `AUTO_DETECT` chooses the
verified executable name. Unknown keys and invalid limits fail clearly.

Natural-language trigger discovery varies by host. Explicitly select the installed
skill if needed. Install DUB for the underlying CLI when using Herdr; there is no
separate Herdr skill installation or automatic change to Herdr's configuration.
