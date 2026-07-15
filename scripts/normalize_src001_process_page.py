import argparse
from html import escape, unescape
from pathlib import Path
import re
import unicodedata

import yaml

from confluence_client import ConfluenceClient


ROOT = Path(__file__).resolve().parent.parent
REPORT_DIR = ROOT / "reports"
BEFORE_STORAGE_PATH = REPORT_DIR / "src001_before_storage.xhtml"
AFTER_STORAGE_PATH = REPORT_DIR / "src001_after_storage.xhtml"
REPORT_PATH = REPORT_DIR / "src001_normalization_report.md"

TARGET_TITLE = "SRÇ.001 - Dokümantasyon Süreci"

HIGH_LEVEL_SECTIONS = [
    "Doküman Bilgileri",
    "Amaç",
    "Kapsam",
    "Roller ve Sorumluluklar",
    "Süreç Akışı",
    "Girdiler",
    "Çıktılar",
    "Uygulama Esasları",
    "İlgili Dokümanlar",
    "Kayıtlar",
    "Gözden Geçirme ve İyileştirme",
]

CODE_MACRO_PATTERN = re.compile(
    r"<ac:structured-macro\b(?=[^>]*\bac:name\s*=\s*['\"]code['\"])[^>]*>.*?</ac:structured-macro>",
    flags=re.I | re.S,
)
PRE_PATTERN = re.compile(r"<pre\b[^>]*>.*?</pre>", flags=re.I | re.S)
CODE_TAG_PATTERN = re.compile(r"<code\b[^>]*>.*?</code>", flags=re.I | re.S)
PARAGRAPH_PATTERN = re.compile(r"<p\b[^>]*>.*?</p>", flags=re.I | re.S)
TABLE_PATTERN = re.compile(r"<table\b.*?</table>", flags=re.I | re.S)
TABLE_ROW_PATTERN = re.compile(r"<tr\b.*?</tr>", flags=re.I | re.S)
TABLE_CELL_PATTERN = re.compile(
    r"<(?P<tag>td|th)\b[^>]*>(?P<body>.*?)</(?P=tag)>",
    flags=re.I | re.S,
)
METADATA_LABEL_PATTERN = re.compile(
    r"^(dosya adı|kaynak dosya|kaynak dosyası|yerel dosya|dosya yolu|filename|path)\s*[:：-]",
    flags=re.I,
)
MARKDOWN_HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.+)$")
UNORDERED_LIST_PATTERN = re.compile(r"^\s*[-*]\s+(.+)$")
ORDERED_LIST_PATTERN = re.compile(r"^\s*\d+[\.)]\s+(.+)$")


