from pathlib import Path

import yaml

from confluence_publisher import ConfluencePublisher


def main():
    manifest_path = Path(__file__).resolve().parent.parent / "manifest.yaml"

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = yaml.safe_load(f)

    publisher = ConfluencePublisher()

    for result in publisher.sync_structure(manifest):
        status = "CREATE" if result["created"] else "EXISTS"
        print(f'[{status}] {result["code"]}')

    print("[DONE]")


if __name__ == "__main__":
    main()
