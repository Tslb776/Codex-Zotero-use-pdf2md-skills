import argparse
import datetime as dt
import html
import json
import os
import re
import shutil
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

import requests


MINERU_BASE = "https://mineru.net/api/v4"
MARKDOWN_TITLE = "MinerU VLM Markdown Full Text"
HTML_TITLE = "MinerU VLM HTML Reader"


class ZoteroBridge:
    def __init__(self, config_path):
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
            with urllib.request.urlopen(request, timeout=60) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            raise RuntimeError(error.read().decode("utf-8", errors="replace")) from error

    def ping(self):
        return self.request("GET", "/ping")

    def add_attachment(self, item_key, path, *, mode="link", title=None):
        payload = {"path": str(Path(path).resolve()), "mode": mode}
        if title:
            payload["title"] = title
        return self.request("POST", f"/items/{item_key}/attachments", payload)


def get_json(url):
    with urllib.request.urlopen(url, timeout=90) as response:
        return json.load(response)


def fetch_all(url):
    items = []
    start = 0
    while True:
        sep = "&" if "?" in url else "?"
        batch = get_json(f"{url}{sep}limit=100&start={start}")
        items.extend(batch)
        if len(batch) < 100:
            return items
        start += len(batch)


def api_json(response):
    response.raise_for_status()
    result = response.json()
    if result.get("code") != 0:
        raise RuntimeError(f"MinerU API error: {result.get('code')} {result.get('msg')}")
    return result


def safe_extract(archive, target):
    target = Path(target).resolve()
    for member in archive.infolist():
        destination = (target / member.filename).resolve()
        if target not in destination.parents and destination != target:
            raise RuntimeError(f"Unsafe ZIP member: {member.filename}")
    archive.extractall(target)


def simple_markdown_to_html(md_text, title):
    body = html.escape(md_text)
    body = re.sub(r"^# (.+)$", r"<h1>\1</h1>", body, flags=re.M)
    body = re.sub(r"^## (.+)$", r"<h2>\1</h2>", body, flags=re.M)
    body = re.sub(r"^### (.+)$", r"<h3>\1</h3>", body, flags=re.M)
    body = body.replace("\n\n", "</p><p>").replace("\n", "<br>\n")
    return (
        "<!doctype html><html><head><meta charset=\"utf-8\">"
        f"<title>{html.escape(title)}</title>"
        "<style>body{font-family:Segoe UI,Arial,sans-serif;line-height:1.65;max-width:960px;margin:32px auto;padding:0 24px;}img{max-width:100%;}</style>"
        "</head><body><p>" + body + "</p></body></html>"
    )


def first_pdf_path(child, storage_root):
    data = child["data"]
    raw_path = data.get("path") or ""
    if raw_path and not raw_path.startswith("attachments:"):
        candidate = Path(raw_path)
        if candidate.exists() and candidate.suffix.lower() == ".pdf":
            return candidate
    folder = storage_root / child["key"]
    matches = sorted(folder.glob("*.pdf"))
    return matches[0] if matches else None


def likely_scan(pdf_path):
    try:
        from pypdf import PdfReader

        reader = PdfReader(str(pdf_path))
        text = " ".join((page.extract_text() or "") for page in reader.pages[:2])
        return len(text.strip()) < 200, len(reader.pages)
    except Exception:
        return True, None


def load_target_items(args):
    if args.item_key:
        return [get_json(f"{args.zotero_api.rstrip('/')}/items/{key}") for key in args.item_key]
    if not args.collection_key:
        raise RuntimeError("Provide --collection-key or --item-key")
    encoded = urllib.parse.quote(args.collection_key)
    return fetch_all(f"{args.zotero_api.rstrip('/')}/collections/{encoded}/items/top")