def load_manifest():
    with open(ROOT / "manifest.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def normalize_text(value):
    return unicodedata.normalize("NFC", str(value)).strip()


def normalize_key(value):
    value = normalize_text(value).casefold()
    value = re.sub(r"^#+\s*", "", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def clean_storage_text(storage, preserve_lines=False):
    storage = re.sub(r"<!\[CDATA\[(.*?)\]\]>", r"\1", storage, flags=re.S)
    storage = re.sub(r"<br\s*/?>", "\n", storage, flags=re.I)
    storage = re.sub(r"<[^>]+>", " " if not preserve_lines else "", storage)
    text = unescape(storage).replace("\xa0", " ")

    if preserve_lines:
        lines = [
            re.sub(r"[ \t]+", " ", line).strip()
            for line in text.splitlines()
        ]
        return "\n".join(lines).strip()

    return re.sub(r"\s+", " ", text).strip()


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


def empty_stats():
    return {
        "code_pre_blocks_converted": 0,
        "markdown_artifacts_removed": 0,
        "metadata_remnants_removed": 0,
    }


def normalize_body(body, page_title):
    stats = empty_stats()
    normalized = body
    normalized = convert_accidental_code_blocks(normalized, page_title, stats)
    normalized = remove_duplicate_initial_title_heading(normalized, page_title, stats)
    normalized = remove_metadata_table_rows(normalized, stats)
    normalized = normalize_paragraphs(normalized, page_title, stats)
    normalized = remove_empty_paragraph_runs(normalized)
    return normalized.strip(), stats


def convert_accidental_code_blocks(body, page_title, stats):
    for pattern in (CODE_MACRO_PATTERN, PRE_PATTERN, CODE_TAG_PATTERN):
        body = pattern.sub(
            lambda match: convert_code_block(match.group(0), page_title, stats),
            body,
        )

    return body


def convert_code_block(block_html, page_title, stats):
    if contains_internal_confluence_link(block_html):
        return block_html

    text = clean_storage_text(block_html, preserve_lines=True)

    if not text:
        return block_html

    if should_keep_code_block(block_html, text):
        return block_html

    rendered = render_markdownish_text(text, page_title, stats)

    if not rendered:
        return ""

    stats["code_pre_blocks_converted"] += 1
    return rendered


def should_keep_code_block(block_html, text):
    lower_block = block_html.lower()
    single_line = "\n" not in text.strip()

    if lower_block.startswith("<code") and single_line and not looks_like_markdown_document_text(text):
        return True

    return looks_like_true_code(text)


def looks_like_markdown_document_text(text):
    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    if not lines:
        return False

    if any(MARKDOWN_HEADING_PATTERN.match(line) for line in lines):
        return True

    if any(UNORDERED_LIST_PATTERN.match(line) for line in lines):
        return True

    if any(ORDERED_LIST_PATTERN.match(line) for line in lines):
        return True

    if any(is_markdown_table_line(line) for line in lines):
        return True

    normalized = normalize_key(text)
    return any(
        normalize_key(section) in normalized
        for section in HIGH_LEVEL_SECTIONS
    )


def looks_like_true_code(text):
    if looks_like_markdown_document_text(text):
        return False

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    if not lines:
        return False

    code_keyword_pattern = re.compile(
        r"\b(def|class|import|from|function|const|let|var|return|select|insert|update|delete|"
        r"create table|curl|git|npm|python|bash|json|yaml|xml|http|https)\b",
        flags=re.I,
    )

    if any(code_keyword_pattern.search(line) for line in lines):
        return True

    punctuation_count = len(re.findall(r"[{}();=<>]", text))
    return punctuation_count >= 8 and punctuation_count >= len(lines) * 2


def remove_duplicate_initial_title_heading(body, page_title, stats):
    heading_match = re.match(
        r"(?P<prefix>\s*)<h(?P<level>[1-6])\b[^>]*>(?P<body>.*?)</h(?P=level)>",
        body,
        flags=re.I | re.S,
    )

    if heading_match:
        heading_text = clean_storage_text(heading_match.group("body"))

        if duplicates_page_title(heading_text, page_title):
            stats["markdown_artifacts_removed"] += 1
            return heading_match.group("prefix") + body[heading_match.end():]

    paragraph_match = re.match(
        r"(?P<prefix>\s*)<p\b[^>]*>(?P<body>.*?)</p>",
        body,
        flags=re.I | re.S,
    )

    if paragraph_match:
        paragraph_text = clean_storage_text(paragraph_match.group("body"))
        paragraph_text = re.sub(r"^#+\s*", "", paragraph_text).strip()

        if duplicates_page_title(paragraph_text, page_title):
            stats["markdown_artifacts_removed"] += 1
            return paragraph_match.group("prefix") + body[paragraph_match.end():]

    return body


def duplicates_page_title(value, page_title):
    value_key = normalize_key(value)
    title_key = normalize_key(page_title)

    if value_key == title_key:
        return True

    if " - " in page_title:
        title_without_code = normalize_key(page_title.split(" - ", 1)[1])

        if value_key == title_without_code:
            return True

    return False


def remove_metadata_table_rows(body, stats):
    def replace_table(table_match):
        table_html = table_match.group(0)

        def replace_row(row_match):
            row_html = row_match.group(0)
            row_text = clean_storage_text(row_html)

            if is_markdown_table_separator_text(row_text):
                stats["markdown_artifacts_removed"] += 1
                return ""

            if is_metadata_row(row_html):
                stats["metadata_remnants_removed"] += 1
                return ""

            return row_html

        return TABLE_ROW_PATTERN.sub(replace_row, table_html)

    return TABLE_PATTERN.sub(replace_table, body)


def is_metadata_row(row_html):
    cells = [
        clean_storage_text(match.group("body"))
        for match in TABLE_CELL_PATTERN.finditer(row_html)
    ]
    row_text = clean_storage_text(row_html)
    return is_metadata_text(row_text, cells=cells)


def normalize_paragraphs(body, page_title, stats):
    def replace_paragraph(match):
        paragraph_html = match.group(0)
        paragraph_body = re.sub(
            r"^<p\b[^>]*>|</p>$",
            "",
            paragraph_html,
            flags=re.I | re.S,
        )
        paragraph_text = clean_storage_text(paragraph_body, preserve_lines=True)

        if not paragraph_text:
            return paragraph_html

        if is_metadata_paragraph(paragraph_body, paragraph_text):
            stats["metadata_remnants_removed"] += 1
            return ""

        if is_markdown_table_separator_text(paragraph_text):
            stats["markdown_artifacts_removed"] += 1
            return ""

        if contains_internal_confluence_link(paragraph_body):
            return paragraph_html

        rendered = normalize_plain_markdown_paragraph(paragraph_text, page_title, stats)

        if rendered is None:
            return paragraph_html

        return rendered

    return PARAGRAPH_PATTERN.sub(replace_paragraph, body)


def is_metadata_paragraph(paragraph_body, paragraph_text):
    if contains_internal_confluence_link(paragraph_body):
        return False

    return is_metadata_text(paragraph_text)


def is_metadata_text(text, cells=None):
    text = normalize_text(text)

    if not text:
        return False

    lowered = text.casefold()
    lowered = re.sub(r"\s+", " ", lowered).strip()
    short_metadata_shape = len(text) <= 300

    if METADATA_LABEL_PATTERN.search(lowered):
        return has_source_file_signal(lowered)

    if cells:
        first_cell = normalize_key(cells[0]) if cells else ""

        if METADATA_LABEL_PATTERN.search(first_cell) and has_source_file_signal(lowered):
            return True

        if len(cells) <= 4 and has_markdown_source_note(lowered):
            return True

    if short_metadata_shape and has_markdown_source_note(lowered):
        return True

    if short_metadata_shape and has_standalone_markdown_filename(lowered):
        return True

    return False


def has_source_file_signal(lowered):
    return any(
        signal in lowered
        for signal in (
            ".md",
            ".markdown",
            "markdown",
            "kaynak",
            "yerel",
            "local",
            "filename",
            "path",
            "dosya yolu",
            "/",
            "\\",
        )
    )


def has_markdown_source_note(lowered):
    return any(
        phrase in lowered
        for phrase in (
            "markdown dosyası",
            "markdown dosyasi",
            "markdown formatında",
            "markdown formatinda",
            ".md dosyası",
            ".md dosyasi",
            ".markdown dosyası",
            ".markdown dosyasi",
            "markdown'dan",
            "markdown’dan",
        )
    )


def has_standalone_markdown_filename(lowered):
    return bool(
        re.search(r"(^|\s)[^\s<>]+\.m(?:arkdown|d)($|\s)", lowered)
    ) and has_source_file_signal(lowered)


def contains_internal_confluence_link(storage):
    lowered = storage.lower()
    return "<ac:link" in lowered or "<ri:page" in lowered


def normalize_plain_markdown_paragraph(text, page_title, stats):
    stripped = text.strip()

    if not stripped:
        return ""

    heading_match = MARKDOWN_HEADING_PATTERN.match(stripped)

    if heading_match:
        heading_text = heading_match.group(2).strip()

        if duplicates_page_title(heading_text, page_title):
            stats["markdown_artifacts_removed"] += 1
            return ""

        level = min(len(heading_match.group(1)), 6)
        stats["markdown_artifacts_removed"] += 1
        return f"<h{level}>{escape(clean_inline_markdown(heading_text), quote=True)}</h{level}>"

    if has_markdown_fence(stripped):
        return render_markdownish_text(stripped, page_title, stats)

    if text_contains_markdown_block(text):
        return render_markdownish_text(text, page_title, stats)

    return None


def text_contains_markdown_block(text):
    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    if len(lines) < 2:
        return False

    return (
        all(UNORDERED_LIST_PATTERN.match(line) for line in lines)
        or all(ORDERED_LIST_PATTERN.match(line) for line in lines)
        or any(is_markdown_table_line(line) for line in lines)
        or any(MARKDOWN_HEADING_PATTERN.match(line) for line in lines)
    )


def render_markdownish_text(text, page_title, stats):
    lines = strip_markdown_fences(text, stats).splitlines()
    lines = [
        normalize_text(line)
        for line in lines
    ]
    blocks = []
    index = 0

    while index < len(lines):
        line = lines[index].strip()

        if not line:
            index += 1
            continue

        if is_metadata_text(line):
            stats["metadata_remnants_removed"] += 1
            index += 1
            continue

        if is_markdown_table_separator_text(line):
            stats["markdown_artifacts_removed"] += 1
            index += 1
            continue

        heading_match = MARKDOWN_HEADING_PATTERN.match(line)

        if heading_match:
            heading_text = heading_match.group(2).strip()

            if duplicates_page_title(heading_text, page_title):
                stats["markdown_artifacts_removed"] += 1
                index += 1
                continue

            level = min(len(heading_match.group(1)), 6)
            blocks.append(
                f"<h{level}>{escape(clean_inline_markdown(heading_text), quote=True)}</h{level}>"
            )
            stats["markdown_artifacts_removed"] += 1
            index += 1
            continue

        if UNORDERED_LIST_PATTERN.match(line):
            items = []

            while index < len(lines):
                item_match = UNORDERED_LIST_PATTERN.match(lines[index].strip())

                if item_match is None:
                    break

                items.append(clean_inline_markdown(item_match.group(1).strip()))
                stats["markdown_artifacts_removed"] += 1
                index += 1

            blocks.append(build_list("ul", items))
            continue

        if ORDERED_LIST_PATTERN.match(line):
            items = []

            while index < len(lines):
                item_match = ORDERED_LIST_PATTERN.match(lines[index].strip())

                if item_match is None:
                    break

                items.append(clean_inline_markdown(item_match.group(1).strip()))
                stats["markdown_artifacts_removed"] += 1
                index += 1

            blocks.append(build_list("ol", items))
            continue

        if is_markdown_table_line(line):
            table_lines = []

            while index < len(lines) and is_markdown_table_line(lines[index].strip()):
                table_lines.append(lines[index].strip())
                index += 1

            table_html = build_table_from_markdown_lines(table_lines, stats)

            if table_html:
                blocks.append(table_html)

            continue

        paragraph_lines = [line]
        index += 1

        while index < len(lines):
            next_line = lines[index].strip()

            if not next_line:
                break

            if (
                MARKDOWN_HEADING_PATTERN.match(next_line)
                or UNORDERED_LIST_PATTERN.match(next_line)
                or ORDERED_LIST_PATTERN.match(next_line)
                or is_markdown_table_line(next_line)
            ):
                break

            if is_metadata_text(next_line):
                stats["metadata_remnants_removed"] += 1
                index += 1
                continue

            paragraph_lines.append(next_line)
            index += 1

        paragraph = " ".join(paragraph_lines).strip()

        if paragraph:
            blocks.append(f"<p>{escape(clean_inline_markdown(paragraph), quote=True)}</p>")

    return "\n".join(blocks)


def strip_markdown_fences(text, stats):
    cleaned_lines = []

    for line in text.splitlines():
        stripped = line.strip()

        if stripped.startswith("```") or stripped == "`":
            stats["markdown_artifacts_removed"] += 1
            continue

        if len(stripped) > 2 and stripped.startswith("`") and stripped.endswith("`"):
            stats["markdown_artifacts_removed"] += 2
            cleaned_lines.append(stripped[1:-1])
            continue

        cleaned_lines.append(line)

    return "\n".join(cleaned_lines)


def has_markdown_fence(text):
    return any(
        line.strip().startswith("```") or line.strip() == "`"
        for line in text.splitlines()
    )


def clean_inline_markdown(text):
    text = normalize_text(text)
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"__(.*?)__", r"\1", text)
    text = re.sub(r"(?<!\*)\*(?!\*)(.*?)(?<!\*)\*(?!\*)", r"\1", text)
    text = re.sub(r"(?<!_)_(?!_)(.*?)(?<!_)_(?!_)", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    return text


def build_list(tag, items):
    if not items:
        return ""

    return (
        f"<{tag}>"
        + "".join(
            f"<li>{escape(item, quote=True)}</li>"
            for item in items
        )
        + f"</{tag}>"
    )


def is_markdown_table_line(line):
    if "|" not in line:
        return False

    cells = parse_markdown_table_cells(line)
    return len(cells) >= 2


def is_markdown_table_separator_text(text):
    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    if not lines:
        return False

    return all(is_markdown_separator_line(line) for line in lines)


def is_markdown_separator_line(line):
    if "|" not in line:
        return False

    cells = parse_markdown_table_cells(line)

    if not cells:
        return False

    return all(re.fullmatch(r":?-{3,}:?", cell.strip()) for cell in cells)


def parse_markdown_table_cells(line):
    line = line.strip()

    if line.startswith("|"):
        line = line[1:]

    if line.endswith("|"):
        line = line[:-1]

    return [
        cell.strip()
        for cell in line.split("|")
    ]


def build_table_from_markdown_lines(lines, stats):
    rows = []
    has_separator = False

    for line in lines:
        if is_markdown_separator_line(line):
            stats["markdown_artifacts_removed"] += 1
            has_separator = True
            continue

        cells = parse_markdown_table_cells(line)

        if cells:
            rows.append(cells)

    if not rows:
        return ""

    max_columns = max(len(row) for row in rows)
    normalized_rows = [
        row + [""] * (max_columns - len(row))
        for row in rows
    ]

    table_lines = ["<table>"]

    if has_separator:
        header = normalized_rows[0]
        data_rows = normalized_rows[1:]
        table_lines.extend(
            [
                "<thead>",
                "<tr>",
                *[
                    f"<th>{escape(clean_inline_markdown(cell), quote=True)}</th>"
                    for cell in header
                ],
                "</tr>",
                "</thead>",
                "<tbody>",
            ]
        )
    else:
        data_rows = normalized_rows
        table_lines.append("<tbody>")

    for row in data_rows:
        table_lines.extend(
            [
                "<tr>",
                *[
                    f"<td>{escape(clean_inline_markdown(cell), quote=True)}</td>"
                    for cell in row
                ],
                "</tr>",
            ]
        )

    table_lines.extend(["</tbody>", "</table>"])
    return "\n".join(table_lines)


def remove_empty_paragraph_runs(body):
    return re.sub(
        r"(?:<p>\s*(?:&nbsp;|\s|<br\s*/?>)*</p>\s*){3,}",
        "<p>&nbsp;</p>\n<p>&nbsp;</p>\n",
        body,
        flags=re.I,
    )


def write_outputs(page, original_body, normalized_body, stats, dry_run):
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    BEFORE_STORAGE_PATH.write_text(original_body, encoding="utf-8")
    AFTER_STORAGE_PATH.write_text(normalized_body, encoding="utf-8")
    REPORT_PATH.write_text(
        build_report(page, original_body, normalized_body, stats, dry_run),
        encoding="utf-8",
    )


def build_report(page, original_body, normalized_body, stats, dry_run):
    lines = [
        "# SRÇ.001 Process Page Normalization Report",
        "",
        "## Summary",
        "",
        f"- Mode: {'dry-run' if dry_run else 'normal'}",
        f"- Page title: {page['title']}",
        f"- Page ID: {page['id']}",
        f"- Original body length: {len(original_body)}",
        f"- Normalized body length: {len(normalized_body)}",
        f"- Code/pre blocks converted: {stats['code_pre_blocks_converted']}",
        f"- Markdown artifacts removed: {stats['markdown_artifacts_removed']}",
        f"- Metadata remnants removed: {stats['metadata_remnants_removed']}",
        "",
        "## Preview Files",
        "",
        f"- Before: reports/{BEFORE_STORAGE_PATH.name}",
        f"- After: reports/{AFTER_STORAGE_PATH.name}",
        "",
        "## Scope",
        "",
        f"- Target page only: {TARGET_TITLE}",
        "- Child pages were not updated by this script.",
    ]

    return "\n".join(lines) + "\n"


def print_dry_run_summary(page, original_body, normalized_body, stats):
    print(f"Page title: {page['title']}")
    print(f"Original body length: {len(original_body)}")
    print(f"Normalized body length: {len(normalized_body)}")
    print(f"Code/pre blocks converted: {stats['code_pre_blocks_converted']}")
    print(f"Markdown artifacts removed: {stats['markdown_artifacts_removed']}")
    print(f"Metadata remnants removed: {stats['metadata_remnants_removed']}")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Write preview files and summary without updating Confluence.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    manifest = load_manifest()
    client = ConfluenceClient()
    space_key = manifest["confluence"]["space"]
    root_page_id = str(manifest["confluence"]["root"]["page_id"])
    pages_by_id = crawl_page_tree(client, root_page_id)
    page = find_target_page(pages_by_id)
    original_body = page["body"]
    normalized_body, stats = normalize_body(original_body, page["title"])

    write_outputs(page, original_body, normalized_body, stats, args.dry_run)

    if args.dry_run:
        print_dry_run_summary(page, original_body, normalized_body, stats)
        return

    print(f"[NORMALIZE] {TARGET_TITLE}")

    if normalized_body != original_body:
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
