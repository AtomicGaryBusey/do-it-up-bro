# Optional native plugin bundles

`dub install` remains the direct skill installer. For an isolated Claude Code or
Grok plugin, export a host-specific bundle from this checkout or installed wheel:

```sh
dub plugin --provider claude --output /private/tmp/dub-claude --dry-run
dub plugin --provider claude --output /private/tmp/dub-claude
claude plugin validate --strict /private/tmp/dub-claude
claude --plugin-dir /private/tmp/dub-claude
```

For Grok:

```sh
dub plugin --provider grok --output /private/tmp/dub-grok
grok plugin validate /private/tmp/dub-grok
grok plugin install /private/tmp/dub-grok
```

The Grok installation command changes host plugin state; run it intentionally.
The exporter only writes the destination you specify and does not register,
install, or invoke a host model. Grok's exported plugin contains a reader agent
and a skill. Claude's contains a skill. Both copy the canonical DUB source and
embed that host's adapter. They do not include an unvalidated campaign workflow.

Existing output is a conflict (exit 1). `--force` archives the exact old output
beside it as a `.tar.gz` backup before replacement; the returned `backup` is the
recovery path. The output must be a dedicated directory, with no symlink ancestor.
Versioned sources should be exported afresh when updating the plugin.

The Grok marketplace is a separate distribution mechanism that requires a
repository index at `.grok-plugin/marketplace.json`. This export produces a local
plugin, not a marketplace index. Native validators passed for both local bundles
with the installed Claude 2.1.277 and Grok 1.0.34 CLIs, without model calls.
Loading and runtime behavior still depend on the actual host and its policies.
