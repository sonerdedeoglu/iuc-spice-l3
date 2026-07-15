#!/usr/bin/env python3
"""Create the local SRÇ.025 measurement package without writing to Confluence."""
from __future__ import annotations

import html
import re
from datetime import datetime, timezone
from pathlib import Path

import yaml

import create_src024_quality_management_package as core
from align_lst010_to_src006_structure import process_body as raci_body


ROOT = Path(__file__).resolve().parents[1]
CONFLUENCE = core.CONFLUENCE
PAGE_ROOT = core.PAGE_ROOT
PAGE_ROOT_REL = core.PAGE_ROOT_REL
INDEX_PATH = core.INDEX_PATH

SRC025_ID = "137265883"
SRC025 = "SRÇ.025 - Ölçüm Süreci"
PRS009 = "PRS.009 - Ölçüm ve Analiz Prosedürü"
OWNER = "Levent BAYEZİT - Proje Yöneticisi"
REVIEWER = "Seçil NEBİLER - İdari İşler Şube Müdürü"
APPROVER = "Mustafa Nusret SARISAKAL - Bilgi İşlem Daire Başkanı"

SRC025_REL = f"{PAGE_ROOT_REL}/01-surec-dokumanlari/src-025-olcum-sureci"
RECORDS_REL = f"{PAGE_ROOT_REL}/03-kayitlar-ve-listeler"
LST001_REL = f"{RECORDS_REL}/lst-001-aktif-dokumanlar-listesi"
LST006_REL = f"{RECORDS_REL}/lst-006-standart-surec-envanteri"
RPR001_REL = f"{PAGE_ROOT_REL}/09-raporlar/rpr-001-surec-performanslari-raporu"

FLOW_PNG = "SRÇ.025 - Flowchart.png"
FLOW_MMD = "src025-surec-akisi.mmd"
INTERACTION_PNG = "src025-surec-etkilesim.png"
INTERACTION_MMD = "src025-surec-etkilesim.mmd"

MAN6_BPS = [
    ("MAN.6.BP1", "Ölçüm taahhüdünü oluştur", "Yönetim ve çalışanların ölçüm sürecini uygulama taahhüdünü oluşturmak, sürdürmek ve ilgili birime duyurmak."),
    ("MAN.6.BP2", "Ölçüm stratejisini geliştir", "Kurumsal ve proje ihtiyaçlarına dayalı ölçüm faaliyetlerini ve sonuçlarını belirleme, yürütme ve değerlendirme stratejisini tanımlamak."),
    ("MAN.6.BP3", "Ölçüm bilgi ihtiyaçlarını belirle", "Kurumsal ve yönetim süreçlerinin kararlarını destekleyecek ölçüm bilgi ihtiyaçlarını belirlemek."),
    ("MAN.6.BP4", "Ölçümleri tanımla", "Belirlenen bilgi ihtiyaçlarına dayalı, uygulanabilir ve anlamlı ölçüm setini geliştirmek."),
    ("MAN.6.BP5", "Ölçüm verisini topla ve sakla", "Veriyi doğrulamak, anlamak ve değerlendirmek için gerekli bağlam bilgileriyle birlikte ölçüm verisini toplamak ve saklamak."),
    ("MAN.6.BP6", "Ölçüm verisini analiz et", "Ölçüm verisini analiz edip yorumlamak ve kararları destekleyecek bilgi ürünlerini geliştirmek."),
    ("MAN.6.BP7", "Bilgi ürünlerini kararlarda kullan", "Doğru ve güncel ölçüm bilgi ürünlerini ilgili karar süreçleri için erişilebilir kılmak."),
    ("MAN.6.BP8", "Ölçüm sonuçlarını paylaş", "Ölçüm bilgi ürünlerini kullanacak taraflara iletmek ve kullanım uygunluğuna ilişkin geri bildirim toplamak."),
    ("MAN.6.BP9", "Ölçüm faaliyetlerini değerlendir", "Bilgi ürünlerini ve ölçüm faaliyetlerini bilgi ihtiyaçları ile stratejiye göre değerlendirip iyileştirme ihtiyacını süreç sahiplerine iletmek."),
]

FLOW_LINES = [
    "%%{init: {'flowchart': {'htmlLabels': false}}}%%",
    "flowchart TD",
    'A["Yönetim, süreç veya proje bilgi ihtiyacı"] --> B["Ölçüm taahhüdü ve stratejisi doğrulanır"]',
    'B --> C["Desteklenecek karar ve bilgi ihtiyacı tanımlanır"]',
    'C --> D["Uygulanabilir ölçüm LST.009 içinde tanımlanır"]',
    'D --> E["Kaynak veri bağlam bilgileriyle doğal sistemden alınır"]',
    'E --> F["Veri doğrulanır, analiz edilir ve yorumlanır"]',
    'F --> G["RPR, gösterge, tablo veya karar girdisi hazırlanır"]',
    'G --> H["Bilgi ürünü yetkili karar sahiplerine sunulur"]',
    'H --> I["Kullanım ve anlaşılabilirlik geri bildirimi alınır"]',
    'I --> J["Ölçüm ve bilgi ürünü yıllık YGG hazırlığında değerlendirilir"]',
    'J --> K{"Ölçüm değişikliği gerekli mi?"}',
    'K -- "Hayır" --> C',
    'K -- "Evet" --> L["SRÇ.018 kontrollü değişiklik"]',
    'L --> M{"Kapsamlı süreç iyileştirmesi mi?"}',
    'M -- "Evet" --> N["SRÇ.006 süreç iyileştirmesi"]',
    'M -- "Hayır" --> D',
    'N --> D',
]

INTERACTION_LINES = [
    "%%{init: {'flowchart': {'htmlLabels': false}}}%%",
    "flowchart LR",
    'A["SRÇ.023 yönetim kararları ve bilgi ihtiyaçları"] --> Q["SRÇ.025 Ölçüm"]',
    'B["SRÇ.024 kalite hedefleri"] --> Q',
    'C["SRÇ.002 güvence ve SRÇ.005 değerlendirme sonuçları"] --> Q',
    'D["SRÇ.007 proje yönetimi ve süreç sahipleri"] --> Q',
    'E["Jira, Confluence, Bitbucket, Google Drive ve doğal kayıtlar"] --> Q',
    'Q --> P["PRS.009 Ölçüm ve Analiz Prosedürü"]',
    'Q --> L["Süreç özel LST.009 ölçüm tanımları"]',
    'Q --> R1["RPR.001 süreç performansı bilgi ürünü"]',
    'Q --> R2["RPR.002 ve proje özel bilgi ürünleri"]',
    'Q --> Y["SRÇ.023 YGG karar girdisi"]',
    'Q --> X["SRÇ.018 ölçüm değişikliği"]',
    'X --> I["SRÇ.006 kapsamlı iyileştirme"]',
]


