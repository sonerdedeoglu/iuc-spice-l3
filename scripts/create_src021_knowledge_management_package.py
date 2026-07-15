#!/usr/bin/env python3
"""Create the local SRÇ.021 knowledge-management package.

This script is local-only. It never calls Confluence APIs. Existing page ids are
preserved; newly materialized pages keep an empty id until a reviewed publish.
"""
from __future__ import annotations

import html
import re
from pathlib import Path
from urllib.parse import quote

import yaml

from create_src005_process_assessment_package import (
    CONFLUENCE,
    GPS,
    INDEX_PATH,
    LABELS,
    PAGE_ROOT,
    PAGE_ROOT_REL,
    PREPARED_BY,
    PROCEDURES_ID,
    PROCEDURES_REL,
    REPORTS_REL,
    REVIEWS_ID,
    REVIEWS_REL,
    ROOT_ID,
    TEMPLATES_ID,
    TEMPLATES_REL,
    build_view,
    history,
    info_macro,
    info_view,
    p,
    parent_register_body,
    table,
    template_register_body,
    upsert_index,
    write_page,
)


SRC021_ID = "137265879"
RECORDS_ID = "137265786"
SRC021 = "SRÇ.021 - Bilgi Yönetimi Süreci"
PRS005 = "PRS.005 - Bilgi Yönetimi Prosedürü"
LST002 = "LST.002 - Doküman Değişiklik Kaydı"
LST004 = "LST.004 - Bilgi Kataloğu"
OWNER = "Levent BAYEZİT - Proje Yöneticisi"
REVIEWER = "Levent BAYEZİT - Süreç Sahibi"
APPROVER = "Mustafa Nusret SARISAKAL - Bilgi İşlem Daire Başkanı"

SRC021_REL = f"{PAGE_ROOT_REL}/01-surec-dokumanlari/src-021-bilgi-yonetimi-sureci"
RECORDS_REL = f"{PAGE_ROOT_REL}/03-kayitlar-ve-listeler"
LST006_REL = f"{RECORDS_REL}/lst-006-standart-surec-envanteri"
RPR001_REL = f"{REPORTS_REL}/rpr-001-surec-performanslari-raporu"

FLOW_PNG = "SRÇ.021 - Flowchart.png"
FLOW_MMD = "src021-surec-akisi.mmd"
INTERACTION_PNG = "src021-surec-etkilesim.png"
INTERACTION_MMD = "src021-surec-etkilesim.mmd"

RIN3_BPS = [
    ("RIN.3.BP1", "Bilgi yönetimi sistemini kur", "Bilgi varlıklarını belirleme, sınıflandırma, paylaşma ve kullanmayı destekleyen altyapı ve mekanizmayı kurmak ve sürdürmek."),
    ("RIN.3.BP2", "Bilgi katkıcıları ağını oluştur", "Uzmanları, ilgili birimleri ve karşılıklı etkileşimlerini bilgi ihtiyacına göre görünür kılmak."),
    ("RIN.3.BP3", "Bilgi yönetimi stratejisini geliştir", "Kurumsal, bireysel, alan ve proje ihtiyaçlarına uygun bilgi yönetimi stratejisini tanımlamak."),
    ("RIN.3.BP4", "Bilgiyi yakala", "Bilgi öğelerini sınıflandırma yapısı ve varlık ölçütlerine göre belirlemek ve kaydetmek."),
    ("RIN.3.BP5", "Bilgi varlıklarını yaygınlaştır", "Bilgi varlıklarını uzmanlar, kullanıcılar ve projelerle uygun kanallardan paylaşmak."),
    ("RIN.3.BP6", "Bilgi varlıklarını iyileştir", "Bilgi varlıklarının kurumsal uygunluğunu ve değerini korumak için doğrulamak, zenginleştirmek, güncellemek veya arşivlemek."),
]

FLOW_LINES = [
    "%%{init: {'flowchart': {'htmlLabels': false}}}%%",
    "flowchart TD",
    'A["Yeni veya değişen bilgi kaynağı"] --> B["Bilgi adayı ve kaynak sistem belirlenir"]',
    'B --> C["Kategori, ilgili süreç/proje/sistem ve erişim sınıfı belirlenir"]',
    'C --> D{"Kataloğa alınması gerekli mi?"}',
    'D -- "Hayır" --> E["Bilgi kendi kaynak sisteminde kullanılır"]',
    'D -- "Evet" --> F["Bağlantı ve erişim koşulları doğrulanır"]',
    'F --> G["LST.004 kaydı oluşturulur veya güncellenir"]',
    'G --> H{"Teknik ya da standart/mevzuat doğrulaması gerekli mi?"}',
    'H -- "Evet" --> I["İlgili uzman/birim veya Kalite Danışmanı içeriği doğrular"]',
    'H -- "Hayır" --> J["Bilgi Confluence başlangıç noktasından erişilebilir hale gelir"]',
    'I --> J',
    'J --> K{"Hedef kitle için önemli duyuru gerekli mi?"}',
    'K -- "Evet" --> L["Uygun kurumsal kanaldan bilgilendirme yapılır"]',
    'K -- "Hayır" --> M["Rutin kullanıma alınır"]',
    'L --> N["Yıllık veya olay bazlı gözden geçirme"]',
    'M --> N',
    'N --> O{"Bilgi güncel ve kullanılabilir mi?"}',
    'O -- "Evet" --> P["Aktif olarak sürdürülür"]',
    'O -- "Düzeltme gerekli" --> Q["Gözden Geçirilecek durumuna alınır ve güncellenir"]',
    'O -- "Geçersiz" --> R["Arşivlenir ve varsa ardıl bilgi bağlanır"]',
    'Q --> G',
    'P --> N',
]

INTERACTION_LINES = [
    "%%{init: {'flowchart': {'htmlLabels': false}}}%%",
    "flowchart LR",
    'A["SRÇ.001 doküman ve şablonlar"] --> K["SRÇ.021 Bilgi Yönetimi"]',
    'B["Jira analiz, karar ve iş kayıtları"] --> K',
    'C["Confluence süreç, proje ve teknik bilgi"] --> K',
    'D["Bitbucket kod ve repository teknik bilgisi"] --> K',
    'E["Google Drive paylaşımlı doküman ve toplantı kayıtları"] --> K',
    'F["SRÇ.007 öğrenilmiş dersler"] --> K',
    'G["SRÇ.017 çözüm ve deneyim bilgisi"] --> K',
    'H["SRÇ.020 eğitim ve kılavuz kayıtları"] --> K',
    'I["Uluslararası standartlar ve mevzuat"] --> K',
    'K --> L["LST.004 Bilgi Kataloğu"]',
    'K --> M["PRS.005 Bilgi Yönetimi Prosedürü"]',
    'L --> N["Uzmanlar, birimler, projeler ve süreçler"]',
    'I --> O["SRÇ.018 etki ve değişiklik değerlendirmesi"]',
    'K --> P["LST.012 koşullu yaygınlaştırma kaydı"]',
]


def image(storage: bool, filename: str, alt: str, width: int = 900) -> str:
    if storage:
        return f'<p><ac:image ac:width="{width}"><ri:attachment ri:filename="{html.escape(filename)}" /></ac:image></p>'
    return f'<p style="text-align:center"><img class="diagram" src="attachments/{quote(filename)}" alt="{html.escape(alt)}" /></p>'


