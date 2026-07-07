import json
import os
import argparse
import urllib.error
import urllib.request
from pathlib import Path


CONFIG_PATH = Path(os.environ.get("CODEX_ZOTERO_BRIDGE_CONFIG", Path(__file__).with_name("codex_zotero_bridge_config.json")))


class ZoteroBridge:
    def __init__(self, config_path=CONFIG_PATH):
        config = json.loads(Path(config_path).read_text(encoding="utf-8"))
        self.base_url = config["base_url"].rstrip("/")
        self.token = config["token"]

    def request(self, method, path, data=None):
        body = None if data is None else json.dumps(data, ensure_ascii=False).encode("utf-8")
        request = urllib.request.Request(
            self.base_url + path,
            data=body,
            method=method,
            headers={
                "X-Codex-Zotero-Key": self.token,
                "Content-Type": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            raise RuntimeError(error.read().decode("utf-8")) from error

    def ping(self):
        return self.request("GET", "/ping")

    def get_item(self, item_key, library_id=None):
        suffix = "" if library_id is None else f"?libraryID={library_id}"
        return self.request("GET", f"/items/{item_key}{suffix}")

    def update_item(self, item_key, *, fields=None, extra=None, tags=None, library_id=None):
        payload = {}
        if fields is not None:
            payload["fields"] = fields
        if extra is not None:
            payload["extra"] = extra
        if tags is not None:
            payload["tags"] = tags
        if library_id is not None:
            payload["libraryID"] = library_id
        return self.request("POST", f"/items/{item_key}/update", payload)

    def add_attachment(self, item_key, path, *, mode="import", title=None, library_id=None):
        payload = {"path": str(Path(path).resolve()), "mode": mode}
        if title is not None:
            payload["title"] = title
        if library_id is not None:
            payload["libraryID"] = library_id
        return self.request("POST", f"/items/{item_key}/attachments", payload)

    def add_note(self, item_key, html, *, library_id=None):
        payload = {"html": html}
        if library_id is not None:
            payload["libraryID"] = library_id
        return self.request("POST", f"/items/{item_key}/notes", payload)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test Codex Zotero Bridge connection.")
    parser.add_argument("--config", default=str(CONFIG_PATH))
    args = parser.parse_args()
    print(json.dumps(ZoteroBridge(args.config).ping(), ensure_ascii=False, indent=2))
