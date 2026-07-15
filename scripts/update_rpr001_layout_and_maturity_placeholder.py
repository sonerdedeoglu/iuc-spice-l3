#!/usr/bin/env python3
"""Align RPR.001 and RPR.001.Ş for scalable trend reporting.

The trend matrix keeps processes on rows and the fixed label set on columns.
The process summary also reserves an intentionally empty SPICE maturity column;
its calculation and display rule will be defined after all process work is done.
"""
from __future__ import annotations

import html
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAGE_ROOT = ROOT / "confluence/pages/000-root-iuc-bidb-spice-2026-level-3"
REPORT_DIR = PAGE_ROOT / "09-raporlar/rpr-001-surec-performanslari-raporu"
TEMPLATE_DIR = PAGE_ROOT / "02-sablonlar/rpr-001-s-surec-performanslari-raporu-sablonu"

REPORT_TITLE = "RPR.001 - Süreç Performansları Raporu"
TEMPLATE_TITLE = "RPR.001.Ş - Süreç Performansları Raporu Şablonu"
MATURITY_HEADER = "SPICE Olgunluk Seviyesi"
TREND_FIRST_HEADER = "Süreç / Gösterge"
TREND_INDICATORS = [
    "BP - VAR", "BP - DAĞINIK", "BP - ZAYIF", "BP - YOK",
    "PA/GP - VAR", "PA/GP - DAĞINIK", "PA/GP - ZAYIF", "PA/GP - YOK",
]

CSS = """
body{margin:0;background:#fff;color:#172b4d;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;line-height:1.55}
.confluence-page{max-width:1200px;margin:0 auto;padding:32px 24px 56px}
h1,h2,h3{color:#0f172a;line-height:1.25}h1{margin-top:0;padding-bottom:12px;border-bottom:1px solid #d8dee4}
table{width:100%;border-collapse:collapse;margin:16px 0;table-layout:auto}
th,td{border:1px solid #c9d1d9;padding:8px 10px;vertical-align:top;overflow-wrap:anywhere}
th{background:#f6f8fa;font-weight:600;text-align:left}
""".strip()