def process_body(storage: bool) -> str:
    related = "<br />".join([
        "SRÇ.001 - Dokümantasyon Süreci",
        "SRÇ.007 - Proje Yönetimi Süreci",
        "SRÇ.017 - Problem Çözüm Yönetimi Süreci",
        "SRÇ.018 - Değişiklik Talebi Yönetimi Süreci",
        "SRÇ.020 - Eğitim Süreci",
        "SRÇ.023 - Organizasyonel Yönetim Süreci",
    ])
    mermaid = info_macro("Mermaid Kodu", FLOW_LINES) if storage else info_view("Mermaid Kodu", FLOW_LINES)
    activities = [
        ["F1", "Bilgi yönetimi altyapısını sürdür", "Confluence'ı bilgi ağının başlangıç noktası; Jira, Bitbucket, Google Drive ve diğer kaynak sistemleri bilginin asli saklama ortamları olarak kullan. Bağlantıları LST.004 ile görünür kıl. (RIN.3.BP1)", LST004],
        ["F2", "Uzman ve katkı rollerini görünür kıl", "Bilgi Kataloğunda ilgili uzman veya birimi belirt; katalog bakım sorumluluğunu Proje Yöneticisinde tut. Kalite Danışmanı standart ve kalite bilgisinde ana katkı rolüdür. (RIN.3.BP2)", "İlgili Uzman/Birim alanı; LST.010"],
        ["F3", "Bilgi yönetimi stratejisini uygula", "Bilgiyi kaynak sisteminde koru, Confluence üzerinden erişim bağlantısı kur, asgari katalog alanlarını kullan ve yalnızca doğrulanmış bağlantıları kaydet. (RIN.3.BP3)", PRS005],
        ["F4", "Bilgiyi belirle, sınıflandır ve kaydet", "Tanımlı tetikleyicilerde bilgi adayını; kategori, kaynak sistem, ilgili süreç/proje/sistem, uzman/birim ve erişim sınıfıyla LST.004'e ekle. (RIN.3.BP4)", LST004],
        ["F5", "Bilgiyi paylaş", "Bilgiyi ilgili kullanıcı ve projelere mevcut kurumsal kanallardan ulaştır. Rutin katalog ekleri için ayrı duyuru yapma; süreç dokümanı ve önemli değişikliklerde LST.012'yi kullan. (RIN.3.BP5)", "Confluence erişimi; koşullu LST.012 kaydı"],
        ["F6", "Bilgiyi gözden geçir ve iyileştir", "Kataloğu yılda bir kez ve tanımlı olaylarda gözden geçir. Kaydı Aktif, Gözden Geçirilecek veya Arşivlenmiş durumunda sürdür; ardıl bilgi varsa bağlantıyı koru. (RIN.3.BP6)", "LST.004 durum ve son kontrol kaydı"],
    ]
    return "".join([
        "<h2>1. Süreç Bilgileri</h2>", table(["Alan", "Değer"], [
            ["Kurum", "İstanbul Üniversitesi - Cerrahpaşa Bilgi İşlem Daire Başkanlığı"], ["Süreç Kodu ve Adı", SRC021],
            ["Süreç Referansı", "ISO/IEC 15504-5:2006 RIN.3 - Knowledge management"], ["Süreç Sahibi", OWNER],
            ["Hedef Kitle", "Bilgi İşlem Daire Başkanı, Proje Yöneticisi, Kalite Danışmanı, süreç sahipleri, proje ekipleri, ilgili uzmanlar ve bilgi kullanıcıları"],
            ["Yayın ve Erişim Ortamı", "Confluence başlangıç noktası; Jira, Bitbucket, Google Drive ve ilgili kaynak sistemlere kontrollü bağlantılar"],
            ["Durum", "Aktif"], ["Sürüm", "v1.0"], ["Yürürlük Tarihi", "15-02-2025"], ["Son Gözden Geçirme Tarihi", "15-07-2026"],
            ["Güncelleme Sıklığı", "Yılda en az bir kez veya bilgi kaynağı, erişim, süreç, proje, sistem, standart ya da mevzuat değiştiğinde"],
        ]),
        "<h2>2. Amaç</h2>", p("Bu sürecin amacı; bireysel ve kurumsal bilgi, enformasyon ve becerilerin belirlenmesini, kaynak sistemlerinde korunmasını, kolay erişilebilir biçimde paylaşılmasını, yeniden kullanılmasını ve iyileştirilmesini sağlamaktır."),
        "<h3>2.1. Süreç Sonuçları</h3>", table(["Sonuç ID", "Süreç Sonucu"], [["S1", "Ortak ve alan bilgisinin kurum genelinde paylaşılması için altyapı kurulur ve sürdürülür."], ["S2", "Bilgi erişilebilir duruma getirilir ve ilgili taraflarla paylaşılır."], ["S3", "Kurumsal ihtiyaçlara uygun bilgi yönetimi stratejisi seçilir ve uygulanır."]]),
        "<h2>3. Kapsam</h2>", table(["Kapsam Öğesi", "Açıklama"], [
            ["Kapsama Dahil", "Süreç ve kalite bilgisi; proje, analiz, tasarım ve mimari bilgisi; yazılım/kaynak kod; altyapı ve işletim bilgisi; destek çözümleri ve öğrenilmiş dersler; müşteri/toplantı/karar kayıtları; eğitim ve kılavuzlar; uygulanabilir standartlar ve mevzuat"],
            ["Kapsam Dışı", "Bilginin asli kaynak sisteminden kopyalanarak ayrı bir merkezi depoda çoğaltılması; kaynak sistem yetkilendirmesinin LST.004 tarafından değiştirilmesi; her katalog satırı için ayrı resmî onay"],
            ["Uygulama Alanı", "BİDB süreçleri, projeleri, sistemleri, teknik ve idari bilgi varlıkları ile bunların doğrulanmış erişim bağlantıları"],
        ]),
        "<h2>4. Referanslar</h2>", table(["Referans", "Açıklama"], [["ISO/IEC 15504-5:2006 RIN.3 - Knowledge management", "Süreç amacı, sonuçları ve BP1-BP6 temel uygulamaları"], ["ISO/IEC 15504-5:2006 - Process Assessment Model", "Süreç boyutu ve değerlendirme göstergeleri"], ["ISO/IEC 15504-5:2006 - Process Attributes", "PA 2.1, PA 2.2, PA 3.1 ve PA 3.2 süreç öznitelikleri ile genel uygulamalar"]]),
        "<h2>5. Terimler ve Kısaltmalar</h2>", table(["Terim / Kısaltma", "Açıklama"], [["Bilgi Varlığı", "Kurumsal karar, uygulama veya yeniden kullanım için değer taşıyan bilgi, belge, kayıt, kod, video, kılavuz, standart veya bağlantı"], ["Bilgi Kataloğu", "Bilgi varlıklarının kaynak sistemini, erişim bağlantısını, sınıfını ve durumunu gösteren LST.004"], ["Kaynak Sistem", "Bilginin asıl ve yetkili kopyasının tutulduğu Confluence, Jira, Bitbucket, Google Drive veya diğer kurumsal ortam"], ["Erişim Sınıfı", "BİDB Geneli, İlgili Proje/Ekip, Yönetimle Sınırlı veya Müşteri Birimiyle Paylaşımlı etiketi"]]),
        "<h2>6. Süreç Aktivitesi</h2>", table(["Alan", "Açıklama"], [["Süreç Başlatıcısı", "Yeni veya güncellenen süreç/doküman; kalıcı analiz, tasarım veya mimari karar; yeniden kullanılabilir teknik çözüm; problem/deneyim/öğrenilmiş ders; müşteri kararı; eğitim/kılavuz/toplantı kaydı; kod deposu/teknik referans; standart veya mevzuat değişikliği"], ["Süreç Başlangıcı", "Bilgi adayının ve yetkili kaynak sisteminin belirlenmesi"], ["Süreç Bitişi", "Bilginin kaynak sisteminde korunarak doğrulanmış bağlantıyla LST.004'te erişilebilir olması; gerekli bilgilendirmenin yapılması ve gözden geçirme durumunun sürdürülmesi"], ["Ana Faaliyetler", "Altyapıyı sürdürme; uzman ve katkı rollerini görünür kılma; stratejiyi uygulama; bilgiyi yakalama ve sınıflandırma; yaygınlaştırma; gözden geçirme ve iyileştirme"], ["İlgili Süreçler", related]]),
        "<h2>7. Roller ve Sorumluluklar</h2>", p("Rol, sorumluluk, yetki, yetkinlik ve RACI bilgileri LST.010 - Süreç Rol Yetki ve RACI Matrisi (SRÇ.021) dokümanında yönetilir."),
        "<h2>8. Araçlar ve Altyapı</h2>", table(["Tür", "Araç / Altyapı Bileşeni", "Kullanım Amacı", "Erişim ve Kullanım Koşulu", "Sorumlu Rol / Birim"], [
            ["Araç", "Confluence", "Bilgi ağının başlangıç noktası; süreç, proje ve teknik bilgi sayfaları ile kaynak bağlantıları", "Kurumsal hesap ve sayfa yetkisi; uzaktan erişimde gerekli kurumsal erişim koşulları", "Proje Yöneticisi / Confluence Yöneticisi"],
            ["Araç", "Jira", "Gereksinim, analiz, karar, faaliyet ve proje iş kayıtları", "Proje bazlı yetkilendirme", "Proje Yöneticisi / Jira Yöneticisi"],
            ["Araç", "Bitbucket", "Kaynak kod ve repository düzeyi teknik dokümantasyon", "Repository yetkisi", "Proje Yöneticisi / Repository Yöneticisi"],
            ["Altyapı", "Google Drive", "Müşteri birimleriyle paylaşılan dokümanlar ve çevrim içi toplantı video kayıtları", "Kurumsal hesap ve dosya/klasör yetkisi", "Proje Yöneticisi / Dosya Sahibi"],
            ["Altyapı", "Kurumsal kimlik, erişim ve yedekleme altyapısı", "Kaynak sistemlerdeki bilgiye güvenli ve sürdürülebilir erişim", "Kaynak sistemin bilgi güvenliği ve yetkilendirme kuralları", "İlgili Sistem Sahibi / BİDB"],
        ], fixed=True),
        "<h2>9. Süreç İş Ürünleri</h2>", p("Girdi ve çıktı iş ürünleri ile kalite kriterleri LST.008 - İş Ürünleri ve Kalite Kriterleri Listesi (SRÇ.021) dokümanında yönetilir."),
        "<h2>10. Süreç Akışı</h2>", image(storage, FLOW_PNG, "SRÇ.021 bilgi yönetimi süreç akışı") + mermaid,
        "<h2>11. Süreç Faaliyetleri</h2>", table(["Faaliyet ID", "Faaliyet", "Açıklama", "Elde Edilen / Güncellenen İş Ürünü"], activities),
        "<h2>12. Ölçüm ve İzleme</h2>", p("Yönetilebilir iki ölçüm LST.009 - Süreç Performans Ölçüm Seti (SRÇ.021) dokümanında tanımlanır: geçerli bağlantı oranı ve yıllık gözden geçirme tamamlama oranı. Kayıt sayısı performans göstergesi değildir."),
        "<h2>13. Uygulama ve Uyarlama Kuralları</h2>",
        "<h3>13.1. Kaynak Sistem ve Bağlantı İlkesi</h3>" + p("Bilgi kendi yetkili kaynak sisteminde tutulur; ortamlar arasında gereksiz kopyalanmaz. Confluence ve LST.004, ayrıntıya ulaşmak için doğrulanmış erişim bağlantısı sağlar. Erişim yetkisi kaynak sistem tarafından uygulanır."),
        "<h3>13.2. Katalog Sahipliği ve Doğrulama</h3>" + p("LST.004 kayıtlarını Proje Yöneticisi oluşturur ve sürdürür. Teknik içerik gerektiğinde ilgili uzman veya birimce; uluslararası standart ve kalite bilgisi Kalite Danışmanınca doğrulanır. Her satır için ayrı resmî onay aranmaz."),
        "<h3>13.3. Erişim Sınıfları</h3>" + p("Bilgi varlığı BİDB Geneli, İlgili Proje/Ekip, Yönetimle Sınırlı veya Müşteri Birimiyle Paylaşımlı olarak etiketlenir. Etiket, kaynak sistem yetkisinin yerine geçmez."),
        "<h3>13.4. Standart ve Mevzuat Değişikliği</h3>" + p("Uluslararası standartlardaki değişiklikleri Kalite Danışmanı; BİDB teknik ve kurumsal gerekliliklerini Proje Yöneticisi izler. Değişikliğin bir süreci etkileme ihtimali varsa LST.004 güncellenir ve konu SRÇ.018 etki/değişiklik değerlendirmesine aktarılır."),
        "<h3>13.5. Gözden Geçirme ve Arşiv</h3>" + p("Toplu katalog gözden geçirmesi yılda bir kez yapılır. Bozuk bağlantı, kaynak taşınması, süreç/proje/sistem değişikliği, standart/mevzuat değişikliği veya hata bildirimi olay bazlı gözden geçirmeyi tetikler. Geçersiz kayıt Arşivlenmiş yapılır ve ardıl bilgi bağlanır; yalnızca hatalı veya mükerrer kayıt silinir."),
        "<h3>13.6. Yaygınlaştırma</h3>" + p("Rutin katalog ekleri için ayrı duyuru yapılmaz. Önemli teknik veya operasyonel bilgi mevcut kurumsal kanaldan paylaşılır. Süreç dokümanı, standart/mevzuat etkisi veya süreç değişikliği hedef kitleyi etkiliyorsa bilgilendirme yapılır; süreç dokümanlarına ilişkin yaygınlaştırma LST.012'de kaydedilir."),
        "<h2>14. Süreç Etkileşimleri</h2>", p("Sürecin diğer süreçler, kaynak sistemler ve iş ürünleriyle etkileşimi LST.007 - Süreç Etkileşim Matrisi (SRÇ.021) dokümanında yönetilir."),
        "<h2>15. Sürüm Geçmişi</h2>", history("Bilgi Yönetimi Süreci", REVIEWER, APPROVER),
    ])


def lst007_body(storage: bool) -> str:
    mermaid = info_macro("Mermaid Kodu", INTERACTION_LINES) if storage else info_view("Mermaid Kodu", INTERACTION_LINES)
    return "".join([
        "<h2>1. Liste Özeti</h2>", table(["Alan", "Değer"], [["Liste Kodu ve Adı", "LST.007 - Süreç Etkileşim Matrisi (SRÇ.021)"], ["Kullanım Amacı", "Bilgi Yönetimi Sürecinin süreçler, kaynak sistemler ve iş ürünleriyle etkileşimini göstermek"], ["Sorumlu", OWNER], ["Durum", "Aktif"], ["Sürüm", "v1.0"], ["Son Gözden Geçirme Tarihi", "15-07-2026"]]),
        "<h2>2. Etkileşim Matrisi</h2>", table(["Kaynak Süreç / Sistem / Doküman", "Etkileşim", "Hedef Süreç / Sistem / Doküman", "Yön", "Sorumlu"], [
            ["SRÇ.001 - Dokümantasyon Süreci", "Onaylı doküman, şablon ve değişiklik bilgisi", SRC021, "Girdi", "Proje Yöneticisi / Kalite Danışmanı"],
            ["Jira / Confluence / Bitbucket / Google Drive", "Analiz, tasarım, karar, kod, paylaşımlı doküman ve toplantı kayıtları", SRC021, "Girdi", "Proje Yöneticisi / İlgili Uzman"],
            ["SRÇ.007 - Proje Yönetimi Süreci", "Proje kapanışı ve öğrenilmiş dersler", SRC021, "Girdi", "Proje Yöneticisi"],
            ["SRÇ.017 - Problem Çözüm Yönetimi Süreci", "Yeniden kullanılabilir çözüm ve deneyim bilgisi", SRC021, "Girdi", "İlgili Uzman / Proje Yöneticisi"],
            ["SRÇ.020 - Eğitim Süreci", "Eğitim, kılavuz ve görsel kayıtlar", SRC021, "Girdi", "Eğitim Sorumlusu / Proje Yöneticisi"],
            ["Uluslararası standartlar ve mevzuat", "Uygulanabilir gereklilik ve değişiklik bilgisi", SRC021, "Girdi", "Kalite Danışmanı / Proje Yöneticisi"],
            [SRC021, "Doğrulanmış bilgi erişim kaydı", LST004, "Çıktı", "Proje Yöneticisi"],
            [SRC021, "Bilgi yönetimi uygulama kuralları", PRS005, "Çıktı", "Proje Yöneticisi / Kalite Danışmanı"],
            [SRC021, "Etki ihtimali bulunan standart, mevzuat veya bilgi değişikliği", "SRÇ.018 - Değişiklik Talebi Yönetimi Süreci", "Çıktı", "Proje Yöneticisi / Kalite Danışmanı"],
            [SRC021, "Hedef kitleyi etkileyen süreç bilgi duyurusu", "LST.012 - Süreç Yaygınlaştırma ve Bilgilendirme Kaydı", "Koşullu Çıktı", "Proje Yöneticisi"],
        ]),
        "<h2>3. Süreç Etkileşim Diyagramı</h2>", image(storage, INTERACTION_PNG, "SRÇ.021 süreç etkileşim diyagramı", 850) + mermaid,
        "<h2>4. Sürüm Geçmişi</h2>", history("Süreç Etkileşim Matrisi (SRÇ.021)", REVIEWER, APPROVER),
    ])


