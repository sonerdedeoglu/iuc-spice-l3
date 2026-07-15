#!/usr/bin/env python3
"""Verify the published SRÇ.005 package and its PLN/RPR document family."""
from __future__ import annotations

import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from confluence_client import ConfluenceClient


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "confluence/pages/000-root-iuc-bidb-spice-2026-level-3"
REPORT = ROOT / "reports/src005_confluence_package_verification_report.md"


def nfc(value: str) -> str:
    return unicodedata.normalize("NFC", value)


SPECS = [
    {
        "path": "01-surec-dokumanlari/src-005-surec-degerlendirme-sureci",
        "required": ["PIM.2.BP8", "10. Süreç Akışı", "Mermaid Kodu", "PLN.001", "RPR.001"],
        "attachment": "SRÇ.005 - Flowchart.png",
    },
    {
        "path": "01-surec-dokumanlari/src-005-surec-degerlendirme-sureci/lst-007-surec-etkilesim-matrisi-src-005",
        "required": ["flowchart LR", "Mermaid Kodu", "SRÇ.005", "PLN.001", "RPR.001", "FRM.001"],
        "attachment": "src005-surec-etkilesim.png",
    },
    {
        "path": "01-surec-dokumanlari/src-005-surec-degerlendirme-sureci/lst-008-is-urunleri-ve-kalite-kriterleri-listesi-src-005",
        "required": ["PLN.001", "RPR.001", "FRM.001", "LST.006"],
    },
    {
        "path": "01-surec-dokumanlari/src-005-surec-degerlendirme-sureci/lst-009-surec-performans-olcum-seti-src-005",
        "required": ["SRÇ.005-Ö01", "SRÇ.005-Ö02", "SRÇ.005-Ö03"],
    },
    {
        "path": "01-surec-dokumanlari/src-005-surec-degerlendirme-sureci/lst-010-surec-rol-yetki-ve-raci-matrisi-src-005",
        "required": ["Kalite Danışmanı", "Süreç Sahibi", "Gözden Geçiren", "Onaylayan"],
    },
    {
        "path": "01-surec-dokumanlari/src-005-surec-degerlendirme-sureci/frm-001-surec-gozden-gecirme-formu-src-005",
        "required": ["GG-AA-YYYY", "Öncelikli Tamamlama Listesi"],
    },
    {
        "path": "91-ic-denetimler/surec-gozden-gecirmeleri/frm-001-surec-gozden-gecirme-formu-src-005-degerlendirme-1",
        "required": ["Değerlendirme #1", "PIM.2.BP1", "PA 3.2", "Öncelikli Tamamlama Listesi"],
    },
    {
        "path": "07-prosedurler/prs-003-surec-degerlendirme-proseduru",
        "required": ["PIM.2.BP1", "SRÇ.017", "SRÇ.018", "PLN.001", "RPR.001"],
    },
    {
        "path": "02-sablonlar/pln-001-s-surec-kalite-plani-sablonu",
        "required": ["PLN.001.Ş", "Süreç Kalite Planı Şablonu", "Yıllık Değerlendirme Takvimi", "Bulguların Yönetimi"],
        "forbidden": ["PLN.XXX.Ş"],
    },
    {
        "path": "08-planlar/pln-001-surec-kalite-plani",
        "required": ["PLN.001", "Ocak", "Şubat", "Mart", "RPR.001"],
    },
    {
        "path": "02-sablonlar/rpr-001-s-surec-performanslari-raporu-sablonu",
        "required": ["RPR.001.Ş", "Süreç Sonuç Özeti", "Etiket Dağılımları ve Eğilimler"],
        "forbidden": ["RPR.XXX.Ş"],
    },
    {
        "path": "09-raporlar/rpr-001-surec-performanslari-raporu",
        "required": ["RPR.001", "SRÇ.001", "SRÇ.004", "SRÇ.005", "Değerlendirme Bağlantısı"],
    },
]