def plain(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", value))).strip()


def table(headers: list[str], rows: list[list[str]]) -> str:
    head = "".join(f'<th class="confluenceTh">{item}</th>' for item in headers)
    body = "".join(
        "<tr>" + "".join(f'<td class="confluenceTd">{cell}</td>' for cell in row) + "</tr>"
        for row in rows
    )
    return f'<table class="wrapped confluenceTable"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>'


def build_view(title: str, storage: str) -> str:
    return (
        '<!doctype html><html lang="tr"><head><meta charset="utf-8">'
        f"<title>{html.escape(title)}</title><style>{CSS}</style></head>"
        f'<body><main class="confluence-page"><h1>{html.escape(title)}</h1>{storage}</main></body></html>'
    )


def section_bounds(doc: str, heading: str) -> tuple[int, int, int]:
    heads = list(re.finditer(r"<h2[^>]*>(.*?)</h2>", doc, flags=re.I | re.S))
    for index, match in enumerate(heads):
        if plain(match.group(1)) == heading:
            end = heads[index + 1].start() if index + 1 < len(heads) else len(doc)
            return match.end(), end, match.start()
    raise RuntimeError(f"RPR.001 section not found: {heading}")


def replace_section_body(doc: str, heading: str, body: str) -> str:
    start, end, _ = section_bounds(doc, heading)
    return doc[:start] + body + doc[end:]


def parse_first_table(section: str) -> tuple[list[str], list[list[str]]]:
    match = re.search(r"<table[^>]*>(.*?)</table>", section, flags=re.I | re.S)
    if not match:
        raise RuntimeError("Expected table was not found")
    rows = re.findall(r"<tr[^>]*>(.*?)</tr>", match.group(1), flags=re.I | re.S)
    parsed = [re.findall(r"<(?:th|td)[^>]*>(.*?)</(?:th|td)>", row, flags=re.I | re.S) for row in rows]
    if len(parsed) < 2:
        raise RuntimeError("Expected table header and body rows")
    return parsed[0], parsed[1:]


def add_maturity_placeholder(doc: str) -> str:
    heading = "4. Süreç Sonuç Özeti"
    start, end, _ = section_bounds(doc, heading)
    headers, rows = parse_first_table(doc[start:end])
    labels = [plain(item) for item in headers]
    if MATURITY_HEADER in labels:
        return doc
    try:
        insert_at = labels.index("PA / GP Dağılımı") + 1
    except ValueError as exc:
        raise RuntimeError("PA / GP Dağılımı column not found in RPR.001 summary") from exc
    headers.insert(insert_at, MATURITY_HEADER)
    for row in rows:
        row.insert(insert_at, "")
    return replace_section_body(doc, heading, table(headers, rows))


def transpose_trends(doc: str, *, template: bool) -> str:
    heading = "5. Etiket Dağılımları ve Eğilimler"
    start, end, _ = section_bounds(doc, heading)
    headers, rows = parse_first_table(doc[start:end])
    labels = [plain(item) for item in headers]
    if labels and labels[0] == TREND_FIRST_HEADER:
        return doc

    if template:
        new_headers = [TREND_FIRST_HEADER, *TREND_INDICATORS]
        new_rows = [
            ["<em>SRÇ.XXX</em>", "", "", "", "", "", "", "", ""],
            ["Eğilim Yorumu", "<em>Gösterge yorumu</em>", "<em>Gösterge yorumu</em>", "<em>Gösterge yorumu</em>", "<em>Gösterge yorumu</em>", "<em>Gösterge yorumu</em>", "<em>Gösterge yorumu</em>", "<em>Gösterge yorumu</em>", "<em>Gösterge yorumu</em>"],
        ]
        return replace_section_body(doc, heading, table(new_headers, new_rows))

    if not labels or labels[0] != "Gösterge" or labels[-1] != "Yorum":
        raise RuntimeError(f"Unsupported RPR.001 trend layout: {labels}")
    row_map = {plain(row[0]): row for row in rows}
    normalized_rows: list[list[str]] = []
    for indicator in TREND_INDICATORS:
        if indicator in row_map:
            normalized_rows.append(row_map[indicator])
        else:
            normalized_rows.append([indicator, *(["0"] * (len(headers) - 2)), "İlgili süreçlerde bu etiket görülmemiştir."])
    new_headers = [TREND_FIRST_HEADER, *TREND_INDICATORS]
    process_headers = headers[1:-1]
    process_rows: list[list[str]] = []
    for process_index, process in enumerate(process_headers, start=1):
        process_rows.append([process, *[row[process_index] for row in normalized_rows]])
    comments = [row[-1] for row in normalized_rows]
    process_rows.append(["Eğilim Yorumu", *comments])
    return replace_section_body(doc, heading, table(new_headers, process_rows))


def align_rpr001_layout(doc: str, *, template: bool = False) -> str:
    return transpose_trends(add_maturity_placeholder(doc), template=template)


def verify(doc: str, *, template: bool) -> None:
    if MATURITY_HEADER not in doc:
        raise RuntimeError("SPICE maturity placeholder column is missing")
    start, end, _ = section_bounds(doc, "5. Etiket Dağılımları ve Eğilimler")
    headers, rows = parse_first_table(doc[start:end])
    if plain(headers[0]) != TREND_FIRST_HEADER:
        raise RuntimeError("Trend table was not transposed")
    if len(headers) != 9 or any(len(row) != len(headers) for row in rows):
        raise RuntimeError("Trend table does not have the fixed nine-column layout")
    if not template and not any(plain(row[0]) == "Eğilim Yorumu" for row in rows):
        raise RuntimeError("Trend comments were not preserved")


def write_page(page_dir: Path, title: str, storage: str) -> None:
    (page_dir / "body.storage.xhtml").write_text(storage.strip() + "\n", encoding="utf-8")
    (page_dir / "body.view.html").write_text(build_view(title, storage.strip()), encoding="utf-8")


def main() -> None:
    targets = [(REPORT_DIR, REPORT_TITLE, False), (TEMPLATE_DIR, TEMPLATE_TITLE, True)]
    for page_dir, title, is_template in targets:
        storage = (page_dir / "body.storage.xhtml").read_text(encoding="utf-8")
        storage = align_rpr001_layout(storage, template=is_template)
        verify(storage, template=is_template)
        write_page(page_dir, title, storage)
        print(f"[UPDATED] {title}")
    print("[TASK] SPICE Olgunluk Seviyesi calculation deferred until all process work is complete")


if __name__ == "__main__":
    main()