def process_page(storage: bool) -> str:
    related = "<br />".join([
        "SRÇ.002 - Kalite Güvencesi Süreci",
        "SRÇ.005 - Süreç Değerlendirme Süreci",
        "SRÇ.006 - Süreç İyileştirme Süreci",
        "SRÇ.007 - Proje Yönetimi Süreci",
        "SRÇ.018 - Değişiklik Talebi Yönetimi Süreci",
        "SRÇ.021 - Bilgi Yönetimi Süreci",
        "SRÇ.023 - Organizasyonel Yönetim Süreci",
        "SRÇ.024 - Kalite Yönetimi Süreci",
    ])
    mermaid = core.info_macro("Mermaid Kodu", FLOW_LINES) if storage else core.info_view("Mermaid Kodu", FLOW_LINES)
    activities = [
        ["F1", "Ölçüm taahhüdünü oluştur", "Yönetim ve ilgili rollerin ölçüm verisini zamanında üretme, doğrulama ve kullanma sorumlulukları belirlenir ve duyurulur. (MAN.6.BP1)", SRC025],
        ["F2", "Ölçüm stratejisini geliştir", "Bilgi ihtiyacına dayalı, az sayıda ölçüm kullanan, doğal kaynak sistemleri ve mevcut bilgi ürünlerini esas alan strateji tanımlanır. (MAN.6.BP2)", PRS009],
        ["F3", "Bilgi ihtiyacını belirle", "Her ölçüm için desteklenecek yönetim veya proje kararı, kullanıcı, dönem ve beklenen bilgi ürünü belirlenir. (MAN.6.BP3)", "Bilgi ihtiyacı / karar bağlantısı"],
        ["F4", "Ölçümü tanımla", "Tanım, hesaplama, veri kaynağı, sıklık, sorumlu, hedef veya değerlendirme yöntemi ve sonuç kullanım yeri ilgili LST.009'a yazılır. (MAN.6.BP4)", "LST.009 - Süreç Performans Ölçüm Seti"],
        ["F5", "Veriyi topla ve sakla", "Veri; dönem, kapsam, kaynak bağlantısı, yöntem, hazırlayan, analiz tarihi ve sınırlamalarla birlikte doğal sisteminde tutulur. (MAN.6.BP5)", "Bağlam bilgili ölçüm verisi"],
        ["F6", "Veriyi analiz et", "Veri hedefe, eğilime, başlangıç değerine, gerçekleşme durumuna veya nitel yönteme göre analiz edilip yorumlanır. (MAN.6.BP6)", "Ölçüm bilgi ürünü"],
        ["F7", "Kararlarda kullan", "Güncel bilgi ürünü ilgili süreç, proje, kalite veya yönetim kararında erişilebilir kılınır. (MAN.6.BP7)", "RPR.001 / RPR.002 / proje raporu / karar girdisi"],
        ["F8", "Sonucu paylaş", "Ölçüm sonucu ilgili taraflara planlanan tarihte sunulur; anlaşılabilirlik ve kullanım uygunluğu geri bildirimi alınır. (MAN.6.BP8)", "Sunum / toplantı / bağlantı / doğal bilgilendirme kaydı"],
        ["F9", "Ölçümü değerlendir", "Ölçümün bilgi ihtiyacını karşılaması, veri güvenilirliği, iş yükü ve kullanılabilirliği yıllık YGG hazırlığında gözden geçirilir. (MAN.6.BP9)", "Ölçüm gözden geçirme sonucu; koşullu SRÇ.018 / SRÇ.006"],
    ]
    return "".join([
        "<h2>1. Süreç Bilgileri</h2>", core.table(["Alan", "Değer"], [
            ["Kurum", "İstanbul Üniversitesi - Cerrahpaşa Bilgi İşlem Daire Başkanlığı"],
            ["Süreç Kodu ve Adı", SRC025], ["Süreç Referansı", "ISO/IEC 15504-5:2006 MAN.6 - Measurement"],
            ["Süreç Sahibi", OWNER], ["Hedef Kitle", "BİDB Başkanı, Proje Yöneticisi, Kalite Danışmanı, süreç/proje sahipleri, veri sahipleri ve ölçüm sonuçlarını kullanan ilgili roller"],
            ["Yayın ve Erişim Ortamı", "Confluence; kontrollü kaynaklar için Bitbucket; faaliyet ve proje verileri için Jira; yetkili ekler için Google Drive"],
            ["Durum", "Aktif"], ["Sürüm", "v1.0"], ["Yürürlük Tarihi", "15-02-2025"], ["Son Gözden Geçirme Tarihi", "15-07-2026"],
            ["Güncelleme Sıklığı", "Yılda en az bir kez veya bilgi ihtiyacı, ölçüm, veri kaynağı, raporlama ya da karar yapısı değiştiğinde"],
        ]),
        "<h2>2. Amaç</h2>", core.para("Bu sürecin amacı; BİDB bünyesinde uygulanan süreçler, projeler ve geliştirilen ürünlerle ilgili verileri bilgi ihtiyaçlarına dayalı olarak toplamak, analiz etmek ve etkili yönetim ile ürün kalitesinin nesnel gösterimi için kullanılabilir bilgi ürünlerine dönüştürmektir."),
        "<h3>2.1. Süreç Sonuçları</h3>", core.table(["Sonuç ID", "Süreç Sonucu"], [
            ["S1", "Ölçüm sürecini uygulamak için kurumsal taahhüt oluşturulur ve sürdürülür."],
            ["S2", "Kurumsal ve yönetim süreçlerinin ölçüm bilgi ihtiyaçları belirlenir."],
            ["S3", "Bilgi ihtiyaçlarından türetilen uygulanabilir ölçüm setleri geliştirilir."],
            ["S4", "Ölçüm faaliyetleri belirlenir ve gerçekleştirilir."],
            ["S5", "Gerekli veri bağlamıyla toplanır, saklanır, analiz edilir ve yorumlanır."],
            ["S6", "Bilgi ürünleri kararları desteklemek ve nesnel iletişim sağlamak için kullanılır."],
            ["S7", "Ölçüm süreci, ölçümler ve bilgi ürünleri değerlendirilerek süreç sahiplerine iletilir."],
        ]),
        "<h2>3. Kapsam</h2>", core.table(["Kapsam Öğesi", "Açıklama"], [
            ["Kapsama Dahil", "LST.006 standart süreç envanterindeki süreçlerin ve BİDB yazılım projelerinin bilgi ihtiyaçları, ölçüm tanımları, doğal kaynak verileri, analizleri, mevcut rapor/gösterge bilgi ürünleri ve bunların karar süreçlerinde kullanımı"],
            ["Kapsam Dışı", "Yeni merkezi ölçüm veri tabanı veya genel ölçüm raporu; bilgi ihtiyacına dayanmayan göstergeler; ilgili süreç ya da proje sahibinin sorumluluğundaki faaliyetlerin SRÇ.025 altında yeniden işletilmesi"],
            ["Uygulama Alanı", "Süreç özel LST.009 ölçümleri, proje ölçümleri, RPR.001, RPR.002 ve ilgili doğal rapor/gösterge/karar girdileri"],
        ]),
        "<h2>4. Referanslar</h2>", core.table(["Referans", "Açıklama"], [
            ["ISO/IEC 15504-5:2006 MAN.6 - Measurement", "Süreç amacı, sonuçları ve MAN.6.BP1-BP9 temel uygulamaları"],
            ["ISO/IEC 15504-5:2006 - Process Assessment Model", "Süreç boyutu ve değerlendirme göstergeleri"],
            ["ISO/IEC 15504-5:2006 - Process Attributes", "PA 2.1, PA 2.2, PA 3.1 ve PA 3.2 süreç öznitelikleri ile genel uygulamalar"],
        ]),
        "<h2>5. Terimler ve Kısaltmalar</h2>", core.table(["Terim / Kısaltma", "Açıklama"], [
            ["Bilgi İhtiyacı", "Bir yönetim, süreç veya proje kararını desteklemek için cevaplanması gereken soru"],
            ["Ölçüm", "Belirli bir bilgi ihtiyacını karşılamak üzere tanımı, kaynağı, yöntemi ve kullanım yeri belirlenmiş gösterge"],
            ["Bilgi Ürünü", "Analiz ve yorum içeren rapor, gösterge, tablo, sunum veya karar girdisi"],
            ["Başlangıç Değeri", "Geçmiş veri veya geçerli hedef bulunmadığında ilk ölçüm döneminde oluşturulan karşılaştırma değeri"],
            ["Doğal Kayıt", "İşin gerçek yürütülmesi sırasında kaynak sistemde oluşan kayıt"],
        ]),
        "<h2>6. Süreç Aktivitesi</h2>", core.table(["Alan", "Açıklama"], [
            ["Süreç Başlatıcısı", "Yeni veya değişen yönetim/proje bilgi ihtiyacı; yeni süreç ölçümü; raporlama dönemi; veri kaynağı değişikliği; yıllık ölçüm gözden geçirmesi"],
            ["Süreç Başlangıcı", "Desteklenecek kararın ve ölçüm bilgi ihtiyacının belirlenmesi"],
            ["Süreç Bitişi", "Bilgi ürününün ilgili karar sahiplerine sunulması, kullanım geri bildiriminin alınması ve ölçümün sürdürülmesi/değiştirilmesi kararının verilmesi"],
            ["Ana Faaliyetler", "Taahhüt ve strateji; bilgi ihtiyacı; ölçüm tanımı; veri toplama/saklama; analiz; bilgi ürünü; karar kullanımı; paylaşım ve gözden geçirme"],
            ["İlgili Süreçler", related],
        ]),
        "<h2>7. Roller ve Sorumluluklar</h2>", core.para("Süreçteki rol, sorumluluk, yetkinlik, RACI ve onay ilişkileri LST.010 - Süreç Rol Yetki ve RACI Matrisi (SRÇ.025) dokümanında yönetilir. Proje Yöneticisi ölçüm stratejisinin işletilmesini; Kalite Danışmanı tanım, birleştirme ve analizi; ilgili süreç/veri sahibi kaynak verinin doğruluğunu; BİDB Başkanı kurumsal öncelik ve kaynak kararlarını yürütür."),
        "<h2>8. Araçlar ve Altyapı</h2>", core.table(["Tür", "Araç / Altyapı Bileşeni", "Kullanım Amacı", "Erişim ve Kullanım Koşulu", "Sorumlu Rol / Birim"], [
            ["Araç", "Confluence", "LST.009, süreç değerlendirmeleri, raporlar, gösterge ve karar bağlantılarının yayımlanması", "Kurumsal hesap ve sayfa yetkisi", "Proje Yöneticisi / Belge Sahibi"],
            ["Araç", "Jira", "Proje, problem, değişiklik ve faaliyet ölçüm verilerinin doğal kaynağı", "Proje ve rol bazlı yetki", "Proje Yöneticisi / İlgili Süreç Sahibi"],
            ["Araç", "Bitbucket", "Kod, değişiklik ve sürüm kontrollü kaynak verilerin doğal kaynağı", "Repository yetkisi", "Proje Yöneticisi / Repository Yöneticisi"],
            ["Araç", "Google Drive", "Yetkili ekler, müşteri paylaşımları ve kaynak dosyalara bağlantı", "Kurumsal hesap ve klasör yetkisi", "Belge / Veri Sahibi"],
            ["Altyapı", "RPR.001, RPR.002 ve proje özel rapor/göstergeleri", "Ölçüm verisini karar için kullanılabilir bilgi ürününe dönüştürmek", "İlgili doküman ve veri erişim yetkisi", "Kalite Danışmanı / Proje Yöneticisi / İlgili Süreç Sahibi"],
        ], fixed=True),
        "<h2>9. Süreç İş Ürünleri</h2>", core.para("Girdi ve çıktı iş ürünleri, tam doküman adları ve kalite kriterleri LST.008 - İş Ürünleri ve Kalite Kriterleri Listesi (SRÇ.025) dokümanında yönetilir."),
        "<h2>10. Süreç Akışı</h2>", core.image(storage, FLOW_PNG, "SRÇ.025 ölçüm süreç akışı", 900) + mermaid,
        "<h2>11. Süreç Faaliyetleri</h2>", core.table(["Faaliyet ID", "Faaliyet", "Açıklama", "Elde Edilen / Güncellenen İş Ürünü"], activities, fixed=True),
        "<h2>12. Ölçüm ve İzleme</h2>", core.para("SRÇ.025 için yalnız zamanında üretilen ölçüm sonucu oranı ile ölçüm sonuçlarının zamanında ilgili taraflara sunulma oranı izlenir. İlk gerçek dönemde başlangıç değeri oluşturulur; yeterli veri olmadan yapay hedef belirlenmez. Ayrıntılar LST.009'da yönetilir."),
        "<h2>13. Uygulama ve Uyarlama Kuralları</h2>",
        "<h3>13.1. Bilgi İhtiyacına Dayalı Ölçüm</h3>" + core.para("Her ölçüm cevaplayacağı bilgi ihtiyacına ve destekleyeceği karara bağlıdır. Yalnız kolay üretilebildiği için gösterge eklenmez; kullanılmayan ölçüm gözden geçirilip kaldırılabilir."),
        "<h3>13.2. Doğal Kaynak ve Bağlam</h3>" + core.para("Veri merkezi bir tabloya kopyalanmak yerine doğal kaynağında tutulur. Dönem, kapsam, kaynak bağlantısı, hesaplama yöntemi, hazırlayan, analiz tarihi ve varsa veri sınırlaması bilgi ürünüyle ilişkilendirilir."),
        "<h3>13.3. Hedef ve Yorumlama</h3>" + core.para("Geçerli geçmiş veri veya yönetim beklentisi varsa hedef karşılaştırması; yoksa eğilim, başlangıç değeri, gerçekleşti/gerçekleşmedi veya nitel değerlendirme kullanılır. Gerekçesiz eşik üretilmez."),
        "<h3>13.4. Gizlilik ve Erişim</h3>" + core.para("Kişisel veya müşteri verisi mümkün olduğunca toplulaştırılır; ham veriye görev gereği erişilir. Yönetim sunumlarında gerekli ayrıntı seviyesi kullanılır ve rapor için gereksiz veri kopyalanmaz."),
        "<h3>13.5. Ölçüm Gözden Geçirmesi</h3>" + core.para("Ölçümler yılda bir kez SRÇ.023 YGG hazırlığı sırasında; bilgi ihtiyacı, veri güvenilirliği, iş yükü ve kullanılabilirlik açısından değerlendirilir. Kontrollü değişiklik SRÇ.018'e, kapsamlı süreç iyileştirmesi gerektiğinde sonuç SRÇ.006'ya yönlendirilir."),
        "<h2>14. Süreç Etkileşimleri</h2>", core.para("Süreç ve doküman düzeyindeki girdi/çıktı ilişkileri LST.007 - Süreç Etkileşim Matrisi (SRÇ.025) dokümanında gösterilir."),
        "<h2>15. Sürüm Geçmişi</h2>", core.history("Ölçüm Süreci", REVIEWER, APPROVER),
    ])


