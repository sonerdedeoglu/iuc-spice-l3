import argparse
from html import escape, unescape
from pathlib import Path
import re
import unicodedata

import yaml

from confluence_client import ConfluenceClient


ROOT = Path(__file__).resolve().parent.parent
REPORT_DIR = ROOT / "reports" / "placeholders"
REPORT_PATH = REPORT_DIR / "templates_placeholder_style_report.md"

ROOT_02_CODE = "ROOT-02"
TEMPLATE_TITLE_PREFIX = "İÜC.BİDB.ŞBL."

PROTECTED_PATTERN = re.compile(
    r"(<ac:link\b.*?</ac:link>|"
    r"<ac:structured-macro\b.*?</ac:structured-macro>|"
    r"<pre\b.*?</pre>|"
    r"<ri:page\b[^>]*/?>|"
    r"```.*?```)",
    flags=re.I | re.S,
)
CODE_TAG_PATTERN = re.compile(
    r"<code\b(?P<attrs>[^>]*)>(?P<body>.*?)</code>",
    flags=re.I | re.S,
)
RAW_TAG_PATTERN = re.compile(r"<[^<>]*>", flags=re.S)
PARAGRAPH_PATTERN = re.compile(
    r"<p\b(?P<attrs>[^>]*)>(?P<body>.*?)</p>",
    flags=re.I | re.S,
)
PLACEHOLDER_PATTERN = re.compile(
    r"(?P<double_escaped>&amp;lt;(?P<double_escaped_text>(?:(?!&amp;lt;|&amp;gt;).){1,500})&amp;gt;)|"
    r"(?P<escaped>&lt;(?P<escaped_text>(?:(?!&lt;|&gt;).){1,500})&gt;)",
    flags=re.S,
)

HTML_TAG_NAMES = {
    "a",
    "abbr",
    "ac:link",
    "ac:parameter",
    "ac:plain-text-link-body",
    "ac:rich-text-body",
    "ac:structured-macro",
    "b",
    "blockquote",
    "body",
    "br",
    "caption",
    "code",
    "col",
    "colgroup",
    "div",
    "em",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "head",
    "hr",
    "html",
    "i",
    "img",
    "li",
    "ol",
    "p",
    "pre",
    "ri:page",
    "span",
    "strong",
    "table",
    "tbody",
    "td",
    "tfoot",
    "th",
    "thead",
    "tr",
    "u",
    "ul",
}

INSTRUCTION_WORDS = [
    "açıklayınız",
    "aciklayiniz",
    "belirtiniz",
    "doldurunuz",
    "ekleyiniz",
    "giriniz",
    "seçiniz",
    "seciniz",
    "tanımlayınız",
    "tanimlayiniz",
    "yazınız",
    "yaziniz",
    "buraya",
    "örnek",
    "ornek",
    "kullanım",
    "kullanim",
    "not",
]


