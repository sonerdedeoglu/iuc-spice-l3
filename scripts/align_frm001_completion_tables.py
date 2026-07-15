#!/usr/bin/env python3
"""Align FRM.001 priority-completion tables to the approved five-column format.

This is a local-only content migration. It updates the active FRM.001 template,
the blank forms for completed processes, and the existing SRÇ.001/SRÇ.004
Değerlendirme #1 records without calling Confluence APIs.
"""
from __future__ import annotations

import html
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAGE_ROOT = ROOT / "confluence/pages/000-root-iuc-bidb-spice-2026-level-3"

TEMPLATE = PAGE_ROOT / "02-sablonlar/iuc-bidb-frm-001-s-surec-gozden-gecirme-formu-sablonu"
SRC001_BLANK = PAGE_ROOT / "01-surec-dokumanlari/iuc-bidb-src-001-dokumantasyon-sureci/iuc-bidb-frm-001-surec-gozden-gecirme-formu-iuc-bidb-src-001"
SRC004_BLANK = PAGE_ROOT / "01-surec-dokumanlari/iuc-bidb-src-004-surec-kurulumu-sureci/iuc-bidb-frm-001-surec-gozden-gecirme-formu-iuc-bidb-src-004"
REVIEWS = PAGE_ROOT / "91-ic-denetimler/surec-gozden-gecirmeleri"
SRC001_REVIEW = REVIEWS / "iuc-bidb-frm-001-surec-gozden-gecirme-formu-iuc-bidb-src-001-degerlendirme-1"
SRC004_REVIEW = REVIEWS / "iuc-bidb-frm-001-surec-gozden-gecirme-formu-iuc-bidb-src-004-degerlendirme-1"

HEADERS = ["Öncelik", "Bulgu / Aksiyon", "Bulgu Türü", "İlgili BP / GP", "Hedef Süreç / İzleme Yeri"]
PLACEHOLDER = [[
    "1",
    "Değerlendirme sırasında doldurulur.",
    "Uygunsuzluk / İyileştirme Fırsatı / Gözlem / Güçlü Uygulama",
    "BP / GP",
    "SRÇ.017 / SRÇ.018 / Değerlendirme #1 / ilgili kayıt",
]]

SRC001_ROWS = [
    ["1", "SRÇ.001 için rol bazlı yetkinlikler tanımlanmalı; ilgili personele süreç eğitimi/bilgilendirmesi verilmeli ve kayıtları tutulmalıdır.", "Gözlem", "GP 3.2.3", "İÜC.BİDB.SRÇ.020 - Eğitim Süreci / Değerlendirme #1"],
    ["2", "İÜC.BİDB.LST.009 - Süreç Performans Ölçüm Seti (İÜC.BİDB.SRÇ.001) kapsamında gerçekleşen performans verileri toplanmalı, analiz edilmeli ve iyileştirme kararlarıyla ilişkilendirilmelidir.", "Gözlem", "GP 3.2.6; GP 3.1.5; GP 2.1.2", "İÜC.BİDB.LST.009 - Süreç Performans Ölçüm Seti (İÜC.BİDB.SRÇ.001) / İÜC.BİDB.RPR.001 - Süreç Performansları Raporu"],
    ["3", "Performans sapmaları için neden, karar, sorumlu, yeniden planlama ve kapanış bilgilerini içeren sistematik izleme kaydı oluşturulmalıdır.", "Gözlem", "GP 2.1.3", "Değerlendirme #1 / İÜC.BİDB.RPR.001 - Süreç Performansları Raporu"],
    ["4", "SRÇ.001 ve temel destek dokümanları için gerçek gözden geçirme, bulgu, çözüm, kapanış ve yayın onayı kayıtları İÜC.BİDB.LST.003 - Doküman Gözden Geçirme Kaydı üzerinden tamamlanmalıdır.", "Gözlem", "SUP.7.BP6; GP 2.2.4", "İÜC.BİDB.LST.003 - Doküman Gözden Geçirme Kaydı / Değerlendirme #1"],
    ["5", "Confluence yayın kaydını tamamlayacak hedef kitle bilgilendirmesi yapılmalı; duyuru/teslim ve gerektiğinde teyit kanıtı İÜC.BİDB.LST.012 - Süreç Yaygınlaştırma ve Bilgilendirme Kaydı ile ilişkilendirilmelidir.", "Gözlem", "SUP.7.BP7; GP 2.1.6; GP 3.2.2", "İÜC.BİDB.LST.012 - Süreç Yaygınlaştırma ve Bilgilendirme Kaydı / Değerlendirme #1"],
    ["6", "Son doküman ve şablon revizyonları İÜC.BİDB.LST.002 - Doküman Değişiklik Kaydı'na işlenmeli; kontrollü dokümanların değişiklik, sürüm ve baseline ilişkisi SRÇ.016 ile uyumlu hâle getirilmelidir.", "Gözlem", "SUP.7.BP8; GP 2.2.3", "İÜC.BİDB.LST.002 - Doküman Değişiklik Kaydı / İÜC.BİDB.SRÇ.016 - Yapılandırma Yönetimi Süreci"],
    ["7", "SRÇ.001'in uygulandığı proje veya kurumsal bağlama özgü uyarlamalar, gerekçeleri ve standart sürece uygunluk kontrolü kayıt altına alınmalıdır.", "Gözlem", "GP 3.2.1", "Değerlendirme #1"],
    ["8", "SRÇ.001 için gerekli insan kaynağı ve zaman tahsisi ile fiilî kaynak kullanımı kayıt altına alınmalıdır.", "Gözlem", "GP 2.1.5; GP 3.2.4", "Değerlendirme #1"],
]

