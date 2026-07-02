import argparse
from copy import deepcopy
from pathlib import Path
import unicodedata

import yaml

from confluence_publisher import ConfluencePublisher
from sync_registers import REGISTER_DEFINITIONS


ROOT_FOLDER_MAPPING = [
    ("00 - Genel Bilgiler", "ROOT-00"),
    ("01 - Süreç Dokümanları", "ROOT-01"),
    ("02 - Şablonlar", "ROOT-02"),
    ("03 - Kayıtlar ve Listeler", "ROOT-03"),
    ("04 - Formlar", "ROOT-04"),
    ("05 - Kılavuzlar", "ROOT-05"),
    ("06 - Politikalar", "ROOT-06"),
    ("07 - Prosedürler", "ROOT-07"),
    ("08 - Planlar", "ROOT-08"),
    ("90 - Denetim Hazırlık", "ROOT-90"),
    ("91 - İç Denetimler", "ROOT-91"),
]
MARKDOWN_EXTENSIONS = (".md", ".markdown")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source-root",
        required=True,
    )

    return parser.parse_args()


def load_manifest():
    manifest_path = Path(__file__).resolve().parent.parent / "manifest.yaml"

    with open(manifest_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def normalize_text(value):
    return unicodedata.normalize("NFC", str(value)).strip()


def normalize_content(value):
    return unicodedata.normalize("NFC", str(value)).replace("\r\n", "\n").replace("\r", "\n")


def sorted_children(path):
    return sorted(
        path.iterdir(),
        key=lambda child: normalize_text(child.name),
    )


def is_markdown_file(path):
    return path.is_file() and path.suffix.lower() in MARKDOWN_EXTENSIONS


def read_markdown(path):
    return normalize_content(path.read_text(encoding="utf-8-sig"))


def load_source_root(source_root):
    source_path = Path(source_root).expanduser()

    if not source_path.is_dir():
        raise ValueError(f"Source root does not exist: {source_path}")

    return source_path


def collect_source_folders(source_root):
    mapping = {
        normalize_text(folder_name): root_code
        for folder_name, root_code in ROOT_FOLDER_MAPPING
    }
    folders = {}
    skipped_folders = []

    for child in sorted_children(source_root):
        if not child.is_dir():
            continue

        folder_name = normalize_text(child.name)

        if folder_name not in mapping:
            skipped_folders.append(folder_name)
            continue

        folders[mapping[folder_name]] = child

    return folders, skipped_folders


def import_root_folder(publisher, manifest, root_code, source_folder):
    space_key = manifest["confluence"]["space"]
    root_page = publisher.find_root_child_page(
        manifest,
        root_code,
    )
    events = []
    documents = []

    import_directory(
        publisher,
        space_key,
        root_page["id"],
        source_folder,
        root_code,
        events,
        documents,
    )

    return events, documents


def import_directory(
    publisher,
    space_key,
    parent_id,
    source_directory,
    root_code,
    events,
    documents,
    ignored_files=None,
):
    ignored_files = ignored_files or set()

    for child in sorted_children(source_directory):
        child_path = child.resolve()

        if child_path in ignored_files:
            continue

        if child.is_dir():
            title = normalize_text(child.name)
            same_named_markdown = find_same_named_markdown_file(
                child,
                title,
            )

            if same_named_markdown is None:
                page = publisher.upsert_child_page(
                    space_key,
                    parent_id,
                    title,
                    publisher.build_folder_body(),
                )
                events.append(
                    {
                        "type": "FOLDER",
                        "title": title,
                    }
                )
                ignored_child_files = set()
            else:
                try:
                    page = publisher.upsert_child_page(
                        space_key,
                        parent_id,
                        title,
                        publisher.markdown_to_storage(
                            read_markdown(same_named_markdown),
                            title,
                        ),
                    )
                except Exception:
                    print(f"[ERROR] Source file: {same_named_markdown.resolve()}")
                    raise

                add_imported_document(
                    publisher,
                    root_code,
                    title,
                    page,
                    documents,
                    events,
                )
                ignored_child_files = {
                    same_named_markdown.resolve(),
                }

            import_directory(
                publisher,
                space_key,
                page["id"],
                child,
                root_code,
                events,
                documents,
                ignored_child_files,
            )
            continue

        if not is_markdown_file(child):
            continue

        title = normalize_text(child.stem)
        try:
            page = publisher.upsert_child_page(
                space_key,
                parent_id,
                title,
                publisher.markdown_to_storage(
                    read_markdown(child),
                    title,
                ),
            )
        except Exception:
            print(f"[ERROR] Source file: {child.resolve()}")
            raise

        add_imported_document(
            publisher,
            root_code,
            title,
            page,
            documents,
            events,
        )


def find_same_named_markdown_file(source_directory, folder_title):
    for child in sorted_children(source_directory):
        if is_markdown_file(child) and normalize_text(child.stem) == folder_title:
            return child

    return None


def add_imported_document(publisher, root_code, title, page, documents, events):
    metadata = publisher.extract_document_metadata(title)
    document = {
        "root_code": root_code,
        "title": title,
        "code": metadata["code"],
        "name": metadata["name"],
        "page": page,
    }

    documents.append(document)
    events.append(
        {
            "type": "IMPORT",
            "title": title,
        }
    )


def build_registers_for_imported_documents(publisher, manifest, documents_by_root, root_codes):
    registers_by_code = {
        register["code"]: register
        for register in deepcopy(REGISTER_DEFINITIONS)
    }
    registers = []

    for folder_name, root_code in ROOT_FOLDER_MAPPING:
        if root_code not in root_codes:
            continue

        register = registers_by_code[root_code]
        documents = documents_by_root.get(root_code, [])

        if root_code == "ROOT-01":
            fill_process_register_links(
                publisher,
                manifest,
                register,
                documents,
            )
        else:
            register["rows"] = build_document_register_rows(
                publisher,
                manifest,
                register,
                documents,
            )

        registers.append(register)

    return registers


def fill_process_register_links(publisher, manifest, register, documents):
    space_key = manifest["confluence"]["space"]
    documents_by_code = {
        document["code"]: document
        for document in documents
    }

    for row in register["rows"]:
        document = documents_by_code.get(row[1])

        if document is None:
            continue

        row[4] = publisher.build_page_link_cell(
            document["title"],
            space_key,
        )


def build_document_register_rows(publisher, manifest, register, documents):
    space_key = manifest["confluence"]["space"]
    rows = []
    sorted_documents = sorted(
        documents,
        key=lambda document: normalize_text(document["code"]),
    )

    for sequence_no, document in enumerate(sorted_documents, start=1):
        link = publisher.build_page_link_cell(
            document["title"],
            space_key,
        )

        if len(register["columns"]) == 4:
            rows.append(
                [
                    sequence_no,
                    document["name"],
                    "Aktif",
                    link,
                ]
            )
        else:
            rows.append(
                [
                    sequence_no,
                    document["code"],
                    document["name"],
                    "Aktif",
                    link,
                ]
            )

    return rows


def main():
    args = parse_args()
    source_root = load_source_root(args.source_root)
    manifest = load_manifest()
    publisher = ConfluencePublisher()
    source_folders, skipped_folders = collect_source_folders(source_root)
    events = []
    documents_by_root = {}
    root_codes = set()

    for folder_name, root_code in ROOT_FOLDER_MAPPING:
        source_folder = source_folders.get(root_code)

        if source_folder is None:
            continue

        root_codes.add(root_code)
        root_events, root_documents = import_root_folder(
            publisher,
            manifest,
            root_code,
            source_folder,
        )
        events.extend(root_events)
        documents_by_root[root_code] = root_documents

    registers = build_registers_for_imported_documents(
        publisher,
        manifest,
        documents_by_root,
        root_codes,
    )
    updated_registers = publisher.sync_registers(
        manifest,
        registers,
    )

    for folder_name in skipped_folders:
        print(f"[SKIP] {folder_name}")

    for event in events:
        print(f'[{event["type"]}] {event["title"]}')

    for register in updated_registers:
        print(f'[UPDATE] {register["code"]} Register')

    print("[DONE]")


if __name__ == "__main__":
    main()
