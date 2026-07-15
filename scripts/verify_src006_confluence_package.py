#!/usr/bin/env python3
"""Verify the published SRÇ.006 process-improvement package."""
from __future__ import annotations

import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from confluence_client import ConfluenceClient


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "confluence/pages/000-root-iuc-bidb-spice-2026-level-3"
REPORT = ROOT / "reports/src006_confluence_package_verification_report.md"


def nfc(value: str) -> str:
    return unicodedata.normalize("NFC", value)


SPECS = [
    {
        "path": "01-surec-dokumanlari/src-006-surec-iyilestirme-sureci",
        "required": ["PIM.3.BP9", "10. Süreç Akışı", "Mermaid Kodu", "PLN.002"],
        "attachment": "SRÇ.006 - Flowchart.png",
    },
    {
        "path": "01-surec-dokumanlari/src-006-surec-iyilestirme-sureci/lst-007-surec-etkilesim-matrisi-src-006",
        "required": ["flowchart LR", "Mermaid Kodu", "FRM.001 - Süreç Gözden Geçirme Formu (İlgili Süreç)", "RPR.001"],
        "forbidden": ["FRM.001 Değerlendirme #1"],
        "attachment": "src006-surec-etkilesim.png",
    },
    {
        "path": "01-surec-dokumanlari/src-006-surec-iyilestirme-sureci/lst-008-is-urunleri-ve-kalite-kriterleri-listesi-src-006",
        "required": ["PRS.004", "PLN.002", "FRM.001 - Süreç Gözden Geçirme Formu (İlgili Süreç)"],
        "forbidden": ["FRM.001 Değerlendirme #1"],
    },
    {
        "path": "01-surec-dokumanlari/src-006-surec-iyilestirme-sureci/lst-009-surec-performans-olcum-seti-src-006",
        "required": ["ÖLÇ.006.01", "ÖLÇ.006.02", "ÖLÇ.006.03"],
    },
    {
        "path": "01-surec-dokumanlari/src-006-surec-iyilestirme-sureci/lst-010-surec-rol-yetki-ve-raci-matrisi-src-006",
        "required": ["Bilgi İşlem Daire Başkanı", "Proje Yöneticisi", "Kalite Danışmanı", "Yetki ve Onay Matrisi"],
    },
    {
        "path": "01-surec-dokumanlari/src-006-surec-iyilestirme-sureci/frm-001-surec-gozden-gecirme-formu-src-006",
        "required": ["GG-AA-YYYY", "Öncelikli Tamamlama Listesi"],
    },
    {
        "path": "91-ic-denetimler/surec-gozden-gecirmeleri/frm-001-surec-gozden-gecirme-formu-src-006-degerlendirme-1",
        "required": ["Değerlendirme #1", "PIM.3.BP1", "PIM.3.BP9", "PA 3.2", "Öncelikli Tamamlama Listesi"],
    },
    {
        "path": "07-prosedurler/prs-004-surec-iyilestirme-ve-degisiklik-yonetimi-proseduru",
        "required": ["SRÇ.006", "SRÇ.018", "SRÇ.018 değişiklik gözden geçirmesi", "PLN.002"],
        "forbidden": ["SUP.10.BP9"],
    },
    {
        "path": "02-sablonlar/pln-002-s-surec-iyilestirme-plani-sablonu",
        "required": ["PLN.002.Ş", "Etki ve Uygulama Önceliği", "Sonuç Doğrulama", "Yeniden Kullanım"],
    },
    {
        "path": "02-sablonlar/rpr-001-s-surec-performanslari-raporu-sablonu",
        "required": ["Doğrulanmış İyileştirme Sonuçları", "SRÇ.018 değişiklik gözden geçirme sonucu"],
    },
    {
        "path": "09-raporlar/rpr-001-surec-performanslari-raporu",
        "required": ["SRÇ.006", "4 VAR; 2 DAĞINIK; 3 ZAYIF", "Doğrulanmış İyileştirme Sonuçları"],
    },
    {
        "path": "03-kayitlar-ve-listeler/lst-001-aktif-dokumanlar-listesi",
        "required": ["PRS.004", "PLN.002.Ş", "SRÇ.006"],
    },
    {
        "path": "03-kayitlar-ve-listeler/lst-006-standart-surec-envanteri",
        "required": ["PIM.2", "PIM.3", "SRÇ.005", "SRÇ.006", "Confluence'ta yayımlanmış"],
    },
    {
        "path": "03-kayitlar-ve-listeler/lst-012-surec-yayginlastirma-ve-bilgilendirme-kaydi",
        "required": ["SRÇ.006", "RPR.001 güncellemesi", "Confluence yayını", "iki PNG eki doğrulandı"],
    },
    {
        "path": "02-sablonlar",
        "required": ["PLN.002.Ş", "Süreç İyileştirme Planı Şablonu"],
    },
    {
        "path": "07-prosedurler",
        "required": ["PRS.004", "Süreç İyileştirme ve Değişiklik Yönetimi Prosedürü"],
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


def local_attachment(folder: Path, wanted: str) -> Path:
    matches = [item for item in (folder / "attachments").iterdir() if nfc(item.name) == nfc(wanted)]
    if len(matches) != 1:
        raise RuntimeError(f"Yerel ek tekil bulunamadı: {folder} / {wanted}")
    return matches[0]


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

        combined = nfc(f"{remote['body']['storage']['value']}\n{remote['body']['view']['value']}")
        missing = [term for term in spec["required"] if nfc(term) not in combined]
        forbidden = [term for term in spec.get("forbidden", []) if nfc(term) in combined]
        if missing or forbidden:
            raise RuntimeError(f"İçerik doğrulanamadı: {remote['title']} eksik={missing} yasaklı={forbidden}")

        attachment_status = "uygulanamaz"
        if spec.get("attachment"):
            wanted = nfc(spec["attachment"])
            attachment = next((item for item in list_attachments(client, page_id) if nfc(str(item.get("title") or "")) == wanted), None)
            if not attachment:
                raise RuntimeError(f"Ek bulunamadı: {remote['title']} / {spec['attachment']}")
            local_path = local_attachment(folder, spec["attachment"])
            local_size = local_path.stat().st_size
            remote_size = int((attachment.get("extensions") or {}).get("fileSize") or 0)
            if remote_size and remote_size != local_size:
                raise RuntimeError(f"Ek boyutu uyuşmuyor: {spec['attachment']} {local_size} != {remote_size}")
            if wanted not in nfc(remote["body"]["view"]["value"]) or "<img" not in remote["body"]["view"]["value"]:
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
        "# SRÇ.006 Confluence Paket Doğrulama Raporu",
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