def lst007_page(storage: bool) -> str:
    mermaid = core.info_macro("Mermaid Kodu", INTERACTION_LINES) if storage else core.info_view("Mermaid Kodu", INTERACTION_LINES)
    rows = [
        ["Girdi", "SRÇ.023 - Organizasyonel Yönetim Süreci / yönetim kararları", SRC025, "Ölçüm bilgi ihtiyacını ve karar kullanımını belirlemek"],
        ["Girdi", "SRÇ.024 - Kalite Yönetimi Süreci / kalite hedefleri", SRC025, "Kalite performansı ölçüm ihtiyaçlarını sağlamak"],
        ["Girdi", "SRÇ.002 - Kalite Güvencesi Süreci ve SRÇ.005 - Süreç Değerlendirme Süreci sonuçları", SRC025, "Güvence ve değerlendirme verilerini analiz etmek"],
        ["Girdi", "SRÇ.007 - Proje Yönetimi Süreci / proje bilgi ihtiyaçları", SRC025, "Proje kararlarını destekleyecek ölçümleri belirlemek"],
        ["Girdi", "Jira, Confluence, Bitbucket, Google Drive ve ilgili doğal kayıtlar", SRC025, "Bağlam bilgili kaynak veriyi sağlamak"],
        ["Çıktı", SRC025, PRS009, "Ölçüm stratejisi, analiz ve kullanım kurallarını uygulamak"],
        ["Çıktı", SRC025, "Süreç özel LST.009 - Süreç Performans Ölçüm Setleri", "Bilgi ihtiyacına dayalı ölçümleri tanımlamak"],
        ["Çıktı", "Analiz edilmiş ölçüm sonucu", "RPR.001 - Süreç Performansları Raporu / RPR.002 - Proje Müşteri Memnuniyeti Değerlendirme Raporu / proje özel bilgi ürünü", "Karar için ölçüm bilgisini sunmak"],
        ["Çıktı", "Ölçüm gözden geçirme sonucu", "SRÇ.018 - Değişiklik Talebi Yönetimi Süreci", "Kontrollü ölçüm değişikliğini yürütmek"],
        ["Çıktı", "Kapsamlı ölçüm iyileştirme ihtiyacı", "SRÇ.006 - Süreç İyileştirme Süreci", "Süreç iyileştirmesini yürütmek"],
    ]
    return "".join([
        "<h2>1. Liste Özeti</h2>", core.table(["Alan", "Değer"], [["İlgili Süreç", SRC025], ["Kullanım Amacı", "SRÇ.025'in süreç, araç ve bilgi ürünü düzeyindeki girdi/çıktı ilişkilerini göstermek"], ["Sorumlu", OWNER], ["Durum", "Aktif"], ["Sürüm", "v1.0"]]),
        "<h2>2. Süreç ve Doküman Etkileşim Matrisi</h2>", core.table(["Yön", "Kaynak", "Hedef", "Etkileşim / Aktarılan Bilgi"], rows, fixed=True),
        "<h2>3. Süreç Etkileşim Diyagramı</h2>", core.image(storage, INTERACTION_PNG, "SRÇ.025 süreç etkileşim diyagramı", 820) + mermaid,
        "<h2>4. Sürüm Geçmişi</h2>", core.history("Süreç Etkileşim Matrisi (SRÇ.025)", REVIEWER, APPROVER),
    ])


def lst008_page() -> str:
    rows = [
        ["Girdi", "LST.006 - Standart Süreç Envanteri", "SRÇ.004 - Süreç Kurulumu Süreci", "Aktif süreç kapsamı, kodu ve sahipliği güncel olmalıdır.", "Ölçüm kapsamını belirlemek"],
        ["Girdi", "Süreç özel LST.009 - Süreç Performans Ölçüm Setleri", "İlgili Süreç Sahibi", "Bilgi ihtiyacı, yöntem, kaynak, sıklık, sorumlu ve kullanım yeri belirli olmalıdır.", "Ölçüm tanımlarını yönetmek"],
        ["Girdi", "Jira, Confluence, Bitbucket, Google Drive ve ilgili doğal kaynak verileri", "İlgili Veri Sahibi", "Dönem, kapsam, kaynak bağlantısı, hesaplama yöntemi, hazırlayan, analiz tarihi ve sınırlamalar izlenebilir olmalıdır.", "Ölçüm verisini sağlamak"],
        ["Girdi", "RPR.001 - Süreç Performansları Raporu, RPR.002 - Proje Müşteri Memnuniyeti Değerlendirme Raporu ve proje özel bilgi ürünleri", "Kalite Danışmanı / Proje Yöneticisi / İlgili Süreç Sahibi", "Kaynak veriyle izlenebilir, güncel ve karar bağlamı açıklanmış olmalıdır.", "Mevcut bilgi ürünlerini değerlendirmek"],
        ["Çıktı", SRC025, "Proje Yöneticisi", "MAN.6.BP1-BP9, onaylı roller, kapsam ve kullanım kuralları izlenebilir olmalıdır.", "Kurumsal ölçüm çerçevesi"],
        ["Çıktı", PRS009, "Proje Yöneticisi", "PRS.XXX.Ş yapısına uygun; strateji, bilgi ihtiyacı, ölçüm tanımı, veri, analiz, paylaşım ve gözden geçirme kurallarını içermelidir.", "Ölçüm ve analiz işleyişi"],
        ["Çıktı", "Güncellenmiş LST.009 - Süreç Performans Ölçüm Seti (İlgili Süreç)", "İlgili Süreç Sahibi", "Az sayıda, düzenli üretilebilir ve karar kullanımına bağlı ölçüm içermelidir.", "Ölçüm devreye alma ve bakım"],
        ["Çıktı", "Bağlam bilgili ölçüm verisi ve analiz sonucu", "İlgili Veri Sahibi / Kalite Danışmanı", "Kaynak, dönem, kapsam, yöntem ve sınırlama doğrulanabilir olmalıdır.", "Bilgi ürünü hazırlamak"],
        ["Çıktı", "Ölçüm bilgi ürünü (RPR.001 / RPR.002 / proje raporu veya göstergesi / yönetim karar girdisi)", "Kalite Danışmanı / Proje Yöneticisi / İlgili Süreç Sahibi", "İlgili kullanıcıya zamanında sunulmuş, anlaşılır ve güncel olmalıdır.", "Kararı desteklemek"],
        ["Çıktı", "Ölçüm değişikliği veya iyileştirme ihtiyacı", "Proje Yöneticisi / İlgili Süreç Sahibi", "Gerekçe, etki ve hedef ölçüm/süreç belirtilmeli; kontrollü değişiklik SRÇ.018'e yönlendirilmelidir.", "Ölçümü sürdürmek veya iyileştirmek"],
        ["Çıktı", "FRM.001 - Süreç Gözden Geçirme Formu (SRÇ.025)", "Kalite Danışmanı", "MAN.6 BP ve PA/GP değerlendirmeleri kanıt, etiket ve tamamlayıcı aksiyonlarla izlenebilir olmalıdır.", "Süreç değerlendirmesi"],
    ]
    return "".join([
        "<h2>1. Liste Özeti</h2>", core.table(["Alan", "Değer"], [["İlgili Süreç", SRC025], ["Kullanım Amacı", "SRÇ.025 girdi ve çıktı iş ürünlerini tam adları ve kalite kriterleriyle yönetmek"], ["Sorumlu", OWNER], ["Durum", "Aktif"], ["Sürüm", "v1.0"]]),
        "<h2>2. İş Ürünleri ve Kalite Kriterleri</h2>", core.table(["Tür", "İş Ürünü / Kayıt", "Sahibi / Kaynağı", "Kalite Kriteri", "Kullanım Amacı"], rows, fixed=True),
        "<h2>3. Kontrol Kuralları</h2>", core.table(["Kural", "Açıklama"], [
            ["Bilgi ihtiyacı", "Her ölçüm cevaplayacağı soruyu ve destekleyeceği kararı gösterir."],
            ["Az sayıda ölçüm", "Düzenli üretilemeyecek veya kullanılmayacak ölçüm eklenmez."],
            ["Doğal kaynak", "Veri gereksiz yere kopyalanmaz; yetkili kaynağa bağlantı kurulur."],
            ["Gerçek kayıt", "Henüz oluşmamış dönem sonucu, sunum veya karar kanıt gibi gösterilmez."],
            ["Tekil bilgi ürünü", "Genel ölçüm raporu oluşturulmaz; sonuç ihtiyaca uygun mevcut rapor veya gösterge içinde tutulur."],
        ]),
        "<h2>4. Sürüm Geçmişi</h2>", core.history("İş Ürünleri ve Kalite Kriterleri Listesi (SRÇ.025)", REVIEWER, APPROVER),
    ])


