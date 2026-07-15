#!/usr/bin/env python3
"""Publish approved process flowchart PNG attachments.

The command is intentionally scoped to two known process pages and supports a
mandatory dry-run before any Confluence write.
"""
from __future__ import annotations

import argparse
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from confluence_client import ConfluenceClient


ROOT = Path(__file__).resolve().parents[1]
PAGES_ROOT = ROOT / "confluence/pages/000-root-iuc-bidb-spice-2026-level-3/01-surec-dokumanlari"
REPORT = ROOT / "reports/process_flow_attachment_publish_report.md"

SPECS = [
    {
        "folder": PAGES_ROOT / "src-001-dokumantasyon-sureci",
        "title": "SRÇ.001 - Dokümantasyon Süreci",
        "filename": unicodedata.normalize("NFD", "SRÇ.001 - Flowchart.png"),
        "process": "SRÇ.001",
    },
    {
        "folder": PAGES_ROOT / "src-004-surec-kurulumu-sureci",
        "title": "SRÇ.004 - Süreç Kurulumu Süreci",
        "filename": unicodedata.normalize("NFD", "SRÇ.004 - Flowchart.png"),
        "process": "SRÇ.004",
    },
    {
        "folder": PAGES_ROOT / "src-005-surec-degerlendirme-sureci",
        "title": "SRÇ.005 - Süreç Değerlendirme Süreci",
        "filename": unicodedata.normalize("NFD", "SRÇ.005 - Flowchart.png"),
        "process": "SRÇ.005",
    },
    {
        "folder": PAGES_ROOT / "src-006-surec-iyilestirme-sureci",
        "title": "SRÇ.006 - Süreç İyileştirme Süreci",
        "filename": unicodedata.normalize("NFD", "SRÇ.006 - Flowchart.png"),
        "process": "SRÇ.006",
    },
    {
        "folder": PAGES_ROOT / "src-021-bilgi-yonetimi-sureci",
        "title": "SRÇ.021 - Bilgi Yönetimi Süreci",
        "filename": unicodedata.normalize("NFD", "SRÇ.021 - Flowchart.png"),
        "process": "SRÇ.021",
    },
    {
        "folder": PAGES_ROOT / "src-023-organizasyonel-yonetim-sureci",
        "title": "SRÇ.023 - Organizasyonel Yönetim Süreci",
        "filename": unicodedata.normalize("NFD", "SRÇ.023 - Flowchart.png"),
        "process": "SRÇ.023",
    },
    {
        "folder": PAGES_ROOT / "src-024-kalite-yonetimi-sureci",
        "title": "SRÇ.024 - Kalite Yönetimi Süreci",
        "filename": unicodedata.normalize("NFD", "SRÇ.024 - Flowchart.png"),
        "process": "SRÇ.024",
    },
    {
        "folder": PAGES_ROOT / "src-025-olcum-sureci",
        "title": "SRÇ.025 - Ölçüm Süreci",
        "filename": unicodedata.normalize("NFD", "SRÇ.025 - Flowchart.png"),
        "process": "SRÇ.025",
    },
]


def load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def normalized(value: str) -> str:
    return unicodedata.normalize("NFC", value)


def attachment_path(spec: dict[str, Any]) -> Path:
    return spec["folder"] / "attachments" / spec["filename"]


def validate_local(spec: dict[str, Any]) -> tuple[str, Path, int]:
    metadata = load_yaml(spec["folder"] / "page.yaml")
    page_id = str(metadata.get("page_id") or "").strip()
    if not page_id:
        raise RuntimeError(f"Confluence page_id eksik: {spec['title']}")
    if metadata.get("title") != spec["title"]:
        raise RuntimeError(f"Sayfa başlığı uyuşmuyor: {spec['title']}")
    path = attachment_path(spec)
    if not path.exists():
        raise RuntimeError(f"PNG dosyası bulunamadı: {path}")
    data = path.read_bytes()
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise RuntimeError(f"Dosya geçerli PNG değil: {path}")
    return page_id, path, len(data)


def list_attachments(client: ConfluenceClient, page_id: str) -> list[dict[str, Any]]:
    result = client.get(
        f"/rest/api/content/{page_id}/child/attachment",
        {"limit": 1000, "expand": "version,extensions"},
    )
    return result.get("results", []) or []


def find_attachment(items: list[dict[str, Any]], filename: str) -> dict[str, Any] | None:
    desired = normalized(filename)
    for item in items:
        if normalized(str(item.get("title") or "")) == desired:
            return item
    return None


def upload(
    client: ConfluenceClient,
    page_id: str,
    path: Path,
    filename: str,
    existing: dict[str, Any] | None,
) -> dict[str, Any]:
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
            data={"minorEdit": "true", "comment": "Süreç akış PNG görseli güncellendi."},
        )
    response.raise_for_status()
    return response.json()


def write_report(results: list[dict[str, Any]], dry_run: bool) -> None:
    lines = [
        "# Süreç Akış PNG Confluence Yayın Raporu",
        "",
        f"Çalışma modu: {'DRY-RUN' if dry_run else 'NORMAL'}",
        f"Zaman: {datetime.now(timezone.utc).isoformat()}",
        "",
    ]
    for item in results:
        lines.append(
            f"- {item['action']} — {item['title']} — `{item['filename']}` — "
            f"{item['size']} bayt — doğrulama: {item['verified']}"
        )
    lines.append("")
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish approved process flowchart PNG attachments")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--process", action="append", choices=sorted({spec["process"] for spec in SPECS}), help="Publish only the selected process; may be repeated")
    args = parser.parse_args()

    client = ConfluenceClient()
    results: list[dict[str, Any]] = []
    selected = set(args.process or [])
    for spec in (item for item in SPECS if not selected or item["process"] in selected):
        page_id, path, size = validate_local(spec)
        attachments = list_attachments(client, page_id)
        existing = find_attachment(attachments, spec["filename"])
        action = "UPDATE" if existing else "CREATE"
        if args.dry_run:
            print(f"[DRY-RUN] {action} {spec['title']} — {spec['filename']}")
            verified = "planlandı"
        else:
            upload(client, page_id, path, spec["filename"], existing)
            refreshed = list_attachments(client, page_id)
            uploaded = find_attachment(refreshed, spec["filename"])
            if not uploaded:
                raise RuntimeError(f"Ek yükleme sonrası bulunamadı: {spec['filename']}")
            remote_size = int((uploaded.get("extensions") or {}).get("fileSize") or 0)
            if remote_size and remote_size != size:
                raise RuntimeError(
                    f"Ek boyutu doğrulanamadı: {spec['filename']} local={size} remote={remote_size}"
                )
            verified = "başarılı"
            print(f"[{action}] {spec['title']} — {spec['filename']}")
        results.append({
            "action": action,
            "title": spec["title"],
            "filename": spec["filename"],
            "size": size,
            "verified": verified,
        })

    write_report(results, args.dry_run)
    print(f"[REPORT] {REPORT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
