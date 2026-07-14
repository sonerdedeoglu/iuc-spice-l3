#!/usr/bin/env python3
"""Rebuild the remaining SRÇ.004 process-specific documents from active templates."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from rework_src004_work_products_quality import CSS, INDEX_PATH, ROOT, e, t, table


SRC004_TITLE = "İÜC.BİDB.SRÇ.004 - Süreç Kurulumu Süreci"
SRC004_ID = "137265862"
SRC004_REL = (
    "pages/000-root-iuc-bidb-spice-2026-level-3/01-surec-dokumanlari/"
    "iuc-bidb-src-004-surec-kurulumu-sureci"
)
CENTRAL_REL = "pages/000-root-iuc-bidb-spice-2026-level-3/03-kayitlar-ve-listeler"

PREPARED_BY = "Soner DEDEOĞLU - Kalite Danışmanı"
REVIEWED_BY = "Levent Bayezit - Proje Yöneticisi"
APPROVED_BY = "Mustafa Nusret SARISAKAL - Bilgi İşlem Daire Başkanı"

LST001 = "İÜC.BİDB.LST.001 - Aktif Dokümanlar Listesi"
LST006 = "İÜC.BİDB.LST.006 - Standart Süreç Envanteri"
LST007 = "İÜC.BİDB.LST.007 - Süreç Etkileşim Matrisi (İÜC.BİDB.SRÇ.004)"
LST008 = "İÜC.BİDB.LST.008 - İş Ürünleri ve Kalite Kriterleri Listesi (İÜC.BİDB.SRÇ.004)"
LST009 = "İÜC.BİDB.LST.009 - Süreç Performans Ölçüm Seti (İÜC.BİDB.SRÇ.004)"
LST010 = "İÜC.BİDB.LST.010 - Süreç Rol Yetki ve RACI Matrisi (İÜC.BİDB.SRÇ.004)"
LST011 = "İÜC.BİDB.LST.011 - Repository Yapısı"
LST012 = "İÜC.BİDB.LST.012 - Süreç Yaygınlaştırma ve Bilgilendirme Kaydı"
FRM001 = "İÜC.BİDB.FRM.001 - Süreç Gözden Geçirme Formu (İÜC.BİDB.SRÇ.004)"
KLV002 = "İÜC.BİDB.KLV.002 - Süreç Uyarlama Kılavuzu"
KLV003 = "İÜC.BİDB.KLV.003 - Süreç Tasarımı Kontrol Kılavuzu"
PRS002 = "İÜC.BİDB.PRS.002 - Süreç Tasarım Prosedürü"
SRC018 = "İÜC.BİDB.SRÇ.018 - Değişiklik Talebi Yönetimi Süreci"
SRC020 = "İÜC.BİDB.SRÇ.020 - Eğitim Süreci"
SRC001 = "İÜC.BİDB.SRÇ.001 - Dokümantasyon Süreci"
SRC_TEMPLATE = "İÜC.BİDB.SRÇ.XXX.Ş - Süreç Tanımı Şablonu"

LST009_SLUG = "iuc-bidb-lst-009-surec-performans-olcum-seti-iuc-bidb-src-004"
LST010_SLUG = "iuc-bidb-lst-010-surec-rol-yetki-ve-raci-matrisi-iuc-bidb-src-004"
FRM001_SLUG = "iuc-bidb-frm-001-surec-gozden-gecirme-formu-iuc-bidb-src-004"
REVIEW_PARENT_ID = "137265917"
REVIEW_PARENT_TITLE = "Süreç Gözden Geçirmeleri"
REVIEW_PARENT_REL = (
    "pages/000-root-iuc-bidb-spice-2026-level-3/91-ic-denetimler/"
    "surec-gozden-gecirmeleri"
)
FRM001_ASSESSMENT_TITLE = f"{FRM001} - Değerlendirme #1"
FRM001_ASSESSMENT_SLUG = f"{FRM001_SLUG}-degerlendirme-1"
FRM001_ASSESSMENT_REL = f"{REVIEW_PARENT_REL}/{FRM001_ASSESSMENT_SLUG}"

DOCS: dict[str, dict[str, str]] = {
    "lst009": {
        "page_id": "137265909",
        "title": LST009,
        "slug": LST009_SLUG,
        "old_rel": f"{CENTRAL_REL}/{LST009_SLUG}",
        "new_rel": f"{SRC004_REL}/{LST009_SLUG}",
    },
    "lst010": {
        "page_id": "137265910",
        "title": LST010,
        "slug": LST010_SLUG,
        "old_rel": f"{CENTRAL_REL}/{LST010_SLUG}",
        "new_rel": f"{SRC004_REL}/{LST010_SLUG}",
    },
    "frm001": {
        "page_id": "137266147",
        "title": FRM001,
        "slug": FRM001_SLUG,
        "old_rel": f"{SRC004_REL}/{FRM001_SLUG}",
        "new_rel": f"{SRC004_REL}/{FRM001_SLUG}",
    },
}

REPORT = ROOT / "reports/src004_remaining_documents_report.md"


def build_view(title: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="tr">
<head>
  <meta charset="utf-8">
  <title>{e(title)}</title>
  <style>{CSS}</style>
</head>
<body>
<main class="confluence-page">
<h1>{e(title)}</h1>
{body}
</main>
</body>
</html>
"""


