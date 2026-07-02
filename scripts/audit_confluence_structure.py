from html import unescape
from pathlib import Path
import re
import unicodedata

import yaml

from confluence_client import ConfluenceClient


ROOT = Path(__file__).resolve().parent.parent
REPORT_PATH = ROOT / "reports" / "confluence_audit_report.md"
FOLDER_PLACEHOLDER = "Bu sayfa, alt dokümanların gruplanması amacıyla oluşturulmuştur."
BODY_SHORT_THRESHOLD = 180
TEMPLATE_SHORT_THRESHOLD = 300

EXPECTED_REGISTER_COLUMNS = {
    "ROOT-00": [
        "Sıra No",
        "Bilgi Başlığı",
        "Durum",
        "Erişim Linki",
    ],
    "ROOT-01": [
        "Sıra No",
        "Kurumsal Kod",
        "Kurumsal Süreç Adı",
        "Durum",
        "Erişim Linki",
    ],
    "ROOT-02": [
        "Sıra No",
        "Şablon Kodu",
        "Şablon Adı",
        "Durum",
        "Erişim Linki",
    ],
    "ROOT-03": [
        "Sıra No",
        "Kayıt/Listesi Kodu",
        "Kayıt/Listesi Adı",
        "Durum",
        "Erişim Linki",
    ],
    "ROOT-04": [
        "Sıra No",
        "Form Kodu",
        "Form Adı",
        "Durum",
        "Erişim Linki",
    ],
    "ROOT-05": [
        "Sıra No",
        "Kılavuz Kodu",
        "Kılavuz Adı",
        "Durum",
        "Erişim Linki",
    ],
    "ROOT-06": [
        "Sıra No",
        "Politika Kodu",
        "Politika Adı",
        "Durum",
        "Erişim Linki",
    ],
    "ROOT-07": [
        "Sıra No",
        "Prosedür Kodu",
        "Prosedür Adı",
        "Durum",
        "Erişim Linki",
    ],
    "ROOT-08": [
        "Sıra No",
        "Plan Kodu",
        "Plan Adı",
        "Durum",
        "Erişim Linki",
    ],
    "ROOT-90": [
        "Sıra No",
        "Çalışma Kodu",
        "Çalışma Adı",
        "Durum",
        "Erişim Linki",
    ],
    "ROOT-91": [
        "Sıra No",
        "Denetim Kodu",
        "Denetim Adı",
        "Durum",
        "Erişim Linki",
    ],
}

CODE_PREFIX_ROOT = {
    "ŞBL": "ROOT-02",
    "LST": "ROOT-03",
    "KLV": "ROOT-05",
    "PRS": "ROOT-07",
    "SRÇ": "ROOT-01",
}

CLEANUP_TERMS = [
    "Dosya Adı",
    "Dosya adı",
    "Markdown",
    ".md",
    ".markdown",
    "Kaynak Dosya",
    "Local",
    "Yerel dosya",
    "dosya yolu",
    "path",
    "filename",
]

PLACEHOLDER_TERMS = [
    "TBD",
    "TODO",
    "Doldurulacak",
    "Hazırlanacak",
    "[...]",
]

MARKDOWN_ARTIFACTS = [
    "# ",
    "## ",
    "|---",
    "- [ ]",
    "`",
    "```",
]