def lst008_body() -> str:
    return "".join([
        "<h2>1. Liste Özeti</h2>", table(["Alan", "Değer"], [["Liste Kodu ve Adı", "LST.008 - İş Ürünleri ve Kalite Kriterleri Listesi (SRÇ.021)"], ["Kullanım Amacı", "Bilgi Yönetimi Sürecinin girdi ve çıktı iş ürünleri ile kabul kriterlerini tanımlamak"], ["Sorumlu", OWNER], ["Durum", "Aktif"], ["Sürüm", "v1.0"], ["Son Gözden Geçirme Tarihi", "15-07-2026"]]),
        "<h2>2. Girdi İş Ürünleri</h2>", table(["İş Ürünü", "Kaynak", "Kalite Kriteri", "İlgili BP"], [
            ["Onaylı süreç, prosedür, şablon, liste ve diğer kurumsal dokümanlar", "SRÇ.001 - Dokümantasyon Süreci / Confluence", "Güncel başlık, sürüm ve yetkili erişim bağlantısı bulunur.", "RIN.3.BP1, BP4"],
            ["Proje analiz, tasarım, mimari ve karar kayıtları", "Jira / Confluence", "Kalıcı kurumsal değer veya yeniden kullanım ihtiyacı açıktır.", "RIN.3.BP3, BP4"],
            ["Kaynak kod ve repository teknik bilgisi", "Bitbucket", "Repository ve erişim bağlantısı doğrulanmıştır.", "RIN.3.BP1, BP4"],
            ["Müşteri paylaşımlı dokümanlar ve toplantı video kayıtları", "Google Drive", "Paylaşım kapsamı ve erişim sınıfı bellidir.", "RIN.3.BP4, BP5"],
            ["Öğrenilmiş ders, çözüm ve eğitim kayıtları", "SRÇ.007 / SRÇ.017 / SRÇ.020", "Bilgi tekrar kullanılabilir ve kaynağı izlenebilirdir.", "RIN.3.BP2, BP4"],
            ["Uygulanabilir uluslararası standart ve mevzuat", "Yetkili standart/mevzuat kaynağı", "Kaynak, kapsam, son kontrol ve ilgili süreç bağlantısı doğrulanmıştır.", "RIN.3.BP3, BP4, BP6"],
        ]),
        "<h2>3. Çıktı İş Ürünleri</h2>", table(["İş Ürünü", "Kullanım Amacı", "Kalite Kriteri", "İlgili BP"], [
            [LST004, "Bilgi varlıklarının nerede ve nasıl erişilebilir olduğunu göstermek", "Zorunlu alanlar doludur; bağlantı ve erişim sınıfı doğrulanmıştır; durum ve son kontrol tarihi günceldir.", "RIN.3.BP1-BP6"],
            [PRS005, "Bilgi seçimi, sınıflandırma, paylaşma ve gözden geçirme kurallarını tanımlamak", "Kaynak sistem, sahiplik, erişim, doğrulama, yaygınlaştırma ve arşiv kurallarını kapsar.", "RIN.3.BP1-BP6"],
            ["LST.012 - Süreç Yaygınlaştırma ve Bilgilendirme Kaydı", "Hedef kitleyi etkileyen süreç dokümanı bilgilendirmesini kaydetmek", "Süreç, hedef kitle, kanal, tarih ve kanıt bağlantısı bulunur; rutin katalog güncellemeleri için kullanılmaz.", "RIN.3.BP5"],
            ["SRÇ.018 - Değişiklik Talebi Yönetimi Süreci etki/değişiklik kaydı", "Standart, mevzuat veya bilgi değişikliğinin süreç etkisini değerlendirmek", "Etkilenen süreç ve kaynak bilgi bağlantısı izlenebilirdir.", "RIN.3.BP6"],
            ["FRM.001 - Süreç Gözden Geçirme Formu (SRÇ.021)", "BP ve PA/GP karşılama durumunu kanıtla izlemek", "Etiketler gerekçeli, kanıtlar erişilebilir ve aksiyon yönlendirmeleri açıktır.", "PA 2.1-PA 3.2"],
        ]),
        "<h2>4. Sürüm Geçmişi</h2>", history("İş Ürünleri ve Kalite Kriterleri Listesi (SRÇ.021)", REVIEWER, APPROVER),
    ])


def lst009_body() -> str:
    return "".join([
        "<h2>1. Liste Özeti</h2>", table(["Alan", "Değer"], [["Liste Kodu ve Adı", "LST.009 - Süreç Performans Ölçüm Seti (SRÇ.021)"], ["Kullanım Amacı", "Bilgi kataloğunun erişilebilirliğini ve bakım düzenini az sayıda uygulanabilir ölçümle izlemek"], ["Sorumlu", OWNER], ["Durum", "Aktif"], ["Sürüm", "v1.0"], ["Son Gözden Geçirme Tarihi", "15-07-2026"]]),
        "<h2>2. Hedef ve İzleme Matrisi</h2>", table(["Ölçüm", "Tanım / Hesaplama", "Hedef", "Sıklık", "Veri Kaynağı", "Sorumlu", "Sonuç Kullanımı"], [
            ["Geçerli bağlantı oranı", "Erişilebilir ve doğru hedefe açılan Aktif katalog bağlantısı / kontrol edilen Aktif katalog bağlantısı x 100", "En az %95", "Yıllık ve olay bazlı", LST004, "Proje Yöneticisi", "Bozuk veya taşınmış bağlantıları Gözden Geçirilecek durumuna almak"],
            ["Yıllık gözden geçirme tamamlama oranı", "Yıllık kontrolden geçirilen katalog kaydı / yıllık kontrol kapsamındaki katalog kaydı x 100", "%100", "Yıllık", "LST.004 Son Kontrol Tarihi ve Durum alanları", "Proje Yöneticisi / Kalite Danışmanı", "Eksik kontrolleri tamamlamak ve arşiv/güncelleme ihtiyacını belirlemek"],
        ]),
        "<h2>3. Ölçüm Uygulama Kuralları</h2>", table(["Kural", "Açıklama"], [["Kayıt sayısı", "Bilgi Kataloğu satır sayısı performans göstergesi değildir."], ["Kanıt", "Sonuç, LST.004 üzerindeki bağlantı kontrolü, son kontrol tarihi ve durum alanlarından üretilir."], ["Aksiyon", "Hedef altı sonuçta düzeltme LST.004 üzerinde yapılır; süreç veya sistem etkisi varsa SRÇ.018'e aktarılır."]]),
        "<h2>4. Sürüm Geçmişi</h2>", history("Süreç Performans Ölçüm Seti (SRÇ.021)", REVIEWER, APPROVER),
    ])


def lst010_body() -> str:
    # LST.010 is maintained in the SRÇ.006 role-column structure.
    from align_lst010_to_src006_structure import process_body, src021
    return process_body(src021())

    roles = [["Proje Yöneticisi", "Bilgi yönetimi stratejisini ve LST.004'ü sürdürmek; kaynak sistem ve bağlantıları koordine etmek", "Rutin katalog kaydı oluşturma, güncelleme ve arşivleme"], ["Kalite Danışmanı", "Uluslararası standartları, kalite ve süreç bilgisini izlemek; katalog içeriğine katkı sağlamak", "Standart/kalite bilgisini doğrulama ve süreç etkisi önerisi"], ["İlgili Uzman / Birim", "Gerektiğinde teknik veya alan bilgisinin doğruluğunu teyit etmek", "Kendi uzmanlık alanında teknik uygunluk görüşü"], ["Süreç / Proje / Sistem Sahibi", "Bilgi kaynağındaki değişikliği bildirmek ve yetkili kaynağı korumak", "Kendi alanındaki kaynak içeriği ve erişim kararı"], ["Bilgi İşlem Daire Başkanı", "Bilgi yönetimi süreci ve prosedürünü onaylamak; kurumsal kapsamda kaynak/yetki sağlamak", "Süreç onayı ve kurumsal karar"], ["Bilgi Kullanıcısı", "Kataloğu kullanmak; bozuk bağlantı, güncellik veya hata sorununu bildirmek", "Düzeltme talebi ve geri bildirim"]]
    raci = [
        ["Bilgi yönetimi stratejisini sürdür", "R/A", "C", "I", "C", "I"],
        ["Bilgi adayını ve kaynak sistemi belirle", "A", "C", "R/C", "R/C", "I"],
        ["LST.004 kaydını oluştur/güncelle", "R/A", "C", "C", "C", "I"],
        ["Teknik bilgiyi doğrula", "A", "I", "R", "C", "I"],
        ["Standart ve kalite bilgisini doğrula", "A", "R", "C", "C", "I"],
        ["Bilgiyi yaygınlaştır", "R/A", "C", "C", "C", "I"],
        ["Yıllık ve olay bazlı gözden geçir", "R/A", "R/C", "C", "C", "I"],
        ["Süreç etkisi için SRÇ.018'e aktar", "R", "R/C", "C", "C", "A/I"],
    ]
    return "".join([
        "<h2>1. Liste Özeti</h2>", table(["Alan", "Değer"], [["Liste Kodu ve Adı", "LST.010 - Süreç Rol Yetki ve RACI Matrisi (SRÇ.021)"], ["Kullanım Amacı", "Bilgi Yönetimi Sürecindeki rol, sorumluluk, yetki ve RACI atamalarını tanımlamak"], ["Sorumlu", OWNER], ["Durum", "Aktif"], ["Sürüm", "v1.0"], ["Son Gözden Geçirme Tarihi", "15-07-2026"]]),
        "<h2>2. Roller, Sorumluluklar ve Yetkiler</h2>", table(["Rol", "Sorumluluk", "Yetki"], roles),
        "<h2>3. RACI Matrisi</h2>", table(["Faaliyet", "Proje Yöneticisi", "Kalite Danışmanı", "İlgili Uzman / Birim", "Süreç / Proje / Sistem Sahibi", "Bilgi İşlem Daire Başkanı"], raci, fixed=True),
        "<h2>4. RACI Gösterimi</h2>", table(["Kod", "Anlamı"], [["R", "Faaliyeti gerçekleştirir."], ["A", "Nihai sorumluluğu taşır / karar verir."], ["C", "Görüşü alınır."], ["I", "Bilgilendirilir."]]),
        "<h2>5. Sürüm Geçmişi</h2>", history("Süreç Rol Yetki ve RACI Matrisi (SRÇ.021)", REVIEWER, APPROVER),
    ])


def blank_review_body() -> str:
    return "".join([
        "<h2>1. Form Bilgileri</h2>", table(["Alan", "Değer"], [["Form Kodu ve Adı", "FRM.001 - Süreç Gözden Geçirme Formu (SRÇ.021)"], ["Süreç", SRC021], ["Değerlendirme Tarihi", "<em>GG-AA-YYYY</em>"], ["Değerlendiren", "<em>Rol / kişi</em>"], ["Durum", "Boş Form"], ["Sürüm", "v1.0"]]),
        "<h2>2. Durum Değerleri</h2>", table(["Durum", "Anlamı"], LABELS),
        "<h2>3. BP Takip Matrisi</h2>", table(["BP", "Standart Beklentisi", "Mevcut Karşılama", "Karşılayan Doküman / Kayıt", "Durum", "Eksik / Tamamlayıcı Aksiyon"], [[bp, expectation, "<em>Değerlendirme açıklaması</em>", "<em>Kanıt bağlantısı</em>", "<em>YOK / ZAYIF / DAĞINIK / VAR / KAPSAM DIŞI</em>", "<em>Aksiyon / gerekçe</em>"] for bp, _, expectation in RIN3_BPS]),
        "<h2>4. PA / GP Takip Matrisi</h2>", table(["PA", "GP", "Standart Beklentisi", "Mevcut Karşılama", "Karşılayan Doküman / Kayıt", "Durum", "Eksik / Tamamlayıcı Aksiyon"], [[pa, gp, expectation, "<em>Değerlendirme açıklaması</em>", "<em>Kanıt bağlantısı</em>", "<em>Etiket</em>", "<em>Aksiyon / gerekçe</em>"] for pa, gp, expectation in GPS]),
        "<h2>5. Öncelikli Tamamlama Listesi</h2>", table(["Öncelik", "Bulgu / Aksiyon", "Bulgu Türü", "İlgili BP / GP", "Hedef Süreç / İzleme Yeri"], [["<em>Yüksek / Orta / Düşük</em>", "<em>Bulgu veya aksiyon</em>", "<em>Uygunsuzluk / İyileştirme Fırsatı / Gözlem / Güçlü Uygulama</em>", "<em>BP / GP</em>", "<em>SRÇ.017 / SRÇ.018 / ilgili kayıt</em>"]]),
    ])


