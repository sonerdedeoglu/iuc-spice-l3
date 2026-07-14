#!/usr/bin/env python3
"""Align the central LST.012 register with active LST.012.Ş and verified events."""
from __future__ import annotations

from pathlib import Path

from rework_src004_work_products_quality import CSS, e, t, table


ROOT = Path(__file__).resolve().parents[1]
PAGE_DIR = ROOT / (
    "confluence/pages/000-root-iuc-bidb-spice-2026-level-3/03-kayitlar-ve-listeler/"
    "iuc-bidb-lst-012-surec-yayginlastirma-ve-bilgilendirme-kaydi"
)
TEMPLATE_DIR = ROOT / (
    "confluence/pages/000-root-iuc-bidb-spice-2026-level-3/02-sablonlar/"
    "iuc-bidb-lst-012-s-surec-yayginlastirma-ve-bilgilendirme-kaydi-sablonu"
)
STORAGE = PAGE_DIR / "body.storage.xhtml"
VIEW = PAGE_DIR / "body.view.html"
TEMPLATE_STORAGE = TEMPLATE_DIR / "body.storage.xhtml"
TEMPLATE_VIEW = TEMPLATE_DIR / "body.view.html"
REPORT = ROOT / "reports/lst012_template_alignment_report.md"

TITLE = "İÜC.BİDB.LST.012 - Süreç Yaygınlaştırma ve Bilgilendirme Kaydı"
TEMPLATE = "İÜC.BİDB.LST.012.Ş - Süreç Yaygınlaştırma ve Bilgilendirme Kaydı Şablonu"
PREPARED_BY = "Soner DEDEOĞLU - Kalite Danışmanı"
REVIEWED_BY = "Levent Bayezit - Proje Yöneticisi"
APPROVED_BY = "Mustafa Nusret SARISAKAL - Bilgi İşlem Daire Başkanı"

PAGES = {
    "SRÇ.001": (
        "İÜC.BİDB.SRÇ.001 - Dokümantasyon Süreci",
        "https://confluence.iuc.edu.tr/pages/viewpage.action?pageId=137265842",
    ),
    "SRÇ.004": (
        "İÜC.BİDB.SRÇ.004 - Süreç Kurulumu Süreci",
        "https://confluence.iuc.edu.tr/pages/viewpage.action?pageId=137265862",
    ),
}


def page_link(key: str, view: bool) -> str:
    title, url = PAGES[key]
    if view:
        return f'<a href="{e(url)}">{e(title)}</a>'
    return (
        f'<ac:link><ri:page ri:content-title="{e(title)}" />'
        f'<ac:plain-text-link-body><![CDATA[{title}]]></ac:plain-text-link-body></ac:link>'
    )


