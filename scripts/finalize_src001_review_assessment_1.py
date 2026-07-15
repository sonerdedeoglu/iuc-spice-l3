#!/usr/bin/env python3
"""Finalize SRÇ.001 Assessment #1 without changing form/table structures.

Updates only:
- Evaluation date
- Evaluator
- Approver
- Overall evaluation result
- Rows of the existing table under section 5, preserving its headers
"""
from __future__ import annotations

import html
import re
from pathlib import Path

TARGET_DIR = Path(
    "confluence/pages/000-root-iuc-bidb-spice-2026-level-3/91-ic-denetimler/"
    "surec-gozden-gecirmeleri/"
    "frm-001-surec-gozden-gecirme-formu-src-001-degerlendirme-1"
)
STORAGE = TARGET_DIR / "body.storage.xhtml"
VIEW = TARGET_DIR / "body.view.html"

SUMMARY_VALUES = {
    "Değerlendirme Tarihi": "13-02-2026",
    "Değerlendirmeyi Yapan": "Soner DEDEOĞLU - Kalite Danışmanı",
    "Değerlendirmeyi Onaylayan": "Levent BAYEZİT - Süreç Sahibi",
    "Değerlendirme Sonucu": (
        "SRÇ.001 Dokümantasyon Süreci; süreç tanımı, doküman standartları, şablon ailesi, "
        "rol ve sorumluluklar ile temel iş ürünü yapısı bakımından büyük ölçüde kurulmuş ve "
        "uygulanabilir durumdadır. Bununla birlikte gözden geçirme ve yayın onayı kayıtları, "
        "hedef kitleye dağıtım kanıtları, performans sapmalarının izlenmesi, eğitim/yetkinlik "
        "kayıtları ve ölçüm sonuçlarının iyileştirmeye dönüştürülmesi alanlarında tamamlayıcı "
        "çalışmalara ihtiyaç bulunmaktadır. Öncelikli aksiyonların kapatılmasıyla sürecin "
        "Seviye 3 uygulama kanıtları önemli ölçüde güçlenecektir."
    ),
}

ACTIONS = [
    {
        "priority": "Yüksek",
        "action": "SRÇ.001 için rol bazlı yetkinlikler tanımlanmalı; ilgili personele süreç eğitimi/bilgilendirmesi verilmeli ve kayıtları tutulmalıdır.",
        "refs": "GP 3.2.3",
        "target": "31-03-2026",
    },
    {
        "priority": "Yüksek",
        "action": "LST.009 kapsamında gerçekleşen performans verileri toplanmalı, analiz edilmeli ve iyileştirme kararlarıyla ilişkilendirilmelidir.",
        "refs": "GP 3.2.6, GP 3.1.5, GP 2.1.2",
        "target": "31-03-2026",
    },
    {
        "priority": "Yüksek",
        "action": "Performans sapmaları için neden, karar, sorumlu, yeniden planlama ve kapanış bilgilerini içeren sistematik izleme kaydı oluşturulmalıdır.",
        "refs": "GP 2.1.3",
        "target": "31-03-2026",
    },
    {
        "priority": "Yüksek",
        "action": "SRÇ.001, PRS.001, KLV.001, LST.001 ve LST.007 için gerçek gözden geçirme, bulgu, çözüm, kapanış ve yayın onayı kayıtları LST.003 üzerinden tamamlanmalıdır.",
        "refs": "SUP.7.BP6, GP 2.2.4",
        "target": "31-03-2026",
    },
    {
        "priority": "Orta",
        "action": "Doküman türü bazında hedef kitle ve dağıtım yöntemi netleştirilmeli; kritik yayınlar için bilgilendirme/teslim kayıtları tutulmalıdır.",
        "refs": "SUP.7.BP7, GP 2.1.6, GP 3.2.2",
        "target": "15-04-2026",
    },
    {
        "priority": "Orta",
        "action": "Son doküman ve şablon revizyonları LST.002'ye işlenmeli; kontrollü dokümanların değişiklik, sürüm ve baseline ilişkisi SRÇ.016 ile uyumlu hale getirilmelidir.",
        "refs": "SUP.7.BP8, GP 2.2.3",
        "target": "15-04-2026",
    },
    {
        "priority": "Orta",
        "action": "Soru Bankası Projesi için SRÇ.001 uyarlamaları, uyarlama gerekçeleri ve standart sürece uygunluk kontrolü kayıt altına alınmalıdır.",
        "refs": "GP 3.2.1",
        "target": "15-04-2026",
    },
    {
        "priority": "Orta",
        "action": "SRÇ.001 için gerekli insan kaynağı, zaman, araç ve bilgi kaynaklarının tahsis ve kullanım durumu kayıt altına alınmalıdır.",
        "refs": "GP 2.1.5, GP 3.2.4",
        "target": "15-04-2026",
    },
]


def esc(value: object) -> str:
    return html.escape(str(value), quote=False)


def clean(value: str) -> str:
    return html.unescape(re.sub(r"<.*?>", "", value, flags=re.DOTALL)).strip()


def parse_table(block: str) -> tuple[list[str], list[list[str]]]:
    headers = [clean(x) for x in re.findall(r"<th[^>]*>(.*?)</th>", block, flags=re.DOTALL)]
    tbody = re.search(r"<tbody[^>]*>(.*?)</tbody>", block, flags=re.DOTALL)
    rows: list[list[str]] = []
    if tbody:
        for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", tbody.group(1), flags=re.DOTALL):
            rows.append(re.findall(r"<td[^>]*>(.*?)</td>", tr, flags=re.DOTALL))
    return headers, rows