def lst009_data(view: bool) -> str:
    parts: list[str] = ["<h2>1. Liste Özeti</h2>"]
    parts.append(table(["Alan", "Değer"], [
        [t("İlgili Süreç"), t(SRC004_TITLE)],
        [t("Liste Kapsamı"), t("Süreç kurulum paketinin tamlığı, zamanında gözden geçirilmesi ve onay sonrası yayın/bilgilendirme performansı")],
        [t("Liste Tarihi"), t("15-02-2025")],
        [t("Listeyi Hazırlayan"), t(PREPARED_BY)],
        [t("Listeyi Gözden Geçiren"), t(REVIEWED_BY)],
        [t("Listeyi Onaylayan"), t(APPROVED_BY)],
        [t("Genel Not"), t("Yalnızca düzenli olarak üretilebilen ve karar almaya yarayan üç ölçüm kullanılır. Ölçüm sonuçları gerçek kaynak kayıtlar oluştukça izlenir; geçmişe dönük sonuç üretilmez.")],
    ], view))

    parts.append("<h2>2. Kullanım Değerleri</h2>")
    values = [
        ("Ölçüm ID", "Sürece özel tekil ölçüm kimliği. Format: SRÇ.004-Ö01, SRÇ.004-Ö02."),
        ("Veri Kaynağı", "Ölçümün elde edileceği kayıt, liste, sistem, rapor veya gözden geçirme çıktısı."),
        ("Hedef", "Ölçüm için beklenen sayısal veya nitel başarı değeri."),
        ("Eşik", "Sapma değerlendirmesinde kullanılacak asgari veya kritik sınır."),
        ("Sıklık", "Ölçümün hangi periyotta toplanacağı ve değerlendirileceği."),
        ("Aktif", "Ölçüm ilgili süreç için yürürlükte ve izleniyor."),
        ("Askıda", "Ölçüm tanımlı ancak veri toplama henüz başlamamış veya geçici olarak durdurulmuş."),
        ("Kapsam Dışı", "Ölçüm ilgili süreç veya proje bağlamında uygulanmıyor."),
    ]
    parts.append(table(["Değer", "Anlamı"], [[t(a), t(b)] for a, b in values], view))

    parts.append("<h2>3. Performans Ölçüm Matrisi</h2>")
    metrics = [
        (
            "SRÇ.004-Ö01", "Süreç tasarım paketi tamlık oranı",
            "Standart süreç setindeki süreçler için zorunlu süreç özel doküman paketinin tamamlanma durumunu izlemek",
            f"{LST006} içinde yer alan ve SRÇ, LST.008, LST.009, LST.010 ile FRM.001 kayıtları tamamlanan süreç sayısı / güncel standart süreç setindeki süreç sayısı × 100",
            f"{LST006}, ilgili süreç alt sayfaları ve {LST001}", "Aylık",
            "Hedef: %100 / Eşik: %90", "Kalite Danışmanı / Süreç Mimarı", "PIM.1.BP3; GP.2.2.3; GP.3.1.1", "Aktif",
        ),
        (
            "SRÇ.004-Ö02", "Zamanında süreç gözden geçirme oranı",
            "Gözden geçirme zamanı gelen süreçlerin planlanan dönemde değerlendirilmesini izlemek",
            "Planlanan dönemde FRM.001 gözden geçirmesi tamamlanan süreç sayısı / aynı dönemde gözden geçirmesi gereken süreç sayısı × 100",
            f"{LST001} ve ilgili süreçlerin FRM.001 kayıtları", "Üç aylık",
            "Hedef: %100 / Eşik: %90", "Süreç Sahibi / Kalite Danışmanı", "GP.2.1.2; GP.2.2.4; GP.3.1.5", "Aktif",
        ),
        (
            "SRÇ.004-Ö03", "Zamanında yayın ve bilgilendirme oranı",
            "Onaylanan yeni veya güncellenen süreç varlıklarının hedef kitleye zamanında ulaştırılmasını izlemek",
            "Onaydan sonra beş iş günü içinde yayımlanan ve bilgilendirme kaydı oluşturulan süreç varlığı sayısı / dönemde onaylanan süreç varlığı sayısı × 100",
            f"Confluence sürüm/onay bilgisi, {LST001} ve {LST012}", "Her yayın sonrası; aylık özet",
            "Hedef: %100 / Eşik: %90", "Proje Yöneticisi / Yayımlayan", "PIM.1.BP2; GP.3.2.2", "Aktif",
        ),
    ]
    parts.append(table(
        ["Ölçüm ID", "Ölçüm Adı", "Ölçüm Amacı", "Hesaplama / Ölçüm Tanımı", "Veri Kaynağı", "Sıklık", "Hedef / Eşik", "Sorumlu", "İlgili BP / GP", "Durum"],
        [[t(x) for x in row] for row in metrics], view,
    ))

    parts.append("<h2>4. Veri Toplama ve Hesaplama Matrisi</h2>")
    collection = [
        ("SRÇ.004-Ö01", "Güncel süreç sayısı; zorunlu paket bileşenlerinin varlık ve gözden geçirme durumu", f"{LST006}, {LST001} ve ilgili süreç alt sayfaları", "Aylık liste ve sayfa kontrolü", "Tam paketli süreç / güncel süreç × 100", "Kalite Danışmanı / Süreç Mimarı", "Aylık ölçüm özeti ve kaynak sayfa bağlantıları"),
        ("SRÇ.004-Ö02", "Dönemde gözden geçirmesi gereken ve tamamlanan süreç sayıları", f"{LST001} ve ilgili FRM.001 kayıtları", "Üç aylık kayıt kontrolü", "Zamanında tamamlanan / gözden geçirmesi gereken × 100", "Süreç Sahibi / Kalite Danışmanı", "FRM.001 ve dönemsel ölçüm özeti"),
        ("SRÇ.004-Ö03", "Onay, yayın ve hedef kitle bilgilendirme tarihleri", f"Confluence, {LST001} ve {LST012}", "Her yayın sonrası tarih ve bağlantı kontrolü", "Beş iş günü içinde tamamlanan / onaylanan × 100", "Proje Yöneticisi / Yayımlayan", f"{LST012} kaydı ve Confluence sayfa geçmişi"),
    ]
    parts.append(table(
        ["Ölçüm ID", "Veri Alanı", "Veri Kaynağı", "Toplama Yöntemi", "Hesaplama Yöntemi", "Veri Sahibi", "Kayıt / Kanıt"],
        [[t(x) for x in row] for row in collection], view,
    ))

    parts.append("<h2>5. Hedef ve İzleme Matrisi</h2>")
    monitoring = [
        ("SRÇ.004-Ö01", "Hedef: %100 / Eşik: %90", "Aylık", "SRÇ.004 performans gözden geçirmesi", "İzleniyor", f"Eşik altındaki eksik paket bileşenleri {SRC018} kapsamında önceliklendirilir.", "İlk gerçek veri toplama döneminde sonuç oluşturulur."),
        ("SRÇ.004-Ö02", "Hedef: %100 / Eşik: %90", "Üç aylık", "SRÇ.004 performans gözden geçirmesi", "İzleniyor", f"Geciken gözden geçirmeler süreç sahibiyle planlanır; gerekli değişiklikler {SRC018} kapsamına aktarılır.", "Geçmişe dönük sonuç üretilmez."),
        ("SRÇ.004-Ö03", "Hedef: %100 / Eşik: %90", "Her yayın sonrası; aylık özet", "Yayın kontrolü ve SRÇ.004 performans gözden geçirmesi", "İzleniyor", "Geciken yayın veya bilgilendirme tamamlanır; tekrarın önlenmesi için sorumluluk ve yayın adımları gözden geçirilir.", "Yalnızca gerçek onay ve bilgilendirme kayıtları kullanılır."),
    ]
    parts.append(table(
        ["Ölçüm ID", "Hedef / Eşik", "İzleme Sıklığı", "Raporlama / Gözden Geçirme Yeri", "Sapma Durumu", "Tamamlayıcı Aksiyon Yaklaşımı", "Açıklama / Not"],
        [[t(x) for x in row] for row in monitoring], view,
    ))

    parts.append("<h2>6. Sürüm Geçmişi</h2>")
    parts.append(table(
        ["Sürüm", "Tarih", "Açıklama", "Hazırlayan/Güncelleyen", "Gözden Geçiren", "Onay"],
        [[t("v1.0"), t("15-02-2025"), t("Süreç Kurulumu Süreci performans ölçüm seti oluşturuldu."), t(PREPARED_BY), t(REVIEWED_BY), t(APPROVED_BY)]],
        view,
    ))
    return "".join(parts) + "\n"