def assessment_body() -> str:
    bp = {
        "RIN.3.BP1": ("Confluence merkezli bağlantı ağı, kaynak sistemler, LST.004 ve PRS.005 tanımlanmıştır.", f"{SRC021}; {PRS005}; {LST004}", "VAR", "Altyapı ve mekanizma tanımlıdır; gerçek bağlantılar katalog olgunlaştıkça artırılacaktır."),
        "RIN.3.BP2": ("İlgili Uzman/Birim alanı, Proje Yöneticisi ve Kalite Danışmanı rolleri tanımlıdır; uzman ağı henüz kullanım kanıtı üretmemiştir.", "LST.004; LST.010", "DAĞINIK", "Gerçek katalog satırlarında uzman/birim bağlantıları oluştukça doğrulanmalıdır."),
        "RIN.3.BP3": ("Kaynakta tutma, bağlantıyla erişim, sınıflandırma, sahiplik ve gözden geçirme stratejisi tanımlanmıştır.", f"{SRC021}; {PRS005}", "VAR", "Strateji tanımlıdır."),
        "RIN.3.BP4": ("Bilgi yakalama tetikleyicileri ve katalog alanları tanımlıdır; ilk katalog yalnızca doğrulanmış süreç/kalite bağlantılarıyla başlatılmıştır.", f"{LST004}; {PRS005}", "DAĞINIK", "Diğer süreçler tamamlandıkça doğrulanmış bilgi varlıkları eklenmelidir."),
        "RIN.3.BP5": ("Rutin ve önemli bilginin paylaşım kuralları tanımlıdır; henüz sistematik yaygınlaştırma kanıtı sınırlıdır.", "PRS.005; LST.012", "DAĞINIK", "Önemli bilgi paylaşımları oluştukça doğal kanal ve koşullu LST.012 kanıtı korunmalıdır."),
        "RIN.3.BP6": ("Yıllık ve olay bazlı gözden geçirme, durum ve arşiv kuralları tanımlıdır; tamamlanmış katalog gözden geçirme kanıtı henüz yoktur.", f"{SRC021}; {PRS005}; {LST004}", "ZAYIF", "İlk yıllık katalog gözden geçirmesi gerçekleştirilmeli ve LST.004 son kontrol alanları güncellenmelidir."),
    }
    bp_rows = [[code, expectation, *bp[code]] for code, _, expectation in RIN3_BPS]
    statuses = {
        "GP.2.1.1":"VAR", "GP.2.1.2":"DAĞINIK", "GP.2.1.3":"ZAYIF", "GP.2.1.4":"VAR", "GP.2.1.5":"VAR", "GP.2.1.6":"VAR",
        "GP.2.2.1":"VAR", "GP.2.2.2":"VAR", "GP.2.2.3":"DAĞINIK", "GP.2.2.4":"DAĞINIK",
        "GP.3.1.1":"VAR", "GP.3.1.2":"VAR", "GP.3.1.3":"VAR", "GP.3.1.4":"VAR", "GP.3.1.5":"VAR",
        "GP.3.2.1":"DAĞINIK", "GP.3.2.2":"DAĞINIK", "GP.3.2.3":"YOK", "GP.3.2.4":"DAĞINIK", "GP.3.2.5":"VAR", "GP.3.2.6":"ZAYIF",
    }
    evidence = f"{SRC021}; LST.007; LST.008; LST.009; LST.010; {PRS005}; {LST004}"
    gp_rows = []
    for pa, gp, expectation in GPS:
        status = statuses[gp]
        if status == "VAR":
            current, action = "Süreç paketi, roller, iş ürünleri, etkileşimler, altyapı ve kontrol kurallarıyla tanımlanmıştır.", "Tanımlı yapı korunmalı ve gerçek kayıtlarla sürdürülmelidir."
        elif status == "DAĞINIK":
            current, action = "Tanım ve kısmi kanıt vardır; gerçek uygulama, atama veya gözden geçirme kanıtı henüz sistematik değildir.", "Süreç işletildikçe doğal kaynak sistem kanıtları ve katalog kayıtları tamamlanmalıdır."
        elif status == "ZAYIF":
            current, action = "Yöntem tanımlıdır; ayarlama veya gerçek performans analizi henüz yapılmamıştır.", "İlk gerçek ölçüm ve gözden geçirme döneminde sonuç üretilmelidir."
        else:
            current, action = "Rol bazlı yetkinlik ve eğitim kanıtı henüz bulunmamaktadır.", "Gerçek ihtiyaç SRÇ.020 kapsamında değerlendirilmelidir."
        gp_rows.append([pa, gp, expectation, current, evidence, status, action])
    completion = [
        ["Yüksek", "İlk yıllık Bilgi Kataloğu gözden geçirmesini gerçekleştir ve geçerli bağlantı oranını hesapla.", "Gözlem", "RIN.3.BP6; GP.2.1.3; GP.3.2.6", "LST.004 / LST.009 / FRM.001 Değerlendirme #1"],
        ["Orta", "Diğer süreç paketleri tamamlandıkça doğrulanmış bilgi varlıklarını ve ilgili uzman/birim alanını LST.004'e ekle.", "İyileştirme Fırsatı", "RIN.3.BP2; RIN.3.BP4", "SRÇ.018 / LST.004"],
        ["Orta", "Önemli ilk bilgi paylaşımında hedef kitle, kanal ve erişim kanıtını doğrula.", "Gözlem", "RIN.3.BP5; GP.3.2.1; GP.3.2.2", "Doğal iletişim kaydı / koşullu LST.012"],
        ["Düşük", "Rol bazlı yetkinlik ihtiyacı oluştuğunda SRÇ.020 kapsamında eğitim/katılım kanıtı oluştur.", "Gözlem", "GP.3.2.3", "SRÇ.020"],
    ]
    return "".join([
        "<h2>1. Değerlendirme Özeti</h2>", table(["Alan", "Değer"], [["Süreç", SRC021], ["Değerlendirme Kaydı", "Değerlendirme #1"], ["Değerlendirme Tarihi", "15-07-2026"], ["Değerlendiren", PREPARED_BY], ["Yaklaşım", "Yalnızca gerekçeli etiket; sayısal puan veya tek genel süreç etiketi kullanılmaz."], ["BP Dağılımı", "2 VAR, 3 DAĞINIK ve 1 ZAYIF"], ["PA / GP Dağılımı", "12 VAR, 6 DAĞINIK, 2 ZAYIF ve 1 YOK"], ["Genel Not", "Bilgi yönetimi stratejisi, araç ekosistemi, sahiplik, katalog şeması ve kontrol kuralları tanımlıdır. Gerçek katalog kapsamı, uzman ağı, yaygınlaştırma, yıllık gözden geçirme ve performans kanıtları süreç işletildikçe olgunlaştırılacaktır."]]),
        "<h2>2. Durum Değerleri</h2>", table(["Durum", "Anlamı"], LABELS),
        "<h2>3. BP Takip Matrisi</h2>", table(["BP", "Standart Beklentisi", "Mevcut Karşılama", "Karşılayan Doküman / Kayıt", "Durum", "Eksik / Tamamlayıcı Aksiyon"], bp_rows),
        "<h2>4. PA / GP Takip Matrisi</h2>", table(["PA", "GP", "Standart Beklentisi", "Mevcut Karşılama", "Karşılayan Doküman / Kayıt", "Durum", "Eksik / Tamamlayıcı Aksiyon"], gp_rows),
        "<h2>5. Öncelikli Tamamlama Listesi</h2>", table(["Öncelik", "Bulgu / Aksiyon", "Bulgu Türü", "İlgili BP / GP", "Hedef Süreç / İzleme Yeri"], completion),
    ])


