#!/usr/bin/env python3
"""Create the local SRÇ.006 process-improvement package.

This script is local-only. It does not call Confluence APIs. Existing page ids are
preserved; new pages receive empty ids for a later reviewed publish.
"""
from __future__ import annotations

import html
import re
from pathlib import Path
from urllib.parse import quote

import yaml

from create_src005_process_assessment_package import (
    APPROVED_BY,
    CONFLUENCE,
    GPS,
    INDEX_PATH,
    LABELS,
    PAGE_ROOT,
    PAGE_ROOT_REL,
    PLN002_TEMPLATE_CODE,
    PLN002_TEMPLATE_TITLE,
    PREPARED_BY,
    PROCESS_OWNER,
    REPORTS_REL,
    REVIEWED_BY,
    REVIEWS_ID,
    REVIEWS_REL,
    RPR001,
    TEMPLATES_ID,
    TEMPLATES_REL,
    build_view,
    history,
    info_macro,
    info_view,
    p,
    report_body,
    table,
    template_register_body,
    update_lst001,
    upsert_index,
    write_page,
)


SRC006_ID = "137265864"
SRC006 = "İÜC.BİDB.SRÇ.006 - Süreç İyileştirme Süreci"
SRC018 = "İÜC.BİDB.SRÇ.018 - Değişiklik Talebi Yönetimi Süreci"
PRS004 = "İÜC.BİDB.PRS.004 - Süreç İyileştirme ve Değişiklik Yönetimi Prosedürü"
PLN002 = "İÜC.BİDB.PLN.002 - Süreç İyileştirme Planı"
LST012 = "İÜC.BİDB.LST.012 - Süreç Yaygınlaştırma ve Bilgilendirme Kaydı"
SRC006_REL = f"{PAGE_ROOT_REL}/01-surec-dokumanlari/iuc-bidb-src-006-surec-iyilestirme-sureci"
LST006_REL = f"{PAGE_ROOT_REL}/03-kayitlar-ve-listeler/iuc-bidb-lst-006-standart-surec-envanteri"

FLOW_PNG = "İÜC.BİDB.SRÇ.006 - Flowchart.png"
FLOW_MMD = "src006-surec-akisi.mmd"
INTERACTION_PNG = "src006-surec-etkilesim.png"
INTERACTION_MMD = "src006-surec-etkilesim.mmd"
PLN002_TEMPLATE_SLUG = "iuc-bidb-pln-002-s-surec-iyilestirme-plani-sablonu"

PIM3_BPS = [
    ("PIM.3.BP1", "Kaynak taahhüdünü oluştur", "İyileştirme faaliyetlerini sürdürecek yönetim, kaynak ve onay taahhüdünü sağlamak."),
    ("PIM.3.BP2", "İyileştirme fırsatlarını belirle", "İç ve dış çevreden doğan konuları gerekçeli iyileştirme fırsatları olarak belirlemek."),
    ("PIM.3.BP3", "Süreç iyileştirme hedeflerini oluştur", "Mevcut durumu ve süreç kaynaklı riskleri analiz ederek ölçülebilir iyileştirme hedeflerini belirlemek."),
    ("PIM.3.BP4", "İyileştirmeleri önceliklendir", "İyileştirme hedeflerinin uygulama önceliğini belirlemek."),
    ("PIM.3.BP5", "Süreç değişikliklerini planla", "Hedeflere ulaşmak için gerekli süreç değişikliklerini tanımlamak ve planlamak."),
    ("PIM.3.BP6", "Süreç değişikliklerini uygula", "Onaylanan iyileştirme değişikliklerini kontrollü biçimde uygulamak."),
    ("PIM.3.BP7", "Süreç iyileştirmesini doğrula", "Uygulama etkisini izlemek, ölçmek ve tanımlı iyileştirme hedeflerine göre doğrulamak."),
    ("PIM.3.BP8", "İyileştirme sonuçlarını duyur", "İyileştirmelerden elde edilen bilgiyi kurumun ilgili bölümleriyle paylaşmak."),
    ("PIM.3.BP9", "İyileştirme sonuçlarını değerlendir", "Doğrulanmış çözümün kurumun başka süreç veya birimlerinde kullanılabilirliğini değerlendirmek."),
]

FLOW_LINES = [
    "flowchart TD",
    'A["Değerlendirme, denetim, performans, risk veya geri bildirim girdisi"] --> B["SRÇ.018 değişiklik kaydı açılır"]',
    'B --> C["Ön değerlendirme ve etki analizi yapılır"]',
    'C --> D{"İyileştirme fırsatı mı?"}',
    'D -- "Hayır" --> E["Normal değişiklik SRÇ.018 akışında sürdürülür"]',
    'D -- "Evet" --> F["Mevcut durum, gerekçe ve iyileştirme hedefi belirlenir"]',
    'F --> G["Kaynak taahhüdü ile onay yetkisi netleştirilir"]',
    'G --> H["Etki ve uygulama önceliği ayrı ayrı belirlenir"]',
    'H --> I{"Kapsamlı plan gerekli mi?"}',
    'I -- "Hayır" --> J["Faaliyetler SRÇ.018 kaydında planlanır"]',
    'I -- "Evet" --> K["PLN.002 Süreç İyileştirme Planı hazırlanır"]',
    'J --> L["Değişiklik SRÇ.018 kapsamında uygulanır"]',
    'K --> L',
    'L --> M["SRÇ.018 değişiklik gözden geçirmesi yapılır"]',
    'M --> N{"İyileştirme hedefi gerçekleşti mi?"}',
    'N -- "Hayır" --> C',
    'N -- "Evet" --> O["Sonuç raporlanır ve ilgili taraflara duyurulur"]',
    'O --> P["Başka süreçlerde yeniden kullanım değerlendirilir"]',
    'P --> Q{"Yeni uygulama alanı var mı?"}',
    'Q -- "Evet" --> R["Her yeni kapsam için ayrı SRÇ.018 kaydı açılır"]',
    'Q -- "Hayır" --> S["İyileştirme kapatılır"]',
    'R --> B',
]

INTERACTION_LINES = [
    "flowchart LR",
    'A["SRÇ.005 Değerlendirme sonuçları"] --> I["SRÇ.006 Süreç İyileştirme"]',
    'B["SRÇ.026 Denetim sonuçları"] --> I',
    'C["SRÇ.017 Problem çözüm sonuçları"] --> I',
    'D["LST.009 ve RPR.001 performans sonuçları"] --> I',
    'E["SRÇ.008 Risk sonuçları"] --> I',
    'F["SRÇ.007 Öğrenilmiş dersler"] --> I',
    'G["SRÇ.002 Müşteri memnuniyeti ve YGG çıktıları"] --> I',
    'H["Kullanıcı ve paydaş geri bildirimleri"] --> I',
    'I <--> J["SRÇ.018 Değişiklik kaydı ve uygulama"]',
    'I --> K["PLN.002 Süreç İyileştirme Planı"]',
    'J --> L["SRÇ.018 Değişiklik gözden geçirme sonucu"]',
    'L --> M["RPR.001 Süreç Performansları Raporu"]',
    'L --> N["LST.012 Yaygınlaştırma ve bilgilendirme"]',
    'L --> O["Yeniden kullanım kararı ve yeni SRÇ.018 kayıtları"]',
]


def _image(storage: bool, filename: str, alt: str, width: int = 1000) -> str:
    if storage:
        return f'<p><ac:image ac:width="{width}"><ri:attachment ri:filename="{html.escape(filename)}" /></ac:image></p>'
    return f'<p style="text-align:center"><img class="diagram" src="attachments/{quote(filename)}" alt="{html.escape(alt)}" /></p>'