def build_jobs(args):
    storage_root = Path(args.storage_root)
    jobs = []
    for wrapped in load_target_items(args):
        data = wrapped["data"]
        key = data["key"]
        title = data.get("title", "")
        if args.item_type and data.get("itemType") != args.item_type:
            continue
        if args.title and args.title.lower() not in title.lower():
            continue
        children = fetch_all(f"{args.zotero_api.rstrip('/')}/items/{key}/children")
        pdf_children = [
            child for child in children
            if child["data"].get("itemType") == "attachment"
            and child["data"].get("contentType") == "application/pdf"
        ]
        pdf_paths = []
        for child in pdf_children:
            path = first_pdf_path(child, storage_root)
            if path:
                pdf_paths.append(str(path))
        result_dir = Path(args.output_dir) / key / "mineru-result"
        titles = {child["data"].get("title", "") for child in children}
        scan = False
        pages = None
        if pdf_paths and not args.dry_run:
            scan, pages = likely_scan(Path(pdf_paths[0]))
        jobs.append(
            {
                "key": key,
                "title": title,
                "itemType": data.get("itemType", ""),
                "pdfPaths": pdf_paths,
                "pdfExists": bool(pdf_paths),
                "pages": pages,
                "likelyScan": scan,
                "resultDir": str(result_dir),
                "localMarkdownExists": (result_dir / "full.md").exists(),
                "localHtmlExists": (result_dir / "full.html").exists(),
                "existingMarkdownAttachment": MARKDOWN_TITLE in titles,
                "existingHtmlAttachment": HTML_TITLE in titles,
            }
        )
    return jobs


def save(path, state):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def download_result(record, output_dir, title):
    result_dir = Path(output_dir) / record["data_id"] / "mineru-result"
    zip_path = result_dir.parent / "mineru-result.zip"
    result_dir.parent.mkdir(parents=True, exist_ok=True)
    response = requests.get(record["full_zip_url"], timeout=300)
    response.raise_for_status()
    zip_path.write_bytes(response.content)
    if result_dir.exists():
        shutil.rmtree(result_dir)
    result_dir.mkdir(parents=True)
    with zipfile.ZipFile(zip_path) as archive:
        safe_extract(archive, result_dir)
    md = result_dir / "full.md"
    html_path = result_dir / "full.html"
    if not md.exists():
        raise RuntimeError(f"MinerU result missing full.md for {record['data_id']}")
    if not html_path.exists():
        html_path.write_text(simple_markdown_to_html(md.read_text(encoding="utf-8", errors="replace"), title), encoding="utf-8")
    return result_dir


