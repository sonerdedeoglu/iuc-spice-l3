#!/usr/bin/env python3
"""Create the local SRÇ.024 quality-management package.

The script is local-only. It never calls Confluence APIs and preserves existing
page ids. New pages receive empty ids until a reviewed publication.
"""
from __future__ import annotations

import html
import re
from datetime import datetime, timezone
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
    REVIEWS_ID,
    REVIEWS_REL,
    TEMPLATES_ID,
    TEMPLATES_REL,
    build_view,
    history,
    info_macro,
    info_view,
    table,
    write_page,
)
from align_lst010_to_src006_structure import process_body as raci_body


ROOT = Path(__file__).resolve().parents[1]
SRC024_ID = "137265882"
SRC024 = "SRÇ.024 - Kalite Yönetimi Süreci"
PRS007 = "PRS.007 - Kalite Yönetimi Prosedürü"
PRS008 = "PRS.008 - Müşteri Memnuniyeti Prosedürü"
FRM003_TEMPLATE = "FRM.003.Ş - Müşteri Memnuniyeti Anketi Şablonu"
RPR002_TEMPLATE = "RPR.002.Ş - Proje Müşteri Memnuniyeti Değerlendirme Raporu Şablonu"
OWNER = "Mustafa Nusret SARISAKAL - Bilgi İşlem Daire Başkanı"
REVIEWER = "Seçil NEBİLER - İdari İşler Şube Müdürü"
APPROVER = OWNER
RESULT_REVIEWER = "Proje Yöneticisi"

SRC024_REL = f"{PAGE_ROOT_REL}/01-surec-dokumanlari/src-024-kalite-yonetimi-sureci"
RECORDS_REL = f"{PAGE_ROOT_REL}/03-kayitlar-ve-listeler"
LST001_REL = f"{RECORDS_REL}/lst-001-aktif-dokumanlar-listesi"
LST006_REL = f"{RECORDS_REL}/lst-006-standart-surec-envanteri"
RPR001_REL = f"{PAGE_ROOT_REL}/09-raporlar/rpr-001-surec-performanslari-raporu"

FLOW_PNG = "SRÇ.024 - Flowchart.png"
FLOW_MMD = "src024-surec-akisi.mmd"
INTERACTION_PNG = "src024-surec-etkilesim.png"
INTERACTION_MMD = "src024-surec-etkilesim.mmd"

MAN4_BPS = [
    ("MAN.4.BP1", "Kalite hedeflerini belirle", "Müşterinin açık ve örtük kalite gereksinimlerinden kurumsal, ürün ve süreç kalite hedeflerini belirlemek."),
    ("MAN.4.BP2", "Genel stratejiyi tanımla", "Tanımlanan hedeflere ulaşmak için gerekli kaynak ve sorumlulukları içeren genel kalite stratejisini oluşturmak."),
    ("MAN.4.BP3", "Kalite kriterlerini tanımla", "Kalite hedeflerinin başarısını ölçmek ve doğrulamak için standart, referans, ölçüm ve kabul kriterlerini belirlemek."),
    ("MAN.4.BP4", "Kalite yönetim sistemini kur", "Düzeltici ve önleyici faaliyetleri planlayacak, uygulayacak, izleyecek ve kontrol edecek kalite yönetim sistemini kurmak ve sürdürmek."),
    ("MAN.4.BP5", "Kalite hedeflerinin gerçekleşmesini değerlendir", "Kalite hedeflerinin gerçekleşmesini tanımlı kriterlerle düzenli olarak yönetim seviyesinde değerlendirmek ve uygun kararları almak."),
    ("MAN.4.BP6", "Düzeltici veya önleyici faaliyet başlat", "Kalite hedefleri karşılanmadığında proje ve kurumsal düzeyde uygun düzeltici veya önleyici faaliyeti başlatmak."),
    ("MAN.4.BP7", "Geri bildirim topla", "Kalitenin sürekli iyileştirilmesi için müşteri, proje, süreç ve personel geri bildirimlerini toplamak."),
    ("MAN.4.BP8", "Gerçek kalite performansını izle", "Kalitenin gerçekleşen performansını kalite hedeflerine göre ölçmek ve izlemek."),
]

FLOW_LINES = [
    "%%{init: {'flowchart': {'htmlLabels': false}}}%%",
    "flowchart TD",
    'A["Müşteri gereksinimleri, standartlar, süreç ve proje girdileri"] --> B["Kurumsal kalite hedefleri ve stratejisi belirlenir"]',
    'B --> C["Kalite kriterleri, sorumluluklar ve ölçümler tanımlanır"]',
    'C --> D["Kalite güvence, süreç ve proje uygulamalarından veriler toplanır"]',
    'D --> E["Müşteri, proje, süreç ve personel geri bildirimleri derlenir"]',
    'E --> F["Kalite Danışmanı sonuçları analiz eder"]',
    'F --> G["Proje Yöneticisi sonuçları operasyonel olarak gözden geçirir"]',
    'G --> H{"Kalite uygunsuzluğu var mı?"}',
    'H -- "Evet" --> I["SRÇ.017 Problem Çözüm ve kök neden analizi"]',
    'I --> J{"Değişiklik gerekli mi?"}',
    'J -- "Evet" --> K["SRÇ.018 Değişiklik Talebi Yönetimi"]',
    'J -- "Hayır" --> L["Düzeltici faaliyet sonucu izlenir"]',
    'H -- "Hayır" --> M["Kalite sonuçları yıllık değerlendirmeye hazırlanır"]',
    'K --> M',
    'L --> M',
    'M --> N["Haziran-Temmuz YGG değerlendirmesi"]',
    'N --> O["Kalite hedefleri ve iyileştirme kararları güncellenir"]',
    'O --> B',
]

INTERACTION_LINES = [
    "%%{init: {'flowchart': {'htmlLabels': false}}}%%",
    "flowchart LR",
    'A["Müşteri ve proje gereksinimleri"] --> Q["SRÇ.024 Kalite Yönetimi"]',
    'B["SRÇ.002 kalite güvence sonuçları"] --> Q',
    'C["SRÇ.005 süreç değerlendirmeleri"] --> Q',
    'D["SRÇ.023 YGG girdileri ve kararları"] --> Q',
    'E["Standart, mevzuat, LST.009 ve proje kayıtları"] --> Q',
    'Q --> P1["PRS.007 Kalite Yönetimi Prosedürü"]',
    'Q --> P2["PRS.008 Müşteri Memnuniyeti Prosedürü"]',
    'P2 --> F["FRM.003 müşteri memnuniyeti anket kayıtları"]',
    'F --> R["RPR.002 proje müşteri memnuniyeti raporu"]',
    'Q --> G["SRÇ.017 kalite uygunsuzlukları ve kök neden"]',
    'G --> H["SRÇ.018 gerekli değişiklikler"]',
    'Q --> I["SRÇ.006 iyileştirme girdileri"]',
    'Q --> J["SRÇ.023 yıllık YGG"]',
]


def para(value: str) -> str:
    return f"<p>{html.escape(value)}</p>"


def image(storage: bool, filename: str, alt: str, width: int = 900) -> str:
    if storage:
        return f'<p><ac:image ac:width="{width}"><ri:attachment ri:filename="{html.escape(filename)}" /></ac:image></p>'
    return f'<p style="text-align:center"><img class="diagram" src="attachments/{quote(filename)}" alt="{html.escape(alt)}" /></p>'