def lst009_page() -> str:
    rows = [
        ["ÖLÇ-01", "Zamanında üretilen ölçüm sonucu oranı", "Planlanan dönemde verisi toplanıp analiz edilen ölçüm sonucu / dönemde sonucu beklenen ölçüm × 100", "İlk gerçek dönemde başlangıç değeri; sonraki hedef veri oluşunca yönetimce belirlenir", "Her ölçüm döneminde ve yıllık YGG hazırlığında", "İlgili LST.009; kaynak veri; bilgi ürünü", "Kalite Danışmanı / İlgili Veri Sahibi", "Gecikme ve veri üretilebilirliği sorunlarını değerlendirmek"],
        ["ÖLÇ-02", "Ölçüm sonuçlarının zamanında sunulma oranı", "Planlanan tarihte ilgili taraflara sunulan ölçüm sonucu / sunulması gereken ölçüm sonucu × 100", "İlk gerçek dönemde başlangıç değeri; sonraki hedef veri oluşunca yönetimce belirlenir", "Her ölçüm döneminde ve yıllık YGG hazırlığında", "Rapor, gösterge, toplantı veya bağlantılı doğal sunum kaydı", "Proje Yöneticisi / Kalite Danışmanı", "İletişim ve karar kullanımındaki gecikmeleri değerlendirmek"],
    ]
    return "".join([
        "<h2>1. Liste Özeti</h2>", core.table(["Alan", "Değer"], [["İlgili Süreç", SRC025], ["Kullanım Amacı", "Ölçüm Sürecinin sonuç üretme ve sonuçları ilgili taraflara sunma zamanlamasını az sayıda uygulanabilir ölçümle izlemek"], ["Sorumlu", OWNER], ["Durum", "Aktif"], ["Sürüm", "v1.0"]]),
        "<h2>2. Hedef ve İzleme Matrisi</h2>", core.table(["Ölçüm Kodu", "Ölçüm", "Tanım / Hesaplama", "Hedef / Değerlendirme", "Sıklık", "Veri Kaynağı", "Sorumlu", "Sonuç Kullanımı"], rows, fixed=True),
        "<h2>3. Ölçüm Uygulama Kuralları</h2>", core.table(["Kural", "Açıklama"], [
            ["Başlangıç değeri", "Yeterli geçmiş veri veya geçerli yönetim hedefi yoksa ilk gerçek dönem yalnız başlangıç değeri üretir."],
            ["Payda", "Henüz planlanan tarihi gelmeyen veya gerekçeli biçimde iptal edilen ölçüm sonucu paydada gecikmiş olarak sayılmaz."],
            ["Doğal kanıt", "Ayrı ölçüm registerı oluşturulmaz; sonuç ve sunum kanıtı mevcut LST.009, rapor, gösterge veya toplantı kaydından doğrulanır."],
            ["Yorum", "Oran tek başına uygunsuzluk oluşturmaz; veri bağlamı ve ölçümün kullanılabilirliği birlikte değerlendirilir."],
        ]),
        "<h2>4. Sürüm Geçmişi</h2>", core.history("Süreç Performans Ölçüm Seti (SRÇ.025)", REVIEWER, APPROVER),
    ])


def lst010_page() -> str:
    spec = {
        "process": "SRÇ.025", "name": "Ölçüm Süreci", "purpose": "SRÇ.025 rol, yetki, yetkinlik ve RACI yapısını tanımlamak",
        "owner": OWNER, "reviewer": REVIEWER, "approver": APPROVER,
        "raci_roles": ["BİDB Başkanı", "Proje Yöneticisi", "Kalite Danışmanı", "İlgili Süreç Sahibi", "Veri Sahibi", "İdari İşler Şube Müdürü"],
        "roles": [
            ["BİDB Başkanı", "Kurumsal ölçüm öncelik ve kaynak kararlarını vermek", "Önemli kurumsal ölçüm ve kaynak kararlarını onaylamak", "Kurumsal yönetim ve karar yetkisi", "Onaylayan / karar sahibi"],
            ["Proje Yöneticisi", "Ölçüm stratejisini işletmek ve bilgi ürünlerinin kararlarda kullanımını koordine etmek", "Ortak yönteme uygunluğu kontrol etmek ve sonuç sunumunu yönlendirmek", "Proje, süreç, ölçüm ve araç koordinasyonu", "Süreç sahibi / Accountable"],
            ["Kalite Danışmanı", "Ölçüm tanımını hazırlamak; veriyi birleştirmek, analiz etmek ve bilgi ürünü hazırlamak", "Yöntem ve veri kalitesi görüşü vermek", "ISO/IEC 15504-5, ölçüm, analiz ve raporlama", "Hazırlayan / Responsible"],
            ["İlgili Süreç Sahibi", "Kendi sürecinin bilgi ihtiyacını ve ölçümlerini sahiplenmek", "Kendi LST.009 ölçümünü onaylamak ve kullanım kararı vermek", "İlgili süreç ve karar alanı bilgisi", "Ölçüm sahibi / Accountable"],
            ["Veri Sahibi", "Kaynak veriyi doğru, kapsamlı ve zamanında sağlamak", "Kendi kaynağındaki veriyi doğrulamak", "Kaynak sistem, veri tanımı ve erişim bilgisi", "Veri sağlayan / Responsible"],
            ["İdari İşler Şube Müdürü", "Süreç dokümanının yönetimsel uygulanabilirliğini gözden geçirmek", "Doküman gözden geçirme görüşü vermek", "İdari koordinasyon ve kurumsal uygulama", "Gözden geçiren / Consulted"],
        ],
        "activities": [
            ["F1 Ölçüm taahhüdünü oluştur", "A", "R", "C", "C", "I", "C"],
            ["F2 Ölçüm stratejisini geliştir", "I", "A", "R", "C", "C", "C"],
            ["F3 Bilgi ihtiyacını belirle", "I", "A", "R", "R", "C", "I"],
            ["F4 Ölçümü tanımla", "I", "A", "R", "A/R", "C", "I"],
            ["F5 Veriyi topla ve sakla", "I", "A", "C", "C", "R", "I"],
            ["F6 Veriyi analiz et", "I", "A", "R", "C", "C", "I"],
            ["F7 Bilgi ürününü kararda kullan", "C", "A/R", "R", "R/C", "I", "C"],
            ["F8 Sonucu paylaş", "I", "A", "R", "C", "I", "C"],
            ["F9 Ölçümü değerlendir", "I", "A", "R", "R/C", "C", "C"],
        ],
        "products": [
            [PRS009, "A", "A", "R", "C", "I", "C"],
            ["LST.009 - Süreç Performans Ölçüm Seti (İlgili Süreç)", "I", "C", "R", "A", "C", "I"],
            ["Bağlam bilgili ölçüm verisi", "I", "A", "C", "C", "R", "I"],
            ["Ölçüm bilgi ürünü (RPR.001 / RPR.002 / proje raporu veya göstergesi)", "I", "A", "R", "R/C", "C", "I"],
            ["Ölçüm değişikliği / iyileştirme ihtiyacı", "I", "A", "R", "R/C", "C", "I"],
            ["FRM.001 - Süreç Gözden Geçirme Formu (SRÇ.025)", "A", "C", "R", "C", "I", "C"],
        ],
        "authority": [
            ["SRÇ.025 ve PRS.009 yürürlük/onay kararı", "Kalite Danışmanı", "İdari İşler Şube Müdürü", "BİDB Başkanı", "Kontrollü doküman değişikliği SRÇ.018 üzerinden yürütülür."],
            ["Süreç özel ölçümün devreye alınması", "Kalite Danışmanı / Veri Sahibi", "SRÇ.025 Süreç Sahibi", "İlgili Süreç Sahibi", "Bilgi ihtiyacı, veri üretilebilirliği ve kullanım yeri doğrulanır."],
            ["Ortak ölçüm yöntemine uygunluk", "Kalite Danışmanı", "İlgili Süreç / Veri Sahibi", "SRÇ.025 Süreç Sahibi", "PRS.009 ve LST.009 kurallarına göre değerlendirilir."],
            ["Kurumsal öncelik veya ek kaynak kararı", "Proje Yöneticisi / İlgili Süreç Sahibi", "Kalite Danışmanı / İdari İşler Şube Müdürü", "BİDB Başkanı", "Birden fazla süreç/birim, ek kaynak veya üst yönetim etkisinde uygulanır."],
            ["Ölçüm tanımı değişikliği", "Kalite Danışmanı / İlgili Süreç Sahibi", "SRÇ.025 Süreç Sahibi", "İlgili Doküman Onaycısı", "Kontrollü değişiklik SRÇ.018 ve SRÇ.001 kurallarıyla yürütülür."],
        ],
    }
    return raci_body(spec)