def process_body(storage: bool = True) -> str:
    related = "<br />".join([
        "İÜC.BİDB.SRÇ.002 - Kalite Güvencesi Süreci",
        "İÜC.BİDB.SRÇ.005 - Süreç Değerlendirme Süreci",
        "İÜC.BİDB.SRÇ.007 - Proje Yönetimi Süreci",
        "İÜC.BİDB.SRÇ.008 - Risk Yönetimi Süreci",
        "İÜC.BİDB.SRÇ.017 - Problem Çözüm Yönetimi Süreci",
        SRC018,
        "İÜC.BİDB.SRÇ.025 - Ölçüm Süreci",
        "İÜC.BİDB.SRÇ.026 - Denetim Süreci",
    ])
    mermaid = info_macro("Mermaid Kodu", FLOW_LINES) if storage else info_view("Mermaid Kodu", FLOW_LINES)
    activities = [
        ["F1", "İyileştirme fırsatını belirle", "İç ve dış kaynaklardan gelen konu SRÇ.018 değişiklik kaydında gerekçesi ve kaynak bağlantısıyla kaydedilir; normal değişiklik veya iyileştirme fırsatı olarak sınıflandırılır. (PIM.3.BP2)", "SRÇ.018 değişiklik kaydı ve sınıflandırma kararı"],
        ["F2", "Mevcut durumu analiz et ve hedef oluştur", "Etkilenen süreçlerin mevcut durumu, süreç kaynaklı riskleri, beklenen fayda ve başarı ölçütü analiz edilerek iyileştirme hedefi belirlenir. (PIM.3.BP3)", "SRÇ.018 etki analizi; iyileştirme hedefi ve başarı ölçütü"],
        ["F3", "Kaynak taahhüdü ve onayı sağla", "Gerekli insan, zaman, bütçe, araç ve yönetim desteği belirlenir; rol bazlı onay yetkisine göre taahhüt alınır. (PIM.3.BP1)", "Onay ve kaynak taahhüt kaydı"],
        ["F4", "Etki ve uygulama önceliğini belirle", "Etki ve uygulama önceliği birbirinden ayrı olarak Yüksek, Orta veya Düşük etiketiyle belirlenir. (PIM.3.BP4)", "Etki ve uygulama önceliği"],
        ["F5", "Süreç değişikliğini planla", "Faaliyet, sorumlu, kaynak, zamanlama, bağımlılık, risk, başarı ölçütü ve doğrulama yöntemi tanımlanır. Uyarlama koşuluna göre SRÇ.018 kaydı veya PLN.002 kullanılır. (PIM.3.BP5)", f"SRÇ.018 değişiklik kaydı veya {PLN002}"],
        ["F6", "Süreç değişikliğini uygula", "Onaylanan süreç, doküman, araç veya uygulama değişikliği SRÇ.018 kapsamında kontrollü biçimde gerçekleştirilir ve kanıtları kaydedilir. (PIM.3.BP6)", "SRÇ.018 uygulama, sürüm ve kanıt kayıtları"],
        ["F7", "İyileştirmeyi doğrula", "Uygulamanın etkisi hedef ve başarı ölçütleriyle karşılaştırılarak SRÇ.018 değişiklik gözden geçirmesi içinde doğrulanır. (PIM.3.BP7)", "SRÇ.018 değişiklik gözden geçirme sonucu"],
        ["F8", "Sonuçları duyur ve raporla", "Elde edilen bilgi ilgili taraflarla paylaşılır; hedef kitleyi etkileyen sonuç LST.012'ye, doğrulanmış önemli kazanım RPR.001'e işlenir. (PIM.3.BP8)", f"{LST012}; {RPR001}; doğal iletişim kanıtı"],
        ["F9", "Yeniden kullanımı değerlendir", "Doğrulanmış çözümün başka süreçlerde kullanım olanağı ilgili süreç sahipleriyle değerlendirilir; her yeni uygulama alanı için ayrı SRÇ.018 kaydı açılır. (PIM.3.BP9)", "Yeniden kullanım kararı; yeni SRÇ.018 kayıtları"],
    ]
    return "".join([
        "<h2>1. Süreç Bilgileri</h2>",
        table(["Alan", "Değer"], [
            ["Kurum", "İstanbul Üniversitesi - Cerrahpaşa Bilgi İşlem Daire Başkanlığı"],
            ["Süreç Kodu ve Adı", SRC006],
            ["Süreç Referansı", "ISO/IEC 15504-5:2006 PIM.3 - Process improvement"],
            ["Süreç Sahibi", PROCESS_OWNER],
            ["Hedef Kitle", "Bilgi İşlem Daire Başkanı, Proje Yöneticisi, süreç sahipleri, Kalite Danışmanı, değişiklik sorumluları ve gözden geçirenler"],
            ["Yayın ve Erişim Ortamı", "Confluence ve Google Drive; uzaktan erişimde İÜC VPN ve kurumsal yetkilendirme"],
            ["Durum", "Aktif"], ["Sürüm", "v1.0"], ["Yürürlük Tarihi", "15-02-2025"],
            ["Son Gözden Geçirme Tarihi", "14-07-2026"],
            ["Güncelleme Sıklığı", "Yılda en az bir kez veya iyileştirme/değişiklik yaklaşımında önemli değişiklik olduğunda"],
        ]),
        "<h2>2. Amaç</h2>",
        p("Bu sürecin amacı, kurumun iş ihtiyaçlarıyla uyumlu olarak kullanılan süreçlerin etkinliğini ve verimliliğini sürekli geliştirmek; iyileştirme fırsatlarını gerekçeli hedeflere, kontrollü değişikliklere ve doğrulanmış kurumsal kazanımlara dönüştürmektir."),
        "<h3>2.1. Süreç Sonuçları</h3>",
        table(["Sonuç ID", "Süreç Sonucu"], [
            ["S1", "İyileştirme faaliyetlerini sürdürecek kaynak ve yönetim taahhüdü sağlanır."],
            ["S2", "İç ve dış çevreden kaynaklanan konular, gerekçeli iyileştirme fırsatları olarak belirlenir."],
            ["S3", "İyileştirme uyarısının geldiği süreçlerin mevcut durumu analiz edilir."],
            ["S4", "İyileştirme hedefleri belirlenir ve önceliklendirilir; gerekli süreç değişiklikleri tanımlanır, planlanır ve uygulanır."],
            ["S5", "Uygulama etkileri izlenir, ölçülür ve tanımlı iyileştirme hedeflerine göre doğrulanır."],
            ["S6", "İyileştirmelerden elde edilen bilgi kurumun ilgili bölümleriyle paylaşılır."],
            ["S7", "İyileştirme sonuçları değerlendirilir ve çözümün kurumun başka alanlarında kullanımı ele alınır."],
        ]),
        "<h2>3. Kapsam</h2>",
        table(["Kapsam Öğesi", "Açıklama"], [
            ["Kapsama Dahil", "LST.006 içinde tanımlanan güncel standart süreç setine ilişkin iyileştirme fırsatlarının belirlenmesi, hedeflendirilmesi, önceliklendirilmesi, planlanması, kaynak/onay kararları, değişiklik uygulamasının SRÇ.018 üzerinden yönetilmesi, sonuç doğrulama, raporlama, duyuru ve yeniden kullanım değerlendirmesi"],
            ["Kapsam Dışı", "Değişiklik talebinin ayrıntılı uygulanması ve sürüm kontrolü; bunlar SRÇ.018 kapsamındadır. Problem kök neden ve düzeltici faaliyet yönetimi SRÇ.017, resmî denetimler SRÇ.026 kapsamındadır. Ayrı iyileştirme registerı tutulmaz."],
            ["Uygulama Alanı", "İÜC BİDB standart süreçleri, bunların dokümanları, araçları, yöntemleri, rolleri ve uygulamaları"],
        ]),
        "<h2>4. Referanslar</h2>",
        table(["Referans", "Açıklama"], [
            ["ISO/IEC 15504-5:2006 PIM.3 - Process improvement", "Süreç amacı, sonuçları, BP1-BP9 temel uygulamaları ve ilişkili iş ürünleri"],
            ["ISO/IEC 15504-5:2006 - Process Assessment Model", "Süreç boyutu ve değerlendirme göstergeleri"],
            ["ISO/IEC 15504-5:2006 - Process Attributes", "PA 2.1, PA 2.2, PA 3.1 ve PA 3.2 süreç öznitelikleri ile genel uygulamalar"],
        ]),
        "<h2>5. Terimler ve Kısaltmalar</h2>",
        table(["Terim / Kısaltma", "Açıklama"], [
            ["PIM.3", "ISO/IEC 15504-5 içindeki Process improvement süreci"],
            ["İyileştirme Fırsatı", "Bir problem bulunması zorunlu olmaksızın süreç etkinliği, verimliliği, uygunluğu veya risk durumunu geliştirme olanağı"],
            ["Etki", "İyileştirmenin beklenen fayda, risk, kapsam veya kurumsal sonuç büyüklüğü"],
            ["Uygulama Önceliği", "Yasal/denetim tarihi, risk aciliyeti, bağımlılık, gecikme sonucu, kaynak uygunluğu ve etkiye göre belirlenen ele alınma sırası"],
            ["SRÇ.018 Değişiklik Gözden Geçirmesi", "Uygulanan değişikliğin hedeflenen sonucu üretip üretmediğinin SRÇ.018 kapsamında incelenmesi"],
            ["Yeniden Kullanım", "Doğrulanmış iyileştirme çözümünün başka süreç veya birimlerde uygulanabilirliğinin değerlendirilmesi"],
        ]),
        "<h2>6. Süreç Aktivitesi</h2>",
        table(["Alan", "Açıklama"], [
            ["Süreç Başlatıcısı", "SRÇ.005 süreç değerlendirmesi; SRÇ.026 denetim sonucu; SRÇ.017 problem çözüm sonucu; SRÇ.018 talebi; LST.009/RPR.001 performans sonucu; SRÇ.008 risk sonucu; kullanıcı/paydaş geri bildirimi; SRÇ.007 öğrenilmiş ders; SRÇ.002 müşteri memnuniyeti veya Yönetim Gözden Geçirme çıktısı"],
            ["Süreç Başlangıcı", "İyileştirme adayının SRÇ.018 değişiklik kaydı olarak açılması ve ön değerlendirmeye alınması"],
            ["Süreç Bitişi", "İyileştirme hedefinin SRÇ.018 değişiklik gözden geçirmesiyle doğrulanması; sonucun raporlanması/duyurulması; yeniden kullanım kararının verilmesi ve gerekli yeni kayıtların açılması"],
            ["Ana Faaliyetler", "Fırsat belirleme; mevcut durum analizi ve hedef oluşturma; kaynak taahhüdü; önceliklendirme; planlama; değişikliği uygulama; sonucu doğrulama; duyuru/raporlama; yeniden kullanım değerlendirmesi"],
            ["İlgili Süreçler", related],
        ]),
        "<h2>7. Roller ve Sorumluluklar</h2>", p("Bu süreç kapsamındaki rol, sorumluluk, yetki, yetkinlik ve RACI bilgileri İÜC.BİDB.LST.010 - Süreç Rol Yetki ve RACI Matrisi (İÜC.BİDB.SRÇ.006) dokümanında yönetilir."),
        "<h2>8. Araçlar ve Altyapı</h2>",
        table(["Tür", "Araç / Altyapı Bileşeni", "Kullanım Amacı", "Erişim ve Kullanım Koşulu", "Sorumlu Rol / Birim"], [
            ["Araç", "Confluence", "Süreç, prosedür, plan, rapor ve ilgili iyileştirme dokümanlarının yayımlanması", "Kurumsal hesap ve atanmış okuma/yazma yetkisi; uzaktan erişimde VPN", "Proje Geliştirme Yönetimi / Confluence Yöneticisi"],
            ["Altyapı", "Google Drive", "İyileştirme ekleri, karar ve doğrulama kanıtlarının kontrollü saklanması", "Kurumsal hesap ve rol bazlı klasör yetkisi", "İlgili Süreç Sahibi / Kalite Danışmanı"],
            ["Araç", "Jira", "Değişiklik, iyileştirme faaliyeti, bağımlılık ve uygulama takibinin yürütülmesi", "Proje veya süreç bazlı yetkilendirme", "Proje Yöneticisi / Jira Yöneticisi"],
            ["Araç", "Bitbucket", "Süreç/doküman değişikliklerinin sürüm kontrollü kaynak ve değişiklik geçmişinin yönetilmesi", "Repository yetkisi ve tanımlı değişiklik kuralları", "Proje Geliştirme Yönetimi / Bitbucket Yöneticisi"],
            ["İletişim", "Kurumsal e-posta", "Onay, kaynak taahhüdü, gözden geçirme ve sonuç bilgilendirmeleri", "Kurumsal hesap ve ilgili dağıtım listeleri", "Süreç Sahibi / Proje Yöneticisi / Kalite Danışmanı"],
            ["Altyapı", "İÜC VPN ve kurumsal kimlik altyapısı", "Kurum dışından kayıt ve kanıt sistemlerine güvenli erişim", "Geçerli hesap, VPN yetkisi ve bilgi güvenliği kuralları", "İÜC BİDB Altyapı ve Erişim Yönetimi"],
        ], fixed=True),
        "<h2>9. Süreç İş Ürünleri</h2>", p("Sürecin girdi ve çıktı iş ürünleri ile kalite kriterleri İÜC.BİDB.LST.008 - İş Ürünleri ve Kalite Kriterleri Listesi (İÜC.BİDB.SRÇ.006) dokümanında yönetilir."),
        "<h2>10. Süreç Akışı</h2>", _image(storage, FLOW_PNG, "SRÇ.006 süreç akışı") + mermaid,
        "<h2>11. Süreç Faaliyetleri</h2>", table(["Faaliyet ID", "Faaliyet", "Açıklama", "Elde Edilen / Güncellenen İş Ürünü"], activities),
        "<h2>12. Ölçüm ve İzleme</h2>", p("Az sayıda yönetilebilir performans ölçümü İÜC.BİDB.LST.009 - Süreç Performans Ölçüm Seti (İÜC.BİDB.SRÇ.006) dokümanında tanımlanır. Sonuçlar doğal SRÇ.018 kayıtlarından ve RPR.001'den üretilir; ayrı iyileştirme registerı oluşturulmaz."),
        "<h2>13. Uygulama ve Uyarlama Kuralları</h2>",
        "<h3>13.1. Tek Giriş ve Sınıflandırma</h3>" + p("Her değişiklik veya iyileştirme adayı önce SRÇ.018 değişiklik kaydı olarak açılır. Ön değerlendirme ve etki analizi SRÇ.018 kaydında yürütülür; normal değişiklikler SRÇ.018 akışında kalır, iyileştirme fırsatları SRÇ.006 yönetişiminde devam eder."),
        "<h3>13.2. Etki, Öncelik ve Yetki</h3>" + p("Etki ve uygulama önceliği ayrı alanlardır ve sayısal puan kullanılmadan Yüksek, Orta veya Düşük etiketiyle gösterilir. Proje Geliştirme Yönetimi kapsamındaki, ilave bütçe gerektirmeyen, organizasyon yapısını değiştirmeyen ve kurum genelinde önemli etki oluşturmayan iyileştirmeler Proje Yöneticisinin devredilmiş yetkisinde onaylanabilir; diğerleri Bilgi İşlem Daire Başkanı onayına sunulur."),
        "<h3>13.3. Planlama Uyarlaması</h3>" + table(["Koşul", "Planlama Yöntemi"], [["Tek süreçle sınırlı ve önemli kaynak gerektirmeyen iyileştirme", "Faaliyetler SRÇ.018 değişiklik kaydı içinde planlanır."], ["Yüksek etkili, birden fazla süreci etkileyen veya önemli kaynak gerektiren iyileştirme", f"{PLN002} hazırlanır ve kaynak SRÇ.018 kaydıyla ilişkilendirilir."]]),
        "<h3>13.4. Uygulama ve Doğrulama</h3>" + p("Süreç, doküman, araç veya uygulama üzerindeki gerçek değişiklik SRÇ.018 kapsamında kontrollü olarak uygulanır. İyileştirme başarısı SRÇ.018 değişiklik gözden geçirmesinde, önceden belirlenmiş hedef ve kanıtlarla değerlendirilir. Olumlu sonuç olmadan iyileştirme tamamlanmış sayılmaz."),
        "<h3>13.5. Raporlama, Duyuru ve Yeniden Kullanım</h3>" + p("Doğrulanmış önemli kazanımlar RPR.001 içinde özetlenir. Süreç kullanıcılarını etkileyen sonuçlar LST.012 ile duyurulur; sınırlı teknik değişikliklerde doğal ekip iletişim kaydı kanıt olabilir. Başarılı çözümün başka süreçlerde uygulanabilirliği değerlendirilir ve her yeni uygulama alanı için ayrı SRÇ.018 kaydı açılır."),
        "<h2>14. Süreç Etkileşimleri</h2>", p("Sürecin diğer süreç ve dokümanlarla girdi/çıktı etkileşimleri İÜC.BİDB.LST.007 - Süreç Etkileşim Matrisi (İÜC.BİDB.SRÇ.006) dokümanında yönetilir."),
        "<h2>15. Sürüm Geçmişi</h2>", history("Süreç İyileştirme Süreci", REVIEWED_BY, APPROVED_BY),
    ])


