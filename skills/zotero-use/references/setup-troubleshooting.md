# Setup Troubleshooting

Load this for failures after using `references/pyzotero-cli.md` or `references/zotero-mcp.md`.

## Pyzotero CLI Checks

```bash
command -v zot
zot --help
uv tool list | rg -i 'pyzotero|zotero'
```

If `zot` is missing:

```bash
uv tool install pyzotero-cli -U
uv tool update-shell
hash -r
```

If local mode fails:

- Confirm Zotero is open.
- Confirm Zotero Settings -> Advanced -> Allow other applications on this computer to communicate with Zotero is enabled.
- Use `--local --library-id 0 --library-type user` before the command group.

## API/Profile Checks

For API-backed profiles:

- Personal library type is `user`.
- Group library type is `group`.
- Config file: `~/.config/zotcli/config.ini`.
- Precedence: command-line flags, environment variables, active profile.

Relevant environment variables:

```bash
ZOTERO_API_KEY
ZOTERO_LIBRARY_ID
ZOTERO_LIBRARY_TYPE
```

Do not expose API keys in responses or logs.

## MCP Checks

If using Zotero MCP externally:

```bash
command -v zotero-mcp
zotero-mcp version
zotero-mcp setup-info
zotero-mcp db-status
```

If search/database behavior looks stale:

```bash
zotero-mcp update-db --force-rebuild
```

## DOCX Render Checks

Routine Zotero citation insertion should use structural OOXML validation, not full rendering.

If the user explicitly asks for full DOCX visual QA, use a local document-rendering workflow available in their environment. For Codex Desktop users, prefer the installed document-rendering skill or runtime helper. For a custom setup, install the required PDF/rendering dependencies in a dedicated virtual environment and pass the target `.docx` plus an output directory.

```bash
python path/to/render_docx.py file.docx --output_dir path/to/render-output --emit_pdf --verbose
```

If LibreOffice or the renderer fails, first confirm that LibreOffice is installed and callable from the same terminal, then verify that the Python environment has the renderer dependencies such as `pdf2image` and Poppler.