def blank_review_page() -> str:
    return "".join([
        "<h2>1. Form Bilgileri</h2>", core.table(["Alan", "Değer"], [["Form Kodu ve Adı", "FRM.001 - Süreç Gözden Geçirme Formu (SRÇ.025)"], ["Süreç", SRC025], ["Değerlendirme Tarihi", "<em>GG-AA-YYYY</em>"], ["Değerlendiren", "<em>Rol / kişi</em>"], ["Durum", "Boş Form"], ["Sürüm", "v1.0"]]),
        "<h2>2. Durum Değerleri</h2>", core.table(["Durum", "Anlamı"], core.LABELS),
        "<h2>3. BP Takip Matrisi</h2>", core.table(["BP", "Standart Beklentisi", "Mevcut Karşılama", "Karşılayan Doküman / Kayıt", "Durum", "Eksik / Tamamlayıcı Aksiyon"], [[bp, expectation, "<em>Değerlendirme açıklaması</em>", "<em>Kanıt bağlantısı</em>", "<em>YOK / ZAYIF / DAĞINIK / VAR / KAPSAM DIŞI</em>", "<em>Aksiyon / gerekçe</em>"] for bp, _, expectation in MAN6_BPS]),
        "<h2>4. PA / GP Takip Matrisi</h2>", core.table(["PA", "GP", "Standart Beklentisi", "Mevcut Karşılama", "Karşılayan Doküman / Kayıt", "Durum", "Eksik / Tamamlayıcı Aksiyon"], [[pa, gp, expectation, "<em>Değerlendirme açıklaması</em>", "<em>Kanıt bağlantısı</em>", "<em>Etiket</em>", "<em>Aksiyon / gerekçe</em>"] for pa, gp, expectation in core.GPS]),
        "<h2>5. Öncelikli Tamamlama Listesi</h2>", core.table(["Öncelik", "Bulgu / Aksiyon", "Bulgu Türü", "İlgili BP / GP", "Hedef Süreç / İzleme Yeri"], [["<em>Yüksek / Orta / Düşük</em>", "<em>Bulgu veya aksiyon</em>", "<em>Uygunsuzluk / İyileştirme Fırsatı / Gözlem / Güçlü Uygulama</em>", "<em>BP / GP</em>", "<em>SRÇ.017 / SRÇ.018 / ilgili kayıt</em>"]]),
    ])


def assessment_page() -> str:
    bp_status = {"MAN.6.BP1":"DAĞINIK", "MAN.6.BP2":"VAR", "MAN.6.BP3":"VAR", "MAN.6.BP4":"VAR", "MAN.6.BP5":"DAĞINIK", "MAN.6.BP6":"DAĞINIK", "MAN.6.BP7":"DAĞINIK", "MAN.6.BP8":"ZAYIF", "MAN.6.BP9":"ZAYIF"}
    evidence = f"{SRC025}; {PRS009}; LST.007-LST.010 (SRÇ.025); mevcut RPR.001 ve süreç özel LST.009 kayıtları"
    bp_rows = []
    for code, _, expectation in MAN6_BPS:
        status = bp_status[code]
        if status == "VAR":
            current, action = "Strateji, bilgi ihtiyacı ve ölçüm tanımlama kuralları süreç paketi ile prosedürde açık ve izlenebilir biçimde tanımlanmıştır.", "Tanımlı yaklaşım yeni ve mevcut LST.009 kayıtlarında korunmalıdır."
        elif status == "DAĞINIK":
            current, action = "Yöntem ve sorumluluk tanımlıdır; mevcut ölçüm ve bilgi ürünleri bulunmakla birlikte ortak yöntemle üretilmiş dönemsel uygulama kanıtı henüz sınırlıdır.", "İlk gerçek ölçüm döneminde bağlam bilgili veri, analiz ve karar bağlantısı doğrulanmalıdır."
        else:
            current, action = "Paylaşım ve yıllık ölçüm gözden geçirmesi tanımlıdır; bu yöntemle gerçekleştirilmiş geri bildirim ve gözden geçirme kaydı henüz bulunmamaktadır.", "İlk YGG hazırlığında doğal iletişim ve gözden geçirme kanıtı oluşturulmalıdır."
        bp_rows.append([code, expectation, current, evidence, status, action])
    gp_status = {
        "GP.2.1.1":"VAR", "GP.2.1.2":"DAĞINIK", "GP.2.1.3":"ZAYIF", "GP.2.1.4":"VAR", "GP.2.1.5":"VAR", "GP.2.1.6":"VAR",
        "GP.2.2.1":"VAR", "GP.2.2.2":"VAR", "GP.2.2.3":"DAĞINIK", "GP.2.2.4":"DAĞINIK",
        "GP.3.1.1":"VAR", "GP.3.1.2":"VAR", "GP.3.1.3":"VAR", "GP.3.1.4":"VAR", "GP.3.1.5":"VAR",
        "GP.3.2.1":"DAĞINIK", "GP.3.2.2":"DAĞINIK", "GP.3.2.3":"DAĞINIK", "GP.3.2.4":"ZAYIF", "GP.3.2.5":"VAR", "GP.3.2.6":"ZAYIF",
    }
    gp_rows = []
    for pa, gp, expectation in core.GPS:
        status = gp_status[gp]
        if status == "VAR":
            current, action = "Süreç paketi; amaç, rol, iş ürünü, etkileşim, altyapı, yöntem ve kontrol kurallarıyla tanımlanmıştır.", "Tanımlı yapı gerçek ölçüm uygulamalarında sürdürülmelidir."
        elif status == "DAĞINIK":
            current, action = "Tanım ve mevcut kaynaklar vardır; ortak yöntemle yürütülen dönemsel ölçüm, kaynak tahsisi veya karar kullanımı henüz sistematik değildir.", "İlk işletim döneminde doğal kayıtlarla doğrulanmalıdır."
        else:
            current, action = "İzleme, geri bildirim ve iyileştirme yöntemi tanımlıdır; gerçekleşen performans ayarlama veya yıllık gözden geçirme kanıtı bulunmamaktadır.", "İlk gerçek ölçüm döngüsünde sonuç üretilmelidir."
        gp_rows.append([pa, gp, expectation, current, evidence, status, action])
    completion = [
        ["Yüksek", "Aktif süreçlerin LST.009 ölçümlerini bilgi ihtiyacı, veri kaynağı ve kullanım yeri açısından ortak yöntemle gözden geçir.", "Gözlem", "MAN.6.BP3-BP4; GP.3.2.1", "Süreç özel LST.009 kayıtları"],
        ["Yüksek", "İlk gerçek ölçüm döneminde sonuçları bağlam bilgileriyle üret ve zamanında sunum kanıtını doğal kaynakta doğrula.", "Gözlem", "MAN.6.BP5-BP8; GP.2.1.2-GP.2.1.3", "İlgili bilgi ürünü / LST.009"],
        ["Orta", "İlk yıllık YGG hazırlığında ölçümlerin bilgi ihtiyacını, veri güvenilirliğini, iş yükünü ve kullanılabilirliğini değerlendir.", "Gözlem", "MAN.6.BP9; GP.3.2.4-GP.3.2.6", "SRÇ.023 YGG hazırlığı / SRÇ.018"],
        ["Orta", "Ölçüm bilgi ürünlerinin kişisel ve müşteri verisini gereksiz ayrıntı olmadan sunduğunu doğrula.", "Gözlem", "MAN.6.BP5-BP8; GP.2.2.3-GP.2.2.4", "Kaynak sistem yetkileri / ilgili bilgi ürünü"],
    ]
    return "".join([
        "<h2>1. Değerlendirme Özeti</h2>", core.table(["Alan", "Değer"], [["Süreç", SRC025], ["Değerlendirme Kaydı", "Değerlendirme #1"], ["Değerlendirme Tarihi", "15-07-2026"], ["Değerlendiren", core.PREPARED_BY], ["Yaklaşım", "Sayısal puan ve tek toplam süreç etiketi kullanılmadan gerekçeli BP ve PA/GP etiketleri"], ["BP Dağılımı", "3 VAR, 4 DAĞINIK ve 2 ZAYIF"], ["PA/GP Dağılımı", "12 VAR, 6 DAĞINIK ve 3 ZAYIF"]]),
        "<h2>2. Durum Değerleri</h2>", core.table(["Durum", "Anlamı"], core.LABELS),
        "<h2>3. BP Takip Matrisi</h2>", core.table(["BP", "Standart Beklentisi", "Mevcut Karşılama", "Karşılayan Doküman / Kayıt", "Durum", "Eksik / Tamamlayıcı Aksiyon"], bp_rows, fixed=True),
        "<h2>4. PA / GP Takip Matrisi</h2>", core.table(["PA", "GP", "Standart Beklentisi", "Mevcut Karşılama", "Karşılayan Doküman / Kayıt", "Durum", "Eksik / Tamamlayıcı Aksiyon"], gp_rows, fixed=True),
        "<h2>5. Öncelikli Tamamlama Listesi</h2>", core.table(["Öncelik", "Bulgu / Aksiyon", "Bulgu Türü", "İlgili BP / GP", "Hedef Süreç / İzleme Yeri"], completion, fixed=True),
        "<h2>6. Sonuç</h2>", core.para("Ölçüm stratejisi, bilgi ihtiyacı, az sayıda ölçüm, doğal kaynak, bağlam bilgisi, analiz, mevcut bilgi ürünleri, karar kullanımı ve yıllık gözden geçirme kuralları tanımlanmıştır. Ortak yöntemle üretilmiş gerçek dönem ölçüm sonuçları, zamanında sunum ve yıllık değerlendirme kanıtları henüz oluşmadığından uygulama alanları ihtiyatlı etiketlenmiştir; aynı Değerlendirme #1 kaydı doğal kanıtlar oluştukça güncellenecektir."),
    ])


