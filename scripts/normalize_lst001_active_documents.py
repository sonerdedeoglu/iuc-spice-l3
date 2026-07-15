import argparse
from html import escape, unescape
from pathlib import Path
import re
import unicodedata

import yaml

from confluence_client import ConfluenceClient


ROOT = Path(__file__).resolve().parent.parent
REPORT_PATH = ROOT / "reports" / "lst001_normalization_report.md"
TARGET_TITLE = "LST.001 - Aktif Dokümanlar Listesi"

FINAL_COLUMNS = [
    "Doküman Kodu",
    "Doküman Adı",
    "Tür",
    "Sürüm",
    "Durum",
    "Sahip",
    "Kullanılan Şablon",
    "Klasör",
    "Yürürlük Tarihi",
    "Son Gözden Geçirme",
    "Erişim Linki",
]

REMOVED_COLUMNS = [
    "Dosya Adı",
    "Format",
]

DOCUMENT_CODE_COLUMN_ALIASES = [
    "Doküman Kodu",
    "Doküman ID",
    "ID",
    "Kod",
]

LINK_COLUMN_ALIASES = [
    "Bağlantı / Konum",
    "Bağlantı/Konum",
    "Erişim Linki",
]

REQUIRED_ACTIVE_TABLE_COLUMNS = [
    "Doküman Adı",
    "Tür",
    "Sürüm",
    "Durum",
    "Sahip",
    "Kullanılan Şablon",
    "Klasör",
    "Dosya Adı",
    "Format",
    "Yürürlük Tarihi",
    "Son Gözden Geçirme",
]

TABLE_PATTERN = re.compile(r"<table\b.*?</table>", flags=re.I | re.S)
TABLE_ROW_PATTERN = re.compile(r"<tr\b.*?</tr>", flags=re.I | re.S)
TABLE_CELL_PATTERN = re.compile(
    r"<(?P<tag>td|th)\b(?P<attrs>[^>]*)>(?P<body>.*?)</(?P=tag)>",
    flags=re.I | re.S,
)
ANCHOR_PATTERN = re.compile(r"<a\b(?P<attrs>[^>]*)>.*?</a>", flags=re.I | re.S)
HREF_PATTERN = re.compile(
    r"\bhref\s*=\s*(?P<quote>[\"'])(?P<href>.*?)(?P=quote)",
    flags=re.I | re.S,
)