def lst010_data(view: bool) -> str:
    parts: list[str] = ["<h2>1. Liste Özeti</h2>"]
    parts.append(table(["Alan", "Değer"], [
        [t("İlgili Süreç"), t(SRC004_TITLE)],
        [t("Liste Kapsamı"), t("Süreç Kurulumu Sürecinin rol, yetki, RACI, yetkinlik ve onay kapsamı")],
        [t("Liste Tarihi"), t("15-02-2025")],
        [t("Listeyi Hazırlayan"), t(PREPARED_BY)],
        [t("Listeyi Gözden Geçiren"), t(REVIEWED_BY)],
        [t("Listeyi Onaylayan"), t(APPROVED_BY)],
        [t("Genel Not"), t("RACI atamaları SRÇ.004 faaliyetleri ve süreç tasarım paketinin temel iş ürünleriyle sınırlıdır. Her sürecin kendi sahibi ayrıca doğrulanır.")],
    ], view))

    parts.append("<h2>2. Kullanım Değerleri</h2>")
    values = [
        ("R", "Responsible / Sorumlu: Faaliyeti veya iş ürününü fiilen gerçekleştiren rol."),
        ("A", "Accountable / Hesap Veren-Onaylayan: Sonuçtan nihai olarak sorumlu olan ve karar/onay veren rol."),
        ("C", "Consulted / Danışılan: Faaliyet veya iş ürünü için görüşü alınan rol."),
        ("I", "Informed / Bilgilendirilen: Faaliyet veya sonuç hakkında bilgilendirilen rol."),
        ("Yetkili", "İlgili karar, onay, yayın, değişiklik veya erişim işlemini yapma yetkisi bulunan rol."),
        ("Destek", "Faaliyetin yürütülmesine katkı sağlayan ancak ana sorumlu olmayan rol."),
        ("Kapsam Dışı", "İlgili rolün süreç faaliyeti veya iş ürünü bağlamında görevi yoktur."),
    ]
    parts.append(table(["Değer", "Anlamı"], [[t(a), t(b)] for a, b in values], view))

    parts.append("<h2>3. Rol ve Yetkinlik Matrisi</h2>")
    roles = [
        ("SRÇ.004 Süreç Sahibi", "Standart süreç setinin kurulması, sürdürülmesi ve kurumsal uygulanabilirliğinin gözetilmesi", "Süreç yönetimi, kurumsal karar ve onay yetkisi, ISO/IEC 15504-5 yaklaşımı hakkında yönetsel bilgi", "BİD Başkanı tarafından yetkilendirilen yönetici", f"Süreç sahibi: {APPROVED_BY}"),
        ("Kalite Danışmanı / Süreç Mimarı", "Süreç mimarisini, standart süreç tanımlarını, iş ürünlerini, ölçümleri ve uyarlama kurallarını tasarlamak", "ISO/IEC 15504-5, süreç modelleme, BP/PA/GP izlenebilirliği ve doküman şablonları", "Yetkilendirilmiş kalite veya süreç uzmanı", f"Hazırlayan: {PREPARED_BY}"),
        ("Proje Yöneticisi / Gözden Geçiren / Yayımlayan", "Tasarım paketini uygulanabilirlik bakımından gözden geçirmek; onaylı içeriğin yayın ve bilgilendirmesini koordine etmek", "Proje yönetimi, Confluence yayın akışı, paydaş iletişimi ve doküman kontrolü", "Yetkilendirilmiş proje yöneticisi", f"Gözden geçiren: {REVIEWED_BY}"),
        ("İlgili Süreç Sahibi", "Kendi sürecinin kapsamını, faaliyetlerini, iş ürünlerini, rolleri ve uygulama koşullarını doğrulamak", "İlgili iş alanı, operasyonel uygulama ve karar yetkisi", "İlgili birimde yetkilendirilmiş yönetici", "Her süreç çalışmasında ayrıca doğrulanır."),
        ("Ölçüm Sorumlusu", "Tanımlı veri kaynaklarından ölçüm verisini toplamak, hesaplamak ve sapmaları raporlamak", "Veri kaynağı bilgisi, temel analiz ve ölçüm hesaplama yetkinliği", "Süreç sahibi tarafından atanan veri sahibi", f"{LST009} içinde ölçüm bazında atanır."),
        ("Doküman Sorumlusu", "Kod, ad, sürüm, şablon, bağlantı ve repository bilgilerinin tutarlılığını sağlamak", f"{SRC001}, aktif şablonlar, Confluence ve repository yapısı", "Yetkilendirilmiş doküman yönetimi rolü", f"{LST001} ve {LST011} ile çalışır."),
        ("Repository / Sistem Yöneticisi", "Süreç varlıkları için gerekli erişim, yetkilendirme ve teknik çalışma ortamını sağlamak", "Confluence, Google Drive, Jira, Bitbucket, VPN ve kurumsal yetkilendirme", "Yetkilendirilmiş sistem yöneticisi", "Araç veya erişim ihtiyacında danışılır."),
        ("Eğitim Sorumlusu", f"Gerekli süreç eğitimi ve katılım kayıtlarını {SRC020} kapsamında yönetmek", "Eğitim planlama, katılım ve kayıt yönetimi", f"{SRC020} kapsamında yetkilendirilen rol", f"Yalnızca eğitim ihtiyacı oluştuğunda devreye girer; {SRC020} esas alınır."),
    ]
    parts.append(table(
        ["Rol", "Rolün Süreçteki Amacı", "Asgari Yetkinlik / Bilgi", "Vekil / Alternatif Rol", "Durum / Not"],
        [[t(x) for x in row] for row in roles], view,
    ))

    parts.append("<h2>4. Süreç Faaliyetleri RACI Matrisi</h2>")
    activities = [
        ("F1", "Süreç mimarisini tanımla", "Kalite Danışmanı / Süreç Mimarı", "SRÇ.004 Süreç Sahibi", "İlgili Süreç Sahipleri; Proje Yöneticisi", "Doküman Sorumlusu; Ölçüm Sorumlusu", f"{LST006} ve {LST007} güncellenir."),
        ("F2", "Süreçlerin kurumsal kullanımını destekle", "Proje Yöneticisi / Yayımlayan", "SRÇ.004 Süreç Sahibi", "Doküman Sorumlusu; Eğitim Sorumlusu; Repository / Sistem Yöneticisi", "Hedef Kitle; İlgili Süreç Sahipleri", f"Yayın ve bilgilendirme {LST001} ve {LST012} ile izlenir."),
        ("F3", "Standart süreçleri tanımla ve sürdür", "Kalite Danışmanı / Süreç Mimarı; İlgili Süreç Sahibi", "SRÇ.004 Süreç Sahibi", "Proje Yöneticisi; Doküman Sorumlusu", "Hedef Kitle", f"İlgili SRÇ süreç tanımı, {LST008}, {LST010} ve {FRM001} birlikte ele alınır."),
        ("F4", "Performans beklentilerini belirle", "Ölçüm Sorumlusu; Kalite Danışmanı / Süreç Mimarı", "SRÇ.004 Süreç Sahibi", "İlgili Süreç Sahibi", "Proje Yöneticisi", f"Az sayıda yönetilebilir ölçüm {LST009} içinde tanımlanır."),
        ("F5", "Süreç uyarlama kılavuzlarını oluştur", "Kalite Danışmanı / Süreç Mimarı", "SRÇ.004 Süreç Sahibi", "İlgili Süreç Sahipleri; Proje Yöneticisi", "Hedef Kitle", f"Uyarlama sınırları {KLV002} ile uyumlu olmalıdır."),
        ("F6", "Süreç kullanım verisini sürdür", "Ölçüm Sorumlusu; İlgili Süreç Sahibi", "SRÇ.004 Süreç Sahibi", "Kalite Danışmanı / Süreç Mimarı", "Proje Yöneticisi", "Veriler doğal kaynak sistemlerde tutulur; ayrı merkezi register oluşturulmaz."),
    ]
    parts.append(table(
        ["Faaliyet Kodu", "Süreç Faaliyeti", "Responsible", "Accountable", "Consulted", "Informed", "Açıklama / Not"],
        [[t(x) for x in row] for row in activities], view,
    ))

    parts.append("<h2>5. İş Ürünleri RACI Matrisi</h2>")
    products = [
        (LST006, "F1", "Kalite Danışmanı / Süreç Mimarı", "SRÇ.004 Süreç Sahibi", "İlgili Süreç Sahipleri", "Proje Yöneticisi", "Ortak kayıt; ilgili satırlar güncellenir."),
        (LST007, "F1", "Kalite Danışmanı / Süreç Mimarı", "SRÇ.004 Süreç Sahibi", "İlgili Süreç Sahipleri", "Proje Yöneticisi", "Ortak süreç etkileşim kaydıdır."),
        ("İlgili SRÇ süreç tanımı", "F3", "Kalite Danışmanı / Süreç Mimarı; İlgili Süreç Sahibi", "SRÇ.004 Süreç Sahibi", "Proje Yöneticisi; Doküman Sorumlusu", "Hedef Kitle", f"Aktif {SRC_TEMPLATE} yapısı kullanılır."),
        (LST008, "F3", "Kalite Danışmanı / Süreç Mimarı", "SRÇ.004 Süreç Sahibi", "İlgili Süreç Sahibi", "Proje Yöneticisi", "Girdi, çıktı ve kalite kriterlerini yönetir."),
        (LST009, "F4", "Ölçüm Sorumlusu; Kalite Danışmanı / Süreç Mimarı", "SRÇ.004 Süreç Sahibi", "İlgili Süreç Sahibi", "Proje Yöneticisi", "Yalnızca düzenli üretilebilen anlamlı ölçümler tutulur."),
        (LST010, "F3", "Kalite Danışmanı / Süreç Mimarı", "SRÇ.004 Süreç Sahibi", "İlgili Süreç Sahibi; Proje Yöneticisi", "Hedef Kitle", "Rol, yetki, RACI ve yetkinlik kaydıdır."),
        (KLV002, "F5", "Kalite Danışmanı / Süreç Mimarı", "SRÇ.004 Süreç Sahibi", "İlgili Süreç Sahipleri; Proje Yöneticisi", "Hedef Kitle", "Amaç ve zorunlu sonuçlar korunur."),
        (FRM001, "F3", "Kalite Danışmanı / Gözden Geçiren", "SRÇ.004 Süreç Sahibi", "Proje Yöneticisi; İlgili Süreç Sahibi", "Doküman Sorumlusu", "BP ve PA/GP kanıt durumu gerçek kayıtlara göre değerlendirilir."),
        (f"Onaylı süreç varlıkları ve {LST012}", "F2", "Proje Yöneticisi / Yayımlayan", "SRÇ.004 Süreç Sahibi", "Doküman Sorumlusu; Repository / Sistem Yöneticisi", "Hedef Kitle", "Yalnızca onaylı sürüm yayımlanır."),
        ("Süreç kullanım ve performans kayıtları", "F6", "Ölçüm Sorumlusu; İlgili Süreç Sahibi", "SRÇ.004 Süreç Sahibi", "Kalite Danışmanı / Süreç Mimarı", "Proje Yöneticisi", "Doğal kaynak sistemler esas alınır."),
    ]
    parts.append(table(
        ["İş Ürünü", "İlgili Faaliyet", "Responsible", "Accountable", "Consulted", "Informed", "Açıklama / Not"],
        [[t(x) for x in row] for row in products], view,
    ))

    parts.append("<h2>6. Yetki ve Onay Matrisi</h2>")
    authority = [
        ("Standart süreç mimarisini ve kapsamını onaylama", "SRÇ.004 Süreç Sahibi", "Evet", "Bilgi İşlem Daire Başkanı", f"{LST006}, {LST007} ve onay kaydı", f"Değişiklik ihtiyacı {SRC018} kapsamında yönetilir."),
        ("Süreç tasarım paketini onaylama", "SRÇ.004 Süreç Sahibi", "Evet", "Bilgi İşlem Daire Başkanı", f"İlgili SRÇ süreç tanımı, {LST008}, {LST009}, {LST010} ve {FRM001}", "İlgili süreç sahibinin görüşü alınır."),
        ("Süreç uyarlama veya zorunlu kontrol sapmasını onaylama", "SRÇ.004 Süreç Sahibi", "Evet", "Bilgi İşlem Daire Başkanı", f"{KLV002} ve uyarlama kararı", "Süreç amacı ve zorunlu sonuçlar kaldırılamaz."),
        ("Onaylı dokümanı yayımlama ve duyurma", "Proje Yöneticisi / Yayımlayan", "Koşullu", "Bilgi İşlem Daire Başkanı", f"Onay kaydı, {LST001} ve {LST012}", "Yayın yetkisi yalnızca onaylı sürüm için kullanılır."),
        ("Ölçüm setini veya hedef/eşiği değiştirme", "SRÇ.004 Süreç Sahibi / Ölçüm Sorumlusu", "Evet", "SRÇ.004 Süreç Sahibi", f"{LST009} ve {SRC018} kapsamındaki karar", "Düzenli üretilemeyen ölçüm eklenmez."),
        ("Repository erişim ve yetkisini tanımlama", "Repository / Sistem Yöneticisi", "Koşullu", "SRÇ.004 Süreç Sahibi", f"Erişim kaydı ve {LST011}", "Kurumsal yetkilendirme ve VPN kuralları uygulanır."),
    ]
    parts.append(table(
        ["Yetki / Karar Alanı", "Yetkili Rol", "Onay Gerektirir mi?", "Onaylayan Rol", "Kayıt / Kanıt", "Açıklama / Not"],
        [[t(x) for x in row] for row in authority], view,
    ))

    parts.append("<h2>7. Sürüm Geçmişi</h2>")
    parts.append(table(
        ["Sürüm", "Tarih", "Açıklama", "Hazırlayan/Güncelleyen", "Gözden Geçiren", "Onay"],
        [[t("v1.0"), t("15-02-2025"), t("Süreç Kurulumu Süreci rol, yetki ve RACI matrisi oluşturuldu."), t(PREPARED_BY), t(REVIEWED_BY), t(APPROVED_BY)]],
        view,
    ))
    return "".join(parts) + "\n"


