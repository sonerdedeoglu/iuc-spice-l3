#!/usr/bin/env python3
"""Publish approved process-specific LST.007 Mermaid PNG attachments."""
from __future__ import annotations

import argparse
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from confluence_client import ConfluenceClient


ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "confluence/pages/000-root-iuc-bidb-spice-2026-level-3/01-surec-dokumanlari"
REPORT = ROOT / "reports/lst007_interaction_attachment_publish_report.md"

SPECS = [
    {
        "folder": PAGES / "src-001-dokumantasyon-sureci/lst-007-surec-etkilesim-matrisi-src-001",
        "title": "LST.007 - Süreç Etkileşim Matrisi (SRÇ.001)",
        "filename": "src001-surec-etkilesim.png",
        "process": "SRÇ.001",
    },
    {
        "folder": PAGES / "src-004-surec-kurulumu-sureci/lst-007-surec-etkilesim-matrisi-src-004",
        "title": "LST.007 - Süreç Etkileşim Matrisi (SRÇ.004)",
        "filename": "src004-surec-etkilesim.png",
        "process": "SRÇ.004",
    },
    {
        "folder": PAGES / "src-005-surec-degerlendirme-sureci/lst-007-surec-etkilesim-matrisi-src-005",
        "title": "LST.007 - Süreç Etkileşim Matrisi (SRÇ.005)",
        "filename": "src005-surec-etkilesim.png",
        "process": "SRÇ.005",
    },
    {
        "folder": PAGES / "src-006-surec-iyilestirme-sureci/lst-007-surec-etkilesim-matrisi-src-006",
        "title": "LST.007 - Süreç Etkileşim Matrisi (SRÇ.006)",
        "filename": "src006-surec-etkilesim.png",
        "process": "SRÇ.006",
    },
    {
        "folder": PAGES / "src-021-bilgi-yonetimi-sureci/lst-007-surec-etkilesim-matrisi-src-021",
        "title": "LST.007 - Süreç Etkileşim Matrisi (SRÇ.021)",
        "filename": "src021-surec-etkilesim.png",
        "process": "SRÇ.021",
    },
    {
        "folder": PAGES / "src-023-organizasyonel-yonetim-sureci/lst-007-surec-etkilesim-matrisi-src-023",
        "title": "LST.007 - Süreç Etkileşim Matrisi (SRÇ.023)",
        "filename": "src023-surec-etkilesim.png",
        "process": "SRÇ.023",
    },
    {
        "folder": PAGES / "src-024-kalite-yonetimi-sureci/lst-007-surec-etkilesim-matrisi-src-024",
        "title": "LST.007 - Süreç Etkileşim Matrisi (SRÇ.024)",
        "filename": "src024-surec-etkilesim.png",
        "process": "SRÇ.024",
    },
    {
        "folder": PAGES / "src-025-olcum-sureci/lst-007-surec-etkilesim-matrisi-src-025",
        "title": "LST.007 - Süreç Etkileşim Matrisi (SRÇ.025)",
        "filename": "src025-surec-etkilesim.png",
        "process": "SRÇ.025",
    },
]


def nfc(value: str) -> str:
    return unicodedata.normalize("NFC", value)


def load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def validate_local(spec: dict[str, Any], allow_missing_page_id: bool = False) -> tuple[str, Path, int]:
    metadata = load_yaml(spec["folder"] / "page.yaml")
    page_id = str(metadata.get("page_id") or "").strip()
    if not page_id and not allow_missing_page_id:
        raise RuntimeError(f"Confluence page_id eksik: {spec['title']}")
    if nfc(str(metadata.get("title") or "")) != nfc(spec["title"]):
        raise RuntimeError(f"Sayfa başlığı uyuşmuyor: {spec['title']}")
    path = spec["folder"] / "attachments" / spec["filename"]
    if not path.exists() or not path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"):
        raise RuntimeError(f"Geçerli PNG bulunamadı: {path}")
    return page_id, path, path.stat().st_size


