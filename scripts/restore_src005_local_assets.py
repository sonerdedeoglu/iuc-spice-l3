#!/usr/bin/env python3
"""Restore SRÇ.005 Mermaid sources and approved PNGs from Confluence."""
from __future__ import annotations

import unicodedata
from pathlib import Path
from typing import Any

import yaml

from confluence_client import ConfluenceClient
from create_src005_process_assessment_package import FLOW_LINES, INTERACTION_LINES


ROOT = Path(__file__).resolve().parents[1]
PROCESS_DIR = (
    ROOT
    / "confluence/pages/000-root-iuc-bidb-spice-2026-level-3/01-surec-dokumanlari"
    / "iuc-bidb-src-005-surec-degerlendirme-sureci"
)
INTERACTION_DIR = (
    PROCESS_DIR
    / "iuc-bidb-lst-007-surec-etkilesim-matrisi-iuc-bidb-src-005"
)

SPECS = [
    {
        "folder": PROCESS_DIR,
        "filename": unicodedata.normalize("NFD", "İÜC.BİDB.SRÇ.005 - Flowchart.png"),
    },
    {
        "folder": INTERACTION_DIR,
        "filename": "src005-surec-etkilesim.png",
    },
]


def nfc(value: str) -> str:
    return unicodedata.normalize("NFC", value)


def load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def list_attachments(client: ConfluenceClient, page_id: str) -> list[dict[str, Any]]:
    result = client.get(
        f"/rest/api/content/{page_id}/child/attachment",
        {"limit": 1000, "expand": "version,extensions"},
    )
    return result.get("results", []) or []


def restore_png(client: ConfluenceClient, spec: dict[str, Any]) -> Path:
    page_id = str(load_yaml(spec["folder"] / "page.yaml").get("page_id") or "").strip()
    if not page_id:
        raise RuntimeError(f"page_id bulunamadı: {spec['folder']}")

    wanted = nfc(spec["filename"])
    attachment = next(
        (
            item
            for item in list_attachments(client, page_id)
            if nfc(str(item.get("title") or "")) == wanted
        ),
        None,
    )
    if attachment is None:
        raise RuntimeError(f"Confluence eki bulunamadı: {spec['filename']}")

    download_path = str(attachment.get("_links", {}).get("download") or "")
    if not download_path:
        raise RuntimeError(f"Ek indirme bağlantısı bulunamadı: {spec['filename']}")

    response = client.request("GET", download_path)
    response.raise_for_status()
    if not response.content.startswith(b"\x89PNG\r\n\x1a\n"):
        raise RuntimeError(f"İndirilen ek geçerli PNG değil: {spec['filename']}")

    target = spec["folder"] / "attachments" / spec["filename"]
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(response.content)
    return target


def main() -> None:
    client = ConfluenceClient()
    for spec in SPECS:
        target = restore_png(client, spec)
        print(f"[RESTORE] {target.relative_to(ROOT)}")

    flow_source = PROCESS_DIR / "attachments/src005-surec-akisi.mmd"
    interaction_source = INTERACTION_DIR / "attachments/src005-surec-etkilesim.mmd"
    flow_source.write_text("\n".join(FLOW_LINES) + "\n", encoding="utf-8")
    interaction_source.write_text("\n".join(INTERACTION_LINES) + "\n", encoding="utf-8")
    print(f"[RESTORE] {flow_source.relative_to(ROOT)}")
    print(f"[RESTORE] {interaction_source.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
