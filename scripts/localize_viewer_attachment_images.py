#!/usr/bin/env python3
"""Point exported view HTML images at their local attachment copies.

Confluence view exports keep ``/download/attachments/...`` URLs. Those URLs are
valid on Confluence but make images disappear in the repository's local viewer.
This script changes only ``body.view.html`` image URLs when the corresponding
file exists in the page's local ``attachments`` directory. Storage XHTML is
left untouched for later Confluence synchronization.
"""

from __future__ import annotations

import html
import re
import unicodedata
from pathlib import Path
from urllib.parse import quote, unquote


ROOT = Path(__file__).resolve().parents[1]
PAGES_ROOT = ROOT / "confluence" / "pages"
CORPORATE_PREFIX = "İÜC" + ".BİDB."
IMAGE_TAG_RE = re.compile(r"<img\b[^>]*>", re.IGNORECASE)
ATTRIBUTE_RE = re.compile(r'(?P<name>src|data-image-src)="(?P<value>[^"]*)"')
ALIAS_RE = re.compile(r'data-linked-resource-default-alias="([^"]+)"')


def normalized(value: str) -> str:
    return unicodedata.normalize("NFC", value)


def simplified_filename(value: str) -> str:
    value = html.unescape(unquote(value)).split("?", 1)[0].rsplit("/", 1)[-1]
    value = normalized(value)
    if value.startswith(CORPORATE_PREFIX):
        value = value[len(CORPORATE_PREFIX) :]
    return value


def attachment_map(page_dir: Path) -> dict[str, Path]:
    attachments = page_dir / "attachments"
    if not attachments.is_dir():
        return {}
    return {normalized(path.name): path for path in attachments.iterdir() if path.is_file()}


def resolve_attachment(tag: str, files: dict[str, Path]) -> Path | None:
    alias_match = ALIAS_RE.search(tag)
    candidates: list[str] = []
    if alias_match:
        candidates.append(alias_match.group(1))
    candidates.extend(match.group("value") for match in ATTRIBUTE_RE.finditer(tag))

    for candidate in candidates:
        filename = simplified_filename(candidate)
        match = files.get(normalized(filename))
        if match is not None:
            return match
    return None


def localize_tag(tag: str, attachment: Path) -> str:
    local_url = f"attachments/{quote(attachment.name)}"

    def replace_attribute(match: re.Match[str]) -> str:
        return f'{match.group("name")}="{local_url}"'

    return ATTRIBUTE_RE.sub(replace_attribute, tag)


def process_page(view_file: Path) -> int:
    source = view_file.read_text(encoding="utf-8")
    files = attachment_map(view_file.parent)
    if not files:
        return 0

    changed = 0

    def replace_tag(match: re.Match[str]) -> str:
        nonlocal changed
        tag = match.group(0)
        attachment = resolve_attachment(tag, files)
        if attachment is None:
            return tag
        localized = localize_tag(tag, attachment)
        if localized != tag:
            changed += 1
        return localized

    updated = IMAGE_TAG_RE.sub(replace_tag, source)
    if updated != source:
        view_file.write_text(updated, encoding="utf-8")
    return changed


def main() -> None:
    pages_changed = 0
    images_changed = 0
    for view_file in PAGES_ROOT.glob("**/body.view.html"):
        count = process_page(view_file)
        if count:
            pages_changed += 1
            images_changed += count
    print(f"[DONE] {pages_changed} sayfada {images_changed} görsel yerelleştirildi.")


if __name__ == "__main__":
    main()