def lst007_body(storage: bool = True) -> str:
    mermaid = info_macro("Mermaid Kodu", INTERACTION_LINES) if storage else info_view("Mermaid Kodu", INTERACTION_LINES)
    return "".join([
        "<h2>1. Liste Özeti</h2>", table(["Alan", "Değer"], [["İlgili Süreç", SRC006], ["Kullanım Amacı", "SRÇ.006'nın süreç ve doküman arayüzlerini, iyileştirme girdilerini ve doğrulanmış çıktı yönlendirmelerini tanımlamak"], ["Sorumlu", PREPARED_BY], ["Durum", "Aktif"], ["Sürüm", "v1.0"]]),
        "<h2>2. Kullanım Değerleri</h2>", table(["Değer", "Anlamı"], [["Girdi", "İyileştirme fırsatının belirlenmesi, gerekçelendirilmesi veya önceliklendirilmesi için kullanılan süreç, kayıt, veri veya geri bildirim"], ["Çıktı", "İyileştirme yönetimi sonucunda oluşan hedef, plan, doğrulama, raporlama, duyuru veya yeniden kullanım kararı"], ["Çift yönlü", "SRÇ.006 yönetişimi ile SRÇ.018 değişiklik uygulaması arasındaki karşılıklı bilgi ve karar akışı"]]),
        "<h2>3. Süreç Etkileşim Diyagramı</h2>", _image(storage, INTERACTION_PNG, "SRÇ.006 süreç etkileşim diyagramı", 900) + mermaid,
        "<h2>4. Girdi Etkileşimleri Matrisi</h2>", table(["Kaynak Süreç / Doküman", "Etkileşim Türü", "Girdi / Bilgi", "Kayıt / Kanıt", "Açıklama"], [
            ["İÜC.BİDB.SRÇ.005 - Süreç Değerlendirme Süreci", "İyileştirme girdisi", "Güçlü/zayıf yönler ve iyileştirme fırsatları", "İÜC.BİDB.FRM.001 - Süreç Gözden Geçirme Formu (İlgili Süreç); İÜC.BİDB.RPR.001 - Süreç Performansları Raporu", "Değerlendirme bulgularının iyileştirme hedeflerine dönüşmesini destekler."],
            ["İÜC.BİDB.SRÇ.026 - Denetim Süreci", "Denetim girdisi", "Denetim bulguları ve öneriler", "Denetim raporu / bulgu kaydı", "Kurumsal veya dış çevre kaynaklı iyileştirme uyarısı sağlar."],
            ["İÜC.BİDB.SRÇ.017 - Problem Çözüm Yönetimi Süreci", "Düzeltici iyileştirme girdisi", "Problem çözüm ve düzeltici faaliyet sonuçları", "Problem ve faaliyet kaydı", "Çözümden doğan süreç değişikliği veya iyileştirme fırsatını sağlar."],
            [SRC018, "Değişiklik girdisi", "Ön değerlendirilmiş ve iyileştirme fırsatı olarak sınıflandırılmış değişiklik kaydı", "SRÇ.018 değişiklik kaydı ve etki analizi", "SRÇ.006 için tek kayıt girişini ve tekrarsız analizi sağlar."],
            ["İÜC.BİDB.LST.009 süreç özel ölçüm setleri ve RPR.001", "Performans girdisi", "Hedef, sapma, eğilim ve süreç performans sonuçları", "LST.009 doğal veri kaynakları; RPR.001", "Ölçülebilir iyileştirme ihtiyacını ve hedefini destekler."],
            ["İÜC.BİDB.SRÇ.008 - Risk Yönetimi Süreci", "Risk girdisi", "Süreç kaynaklı risk ve fırsatlar", "Risk kaydı ve değerlendirmesi", "Risk azaltma veya fırsat gerçekleştirme hedefi sağlar."],
            ["SRÇ.007 öğrenilmiş dersler; SRÇ.002 müşteri memnuniyeti; Yönetim Gözden Geçirme; kullanıcı/paydaş geri bildirimleri", "Kurumsal geri bildirim girdisi", "Dersler, memnuniyet sonuçları, yönetim kararları ve geri bildirimler", "Kaynak toplantı, anket, rapor veya iletişim kaydı", "İç ve dış çevreden iyileştirme fırsatı sağlar."],
            [PRS004, "Yöntem girdisi", "Sınıflandırma, etki/öncelik, planlama uyarlaması, onay, doğrulama ve yeniden kullanım kuralları", PRS004, "SRÇ.006 ve SRÇ.018 arasındaki ortak çalışma yöntemini belirler."],
        ]),
        "<h2>5. Çıktı Etkileşimleri Matrisi</h2>", table(["Hedef Süreç / Doküman", "Etkileşim Türü", "Çıktı / Yönlendirme", "Kayıt / Kanıt", "Açıklama"], [
            [SRC018, "Uygulama yönlendirmesi", "Onaylı hedef, plan, kaynak, öncelik ve değişiklik kapsamı", "SRÇ.018 değişiklik kaydı", "Gerçek değişiklik SRÇ.018 kapsamında kontrollü uygulanır."],
            [PLN002, "Koşullu plan çıktısı", "Yüksek etkili, çok süreçli veya önemli kaynak gerektiren iyileştirme planı", PLN002, "Kaynak SRÇ.018 kaydıyla ilişkilendirilir."],
            ["SRÇ.018 değişiklik gözden geçirme sonucu", "Doğrulama çıktısı", "Hedef, kanıt ve gerçekleşen sonuç karşılaştırması", "SRÇ.018 değişiklik kaydı", "Olumlu sonuç olmadan iyileştirme tamamlanmaz."],
            [RPR001, "Kümülatif raporlama", "Doğrulanmış önemli iyileştirme kazanımı", RPR001, "RPR.001 başarıyı yeniden değerlendirmez; kaynak sonucu özetler."],
            [LST012, "Yaygınlaştırma çıktısı", "Süreç kullanıcılarını etkileyen iyileştirme sonucu", LST012, "Hedef kitle, kanal, tarih ve kanıt bağlantısı kaydedilir."],
            ["Yeniden kullanım kararı ve yeni SRÇ.018 kayıtları", "Kurumsal yayılım çıktısı", "Çözümün diğer süreçlerde uygulanabilirlik kararı", "Kaynak karar ve ilgili yeni SRÇ.018 kayıtları", "Her yeni uygulama alanı ayrı değerlendirilir."],
        ]),
        "<h2>6. Etkileşim Notları</h2>", p("SRÇ.006 iyileştirme hedefini, önceliğini, planını ve sonuç görünürlüğünü yönetir; gerçek süreç/doküman/araç değişikliği ile değişiklik gözden geçirmesi SRÇ.018 kapsamında yürütülür. Ayrı iyileştirme registerı oluşturulmaz."),
        "<h2>7. Sürüm Geçmişi</h2>", history("SRÇ.006 Süreç Etkileşim Matrisi", REVIEWED_BY, APPROVED_BY),
    ])