def procedure_page() -> str:
    return "".join([
        "<h2>1. Prosedür Bilgileri</h2>", core.table(["Alan", "Değer"], [["Kurum", "İstanbul Üniversitesi - Cerrahpaşa Bilgi İşlem Daire Başkanlığı"], ["Prosedür Kodu ve Adı", PRS009], ["Prosedür Referansı", SRC025], ["Prosedür Sahibi", OWNER], ["Durum", "Aktif"], ["Sürüm", "v1.0"], ["Yürürlük Tarihi", "15-02-2025"], ["Son Gözden Geçirme Tarihi", "15-07-2026"]]),
        "<h2>2. Amaç</h2>", core.para("BİDB süreç ve projelerinde ölçüm bilgi ihtiyaçlarının belirlenmesi, uygulanabilir ölçümlerin tanımlanması, verilerin bağlamıyla toplanıp analiz edilmesi ve sonuçların mevcut bilgi ürünleri üzerinden kararlarda kullanılması için ortak yöntemi tanımlamak."),
        "<h2>3. Kapsam</h2>", core.para("LST.006 standart süreç envanterindeki süreçler, bunların uygulandığı yazılım projeleri, süreç özel LST.009 ölçümleri, doğal kaynak verileri, analizler, mevcut rapor ve göstergeler ile ölçüm gözden geçirmeleri."),
        "<h2>4. Kapsam Dışı</h2>", core.para("Merkezi ölçüm veri tabanı veya genel ölçüm raporu kurulması; bilgi ihtiyacına dayanmayan göstergeler; süreç ve proje sahiplerinin faaliyetlerinin bu prosedürde yeniden işletilmesi."),
        "<h2>5. Referanslar</h2>", core.table(["Referans", "Açıklama"], [[SRC025, "MAN.6 ölçüm süreci kapsam ve faaliyetleri"], ["LST.009.Ş - Süreç Performans Ölçüm Seti Şablonu", "Süreç özel ölçüm tanımı yapısı"], ["RPR.001 - Süreç Performansları Raporu", "Süreç değerlendirme ve etiket eğilimleri bilgi ürünü"], ["RPR.002.Ş - Proje Müşteri Memnuniyeti Değerlendirme Raporu Şablonu", "Proje müşteri memnuniyeti bilgi ürünü"], ["SRÇ.018 - Değişiklik Talebi Yönetimi Süreci", "Kontrollü ölçüm ve doküman değişikliği"], ["SRÇ.006 - Süreç İyileştirme Süreci", "Kapsamlı ölçüm süreci iyileştirmesi"], ["PRS.XXX.Ş - Prosedür Tanımı Şablonu", "Doküman yapısı"]]),
        "<h2>6. Terimler ve Kısaltmalar</h2>", core.table(["Terim / Kısaltma", "Açıklama"], [["Bilgi İhtiyacı", "Bir karar için cevaplanması gereken soru"], ["Ölçüm Bilgi Ürünü", "Analiz ve yorum içeren rapor, gösterge, tablo, sunum veya karar girdisi"], ["Başlangıç Değeri", "İlk gerçek dönemde oluşturulan karşılaştırma değeri"], ["Doğal Kaynak", "Verinin işin yürütülmesi sırasında oluştuğu yetkili sistem veya kayıt"]]),
        "<h2>7. Roller ve Sorumluluklar</h2>", core.table(["Rol", "Sorumluluk", "Yetki"], [["BİDB Başkanı", "Kurumsal öncelik ve kaynak kararlarını vermek", "Önemli kurumsal ölçüm kararlarını onaylamak"], ["Proje Yöneticisi", "Ölçüm stratejisini işletmek ve sonuçların karar kullanımını koordine etmek", "Ortak yönteme uygunluğu kontrol etmek"], ["Kalite Danışmanı", "Ölçüm tanımını hazırlamak, veriyi birleştirmek, analiz etmek ve bilgi ürünü hazırlamak", "Yöntem ve veri kalitesi görüşü vermek"], ["İlgili Süreç Sahibi", "Bilgi ihtiyacını, ölçümü ve kullanım kararını sahiplenmek", "Kendi LST.009 ölçümünü onaylamak"], ["Veri Sahibi", "Kaynak veriyi doğru ve zamanında sağlamak", "Kendi kaynağındaki veriyi doğrulamak"]]),
        "<h2>8. Genel İlkeler</h2>", core.table(["İlke", "Açıklama"], [["Karar odaklılık", "Her ölçüm bir bilgi ihtiyacına ve karar kullanımına bağlıdır."], ["Az sayıda ölçüm", "Düzenli üretilebilen ve kullanılan sınırlı sayıda gösterge tutulur."], ["Doğal kaynak", "Veri gereksiz yere kopyalanmaz; yetkili kaynağına bağlantı kurulur."], ["Gerekçeli hedef", "Geçerli veri yoksa yapay eşik yerine başlangıç değeri veya nitel yöntem kullanılır."], ["Mevcut bilgi ürünü", "Yeni genel ölçüm raporu üretilmez; sonuç ihtiyaca uygun mevcut rapor veya göstergede sunulur."], ["Gizlilik", "Kişisel ve müşteri verisi toplulaştırılır; ham veriye görev gereği erişilir."]]),
        "<h2>9. Prosedür Esasları</h2>", core.table(["Esas / Kural", "Açıklama", "Zorunluluk", "Not"], [["Bilgi ihtiyacı", "Ölçüm, cevaplayacağı soru ve destekleyeceği karar olmadan devreye alınmaz.", "Zorunlu", "MAN.6.BP3"], ["Ölçüm tanımı", "Tanım, hesaplama, kaynak, sıklık, sorumlu, değerlendirme ve kullanım yeri ilgili LST.009'da bulunur.", "Zorunlu", "MAN.6.BP4"], ["Bağlam bilgisi", "Dönem, kapsam, kaynak bağlantısı, yöntem, hazırlayan, analiz tarihi ve sınırlama izlenir.", "Zorunlu", "MAN.6.BP5-BP6"], ["Sunum ve geri bildirim", "Bilgi ürünü planlanan tarihte ilgili kullanıcıya sunulur ve kullanım uygunluğu değerlendirilir.", "Zorunlu", "MAN.6.BP7-BP9"], ["Kontrollü değişiklik", "Ölçüm veya doküman değişikliği SRÇ.018 üzerinden yürütülür.", "Koşullu", "Kapsamlı iyileştirme SRÇ.006'ya yönlendirilir."]]),
        "<h2>10. Ölçüm ve Analiz Uygulama Matrisi</h2>", core.table(["Aşama", "Uygulama Kuralı", "Sorumlu", "Kayıt / Kanıt", "Kontrol"], [["1. İhtiyacı öner", "BİDB Başkanı, Proje Yöneticisi, süreç sahibi veya Kalite Danışmanı bilgi ihtiyacını önerebilir.", "Öneren Rol", "Karar / ihtiyaç kaydı", "Hedef karar belirtilir"], ["2. Üretilebilirliği değerlendir", "Kalite Danışmanı veri sahibiyle kaynak, bağlam, yöntem ve iş yükünü doğrular.", "Kalite Danışmanı / Veri Sahibi", "Kaynak bağlantısı / yöntem notu", "Gereksiz ölçüm elenir"], ["3. Ölçümü tanımla", "Ölçüm ilgili LST.009'a eklenir ve ilgili süreç sahibi kullanım kararını verir.", "Kalite Danışmanı / İlgili Süreç Sahibi", "LST.009", "SRÇ.025 yöntem uygunluğu"], ["4. Veriyi topla", "Veri doğal kaynaktan dönem ve kapsam bilgisiyle alınır.", "Veri Sahibi", "Kaynak kayıt / bağlantı", "Doğruluk ve erişim"], ["5. Analiz et", "Uygun hedef, eğilim, başlangıç değeri, gerçekleşme veya nitel yöntemle yorumlanır.", "Kalite Danışmanı / İlgili Süreç Sahibi", "Analiz sonucu", "Sınırlamalar belirtilir"], ["6. Bilgi ürünü oluştur", "Sonuç RPR.001, RPR.002, proje raporu/göstergesi veya karar girdisinde sunulur.", "Kalite Danışmanı / Proje Yöneticisi", "Bilgi ürünü", "Yeni genel rapor yok"], ["7. Sonucu paylaş", "İlgili karar sahiplerine planlanan tarihte erişim sağlanır.", "Proje Yöneticisi / Kalite Danışmanı", "Toplantı, rapor veya bağlantı", "Yetki ve gizlilik"], ["8. Ölçümü değerlendir", "Yıllık YGG hazırlığında ihtiyaç, veri güvenilirliği, iş yükü ve kullanılabilirlik gözden geçirilir.", "Proje Yöneticisi / Süreç Sahibi / Kalite Danışmanı", "Gözden geçirme sonucu", "Gerekirse SRÇ.018 / SRÇ.006"]], fixed=True),
        "<h2>11. Yayın, Erişim ve Bakım Kuralları</h2>", core.table(["Kural Alanı", "Kural", "Sorumlu", "Kayıt / Kanıt"], [["Yayın", "Onaylı prosedür, LST.009 ve ilgili bilgi ürünleri Confluence veya yetkili doğal sistemde erişilebilir tutulur.", "Proje Yöneticisi / Belge Sahibi", "Confluence / kaynak sistem sürümü"], ["Erişim", "Ham veri ve kişisel/müşteri bilgisine görev gereği erişim verilir.", "Veri Sahibi / Sistem Yöneticisi", "Kaynak sistem yetkisi"], ["Bakım", "Ölçümler yılda bir ve bilgi ihtiyacı/veri kaynağı değiştiğinde gözden geçirilir.", "Proje Yöneticisi / İlgili Süreç Sahibi", "YGG hazırlığı / LST.009"], ["Değişiklik", "Kontrollü değişiklik SRÇ.018 ve SRÇ.001 kurallarıyla yürütülür.", "İlgili Süreç Sahibi / Kalite Danışmanı", "SRÇ.018 / LST.002"]]),
        "<h2>12. Kayıtlar ve Kanıtlar</h2>", core.table(["Kayıt / Kanıt", "Kullanım Amacı", "Saklama Yeri", "Sorumlu", "Not"], [["LST.009 - Süreç Performans Ölçüm Seti (İlgili Süreç)", "Ölçüm tanımı", "İlgili SRÇ sayfası altı", "İlgili Süreç Sahibi", "Az sayıda ölçüm"], ["Kaynak veri ve bağlam bilgileri", "Hesaplama ve doğrulama", "Jira / Confluence / Bitbucket / Google Drive / ilgili doğal sistem", "Veri Sahibi", "Gereksiz kopya yok"], ["RPR.001 - Süreç Performansları Raporu", "Süreç değerlendirme ve etiket eğilimleri", "09 - Raporlar", "Kalite Danışmanı", "Kümülatif bilgi ürünü"], ["RPR.002 - Proje Müşteri Memnuniyeti Değerlendirme Raporu ([Proje Adı])", "Proje müşteri memnuniyeti sonucu", "09 - Raporlar", "Kalite Danışmanı", "Yalnız gerçek uygulamada"], ["Proje raporu, gösterge veya karar girdisi", "Proje özel ölçüm bilgisi", "İlgili proje alanı", "Proje Yöneticisi / İlgili Süreç Sahibi", "Doğal bilgi ürünü"], ["Ölçüm gözden geçirme ve değişiklik kaydı", "Ölçümü sürdürme/değiştirme kararı", "YGG hazırlığı / SRÇ.018", "Proje Yöneticisi / İlgili Süreç Sahibi", "Koşullu"]], fixed=True),
        "<h2>13. Sürüm Geçmişi</h2>", core.history("Ölçüm ve Analiz Prosedürü", REVIEWER, APPROVER),
    ])