def body(view: bool) -> str:
    parts: list[str] = []
    parts.append("<h2>1. Liste Özeti</h2>")
    parts.append(table(["Alan", "Değer"], [
        [t("Liste Kodu ve Adı"), t(TITLE)],
        [t("Kullanım Amacı"), t("Süreç dokümanları ve ilgili değişiklikler için gerçek yaygınlaştırma ve bilgilendirme kayıtlarını tekil ve izlenebilir biçimde yönetmek")],
        [t("Kullanılan Şablon"), t(TEMPLATE)],
        [t("Sorumlu"), t("Proje Yöneticisi / Yayımlayan")],
        [t("Durum"), t("Aktif")],
        [t("Sürüm"), t("v1.0")],
        [t("Yürürlük Tarihi"), t("14-07-2026")],
    ], view))

    parts.append("<h2>2. Kullanım Değerleri</h2>")
    parts.append(table(["Alan", "Kullanım Kuralı"], [
        [t("Kapsam"), t("Onaylı süreç ve ilişkili dokümanların yayımlanması, hedef kitleye duyurulması, bilgilendirilmesi ve gerektiğinde katılım veya erişim teyidi bu listede izlenir.")],
        [t("Kapsam Dışı"), t("Yalnızca taslak hazırlığı, planlanan duyurular ve gerçekleşmemiş bilgilendirmeler tamamlanmış kayıt olarak gösterilmez.")],
        [t("Güncelleme"), t("Her gerçek yayın veya bilgilendirme olayı sonrasında sorumlu rol tarafından güncellenir.")],
        [t("Kanıt"), t("Her kayıt gerçek Confluence sayfası, e-posta, toplantı kaydı veya eşdeğer doğal kaynak kanıtıyla ilişkilendirilir.")],
        [t("Durum Notu"), t("Yayın yapılmış ancak ayrı hedef kitle duyurusu doğrulanmamışsa bu durum not alanında açıkça belirtilir.")],
    ], view))

    parts.append("<h2>3. Yaygınlaştırma ve Bilgilendirme Kayıtları</h2>")
    parts.append(table(
        ["Tarih", "Süreç", "Konu", "Hedef Kitle", "Yöntem", "Sorumlu", "Kanıt / Bağlantı", "Not"],
        [
            [
                t("14-07-2026"),
                t(PAGES["SRÇ.001"][0]),
                t("SRÇ.001 Dokümantasyon Süreci ve ilişkili destek dokümanlarının güncel Confluence yayını"),
                t("Doküman sorumluları, gözden geçirenler, yayımlayan rolü ve ilgili süreç sahipleri"),
                t("Confluence yayını"),
                t("Proje Yöneticisi / Yayımlayan"),
                page_link("SRÇ.001", view),
                t("Yayın doğrulandı; hedef kitleye ayrı bir duyuru yapıldığı henüz doğrulanmadı. Bilgilendirme bekleniyor."),
            ],
            [
                t("14-07-2026"),
                t(PAGES["SRÇ.004"][0]),
                t("SRÇ.004 Süreç Kurulumu Süreci, PRS.002, KLV.002, KLV.003 ve süreç özel destek dokümanlarının Confluence yayını"),
                t("Süreç sahibi, proje yöneticisi, kalite danışmanı, doküman sorumluları ve ilgili süreç sahipleri"),
                t("Confluence yayını"),
                t("Proje Yöneticisi / Yayımlayan"),
                page_link("SRÇ.004", view),
                t("Yayın doğrulandı; hedef kitleye ayrı bir duyuru yapıldığı henüz doğrulanmadı. Bilgilendirme bekleniyor."),
            ],
        ],
        view,
    ))

    parts.append("<h2>4. Sürüm Geçmişi</h2>")
    parts.append(table(
        ["Sürüm", "Tarih", "Açıklama", "Hazırlayan/Güncelleyen", "Gözden Geçiren", "Onay"],
        [
            [t("v0.1"), t("30-06-2026"), t("İlk taslak oluşturuldu."), t(PREPARED_BY), t("-"), t("-")],
            [
                t("v1.0"),
                t("14-07-2026"),
                t("Kayıt aktif LST.012.Ş yapısına taşındı; doğrulanmamış hazırlık kayıtları kaldırıldı ve doğrulanan Confluence yayınları eklendi."),
                t(PREPARED_BY),
                t(REVIEWED_BY),
                t(APPROVED_BY),
            ],
        ],
        view,
    ))
    return "".join(parts)


def build_view(content: str) -> str:
    return (
        '<!doctype html><html lang="tr"><head><meta charset="utf-8">'
        f'<title>{e(TITLE)}</title><style>{CSS}</style></head>'
        f'<body><main class="confluence-page"><h1>{e(TITLE)}</h1>{content}</main></body></html>\n'
    )


