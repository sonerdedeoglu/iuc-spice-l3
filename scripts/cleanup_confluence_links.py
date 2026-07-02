import argparse
from html import escape, unescape
from pathlib import Path
import re
import unicodedata
from urllib.parse import unquote

import yaml

from confluence_client import ConfluenceClient


ROOT = Path(__file__).resolve().parent.parent
REPORT_PATH = ROOT / "reports" / "confluence_link_cleanup_report.md"

PROTECTED_BLOCK_PATTERN = re.compile(
    r"(<ac:structured-macro\b(?=[^>]*\bac:name=[\"']code[\"']).*?</ac:structured-macro>|"
    r"<pre\b.*?</pre>)",
    flags=re.I | re.S,
)
ANCHOR_PATTERN = re.compile(
    r"<a\b(?P<attrs>[^>]*)>(?P<body>.*?)</a>",
    flags=re.I | re.S,
)
HREF_PATTERN = re.compile(
    r"\bhref\s*=\s*(?P<quote>[\"'])(?P<href>.*?)(?P=quote)",
    flags=re.I | re.S,
)
TABLE_ROW_PATTERN = re.compile(r"<tr\b.*?</tr>", flags=re.I | re.S)
MARKDOWN_FILENAME_PATTERN = re.compile(
    r"(?P<filename>[^<>\"']+?\.(?:markdown|md))(?=\b|$)",
    flags=re.I | re.S,
)
DOCUMENT_CODE_PATTERN = re.compile(
    r"\b(İÜC\.BİDB\.(?:SRÇ|ŞBL|LST|KLV|PRS|PLN|PLT|FRM)\.\d{3})\b",
    flags=re.I,
)

OLD_SOURCE_HINTS = [
    "google drive",
    "drive.google.com",
    "docs.google.com",
    ".md",
    ".markdown",
    "file://",
    "/users/",
    "çalışma alanı",
    "iuc-spice",
    "i̇üc - denetim 2026 - level 3",
]

GENERIC_LINK_TEXTS = {
    "",
    "burada",
    "click here",
    "download",
    "google drive",
    "incele",
    "i̇ncele",
    "link",
    "open",
    "tıklayın",
}