def load_meta(folder: Path) -> dict[str, Any]:
    return yaml.safe_load((folder / "page.yaml").read_text(encoding="utf-8")) or {}


def list_attachments(client: ConfluenceClient, page_id: str) -> list[dict[str, Any]]:
    response = client.get(
        f"/rest/api/content/{page_id}/child/attachment",
        {"limit": 1000, "expand": "version,extensions"},
    )
    return response.get("results", []) or []


def main() -> None:
    client = ConfluenceClient()
    results: list[dict[str, Any]] = []
    for spec in SPECS:
        folder = BASE / spec["path"]
        meta = load_meta(folder)
        page_id = str(meta.get("page_id") or "")
        if not page_id:
            raise RuntimeError(f"Sayfa ID eksik: {meta.get('title') or spec['path']}")
        remote = client.get(
            f"/rest/api/content/{page_id}",
            {"expand": "version,body.storage,body.view,ancestors"},
        )
        if nfc(str(remote.get("title") or "")) != nfc(str(meta.get("title") or "")):
            raise RuntimeError(f"Başlık uyuşmuyor: {page_id}")
        ancestors = remote.get("ancestors") or []
        actual_parent = str(ancestors[-1].get("id") or "") if ancestors else ""
        expected_parent = str(meta.get("parent_id") or "")
        if expected_parent and actual_parent != expected_parent:
            raise RuntimeError(f"Ebeveyn uyuşmuyor: {remote['title']} {actual_parent} != {expected_parent}")

        storage = nfc(remote["body"]["storage"]["value"])
        view = nfc(remote["body"]["view"]["value"])
        combined = f"{storage}\n{view}"
        missing = [term for term in spec["required"] if nfc(term) not in combined]
        forbidden = [term for term in spec.get("forbidden", []) if nfc(term) in combined]
        if missing or forbidden:
            raise RuntimeError(f"İçerik doğrulanamadı: {remote['title']} eksik={missing} yasaklı={forbidden}")

        attachment_status = "uygulanamaz"
        if spec.get("attachment"):
            wanted = nfc(spec["attachment"])
            attachment = next(
                (item for item in list_attachments(client, page_id) if nfc(str(item.get("title") or "")) == wanted),
                None,
            )
            if not attachment:
                raise RuntimeError(f"Ek bulunamadı: {remote['title']} / {spec['attachment']}")
            local_path = folder / "attachments" / spec["attachment"]
            local_size = local_path.stat().st_size
            remote_size = int((attachment.get("extensions") or {}).get("fileSize") or 0)
            if remote_size and remote_size != local_size:
                raise RuntimeError(f"Ek boyutu uyuşmuyor: {spec['attachment']} {local_size} != {remote_size}")
            if wanted not in view or "<img" not in view:
                raise RuntimeError(f"Ek görünümde çözümlenmedi: {spec['attachment']}")
            attachment_status = f"başarılı ({local_size} bayt)"

        results.append({
            "title": remote["title"],
            "page_id": page_id,
            "version": remote["version"]["number"],
            "parent_id": actual_parent,
            "attachment": attachment_status,
            "url": meta.get("url") or "",
        })
        print(f"[OK] {remote['title']} — sürüm {remote['version']['number']}")

    lines = [
        "# SRÇ.005 Confluence Paket Doğrulama Raporu",
        "",
        f"Zaman: {datetime.now(timezone.utc).isoformat()}",
        "",
        f"Doğrulanan sayfa sayısı: {len(results)}",
        "",
    ]
    for item in results:
        lines.extend([
            f"- **{item['title']}**",
            f"  - Sayfa ID / sürüm: {item['page_id']} / {item['version']}",
            f"  - Ebeveyn ID: {item['parent_id']}",
            f"  - Ek: {item['attachment']}",
            f"  - Bağlantı: {item['url']}",
        ])
    lines.append("")
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"[REPORT] {REPORT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
