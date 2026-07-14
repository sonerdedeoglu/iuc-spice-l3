#!/usr/bin/env python3
"""Verify the complete local SRÇ.004 design package and supporting documents."""
from __future__ import annotations

import re
from pathlib import Path

import yaml

from create_src001_review_assessment_1 import clean, parse_table


ROOT = Path(__file__).resolve().parents[1]
CONFLUENCE = ROOT / "confluence"
INDEX_PATH = CONFLUENCE / "index.yaml"
BASE = CONFLUENCE / "pages/000-root-iuc-bidb-spice-2026-level-3"
SRC004 = BASE / "01-surec-dokumanlari/iuc-bidb-src-004-surec-kurulumu-sureci"
SRC001 = BASE / "01-surec-dokumanlari/iuc-bidb-src-001-dokumantasyon-sureci"
REVIEW = BASE / "91-ic-denetimler/surec-gozden-gecirmeleri"
REPORT = ROOT / "reports/src004_integrated_review_report.md"


PAGES = {
    "SRÇ.004": SRC004,
    "LST.007": SRC004 / "iuc-bidb-lst-007-surec-etkilesim-matrisi-iuc-bidb-src-004",
    "LST.007 SRÇ.001": SRC001 / "iuc-bidb-lst-007-surec-etkilesim-matrisi-iuc-bidb-src-001",
    "LST.008": SRC004 / "iuc-bidb-lst-008-is-urunleri-ve-kalite-kriterleri-listesi-iuc-bidb-src-004",
    "LST.009": SRC004 / "iuc-bidb-lst-009-surec-performans-olcum-seti-iuc-bidb-src-004",
    "LST.010": SRC004 / "iuc-bidb-lst-010-surec-rol-yetki-ve-raci-matrisi-iuc-bidb-src-004",
    "FRM.001 boş": SRC004 / "iuc-bidb-frm-001-surec-gozden-gecirme-formu-iuc-bidb-src-004",
    "FRM.001 Değerlendirme #1": REVIEW / "iuc-bidb-frm-001-surec-gozden-gecirme-formu-iuc-bidb-src-004-degerlendirme-1",
    "KLV.002": BASE / "05-kilavuzlar/iuc-bidb-klv-002-surec-uyarlama-kilavuzu",
    "KLV.003": BASE / "05-kilavuzlar/iuc-bidb-klv-003-surec-tasarimi-kontrol-kilavuzu",
    "LST.006": BASE / "03-kayitlar-ve-listeler/iuc-bidb-lst-006-standart-surec-envanteri",
    "PRS.002": BASE / "07-prosedurler/iuc-bidb-prs-002-surec-tasarim-proseduru",
}

FULL_LST007 = "İÜC.BİDB.LST.007 - Süreç Etkileşim Matrisi (İÜC.BİDB.SRÇ.004)"
REMOVED_PAGES = [
    REVIEW / "iuc-bidb-lst-004-surec-gozden-gecirme-matrisi-iuc-bidb-src-001",
    REVIEW / "iuc-bidb-lst-004-surec-gozden-gecirme-matrisi-iuc-bidb-src-004",
    BASE / "03-kayitlar-ve-listeler/iuc-bidb-lst-007-surec-mimari-ve-etkilesim-matrisi",
]
FORBIDDEN = [
    "ŞBL.001", "ŞBL.007", "ŞBL.010", "ŞBL.011", "ŞBL.012", "ŞBL.013", "ŞBL.014", "ŞBL.015",
    "Süreç Mimari ve Etkileşim Matrisi", "26 süreç", "26 sürec", "LST.004",
]


def body(name: str) -> str:
    return (PAGES[name] / "body.storage.xhtml").read_text(encoding="utf-8")


def headers(storage: str) -> list[list[str]]:
    output: list[list[str]] = []
    for block in re.findall(r"<table.*?</table>", storage, flags=re.DOTALL):
        table_headers, _ = parse_table(block)
        output.append(table_headers)
    return output


def rows_for(storage: str, required_header: str) -> list[list[str]]:
    for block in re.findall(r"<table.*?</table>", storage, flags=re.DOTALL):
        table_headers, rows = parse_table(block)
        if required_header in table_headers:
            return [[clean(cell) for cell in row] for row in rows]
    raise RuntimeError(f"Tablo bulunamadı: {required_header}")


