---
name: zotero-use
description: "Use when Codex needs to operate Zotero: search/query/retrieve references, read item metadata or attachments, update Zotero items/tags/Extra, add notes or attachments through the local Codex Zotero Bridge plugin, brainstorm from Zotero evidence, or edit Word DOCX text and add selected Zotero items as live citation fields. Prefer Codex Zotero Bridge for local Zotero item read/write, attachments, notes, and library mutations it supports; use Pyzotero CLI (`zot`) for broad search/browse tasks not covered by the bridge; use Zotero MCP only when already active or explicitly requested. Trigger on Zotero, Codex Zotero Bridge, Pyzotero, zot, Zotero MCP, Word/DOCX Zotero citations, literature searches, reference review, paper brainstorming, metadata, collections, tags, recent items, attachments/notes, full-text retrieval, or Zotero setup."
---

# Zotero Use

## Routing

1. Bridge-first: use the local Codex Zotero Bridge plugin for item-key based Zotero operations it supports: ping, read one item, update fields/Extra/tags, add attachments, and add notes.
2. Use Pyzotero CLI (`zot`) for broad discovery that the bridge does not cover well: search by title/creator/year/tag, list collections, browse recent items, and inspect many metadata records.
3. Use Zotero MCP tools only when they are already active or the user explicitly prefers MCP.
4. Do not add MCP config to `.agents`, Codex skill metadata, or agent config by default.
5. Warn that adding MCP tools to an agent session consumes context/tool-list budget.
6. Treat Zotero library create/update/delete as explicit-write operations; perform them only when the user asks for the change.
7. Avoid raw SQLite. Prefer bridge for supported local writes, Pyzotero for structured search, and MCP only as a requested/available fallback.
8. For narrow DOCX Zotero-field edits, use this skill's OOXML checks. Do not run `soffice`, LibreOffice PDF conversion, PDF2image rendering, or full document-render workflows unless the user explicitly asks or the task is layout-heavy rather than Zotero-field insertion.

## Work Pattern

1. Start by checking whether Codex Zotero Bridge is available when the task involves a known Zotero item key, local write, attachment, note, or bridge-dependent workflow.
2. For broad search, use Pyzotero CLI first to find candidate parent bibliographic items, then use the bridge for supported item-level operations.
3. Inspect metadata for shortlisted parent bibliographic items; avoid citing attachment keys.
4. For a single selected item, check children/attachments and report whether a PDF is available.
5. For brainstorming/review, use the abstract plus PDF/full text when available; if only metadata/abstract was reviewed, say so.
6. For write operations, state the target item keys and requested change before changing Zotero unless the user has already made the exact operation explicit.
7. For Word work, edit text and add live Zotero citation fields with narrow OOXML changes; use structural validation by default.
8. Report Zotero item keys with conclusions, changed fields/attachments/notes, and citation-placement suggestions.
9. Distinguish Zotero evidence from external knowledge or inference.

## Lazy References

- Codex Zotero Bridge local plugin, Python client, endpoints, and safety rules: `references/codex-zotero-bridge.md`
- Pyzotero CLI install, local mode, profiles, and command examples: `references/pyzotero-cli.md`
- Search/query/retrieve/brainstorm from Zotero references: `references/search-retrieve-brainstorm.md`
- Adding Zotero citation fields to Word DOCX files: `references/word-docx-citations.md`
- Zotero MCP server setup, context warning, and MCP tool usage: `references/zotero-mcp.md`
- Troubleshooting and common checks: `references/setup-troubleshooting.md`
