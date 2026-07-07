# Codex Zotero Bridge

Use this reference when Zotero operations can be handled by the local Codex Zotero Bridge plugin.

## What It Is

Codex Zotero Bridge is a Zotero Desktop plugin that registers authenticated local endpoints under Zotero's local HTTP server:

```text
http://127.0.0.1:23119/codex-zotero-bridge
```

It is intended for local Codex-to-Zotero operations and should not be exposed to public networks.

## Recommended Repository Layout

When this toolkit is cloned from GitHub, common relative paths are:

```text
python/codex_zotero_bridge_client.py
examples/codex_zotero_bridge_config.example.json
zotero-plugin/
skills/zotero-use/
skills/zotero-mineru-md-html/
```

Copy the example config to a local untracked config file and do not print or commit the token.

## Supported Operations

Prefer the bridge for:

- `GET /ping`: check bridge status.
- `GET /items/:itemKey`: read one Zotero item JSON by key.
- `POST /items/:itemKey/update`: update item fields, `Extra`, and tags.
- `POST /items/:itemKey/attachments`: add local file attachment as `link` or `import`.
- `POST /items/:itemKey/notes`: add child note HTML.

The bridge does not provide broad search/list endpoints. Use Pyzotero CLI for discovery, then bridge for item-level operations.

## Python Client Pattern

If the local client exists, prefer importing it instead of writing raw HTTP calls:

```python
from codex_zotero_bridge_client import ZoteroBridge

bridge = ZoteroBridge(r"path\to\codex_zotero_bridge_config.json")
print(bridge.ping())
item = bridge.get_item("ITEMKEY")
```

Update tags/fields/Extra:

```python
bridge.update_item(
    "ITEMKEY",
    fields={"title": "Updated title"},
    extra={
        "mode": "append",
        "dedupeMarker": "[CodexBridge:example]",
        "text": "[CodexBridge:example]\nProcessed by Codex.",
    },
    tags={"add": ["codex-processed"]},
)
```

Add attachment:

```python
bridge.add_attachment(
    "ITEMKEY",
    r"D:\path\to\full.md",
    mode="link",
    title="MinerU VLM Markdown Full Text",
)
```

Add note:

```python
bridge.add_note("ITEMKEY", "<p>Note body</p>")
```

## Safety Rules

1. Never print or commit the bridge token.
2. Do not modify Zotero unless the user explicitly asks for a write.
3. Prefer dry runs for batch workflows.
4. Use parent bibliographic item keys, not attachment item keys, for citation/write targets.
5. Report item keys, changed fields/tags, created note keys, and attachment titles after writes.

## When to Fall Back

Use Pyzotero CLI or active Zotero MCP tools when the task requires:

- keyword search across the library;
- listing collections/tags/recent items;
- browsing many candidate metadata records;
- reading indexed full text not available through the bridge;
- Word live citation fields.
