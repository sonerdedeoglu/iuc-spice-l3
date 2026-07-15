#!/usr/bin/env python3
"""Verify published process dissemination records in LST.012."""
from __future__ import annotations

import html
import re
import unicodedata
from pathlib import Path

import yaml

from confluence_client import ConfluenceClient


ROOT = Path(__file__).resolve().parents[1]
PAGE_DIR = ROOT / (
    "confluence/pages/000-root-iuc-bidb-spice-2026-level-3/03-kayitlar-ve-listeler/"
    "iuc-bidb-lst-012-surec-yayginlastirma-ve-bilgilendirme-kaydi"
)


def nfc(value: str) -> str:
    return unicodedata.normalize("NFC", value)


def visible_text(value: str) -> str:
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", value)).split())


def main() -> None:
    metadata = yaml.safe_load((PAGE_DIR / "page.yaml").read_text(encoding="utf-8")) or {}
    page_id = str(metadata.get("page_id") or "")
    remote = ConfluenceClient().get(
        f"/rest/api/content/{page_id}",
        {"expand": "version,body.storage,body.view,ancestors"},
    )
    storage = nfc(remote["body"]["storage"]["value"])
    view = nfc(remote["body"]["view"]["value"])
    combined = f"{storage}\n{view}\n{visible_text(view)}"
    required = [
        "İÜC.BİDB.SRÇ.005 - Süreç Değerlendirme Süreci",
        "PRS.003, PLN.001, RPR.001",
        "Confluence yayını",
        "Bilgilendirme bekleniyor",
        "137265863",
        "İÜC.BİDB.SRÇ.023 - Organizasyonel Yönetim Süreci",
        "PRS.006, FRM.002.Ş, LST.013.Ş, LST.013, RPR.001 güncellemesi",
        "Yayın ve iki PNG eki doğrulandı",
        "137265881",
    ]
    missing = [item for item in required if nfc(item) not in combined]
    parent_id = str((remote.get("ancestors") or [{}])[-1].get("id") or "")
    if parent_id != str(metadata.get("parent_id") or ""):
        missing.append(f"ebeveyn: {metadata.get('parent_id')}")
    if missing:
        raise RuntimeError(f"LST.012 canlı doğrulaması başarısız; eksik: {missing}")

    print(
        f"[OK] {remote['title']} — sayfa {page_id} — "
        f"sürüm {remote['version']['number']} — SRÇ.005 ve SRÇ.023 kayıtları doğrulandı"
    )


if __name__ == "__main__":
    main()