def procedure_body() -> str:
    categories = "Süreç ve kalite; Proje/analiz/tasarım/mimari; Yazılım/kaynak kod; Altyapı/sistem/işletim; Destek/çözüm/öğrenilmiş ders; Müşteri/toplantı/karar; Eğitim/kılavuz/görsel kayıt; Uygulanabilir Standartlar ve Mevzuat"
    return "".join([
        "<h2>1. Prosedür Bilgileri</h2>", table(["Alan", "Değer"], [["Kurum", "İstanbul Üniversitesi - Cerrahpaşa Bilgi İşlem Daire Başkanlığı"], ["Prosedür Kodu ve Adı", PRS005], ["Prosedür Referansı", SRC021], ["Prosedür Sahibi", OWNER], ["Durum", "Aktif"], ["Sürüm", "v1.0"], ["Yürürlük Tarihi", "15-02-2025"], ["Son Gözden Geçirme Tarihi", "15-07-2026"]]),
        "<h2>2. Amaç</h2>", p("Bu prosedürün amacı, BİDB bilgi varlıklarının kaynak sistemlerinde korunarak belirlenmesi, sınıflandırılması, doğrulanmış bağlantılarla kataloglanması, uygun hedef kitleye ulaştırılması, gözden geçirilmesi ve iyileştirilmesi için uygulanacak kuralları tanımlamaktır."),
        "<h2>3. Kapsam</h2>", p("Bu prosedür; BİDB süreç, proje, yazılım, altyapı, destek, müşteri, eğitim, standart ve mevzuat bilgisinin Confluence, Jira, Bitbucket, Google Drive ve ilgili kaynak sistemlerde yönetilmesine uygulanır."),
        "<ul><li>bilgi adayının ve yetkili kaynağın belirlenmesi,</li><li>kategori ve erişim sınıfının belirlenmesi,</li><li>LST.004 kaydının oluşturulması ve sürdürülmesi,</li><li>teknik veya standart/mevzuat doğrulaması,</li><li>yaygınlaştırma, gözden geçirme ve arşivleme.</li></ul>",
        "<h2>4. Kapsam Dışı</h2>", "<ul><li>Kaynak sistemler arasında dosya kopyalayarak yeni bir merkezi bilgi deposu oluşturmak,</li><li>kaynak sistem erişim yetkilerini LST.004 üzerinden vermek veya değiştirmek,</li><li>her rutin katalog satırı için ayrı resmî onay almak,</li><li>proje iş takibini veya kaynak kod sürüm yönetimini LST.004 üzerinden yürütmek.</li></ul>",
        "<h2>5. Referanslar</h2>", table(["Referans", "Açıklama"], [[SRC021, "Bilgi yönetimi süreç kapsamı ve RIN.3 uygulamaları"], [LST004, "Bilgi varlığı erişim, sınıflandırma ve durum kaydı"], ["PRS.XXX.Ş - Prosedür Tanımı Şablonu", "Bu prosedürün doküman yapısı"], ["SRÇ.001 - Dokümantasyon Süreci", "Onaylı doküman ve değişiklik kontrolü"], ["SRÇ.018 - Değişiklik Talebi Yönetimi Süreci", "Süreç etkisi doğurabilecek bilgi, standart veya mevzuat değişikliğinin değerlendirilmesi"]]),
        "<h2>6. Terimler ve Kısaltmalar</h2>", table(["Terim / Kısaltma", "Açıklama"], [["Bilgi Varlığı", "Kurumsal karar veya yeniden kullanım için değer taşıyan bilgi ya da bilgiye erişim bağlantısı"], ["Yetkili Kaynak", "Bilginin güncel ve asıl kopyasının tutulduğu sistem"], ["Bilgi Kataloğu", "Bilgi varlıklarının asgari metadata ve erişim bağlantılarını tutan LST.004"], ["Olay Bazlı Gözden Geçirme", "Bozuk bağlantı, kaynak taşınması, süreç/proje/sistem veya standart/mevzuat değişikliği gibi bir tetikleyiciyle yapılan kontrol"]]),
        "<h2>7. Roller ve Sorumluluklar</h2>", table(["Rol", "Sorumluluk", "Yetki"], [["Proje Yöneticisi", "Bilgi yönetimi stratejisini, katalog yapısını ve kayıtları sürdürmek", "Rutin kayıt oluşturma, güncelleme ve arşivleme"], ["Kalite Danışmanı", "Uluslararası standart, kalite ve süreç bilgisini izlemek ve doğrulamak", "Standart/kalite bilgisi ve süreç etkisi önerisi"], ["İlgili Uzman / Birim", "Gerektiğinde teknik veya alan bilgisini doğrulamak", "Uzmanlık alanında uygunluk görüşü"], ["Süreç / Proje / Sistem Sahibi", "Yetkili kaynağı sürdürmek ve değişikliği bildirmek", "Kendi kaynağında içerik ve erişim kararı"], ["Bilgi Kullanıcısı", "Bilgiyi kullanmak ve hata/güncellik sorunu bildirmek", "Geri bildirim ve düzeltme talebi"]]),
        "<h2>8. Genel İlkeler</h2>", table(["İlke", "Açıklama"], [["Kaynakta koruma", "Dosya ve kayıt yetkili kaynak sisteminde tutulur; katalog erişim bağlantısı sağlar."], ["Asgari bürokrasi", "Rutin katalog ekleri ayrı onay veya duyuru gerektirmez; bakım sorumluluğu Proje Yöneticisindedir."], ["Doğrulanmış bağlantı", "Kaynak ve erişim hedefi doğrulanmadan katalog satırı eklenmez."], ["Rol bazlı erişim", "Erişim sınıfı bilgilendiricidir; gerçek yetki kaynak sistem tarafından uygulanır."], ["Yaşayan katalog", "Katalog diğer süreçler ve projeler olgunlaştıkça güncellenir."], ["İzlenebilir değişiklik", "Süreç etkisi doğurabilecek standart, mevzuat veya bilgi değişikliği SRÇ.018'e aktarılır."]]),
        "<h2>9. Prosedür Esasları</h2>", table(["Esas / Kural", "Açıklama", "Zorunluluk", "Not"], [["Katalog alanları", "Bilgi başlığı, kısa açıklama, kategori, kaynak sistem, erişim bağlantısı, ilgili süreç/proje/sistem, ilgili uzman/birim, erişim sınıfı, son kontrol tarihi ve durum tutulur.", "Zorunlu", "LST.004"], ["Bilgi kategorileri", categories, "Zorunlu", "Gerektiğinde mevcut kategori içinde alt açıklama kullanılır."], ["Erişim sınıfları", "BİDB Geneli; İlgili Proje/Ekip; Yönetimle Sınırlı; Müşteri Birimiyle Paylaşımlı", "Zorunlu", "Kaynak sistem yetkisinin yerine geçmez."], ["Durumlar", "Aktif; Gözden Geçirilecek; Arşivlenmiş", "Zorunlu", "Hatalı/mükerrer kayıt dışında silme yapılmaz."], ["Doğrulama", "Teknik içerik gerektiğinde uzman/birim; standart ve kalite bilgisi Kalite Danışmanı tarafından doğrulanır.", "Koşullu", "Rutin katalog satırı resmî onay gerektirmez."], ["Yaygınlaştırma", "Rutin ek için duyuru yoktur; hedef kitleyi etkileyen önemli bilgi uygun kurumsal kanaldan paylaşılır.", "Koşullu", "Süreç dokümanı duyurusu LST.012'de izlenir."]]),
        "<h2>10. Uygulama / Strateji Matrisi</h2>", table(["Alan / Aşama", "Uygulama Kuralı", "Sorumlu", "Kayıt / Kanıt", "Not"], [["1. Bilgi adayını belirle", "Tanımlı tetikleyicilerden doğan, kalıcı değer veya yeniden kullanım potansiyeli bulunan bilgiyi seç.", "Proje Yöneticisi / Kalite Danışmanı / İlgili Sahip", "Kaynak sistem kaydı", "Her geçici iş kaydı kataloğa alınmaz."], ["2. Yetkili kaynağı doğrula", "Bilginin asıl sistemini, bağlantısını ve erişim koşulunu kontrol et.", "Proje Yöneticisi", "Doğrulanmış bağlantı", "Tahmini veya genel bağlantı kullanılmaz."], ["3. Sınıflandır", "Kategori, ilgili süreç/proje/sistem, uzman/birim ve erişim sınıfını belirle.", "Proje Yöneticisi", LST004, "Asgari metadata"], ["4. Doğrula", "Gerekiyorsa teknik içeriği ilgili uzman/birime; standart/kalite bilgisini Kalite Danışmanına doğrulat.", "İlgili Uzman / Kalite Danışmanı", "Kaynak ve katalog kaydı", "Koşullu"], ["5. Katalogla", "Yeni satır oluştur veya mevcut satırı güncelle.", "Proje Yöneticisi", LST004, "Durum Aktif veya Gözden Geçirilecek"], ["6. Paylaş", "Rutin bilgiyi katalogda erişilebilir kıl; önemli bilgiyi hedef kitleye mevcut kurumsal kanaldan duyur.", "Proje Yöneticisi / İlgili Sahip", "Confluence / doğal iletişim kaydı / koşullu LST.012", "Gereksiz duyuru üretilmez."], ["7. Gözden geçir", "Yıllık veya olay bazlı olarak bağlantı, kaynak, erişim ve güncelliği kontrol et.", "Proje Yöneticisi / Kalite Danışmanı", "Son Kontrol Tarihi / Durum", "Standart/mevzuat alanında Kalite Danışmanı katkısı"], ["8. Güncelle veya arşivle", "Geçerli bilgiyi Aktif tut; düzeltilecek bilgiyi Gözden Geçirilecek yap; geçersiz bilgiyi Arşivlenmiş yap ve ardıl bağlantıyı koru.", "Proje Yöneticisi", LST004, "Hatalı/mükerrer kayıt silinebilir."], ["9. Süreç etkisini yönlendir", "Standart, mevzuat veya bilgi değişikliği süreci etkileyebilecekse SRÇ.018'e aktar.", "Proje Yöneticisi / Kalite Danışmanı", "SRÇ.018 kaydı", "Etki analizi SRÇ.018 kapsamındadır."]]),
        "<h2>11. Yayın, Erişim ve Bakım Kuralları</h2>", table(["Kural Alanı", "Kural", "Sorumlu", "Kayıt / Kanıt"], [["Yayın", "Onaylı süreç ve prosedür Confluence'ta; bilgi varlığı kendi yetkili kaynak sisteminde tutulur.", "Proje Yöneticisi / Yayımlayan", "Confluence ve kaynak sistem geçmişi"], ["Erişim", "Katalog, erişim sınıfını gösterir; kaynağa erişim kaynak sistem kurallarına tabidir.", "Kaynak Sistem Sahibi", "Sistem yetkileri"], ["Bakım", "Katalog yılda bir kez ve olay bazlı tetikleyicilerde gözden geçirilir.", "Proje Yöneticisi / Kalite Danışmanı", "LST.004 Son Kontrol Tarihi ve Durum"], ["Duyuru", "Rutin ek duyurulmaz; önemli değişiklik hedef kitleye uygun kanaldan iletilir.", "Proje Yöneticisi / İlgili Sahip", "Doğal iletişim kaydı / koşullu LST.012"], ["Arşiv", "Geçersiz bilgi Arşivlenmiş yapılır ve varsa ardıl bağlantı korunur.", "Proje Yöneticisi", LST004]]),
        "<h2>12. Kayıtlar ve Kanıtlar</h2>", table(["Kayıt / Kanıt", "Kullanım Amacı", "Saklama Yeri", "Sorumlu", "Not"], [[LST004, "Bilgi varlıklarını ve doğrulanmış erişim bağlantılarını izlemek", "03 - Kayıtlar ve Listeler", "Proje Yöneticisi", "Yaşayan merkezi katalog"], ["Kaynak sistem kaydı", "Bilginin asıl ve güncel kopyasını korumak", "Confluence / Jira / Bitbucket / Google Drive / ilgili sistem", "Kaynak Sistem Sahibi", "Katalog içeriğin yerine geçmez."], ["LST.012 - Süreç Yaygınlaştırma ve Bilgilendirme Kaydı", "Süreç dokümanının hedef kitle bilgilendirmesini izlemek", "03 - Kayıtlar ve Listeler", "Proje Yöneticisi", "Rutin katalog satırı için kullanılmaz."], ["SRÇ.018 etki/değişiklik kaydı", "Süreç etkisi doğurabilecek değişikliği değerlendirmek", "SRÇ.018 kapsamında tanımlı ortam", "Proje Yöneticisi / Kalite Danışmanı", "Koşullu"]]),
        "<h2>13. Sürüm Geçmişi</h2>", history("Bilgi Yönetimi Prosedürü", REVIEWER, APPROVER),
    ])


def template_header(code: str, title: str, usage: str) -> str:
    return "".join(["<h2>0. Liste Hakkında</h2>", "<h3>0.1. Liste Üst Bilgisi</h3>", table(["Alan", "Değer"], [["Kurum", "İstanbul Üniversitesi - Cerrahpaşa Bilgi İşlem Daire Başkanlığı"], ["Doküman Kodu", code], ["Doküman Türü", "Liste / Kayıt Şablonu"], ["Kullanım Alanı", usage], ["Durum", "Aktif"], ["Sürüm", "v1.0"], ["Yürürlük Tarihi", "15-02-2025"], ["Güncelleme Sıklığı", "İlgili süreç veya kayıt yapısı değiştiğinde"]]), "<h3>0.2. Şablonun Kullanım Amacı</h3>", p(title), "<h3>0.3. Doküman Adlandırma Kuralı</h3>", p(usage), "<h3>0.4. Sürüm Geçmişi</h3>", history(title, REVIEWER, APPROVER)])


def lst002_template_body() -> str:
    return template_header("LST.002.Ş", "Doküman değişikliklerinin SRÇ.001'de tanımlı mevcut kayıt yapısıyla izlenmesi için kullanılır; yeni bir onay veya talep iş akışı oluşturmaz.", LST002) + "".join([
        "<h2>1. Liste Özeti</h2>", table(["Alan", "Değer"], [["Liste Kodu ve Adı", LST002], ["Kullanım Amacı", "Doküman değişikliklerini tarih, neden, etkilenen doküman, sorumlu ve durum bilgisiyle izlemek"], ["Sorumlu", "Doküman Sorumlusu / Proje Yöneticisi"], ["Durum", "<em>Aktif</em>"], ["Sürüm", "<em>v1.0</em>"], ["Son Gözden Geçirme Tarihi", "<em>GG-AA-YYYY</em>"]]),
        "<h2>2. Kullanım Değerleri</h2>", table(["Alan", "Kullanım Kuralı"], [["Kapsam", "Yeni veya güncellenen kontrollü dokümanın değişiklik kaydı."], ["Zorunlu Bilgi", "Değişiklik nedeni/özeti, tarih, etkilenen doküman, uygulayan ve durum."], ["Sürüm", "Dokümanın değişiklik öncesi ve sonrası sürümü yazılır; yeni dokümanda önceki sürüm '-' kullanılır."], ["Durum", "Kayıt, gerçek doküman değişikliğinin mevcut durumunu gösterir."]]),
        "<h2>3. Doküman Değişiklik Kayıtları</h2>", table(["Kayıt No", "Tarih", "Doküman Kodu", "Doküman Adı", "Önceki Sürüm", "Yeni Sürüm", "Değişiklik Özeti", "Talep Eden", "Uygulayan", "Durum"], [["<em>DK-YYYY-NNN</em>", "<em>GG-AA-YYYY</em>", "<em>[TÜR].[NO]</em>", "<em>Doküman Adı</em>", "<em>Sürüm / -</em>", "<em>Sürüm</em>", "<em>Değişiklik nedeni ve özeti</em>", "<em>Rol / kişi</em>", "<em>Rol / kişi</em>", "<em>Durum</em>"]]),
        "<h2>4. Sürüm Geçmişi</h2>", table(["Sürüm", "Tarih", "Açıklama", "Hazırlayan / Güncelleyen", "Gözden Geçiren", "Onay"], [["<em>v0.1</em>", "<em>GG-AA-YYYY</em>", "<em>İlk taslak</em>", PREPARED_BY, "<em>Rol / kişi</em>", "<em>Rol / kişi</em>"]]),
    ])


