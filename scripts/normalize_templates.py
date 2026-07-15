import argparse
from html import escape, unescape
from pathlib import Path
import re
import unicodedata

import yaml

from confluence_client import ConfluenceClient


ROOT = Path(__file__).resolve().parent.parent
REPORT_DIR = ROOT / "reports"
PREVIEW_DIR = REPORT_DIR / "templates"
REPORT_PATH = REPORT_DIR / "templates_normalization_report.md"
PREVIEW_INDEX_PATH = REPORT_DIR / "templates_normalization_preview_index.md"

ROOT_02_CODE = "ROOT-02"
TEMPLATE_TITLE_PREFIX = "ŞBL."

TEMPLATE_SECTION_HINTS = [
    "Doküman Bilgileri",
    "Amaç",
    "Kapsam",
    "Girdi",
    "Girdiler",
    "Çıktı",
    "Çıktılar",
    "Roller",
    "Sorumluluklar",
    "Faaliyet",
    "İş Ürünü",
    "Ölçüm",
    "Hazırlayan",
    "Gözden Geçiren",
    "Onaylayan",
    "Tarih",
    "Sürüm",
    "Durum",
]

CODE_MACRO_PATTERN = re.compile(
    r"<ac:structured-macro\b(?=[^>]*\bac:name\s*=\s*['\"]code['\"])[^>]*>.*?</ac:structured-macro>",
    flags=re.I | re.S,
)
PRE_PATTERN = re.compile(r"<pre\b[^>]*>.*?</pre>", flags=re.I | re.S)
TABLE_PATTERN = re.compile(r"<table\b.*?</table>", flags=re.I | re.S)
TABLE_ROW_PATTERN = re.compile(r"<tr\b.*?</tr>", flags=re.I | re.S)
TABLE_CELL_PATTERN = re.compile(
    r"<(?P<tag>td|th)\b[^>]*>(?P<body>.*?)</(?P=tag)>",
    flags=re.I | re.S,
)
PARAGRAPH_PATTERN = re.compile(r"<p\b[^>]*>.*?</p>", flags=re.I | re.S)
STYLE_TAG_PATTERN = re.compile(
    r"<(?P<tag>[A-Za-z][\w:-]*)(?P<before>[^>]*?)\sstyle\s*=\s*(?P<quote>[\"'])(?P<style>.*?)(?P=quote)(?P<after>[^>]*)>",
    flags=re.I | re.S,
)
CDATA_PATTERN = re.compile(r"<!\[CDATA\[(.*?)\]\]>", flags=re.S)

MARKDOWN_HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.+)$")
UNORDERED_LIST_PATTERN = re.compile(r"^\s*[-*]\s+(.+)$")
ORDERED_LIST_PATTERN = re.compile(r"^\s*\d+[\.)]\s+(.+)$")
METADATA_LABEL_PATTERN = re.compile(
    r"^(dosya adı|kaynak dosya|kaynak dosyası|yerel dosya|dosya yolu|source file|filename|path)\s*[:：-]",
    flags=re.I,
)

STYLE_PROPERTIES_TO_REMOVE = {
    "font-family",
    "font-size",
    "color",
}


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


def normalize_content(value):
    return unicodedata.normalize("NFC", str(value)).replace("\r\n", "\n").replace("\r", "\n")


