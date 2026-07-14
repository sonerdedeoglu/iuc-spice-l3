#!/usr/bin/env python3
"""Rebuild SRÇ.004 LST.008 with the active LST.008.Ş structure."""
from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "confluence/index.yaml"
OLD_PAGE_DIR = ROOT / (
    "confluence/pages/000-root-iuc-bidb-spice-2026-level-3/03-kayitlar-ve-listeler/"
    "iuc-bidb-lst-008-is-urunleri-ve-kalite-kriterleri-listesi-iuc-bidb-src-004"
)
RELATIVE_PATH = (
    "pages/000-root-iuc-bidb-spice-2026-level-3/01-surec-dokumanlari/"
    "iuc-bidb-src-004-surec-kurulumu-sureci/"
    "iuc-bidb-lst-008-is-urunleri-ve-kalite-kriterleri-listesi-iuc-bidb-src-004"
)
PAGE_DIR = ROOT / "confluence" / RELATIVE_PATH
STORAGE = PAGE_DIR / "body.storage.xhtml"
VIEW = PAGE_DIR / "body.view.html"
REPORT = ROOT / "reports/src004_lst008_rework_report.md"

TITLE = "İÜC.BİDB.LST.008 - İş Ürünleri ve Kalite Kriterleri Listesi (İÜC.BİDB.SRÇ.004)"
PARENT_ID = "137265862"
PARENT_TITLE = "İÜC.BİDB.SRÇ.004 - Süreç Kurulumu Süreci"
PREPARED_BY = "Soner DEDEOĞLU - Kalite Danışmanı"
REVIEWED_BY = "Levent Bayezit - Proje Yöneticisi"
APPROVED_BY = "Mustafa Nusret SARISAKAL - Bilgi İşlem Daire Başkanı"

# Aktif "02 - Şablonlar" sayfalarındaki güncel doküman adları.
LST001 = "İÜC.BİDB.LST.001 - Aktif Dokümanlar Listesi"
LST006 = "İÜC.BİDB.LST.006 - Standart Süreç Envanteri"
LST007 = "İÜC.BİDB.LST.007 - Süreç Etkileşim Matrisi (İÜC.BİDB.SRÇ.004)"
LST008 = TITLE
LST009 = "İÜC.BİDB.LST.009 - Süreç Performans Ölçüm Seti (İÜC.BİDB.SRÇ.004)"
LST010 = "İÜC.BİDB.LST.010 - Süreç Rol Yetki ve RACI Matrisi (İÜC.BİDB.SRÇ.004)"
LST011 = "İÜC.BİDB.LST.011 - Repository Yapısı"
LST012 = "İÜC.BİDB.LST.012 - Süreç Yaygınlaştırma ve Bilgilendirme Kaydı"
FRM001 = "İÜC.BİDB.FRM.001 - Süreç Gözden Geçirme Formu (İÜC.BİDB.SRÇ.004)"
SRC_TEMPLATE = "İÜC.BİDB.SRÇ.XXX.Ş - Süreç Tanımı Şablonu"
SRC018 = "İÜC.BİDB.SRÇ.018 - Değişiklik Talebi Yönetimi Süreci"
SRC020 = "İÜC.BİDB.SRÇ.020 - Eğitim Süreci"
KLV002 = "İÜC.BİDB.KLV.002 - Süreç Uyarlama Kılavuzu"
KLV003 = "İÜC.BİDB.KLV.003 - Süreç Tasarımı Kontrol Kılavuzu"


CSS = """
body{margin:0;background:#fff;color:#172b4d;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;line-height:1.55}
.confluence-page{max-width:1180px;margin:0 auto;padding:32px 24px 56px}
h1,h2,h3{color:#0f172a;line-height:1.25}h1{margin:0 0 24px;padding-bottom:12px;border-bottom:1px solid #d8dee4}h2{margin:1.45em 0 .55em}
p{margin:0 0 12px}.table-wrap{overflow-x:auto;margin:16px 0}table{width:100%;border-collapse:collapse;table-layout:auto}th,td{border:1px solid #c9d1d9;padding:8px 10px;vertical-align:top}th{background:#f6f8fa;font-weight:600;text-align:left}
code{background:#f6f8fa;border:1px solid #d8dee4;border-radius:4px;padding:1px 4px;font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:.92em}
""".strip()