def load_manifest():
    with open(ROOT / "manifest.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def normalize_text(value):
    return unicodedata.normalize("NFC", str(value)).strip()


def normalize_for_compare(value):
    value = normalize_text(value).lower()
    value = re.sub(r"^#+\s*", "", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def strip_document_code(value):
    value = normalize_for_compare(value)
    return re.sub(
        r"^i̇?üc\.bi̇?db\.[a-zçğıöşü]+(?:\.\d{3})?\s*-\s*",
        "",
        value,
    ).strip()


def clean_storage_text(storage):
    storage = re.sub(r"<!\[CDATA\[(.*?)\]\]>", r"\1", storage, flags=re.S)
    storage = re.sub(r"<[^>]+>", " ", storage)
    storage = unescape(storage)
    return re.sub(r"\s+", " ", storage).strip()


def clean_cell_text(storage):
    return clean_storage_text(storage)


def extract_page_link_target(storage):
    match = re.search(
        r'ri:content-title\s*=\s*["\']([^"\']+)["\']',
        storage,
        flags=re.I,
    )

    if match is None:
        return ""

    return unescape(match.group(1)).strip()


def extract_tables(storage):
    tables = []

    for table_match in re.finditer(r"<table\b.*?</table>", storage, flags=re.I | re.S):
        table_html = table_match.group(0)
        rows = []

        for tr_match in re.finditer(r"<tr\b.*?</tr>", table_html, flags=re.I | re.S):
            tr_html = tr_match.group(0)
            cells = []

            for cell_match in re.finditer(
                r"<(th|td)\b[^>]*>(.*?)</\1>",
                tr_html,
                flags=re.I | re.S,
            ):
                tag = cell_match.group(1).lower()
                cell_html = cell_match.group(2)
                cells.append(
                    {
                        "tag": tag,
                        "text": clean_cell_text(cell_html),
                        "link_target": extract_page_link_target(cell_html),
                        "raw": cell_html,
                    }
                )

            if cells:
                rows.append(cells)

        headers = []

        if rows and all(cell["tag"] == "th" for cell in rows[0]):
            headers = [cell["text"] for cell in rows[0]]

        tables.append(
            {
                "headers": headers,
                "rows": rows,
                "data_rows": rows[1:] if headers else rows,
                "raw": table_html,
            }
        )

    return tables


def extract_first_heading(storage):
    match = re.search(
        r"<h([1-6])\b[^>]*>(.*?)</h\1>",
        storage,
        flags=re.I | re.S,
    )

    if match is None:
        return ""

    return clean_storage_text(match.group(2))


def extract_document_code(title):
    match = re.search(
        r"(İÜC\.BİDB\.([A-ZÇĞİÖŞÜ]+)\.\d{3})",
        normalize_text(title),
    )

    if match is None:
        return "", ""

    return match.group(1), match.group(2)


def is_folder_placeholder(body_text):
    return normalize_for_compare(body_text) == normalize_for_compare(FOLDER_PLACEHOLDER)


def page_path(page, pages_by_id):
    parts = [page["title"]]
    parent_id = page.get("parent_id")

    while parent_id and parent_id in pages_by_id:
        parent = pages_by_id[parent_id]
        parts.append(parent["title"])
        parent_id = parent.get("parent_id")

    return " / ".join(reversed(parts))


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


def index_pages_by_title(pages_by_id):
    pages_by_title = {}

    for page in pages_by_id.values():
        key = normalize_text(page["title"])
        pages_by_title.setdefault(key, []).append(page)

    return pages_by_title


def find_root_pages(manifest, pages_by_id, root_page_id):
    root_page = pages_by_id[str(root_page_id)]
    child_pages = [
        pages_by_id[child_id]
        for child_id in root_page["children"]
        if child_id in pages_by_id
    ]
    root_pages = {}

    for node in manifest["nodes"]:
        for child in child_pages:
            if child["title"] == node["title"]:
                root_pages[node["code"]] = child
                break

    return root_pages


def table_cell(row, index):
    if index >= len(row):
        return {
            "text": "",
            "link_target": "",
            "raw": "",
        }

    return row[index]


def find_column_index(columns, exact_name):
    try:
        return columns.index(exact_name)
    except ValueError:
        return -1


def find_code_column(columns):
    for index, column in enumerate(columns):
        if column in ("Kurumsal Kod",):
            return index

        if "Kodu" in column:
            return index

    return -1


def audit_page_tree(pages_by_id, root_pages, pages_by_title):
    no_children_short = []
    folder_pages = []
    duplicate_codes = []
    code_map = {}

    for page in pages_by_id.values():
        body_length = len(page["text"])

        if not page["children"] and body_length < BODY_SHORT_THRESHOLD:
            no_children_short.append(page)

        if is_folder_placeholder(page["text"]) or (page["children"] and body_length < BODY_SHORT_THRESHOLD):
            folder_pages.append(page)

        code, _prefix = extract_document_code(page["title"])

        if code:
            code_map.setdefault(code, []).append(page)

    for code, pages in sorted(code_map.items()):
        if len(pages) > 1:
            duplicate_codes.append(
                {
                    "code": code,
                    "pages": pages,
                }
            )

    return {
        "top_level_roots": root_pages,
        "no_children_short": no_children_short,
        "folder_pages": folder_pages,
        "duplicate_codes": duplicate_codes,
    }


def audit_registers(root_pages, pages_by_title):
    findings = []
    linked_folder_pages = []
    process_rows = []

    for root_code, expected_columns in EXPECTED_REGISTER_COLUMNS.items():
        page = root_pages.get(root_code)

        if page is None:
            findings.append(f"{root_code}: ROOT register page not found.")
            continue

        tables = extract_tables(page["body"])

        if not tables:
            findings.append(f"{root_code}: register table not found.")
            continue

        table = tables[0]

        if table["headers"] != expected_columns:
            findings.append(
                f"{root_code}: expected columns {expected_columns}, found {table['headers']}."
            )

        link_index = find_column_index(table["headers"], "Erişim Linki")
        code_index = find_code_column(table["headers"])
        seen_codes = {}

        for row_number, row in enumerate(table["data_rows"], start=1):
            link_cell = table_cell(row, link_index) if link_index >= 0 else {"text": "", "link_target": ""}
            target_title = normalize_text(link_cell.get("link_target", ""))
            row_label = table_cell(row, code_index)["text"] if code_index >= 0 else f"row {row_number}"

            if link_index >= 0 and not target_title:
                findings.append(f"{root_code}: row {row_number} ({row_label}) has empty Erişim Linki.")

            if target_title:
                target_pages = pages_by_title.get(target_title, [])

                if target_pages and is_folder_placeholder(target_pages[0]["text"]):
                    findings.append(
                        f"{root_code}: row {row_number} ({row_label}) links to folder-only page {target_title}."
                    )
                    linked_folder_pages.append(target_pages[0])

            if code_index >= 0:
                document_code = table_cell(row, code_index)["text"]

                if document_code:
                    if document_code in seen_codes:
                        findings.append(
                            f"{root_code}: duplicate document code {document_code} in rows {seen_codes[document_code]} and {row_number}."
                        )
                    else:
                        seen_codes[document_code] = row_number

                    _full_code, prefix = extract_document_code(document_code)
                    expected_root = CODE_PREFIX_ROOT.get(prefix)

                    if expected_root is not None and expected_root != root_code:
                        findings.append(
                            f"{root_code}: code {document_code} appears to belong under {expected_root}."
                        )

            if root_code == "ROOT-01":
                process_rows.append(
                    build_process_readiness_row(row, link_index, pages_by_title)
                )

    return {
        "findings": findings,
        "linked_folder_pages": linked_folder_pages,
        "process_rows": process_rows,
    }


def build_process_readiness_row(row, link_index, pages_by_title):
    code = table_cell(row, 1)["text"]
    name = table_cell(row, 2)["text"]
    link_cell = table_cell(row, link_index) if link_index >= 0 else {"link_target": ""}
    target_title = normalize_text(link_cell.get("link_target", ""))

    if not target_title:
        status = "MISSING_LINK"
        children = []
    else:
        target_pages = pages_by_title.get(target_title, [])

        if not target_pages:
            status = "NOT_FOUND"
            children = []
        elif is_folder_placeholder(target_pages[0]["text"]):
            status = "FOLDER_ONLY"
            children = target_pages[0]["children"]
        else:
            status = "REAL_CONTENT"
            children = target_pages[0]["children"]

    return {
        "code": code,
        "name": name,
        "target_title": target_title,
        "status": status,
        "children": children,
    }


def audit_cleanup_candidates(pages_by_id):
    candidates = []

    for page in pages_by_id.values():
        raw = page["body"]
        text = page["text"]
        haystacks = {
            "raw": raw.lower(),
            "text": text.lower(),
        }
        matches = []

        for term in CLEANUP_TERMS:
            term_lower = term.lower()

            if term_lower in haystacks["raw"] or term_lower in haystacks["text"]:
                matches.append(term)

        if matches:
            candidates.append(
                {
                    "page": page,
                    "terms": sorted(set(matches)),
                }
            )

    return candidates


def audit_heading_duplication(pages_by_id):
    findings = []

    for page in pages_by_id.values():
        first_heading = extract_first_heading(page["body"])

        if not first_heading:
            continue

        title = page["title"]
        title_compare = normalize_for_compare(title)
        heading_compare = normalize_for_compare(first_heading)

        if title_compare == heading_compare or strip_document_code(title) == strip_document_code(first_heading):
            findings.append(
                {
                    "page": page,
                    "heading": first_heading,
                }
            )

    return findings


def audit_formatting(pages_by_id):
    findings = []

    for page in pages_by_id.values():
        body = page["body"]
        text = page["text"]
        page_findings = []
        style_count = len(re.findall(r"\sstyle\s*=", body, flags=re.I))

        if style_count > 10:
            page_findings.append(f"excessive inline styles ({style_count})")

        if re.search(r"font-family", body, flags=re.I):
            page_findings.append("font-family attributes")

        if re.search(r"font-size", body, flags=re.I):
            page_findings.append("font-size attributes")

        empty_paragraph_count = len(
            re.findall(
                r"<p>\s*(?:&nbsp;|\s|<br\s*/?>)*</p>",
                body,
                flags=re.I,
            )
        )

        if empty_paragraph_count > 2:
            page_findings.append(f"empty paragraphs repeated ({empty_paragraph_count})")

        for table_index, table in enumerate(extract_tables(body), start=1):
            if not table["headers"]:
                page_findings.append(f"table {table_index} has no header row")

            total_cells = 0
            empty_cells = 0

            for row in table["data_rows"]:
                for cell in row:
                    total_cells += 1

                    if not cell["text"] and not cell["link_target"]:
                        empty_cells += 1

            if total_cells >= 10 and empty_cells / total_cells > 0.4:
                page_findings.append(
                    f"table {table_index} has many empty cells ({empty_cells}/{total_cells})"
                )

        for block in re.findall(r"<pre\b.*?</pre>", body, flags=re.I | re.S):
            block_text = clean_storage_text(block)

            if len(block_text) > 120 and len(re.findall(r"[{}();=]", block_text)) < 5:
                page_findings.append("code block may contain regular document text")
                break

        artifact_matches = [
            artifact
            for artifact in MARKDOWN_ARTIFACTS
            if artifact in text or artifact in body
        ]

        if artifact_matches:
            page_findings.append(
                "markdown artifacts: " + ", ".join(sorted(set(artifact_matches)))
            )

        if re.search(r"(&lt;/?[a-z][^&]*&gt;|<\s*/?\s*[a-z]+[^>]*>)", text, flags=re.I):
            page_findings.append("raw HTML fragments that may be broken")

        if page_findings:
            findings.append(
                {
                    "page": page,
                    "findings": page_findings,
                }
            )

    return findings


def audit_completeness(pages_by_id):
    findings = []

    for page in pages_by_id.values():
        text = page["text"]
        page_findings = []
        code, prefix = extract_document_code(page["title"])

        if len(text) < BODY_SHORT_THRESHOLD:
            page_findings.append(f"body length below threshold ({len(text)} chars)")

        if prefix == "SRÇ" and is_folder_placeholder(text):
            page_findings.append("process page is only the folder placeholder")

        if prefix == "ŞBL" and len(text) < TEMPLATE_SHORT_THRESHOLD:
            page_findings.append(f"template page has suspiciously short content ({len(text)} chars)")

        lower_text = text.lower()

        for term in PLACEHOLDER_TERMS:
            if term.lower() in lower_text:
                page_findings.append(f"placeholder term: {term}")

        if re.search(r"(?m)^\s*\.\.\.\s*$", text):
            page_findings.append("standalone placeholder: ...")

        if page_findings:
            findings.append(
                {
                    "page": page,
                    "findings": page_findings,
                }
            )

    return findings


def bullet_page(page, pages_by_id):
    return f"{page_path(page, pages_by_id)} (`{page['id']}`)"


def add_items(lines, items, empty_text="No findings."):
    if not items:
        lines.append(f"- {empty_text}")
        return

    lines.extend(items)


def build_report(
    manifest,
    root_page_id,
    pages_by_id,
    root_pages,
    tree_findings,
    register_findings,
    cleanup_candidates,
    heading_findings,
    formatting_findings,
    completeness_findings,
):
    root_page = pages_by_id[str(root_page_id)]
    lines = []
    total_descendants = len(pages_by_id) - 1
    root_codes_found = ", ".join(sorted(root_pages.keys()))
    folder_link_titles = sorted(
        {
            page["title"]
            for page in register_findings["linked_folder_pages"]
        }
    )

    lines.append("# Confluence Structure Audit Report")
    lines.append("")
    lines.append("## Summary")
    lines.append(f"- Root page: {root_page['title']} (`{root_page['id']}`)")
    lines.append(f"- Total descendant pages: {total_descendants}")
    lines.append(f"- Top-level ROOT pages found: {root_codes_found or 'None'}")
    lines.append(f"- Register findings: {len(register_findings['findings'])}")
    lines.append(f"- Content cleanup candidates: {len(cleanup_candidates)}")
    lines.append(f"- Heading duplication findings: {len(heading_findings)}")
    lines.append(f"- Formatting findings: {len(formatting_findings)}")
    lines.append(f"- Content completeness findings: {len(completeness_findings)}")
    lines.append("")

    lines.append("## Page Tree Findings")
    lines.append("### Top-Level ROOT Pages")
    for node in manifest["nodes"]:
        page = root_pages.get(node["code"])

        if page is None:
            lines.append(f"- [MISSING] {node['code']} - {node['title']}")
        else:
            lines.append(f"- [FOUND] {node['code']} - {page['title']} (`{page['id']}`)")

    lines.append("")
    lines.append("### Pages With No Children And Very Short Body")
    add_items(
        lines,
        [
            f"- {bullet_page(page, pages_by_id)} - {len(page['text'])} chars"
            for page in tree_findings["no_children_short"]
        ],
    )
    lines.append("")
    lines.append("### Folder/Grouping Pages")
    add_items(
        lines,
        [
            f"- {bullet_page(page, pages_by_id)}"
            for page in tree_findings["folder_pages"]
        ],
    )
    lines.append("")
    lines.append("### Folder Pages Linked As Documents")
    add_items(
        lines,
        [
            f"- {title}"
            for title in folder_link_titles
        ],
    )
    lines.append("")
    lines.append("### Duplicate-Looking Document Codes")
    add_items(
        lines,
        [
            "- "
            + duplicate["code"]
            + ": "
            + "; ".join(bullet_page(page, pages_by_id) for page in duplicate["pages"])
            for duplicate in tree_findings["duplicate_codes"]
        ],
    )
    lines.append("")

    lines.append("## Register Findings")
    add_items(
        lines,
        [f"- {finding}" for finding in register_findings["findings"]],
    )
    lines.append("")

    lines.append("## Content Cleanup Candidates")
    add_items(
        lines,
        [
            f"- {bullet_page(item['page'], pages_by_id)} - terms: {', '.join(item['terms'])}"
            for item in cleanup_candidates
        ],
    )
    lines.append("")

    lines.append("## Heading Duplication Findings")
    add_items(
        lines,
        [
            f"- {bullet_page(item['page'], pages_by_id)} - first heading: {item['heading']}"
            for item in heading_findings
        ],
    )
    lines.append("")

    lines.append("## Formatting Findings")
    add_items(
        lines,
        [
            f"- {bullet_page(item['page'], pages_by_id)} - {', '.join(item['findings'])}"
            for item in formatting_findings
        ],
    )
    lines.append("")

    lines.append("## Content Completeness Findings")
    add_items(
        lines,
        [
            f"- {bullet_page(item['page'], pages_by_id)} - {', '.join(item['findings'])}"
            for item in completeness_findings
        ],
    )
    lines.append("")

    lines.append("## Process Readiness")
    process_rows = register_findings["process_rows"]

    if not process_rows:
        lines.append("- ROOT-01 process register rows were not detected.")
    else:
        for process in process_rows:
            child_titles = [
                pages_by_id[child_id]["title"]
                for child_id in process["children"]
                if child_id in pages_by_id
            ]
            children_text = ", ".join(child_titles) if child_titles else "None"
            target = process["target_title"] or "None"
            lines.append(
                f"- {process['code']} | {process['name']} | link: {target} | {process['status']} | child support documents: {children_text}"
            )

    lines.append("")
    lines.append("## Suggested Fix Plan")
    priority_1 = []
    priority_2 = []
    priority_3 = []

    priority_1.extend(
        finding
        for finding in register_findings["findings"]
        if "empty Erişim Linki" in finding
        or "links to folder-only page" in finding
        or "duplicate document code" in finding
    )
    priority_1.extend(
        f"Duplicate code {duplicate['code']}"
        for duplicate in tree_findings["duplicate_codes"]
    )
    priority_2.extend(
        f"{item['page']['title']} contains {', '.join(item['terms'])}"
        for item in cleanup_candidates
    )
    priority_2.extend(
        f"{item['page']['title']} has duplicate first heading"
        for item in heading_findings
    )
    priority_2.extend(
        f"{item['page']['title']} has {', '.join(item['findings'])}"
        for item in completeness_findings
        if any("placeholder" in finding for finding in item["findings"])
    )
    priority_3.extend(
        f"{item['page']['title']} has {', '.join(item['findings'])}"
        for item in formatting_findings
    )

    lines.append("### Priority 1")
    add_items(lines, [f"- {item}" for item in priority_1], "No priority 1 fixes identified.")
    lines.append("")
    lines.append("### Priority 2")
    add_items(lines, [f"- {item}" for item in priority_2], "No priority 2 fixes identified.")
    lines.append("")
    lines.append("### Priority 3")
    add_items(lines, [f"- {item}" for item in priority_3], "No priority 3 fixes identified.")
    lines.append("")

    return lines


def main():
    manifest = load_manifest()
    root_page_id = str(manifest["confluence"]["root"]["page_id"])
    client = ConfluenceClient()
    pages_by_id = crawl_page_tree(client, root_page_id)
    pages_by_title = index_pages_by_title(pages_by_id)
    root_pages = find_root_pages(manifest, pages_by_id, root_page_id)
    tree_findings = audit_page_tree(pages_by_id, root_pages, pages_by_title)
    register_findings = audit_registers(root_pages, pages_by_title)
    cleanup_candidates = audit_cleanup_candidates(pages_by_id)
    heading_findings = audit_heading_duplication(pages_by_id)
    formatting_findings = audit_formatting(pages_by_id)
    completeness_findings = audit_completeness(pages_by_id)
    report_lines = build_report(
        manifest,
        root_page_id,
        pages_by_id,
        root_pages,
        tree_findings,
        register_findings,
        cleanup_candidates,
        heading_findings,
        formatting_findings,
        completeness_findings,
    )

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        "\n".join(report_lines) + "\n",
        encoding="utf-8",
    )

    print("\n".join(report_lines))
    print("[DONE] Audit report written to reports/confluence_audit_report.md")


if __name__ == "__main__":
    main()