def process_body(storage: bool) -> str:
    related = "<br />".join([
        "SRÇ.002 - Kalite Güvencesi Süreci",
        "SRÇ.005 - Süreç Değerlendirme Süreci",
        "SRÇ.006 - Süreç İyileştirme Süreci",
        "SRÇ.007 - Proje Yönetimi Süreci",
        "SRÇ.015 - Ürün Yayınlama / Sürüm Süreci",
        "SRÇ.017 - Problem Çözüm Yönetimi Süreci",
        "SRÇ.018 - Değişiklik Talebi Yönetimi Süreci",
        "SRÇ.021 - Bilgi Yönetimi Süreci",
        "SRÇ.023 - Organizasyonel Yönetim Süreci",
        "SRÇ.025 - Ölçüm Süreci",
        "SRÇ.026 - Denetim Süreci",
    ])
    mermaid = info_macro("Mermaid Kodu", FLOW_LINES) if storage else info_view("Mermaid Kodu", FLOW_LINES)
    activities = [
        ["F1", "Kalite hedeflerini belirle", "Müşteri gereksinimleri ile mevzuat, standart, süreç ve proje beklentilerinden kurumsal ortak kalite hedefleri belirlenir. Proje özel hedefler SRÇ.002 kalite planlarında türetilir. (MAN.4.BP1)", f"{SRC024}; proje/süreç kalite hedefleri"],
        ["F2", "Kalite stratejisini tanımla", "Hedeflere ulaşmak için sorumluluk, kaynak, yıllık döngü ve karar yapısı belirlenir. Kalite Danışmanı koordinasyonu yürütür; Proje Yöneticisi sonuçları gözden geçirir. (MAN.4.BP2)", PRS007],
        ["F3", "Kalite kriterlerini tanımla", "ISO/IEC 15504-5, mevzuat, standartlar, müşteri gereksinimleri, süreç dokümanları, proje kabul kriterleri ve LST.009 ölçümleri esas alınır. (MAN.4.BP3)", "LST.008; LST.009; proje kabul kriterleri"],
        ["F4", "Kalite yönetim sistemini işlet", "Süreç tanımları, kalite planları, güvence/değerlendirme kayıtları, performans ölçümleri, YGG ve problem/değişiklik mekanizmaları bütünleşik olarak işletilir. Ayrı bir kalite el kitabı oluşturulmaz. (MAN.4.BP4)", f"{PRS007}; SRÇ.002; SRÇ.005; SRÇ.023"],
        ["F5", "Hedeflerin gerçekleşmesini değerlendir", "Ocak-Mart verileri ve süreç değerlendirmeleri, Nisan-Mayıs döneminde konsolide edilir; sonuçlar Haziran-Temmuz YGG'sinde yönetim seviyesinde değerlendirilir. (MAN.4.BP5)", "Kalite sonuçları; YGG girdisi ve kararı"],
        ["F6", "Kalite uygunsuzluğunu yönlendir", "Kalite uygunsuzluğu SRÇ.017'ye aktarılır; kök neden ve düzeltici faaliyet burada yönetilir. Çözüm değişiklik gerektirirse SRÇ.018'e yönlendirilir. (MAN.4.BP6)", "SRÇ.017 kaydı; koşullu SRÇ.018 kaydı"],
        ["F7", "Geri bildirim topla ve değerlendir", "Müşteri toplantıları, proje kapanış/uygulama kayıtları, kabul sonuçları, süreç/personel geri bildirimleri ve devreye alınan müşteri anketleri değerlendirilir. (MAN.4.BP7)", f"{PRS008}; FRM.003 kayıtları; RPR.002"],
        ["F8", "Kalite performansını izle", "Kalite hedeflerinin gerçekleşmesi, kalite uygunsuzluklarının zamanında sonuçlandırılması ve devreye alınan projelerde müşteri memnuniyeti LST.009'a göre izlenir. (MAN.4.BP8)", "LST.009 ölçüm sonuçları; RPR.002"],
    ]
    return "".join([
        "<h2>1. Süreç Bilgileri</h2>", table(["Alan", "Değer"], [
            ["Kurum", "İstanbul Üniversitesi - Cerrahpaşa Bilgi İşlem Daire Başkanlığı"],
            ["Süreç Kodu ve Adı", SRC024], ["Süreç Referansı", "ISO/IEC 15504-5:2006 MAN.4 - Quality management"],
            ["Süreç Sahibi", OWNER], ["Hedef Kitle", "BİDB Başkanı, Proje Yöneticisi, Kalite Danışmanı, süreç/proje sahipleri, müşteri birimi temsilcileri ve ilgili uzmanlar"],
            ["Yayın ve Erişim Ortamı", "Confluence; kontrollü kaynaklar için Bitbucket; faaliyet takibi için Jira; yetkili ekler için Google Drive"],
            ["Durum", "Aktif"], ["Sürüm", "v1.0"], ["Yürürlük Tarihi", "15-02-2025"], ["Son Gözden Geçirme Tarihi", "15-07-2026"],
            ["Güncelleme Sıklığı", "Yılda en az bir kez veya önemli müşteri, kalite, standart, mevzuat, süreç ya da hizmet değişikliğinde"],
        ]),
        "<h2>2. Amaç</h2>", para("Bu sürecin amacı; standart süreç envanterindeki süreçler ile bu süreçlerin uygulandığı yazılım proje ve hizmetlerinde müşteri gereksinimlerini karşılayan kalite hedeflerini ve stratejisini belirlemek, kalite yönetim sistemini işletmek, kalite performansını izlemek ve hedef sapmalarında uygun faaliyeti başlatmaktır."),
        "<h3>2.1. Süreç Sonuçları</h3>", table(["Sonuç ID", "Süreç Sonucu"], [
            ["S1", "Müşterinin açık ve örtük kalite gereksinimlerine dayalı kalite hedefleri belirlenir."],
            ["S2", "Tanımlı hedeflere ulaşmak için genel kalite stratejisi geliştirilir."],
            ["S3", "Stratejiyi uygulayacak bütünleşik kalite yönetim sistemi kurulur ve sürdürülür."],
            ["S4", "Kalite kontrol ve güvence faaliyetleri gerçekleştirilir ve sonuçları doğrulanır."],
            ["S5", "Gerçek kalite performansı hedeflere göre izlenir."],
            ["S6", "Kalite hedefleri karşılanmadığında uygun faaliyet başlatılır."],
        ]),
        "<h2>3. Kapsam</h2>", table(["Kapsam Öğesi", "Açıklama"], [
            ["Kapsama Dahil", "LST.006 standart süreç envanterindeki süreçler ile bunların uygulandığı yazılım proje ve hizmetlerinin kalite hedefleri, stratejisi, kriterleri, güvence/değerlendirme girdileri, performans izlemesi, proje müşteri memnuniyeti ve yönetim değerlendirmesi"],
            ["Kapsam Dışı", "İÜC'nin BİDB dışındaki genel kalite yönetim sistemi; genel ve sürekli BT destek hizmeti memnuniyetinin ISO/IEC 20000-1 kapsamındaki işletimi; resmî dış denetim ve belgelendirme faaliyetleri"],
            ["Uygulama Alanı", "BİDB standart yazılım süreçleri, yazılım projeleri, bunlarla ilişkili ürünler ve proje özelindeki geliştirme/destek hizmetleri"],
        ]),
        "<h2>4. Referanslar</h2>", table(["Referans", "Açıklama"], [
            ["ISO/IEC 15504-5:2006 MAN.4 - Quality management", "Süreç amacı, sonuçları ve MAN.4.BP1-BP8 temel uygulamaları"],
            ["ISO/IEC 15504-5:2006 - Process Assessment Model", "Süreç boyutu ve değerlendirme göstergeleri"],
            ["ISO/IEC 15504-5:2006 - Process Attributes", "PA 2.1, PA 2.2, PA 3.1 ve PA 3.2 süreç öznitelikleri ile genel uygulamalar"],
        ]),
        "<h2>5. Terimler ve Kısaltmalar</h2>", table(["Terim / Kısaltma", "Açıklama"], [
            ["Kalite Hedefi", "Müşteri, ürün, süreç veya proje için ulaşılması ve değerlendirilebilmesi beklenen kalite sonucu"],
            ["Kalite Uygunsuzluğu", "Tanımlı kalite hedefi, kriteri, gereksinimi veya standardının karşılanmadığını gösteren durum"],
            ["YGG", "Yönetim Gözden Geçirme"], ["Proje Özelindeki Destek", "İlgili ürünün devreye alınması ve yaygın kullanımına bağlı destek deneyimi"],
        ]),
        "<h2>6. Süreç Aktivitesi</h2>", table(["Alan", "Açıklama"], [
            ["Süreç Başlatıcısı", "Yıllık kalite yönetimi döngüsü; yeni proje veya kalite hedefi; müşteri/standart/mevzuat değişikliği; kalite uygunsuzluğu; proje geri bildirimi"],
            ["Süreç Başlangıcı", "Kalite gereksinimleri, hedefleri, kriterleri ve izleme kapsamının belirlenmesi"],
            ["Süreç Bitişi", "Kalite sonuçlarının yönetim seviyesinde değerlendirilmesi, kararların ilgili sürece yönlendirilmesi ve hedeflerin güncellenmesi"],
            ["Ana Faaliyetler", "Hedef ve strateji belirleme; kriter ve sistem kurma; kalite verisi/geri bildirim toplama; performansı değerlendirme; uygunsuzluğu yönlendirme; sonuçları izleme"],
            ["İlgili Süreçler", related],
        ]),
        "<h2>7. Roller ve Sorumluluklar</h2>", para("Süreçteki rol, sorumluluk, yetkinlik, RACI ve onay ilişkileri LST.010 - Süreç Rol Yetki ve RACI Matrisi (SRÇ.024) dokümanında yönetilir. Kalite Danışmanı operasyonel koordinasyonu ve raporlamayı, Proje Yöneticisi kalite sonuçlarının operasyonel gözden geçirmesini, BİDB Başkanı yönetim kararını ve nihai onayı yürütür."),
        "<h2>8. Araçlar ve Altyapı</h2>", table(["Tür", "Araç / Altyapı Bileşeni", "Kullanım Amacı", "Erişim ve Kullanım Koşulu", "Sorumlu Rol / Birim"], [
            ["Araç", "Confluence", "Süreç paketi, prosedürler, değerlendirmeler ve raporların yayımlanması", "Kurumsal hesap ve sayfa yetkisi", "Proje Yöneticisi / Confluence Yöneticisi"],
            ["Araç", "Bitbucket", "Kontrollü doküman kaynaklarının sürüm yönetimi", "Repository yetkisi", "Proje Yöneticisi / Repository Yöneticisi"],
            ["Araç", "Jira", "SRÇ.017 kalite uygunsuzluğu ve SRÇ.018 değişiklik faaliyetlerinin izlenmesi", "Proje/ekip bazlı yetkilendirme", "Proje Yöneticisi / İlgili Süreç Sahibi"],
            ["Araç", "Kurumun anket sistemi veya Google Forms", "Devreye alınmasına karar verilen müşteri memnuniyeti anketlerinin uygulanması", "BİDB Başkanı uygulama kararı; yetkili hesap ve veri erişimi", "Kalite Danışmanı / Proje Yöneticisi"],
            ["Altyapı", "Google Drive", "Yetkili anket ham çıktıları ve müşteriyle paylaşılan eklerin saklanması", "Kurumsal hesap ve klasör yetkisi", "Belge Sahibi / Kalite Danışmanı"],
        ], fixed=True),
        "<h2>9. Süreç İş Ürünleri</h2>", para("Girdi ve çıktı iş ürünleri ile tam doküman adları ve kalite kriterleri LST.008 - İş Ürünleri ve Kalite Kriterleri Listesi (SRÇ.024) dokümanında yönetilir."),
        "<h2>10. Süreç Akışı</h2>", image(storage, FLOW_PNG, "SRÇ.024 kalite yönetimi süreç akışı", 900) + mermaid,
        "<h2>11. Süreç Faaliyetleri</h2>", table(["Faaliyet ID", "Faaliyet", "Açıklama", "Elde Edilen / Güncellenen İş Ürünü"], activities),
        "<h2>12. Ölçüm ve İzleme</h2>", para("Süreçte yalnızca kalite hedefleri gerçekleşme oranı, süresi içinde sonuçlandırılan kalite uygunsuzluğu oranı ve devreye alınan projelerde müşteri memnuniyeti seviyesi izlenir. Ölçüm tanımları LST.009'da; proje müşteri memnuniyeti sonuçları RPR.002'de yönetilir. RPR.001'e müşteri memnuniyeti verisi eklenmez."),
        "<h2>13. Uygulama ve Uyarlama Kuralları</h2>",
        "<h3>13.1. Yıllık Döngü</h3>" + para("Ocak-Mart döneminde süreç değerlendirmeleri ve kalite verileri toplanır; Nisan-Mayıs döneminde sonuçlar konsolide edilir; Haziran-Temmuz döneminde YGG yapılır; kararlar sonrasında hedefler ve ilgili süreç kayıtları güncellenir."),
        "<h3>13.2. Kalite Uygunsuzluğu</h3>" + para("Kalite uygunsuzlukları SRÇ.017'de kök neden analizi ve düzeltici faaliyet için yönetilir. BİDB Başkanına bildirim gerektiren tür, seviye, etki ve aciliyet ölçütleri SRÇ.017 dokümanlarında belirlenir. Çözüm değişiklik gerektirirse SRÇ.018'e aktarılır."),
        "<h3>13.3. Müşteri Memnuniyeti</h3>" + para("Anket altyapısı hazır tutulur; uygulanmış bir çalışma gibi gösterilmez. Ürün, geliştirme ve proje özelindeki destek memnuniyeti, proje yaygın kullanıma geçtikten ve kullanıcılar yeterli deneyim kazandıktan sonra ölçülebilir. Uygulama zamanını Proje Yöneticisi müşteri birimiyle belirler; devreye alma kararı BİDB Başkanına aittir."),
        "<h3>13.4. Genel Destek Hizmetleri</h3>" + para("BİDB'nin genel ve sürekli BT destek hizmeti memnuniyeti ISO/IEC 20000-1 kapsamındaki hizmet yönetimi uygulamalarında ele alınır. SRÇ.024 bu sonuçları girdi olarak kullanabilir; mükerrer genel destek anketi üretmez."),
        "<h3>13.5. Asgari Bürokrasi</h3>" + para("Ayrı bir kalite el kitabı veya kalite hedefleri listesi oluşturulmaz. Ana hedefler SRÇ.024'te, ölçüm yöntemleri LST.009'da, proje müşteri memnuniyeti sonuçları RPR.002'de ve uygunsuzluklar SRÇ.017'de izlenir."),
        "<h2>14. Süreç Etkileşimleri</h2>", para("Süreç ve doküman düzeyindeki girdi/çıktı ilişkileri LST.007 - Süreç Etkileşim Matrisi (SRÇ.024) dokümanında gösterilir."),
        "<h2>15. Sürüm Geçmişi</h2>", history("Kalite Yönetimi Süreci", REVIEWER, APPROVER),
    ])


def lst007_body(storage: bool) -> str:
    mermaid = info_macro("Mermaid Kodu", INTERACTION_LINES) if storage else info_view("Mermaid Kodu", INTERACTION_LINES)
    rows = [
        ["Girdi", "SRÇ.002 / kalite planları ve kalite güvence sonuçları", SRC024, "Kalite güvence sonuçlarını kalite hedefleri ve yönetim değerlendirmesine taşımak"],
        ["Girdi", "SRÇ.005 / FRM.001 süreç değerlendirmeleri", SRC024, "Süreç kalite güçlü/zayıf yönlerini kullanmak"],
        ["Girdi", "SRÇ.023 / YGG girdileri ve kararları", SRC024, "Yönetim değerlendirmesi ve karar yönlendirmesi"],
        ["Girdi", "Müşteri, proje, süreç ve personel geri bildirimleri", SRC024, "Kalite durumunu ve iyileştirme ihtiyacını değerlendirmek"],
        ["Çıktı", SRC024, PRS007, "Kalite hedefleri, strateji ve yıllık kalite döngüsünü uygulamak"],
        ["Çıktı", SRC024, PRS008, "Proje müşteri memnuniyeti yöntemini uygulamak"],
        ["Çıktı", "FRM.003 müşteri memnuniyeti anket kayıtları", "RPR.002 - Proje Müşteri Memnuniyeti Değerlendirme Raporu", "Proje bazlı sonuçları değerlendirmek"],
        ["Çıktı", "Kalite uygunsuzluğu", "SRÇ.017 - Problem Çözüm Yönetimi Süreci", "Kök neden ve düzeltici faaliyeti yürütmek"],
        ["Çıktı", "SRÇ.017 çözüm kararı", "SRÇ.018 - Değişiklik Talebi Yönetimi Süreci", "Gerekli değişikliği analiz etmek ve uygulamak"],
        ["Çıktı", "Kalite sonucu / iyileştirme ihtiyacı", "SRÇ.006 / SRÇ.023", "İyileştirme ve YGG kararlarına girdi sağlamak"],
    ]
    return "".join([
        "<h2>1. Liste Özeti</h2>", table(["Alan", "Değer"], [["İlgili Süreç", SRC024], ["Kullanım Amacı", "SRÇ.024'ün süreç ve doküman düzeyindeki girdi/çıktı ilişkilerini göstermek"], ["Sorumlu", "Kalite Danışmanı"], ["Durum", "Aktif"], ["Sürüm", "v1.0"]]),
        "<h2>2. Süreç ve Doküman Etkileşim Matrisi</h2>", table(["Yön", "Kaynak", "Hedef", "Etkileşim / Aktarılan Bilgi"], rows),
        "<h2>3. Süreç Etkileşim Diyagramı</h2>", image(storage, INTERACTION_PNG, "SRÇ.024 süreç etkileşim diyagramı", 820) + mermaid,
        "<h2>4. Sürüm Geçmişi</h2>", history("Süreç Etkileşim Matrisi (SRÇ.024)", REVIEWER, APPROVER),
    ])


