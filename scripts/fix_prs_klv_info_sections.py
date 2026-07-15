#!/usr/bin/env python3
from __future__ import annotations

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOCS = [
    {
        "path": ROOT / "confluence/pages/000-root-iuc-bidb-spice-2026-level-3/02-sablonlar/prs-xxx-s-prosedur-tanimi-sablonu/body.storage.xhtml",
        "heading": "1. Prosedür Bilgileri",
        "rows": [
            ("Kurum", "İstanbul Üniversitesi - Cerrahpaşa Bilgi İşlem Daire Başkanlığı"),
            ("Prosedür Kodu ve Adı", "PRS.<em>XXX</em> - <em>Prosedür adı</em>"),
            ("Prosedür Referansı", "<em>Standart / iç referans / ilişkili süreç</em>"),
            ("Prosedür Sahibi", "<em>Birim / rol</em>"),
            ("Durum", "<em>Taslak / Gözden Geçirildi / Onaylı / Aktif</em>"),
            ("Sürüm", "<em>v0.1 / v1.0 / v1.1</em>"),
            ("Yürürlük Tarihi", "<em>GG-AA-YYYY</em>"),
            ("Son Gözden Geçirme Tarihi", "<em>GG-AA-YYYY</em>"),
        ],
    },
    {
        "path": ROOT / "confluence/pages/000-root-iuc-bidb-spice-2026-level-3/02-sablonlar/klv-xxx-s-kilavuz-ve-talimat-tanimi-sablonu/body.storage.xhtml",
        "heading": "1. Kılavuz / Talimat Bilgileri",
        "rows": [
            ("Kurum", "İstanbul Üniversitesi - Cerrahpaşa Bilgi İşlem Daire Başkanlığı"),
            ("Kılavuz / Talimat Kodu ve Adı", "KLV.<em>XXX</em> - <em>Kılavuz / Talimat adı</em>"),
            ("Kılavuz / Talimat Referansı", "<em>Standart / iç referans / ilişkili süreç</em>"),
            ("Kılavuz / Talimat Sahibi", "<em>Birim / rol</em>"),
            ("Durum", "<em>Taslak / Gözden Geçirildi / Onaylı / Aktif</em>"),
            ("Sürüm", "<em>v0.1 / v1.0 / v1.1</em>"),
            ("Yürürlük Tarihi", "<em>GG-AA-YYYY</em>"),
            ("Son Gözden Geçirme Tarihi", "<em>GG-AA-YYYY</em>"),
        ],
    },
    {
        "path": ROOT / "confluence/pages/000-root-iuc-bidb-spice-2026-level-3/07-prosedurler/prs-001-yazilim-projeleri-dokumantasyon-proseduru/body.storage.xhtml",
        "heading": "1. Prosedür Bilgileri",
        "rows": [
            ("Kurum", "İstanbul Üniversitesi - Cerrahpaşa Bilgi İşlem Daire Başkanlığı"),
            ("Prosedür Kodu ve Adı", "PRS.001 - Yazılım Projeleri Dokümantasyon Prosedürü"),
            ("Prosedür Referansı", "ISO/IEC 15504-5 SUP.7 - Documentation; SRÇ.001 - Dokümantasyon Süreci"),
            ("Prosedür Sahibi", "Levent BAYEZİT - Proje Yöneticisi"),
            ("Durum", "Onaylı"),
            ("Sürüm", "v1.2"),
            ("Yürürlük Tarihi", "29-06-2026"),
            ("Son Gözden Geçirme Tarihi", "30-06-2026"),
        ],
    },
    {
        "path": ROOT / "confluence/pages/000-root-iuc-bidb-spice-2026-level-3/05-kilavuzlar/klv-001-dokuman-yazim-kurallari-talimati/body.storage.xhtml",
        "heading": "1. Kılavuz / Talimat Bilgileri",
        "rows": [
            ("Kurum", "İstanbul Üniversitesi - Cerrahpaşa Bilgi İşlem Daire Başkanlığı"),
            ("Kılavuz / Talimat Kodu ve Adı", "KLV.001 - Doküman Yazım Kuralları Talimatı"),
            ("Kılavuz / Talimat Referansı", "ISO/IEC 15504-5 SUP.7 - Documentation; SRÇ.001 - Dokümantasyon Süreci"),
            ("Kılavuz / Talimat Sahibi", "Proje Geliştirme Yönetimi"),
            ("Durum", "Onaylı"),
            ("Sürüm", "v1.2"),
            ("Yürürlük Tarihi", "29-06-2026"),
            ("Son Gözden Geçirme Tarihi", "30-06-2026"),
        ],
    },
]

FIRST_INFO_RE = re.compile(
    r"<h2>\s*1\.\s*.*?Bilgileri\s*</h2>\s*<table.*?</table>",
    flags=re.DOTALL,
)


def table(rows: list[tuple[str, str]]) -> str:
    body = "".join(
        f"<tr><td>{html.escape(label, quote=False)}</td><td>{value}</td></tr>"
        for label, value in rows
    )
    return (
        '<table class="wrapped">'
        "<thead><tr><th>Alan</th><th>Değer</th></tr></thead>"
        f"<tbody>{body}</tbody>"
        "</table>"
    )


def fix(path: Path, heading: str, rows: list[tuple[str, str]]) -> None:
    text = path.read_text(encoding="utf-8")

    if "<h2>1." not in text and "<h2>1&nbsp;" not in text and text.lstrip().startswith("<table"):
        text = "<h2>1. Doküman Bilgileri</h2>\n" + text

    replacement = f"<h2>{heading}</h2>\n{table(rows)}"

    new_text, count = FIRST_INFO_RE.subn(replacement, text, count=1)
    if count != 1:
        raise RuntimeError(f"1. bilgi bölümü bulunamadı: {path}")

    path.write_text(new_text, encoding="utf-8")
    print(f"[DONE] {path.relative_to(ROOT)}")


def main() -> None:
    for doc in DOCS:
        fix(doc["path"], doc["heading"], doc["rows"])


if __name__ == "__main__":
    main()
