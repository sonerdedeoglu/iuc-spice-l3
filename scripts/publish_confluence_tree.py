#!/usr/bin/env python3
"""Publish the local exported Confluence tree back to Confluence.

This script is intentionally generic. It starts from the exported root tree under
confluence/pages/ and publishes every page that has page.yaml + body.storage.xhtml.

It creates missing pages, updates existing pages, and preserves the local tree's
parent-child structure. It does not delete remote pages.
"""
from __future__ import annotations

import argparse
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from config import SPACE_KEY
from confluence_client import ConfluenceClient

ROOT = Path(__file__).resolve().parents[1]
CONFLUENCE_DIR = ROOT / "confluence"
PAGES_DIR = CONFLUENCE_DIR / "pages"
INDEX_PATH = CONFLUENCE_DIR / "index.yaml"
REPORT_PATH = ROOT / "reports/confluence_tree_publish_report.md"


class PublishError(RuntimeError):
    pass


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def write_yaml(path: Path, data: dict[str, Any]) -> None:
    path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def normalize_body(value: str) -> str:
    return value.strip()


def hash_body(value: str) -> str:
    return hashlib.sha256(normalize_body(value).encode("utf-8")).hexdigest()


def find_page_folder_by_relative_path(relative_path: str) -> Path | None:
    path = CONFLUENCE_DIR / relative_path
    return path if path.exists() else None


def discover_pages() -> list[dict[str, Any]]:
    if not PAGES_DIR.exists():
        raise FileNotFoundError(f"Confluence pages folder not found: {PAGES_DIR}")

    records: list[dict[str, Any]] = []
    for page_yaml in sorted(PAGES_DIR.rglob("page.yaml")):
        folder = page_yaml.parent
        body_path = folder / "body.storage.xhtml"
        if not body_path.exists():
            continue
        metadata = load_yaml(page_yaml)
        title = metadata.get("title")
        if not title:
            raise PublishError(f"Missing title in {page_yaml}")
        relative_path = str(folder.relative_to(CONFLUENCE_DIR)).replace("\\", "/")
        depth = int(metadata.get("depth", len(folder.relative_to(PAGES_DIR).parts) - 1))
        records.append(
            {
                "folder": folder,
                "page_yaml": page_yaml,
                "body_path": body_path,
                "metadata": metadata,
                "title": title,
                "relative_path": relative_path,
                "depth": depth,
                "page_id": str(metadata.get("page_id") or "").strip(),
                "parent_id": str(metadata.get("parent_id") or "").strip(),
                "parent_title": str(metadata.get("parent_title") or "").strip(),
            }
        )

    records.sort(key=lambda item: (item["depth"], item["relative_path"]))
    return records


def load_index_pages() -> list[dict[str, Any]]:
    if not INDEX_PATH.exists():
        return []
    return load_yaml(INDEX_PATH).get("pages", []) or []


def update_index_page_id(relative_path: str, page_id: str) -> None:
    if not INDEX_PATH.exists():
        return
    data = load_yaml(INDEX_PATH)
    changed = False
    for page in data.get("pages", []) or []:
        if page.get("relative_path") == relative_path:
            if str(page.get("page_id") or "") != str(page_id):
                page["page_id"] = str(page_id)
                changed = True
    if changed:
        data["exported_at"] = datetime.now(timezone.utc).isoformat()
        write_yaml(INDEX_PATH, data)


def find_existing_page(client: ConfluenceClient, title: str) -> dict[str, Any] | None:
    result = client.find_page(SPACE_KEY, title)
    results = result.get("results", [])
    if not results:
        return None
    return results[0]


def get_existing_by_id(client: ConfluenceClient, page_id: str) -> dict[str, Any] | None:
    if not page_id:
        return None
    try:
        return client.get_page(page_id)
    except Exception:
        return None


def resolve_parent_id(record: dict[str, Any], path_to_id: dict[str, str]) -> str:
    if record["depth"] == 0:
        return ""

    parent_folder = record["folder"].parent
    parent_relative_path = str(parent_folder.relative_to(CONFLUENCE_DIR)).replace("\\", "/")
    parent_id = path_to_id.get(parent_relative_path)
    if parent_id:
        return parent_id

    metadata_parent_id = record["parent_id"]
    if metadata_parent_id:
        return metadata_parent_id

    raise PublishError(
        f"Parent page id could not be resolved for {record['title']} "
        f"(parent path: {parent_relative_path})"
    )


