#!/usr/bin/env python3
"""Finalize PRS.XXX.Ş and KLV.XXX.Ş template candidates.

Actions:
- Move the currently active PRS/KLV template pages under `Arşiv - Kaldırılan Şablonlar`
  and rename them with `KALDIRILDI - ...`.
- Promote the draft PRS/KLV template candidates to the active template paths/titles.
- Keep current active page Confluence page_ids on archived pages.
- Keep promoted candidates as new pages to be created by the publisher.
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

TEMPLATES_PARENT_ID = "137265785"
TEMPLATES_PARENT_TITLE = "02 - Şablonlar"
ARCHIVE_PARENT_TITLE = "Arşiv - Kaldırılan Şablonlar"

ITEMS = [
    {
        "old_slug": "iuc-bidb-prs-xxx-s-prosedur-tanimi-sablonu",
        "draft_slug": "taslak-iuc-bidb-prs-xxx-s-prosedur-tanimi-sablonu",
        "archived_slug": "kaldirildi-iuc-bidb-prs-xxx-s-prosedur-tanimi-sablonu",
        "active_title": "İÜC.BİDB.PRS.XXX.Ş - Prosedür Tanımı Şablonu",
        "archived_title": "KALDIRILDI - İÜC.BİDB.PRS.XXX.Ş - Prosedür Tanımı Şablonu",
    },
    {
        "old_slug": "iuc-bidb-klv-xxx-s-kilavuz-ve-talimat-tanimi-sablonu",
        "draft_slug": "taslak-iuc-bidb-klv-xxx-s-kilavuz-ve-talimat-tanimi-sablonu",
        "archived_slug": "kaldirildi-iuc-bidb-klv-xxx-s-kilavuz-ve-talimat-tanimi-sablonu",
        "active_title": "İÜC.BİDB.KLV.XXX.Ş - Kılavuz ve Talimat Tanımı Şablonu",
        "archived_title": "KALDIRILDI - İÜC.BİDB.KLV.XXX.Ş - Kılavuz ve Talimat Tanımı Şablonu",
    },
]


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def write_yaml(path: Path, data: dict[str, Any]) -> None:
    path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")


def rel_for(path: Path) -> str:
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
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        text = text.replace(old, new)
        text = text.replace("TASLAK - ", "")
        path.write_text(text, encoding="utf-8")


def update_index(index_changes: list[dict[str, str]]) -> None:
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

    for change in index_changes:
        remove(change["draft_rel"])
        remove(change["active_rel"])
        remove(change["archived_rel"])

        archived_meta = load_yaml(Path(change["archived_dir"]) / "page.yaml")
        active_meta = load_yaml(Path(change["active_dir"]) / "page.yaml")

        upsert({
            "page_id": str(archived_meta.get("page_id") or ""),
            "title": change["archived_title"],
            "parent_id": str(archived_meta.get("parent_id") or archive_parent_id()),
            "depth": 3,
            "relative_path": change["archived_rel"],
            "slug": change["archived_slug"],
            "storage_file": f"{change['archived_rel']}/body.storage.xhtml",
            "view_file": f"{change['archived_rel']}/body.view.html",
        })
        upsert({
            "page_id": str(active_meta.get("page_id") or ""),
            "title": change["active_title"],
            "parent_id": TEMPLATES_PARENT_ID,
            "depth": 2,
            "relative_path": change["active_rel"],
            "slug": change["old_slug"],
            "storage_file": f"{change['active_rel']}/body.storage.xhtml",
            "view_file": f"{change['active_rel']}/body.view.html",
        })

    index["total_page_count"] = len(pages)
    write_yaml(INDEX_PATH, index)


def main() -> None:
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    archive_pid = archive_parent_id()
    if not archive_pid:
        raise RuntimeError("Arşiv - Kaldırılan Şablonlar page_id bulunamadı.")

    index_changes: list[dict[str, str]] = []

    for item in ITEMS:
        old_dir = TEMPLATES_DIR / item["old_slug"]
        draft_dir = TEMPLATES_DIR / item["draft_slug"]
        archived_dir = ARCHIVE_DIR / item["archived_slug"]

        active_rel = f"pages/000-root-iuc-bidb-spice-2026-level-3/02-sablonlar/{item['old_slug']}"
        draft_rel = f"pages/000-root-iuc-bidb-spice-2026-level-3/02-sablonlar/{item['draft_slug']}"
        archived_rel = f"pages/000-root-iuc-bidb-spice-2026-level-3/02-sablonlar/arsiv-kaldirilan-sablonlar/{item['archived_slug']}"

        if not old_dir.exists():
            raise FileNotFoundError(f"Current active template page not found: {old_dir}")
        if not draft_dir.exists():
            raise FileNotFoundError(f"Draft template candidate page not found: {draft_dir}")
        if archived_dir.exists():
            shutil.rmtree(archived_dir)

        shutil.move(str(old_dir), str(archived_dir))
        shutil.move(str(draft_dir), str(old_dir))

        update_page_meta(
            archived_dir,
            title=item["archived_title"],
            slug=item["archived_slug"],
            rel=archived_rel,
            parent_id=archive_pid,
            parent_title=ARCHIVE_PARENT_TITLE,
            status="archived",
        )
        replace_title_in_files(archived_dir, item["active_title"], item["archived_title"])

        update_page_meta(
            old_dir,
            title=item["active_title"],
            slug=item["old_slug"],
            rel=active_rel,
            parent_id=TEMPLATES_PARENT_ID,
            parent_title=TEMPLATES_PARENT_TITLE,
            status="active",
        )
        replace_title_in_files(old_dir, "TASLAK - " + item["active_title"], item["active_title"])

        index_changes.append({
            **item,
            "active_rel": active_rel,
            "draft_rel": draft_rel,
            "archived_rel": archived_rel,
            "active_dir": str(old_dir),
            "archived_dir": str(archived_dir),
        })

        print(f"[ARCHIVED] {rel_for(archived_dir)}")
        print(f"[ACTIVE]   {rel_for(old_dir)}")

    update_index(index_changes)
    print("[DONE] PRS/KLV template candidates promoted to active templates.")


if __name__ == "__main__":
    main()
