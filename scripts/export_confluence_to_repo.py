from datetime import datetime, timezone
from html import escape
from pathlib import Path
import re
import shutil
import unicodedata

import yaml

from confluence_client import ConfluenceClient


ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = ROOT / "manifest.yaml"
EXPORT_ROOT = ROOT / "confluence"
PAGES_DIR = EXPORT_ROOT / "pages"
INDEX_PATH = EXPORT_ROOT / "index.yaml"
REPORT_PATH = ROOT / "reports" / "confluence_export_report.md"
STORAGE_FILE_NAME = "body.storage.xhtml"
VIEW_FILE_NAME = "body.view.html"


TURKISH_ASCII_MAP = str.maketrans(
    {
        "Ç": "C",
        "Ğ": "G",
        "İ": "I",
        "I": "I",
        "Ö": "O",
        "Ş": "S",
        "Ü": "U",
        "ç": "c",
        "ğ": "g",
        "ı": "i",
        "i": "i",
        "ö": "o",
        "ş": "s",
        "ü": "u",
    }
)


def load_manifest():
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def normalize_text(value):
    return unicodedata.normalize("NFC", str(value)).strip()


def export_timestamp():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def page_url(client, page_id):
    return f"{client.base_url.rstrip('/')}/pages/viewpage.action?pageId={page_id}"


def safe_slug(title):
    value = normalize_text(title).translate(TURKISH_ASCII_MAP)
    value = unicodedata.normalize("NFKD", value)
    value = "".join(char for char in value if not unicodedata.combining(char))
    value = value.casefold()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or "page"


def crawl_pages(client, root_page_id, space_key):
    pages = []

    def crawl(page_id, parent_id="", parent_title="", depth=0):
        page = get_export_page(
            client,
            page_id,
        )
        page_id_text = str(page["id"])
        children = client.get_children(page_id_text).get("results", [])
        record = {
            "page_id": page_id_text,
            "space": space_key,
            "title": normalize_text(page["title"]),
            "parent_id": str(parent_id) if parent_id else "",
            "parent_title": normalize_text(parent_title) if parent_title else "",
            "version": page["version"]["number"],
            "url": page_url(client, page_id_text),
            "depth": depth,
            "status": "active",
            "children_count": len(children),
            "body": page.get("body", {}).get("storage", {}).get("value", ""),
            "view_body": page.get("body", {}).get("view", {}).get("value", ""),
        }
        pages.append(record)

        for child in children:
            crawl(
                child["id"],
                page_id_text,
                record["title"],
                depth + 1,
            )

    crawl(str(root_page_id))
    return pages


def get_export_page(client, page_id):
    return client.get(
        f"/rest/api/content/{page_id}",
        {
            "expand": "body.storage,body.view,version,ancestors",
        },
    )


def assign_export_paths(pages):
    pages_by_id = {
        page["page_id"]: page
        for page in pages
    }
    pages_by_parent_id = {}
    warnings = []

    for page in pages:
        pages_by_parent_id.setdefault(page["parent_id"], []).append(page)

    for sibling_pages in pages_by_parent_id.values():
        assign_sibling_slugs(
            sibling_pages,
            warnings,
        )

    for page in pages:
        parent_id = page["parent_id"]

        if not parent_id:
            page["relative_path"] = f"pages/{page['slug']}"
            page["export_path"] = PAGES_DIR / page["slug"]
        else:
            parent = pages_by_id[parent_id]
            page["relative_path"] = f"{parent['relative_path']}/{page['slug']}"
            page["export_path"] = parent["export_path"] / page["slug"]

    return warnings


def assign_sibling_slugs(pages, warnings):
    base_slugs = {}
    slug_counts = {}

    for page in pages:
        base_slug = build_base_slug(page)
        base_slugs[page["page_id"]] = base_slug
        slug_counts[base_slug] = slug_counts.get(base_slug, 0) + 1

    used_slugs = set()

    for page in pages:
        base_slug = base_slugs[page["page_id"]]

        if slug_counts[base_slug] > 1:
            slug = f"{base_slug}-{page['page_id']}"
            warnings.append(
                f"Aynı üst sayfa altında aynı slug birden fazla üretildi; sayfa ID eklendi: {page['title']}"
            )
        else:
            slug = base_slug

        counter = 2

        while slug in used_slugs:
            slug = f"{base_slug}-{page['page_id']}-{counter}"
            counter += 1

        if slug != base_slug and not slug.endswith(page["page_id"]):
            warnings.append(
                f"Slug çakışması ek sayaç ile giderildi: {page['title']}"
            )

        used_slugs.add(slug)
        page["slug"] = slug