def verify(storage: str) -> None:
    required = (
        "1. Liste Özeti",
        "2. Kullanım Değerleri",
        "3. Yaygınlaştırma ve Bilgilendirme Kayıtları",
        "<th>Süreç</th>",
        "4. Sürüm Geçmişi",
        TEMPLATE,
        "SRÇ.001 Dokümantasyon Süreci",
        "SRÇ.004 Süreç Kurulumu Süreci",
        "Bilgilendirme bekleniyor",
    )
    missing = [item for item in required if item not in storage]
    if missing:
        raise RuntimeError(f"LST.012 zorunlu içerik eksik: {missing}")
    forbidden = ("ŞBL.017", "LST.004", "Drive paylaşımı", "<Rol / kişi>", "<Onay bilgisi>")
    found = [item for item in forbidden if item in storage]
    if found:
        raise RuntimeError(f"LST.012 eski veya doğrulanmamış içerik barındırıyor: {found}")


def replace_once(content: str, old: str, new: str, label: str) -> str:
    if new in content and old not in content:
        return content
    count = content.count(old)
    if count != 1:
        raise RuntimeError(f"LST.012.Ş {label} kalıbı tekil değil: {count}")
    return content.replace(old, new, 1)


def align_template() -> None:
    storage = TEMPLATE_STORAGE.read_text(encoding="utf-8")
    storage = replace_once(
        storage,
        "<th>Tarih</th><th>Konu</th>",
        "<th>Tarih</th><th>S&uuml;re&ccedil;</th><th>Konu</th>",
        "başlık",
    )
    storage = replace_once(
        storage,
        "<td><em>Tarih</em></td><td><em>Konu</em></td>",
        "<td><em>Tarih</em></td><td><em>İ&Uuml;C.BİDB.SR&Ccedil;.XXX - S&uuml;re&ccedil; Adı</em></td><td><em>Konu</em></td>",
        "örnek satır",
    )

    view = TEMPLATE_VIEW.read_text(encoding="utf-8")
    view = replace_once(
        view,
        '<th class="confluenceTh">Tarih</th><th class="confluenceTh">Konu</th>',
        '<th class="confluenceTh">Tarih</th><th class="confluenceTh">Süreç</th><th class="confluenceTh">Konu</th>',
        "yerel görünüm başlığı",
    )
    view = replace_once(
        view,
        '<td class="confluenceTd"><em>Tarih</em></td><td class="confluenceTd"><em>Konu</em></td>',
        '<td class="confluenceTd"><em>Tarih</em></td><td class="confluenceTd"><em>İÜC.BİDB.SRÇ.XXX - Süreç Adı</em></td><td class="confluenceTd"><em>Konu</em></td>',
        "yerel görünüm örnek satırı",
    )
    TEMPLATE_STORAGE.write_text(storage, encoding="utf-8")
    TEMPLATE_VIEW.write_text(view, encoding="utf-8")


def main() -> None:
    align_template()
    storage = body(False)
    view_body = body(True)
    verify(storage)
    STORAGE.write_text(storage + "\n", encoding="utf-8")
    VIEW.write_text(build_view(view_body), encoding="utf-8")
    REPORT.write_text(
        "\n".join([
            "# LST.012 Aktif Şablona Uyum Raporu",
            "",
            "Tarih: 14-07-2026",
            "",
            "- LST.012, aktif LST.012.Ş bölüm ve tablo yapısına taşındı.",
            "- LST.012.Ş ve LST.012 kayıt tablosuna Süreç sütunu eklendi.",
            "- Eski ŞBL.017 ve LST.004 referansları kaldırıldı.",
            "- Gerçek duyuru kanıtı olmayan hazırlık satırları tamamlanmış kayıt olarak taşınmadı.",
            "- SRÇ.001 ve SRÇ.004 için doğrulanan Confluence yayınları kaydedildi.",
            "- Ayrı hedef kitle duyurusu doğrulanmadığı için iki kayıt da 'Bilgilendirme bekleniyor' notuyla tutuldu.",
            "- Confluence yayını kullanıcı incelemesi ve onayından önce yapılmadı.",
            "",
        ]),
        encoding="utf-8",
    )
    print("[PASS] LST.012.Ş ve LST.012 Süreç sütunuyla yerelde güncellendi.")
    print(f"[REPORT] {REPORT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