def verify() -> list[str]:
    findings: list[str] = []
    for name, page_dir in PAGES.items():
        for filename in ("page.yaml", "body.storage.xhtml", "body.view.html"):
            if not (page_dir / filename).exists():
                raise RuntimeError(f"{name} dosyası eksik: {filename}")
        findings.append(f"{name}: temel sayfa dosyaları mevcut")

    for name in PAGES:
        storage = body(name)
        for phrase in FORBIDDEN:
            if phrase in storage:
                raise RuntimeError(f"{name} içinde eski/sabit ifade bulundu: {phrase}")

    guide_headers = [
        ["Alan", "Değer"], ["Referans", "Açıklama"], ["Terim / Kısaltma", "Açıklama"],
        ["İlke", "Açıklama"], ["Kural / Alan", "Açıklama", "Örnek", "Not"],
        ["Adım", "Talimat / Uygulama Adımı", "Açıklama", "Örnek / Kanıt"],
        ["Örnek Alanı", "Kullanım", "Örnek", "Açıklama"],
        ["Kontrol Alanı", "Kontrol Yöntemi", "Sıklık", "Sorumlu", "Kayıt / Kanıt"],
        ["Kayıt / Kanıt", "Kullanım Amacı", "Saklama Yeri", "Sorumlu", "Not"],
        ["Sürüm", "Tarih", "Açıklama", "Hazırlayan/Güncelleyen", "Gözden Geçiren", "Onay"],
    ]
    for name in ("KLV.002", "KLV.003"):
        if headers(body(name)) != guide_headers:
            raise RuntimeError(f"{name} aktif KLV.XXX.Ş tablo yapısıyla uyuşmuyor")
        findings.append(f"{name}: aktif kılavuz şablonu tablo yapısıyla uyumlu")

    lst006_headers = [
        ["Alan", "Değer"], ["Alan", "Kullanım Kuralı"],
        ["Standart Süreç Kodu", "Standart Süreç Adı", "Kurumsal Süreç Kodu", "Kurumsal Süreç Adı", "Süreç Sahibi", "Durum", "Not"],
        ["Sürüm", "Tarih", "Açıklama", "Hazırlayan/Güncelleyen", "Gözden Geçiren", "Onay"],
    ]
    if headers(body("LST.006")) != lst006_headers:
        raise RuntimeError("LST.006 aktif LST.006.Ş tablo yapısıyla uyuşmuyor")
    inventory = rows_for(body("LST.006"), "Standart Süreç Kodu")
    src004_rows = [row for row in inventory if row[2] == "İÜC.BİDB.SRÇ.004"]
    if len(src004_rows) != 1:
        raise RuntimeError("LST.006 içinde tek SRÇ.004 satırı bekleniyordu")
    if src004_rows[0][4] != "Mustafa Nusret SARISAKAL - Bilgi İşlem Daire Başkanı" or src004_rows[0][5] != "Aktif":
        raise RuntimeError("LST.006 SRÇ.004 sahiplik/durum bilgisi yanlış")
    findings.append("LST.006: SRÇ.004 sahiplik ve durum kaydı doğrulandı")

    lst007_dir = PAGES["LST.007"]
    if FULL_LST007 not in body("LST.007"):
        raise RuntimeError("SRÇ.004 süreç özel LST.007 tam adı eksik")
    if "flowchart LR" not in body("LST.007"):
        raise RuntimeError("LST.007 Mermaid kaynağı eksik")
    for asset in (lst007_dir / "assets/src004-surec-etkilesim.mmd", lst007_dir / "attachments/src004-surec-etkilesim.png"):
        if not asset.exists() or asset.stat().st_size == 0:
            raise RuntimeError(f"LST.007 etkileşim varlığı eksik: {asset}")
    for name, png, mmd in (
        ("LST.007", "src004-surec-etkilesim.png", "src004-surec-etkilesim.mmd"),
        ("LST.007 SRÇ.001", "src001-surec-etkilesim.png", "src001-surec-etkilesim.mmd"),
    ):
        storage = body(name)
        section = re.search(r"<h2[^>]*>3\..*?(?=<h2[^>]*>4\.)", storage, flags=re.DOTALL)
        if not section or section.group(0).find("<ac:image") > section.group(0).find("<ac:structured-macro"):
            raise RuntimeError(f"{name} içinde diyagram Mermaid bilgi kutusunun üstünde değil")
        if "Mermaid Kodu" not in section.group(0) or png not in section.group(0):
            raise RuntimeError(f"{name} bölüm 3 içinde PNG veya Mermaid bilgi kutusu eksik")
        if 'ac:width="1000"' not in section.group(0) or "ac:height=" in section.group(0):
            raise RuntimeError(f"{name} diyagramı Confluence için 1000 px genişliğe ayarlanmamış")
        page_dir = PAGES[name]
        for asset in (page_dir / "assets" / mmd, page_dir / "assets" / png, page_dir / "attachments" / png):
            if not asset.exists() or asset.stat().st_size == 0:
                raise RuntimeError(f"{name} etkileşim varlığı eksik: {asset}")
    src004_mermaid = (lst007_dir / "assets/src004-surec-etkilesim.mmd").read_text(encoding="utf-8")
    for document_node in ("TEMPLATES", "PRS002", "KLV002", "KLV003", "LST006", "LST008", "LST009", "LST010", "FRM001", "LST012"):
        if document_node not in src004_mermaid:
            raise RuntimeError(f"SRÇ.004 LST.007 Mermaid modelinde doküman eksik: {document_node}")
    findings.append("LST.007: SRÇ.001 ve SRÇ.004 diyagramları 1000 px genişlikte üstte, Mermaid bilgi kutuları altta; süreç ve doküman etkileşimleri mevcut")

    for name in ("SRÇ.004", "LST.008", "LST.010"):
        if FULL_LST007 not in body(name):
            raise RuntimeError(f"{name} içinde süreç özel LST.007 tam adı bulunamadı")
    findings.append("SRÇ.004, LST.008 ve LST.010: süreç özel LST.007 adıyla tutarlı")

    lst009 = body("LST.009")
    if lst009.count("SRÇ.004-Ö01</td>") != 3 or "SRÇ.004-Ö04" in lst009:
        raise RuntimeError("LST.009 yönetilebilir üç ölçüm kuralıyla uyuşmuyor")
    findings.append("LST.009: üç yönetilebilir ölçüm sınırı korunuyor")

    blank = body("FRM.001 boş")
    if "GG-AA-YYYY" not in blank or "14-07-2026" in blank or "ÖZET SONUÇ" not in blank:
        raise RuntimeError("SRÇ.004 altındaki FRM.001 boş form niteliğinde değil")
    assessment_meta = yaml.safe_load((PAGES["FRM.001 Değerlendirme #1"] / "page.yaml").read_text(encoding="utf-8")) or {}
    assessment = body("FRM.001 Değerlendirme #1")
    if assessment_meta.get("parent_id") != "137265917" or not str(assessment_meta.get("title", "")).endswith("- Değerlendirme #1") or "14-07-2026" not in assessment:
        raise RuntimeError("FRM.001 Değerlendirme #1 yerleşim/ad/içerik kontrolü başarısız")
    findings.append("FRM.001: boş form ve Değerlendirme #1 ayrımı doğru")

    klv002 = body("KLV.002")
    if "ayrı form oluşturulmaz" not in klv002 or "ayrı bir uyarlama/değişiklik formu" not in klv002 or "İÜC.BİDB.SRÇ.018 - Değişiklik Talebi Yönetimi Süreci" not in klv002:
        raise RuntimeError("KLV.002 tek değişiklik yolu kuralını içermiyor")
    findings.append("KLV.002: ayrı form yok; tüm değişiklik ve talepler SRÇ.018'e yönlendiriliyor")

    klv003 = body("KLV.003")
    if "Boş FRM.001" not in klv003 or "Değerlendirme #n" not in klv003 or "sabit toplam" not in klv003:
        raise RuntimeError("KLV.003 yerleşim veya sabit süreç sayısı kontrolünü içermiyor")
    findings.append("KLV.003: boş form, numaralandırılmış değerlendirme ve sabit sayı kuralları tanımlı")

    index = yaml.safe_load(INDEX_PATH.read_text(encoding="utf-8")) or {}
    indexed = index.get("pages", [])
    indexed_rels = {str(page.get("relative_path") or "") for page in indexed}
    for removed in REMOVED_PAGES:
        rel = str(removed.relative_to(CONFLUENCE)).replace("\\", "/")
        if removed.exists() or rel in indexed_rels:
            raise RuntimeError(f"Eski sayfa tamamen kaldırılmadı: {rel}")
    findings.append("Eski iki LST.004 ve merkezi eski LST.007 yerel paket ve indeksten kaldırıldı")
    for name, page_dir in PAGES.items():
        rel = str(page_dir.relative_to(CONFLUENCE)).replace("\\", "/")
        if sum(1 for page in indexed if page.get("relative_path") == rel) != 1:
            raise RuntimeError(f"Confluence indeksinde tek kayıt bekleniyordu: {name}")
    findings.append("Confluence yerel indeksi: tüm hedef sayfalar tekil")
    return findings


def main() -> None:
    findings = verify()
    REPORT.write_text("\n".join([
        "# SRÇ.004 Bütünsel Yerel Gözden Geçirme Raporu", "", "Tarih: 14-07-2026", "",
        "## Sonuç", "", "SRÇ.004 tasarım paketi ve destek dokümanları yerel kontrolleri geçti.", "",
        "## Doğrulanan Kontroller", "", *[f"- {item}" for item in findings], "",
        "## Bilinçli Olarak Bekletilen Kanıtlar", "",
        "- Confluence yayını ve yayın sonrası LST.012 bilgilendirme kaydı yerel onaydan önce üretilmedi.",
        "- Gerçek ölçüm/kullanım verisi oluşmadan performans sonucu üretilmedi.",
        "- Yeni kanıt çevrimi tamamlanmadan Değerlendirme #2 oluşturulmadı.", "",
    ]), encoding="utf-8")
    print("[PASS] SRÇ.004 bütünsel yerel paket kontrolü tamamlandı.")
    print(f"[REPORT] {REPORT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