def build_base_slug(page):
    slug = safe_slug(page["title"])

    if page["depth"] == 0:
        return f"000-root-{slug}"

    return slug


def clear_generated_export_paths():
    remove_path(PAGES_DIR)
    remove_path(INDEX_PATH)
    remove_path(REPORT_PATH)


def remove_path(path):
    if not path.exists() and not path.is_symlink():
        return

    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
        return

    path.unlink()


def write_page_export(page, exported_at):
    page_dir = page["export_path"]
    page_dir.mkdir(parents=True, exist_ok=True)
    metadata = {
        "page_id": page["page_id"],
        "space": page["space"],
        "title": page["title"],
        "parent_id": page["parent_id"],
        "parent_title": page["parent_title"],
        "version": page["version"],
        "url": page["url"],
        "depth": page["depth"],
        "status": page["status"],
        "exported_at": exported_at,
        "children_count": page["children_count"],
        "relative_path": page["relative_path"],
        "slug": page["slug"],
        "has_view_html": True,
        "view_file": VIEW_FILE_NAME,
        "storage_file": STORAGE_FILE_NAME,
    }

    (page_dir / "page.yaml").write_text(
        yaml.safe_dump(
            metadata,
            allow_unicode=True,
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    (page_dir / STORAGE_FILE_NAME).write_text(
        page["body"],
        encoding="utf-8",
    )
    (page_dir / VIEW_FILE_NAME).write_text(
        build_view_html(
            page["title"],
            page["view_body"],
        ),
        encoding="utf-8",
    )


def build_view_html(title, body_view):
    escaped_title = escape(title, quote=True)

    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="tr">',
            "<head>",
            '  <meta charset="utf-8">',
            f"  <title>{escaped_title}</title>",
            "  <style>",
            "    body {",
            "      margin: 0;",
            "      background: #fff;",
            "      color: #172b4d;",
            "      font-family: -apple-system, BlinkMacSystemFont, \"Segoe UI\", sans-serif;",
            "      line-height: 1.55;",
            "    }",
            "    .confluence-page {",
            "      max-width: 1100px;",
            "      margin: 0 auto;",
            "      padding: 32px 24px 56px;",
            "    }",
            "    h1, h2, h3, h4, h5, h6 {",
            "      margin: 1.4em 0 0.55em;",
            "      line-height: 1.25;",
            "      color: #0f172a;",
            "    }",
            "    h1 {",
            "      margin-top: 0;",
            "      padding-bottom: 12px;",
            "      border-bottom: 1px solid #d8dee4;",
            "    }",
            "    p {",
            "      margin: 0 0 12px;",
            "    }",
            "    table {",
            "      width: 100%;",
            "      border-collapse: collapse;",
            "      margin: 16px 0;",
            "      table-layout: auto;",
            "    }",
            "    th, td {",
            "      border: 1px solid #c9d1d9;",
            "      padding: 8px 10px;",
            "      vertical-align: top;",
            "    }",
            "    th {",
            "      background: #f6f8fa;",
            "      font-weight: 600;",
            "      text-align: left;",
            "    }",
            "    code {",
            "      background: #f6f8fa;",
            "      border: 1px solid #d8dee4;",
            "      border-radius: 4px;",
            "      padding: 1px 4px;",
            "      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;",
            "      font-size: 0.92em;",
            "    }",
            "    pre {",
            "      background: #f6f8fa;",
            "      border: 1px solid #d8dee4;",
            "      border-radius: 6px;",
            "      padding: 12px;",
            "      overflow-x: auto;",
            "    }",
            "    pre code {",
            "      border: 0;",
            "      padding: 0;",
            "      background: transparent;",
            "    }",
            "    blockquote {",
            "      margin: 16px 0;",
            "      padding: 8px 16px;",
            "      border-left: 4px solid #c9d1d9;",
            "      color: #57606a;",
            "      background: #f6f8fa;",
            "    }",
            "    a {",
            "      color: #0969da;",
            "    }",
            "    .status, span.status-macro, span.aui-lozenge {",
            "      display: inline-block;",
            "      border-radius: 3px;",
            "      padding: 1px 6px;",
            "      background: #eaeef2;",
            "      color: #24292f;",
            "      font-size: 0.85em;",
            "      font-weight: 600;",
            "    }",
            "  </style>",
            "</head>",
            "<body>",
            '  <main class="confluence-page">',
            f"    <h1>{escaped_title}</h1>",
            body_view,
            "  </main>",
            "</body>",
            "</html>",
            "",
        ]
    )