def update_lst001() -> Path:
    page = CONFLUENCE / LST001_REL
    storage = html.unescape((page / "body.storage.xhtml").read_text(encoding="utf-8"))
    storage = core.upsert_section_row(storage, "3. Süreç Dokümanları", "SRÇ.025", ["SRÇ.025", "Ölçüm Süreci", "MAN.6", OWNER, "Aktif", "v1.0", "15-02-2025", "01 - Süreç Dokümanları"])
    storage = core.upsert_section_row(storage, "4. Prosedürler", "PRS.009", ["PRS.009", "Ölçüm ve Analiz Prosedürü", "SRÇ.025", OWNER, "Aktif", "v1.0", "15-02-2025", "07 - Prosedürler"])
    (page / "body.storage.xhtml").write_text(storage, encoding="utf-8")
    (page / "body.view.html").write_text(core.build_view("LST.001 - Aktif Dokümanlar Listesi", storage), encoding="utf-8")
    return page


def update_lst006() -> Path:
    page = CONFLUENCE / LST006_REL
    storage = html.unescape((page / "body.storage.xhtml").read_text(encoding="utf-8"))
    heads = list(re.finditer(r"<h2[^>]*>(.*?)</h2>", storage, flags=re.I | re.S))
    for index, heading in enumerate(heads):
        if "3. Standart Süreç Envanteri" not in html.unescape(re.sub(r"<[^>]+>", "", heading.group(1))):
            continue
        end = heads[index + 1].start() if index + 1 < len(heads) else len(storage)
        section = storage[heading.end():end]
        rows = re.findall(r"<tr[^>]*>.*?</tr>", section, flags=re.I | re.S)
        target = next((row for row in rows if "SRÇ.025" in html.unescape(re.sub(r"<[^>]+>", "", row))), None)
        if not target:
            raise RuntimeError("SRÇ.025 row missing in LST.006")
        cells = ["MAN.6", "Measurement", "SRÇ.025", "Ölçüm Süreci", OWNER, "Aktif", "Süreç paketi yerelde oluşturulmuş; kullanıcı incelemesi ve kontrollü Confluence yayını beklenmektedir."]
        replacement = "<tr>" + "".join(f"<td>{html.escape(value)}</td>" for value in cells) + "</tr>"
        storage = storage[:heading.end()] + section.replace(target, replacement) + storage[end:]
        break
    (page / "body.storage.xhtml").write_text(storage, encoding="utf-8")
    (page / "body.view.html").write_text(core.build_view("LST.006 - Standart Süreç Envanteri", storage), encoding="utf-8")
    return page


def update_rpr001() -> Path:
    page = CONFLUENCE / RPR001_REL
    storage = html.unescape((page / "body.storage.xhtml").read_text(encoding="utf-8"))
    storage = storage.replace(
        "Şu aşamada SRÇ.001, SRÇ.004, SRÇ.005, SRÇ.006, SRÇ.021, SRÇ.023 ve SRÇ.024 değerlendirmeleri rapora alınmıştır.",
        "Şu aşamada SRÇ.001, SRÇ.004, SRÇ.005, SRÇ.006, SRÇ.021, SRÇ.023, SRÇ.024 ve SRÇ.025 değerlendirmeleri rapora alınmıştır.",
    )
    storage = core.append_section_row(storage, "4. Süreç Sonuç Özeti", "SRÇ.025", [SRC025, "MAN.6 BP1-BP9; PA 2.1-PA 3.2", "3 VAR; 4 DAĞINIK; 2 ZAYIF", "12 VAR; 6 DAĞINIK; 3 ZAYIF", "", "FRM.001 - Süreç Gözden Geçirme Formu (SRÇ.025) - Değerlendirme #1", "Ölçüm stratejisi, bilgi ihtiyacı, doğal kaynak, bağlam bilgisi, analiz ve mevcut bilgi ürünü yapısı tanımlı; ortak yöntemle gerçek dönem ölçümü, zamanında sunum ve yıllık gözden geçirme kanıtları henüz oluşmamıştır."])
    storage = core.append_section_row(storage, "5. Etiket Dağılımları ve Eğilimler", "SRÇ.025", ["SRÇ.025", "3", "4", "2", "0", "12", "6", "3", "0"], before_key="Eğilim Yorumu")
    (page / "body.storage.xhtml").write_text(storage, encoding="utf-8")
    (page / "body.view.html").write_text(core.build_view("RPR.001 - Süreç Performansları Raporu", storage), encoding="utf-8")
    return page


def upsert_index(page_dirs: list[Path]) -> None:
    index = yaml.safe_load(INDEX_PATH.read_text(encoding="utf-8")) or {}
    pages = index.setdefault("pages", [])
    rels = {str(directory.relative_to(CONFLUENCE)).replace("\\", "/") for directory in page_dirs if (directory / "page.yaml").exists()}
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
    for directory in [PAGE_ROOT / "07-prosedurler", PAGE_ROOT / "91-ic-denetimler/surec-gozden-gecirmeleri", CONFLUENCE / SRC025_REL]:
        meta_path = directory / "page.yaml"
        if not meta_path.exists():
            continue
        meta = yaml.safe_load(meta_path.read_text(encoding="utf-8")) or {}
        stable = str(meta.get("page_id") or f"local:{meta.get('relative_path')}")
        meta["children_count"] = sum(1 for item in pages if str(item.get("parent_id") or "") == stable)
        meta_path.write_text(yaml.safe_dump(meta, allow_unicode=True, sort_keys=False), encoding="utf-8")