def e(value: Any) -> str:
    return escape(str(value), quote=True)


def t(value: Any) -> str:
    return e(value)


def table(headers: list[str], rows: list[list[str]], view: bool = False) -> str:
    table_class = ' class="wrapped confluenceTable"' if view else ' class="wrapped"'
    th_class = ' class="confluenceTh"' if view else ""
    td_class = ' class="confluenceTd"' if view else ""
    head = "".join(f"<th{th_class}>{e(header)}</th>" for header in headers)
    body = "".join(
        "<tr>" + "".join(f"<td{td_class}>{cell}</td>" for cell in row) + "</tr>"
        for row in rows
    )
    return (
        f'<div class="table-wrap"><table{table_class}><thead><tr>{head}</tr></thead>'
        f"<tbody>{body}</tbody></table></div>"
    )


def data(view: bool) -> str:
    parts: list[str] = []

    parts.append("<h2>1. Liste Özeti</h2>")
    parts.append(table(["Alan", "Değer"], [
        [t("İlgili Süreç"), t("İÜC.BİDB.SRÇ.004 - Süreç Kurulumu Süreci")],
        [t("Liste Kapsamı"), t("SRÇ.004 kapsamında kullanılan girdi iş ürünleri, üretilen çıktı iş ürünleri ve bu iş ürünlerine uygulanacak kalite kriterleri")],
        [t("Liste Tarihi"), t("15-02-2025")],
        [t("Listeyi Hazırlayan"), t(PREPARED_BY)],
        [t("Listeyi Gözden Geçiren"), t(REVIEWED_BY)],
        [t("Listeyi Onaylayan"), t(APPROVED_BY)],
        [t("Genel Not"), t("Bu liste, Süreç Kurulumu Süreci tasarım paketinin iş ürünlerini tekil, uygulanabilir ve PIM.1 ile izlenebilir şekilde yönetmek amacıyla oluşturulmuştur.")],
    ], view))

    parts.append("<h2>2. Kullanım Değerleri</h2>")
    values = [
        ("Girdi", "Sürecin yürütülmesi için başka süreç, sistem, doküman veya karardan alınan iş ürünü."),
        ("Çıktı", "Süreç faaliyeti sonucunda oluşturulan, güncellenen, onaylanan veya yayımlanan iş ürünü."),
        ("Zorunlu", "Süreç kapsamında beklenen ve yokluğu gerekçelendirilmesi gereken iş ürünü."),
        ("Koşullu", "Belirli değişiklik, uyarlama, eğitim veya uygulama koşulunda beklenen iş ürünü."),
        ("Opsiyonel", "Süreç olgunluğunu destekleyen ancak her durumda zorunlu olmayan yardımcı iş ürünü."),
        ("Uygun", "İş ürünü tanımlı kalite kriterlerini karşılıyor."),
        ("Eksik", "İş ürünü var ancak kalite kriterlerinden biri veya daha fazlası eksik."),
        ("Yok", "Beklenen iş ürünü henüz oluşturulmamış veya erişilebilir değildir."),
        ("Kapsam Dışı", "İlgili süreç tasarımı veya değişiklik bağlamında uygulanmıyor."),
    ]
    parts.append(table(["Değer", "Anlamı"], [[t(a), t(b)] for a, b in values], view))

    parts.append("<h2>3. Girdi İş Ürünleri Matrisi</h2>")
    inputs = [
        ("Yeni süreç veya süreç değişikliği kararı", SRC018, "Süreç tasarımını yetkili karar, kapsam ve öncelik bilgisiyle başlatmak", "Zorunlu", f"Talep ve karar {SRC018} kapsamında izlenebilir olmalıdır; ayrı süreç tasarım talep formu kullanılmaz."),
        ("İlgili standart süreç beklentileri", "ISO/IEC 15504-5 ilgili süreç bölümü, Process Assessment Model ve Process Attributes", "Süreç amacı, sonuçları, BP ve PA/GP beklentilerini belirlemek", "Zorunlu", "Kullanılan standart bölümü ve izlenebilirlik kapsamı açık olmalıdır."),
        ("Standart süreç kimliği ve kapsamı", LST006, "Standart kod, kurumsal kod, Türkçe ad ve süreç seti kapsamını doğrulamak", "Zorunlu", f"Resmî dokümanda sabit süreç sayısı kullanılmaz; güncel kapsam {LST006} üzerinden belirlenir."),
        ("Süreç mimarisi ve etkileşim bilgileri", LST007, "Besleyen/beslenen süreçleri, girdileri, çıktıları ve arayüzleri belirlemek", "Zorunlu", "İlgili süreç satırı güncel olmalıdır."),
        ("Süreç tanımı şablonu", SRC_TEMPLATE, "Süreç dokümanını ortak yapıda hazırlamak", "Zorunlu", "Gerçek süreç dokümanı 1. Süreç Bilgileri bölümüyle başlar; şablonun 0. bölümü taşınmaz."),
        ("Süreç tasarım uygulama yöntemi", "İÜC.BİDB.PRS.002 - Süreç Tasarım Prosedürü", "Tasarım adımlarını, kontrol kapılarını ve kayıt ilişkilerini uygulamak", "Zorunlu", "Güncel ve onaylı prosedür esas alınmalıdır."),
        ("Süreç uyarlama kuralları", KLV002, "Uyarlanabilir alanları, sınırları ve onay koşullarını belirlemek", "Zorunlu", "Süreç amacı ve zorunlu sonuçlar korunmalıdır."),
        ("Süreç tasarım kontrol noktaları", KLV003, "Tasarım paketinin eksiksizliğini ve yayıma hazırlığını kontrol etmek", "Zorunlu", f"Kontrol sonuçları {FRM001} kanıtlarıyla uyumlu olmalıdır."),
        ("Mevcut süreç tanımı ve kullanım verileri", f"İlgili SRÇ dokümanı, {LST009} ve doğal kaynak sistem kayıtları", "Revizyon halinde mevcut durum, performans ve kullanım bilgisini değerlendirmek", "Koşullu", "Yalnızca mevcut süreç güncelleniyorsa kullanılır; ayrı merkezi kullanım registerı oluşturulmaz."),
        ("Değerlendirme ve iyileştirme bulguları", "İÜC.BİDB.SRÇ.005 - Süreç Değerlendirme Süreci ve İÜC.BİDB.SRÇ.006 - Süreç İyileştirme Süreci kapsamındaki kayıtlar", "Tasarım veya revizyon gerektiren GAP ve iyileştirme ihtiyaçlarını değerlendirmek", "Koşullu", "Güncel ve gerçek kanıta dayalı bulgular kullanılmalıdır."),
    ]
    parts.append(table(
        ["Girdi İş Ürünü", "Kaynak Süreç / Kaynak Doküman", "Kullanım Amacı", "Zorunluluk", "Durum / Not"],
        [[t(a), t(b), t(c), t(d), t(f)] for a, b, c, d, f in inputs], view,
    ))

    parts.append("<h2>4. Çıktı İş Ürünleri Matrisi</h2>")
    outputs = [
        ("İlgili SRÇ süreç tanımı", "F3", "Sürecin amaç, sonuç, kapsam, faaliyet, araç, uyarlama ve etkileşimlerini tanımlamak", "Zorunlu", "01 - Süreç Dokümanları / Confluence", f"{SRC_TEMPLATE} kullanılarak hazırlanır; aktif sürüm gözden geçirilmiş ve onaylanmış olmalıdır."),
        (f"Güncellenmiş {LST006} kaydı", "F1", "Süreç kimliğini ve standart süreç seti kapsamını güncel tutmak", "Zorunlu", "03 - Kayıtlar ve Listeler / Confluence", "Ortak kaydın yalnızca ilgili süreç satırı güncellenir."),
        (f"Güncellenmiş {LST007} kaydı", "F1", "Süreç mimarisi, girdiler, çıktılar ve etkileşimleri izlemek", "Zorunlu", "03 - Kayıtlar ve Listeler / Confluence", "Besleyen ve beslenen süreçler kurumsal kod ve adla yazılır."),
        (LST008, "F3", "Süreç girdileri, çıktıları ve kalite kriterlerini yönetmek", "Zorunlu", "İlgili süreç kayıt alanı / Confluence", "Bu liste süreç tasarım paketinin iş ürünü kontrol kaydıdır."),
        (LST009, "F4", "Süreç için az sayıda, yönetilebilir ve karar almaya yarayan ölçümü tanımlamak", "Zorunlu", "İlgili süreç kayıt alanı / Confluence", "Her ölçümün veri kaynağı, hesaplama yöntemi, hedef/eşik, sıklık ve sorumlusu tanımlı olmalıdır."),
        (LST010, "F3", "Rol, sorumluluk, yetki, RACI ve yetkinlikleri tanımlamak", "Zorunlu", "İlgili süreç kayıt alanı / Confluence", "SRÇ faaliyetleriyle tutarlı olmalıdır."),
        ("Süreç uyarlama kuralları", "F5", "Sürecin hangi sınırlar içinde uyarlanabileceğini ve onay koşullarını tanımlamak", "Zorunlu", f"İlgili SRÇ ve {KLV002}", "Amaç ve zorunlu süreç sonuçları korunmalıdır."),
        (FRM001, "F3", "BP ve PA/GP durumunu, kanıtları ve GAP bilgisini izlemek", "Zorunlu", "İlgili süreç alt sayfası / Confluence", f"{KLV003} ile tutarlı ve güncel kanıta dayalı olmalıdır."),
        ("Onaylanmış ve yayımlanmış süreç varlıkları", "F2 / F3", "Süreç setini kurumsal kullanıma açmak", "Zorunlu", "Confluence; gerektiğinde Google Drive", f"{LST001} ve {LST011} yayın/repository bilgileri güncellenmelidir."),
        (LST012, "F2", "Yeni veya güncellenen sürecin hedef kitleye duyurulduğunu izlemek", "Zorunlu", "03 - Kayıtlar ve Listeler / Confluence", "Hedef kitle, tarih, kanal ve bağlantı izlenebilir olmalıdır."),
        ("Eğitim ve katılım kayıtları", "F2", "Süreç uygulaması için gerekli yetkinlik desteğini göstermek", "Koşullu", f"{SRC020} kapsamında belirlenen ortam", "Eğitim gerektiğinde oluşturulur; geçmiş tarihli sahte kayıt üretilmez."),
        ("Süreç kullanım ve performans kayıtları", "F6", "Sürecin belirli bağlamlarda kullanımı ve sonuçlarını izlemek", "Zorunlu", f"{LST009} ve ilgili doğal kaynak sistemler", "Aynı veriyi tekrarlayan ayrı merkezi register oluşturulmaz."),
    ]
    parts.append(table(
        ["Çıktı İş Ürünü", "Üreten Faaliyet", "Kullanım Amacı", "Zorunluluk", "Saklama Yeri / Kayıt", "Durum / Not"],
        [[t(a), t(b), t(c), t(d), t(f), t(g)] for a, b, c, d, f, g in outputs], view,
    ))

    parts.append("<h2>5. Kalite Kriterleri Kontrol Matrisi</h2>")
    criteria = [
        (f"{SRC018} kapsamındaki talep ve karar kaydı", "Tasarımın yetkili ve izlenebilir bir girdisi olmalı", "Yeni süreç veya değişiklik ihtiyacının kapsamı, gerekçesi ve kararı izlenebiliyor mu?", "Kayıt kontrolü", "Süreç Sahibi", f"Talep ve karar {SRC018} kapsamında erişilebilir olmalıdır.", f"Eksikse tasarım başlatılmaz; kayıt {SRC018} kapsamında tamamlanır."),
        (LST006, "Süreç kimliği ve kapsamı güncel olmalı", "Standart kod, kurumsal kod, Türkçe ad ve süreç sahibi tutarlı mı?", "Liste kontrolü", "Süreç Mimarı", "İlgili süreç satırı tekil ve güncel olmalıdır; resmî dokümanda sabit süreç sayısı kullanılmamalıdır.", "Eksik veya çelişkili kayıt düzeltilir."),
        ("İlgili SRÇ süreç tanımı", "Standart beklentileri ve şablon yapısı karşılanmalı", "Amaç, sonuçlar, kapsam, referanslar, faaliyetler, araçlar, ölçüm, uyarlama ve etkileşimler tamam mı?", "Doküman gözden geçirme", "Gözden Geçiren / Kalite Danışmanı", f"{SRC_TEMPLATE} bölümleri tamamlanmış ve ilgili BP/PA beklentileriyle izlenebilir olmalıdır.", "Eksik bölüm veya izlenebilirlik tamamlanır."),
        (LST007, "Süreç etkileşimleri tutarlı olmalı", "Besleyen/beslenen süreçler, girdiler ve çıktılar SRÇ ile uyumlu mu?", "Matris kontrolü", "Süreç Mimarı", "İlgili süreç satırı karşılıklı ilişkilerle tutarlı olmalıdır.", f"Etkilenen {LST007} satırları güncellenir."),
        (LST008, "Girdi, çıktı ve kalite kriterleri yeterli olmalı", "Sürecin temel iş ürünleri, zorunlulukları ve kabul ölçütleri tanımlı mı?", "Liste kontrolü", "Süreç Sahibi / Kalite Danışmanı", "Süreç amacı ve faaliyetlerini destekleyen temel iş ürünleri tekil ve kontrol edilebilir olmalıdır.", "Eksik iş ürünü veya kriter eklenir."),
        (LST009, "Ölçüm seti az sayıda ve yönetilebilir olmalı", "Her ölçüm düzenli üretilebilir mi ve karar almaya yarıyor mu?", "Ölçüm tasarım kontrolü", "Süreç Sahibi / Ölçüm Sorumlusu", "Yalnızca veri kaynağı, hesaplama, hedef/eşik, sıklık ve sorumlusu tanımlı anlamlı ölçümler bulunmalıdır.", "Üretilemeyen veya kullanılmayan ölçüm çıkarılır; eksik alanlar tamamlanır."),
        (LST010, "Rol ve RACI sürecin faaliyetleriyle uyumlu olmalı", "Her temel faaliyet için sorumlu ve hesap veren rol tanımlı mı?", "RACI kontrolü", "Süreç Sahibi", "Rol, yetki, RACI ve yetkinlik bilgileri çelişkisiz ve yeterli olmalıdır.", "Eksik veya çakışan rol/RACI kaydı düzeltilir."),
        ("Araçlar ve Altyapı bölümü", "Uygulama ortamı ve erişim koşulları tanımlı olmalı", "Gerekli araç, altyapı, kullanım amacı, erişim koşulu ve sorumlu birim yazılmış mı?", "Doküman kontrolü", "Süreç Sahibi / Altyapı Sorumlusu", "Sürecin uygulanabilmesi için gerekli çalışma ortamı açıkça tanımlanmalıdır.", "Eksik araç veya altyapı bilgisi tamamlanır."),
        ("Uyarlama kuralları", "Amaç ve zorunlu sonuçlar korunmalı", "Uyarlanabilir alanlar, sınırlar, gerekçe ve onay koşulları tanımlı mı?", f"{KLV002} uyum kontrolü", "Süreç Sahibi / Süreç Mimarı", "Kontrollü uyarlama yaklaşımı açık ve izlenebilir olmalıdır.", "Kural veya onay koşulu netleştirilir."),
        (f"{KLV003} ve {FRM001}", "Yayın öncesi tasarım kontrolü tamamlanmış olmalı", "Şablon, BP, PA/GP, iş ürünü, ölçüm, RACI ve etkileşim kontrolleri yapılmış mı?", "Kontrol listesi ve form kontrolü", "Gözden Geçiren / Kalite Danışmanı", "Kontrol sonucu ve kanıtlar güncel olmalı; eksikler giderilmiş veya açık GAP olarak gösterilmelidir.", "Eksikler tamamlanır veya açık GAP kaydı oluşturulur."),
        ("Onay ve yayın kayıtları", "Yalnızca onaylı sürüm aktif yayımlanmalı", "Gözden geçirme, onay, sürüm ve yayın bilgileri birbiriyle tutarlı mı?", "Yayın kontrolü", "Proje Yöneticisi / Doküman Sorumlusu", f"Aktif sürüm Confluence'da yayımlanmış; {LST001} ve {LST011} bilgileri güncel olmalıdır.", "Onay/yayın tutarsızlığı giderilir."),
        (LST012, "Hedef kitle bilgilendirmesi izlenebilir olmalı", "Yayınlanan süreç için hedef kitle, tarih, kanal ve bağlantı kaydedilmiş mi?", "Kayıt kontrolü", "Proje Yöneticisi / Süreç Sahibi", "Bilgilendirme kaydı yayımlanan sürümle ilişkilendirilmiş olmalıdır.", "Eksik bilgilendirme yapılır ve kayıt güncellenir."),
    ]
    parts.append(table(
        ["İş Ürünü", "Kalite Kriteri", "Kontrol Sorusu", "Kontrol Yöntemi", "Kontrol Sorumlusu", "Kabul Ölçütü", "Uygunsuzluk / Tamamlayıcı Aksiyon"],
        [[t(a), t(b), t(c), t(d), t(f), t(g), t(h)] for a, b, c, d, f, g, h in criteria], view,
    ))

    parts.append("<h2>6. Sürüm Geçmişi</h2>")
    parts.append(table(
        ["Sürüm", "Tarih", "Açıklama", "Hazırlayan / Güncelleyen", "Gözden Geçiren", "Onay"],
        [[t("v1.0"), t("15-02-2025"), t("Süreç Kurulumu Süreci iş ürünleri ve kalite kriterleri listesi oluşturuldu."), t(PREPARED_BY), t(REVIEWED_BY), t(APPROVED_BY)]],
        view,
    ))
    return "".join(parts) + "\n"