def clean_storage_text(storage, preserve_lines=False):
    cdata_parts = CDATA_PATTERN.findall(storage)

    if cdata_parts:
        text = "\n".join(cdata_parts)
    else:
        storage = re.sub(r"<br\s*/?>", "\n", storage, flags=re.I)
        storage = re.sub(r"<[^>]+>", " " if not preserve_lines else "", storage)
        text = storage

    text = unescape(text).replace("\xa0", " ")

    if preserve_lines:
        lines = [
            re.sub(r"[ \t]+", " ", line).strip()
            for line in normalize_content(text).splitlines()
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


def find_manifest_node(manifest, code):
    for node in manifest["nodes"]:
        if node["code"] == code:
            return node

    raise ValueError(f"Node does not exist in manifest: {code}")


def find_root_child_page(manifest, pages_by_id, root_page_id, code):
    node = find_manifest_node(manifest, code)
    root_page = pages_by_id[str(root_page_id)]

    for child_id in root_page["children"]:
        child = pages_by_id.get(child_id)

        if child is not None and child["title"] == normalize_text(node["title"]):
            return child

    raise ValueError(f"{code} page does not exist under configured root page")


def collect_descendants(pages_by_id, page_id):
    descendants = []

    def collect(current_id):
        current = pages_by_id[current_id]

        for child_id in current["children"]:
            child = pages_by_id.get(child_id)

            if child is None:
                continue

            descendants.append(child)
            collect(child_id)

    collect(str(page_id))
    return descendants


def select_template_pages(root_02_page, pages_by_id):
    descendants = collect_descendants(pages_by_id, root_02_page["id"])

    return [
        page
        for page in descendants
        if normalize_text(page["title"]).startswith(TEMPLATE_TITLE_PREFIX)
    ]


def empty_stats():
    return {
        "code_pre_blocks_converted": 0,
        "markdown_artifacts_removed": 0,
        "metadata_remnants_removed": 0,
        "inline_styles_removed": 0,
    }


def normalize_body(body, page_title):
    stats = empty_stats()
    warnings = []
    normalized = body
    normalized = convert_accidental_code_blocks(normalized, page_title, stats, warnings)
    normalized = remove_duplicate_initial_title_heading(normalized, page_title, stats)
    normalized = remove_metadata_table_rows(normalized, stats, warnings)
    normalized = normalize_paragraphs(normalized, page_title, stats, warnings)
    normalized = remove_safe_inline_styles(normalized, stats, warnings)
    normalized = remove_empty_paragraph_runs(normalized)
    return normalized.strip(), stats, warnings


def convert_accidental_code_blocks(body, page_title, stats, warnings):
    for pattern in (CODE_MACRO_PATTERN, PRE_PATTERN):
        body = pattern.sub(
            lambda match: convert_code_block(match.group(0), page_title, stats, warnings),
            body,
        )

    return body


def convert_code_block(block_html, page_title, stats, warnings):
    if contains_internal_confluence_link(block_html):
        warnings.append("Skipped code/pre block containing Confluence internal link.")
        return block_html

    text = clean_storage_text(block_html, preserve_lines=True)

    if not text:
        return block_html

    if should_keep_code_block(block_html, text):
        return block_html

    rendered = render_markdownish_text(text, page_title, stats, warnings)

    if not rendered:
        return ""

    stats["code_pre_blocks_converted"] += 1
    return rendered


def should_keep_code_block(block_html, text):
    lower_block = block_html.lower()
    single_line = "\n" not in text.strip()

    if lower_block.startswith("<code") and single_line and not looks_like_markdown_template_text(text):
        return True

    return looks_like_true_code(text)


def looks_like_markdown_template_text(text):
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

    if any(contains_template_placeholder(line) for line in lines):
        return True

    normalized = normalize_key(text)
    return any(
        normalize_key(section) in normalized
        for section in TEMPLATE_SECTION_HINTS
    )


def looks_like_true_code(text):
    if looks_like_markdown_template_text(text):
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


def contains_template_placeholder(text):
    return bool(re.search(r"<[^>\n]{2,80}>", text))


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


def remove_metadata_table_rows(body, stats, warnings):
    def replace_table(table_match):
        table_html = table_match.group(0)

        def replace_row(row_match):
            row_html = row_match.group(0)
            row_text = clean_storage_text(row_html)

            if is_markdown_table_separator_text(row_text):
                stats["markdown_artifacts_removed"] += 1
                return ""

            decision = metadata_decision(row_text, row_html)

            if decision["remove"]:
                stats["metadata_remnants_removed"] += 1
                return ""

            if decision["warning"]:
                warnings.append(decision["warning"])

            return row_html

        return TABLE_ROW_PATTERN.sub(replace_row, table_html)

    return TABLE_PATTERN.sub(replace_table, body)


def normalize_paragraphs(body, page_title, stats, warnings):
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

        decision = metadata_decision(paragraph_text, paragraph_body)

        if decision["remove"]:
            stats["metadata_remnants_removed"] += 1
            return ""

        if decision["warning"]:
            warnings.append(decision["warning"])

        if is_markdown_table_separator_text(paragraph_text):
            stats["markdown_artifacts_removed"] += 1
            return ""

        if contains_internal_confluence_link(paragraph_body):
            return paragraph_html

        rendered = normalize_plain_markdown_paragraph(paragraph_text, page_title, stats, warnings)

        if rendered is None:
            return paragraph_html

        return rendered

    return PARAGRAPH_PATTERN.sub(replace_paragraph, body)


def metadata_decision(text, html_context):
    text = normalize_text(text)

    if not text:
        return {
            "remove": False,
            "warning": "",
        }

    lowered = re.sub(r"\s+", " ", text.casefold()).strip()
    short_metadata_shape = len(text) <= 350

    if contains_internal_confluence_link(html_context):
        return {
            "remove": False,
            "warning": "",
        }

    if has_metadata_label(lowered) and has_source_metadata_signal(lowered):
        return {
            "remove": True,
            "warning": "",
        }

    if short_metadata_shape and has_markdown_migration_note(lowered):
        return {
            "remove": True,
            "warning": "",
        }

    if short_metadata_shape and has_standalone_source_filename(lowered):
        return {
            "remove": True,
            "warning": "",
        }

    if short_metadata_shape and has_source_drive_note(lowered):
        return {
            "remove": True,
            "warning": "",
        }

    if has_possible_metadata_term(lowered):
        return {
            "remove": False,
            "warning": f"Skipped possible metadata candidate: {text[:180]}",
        }

    return {
        "remove": False,
        "warning": "",
    }


def has_metadata_label(lowered):
    return METADATA_LABEL_PATTERN.search(lowered) is not None


def has_source_metadata_signal(lowered):
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
            "drive.google.com",
            "docs.google.com",
        )
    ) or looks_like_local_path(lowered)


