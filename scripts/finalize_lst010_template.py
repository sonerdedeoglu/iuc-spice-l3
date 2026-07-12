#!/usr/bin/env python3
"""Finalize the LST.010 template candidate.

Actions:
- Move the currently active LST.010 template page under `Arşiv - Kaldırılan Şablonlar`
  and rename it with `KALDIRILDI - ...`.
- Promote the draft LST.010 template candidate to the active template path/title.
- Keep the current active page's Confluence page_id on the archived page.
- Keep the promoted candidate as a new page to be created by the publisher.
- Update confluence/index.yaml entries accordingly.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import shutil
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "confluence/index.yaml"
ROOT_PAGE = ROOT / "confluence/pages/000-root-iuc-bidb-spice-2026-level-3"
TEMPLATES_DIR = ROOT_PAGE / "02-sablonlar"
ARCHIVE_DIR = TEMPLATES_DIR / "arsiv-kaldirilan-sablonlar"

OLD_SLUG = "iuc-bidb-lst-010-s-surec-rol-yetki-ve-raci-matrisi-sablonu"
DRAFT_SLUG = "taslak-iuc-bidb-lst-010-s-surec-rol-yetki-ve-raci-matrisi-sablonu"
ARCHIVED_SLUG = "kaldirildi-iuc-bidb-lst-010-s-surec-rol-yetki-ve-raci-matrisi-sablonu"

OLD_DIR = TEMPLATES_DIR / OLD_SLUG
DRAFT_DIR = TEMPLATES_DIR / DRAFT_SLUG
ARCHIVED_DIR = ARCHIVE_DIR / ARCHIVED_SLUG

ACTIVE_TITLE = "İÜC.BİDB.LST.010.Ş - Süreç Rol Yetki ve RACI Matrisi Şablonu"
ARCHIVED_TITLE = "KALDIRILDI - İÜC.BİDB.LST.010.Ş - Süreç Rol Yetki ve RACI Matrisi Şablonu"
TEMPLATES_PARENT_ID = "137265785"
TEMPLATES_PARENT_TITLE = "02 - Şablonlar"
ARCHIVE_PARENT_TITLE = "Arşiv - Kaldırılan Şablonlar"

ACTIVE_REL = f"pages/000-root-iuc-bidb-spice-2026-level-3/02-sablonlar/{OLD_SLUG}"
DRAFT_REL = f"pages/000-root-iuc-bidb-spice-2026-level-3/02-sablonlar/{DRAFT_SLUG}"
ARCHIVED_REL = f"pages/000-root-iuc-bidb-spice-2026-level-3/02-sablonlar/arsiv-kaldirilan-sablonlar/{ARCHIVED_SLUG}"


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def write_yaml(path: Path, data: dict[str, Any]) -> None:
    path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")


def relative_path(path: Path) -> str:
    return str(path.relative_to(ROOT / "confluence")).replace("\\", "/")


def archive_parent_id() -> str:
    meta = load_yaml(ARCHIVE_DIR / "page.yaml")
    return str(meta.get("page_id") or "")


def update_page_meta(page_dir: Path, *, title: str, slug: str, rel: str, parent_id: str, parent_title: str, status: str) -> None:
    meta_path = page_dir / "page.yaml"
    meta = load_yaml(meta_path)
    meta.update({
        "title": title,
        "slug": slug,
        "relative_path": rel,
        "parent_id": parent_id,
        "parent_title": parent_title,
        "status": status,
        "storage_file": "body.storage.xhtml",
        "view_file": "body.view.html",
        "exported_at": datetime.now(timezone.utc).isoformat(),
    })
    write_yaml(meta_path, meta)


def replace_title_in_files(page_dir: Path, old: str, new: str) -> None:
    for filename in ("body.storage.xhtml", "body.view.html"):
        path = page_dir / filename
        if path.exists():
            text = path.read_text(encoding="utf-8")
            text = text.replace(old, new)
            text = text.replace("TASLAK - ", "")
            path.write_text(text, encoding="utf-8")


def update_index() -> None:
    index = load_yaml(INDEX_PATH)
    pages = index.setdefault("pages", [])

    def remove(rel: str) -> None:
        pages[:] = [p for p in pages if p.get("relative_path") != rel]

    def upsert(entry: dict[str, Any]) -> None:
        existing = next((p for p in pages if p.get("relative_path") == entry["relative_path"]), None)
        if existing:
            existing.update(entry)
        else:
            pages.append(entry)

    archived_meta = load_yaml(ARCHIVED_DIR / "page.yaml")
    active_meta = load_yaml(OLD_DIR / "page.yaml")

    remove(DRAFT_REL)
    remove(ACTIVE_REL)
    remove(ARCHIVED_REL)

    upsert({
        "page_id": str(archived_meta.get("page_id") or ""),
        "title": ARCHIVED_TITLE,
        "parent_id": str(archived_meta.get("parent_id") or archive_parent_id()),
        "depth": 3,
        "relative_path": ARCHIVED_REL,
        "slug": ARCHIVED_SLUG,
        "storage_file": f"{ARCHIVED_REL}/body.storage.xhtml",
        "view_file": f"{ARCHIVED_REL}/body.view.html",
    })
    upsert({
        "page_id": str(active_meta.get("page_id") or ""),
        "title": ACTIVE_TITLE,
        "parent_id": TEMPLATES_PARENT_ID,
        "depth": 2,
        "relative_path": ACTIVE_REL,
        "slug": OLD_SLUG,
        "storage_file": f"{ACTIVE_REL}/body.storage.xhtml",
        "view_file": f"{ACTIVE_REL}/body.view.html",
    })

    index["total_page_count"] = len(pages)
    write_yaml(INDEX_PATH, index)


def main() -> None:
    if not OLD_DIR.exists():
        raise FileNotFoundError(f"Current active LST.010 template page not found: {OLD_DIR}")
    if not DRAFT_DIR.exists():
        raise FileNotFoundError(f"Draft LST.010 template candidate page not found: {DRAFT_DIR}")
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    if ARCHIVED_DIR.exists():
        shutil.rmtree(ARCHIVED_DIR)

    shutil.move(str(OLD_DIR), str(ARCHIVED_DIR))
    shutil.move(str(DRAFT_DIR), str(OLD_DIR))

    archive_pid = archive_parent_id()
    update_page_meta(
        ARCHIVED_DIR,
        title=ARCHIVED_TITLE,
        slug=ARCHIVED_SLUG,
        rel=ARCHIVED_REL,
        parent_id=archive_pid,
        parent_title=ARCHIVE_PARENT_TITLE,
        status="archived",
    )
    replace_title_in_files(ARCHIVED_DIR, ACTIVE_TITLE, ARCHIVED_TITLE)

    update_page_meta(
        OLD_DIR,
        title=ACTIVE_TITLE,
        slug=OLD_SLUG,
        rel=ACTIVE_REL,
        parent_id=TEMPLATES_PARENT_ID,
        parent_title=TEMPLATES_PARENT_TITLE,
        status="active",
    )
    replace_title_in_files(OLD_DIR, "TASLAK - " + ACTIVE_TITLE, ACTIVE_TITLE)

    update_index()

    print("[DONE] LST.010 template candidate promoted to active template.")
    print(f"[ARCHIVED] {relative_path(ARCHIVED_DIR)}")
    print(f"[ACTIVE]   {relative_path(OLD_DIR)}")


if __name__ == "__main__":
    main()