def update_project_records() -> None:
    status = ROOT / "docs/CURRENT_STATUS.md"
    text = status.read_text(encoding="utf-8")
    addition = "- SRÇ.025 Ölçüm paketi; süreç tanımı, PRS.009, süreç özel LST.007-LST.010, boş FRM.001 ve Değerlendirme #1 ile yerelde oluşturulmuş; değerlendirme sonuçları RPR.001'e eklenmiştir. Gerçek dönem ölçüm sonucu veya sunum kaydı üretilmemiş ve Confluence yayını kullanıcı incelemesine bırakılmıştır.\n"
    if addition not in text:
        text += ("\n" if not text.endswith("\n") else "") + addition
        status.write_text(text, encoding="utf-8")
    decisions = ROOT / "docs/DECISIONS.md"
    text = decisions.read_text(encoding="utf-8")
    if "## SRÇ.025 ölçüm yaklaşımı" not in text:
        text += """

## SRÇ.025 ölçüm yaklaşımı

- Süreç sahibi Levent BAYEZİT - Proje Yöneticisi, gözden geçiren Seçil NEBİLER - İdari İşler Şube Müdürü, onaylayan Mustafa Nusret SARISAKAL - Bilgi İşlem Daire Başkanıdır.
- SRÇ.025 merkezi ölçüm deposu veya yeni genel ölçüm raporu oluşturmaz. Ölçüm stratejisi ve ortak yöntem PRS.009 - Ölçüm ve Analiz Prosedüründe; süreç ölçümleri süreç özel LST.009 kayıtlarında; sonuçlar RPR.001, RPR.002 veya ilgili proje rapor/göstergelerinde yönetilir.
- Her ölçüm açık bir bilgi ihtiyacına ve destekleyeceği karara bağlıdır. Düzenli üretilemeyen veya karar süreçlerinde kullanılmayan ölçüm eklenmez; mevcut LST.009 yapısında az sayıda ölçüm yaklaşımı korunur.
- Ölçüm verisi Jira, Confluence, Bitbucket, Google Drive veya diğer doğal kaynaklarda tutulur. Bilgi ürününde dönem, kapsam, kaynak bağlantısı, hesaplama yöntemi, hazırlayan, analiz tarihi ve varsa veri sınırlaması izlenir; gereksiz veri kopyalanmaz.
- Geçerli geçmiş veri veya yönetim beklentisi yoksa ilk dönemde başlangıç değeri oluşturulur. Hedef karşılaştırması, eğilim, gerçekleşti/gerçekleşmedi veya nitel değerlendirme ihtiyaca göre kullanılır; gerekçesiz eşik üretilmez.
- Proje Yöneticisi stratejinin işletilmesini ve sonuçların karar kullanımını; Kalite Danışmanı ölçüm tanımı, veri birleştirme, analiz ve bilgi ürünü hazırlığını; ilgili süreç/veri sahibi kaynak verinin doğruluğu ile kendi ölçümünü; BİDB Başkanı kurumsal öncelik ve kaynak kararlarını yürütür.
- Yeni ölçüm BİDB Başkanı, Proje Yöneticisi, süreç sahibi veya Kalite Danışmanı tarafından önerilebilir. Kalite Danışmanı veri sahibiyle üretilebilirliği doğrular; ilgili süreç sahibi LST.009 ölçümünü devreye alır; SRÇ.025 süreç sahibi yöntem uygunluğunu kontrol eder. Kontrollü değişiklik SRÇ.018 üzerinden yürütülür.
- SRÇ.025 LST.009 içinde yalnız zamanında üretilen ölçüm sonucu oranı ile ölçüm sonuçlarının zamanında ilgili taraflara sunulma oranı izlenir. İlk gerçek dönemde başlangıç değeri oluşturulur.
- Ölçümler yılda bir kez SRÇ.023 YGG hazırlığında bilgi ihtiyacı, veri güvenilirliği, iş yükü ve kullanılabilirlik açısından değerlendirilir. Değişiklik SRÇ.018'e, kapsamlı süreç iyileştirmesi gerektiğinde sonuç SRÇ.006'ya yönlendirilir.
- Kişisel ve müşteri verileri mümkün olduğunca toplulaştırılır; ham veriye yalnız yetkili roller erişir ve yönetim bilgi ürünlerinde yalnız gerekli ayrıntı kullanılır.
"""
        decisions.write_text(text, encoding="utf-8")
    report = ROOT / "reports/src025_measurement_package_report.md"
    report.write_text("""# SRÇ.025 Ölçüm Paketi Yerel Raporu

Tarih: 15-07-2026

## Oluşturulan Yapı

- SRÇ.025 süreç tanımı MAN.6 BP1-BP9 izlenebilirliğiyle oluşturuldu.
- PRS.009 Ölçüm ve Analiz Prosedürü hazırlandı.
- Süreç özel LST.007-LST.010, boş FRM.001 ve Değerlendirme #1 hazırlandı.
- LST.001 ve LST.006 güncellendi. LST.012 gerçek Confluence yayını gerçekleşmeden değiştirilmedi.
- RPR.001'e SRÇ.025 Değerlendirme #1 sonuç özeti ve etiket dağılımları eklendi.
- Ayrı ölçüm planı, merkezi ölçüm registerı veya yeni genel ölçüm raporu oluşturulmadı.

## Değerlendirme Özeti

- BP: 3 VAR, 4 DAĞINIK, 2 ZAYIF.
- PA/GP: 12 VAR, 6 DAĞINIK, 3 ZAYIF.
- Ortak yöntemle gerçek dönem verisi, zamanında sunum ve yıllık ölçüm gözden geçirme kanıtları henüz bulunmadığından uygulama alanları ihtiyatlı etiketlendi.

## Yayın Durumu

- Çalışma yalnız yerel repository ve viewer için hazırlanmıştır.
- Confluence'a yazma yapılmamıştır; kullanıcı incelemesi ve onayı beklenmektedir.
""", encoding="utf-8")


def validate(page_dirs: list[Path]) -> None:
    process = (CONFLUENCE / SRC025_REL / "body.storage.xhtml").read_text(encoding="utf-8")
    headings = [html.unescape(re.sub(r"<[^>]+>", "", value)) for value in re.findall(r"<h2[^>]*>(.*?)</h2>", process, flags=re.S)]
    expected = ["1. Süreç Bilgileri", "2. Amaç", "3. Kapsam", "4. Referanslar", "5. Terimler ve Kısaltmalar", "6. Süreç Aktivitesi", "7. Roller ve Sorumluluklar", "8. Araçlar ve Altyapı", "9. Süreç İş Ürünleri", "10. Süreç Akışı", "11. Süreç Faaliyetleri", "12. Ölçüm ve İzleme", "13. Uygulama ve Uyarlama Kuralları", "14. Süreç Etkileşimleri", "15. Sürüm Geçmişi"]
    if headings != expected:
        raise RuntimeError(f"SRÇ.025 heading mismatch: {headings}")
    for bp, _, _ in MAN6_BPS:
        if bp not in process:
            raise RuntimeError(f"Missing BP trace: {bp}")
    if "26 süreç" in html.unescape(re.sub(r"<[^>]+>", "", process)):
        raise RuntimeError("Forbidden fixed process count found")
    for directory in page_dirs:
        for filename in ["page.yaml", "body.storage.xhtml", "body.view.html"]:
            if not (directory / filename).exists():
                raise RuntimeError(f"Missing artifact: {directory / filename}")
    assessment = (CONFLUENCE / core.REVIEWS_REL / "frm-001-surec-gozden-gecirme-formu-src-025-degerlendirme-1/body.storage.xhtml").read_text(encoding="utf-8")
    if "3 VAR, 4 DAĞINIK ve 2 ZAYIF" not in assessment or "12 VAR, 6 DAĞINIK ve 3 ZAYIF" not in assessment:
        raise RuntimeError("Assessment distribution mismatch")
    rpr = (CONFLUENCE / RPR001_REL / "body.storage.xhtml").read_text(encoding="utf-8")
    if rpr.count("SRÇ.025 - Ölçüm Süreci") != 1 or "3 VAR; 4 DAĞINIK; 2 ZAYIF" not in rpr:
        raise RuntimeError("RPR.001 SRÇ.025 summary mismatch")
    lst009 = (CONFLUENCE / SRC025_REL / "lst-009-surec-performans-olcum-seti-src-025/body.storage.xhtml").read_text(encoding="utf-8")
    if lst009.count("ÖLÇ-01") != 1 or lst009.count("ÖLÇ-02") != 1 or "ÖLÇ-03" in lst009:
        raise RuntimeError("LST.009 limited measurement set mismatch")


def main() -> None:
    src = CONFLUENCE / SRC025_REL
    attachments = src / "attachments"
    attachments.mkdir(parents=True, exist_ok=True)
    (attachments / FLOW_MMD).write_text("\n".join(FLOW_LINES) + "\n", encoding="utf-8")
    core.write_page(src, SRC025, "137265784", "01 - Süreç Dokümanları", 2, process_page(True), process_page(False))
    pages: list[Path] = [src]
    children = [
        ("lst-007-surec-etkilesim-matrisi-src-025", "LST.007 - Süreç Etkileşim Matrisi (SRÇ.025)", lst007_page(True), lst007_page(False)),
        ("lst-008-is-urunleri-ve-kalite-kriterleri-listesi-src-025", "LST.008 - İş Ürünleri ve Kalite Kriterleri Listesi (SRÇ.025)", lst008_page(), None),
        ("lst-009-surec-performans-olcum-seti-src-025", "LST.009 - Süreç Performans Ölçüm Seti (SRÇ.025)", lst009_page(), None),
        ("lst-010-surec-rol-yetki-ve-raci-matrisi-src-025", "LST.010 - Süreç Rol Yetki ve RACI Matrisi (SRÇ.025)", lst010_page(), None),
    ]
    for slug, title, storage, view in children:
        directory = src / slug
        core.write_page(directory, title, SRC025_ID, SRC025, 3, storage, view)
        pages.append(directory)
        if slug.startswith("lst-007"):
            target = directory / "attachments"
            target.mkdir(exist_ok=True)
            (target / INTERACTION_MMD).write_text("\n".join(INTERACTION_LINES) + "\n", encoding="utf-8")
    blank = src / "frm-001-surec-gozden-gecirme-formu-src-025"
    core.write_page(blank, "FRM.001 - Süreç Gözden Geçirme Formu (SRÇ.025)", SRC025_ID, SRC025, 3, blank_review_page())
    pages.append(blank)
    assessment = CONFLUENCE / core.REVIEWS_REL / "frm-001-surec-gozden-gecirme-formu-src-025-degerlendirme-1"
    core.write_page(assessment, "FRM.001 - Süreç Gözden Geçirme Formu (SRÇ.025) - Değerlendirme #1", core.REVIEWS_ID, "Süreç Gözden Geçirmeleri", 3, assessment_page())
    pages.append(assessment)
    procedure = CONFLUENCE / core.PROCEDURES_REL / "prs-009-olcum-ve-analiz-proseduru"
    core.write_page(procedure, PRS009, core.PROCEDURES_ID, "07 - Prosedürler", 2, procedure_page())
    pages.append(procedure)
    pages.extend([update_lst001(), update_lst006(), update_rpr001()])
    pages.append(core.rebuild_parent_register(PAGE_ROOT / "07-prosedurler", r"^(PRS\.\d{3})\s+-\s+(.+)$", "Prosedür Kodu", "Prosedür Adı"))
    unique = list(dict.fromkeys(pages))
    upsert_index(unique)
    update_project_records()
    validate([directory for directory in unique if (directory / "page.yaml").exists()])
    print(f"[DONE] SRÇ.025 package materialized: {len(unique)} page directories")


if __name__ == "__main__":
    main()