def list_attachments(client: ConfluenceClient, page_id: str) -> list[dict[str, Any]]:
    result = client.get(
        f"/rest/api/content/{page_id}/child/attachment",
        {"limit": 1000, "expand": "version,extensions"},
    )
    return result.get("results", []) or []


def find_attachment(items: list[dict[str, Any]], filename: str) -> dict[str, Any] | None:
    wanted = nfc(filename)
    return next((item for item in items if nfc(str(item.get("title") or "")) == wanted), None)


def upload(client: ConfluenceClient, page_id: str, path: Path, filename: str, existing: dict[str, Any] | None) -> None:
    if existing:
        endpoint = f"/rest/api/content/{page_id}/child/attachment/{existing['id']}/data"
        upload_name = str(existing.get("title") or filename)
    else:
        endpoint = f"/rest/api/content/{page_id}/child/attachment"
        upload_name = filename
    with path.open("rb") as stream:
        response = client.request(
            "POST",
            endpoint,
            headers={"X-Atlassian-Token": "no-check"},
            files={"file": (upload_name, stream, "image/png")},
            data={"minorEdit": "true", "comment": "LST.007 Mermaid PNG görseli güncellendi."},
        )
    response.raise_for_status()


def write_report(results: list[dict[str, Any]], dry_run: bool) -> None:
    lines = [
        "# LST.007 Etkileşim PNG Confluence Yayın Raporu",
        "",
        f"Çalışma modu: {'DRY-RUN' if dry_run else 'NORMAL'}",
        f"Zaman: {datetime.now(timezone.utc).isoformat()}",
        "",
    ]
    lines.extend(
        f"- {item['action']} — {item['title']} — `{item['filename']}` — {item['size']} bayt — {item['verified']}"
        for item in results
    )
    lines.append("")
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish approved process-specific LST.007 Mermaid PNG attachments")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--process", action="append", choices=sorted({spec["process"] for spec in SPECS}), help="Publish only the selected process; may be repeated")
    args = parser.parse_args()

    client = ConfluenceClient()
    results: list[dict[str, Any]] = []
    selected = set(args.process or [])
    for spec in (item for item in SPECS if not selected or item["process"] in selected):
        page_id, path, size = validate_local(spec, allow_missing_page_id=args.dry_run)
        if args.dry_run and not page_id:
            print(f"[DRY-RUN] CREATE {spec['title']} — {spec['filename']} (sayfa yayını sonrasında)")
            results.append({"action": "CREATE", "title": spec["title"], "filename": spec["filename"], "size": size, "verified": "sayfa yayını sonrasında planlandı"})
            continue
        remote_page = client.get_page(page_id)
        if nfc(str(remote_page.get("title") or "")) != nfc(spec["title"]):
            raise RuntimeError(f"Uzak sayfa başlığı uyuşmuyor: {spec['title']}")
        existing = find_attachment(list_attachments(client, page_id), spec["filename"])
        action = "UPDATE" if existing else "CREATE"
        if args.dry_run:
            verified = "planlandı"
            print(f"[DRY-RUN] {action} {spec['title']} — {spec['filename']}")
        else:
            upload(client, page_id, path, spec["filename"], existing)
            refreshed = find_attachment(list_attachments(client, page_id), spec["filename"])
            if not refreshed:
                raise RuntimeError(f"Yükleme sonrası ek bulunamadı: {spec['filename']}")
            remote_size = int((refreshed.get("extensions") or {}).get("fileSize") or 0)
            if remote_size and remote_size != size:
                raise RuntimeError(f"Ek boyutu uyuşmuyor: local={size}, remote={remote_size}")
            verified = "başarılı"
            print(f"[{action}] {spec['title']} — {spec['filename']}")
        results.append({"action": action, "title": spec["title"], "filename": spec["filename"], "size": size, "verified": verified})

    write_report(results, args.dry_run)
    print(f"[REPORT] {REPORT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