def load_manifest():
    with open(ROOT / "manifest.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def normalize_text(value):
    return unicodedata.normalize("NFC", str(value)).strip()


def normalize_key(value):
    value = normalize_text(value).casefold()
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def find_manifest_node(manifest, code):
    for node in manifest["nodes"]:
        if node["code"] == code:
            return node

    raise ValueError(f"Node does not exist in manifest: {code}")


def get_page_record(client, page_id, parent_id=None, depth=0):
    page = client.get_page(page_id)
    body = page.get("body", {}).get("storage", {}).get("value", "")

    return {
        "id": str(page["id"]),
        "title": normalize_text(page["title"]),
        "body": body,
        "version_number": page["version"]["number"],
        "parent_id": str(parent_id) if parent_id is not None else None,
        "depth": depth,
        "children": [],
    }


def find_root_child_page(client, manifest, root_page_id, code):
    node = find_manifest_node(manifest, code)
    expected_title = normalize_text(node["title"])
    children = client.get_children(root_page_id).get("results", [])

    for child in children:
        if normalize_text(child["title"]) == expected_title:
            return get_page_record(
                client,
                child["id"],
                root_page_id,
                1,
            )

    raise ValueError(f"{code} page does not exist under configured root page")


def crawl_subtree(client, root_page):
    pages_by_id = {}

    def crawl(page_id, parent_id=None, depth=0):
        page = get_page_record(
            client,
            page_id,
            parent_id,
            depth,
        )
        pages_by_id[page["id"]] = page
        children = client.get_children(page["id"]).get("results", [])

        for child in children:
            child_id = str(child["id"])
            page["children"].append(child_id)

        for child_id in page["children"]:
            if child_id not in pages_by_id:
                crawl(child_id, page["id"], depth + 1)

    crawl(root_page["id"], root_page["parent_id"], root_page["depth"])
    return pages_by_id


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


def style_placeholders(body):
    report = {
        "placeholder_count": 0,
        "escaped_count": 0,
        "inline_code_count": 0,
        "short_count": 0,
        "long_count": 0,
        "short_placeholders": [],
        "long_placeholders": [],
        "skipped_tag_like": [],
        "skipped": [],
    }
    parts = []
    position = 0

    for match in PROTECTED_PATTERN.finditer(body):
        parts.append(
            style_unprotected_segment(
                body[position:match.start()],
                report,
            )
        )
        parts.append(match.group(0))
        position = match.end()

    parts.append(
        style_unprotected_segment(
            body[position:],
            report,
        )
    )

    return "".join(parts), report


def style_unprotected_segment(segment, report):
    return style_paragraph_segment(segment, report)


def style_inline_code_placeholder(match, report, allow_long):
    original = match.group(0)
    code_body = match.group("body")
    exact_placeholder = extract_exact_placeholder_from_body(code_body)

    if exact_placeholder is None:
        return original

    report["inline_code_count"] += 1
    replacement = build_placeholder_replacement(
        exact_placeholder,
        original,
        report,
        allow_long=allow_long,
    )

    if replacement is None:
        return original

    return replacement


def style_paragraph_segment(segment, report):
    parts = []
    position = 0

    for match in PARAGRAPH_PATTERN.finditer(segment):
        parts.append(
            replace_visible_placeholders(
                segment[position:match.start()],
                report,
                allow_long=True,
            )
        )
        parts.append(
            style_paragraph(
                match,
                report,
            )
        )
        position = match.end()

    parts.append(
        replace_visible_placeholders(
            segment[position:],
            report,
            allow_long=True,
        )
    )

    return "".join(parts)


def style_paragraph(match, report):
    paragraph_html = match.group(0)
    paragraph_attrs = match.group("attrs")
    paragraph_body = match.group("body")
    exact_placeholder = extract_exact_placeholder_from_body(paragraph_body)
    inline_code_placeholder = False

    if exact_placeholder is None:
        exact_placeholder = extract_exact_code_placeholder_from_body(paragraph_body)
        inline_code_placeholder = exact_placeholder is not None

    if exact_placeholder is not None:
        if inline_code_placeholder:
            report["inline_code_count"] += 1

        replacement = build_placeholder_replacement(
            exact_placeholder,
            paragraph_html,
            report,
            allow_long=True,
        )

        if replacement is None:
            return paragraph_html

        if replacement.startswith('<ac:structured-macro ac:name="info"'):
            return replacement

        return f"<p{paragraph_attrs}>{replacement}</p>"

    return replace_visible_placeholders(
        paragraph_html,
        report,
        allow_long=False,
    )


def extract_exact_placeholder_from_body(body):
    stripped = normalize_text(body)
    match = PLACEHOLDER_PATTERN.fullmatch(stripped)

    if match is None:
        return None

    placeholder = match.group("escaped_text")

    if placeholder is None:
        placeholder = match.group("double_escaped_text")

    placeholder = unescape(placeholder)

    if "<" in placeholder or ">" in placeholder:
        return None

    return placeholder


def extract_exact_code_placeholder_from_body(body):
    match = CODE_TAG_PATTERN.fullmatch(normalize_text(body))

    if match is None:
        return None

    return extract_exact_placeholder_from_body(match.group("body"))


def replace_visible_placeholders(segment, report, allow_long):
    parts = []
    position = 0

    for match in CODE_TAG_PATTERN.finditer(segment):
        parts.append(
            replace_visible_placeholder_text_nodes(
                segment[position:match.start()],
                report,
                allow_long,
            )
        )
        parts.append(style_inline_code_placeholder(match, report, allow_long))
        position = match.end()

    parts.append(
        replace_visible_placeholder_text_nodes(
            segment[position:],
            report,
            allow_long,
        )
    )

    return "".join(parts)


def replace_visible_placeholder_text_nodes(segment, report, allow_long):
    parts = []
    position = 0

    for match in RAW_TAG_PATTERN.finditer(segment):
        parts.append(
            replace_placeholder_text(
                segment[position:match.start()],
                report,
                allow_long,
            )
        )
        parts.append(match.group(0))
        position = match.end()

    parts.append(
        replace_placeholder_text(
            segment[position:],
            report,
            allow_long,
        )
    )

    return "".join(parts)


def replace_placeholder_text(text, report, allow_long):
    def replace(match):
        raw_text = match.group("escaped_text")

        if raw_text is None:
            raw_text = match.group("double_escaped_text")

        replacement = build_placeholder_replacement(
            unescape(raw_text),
            match.group(0),
            report,
            allow_long=allow_long,
        )

        if replacement is None:
            return match.group(0)

        return replacement

    return PLACEHOLDER_PATTERN.sub(replace, text)


def build_placeholder_replacement(raw_placeholder, original_text, report, allow_long):
    placeholder = normalize_placeholder_text(raw_placeholder)

    if not placeholder:
        return None

    report["escaped_count"] += 1
    classification = classify_placeholder(placeholder, original_text)

    if classification["kind"] == "skip_tag_like":
        report["skipped_tag_like"].append(
            {
                "placeholder": placeholder,
                "reason": classification["reason"],
            }
        )
        return None

    if classification["kind"] == "skip":
        if classification["reason"]:
            report["skipped"].append(
                {
                    "placeholder": placeholder,
                    "reason": classification["reason"],
                }
            )

        return None

    if classification["kind"] == "short":
        report["placeholder_count"] += 1
        report["short_count"] += 1
        report["short_placeholders"].append(placeholder)
        return build_status_macro(placeholder)

    if not allow_long:
        report["skipped"].append(
            {
                "placeholder": placeholder,
                "reason": "long placeholder inside mixed paragraph",
            }
        )
        return None

    report["placeholder_count"] += 1
    report["long_count"] += 1
    report["long_placeholders"].append(placeholder)
    return build_info_macro(placeholder)


def normalize_placeholder_text(value):
    value = unescape(str(value)).replace("\xa0", " ")
    value = re.sub(r"\s+", " ", value)
    return normalize_text(value)


def classify_placeholder(placeholder, original_text):
    if is_tag_like_candidate(placeholder):
        return {
            "kind": "skip_tag_like",
            "reason": "XHTML/HTML tag-like candidate",
        }

    if is_real_markup(placeholder):
        return {
            "kind": "skip",
            "reason": "",
        }

    if not has_letter(placeholder):
        return {
            "kind": "skip",
            "reason": "",
        }

    if "<" in placeholder or ">" in placeholder:
        return {
            "kind": "skip",
            "reason": "nested angle brackets",
        }

    if looks_like_path_or_url(placeholder):
        return {
            "kind": "skip",
            "reason": "path or URL-like value",
        }

    words = placeholder_words(placeholder)
    instruction = looks_like_instruction(placeholder, words)

    if len(placeholder) <= 60 and 1 <= len(words) <= 6 and not instruction:
        return {
            "kind": "short",
            "reason": "",
        }

    if len(placeholder) > 60 or instruction:
        return {
            "kind": "long",
            "reason": "",
        }

    return {
        "kind": "skip",
        "reason": "ambiguous placeholder length",
    }


def is_tag_like_candidate(placeholder):
    stripped = normalize_text(placeholder)

    if not stripped:
        return True

    lowered = stripped.casefold()
    lowered = re.sub(r"\s+", " ", lowered)
    lowered_without_slash = re.sub(r"\s*/\s*$", "", lowered).strip()
    tag_name = lowered_without_slash.split(" ", 1)[0]

    if lowered.startswith(("/", "!", "?")):
        return True

    if lowered.startswith(("ac:", "ri:")):
        return True

    if tag_name.startswith(("ac:", "ri:")):
        return True

    if tag_name in HTML_TAG_NAMES:
        return True

    if re.fullmatch(r"[a-z][a-z0-9_-]*(?:\s*/)?", stripped):
        return True

    return False


def is_real_markup(placeholder):
    stripped = normalize_text(placeholder)

    if not stripped:
        return True

    lowered = stripped.casefold()

    if any(char in stripped for char in ('"', "'", "`", "=")):
        return True

    if lowered.startswith(("ac:", "ri:")):
        return True

    if ":" in lowered:
        return True

    if lowered in HTML_TAG_NAMES:
        return True

    if re.fullmatch(r"[a-z][a-z0-9_-]*", stripped):
        return True

    return False


def has_letter(value):
    return any(char.isalpha() for char in value)


def looks_like_path_or_url(value):
    lowered = normalize_key(value)

    return any(
        signal in lowered
        for signal in (
            "http://",
            "https://",
            "file://",
            "/users/",
            "/volumes/",
            "drive.google.com",
            "docs.google.com",
            ".md",
            ".markdown",
        )
    )


def placeholder_words(value):
    return [
        word
        for word in re.split(r"\s+", normalize_text(value))
        if word
    ]


def looks_like_instruction(value, words):
    lowered = normalize_key(value)

    if len(words) > 6:
        return True

    if lowered.endswith((".", ":", ";")):
        return True

    return any(word in lowered for word in INSTRUCTION_WORDS)


def build_status_macro(title):
    return (
        '<ac:structured-macro ac:name="status">'
        '<ac:parameter ac:name="colour">Grey</ac:parameter>'
        f'<ac:parameter ac:name="title">{escape(title, quote=True)}</ac:parameter>'
        "</ac:structured-macro>"
    )


def build_info_macro(text):
    return (
        '<ac:structured-macro ac:name="info">'
        '<ac:parameter ac:name="title">Kullanım Notu</ac:parameter>'
        "<ac:rich-text-body>"
        f"<p>{escape(text, quote=True)}</p>"
        "</ac:rich-text-body>"
        "</ac:structured-macro>"
    )


def safe_page_file_id(page):
    safe_id = re.sub(r"[^0-9A-Za-z_-]+", "_", str(page["id"]))
    return safe_id.strip("_") or "page"


def write_preview_files(page, original_body, styled_body):
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    safe_id = safe_page_file_id(page)
    before_path = REPORT_DIR / f"{safe_id}_before_storage.xhtml"
    after_path = REPORT_DIR / f"{safe_id}_after_storage.xhtml"
    before_path.write_text(original_body, encoding="utf-8")
    after_path.write_text(styled_body, encoding="utf-8")
    return before_path, after_path


def relative_path(path):
    return str(path.relative_to(ROOT)) if path is not None else ""


def write_report(page_reports, changed_reports, skipped_reports, dry_run):
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        build_report(
            page_reports,
            changed_reports,
            skipped_reports,
            dry_run,
        ),
        encoding="utf-8",
    )


