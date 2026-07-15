#!/usr/bin/env python3
"""Normalize generated process review form pages before publishing.

Fixes:
- Rename generated form pages from "Matrisi" to "Formu".
- Remove duplicated page title from body.storage.xhtml.
- Rebuild body.view.html with one visible title.
- Rename local folders and update page.yaml + confluence/index.yaml.

This script only touches generated FRM.001 process review forms under:
confluence/pages/000-root-iuc-bidb-spice-2026-level-3/91-ic-denetimler/surec-gozden-gecirmeleri/
"""
from __future__ import annotations

import html
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
CONFLUENCE_DIR = ROOT / "confluence"
TARGET_PARENT = CONFLUENCE_DIR / "pages/000-root-iuc-bidb-spice-2026-level-3/91-ic-denetimler/surec-gozden-gecirmeleri"
INDEX_PATH = CONFLUENCE_DIR / "index.yaml"
REPORT_PATH = ROOT / "reports/process_review_forms_normalization_report.md"

TR_MAP = str.maketrans({
    "İ": "i", "I": "i", "ı": "i", "Ü": "u", "ü": "u",
    "Ç": "c", "ç": "c", "Ş": "s", "ş": "s", "Ö": "o", "ö": "o",
    "Ğ": "g", "ğ": "g",
})

CSS = (
    'body{margin:0;background:#fff;color:#172b4d;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;line-height:1.55}'
    '.confluence-page{max-width:1180px;margin:0 auto;padding:32px 24px 56px}'
    'h1,h2,h3{color:#0f172a;line-height:1.25}'
    'h1{margin-top:0;padding-bottom:12px;border-bottom:1px solid #d8dee4}'
    'table{width:100%;border-collapse:collapse;margin:16px 0;table-layout:auto}'
    'th,td{border:1px solid #c9d1d9;padding:8px 10px;vertical-align:top}'
    'th{background:#f6f8fa;font-weight:600;text-align:left}'
)

FORM_TITLE_RE = re.compile(
    r"İÜC\.BİDB\.FRM\.001 - Süreç Gözden Geçirme (?:Matrisi|Formu) "
    r"\((İÜC\.BİDB\.SRÇ\.\d{3})\)"
)


def slugify(value: str) -> str:
    value = value.translate(TR_MAP).lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return re.sub(r"-+", "-", value).strip("-")


def read_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def write_yaml(path: Path, data: dict[str, Any]) -> None:
    path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")


def e(value: object) -> str:
    return html.escape(str(value), quote=False)


def desired_title(process_code: str) -> str:
    return f"FRM.001 - Süreç Gözden Geçirme Formu ({process_code})"


def strip_leading_h1(body: str) -> str:
    return re.sub(r"^\s*<h1[^>]*>.*?</h1>\s*", "", body, count=1, flags=re.DOTALL | re.IGNORECASE)


def build_view_html(title: str, storage_body: str) -> str:
    return f"""<!doctype html>
<html lang="tr">
<head>
  <meta charset="utf-8">
  <title>{e(title)}</title>
  <style>{CSS}</style>
</head>
<body>
<main class="confluence-page">
<h1>{e(title)}</h1>
{storage_body}
</main>
</body>
</html>
"""


def find_generated_form_folders() -> list[Path]:
    folders: list[Path] = []
    if not TARGET_PARENT.exists():
        return folders
    for page_yaml in sorted(TARGET_PARENT.rglob("page.yaml")):
        folder = page_yaml.parent
        meta = read_yaml(page_yaml)
        title = str(meta.get("title") or "")
        if FORM_TITLE_RE.match(title):
            folders.append(folder)
    return folders


def normalize_folder(folder: Path) -> dict[str, Any]:
    page_yaml = folder / "page.yaml"
    storage_path = folder / "body.storage.xhtml"
    view_path = folder / "body.view.html"

    meta = read_yaml(page_yaml)
    old_title = str(meta.get("title") or "")
    match = FORM_TITLE_RE.match(old_title)
    if not match:
        raise RuntimeError(f"Unexpected form title in {page_yaml}: {old_title}")

    process_code = match.group(1)
    new_title = desired_title(process_code)
    new_slug = slugify(new_title)
    new_folder = TARGET_PARENT / new_slug

    if storage_path.exists():
        storage_body = storage_path.read_text(encoding="utf-8")
    else:
        storage_body = ""
    storage_body = strip_leading_h1(storage_body).strip() + "\n"

    if new_folder != folder:
        if new_folder.exists():
            shutil.rmtree(new_folder)
        folder.rename(new_folder)
        folder = new_folder
        page_yaml = folder / "page.yaml"
        storage_path = folder / "body.storage.xhtml"
        view_path = folder / "body.view.html"

    relative_path = str(folder.relative_to(CONFLUENCE_DIR)).replace("\\", "/")

    meta["title"] = new_title
    meta["slug"] = new_slug
    meta["relative_path"] = relative_path
    meta["storage_file"] = "body.storage.xhtml"
    meta["view_file"] = "body.view.html"
    meta["document_code"] = "FRM.001"
    meta["related_process_code"] = process_code

    storage_path.write_text(storage_body, encoding="utf-8")
    view_path.write_text(build_view_html(new_title, storage_body), encoding="utf-8")
    write_yaml(page_yaml, meta)

    return {
        "old_title": old_title,
        "new_title": new_title,
        "process_code": process_code,
        "page_id": str(meta.get("page_id") or ""),
        "relative_path": relative_path,
        "slug": new_slug,
    }


def update_index(normalized: list[dict[str, Any]]) -> None:
    if not INDEX_PATH.exists():
        return

    data = read_yaml(INDEX_PATH)
    pages = data.get("pages", []) or []
    by_process = {item["process_code"]: item for item in normalized}
    output = []
    seen_processes = set()

    for page in pages:
        title = str(page.get("title") or "")
        match = FORM_TITLE_RE.match(title)
        if not match:
            output.append(page)
            continue

        process_code = match.group(1)
        if process_code in seen_processes:
            continue
        seen_processes.add(process_code)
        item = by_process.get(process_code)
        if not item:
            continue

        page["title"] = item["new_title"]
        page["page_id"] = item["page_id"]
        page["relative_path"] = item["relative_path"]
        page["slug"] = item["slug"]
        page["storage_file"] = f"{item['relative_path']}/body.storage.xhtml"
        page["view_file"] = f"{item['relative_path']}/body.view.html"
        output.append(page)

    data["pages"] = output
    data["total_page_count"] = len(output)
    data["exported_at"] = datetime.now(timezone.utc).isoformat()
    write_yaml(INDEX_PATH, data)


def write_report(normalized: list[dict[str, Any]]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Süreç Gözden Geçirme Formları Normalizasyon Raporu",
        "",
        f"Düzeltilen form sayısı: {len(normalized)}",
        "",
        "## Düzeltmeler",
    ]
    for item in normalized:
        lines.append(f"- {item['process_code']}: {item['old_title']} → {item['new_title']}")
    lines.append("")
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    normalized = [normalize_folder(folder) for folder in find_generated_form_folders()]
    update_index(normalized)
    write_report(normalized)
    print(f"[DONE] {len(normalized)} süreç gözden geçirme formu normalize edildi.")
    print(f"[REPORT] {REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
