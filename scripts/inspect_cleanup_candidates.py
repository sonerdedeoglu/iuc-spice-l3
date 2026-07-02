from html import unescape
from pathlib import Path
import re
import unicodedata

import yaml

from confluence_client import ConfluenceClient


ROOT = Path(__file__).resolve().parent.parent
REPORT_PATH = ROOT / "reports" / "cleanup_candidate_inspection.md"

SEARCH_TERMS = [
    "Dosya Adı",
    "Dosya adı",
    ".md",
    ".markdown",
    "Markdown",
    "dosya yolu",
    "Kaynak Dosya",
    "Kaynak dosya",
]

CODE_BLOCK_PATTERN = re.compile(
    r"<ac:structured-macro\b(?=[^>]*\bac:name=[\"']code[\"']).*?</ac:structured-macro>|"
    r"<pre\b.*?</pre>|"
    r"<code\b.*?</code>",
    flags=re.I | re.S,
)
TABLE_ROW_PATTERN = re.compile(r"<tr\b.*?</tr>", flags=re.I | re.S)
PARAGRAPH_PATTERN = re.compile(r"<p\b.*?</p>", flags=re.I | re.S)
LINK_PATTERN = re.compile(r"<a\b.*?</a>|<ac:link\b.*?</ac:link>", flags=re.I | re.S)


def load_manifest():
    with open(ROOT / "manifest.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def normalize_text(value):
    return unicodedata.normalize("NFC", str(value)).strip()


def clean_storage_text(storage):
    storage = re.sub(r"<!\[CDATA\[(.*?)\]\]>", r"\1", storage, flags=re.S)
    storage = re.sub(r"<[^>]+>", " ", storage)
    storage = unescape(storage)
    return re.sub(r"\s+", " ", storage).strip()


def compact_snippet(value):
    value = re.sub(r"\s+", " ", unescape(value))
    return value.strip()


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


def find_matches(pages_by_id):
    matches = []

    for page in pages_by_id.values():
        page_matches = find_page_matches(page)

        if not page_matches:
            continue

        print(f'[MATCH] {page["title"]} ({page["id"]})')

        for match in page_matches:
            print(f'  - term: {match["term"]}')
            print(f'    inside: {match["location"]}')
            print(f'    snippet: {match["snippet"]}')

        matches.extend(page_matches)

    return matches


def find_page_matches(page):
    body = page["body"]
    matches = []

    for term in SEARCH_TERMS:
        for match in re.finditer(re.escape(term), body):
            matches.append(
                {
                    "page_title": page["title"],
                    "page_id": page["id"],
                    "term": match.group(0),
                    "offset": match.start(),
                    "location": classify_match(body, match.start(), match.end()),
                    "snippet": build_snippet(body, match.start(), match.end()),
                }
            )

    return sorted(
        matches,
        key=lambda item: (
            item["page_title"],
            item["offset"],
            item["term"].lower(),
        ),
    )


def classify_match(body, start, end):
    if is_inside_pattern(CODE_BLOCK_PATTERN, body, start, end):
        return "code/pre block"

    if is_inside_pattern(LINK_PATTERN, body, start, end):
        return "link"

    if is_inside_pattern(TABLE_ROW_PATTERN, body, start, end):
        return "table row"

    if is_inside_pattern(PARAGRAPH_PATTERN, body, start, end):
        return "paragraph"

    return "unknown"


def is_inside_pattern(pattern, body, start, end):
    for match in pattern.finditer(body):
        if match.start() <= start and end <= match.end():
            return True

    return False


def build_snippet(body, start, end, radius=150):
    snippet_start = max(0, start - radius)
    snippet_end = min(len(body), end + radius)
    prefix = "..." if snippet_start > 0 else ""
    suffix = "..." if snippet_end < len(body) else ""
    return compact_snippet(prefix + body[snippet_start:snippet_end] + suffix)


def group_matches_by_location(matches):
    grouped = {
        "table row": [],
        "paragraph": [],
        "code/pre block": [],
        "link": [],
        "unknown": [],
    }

    for match in matches:
        grouped[match["location"]].append(match)

    return grouped


def write_report(matches, pages_by_id):
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    grouped = group_matches_by_location(matches)
    matched_page_ids = sorted({match["page_id"] for match in matches})
    lines = [
        "# Cleanup Candidate Inspection",
        "",
        "## Summary",
        "",
        f"- Pages scanned: {len(pages_by_id)}",
        f"- Pages with matches: {len(matched_page_ids)}",
        f"- Total matches: {len(matches)}",
        f"- Matches inside tables: {len(grouped['table row'])}",
        f"- Matches inside paragraphs: {len(grouped['paragraph'])}",
        f"- Matches inside code/pre blocks: {len(grouped['code/pre block'])}",
        f"- Matches inside links: {len(grouped['link'])}",
        f"- Unknown matches: {len(grouped['unknown'])}",
        "",
        "## Matches by Page",
        "",
    ]

    add_matches_by_page(lines, matches)
    add_location_section(lines, "Matches Inside Tables", grouped["table row"])
    add_location_section(lines, "Matches Inside Paragraphs", grouped["paragraph"])
    add_location_section(lines, "Matches Inside Code/Pre Blocks", grouped["code/pre block"])
    add_location_section(lines, "Matches Inside Links", grouped["link"])
    add_location_section(lines, "Unknown Matches", grouped["unknown"])

    REPORT_PATH.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def add_matches_by_page(lines, matches):
    if not matches:
        lines.append("No matches found.")
        return

    pages = {}

    for match in matches:
        pages.setdefault(
            (match["page_title"], match["page_id"]),
            [],
        ).append(match)

    for (page_title, page_id), page_matches in sorted(pages.items()):
        lines.append(f"- {markdown_text(page_title)} (`{page_id}`): {len(page_matches)} matches")


def add_location_section(lines, title, matches):
    lines.extend(["", f"## {title}", ""])

    if not matches:
        lines.append("No matches.")
        return

    for match in matches:
        lines.extend(
            [
                f"- Page: {markdown_text(match['page_title'])} (`{match['page_id']}`)",
                f"  Term: {markdown_text(match['term'])}",
                f"  Snippet: {markdown_text(match['snippet'])}",
            ]
        )


def markdown_text(value):
    return normalize_text(value).replace("\n", " ")


def main():
    manifest = load_manifest()
    client = ConfluenceClient()
    root_page_id = str(manifest["confluence"]["root"]["page_id"])
    pages_by_id = crawl_page_tree(
        client,
        root_page_id,
    )
    matches = find_matches(pages_by_id)
    write_report(
        matches,
        pages_by_id,
    )
    print("[DONE] Inspection report written to reports/cleanup_candidate_inspection.md")


if __name__ == "__main__":
    main()