def frm001_data(view: bool) -> str:
    parts: list[str] = ["<h2>1. Değerlendirme Özeti</h2>"]
    parts.append(table(["Alan", "Değer"], [
        [t("Değerlendirilen Süreç"), t(SRC004_TITLE)],
        [t("Süreç Referansı"), t("ISO/IEC 15504-5:2006 PIM.1 - Process establishment")],
        [t("Süreç Durumu"), t("Taslak")],
        [t("Süreç Sürümü"), t("v1.0")],
        [t("Değerlendirme Kapsamı"), t("PIM.1.BP1-BP6; PA 2.1, PA 2.2, PA 3.1 ve PA 3.2 genel uygulamaları")],
        [t("Değerlendirme Tarihi"), t("14-07-2026")],
        [t("Değerlendirmeyi Yapan"), t(PREPARED_BY)],
        [t("Değerlendirmeyi Onaylayan"), t(APPROVED_BY)],
        [t("Değerlendirme Sonucu"), t(f"{SRC004_TITLE} tasarım paketi yerel olarak güncel şablonlara göre yeniden oluşturulmaktadır. Tanım, iş ürünü, ölçüm ve RACI yapıları mevcut olmakla birlikte; {LST007}, {KLV002} ve {KLV003} uyumu, onaylı Confluence yayını, gerçek yaygınlaştırma kaydı ve ilk performans/kullanım kanıtları henüz tamamlanmamıştır.")],
    ], view))

    parts.append("<h2>2. Durum Değerleri</h2>")
    statuses = [
        ("VAR", "Beklenti mevcut doküman/kayıt setiyle büyük ölçüde karşılanıyor."),
        ("ZAYIF", "Temel yapı var; ancak uygulama kaydı, onay, ölçüm, kapanış veya izlenebilirlik güçlendirilmeli."),
        ("DAĞINIK", "Bilgi birden fazla yerde var; tekil ve tutarlı izlenebilirlik güçlendirilmeli."),
        ("YOK", "Beklentiyi karşılayan yeterli kayıt veya tanım henüz yok."),
        ("KAPSAM DIŞI", "Bu değerlendirme bağlamında uygulanmıyor."),
    ]
    parts.append(table(["Durum", "Anlamı"], [[t(a), t(b)] for a, b in statuses], view))

    parts.append("<h2>3. BP Takip Matrisi</h2>")
    bp_rows = [
        ("PIM.1.BP1", "Süreç mimarisini tanımlama", f"Süreç seti ve etkileşim yaklaşımı tanımlıdır; ortak etkileşim matrisi aktif şablon adı ve yapısıyla ayrıca doğrulanmalıdır.", f"{SRC004_TITLE}; {LST006}; {LST007}", "ZAYIF", f"{LST007} aktif şablona göre gözden geçirilmeli ve karşılıklı etkileşimler doğrulanmalıdır."),
        ("PIM.1.BP2", "Süreçlerin kurumsal kullanımını destekleme", "Yayın, e-posta bilgilendirmesi ve gerektiğinde eğitim yaklaşımı tanımlıdır; bu yerel revizyon için gerçek yayın ve duyuru henüz yapılmamıştır.", f"{SRC004_TITLE}; {LST012}; {SRC020}", "ZAYIF", f"Onay sonrası Confluence yayını yapılmalı ve gerçek bilgilendirme kaydı {LST012} içine eklenmelidir."),
        ("PIM.1.BP3", "Standart süreçleri tanımlama ve sürdürme", "Aktif SRÇ yapısı ve süreç özel LST/FRM paketi uygulanmaktadır; paket henüz onaylı olarak yayımlanmamıştır.", f"{SRC004_TITLE}; {PRS002}; {LST008}; {LST010}; {FRM001}", "ZAYIF", "Süreç tasarım paketi gözden geçirilmeli, onaylanmalı ve tekil sayfa yapısıyla yayımlanmalıdır."),
        ("PIM.1.BP4", "Standart süreçlerin performans beklentilerini belirleme", "Az sayıda ve yönetilebilir üç ölçüm; veri kaynağı, hesaplama, hedef/eşik, sıklık ve sorumlularıyla tanımlanmıştır. Sonuç verisi henüz yoktur.", LST009, "ZAYIF", "İlk gerçek ölçüm döneminde veriler toplanmalı, sonuçlar gözden geçirilmeli ve sapmalar izlenmelidir."),
        ("PIM.1.BP5", "Süreç uyarlama kılavuzlarını oluşturma", "Amaç ve zorunlu sonuçları koruyan uyarlama yaklaşımı tanımlıdır; kılavuzun aktif şablon ve süreç paketiyle uyumu yeniden doğrulanmalıdır.", f"{SRC004_TITLE}; {KLV002}; {PRS002}", "ZAYIF", f"{KLV002}, aktif kılavuz şablonu ve {SRC018} değişiklik yolu ile tutarlılık bakımından gözden geçirilmelidir."),
        ("PIM.1.BP6", "Standart süreçlerin belirli bağlamlardaki kullanım verisini sürdürme", "Verilerin doğal kaynak sistemlerde tutulması ilkesi tanımlıdır; SRÇ.004 için ilk kullanım ve performans verileri henüz toplanmamıştır.", f"{SRC004_TITLE}; {LST009}; ilgili doğal kaynak sistem kayıtları", "YOK", "Onaylı kullanım başladıktan sonra ilk veri dönemi işletilmeli; analiz sonucu süreç değerlendirme ve iyileştirme faaliyetlerine aktarılmalıdır."),
    ]
    parts.append(table(
        ["BP", "Standart Beklentisi", "Mevcut Karşılama", "Karşılayan Doküman / Kayıt", "Durum", "Eksik / Tamamlayıcı Aksiyon"],
        [[t(x) for x in row] for row in bp_rows], view,
    ))

    parts.append("<h2>4. PA / GP Takip Matrisi</h2>")
    pa_rows = [
        ("PA 2.1", "GP.2.1.1", "Süreç performansı için hedefleri belirleme", "Üç performans ölçümü için hedef ve eşikler tanımlı; gerçek sonuç yoktur.", LST009, "ZAYIF", "İlk ölçüm dönemi işletilmelidir."),
        ("PA 2.1", "GP.2.1.2", "Tanımlanan hedefleri karşılamak için süreç performansını planlama ve izleme", "Sıklık, veri kaynağı ve gözden geçirme yeri tanımlı; izleme kaydı henüz oluşmamıştır.", LST009, "ZAYIF", "Ölçüm takvimi işletilmeli ve dönemsel özet saklanmalıdır."),
        ("PA 2.1", "GP.2.1.3", "Süreç performansını ayarlama", "Sapma aksiyonu yaklaşımı tanımlı; gerçek sapma ve ayarlama kaydı yoktur.", f"{LST009}; {SRC018}", "YOK", "İlk sapma oluştuğunda gerçek aksiyon ve karar izlenmelidir."),
        ("PA 2.1", "GP.2.1.4", "Süreci gerçekleştirmek için sorumluluk ve yetkileri tanımlama", "Faaliyet, iş ürünü ve karar alanı bazında RACI ve yetkiler tanımlanmıştır.", LST010, "VAR", "Onay sonrası rol atamaları hedef kitleye duyurulmalıdır."),
        ("PA 2.1", "GP.2.1.5", "Süreci plana göre gerçekleştirmek için kaynakları belirleme ve kullanıma sunma", "Araç ve altyapı bileşenleri tanımlı; erişim ve kullanıma sunma kanıtları henüz paketle ilişkilendirilmemiştir.", f"{SRC004_TITLE}; {LST010}; {LST011}", "ZAYIF", "Gerekli erişim ve yetkilendirme kayıtları doğrulanmalıdır."),
        ("PA 2.1", "GP.2.1.6", "İlgili taraflar arasındaki arayüzleri yönetme", "İlgili süreçler ve RACI arayüzleri tanımlı; ortak etkileşim matrisi güncel ad/yapıyla doğrulanmalıdır.", f"{LST007}; {LST010}", "ZAYIF", "Karşılıklı etkileşim ve sorumluluklar gözden geçirilmelidir."),
        ("PA 2.2", "GP.2.2.1", "İş ürünleri için gereksinimleri tanımlama", "Girdi, çıktı, zorunluluk ve kalite kriterleri tanımlanmıştır.", LST008, "VAR", "Onay öncesi iş ürünü listesi süreç sahibiyle doğrulanmalıdır."),
        ("PA 2.2", "GP.2.2.2", "İş ürünlerinin dokümantasyonu ve kontrolü için gereksinimleri tanımlama", "Aktif şablon, repository ve doküman kontrol kuralları tanımlı; yerel paket henüz onaylı yayında değildir.", f"{LST008}; {LST011}; {SRC001}", "ZAYIF", "Yayın öncesi şablon ve repository kontrolü tamamlanmalıdır."),
        ("PA 2.2", "GP.2.2.3", "İş ürünlerini belirleme, dokümante etme ve kontrol etme", "Süreç paketi yerelde oluşturulmuş ve kontrol edilebilir durumdadır; onaylı Confluence sürümü henüz yoktur.", f"{SRC004_TITLE}; {LST008}; {LST009}; {LST010}; {FRM001}", "ZAYIF", "Gözden geçirme, onay ve kontrollü yayın tamamlanmalıdır."),
        ("PA 2.2", "GP.2.2.4", "İş ürünlerini tanımlı gereksinimleri karşılayacak şekilde gözden geçirme ve düzenleme", "Yerel şablon ve yapı kontrolleri yapılmıştır; yetkili gözden geçirme ve onay kaydı henüz oluşmamıştır.", f"{KLV003}; {FRM001}", "YOK", "Levent Bayezit gözden geçirmesi ve Mustafa Nusret SARISAKAL onayı kaydedilmelidir."),
        ("PA 3.1", "GP.3.1.1", "Tanımlı sürecin uygulanmasını destekleyecek standart süreci tanımlama", "SRÇ.004 ve süreç tasarım prosedürü yerel taslak olarak tanımlıdır.", f"{SRC004_TITLE}; {PRS002}", "ZAYIF", "Taslaklar onaylanıp kurumsal yayına alınmalıdır."),
        ("PA 3.1", "GP.3.1.2", "Süreçlerin bütünleşik bir sistem olarak çalışması için sıra ve etkileşimleri belirleme", "Süreç etkileşim yaklaşımı tanımlı; ortak matriste güncel şablon ve çift yönlü tutarlılık kontrolü gereklidir.", LST007, "ZAYIF", f"{LST007} aktif şablona göre tamamlanmalıdır."),
        ("PA 3.1", "GP.3.1.3", "Standart süreci gerçekleştirmek için rol ve yetkinlikleri belirleme", "Rol amaçları, asgari yetkinlikler, vekiller ve RACI tanımlanmıştır.", LST010, "ZAYIF", "Yetkili onay ve rol duyurusu tamamlanmalıdır."),
        ("PA 3.1", "GP.3.1.4", "Standart sürecin gerçekleştirilmesi için gerekli altyapı ve çalışma ortamını belirleme", "Confluence, Google Drive, Jira, Bitbucket, VPN ve erişim koşulları tanımlanmıştır.", SRC004_TITLE, "VAR", "Erişim kanıtları gerektiğinde doğal kaynak sistemden gösterilmelidir."),
        ("PA 3.1", "GP.3.1.5", "Standart sürecin etkinliğini ve uygunluğunu izlemek için yöntemleri belirleme", "Üç ölçüm ve sapma yaklaşımı tanımlı; sonuç verisi yoktur.", LST009, "ZAYIF", "İlk ölçüm dönemi işletilmelidir."),
        ("PA 3.2", "GP.3.2.1", "Kullanım bağlamı gereksinimlerini karşılayan tanımlı süreci uygulamaya alma", "Yerel tasarım paketi oluşturulmuş ancak onaylı kurumsal uygulamaya alma tamamlanmamıştır.", f"{SRC004_TITLE}; {PRS002}", "YOK", "Onay, Confluence yayını ve hedef kitle bilgilendirmesi tamamlanmalıdır."),
        ("PA 3.2", "GP.3.2.2", "Tanımlı süreci gerçekleştirmek için rol, sorumluluk ve yetkileri atama ve duyurma", "RACI tanımlı; resmî duyuru henüz yapılmamıştır.", f"{LST010}; {LST012}", "ZAYIF", "Onaylanan rol ve sorumluluklar hedef kitleye duyurulmalıdır."),
        ("PA 3.2", "GP.3.2.3", "Tanımlı süreci gerçekleştirmek için gerekli yetkinlikleri sağlama", "Asgari yetkinlikler tanımlı; bu revizyon için ihtiyaç analizi ve eğitim/katılım kaydı yoktur.", f"{LST010}; {SRC020}", "YOK", f"Yetkinlik ihtiyacı değerlendirilmeli; gerekiyorsa {SRC020} kapsamında gerçek kayıt oluşturulmalıdır."),
        ("PA 3.2", "GP.3.2.4", "Tanımlı sürecin performansını desteklemek için kaynak ve bilgi sağlama", "Gerekli doküman ve bilgi kaynakları tanımlı; kullanıma sunma doğrulaması beklenmektedir.", f"{LST008}; {LST010}; {LST011}", "ZAYIF", "Yayın ve erişim kontrolleri tamamlanmalıdır."),
        ("PA 3.2", "GP.3.2.5", "Sürecin performansını desteklemek için yeterli süreç altyapısı sağlama", "Altyapı bileşenleri ve sorumluları tanımlı; gerçek erişim/yetkilendirme kanıtı paketle ilişkilendirilmemiştir.", f"{SRC004_TITLE}; {LST011}", "ZAYIF", "Erişim ve yetkilendirme doğrulaması yapılmalıdır."),
        ("PA 3.2", "GP.3.2.6", "Sürecin uygunluğunu ve etkinliğini göstermek için performans verilerini toplama ve analiz etme", "Veri toplama ve hesaplama yöntemi tanımlı; henüz gerçek performans verisi ve analiz sonucu yoktur.", LST009, "YOK", "İlk ölçüm sonuçları toplanmalı, analiz edilmeli ve gözden geçirme kaydına bağlanmalıdır."),
    ]
    parts.append(table(
        ["PA", "GP", "Standart Beklentisi", "Mevcut Karşılama", "Karşılayan Doküman / Kayıt", "Durum", "Eksik / Tamamlayıcı Aksiyon"],
        [[t(x) for x in row] for row in pa_rows], view,
    ))

    parts.append("<h2>5. Öncelikli Tamamlama Listesi</h2>")
    priorities = [
        ("1", f"{LST007}, {KLV002} ve {KLV003} dokümanlarını aktif şablon adı/yapısı ve SRÇ.004 tasarım paketiyle uyumlu hale getirmek", "PIM.1.BP1; PIM.1.BP5; GP.3.1.2", "SRÇ.004 onayı öncesi"),
        ("2", "SRÇ.004 süreç tasarım paketinin yetkili gözden geçirme ve onay kayıtlarını tamamlamak", "GP.2.2.3; GP.2.2.4; GP.3.2.1", "Confluence yayını öncesi"),
        ("3", f"Onaylı paketi Confluence'da yayımlamak ve gerçek hedef kitle bilgilendirmesini {LST012} içinde kaydetmek", "PIM.1.BP2; GP.3.2.2", "Onay sonrası beş iş günü içinde"),
        ("4", f"{LST009} için ilk gerçek veri toplama dönemini işletmek ve sonuçları gözden geçirmek", "PIM.1.BP4; PIM.1.BP6; GP.3.2.6", "İlk ölçüm dönemi sonunda"),
        ("5", "Rol duyurusu, yetkinlik ihtiyacı ve gerekli erişim/yetkilendirme kanıtlarını gerçek kaynak sistemlerde doğrulamak", "GP.3.2.2; GP.3.2.3; GP.3.2.5", "Kurumsal kullanım başlamadan önce"),
    ]
    parts.append(table(
        ["Öncelik", "Aksiyon", "İlgili BP / GP", "Hedef Kapanış"],
        [[t(x) for x in row] for row in priorities], view,
    ))
    return "".join(parts) + "\n"