def lst002_body() -> str:
    rows = [
        ["DK-2026-001", "15-07-2026", "LST.002", "Doküman Değişiklik Kaydı", "Eski kayıt yapısı", "v1.0", "Eski ve kullanılmayan içerik kaldırıldı; SRÇ.001'de tanımlı değişiklik kaydı alanlarıyla yeniden oluşturuldu.", "Kalite Danışmanı", PREPARED_BY, "Tamamlandı"],
        ["DK-2026-002", "15-07-2026", "SRÇ.021", "Bilgi Yönetimi Süreci", "-", "v1.0", "RIN.3 BP1-BP6 izlenebilir süreç tanımı ve destek paketi oluşturuldu.", "Süreç Sahibi", PREPARED_BY, "Confluence'ta yayımlandı"],
        ["DK-2026-003", "15-07-2026", "PRS.005", "Bilgi Yönetimi Prosedürü", "-", "v1.0", "Bilgi seçimi, kaynakta tutma, kataloglama, erişim, yaygınlaştırma ve gözden geçirme kuralları oluşturuldu.", "Süreç Sahibi", PREPARED_BY, "Confluence'ta yayımlandı"],
        ["DK-2026-004", "15-07-2026", "LST.004", "Bilgi Kataloğu", "-", "v1.0", "Boş kod, eski gözden geçirme matrisi anlamından ayrı olarak Bilgi Kataloğu için tanımlandı; ilk doğrulanmış kayıtlar eklendi.", "Süreç Sahibi", PREPARED_BY, "Confluence'ta yayımlandı"],
    ]
    return "".join([
        "<h2>1. Liste Özeti</h2>", table(["Alan", "Değer"], [["Liste Kodu ve Adı", LST002], ["Kullanım Amacı", "Doküman değişikliklerini SRÇ.001'de tanımlı mevcut işleyişle izlemek"], ["Sorumlu", "Doküman Sorumlusu / Proje Yöneticisi"], ["Durum", "Aktif"], ["Sürüm", "v1.0"], ["Son Gözden Geçirme Tarihi", "15-07-2026"]]),
        "<h2>2. Kullanım Değerleri</h2>", table(["Alan", "Kullanım Kuralı"], [["Kapsam", "Yeni veya güncellenen kontrollü doküman değişiklikleri."], ["Zorunlu Bilgi", "Değişiklik nedeni/özeti, tarih, etkilenen doküman, uygulayan ve durum."], ["Sınır", "Bu liste yeni bir değişiklik talebi, onay veya SRÇ.018 iş akışı oluşturmaz; SRÇ.001'de tariflenen kayıt rolünü korur."]]),
        "<h2>3. Doküman Değişiklik Kayıtları</h2>", table(["Kayıt No", "Tarih", "Doküman Kodu", "Doküman Adı", "Önceki Sürüm", "Yeni Sürüm", "Değişiklik Özeti", "Talep Eden", "Uygulayan", "Durum"], rows),
        "<h2>4. Sürüm Geçmişi</h2>", history("Doküman Değişiklik Kaydı", REVIEWER, APPROVER),
    ])


def lst004_template_body() -> str:
    return template_header("LST.004.Ş", "Bilgi varlıklarının yetkili kaynaklarını, doğrulanmış erişim bağlantılarını, sınıflarını ve gözden geçirme durumlarını yönetmek için kullanılır.", LST004) + "".join([
        "<h2>1. Liste Özeti</h2>", table(["Alan", "Değer"], [["Liste Kodu ve Adı", LST004], ["Kullanım Amacı", "Bilgi varlıklarına doğrulanmış ve sınıflandırılmış erişim sağlamak"], ["Sorumlu", "Proje Yöneticisi"], ["Durum", "<em>Aktif</em>"], ["Sürüm", "<em>v1.0</em>"], ["Son Gözden Geçirme Tarihi", "<em>GG-AA-YYYY</em>"]]),
        "<h2>2. Kullanım Değerleri</h2>", table(["Alan", "Kullanım Kuralı"], [["Kategori", "Süreç ve kalite; Proje/analiz/tasarım/mimari; Yazılım/kaynak kod; Altyapı/sistem/işletim; Destek/çözüm/öğrenilmiş ders; Müşteri/toplantı/karar; Eğitim/kılavuz/görsel kayıt; Uygulanabilir Standartlar ve Mevzuat"], ["Erişim Sınıfı", "BİDB Geneli; İlgili Proje/Ekip; Yönetimle Sınırlı; Müşteri Birimiyle Paylaşımlı"], ["Durum", "Aktif; Gözden Geçirilecek; Arşivlenmiş"], ["Bağlantı", "Yalnızca doğrulanmış yetkili kaynak bağlantısı kullanılır."]]),
        "<h2>3. Bilgi Kataloğu</h2>", table(["Bilgi Başlığı", "Kısa Açıklama", "Bilgi Kategorisi", "Kaynak Sistem", "Erişim Bağlantısı", "İlgili Süreç / Proje / Sistem", "İlgili Uzman / Birim", "Erişim Sınıfı", "Son Kontrol Tarihi", "Durum"], [["<em>Bilgi başlığı</em>", "<em>Kısa açıklama</em>", "<em>Kategori</em>", "<em>Kaynak sistem</em>", "<em>Doğrulanmış bağlantı</em>", "<em>Süreç / proje / sistem</em>", "<em>Uzman / birim</em>", "<em>Erişim sınıfı</em>", "<em>GG-AA-YYYY</em>", "<em>Aktif / Gözden Geçirilecek / Arşivlenmiş</em>"]]),
        "<h2>4. Sürüm Geçmişi</h2>", table(["Sürüm", "Tarih", "Açıklama", "Hazırlayan / Güncelleyen", "Gözden Geçiren", "Onay"], [["<em>v0.1</em>", "<em>GG-AA-YYYY</em>", "<em>İlk taslak</em>", PREPARED_BY, "<em>Rol / kişi</em>", "<em>Rol / kişi</em>"]]),
    ])


def page_link(title: str) -> str:
    return f'<ac:link><ri:page ri:content-title="{html.escape(title)}" /><ac:plain-text-link-body><![CDATA[{title}]]></ac:plain-text-link-body></ac:link>'


def lst004_body(storage: bool = True) -> str:
    entries = [
        [SRC021, "BİDB bilgi varlıklarının belirlenmesi, paylaşılması ve iyileştirilmesi için süreç tanımı", "Süreç ve kalite", "Confluence", page_link(SRC021) if storage else SRC021, SRC021, "Proje Yöneticisi / Kalite Danışmanı", "BİDB Geneli", "15-07-2026", "Aktif"],
        [PRS005, "Bilgi seçimi, kaynakta tutma, kataloglama, yaygınlaştırma ve gözden geçirme kuralları", "Süreç ve kalite", "Confluence", page_link(PRS005) if storage else PRS005, SRC021, "Proje Yöneticisi / Kalite Danışmanı", "BİDB Geneli", "15-07-2026", "Aktif"],
        ["LST.001 - Aktif Dokümanlar Listesi", "Aktif kurumsal dokümanların kod, ad, sahiplik, sürüm ve konum bilgileri", "Süreç ve kalite", "Confluence", page_link("LST.001 - Aktif Dokümanlar Listesi") if storage else "LST.001 - Aktif Dokümanlar Listesi", "SRÇ.001 - Dokümantasyon Süreci", "Proje Yöneticisi / Kalite Danışmanı", "BİDB Geneli", "15-07-2026", "Aktif"],
        ["LST.006 - Standart Süreç Envanteri", "Güncel standart süreç seti, kurumsal eşleştirme, sahiplik ve durum bilgileri", "Süreç ve kalite", "Confluence", page_link("LST.006 - Standart Süreç Envanteri") if storage else "LST.006 - Standart Süreç Envanteri", "SRÇ.004 - Süreç Kurulumu Süreci", "Kalite Danışmanı / Süreç Sahipleri", "BİDB Geneli", "15-07-2026", "Aktif"],
        ["PRS.001 - Yazılım Projeleri Dokümantasyon Prosedürü", "Doküman üretim, kodlama, yayın ve sürdürme kuralları", "Süreç ve kalite", "Confluence", page_link("PRS.001 - Yazılım Projeleri Dokümantasyon Prosedürü") if storage else "PRS.001 - Yazılım Projeleri Dokümantasyon Prosedürü", "SRÇ.001 - Dokümantasyon Süreci", "Proje Yöneticisi / Kalite Danışmanı", "BİDB Geneli", "15-07-2026", "Aktif"],
        ["KLV.001 - Doküman Yazım Kuralları Talimatı", "Kurumsal doküman adlandırma, yapı ve yazım kuralları", "Süreç ve kalite", "Confluence", page_link("KLV.001 - Doküman Yazım Kuralları Talimatı") if storage else "KLV.001 - Doküman Yazım Kuralları Talimatı", "SRÇ.001 - Dokümantasyon Süreci", "Kalite Danışmanı", "BİDB Geneli", "15-07-2026", "Aktif"],
    ]
    return "".join([
        "<h2>1. Liste Özeti</h2>", table(["Alan", "Değer"], [["Liste Kodu ve Adı", LST004], ["Kullanım Amacı", "Bilgi varlıklarının yetkili kaynağına doğrulanmış ve sınıflandırılmış erişim sağlamak"], ["Sorumlu", OWNER], ["Durum", "Aktif"], ["Sürüm", "v1.0"], ["Son Gözden Geçirme Tarihi", "15-07-2026"]]),
        "<h2>2. Kullanım Değerleri</h2>", table(["Alan", "Kullanım Kuralı"], [["Kaynakta Tutma", "Bilgi kendi yetkili kaynak sisteminde tutulur; katalog erişim bağlantısı ve metadata sağlar."], ["Bağlantı", "Yalnızca doğrulanmış tam hedef bağlantıları kaydedilir. Jira, Bitbucket ve Google Drive satırları doğru hedef bağlantıları elde edildikçe eklenir."], ["Sahiplik", "Katalog bakımı Proje Yöneticisindedir; ilgili uzman/birim alanı bilgi kaynağını gösterir, katalog bakım sorumluluğu doğurmaz."], ["Bakım", "Yıllık toplu ve olay bazlı gözden geçirme uygulanır."]]),
        "<h2>3. Bilgi Kataloğu</h2>", table(["Bilgi Başlığı", "Kısa Açıklama", "Bilgi Kategorisi", "Kaynak Sistem", "Erişim Bağlantısı", "İlgili Süreç / Proje / Sistem", "İlgili Uzman / Birim", "Erişim Sınıfı", "Son Kontrol Tarihi", "Durum"], entries, fixed=True),
        "<h2>4. Sürüm Geçmişi</h2>", history("Bilgi Kataloğu", REVIEWER, APPROVER),
    ])


def update_lst006() -> None:
    page = CONFLUENCE / LST006_REL
    for name in ("body.storage.xhtml", "body.view.html"):
        path = page / name
        doc = path.read_text(encoding="utf-8")
        def repl(match: re.Match[str]) -> str:
            row = match.group(0)
            plain = html.unescape(re.sub(r"<[^>]+>", "", row))
            if "SRÇ.021" not in plain:
                return row
            cells = re.findall(r"(<td[^>]*>)(.*?)(</td>)", row, flags=re.I | re.S)
            values = ["RIN.3", "Knowledge management", "SRÇ.021", "Bilgi Yönetimi Süreci", OWNER, "Aktif", "Süreç paketi oluşturulmuş, Confluence'ta yayımlanmış ve süreç özel kayıtlarıyla yönetilmektedir."]
            return "<tr>" + "".join(f"{a}{html.escape(v)}{c}" for (a, _, c), v in zip(cells, values)) + "</tr>"
        updated = re.sub(r"<tr[^>]*>.*?</tr>", repl, doc, flags=re.I | re.S)
        path.write_text(updated, encoding="utf-8")


def section_upsert(doc: str, heading_fragment: str, code: str, cells: list[str]) -> str:
    heads = list(re.finditer(r"<h2[^>]*>(.*?)</h2>", doc, flags=re.I | re.S))
    for i, h in enumerate(heads):
        title = html.unescape(re.sub(r"<[^>]+>", "", h.group(1)))
        if heading_fragment not in title:
            continue
        end = heads[i + 1].start() if i + 1 < len(heads) else len(doc)
        section = doc[h.end():end]
        tbody = re.search(r"(<tbody[^>]*>)(.*?)(</tbody>)", section, flags=re.I | re.S)
        if not tbody:
            raise RuntimeError(f"No table body under {heading_fragment}")
        rows = re.findall(r"<tr[^>]*>.*?</tr>", tbody.group(2), flags=re.I | re.S)
        rows = [r for r in rows if code not in html.unescape(re.sub(r"<[^>]+>", "", r))]
        new_row = "<tr>" + "".join(f'<td class="confluenceTd">{html.escape(x)}</td>' for x in cells) + "</tr>"
        new_body = "".join(rows) + new_row
        section = section[:tbody.start(2)] + new_body + section[tbody.end(2):]
        return doc[:h.end()] + section + doc[end:]
    raise RuntimeError(f"Section not found: {heading_fragment}")