def lst008_body() -> str:
    rows = [
        ["Girdi", "Müşteri, ürün, proje ve süreç kalite gereksinimleri", "Müşteri birimi / Proje Yöneticisi / Süreç Sahibi", "Güncel, kapsamı belirli ve yetkili kaynağa bağlı olmalıdır.", "Kalite hedeflerinin belirlenmesi"],
        ["Girdi", "Mevzuat, uluslararası standartlar ve kurumsal kriterler", "Kalite Danışmanı / Bilgi Sahibi", "Yürürlük ve uygulanabilirlik bilgisi doğrulanmalıdır.", "Kalite kriterlerinin belirlenmesi"],
        ["Girdi", "SRÇ.002 kalite güvence ve kalite planı sonuçları", "Kalite Güvencesi Sorumlusu", "İlgili proje/süreç, dönem, bulgu ve kanıt bağlantısı belirli olmalıdır.", "Kalite sisteminin işletilmesi"],
        ["Girdi", "SRÇ.005 süreç değerlendirmeleri ve LST.009 ölçüm sonuçları", "Kalite Danışmanı / Ölçüm Sorumlusu", "Güncel değerlendirme ve ölçüm tanımına dayanmalıdır.", "Kalite performansının değerlendirilmesi"],
        ["Girdi", "Müşteri, proje, süreç ve personel geri bildirimleri", "İlgili Paydaş", "Kaynağı ve bağlamı belli olmalı; uygulanmamış anket sonucu varmış gibi gösterilmemelidir.", "Geri bildirimin değerlendirilmesi"],
        ["Çıktı", SRC024, "Kalite Danışmanı", "MAN.4 BP1-BP8, onaylı kapsam, hedefler ve yıllık döngü izlenebilir olmalıdır.", "Kalite yönetimi ortak çerçevesi"],
        ["Çıktı", PRS007, "Kalite Danışmanı", "PRS.XXX.Ş yapısına uygun; hedef, strateji, kriter, değerlendirme ve yönlendirme kurallarını içermelidir.", "Kalite yönetimi işleyişi"],
        ["Çıktı", PRS008, "Kalite Danışmanı", "Anketin devreye alınma, uygulama, kayıt ve değerlendirme kurallarını; ISO/IEC 20000-1 sınırını içermelidir.", "Müşteri memnuniyeti işleyişi"],
        ["Çıktı", FRM003_TEMPLATE, "Kalite Danışmanı", "Ürün, geliştirme ve proje özelindeki destek bölümleri; yalnızca 5'li ölçek; zorunlu müşteri birimi/proje ve isteğe bağlı kişi adı içermelidir.", "Anket kayıtlarının üretilmesi"],
        ["Çıktı", RPR002_TEMPLATE, "Kalite Danışmanı", "Anket kapsamı, katılım, üç memnuniyet boyutu, görüşler, değerlendirme ve varsa SRÇ.017 bağlantıları izlenebilir olmalıdır.", "Proje müşteri memnuniyeti sonucu"],
        ["Çıktı", "Kalite uygunsuzluğu / SRÇ.017 kaydı", "Proje Yöneticisi / İlgili Süreç Sahibi", "Kalite bağlamı, etki ve kaynak kanıtı belirtilmeli; kök neden SRÇ.017'de ele alınmalıdır.", "Düzeltici faaliyet"],
        ["Çıktı", "YGG kalite girdisi ve kararı", "BİDB Başkanı / Proje Yöneticisi", "Değerlendirilen dönem, hedef sonucu, karar ve yönlendirme açık olmalıdır.", "Yönetim değerlendirmesi"],
    ]
    return "".join([
        "<h2>1. Liste Özeti</h2>", table(["Alan", "Değer"], [["İlgili Süreç", SRC024], ["Kullanım Amacı", "SRÇ.024 girdi ve çıktı iş ürünlerini tam adları ve kalite kriterleriyle yönetmek"], ["Sorumlu", "Kalite Danışmanı"], ["Durum", "Aktif"], ["Sürüm", "v1.0"]]),
        "<h2>2. İş Ürünleri ve Kalite Kriterleri</h2>", table(["Tür", "İş Ürünü / Kayıt", "Sahibi / Kaynağı", "Kalite Kriteri", "Kullanım Amacı"], rows, fixed=True),
        "<h2>3. Kontrol Kuralları</h2>", table(["Kural", "Açıklama"], [["Tam ad kullanımı", "İş ürünü listelerinde doküman kodu ile adı birlikte yazılır; değerlendirme numarası genel iş ürünü adına eklenmez."], ["Gerçek kayıt", "Gerçekleşmemiş anket, YGG, uygunsuzluk veya düzeltici faaliyet kanıt gibi gösterilmez."], ["Tekil kayıt", "Uygunsuzluk SRÇ.017'de, değişiklik SRÇ.018'de, proje müşteri memnuniyeti RPR.002'de yönetilir."], ["Yetkili kaynak", "Standart, mevzuat ve hizmet yönetimi kayıtları yetkili kaynağa bağlantı verilerek kullanılır."]]),
        "<h2>4. Sürüm Geçmişi</h2>", history("İş Ürünleri ve Kalite Kriterleri Listesi (SRÇ.024)", REVIEWER, APPROVER),
    ])


def lst009_body() -> str:
    rows = [
        ["KM-01", "Kalite hedefleri gerçekleşme oranı", "Gerçekleşen hedef sayısı / değerlendirilen hedef sayısı x 100", "Yıllık", "Kalite hedefi değerlendirmeleri / YGG girdileri", "Kalite Danışmanı", "İlk gerçek yıllık döngüde oluşturulur; bu aşamada sonuç üretilmez."],
        ["KM-02", "Süresi içinde sonuçlandırılan kalite uygunsuzluğu oranı", "Hedef süresinde kapatılan kalite uygunsuzluğu sayısı / dönemde sonuçlandırılması gereken kalite uygunsuzluğu sayısı x 100", "Yıllık", "SRÇ.017 kayıtları", "Kalite Danışmanı / Proje Yöneticisi", "Uygunsuzluk türü, seviyesi ve bildirim kuralları SRÇ.017'de tanımlanır."],
        ["KM-03", "Proje müşteri memnuniyeti seviyesi", "Uygulanan 5'li anket cevaplarının ürün, geliştirme ve proje özelindeki destek boyutlarında aritmetik ortalaması", "Proje yaygın kullanıma geçtikten sonra, anket devreye alınmışsa", "FRM.003 kayıtları ve RPR.002", "Kalite Danışmanı", "Sabit eşik ve otomatik uygunsuzluk tetikleyicisi tanımlanmaz; RPR.001'e aktarılmaz."],
    ]
    return "".join([
        "<h2>1. Liste Özeti</h2>", table(["Alan", "Değer"], [["İlgili Süreç", SRC024], ["Kullanım Amacı", "Az sayıda sürdürülebilir kalite yönetimi ölçümünü tanımlamak"], ["Sorumlu", "Kalite Danışmanı"], ["Durum", "Aktif"], ["Sürüm", "v1.0"]]),
        "<h2>2. Ölçüm Tanımları</h2>", table(["Ölçüm ID", "Ölçüm Adı", "Hesaplama / Değerlendirme Yöntemi", "Sıklık / Tetikleyici", "Veri Kaynağı", "Sorumlu", "Hedef / Yorum Kuralı"], rows, fixed=True),
        "<h2>3. Ölçüm Kullanım Kuralları</h2>", table(["Kural", "Açıklama"], [["Sınırlı ölçüm seti", "Yalnız düzenli ve güvenilir veri üretilebilen üç ölçüm izlenir."], ["Anket koşulu", "KM-03 yalnız anket devreye alındığında ve gerçek cevap oluştuğunda hesaplanır."], ["Yorum", "Sayısal sonuç tek başına uygunsuzluk oluşturmaz; Kalite Danışmanı bağlamla birlikte değerlendirir."], ["Rapor ayrımı", "Müşteri memnuniyeti sonuçları RPR.002'de tutulur; RPR.001 değiştirilmez."]]),
        "<h2>4. Sürüm Geçmişi</h2>", history("Süreç Performans Ölçüm Seti (SRÇ.024)", REVIEWER, APPROVER),
    ])


def lst010_body() -> str:
    rr = ["BİDB Başkanı", "Kalite Danışmanı", "Proje Yöneticisi", "Süreç / Proje Sahibi", "Müşteri Birimi", "İdari İşler Şube Müdürü"]
    spec = {
        "process": SRC024,
        "name": "Kalite Yönetimi Süreci",
        "purpose": "SRÇ.024 rol, yetki, yetkinlik ve RACI yapısını tanımlamak",
        "owner": OWNER,
        "reviewer": REVIEWER,
        "approver": APPROVER,
        "raci_roles": rr,
        "roles": [
            ["Bilgi İşlem Daire Başkanı", "Kalite yönetimini sahiplenmek; hedef, strateji, anket devreye alma ve yönetim kararlarını onaylamak", "Nihai kurumsal karar ve onay vermek", "Kurumsal yönetim, kalite hedefleri ve kaynak yetkisi", "Süreç sahibi / onaylayan"],
            ["Kalite Danışmanı", "Kalite hedefi, kriter, ölçüm, veri toplama, analiz ve RPR.002 hazırlığını koordine etmek", "Kalite değerlendirmesi ve yönlendirme önerisi vermek", "ISO/IEC 15504-5, kalite yönetimi, analiz ve dokümantasyon", "Operasyonel koordinatör / hazırlayan"],
            ["Proje Yöneticisi", "Kalite sonuçlarını operasyonel olarak gözden geçirmek; proje ve müşteri girdilerini koordine etmek", "Düzeltme istemek ve anket uygulama zamanını müşteri birimiyle belirlemek", "Proje, müşteri, ürün ve operasyon bilgisi", "Sonuçları gözden geçiren"],
            ["Süreç / Proje Sahibi", "Kendi kapsamındaki hedef, kriter, performans ve kanıtları sağlamak", "Kendi görev alanında uygulama ve uygunluk görüşü vermek", "İlgili süreç, proje ve ürün bilgisi", "Uygulama / kanıt sahibi"],
            ["Müşteri Birimi Temsilcisi", "Gereksinim, kullanım deneyimi ve memnuniyet geri bildirimi sağlamak", "Kendi birimi adına görüş bildirmek", "Ürün ve hizmet kullanım deneyimi", "Geri bildirim kaynağı"],
            ["İdari İşler Şube Müdürü", "Süreç ve bağlı kontrollü dokümanları gözden geçirmek", "Doküman düzeltmesi istemek ve uygunluk görüşü vermek", "Kurumsal süreç ve doküman gözden geçirme bilgisi", "Doküman gözden geçiren"],
        ],
        "activities": [
            ["F1 Kalite hedeflerini belirle", "A", "R", "C", "C", "C", "I"],
            ["F2 Kalite stratejisini tanımla", "A", "R", "C", "C", "I", "C"],
            ["F3 Kalite kriterlerini tanımla", "A", "R", "C", "R/C", "C", "I"],
            ["F4 Kalite yönetim sistemini işlet", "A", "R", "R", "R", "I", "I"],
            ["F5 Hedeflerin gerçekleşmesini değerlendir", "A", "R", "R", "C", "C", "I"],
            ["F6 Kalite uygunsuzluğunu yönlendir", "A/I", "R", "R", "R/C", "I", "I"],
            ["F7 Geri bildirim ve anketi yönet", "A", "R", "R", "C", "R", "I"],
            ["F8 Kalite performansını izle", "A", "R", "R/C", "R/C", "I", "I"],
        ],
        "products": [
            [SRC024, "A", "R", "C", "C", "I", "R"],
            [PRS007, "A", "R", "C", "C", "I", "R"],
            [PRS008, "A", "R", "C", "C", "C", "R"],
            [FRM003_TEMPLATE, "A", "R", "C", "C", "C", "R"],
            [RPR002_TEMPLATE, "A", "R", "R", "C", "I", "R"],
            ["RPR.002 - Proje Müşteri Memnuniyeti Değerlendirme Raporu ([Proje Adı])", "A", "R", "R", "C", "C", "I"],
            ["LST.009 - Süreç Performans Ölçüm Seti (SRÇ.024)", "A", "R", "C", "C", "I", "I"],
            ["SRÇ.017 kalite uygunsuzluğu kaydı", "I", "R/C", "R", "R", "I", "I"],
            ["FRM.001 - Süreç Gözden Geçirme Formu (SRÇ.024)", "A", "R", "C", "C", "I", "R"],
        ],
        "authority": [
            ["SRÇ.024 ve PRS.007/PRS.008 yürürlük kararı", "Kalite Danışmanı", "İdari İşler Şube Müdürü", "Bilgi İşlem Daire Başkanı", "Kontrollü doküman değişikliği SRÇ.018 üzerinden yürütülür."],
            ["Kurumsal kalite hedefi ve stratejisi", "Kalite Danışmanı / Proje Yöneticisi", "İlgili Süreç ve Proje Sahipleri", "Bilgi İşlem Daire Başkanı", "Standart süreç envanteri ve yazılım proje/hizmet kapsamıyla sınırlıdır."],
            ["Müşteri memnuniyeti anketini devreye alma", "Kalite Danışmanı / Proje Yöneticisi", "İlgili Müşteri Birimi", "Bilgi İşlem Daire Başkanı", "Proje yaygın kullanıma geçtikten sonra uygulanır."],
            ["RPR.002 raporu", "Kalite Danışmanı", "Proje Yöneticisi", "Bilgi İşlem Daire Başkanı", "Gerçek anket cevapları ve proje bağlamı esas alınır."],
            ["Kalite uygunsuzluğu yönlendirmesi", "Kalite Danışmanı / Proje Yöneticisi", "İlgili Süreç / Proje Sahibi", "SRÇ.017 yetki yapısı", "Kök neden ve düzeltici faaliyet SRÇ.017'de yürütülür."],
        ],
    }
    return raci_body(spec)