def looks_like_local_path(lowered):
    return bool(
        re.search(
            r"(file://|/users/|/volumes/|çalışma alanı|calisma alani|iuc-spice|[a-z]:\\|"
            r"\.\.?/|\\[^\\]+\\)",
            lowered,
        )
    )


def has_markdown_migration_note(lowered):
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
            "markdown olarak",
        )
    ) and any(
        signal in lowered
        for signal in (
            "aktar",
            "içe",
            "ice",
            "oluşturul",
            "olusturul",
            "kaynak",
            "dosya",
            ".md",
            ".markdown",
        )
    )


def has_standalone_source_filename(lowered):
    return bool(
        re.search(r"(^|\s)[^\s<>]+\.m(?:arkdown|d)($|\s)", lowered)
    ) and any(
        signal in lowered
        for signal in (
            ".md",
            ".markdown",
            "dosya adı",
            "kaynak",
            "filename",
            "path",
            "/",
            "\\",
        )
    )


def has_source_drive_note(lowered):
    if "drive.google.com" not in lowered and "docs.google.com" not in lowered:
        return False

    return any(
        signal in lowered
        for signal in (
            "kaynak",
            "eski",
            "yerel",
            "dosya",
            "markdown",
            "aktar",
            "içe",
            "ice",
        )
    )


def has_possible_metadata_term(lowered):
    return any(
        term in lowered
        for term in (
            "dosya adı",
            "kaynak dosya",
            ".md",
            ".markdown",
            "markdown",
            "yerel dosya",
            "dosya yolu",
            "filename",
            "path",
        )
    )


def contains_internal_confluence_link(storage):
    lowered = storage.lower()
    return "<ac:link" in lowered or "<ri:page" in lowered


def normalize_plain_markdown_paragraph(text, page_title, stats, warnings):
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
        return render_markdownish_text(stripped, page_title, stats, warnings)

    if text_contains_markdown_block(text):
        return render_markdownish_text(text, page_title, stats, warnings)

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


def render_markdownish_text(text, page_title, stats, warnings):
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

        decision = metadata_decision(line, line)

        if decision["remove"]:
            stats["metadata_remnants_removed"] += 1
            index += 1
            continue

        if decision["warning"]:
            warnings.append(decision["warning"])

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

            decision = metadata_decision(next_line, next_line)

            if decision["remove"]:
                stats["metadata_remnants_removed"] += 1
                index += 1
                continue

            if decision["warning"]:
                warnings.append(decision["warning"])

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


def remove_safe_inline_styles(body, stats, warnings):
    def replace(match):
        tag = match.group("tag")

        if tag.lower().startswith(("ac:", "ri:")):
            return match.group(0)

        style = unescape(match.group("style"))
        kept_properties = []
        removed_count = 0

        for property_text in style.split(";"):
            property_text = property_text.strip()

            if not property_text:
                continue

            if ":" not in property_text:
                kept_properties.append(property_text)
                continue

            name, value = property_text.split(":", 1)
            property_name = name.strip().casefold()

            if property_name in STYLE_PROPERTIES_TO_REMOVE:
                removed_count += 1
                continue

            kept_properties.append(f"{name.strip()}: {value.strip()}")

        if removed_count == 0:
            return match.group(0)

        stats["inline_styles_removed"] += removed_count
        kept_style = "; ".join(kept_properties)
        before = match.group("before")
        after = match.group("after")

        if kept_style:
            return f'<{tag}{before} style="{escape(kept_style, quote=True)}"{after}>'

        return f"<{tag}{before}{after}>"

    return STYLE_TAG_PATTERN.sub(replace, body)