def update_lst001() -> None:
    page = PAGE_ROOT / "03-kayitlar-ve-listeler/lst-001-aktif-dokumanlar-listesi"
    storage = (page / "body.storage.xhtml").read_text(encoding="utf-8")
    storage = section_upsert(storage, "3. Süreç Dokümanları", "SRÇ.021", ["SRÇ.021", "Bilgi Yönetimi Süreci", "RIN.3", OWNER, "Aktif", "v1.0", "15-02-2025", "01 - Süreç Dokümanları"])
    for code, name, scope in [
        ("LST.002", "Doküman Değişiklik Kaydı", "SRÇ.001 kontrollü doküman değişiklik kaydı"),
        ("LST.004", "Bilgi Kataloğu", "SRÇ.021 bilgi varlığı erişim ve durum kataloğu"),
    ]:
        storage = section_upsert(storage, "7. Genel Kayıt ve Listeler", code, [code, name, scope, OWNER if code.endswith("004") else "Doküman Sorumlusu / Proje Yöneticisi", "Aktif", "v1.0", "03 - Kayıtlar ve Listeler"])
    for code, name, usage in [
        ("LST.002.Ş", "Doküman Değişiklik Kaydı Şablonu", "LST.002 üretimi"),
        ("LST.004.Ş", "Bilgi Kataloğu Şablonu", "LST.004 üretimi"),
    ]:
        storage = section_upsert(storage, "6. Şablonlar", code, [code, name, usage, "Aktif", "v1.0", "15-02-2025", "02 - Şablonlar"])
    storage = section_upsert(storage, "4. Prosedürler", "PRS.005", ["PRS.005", "Bilgi Yönetimi Prosedürü", "SRÇ.021", OWNER, "Aktif", "v1.0", "15-02-2025", "07 - Prosedürler"])
    (page / "body.storage.xhtml").write_text(storage, encoding="utf-8")
    (page / "body.view.html").write_text(build_view("LST.001 - Aktif Dokümanlar Listesi", storage), encoding="utf-8")


def update_parent_registers(pages: list[Path]) -> None:
    template_doc = template_register_body()
    tbody = re.search(r"(<tbody[^>]*>)(.*?)(</tbody>)", template_doc, flags=re.I | re.S)
    if not tbody:
        raise RuntimeError("Template register table body not found")
    rows = re.findall(r"<tr[^>]*>.*?</tr>", tbody.group(2), flags=re.I | re.S)
    rows = [r for r in rows if not any(code in html.unescape(re.sub(r"<[^>]+>", "", r)) for code in ("LST.002.Ş", "LST.004.Ş"))]
    additions = []
    for code, name, title in [
        ("LST.002.Ş", "Doküman Değişiklik Kaydı Şablonu", "LST.002.Ş - Doküman Değişiklik Kaydı Şablonu"),
        ("LST.004.Ş", "Bilgi Kataloğu Şablonu", "LST.004.Ş - Bilgi Kataloğu Şablonu"),
    ]:
        number = str(len(rows) + len(additions) + 1)
        additions.append("<tr>" + "".join(f'<td class="confluenceTd">{cell}</td>' for cell in [number, html.escape(code), html.escape(name), "Aktif", page_link(title)]) + "</tr>")
    template_doc = template_doc[:tbody.start(2)] + "".join(rows + additions) + template_doc[tbody.end(2):]
    template_dir = PAGE_ROOT / "02-sablonlar"
    (template_dir / "body.storage.xhtml").write_text(template_doc + "\n", encoding="utf-8")
    (template_dir / "body.view.html").write_text(build_view("02 - Şablonlar", template_doc), encoding="utf-8")
    procedures = parent_register_body("Prosedür", [("PRS.001", "Yazılım Projeleri Dokümantasyon Prosedürü", "PRS.001 - Yazılım Projeleri Dokümantasyon Prosedürü"), ("PRS.002", "Süreç Tasarım Prosedürü", "PRS.002 - Süreç Tasarım Prosedürü"), ("PRS.003", "Süreç Değerlendirme Prosedürü", "PRS.003 - Süreç Değerlendirme Prosedürü"), ("PRS.004", "Süreç İyileştirme ve Değişiklik Yönetimi Prosedürü", "PRS.004 - Süreç İyileştirme ve Değişiklik Yönetimi Prosedürü"), ("PRS.005", "Bilgi Yönetimi Prosedürü", PRS005)])
    proc_dir = PAGE_ROOT / "07-prosedurler"
    (proc_dir / "body.storage.xhtml").write_text(procedures + "\n", encoding="utf-8")
    (proc_dir / "body.view.html").write_text(build_view("07 - Prosedürler", procedures), encoding="utf-8")
    record_items = []
    for child in sorted((PAGE_ROOT / "03-kayitlar-ve-listeler").iterdir()):
        meta = child / "page.yaml"
        if not meta.exists():
            continue
        title = (yaml.safe_load(meta.read_text(encoding="utf-8")) or {}).get("title", "")
        match = re.match(r"(İÜC\.BİDB\.LST\.\d{3})\s+-\s+(.+)", title)
        if match:
            record_items.append((match.group(1), match.group(2), title))
    records = parent_register_body("Liste / Kayıt", record_items)
    records_dir = PAGE_ROOT / "03-kayitlar-ve-listeler"
    (records_dir / "body.storage.xhtml").write_text(records + "\n", encoding="utf-8")
    (records_dir / "body.view.html").write_text(build_view("03 - Kayıtlar ve Listeler", records), encoding="utf-8")
    pages.extend([template_dir, proc_dir, records_dir])


def replace_section(doc: str, heading: str, body: str) -> str:
    heads = list(re.finditer(r"<h2[^>]*>(.*?)</h2>", doc, flags=re.I | re.S))
    for i, h in enumerate(heads):
        title = html.unescape(re.sub(r"<[^>]+>", "", h.group(1))).strip()
        if title == heading:
            end = heads[i + 1].start() if i + 1 < len(heads) else len(doc)
            return doc[:h.end()] + body + doc[end:]
    raise RuntimeError(f"RPR section not found: {heading}")


def update_rpr001() -> None:
    page = CONFLUENCE / RPR001_REL
    storage = html.unescape((page / "body.storage.xhtml").read_text(encoding="utf-8"))
    storage = storage.replace("SRÇ.001, SRÇ.004, SRÇ.005 ve SRÇ.006 değerlendirmeleri", "SRÇ.001, SRÇ.004, SRÇ.005, SRÇ.006 ve SRÇ.021 değerlendirmeleri")
    storage = storage.replace("<td class=\"confluenceTd\">14-07-2026</td>", "<td class=\"confluenceTd\">15-07-2026</td>", 1)
    summary_rows = [
        ["SRÇ.001 - Dokümantasyon Süreci", "SUP.7 BP1-BP8; PA 2.1-PA 3.2", "5 VAR; 3 DAĞINIK", "9 VAR; 9 DAĞINIK; 3 ZAYIF", "FRM.001 - Süreç Gözden Geçirme Formu (SRÇ.001) - Değerlendirme #1", "Doküman standartları, şablonlar ve teknik yayın/bakım yapısı güçlü; formal gözden geçirme, gerçek ölçüm, yetkinlik ve bilgilendirme kanıtları geliştirilmelidir."],
        ["SRÇ.004 - Süreç Kurulumu Süreci", "PIM.1 BP1-BP6; PA 2.1-PA 3.2", "4 VAR; 1 DAĞINIK; 1 YOK", "10 VAR; 7 DAĞINIK; 1 ZAYIF; 3 YOK", "FRM.001 - Süreç Gözden Geçirme Formu (SRÇ.004) - Değerlendirme #1", "Süreç mimarisi, paketler, uyarlama, rol ve ölçüm tanımları güçlü; gerçek kullanım, bilgilendirme ve yetkinlik kanıtları eksiktir."],
        ["SRÇ.005 - Süreç Değerlendirme Süreci", "PIM.2 BP1-BP8; PA 2.1-PA 3.2", "6 VAR; 2 DAĞINIK", "11 VAR; 7 DAĞINIK; 2 ZAYIF; 1 YOK", "FRM.001 - Süreç Gözden Geçirme Formu (SRÇ.005) - Değerlendirme #1", "Değerlendirme yöntemi, plan, etiketler, iş ürünleri ve raporlama tanımlı; gerçek dönem taahhütleri, doğrulama, eğitim ve performans sonuçları tamamlanmalıdır."],
        ["SRÇ.006 - Süreç İyileştirme Süreci", "PIM.3 BP1-BP9; PA 2.1-PA 3.2", "4 VAR; 2 DAĞINIK; 3 ZAYIF", "11 VAR; 7 DAĞINIK; 2 ZAYIF; 1 YOK", "FRM.001 - Süreç Gözden Geçirme Formu (SRÇ.006) - Değerlendirme #1", "Tek SRÇ.018 girişi, hedef/öncelik, planlama, yetki, doğrulama ve yeniden kullanım tanımlı; gerçek uygulama ve sonuç kanıtları beklenmektedir."],
        [SRC021, "RIN.3 BP1-BP6; PA 2.1-PA 3.2", "2 VAR; 3 DAĞINIK; 1 ZAYIF", "12 VAR; 6 DAĞINIK; 2 ZAYIF; 1 YOK", "FRM.001 - Süreç Gözden Geçirme Formu (SRÇ.021) - Değerlendirme #1", "Kaynak sistem, bağlantı ağı, sahiplik, katalog şeması ve bakım kuralları tanımlı; gerçek katalog kapsamı, uzman ağı, yaygınlaştırma ve performans kanıtları olgunlaştırılmalıdır."],
    ]
    storage = replace_section(storage, "4. Süreç Sonuç Özeti", table(["Süreç", "Değerlendirme Kapsamı", "BP Dağılımı", "PA / GP Dağılımı", "Değerlendirme Bağlantısı", "Özet"], summary_rows))
    trends = [["BP - VAR", "5", "4", "6", "4", "2", "Tanım, yöntem ve yönetişim bileşenleri oluşturulan alanlarda güçlü karşılama vardır."], ["BP - DAĞINIK", "3", "1", "2", "2", "3", "Gerçek uygulama, uzman ağı ve yaygınlaştırma kanıtları henüz sistematik değildir."], ["BP - ZAYIF", "0", "0", "0", "3", "1", "SRÇ.021 katalog gözden geçirme ve iyileştirme kanıtı henüz oluşmamıştır."], ["BP - YOK", "0", "1", "0", "0", "0", "SRÇ.004 kullanım verisi henüz oluşmamıştır."], ["PA/GP - VAR", "9", "10", "11", "11", "12", "Tanım, rol, iş ürünü, etkileşim ve altyapı bileşenleri güçlenmektedir."], ["PA/GP - DAĞINIK", "9", "7", "7", "7", "6", "Gerçek uygulama ve formal kayıt bütünlüğü ortak gelişim alanıdır."], ["PA/GP - ZAYIF", "3", "1", "2", "2", "2", "Performans ayarlama ve gerçek veri analizi başlangıç düzeyindedir."], ["PA/GP - YOK", "0", "3", "1", "1", "1", "Yetkinlik/eğitim ve bazı gerçek kullanım kanıtları eksiktir."]]
    storage = replace_section(storage, "5. Etiket Dağılımları ve Eğilimler", table(["Gösterge", "SRÇ.001", "SRÇ.004", "SRÇ.005", "SRÇ.006", "SRÇ.021", "Yorum"], trends))
    from update_rpr001_layout_and_maturity_placeholder import align_rpr001_layout
    storage = align_rpr001_layout(storage)
    (page / "body.storage.xhtml").write_text(storage, encoding="utf-8")
    (page / "body.view.html").write_text(build_view("RPR.001 - Süreç Performansları Raporu", storage), encoding="utf-8")