def frm001_blank_data(view: bool) -> str:
    """Build the reusable empty process-specific form kept under SRÇ.004."""
    parts: list[str] = ["<h2>1. Değerlendirme Özeti</h2>"]
    parts.append(table(["Alan", "Değer"], [
        [t("Değerlendirilen Süreç"), t(SRC004_TITLE)],
        [t("Süreç Referansı"), t("ISO/IEC 15504-5:2006 PIM.1 - Process establishment")],
        [t("Süreç Durumu"), t("Aktif")],
        [t("Süreç Sürümü"), t("v1.0")],
        [t("Değerlendirme Kapsamı"), t("PIM.1.BP1-BP6; PA 2.1, PA 2.2, PA 3.1 ve PA 3.2 genel uygulamaları")],
        [t("Değerlendirme Tarihi"), t("GG-AA-YYYY")],
        [t("Değerlendirmeyi Yapan"), t("ROL / KİŞİ")],
        [t("Değerlendirmeyi Onaylayan"), t("ROL / KİŞİ")],
        [t("Değerlendirme Sonucu"), t("ÖZET SONUÇ")],
    ], view))

    parts.append("<h2>2. Durum Değerleri</h2>")
    statuses = [
        ("VAR", "Beklenti mevcut doküman/kayıt setiyle büyük ölçüde karşılanıyor."),
        ("ZAYIF", "Temel yapı var; ancak uygulama kaydı, onay, ölçüm, kapanış veya izlenebilirlik güçlendirilmeli."),
        ("DAĞINIK", "Bilgi birden fazla yerde var; tekil ve tutarlı izlenebilirlik güçlendirilmeli."),
        ("YOK", "Beklentiyi karşılayan yeterli kayıt veya tanım henüz yok."),
        ("KAPSAM DIŞI", "Bu değerlendirme bağlamında uygulanmıyor."),
    ]
    parts.append(table(["Durum", "Anlamı"], [[t(a), t(b)] for a, b in statuses], view))

    parts.append("<h2>3. BP Takip Matrisi</h2>")
    bp_expectations = [
        ("PIM.1.BP1", "Süreç mimarisini tanımlama"),
        ("PIM.1.BP2", "Süreçlerin kurumsal kullanımını destekleme"),
        ("PIM.1.BP3", "Standart süreçleri tanımlama ve sürdürme"),
        ("PIM.1.BP4", "Standart süreçlerin performans beklentilerini belirleme"),
        ("PIM.1.BP5", "Süreç uyarlama kılavuzlarını oluşturma"),
        ("PIM.1.BP6", "Standart süreçlerin belirli bağlamlardaki kullanım verisini sürdürme"),
    ]
    parts.append(table(
        ["BP", "Standart Beklentisi", "Mevcut Karşılama", "Karşılayan Doküman / Kayıt", "Durum", "Eksik / Tamamlayıcı Aksiyon"],
        [[t(bp), t(expectation), "", "", "", ""] for bp, expectation in bp_expectations],
        view,
    ))

    parts.append("<h2>4. PA / GP Takip Matrisi</h2>")
    pa_expectations = [
        ("PA 2.1", "GP.2.1.1", "Süreç performansı için hedefleri belirleme"),
        ("PA 2.1", "GP.2.1.2", "Tanımlanan hedefleri karşılamak için süreç performansını planlama ve izleme"),
        ("PA 2.1", "GP.2.1.3", "Süreç performansını ayarlama"),
        ("PA 2.1", "GP.2.1.4", "Süreci gerçekleştirmek için sorumluluk ve yetkileri tanımlama"),
        ("PA 2.1", "GP.2.1.5", "Süreci plana göre gerçekleştirmek için kaynakları belirleme ve kullanıma sunma"),
        ("PA 2.1", "GP.2.1.6", "İlgili taraflar arasındaki arayüzleri yönetme"),
        ("PA 2.2", "GP.2.2.1", "İş ürünleri için gereksinimleri tanımlama"),
        ("PA 2.2", "GP.2.2.2", "İş ürünlerinin dokümantasyonu ve kontrolü için gereksinimleri tanımlama"),
        ("PA 2.2", "GP.2.2.3", "İş ürünlerini belirleme, dokümante etme ve kontrol etme"),
        ("PA 2.2", "GP.2.2.4", "İş ürünlerini tanımlı gereksinimleri karşılayacak şekilde gözden geçirme ve düzenleme"),
        ("PA 3.1", "GP.3.1.1", "Tanımlı sürecin uygulanmasını destekleyecek standart süreci tanımlama"),
        ("PA 3.1", "GP.3.1.2", "Süreçlerin bütünleşik bir sistem olarak çalışması için sıra ve etkileşimleri belirleme"),
        ("PA 3.1", "GP.3.1.3", "Standart süreci gerçekleştirmek için rol ve yetkinlikleri belirleme"),
        ("PA 3.1", "GP.3.1.4", "Standart sürecin gerçekleştirilmesi için gerekli altyapı ve çalışma ortamını belirleme"),
        ("PA 3.1", "GP.3.1.5", "Standart sürecin etkinliğini ve uygunluğunu izlemek için yöntemleri belirleme"),
        ("PA 3.2", "GP.3.2.1", "Kullanım bağlamı gereksinimlerini karşılayan tanımlı süreci uygulamaya alma"),
        ("PA 3.2", "GP.3.2.2", "Tanımlı süreci gerçekleştirmek için rol, sorumluluk ve yetkileri atama ve duyurma"),
        ("PA 3.2", "GP.3.2.3", "Tanımlı süreci gerçekleştirmek için gerekli yetkinlikleri sağlama"),
        ("PA 3.2", "GP.3.2.4", "Tanımlı sürecin performansını desteklemek için kaynak ve bilgi sağlama"),
        ("PA 3.2", "GP.3.2.5", "Sürecin performansını desteklemek için yeterli süreç altyapısı sağlama"),
        ("PA 3.2", "GP.3.2.6", "Sürecin uygunluğunu ve etkinliğini göstermek için performans verilerini toplama ve analiz etme"),
    ]
    parts.append(table(
        ["PA", "GP", "Standart Beklentisi", "Mevcut Karşılama", "Karşılayan Doküman / Kayıt", "Durum", "Eksik / Tamamlayıcı Aksiyon"],
        [[t(pa), t(gp), t(expectation), "", "", "", ""] for pa, gp, expectation in pa_expectations],
        view,
    ))

    parts.append("<h2>5. Öncelikli Tamamlama Listesi</h2>")
    parts.append(table(
        ["Öncelik", "Aksiyon", "İlgili BP / GP", "Hedef Kapanış"],
        [["", "", "", ""] for _ in range(4)],
        view,
    ))
    return "".join(parts) + "\n"


