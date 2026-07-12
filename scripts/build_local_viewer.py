import json
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parent.parent
CONFLUENCE_DIR = ROOT / "confluence"
INDEX_PATH = CONFLUENCE_DIR / "index.yaml"
VIEWER_DIR = ROOT / "viewer"
PAGES_JSON_PATH = VIEWER_DIR / "pages.json"


def load_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_index():
    if not INDEX_PATH.exists():
        raise FileNotFoundError(f"Export index not found: {INDEX_PATH}")

    return load_yaml(INDEX_PATH)


def load_page_metadata(index_page):
    relative_path = index_page["relative_path"]
    page_yaml_path = CONFLUENCE_DIR / relative_path / "page.yaml"

    if not page_yaml_path.exists():
        return {}

    return load_yaml(page_yaml_path)


def viewer_relative_path(confluence_relative_path):
    return f"../confluence/{confluence_relative_path}"


def page_file_path(index_page, metadata, file_key, default_name):
    index_file = index_page.get(file_key)

    if index_file:
        return viewer_relative_path(index_file)

    metadata_file = metadata.get(file_key)

    if metadata_file and "/" in metadata_file:
        return viewer_relative_path(metadata_file)

    return viewer_relative_path(f"{index_page['relative_path']}/{metadata_file or default_name}")


def build_flat_pages(index):
    pages = []

    for index_page in index.get("pages", []):
        metadata = load_page_metadata(index_page)
        pages.append(
            {
                "page_id": str(index_page["page_id"]),
                "title": metadata.get("title", index_page.get("title", "")),
                "parent_id": str(index_page.get("parent_id") or ""),
                "depth": int(index_page.get("depth", metadata.get("depth", 0))),
                "relative_path": index_page["relative_path"],
                "slug": index_page.get("slug", metadata.get("slug", "")),
                "view_file": page_file_path(
                    index_page,
                    metadata,
                    "view_file",
                    "body.view.html",
                ),
                "storage_file": page_file_path(
                    index_page,
                    metadata,
                    "storage_file",
                    "body.storage.xhtml",
                ),
                "children": [],
            }
        )

    return pages


def build_tree(flat_pages):
    pages_by_id = {
        page["page_id"]: page
        for page in flat_pages
    }
    roots = []

    for page in flat_pages:
        parent_id = page["parent_id"]
        parent = pages_by_id.get(parent_id)

        if parent is None:
            roots.append(page)
        else:
            parent["children"].append(page)

    return roots[0] if len(roots) == 1 else {
        "page_id": "",
        "title": "Confluence Export",
        "parent_id": "",
        "depth": 0,
        "relative_path": "",
        "slug": "confluence-export",
        "view_file": "",
        "storage_file": "",
        "children": roots,
    }


def build_pages_json():
    index = load_index()
    flat_pages = build_flat_pages(index)
    tree = build_tree(flat_pages)
    return {
        "exported_at": index.get("exported_at", ""),
        "root_page_id": str(index.get("root_page_id", "")),
        "root_title": index.get("root_title", ""),
        "total_page_count": int(index.get("total_page_count", len(flat_pages))),
        "pages": flat_pages,
        "tree": tree,
    }


def main():
    VIEWER_DIR.mkdir(parents=True, exist_ok=True)
    PAGES_JSON_PATH.write_text(
        json.dumps(
            build_pages_json(),
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print("[BUILD] viewer/pages.json")
    print("[DONE] Local viewer generated.")


if __name__ == "__main__":
    main()
