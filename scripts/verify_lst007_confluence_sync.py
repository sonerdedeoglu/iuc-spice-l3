#!/usr/bin/env python3
"""Verify the approved LST.007 publication, attachments, parents and removals."""
from __future__ import annotations

import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from config import SPACE_KEY
from confluence_client import ConfluenceClient


ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "confluence/pages/000-root-iuc-bidb-spice-2026-level-3/01-surec-dokumanlari"
REPORT = ROOT / "reports/lst007_confluence_sync_verification_report.md"

SPECS = [
    {
        "folder": PAGES / "src-001-dokumantasyon-sureci/lst-007-surec-etkilesim-matrisi-src-001",
        "title": "LST.007 - Süreç Etkileşim Matrisi (SRÇ.001)",
        "parent_id": "137265842",
        "png": "src001-surec-etkilesim.png",
        "required": ("flowchart LR", "PRS001", "KLV001", "LST008", "LST009", "LST010"),
    },
    {
        "folder": PAGES / "src-004-surec-kurulumu-sureci/lst-007-surec-etkilesim-matrisi-src-004",
        "title": "LST.007 - Süreç Etkileşim Matrisi (SRÇ.004)",
        "parent_id": "137265862",
        "png": "src004-surec-etkilesim.png",
        "required": ("flowchart LR", "TEMPLATES", "PRS002", "KLV002", "KLV003", "LST008", "LST009", "LST010", "FRM001"),
    },
]

REMOVED = [
    ("137265918", "LST.004 - Süreç Gözden Geçirme Matrisi (SRÇ.001)"),
    ("137265919", "LST.004 - Süreç Gözden Geçirme Matrisi (SRÇ.004)"),
    ("137265907", "LST.007 - Süreç Mimari ve Etkileşim Matrisi"),
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


def main() -> None:
    client = ConfluenceClient()
    results: list[dict[str, Any]] = []
    for spec in SPECS:
        meta = load_yaml(spec["folder"] / "page.yaml")
        page_id = str(meta.get("page_id") or "")
        remote = client.get(
            f"/rest/api/content/{page_id}",
            {"expand": "version,body.storage,body.view,ancestors"},
        )
        if nfc(str(remote.get("title") or "")) != nfc(spec["title"]):
            raise RuntimeError(f"Uzak sayfa başlığı uyuşmuyor: {page_id}")
        ancestors = remote.get("ancestors") or []
        actual_parent = str(ancestors[-1].get("id") or "") if ancestors else ""
        if actual_parent != spec["parent_id"]:
            raise RuntimeError(f"Yanlış ebeveyn: {spec['title']} -> {actual_parent}")

        storage = nfc(remote["body"]["storage"]["value"])
        view = nfc(remote["body"]["view"]["value"])
        section = re.search(r"<h2[^>]*>3\..*?(?=<h2[^>]*>4\.)", storage, flags=re.DOTALL)
        if not section:
            raise RuntimeError(f"3. bölüm bulunamadı: {spec['title']}")
        image_pos = section.group(0).find("<ac:image")
        info_pos = section.group(0).find("<ac:structured-macro")
        if image_pos < 0 or info_pos < 0 or image_pos > info_pos or "Mermaid Kodu" not in section.group(0):
            raise RuntimeError(f"Diyagram / Mermaid bilgi kutusu sırası yanlış: {spec['title']}")
        if 'ac:width="1000"' not in section.group(0) or "ac:height=" in section.group(0):
            raise RuntimeError(f"Diyagram genişliği 1000 px değil: {spec['title']}")
        missing = [item for item in spec["required"] if item not in storage]
        if missing:
            raise RuntimeError(f"Uzak sayfa içeriği eksik: {spec['title']} -> {missing}")

        attachment = next(
            (item for item in list_attachments(client, page_id) if nfc(str(item.get("title") or "")) == nfc(spec["png"])),
            None,
        )
        if not attachment:
            raise RuntimeError(f"PNG eki bulunamadı: {spec['png']}")
        local_size = (spec["folder"] / "attachments" / spec["png"]).stat().st_size
        remote_size = int((attachment.get("extensions") or {}).get("fileSize") or 0)
        if remote_size and remote_size != local_size:
            raise RuntimeError(f"PNG boyutu uyuşmuyor: {spec['png']} local={local_size} remote={remote_size}")
        if "<img" not in view or spec["png"] not in view:
            raise RuntimeError(f"PNG Confluence görünümünde çözümlenmedi: {spec['png']}")

        results.append({
            "title": spec["title"],
            "page_id": page_id,
            "version": remote["version"]["number"],
            "parent_id": actual_parent,
            "png": spec["png"],
            "size": local_size,
            "url": meta.get("url") or "",
        })

    for page_id, title in REMOVED:
        response = client.request("GET", f"/rest/api/content/{page_id}")
        if response.status_code != 404:
            raise RuntimeError(f"Silinen sayfa ID ile hâlâ erişilebilir: {page_id} ({response.status_code})")
        found = client.find_page(SPACE_KEY, title).get("results", []) or []
        if found:
            raise RuntimeError(f"Silinen sayfa başlıkla hâlâ bulunuyor: {title}")

    lines = [
        "# LST.007 Confluence Senkronizasyon Doğrulama Raporu",
        "",
        f"Zaman: {datetime.now(timezone.utc).isoformat()}",
        "",
        "## Yayımlanan Sayfalar",
        "",
    ]
    for item in results:
        lines.extend([
            f"- **{item['title']}**",
            f"  - Sayfa ID / sürüm: {item['page_id']} / {item['version']}",
            f"  - Ebeveyn ID: {item['parent_id']}",
            f"  - PNG: `{item['png']}` / {item['size']} bayt",
            "  - Confluence görüntüleme genişliği: 1000 px",
            "  - Diyagram → Mermaid Kodu sırası: başarılı",
            f"  - Bağlantı: {item['url']}",
        ])
    lines.extend(["", "## Silinen Sayfalar", ""])
    lines.extend(f"- {page_id} — {title} — doğrulama: 404 ve başlık aramasında sonuç yok" for page_id, title in REMOVED)
    lines.append("")
    REPORT.write_text("\n".join(lines), encoding="utf-8")

    for item in results:
        print(f"[OK] {item['title']} — sürüm {item['version']} — {item['png']} ({item['size']} bayt)")
    for page_id, title in REMOVED:
        print(f"[REMOVED] {page_id} — {title}")
    print(f"[REPORT] {REPORT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
