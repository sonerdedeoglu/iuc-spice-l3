#!/usr/bin/env python3
"""Verify the three approved process pages and two flowchart attachments."""
from __future__ import annotations

import html
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from confluence_client import ConfluenceClient


ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "confluence/pages/000-root-iuc-bidb-spice-2026-level-3"
REPORT = ROOT / "reports/selected_confluence_verification_report.md"


def nfc(value: str) -> str:
    return unicodedata.normalize("NFC", value)


def text_content(value: str) -> str:
    value = re.sub(r"<[^>]+>", " ", value)
    return " ".join(html.unescape(value).split())


SPECS = [
    {
        "folder": PAGES / "01-surec-dokumanlari/iuc-bidb-src-001-dokumantasyon-sureci",
        "required": [
            "1. Süreç Bilgileri",
            "Araçlar ve Altyapı",
            "Levent BAYEZİT - Proje Yöneticisi",
            "Mustafa Nusret SARISAKAL - BİD Başkanı",
            "ISO/IEC 15504-5:2006 SUP.7 - Documentation",
            "ISO/IEC 15504-5:2006 - Process Assessment Model",
            "ISO/IEC 15504-5:2006 - Process Attributes",
            "Mermaid Kodu",
            "v1.0",
        ],
        "forbidden": ["Aşağıdaki kaynak kod", "Mermaid Online Editor", "v1.1"],
        "attachment": "İÜC.BİDB.SRÇ.001 - Flowchart.png",
    },
    {
        "folder": PAGES / "01-surec-dokumanlari/iuc-bidb-src-004-surec-kurulumu-sureci",
        "required": [
            "1. Süreç Bilgileri",
            "Araçlar ve Altyapı",
            "Mustafa Nusret SARISAKAL - Bilgi İşlem Daire Başkanı",
            "Levent Bayezit - Proje Yöneticisi",
            "ISO/IEC 15504-5:2006 PIM.1 - Process establishment",
            "ISO/IEC 15504-5:2006 - Process Assessment Model",
            "ISO/IEC 15504-5:2006 - Process Attributes",
            "Mermaid Kodu",
            "v1.0",
        ],
        "forbidden": ["Aşağıdaki kaynak kod", "Mermaid Online Editor", "v0.9"],
        "attachment": "İÜC.BİDB.SRÇ.004 - Flowchart.png",
    },
    {
        "folder": PAGES / "02-sablonlar/iuc-bidb-src-xxx-s-surec-tanimi-sablonu",
        "required": [
            "1. Süreç Bilgileri",
            "Araçlar ve Altyapı",
            "ISO/IEC 15504-5 - Process Assessment Model",
            "ISO/IEC 15504-5 - Process Attributes",
            "Mermaid Kodu",
            "10 Jan 2025",
            "15 Feb 2025",
            "v1.0",
        ],
        "forbidden": ["Aşağıdaki kaynak kod"],
        "attachment": None,
    },
]


def metadata(folder: Path) -> dict[str, Any]:
    return yaml.safe_load((folder / "page.yaml").read_text(encoding="utf-8")) or {}


def attachments(client: ConfluenceClient, page_id: str) -> list[dict[str, Any]]:
    payload = client.get(
        f"/rest/api/content/{page_id}/child/attachment",
        {"limit": 1000, "expand": "version,extensions"},
    )
    return payload.get("results", []) or []


def verify() -> list[dict[str, Any]]:
    client = ConfluenceClient()
    results: list[dict[str, Any]] = []

    for spec in SPECS:
        local_meta = metadata(spec["folder"])
        page_id = str(local_meta["page_id"])
        remote = client.get(
            f"/rest/api/content/{page_id}",
            {"expand": "version,body.storage,body.view"},
        )
        storage = nfc(remote["body"]["storage"]["value"])
        view = nfc(remote["body"]["view"]["value"])
        visible = text_content(view)
        combined = f"{storage}\n{view}\n{visible}"

        missing = [item for item in spec["required"] if nfc(item) not in combined]
        forbidden = [item for item in spec["forbidden"] if nfc(item) in combined]
        attachment_status = "uygulanamaz"

        if spec["attachment"]:
            wanted = nfc(spec["attachment"])
            items = attachments(client, page_id)
            found = next((item for item in items if nfc(str(item.get("title") or "")) == wanted), None)
            if not found:
                missing.append(f"ek: {spec['attachment']}")
                attachment_status = "bulunamadı"
            else:
                local_path = spec["folder"] / "attachments" / unicodedata.normalize("NFD", spec["attachment"])
                local_size = local_path.stat().st_size
                remote_size = int((found.get("extensions") or {}).get("fileSize") or 0)
                if remote_size and remote_size != local_size:
                    missing.append(f"ek boyutu: yerel {local_size}, uzak {remote_size}")
                    attachment_status = "boyut uyuşmuyor"
                elif wanted not in view or "<img" not in view:
                    missing.append(f"sayfada çözümlenmiş görsel: {spec['attachment']}")
                    attachment_status = "ek var, görünümde çözümlenmedi"
                else:
                    attachment_status = f"başarılı ({local_size} bayt)"

        if missing or forbidden:
            raise RuntimeError(
                f"{remote['title']} doğrulanamadı; eksik={missing or '-'}; yasaklı={forbidden or '-'}"
            )

        results.append(
            {
                "title": remote["title"],
                "page_id": page_id,
                "version": remote["version"]["number"],
                "attachment": attachment_status,
                "url": local_meta["url"],
            }
        )
    return results


def write_report(results: list[dict[str, Any]]) -> None:
    lines = [
        "# Seçili Confluence Sayfaları Doğrulama Raporu",
        "",
        f"Zaman: {datetime.now(timezone.utc).isoformat()}",
        "",
        "Yayımlanan depolama içeriği, Confluence tarafından oluşturulan görünüm ve süreç akış ekleri doğrulanmıştır.",
        "",
    ]
    for item in results:
        lines.extend(
            [
                f"- **{item['title']}**",
                f"  - Sayfa: {item['page_id']} / sürüm {item['version']}",
                f"  - Ek doğrulaması: {item['attachment']}",
                f"  - Sonuç: başarılı",
                f"  - Bağlantı: {item['url']}",
            ]
        )
    lines.append("")
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    results = verify()
    write_report(results)
    for item in results:
        print(
            f"[OK] {item['title']} — sürüm {item['version']} — ek: {item['attachment']}"
        )
    print(f"[REPORT] {REPORT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