def blank_review_body() -> str:
    return "".join([
        "<h2>1. Form Bilgileri</h2>", table(["Alan", "Değer"], [["Form Kodu ve Adı", "FRM.001 - Süreç Gözden Geçirme Formu (SRÇ.024)"], ["Süreç", SRC024], ["Değerlendirme Tarihi", "<em>GG-AA-YYYY</em>"], ["Değerlendiren", "<em>Rol / kişi</em>"], ["Durum", "Boş Form"], ["Sürüm", "v1.0"]]),
        "<h2>2. Durum Değerleri</h2>", table(["Durum", "Anlamı"], LABELS),
        "<h2>3. BP Takip Matrisi</h2>", table(["BP", "Standart Beklentisi", "Mevcut Karşılama", "Karşılayan Doküman / Kayıt", "Durum", "Eksik / Tamamlayıcı Aksiyon"], [[bp, expectation, "<em>Değerlendirme açıklaması</em>", "<em>Kanıt bağlantısı</em>", "<em>YOK / ZAYIF / DAĞINIK / VAR / KAPSAM DIŞI</em>", "<em>Aksiyon / gerekçe</em>"] for bp, _, expectation in MAN4_BPS]),
        "<h2>4. PA / GP Takip Matrisi</h2>", table(["PA", "GP", "Standart Beklentisi", "Mevcut Karşılama", "Karşılayan Doküman / Kayıt", "Durum", "Eksik / Tamamlayıcı Aksiyon"], [[pa, gp, expectation, "<em>Değerlendirme açıklaması</em>", "<em>Kanıt bağlantısı</em>", "<em>Etiket</em>", "<em>Aksiyon / gerekçe</em>"] for pa, gp, expectation in GPS]),
        "<h2>5. Öncelikli Tamamlama Listesi</h2>", table(["Öncelik", "Bulgu / Aksiyon", "Bulgu Türü", "İlgili BP / GP", "Hedef Süreç / İzleme Yeri"], [["<em>Yüksek / Orta / Düşük</em>", "<em>Bulgu veya aksiyon</em>", "<em>Uygunsuzluk / İyileştirme Fırsatı / Gözlem / Güçlü Uygulama</em>", "<em>BP / GP</em>", "<em>SRÇ.017 / SRÇ.018 / ilgili kayıt</em>"]]),
    ])


def assessment_body() -> str:
    bp_status = {"MAN.4.BP1": "VAR", "MAN.4.BP2": "VAR", "MAN.4.BP3": "VAR", "MAN.4.BP4": "DAĞINIK", "MAN.4.BP5": "ZAYIF", "MAN.4.BP6": "DAĞINIK", "MAN.4.BP7": "ZAYIF", "MAN.4.BP8": "ZAYIF"}
    bp_rows = []
    evidence = f"{SRC024}; {PRS007}; {PRS008}; FRM.003.Ş; RPR.002.Ş; LST.007-LST.010 (SRÇ.024)"
    for code, _, expectation in MAN4_BPS:
        status = bp_status[code]
        if status == "VAR":
            current, action = "Hedef, strateji, kriter kaynakları ve sorumluluklar süreç paketi içinde tanımlanmıştır.", "Tanımlı yapı ilk gerçek yıllık döngü ve proje uygulamalarında korunmalıdır."
        elif status == "DAĞINIK":
            current, action = "Bütünleşik yöntem ve süreç yönlendirmesi tanımlıdır; bağlı süreçlerin tamamı ve gerçek uygulama kayıtları henüz oluşmamıştır.", "SRÇ.002 ve SRÇ.017 çalışılırken kalite yönetimi arayüzleri doğrulanmalıdır."
        else:
            current, action = "Uygulama ve değerlendirme yöntemi tanımlıdır; gerçek anket, yıllık hedef değerlendirmesi veya ölçüm sonucu henüz bulunmamaktadır.", "İlk gerçek uygulamada doğal kayıt ve sonuç oluşturulmalıdır."
        bp_rows.append([code, expectation, current, evidence, status, action])
    gp_status = {
        "GP.2.1.1":"VAR", "GP.2.1.2":"DAĞINIK", "GP.2.1.3":"ZAYIF", "GP.2.1.4":"VAR", "GP.2.1.5":"VAR", "GP.2.1.6":"VAR",
        "GP.2.2.1":"VAR", "GP.2.2.2":"VAR", "GP.2.2.3":"DAĞINIK", "GP.2.2.4":"DAĞINIK",
        "GP.3.1.1":"VAR", "GP.3.1.2":"VAR", "GP.3.1.3":"VAR", "GP.3.1.4":"VAR", "GP.3.1.5":"VAR",
        "GP.3.2.1":"DAĞINIK", "GP.3.2.2":"DAĞINIK", "GP.3.2.3":"DAĞINIK", "GP.3.2.4":"ZAYIF", "GP.3.2.5":"VAR", "GP.3.2.6":"ZAYIF",
    }
    gp_rows = []
    for pa, gp, expectation in GPS:
        status = gp_status[gp]
        if status == "VAR":
            current, action = "Süreç paketi; amaç, rol, iş ürünü, etkileşim, altyapı ve kontrol kurallarıyla tanımlanmıştır.", "Tanımlı yapı gerçek uygulama kayıtlarıyla sürdürülmelidir."
        elif status == "DAĞINIK":
            current, action = "Tanım vardır; bağlı süreç, görevlendirme, anket veya yıllık döngü kanıtı henüz sistematik değildir.", "İlk işletim döneminde doğal kayıtlarla doğrulanmalıdır."
        else:
            current, action = "Yöntem ve kaynak ihtiyacı tanımlıdır; gerçekleşen performans ayarlama, veri analizi veya uygulama kanıtı bulunmamaktadır.", "İlk gerçek kalite döngüsünde sonuç üretilmelidir."
        gp_rows.append([pa, gp, expectation, current, evidence, status, action])
    completion = [
        ["Yüksek", "SRÇ.002 kalite güvence ve kalite planı kapsamını SRÇ.024 kalite hedefleri ve stratejisiyle uyumlandır.", "Gözlem", "MAN.4.BP4; GP.2.1.6; GP.3.2.1", "SRÇ.002 / FRM.001 Değerlendirme #1"],
        ["Yüksek", "SRÇ.017 çalışmasında kalite uygunsuzluğu tür/seviye/etki/aciliyet ve BİDB Başkanı bildirim kurallarını tanımla.", "Gözlem", "MAN.4.BP6; GP.2.2.3-GP.2.2.4", "SRÇ.017"],
        ["Orta", "Uygun bir proje yaygın kullanıma geçtikten ve anket devreye alındıktan sonra ilk gerçek FRM.003 kayıtlarını ve RPR.002'yi oluştur.", "Gözlem", "MAN.4.BP7-BP8; GP.3.2.4; GP.3.2.6", "FRM.003 / RPR.002"],
        ["Orta", "İlk yıllık kalite döngüsünde hedef gerçekleşmelerini konsolide ederek Haziran-Temmuz YGG'sinde değerlendir.", "Gözlem", "MAN.4.BP5; GP.2.1.2-GP.2.1.3", "SRÇ.023 YGG / LST.009"],
    ]
    return "".join([
        "<h2>1. Değerlendirme Özeti</h2>", table(["Alan", "Değer"], [["Süreç", SRC024], ["Değerlendirme Kaydı", "Değerlendirme #1"], ["Değerlendirme Tarihi", "15-07-2026"], ["Değerlendiren", PREPARED_BY], ["Yaklaşım", "Sayısal puan ve tek toplam süreç etiketi kullanılmadan gerekçeli BP ve PA/GP etiketleri"], ["BP Dağılımı", "3 VAR, 2 DAĞINIK ve 3 ZAYIF"], ["PA/GP Dağılımı", "12 VAR, 6 DAĞINIK ve 3 ZAYIF"]]),
        "<h2>2. Durum Değerleri</h2>", table(["Durum", "Anlamı"], LABELS),
        "<h2>3. BP Takip Matrisi</h2>", table(["BP", "Standart Beklentisi", "Mevcut Karşılama", "Karşılayan Doküman / Kayıt", "Durum", "Eksik / Tamamlayıcı Aksiyon"], bp_rows),
        "<h2>4. PA / GP Takip Matrisi</h2>", table(["PA", "GP", "Standart Beklentisi", "Mevcut Karşılama", "Karşılayan Doküman / Kayıt", "Durum", "Eksik / Tamamlayıcı Aksiyon"], gp_rows),
        "<h2>5. Öncelikli Tamamlama Listesi</h2>", table(["Öncelik", "Bulgu / Aksiyon", "Bulgu Türü", "İlgili BP / GP", "Hedef Süreç / İzleme Yeri"], completion),
        "<h2>6. Sonuç</h2>", para("Kalite hedefleri, strateji, kriterler, yıllık döngü, müşteri memnuniyeti altyapısı ve süreç yönlendirmeleri tanımlanmıştır. Gerçek kalite hedefi sonuçları, müşteri anketleri ve bağlı süreç uygulamaları henüz oluşmadığından uygulama ve performans alanları ihtiyatlı etiketlenmiştir; aynı Değerlendirme #1 kaydı doğal kanıtlar oluştukça güncellenecektir."),
    ])


