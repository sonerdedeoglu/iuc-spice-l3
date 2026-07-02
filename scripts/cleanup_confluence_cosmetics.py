import argparse
from html import unescape
from pathlib import Path
import re
import unicodedata

import yaml

from confluence_client import ConfluenceClient


ROOT = Path(__file__).resolve().parent.parent
REPORT_PATH = ROOT / "reports" / "confluence_cosmetic_cleanup_report.md"
FOLDER_PLACEHOLDER = "Bu sayfa, alt dokümanların gruplanması amacıyla oluşturulmuştur."

METADATA_LABELS = [
    "dosya adı",
    "kaynak dosya",
    "yerel dosya",
    "dosya yolu",
    "filename",
    "path",
]

METADATA_SOURCE_TERMS = [
    "dosya adı",
    "kaynak dosya",
    "markdown",
    ".md",
    ".markdown",
]

PROTECTED_BLOCK_PATTERN = re.compile(
    r"(<ac:structured-macro\b(?=[^>]*\bac:name=[\"']code[\"']).*?</ac:structured-macro>|"
    r"<pre\b.*?</pre>)",
    flags=re.I | re.S,
)
TABLE_PATTERN = re.compile(r"<table\b.*?</table>", flags=re.I | re.S)
TABLE_ROW_PATTERN = re.compile(r"<tr\b.*?</tr>", flags=re.I | re.S)
TABLE_CELL_PATTERN = re.compile(r"<(td|th)\b[^>]*>(.*?)</\1>", flags=re.I | re.S)
PARAGRAPH_PATTERN = re.compile(r"<p\b[^>]*>.*?</p>", flags=re.I | re.S)
ANCHOR_PATTERN = re.compile(
    r"<a\b(?P<attrs>[^>]*)>(?P<body>.*?)</a>",
    flags=re.I | re.S,
)
HREF_PATTERN = re.compile(
    r"\bhref\s*=\s*(?P<quote>[\"'])(?P<href>.*?)(?P=quote)",
    flags=re.I | re.S,
)