def lst008_body() -> str:
    inputs = [
        [PRS004, "Girdi", "İyileştirme ve değişiklik yaşam döngüsü kuralları", "Aktif sürüm; SRÇ.006/SRÇ.018 geçişi, etki, öncelik, onay ve doğrulama kuralları tanımlı", "Zorunlu", "PIM.3.BP1-BP9"],
        ["İÜC.BİDB.FRM.001 - Süreç Gözden Geçirme Formu (İlgili Süreç) ve İÜC.BİDB.RPR.001 - Süreç Performansları Raporu", "Girdi", "Süreç değerlendirme bulguları, güçlü/zayıf yönler ve performans eğilimleri", "Kaynak süreç, BP/GP, bulgu türü ve değerlendirme bağlantısı izlenebilir", "Koşullu", "PIM.3.BP2-BP4"],
        ["İÜC.BİDB.SRÇ.026 - Denetim Süreci bulgu/rapor kayıtları", "Girdi", "Denetim bulguları ve iyileştirme önerileri", "Kaynak denetim, bulgu, tarih ve sorumluluk izlenebilir", "Koşullu", "PIM.3.BP2-BP3"],
        ["İÜC.BİDB.SRÇ.017 - Problem Çözüm Yönetimi Süreci sonuç kayıtları", "Girdi", "Problem çözüm ve düzeltici faaliyet sonucundan doğan iyileştirme ihtiyacı", "Kaynak problem ve çözüm kararı bağlantısı mevcut", "Koşullu", "PIM.3.BP2-BP3"],
        ["İÜC.BİDB.SRÇ.018 - Değişiklik Talebi Yönetimi Süreci değişiklik kaydı ve etki analizi", "Girdi", "İyileştirme fırsatı sınıflandırması, mevcut durum, etki, risk, beklenen fayda ve etkilenen varlıklar", "Alanlar tamamlanmış, kaynak bağlantıları ve sınıflandırma kararı izlenebilir", "Zorunlu", "PIM.3.BP2-BP5"],
        ["İÜC.BİDB.LST.009 süreç özel ölçüm sonuçları; İÜC.BİDB.SRÇ.008 risk kayıtları; kullanıcı/paydaş geri bildirimleri; SRÇ.007 öğrenilmiş dersleri; SRÇ.002 müşteri memnuniyeti ve Yönetim Gözden Geçirme çıktıları", "Girdi", "Performans, risk, deneyim, memnuniyet ve yönetim kararlarından doğan iyileştirme uyarıları", "Kaynak, dönem, bağlam ve ilgili süreç açıklanabilir", "Koşullu", "PIM.3.BP2-BP4"],
    ]
    outputs = [
        ["İÜC.BİDB.SRÇ.018 - Değişiklik Talebi Yönetimi Süreci iyileştirme/değişiklik kaydı", "Çıktı", "Hedef, etki, uygulama önceliği, onay, kaynak taahhüdü, plan ve uygulama bağlantıları", "Kaynak fırsat, etkilenen süreç/doküman, beklenen fayda, risk, sorumlu ve doğrulama ölçütü tamamlanmış", "Zorunlu", "PIM.3.BP1-BP6"],
        [PLN002, "Çıktı", "Kapsamlı iyileştirmenin faaliyet, kaynak, takvim, risk, bağımlılık ve başarı ölçütü planı", "Yüksek etkili, çok süreçli veya önemli kaynak gerektiren çalışmalar için onaylı ve kaynak SRÇ.018 kaydıyla bağlı", "Koşullu", "PIM.3.BP1, BP4-BP5"],
        ["SRÇ.018 değişiklik gözden geçirme sonucu", "Çıktı", "Hedef ve gerçekleşen sonucun kanıta dayalı karşılaştırması", "Hedef, başarı ölçütü, başlangıç/sonuç verisi, sapma, karar ve gözden geçiren bilgisi mevcut", "Zorunlu", "PIM.3.BP7"],
        [RPR001, "Çıktı", "Doğrulanmış önemli iyileştirme kazanımlarının kümülatif yönetim özeti", "Kaynak SRÇ.018 sonucu ve ilgili süreç bağlantısı mevcut; başarı yeniden değerlendirilmemiş", "Koşullu", "PIM.3.BP7-BP8"],
        [LST012, "Çıktı", "Süreç kullanıcılarını etkileyen sonuçların yaygınlaştırma kaydı", "Süreç, hedef kitle, kanal, tarih, yayımlayan ve kanıt bağlantısı mevcut", "Koşullu", "PIM.3.BP8"],
        ["Yeniden kullanım kararı ve ilgili yeni SRÇ.018 kayıtları", "Çıktı", "Doğrulanmış çözümün diğer süreçlere aktarım kararı", "Değerlendirilen kapsam, karar gerekçesi, ilgili süreç sahibi ve her yeni kapsam için ayrı kayıt bağlantısı mevcut", "Zorunlu", "PIM.3.BP9"],
    ]
    quality = [
        ["SRÇ.018 iyileştirme/değişiklik kaydı", "Analiz ve İzlenebilirlik", "Kaynak, mevcut durum, etkilenen varlıklar, beklenen fayda, risk, hedef, etki ve uygulama önceliği birbirinden ayrılmış olmalı", "Alan ve bağlantı kontrolü", "Kalite Danışmanı / İlgili Süreç Sahibi", "Planlama öncesi"],
        [PLN002, "Uyarlama ve Plan Tamlığı", "Yalnızca uyarlama koşulu oluştuğunda hazırlanmalı; faaliyet, sorumlu, kaynak, takvim, risk, bağımlılık, başarı ölçütü ve doğrulama yöntemi bulunmalı", "Plan gözden geçirmesi", "Proje Yöneticisi / Bilgi İşlem Daire Başkanı", "Onay öncesi"],
        ["SRÇ.018 değişiklik gözden geçirme sonucu", "Doğrulama", "Uygulama öncesi hedef ve ölçüt ile gerçekleşen sonuç karşılaştırılmalı; olumlu/olumsuz karar ve takip ihtiyacı yazılmalı", "Kanıt ve karar kontrolü", "Gözden Geçiren", "Kapanış öncesi"],
        [RPR001, "Kaynak Sonuca Bağlılık", "Yalnızca doğrulanmış önemli kazanımlar alınmalı; kaynak SRÇ.018 sonucu gösterilmeli ve başarı yeniden değerlendirilmemeli", "Rapor satırı ve kaynak bağlantısı kontrolü", "Kalite Danışmanı", "Rapor güncellemesinde"],
        [LST012, "Yaygınlaştırma Kanıtı", "Süreç, hedef kitle, kanal, tarih ve kanıt bağlantısı eksiksiz olmalı", "LST.012 satır kontrolü", "Proje Yöneticisi / Yayımlayan", "Duyuru sonrasında"],
        ["Yeniden kullanım kararı", "Kapsam Ayrımı", "Her yeni süreç veya uygulama alanı için ayrı SRÇ.018 kaydı açılmalı; kaynak çözüm bağlantısı korunmalı", "Karar ve kayıt bağlantıları kontrolü", "Kalite Danışmanı / İlgili Süreç Sahibi", "İyileştirme kapanışında"],
    ]
    return "".join([
        "<h2>1. Liste Özeti</h2>", table(["Alan", "Değer"], [["İlgili Süreç", SRC006], ["Kullanım Amacı", "SRÇ.006 girdi ve çıktı iş ürünleri ile kalite kriterlerini tanımlamak"], ["Sorumlu", PREPARED_BY], ["Durum", "Aktif"], ["Sürüm", "v1.0"]]),
        "<h2>2. Kullanım Değerleri</h2>", table(["Değer", "Anlamı"], [["Zorunlu", "İlgili iyileştirme çalışmasında bulunması gereken iş ürünü"], ["Koşullu", "Kaynak, kapsam, etki veya uyarlama koşulu oluştuğunda kullanılan iş ürünü"], ["Doğal kayıt", "Ayrı bir register oluşturmadan kaynak süreç veya sistem içinde oluşan kanıt"]]),
        "<h2>3. Girdi İş Ürünleri Matrisi</h2>", table(["İş Ürünü", "Tür", "Kullanım Amacı / İçerik", "Kalite Kriteri", "Zorunluluk", "İlgili BP"], inputs),
        "<h2>4. Çıktı İş Ürünleri Matrisi</h2>", table(["İş Ürünü", "Tür", "Kullanım Amacı / İçerik", "Kalite Kriteri", "Zorunluluk", "İlgili BP"], outputs),
        "<h2>5. Kalite Kriterleri Kontrol Matrisi</h2>", table(["İş Ürünü", "Kontrol Alanı", "Kalite Kriteri", "Kontrol Yöntemi", "Kontrol Eden", "Kontrol Zamanı"], quality),
        "<h2>6. Sürüm Geçmişi</h2>", history("SRÇ.006 İş Ürünleri ve Kalite Kriterleri Listesi", REVIEWED_BY, APPROVED_BY),
    ])


def lst009_body() -> str:
    measures = [
        ["ÖLÇ.006.01", "İyileştirme Tanım Tamlığı", "İyileştirme fırsatlarının hedef, etki ve uygulama önceliği alanlarının eksiksizliği", "Hedef, etki ve uygulama önceliği eksiksiz kayıt / incelenen iyileştirme fırsatı × 100", "%", "%100", "Üç aylık / iyileştirme gözden geçirmesinde", "Kalite Danışmanı", "SRÇ.018 değişiklik kayıtları"],
        ["ÖLÇ.006.02", "Planlanan Faaliyetlerin Zamanında Tamamlanma Oranı", "Onaylanan iyileştirme faaliyetlerinin planlanan tarihte tamamlanması", "Zamanında tamamlanan faaliyet / dönemde tamamlanması planlanan faaliyet × 100", "%", "En az %90", "Üç aylık", "İlgili Süreç Sahibi / Proje Yöneticisi", "SRÇ.018 değişiklik kaydı veya PLN.002"],
        ["ÖLÇ.006.03", "Hedefi Doğrulanan İyileştirme Oranı", "SRÇ.018 değişiklik gözden geçirmesi tamamlanan iyileştirmelerin hedefe ulaşma durumu", "Hedefe ulaştığı doğrulanan iyileştirme / değişiklik gözden geçirmesi tamamlanan iyileştirme × 100", "%", "En az %80", "Yıllık ve yeterli veri oluştuğunda", "Kalite Danışmanı / Gözden Geçiren", "SRÇ.018 değişiklik gözden geçirme sonuçları; RPR.001"],
    ]
    collection = [[row[0], row[1], row[8], row[3], "Kaynak kayıtlarda dönem, durum ve sorumluluk alanları tamamlanır; payda sıfırsa sonuç 'Hesaplanmadı' olarak raporlanır.", row[6], row[7]] for row in measures]
    targets = [[row[0], row[1], row[5], "İlk gerçek dönem sonucu oluştuğunda karşılaştırılır.", "Hedef altı sonuçta neden, risk ve gerekli değişiklik SRÇ.018 kaydında değerlendirilir.", RPR001] for row in measures]
    return "".join([
        "<h2>1. Liste Özeti</h2>", table(["Alan", "Değer"], [["İlgili Süreç", SRC006], ["Kullanım Amacı", "SRÇ.006 performansını az sayıda üretilebilir ölçümle izlemek"], ["Sorumlu", PREPARED_BY], ["Durum", "Aktif"], ["Sürüm", "v1.0"]]),
        "<h2>2. Kullanım Değerleri</h2>", table(["Değer", "Anlamı"], [["Hedef", "Ölçüm için beklenen başarı düzeyi"], ["Hesaplanmadı", "İlgili dönemde payda veya yeterli gerçek veri oluşmadı"], ["Doğal veri kaynağı", "Ayrı ölçüm registerı oluşturmadan SRÇ.018, PLN.002 veya RPR.001 içinde oluşan kayıt"]]),
        "<h2>3. Performans Ölçüm Matrisi</h2>", table(["Ölçüm ID", "Ölçüm Adı", "Amaç", "Hesaplama", "Birim", "Hedef", "Sıklık", "Sorumlu", "Veri Kaynağı"], measures),
        "<h2>4. Veri Toplama ve Hesaplama Matrisi</h2>", table(["Ölçüm ID", "Ölçüm", "Ham Veri Kaynağı", "Hesaplama / Toplama Yöntemi", "Veri Kalitesi Kontrolü", "Toplama Zamanı", "Toplayan / Doğrulayan"], collection),
        "<h2>5. Hedef ve İzleme Matrisi</h2>", table(["Ölçüm ID", "Ölçüm", "Hedef", "Mevcut Sonuç", "Sapma ve Karar Kuralı", "Raporlama Yeri"], targets),
        "<h2>6. Sürüm Geçmişi</h2>", history("SRÇ.006 Süreç Performans Ölçüm Seti", REVIEWED_BY, APPROVED_BY),
    ])