def load_manifest():
    with open(ROOT / "manifest.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def normalize_text(value):
    return unicodedata.normalize("NFC", str(value)).strip()


def normalize_lower(value):
    value = normalize_text(value).casefold()
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def clean_storage_text(storage):
    storage = re.sub(r"<!\[CDATA\[(.*?)\]\]>", r"\1", storage, flags=re.S)
    storage = re.sub(r"<[^>]+>", " ", storage)
    storage = unescape(storage)
    return re.sub(r"\s+", " ", storage).strip()


def decode_link_value(value):
    return normalize_text(unquote(unescape(str(value))).replace("+", " "))


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


def index_pages_by_title(pages_by_id):
    pages_by_title = {}

    for page in pages_by_id.values():
        pages_by_title.setdefault(page["title"], []).append(page)

    return pages_by_title


def cleanup_body_links(page, pages_by_title, report):
    cleaned_parts = []
    position = 0
    page_replacements = []

    for match in PROTECTED_BLOCK_PATTERN.finditer(page["body"]):
        cleaned_segment, replacements = cleanup_unprotected_segment_links(
            page,
            page["body"][position:match.start()],
            pages_by_title,
            report,
        )
        cleaned_parts.append(cleaned_segment)
        cleaned_parts.append(match.group(0))
        page_replacements.extend(replacements)
        position = match.end()

    cleaned_segment, replacements = cleanup_unprotected_segment_links(
        page,
        page["body"][position:],
        pages_by_title,
        report,
    )
    cleaned_parts.append(cleaned_segment)
    page_replacements.extend(replacements)

    return "".join(cleaned_parts), page_replacements


def cleanup_unprotected_segment_links(page, segment, pages_by_title, report):
    cleaned_parts = []
    replacements = []
    position = 0

    for match in TABLE_ROW_PATTERN.finditer(segment):
        cleaned_segment, segment_replacements = replace_anchors_in_segment(
            page,
            segment[position:match.start()],
            pages_by_title,
            report,
            "",
        )
        cleaned_parts.append(cleaned_segment)
        replacements.extend(segment_replacements)

        row_html = match.group(0)
        cleaned_row, row_replacements = replace_anchors_in_segment(
            page,
            row_html,
            pages_by_title,
            report,
            clean_storage_text(row_html),
        )
        cleaned_parts.append(cleaned_row)
        replacements.extend(row_replacements)
        position = match.end()

    cleaned_segment, segment_replacements = replace_anchors_in_segment(
        page,
        segment[position:],
        pages_by_title,
        report,
        "",
    )
    cleaned_parts.append(cleaned_segment)
    replacements.extend(segment_replacements)

    return "".join(cleaned_parts), replacements


def replace_anchors_in_segment(page, segment, pages_by_title, report, row_text):
    replacements = []

    def replace_anchor(match):
        anchor_html = match.group(0)
        attrs = match.group("attrs")
        link_body = match.group("body")
        href = extract_href(attrs)
        link_text = clean_storage_text(link_body)
        decision = resolve_link(
            page,
            href,
            link_text,
            pages_by_title,
            report,
            row_text,
        )

        if decision["action"] != "replace":
            return anchor_html

        replacements.append(decision)
        report["replaced"].append(decision)
        return build_confluence_page_link(
            decision["target_title"],
            decision["visible_text"],
        )

    cleaned_segment = ANCHOR_PATTERN.sub(replace_anchor, segment)
    return cleaned_segment, replacements


def extract_href(attrs):
    match = HREF_PATTERN.search(attrs)

    if match is None:
        return ""

    return decode_link_value(match.group("href"))


def resolve_link(page, href, link_text, pages_by_title, report, row_text=""):
    report["links_scanned"] += 1
    reference = href or link_text

    if not href:
        report["skipped"].append(
            build_skipped_entry(page, reference, "No href attribute")
        )
        return {
            "action": "skip",
        }

    if is_drive_folder_link(href):
        report["skipped"].append(
            build_skipped_entry(page, reference, "Google Drive folder link")
        )
        return {
            "action": "skip",
        }

    if is_email_or_phone_link(href):
        report["skipped"].append(
            build_skipped_entry(page, reference, "Email or phone link")
        )
        return {
            "action": "skip",
        }

    if not is_old_source_reference(href, link_text):
        report["skipped"].append(
            build_skipped_entry(page, reference, "Not an old source link")
        )
        return {
            "action": "skip",
        }

    candidate_titles = extract_candidate_titles(
        href,
        link_text,
    )
    matched_pages = []
    ambiguous_titles = []

    for candidate_title in candidate_titles:
        matches = pages_by_title.get(candidate_title, [])

        if len(matches) > 1:
            ambiguous_titles.append(candidate_title)

        for match in matches:
            if match["id"] not in {page["id"] for page in matched_pages}:
                matched_pages.append(match)

    if ambiguous_titles or len(matched_pages) > 1:
        candidate_title = ambiguous_titles[0] if ambiguous_titles else candidate_titles[0]
        entry = {
            "source_page": page["title"],
            "reference": reference,
            "candidate_title": candidate_title,
            "matches": [matched_page["title"] for matched_page in matched_pages],
        }
        report["ambiguous"].append(entry)
        print(f'[AMBIGUOUS] {page["title"]} -> {candidate_title}')
        return {
            "action": "skip",
        }

    if not matched_pages:
        row_context_decision = resolve_link_from_row_context(
            page,
            href,
            link_text,
            row_text,
            pages_by_title,
            report,
            reference,
        )

        if row_context_decision is not None:
            return row_context_decision

        entry = {
            "source_page": page["title"],
            "reference": reference,
            "candidate_titles": candidate_titles,
        }
        report["unresolved"].append(entry)
        print(f'[UNRESOLVED] {page["title"]} -> {reference}')
        return {
            "action": "skip",
        }

    target_page = matched_pages[0]
    return {
        "action": "replace",
        "source_page": page["title"],
        "old_href": href,
        "old_text": link_text,
        "target_title": target_page["title"],
        "visible_text": choose_visible_text(link_text),
    }


def resolve_link_from_row_context(page, href, link_text, row_text, pages_by_title, report, reference):
    if not row_text:
        return None

    if not is_drive_document_link(href, link_text):
        return None

    document_code = extract_document_code(row_text)

    if not document_code:
        return None

    matched_pages = find_pages_by_code_prefix(
        pages_by_title,
        document_code,
    )

    if len(matched_pages) > 1:
        entry = {
            "source_page": page["title"],
            "reference": reference,
            "candidate_title": document_code,
            "matches": [matched_page["title"] for matched_page in matched_pages],
        }
        report["ambiguous"].append(entry)
        print(f'[AMBIGUOUS] {page["title"]} -> {document_code}')
        return {
            "action": "skip",
        }

    if len(matched_pages) == 1:
        target_page = matched_pages[0]
        return {
            "action": "replace",
            "source_page": page["title"],
            "old_href": href,
            "old_text": link_text,
            "target_title": target_page["title"],
            "visible_text": "İncele",
        }

    return None


def is_drive_folder_link(href):
    return "drive.google.com/drive/folders" in normalize_lower(href)


def is_drive_document_link(href, link_text):
    combined = normalize_lower(f"{href} {link_text}")

    return (
        "drive.google.com" in combined
        or "docs.google.com" in combined
    )


def extract_document_code(text):
    match = DOCUMENT_CODE_PATTERN.search(normalize_text(text))

    if match is None:
        return ""

    return normalize_text(match.group(1))


def find_pages_by_code_prefix(pages_by_title, document_code):
    matches = []
    seen_ids = set()

    for pages in pages_by_title.values():
        for page in pages:
            if page["id"] in seen_ids:
                continue

            if page_title_starts_with_code(page["title"], document_code):
                matches.append(page)
                seen_ids.add(page["id"])

    return matches


def page_title_starts_with_code(title, document_code):
    title = normalize_text(title)

    if not title.startswith(document_code):
        return False

    remaining = title[len(document_code):]

    return (
        remaining == ""
        or remaining[0].isspace()
        or remaining.startswith("-")
    )


def is_email_or_phone_link(href):
    lower_href = normalize_lower(href)
    return lower_href.startswith(("mailto:", "tel:"))


def is_old_source_reference(href, link_text):
    combined = normalize_lower(f"{href} {link_text}")

    if any(hint in combined for hint in OLD_SOURCE_HINTS):
        return True

    return looks_like_local_path(href) or looks_like_local_path(link_text)


def looks_like_local_path(value):
    text = decode_link_value(value)
    lower_text = normalize_lower(text)

    if lower_text.startswith(("file://", "~/", "/users/")):
        return True

    if re.search(r"\b[a-z]:\\", lower_text) is not None:
        return True

    if "\\" in text:
        return True

    if "çalışma alanı" in lower_text:
        return True

    if "iuc-spice" in lower_text:
        return True

    if "i̇üc - denetim 2026 - level 3" in lower_text:
        return True

    return False


def extract_candidate_titles(href, link_text):
    candidates = []

    for value in (link_text, href):
        for title in extract_markdown_titles(value):
            append_unique(candidates, title)

    if candidates:
        return candidates

    visible_title = extract_visible_title_candidate(link_text)

    if visible_title:
        append_unique(candidates, visible_title)

    path_title = extract_path_title_candidate(href)

    if path_title:
        append_unique(candidates, path_title)

    return candidates


def extract_markdown_titles(value):
    decoded_value = decode_link_value(value)
    titles = []

    for match in MARKDOWN_FILENAME_PATTERN.finditer(decoded_value):
        title = normalize_markdown_filename(match.group("filename"))

        if title:
            append_unique(titles, title)

    return titles


def normalize_markdown_filename(filename):
    filename = decode_link_value(filename)
    filename = filename.replace("\\", "/")
    filename = re.split(r"[?#]", filename, maxsplit=1)[0]
    filename = filename.rsplit("/", 1)[-1]
    filename = filename.strip().strip("\"'<>[]")
    lower_filename = normalize_lower(filename)

    if lower_filename.endswith(".markdown"):
        return normalize_text(filename[:-len(".markdown")])

    if lower_filename.endswith(".md"):
        return normalize_text(filename[:-len(".md")])

    return ""


def extract_visible_title_candidate(link_text):
    text = clean_candidate_text(link_text)

    if not text:
        return ""

    if normalize_lower(text) in GENERIC_LINK_TEXTS:
        return ""

    if looks_like_url_or_source_path(text):
        return ""

    return text


def extract_path_title_candidate(href):
    text = decode_link_value(href)

    if not looks_like_local_path(text):
        return ""

    text = re.split(r"[?#]", text, maxsplit=1)[0]
    text = text.replace("\\", "/").rstrip("/")
    title = text.rsplit("/", 1)[-1]
    title = clean_candidate_text(title)

    if not title or normalize_lower(title) in GENERIC_LINK_TEXTS:
        return ""

    return title


def clean_candidate_text(value):
    text = decode_link_value(value)
    text = re.sub(r"\s+", " ", text)
    return text.strip().strip("\"'<>[]")


def looks_like_url_or_source_path(value):
    text = decode_link_value(value)
    lower_text = normalize_lower(text)

    if re.match(r"^[a-z][a-z0-9+.-]*:", lower_text) is not None:
        return True

    if ".md" in lower_text or ".markdown" in lower_text:
        return True

    if looks_like_local_path(text):
        return True

    return False


def choose_visible_text(link_text):
    text = clean_storage_text(link_text)

    if not text:
        return "İncele"

    if looks_like_url_or_source_path(text):
        return "İncele"

    return text


def build_confluence_page_link(target_title, visible_text):
    return (
        "<ac:link>"
        f'<ri:page ri:content-title="{escape(target_title, quote=True)}" />'
        "<ac:plain-text-link-body>"
        f"<![CDATA[{cdata_text(visible_text)}]]>"
        "</ac:plain-text-link-body>"
        "</ac:link>"
    )


def cdata_text(value):
    return str(value).replace("]]>", "]]]]><![CDATA[>")


def append_unique(items, value):
    value = normalize_text(value)

    if value and value not in items:
        items.append(value)


def build_skipped_entry(page, reference, reason):
    return {
        "source_page": page["title"],
        "reference": reference,
        "reason": reason,
    }


def write_report(report):
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Confluence Link Cleanup Report",
        "",
        "## Summary",
        "",
        f"- Mode: {report['mode']}",
        f"- Pages scanned: {report['pages_scanned']}",
        f"- Links scanned: {report['links_scanned']}",
        f"- Pages changed: {len(report['changed_pages'])}",
        f"- Replaced links: {len(report['replaced'])}",
        f"- Unresolved links: {len(report['unresolved'])}",
        f"- Ambiguous links: {len(report['ambiguous'])}",
        f"- Skipped links: {len(report['skipped'])}",
        "",
        "## Replaced Links",
        "",
    ]

    add_replaced_links(lines, report["replaced"])
    lines.extend(["", "## Unresolved Links", ""])
    add_unresolved_links(lines, report["unresolved"])
    lines.extend(["", "## Ambiguous Links", ""])
    add_ambiguous_links(lines, report["ambiguous"])
    lines.extend(["", "## Skipped Links", ""])
    add_skipped_links(lines, report["skipped"])

    REPORT_PATH.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def add_replaced_links(lines, entries):
    if not entries:
        lines.append("No replaced links.")
        return

    for entry in entries:
        lines.extend(
            [
                f"- Source page: {markdown_text(entry['source_page'])}",
                f"  Old href: {markdown_text(entry['old_href'])}",
                f"  Old text: {markdown_text(entry['old_text'])}",
                f"  Target page: {markdown_text(entry['target_title'])}",
                f"  Visible text: {markdown_text(entry['visible_text'])}",
            ]
        )


