#!/usr/bin/env python3
"""Verify the published SRÇ.023 package, shared records, and PNG attachments."""
from __future__ import annotations

import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from confluence_client import ConfluenceClient


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "confluence/pages/000-root-iuc-bidb-spice-2026-level-3"
REPORT = ROOT / "reports/src023_confluence_package_verification_report.md"


def nfc(value: str) -> str:
    return unicodedata.normalize("NFC", value)


SPECS = [
    {
        "path": "01-surec-dokumanlari/iuc-bidb-src-023-organizasyonel-yonetim-sureci",
        "required": ["MAN.2.BP1", "MAN.2.BP6", "10. Süreç Akışı", "Mermaid Kodu", "İÜC.BİDB.LST.013"],
        "attachment": "İÜC.BİDB.SRÇ.023 - Flowchart.png",
    },
    {
        "path": "01-surec-dokumanlari/iuc-bidb-src-023-organizasyonel-yonetim-sureci/iuc-bidb-lst-007-surec-etkilesim-matrisi-iuc-bidb-src-023",
        "required": ["Mermaid Kodu", "İÜC.BİDB.LST.013", "İÜC.BİDB.PRS.006"],
        "attachment": "src023-surec-etkilesim.png",
    },
    {
        "path": "01-surec-dokumanlari/iuc-bidb-src-023-organizasyonel-yonetim-sureci/iuc-bidb-lst-008-is-urunleri-ve-kalite-kriterleri-listesi-iuc-bidb-src-023",
        "required": ["İÜC.BİDB.LST.013 - Görev Tanımları ve Görevli Personel Listesi", "İÜC.BİDB.PRS.006 - Organizasyonel Yönetim Prosedürü"],
    },
    {
        "path": "01-surec-dokumanlari/iuc-bidb-src-023-organizasyonel-yonetim-sureci/iuc-bidb-lst-009-surec-performans-olcum-seti-iuc-bidb-src-023",
        "required": ["Planlanan YGG'nin döneminde gerçekleştirilme durumu", "YGG aksiyonlarının hedef tarihte tamamlanma oranı"],
    },
    {
        "path": "01-surec-dokumanlari/iuc-bidb-src-023-organizasyonel-yonetim-sureci/iuc-bidb-lst-010-surec-rol-yetki-ve-raci-matrisi-iuc-bidb-src-023",
        "required": ["Rol ve Yetkinlik Matrisi", "Süreç Faaliyetleri RACI Matrisi", "İş Ürünleri RACI Matrisi", "Yetki ve Onay Matrisi", "İÜC.BİDB.LST.013"],
    },
    {
        "path": "01-surec-dokumanlari/iuc-bidb-src-023-organizasyonel-yonetim-sureci/iuc-bidb-frm-001-surec-gozden-gecirme-formu-iuc-bidb-src-023",
        "required": ["MAN.2.BP1", "MAN.2.BP6", "Öncelikli Tamamlama Listesi", "GG-AA-YYYY"],
    },
    {
        "path": "91-ic-denetimler/surec-gozden-gecirmeleri/iuc-bidb-frm-001-surec-gozden-gecirme-formu-iuc-bidb-src-023-degerlendirme-1",
        "required": ["MAN.2.BP1", "MAN.2.BP6", "2 VAR, 2 DAĞINIK ve 2 ZAYIF", "LST.013'teki kurumsal organizasyon/görev kaynakları"],
    },
    {
        "path": "07-prosedurler/iuc-bidb-prs-006-organizasyonel-yonetim-proseduru",
        "required": ["341.1PR", "İÜC.BİDB.LST.013", "Personel görünümünün niteliği", "Yönetim Gözden Geçirme"],
    },
    {
        "path": "02-sablonlar/iuc-bidb-frm-002-s-toplanti-tutanagi-sablonu",
        "required": ["İÜC.BİDB.FRM.002.Ş", "Kararlar ve Aksiyonlar", "Takip Koordinatörü"],
    },
    {
        "path": "02-sablonlar/iuc-bidb-lst-013-s-gorev-tanimlari-ve-gorevli-personel-listesi-sablonu",
        "required": ["İÜC.BİDB.LST.013.Ş", "Görev Tanımları ve Görevli Personel Eşleştirmesi", "Görevlendirme kanıtı"],
    },
    {
        "path": "03-kayitlar-ve-listeler/iuc-bidb-lst-013-gorev-tanimlari-ve-gorevli-personel-listesi",
        "required": ["32 görev tanımı", "Yönetici Sekreteri", "Maaş İşleri Personeli", "personel eşleştirmesi yayımlanmamış", "profil.iuc.edu.tr"],
        "forbidden": ["@iuc.edu.tr", "Dahili"],
    },
    {
        "path": "03-kayitlar-ve-listeler/iuc-bidb-lst-001-aktif-dokumanlar-listesi",
        "required": ["İÜC.BİDB.PRS.006", "İÜC.BİDB.FRM.002.Ş", "İÜC.BİDB.LST.013.Ş", "İÜC.BİDB.LST.013"],
    },
    {
        "path": "03-kayitlar-ve-listeler/iuc-bidb-lst-006-standart-surec-envanteri",
        "required": ["MAN.2", "İÜC.BİDB.SRÇ.023", "Aktif", "Confluence'ta yayımlanmış"],
    },
    {
        "path": "03-kayitlar-ve-listeler/iuc-bidb-lst-012-surec-yayginlastirma-ve-bilgilendirme-kaydi",
        "required": ["İÜC.BİDB.SRÇ.023", "PRS.006", "FRM.002.Ş", "LST.013.Ş", "RPR.001 güncellemesi", "Yayın ve iki PNG eki doğrulandı"],
    },
    {
        "path": "09-raporlar/iuc-bidb-rpr-001-surec-performanslari-raporu",
        "required": ["İÜC.BİDB.SRÇ.023", "12 VAR; 6 DAĞINIK; 2 ZAYIF; 1 YOK", "SPICE Olgunluk Seviyesi"],
    },
    {
        "path": "02-sablonlar",
        "required": ["İÜC.BİDB.FRM.002.Ş", "İÜC.BİDB.LST.013.Ş"],
    },
    {
        "path": "03-kayitlar-ve-listeler",
        "required": ["İÜC.BİDB.LST.013", "Görev Tanımları ve Görevli Personel Listesi"],
    },
    {
        "path": "07-prosedurler",
        "required": ["İÜC.BİDB.PRS.006", "Organizasyonel Yönetim Prosedürü"],
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
        "# SRÇ.023 Confluence Paket Doğrulama Raporu",
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