def remove_empty_paragraph_runs(body):
    return re.sub(
        r"(?:<p>\s*(?:&nbsp;|\s|<br\s*/?>)*</p>\s*){3,}",
        "<p>&nbsp;</p>\n<p>&nbsp;</p>\n",
        body,
        flags=re.I,
    )


def safe_page_file_id(page):
    safe_id = re.sub(r"[^0-9A-Za-z_-]+", "_", str(page["id"]))
    return safe_id.strip("_") or "page"


def write_preview_files(page, original_body, normalized_body):
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    safe_id = safe_page_file_id(page)
    before_path = PREVIEW_DIR / f"{safe_id}_before_storage.xhtml"
    after_path = PREVIEW_DIR / f"{safe_id}_after_storage.xhtml"
    before_path.write_text(original_body, encoding="utf-8")
    after_path.write_text(normalized_body, encoding="utf-8")
    return before_path, after_path


def build_page_report(page, normalized_body, stats, warnings, before_path=None, after_path=None):
    return {
        "id": page["id"],
        "title": page["title"],
        "original_body_length": len(page["body"]),
        "normalized_body_length": len(normalized_body),
        "code_pre_blocks_converted": stats["code_pre_blocks_converted"],
        "markdown_artifacts_removed": stats["markdown_artifacts_removed"],
        "metadata_remnants_removed": stats["metadata_remnants_removed"],
        "inline_styles_removed": stats["inline_styles_removed"],
        "warnings": warnings,
        "before_path": relative_report_path(before_path) if before_path else "",
        "after_path": relative_report_path(after_path) if after_path else "",
    }


def relative_report_path(path):
    return str(path.relative_to(ROOT)) if path is not None else ""


def aggregate_summary(page_reports, changed_reports):
    return {
        "pages_scanned": len(page_reports),
        "pages_changed": len(changed_reports),
        "total_code_pre_blocks_converted": sum(
            report["code_pre_blocks_converted"]
            for report in page_reports
        ),
        "total_markdown_artifacts_removed": sum(
            report["markdown_artifacts_removed"]
            for report in page_reports
        ),
        "total_metadata_remnants_removed": sum(
            report["metadata_remnants_removed"]
            for report in page_reports
        ),
        "total_inline_styles_removed": sum(
            report["inline_styles_removed"]
            for report in page_reports
        ),
    }


def write_reports(page_reports, changed_reports, skipped_reports, dry_run):
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    summary = aggregate_summary(page_reports, changed_reports)
    REPORT_PATH.write_text(
        build_report(summary, changed_reports, skipped_reports, page_reports, dry_run),
        encoding="utf-8",
    )
    PREVIEW_INDEX_PATH.write_text(
        build_preview_index(changed_reports),
        encoding="utf-8",
    )


def build_report(summary, changed_reports, skipped_reports, page_reports, dry_run):
    lines = [
        "# Templates Normalization Report",
        "",
        "## Summary",
        "",
        f"- Mode: {'dry-run' if dry_run else 'normal'}",
        f"- Pages scanned: {summary['pages_scanned']}",
        f"- Pages that would be updated: {summary['pages_changed']}" if dry_run else f"- Pages updated: {summary['pages_changed']}",
        f"- Total code/pre blocks converted: {summary['total_code_pre_blocks_converted']}",
        f"- Total markdown artifacts removed: {summary['total_markdown_artifacts_removed']}",
        f"- Total metadata remnants removed: {summary['total_metadata_remnants_removed']}",
        f"- Total inline styles removed: {summary['total_inline_styles_removed']}",
        "",
        "## Pages changed",
        "",
    ]

    if changed_reports:
        for report in changed_reports:
            lines.extend(page_report_lines(report))
    else:
        lines.append("No pages changed.")

    lines.extend(
        [
            "",
            "## Pages skipped",
            "",
        ]
    )

    if skipped_reports:
        for report in skipped_reports:
            lines.append(f"- {markdown_text(report['title'])} (`{report['id']}`): no safe changes")
    else:
        lines.append("No pages skipped.")

    lines.extend(
        [
            "",
            "## Per-page counts",
            "",
        ]
    )

    if page_reports:
        for report in page_reports:
            lines.extend(page_count_lines(report))
    else:
        lines.append("No template pages found.")

    lines.extend(
        [
            "",
            "## Warnings / skipped risky candidates",
            "",
        ]
    )

    warnings_written = False

    for report in page_reports:
        for warning in report["warnings"]:
            lines.append(f"- {markdown_text(report['title'])}: {markdown_text(warning)}")
            warnings_written = True

    if not warnings_written:
        lines.append("No risky candidates reported.")

    return "\n".join(lines) + "\n"