def lst010_body() -> str:
    roles = [
        ["Bilgi İşlem Daire Başkanı", "Asıl süreç sahibi, kaynak taahhüdü ve yetki sınırı dışındaki iyileştirme onayı", "Kurumsal önceliklendirme, kaynak tahsisi ve nihai onay yetkisi", "Kurumsal hedef, risk, bütçe ve organizasyon etkisini değerlendirme", "Süreç sahibi ve onaylayan"],
        ["Proje Yöneticisi", "İyileştirme çalışmasını gözden geçirmek, koordine etmek ve devredilmiş sınırlar içinde onaylamak", "İlave bütçe/organizasyon değişikliği/önemli kurum geneli etkisi olmayan çalışmalar için devredilmiş onay", "Proje, kaynak, bağımlılık, değişiklik ve paydaş yönetimi", "Gözden geçiren / koşullu onaylayan"],
        ["Kalite Danışmanı", "Fırsat, hedef, etki, öncelik, plan, doğrulama ve raporlama koordinasyonu", "Sınıflandırma, hedef, ölçüt ve raporlama önerisi", "PIM.3, süreç değerlendirme, ölçüm, analiz ve dokümantasyon", "Hazırlayan / koordinatör"],
        ["İlgili Süreç Sahibi", "Mevcut durum ve etki analizine katılmak, kaynak/uygulanabilirlik görüşü vermek, uygulama kanıtı sağlamak", "Kendi süreç alanında teknik/operasyonel uygunluk görüşü", "İlgili süreç, araç, rol ve iş ürünleri bilgisi", "Katılımcı / uygulama sahibi"],
        ["Değişiklik Sorumlusu", "Onaylanan değişikliği SRÇ.018 kapsamında uygulamak ve kanıtlamak", "Onaylı kapsam içinde uygulama", "İlgili teknik/operasyonel uygulama ve sürüm kontrol yetkinliği", "Uygulayan"],
        ["Gözden Geçiren", "SRÇ.018 değişiklik gözden geçirmesinde hedef ve gerçekleşen sonucu karşılaştırmak", "Ek kanıt/düzeltme isteme ve sonuç görüşü verme", "Kanıt değerlendirme ve ilgili süreç alanı bilgisi", "Doğrulayan"],
    ]
    raci = [
        ["F1 İyileştirme fırsatını belirle", "I", "C", "R", "R", "I", "I"],
        ["F2 Mevcut durumu analiz et ve hedef oluştur", "I", "C", "R", "R", "C", "C"],
        ["F3 Kaynak taahhüdü ve onayı sağla", "A", "R/A*", "C", "C", "I", "I"],
        ["F4 Etki ve uygulama önceliğini belirle", "A", "R", "R", "C", "I", "I"],
        ["F5 Süreç değişikliğini planla", "A", "R", "R", "R", "C", "C"],
        ["F6 Süreç değişikliğini uygula", "I", "A", "C", "R", "R", "I"],
        ["F7 İyileştirmeyi doğrula", "I", "A", "C", "C", "C", "R"],
        ["F8 Sonuçları duyur ve raporla", "I", "A", "R", "C", "I", "C"],
        ["F9 Yeniden kullanımı değerlendir", "A", "R", "R", "R", "C", "C"],
    ]
    products = [
        ["SRÇ.018 değişiklik kaydı ve etki analizi", "I", "A", "R", "R", "C", "C"],
        [PLN002, "A", "R", "R", "R", "C", "C"],
        ["SRÇ.018 değişiklik gözden geçirme sonucu", "I", "A", "C", "C", "C", "R"],
        [RPR001, "I", "A", "R", "C", "I", "C"],
        [LST012, "I", "A", "R", "C", "I", "C"],
        ["Yeniden kullanım kararı / yeni SRÇ.018 kayıtları", "A", "R", "R", "R", "C", "C"],
    ]
    headers = ["Faaliyet / İş Ürünü", "BİD Başkanı", "Proje Yöneticisi", "Kalite Danışmanı", "İlgili Süreç Sahibi", "Değişiklik Sorumlusu", "Gözden Geçiren"]
    return "".join([
        "<h2>1. Liste Özeti</h2>", table(["Alan", "Değer"], [["İlgili Süreç", SRC006], ["Kullanım Amacı", "SRÇ.006 rol, yetki, yetkinlik ve RACI yapısını tanımlamak"], ["Sorumlu", PREPARED_BY], ["Durum", "Aktif"], ["Sürüm", "v1.0"]]),
        "<h2>2. Kullanım Değerleri</h2>", table(["Değer", "Anlamı"], [["R", "Faaliyeti gerçekleştiren / iş ürününü hazırlayan"], ["A", "Nihai hesap veren ve onaylayan"], ["C", "Görüşüne başvurulan"], ["I", "Bilgilendirilen"], ["R/A*", "Yalnızca tanımlı genel yetki devri sınırları içinde sorumlu ve onaylayan"]]),
        "<h2>3. Rol ve Yetkinlik Matrisi</h2>", table(["Rol", "Sorumluluk", "Yetki", "Asgari Yetkinlik", "Süreçteki Konum"], roles),
        "<h2>4. Süreç Faaliyetleri RACI Matrisi</h2>", table(headers, raci),
        "<h2>5. İş Ürünleri RACI Matrisi</h2>", table(headers, products),
        "<h2>6. Yetki ve Onay Matrisi</h2>", table(["Karar / Onay", "Hazırlayan", "Gözden Geçiren", "Onaylayan", "Yetki Sınırı / Kural"], [
            ["İyileştirme fırsatı sınıflandırması", "Kalite Danışmanı / İlgili Süreç Sahibi", "Proje Yöneticisi", "Bilgi İşlem Daire Başkanı veya devredilmiş sınırda Proje Yöneticisi", "Normal değişiklik SRÇ.018'de kalır; iyileştirme fırsatı SRÇ.006 yönetişimine geçer."],
            ["Etki ve uygulama önceliği", "Kalite Danışmanı", "İlgili Süreç Sahibi / Proje Yöneticisi", "Bilgi İşlem Daire Başkanı veya devredilmiş sınırda Proje Yöneticisi", "Etki ve öncelik ayrı Yüksek/Orta/Düşük etiketleridir; sayısal puan kullanılmaz."],
            ["Kaynak taahhüdü ve PLN.002", "Kalite Danışmanı / İlgili Süreç Sahibi", "Proje Yöneticisi", "Bilgi İşlem Daire Başkanı", "İlave bütçe, organizasyon değişikliği, önemli kurum geneli etki veya önemli kaynak ihtiyacı varsa asıl onay mercii karar verir."],
            ["SRÇ.018 değişiklik gözden geçirme sonucu", "Gözden Geçiren", "İlgili Süreç Sahibi / Proje Yöneticisi", "Değişiklik kaydındaki yetkili onay rolü", "Olumlu sonuç olmadan iyileştirme tamamlanmış sayılmaz."],
            ["Yeniden kullanım kararı", "Kalite Danışmanı / İlgili Süreç Sahibi", "Proje Yöneticisi", "Bilgi İşlem Daire Başkanı veya devredilmiş sınırda Proje Yöneticisi", "Her yeni uygulama alanı için ayrı SRÇ.018 kaydı açılır."],
        ]),
        "<h2>7. Sürüm Geçmişi</h2>", history("SRÇ.006 Süreç Rol Yetki ve RACI Matrisi", REVIEWED_BY, APPROVED_BY),
    ])


def blank_review_body() -> str:
    bp_rows = [[bp, title, "<em>Değerlendirme sırasında doldurulur.</em>", "<em>Mevcut kanıt veya kanıt eksikliği yazılır.</em>", "<em>YOK / ZAYIF / DAĞINIK / VAR / KAPSAM DIŞI</em>", "<em>Gerekirse tamamlayıcı aksiyon yazılır.</em>"] for bp, title, _ in PIM3_BPS]
    gp_rows = [[pa, gp, title, "<em>Değerlendirme sırasında doldurulur.</em>", "<em>Mevcut kanıt veya kanıt eksikliği yazılır.</em>", "<em>YOK / ZAYIF / DAĞINIK / VAR / KAPSAM DIŞI</em>", "<em>Gerekirse tamamlayıcı aksiyon yazılır.</em>"] for pa, gp, title in GPS]
    return "".join([
        "<h2>1. Değerlendirme Özeti</h2>", table(["Alan", "Değer"], [["Değerlendirilen Süreç", SRC006], ["Süreç Referansı", "ISO/IEC 15504-5 PIM.3 - Process improvement"], ["Süreç Durumu", "Aktif"], ["Süreç Sürümü", "v1.0"], ["Değerlendirme Kapsamı", "PIM.3 BP1-BP9; PA 2.1; PA 2.2; PA 3.1; PA 3.2"], ["Değerlendirme Tarihi", "<em>GG-AA-YYYY</em>"], ["Değerlendirmeyi Yapan", PREPARED_BY], ["Gözden Geçiren", REVIEWED_BY], ["Değerlendirmeyi Onaylayan", APPROVED_BY], ["Değerlendirme Sonucu", "<em>Etiket dağılımları, kritik bulgular ve güçlü uygulamalarla özetlenir; toplam puan veya tek bir süreç etiketi yazılmaz.</em>"]]),
        "<h2>2. Durum Değerleri</h2>", table(["Durum", "Anlamı"], LABELS),
        "<h2>3. BP Takip Matrisi</h2>", table(["BP", "Standart Beklentisi", "Mevcut Karşılama", "Karşılayan Doküman / Kayıt", "Durum", "Eksik / Tamamlayıcı Aksiyon"], bp_rows),
        "<h2>4. PA / GP Takip Matrisi</h2>", table(["PA", "GP", "Standart Beklentisi", "Mevcut Karşılama", "Karşılayan Doküman / Kayıt", "Durum", "Eksik / Tamamlayıcı Aksiyon"], gp_rows),
        "<h2>5. Öncelikli Tamamlama Listesi</h2>", table(["Öncelik", "Bulgu / Aksiyon", "Bulgu Türü", "İlgili BP / GP", "Hedef Süreç / İzleme Yeri"], [["<em>1</em>", "<em>Değerlendirme sırasında doldurulur.</em>", "<em>Uygunsuzluk / İyileştirme Fırsatı / Gözlem / Güçlü Uygulama</em>", "<em>BP / GP</em>", "<em>SRÇ.017 / SRÇ.018 / Değerlendirme Kaydı</em>"]]),
    ])