def relative_file_path(page, file_name):
    return f"{page['relative_path']}/{file_name}"


def write_index(manifest, pages, exported_at):
    root_page = pages[0] if pages else {}
    index = {
        "exported_at": exported_at,
        "root_page_id": str(manifest["confluence"]["root"]["page_id"]),
        "root_title": root_page.get("title", manifest["confluence"]["root"].get("title", "")),
        "total_page_count": len(pages),
        "pages": [
            {
                "page_id": page["page_id"],
                "title": page["title"],
                "parent_id": page["parent_id"],
                "depth": page["depth"],
                "relative_path": page["relative_path"],
                "slug": page["slug"],
                "storage_file": relative_file_path(
                    page,
                    STORAGE_FILE_NAME,
                ),
                "view_file": relative_file_path(
                    page,
                    VIEW_FILE_NAME,
                ),
            }
            for page in pages
        ],
    }
    EXPORT_ROOT.mkdir(parents=True, exist_ok=True)
    INDEX_PATH.write_text(
        yaml.safe_dump(
            index,
            allow_unicode=True,
            sort_keys=False,
        ),
        encoding="utf-8",
    )


def write_report(pages, warnings):
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        build_report(pages, warnings),
        encoding="utf-8",
    )


def build_report(pages, warnings):
    root_page = pages[0] if pages else None
    top_level_pages = [
        page
        for page in pages
        if page["depth"] == 1
    ]
    lines = [
        "# Confluence Export Raporu",
        "",
        "## Özet",
        "",
        f"- Export edilen sayfa sayısı: {len(pages)}",
        f"- Export klasörü: `{relative_path(EXPORT_ROOT)}`",
        f"- Index dosyası: `{relative_path(INDEX_PATH)}`",
        "- Her sayfa için Storage XHTML ve render edilmiş HTML önizleme dosyası üretildi.",
        "",
        "## Export Edilen Sayfa Sayısı",
        "",
        f"- Toplam: {len(pages)}",
        "",
        "## Kök Sayfa",
        "",
    ]

    if root_page is None:
        lines.append("- Kök sayfa export edilmedi.")
    else:
        lines.extend(
            [
                f"- Başlık: {markdown_text(root_page['title'])}",
                f"- Sayfa ID: `{root_page['page_id']}`",
                f"- URL: {root_page['url']}",
            ]
        )

    lines.extend(
        [
            "",
            "## Üst Seviye Sayfalar",
            "",
        ]
    )

    if top_level_pages:
        for page in top_level_pages:
            lines.append(f"- {markdown_text(page['title'])} ({page['children_count']} alt sayfa)")
    else:
        lines.append("- Üst seviye sayfa bulunamadı.")

    lines.extend(
        [
            "",
            "## Sayfa Ağacı Özeti",
            "",
        ]
    )

    if pages:
        for page in pages:
            indent = "  " * page["depth"]
            lines.append(
                f"{indent}- {markdown_text(page['title'])} "
                f"(`{page['page_id']}`, `{page['relative_path']}`)"
            )
    else:
        lines.append("- Sayfa ağacı boş.")

    lines.extend(
        [
            "",
            "## Uyarılar",
            "",
        ]
    )

    if warnings:
        for warning in warnings:
            lines.append(f"- {markdown_text(warning)}")
    else:
        lines.append("- Uyarı yok.")

    return "\n".join(lines) + "\n"


def relative_path(path):
    return str(path.relative_to(ROOT))


def markdown_text(value):
    return normalize_text(value).replace("\n", " ")


def main():
    manifest = load_manifest()
    client = ConfluenceClient()
    space_key = manifest["confluence"]["space"]
    root_page_id = str(manifest["confluence"]["root"]["page_id"])
    exported_at = export_timestamp()
    pages = crawl_pages(
        client,
        root_page_id,
        space_key,
    )
    warnings = assign_export_paths(pages)

    clear_generated_export_paths()
    PAGES_DIR.mkdir(parents=True, exist_ok=True)

    for page in pages:
        write_page_export(
            page,
            exported_at,
        )
        print(f"[EXPORT] {'  ' * page['depth']}{page['title']}")

    write_index(
        manifest,
        pages,
        exported_at,
    )
    write_report(
        pages,
        warnings,
    )
    print(f"[DONE] Confluence export completed. {len(pages)} pages exported.")


if __name__ == "__main__":
    main()