def build_report(page_reports, changed_reports, skipped_reports, dry_run):
    total_escaped = sum(
        report["escaped_count"]
        for report in page_reports
    )
    total_inline_code = sum(
        report["inline_code_count"]
        for report in page_reports
    )
    total_placeholders = sum(
        report["placeholder_count"]
        for report in page_reports
    )
    total_short = sum(
        report["short_count"]
        for report in page_reports
    )
    total_long = sum(
        report["long_count"]
        for report in page_reports
    )
    lines = [
        "# Template Placeholder Style Report",
        "",
        "## Summary",
        "",
        f"- Mode: {'dry-run' if dry_run else 'normal'}",
        f"- Pages scanned: {len(page_reports)}",
        f"- Pages changed: {len(changed_reports)}",
        f"- Escaped placeholders detected: {total_escaped}",
        f"- Inline code placeholders detected: {total_inline_code}",
        f"- Placeholders converted: {total_placeholders}",
        f"- Short placeholders converted to status macro: {total_short}",
        f"- Long placeholders converted to info macro: {total_long}",
        "",
        "## Pages changed",
        "",
    ]

    if changed_reports:
        for report in changed_reports:
            lines.extend(page_changed_lines(report))
    else:
        lines.append("No pages changed.")

    lines.extend(
        [
            "",
            "## Escaped placeholders detected",
            "",
        ]
    )

    if page_reports:
        for report in page_reports:
            lines.append(
                f"- {markdown_text(report['title'])}: {report['escaped_count']}"
            )
    else:
        lines.append("No template pages found.")

    lines.extend(
        [
            "",
            "## Inline code placeholders detected",
            "",
        ]
    )

    if page_reports:
        for report in page_reports:
            lines.append(
                f"- {markdown_text(report['title'])}: {report['inline_code_count']}"
            )
    else:
        lines.append("No template pages found.")

    lines.extend(
        [
            "",
            "## Placeholder count per page",
            "",
        ]
    )

    if page_reports:
        for report in page_reports:
            lines.append(
                f"- {markdown_text(report['title'])}: {report['placeholder_count']}"
            )
    else:
        lines.append("No template pages found.")

    lines.extend(
        [
            "",
            "## Short placeholders converted to status macro",
            "",
        ]
    )
    add_placeholder_list(lines, changed_reports, "short_placeholders")

    lines.extend(
        [
            "",
            "## Long placeholders converted to info macro",
            "",
        ]
    )
    add_placeholder_list(lines, changed_reports, "long_placeholders")

    lines.extend(
        [
            "",
            "## Skipped tag-like candidates",
            "",
        ]
    )
    add_tag_like_list(lines, page_reports)

    lines.extend(
        [
            "",
            "## Skipped risky candidates",
            "",
        ]
    )
    add_skipped_list(lines, page_reports)

    lines.extend(
        [
            "",
            "## Pages skipped",
            "",
        ]
    )

    if skipped_reports:
        for report in skipped_reports:
            lines.append(f"- {markdown_text(report['title'])}: no placeholder styling changes")
    else:
        lines.append("No pages skipped.")

    return "\n".join(lines) + "\n"