def page_report_lines(report):
    lines = [
        f"### {markdown_text(report['title'])}",
        "",
        f"- Page ID: `{report['id']}`",
        f"- Original body length: {report['original_body_length']}",
        f"- Normalized body length: {report['normalized_body_length']}",
        f"- Code/pre blocks converted: {report['code_pre_blocks_converted']}",
        f"- Markdown artifacts removed: {report['markdown_artifacts_removed']}",
        f"- Metadata remnants removed: {report['metadata_remnants_removed']}",
        f"- Inline styles removed: {report['inline_styles_removed']}",
    ]

    if report["before_path"]:
        lines.append(f"- Before preview: `{report['before_path']}`")

    if report["after_path"]:
        lines.append(f"- After preview: `{report['after_path']}`")

    lines.append("")
    return lines


def page_count_lines(report):
    return [
        f"### {markdown_text(report['title'])}",
        "",
        f"- Original body length: {report['original_body_length']}",
        f"- Normalized body length: {report['normalized_body_length']}",
        f"- Code/pre blocks converted: {report['code_pre_blocks_converted']}",
        f"- Markdown artifacts removed: {report['markdown_artifacts_removed']}",
        f"- Metadata remnants removed: {report['metadata_remnants_removed']}",
        f"- Inline styles removed: {report['inline_styles_removed']}",
        "",
    ]


def build_preview_index(changed_reports):
    lines = [
        "# Templates Normalization Preview Index",
        "",
    ]

    if not changed_reports:
        lines.append("No changed pages.")
        return "\n".join(lines) + "\n"

    for report in changed_reports:
        lines.extend(
            [
                f"## {markdown_text(report['title'])}",
                "",
                f"- Page ID: `{report['id']}`",
                f"- Before: `{report['before_path']}`",
                f"- After: `{report['after_path']}`",
                "",
            ]
        )

    return "\n".join(lines) + "\n"


def markdown_text(value):
    return normalize_text(value).replace("\n", " ")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Write reports and previews without updating Confluence.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    manifest = load_manifest()
    client = ConfluenceClient()
    space_key = manifest["confluence"]["space"]
    root_page_id = str(manifest["confluence"]["root"]["page_id"])
    pages_by_id = crawl_page_tree(client, root_page_id)
    root_02_page = find_root_child_page(
        manifest,
        pages_by_id,
        root_page_id,
        ROOT_02_CODE,
    )
    template_pages = select_template_pages(root_02_page, pages_by_id)
    page_reports = []
    changed_reports = []
    skipped_reports = []
    normalized_pages = []

    for page in template_pages:
        normalized_body, stats, warnings = normalize_body(page["body"], page["title"])
        changed = normalized_body != page["body"]
        before_path = None
        after_path = None

        if changed:
            before_path, after_path = write_preview_files(
                page,
                page["body"],
                normalized_body,
            )

        page_report = build_page_report(
            page,
            normalized_body,
            stats,
            warnings,
            before_path,
            after_path,
        )
        page_reports.append(page_report)

        if changed:
            changed_reports.append(page_report)
            normalized_pages.append(
                {
                    "page": page,
                    "body": normalized_body,
                }
            )

            if args.dry_run:
                print(f"[DRY-RUN NORMALIZE] {page['title']}")
        else:
            skipped_reports.append(page_report)

    write_reports(
        page_reports,
        changed_reports,
        skipped_reports,
        args.dry_run,
    )

    if args.dry_run:
        print(f"Pages scanned: {len(page_reports)}")
        print(f"Pages that would be updated: {len(changed_reports)}")
        print(
            "Total code/pre blocks converted: "
            f"{sum(report['code_pre_blocks_converted'] for report in page_reports)}"
        )
        print(
            "Total markdown artifacts removed: "
            f"{sum(report['markdown_artifacts_removed'] for report in page_reports)}"
        )
        print(
            "Total metadata remnants removed: "
            f"{sum(report['metadata_remnants_removed'] for report in page_reports)}"
        )
        print(
            "Total inline styles removed: "
            f"{sum(report['inline_styles_removed'] for report in page_reports)}"
        )
        return

    for normalized_page in normalized_pages:
        page = normalized_page["page"]
        print(f"[NORMALIZE] {page['title']}")
        client.update_page(
            page["id"],
            space_key,
            page["title"],
            normalized_page["body"],
            page["version_number"] + 1,
        )

    print(f"[DONE] Normalized {len(normalized_pages)} template pages")


if __name__ == "__main__":
    main()