def main():
    parser = argparse.ArgumentParser(description="Convert Zotero PDF attachments to MinerU Markdown/HTML and attach results back to Zotero.")
    parser.add_argument("--root", default=str(Path.cwd()))
    parser.add_argument("--collection-key")
    parser.add_argument("--item-key", action="append")
    parser.add_argument("--title")
    parser.add_argument("--item-type")
    parser.add_argument("--storage-root", default=os.environ.get("ZOTERO_STORAGE_ROOT", str(Path.home() / "Zotero" / "storage")))
    parser.add_argument("--zotero-api", default=os.environ.get("ZOTERO_API"))
    parser.add_argument("--bridge-config")
    parser.add_argument("--output-dir")
    parser.add_argument("--checkpoint")
    parser.add_argument("--model-version", default="vlm")
    parser.add_argument("--language", default="auto")
    parser.add_argument("--poll-seconds", type=int, default=10)
    parser.add_argument("--timeout-seconds", type=int, default=7200)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if not args.zotero_api:
        raise RuntimeError("Provide --zotero-api or set ZOTERO_API, for example http://localhost:23119/api/users/<USER_ID>")

    root = Path(args.root)
    args.output_dir = args.output_dir or str(root / "mineru_outputs")
    args.bridge_config = args.bridge_config or str(root / "zotero_exports" / "codex_zotero_bridge_config.json")
    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    args.checkpoint = args.checkpoint or str(root / "zotero_exports" / f"zotero_mineru_conversion_{stamp}.json")

    jobs = build_jobs(args)
    pending = [
        job for job in jobs
        if job["pdfExists"]
        and (
            args.force
            or not (job["localMarkdownExists"] and job["localHtmlExists"] and job["existingMarkdownAttachment"] and job["existingHtmlAttachment"])
        )
    ]
    summary = {
        "totalTargetItems": len(jobs),
        "withPdf": sum(job["pdfExists"] for job in jobs),
        "withoutPdf": sum(not job["pdfExists"] for job in jobs),
        "pendingConversionOrAttach": len(pending),
        "jobs": jobs,
    }
    print(json.dumps({k: v for k, v in summary.items() if k != "jobs"}, ensure_ascii=False, indent=2))
    if args.dry_run:
        save(args.checkpoint, summary)
        print(args.checkpoint)
        return
    if not pending:
        save(args.checkpoint, summary)
        print("No pending items.")
        return

    token = os.environ.get("MINERU_API_TOKEN")
    if not token:
        raise RuntimeError("MINERU_API_TOKEN is required")
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    state = {"batchId": None, "items": {job["key"]: job for job in pending}}

    files = []
    for job in pending:
        pdf = Path(job["pdfPaths"][0])
        files.append({"name": f"{job['key']}_{pdf.name}", "data_id": job["key"], "is_ocr": bool(job["likelyScan"])})
    payload = {
        "files": files,
        "model_version": args.model_version,
        "language": args.language,
        "enable_formula": True,
        "enable_table": True,
        "extra_formats": ["html"],
    }
    result = api_json(requests.post(f"{MINERU_BASE}/file-urls/batch", headers=headers, json=payload, timeout=90))
    state["batchId"] = result["data"]["batch_id"]
    save(args.checkpoint, state)

    for job, upload_url in zip(pending, result["data"]["file_urls"]):
        with Path(job["pdfPaths"][0]).open("rb") as file:
            response = requests.put(upload_url, data=file, timeout=300)
            response.raise_for_status()
        state["items"][job["key"]]["state"] = "uploaded"
        save(args.checkpoint, state)
        print(f"uploaded {job['key']} ocr={job['likelyScan']} {job['title'][:80]}")

    deadline = time.time() + args.timeout_seconds
    while time.time() < deadline:
        result = api_json(requests.get(f"{MINERU_BASE}/extract-results/batch/{state['batchId']}", headers=headers, timeout=90))
        counts = {}
        for record in result["data"]["extract_result"]:
            key = record.get("data_id")
            if key not in state["items"]:
                continue
            status = record["state"]
            counts[status] = counts.get(status, 0) + 1
            item = state["items"][key]
            item["state"] = status
            item["progress"] = record.get("extract_progress", {})
            if status == "failed":
                item["error"] = record.get("err_msg")
            if status == "done" and not item.get("downloaded"):
                result_dir = download_result(record, args.output_dir, item["title"])
                md = result_dir / "full.md"
                html_path = result_dir / "full.html"
                item["downloaded"] = True
                item["resultDir"] = str(result_dir)
                item["markdownCharacters"] = len(md.read_text(encoding="utf-8", errors="replace"))
                item["htmlBytes"] = html_path.stat().st_size
                item["imageCount"] = len(list((result_dir / "images").glob("*")))
                print(f"downloaded {key} chars={item['markdownCharacters']} images={item['imageCount']}")
        save(args.checkpoint, state)
        print(json.dumps(counts, ensure_ascii=False))
        if all(item.get("downloaded") or item.get("state") == "failed" for item in state["items"].values()):
            break
        time.sleep(args.poll_seconds)

    bridge = ZoteroBridge(args.bridge_config)
    bridge.ping()
    for key, item in state["items"].items():
        if item.get("state") == "failed":
            continue
        result_dir = Path(item.get("resultDir") or item["resultDir"])
        md = result_dir / "full.md"
        html_path = result_dir / "full.html"
        if not item.get("existingMarkdownAttachment"):
            item["markdownAttachment"] = bridge.add_attachment(key, md, mode="link", title=MARKDOWN_TITLE)
        if not item.get("existingHtmlAttachment"):
            item["htmlAttachment"] = bridge.add_attachment(key, html_path, mode="link", title=HTML_TITLE)
        item["attached"] = True
        save(args.checkpoint, state)
        print(f"attached {key}")

    print(json.dumps({
        "requested": len(state["items"]),
        "downloaded": sum(bool(item.get("downloaded")) for item in state["items"].values()),
        "attached": sum(bool(item.get("attached")) for item in state["items"].values()),
        "failed": {key: item.get("error") for key, item in state["items"].items() if item.get("state") == "failed"},
        "checkpoint": args.checkpoint,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