def procedure_body(code: str) -> str:
    if code == "quality":
        title, purpose, scope, outside = PRS007, "Kalite hedefleri, stratejisi, kriterleri, yıllık değerlendirme döngüsü, kalite uygunsuzluğu yönlendirmesi ve performans izlemesinin uygulanışını tanımlamak.", "LST.006 kapsamındaki süreçler ile bunların uygulandığı yazılım proje ve hizmetlerinin kurumsal ortak kalite yönetimi.", "İÜC genel kalite yönetim sisteminin yeniden tanımlanması; proje özel kalite güvence kontrollerinin SRÇ.002 yerine yürütülmesi; resmî denetim faaliyetleri."
        refs = [[SRC024, "MAN.4 kapsamı ve süreç faaliyetleri"], ["SRÇ.002 - Kalite Güvencesi Süreci", "Proje/süreç kalite planları ve güvence sonuçları"], ["SRÇ.005 - Süreç Değerlendirme Süreci", "Süreç kalite değerlendirme girdileri"], ["SRÇ.017 - Problem Çözüm Yönetimi Süreci", "Kalite uygunsuzluğu, kök neden ve düzeltici faaliyet"], ["SRÇ.023 - Organizasyonel Yönetim Süreci", "YGG ve yönetim kararları"], ["LST.007-LST.010 (SRÇ.024)", "Etkileşim, iş ürünü, ölçüm ve RACI yapısı"], ["PRS.XXX.Ş - Prosedür Tanımı Şablonu", "Doküman yapısı"]]
        principles = [["Bütünleşik sistem", "Ayrı kalite el kitabı oluşturulmaz; mevcut süreç, plan, değerlendirme, ölçüm, YGG, problem ve değişiklik mekanizmaları birlikte kullanılır."], ["Az sayıda ölçüm", "Yalnız LST.009'da tanımlı üç sürdürülebilir ölçüm izlenir."], ["Tekil uygunsuzluk kaydı", "Kalite uygunsuzluğu SRÇ.017'de yönetilir; SRÇ.024'te ikinci kayıt oluşturulmaz."], ["Yönetim değerlendirmesi", "Olağan kalite sonuçları Haziran-Temmuz YGG'sinde; uygunsuzluk bildirimi SRÇ.017 ölçütlerine göre ele alınır."], ["Gerçek kanıt", "Gerçekleşmemiş anket, hedef sonucu veya faaliyet kanıt gibi gösterilmez."]]
        strategy = [["1. Gereksinimleri derle", "Müşteri, standart, mevzuat, süreç ve proje kalite gereksinimlerini belirle.", "Kalite Danışmanı / Proje Yöneticisi", "Yetkili kaynak ve proje kayıtları", "Yıllık veya olay bazlı"], ["2. Hedef ve stratejiyi belirle", "Dört ana kalite hedefini, sorumlulukları ve kaynak yaklaşımını uygula.", "Kalite Danışmanı", SRC024, "BİDB Başkanı onayı"], ["3. Kriter ve ölçümü belirle", "LST.008 kriterlerini ve LST.009 ölçümlerini kullan.", "Kalite Danışmanı / Süreç Sahibi", "LST.008 / LST.009", "Az sayıda ölçüm"], ["4. Veriyi topla", "Ocak-Mart değerlendirmeleri ile kalite güvence, proje ve geri bildirim kayıtlarını derle.", "Kalite Danışmanı", "Doğal süreç/proje kayıtları", "Sahte kayıt yok"], ["5. Sonuçları konsolide et", "Nisan-Mayıs döneminde kalite sonuçlarını analiz et ve Proje Yöneticisine sun.", "Kalite Danışmanı", "Kalite sonuç özeti", "Operasyonel gözden geçirme"], ["6. Uygunsuzluğu yönlendir", "Kalite uygunsuzluğunu SRÇ.017'ye, gerekli değişikliği SRÇ.018'e aktar.", "Kalite Danışmanı / Proje Yöneticisi", "SRÇ.017 / SRÇ.018", "Kök neden SRÇ.017'de"], ["7. Yönetim değerlendirmesi", "Haziran-Temmuz YGG'sinde hedef sonuçlarını ve ihtiyaçları değerlendir.", "BİDB Başkanı", "FRM.002 YGG kaydı", "SRÇ.023"], ["8. Hedefleri güncelle", "Kararları ilgili süreçlere aktar ve kalite hedeflerini gerektiğinde güncelle.", "Kalite Danışmanı / İlgili Süreç Sahibi", "YGG kararı / hedef süreç kaydı", "Yıllık döngü"]]
        records = [[SRC024, "Kalite hedefleri ve genel çerçeve", "01 - Süreç Dokümanları", "Kalite Danışmanı", "Ana hedefler süreçte tutulur"], ["LST.008 - İş Ürünleri ve Kalite Kriterleri Listesi (SRÇ.024)", "Girdi/çıktı kalite kriterleri", "SRÇ.024 altı", "Kalite Danışmanı", "Tam adlar"], ["LST.009 - Süreç Performans Ölçüm Seti (SRÇ.024)", "Kalite yönetimi ölçümleri", "SRÇ.024 altı", "Kalite Danışmanı", "Üç ölçüm"], ["SRÇ.017 kalite uygunsuzluğu kayıtları", "Kök neden ve düzeltici faaliyet", "Jira / ilgili süreç alanı", "İlgili Süreç Sahibi", "Tekil kayıt"], ["FRM.002 YGG kaydı", "Yönetim değerlendirmesi ve kararlar", "SRÇ.023 alanı", "Proje Yöneticisi / İdari İşler Şube Müdürü", "Haziran-Temmuz"]]
    else:
        title, purpose, scope, outside = PRS008, "Yaygın kullanıma geçen yazılım projelerinde ürün, geliştirme hizmeti ve proje özelindeki destek memnuniyetinin ölçülmesi ve değerlendirilmesi için uygulanacak yöntemi tanımlamak.", "BİDB yazılım projelerinin yaygın kullanım sonrasındaki proje özel müşteri memnuniyeti anketi, kayıtları ve RPR.002 değerlendirme raporu.", "BİDB'nin genel ve sürekli BT destek hizmeti memnuniyetinin işletimi; bu alan ISO/IEC 20000-1 kapsamındaki hizmet yönetimi uygulamalarında ele alınır."
        refs = [[SRC024, "Müşteri geri bildirimi ve kalite yönetimi kapsamı"], ["ISO/IEC 20000-1", "Genel ve sürekli BT destek hizmeti memnuniyetinin ayrı hizmet yönetimi kapsamı"], [FRM003_TEMPLATE, "Anket soru ve cevap yapısı"], [RPR002_TEMPLATE, "Proje bazlı değerlendirme raporu"], ["SRÇ.017 - Problem Çözüm Yönetimi Süreci", "Doğrulanan kalite uygunsuzluklarının kök neden ve düzeltici faaliyet yönetimi"], ["PRS.XXX.Ş - Prosedür Tanımı Şablonu", "Doküman yapısı"]]
        principles = [["Gelecekte devreye alma", "Anket altyapısı hazır tutulur; gerçek uygulama BİDB Başkanı kararıyla başlatılır."], ["Uygun zaman", "Anket ilk canlıya geçişte değil, proje yaygın kullanıma geçtikten ve kullanıcılar yeterli deneyim kazandıktan sonra uygulanır."], ["Proje özel destek", "Destek soruları yalnız ilgili projenin devreye alınması ve kullanımına bağlı destek deneyimini kapsar."], ["5'li ölçek", "Yalnız 1-5 memnuniyet ölçeği kullanılır; Uygulanamaz seçeneği bulunmaz. Müşteriye yalnız ilgili bölümler yöneltilir."], ["Kimlik bilgisi", "Müşteri birimi ve proje/ürün bilgisi zorunlu; cevaplayan kişinin adı isteğe bağlıdır."], ["Basit değerlendirme", "Sabit eşik veya otomatik uygunsuzluk tetikleyicisi kullanılmaz; sonuçlar bağlamla birlikte değerlendirilir."]]
        strategy = [["1. Uygulama kararını al", "BİDB Başkanı anketin ilgili proje için devreye alınmasını onaylar.", "BİDB Başkanı", "Yönetim kararı", "Henüz genel zorunluluk değildir"], ["2. Zamanı belirle", "Proje Yöneticisi müşteri birimiyle yaygın kullanım ve yeterli deneyim durumunu doğrular.", "Proje Yöneticisi", "Uygulama kapsamı", "Sabit gün sayısı yok"], ["3. Anketi hazırla", "Müşteriye yalnız ilgili ürün, geliştirme ve proje özel destek bölümlerini aç.", "Kalite Danışmanı", FRM003_TEMPLATE, "Kurum anket sistemi veya Google Forms"], ["4. Cevapları topla", "Birim/proje bilgisini al; kişi adını isteğe bağlı tut; 5'li cevap ve görüşleri kaydet.", "Kalite Danışmanı", "FRM.003 kayıtları / anket çıktısı", "Erişim yetkisi korunur"], ["5. Sonuçları değerlendir", "Üç boyutu ayrı özetle; müşteri görüşlerini bağlamla birlikte incele.", "Kalite Danışmanı", "RPR.002 taslağı", "Sabit eşik yok"], ["6. Gözden geçir ve onayla", "Proje Yöneticisi operasyonel doğruluğu gözden geçirir; BİDB Başkanı raporu onaylar.", "Proje Yöneticisi / BİDB Başkanı", "RPR.002", "Müşteri birimi rapor onaycısı değildir"], ["7. Uygunsuzluğu yönlendir", "Açık kalite uygunsuzluğu görülürse SRÇ.017'ye aktar.", "Kalite Danışmanı / Proje Yöneticisi", "SRÇ.017 kaydı", "Düşük puan tek başına otomatik kayıt değildir"], ["8. Kayıtları sakla", "Anket ham çıktısı ile onaylı RPR.002 arasında bağlantı kur ve erişimi sınırla.", "Kalite Danışmanı", "Anket sistemi / Google Drive / Confluence", "RPR.001'e aktarım yok"]]
        records = [[FRM003_TEMPLATE, "Anket formatı", "02 - Şablonlar", "Kalite Danışmanı", "Boş şablon"], ["FRM.003 - Müşteri Memnuniyeti Anketi ([Proje Adı])", "Gerçek müşteri cevapları", "Kurum anket sistemi / Google Forms / yetkili alan", "Kalite Danışmanı", "Yalnız uygulama gerçekleştiğinde"], [RPR002_TEMPLATE, "Rapor formatı", "02 - Şablonlar", "Kalite Danışmanı", "Boş şablon"], ["RPR.002 - Proje Müşteri Memnuniyeti Değerlendirme Raporu ([Proje Adı])", "Proje bazlı memnuniyet sonucu", "09 - Raporlar", "Kalite Danışmanı", "Hazırlayan: Kalite Danışmanı; gözden geçiren: Proje Yöneticisi; onay: BİDB Başkanı"], ["SRÇ.017 kalite uygunsuzluğu kaydı", "Doğrulanan uygunsuzluk", "Jira / ilgili süreç alanı", "İlgili Süreç Sahibi", "Koşullu"]]
    roles = [["BİDB Başkanı", "Kalite yönetimi veya anket devreye alma kararını ve nihai raporu onaylamak", "Nihai kurumsal karar vermek"], ["Kalite Danışmanı", "Yöntemi uygulamak, veriyi derlemek, analiz etmek ve kayıt/rapor hazırlamak", "Kalite değerlendirmesi ve yönlendirme önerisi vermek"], ["Proje Yöneticisi", "Proje ve müşteri girdilerini koordine etmek; sonuçları operasyonel olarak gözden geçirmek", "Anket zamanını müşteri birimiyle belirlemek ve düzeltme istemek"], ["Süreç / Proje Sahibi", "Kendi alanındaki hedef, kanıt ve uygulama bilgisini sağlamak", "Kendi görev alanında uygulama görüşü vermek"], ["Müşteri Birimi Temsilcisi", "Kullanım deneyimi ve geri bildirim sağlamak", "Kendi birimi adına görüş bildirmek"]]
    return "".join([
        "<h2>1. Prosedür Bilgileri</h2>", table(["Alan", "Değer"], [["Kurum", "İstanbul Üniversitesi - Cerrahpaşa Bilgi İşlem Daire Başkanlığı"], ["Prosedür Kodu ve Adı", title], ["Prosedür Referansı", SRC024], ["Prosedür Sahibi", OWNER], ["Durum", "Aktif"], ["Sürüm", "v1.0"], ["Yürürlük Tarihi", "15-02-2025"], ["Son Gözden Geçirme Tarihi", "15-07-2026"]]),
        "<h2>2. Amaç</h2>", para(purpose), "<h2>3. Kapsam</h2>", para(scope), "<h2>4. Kapsam Dışı</h2>", para(outside),
        "<h2>5. Referanslar</h2>", table(["Referans", "Açıklama"], refs),
        "<h2>6. Terimler ve Kısaltmalar</h2>", table(["Terim / Kısaltma", "Açıklama"], [["Kalite Hedefi", "Değerlendirilebilir kalite sonucu"], ["Kalite Uygunsuzluğu", "Tanımlı kalite hedefi, kriteri, gereksinimi veya standardının karşılanmaması"], ["YGG", "Yönetim Gözden Geçirme"], ["Doğal Kayıt", "İşin gerçek yürütülmesi sırasında kaynak sistemde oluşan kayıt"]]),
        "<h2>7. Roller ve Sorumluluklar</h2>", table(["Rol", "Sorumluluk", "Yetki"], roles),
        "<h2>8. Genel İlkeler</h2>", table(["İlke", "Açıklama"], principles),
        "<h2>9. Prosedür Esasları</h2>", table(["Esas / Kural", "Açıklama", "Zorunluluk", "Not"], [["Yetkili kapsam", scope, "Zorunlu", "SRÇ.024 kapsam sınırı"], ["İzlenebilir kayıt", "Sonuç ve kararlar yetkili kaynak kaydıyla ilişkilendirilir.", "Zorunlu", "Gerçekleşmemiş kayıt üretilmez"], ["Problem yönlendirmesi", "Kalite uygunsuzluğu SRÇ.017'ye aktarılır.", "Koşullu", "Kök neden SRÇ.017'de"], ["Doküman değişikliği", "Kontrollü doküman değişikliği SRÇ.018 üzerinden yürütülür.", "Koşullu", "Sürüm izlenebilirliği"]]),
        "<h2>10. Uygulama / Strateji Matrisi</h2>", table(["Alan / Aşama", "Uygulama Kuralı", "Sorumlu", "Kayıt / Kanıt", "Not"], strategy, fixed=True),
        "<h2>11. Yayın, Erişim ve Bakım Kuralları</h2>", table(["Kural Alanı", "Kural", "Sorumlu", "Kayıt / Kanıt"], [["Yayın", "Onaylı prosedür ve şablonlar Confluence'ta yayımlanır.", "Proje Yöneticisi", "Confluence sürümü"], ["Erişim", "Müşteri cevabı ve kalite kayıtlarına görev gereği erişim verilir.", "Belge Sahibi / Sistem Yöneticisi", "Kaynak sistem yetkileri"], ["Bakım", "Yılda bir veya yöntem/kapsam değiştiğinde gözden geçirilir.", "Kalite Danışmanı / Süreç Sahibi", "FRM.001 / doküman sürümü"], ["Değişiklik", "Kontrollü değişiklik SRÇ.018 ve SRÇ.001 kurallarıyla yürütülür.", "Kalite Danışmanı / Proje Yöneticisi", "SRÇ.018 / LST.002"]]),
        "<h2>12. Kayıtlar ve Kanıtlar</h2>", table(["Kayıt / Kanıt", "Kullanım Amacı", "Saklama Yeri", "Sorumlu", "Not"], records, fixed=True),
        "<h2>13. Sürüm Geçmişi</h2>", history(title.split(" - ", 1)[1], REVIEWER, APPROVER),
    ])


