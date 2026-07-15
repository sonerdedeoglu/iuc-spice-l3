#!/usr/bin/env python3
"""Normalize PRS.001 and KLV.001 to the current PRS/KLV document structure.

This script intentionally preserves the existing document content. It only:
- Adds `1. Doküman Bilgileri` before the initial metadata table.
- Shifts existing numbered H2 headings by +1.
- Rebuilds `body.view.html` from the updated storage body by using the existing
  view page wrapper.

The actual PRS/KLV documents do not get a `0. Şablon Hakkında` section. That
section is only for templates.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = [
    ROOT / "confluence/pages/000-root-iuc-bidb-spice-2026-level-3/07-prosedurler/prs-001-yazilim-projeleri-dokumantasyon-proseduru",
    ROOT / "confluence/pages/000-root-iuc-bidb-spice-2026-level-3/05-kilavuzlar/klv-001-dokuman-yazim-kurallari-talimati",
]

H2_RE = re.compile(r"<h2>(\d+)\.\s*([^<]+)</h2>")


def normalize_storage(text: str) -> str:
    text = text.strip() + "\n"

    if "<h2>1. Doküman Bilgileri</h2>" not in text:
        if not text.startswith("<table>"):
            raise ValueError("Expected document to start with metadata table.")
        text = "<h2>1. Doküman Bilgileri</h2>\n" + text

    def shift(match: re.Match[str]) -> str:
        number = int(match.group(1))
        heading = match.group(2)
        if number == 1 and heading == "Doküman Bilgileri":
            return match.group(0)
        return f"<h2>{number + 1}. {heading}</h2>"

    # Shift only once. If already normalized, keep as-is.
    if "<h2>2. Amaç</h2>" not in text:
        text = H2_RE.sub(shift, text)

    return text


def rebuild_view(view: str, storage: str) -> str:
    marker_start = '<main class="confluence-page">'
    marker_end = "</main>"
    start = view.find(marker_start)
    end = view.rfind(marker_end)
    if start == -1 or end == -1:
        raise ValueError("Could not find local viewer main wrapper.")

    start_content = view.find("\n", start)
    if start_content == -1:
        raise ValueError("Could not find local viewer content start.")

    prefix = view[: start_content + 1]
    suffix = view[end:]

    # Preserve the H1 line from the existing view, then replace the page body.
    after_prefix = view[start_content + 1 : end]
    h1_match = re.match(r"(<h1>.*?</h1>\n?)", after_prefix, flags=re.DOTALL)
    h1 = h1_match.group(1) if h1_match else ""
    return prefix + h1 + storage + suffix


def main() -> None:
    for doc_dir in DOCS:
        storage_path = doc_dir / "body.storage.xhtml"
        view_path = doc_dir / "body.view.html"
        storage = normalize_storage(storage_path.read_text(encoding="utf-8"))
        storage_path.write_text(storage, encoding="utf-8")

        if view_path.exists():
            view = view_path.read_text(encoding="utf-8")
            view_path.write_text(rebuild_view(view, storage), encoding="utf-8")

        print(f"[DONE] Normalized: {doc_dir.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