def assessment_body() -> str:
    bp_status = {
        "PIM.3.BP1": ("DAĞINIK", "Rol bazlı onay sınırı, kaynak türleri ve taahhüt adımı tanımlıdır; gerçek bir iyileştirme için alınmış kaynak taahhüdü henüz yoktur.", f"{SRC006}; {PRS004}; İÜC.BİDB.LST.010 (SRÇ.006)", "İlk gerçek iyileştirmede onay ve kaynak taahhüdü doğal kayıtlarla doğrulanmalıdır."),
        "PIM.3.BP2": ("VAR", "Değerlendirme, denetim, problem, değişiklik, performans, risk, geri bildirim, öğrenilmiş ders, müşteri memnuniyeti ve yönetim çıktıları kaynak olarak tanımlanmış; tek giriş noktası SRÇ.018 olarak belirlenmiştir.", f"{SRC006}; {PRS004}; İÜC.BİDB.LST.007-LST.008 (SRÇ.006)", "-"),
        "PIM.3.BP3": ("VAR", "Mevcut durum, kaynak kanıt, etkilenen süreç, beklenen fayda, risk, hedef ve başarı ölçütü için analiz yaklaşımı tanımlanmıştır.", f"{SRC006}; {PRS004}; SRÇ.018 etki analizi yaklaşımı", "-"),
        "PIM.3.BP4": ("VAR", "Etki ve uygulama önceliği ayrıştırılmış, her ikisi için Yüksek/Orta/Düşük etiketleri ve karar ölçütleri tanımlanmıştır.", f"{SRC006}; {PRS004}; İÜC.BİDB.LST.010 (SRÇ.006)", "-"),
        "PIM.3.BP5": ("VAR", "Sınırlı iyileştirmelerin SRÇ.018 kaydında; yüksek etkili, çok süreçli veya önemli kaynak gerektiren çalışmaların PLN.002 ile planlanması tanımlanmıştır.", f"{SRC006}; {PRS004}; {PLN002_TEMPLATE_TITLE}", "-"),
        "PIM.3.BP6": ("DAĞINIK", "Gerçek değişikliklerin SRÇ.018 kapsamında kontrollü uygulanacağı ve kanıtlanacağı tanımlıdır; uygulanmış bir iyileştirme örneği henüz bulunmamaktadır.", f"{SRC006}; {PRS004}; {SRC018}", "İlk gerçek iyileştirmede uygulama, sürüm ve kanıt bağlantıları SRÇ.018 kaydında tamamlanmalıdır."),
        "PIM.3.BP7": ("ZAYIF", "SRÇ.018 değişiklik gözden geçirmesiyle hedef, ölçüt ve gerçekleşen sonuç karşılaştırması tanımlıdır; doğrulanmış sonuç verisi henüz yoktur.", f"{SRC006}; {PRS004}; İÜC.BİDB.LST.009 (SRÇ.006)", "İlk uygulanan iyileştirmenin hedef ve sonuç verileriyle değişiklik gözden geçirmesi tamamlanmalıdır."),
        "PIM.3.BP8": ("ZAYIF", "RPR.001, LST.012 ve doğal iletişim kanıtı üzerinden duyuru kuralları tanımlıdır; gerçekleşmiş iyileştirme sonucu iletişimi henüz yoktur.", f"{SRC006}; {PRS004}; {RPR001}; {LST012}", "İlk doğrulanmış sonuçta hedef kitleye uygun iletişim kanıtı oluşturulmalıdır."),
        "PIM.3.BP9": ("ZAYIF", "Başarılı çözümün başka süreçlerde değerlendirilmesi ve her yeni kapsam için ayrı SRÇ.018 kaydı açılması tanımlıdır; gerçek yeniden kullanım kararı henüz yoktur.", f"{SRC006}; {PRS004}; İÜC.BİDB.LST.007-LST.008 (SRÇ.006)", "İlk doğrulanmış iyileştirmede yeniden kullanım kararı ve gerekçesi kaydedilmelidir."),
    }
    bp_rows = [[bp, title, bp_status[bp][1], bp_status[bp][2], bp_status[bp][0], bp_status[bp][3]] for bp, title, _ in PIM3_BPS]
    gp_labels = {
        "GP.2.1.1": "VAR", "GP.2.1.2": "VAR", "GP.2.1.3": "ZAYIF", "GP.2.1.4": "VAR", "GP.2.1.5": "DAĞINIK", "GP.2.1.6": "DAĞINIK",
        "GP.2.2.1": "VAR", "GP.2.2.2": "VAR", "GP.2.2.3": "VAR", "GP.2.2.4": "DAĞINIK",
        "GP.3.1.1": "VAR", "GP.3.1.2": "VAR", "GP.3.1.3": "VAR", "GP.3.1.4": "VAR", "GP.3.1.5": "VAR",
        "GP.3.2.1": "DAĞINIK", "GP.3.2.2": "DAĞINIK", "GP.3.2.3": "YOK", "GP.3.2.4": "DAĞINIK", "GP.3.2.5": "DAĞINIK", "GP.3.2.6": "ZAYIF",
    }
    gp_text = {
        "VAR": ("Standart süreç paketi içinde ilgili hedef, yöntem, rol, iş ürünü, etkileşim veya altyapı tanımı yeterli ve izlenebilir biçimde oluşturulmuştur.", f"{SRC006}; {PRS004}; süreç özel LST.007-LST.010; {PLN002_TEMPLATE_TITLE}", "-"),
        "DAĞINIK": ("Gerekli tanım veya altyapı vardır; ancak gerçek kaynak tahsisi, uygulama, iletişim, gözden geçirme/onay veya kullanım kanıtı henüz sistematik olarak oluşmamıştır.", "SRÇ.006 süreç paketi; mevcut yerel ve Confluence kayıtları", "İlk gerçek iyileştirmede doğal kaynak kanıtları tamamlanmalı ve SRÇ.018 kaydına bağlanmalıdır."),
        "ZAYIF": ("Yaklaşım ve ölçüm tanımlıdır; ancak gerçek sapma/ayarlama veya doğrulanmış iyileştirme performans verisi henüz oluşmamıştır.", "İÜC.BİDB.LST.009 (SRÇ.006); SRÇ.018 değişiklik gözden geçirme yaklaşımı", "İlk gerçek iyileştirmede sonuç, sapma ve karar kayıtları oluşturulmalıdır."),
        "YOK": ("Rol yetkinlikleri tanımlanmış olsa da süreç iyileştirmeye özgü yetkinlik doğrulaması ve eğitim/katılım kaydı bulunmamaktadır.", "İÜC.BİDB.LST.010 (SRÇ.006); SRÇ.020", "Yetkinlik ihtiyacı doğrulanmalı; gerekiyorsa SRÇ.020 kapsamında eğitim ve katılım kaydı oluşturulmalıdır."),
    }
    gp_rows = []
    for pa, gp, title in GPS:
        label = gp_labels[gp]
        current, evidence, action = gp_text[label]
        gp_rows.append([pa, gp, title, current, evidence, label, action])
    completion = [
        ["1", "İlk gerçek iyileştirmede yönetim onayı ve kaynak taahhüdünü doğal kayıtlarla doğrulamak", "Gözlem", "PIM.3.BP1; GP.2.1.5; GP.2.1.6", "SRÇ.018 değişiklik kaydı / Değerlendirme #1"],
        ["2", "Onaylı bir iyileştirmeyi SRÇ.018 kapsamında uygulayıp sürüm ve uygulama kanıtlarını bağlamak", "Gözlem", "PIM.3.BP6; GP.3.2.1; GP.3.2.4; GP.3.2.5", "SRÇ.018 / Değerlendirme #1"],
        ["3", "Uygulanan ilk iyileştirmenin hedef, ölçüt ve gerçekleşen sonucunu SRÇ.018 değişiklik gözden geçirmesiyle doğrulamak", "Gözlem", "PIM.3.BP7; GP.2.1.3; GP.2.2.4; GP.3.2.6", "SRÇ.018 / RPR.001"],
        ["4", "Doğrulanmış sonucu hedef kitleye duyurmak ve gerekiyorsa RPR.001'e işlemek", "Gözlem", "PIM.3.BP8; GP.3.2.2", "LST.012 / RPR.001"],
        ["5", "İlk doğrulanmış çözüm için yeniden kullanım kararını ve varsa yeni SRÇ.018 kayıtlarını oluşturmak", "Gözlem", "PIM.3.BP9", "SRÇ.018 / Değerlendirme #1"],
        ["6", "Süreç iyileştirme rollerinin yetkinlik ihtiyacını doğrulamak ve gerekiyorsa eğitim kaydı oluşturmak", "Gözlem", "GP.3.2.3", "SRÇ.020 / Değerlendirme #1"],
    ]
    return "".join([
        "<h2>1. Değerlendirme Özeti</h2>", table(["Alan", "Değer"], [["Değerlendirilen Süreç", SRC006], ["Süreç Referansı", "ISO/IEC 15504-5 PIM.3 - Process improvement"], ["Süreç Durumu", "Yerel gözden geçirmede"], ["Süreç Sürümü", "v1.0"], ["Değerlendirme Kapsamı", "PIM.3 BP1-BP9; PA 2.1; PA 2.2; PA 3.1; PA 3.2"], ["Değerlendirme Tarihi", "14-07-2026"], ["Değerlendirmeyi Yapan", PREPARED_BY], ["Gözden Geçiren", REVIEWED_BY], ["Değerlendirmeyi Onaylayan", APPROVED_BY], ["Değerlendirme Sonucu", "PIM.3 BP dağılımı 4 VAR, 2 DAĞINIK ve 3 ZAYIF; PA/GP dağılımı 11 VAR, 7 DAĞINIK, 2 ZAYIF ve 1 YOK'tur. Süreç yaklaşımı, tek SRÇ.018 giriş noktası, hedef/öncelik, planlama uyarlaması, yetki, doğrulama, raporlama ve yeniden kullanım kuralları tanımlanmıştır. Gerçek kaynak taahhüdü, uygulanmış/doğrulanmış iyileştirme, sonuç iletişimi, yeniden kullanım ve yetkinlik kanıtları henüz oluşmamıştır. Toplam puan veya tek bir süreç etiketi üretilmemiştir."]]),
        "<h2>2. Durum Değerleri</h2>", table(["Durum", "Anlamı"], LABELS),
        "<h2>3. BP Takip Matrisi</h2>", table(["BP", "Standart Beklentisi", "Mevcut Karşılama", "Karşılayan Doküman / Kayıt", "Durum", "Eksik / Tamamlayıcı Aksiyon"], bp_rows),
        "<h2>4. PA / GP Takip Matrisi</h2>", table(["PA", "GP", "Standart Beklentisi", "Mevcut Karşılama", "Karşılayan Doküman / Kayıt", "Durum", "Eksik / Tamamlayıcı Aksiyon"], gp_rows),
        "<h2>5. Öncelikli Tamamlama Listesi</h2>", table(["Öncelik", "Bulgu / Aksiyon", "Bulgu Türü", "İlgili BP / GP", "Hedef Süreç / İzleme Yeri"], completion),
    ])