def frm003_template_body() -> str:
    scale = [["1", "Hiç memnun değilim"], ["2", "Memnun değilim"], ["3", "Kararsızım / Kısmen memnunum"], ["4", "Memnunum"], ["5", "Çok memnunum"]]
    def questions(items: list[str]) -> str:
        return table(["No", "Değerlendirme İfadesi", "Puan (1-5)"], [[str(i), q, "<em>1 / 2 / 3 / 4 / 5</em>"] for i, q in enumerate(items, 1)], fixed=True)
    return "".join([
        "<h2>0. Şablon Hakkında</h2>", "<h3>0.1. Şablon Üst Bilgisi</h3>", table(["Alan", "Değer"], [["Kurum", "İstanbul Üniversitesi - Cerrahpaşa Bilgi İşlem Daire Başkanlığı"], ["Doküman Kodu", "FRM.003.Ş"], ["Doküman Türü", "Form / Anket Şablonu"], ["Kullanım Alanı", "Yaygın kullanıma geçen projelerde müşteri memnuniyeti"], ["Durum", "Aktif - uygulama kararı bekleyen araç"], ["Sürüm", "v1.0"], ["Yürürlük Tarihi", "15-02-2025"]]),
        "<h3>0.2. Şablonun Kullanım Amacı</h3>", para("Yaygın kullanıma geçen yazılım projelerinde ürün, geliştirme hizmeti ve proje özelindeki destek memnuniyetini 5'li ölçekle toplamak için kullanılır. Şablonun varlığı anketin uygulanmış olduğu anlamına gelmez."),
        "<h3>0.3. Doküman Adlandırma Kuralı</h3>", para("FRM.003 - Müşteri Memnuniyeti Anketi ([Proje Adı])"),
        "<h3>0.4. Şablon Sürüm Geçmişi</h3>", history("Müşteri Memnuniyeti Anketi Şablonu", REVIEWER, APPROVER),
        "<h2>1. Anket Bilgileri</h2>", table(["Alan", "Değer"], [["Müşteri Birimi", "<em>Zorunlu</em>"], ["Proje / Ürün Adı", "<em>Zorunlu</em>"], ["Cevaplayan Kişi", "<em>İsteğe bağlı</em>"], ["Uygulama Tarihi", "<em>GG-AA-YYYY</em>"], ["Uygulanan Bölümler", "<em>Ürün / Geliştirme Hizmeti / Proje Özelindeki Destek</em>"]]),
        "<h2>2. Yanıtlama Ölçeği ve Kullanım Kuralı</h2>", table(["Puan", "Anlamı"], scale) + para("Müşteriye yalnız deneyimlediği bölümler yöneltilir ve yalnız 1-5 arasındaki beş cevap seçeneği gösterilir."),
        "<h2>3. Ürün Memnuniyeti</h2>", questions(["Ürün, birimimizin ihtiyaç ve gereksinimlerini karşılamaktadır.", "Ürünün kullanımı anlaşılır ve kolaydır.", "Ürünün performans ve güvenilirliği beklentimizi karşılamaktadır.", "Ürünün sunduğu çıktıların doğruluğu ve kalitesi yeterlidir.", "Üründen genel olarak memnunum."]),
        "<h2>4. Geliştirme Hizmeti Memnuniyeti</h2>", questions(["İhtiyaçlarımız geliştirme ekibi tarafından doğru anlaşılmıştır.", "Geliştirme sürecindeki iletişim ve bilgilendirme yeterlidir.", "Görüş ve geri bildirimlerimiz uygun biçimde değerlendirilmiştir.", "Ürünün devreye alınması ve kullanım geçişi uygun biçimde yönetilmiştir.", "Sunulan geliştirme hizmetinden genel olarak memnunum."]),
        "<h2>5. Proje Özelindeki Destek Memnuniyeti</h2>", questions(["Projeyle ilgili destek ekibine gerektiğinde ulaşabilmekteyiz.", "Destek taleplerimize uygun sürede geri dönüş yapılmaktadır.", "Sunulan çözümler proje kapsamındaki ihtiyacımızı karşılamaktadır.", "Destek sürecindeki bilgilendirme yeterlidir.", "Projeye özel destek hizmetinden genel olarak memnunum."]),
        "<h2>6. Genel Değerlendirme ve Görüşler</h2>", table(["Alan", "Yanıt"], [["Projeden genel memnuniyetiniz (1-5)", "<em>1 / 2 / 3 / 4 / 5</em>"], ["En memnun kaldığınız özellik / uygulama", "<em>Serbest görüş</em>"], ["Geliştirilmesini önerdiğiniz alan", "<em>Serbest görüş</em>"], ["Diğer görüş ve öneriler", "<em>Serbest görüş</em>"]]),
        "<h2>7. Kayıt ve Gizlilik Bilgisi</h2>", table(["Kural", "Açıklama"], [["Zorunlu bilgi", "Müşteri birimi ile proje/ürün adı zorunludur."], ["İsteğe bağlı bilgi", "Cevaplayan kişinin adı isteğe bağlıdır."], ["Kullanım", "Cevaplar yalnız kalite ve proje geliştirme amacıyla değerlendirilir."], ["Raporlama", "Sonuçlar RPR.002 - Proje Müşteri Memnuniyeti Değerlendirme Raporunda özetlenir."], ["Genel destek sınırı", "Genel ve sürekli BT destek hizmeti memnuniyeti ISO/IEC 20000-1 uygulamalarında ele alınır."]]),
    ])


def rpr002_template_body() -> str:
    return "".join([
        "<h2>0. Şablon Hakkında</h2>", "<h3>0.1. Şablon Üst Bilgisi</h3>", table(["Alan", "Değer"], [["Kurum", "İstanbul Üniversitesi - Cerrahpaşa Bilgi İşlem Daire Başkanlığı"], ["Doküman Kodu", "RPR.002.Ş"], ["Doküman Türü", "Rapor Şablonu"], ["Kullanım Alanı", "Proje müşteri memnuniyeti değerlendirmesi"], ["Durum", "Aktif"], ["Sürüm", "v1.0"], ["Yürürlük Tarihi", "15-02-2025"]]),
        "<h3>0.2. Şablonun Kullanım Amacı</h3>", para("Yaygın kullanıma geçen bir projeye ilişkin ürün, geliştirme hizmeti ve proje özelindeki destek memnuniyeti sonuçlarını proje bazında değerlendirmek için kullanılır."),
        "<h3>0.3. Doküman Adlandırma Kuralı</h3>", para("RPR.002 - Proje Müşteri Memnuniyeti Değerlendirme Raporu ([Proje Adı])"),
        "<h3>0.4. Şablon Sürüm Geçmişi</h3>", history("Proje Müşteri Memnuniyeti Değerlendirme Raporu Şablonu", REVIEWER, APPROVER),
        "<h2>1. Rapor Bilgileri</h2>", table(["Alan", "Değer"], [["Proje / Ürün", "<em>Proje adı</em>"], ["Müşteri Birimi", "<em>Birim adı</em>"], ["Değerlendirme Dönemi", "<em>Tarih / dönem</em>"], ["Hazırlayan", PREPARED_BY], ["Gözden Geçiren", "Proje Yöneticisi"], ["Onaylayan", OWNER], ["Durum", "<em>Taslak / Gözden Geçirildi / Onaylandı</em>"], ["Sürüm", "<em>v1.0</em>"]]),
        "<h2>2. Yönetici Özeti</h2>", para("[Projenin müşteri memnuniyeti görünümü, öne çıkan güçlü alanlar ve geliştirme ihtiyaçları.]"),
        "<h2>3. Kapsam ve Yöntem</h2>", table(["Alan", "Açıklama"], [["Anket Aracı", "<em>Kurumun anket sistemi / Google Forms / diğer onaylı araç</em>"], ["Uygulama Zamanı", "<em>Yaygın kullanım ve yeterli deneyim durumu</em>"], ["Değerlendirilen Bölümler", "<em>Ürün / Geliştirme / Proje özelindeki destek</em>"], ["Ölçek", "1-5 memnuniyet ölçeği"], ["Yöntem Notu", "Sabit eşik veya otomatik uygunsuzluk tetikleyicisi kullanılmaz."]]),
        "<h2>4. Katılım Özeti</h2>", table(["Gösterge", "Sonuç / Açıklama"], [["Davet edilen müşteri birimi / kullanıcı grubu", "<em>Bilgi</em>"], ["Geçerli cevap sayısı", "<em>Sayı</em>"], ["Cevap toplama dönemi", "<em>Tarih aralığı</em>"], ["Veri sınırlılıkları", "<em>Varsa açıklama</em>"]]),
        "<h2>5. Ürün Memnuniyeti Sonuçları</h2>", table(["Değerlendirme Alanı", "Ortalama / Dağılım", "Yorum"], [["Gereksinimleri karşılama", "<em>Sonuç</em>", "<em>Yorum</em>"], ["Kullanılabilirlik", "<em>Sonuç</em>", "<em>Yorum</em>"], ["Performans ve güvenilirlik", "<em>Sonuç</em>", "<em>Yorum</em>"], ["Çıktı doğruluğu ve kalitesi", "<em>Sonuç</em>", "<em>Yorum</em>"], ["Genel ürün memnuniyeti", "<em>Sonuç</em>", "<em>Yorum</em>"]]),
        "<h2>6. Geliştirme Hizmeti Memnuniyeti Sonuçları</h2>", table(["Değerlendirme Alanı", "Ortalama / Dağılım", "Yorum"], [["İhtiyacın anlaşılması", "<em>Sonuç</em>", "<em>Yorum</em>"], ["İletişim ve bilgilendirme", "<em>Sonuç</em>", "<em>Yorum</em>"], ["Geri bildirimin değerlendirilmesi", "<em>Sonuç</em>", "<em>Yorum</em>"], ["Devreye alma ve geçiş", "<em>Sonuç</em>", "<em>Yorum</em>"], ["Genel geliştirme hizmeti memnuniyeti", "<em>Sonuç</em>", "<em>Yorum</em>"]]),
        "<h2>7. Proje Özelindeki Destek Memnuniyeti Sonuçları</h2>", table(["Değerlendirme Alanı", "Ortalama / Dağılım", "Yorum"], [["Erişilebilirlik", "<em>Sonuç</em>", "<em>Yorum</em>"], ["Geri dönüş süresi", "<em>Sonuç</em>", "<em>Yorum</em>"], ["Çözüm yeterliliği", "<em>Sonuç</em>", "<em>Yorum</em>"], ["Bilgilendirme", "<em>Sonuç</em>", "<em>Yorum</em>"], ["Genel proje destek memnuniyeti", "<em>Sonuç</em>", "<em>Yorum</em>"]]),
        "<h2>8. Müşteri Görüşleri ve Önerileri</h2>", table(["Tema", "Özet Görüş", "Değerlendirme Notu"], [["Güçlü alan", "<em>Görüş özeti</em>", "<em>Not</em>"], ["Geliştirme önerisi", "<em>Görüş özeti</em>", "<em>Not</em>"], ["Diğer", "<em>Görüş özeti</em>", "<em>Not</em>"]]),
        "<h2>9. Kalite Danışmanı Değerlendirmesi</h2>", para("[Sonuçların proje bağlamı, güçlü alanlar, geliştirme ihtiyaçları ve olası kalite uygunsuzlukları açısından değerlendirmesi.]"),
        "<h2>10. Kalite Uygunsuzluğu ve Yönlendirmeler</h2>", table(["Konu", "Değerlendirme", "Hedef Süreç / Kayıt", "Bağlantı / Durum"], [["<em>Konu</em>", "<em>Kalite uygunsuzluğu / geliştirme ihtiyacı / izleme</em>", "<em>SRÇ.017 / SRÇ.018 / ilgili proje kaydı</em>", "<em>Bağlantı / durum</em>"]]),
        "<h2>11. Sonuç ve Öneriler</h2>", para("[Genel sonuç, önerilen izleme ve varsa yönetim kararı ihtiyacı.]"),
        "<h2>12. Sürüm Geçmişi</h2>", history("Proje Müşteri Memnuniyeti Değerlendirme Raporu", "Proje Yöneticisi", APPROVER),
    ])


