import argparse
from html import unescape
from pathlib import Path
import re
import unicodedata

import yaml

from confluence_client import ConfluenceClient


ROOT = Path(__file__).resolve().parent.parent
FOLDER_PLACEHOLDER = "Bu sayfa, alt dokümanların gruplanması amacıyla oluşturulmuştur."

METADATA_LABELS = [
    "dosya adı",
    "kaynak dosya",
    "yerel dosya",
    "dosya yolu",
    "filename",
    "path",
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


def cleanup_body(body):
    cleaned_parts = []
    position = 0

    for match in PROTECTED_BLOCK_PATTERN.finditer(body):
        cleaned_parts.append(
            cleanup_unprotected_segment(body[position:match.start()])
        )
        cleaned_parts.append(match.group(0))
        position = match.end()

    cleaned_parts.append(
        cleanup_unprotected_segment(body[position:])
    )

    return "".join(cleaned_parts)


def cleanup_unprotected_segment(segment):
    cleaned_parts = []
    position = 0

    for match in TABLE_PATTERN.finditer(segment):
        cleaned_parts.append(
            remove_metadata_paragraphs(segment[position:match.start()])
        )
        cleaned_parts.append(
            remove_metadata_table_rows(match.group(0))
        )
        position = match.end()

    cleaned_parts.append(
        remove_metadata_paragraphs(segment[position:])
    )

    return "".join(cleaned_parts)


def remove_metadata_paragraphs(segment):
    def replace(match):
        paragraph = match.group(0)

        if is_metadata_paragraph(paragraph):
            return ""

        return paragraph

    return PARAGRAPH_PATTERN.sub(replace, segment)


def remove_metadata_table_rows(table_html):
    def replace(match):
        row = match.group(0)

        if is_metadata_table_row(row):
            return ""

        return row

    return TABLE_ROW_PATTERN.sub(replace, table_html)


def is_metadata_paragraph(paragraph_html):
    text = clean_storage_text(paragraph_html)
    return is_metadata_text(text)


def is_metadata_table_row(row_html):
    cells = [
        clean_storage_text(match.group(2))
        for match in TABLE_CELL_PATTERN.finditer(row_html)
    ]
    nonempty_cells = [
        cell
        for cell in cells
        if normalize_lower(cell)
    ]

    if not nonempty_cells:
        return False

    combined_text = " ".join(nonempty_cells)

    if is_markdown_metadata_note(combined_text):
        return True

    first_cell = nonempty_cells[0]

    if is_metadata_label_only(first_cell):
        if len(nonempty_cells) == 1:
            return True

        remaining_text = " ".join(nonempty_cells[1:])

        if has_metadata_value_hint(remaining_text):
            return True

        if len(combined_text) <= 240 and not looks_like_table_header_row(nonempty_cells):
            return True

    return is_metadata_text(combined_text)


def is_metadata_text(text):
    text = clean_metadata_text(text)

    if not text:
        return False

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


def clean_metadata_text(text):
    text = normalize_text(text)
    text = re.sub(r"^[\s\-–—•*]+", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


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
        normalize_lower(cell) in header_terms
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


def should_skip_page(page, root_page_id, register_page_ids):
    if page["id"] == str(root_page_id):
        return True

    if page["id"] in register_page_ids:
        return True

    if is_folder_placeholder(page["text"]):
        return True

    return False


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
    cleaned_count = 0

    for page in pages_by_id.values():
        if should_skip_page(page, root_page_id, register_page_ids):
            continue

        cleaned_body = cleanup_body(page["body"])

        if cleaned_body == page["body"]:
            continue

        cleaned_count += 1

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

    print(f"[DONE] Cleaned {cleaned_count} pages")


if __name__ == "__main__":
    main()