def load_manifest():
    with open(ROOT / "manifest.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def normalize_text(value):
    return unicodedata.normalize("NFC", str(value)).strip()


def normalize_lower(value):
    value = normalize_text(value).casefold()
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def normalize_for_compare(value):
    value = normalize_lower(value)
    return re.sub(r"\s+", " ", value).strip()


def clean_storage_text(storage):
    storage = re.sub(r"<!\[CDATA\[(.*?)\]\]>", r"\1", storage, flags=re.S)
    storage = re.sub(r"<[^>]+>", " ", storage)
    storage = unescape(storage)
    return re.sub(r"\s+", " ", storage).strip()


def clean_metadata_text(text):
    text = normalize_text(text)
    text = re.sub(r"^[\s\-–—•*]+", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def is_folder_placeholder(body_text):
    return normalize_for_compare(body_text) == normalize_for_compare(FOLDER_PLACEHOLDER)


def crawl_page_tree(client, root_page_id):
    pages_by_id = {}

    def crawl(page_id, parent_id=None, depth=0):
        page = client.get_page(page_id)
        body = page.get("body", {}).get("storage", {}).get("value", "")
        record = {
            "id": str(page["id"]),
            "title": normalize_text(page["title"]),
            "body": body,
            "text": clean_storage_text(body),
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


def find_register_page_ids(manifest, pages_by_id, root_page_id):
    root_page = pages_by_id[str(root_page_id)]
    register_titles = {
        normalize_text(node["title"])
        for node in manifest["nodes"]
        if node["parent"] == "ROOT"
    }
    register_page_ids = set()

    for child_id in root_page["children"]:
        child = pages_by_id.get(child_id)

        if child is not None and child["title"] in register_titles:
            register_page_ids.add(child["id"])

    return register_page_ids


def cleanup_body(body, page_report, report):
    cleaned_parts = []
    position = 0

    for match in PROTECTED_BLOCK_PATTERN.finditer(body):
        cleaned_parts.append(
            cleanup_unprotected_segment(
                body[position:match.start()],
                page_report,
                report,
            )
        )
        cleaned_parts.append(match.group(0))
        position = match.end()

    cleaned_parts.append(
        cleanup_unprotected_segment(
            body[position:],
            page_report,
            report,
        )
    )

    return "".join(cleaned_parts)


def cleanup_unprotected_segment(segment, page_report, report):
    cleaned_parts = []
    position = 0

    for match in TABLE_PATTERN.finditer(segment):
        cleaned_parts.append(
            remove_metadata_paragraphs(
                segment[position:match.start()],
                page_report,
                report,
            )
        )
        cleaned_parts.append(
            remove_metadata_table_rows(
                match.group(0),
                page_report,
                report,
            )
        )
        position = match.end()

    cleaned_parts.append(
        remove_metadata_paragraphs(
            segment[position:],
            page_report,
            report,
        )
    )

    return "".join(cleaned_parts)


def remove_metadata_paragraphs(segment, page_report, report):
    def replace(match):
        paragraph = match.group(0)
        decision = metadata_paragraph_decision(paragraph)

        if decision["remove"]:
            page_report["paragraphs_removed"] += 1
            return ""

        if decision["skip_reason"]:
            add_skipped_candidate(
                report,
                page_report["title"],
                "paragraph",
                decision["skip_reason"],
                decision["text"],
            )

        return paragraph

    return PARAGRAPH_PATTERN.sub(replace, segment)


def remove_metadata_table_rows(table_html, page_report, report):
    def replace(match):
        row = match.group(0)
        decision = metadata_table_row_decision(row)

        if decision["remove"]:
            page_report["rows_removed"] += 1
            return ""

        if decision["skip_reason"]:
            add_skipped_candidate(
                report,
                page_report["title"],
                "table row",
                decision["skip_reason"],
                decision["text"],
            )

        return row

    return TABLE_ROW_PATTERN.sub(replace, table_html)


def metadata_paragraph_decision(paragraph_html):
    text = clean_storage_text(paragraph_html)
    old_markdown_links = extract_old_markdown_links(paragraph_html)

    if not paragraph_has_cleanup_candidate(paragraph_html):
        return keep_decision(text)

    if contains_drive_folder_link(paragraph_html):
        return skip_decision(text, "Drive folder link")

    if contains_confluence_internal_link(paragraph_html):
        return skip_decision(text, "Confluence internal link")

    if paragraph_has_explicit_metadata_phrase(text):
        return remove_decision(text)

    if is_metadata_text(text):
        return remove_decision(text)

    if old_markdown_links and is_metadata_like_context(text, paragraph_html, "paragraph"):
        return remove_decision(text)

    return skip_decision(text, "metadata term outside safe metadata context")


def metadata_table_row_decision(row_html):
    text = clean_storage_text(row_html)
    old_markdown_links = extract_old_markdown_links(row_html)

    if not row_has_cleanup_candidate(row_html):
        return keep_decision(text)

    if contains_drive_folder_link(row_html):
        return skip_decision(text, "Drive folder link")

    if contains_confluence_internal_link(row_html):
        return skip_decision(text, "Confluence internal link")

    if is_table_header_row(row_html):
        return skip_decision(text, "table header row")

    if is_metadata_table_row(row_html):
        return remove_decision(text)

    if old_markdown_links and is_metadata_like_context(text, row_html, "table row"):
        return remove_decision(text)

    return skip_decision(text, "metadata term outside safe metadata context")


def keep_decision(text):
    return {
        "remove": False,
        "skip_reason": "",
        "text": text,
    }


def remove_decision(text):
    return {
        "remove": True,
        "skip_reason": "",
        "text": text,
    }


def skip_decision(text, reason):
    return {
        "remove": False,
        "skip_reason": reason,
        "text": text,
    }


def paragraph_has_cleanup_candidate(paragraph_html):
    return contains_metadata_source_term(paragraph_html) or bool(extract_old_markdown_links(paragraph_html))


def row_has_cleanup_candidate(row_html):
    return contains_metadata_source_term(row_html) or bool(extract_old_markdown_links(row_html))


def contains_metadata_source_term(html):
    haystack = metadata_haystack(html)
    return any(term in haystack for term in METADATA_SOURCE_TERMS)


def metadata_haystack(html):
    link_values = " ".join(
        f"{link['href']} {link['text']}"
        for link in extract_anchor_links(html)
    )
    return normalize_lower(f"{clean_storage_text(html)} {link_values}")


def extract_anchor_links(html):
    links = []

    for match in ANCHOR_PATTERN.finditer(html):
        attrs = match.group("attrs")
        link_body = match.group("body")
        links.append(
            {
                "href": extract_href(attrs),
                "text": clean_storage_text(link_body),
                "raw": match.group(0),
            }
        )

    return links


def extract_href(attrs):
    match = HREF_PATTERN.search(attrs)

    if match is None:
        return ""

    return unescape(match.group("href"))


def extract_old_markdown_links(html):
    return [
        link
        for link in extract_anchor_links(html)
        if link_contains_old_markdown_file(link)
    ]


def link_contains_old_markdown_file(link):
    haystack = normalize_lower(f"{link['href']} {link['text']}")
    return ".md" in haystack or ".markdown" in haystack


def contains_drive_folder_link(html):
    return any(
        "drive.google.com/drive/folders" in normalize_lower(link["href"])
        for link in extract_anchor_links(html)
    )


def contains_confluence_internal_link(html):
    lower_html = normalize_lower(html)

    return (
        "<ac:link" in lower_html
        or "<ri:page" in lower_html
        or any(is_confluence_href(link["href"]) for link in extract_anchor_links(html))
    )


def is_confluence_href(href):
    lower_href = normalize_lower(href)

    return (
        "/pages/viewpage.action" in lower_href
        or "/display/" in lower_href
        or "pageid=" in lower_href
    )


def paragraph_has_explicit_metadata_phrase(text):
    lower_text = normalize_lower(text)
    patterns = [
        r"\bdosya adı\s*:",
        r"\bkaynak dosya\s*:",
        r"\bmarkdown dosyası\b",
        r"\bmarkdown formatında\b",
        r"\.md\s+dosyası\b",
        r"\.markdown\s+dosyası\b",
    ]

    return any(re.search(pattern, lower_text) is not None for pattern in patterns)


def is_metadata_table_row(row_html):
    cells = extract_table_cells(row_html)
    nonempty_cells = [
        cell
        for cell in cells
        if normalize_lower(cell["text"])
    ]

    if not nonempty_cells:
        return False

    combined_text = " ".join(cell["text"] for cell in nonempty_cells)

    if paragraph_has_explicit_metadata_phrase(combined_text):
        return True

    if is_markdown_metadata_note(combined_text):
        return True

    first_cell = nonempty_cells[0]["text"]

    if is_metadata_label_only(first_cell):
        if len(nonempty_cells) == 1:
            return True

        remaining_text = " ".join(cell["text"] for cell in nonempty_cells[1:])

        if has_metadata_value_hint(remaining_text):
            return True

        if len(combined_text) <= 240 and not looks_like_table_header_row(nonempty_cells):
            return True

    return is_metadata_text(combined_text)


def extract_table_cells(row_html):
    return [
        {
            "tag": match.group(1).lower(),
            "text": clean_storage_text(match.group(2)),
            "raw": match.group(2),
        }
        for match in TABLE_CELL_PATTERN.finditer(row_html)
    ]


def is_table_header_row(row_html):
    cells = extract_table_cells(row_html)

    if not cells:
        return False

    if all(cell["tag"] == "th" for cell in cells):
        return True

    return looks_like_table_header_row(cells)


def is_metadata_text(text):
    text = clean_metadata_text(text)

    if not text:
        return False

    if paragraph_has_explicit_metadata_phrase(text):
        return True

    if is_markdown_metadata_note(text):
        return True

    metadata_prefix = parse_metadata_prefix(text)

    if metadata_prefix is None:
        return False

    if metadata_prefix["value"] == "":
        return True

    if metadata_prefix["has_separator"]:
        return True

    return has_metadata_value_hint(metadata_prefix["value"])


def parse_metadata_prefix(text):
    lower_text = normalize_lower(text)

    for label in sorted(METADATA_LABELS, key=len, reverse=True):
        if lower_text == label:
            return {
                "label": label,
                "value": "",
                "has_separator": False,
            }

        if not lower_text.startswith(label):
            continue

        remaining = lower_text[len(label):]

        if not remaining:
            return {
                "label": label,
                "value": "",
                "has_separator": False,
            }

        if not remaining[0].isspace() and remaining[0] not in ":：=|-–—":
            continue

        remaining = remaining.strip()
        has_separator = False

        if remaining.startswith((":", "：", "=", "|", "-", "–", "—")):
            has_separator = True
            remaining = remaining[1:].strip()

        return {
            "label": label,
            "value": remaining,
            "has_separator": has_separator,
        }

    return None


def is_metadata_label_only(text):
    lower_text = normalize_lower(text)
    lower_text = re.sub(r"^[\s:：=|\-–—]+", "", lower_text)
    lower_text = re.sub(r"[\s:：=|\-–—]+$", "", lower_text)
    return lower_text in METADATA_LABELS


def looks_like_table_header_row(cells):
    header_terms = {
        "açıklama",
        "aciklama",
        "description",
        "durum",
        "status",
        "değer",
        "deger",
        "value",
        "bilgi",
    }

    return any(
        normalize_lower(cell["text"]) in header_terms
        for cell in cells[1:]
    )


def has_metadata_value_hint(text):
    lower_text = normalize_lower(text)

    return (
        ".md" in lower_text
        or ".markdown" in lower_text
        or "local" in lower_text
        or "yerel" in lower_text
        or "/" in lower_text
        or "\\" in lower_text
        or re.search(r"\b[a-z]:\\", lower_text) is not None
    )


def is_markdown_metadata_note(text):
    lower_text = normalize_lower(text)

    if "markdown" not in lower_text:
        return False

    return any(
        term in lower_text
        for term in (
            "aktar",
            "import",
            "üretil",
            "olustur",
            "oluştur",
            "format",
            "kaynak",
            "dosya",
        )
    )


def is_metadata_like_context(text, html, container_type):
    lower_text = normalize_lower(text)

    if is_metadata_text(text):
        return True

    if is_only_old_markdown_reference(text, html):
        return True

    if any(term in lower_text for term in ("kaynak", "yerel", "filename", "path", "dosya yolu")):
        return True

    if "markdown" in lower_text and any(term in lower_text for term in ("dosya", "format", "kaynak")):
        return True

    if container_type == "paragraph" and len(lower_text) <= 260 and ".md" in metadata_haystack(html):
        return any(term in lower_text for term in ("dosya", "markdown", "kaynak"))

    return False


def is_only_old_markdown_reference(text, html):
    old_markdown_links = extract_old_markdown_links(html)

    if not old_markdown_links:
        return False

    lower_text = normalize_lower(text)

    if lower_text.endswith(".md") or lower_text.endswith(".markdown"):
        return True

    if len(old_markdown_links) == 1:
        link = old_markdown_links[0]
        link_text = normalize_lower(link["text"])

        if link_text and lower_text == link_text:
            return True

    return False


def add_skipped_candidate(report, page_title, candidate_type, reason, text):
    report["skipped"].append(
        {
            "page": page_title,
            "type": candidate_type,
            "reason": reason,
            "text": text,
        }
    )


def should_skip_page(page, root_page_id, register_page_ids):
    if page["id"] == str(root_page_id):
        return True

    if page["id"] in register_page_ids:
        return True

    if is_folder_placeholder(page["text"]):
        return True

    return False


def write_report(report):
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Confluence Cosmetic Cleanup Report",
        "",
        "## Summary",
        "",
        f"- Mode: {report['mode']}",
        f"- Pages scanned: {report['pages_scanned']}",
        f"- Pages cleaned: {len(report['pages_cleaned'])}",
        f"- Metadata rows removed: {report['rows_removed']}",
        f"- Metadata paragraphs removed: {report['paragraphs_removed']}",
        f"- Skipped candidates: {len(report['skipped'])}",
        "",
        "## Pages cleaned",
        "",
    ]

    if not report["pages_cleaned"]:
        lines.append("No pages cleaned.")
    else:
        for page in report["pages_cleaned"]:
            lines.append(f"- {markdown_text(page['title'])}")

    lines.extend(
        [
            "",
            "## Removed metadata rows/paragraphs count per page",
            "",
        ]
    )

    if not report["pages_cleaned"]:
        lines.append("No metadata rows or paragraphs removed.")
    else:
        for page in report["pages_cleaned"]:
            lines.append(
                f"- {markdown_text(page['title'])}: "
                f"{page['rows_removed']} rows, "
                f"{page['paragraphs_removed']} paragraphs"
            )

    lines.extend(
        [
            "",
            "## Skipped candidates",
            "",
        ]
    )

    if not report["skipped"]:
        lines.append("No skipped candidates.")
    else:
        for skipped in report["skipped"]:
            lines.extend(
                [
                    f"- Page: {markdown_text(skipped['page'])}",
                    f"  Type: {markdown_text(skipped['type'])}",
                    f"  Reason: {markdown_text(skipped['reason'])}",
                    f"  Text: {markdown_text(snippet(skipped['text']))}",
                ]
            )

    REPORT_PATH.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def markdown_text(value):
    return normalize_text(value).replace("\n", " ")


def snippet(value, limit=220):
    text = re.sub(r"\s+", " ", normalize_text(value))

    if len(text) <= limit:
        return text

    return text[:limit - 3] + "..."


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print pages that would be cleaned without updating Confluence.",
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
    register_page_ids = find_register_page_ids(
        manifest,
        pages_by_id,
        root_page_id,
    )
    report = {
        "mode": "dry-run" if args.dry_run else "update",
        "pages_scanned": len(pages_by_id),
        "pages_cleaned": [],
        "rows_removed": 0,
        "paragraphs_removed": 0,
        "skipped": [],
    }

    for page in pages_by_id.values():
        if should_skip_page(page, root_page_id, register_page_ids):
            continue

        page_report = {
            "title": page["title"],
            "rows_removed": 0,
            "paragraphs_removed": 0,
        }
        cleaned_body = cleanup_body(
            page["body"],
            page_report,
            report,
        )

        if cleaned_body == page["body"]:
            continue

        report["rows_removed"] += page_report["rows_removed"]
        report["paragraphs_removed"] += page_report["paragraphs_removed"]
        report["pages_cleaned"].append(page_report)

        if args.dry_run:
            print(f'[DRY-RUN CLEAN] {page["title"]}')
            continue

        print(f'[CLEAN] {page["title"]}')
        client.update_page(
            page["id"],
            space_key,
            page["title"],
            cleaned_body,
            page["version_number"] + 1,
        )

    write_report(report)
    print(f"[DONE] Cleaned {len(report['pages_cleaned'])} pages")


if __name__ == "__main__":
    main()