def pln002_template_body() -> str:
    return "".join([
        "<h2>0. Şablon Hakkında</h2>",
        "<h3>0.1. Şablon Üst Bilgisi</h3>", table(["Alan", "Değer"], [["Kurum", "İstanbul Üniversitesi - Cerrahpaşa Bilgi İşlem Daire Başkanlığı"], ["Doküman Kodu", PLN002_TEMPLATE_CODE], ["Doküman Türü", "Doküman Şablonu"], ["Kullanım Alanı", PLN002], ["Durum", "Aktif"], ["Sürüm", "v1.0"], ["Yürürlük Tarihi", "15-02-2025"], ["Güncelleme Sıklığı", "SRÇ.006 veya SRÇ.018 planlama yaklaşımı değiştiğinde"]]),
        "<h3>0.2. Şablonun Kullanım Amacı</h3>", p("Bu şablon yalnızca yüksek etkili, birden fazla süreci etkileyen veya önemli kaynak gerektiren iyileştirmeler için İÜC.BİDB.PLN.002 - Süreç İyileştirme Planı hazırlanmasında kullanılır. Tek süreçle sınırlı ve önemli kaynak gerektirmeyen iyileştirmeler SRÇ.018 değişiklik kaydı içinde planlanır."),
        "<h3>0.3. Doküman Adlandırma Kuralı</h3>", p("İÜC.BİDB.PLN.002 - Süreç İyileştirme Planı - [İyileştirme Adı]"),
        "<h3>0.4. Sürüm Geçmişi</h3>", history("Süreç İyileştirme Planı Şablonu", REVIEWED_BY, APPROVED_BY),
        "<h2>1. Plan Bilgileri</h2>", table(["Alan", "Değer"], [["Kurum", "İstanbul Üniversitesi - Cerrahpaşa Bilgi İşlem Daire Başkanlığı"], ["Plan Kodu ve Adı", "<em>İÜC.BİDB.PLN.002 - Süreç İyileştirme Planı - [İyileştirme Adı]</em>"], ["Plan Referansı", f"{SRC006}; {SRC018}; {PRS004}"], ["Kaynak SRÇ.018 Değişiklik Kaydı", "<em>Bağlantı / kayıt no</em>"], ["İlgili Süreçler", "<em>Tam süreç kodu ve adı</em>"], ["İyileştirme Sahibi", "<em>İlgili Süreç Sahibi</em>"], ["Plan Sahibi", PREPARED_BY], ["Gözden Geçiren", "<em>Proje Yöneticisi</em>"], ["Onaylayan", "<em>Yetki sınırına göre Proje Yöneticisi veya Bilgi İşlem Daire Başkanı</em>"], ["Dönem", "<em>Başlangıç - bitiş</em>"], ["Durum", "<em>Taslak / Onaylı / Uygulamada / Tamamlandı</em>"], ["Sürüm", "<em>v0.1 / v1.0</em>"]]),
        "<h2>2. Mevcut Durum ve İyileştirme Gerekçesi</h2>", table(["Alan", "Açıklama / Kanıt"], [["Kaynak İyileştirme Fırsatı", "<em>Değerlendirme, denetim, performans, risk, geri bildirim veya diğer kaynak</em>"], ["Mevcut Durum", "<em>Başlangıç durumu ve veri/kanıt</em>"], ["Değişiklik Gerekçesi", "<em>Beklenen fayda ve değişiklik nedeni</em>"], ["Etkilenen Süreç / Doküman / Araç / Rol", "<em>Tam kod/ad ve bağlantılar</em>"]]),
        "<h2>3. İyileştirme Hedefi ve Başarı Ölçütleri</h2>", table(["Hedef", "Başlangıç Değeri / Durumu", "Başarı Ölçütü", "Doğrulama Yöntemi", "Veri / Kanıt Kaynağı"], [["<em>İyileştirme hedefi</em>", "<em>Mevcut değer/durum</em>", "<em>Beklenen sonuç</em>", "<em>SRÇ.018 değişiklik gözden geçirmesinde uygulanacak yöntem</em>", "<em>Kaynak</em>"]]),
        "<h2>4. Etki ve Uygulama Önceliği</h2>", table(["Alan", "Değer", "Gerekçe"], [["Etki", "<em>Yüksek / Orta / Düşük</em>", "<em>Fayda, kapsam, risk veya kurumsal sonuç büyüklüğü</em>"], ["Uygulama Önceliği", "<em>Yüksek / Orta / Düşük</em>", "<em>Yasal/denetim tarihi, risk aciliyeti, bağımlılık, gecikme sonucu ve kaynak uygunluğu</em>"]]),
        "<h2>5. Kapsam ve Uyarlama Kararı</h2>", table(["Alan", "Açıklama"], [["Kapsama Dahil", "<em>Plan kapsamında yapılacaklar</em>"], ["Kapsam Dışı", "<em>Plan kapsamında yapılmayacaklar</em>"], ["PLN.002 Kullanım Gerekçesi", "<em>Yüksek etki / çok süreç / önemli kaynak</em>"], ["Bağımlılıklar", "<em>Diğer süreç, proje, karar veya teknik bağımlılıklar</em>"]]),
        "<h2>6. Faaliyet, Kaynak ve Zamanlama Planı</h2>", table(["No", "Faaliyet", "Sorumlu", "Kaynak", "Başlangıç", "Bitiş", "Çıktı / Kanıt", "Durum"], [["<em>1</em>", "<em>Faaliyet</em>", "<em>Rol</em>", "<em>İnsan/zaman/bütçe/araç</em>", "<em>Tarih</em>", "<em>Tarih</em>", "<em>Çıktı</em>", "<em>Planlandı / Sürüyor / Tamamlandı</em>"]]),
        "<h2>7. Riskler ve Bağımlılıklar</h2>", table(["Risk / Bağımlılık", "Olası Etki", "Önlem / Yanıt", "Sorumlu", "İzleme Yeri"], [["<em>Risk veya bağımlılık</em>", "<em>Etki</em>", "<em>Yanıt</em>", "<em>Rol</em>", "<em>SRÇ.008 / SRÇ.018 / plan</em>"]]),
        "<h2>8. Onay ve Kaynak Taahhüdü</h2>", table(["Karar", "Rol", "Ad Soyad", "Tarih", "Açıklama / Koşul"], [["<em>Gözden Geçirme / Onay / Kaynak Taahhüdü</em>", "<em>Rol</em>", "<em>Ad Soyad</em>", "<em>Tarih</em>", "<em>Karar ve koşullar</em>"]]),
        "<h2>9. Uygulama ve Değişiklik Bağlantıları</h2>", table(["SRÇ.018 Kaydı", "Uygulama Alanı", "Değişiklik / Sürüm", "Uygulama Kanıtı", "Durum"], [["<em>Bağlantı</em>", "<em>Süreç/doküman/araç</em>", "<em>Değişiklik veya sürüm</em>", "<em>Kanıt</em>", "<em>Durum</em>"]]),
        "<h2>10. Sonuç Doğrulama</h2>", table(["Hedef / Ölçüt", "Gerçekleşen Sonuç", "Kanıt", "SRÇ.018 Değişiklik Gözden Geçirme Kararı", "Takip İhtiyacı"], [["<em>Hedef</em>", "<em>Sonuç</em>", "<em>Kanıt</em>", "<em>Olumlu / Olumsuz / Ek çalışma gerekli</em>", "<em>Takip</em>"]]),
        "<h2>11. Raporlama, Yaygınlaştırma ve Yeniden Kullanım</h2>", table(["Alan", "Karar / Kayıt", "Bağlantı / Kanıt"], [["RPR.001'e Aktarım", "<em>Gerekli / Gerekli değil ve gerekçesi</em>", "<em>Bağlantı</em>"], ["LST.012 Bilgilendirmesi", "<em>Hedef kitle ve kanal</em>", "<em>Bağlantı</em>"], ["Yeniden Kullanım", "<em>Diğer süreçler için karar ve gerekçe</em>", "<em>Yeni SRÇ.018 kayıtları</em>"]]),
        "<h2>12. Sürüm Geçmişi</h2>", table(["Sürüm", "Tarih", "Açıklama", "Hazırlayan / Güncelleyen", "Gözden Geçiren", "Onay"], [["<em>v0.1</em>", "<em>GG-AA-YYYY</em>", "<em>İlk taslak</em>", PREPARED_BY, "<em>Rol / kişi</em>", "<em>Rol / kişi</em>"]]),
    ])


def _replace_section(doc: str, heading: str, new_content: str) -> str:
    matches = list(re.finditer(r"<h2[^>]*>(.*?)</h2>", doc, flags=re.I | re.S))
    for i, match in enumerate(matches):
        plain = html.unescape(re.sub(r"<[^>]+>", "", match.group(1))).strip()
        if plain == heading:
            end = matches[i + 1].start() if i + 1 < len(matches) else len(doc)
            return doc[:match.end()] + new_content + doc[end:]
    raise RuntimeError(f"RPR.001 section not found: {heading}")


def updated_report_body() -> str:
    doc = report_body()
    doc = doc.replace("Şu aşamada SRÇ.001, SRÇ.004 ve SRÇ.005 değerlendirmeleri rapora alınmıştır.", "Şu aşamada SRÇ.001, SRÇ.004, SRÇ.005 ve SRÇ.006 değerlendirmeleri rapora alınmıştır.")
    doc = doc.replace("SRÇ.018 SUP.10.BP9 gözden geçirmesiyle", "SRÇ.018 değişiklik gözden geçirmesiyle")
    doc = doc.replace("SUP.10.BP9 gözden geçirmesi", "SRÇ.018 değişiklik gözden geçirmesi")
    doc = doc.replace("SUP.10.BP9 sonucu", "SRÇ.018 değişiklik gözden geçirme sonucu")
    doc = _replace_section(doc, "4. Süreç Sonuç Özeti", table(["Süreç", "Değerlendirme Kapsamı", "BP Dağılımı", "PA / GP Dağılımı", "Değerlendirme Bağlantısı", "Özet"], [
        ["İÜC.BİDB.SRÇ.001 - Dokümantasyon Süreci", "SUP.7 BP1-BP8; PA 2.1-PA 3.2", "5 VAR; 3 DAĞINIK", "9 VAR; 9 DAĞINIK; 3 ZAYIF", "İÜC.BİDB.FRM.001 - Süreç Gözden Geçirme Formu (İÜC.BİDB.SRÇ.001) - Değerlendirme #1", "Doküman standartları, şablonlar ve teknik yayın/bakım yapısı güçlü; formal gözden geçirme, gerçek ölçüm, yetkinlik ve bilgilendirme kanıtları geliştirilmelidir."],
        ["İÜC.BİDB.SRÇ.004 - Süreç Kurulumu Süreci", "PIM.1 BP1-BP6; PA 2.1-PA 3.2", "4 VAR; 1 DAĞINIK; 1 YOK", "10 VAR; 7 DAĞINIK; 1 ZAYIF; 3 YOK", "İÜC.BİDB.FRM.001 - Süreç Gözden Geçirme Formu (İÜC.BİDB.SRÇ.004) - Değerlendirme #1", "Süreç mimarisi, süreç paketleri, uyarlama, rol ve ölçüm tanımları güçlü; gerçek kullanım/performans, bilgilendirme ve yetkinlik kanıtları eksiktir."],
        ["İÜC.BİDB.SRÇ.005 - Süreç Değerlendirme Süreci", "PIM.2 BP1-BP8; PA 2.1-PA 3.2", "6 VAR; 2 DAĞINIK", "11 VAR; 7 DAĞINIK; 2 ZAYIF; 1 YOK", "İÜC.BİDB.FRM.001 - Süreç Gözden Geçirme Formu (İÜC.BİDB.SRÇ.005) - Değerlendirme #1", "Değerlendirme yöntemi, plan, etiketler, iş ürünleri ve kümülatif raporlama tanımlı; gerçek dönem taahhütleri, doğrulama, eğitim ve ilk performans sonuçları tamamlanmalıdır."],
        [SRC006, "PIM.3 BP1-BP9; PA 2.1-PA 3.2", "4 VAR; 2 DAĞINIK; 3 ZAYIF", "11 VAR; 7 DAĞINIK; 2 ZAYIF; 1 YOK", "İÜC.BİDB.FRM.001 - Süreç Gözden Geçirme Formu (İÜC.BİDB.SRÇ.006) - Değerlendirme #1", "Tek SRÇ.018 giriş noktası, hedef/öncelik, planlama uyarlaması, yetki, doğrulama, raporlama ve yeniden kullanım tanımlı; gerçek kaynak, uygulama, doğrulanmış sonuç, iletişim ve yeniden kullanım kanıtları beklenmektedir."],
    ]))
    doc = _replace_section(doc, "5. Etiket Dağılımları ve Eğilimler", table(["Gösterge", "SRÇ.001", "SRÇ.004", "SRÇ.005", "SRÇ.006", "Yorum"], [
        ["BP - VAR", "5", "4", "6", "4", "Tanım, yöntem ve yönetişim bileşenleri oluşturulan alanlarda güçlü karşılama vardır."],
        ["BP - DAĞINIK", "3", "1", "2", "2", "Gerçek kaynak taahhüdü, uygulama veya formal doğrulama kanıtları henüz sistematik değildir."],
        ["BP - ZAYIF", "0", "0", "0", "3", "SRÇ.006 doğrulama, iletişim ve yeniden kullanım kuralları tanımlı olmakla birlikte gerçek sonuç henüz oluşmamıştır."],
        ["BP - YOK", "0", "1", "0", "0", "SRÇ.004 kullanım verisi henüz oluşmamıştır."],
        ["PA/GP - VAR", "9", "10", "11", "11", "Tanım, rol, iş ürünü, etkileşim ve altyapı bileşenleri güçlenmektedir."],
        ["PA/GP - DAĞINIK", "9", "7", "7", "7", "Uygulama kanıtları ve formal kayıt bütünlüğü ortak gelişim alanıdır."],
        ["PA/GP - ZAYIF", "3", "1", "2", "2", "Performans ayarlama ve gerçek veri analizi başlangıç düzeyindedir."],
        ["PA/GP - YOK", "0", "3", "1", "1", "Yetkinlik/eğitim ve bazı gerçek kullanım kanıtları eksiktir."],
    ]))
    from update_rpr001_layout_and_maturity_placeholder import align_rpr001_layout
    return align_rpr001_layout(doc)


def _update_parent_children_count(parent: Path) -> None:
    index = yaml.safe_load(INDEX_PATH.read_text(encoding="utf-8")) or {}
    pages = index.get("pages", [])
    meta_path = parent / "page.yaml"
    meta = yaml.safe_load(meta_path.read_text(encoding="utf-8")) or {}
    stable = str(meta.get("page_id") or f"local:{meta.get('relative_path')}")
    meta["children_count"] = sum(1 for page in pages if str(page.get("parent_id") or "") == stable)
    meta_path.write_text(yaml.safe_dump(meta, allow_unicode=True, sort_keys=False), encoding="utf-8")


