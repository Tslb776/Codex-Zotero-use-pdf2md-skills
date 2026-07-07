---
name: zotero-mineru-md-html
description: Convert PDF attachments under Zotero items to Markdown and HTML through MinerU Precision API, then attach the generated Markdown and HTML reader files back to the same Zotero items through the local Codex Zotero Bridge. Use when the user asks to turn Zotero PDFs into md/html, run MinerU on Zotero entries, batch-convert Zotero papers or patents, or mount generated reading files back under Zotero items.
---

# Zotero MinerU Markdown/HTML

Use this skill when the task is:

- Convert Zotero item PDF attachments to Markdown with MinerU.
- Generate or retrieve HTML reader files from MinerU output.
- Attach `full.md` and `full.html` back under the same Zotero parent item.
- Batch process Zotero items by collection key, item key, title keyword, or item type.

## Safety

MinerU conversion uploads PDFs to an external service. Before uploading PDFs, confirm that the user explicitly allows uploading the selected PDFs to MinerU Precision API.

Never print or repeat the MinerU API token. Prefer `MINERU_API_TOKEN` from the environment.

## Requirements

- Zotero Desktop is running.
- Codex Zotero Bridge plugin is installed and enabled.
- A local bridge config exists, or `--bridge-config` is provided.
- Zotero local API is reachable, normally `http://localhost:23119/api/users/<USER_ID>`.
- Zotero storage path is known, or `--storage-root` is provided.
- `MINERU_API_TOKEN` is set for real conversion.

## Workflow

1. Confirm target scope: item keys, title keyword, item type, or collection key.
2. Confirm upload permission if not already explicit.
3. Run dry run first:

```powershell
python skills\zotero-mineru-md-html\scripts\zotero_mineru_convert.py --root . --collection-key COLLECTION_KEY --bridge-config path\to\codex_zotero_bridge_config.json --dry-run
```

4. Run conversion:

```powershell
$env:MINERU_API_TOKEN = "<token>"
python skills\zotero-mineru-md-html\scripts\zotero_mineru_convert.py --root . --collection-key COLLECTION_KEY --bridge-config path\to\codex_zotero_bridge_config.json
```

5. Report target count, PDF count, converted count, attached count, failures, and checkpoint path.

## Useful Commands

Convert one item:

```powershell
python skills\zotero-mineru-md-html\scripts\zotero_mineru_convert.py --root . --item-key ITEM_KEY --bridge-config path\to\codex_zotero_bridge_config.json
```

Convert matching titles within a collection:

```powershell
python skills\zotero-mineru-md-html\scripts\zotero_mineru_convert.py --root . --collection-key COLLECTION_KEY --title "temperature field" --bridge-config path\to\codex_zotero_bridge_config.json
```

Convert only patents:

```powershell
python skills\zotero-mineru-md-html\scripts\zotero_mineru_convert.py --root . --collection-key COLLECTION_KEY --item-type patent --bridge-config path\to\codex_zotero_bridge_config.json
```

Force reconversion:

```powershell
python skills\zotero-mineru-md-html\scripts\zotero_mineru_convert.py --root . --collection-key COLLECTION_KEY --bridge-config path\to\codex_zotero_bridge_config.json --force
```

## Output Convention

- Markdown: `mineru_outputs/<ITEM_KEY>/mineru-result/full.md`
- HTML: `mineru_outputs/<ITEM_KEY>/mineru-result/full.html`
- Zotero attachment title for Markdown: `MinerU VLM Markdown Full Text`
- Zotero attachment title for HTML: `MinerU VLM HTML Reader`

## Quality Checks

After completion, verify that each converted item has:

- `full.md` exists and is not empty.
- `full.html` exists and is not empty.
- Both Zotero attachment titles are present under the parent item.
- The checkpoint JSON has no failed items.