def migrate_and_update_index() -> None:
    index = yaml.safe_load(INDEX_PATH.read_text(encoding="utf-8")) or {}
    pages = index.get("pages") or []

    for doc in DOCS.values():
        old_dir = ROOT / "confluence" / doc["old_rel"]
        new_dir = ROOT / "confluence" / doc["new_rel"]
        if old_dir != new_dir and old_dir.exists() and new_dir.exists():
            raise RuntimeError(f"Doküman hem eski hem yeni konumda bulunuyor: {doc['title']}")
        if old_dir != new_dir and old_dir.exists():
            new_dir.parent.mkdir(parents=True, exist_ok=True)
            old_dir.rename(new_dir)
        if not new_dir.exists():
            raise RuntimeError(f"Doküman dizini bulunamadı: {new_dir}")

        metadata_path = new_dir / "page.yaml"
        metadata = yaml.safe_load(metadata_path.read_text(encoding="utf-8")) or {}
        metadata.update({
            "title": doc["title"],
            "parent_id": SRC004_ID,
            "parent_title": SRC004_TITLE,
            "depth": 3,
            "relative_path": doc["new_rel"],
        })
        metadata_path.write_text(
            yaml.safe_dump(metadata, allow_unicode=True, sort_keys=False), encoding="utf-8"
        )

        matches = [page for page in pages if str(page.get("page_id")) == doc["page_id"]]
        if len(matches) != 1:
            raise RuntimeError(f"Confluence indeksinde tek kayıt bekleniyordu: {doc['title']}; bulunan={len(matches)}")
        matches[0].update({
            "title": doc["title"],
            "parent_id": SRC004_ID,
            "depth": 3,
            "relative_path": doc["new_rel"],
            "storage_file": f"{doc['new_rel']}/body.storage.xhtml",
            "view_file": f"{doc['new_rel']}/body.view.html",
        })

    INDEX_PATH.write_text(
        yaml.safe_dump(index, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )


def write_document(key: str, body_builder: Any) -> None:
    doc = DOCS[key]
    page_dir = ROOT / "confluence" / doc["new_rel"]
    storage = body_builder(view=False)
    validate_document(key, storage)
    view_body = body_builder(view=True)
    (page_dir / "body.storage.xhtml").write_text(storage, encoding="utf-8")
    (page_dir / "body.view.html").write_text(
        build_view(doc["title"], view_body), encoding="utf-8"
    )


def write_assessment() -> None:
    """Write the filled first assessment under 91 / Süreç Gözden Geçirmeleri."""
    page_dir = ROOT / "confluence" / FRM001_ASSESSMENT_REL
    page_dir.mkdir(parents=True, exist_ok=True)
    metadata_path = page_dir / "page.yaml"
    existing_metadata = (
        yaml.safe_load(metadata_path.read_text(encoding="utf-8")) or {}
        if metadata_path.exists()
        else {}
    )

    storage = frm001_data(view=False)
    validate_assessment(storage)
    view_body = frm001_data(view=True)
    (page_dir / "body.storage.xhtml").write_text(storage, encoding="utf-8")
    (page_dir / "body.view.html").write_text(
        build_view(FRM001_ASSESSMENT_TITLE, view_body), encoding="utf-8"
    )

    metadata = {
        "page_id": str(existing_metadata.get("page_id") or ""),
        "space": "SSSS",
        "title": FRM001_ASSESSMENT_TITLE,
        "parent_id": REVIEW_PARENT_ID,
        "parent_title": REVIEW_PARENT_TITLE,
        "version": existing_metadata.get("version") or "",
        "url": existing_metadata.get("url") or "",
        "depth": 3,
        "status": "active",
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "children_count": 0,
        "relative_path": FRM001_ASSESSMENT_REL,
        "slug": FRM001_ASSESSMENT_SLUG,
        "has_view_html": True,
        "view_file": "body.view.html",
        "storage_file": "body.storage.xhtml",
    }
    metadata_path.write_text(
        yaml.safe_dump(metadata, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )

    index = yaml.safe_load(INDEX_PATH.read_text(encoding="utf-8")) or {}
    pages = index.setdefault("pages", [])
    pages[:] = [
        page for page in pages
        if page.get("relative_path") != FRM001_ASSESSMENT_REL
        and page.get("title") != FRM001_ASSESSMENT_TITLE
    ]
    pages.append({
        "page_id": metadata["page_id"],
        "title": FRM001_ASSESSMENT_TITLE,
        "parent_id": REVIEW_PARENT_ID,
        "depth": 3,
        "relative_path": FRM001_ASSESSMENT_REL,
        "slug": FRM001_ASSESSMENT_SLUG,
        "storage_file": f"{FRM001_ASSESSMENT_REL}/body.storage.xhtml",
        "view_file": f"{FRM001_ASSESSMENT_REL}/body.view.html",
    })
    index["total_page_count"] = len(pages)
    INDEX_PATH.write_text(
        yaml.safe_dump(index, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )


def extract_headers(storage: str) -> list[list[str]]:
    import xml.etree.ElementTree as ET

    root = ET.fromstring(f"<root>{storage}</root>")
    return [
        ["".join(th.itertext()) for th in table_node.findall("./thead/tr/th")]
        for table_node in root.findall(".//table")
    ]


def validate_document(key: str, storage: str) -> None:
    expected: dict[str, list[list[str]]] = {
        "lst009": [
            ["Alan", "Değer"],
            ["Değer", "Anlamı"],
            ["Ölçüm ID", "Ölçüm Adı", "Ölçüm Amacı", "Hesaplama / Ölçüm Tanımı", "Veri Kaynağı", "Sıklık", "Hedef / Eşik", "Sorumlu", "İlgili BP / GP", "Durum"],
            ["Ölçüm ID", "Veri Alanı", "Veri Kaynağı", "Toplama Yöntemi", "Hesaplama Yöntemi", "Veri Sahibi", "Kayıt / Kanıt"],
            ["Ölçüm ID", "Hedef / Eşik", "İzleme Sıklığı", "Raporlama / Gözden Geçirme Yeri", "Sapma Durumu", "Tamamlayıcı Aksiyon Yaklaşımı", "Açıklama / Not"],
            ["Sürüm", "Tarih", "Açıklama", "Hazırlayan/Güncelleyen", "Gözden Geçiren", "Onay"],
        ],
        "lst010": [
            ["Alan", "Değer"],
            ["Değer", "Anlamı"],
            ["Rol", "Rolün Süreçteki Amacı", "Asgari Yetkinlik / Bilgi", "Vekil / Alternatif Rol", "Durum / Not"],
            ["Faaliyet Kodu", "Süreç Faaliyeti", "Responsible", "Accountable", "Consulted", "Informed", "Açıklama / Not"],
            ["İş Ürünü", "İlgili Faaliyet", "Responsible", "Accountable", "Consulted", "Informed", "Açıklama / Not"],
            ["Yetki / Karar Alanı", "Yetkili Rol", "Onay Gerektirir mi?", "Onaylayan Rol", "Kayıt / Kanıt", "Açıklama / Not"],
            ["Sürüm", "Tarih", "Açıklama", "Hazırlayan/Güncelleyen", "Gözden Geçiren", "Onay"],
        ],
        "frm001": [
            ["Alan", "Değer"],
            ["Durum", "Anlamı"],
            ["BP", "Standart Beklentisi", "Mevcut Karşılama", "Karşılayan Doküman / Kayıt", "Durum", "Eksik / Tamamlayıcı Aksiyon"],
            ["PA", "GP", "Standart Beklentisi", "Mevcut Karşılama", "Karşılayan Doküman / Kayıt", "Durum", "Eksik / Tamamlayıcı Aksiyon"],
            ["Öncelik", "Aksiyon", "İlgili BP / GP", "Hedef Kapanış"],
        ],
    }
    actual = extract_headers(storage)
    if actual != expected[key]:
        raise RuntimeError(f"{key} aktif şablon tablo yapısıyla uyuşmuyor: {actual}")

    forbidden = [
        "ŞBL.014", "ŞBL.015", "Süreç Mimari ve Etkileşim Matrisi",
        "LST.004", "FRM.002", "26 süreç", "26 sürec", "Daha sonra",
        "&lt;Rol", "&lt;Onay", "30.09.2025", "15.10.2025", "31.10.2025",
    ]
    for phrase in forbidden:
        if phrase in storage:
            raise RuntimeError(f"{key} içinde eski, sabit veya yer tutucu ifade bulundu: {phrase}")

    if key == "lst009":
        if storage.count("SRÇ.004-Ö01</td>") != 3:
            raise RuntimeError("LST.009 Ö01 satırları beklenen üç matriste bulunamadı")
        if "SRÇ.004-Ö04" in storage:
            raise RuntimeError("LST.009 yönetilebilir üç ölçüm sınırını aştı")
    if key == "lst010":
        for activity in ("F1", "F2", "F3", "F4", "F5", "F6"):
            if f">{activity}</td>" not in storage:
                raise RuntimeError(f"LST.010 içinde faaliyet eksik: {activity}")
    if key == "frm001":
        for bp in range(1, 7):
            if f"PIM.1.BP{bp}" not in storage:
                raise RuntimeError(f"FRM.001 içinde BP eksik: PIM.1.BP{bp}")
        for placeholder in ("GG-AA-YYYY", "ROL / KİŞİ", "ÖZET SONUÇ"):
            if placeholder not in storage:
                raise RuntimeError(f"Boş FRM.001 içinde yer tutucu eksik: {placeholder}")
        if "14-07-2026" in storage or "İlk gerçek ölçüm dönemi" in storage:
            raise RuntimeError("Süreç altındaki FRM.001 değerlendirme kaydı içeriyor; boş olmalıdır")


def validate_assessment(storage: str) -> None:
    expected_headers = [
        ["Alan", "Değer"],
        ["Durum", "Anlamı"],
        ["BP", "Standart Beklentisi", "Mevcut Karşılama", "Karşılayan Doküman / Kayıt", "Durum", "Eksik / Tamamlayıcı Aksiyon"],
        ["PA", "GP", "Standart Beklentisi", "Mevcut Karşılama", "Karşılayan Doküman / Kayıt", "Durum", "Eksik / Tamamlayıcı Aksiyon"],
        ["Öncelik", "Aksiyon", "İlgili BP / GP", "Hedef Kapanış"],
    ]
    if extract_headers(storage) != expected_headers:
        raise RuntimeError("SRÇ.004 Değerlendirme #1 aktif FRM.001.Ş yapısıyla uyuşmuyor")
    for bp in range(1, 7):
        if f"PIM.1.BP{bp}" not in storage:
            raise RuntimeError(f"SRÇ.004 Değerlendirme #1 içinde BP eksik: PIM.1.BP{bp}")
    if "14-07-2026" not in storage:
        raise RuntimeError("SRÇ.004 Değerlendirme #1 değerlendirme tarihini içermiyor")


def write_report() -> None:
    REPORT.write_text(
        "\n".join([
            "# SRÇ.004 Kalan Süreç Özel Dokümanları Yerel Çalışma Raporu",
            "",
            "Tarih: 14-07-2026",
            "",
            "- LST.009, aktif LST.009.Ş yapısına göre altı bölümle yeniden oluşturuldu.",
            "- LST.009 üç düzenli, yönetilebilir ve karar almaya yarayan ölçümle sınırlandırıldı.",
            "- LST.010, aktif LST.010.Ş yapısına göre rol/yetkinlik, faaliyet RACI, iş ürünü RACI ve yetki/onay matrisleriyle yeniden oluşturuldu.",
            "- SRÇ.004 altındaki FRM.001, SRÇ.001 modeli esas alınarak yeniden kullanılabilir boş form haline getirildi.",
            "- Doldurulmuş ilk değerlendirme, 91 - İç Denetimler / Süreç Gözden Geçirmeleri altına 'Değerlendirme #1' adıyla ayrıldı.",
            "- LST.009 ve LST.010 sayfaları mevcut Confluence sayfa kimlikleri korunarak yerelde SRÇ.004 altına taşındı.",
            "- Eski ŞBL referansları, kaldırılan doküman adları, sabit süreç sayısı ve geçmişe dönük varsayımsal kanıtlar kullanılmadı.",
            "- Confluence'a yayın yapılmadı.",
            "",
        ]),
        encoding="utf-8",
    )


def main() -> None:
    migrate_and_update_index()
    write_document("lst009", lst009_data)
    write_document("lst010", lst010_data)
    write_document("frm001", frm001_blank_data)
    write_assessment()
    write_report()
    print("[DONE] SRÇ.004 LST.009, LST.010, boş FRM.001 ve Değerlendirme #1 yerelde güncellendi.")
    print(f"[REPORT] {REPORT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