def update_page_metadata(record: dict[str, Any], page_id: str, version: Any | None = None) -> None:
    metadata = record["metadata"]
    metadata["page_id"] = str(page_id)
    metadata["space"] = SPACE_KEY
    metadata["status"] = "active"
    metadata["storage_file"] = "body.storage.xhtml"
    metadata["view_file"] = "body.view.html"
    if version is not None:
        metadata["version"] = version
    write_yaml(record["page_yaml"], metadata)
    update_index_page_id(record["relative_path"], str(page_id))


def publish_record(client: ConfluenceClient, record: dict[str, Any], path_to_id: dict[str, str], dry_run: bool) -> dict[str, Any]:
    title = record["title"]
    body = read_text(record["body_path"])
    parent_id = resolve_parent_id(record, path_to_id)

    existing = get_existing_by_id(client, record["page_id"])
    if existing is None:
        existing = find_existing_page(client, title)

    if existing is None:
        if record["depth"] == 0:
            raise PublishError(f"Root page not found in Confluence: {title}")
        action = "CREATE"
        page_id = ""
        version_number = None
        changed = True
    else:
        page_id = str(existing["id"])
        version_number = int(existing["version"]["number"])
        existing_body = existing.get("body", {}).get("storage", {}).get("value", "")
        changed = hash_body(existing_body) != hash_body(body)
        action = "UPDATE" if changed else "SKIP"

    if dry_run:
        print(f"[DRY-RUN] {action} {title}")
        return {
            "title": title,
            "action": action,
            "page_id": page_id,
            "changed": changed,
            "relative_path": record["relative_path"],
        }

    if action == "CREATE":
        created = client.create_page(SPACE_KEY, parent_id, title, body)
        page_id = str(created["id"])
        update_page_metadata(record, page_id, created.get("version", {}).get("number"))
        print(f"[CREATE] {title}")
    elif action == "UPDATE":
        updated = client.update_page(page_id, SPACE_KEY, title, body, version_number + 1)
        update_page_metadata(record, page_id, updated.get("version", {}).get("number"))
        print(f"[UPDATE] {title}")
    else:
        update_page_metadata(record, page_id, version_number)
        print(f"[SKIP] {title}")

    return {
        "title": title,
        "action": action,
        "page_id": page_id,
        "changed": changed,
        "relative_path": record["relative_path"],
    }


def write_report(results: list[dict[str, Any]], dry_run: bool) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    counts: dict[str, int] = {}
    for result in results:
        counts[result["action"]] = counts.get(result["action"], 0) + 1

    lines = [
        "# Confluence Tree Publish Raporu",
        "",
        f"Çalışma modu: {'DRY-RUN' if dry_run else 'NORMAL'}",
        f"Zaman: {datetime.now(timezone.utc).isoformat()}",
        f"Kök klasör: `{PAGES_DIR.relative_to(ROOT)}`",
        "",
        "## Özet",
        f"- Toplam sayfa: {len(results)}",
        f"- Oluşturulacak/Oluşturulan: {counts.get('CREATE', 0)}",
        f"- Güncellenecek/Güncellenen: {counts.get('UPDATE', 0)}",
        f"- Değişiklik olmayan: {counts.get('SKIP', 0)}",
        "",
        "## Sayfalar",
    ]
    for result in results:
        lines.append(f"- {result['action']} — {result['title']} — `{result['relative_path']}`")
    lines.append("")
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish local Confluence export tree to Confluence")
    parser.add_argument("--dry-run", action="store_true", help="Show planned create/update/skip actions without writing to Confluence")
    args = parser.parse_args()

    records = discover_pages()
    client = ConfluenceClient()
    path_to_id: dict[str, str] = {}
    results: list[dict[str, Any]] = []

    for record in records:
        result = publish_record(client, record, path_to_id, args.dry_run)
        page_id = result.get("page_id") or str(record["metadata"].get("page_id") or "")
        if page_id:
            path_to_id[record["relative_path"]] = str(page_id)
        results.append(result)

    write_report(results, args.dry_run)
    print(f"[REPORT] {REPORT_PATH.relative_to(ROOT)}")
    print(f"[DONE] {'Dry-run completed' if args.dry_run else 'Confluence tree published'}: {len(results)} pages processed.")


if __name__ == "__main__":
    main()