def upsert_section_row(doc: str, heading_fragment: str, key: str, cells: list[str]) -> str:
    heads = list(re.finditer(r"<h2[^>]*>(.*?)</h2>", doc, flags=re.I | re.S))
    for i, head in enumerate(heads):
        title = html.unescape(re.sub(r"<[^>]+>", "", head.group(1)))
        if heading_fragment not in title:
            continue
        end = heads[i + 1].start() if i + 1 < len(heads) else len(doc)
        section = doc[head.end():end]
        tbody = re.search(r"(<tbody[^>]*>)(.*?)(</tbody>)", section, flags=re.I | re.S)
        if not tbody:
            raise RuntimeError(f"Table body not found under {heading_fragment}")
        rows = re.findall(r"<tr[^>]*>.*?</tr>", tbody.group(2), flags=re.I | re.S)
        rows = [row for row in rows if key not in html.unescape(re.sub(r"<[^>]+>", "", row))]
        new_row = "<tr>" + "".join(f'<td class="confluenceTd">{html.escape(cell)}</td>' for cell in cells) + "</tr>"
        section = section[:tbody.start(2)] + "".join(rows + [new_row]) + section[tbody.end(2):]
        return doc[:head.end()] + section + doc[end:]
    raise RuntimeError(f"Heading not found: {heading_fragment}")


def update_lst001() -> Path:
    page = CONFLUENCE / LST001_REL
    storage = html.unescape((page / "body.storage.xhtml").read_text(encoding="utf-8"))
    storage = upsert_section_row(storage, "3. Süreç Dokümanları", "SRÇ.024", ["SRÇ.024", "Kalite Yönetimi Süreci", "MAN.4", OWNER, "Aktif", "v1.0", "15-02-2025", "01 - Süreç Dokümanları"])
    storage = upsert_section_row(storage, "4. Prosedürler", "PRS.007", ["PRS.007", "Kalite Yönetimi Prosedürü", "SRÇ.024", OWNER, "Aktif", "v1.0", "15-02-2025", "07 - Prosedürler"])
    storage = upsert_section_row(storage, "4. Prosedürler", "PRS.008", ["PRS.008", "Müşteri Memnuniyeti Prosedürü", "SRÇ.024", OWNER, "Aktif", "v1.0", "15-02-2025", "07 - Prosedürler"])
    storage = upsert_section_row(storage, "6. Şablonlar", "FRM.003.Ş", ["FRM.003.Ş", "Müşteri Memnuniyeti Anketi Şablonu", "FRM.003 üretimi", "Aktif", "v1.0", "15-02-2025", "02 - Şablonlar"])
    storage = upsert_section_row(storage, "6. Şablonlar", "RPR.002.Ş", ["RPR.002.Ş", "Proje Müşteri Memnuniyeti Değerlendirme Raporu Şablonu", "RPR.002 üretimi", "Aktif", "v1.0", "15-02-2025", "02 - Şablonlar"])
    (page / "body.storage.xhtml").write_text(storage, encoding="utf-8")
    (page / "body.view.html").write_text(build_view("LST.001 - Aktif Dokümanlar Listesi", storage), encoding="utf-8")
    return page


def update_lst006() -> Path:
    page = CONFLUENCE / LST006_REL
    storage = html.unescape((page / "body.storage.xhtml").read_text(encoding="utf-8"))
    def replace(match: re.Match[str]) -> str:
        row = match.group(0)
        if "SRÇ.024" not in html.unescape(re.sub(r"<[^>]+>", "", row)):
            return row
        cells = re.findall(r"(<td[^>]*>)(.*?)(</td>)", row, flags=re.I | re.S)
        values = ["MAN.4", "Quality management", "SRÇ.024", "Kalite Yönetimi Süreci", OWNER, "Aktif", "Süreç paketi yerelde oluşturulmuş; kullanıcı incelemesi ve kontrollü Confluence yayını beklenmektedir."]
        return "<tr>" + "".join(f"{a}{html.escape(value)}{c}" for (a, _, c), value in zip(cells, values)) + "</tr>"
    storage = re.sub(r"<tr[^>]*>.*?</tr>", replace, storage, flags=re.I | re.S)
    (page / "body.storage.xhtml").write_text(storage, encoding="utf-8")
    (page / "body.view.html").write_text(build_view("LST.006 - Standart Süreç Envanteri", storage), encoding="utf-8")
    return page


def rebuild_parent_register(page_dir: Path, code_pattern: str, code_header: str, name_header: str) -> Path:
    items = []
    for child in page_dir.iterdir():
        meta = child / "page.yaml"
        if not meta.exists():
            continue
        title = str((yaml.safe_load(meta.read_text(encoding="utf-8")) or {}).get("title") or "")
        match = re.match(code_pattern, title)
        if match:
            items.append((match.group(1), match.group(2), title))
    items.sort(key=lambda item: item[0])
    rows = []
    for number, (code, name, title) in enumerate(items, 1):
        link = f'<ac:link><ri:page ri:space-key="SSSS" ri:content-title="{html.escape(title)}" /><ac:plain-text-link-body><![CDATA[İncele]]></ac:plain-text-link-body></ac:link>'
        rows.append([str(number), code, name, "Aktif", link])
    intro = "Bu sayfa, İÜC BİDB çalışmasında kullanılan doküman şablonları için kayıt tablosunu içerir." if code_header == "Şablon Kodu" else "Bu sayfa, İÜC BİDB çalışmasında kullanılan prosedür dokümanları için kayıt tablosunu içerir."
    body = para(intro) + table(["Sıra No", code_header, name_header, "Durum", "Erişim Linki"], rows)
    title = "02 - Şablonlar" if code_header == "Şablon Kodu" else "07 - Prosedürler"
    (page_dir / "body.storage.xhtml").write_text(body, encoding="utf-8")
    (page_dir / "body.view.html").write_text(build_view(title, body), encoding="utf-8")
    return page_dir


def upsert_index(page_dirs: list[Path]) -> None:
    index = yaml.safe_load(INDEX_PATH.read_text(encoding="utf-8")) or {}
    pages = index.setdefault("pages", [])
    rels = {str(d.relative_to(CONFLUENCE)).replace("\\", "/") for d in page_dirs if (d / "page.yaml").exists()}
    pages[:] = [item for item in pages if item.get("relative_path") not in rels]
    for directory in page_dirs:
        meta_path = directory / "page.yaml"
        if not meta_path.exists():
            continue
        meta = yaml.safe_load(meta_path.read_text(encoding="utf-8")) or {}
        rel = meta["relative_path"]
        pages.append({"page_id": str(meta.get("page_id") or ""), "title": meta["title"], "parent_id": str(meta.get("parent_id") or ""), "depth": meta["depth"], "relative_path": rel, "slug": meta["slug"], "storage_file": f"{rel}/body.storage.xhtml", "view_file": f"{rel}/body.view.html"})
    pages.sort(key=lambda item: (int(item.get("depth") or 0), str(item.get("relative_path") or "")))
    index["total_page_count"] = len(pages)
    index["exported_at"] = datetime.now(timezone.utc).isoformat()
    INDEX_PATH.write_text(yaml.safe_dump(index, allow_unicode=True, sort_keys=False), encoding="utf-8")
    for directory in [
        PAGE_ROOT / "02-sablonlar",
        PAGE_ROOT / "07-prosedurler",
        PAGE_ROOT / "91-ic-denetimler/surec-gozden-gecirmeleri",
        CONFLUENCE / SRC024_REL,
    ]:
        meta_path = directory / "page.yaml"
        if not meta_path.exists():
            continue
        meta = yaml.safe_load(meta_path.read_text(encoding="utf-8")) or {}
        stable = str(meta.get("page_id") or f"local:{meta.get('relative_path')}")
        meta["children_count"] = sum(
            1 for item in pages if str(item.get("parent_id") or "") == stable
        )
        meta_path.write_text(
            yaml.safe_dump(meta, allow_unicode=True, sort_keys=False), encoding="utf-8"
        )


def append_section_row(
    document: str,
    heading: str,
    key: str,
    cells: list[str],
    *,
    before_key: str | None = None,
) -> str:
    headings = list(re.finditer(r"<h2[^>]*>(.*?)</h2>", document, flags=re.I | re.S))
    for index, match in enumerate(headings):
        title = html.unescape(re.sub(r"<[^>]+>", "", match.group(1))).strip()
        if title != heading:
            continue
        end = headings[index + 1].start() if index + 1 < len(headings) else len(document)
        section = document[match.end():end]
        tbody = re.search(r"(<tbody[^>]*>)(.*?)(</tbody>)", section, flags=re.I | re.S)
        if not tbody:
            raise RuntimeError(f"No table under {heading}")
        rows = [
            row
            for row in re.findall(r"<tr[^>]*>.*?</tr>", tbody.group(2), flags=re.I | re.S)
            if key not in html.unescape(re.sub(r"<[^>]+>", "", row))
        ]
        new_row = "<tr>" + "".join(
            f'<td class="confluenceTd">{html.escape(value)}</td>' for value in cells
        ) + "</tr>"
        if before_key:
            position = next(
                (
                    row_index
                    for row_index, row in enumerate(rows)
                    if before_key in html.unescape(re.sub(r"<[^>]+>", "", row))
                ),
                len(rows),
            )
            rows.insert(position, new_row)
        else:
            rows.append(new_row)
        section = section[:tbody.start(2)] + "".join(rows) + section[tbody.end(2):]
        return document[:match.end()] + section + document[end:]
    raise RuntimeError(f"Heading not found: {heading}")


