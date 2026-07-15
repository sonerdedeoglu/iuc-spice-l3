#!/usr/bin/env python3
"""Finalize local SRÇ.021 publication statuses after verified Confluence publish."""
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "confluence/pages/000-root-iuc-bidb-spice-2026-level-3"

LST002 = BASE / "03-kayitlar-ve-listeler/lst-002-dokuman-degisiklik-kaydi"
LST006 = BASE / "03-kayitlar-ve-listeler/lst-006-standart-surec-envanteri"


def replace_in_page(folder: Path, replacements: list[tuple[str, str]]) -> None:
    for name in ("body.storage.xhtml", "body.view.html"):
        path = folder / name
        content = path.read_text(encoding="utf-8")
        for old, new in replacements:
            content = content.replace(old, new)
        path.write_text(content, encoding="utf-8")


def main() -> None:
    replace_in_page(
        LST002,
        [
            ("Taslak yer tutucu", "-"),
            ("Yerel incelemede", "Confluence'ta yayımlandı"),
        ],
    )
    replace_in_page(
        LST006,
        [
            (
                "Süreç paketi yerelde oluşturulmuş; kullanıcı incelemesi ve kontrollü Confluence yayını beklenmektedir.",
                "Süreç paketi oluşturulmuş, Confluence'ta yayımlanmış ve süreç özel kayıtlarıyla yönetilmektedir.",
            )
        ],
    )
    print("[PASS] SRÇ.021 yayımlama durumları LST.002 ve LST.006 üzerinde tamamlandı.")


if __name__ == "__main__":
    main()