def add_unresolved_links(lines, entries):
    if not entries:
        lines.append("No unresolved links.")
        return

    for entry in entries:
        candidate_text = ", ".join(entry["candidate_titles"]) or "No candidate title"
        lines.extend(
            [
                f"- Source page: {markdown_text(entry['source_page'])}",
                f"  Reference: {markdown_text(entry['reference'])}",
                f"  Candidate titles: {markdown_text(candidate_text)}",
            ]
        )


def add_ambiguous_links(lines, entries):
    if not entries:
        lines.append("No ambiguous links.")
        return

    for entry in entries:
        matches = ", ".join(entry["matches"]) or "Multiple matching pages"
        lines.extend(
            [
                f"- Source page: {markdown_text(entry['source_page'])}",
                f"  Reference: {markdown_text(entry['reference'])}",
                f"  Candidate title: {markdown_text(entry['candidate_title'])}",
                f"  Matches: {markdown_text(matches)}",
            ]
        )


def add_skipped_links(lines, entries):
    if not entries:
        lines.append("No skipped links.")
        return

    reason_counts = {}

    for entry in entries:
        reason_counts[entry["reason"]] = reason_counts.get(entry["reason"], 0) + 1

    for reason, count in sorted(reason_counts.items()):
        lines.append(f"- {markdown_text(reason)}: {count}")


def markdown_text(value):
    return normalize_text(value).replace("\n", " ")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print pages that would be link-cleaned without updating Confluence.",
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
    pages_by_title = index_pages_by_title(pages_by_id)
    report = {
        "mode": "dry-run" if args.dry_run else "update",
        "pages_scanned": len(pages_by_id),
        "links_scanned": 0,
        "changed_pages": [],
        "replaced": [],
        "unresolved": [],
        "ambiguous": [],
        "skipped": [],
    }

    for page in pages_by_id.values():
        cleaned_body, replacements = cleanup_body_links(
            page,
            pages_by_title,
            report,
        )

        if not replacements:
            continue

        report["changed_pages"].append(
            {
                "title": page["title"],
                "link_count": len(replacements),
            }
        )

        if args.dry_run:
            print(f'[DRY-RUN LINK-CLEAN] {page["title"]} ({len(replacements)} links)')
            continue

        print(f'[LINK-CLEAN] {page["title"]} ({len(replacements)} links)')
        client.update_page(
            page["id"],
            space_key,
            page["title"],
            cleaned_body,
            page["version_number"] + 1,
        )

    write_report(report)
    print("[DONE] Link cleanup report written to reports/confluence_link_cleanup_report.md")


if __name__ == "__main__":
    main()