def page_changed_lines(report):
    lines = [
        f"### {markdown_text(report['title'])}",
        "",
        f"- Page ID: `{report['id']}`",
        f"- Escaped placeholders detected: {report['escaped_count']}",
        f"- Inline code placeholders detected: {report['inline_code_count']}",
        f"- Placeholder count: {report['placeholder_count']}",
        f"- Short placeholders: {report['short_count']}",
        f"- Long placeholders: {report['long_count']}",
        f"- Before preview: `{report['before_path']}`",
        f"- After preview: `{report['after_path']}`",
        "",
    ]
    return lines


def add_placeholder_list(lines, reports, key):
    wrote_any = False

    for report in reports:
        placeholders = report[key]

        if not placeholders:
            continue

        wrote_any = True
        lines.append(f"### {markdown_text(report['title'])}")
        lines.append("")

        for placeholder in placeholders:
            lines.append(f"- {markdown_text(placeholder)}")

        lines.append("")

    if not wrote_any:
        lines.append("No placeholders in this category.")


def add_tag_like_list(lines, reports):
    wrote_any = False

    for report in reports:
        skipped = report["skipped_tag_like"]

        if not skipped:
            continue

        wrote_any = True
        lines.append(f"### {markdown_text(report['title'])}")
        lines.append("")

        for item in skipped:
            lines.append(
                f"- {markdown_text(item['placeholder'])}: {markdown_text(item['reason'])}"
            )

        lines.append("")

    if not wrote_any:
        lines.append("No tag-like candidates skipped.")