def update_rpr001() -> Path:
    page = CONFLUENCE / RPR001_REL
    storage = html.unescape((page / "body.storage.xhtml").read_text(encoding="utf-8"))
    storage = storage.replace(
        "Şu aşamada SRÇ.001, SRÇ.004, SRÇ.005, SRÇ.006, SRÇ.021 ve SRÇ.023 değerlendirmeleri rapora alınmıştır.",
        "Şu aşamada SRÇ.001, SRÇ.004, SRÇ.005, SRÇ.006, SRÇ.021, SRÇ.023 ve SRÇ.024 değerlendirmeleri rapora alınmıştır.",
    )
    storage = append_section_row(
        storage,
        "4. Süreç Sonuç Özeti",
        "SRÇ.024",
        [
            SRC024,
            "MAN.4 BP1-BP8; PA 2.1-PA 3.2",
            "3 VAR; 2 DAĞINIK; 3 ZAYIF",
            "12 VAR; 6 DAĞINIK; 3 ZAYIF",
            "",
            "FRM.001 - Süreç Gözden Geçirme Formu (SRÇ.024) - Değerlendirme #1",
            "Kalite hedefleri, yönetim döngüsü, uygunsuzluk yönlendirmesi ve proje müşteri memnuniyeti yöntemi tanımlı; gerçek anket, RPR.002, yıllık hedef değerlendirmesi ve bağlı süreç uygulama kanıtları henüz oluşmamıştır.",
        ],
    )
    storage = append_section_row(
        storage,
        "5. Etiket Dağılımları ve Eğilimler",
        "SRÇ.024",
        ["SRÇ.024", "3", "2", "3", "0", "12", "6", "3", "0"],
        before_key="Eğilim Yorumu",
    )
    (page / "body.storage.xhtml").write_text(storage, encoding="utf-8")
    (page / "body.view.html").write_text(
        build_view("RPR.001 - Süreç Performansları Raporu", storage), encoding="utf-8"
    )
    return page


def update_status_and_report() -> None:
    current = ROOT / "docs/CURRENT_STATUS.md"
    text = current.read_text(encoding="utf-8")
    old_addition = "- SRÇ.024 Kalite Yönetimi paketi; süreç tanımı, PRS.007, PRS.008, FRM.003.Ş, RPR.002.Ş, süreç özel LST.007-LST.010, boş FRM.001 ve Değerlendirme #1 ile yerelde oluşturulmuştur. Gerçek anket/RPR.002 üretilmemiş, RPR.001 değiştirilmemiş ve Confluence yayını kullanıcı incelemesine bırakılmıştır.\n"
    text = text.replace(old_addition, "")
    addition = "- SRÇ.024 Kalite Yönetimi paketi; süreç tanımı, PRS.007, PRS.008, FRM.003.Ş, RPR.002.Ş, süreç özel LST.007-LST.010, boş FRM.001 ve Değerlendirme #1 ile yerelde oluşturulmuş; değerlendirme sonuçları RPR.001'e eklenmiştir. Gerçek anket/RPR.002 üretilmemiş ve Confluence yayını kullanıcı incelemesine bırakılmıştır.\n"
    if addition not in text:
        text += ("\n" if not text.endswith("\n") else "") + addition
        current.write_text(text, encoding="utf-8")
    report = ROOT / "reports/src024_quality_management_package_report.md"
    report.write_text("""# SRÇ.024 Kalite Yönetimi Paketi Yerel Raporu

Tarih: 15-07-2026

## Oluşturulan Yapı

- SRÇ.024 süreç tanımı MAN.4 BP1-BP8 izlenebilirliğiyle oluşturuldu.
- PRS.007 Kalite Yönetimi Prosedürü ve PRS.008 Müşteri Memnuniyeti Prosedürü hazırlandı.
- FRM.003.Ş ürün, geliştirme ve proje özelindeki destek memnuniyetini 5'li ölçekle ölçmek üzere oluşturuldu.
- RPR.002.Ş proje bazlı müşteri memnuniyeti değerlendirmesi için oluşturuldu.
- Süreç özel LST.007-LST.010, boş FRM.001 ve Değerlendirme #1 hazırlandı.
- LST.001 ve LST.006 güncellendi. LST.012 gerçek Confluence yayını gerçekleşmeden değiştirilmedi.
- RPR.001'e SRÇ.024 Değerlendirme #1 sonuç özeti ve etiket dağılımları eklendi; gerçek müşteri memnuniyeti verisi yalnız RPR.002 ailesinde tutuldu.

## Değerlendirme Özeti

- BP: 3 VAR, 2 DAĞINIK, 3 ZAYIF.
- PA/GP: 12 VAR, 6 DAĞINIK, 3 ZAYIF.
- Gerçek anket, RPR.002, yıllık kalite hedefi değerlendirmesi ve bağlı süreç kanıtları henüz bulunmadığından uygulama alanları ihtiyatlı etiketlendi.

## Yayın Durumu

- Çalışma yalnız yerel repository ve viewer için hazırlanmıştır.
- Confluence'a yazma yapılmamıştır; kullanıcı incelemesi ve onayı beklenmektedir.
""", encoding="utf-8")


def validate(page_dirs: list[Path]) -> None:
    process = (CONFLUENCE / SRC024_REL / "body.storage.xhtml").read_text(encoding="utf-8")
    headings = [html.unescape(re.sub(r"<[^>]+>", "", h)) for h in re.findall(r"<h2[^>]*>(.*?)</h2>", process, flags=re.S)]
    expected = ["1. Süreç Bilgileri", "2. Amaç", "3. Kapsam", "4. Referanslar", "5. Terimler ve Kısaltmalar", "6. Süreç Aktivitesi", "7. Roller ve Sorumluluklar", "8. Araçlar ve Altyapı", "9. Süreç İş Ürünleri", "10. Süreç Akışı", "11. Süreç Faaliyetleri", "12. Ölçüm ve İzleme", "13. Uygulama ve Uyarlama Kuralları", "14. Süreç Etkileşimleri", "15. Sürüm Geçmişi"]
    if headings != expected:
        raise RuntimeError(f"SRÇ.024 heading mismatch: {headings}")
    for bp, _, _ in MAN4_BPS:
        if bp not in process:
            raise RuntimeError(f"Missing BP trace: {bp}")
    process_plain = html.unescape(re.sub(r"<[^>]+>", "", process))
    if "RPR.001'e müşteri memnuniyeti verisi eklenmez" not in process_plain or "26 süreç" in process_plain:
        raise RuntimeError("Scope or forbidden expression validation failed")
    for directory in page_dirs:
        for name in ["page.yaml", "body.storage.xhtml", "body.view.html"]:
            if not (directory / name).exists():
                raise RuntimeError(f"Missing artifact: {directory / name}")
    assessment = (CONFLUENCE / REVIEWS_REL / "frm-001-surec-gozden-gecirme-formu-src-024-degerlendirme-1/body.storage.xhtml").read_text(encoding="utf-8")
    if "3 VAR, 2 DAĞINIK ve 3 ZAYIF" not in assessment or "12 VAR, 6 DAĞINIK ve 3 ZAYIF" not in assessment:
        raise RuntimeError("Assessment distribution mismatch")
    frm = (CONFLUENCE / TEMPLATES_REL / "frm-003-s-musteri-memnuniyeti-anketi-sablonu/body.storage.xhtml").read_text(encoding="utf-8")
    if "Uygulanamaz" in frm or not all(term in frm for term in ["Ürün Memnuniyeti", "Geliştirme Hizmeti", "Proje Özelindeki Destek"]):
        raise RuntimeError("FRM.003.Ş structure mismatch")
    rpr = (CONFLUENCE / TEMPLATES_REL / "rpr-002-s-proje-musteri-memnuniyeti-degerlendirme-raporu-sablonu/body.storage.xhtml").read_text(encoding="utf-8")
    if "RPR.001" in rpr or "SRÇ.017" not in rpr:
        raise RuntimeError("RPR.002.Ş separation mismatch")
    rpr001 = (CONFLUENCE / RPR001_REL / "body.storage.xhtml").read_text(encoding="utf-8")
    if rpr001.count("SRÇ.024 - Kalite Yönetimi Süreci") != 1 or "3 VAR; 2 DAĞINIK; 3 ZAYIF" not in rpr001:
        raise RuntimeError("RPR.001 SRÇ.024 summary mismatch")


def main() -> None:
    src = CONFLUENCE / SRC024_REL
    attachments = src / "attachments"
    attachments.mkdir(parents=True, exist_ok=True)
    (attachments / FLOW_MMD).write_text("\n".join(FLOW_LINES) + "\n", encoding="utf-8")
    write_page(src, SRC024, "137265784", "01 - Süreç Dokümanları", 2, process_body(True), process_body(False))
    pages: list[Path] = [src]
    children = [
        ("lst-007-surec-etkilesim-matrisi-src-024", "LST.007 - Süreç Etkileşim Matrisi (SRÇ.024)", lst007_body(True), lst007_body(False)),
        ("lst-008-is-urunleri-ve-kalite-kriterleri-listesi-src-024", "LST.008 - İş Ürünleri ve Kalite Kriterleri Listesi (SRÇ.024)", lst008_body(), None),
        ("lst-009-surec-performans-olcum-seti-src-024", "LST.009 - Süreç Performans Ölçüm Seti (SRÇ.024)", lst009_body(), None),
        ("lst-010-surec-rol-yetki-ve-raci-matrisi-src-024", "LST.010 - Süreç Rol Yetki ve RACI Matrisi (SRÇ.024)", lst010_body(), None),
    ]
    for slug, title, storage, view in children:
        directory = src / slug
        write_page(directory, title, SRC024_ID, SRC024, 3, storage, view)
        pages.append(directory)
        if slug.startswith("lst-007"):
            interaction = directory / "attachments"
            interaction.mkdir(exist_ok=True)
            (interaction / INTERACTION_MMD).write_text("\n".join(INTERACTION_LINES) + "\n", encoding="utf-8")
    blank = src / "frm-001-surec-gozden-gecirme-formu-src-024"
    write_page(blank, "FRM.001 - Süreç Gözden Geçirme Formu (SRÇ.024)", SRC024_ID, SRC024, 3, blank_review_body())
    pages.append(blank)
    assessment = CONFLUENCE / REVIEWS_REL / "frm-001-surec-gozden-gecirme-formu-src-024-degerlendirme-1"
    write_page(assessment, "FRM.001 - Süreç Gözden Geçirme Formu (SRÇ.024) - Değerlendirme #1", REVIEWS_ID, "Süreç Gözden Geçirmeleri", 3, assessment_body())
    pages.append(assessment)
    for slug, title, body in [
        ("prs-007-kalite-yonetimi-proseduru", PRS007, procedure_body("quality")),
        ("prs-008-musteri-memnuniyeti-proseduru", PRS008, procedure_body("customer")),
    ]:
        directory = CONFLUENCE / PROCEDURES_REL / slug
        write_page(directory, title, PROCEDURES_ID, "07 - Prosedürler", 2, body)
        pages.append(directory)
    for slug, title, body in [
        ("frm-003-s-musteri-memnuniyeti-anketi-sablonu", FRM003_TEMPLATE, frm003_template_body()),
        ("rpr-002-s-proje-musteri-memnuniyeti-degerlendirme-raporu-sablonu", RPR002_TEMPLATE, rpr002_template_body()),
    ]:
        directory = CONFLUENCE / TEMPLATES_REL / slug
        write_page(directory, title, TEMPLATES_ID, "02 - Şablonlar", 2, body)
        pages.append(directory)
    pages.extend([update_lst001(), update_lst006()])
    pages.append(update_rpr001())
    pages.append(rebuild_parent_register(PAGE_ROOT / "02-sablonlar", r"^([A-ZÇŞİÜÖĞ]+\.\d{3}|[A-ZÇŞİÜÖĞ]+\.XXX)\.Ş\s+-\s+(.+)$", "Şablon Kodu", "Şablon Adı"))
    pages.append(rebuild_parent_register(PAGE_ROOT / "07-prosedurler", r"^(PRS\.\d{3})\s+-\s+(.+)$", "Prosedür Kodu", "Prosedür Adı"))
    unique = list(dict.fromkeys(pages))
    upsert_index(unique)
    update_status_and_report()
    validate([directory for directory in unique if (directory / "page.yaml").exists()])
    print(f"[DONE] SRÇ.024 package materialized: {len(unique)} page directories")


if __name__ == "__main__":
    main()
