import argparse
from pathlib import Path
import unicodedata

import yaml

from confluence_publisher import ConfluencePublisher


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source-dir",
        required=True,
    )

    return parser.parse_args()


def load_manifest():
    manifest_path = Path(__file__).resolve().parent.parent / "manifest.yaml"

    with open(manifest_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_templates(source_dir):
    source_path = Path(source_dir).expanduser()

    if not source_path.is_dir():
        raise ValueError(f"Source directory does not exist: {source_path}")

    markdown_files = sorted(
        [
            path
            for path in source_path.iterdir()
            if path.is_file() and path.suffix.lower() in (".md", ".markdown")
        ],
        key=lambda path: normalize_text(path.stem),
    )
    templates = []

    for path in markdown_files:
        templates.append(
            {
                "title": normalize_text(path.stem),
                "content": normalize_content(path.read_text(encoding="utf-8-sig")),
            }
        )

    return templates


def normalize_text(value):
    return unicodedata.normalize("NFC", str(value)).strip()


def normalize_content(value):
    return unicodedata.normalize("NFC", str(value)).replace("\r\n", "\n").replace("\r", "\n")


def main():
    args = parse_args()
    manifest = load_manifest()
    templates = load_templates(args.source_dir)
    publisher = ConfluencePublisher()

    imported_templates = publisher.import_templates(
        manifest,
        templates,
    )

    for template in imported_templates:
        print(f'[IMPORT] {template["title"]}')

    publisher.sync_template_register(
        manifest,
        imported_templates,
    )

    print("[UPDATE] ROOT-02 Register")
    print("[DONE]")


if __name__ == "__main__":
    main()
