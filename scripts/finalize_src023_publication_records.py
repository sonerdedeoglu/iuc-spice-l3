#!/usr/bin/env python3
"""Finalize local SRÇ.023 publication status after verified Confluence publish."""
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "confluence/pages/000-root-iuc-bidb-spice-2026-level-3"
LST006 = BASE / "03-kayitlar-ve-listeler/iuc-bidb-lst-006-standart-surec-envanteri"
REPORT = ROOT / "reports/src023_organization_management_package_report.md"
CURRENT_STATUS = ROOT / "docs/CURRENT_STATUS.md"

PENDING = "Süreç paketi yerelde oluşturulmuş; kullanıcı incelemesi ve kontrollü Confluence yayını beklenmektedir."
PUBLISHED = "Süreç paketi oluşturulmuş, Confluence'ta yayımlanmış ve süreç özel kayıtlarıyla yönetilmektedir."


def main() -> None:
    changed = False
    for name in ("body.storage.xhtml", "body.view.html"):
        path = LST006 / name
        content = path.read_text(encoding="utf-8")
        if PENDING in content:
            content = content.replace(PENDING, PUBLISHED)
            path.write_text(content, encoding="utf-8")
            changed = True
        elif PUBLISHED not in content:
            raise RuntimeError(f"SRÇ.023 yayın durumu bulunamadı: {path}")

    report = REPORT.read_text(encoding="utf-8")
    report = report.replace(
        "- Bu çalışma yalnızca yerel repository ve viewer için hazırlanmıştır.\n- Confluence'a yazma yapılmamıştır; kullanıcı incelemesi ve kontrollü dry-run beklenmektedir.",
        "- Paket 15-07-2026 tarihinde kontrollü dry-run sonrasında Confluence'a yayımlanmıştır.\n- Süreç akışı ve LST.007 etkileşim PNG ekleri yüklenmiş; sayfa başlıkları, ebeveynleri, içerikleri ve ek boyutları canlı ortamdan doğrulanmıştır.\n- Yayın LST.012 altında gerçek Confluence bağlantısıyla kaydedilmiştir.",
    )
    REPORT.write_text(report, encoding="utf-8")
    current_status = CURRENT_STATUS.read_text(encoding="utf-8")
    old_status = "- SRÇ.023 Organizasyonel Yönetim paketinin süreç tanımı, LST.007-LST.010, boş FRM.001 ve Değerlendirme #1 ile yerelde oluşturulması; PRS.006 Organizasyonel Yönetim Prosedürü ile FRM.002.Ş Toplantı Tutanağı Şablonunun hazırlanması. Resmî görev tanımları ve yayımlanan görevli personel bağlantıları için LST.013.Ş ve 03 - Kayıtlar ve Listeler altında LST.013 eklenmiştir. Confluence yayını kullanıcı incelemesi ve onayına bırakılmıştır."
    new_status = "- SRÇ.023 Organizasyonel Yönetim paketi; süreç tanımı, LST.007-LST.010, boş FRM.001, Değerlendirme #1, PRS.006, FRM.002.Ş, LST.013.Ş ve LST.013 ile tamamlanmış; süreç akışı ve etkileşim PNG ekleriyle birlikte 15-07-2026 tarihinde Confluence'a yayımlanıp canlı ortamdan doğrulanmıştır. Yayın LST.012'ye, aktif süreç durumu LST.006'ya işlenmiştir."
    if old_status in current_status:
        current_status = current_status.replace(old_status, new_status)
        CURRENT_STATUS.write_text(current_status, encoding="utf-8")
    elif new_status not in current_status:
        raise RuntimeError("CURRENT_STATUS SRÇ.023 yayın durumu bulunamadı")
    print(f"[PASS] SRÇ.023 yayın durumu tamamlandı; LST.006 değişti={changed}.")


if __name__ == "__main__":
    main()