def render_table(headers: list[str], rows: list[list[str]]) -> str:
    head = "".join(f"<th>{esc(h)}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>" for row in rows)
    return f'<table class="wrapped"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>'


def update_summary_table(storage: str) -> str:
    for match in re.finditer(r"<table.*?</table>", storage, flags=re.DOTALL):
        headers, rows = parse_table(match.group(0))
        if len(headers) != 2:
            continue
        labels = {clean(row[0]) for row in rows if row}
        if not set(SUMMARY_VALUES).intersection(labels):
            continue
        new_rows = []
        for row in rows:
            label = clean(row[0]) if row else ""
            if len(row) >= 2 and label in SUMMARY_VALUES:
                row[1] = esc(SUMMARY_VALUES[label])
            new_rows.append(row)
        return storage[:match.start()] + render_table(headers, new_rows) + storage[match.end():]
    raise RuntimeError("Değerlendirme üst bilgi tablosu bulunamadı.")


def map_action_row(headers: list[str], item: dict[str, str]) -> list[str]:
    result: list[str] = []
    for header in headers:
        h = header.casefold()
        if "öncelik" in h:
            result.append(esc(item["priority"]))
        elif "aksiyon" in h or "düzelt" in h or "tamamla" in h:
            result.append(esc(item["action"]))
        elif "bp" in h or "gp" in h or "ilgili" in h or "kaynak" in h:
            result.append(esc(item["refs"]))
        elif "hedef" in h or "kapanış" in h or "tarih" in h:
            result.append(esc(item["target"]))
        elif "sorumlu" in h:
            result.append("Levent BAYEZİT - Süreç Sahibi")
        elif "durum" in h:
            result.append("Açık")
        else:
            result.append("")
    return result


def update_priority_table(storage: str) -> str:
    # Confluence storage içeriğinde bölüm başlıkları h1-h6 olarak bulunmayabilir.
    # Bu nedenle Öncelikli Tamamlama Listesi tablosunu doğrudan mevcut
    # sütun başlıklarından tespit et.
    candidates = []

    for match in re.finditer(
        r"<table.*?</table>",
        storage,
        flags=re.DOTALL | re.IGNORECASE,
    ):
        headers, _rows = parse_table(match.group(0))
        normalized = [
            re.sub(r"\\s+", " ", header).strip().casefold()
            for header in headers
        ]

        has_priority = any("öncelik" in header for header in normalized)
        has_action = any(
            "aksiyon" in header
            or "düzelt" in header
            or "tamamla" in header
            for header in normalized
        )

        # İlave ayırt edici kolonlar:
        # ilgili BP/GP, kaynak, hedef kapanış, tarih, sorumlu veya durum.
        has_reference_or_tracking = any(
            "bp" in header
            or "gp" in header
            or "ilgili" in header
            or "kaynak" in header
            or "hedef" in header
            or "kapanış" in header
            or "tarih" in header
            or "sorumlu" in header
            or "durum" in header
            for header in normalized
        )

        if has_priority and has_action and has_reference_or_tracking:
            candidates.append((match, headers))

    if not candidates:
        all_headers = []
        for match in re.finditer(
            r"<table.*?</table>",
            storage,
            flags=re.DOTALL | re.IGNORECASE,
        ):
            headers, _rows = parse_table(match.group(0))
            if headers:
                all_headers.append(headers)

        raise RuntimeError(
            "Öncelikli Tamamlama Listesi tablosu sütun başlıklarından "
            f"tespit edilemedi. Dosyada bulunan tablolar: {all_headers}"
        )

    if len(candidates) > 1:
        raise RuntimeError(
            "Öncelikli Tamamlama Listesi olabilecek birden fazla tablo "
            f"bulundu: {[headers for _match, headers in candidates]}"
        )

    table_match, headers = candidates[0]

    # Sütun adlarını ve sırasını değiştirmeden yalnızca satırları doldur.
    rows = [map_action_row(headers, item) for item in ACTIONS]

    return (
        storage[:table_match.start()]
        + render_table(headers, rows)
        + storage[table_match.end():]
    )


def update_view(storage: str) -> None:
    current = VIEW.read_text(encoding="utf-8") if VIEW.exists() else ""
    if '<main class="confluence-page">' in current:
        prefix, rest = current.split('<main class="confluence-page">', 1)
        h1_end = rest.find("</h1>")
        suffix = "</main></body></html>\n"
        if h1_end >= 0:
            h1 = rest[: h1_end + 5]
            VIEW.write_text(prefix + '<main class="confluence-page">' + h1 + storage + suffix, encoding="utf-8")
            return
    VIEW.write_text(storage, encoding="utf-8")


def main() -> None:
    if not STORAGE.exists():
        raise RuntimeError("Önce Değerlendirme #1 oluşturulmalıdır.")
    storage = STORAGE.read_text(encoding="utf-8")
    storage = update_summary_table(storage)
    storage = update_priority_table(storage)
    STORAGE.write_text(storage, encoding="utf-8")
    update_view(storage)
    print("[DONE] SRÇ.001 Değerlendirme #1 üst bilgileri ve öncelikli tamamlama listesi güncellendi.")


if __name__ == "__main__":
    main()