def build_view(view_body: str) -> str:
    return f"""<!doctype html>
<html lang="tr">
<head>
  <meta charset="utf-8">
  <title>{e(TITLE)}</title>
  <style>{CSS}</style>
</head>
<body>
<main class="confluence-page">
<h1>{e(TITLE)}</h1>
{view_body}
</main>
</body>
</html>
"""


def migrate_page_location() -> None:
    if OLD_PAGE_DIR.exists() and PAGE_DIR.exists():
        raise RuntimeError("LST.008 hem eski hem yeni yerel konumda bulunuyor; otomatik taşıma durduruldu")
    if OLD_PAGE_DIR.exists():
        PAGE_DIR.parent.mkdir(parents=True, exist_ok=True)
        OLD_PAGE_DIR.rename(PAGE_DIR)
    PAGE_DIR.mkdir(parents=True, exist_ok=True)

    metadata_path = PAGE_DIR / "page.yaml"
    metadata = yaml.safe_load(metadata_path.read_text(encoding="utf-8")) or {}
    metadata.update({
        "parent_id": PARENT_ID,
        "parent_title": PARENT_TITLE,
        "depth": 3,
        "relative_path": RELATIVE_PATH,
    })
    metadata_path.write_text(
        yaml.safe_dump(metadata, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )

    index = yaml.safe_load(INDEX_PATH.read_text(encoding="utf-8")) or {}
    matching = [
        page for page in (index.get("pages") or [])
        if page.get("title") == TITLE
        or page.get("relative_path") == str(OLD_PAGE_DIR.relative_to(ROOT / "confluence"))
    ]
    if len(matching) != 1:
        raise RuntimeError(f"Confluence indeksinde tek LST.008 kaydı bekleniyordu; bulunan: {len(matching)}")
    matching[0].update({
        "parent_id": PARENT_ID,
        "depth": 3,
        "relative_path": RELATIVE_PATH,
        "storage_file": f"{RELATIVE_PATH}/body.storage.xhtml",
        "view_file": f"{RELATIVE_PATH}/body.view.html",
    })
    INDEX_PATH.write_text(
        yaml.safe_dump(index, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )


def validate(storage: str) -> None:
    headings = [
        "1. Liste Özeti", "2. Kullanım Değerleri", "3. Girdi İş Ürünleri Matrisi",
        "4. Çıktı İş Ürünleri Matrisi", "5. Kalite Kriterleri Kontrol Matrisi",
        "6. Sürüm Geçmişi",
    ]
    for heading in headings:
        if f"<h2>{heading}</h2>" not in storage:
            raise RuntimeError(f"Eksik LST.008.Ş başlığı: {heading}")
    required = [
        SRC018,
        "İÜC.BİDB.PRS.002 - Süreç Tasarım Prosedürü",
        SRC_TEMPLATE,
        LST006,
        LST007,
        LST008,
        LST009,
        LST010,
        FRM001,
        "Üreten Faaliyet",
        "Hazırlayan / Güncelleyen",
        "az sayıda, yönetilebilir ve karar almaya yarayan ölçümü",
        "ayrı merkezi register oluşturulmaz",
    ]
    for phrase in required:
        if phrase not in storage:
            raise RuntimeError(f"Zorunlu karar LST.008 içinde bulunamadı: {phrase}")
    forbidden = [
        "LST.004", "FRM.002", "26 süreç", "26 sürec", "&lt;Rol", "&lt;Onay",
        "Süreç Mimari ve Etkileşim Matrisi", "Hazırlayan/Güncelleyen",
    ]
    for phrase in forbidden:
        if phrase in storage:
            raise RuntimeError(f"Eski veya yasaklı ifade LST.008 içinde bulundu: {phrase}")


def write_report() -> None:
    REPORT.write_text(
        "\n".join([
            "# SRÇ.004 LST.008 Yerel Yeniden Çalışma Raporu",
            "",
            "Tarih: 14-07-2026",
            "",
            "- LST.008.Ş şablonundaki 1-6 ana bölüm yapısı uygulandı.",
            "- Girdi, çıktı ve kalite kriterleri PIM.1 ve PRS.002 ile ilişkilendirildi.",
            "- Süreç değişikliği girdileri SRÇ.018'e yönlendirildi; FRM.002 oluşturulmadı.",
            "- LST.009 için az sayıda ve yönetilebilir ölçüm kuralı kalite kriterine dönüştürüldü.",
            "- Sabit süreç sayısı, legacy LST.004 referansları ve boş rol/onay alanları kaldırıldı.",
            "- Süreç özel LST.008 sayfası, mevcut Confluence sayfa kimliği korunarak SRÇ.004 altına taşındı.",
            "- Yalnızca yerel storage/view içerikleri güncellendi; Confluence'a yayın yapılmadı.",
            "",
        ]),
        encoding="utf-8",
    )


def main() -> None:
    migrate_page_location()
    storage = data(view=False)
    validate(storage)
    view_body = data(view=True)
    STORAGE.write_text(storage, encoding="utf-8")
    VIEW.write_text(build_view(view_body), encoding="utf-8")
    write_report()
    print(f"[DONE] {TITLE} yerelde güncellendi.")
    print(f"[REPORT] {REPORT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
