#!/usr/bin/env python3
"""Apply the approved baseline rules to the local process definition template.

The script changes only the local template storage/view files. It does not
publish to Confluence or modify page metadata.
"""
from __future__ import annotations

import html
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = (
    ROOT
    / "confluence/pages/000-root-iuc-bidb-spice-2026-level-3/02-sablonlar"
    / "iuc-bidb-src-xxx-s-surec-tanimi-sablonu"
)
REPORT = ROOT / "reports/process_template_baseline_rules.md"


def plain(value: str) -> str:
    return " ".join(html.unescape(re.sub(r"<[^>]+>", "", value)).split())


def find_heading(body: str, title: str) -> re.Match[str]:
    for match in re.finditer(r"<h2\b[^>]*>.*?</h2>", body, flags=re.I | re.S):
        if plain(match.group(0)) == title:
            return match
    raise RuntimeError(f"Şablon başlığı bulunamadı: {title}")


def replace_section(body: str, title: str, content: str) -> str:
    heading = find_heading(body, title)
    next_heading = re.search(r"<h2\b[^>]*>.*?</h2>", body[heading.end():], flags=re.I | re.S)
    end = heading.end() + next_heading.start() if next_heading else len(body)
    return body[:heading.end()] + content + body[end:]


def replace_row_value(body: str, section_title: str, label: str, value: str) -> str:
    heading = find_heading(body, section_title)
    next_heading = re.search(r"<h2\b[^>]*>.*?</h2>", body[heading.end():], flags=re.I | re.S)
    end = heading.end() + next_heading.start() if next_heading else len(body)
    section = body[heading.end():end]
    for row in re.finditer(r"<tr\b[^>]*>.*?</tr>", section, flags=re.I | re.S):
        cells = list(re.finditer(r"<td\b[^>]*>.*?</td>", row.group(0), flags=re.I | re.S))
        if len(cells) < 2 or plain(cells[0].group(0)) != label:
            continue
        second = cells[1]
        opening = re.match(r"<td\b[^>]*>", second.group(0), flags=re.I)
        if not opening:
            break
        new_cell = opening.group(0) + value + "</td>"
        new_row = row.group(0)[:second.start()] + new_cell + row.group(0)[second.end():]
        new_section = section[:row.start()] + new_row + section[row.end():]
        return body[:heading.end()] + new_section + body[end:]
    raise RuntimeError(f"Şablon tablo satırı bulunamadı: {section_title} / {label}")


def table(headers: list[str], rows: list[list[str]], view: bool) -> str:
    table_class = ' class="wrapped confluenceTable"' if view else ' class="wrapped"'
    th_class = ' class="confluenceTh"' if view else ""
    td_class = ' class="confluenceTd"' if view else ""
    head = "".join(f"<th{th_class}>{item}</th>" for item in headers)
    body = "".join(
        "<tr>" + "".join(f"<td{td_class}>{cell}</td>" for cell in row) + "</tr>"
        for row in rows
    )
    wrapper = '<div class="table-wrap">' if view else ""
    closing = "</div>" if view else ""
    return f'{wrapper}<table{table_class}><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>{closing}'


def references(view: bool) -> str:
    note = (
        "<p><strong>Kullanım Notu:</strong> Bu bölüm yalnızca ilgili ISO/IEC 15504-5 "
        "süreç bölümü, Process Assessment Model ve Process Attributes referanslarını içerir. "
        "İÜC Bilgi İşlem kaynakları belirlendikçe ayrıca eklenir.</p>"
    )
    return note + table(
        ["Referans", "Açıklama"],
        [
            ["ISO/IEC 15504-5 - <em>İlgili süreç bölümü</em>", "Süreç amacı, sonuçları, temel uygulamaları ve ilişkili iş ürünleri"],
            ["ISO/IEC 15504-5 - Process Assessment Model", "Süreç değerlendirme modelinin süreç boyutu ve değerlendirme göstergeleri"],
            ["ISO/IEC 15504-5 - Process Attributes", "Süreç yetenek boyutundaki süreç öznitelikleri ve genel uygulamalar"],
        ],
        view,
    )


