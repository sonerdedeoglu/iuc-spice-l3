#!/usr/bin/env python3
"""Move each generated process review form under its related process page locally.

The generic publisher will then move the Confluence pages to match this local tree.
The register page under 91 - İç Denetimler / Süreç Gözden Geçirmeleri is kept as a
parent/register page and will no longer contain the generated FRM.001 pages.
"""
from __future__ import annotations

import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
CONFLUENCE_DIR = ROOT / "confluence"
PAGES_ROOT = CONFLUENCE_DIR / "pages/000-root-iuc-bidb-spice-2026-level-3"
PROCESS_ROOT = PAGES_ROOT / "01-surec-dokumanlari"
REVIEW_PARENT = PAGES_ROOT / "91-ic-denetimler/surec-gozden-gecirmeleri"
INDEX_PATH = CONFLUENCE_DIR / "index.yaml"
REPORT_PATH = ROOT / "reports/process_review_forms_move_report.md"

FORM_TITLE_RE = re.compile(
    r"İÜC\.BİDB\.FRM\.001 - Süreç Gözden Geçirme Formu "
    r"\((İÜC\.BİDB\.SRÇ\.(\d{3}))\)"
)
PROCESS_TITLE_RE = re.compile(r"İÜC\.BİDB\.SRÇ\.(\d{3}) - .+")


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def write_yaml(path: Path, data: dict[str, Any]) -> None:
    path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")


def process_folders() -> dict[str, Path]:
    result: dict[str, Path] = {}
    for page_yaml in PROCESS_ROOT.glob("*/page.yaml"):
        metadata = load_yaml(page_yaml)
        title = str(metadata.get("title") or "")
        match = PROCESS_TITLE_RE.match(title)
        if not match:
            continue
        result[f"SRÇ.{match.group(1)}"] = page_yaml.parent
    return result


def review_form_folders() -> list[tuple[str, Path]]:
    result: list[tuple[str, Path]] = []
    for page_yaml in REVIEW_PARENT.glob("*/page.yaml"):
        metadata = load_yaml(page_yaml)
        title = str(metadata.get("title") or "")
        match = FORM_TITLE_RE.match(title)
        if not match:
            continue
        result.append((match.group(1), page_yaml.parent))
    return sorted(result, key=lambda item: item[0])


def update_index_path(old_relative_path: str, new_relative_path: str, parent_id: str, depth: int) -> None:
    if not INDEX_PATH.exists():
        return
    data = load_yaml(INDEX_PATH)
    changed = False
    for page in data.get("pages", []) or []:
        current_path = str(page.get("relative_path") or "")
        if current_path == old_relative_path:
            page["relative_path"] = new_relative_path
            page["parent_id"] = str(parent_id)
            page["depth"] = depth
            page["storage_file"] = f"{new_relative_path}/body.storage.xhtml"
            page["view_file"] = f"{new_relative_path}/body.view.html"
            changed = True
            continue
        prefix = old_relative_path + "/"
        if current_path.startswith(prefix):
            suffix = current_path[len(prefix):]
            page["relative_path"] = f"{new_relative_path}/{suffix}"
            if str(page.get("storage_file") or "").startswith(prefix):
                page["storage_file"] = f"{new_relative_path}/{suffix}/body.storage.xhtml"
            if str(page.get("view_file") or "").startswith(prefix):
                page["view_file"] = f"{new_relative_path}/{suffix}/body.view.html"
            changed = True
    if changed:
        data["exported_at"] = datetime.now(timezone.utc).isoformat()
        write_yaml(INDEX_PATH, data)


def move_one(process_code: str, form_folder: Path, target_process_folder: Path) -> dict[str, str]:
    old_relative_path = str(form_folder.relative_to(CONFLUENCE_DIR)).replace("\\", "/")
    target_folder = target_process_folder / form_folder.name
    if target_folder.exists() and target_folder != form_folder:
        shutil.rmtree(target_folder)
    target_process_folder.mkdir(parents=True, exist_ok=True)
    shutil.move(str(form_folder), str(target_folder))

    process_meta = load_yaml(target_process_folder / "page.yaml")
    parent_id = str(process_meta.get("page_id") or "")
    parent_title = str(process_meta.get("title") or "")
    process_depth = int(process_meta.get("depth", 2))
    new_depth = process_depth + 1
    new_relative_path = str(target_folder.relative_to(CONFLUENCE_DIR)).replace("\\", "/")

    form_yaml = target_folder / "page.yaml"
    form_meta = load_yaml(form_yaml)
    form_meta["parent_id"] = parent_id
    form_meta["parent_title"] = parent_title
    form_meta["depth"] = new_depth
    form_meta["relative_path"] = new_relative_path
    form_meta["storage_file"] = "body.storage.xhtml"
    form_meta["view_file"] = "body.view.html"
    write_yaml(form_yaml, form_meta)

    update_index_path(old_relative_path, new_relative_path, parent_id, new_depth)

    return {
        "process_code": process_code,
        "title": str(form_meta.get("title") or ""),
        "old_path": old_relative_path,
        "new_path": new_relative_path,
        "parent_title": parent_title,
    }


def write_report(moved: list[dict[str, str]], missing: list[str]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Süreç Gözden Geçirme Formları Taşıma Raporu",
        "",
        f"Taşınan form sayısı: {len(moved)}",
        f"Eksik süreç klasörü/form sayısı: {len(missing)}",
        "",
        "## Taşınan Formlar",
    ]
    for item in moved:
        lines.append(f"- {item['process_code']} → {item['parent_title']} — `{item['new_path']}`")
    if missing:
        lines.extend(["", "## Eksikler"])
        lines.extend(f"- {item}" for item in missing)
    lines.append("")
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    processes = process_folders()
    forms = review_form_folders()
    moved: list[dict[str, str]] = []
    missing: list[str] = []

    for process_code, form_folder in forms:
        target_process_folder = processes.get(process_code)
        if not target_process_folder:
            missing.append(f"{process_code}: süreç klasörü bulunamadı")
            continue
        moved.append(move_one(process_code, form_folder, target_process_folder))

    write_report(moved, missing)
    print(f"[DONE] {len(moved)} süreç gözden geçirme formu süreç klasörlerinin altına taşındı.")
    if missing:
        print(f"[WARN] {len(missing)} eksik kayıt var. Raporu kontrol et.")
    print(f"[REPORT] {REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