def add_skipped_list(lines, reports):
    wrote_any = False

    for report in reports:
        skipped = report["skipped"]

        if not skipped:
            continue

        wrote_any = True
        lines.append(f"### {markdown_text(report['title'])}")
        lines.append("")

        for item in skipped:
            lines.append(
                f"- {markdown_text(item['placeholder'])}: {markdown_text(item['reason'])}"
            )

        lines.append("")

    if not wrote_any:
        lines.append("No risky candidates skipped.")


def markdown_text(value):
    return normalize_text(value).replace("\n", " ")


def build_page_report(page, style_report, before_path=None, after_path=None):
    return {
        "id": page["id"],
        "title": page["title"],
        "escaped_count": style_report["escaped_count"],
        "inline_code_count": style_report["inline_code_count"],
        "placeholder_count": style_report["placeholder_count"],
        "short_count": style_report["short_count"],
        "long_count": style_report["long_count"],
        "short_placeholders": style_report["short_placeholders"],
        "long_placeholders": style_report["long_placeholders"],
        "skipped_tag_like": style_report["skipped_tag_like"],
        "skipped": style_report["skipped"],
        "before_path": relative_path(before_path) if before_path else "",
        "after_path": relative_path(after_path) if after_path else "",
    }


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
    root_02_page = find_root_child_page(
        client,
        manifest,
        root_page_id,
        ROOT_02_CODE,
    )
    pages_by_id = crawl_subtree(client, root_02_page)
    template_pages = select_template_pages(root_02_page, pages_by_id)
    page_reports = []
    changed_reports = []
    skipped_reports = []
    styled_pages = []

    for page in template_pages:
        styled_body, style_report = style_placeholders(page["body"])
        changed = styled_body != page["body"]
        before_path = None
        after_path = None

        if changed:
            before_path, after_path = write_preview_files(
                page,
                page["body"],
                styled_body,
            )

        page_report = build_page_report(
            page,
            style_report,
            before_path,
            after_path,
        )
        page_reports.append(page_report)

        if changed:
            changed_reports.append(page_report)
            styled_pages.append(
                {
                    "page": page,
                    "body": styled_body,
                    "placeholder_count": style_report["placeholder_count"],
                }
            )

            if args.dry_run:
                print(
                    f"[DRY-RUN STYLE] {page['title']} "
                    f"({style_report['placeholder_count']} placeholders)"
                )
        else:
            skipped_reports.append(page_report)

    write_report(
        page_reports,
        changed_reports,
        skipped_reports,
        args.dry_run,
    )

    if args.dry_run:
        return

    for styled_page in styled_pages:
        page = styled_page["page"]
        print(
            f"[STYLE] {page['title']} "
            f"({styled_page['placeholder_count']} placeholders)"
        )
        client.update_page(
            page["id"],
            space_key,
            page["title"],
            styled_page["body"],
            page["version_number"] + 1,
        )

    print(f"[DONE] Styled {len(styled_pages)} template pages")


if __name__ == "__main__":
    main()