def flow(view: bool) -> str:
    lines = [
        "flowchart TD",
        "A[Süreç başlangıcı] --&gt; B[Ana faaliyet]",
        "B --&gt; C{Kontrol noktası}",
        "C -- Hayır --&gt; B",
        "C -- Evet --&gt; D[Süreç bitişi]",
    ]
    code = "<br />".join(f'<code class="language-mermaid">{line}</code>' for line in lines)
    intro = (
        "<p>Mermaid kodu <a href=\"https://www.mermaidonline.live/editor\">Mermaid Online Editor</a> "
        "üzerinden PNG olarak dışa aktarılır ve görsel bu bölümde kod bloğunun üstüne eklenir.</p>"
    )
    if view:
        macro = (
            '<div class="confluence-information-macro has-no-icon confluence-information-macro-information conf-macro output-block" '
            'data-hasbody="true" data-macro-name="info"><p class="title">Mermaid Kodu</p>'
            f'<div class="confluence-information-macro-body"><p style="margin-left:40px">{code}</p></div></div>'
        )
    else:
        macro = (
            '<ac:structured-macro ac:name="info" ac:schema-version="1">'
            '<ac:parameter ac:name="icon">false</ac:parameter>'
            '<ac:parameter ac:name="title">Mermaid Kodu</ac:parameter>'
            f'<ac:rich-text-body><p style="margin-left:40px">{code}</p></ac:rich-text-body>'
            '</ac:structured-macro>'
        )
    return intro + macro


def history(view: bool) -> str:
    return table(
        ["Sürüm", "Tarih", "Açıklama", "Hazırlayan / Güncelleyen", "Gözden Geçiren", "Onay"],
        [
            ["v0.1", "10 Jan 2025", "İlk taslak oluşturuldu.", "Soner DEDEOĞLU - Kalite Danışmanı", "-", "-"],
            ["v1.0", "15 Feb 2025", "<em>[Süreç adı]</em> süreci onaylanarak yürürlüğe girmiştir.", "Soner DEDEOĞLU - Kalite Danışmanı", "<em>Gözden geçiren - Görevi</em>", "<em>Onaycı - Görevi</em>"],
        ],
        view,
    )


def related_processes(body: str) -> str:
    return replace_row_value(
        body,
        "6. Süreç Aktivitesi",
        "İlgili Süreçler",
        "<ul><li><em>İÜC.BİDB.SRÇ.XXX - İlgili Süreç</em></li><li><em>Her süreç ayrı satırda yazılır.</em></li></ul>",
    )


def transform(body: str, view: bool) -> str:
    body = replace_row_value(body, "1. Süreç Bilgileri", "Sürüm", "v1.0")
    body = replace_section(body, "4. Referanslar", references(view))
    body = related_processes(body)
    body = replace_section(body, "10. Süreç Akışı", flow(view))
    body = replace_section(body, "15. Sürüm Geçmişi", history(view))
    return body


def validate(body: str) -> None:
    required = [
        "ISO/IEC 15504-5 - Process Assessment Model",
        "ISO/IEC 15504-5 - Process Attributes",
        "Her süreç ayrı satırda yazılır.",
        "https://www.mermaidonline.live/editor",
        "flowchart TD",
        "10 Jan 2025",
        "15 Feb 2025",
        "Soner DEDEOĞLU - Kalite Danışmanı",
    ]
    missing = [item for item in required if item not in html.unescape(body)]
    if missing:
        raise RuntimeError(f"Şablon temel kural doğrulaması başarısız: {missing}")


def main() -> None:
    for name in ("body.storage.xhtml", "body.view.html"):
        path = TEMPLATE_DIR / name
        original = path.read_text(encoding="utf-8")
        updated = transform(original, name == "body.view.html")
        validate(updated)
        path.write_text(updated, encoding="utf-8")
        print(f"[UPDATED] {path.relative_to(ROOT)}")
    REPORT.write_text(
        "\n".join([
            "# Süreç Şablonu Temel Kuralları", "", "Tarih: 14-07-2026", "",
            "- Referanslar üç ISO/IEC 15504-5 referansıyla sınırlandı.",
            "- İlgili süreçlerin ayrı satırlarda yazılması şablona işlendi.",
            "- Mermaid Online Editor bağlantısı ve Mermaid kod bloğu eklendi.",
            "- Süreç sürümü v1.0 olarak sabitlendi.",
            "- Sürüm geçmişi v0.1 ve v1.0 satırlarıyla standartlaştırıldı.",
            "- Hazırlayan Soner DEDEOĞLU - Kalite Danışmanı olarak sabitlendi.",
            "- Süreç sahibi, gözden geçiren ve onaycı her süreç çalışmasında ayrıca doğrulanacaktır.", "",
        ]),
        encoding="utf-8",
    )
    print(f"[REPORT] {REPORT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