def refresh_parent_counts() -> None:
    index = yaml.safe_load(INDEX_PATH.read_text(encoding="utf-8")) or {}
    pages = index.get("pages", [])
    for page in [CONFLUENCE / SRC021_REL, PAGE_ROOT / "03-kayitlar-ve-listeler"]:
        meta_path = page / "page.yaml"
        meta = yaml.safe_load(meta_path.read_text(encoding="utf-8")) or {}
        stable_id = str(meta.get("page_id") or f"local:{meta.get('relative_path')}")
        meta["children_count"] = sum(1 for item in pages if str(item.get("parent_id") or "") == stable_id)
        meta_path.write_text(yaml.safe_dump(meta, allow_unicode=True, sort_keys=False), encoding="utf-8")


def update_context_docs() -> None:
    current = PAGE_ROOT.parents[2] / "docs/CURRENT_STATUS.md"
    text = current.read_text(encoding="utf-8")
    marker = "- SRÇ.006 yayınının LST.012 altında gerçek Confluence bağlantısıyla kaydedilmesi ve LST.006 üzerindeki yayın durumunun güncellenmesi\n"
    addition = "- SRÇ.021 Bilgi Yönetimi paketinin süreç tanımı, LST.007-LST.010, boş FRM.001 ve Değerlendirme #1 ile yerelde oluşturulması; PRS.005, LST.004 Bilgi Kataloğu ve şablonu ile LST.002 Doküman Değişiklik Kaydı/şablonunun hazırlanması. Confluence yayını kullanıcı onayı ve VPN sonrasına bırakılmıştır.\n"
    if addition not in text:
        text = text.replace(marker, marker + addition)
        current.write_text(text, encoding="utf-8")
    decisions = PAGE_ROOT.parents[2] / "docs/DECISIONS.md"
    text = decisions.read_text(encoding="utf-8")
    old = "- `LST.004` yeni yaklaşımda kullanılmaz. Repository'deki mevcut `LST.004` sayfaları legacy kayıttır; açık onay olmadan silinmez veya taşınmaz."
    new = "- Eski `LST.004 - Süreç Gözden Geçirme Matrisi` yaklaşımı kullanılmaz. Boşa çıkan `LST.004` kodu kullanıcı onayıyla SRÇ.021 kapsamında `LST.004 - Bilgi Kataloğu` olarak yeniden tanımlanmıştır; eski legacy anlamına dönülmez."
    text = text.replace(old, new)
    heading = "\n## SRÇ.021 bilgi yönetimi yaklaşımı\n"
    if heading not in text:
        text += heading + "\n- Confluence bilgi ağının başlangıç noktasıdır; Jira, Bitbucket ve Google Drive dahil kaynak sistemlerdeki asıl bilgiler kopyalanmaz, doğrulanmış bağlantılarla erişilebilir kılınır.\n- LST.004 Bilgi Kataloğu Proje Yöneticisi tarafından sürdürülür; Kalite Danışmanı standart/kalite bilgisinde ana katkı rolüdür; ilgili uzman/birim alanı katalog bakım sorumluluğu doğurmaz.\n- Katalogda yalnızca doğrulanmış hedef bağlantıları kullanılır; diğer süreçler tamamlandıkça katalog yaşayan kayıt olarak genişletilir.\n- Rutin katalog ekleri ayrı resmî onay veya LST.012 kaydı gerektirmez. Hedef kitleyi etkileyen süreç dokümanı ve önemli değişiklikler uygun kurumsal kanaldan duyurulur; süreç dokümanı yaygınlaştırması LST.012'de izlenir.\n- Katalog yılda bir kez ve olay bazlı tetikleyicilerde gözden geçirilir. LST.009'da yalnızca geçerli bağlantı oranı ve yıllık gözden geçirme tamamlama oranı izlenir; kayıt sayısı performans göstergesi değildir.\n- Standart veya mevzuat değişikliğinin süreç etkisi ihtimali varsa konu SRÇ.018'e aktarılır.\n"
    decisions.write_text(text, encoding="utf-8")


def validate(page_dirs: list[Path]) -> None:
    process = (CONFLUENCE / SRC021_REL / "body.storage.xhtml").read_text(encoding="utf-8")
    headings = [html.unescape(re.sub(r"<[^>]+>", "", h)) for h in re.findall(r"<h2[^>]*>(.*?)</h2>", process, flags=re.S)]
    expected = ["1. Süreç Bilgileri", "2. Amaç", "3. Kapsam", "4. Referanslar", "5. Terimler ve Kısaltmalar", "6. Süreç Aktivitesi", "7. Roller ve Sorumluluklar", "8. Araçlar ve Altyapı", "9. Süreç İş Ürünleri", "10. Süreç Akışı", "11. Süreç Faaliyetleri", "12. Ölçüm ve İzleme", "13. Uygulama ve Uyarlama Kuralları", "14. Süreç Etkileşimleri", "15. Sürüm Geçmişi"]
    if headings != expected:
        raise RuntimeError(f"SRÇ.021 heading mismatch: {headings}")
    refs = process.split("<h2>4. Referanslar</h2>", 1)[1].split("<h2>5.", 1)[0]
    if len(re.findall(r"<tr>", refs)) != 4:
        raise RuntimeError("SRÇ.021 must contain exactly three process references")
    for bp, _, _ in RIN3_BPS:
        if bp not in process:
            raise RuntimeError(f"Missing BP trace: {bp}")
    if any(term in process for term in ["26 süreç", "Soru Bankası"]):
        raise RuntimeError("Forbidden fixed count or project-specific name in SRÇ.021")
    for page in page_dirs:
        for name in ("page.yaml", "body.storage.xhtml", "body.view.html"):
            if not (page / name).exists():
                raise RuntimeError(f"Missing page artifact: {page / name}")
    assessment = (CONFLUENCE / REVIEWS_REL / "frm-001-surec-gozden-gecirme-formu-src-021-degerlendirme-1/body.storage.xhtml").read_text(encoding="utf-8")
    if "2 VAR, 3 DAĞINIK ve 1 ZAYIF" not in assessment or "12 VAR, 6 DAĞINIK, 2 ZAYIF ve 1 YOK" not in assessment:
        raise RuntimeError("Assessment distribution mismatch")
    lst004 = (CONFLUENCE / RECORDS_REL / "lst-004-bilgi-katalogu/body.storage.xhtml").read_text(encoding="utf-8")
    if "Jira, Bitbucket ve Google Drive satırları" not in lst004 or "Bilgi Başlığı" not in lst004:
        raise RuntimeError("LST.004 verified-link rule/schema missing")


def write_report() -> None:
    report = PAGE_ROOT.parents[2] / "reports/src021_knowledge_management_package_report.md"
    report.write_text("""# SRÇ.021 Bilgi Yönetimi Paketi Yerel Raporu

Tarih: 15-07-2026

## Oluşturulan / Güncellenen Yapı

- SRÇ.021 süreç tanımı RIN.3 BP1-BP6 izlenebilirliğiyle oluşturuldu.
- Süreç özel LST.007, LST.008, LST.009, LST.010 ve boş FRM.001 hazırlandı.
- SRÇ.021 Değerlendirme #1 yalnızca gerekçeli etiket yaklaşımıyla oluşturuldu.
- PRS.005 Bilgi Yönetimi Prosedürü, LST.004 Bilgi Kataloğu ve LST.004.Ş şablonu oluşturuldu.
- LST.002 Doküman Değişiklik Kaydı, SRÇ.001'deki mevcut işleyişi değiştirmeden yenilendi; LST.002.Ş eklendi.
- LST.001, LST.006, RPR.001, merkez sayfalar ve kalıcı karar/durum dokümanları güncellendi.

## Değerlendirme Özeti

- BP: 2 VAR, 3 DAĞINIK, 1 ZAYIF.
- PA/GP: 12 VAR, 6 DAĞINIK, 2 ZAYIF, 1 YOK.
- Sayısal puan veya tek genel süreç etiketi kullanılmadı.

## Yayın Durumu

- Bu çalışma yalnızca yerel repository ve viewer için hazırlanmıştır.
- Confluence'a yazma yapılmamıştır; kullanıcı incelemesi ve VPN sonrası kontrollü dry-run beklenmektedir.
""", encoding="utf-8")


def main() -> None:
    src = CONFLUENCE / SRC021_REL
    attachments = src / "attachments"
    attachments.mkdir(parents=True, exist_ok=True)
    (attachments / FLOW_MMD).write_text("\n".join(FLOW_LINES) + "\n", encoding="utf-8")
    write_page(src, SRC021, "137265784", "01 - Süreç Dokümanları", 2, process_body(True), process_body(False))
    pages: list[Path] = [src]
    children = [
        ("lst-007-surec-etkilesim-matrisi-src-021", "LST.007 - Süreç Etkileşim Matrisi (SRÇ.021)", lst007_body(True), lst007_body(False)),
        ("lst-008-is-urunleri-ve-kalite-kriterleri-listesi-src-021", "LST.008 - İş Ürünleri ve Kalite Kriterleri Listesi (SRÇ.021)", lst008_body(), None),
        ("lst-009-surec-performans-olcum-seti-src-021", "LST.009 - Süreç Performans Ölçüm Seti (SRÇ.021)", lst009_body(), None),
        ("lst-010-surec-rol-yetki-ve-raci-matrisi-src-021", "LST.010 - Süreç Rol Yetki ve RACI Matrisi (SRÇ.021)", lst010_body(), None),
    ]
    for slug, title, storage, view in children:
        page = src / slug
        write_page(page, title, SRC021_ID, SRC021, 3, storage, view)
        pages.append(page)
        if "lst-007" in slug:
            assets = page / "attachments"
            assets.mkdir(exist_ok=True)
            (assets / INTERACTION_MMD).write_text("\n".join(INTERACTION_LINES) + "\n", encoding="utf-8")
    blank = src / "frm-001-surec-gozden-gecirme-formu-src-021"
    write_page(blank, "FRM.001 - Süreç Gözden Geçirme Formu (SRÇ.021)", SRC021_ID, SRC021, 3, blank_review_body())
    pages.append(blank)
    assessment = CONFLUENCE / REVIEWS_REL / "frm-001-surec-gozden-gecirme-formu-src-021-degerlendirme-1"
    write_page(assessment, "FRM.001 - Süreç Gözden Geçirme Formu (SRÇ.021) - Değerlendirme #1", REVIEWS_ID, "Süreç Gözden Geçirmeleri", 3, assessment_body())
    pages.append(assessment)
    prs = CONFLUENCE / PROCEDURES_REL / "prs-005-bilgi-yonetimi-proseduru"
    write_page(prs, PRS005, PROCEDURES_ID, "07 - Prosedürler", 2, procedure_body())
    pages.append(prs)
    lst002_t = CONFLUENCE / TEMPLATES_REL / "lst-002-s-dokuman-degisiklik-kaydi-sablonu"
    write_page(lst002_t, "LST.002.Ş - Doküman Değişiklik Kaydı Şablonu", TEMPLATES_ID, "02 - Şablonlar", 2, lst002_template_body())
    pages.append(lst002_t)
    lst004_t = CONFLUENCE / TEMPLATES_REL / "lst-004-s-bilgi-katalogu-sablonu"
    write_page(lst004_t, "LST.004.Ş - Bilgi Kataloğu Şablonu", TEMPLATES_ID, "02 - Şablonlar", 2, lst004_template_body())
    pages.append(lst004_t)
    lst002 = CONFLUENCE / RECORDS_REL / "lst-002-dokuman-degisiklik-kaydi"
    write_page(lst002, LST002, RECORDS_ID, "03 - Kayıtlar ve Listeler", 2, lst002_body())
    pages.append(lst002)
    lst004 = CONFLUENCE / RECORDS_REL / "lst-004-bilgi-katalogu"
    write_page(lst004, LST004, RECORDS_ID, "03 - Kayıtlar ve Listeler", 2, lst004_body(True), lst004_body(False))
    pages.append(lst004)
    update_lst006()
    update_lst001()
    update_rpr001()
    pages.extend([CONFLUENCE / LST006_REL, PAGE_ROOT / "03-kayitlar-ve-listeler/lst-001-aktif-dokumanlar-listesi", CONFLUENCE / RPR001_REL])
    update_parent_registers(pages)
    update_context_docs()
    unique = list(dict.fromkeys(pages))
    upsert_index(unique)
    refresh_parent_counts()
    validate(unique)
    write_report()
    print(f"[DONE] SRÇ.021 package materialized: {len(unique)} page directories")


if __name__ == "__main__":
    main()