def update_lst006_statuses() -> None:
    """Mark the locally completed PIM.2/PIM.3 process packages active."""
    updates = {
        "İÜC.BİDB.SRÇ.005": (
            PROCESS_OWNER,
            "Aktif",
            "Süreç paketi oluşturulmuş, Confluence'ta yayımlanmış ve süreç özel kayıtlarıyla yönetilmektedir.",
        ),
        "İÜC.BİDB.SRÇ.006": (
            PROCESS_OWNER,
            "Aktif",
            "Süreç paketi oluşturulmuş, Confluence'ta yayımlanmış ve süreç özel kayıtlarıyla yönetilmektedir.",
        ),
    }
    page_dir = CONFLUENCE / LST006_REL
    for filename in ("body.storage.xhtml", "body.view.html"):
        path = page_dir / filename
        content = path.read_text(encoding="utf-8")

        def replace_row(match: re.Match[str]) -> str:
            row = match.group(0)
            plain = html.unescape(re.sub(r"<[^>]+>", "", row))
            code = next((item for item in updates if item in plain), None)
            if not code:
                return row
            values = updates[code]
            cell_index = -1

            def replace_cell(cell_match: re.Match[str]) -> str:
                nonlocal cell_index
                cell_index += 1
                if cell_index not in (4, 5, 6):
                    return cell_match.group(0)
                return f"{cell_match.group(1)}{html.escape(values[cell_index - 4])}{cell_match.group(3)}"

            return re.sub(r"(<td[^>]*>)(.*?)(</td>)", replace_cell, row, flags=re.I | re.S)

        updated = re.sub(r"<tr[^>]*>.*?</tr>", replace_row, content, flags=re.I | re.S)
        for code, (owner, status, note) in updates.items():
            plain_updated = html.unescape(re.sub(r"<[^>]+>", "", updated))
            if code not in plain_updated or owner not in plain_updated or status not in plain_updated or note not in plain_updated:
                raise RuntimeError(f"LST.006 status update failed for {code} in {filename}")
        path.write_text(updated, encoding="utf-8")


def validate(page_dirs: list[Path]) -> None:
    process = (CONFLUENCE / SRC006_REL / "body.storage.xhtml").read_text(encoding="utf-8")
    headings = [html.unescape(re.sub(r"<[^>]+>", "", item)) for item in re.findall(r"<h2[^>]*>(.*?)</h2>", process, flags=re.S)]
    expected = ["1. Süreç Bilgileri", "2. Amaç", "3. Kapsam", "4. Referanslar", "5. Terimler ve Kısaltmalar", "6. Süreç Aktivitesi", "7. Roller ve Sorumluluklar", "8. Araçlar ve Altyapı", "9. Süreç İş Ürünleri", "10. Süreç Akışı", "11. Süreç Faaliyetleri", "12. Ölçüm ve İzleme", "13. Uygulama ve Uyarlama Kuralları", "14. Süreç Etkileşimleri", "15. Sürüm Geçmişi"]
    if headings != expected:
        raise RuntimeError(f"SRÇ.006 heading mismatch: {headings}")
    reference = process.split("<h2>4. Referanslar</h2>", 1)[1].split("<h2>5.", 1)[0]
    if len(re.findall(r"<tr>", reference)) != 4:
        raise RuntimeError("SRÇ.006 must have exactly three process references")
    forbidden = ["26 süreç", "LST.004", "Soru Bankası", "SUP.10.BP9"]
    if any(term in process for term in forbidden):
        raise RuntimeError("SRÇ.006 contains a forbidden fixed count, legacy/project name or technical SUP.10.BP9 wording")
    for bp, _, _ in PIM3_BPS:
        if bp not in process:
            raise RuntimeError(f"Missing BP trace: {bp}")
    if process.count("İlgili Süreçler") != 1 or "<br />" not in process.split("İlgili Süreçler", 1)[1]:
        raise RuntimeError("Related processes are not listed on separate lines")
    for page_dir in page_dirs:
        for filename in ["page.yaml", "body.storage.xhtml", "body.view.html"]:
            if not (page_dir / filename).exists():
                raise RuntimeError(f"Missing page artifact: {page_dir / filename}")
    assessment = (CONFLUENCE / REVIEWS_REL / "iuc-bidb-frm-001-surec-gozden-gecirme-formu-iuc-bidb-src-006-degerlendirme-1/body.storage.xhtml").read_text(encoding="utf-8")
    if "4 VAR, 2 DAĞINIK ve 3 ZAYIF" not in assessment or "Toplam puan" not in assessment:
        raise RuntimeError("SRÇ.006 assessment summary is inconsistent")
    report = (CONFLUENCE / REPORTS_REL / "iuc-bidb-rpr-001-surec-performanslari-raporu/body.storage.xhtml").read_text(encoding="utf-8")
    if SRC006 not in report or "SRÇ.018 değişiklik gözden geçirmesiyle" not in report:
        raise RuntimeError("RPR.001 was not updated for SRÇ.006/corporate review wording")


def write_report() -> None:
    path = Path(__file__).resolve().parents[1] / "reports/src006_process_improvement_package_report.md"
    path.write_text("""# SRÇ.006 Süreç İyileştirme Paketi Yerel Raporu

Tarih: 14-07-2026

## Oluşturulan / Güncellenen Yapı

- SRÇ.006 süreç tanımı PIM.3 amacı, yedi sonucu ve BP1-BP9 izlenebilirliğiyle oluşturuldu.
- Süreç özel LST.007, LST.008, LST.009, LST.010 ve boş FRM.001 aktif şablon yapılarına göre oluşturuldu.
- SRÇ.006 Değerlendirme #1 aynı kayıt ve yalnız etiket yaklaşımıyla oluşturuldu.
- PLN.002.Ş Süreç İyileştirme Planı Şablonu oluşturuldu; gerçek plan yalnızca uyarlama koşulu oluştuğunda hazırlanacaktır.
- PRS.004, SRÇ.006 ile SRÇ.018 arasında ortak uygulama prosedürü olarak referanslandı.
- RPR.001 kümülatif raporuna SRÇ.006 sonucu eklendi.

## Görsel Doğrulama

- SRÇ.006 süreç akışı ve LST.007 etkileşim diyagramı için Mermaid kaynakları oluşturuldu.
- Her iki sayfada üstte PNG, altta Mermaid kaynak kodu düzeni korunmaktadır.

## Yayın Durumu

- Paket 15-07-2026 tarihinde kontrollü dry-run sonrasında Confluence'a yayımlanmıştır.
- SRÇ.006 süreci, süreç özel destek dokümanları, PRS.004, PLN.002.Ş, RPR.001/RPR.001.Ş güncellemeleri, merkezi kayıtlar ve Değerlendirme #1 dahil 16 sayfa canlı olarak doğrulanmıştır.
- Süreç akış ve LST.007 etkileşim PNG ekleri Confluence üzerinde boyut ve görünüm açısından doğrulanmıştır.
- Yayın LST.012 altında gerçek Confluence bağlantısıyla kaydedilmiştir.
""", encoding="utf-8")


def main() -> None:
    src_dir = CONFLUENCE / SRC006_REL
    attachments = src_dir / "attachments"
    attachments.mkdir(parents=True, exist_ok=True)
    (attachments / FLOW_MMD).write_text("\n".join(FLOW_LINES) + "\n", encoding="utf-8")
    write_page(src_dir, SRC006, "137265784", "01 - Süreç Dokümanları", 2, process_body(True), process_body(False))

    pages: list[Path] = [src_dir]
    children = [
        ("iuc-bidb-lst-007-surec-etkilesim-matrisi-iuc-bidb-src-006", "İÜC.BİDB.LST.007 - Süreç Etkileşim Matrisi (İÜC.BİDB.SRÇ.006)", lst007_body(True), lst007_body(False)),
        ("iuc-bidb-lst-008-is-urunleri-ve-kalite-kriterleri-listesi-iuc-bidb-src-006", "İÜC.BİDB.LST.008 - İş Ürünleri ve Kalite Kriterleri Listesi (İÜC.BİDB.SRÇ.006)", lst008_body(), None),
        ("iuc-bidb-lst-009-surec-performans-olcum-seti-iuc-bidb-src-006", "İÜC.BİDB.LST.009 - Süreç Performans Ölçüm Seti (İÜC.BİDB.SRÇ.006)", lst009_body(), None),
        ("iuc-bidb-lst-010-surec-rol-yetki-ve-raci-matrisi-iuc-bidb-src-006", "İÜC.BİDB.LST.010 - Süreç Rol Yetki ve RACI Matrisi (İÜC.BİDB.SRÇ.006)", lst010_body(), None),
    ]
    for slug, title, storage, view in children:
        page_dir = src_dir / slug
        write_page(page_dir, title, SRC006_ID, SRC006, 3, storage, view)
        pages.append(page_dir)
        if "lst-007" in slug:
            child_attachments = page_dir / "attachments"
            child_attachments.mkdir(exist_ok=True)
            (child_attachments / INTERACTION_MMD).write_text("\n".join(INTERACTION_LINES) + "\n", encoding="utf-8")

    blank_dir = src_dir / "iuc-bidb-frm-001-surec-gozden-gecirme-formu-iuc-bidb-src-006"
    write_page(blank_dir, "İÜC.BİDB.FRM.001 - Süreç Gözden Geçirme Formu (İÜC.BİDB.SRÇ.006)", SRC006_ID, SRC006, 3, blank_review_body())
    pages.append(blank_dir)

    assessment_dir = CONFLUENCE / REVIEWS_REL / "iuc-bidb-frm-001-surec-gozden-gecirme-formu-iuc-bidb-src-006-degerlendirme-1"
    write_page(assessment_dir, "İÜC.BİDB.FRM.001 - Süreç Gözden Geçirme Formu (İÜC.BİDB.SRÇ.006) - Değerlendirme #1", REVIEWS_ID, "Süreç Gözden Geçirmeleri", 3, assessment_body())
    pages.append(assessment_dir)

    template_dir = CONFLUENCE / TEMPLATES_REL / PLN002_TEMPLATE_SLUG
    write_page(template_dir, PLN002_TEMPLATE_TITLE, TEMPLATES_ID, "02 - Şablonlar", 2, pln002_template_body())
    pages.append(template_dir)

    templates_dir = PAGE_ROOT / "02-sablonlar"
    template_register = template_register_body()
    (templates_dir / "body.storage.xhtml").write_text(template_register + "\n", encoding="utf-8")
    (templates_dir / "body.view.html").write_text(build_view("02 - Şablonlar", template_register), encoding="utf-8")
    pages.append(templates_dir)

    lst001_dir = PAGE_ROOT / "03-kayitlar-ve-listeler/iuc-bidb-lst-001-aktif-dokumanlar-listesi"
    lst001_storage = update_lst001((lst001_dir / "body.storage.xhtml").read_text(encoding="utf-8"))
    (lst001_dir / "body.storage.xhtml").write_text(lst001_storage, encoding="utf-8")
    (lst001_dir / "body.view.html").write_text(build_view("İÜC.BİDB.LST.001 - Aktif Dokümanlar Listesi", lst001_storage), encoding="utf-8")
    pages.append(lst001_dir)

    rpr_dir = CONFLUENCE / REPORTS_REL / "iuc-bidb-rpr-001-surec-performanslari-raporu"
    write_page(rpr_dir, RPR001, str((yaml.safe_load((rpr_dir / "page.yaml").read_text(encoding="utf-8")) or {}).get("parent_id") or ""), "09 - Raporlar", 2, updated_report_body())
    pages.append(rpr_dir)

    update_lst006_statuses()

    upsert_index(pages)
    _update_parent_children_count(src_dir)
    _update_parent_children_count(CONFLUENCE / REVIEWS_REL)
    _update_parent_children_count(templates_dir)
    validate(pages)
    write_report()
    print("[PASS] SRÇ.006 süreç iyileştirme paketi yerelde oluşturuldu.")


if __name__ == "__main__":
    main()
