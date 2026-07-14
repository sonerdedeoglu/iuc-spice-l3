#!/usr/bin/env python3
"""Delete only the three explicitly approved obsolete Confluence pages."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from confluence_client import ConfluenceClient


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports/obsolete_confluence_pages_delete_report.md"

SPECS = [
    ("137265918", "İÜC.BİDB.LST.004 - Süreç Gözden Geçirme Matrisi (İÜC.BİDB.SRÇ.001)"),
    ("137265919", "İÜC.BİDB.LST.004 - Süreç Gözden Geçirme Matrisi (İÜC.BİDB.SRÇ.004)"),
    ("137265907", "İÜC.BİDB.LST.007 - Süreç Mimari ve Etkileşim Matrisi"),
]


def write_report(results: list[dict[str, str]], dry_run: bool) -> None:
    lines = [
        "# Eski Confluence Sayfaları Silme Raporu",
        "",
        f"Çalışma modu: {'DRY-RUN' if dry_run else 'NORMAL'}",
        f"Zaman: {datetime.now(timezone.utc).isoformat()}",
        "",
    ]
    lines.extend(f"- {item['status']} — {item['page_id']} — {item['title']}" for item in results)
    lines.append("")
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Delete three approved obsolete Confluence pages")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    client = ConfluenceClient()
    results: list[dict[str, str]] = []
    for page_id, expected_title in SPECS:
        remote = client.get_page(page_id)
        remote_title = str(remote.get("title") or "")
        if remote_title != expected_title:
            raise RuntimeError(f"Silme güvenlik kontrolü başarısız: {page_id} başlığı {remote_title!r}")
        children = client.get_children(page_id).get("results", []) or []
        if children:
            raise RuntimeError(f"Alt sayfası bulunan eski sayfa silinmedi: {page_id} ({len(children)} alt sayfa)")
        if args.dry_run:
            status = "SİLİNECEK"
            print(f"[DRY-RUN] DELETE {page_id} — {expected_title}")
        else:
            response = client.request("DELETE", f"/rest/api/content/{page_id}")
            if response.status_code not in (200, 204):
                response.raise_for_status()
            check = client.request("GET", f"/rest/api/content/{page_id}")
            if check.status_code != 404:
                raise RuntimeError(f"Silme sonrası sayfa hâlâ erişilebilir: {page_id} ({check.status_code})")
            status = "SİLİNDİ"
            print(f"[DELETE] {page_id} — {expected_title}")
        results.append({"status": status, "page_id": page_id, "title": expected_title})

    write_report(results, args.dry_run)
    print(f"[REPORT] {REPORT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