SRC004_ROWS = [
    ["1", "SRÇ.004 ve rol/sorumlulukları hedef kitleye duyurmak; gerçek bilgilendirme ve gerektiğinde katılım/teyit kanıtını İÜC.BİDB.LST.012 - Süreç Yaygınlaştırma ve Bilgilendirme Kaydı ile ilişkilendirmek", "Gözlem", "PIM.1.BP2; GP.2.1.6; GP.3.2.1; GP.3.2.2", "İÜC.BİDB.LST.012 - Süreç Yaygınlaştırma ve Bilgilendirme Kaydı / Değerlendirme #1"],
    ["2", "İÜC.BİDB.LST.009 - Süreç Performans Ölçüm Seti (İÜC.BİDB.SRÇ.004) için ilk gerçek veri toplama dönemini işletmek; sonuçları, sapmaları ve kararları kaydetmek", "Gözlem", "PIM.1.BP6; GP.2.1.2; GP.2.1.3; GP.3.2.6", "İÜC.BİDB.LST.009 - Süreç Performans Ölçüm Seti (İÜC.BİDB.SRÇ.004) / İÜC.BİDB.RPR.001 - Süreç Performansları Raporu"],
    ["3", "Yetkili gözden geçirme, bulgu, düzeltme ve kapanış bilgilerini İÜC.BİDB.LST.003 - Doküman Gözden Geçirme Kaydı veya eşdeğer resmî kayıtla tamamlamak", "Gözlem", "GP.2.2.4", "İÜC.BİDB.LST.003 - Doküman Gözden Geçirme Kaydı / Değerlendirme #1"],
    ["4", "Rol bazlı yetkinlik ihtiyacını doğrulamak; gerekiyorsa İÜC.BİDB.SRÇ.020 - Eğitim Süreci kapsamında eğitim ve katılım kaydı oluşturmak", "Gözlem", "GP.3.2.3", "İÜC.BİDB.SRÇ.020 - Eğitim Süreci / Değerlendirme #1"],
    ["5", "İnsan kaynağı tahsisi ile erişim, yetkilendirme, destek ve sürdürme kanıtlarını doğal kaynak sistemlerde doğrulamak", "Gözlem", "GP.2.1.5; GP.3.2.4; GP.3.2.5", "Değerlendirme #1"],
]


def make_table(rows: list[list[str]], placeholders: bool = False) -> str:
    head = "".join(f'<th class="confluenceTh">{html.escape(value)}</th>' for value in HEADERS)
    body_rows = []
    for row in rows:
        cells = []
        for value in row:
            text = html.escape(value)
            if placeholders:
                text = f"<em>{text}</em>"
            cells.append(f'<td class="confluenceTd">{text}</td>')
        body_rows.append("<tr>" + "".join(cells) + "</tr>")
    return '<table class="wrapped confluenceTable"><thead><tr>' + head + "</tr></thead><tbody>" + "".join(body_rows) + "</tbody></table>"


def replace_completion_table(storage: str, replacement: str) -> str:
    heading = re.search(r"<h2[^>]*>5\.\s*(?:Ö|&Ouml;)ncelikli Tamamlama Listesi</h2>", storage)
    if not heading:
        raise RuntimeError("Öncelikli Tamamlama Listesi başlığı bulunamadı")
    start = storage.find("<table", heading.end())
    end = storage.find("</table>", start)
    if start < 0 or end < 0:
        raise RuntimeError("Öncelikli Tamamlama Listesi tablosu bulunamadı")
    return storage[:start] + replacement + storage[end + len("</table>"):]


def update(page_dir: Path, rows: list[list[str]], placeholders: bool = False) -> None:
    replacement = make_table(rows, placeholders)
    for filename in ["body.storage.xhtml", "body.view.html"]:
        path = page_dir / filename
        content = path.read_text(encoding="utf-8")
        updated = replace_completion_table(content, replacement)
        path.write_text(updated, encoding="utf-8")


def main() -> None:
    for page_dir in [TEMPLATE, SRC001_BLANK, SRC004_BLANK]:
        update(page_dir, PLACEHOLDER, placeholders=True)
    update(SRC001_REVIEW, SRC001_ROWS)
    update(SRC004_REVIEW, SRC004_ROWS)
    print("[DONE] FRM.001 Öncelikli Tamamlama Listesi tabloları hizalandı.")


if __name__ == "__main__":
    main()