def load_manifest():
    with open(ROOT / "manifest.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def normalize_text(value):
    return unicodedata.normalize("NFC", str(value)).strip()


def normalize_key(value):
    value = normalize_text(value).casefold()
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def normalize_loose_key(value):
    value = normalize_key(value)
    value = re.sub(r"[^0-9a-zçğıöşüıi]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def clean_storage_text(storage):
    storage = re.sub(r"<!\[CDATA\[(.*?)\]\]>", r"\1", storage, flags=re.S)
    storage = re.sub(r"<[^>]+>", " ", storage)
    storage = unescape(storage)
    return re.sub(r"\s+", " ", storage).strip()


def crawl_page_tree(client, root_page_id):
    pages_by_id = {}

    def crawl(page_id, parent_id=None, depth=0):
        page = client.get_page(page_id)
        body = page.get("body", {}).get("storage", {}).get("value", "")
        record = {
            "id": str(page["id"]),
            "title": normalize_text(page["title"]),
            "body": body,
            "version_number": page["version"]["number"],
            "parent_id": str(parent_id) if parent_id is not None else None,
            "depth": depth,
            "children": [],
        }
        pages_by_id[record["id"]] = record

        children = client.get_children(record["id"]).get("results", [])

        for child in children:
            child_id = str(child["id"])
            record["children"].append(child_id)

        for child_id in record["children"]:
            if child_id not in pages_by_id:
                crawl(child_id, record["id"], depth + 1)

    crawl(str(root_page_id))
    return pages_by_id


def find_target_page(pages_by_id):
    matches = [
        page
        for page in pages_by_id.values()
        if page["title"] == TARGET_TITLE
    ]

    if not matches:
        raise ValueError(f"Target page not found under configured root page: {TARGET_TITLE}")

    if len(matches) > 1:
        raise ValueError(f"Multiple target pages found under configured root page: {TARGET_TITLE}")

    return matches[0]


def normalize_body(body):
    selected_table = None
    detected_tables = []

    for match in TABLE_PATTERN.finditer(body):
        table = parse_table(match.group(0))
        detected_tables.append(table)

        if is_active_documents_table(table):
            selected_table = {
                "match": match,
                "table": table,
            }
            break

    if selected_table is None:
        print_detected_table_headers(detected_tables)
        raise ValueError("Active documents table not found on target page")

    normalized_table, table_report = normalize_table(selected_table["table"])
    start = selected_table["match"].start()
    end = selected_table["match"].end()
    normalized_body = body[:start] + normalized_table + body[end:]

    return normalized_body, table_report


def parse_table(table_html):
    rows = []

    for row_match in TABLE_ROW_PATTERN.finditer(table_html):
        row_html = row_match.group(0)
        cells = []

        for cell_match in TABLE_CELL_PATTERN.finditer(row_html):
            cells.append(
                {
                    "tag": cell_match.group("tag").lower(),
                    "attrs": cell_match.group("attrs"),
                    "body": cell_match.group("body"),
                    "text": clean_storage_text(cell_match.group("body")),
                }
            )

        if cells:
            rows.append(
                {
                    "html": row_html,
                    "cells": cells,
                }
            )

    if not rows:
        raise ValueError("Table has no rows")

    header_index = find_header_row_index(rows)
    header_cells = rows[header_index]["cells"]

    return {
        "rows": rows,
        "header_index": header_index,
        "headers": [cell["text"] for cell in header_cells],
        "data_rows": rows[header_index + 1:],
    }


def find_header_row_index(rows):
    for index, row in enumerate(rows):
        header_texts = [cell["text"] for cell in row["cells"]]

        if (
            find_column_index(header_texts, DOCUMENT_CODE_COLUMN_ALIASES) >= 0
            and find_column_index(header_texts, ["Doküman Adı"]) >= 0
        ):
            return index

        required_match_count = sum(
            1
            for column in REQUIRED_ACTIVE_TABLE_COLUMNS
            if find_column_index(header_texts, [column]) >= 0
        )

        if required_match_count >= 8:
            return index

    return 0


def is_active_documents_table(table):
    headers = table["headers"]

    required_present = all(
        find_column_index(headers, [column]) >= 0
        for column in REQUIRED_ACTIVE_TABLE_COLUMNS
    )
    final_present = all(
        find_column_index(headers, [column]) >= 0
        for column in FINAL_COLUMNS
    )

    return (required_present or final_present) and (
        find_column_index(headers, DOCUMENT_CODE_COLUMN_ALIASES) >= 0
        or required_present
    )


def normalize_table(table):
    old_columns = table["headers"]
    link_column_index = find_column_index(old_columns, LINK_COLUMN_ALIASES)
    removed_column_indexes = find_removed_column_indexes(old_columns)
    renamed_column = find_renamed_column(old_columns)
    normalized_rows = []
    link_summary = {
        "rows_with_internal_links": 0,
        "rows_with_drive_links_only": 0,
        "rows_with_empty_links": 0,
        "rows_with_other_links": 0,
    }

    for row in table["data_rows"]:
        normalized_cells = []

        for column in FINAL_COLUMNS:
            old_index = find_old_column_index(column, old_columns, link_column_index)
            cell_body = get_cell_body(row, old_index)

            if column == "Erişim Linki":
                cell_body = normalize_link_cell(cell_body)
                update_link_summary(link_summary, cell_body)

            normalized_cells.append(cell_body)

        normalized_rows.append(normalized_cells)

    return build_table(normalized_rows), {
        "old_columns": old_columns,
        "new_columns": FINAL_COLUMNS,
        "removed_columns": [
            old_columns[index]
            for index in removed_column_indexes
        ],
        "removed_column_indexes": removed_column_indexes,
        "renamed_column": renamed_column,
        "row_count": len(normalized_rows),
        "link_summary": link_summary,
    }


def find_column_index(headers, aliases):
    normalized_aliases = {
        normalize_key(alias)
        for alias in aliases
    }
    loose_aliases = {
        normalize_loose_key(alias)
        for alias in aliases
    }

    for index, header in enumerate(headers):
        if normalize_key(header) in normalized_aliases:
            return index

        if normalize_loose_key(header) in loose_aliases:
            return index

    return -1


def find_removed_column_indexes(old_columns):
    indexes = []

    for column in REMOVED_COLUMNS:
        index = find_column_index(old_columns, [column])

        if index >= 0 and index not in indexes:
            indexes.append(index)

    return indexes


def find_renamed_column(old_columns):
    old_index = find_column_index(old_columns, ["Bağlantı / Konum", "Bağlantı/Konum"])

    if old_index < 0:
        return ""

    return f"{old_columns[old_index]} -> Erişim Linki"


def find_old_column_index(column, old_columns, link_column_index):
    if column == "Erişim Linki":
        return link_column_index

    if column == "Doküman Kodu":
        index = find_column_index(old_columns, DOCUMENT_CODE_COLUMN_ALIASES)

        if index >= 0:
            return index

        if old_columns:
            return 0

        return -1

    return find_column_index(old_columns, [column])


def print_detected_table_headers(detected_tables):
    if not detected_tables:
        print("Detected table headers: none")
        return

    print("Detected table headers:")

    for table_number, table in enumerate(detected_tables, start=1):
        print(f"Table {table_number}:")

        for header in table["headers"]:
            print(f"- {header}")


def get_cell_body(row, index):
    if index < 0 or index >= len(row["cells"]):
        return ""

    return row["cells"][index]["body"]


def normalize_link_cell(cell_body):
    if has_internal_link(cell_body):
        return remove_drive_links(cell_body)

    return cell_body


def has_internal_link(cell_body):
    lower_body = normalize_key(cell_body)

    if "<ac:link" in lower_body and "<ri:page" in lower_body:
        return True

    if "<ri:page" in lower_body:
        return True

    return any(
        is_confluence_href(extract_href(match.group("attrs")))
        for match in ANCHOR_PATTERN.finditer(cell_body)
    )


def is_confluence_href(href):
    lower_href = normalize_key(href)

    return (
        "/pages/viewpage.action" in lower_href
        or "/display/" in lower_href
        or "pageid=" in lower_href
    )


def remove_drive_links(cell_body):
    def replace(match):
        href = extract_href(match.group("attrs"))

        if is_drive_href(href):
            return ""

        return match.group(0)

    cleaned = ANCHOR_PATTERN.sub(replace, cell_body)
    cleaned = re.sub(
        r"<p>\s*(?:&nbsp;|\s|<br\s*/?>)*</p>",
        "",
        cleaned,
        flags=re.I,
    )
    return cleaned.strip()


def extract_href(attrs):
    match = HREF_PATTERN.search(attrs)

    if match is None:
        return ""

    return unescape(match.group("href"))


def is_drive_href(href):
    lower_href = normalize_key(href)
    return "drive.google.com" in lower_href or "docs.google.com" in lower_href


def update_link_summary(link_summary, cell_body):
    if has_internal_link(cell_body):
        link_summary["rows_with_internal_links"] += 1
    elif has_drive_link(cell_body):
        link_summary["rows_with_drive_links_only"] += 1
    elif clean_storage_text(cell_body):
        link_summary["rows_with_other_links"] += 1
    else:
        link_summary["rows_with_empty_links"] += 1


def has_drive_link(cell_body):
    return any(
        is_drive_href(extract_href(match.group("attrs")))
        for match in ANCHOR_PATTERN.finditer(cell_body)
    )


def build_table(rows):
    table_rows = [
        "<tr>"
        + "".join(
            f"<td>{cell}</td>"
            for cell in row
        )
        + "</tr>"
        for row in rows
    ]

    return "\n".join(
        [
            "<table>",
            "<thead>",
            "<tr>",
            *[
                f"<th>{escape(column, quote=True)}</th>"
                for column in FINAL_COLUMNS
            ],
            "</tr>",
            "</thead>",
            "<tbody>",
            *table_rows,
            "</tbody>",
            "</table>",
        ]
    )


def write_report(report):
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# LST.001 Normalization Report",
        "",
        "## Old columns",
        "",
        *[f"- {markdown_text(column)}" for column in report["old_columns"]],
        "",
        "## New columns",
        "",
        *[f"- {markdown_text(column)}" for column in report["new_columns"]],
        "",
        "## Row count",
        "",
        f"- {report['row_count']}",
        "",
        "## Removed columns",
        "",
    ]

    if report["removed_columns"]:
        lines.extend(f"- {markdown_text(column)}" for column in report["removed_columns"])
    else:
        lines.append("No matching old columns removed.")

    lines.extend(
        [
            "",
            "## Removed column indexes",
            "",
        ]
    )

    if report["removed_column_indexes"]:
        lines.extend(
            f"- {index + 1}"
            for index in report["removed_column_indexes"]
        )
    else:
        lines.append("No matching old column indexes removed.")

    lines.extend(
        [
            "",
            "## Renamed column",
            "",
            f"- {markdown_text(report['renamed_column']) if report['renamed_column'] else 'No column renamed.'}",
            "",
            "## Link column status summary",
            "",
            f"- Rows with internal links: {report['link_summary']['rows_with_internal_links']}",
            f"- Rows with Drive links only: {report['link_summary']['rows_with_drive_links_only']}",
            f"- Rows with other link/text values: {report['link_summary']['rows_with_other_links']}",
            f"- Rows with empty links: {report['link_summary']['rows_with_empty_links']}",
        ]
    )

    REPORT_PATH.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def markdown_text(value):
    return normalize_text(value).replace("\n", " ")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print detected columns and row count without updating Confluence.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    manifest = load_manifest()
    client = ConfluenceClient()
    space_key = manifest["confluence"]["space"]
    root_page_id = str(manifest["confluence"]["root"]["page_id"])
    pages_by_id = crawl_page_tree(
        client,
        root_page_id,
    )
    page = find_target_page(pages_by_id)
    normalized_body, report = normalize_body(page["body"])

    write_report(report)

    if args.dry_run:
        print("Detected table headers:")

        for column in report["old_columns"]:
            print(f"- {column}")

        print("Old columns:")

        for column in report["old_columns"]:
            print(f"- {column}")

        print("Removed column indexes:")

        if report["removed_column_indexes"]:
            for index in report["removed_column_indexes"]:
                print(f"- {index + 1}")
        else:
            print("- none")

        print("Renamed column:")
        print(f"- {report['renamed_column'] if report['renamed_column'] else 'none'}")

        print("Final columns:")

        for column in report["new_columns"]:
            print(f"- {column}")

        print(f'Rows that would be normalized: {report["row_count"]}')
        print("[DONE]")
        return

    print(f"[NORMALIZE] {TARGET_TITLE}")
    client.update_page(
        page["id"],
        space_key,
        page["title"],
        normalized_body,
        page["version_number"] + 1,
    )
    print("[DONE]")


if __name__ == "__main__":
    main()
