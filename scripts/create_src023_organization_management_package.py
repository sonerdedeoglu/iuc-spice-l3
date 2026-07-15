#!/usr/bin/env python3
"""Create the local SRÇ.023 organization-management package.

This script is local-only and never calls Confluence APIs. Existing page ids are
preserved; new page ids remain empty until a reviewed publish.
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
    REPORTS_REL,
    REVIEWS_ID,
    REVIEWS_REL,
    TEMPLATES_ID,
    TEMPLATES_REL,
    build_view,
    history,
    info_macro,
    info_view,
    p,
    parent_register_body,
    table,
    write_page,
)
from align_lst010_to_src006_structure import process_body as raci_body


ROOT = Path(__file__).resolve().parents[1]
SRC023_ID = "137265881"
SRC023 = "SRÇ.023 - Organizasyonel Yönetim Süreci"
PRS006 = "PRS.006 - Organizasyonel Yönetim Prosedürü"
FRM002_TEMPLATE = "FRM.002.Ş - Toplantı Tutanağı Şablonu"
LST013 = "LST.013 - Görev Tanımları ve Görevli Personel Listesi"
LST013_TEMPLATE = "LST.013.Ş - Görev Tanımları ve Görevli Personel Listesi Şablonu"
OWNER = "Mustafa Nusret SARISAKAL - Bilgi İşlem Daire Başkanı"
REVIEWER = "Seçil NEBİLER - İdari İşler Şube Müdürü"
APPROVER = "Mustafa Nusret SARISAKAL - Bilgi İşlem Daire Başkanı"
OFFICIAL_3411 = '<a href="https://cdn.iuc.edu.tr/FileHandler2.ashx?f=341.1pr_bidb-genel-isleyis-proseduru-ve-ekleri-elektronik-nusha-rev.04.pdf">341.1PR - Bilgi İşlem Daire Başkanlığı Genel İşleyiş Prosedürü (Rev.04, 11.06.2025)</a>'
OFFICIAL_ROLE_PAGE_URL = "https://bilgiislem.iuc.edu.tr/tr/content/gorev-tanimlari/gorev-tanimlari"
OFFICIAL_PERSONNEL_BASE_URL = "https://bilgiislem.iuc.edu.tr/tr/content/personelimiz"
OFFICIAL_MANAGEMENT_PAGE_URL = "https://bilgiislem.iuc.edu.tr/tr/content/yonetim/yonetim"

SRC023_REL = f"{PAGE_ROOT_REL}/01-surec-dokumanlari/src-023-organizasyonel-yonetim-sureci"
RECORDS_REL = f"{PAGE_ROOT_REL}/03-kayitlar-ve-listeler"
LST001_REL = f"{RECORDS_REL}/lst-001-aktif-dokumanlar-listesi"
LST006_REL = f"{RECORDS_REL}/lst-006-standart-surec-envanteri"
LST013_REL = f"{RECORDS_REL}/lst-013-gorev-tanimlari-ve-gorevli-personel-listesi"
RPR001_REL = f"{REPORTS_REL}/rpr-001-surec-performanslari-raporu"

ROLE_DEFINITIONS = [
    ("311.6-341.1GT / Rev.02", "Bilgi İşlem Daire Başkanı", "Başkanlık", "https://cdn.iuc.edu.tr/FileHandler2.ashx?f=311.6-341.1gt_bidb-daire-baskani-gt-rev.02_40581397.pdf"),
    ("311.6-341.2GT / Rev.03", "Yönetici Sekreteri", "Başkanlık Sekreterliği", "https://cdn.iuc.edu.tr/FileHandler2.ashx?f=311.6-341.2gt_bidb-yonetici-sekreteri-gt-rev.03_40581398.pdf"),
    ("311.6-341.3GT / Rev.04", "İdari İşler Şube Müdürü", "İdari İşler Şube Müdürlüğü", "https://cdn.iuc.edu.tr/FileHandler2.ashx?f=311.6-341.3gt_bidb-idari-isler-sube-muduru-gt-rev.04_40581399.pdf"),
    ("311.6-341.4GT / Rev.01", "Yazı İşleri Personeli", "İdari İşler Şube Müdürlüğü", "https://cdn.iuc.edu.tr/FileHandler2.ashx?f=311.6-341.4gt_bidb-yazi-isleri-personeli-gt-rev.01_40581400.pdf"),
    ("311.6-341.5GT / Rev.02", "Santral Operatör Personeli", "İdari İşler Şube Müdürlüğü", "https://cdn.iuc.edu.tr/FileHandler2.ashx?f=311.6-341.5gt_bidb-santral-operator-personeli-gt-rev.02_40581401.pdf"),
    ("311.6-341.6GT / Rev.01", "Kalite Personeli", "İdari İşler Şube Müdürlüğü", "https://cdn.iuc.edu.tr/FileHandler2.ashx?f=311.6-341.6gt_bidb-kalite-personeli-gt-rev.01_40581402.pdf"),
    ("311.6-341.7GT / Rev.04", "Mali İşler Şube Müdürü", "Mali İşler Şube Müdürlüğü", "https://cdn.iuc.edu.tr/FileHandler2.ashx?f=311.6-341.7gt_bidb-mali-isler-sube-muduru-gt-rev.04_40581403.pdf"),
    ("311.6-341.8GT / Rev.02", "Satınalma Personeli", "Mali İşler Şube Müdürlüğü", "https://cdn.iuc.edu.tr/FileHandler2.ashx?f=311.6-341.8gt_bidb-satin-alma-personeli-gt-rev.02_40581404.pdf"),
    ("311.6-341.9GT / Rev.02", "Taşınır Kayıt Yetkilisi", "Mali İşler Şube Müdürlüğü", "https://cdn.iuc.edu.tr/FileHandler2.ashx?f=311.6-341.9gt_bidb-tasinir-kayit-yetkilisi-gt-rev.02_40581405.pdf"),
    ("311.6-341.10GT / Rev.02", "Taşınır Kontrol Yetkilisi", "Mali İşler Şube Müdürlüğü", "https://cdn.iuc.edu.tr/FileHandler2.ashx?f=311.6-341.10gt_bidb-tasinir-kontrol-yetkilisi-gt-rev.02_40581406.pdf"),
    ("311.6-341.11GT / Rev.03", "Maaş İşleri Personeli", "Mali İşler Şube Müdürlüğü", "https://cdn.iuc.edu.tr/FileHandler2.ashx?f=311.6-341.11gt_bidb-maas-isleri-personeli-gt-rev.03_40581407.pdf"),
    ("311.6-341.12GT / Rev.04", "Proje Yöneticisi", "Proje Geliştirme Yönetimi", "https://cdn.iuc.edu.tr/FileHandler2.ashx?f=311.6-341.12gt_bidb-proje-yoneticisi-gt-rev.04_40581408.pdf"),
    ("311.6-341.14GT / Rev.04", "Veri Tabanı Yöneticisi", "Proje Geliştirme Yönetimi", "https://cdn.iuc.edu.tr/FileHandler2.ashx?f=311.6-341.14gt_bidb-veri-tabani-yoneticisi-gt-rev.04_40581410.pdf"),
    ("311.6-341.28GT / Rev.01", "Veri Tabanı Uzmanı", "Proje Geliştirme Yönetimi", "https://cdn.iuc.edu.tr/FileHandler2.ashx?f=311.6-341.28gt_bidb-veri-tabani-uzmani-gt-rev.01_40581424.pdf"),
    ("311.6-341.31GT", "Veri Tabanı Analisti", "Proje Geliştirme Yönetimi", "https://cdn.iuc.edu.tr/FileHandler2.ashx?f=311.6-341.31gt_bidb-veri-tabani-analisti-gt_40581427.pdf"),
    ("311.6-341.13GT / Rev.02", "Yazılım Geliştirme Uzmanı", "Proje Geliştirme Yönetimi", "https://cdn.iuc.edu.tr/FileHandler2.ashx?f=311.6-341.13gt_bidb-yazilim-gelistirme-uzmani-gt-rev.02_40581409.pdf"),
    ("311.6-341.32GT", "Yazılım Uygulama ve Destek Elemanı", "Proje Geliştirme Yönetimi", "https://cdn.iuc.edu.tr/FileHandler2.ashx?f=311.6-341.32gt_bidb-yazilim-uygulama-ve-destek-elemani-gt_40581428.pdf"),
    ("311.6-341.16GT / Rev.02", "Yazılım/Program Analisti", "Proje Geliştirme Yönetimi", "https://cdn.iuc.edu.tr/FileHandler2.ashx?f=311.6-341.16gt_bidb-yazilim-program-analisti-gt-rev.02_40581412.pdf"),
    ("311.6-341.30GT", "Yazılım Test Edicisi", "Proje Geliştirme Yönetimi", "https://cdn.iuc.edu.tr/FileHandler2.ashx?f=311.6-341.30gt_bidb-yazilim-test-analisti-gt_40581426.pdf"),
    ("311.6-341.18GT / Rev.03", "Ağ, Sistem ve Güvenlik Yöneticisi", "Ağ, Sistem ve Güvenlik Yönetimi", "https://cdn.iuc.edu.tr/FileHandler2.ashx?f=311.6-341.18gt_bidb-ag,-sistem-ve-guvenlik-yoneticisi-gt-rev.03_40581414.pdf"),
    ("311.6-341.19GT / Rev.01", "Ağ Uzmanı", "Ağ, Sistem ve Güvenlik Yönetimi", "https://cdn.iuc.edu.tr/FileHandler2.ashx?f=311.6-341.19gt_bidb-ag-uzmani-gt-rev.01_40581415.pdf"),
    ("311.6-341.29GT / Rev.01", "Siber Güvenlik Uzmanı", "Ağ, Sistem ve Güvenlik Yönetimi", "https://cdn.iuc.edu.tr/FileHandler2.ashx?f=311.6-341.29gt_bidb-siber-guvenlik-uzmani-gt-rev.01_40581425.pdf"),
    ("311.6-341.20GT / Rev.01", "Sistem ve Güvenlik Uzmanı", "Ağ, Sistem ve Güvenlik Yönetimi", "https://cdn.iuc.edu.tr/FileHandler2.ashx?f=311.6-341.20gt_bidb-sistem-ve-guvenlik-uzmani-gt-rev.01_40581416.pdf"),
    ("311.6-341.15GT / Rev.06", "İş Geliştirme Yöneticisi", "İş Geliştirme Yönetimi", "https://cdn.iuc.edu.tr/FileHandler2.ashx?f=311.6-341.15gt_bidb-is-gelistirme-yoneticisi-gt-rev.06_40581411.pdf"),
    ("311.6-341.17GT / Rev.02", "İş Geliştirme Destek Personeli", "İş Geliştirme Yönetimi", "https://cdn.iuc.edu.tr/FileHandler2.ashx?f=311.6-341.17gt_bidb-is-gelistirme-destek-personeli-gt-rev.02_40581413.pdf"),
    ("311.6-341.25GT / Rev.04", "E-Kart Destek Personeli", "İş Geliştirme Yönetimi", "https://cdn.iuc.edu.tr/FileHandler2.ashx?f=311.6-341.25gt_bidb-e-kart-destek-personeli-gt-rev.04_40581421.pdf"),
    ("311.6-341.26GT / Rev.03", "Web/E-Posta Destek Personeli", "İş Geliştirme Yönetimi", "https://cdn.iuc.edu.tr/FileHandler2.ashx?f=311.6-341.26gt_bidb-web-e-posta-destek-personeli-gt-rev.03_40581422.pdf"),
    ("311.6-341.21GT / Rev.03", "Teknik Hizmetler Yöneticisi", "Teknik Hizmetler Yönetimi", "https://cdn.iuc.edu.tr/FileHandler2.ashx?f=311.6-341.21gt_bidb-teknik-hizmetler-yoneticisi-gt-rev.03_40581417.pdf"),
    ("311.6-341.22GT / Rev.03", "Donanım Destek Personeli", "Teknik Hizmetler Yönetimi", "https://cdn.iuc.edu.tr/FileHandler2.ashx?f=311.6-341.22gt_bidb-donanim-destek-personeli-gt-rev.03_40581418.pdf"),
    ("311.6-341.23GT / Rev.02", "Ağ ve Sistem Destek Birim Sorumlusu", "Teknik Hizmetler Yönetimi", "https://cdn.iuc.edu.tr/FileHandler2.ashx?f=311.6-341.23gt_bidb-ag-ve-sistem-destek-birim-sorumlusu-gt-rev.02_40581419.pdf"),
    ("311.6-341.24GT / Rev.01", "Ağ ve Sistem Destek Personeli", "Teknik Hizmetler Yönetimi", "https://cdn.iuc.edu.tr/FileHandler2.ashx?f=311.6-341.24gt_bidb-ag-ve-sistem-destek-personeli-gt-rev.01_40581420.pdf"),
    ("311.6-341.27GT / Rev.01", "Yardımcı Hizmetler Personeli", "Başkanlık Sekreterliği", "https://cdn.iuc.edu.tr/FileHandler2.ashx?f=311.6-341.27gt_bidb-yardimci-hizmetler-personeli-gt-rev.01_40581423.pdf"),
]

PERSONNEL_BY_ROLE = {
    "Bilgi İşlem Daire Başkanı": [("Mustafa Nusret SARISAKAL", "https://profil.iuc.edu.tr/tr/p/nsarisakal")],
    "İdari İşler Şube Müdürü": [("Seçil NEBİLER", "https://profil.iuc.edu.tr/tr/p/secil.nebiler")],
    "Yazı İşleri Personeli": [("Seda TOPALKARA", "https://profil.iuc.edu.tr/tr/p/seda.topalkara")],
    "Santral Operatör Personeli": [
        ("Bülent AKBABA", "https://profil.iuc.edu.tr/tr/p/bulent.akbaba"),
        ("Ahmet ÇANAKÇI", "https://profil.iuc.edu.tr/tr/p/ahmet.canakci"),
        ("Nesrin AKKUŞ", "https://profil.iuc.edu.tr/tr/p/nesrin.akkus"),
        ("İlyas KARTAL", "https://profil.iuc.edu.tr/tr/p/ilyas.kartal"),
        ("Melisa AKBUDAK", "https://profil.iuc.edu.tr/tr/p/melisa.akbudak"),
    ],
    "Kalite Personeli": [("Ayşe DEMİRTAŞ", "https://profil.iuc.edu.tr/tr/p/ayse.demirtas")],
    "Mali İşler Şube Müdürü": [("Emine TREN", "https://profil.iuc.edu.tr/tr/p/emine.tren")],
    "Satınalma Personeli": [
        ("Semih İSMAİLOĞLU", "https://profil.iuc.edu.tr/tr/p/semih.ismailoglu"),
        ("Kader KESKİN", "https://profil.iuc.edu.tr/tr/p/kader.keskin"),
    ],
    "Taşınır Kayıt Yetkilisi": [
        ("Semih İSMAİLOĞLU", "https://profil.iuc.edu.tr/tr/p/semih.ismailoglu"),
        ("Kader KESKİN", "https://profil.iuc.edu.tr/tr/p/kader.keskin"),
        ("İhsan YILDIZ", "https://profil.iuc.edu.tr/tr/p/ihsan.yildiz"),
    ],
    "Taşınır Kontrol Yetkilisi": [("Emine TREN", "https://profil.iuc.edu.tr/tr/p/emine.tren")],
    "Proje Yöneticisi": [("Levent BAYEZİT", "https://profil.iuc.edu.tr/tr/p/levent")],
    "Veri Tabanı Yöneticisi": [("Turan Turgay GÖRGEL", "https://profil.iuc.edu.tr/tr/p/turgaygorgel")],
    "Veri Tabanı Uzmanı": [("Serhat KOÇAK", "https://profil.iuc.edu.tr/tr/p/serhat.kocak")],
    "Veri Tabanı Analisti": [("Nazım KÜÇÜK", "https://profil.iuc.edu.tr/tr/p/nazim.kucuk")],
    "Yazılım Geliştirme Uzmanı": [
        ("Meltem ACAR TORUN", "https://profil.iuc.edu.tr/tr/p/meltemacar"),
        ("Bayram BAŞDUVAR", "https://profil.iuc.edu.tr/tr/p/bayrambasduvar"),
        ("Halit AYAZ", "https://profil.iuc.edu.tr/tr/p/halit.ayaz"),
        ("Sezgin MARAL", "https://profil.iuc.edu.tr/tr/p/sezgin.maral"),
        ("Recep YAYLA", "https://profil.iuc.edu.tr/tr/p/recep.yayla"),
        ("Seda YEGİN", "https://profil.iuc.edu.tr/tr/p/seda.yegin"),
        ("Betül ÜNVER KULAKAÇ", "https://profil.iuc.edu.tr/tr/p/betul.kulakac"),
        ("Muhammed Zahid CİNİSLİ", "https://profil.iuc.edu.tr/tr/p/muhammed.cinisli"),
    ],
    "Yazılım Uygulama ve Destek Elemanı": [
        ("Sozda EKİN", "https://profil.iuc.edu.tr/tr/p/sozda.ekin"),
        ("Ceren ARDUÇ", "https://profil.iuc.edu.tr/tr/p/ceren.arduc"),
        ("Tuğçe ÇINAR", "https://profil.iuc.edu.tr/tr/p/tugce.cinar"),
        ("Derya TUNALIER", "https://profil.iuc.edu.tr/tr/p/derya.tunalier"),
    ],
    "Yazılım/Program Analisti": [
        ("Asel GÜL", "https://profil.iuc.edu.tr/tr/p/asel.gul"),
        ("Gülay ASLANCA", "https://profil.iuc.edu.tr/tr/p/gulay.aslanca"),
        ("Hatice ATASOY", "https://profil.iuc.edu.tr/tr/p/hatice.atasoy"),
        ("Hasret KESKİN", "https://profil.iuc.edu.tr/tr/p/hasret.keskin"),
        ("Usame GÜMÜŞ", "https://profil.iuc.edu.tr/tr/p/usame.gumus"),
    ],
    "Yazılım Test Edicisi": [
        ("Gülşah AKMAN", "https://profil.iuc.edu.tr/tr/p/gulsah.akman"),
        ("Ebru KARACA EREN", "https://profil.iuc.edu.tr/tr/p/ebru.karaca"),
    ],
    "Ağ, Sistem ve Güvenlik Yöneticisi": [("Eren BÖRÜ", "https://profil.iuc.edu.tr/tr/p/eren")],
    "Ağ Uzmanı": [
        ("İbrahim Halil RAĞBETLİ", "https://profil.iuc.edu.tr/tr/p/halilibrahim"),
        ("Mustafa Recai BİNGÖL", "https://profil.iuc.edu.tr/tr/p/mbingol"),
    ],
    "Siber Güvenlik Uzmanı": [("Berkcan KARABULUT", "https://profil.iuc.edu.tr/tr/p/bkarabulut")],
    "Sistem ve Güvenlik Uzmanı": [
        ("Suat İŞCAN", "https://profil.iuc.edu.tr/tr/p/siscan"),
        ("Murat KAZANÇ", "https://profil.iuc.edu.tr/tr/p/murat.kazanc"),
    ],
    "İş Geliştirme Yöneticisi": [("Akif ÜZEL", "https://profil.iuc.edu.tr/tr/p/akif")],
    "İş Geliştirme Destek Personeli": [
        ("Ahsen AYYILDIZ", "https://profil.iuc.edu.tr/tr/p/ahsen.ayyildiz"),
        ("Merve ERTAŞ ÇİMEN", "https://profil.iuc.edu.tr/tr/p/merveertascimen"),
        ("Alper KARACA", "https://profil.iuc.edu.tr/tr/p/alper.karaca"),
    ],
    "E-Kart Destek Personeli": [
        ("İdris İNAN", "https://profil.iuc.edu.tr/tr/p/idrisinan"),
        ("Alişan YAVUZYİĞİT", "https://profil.iuc.edu.tr/tr/p/alisan.yavuzyigit"),
    ],
    "Web/E-Posta Destek Personeli": [
        ("Atilla EKER", "https://profil.iuc.edu.tr/tr/p/atillaeker"),
        ("Musa YILDIZGÖRER", "https://profil.iuc.edu.tr/tr/p/musa.yildizgorer"),
    ],
    "Teknik Hizmetler Yöneticisi": [("Ali Oğuz CAN", "https://profil.iuc.edu.tr/tr/p/alioguz.can")],
    "Donanım Destek Personeli": [
        ("Ali PAMUKÇU", "https://profil.iuc.edu.tr/tr/p/ali.pamukcu"),
        ("Murat KAYACAN", "https://profil.iuc.edu.tr/tr/p/murat.kayacan"),
        ("Bülent AYGÜN", "https://profil.iuc.edu.tr/tr/p/bulent.aygun"),
        ("Savaş GEYİK", "https://profil.iuc.edu.tr/tr/p/savas.geyik"),
        ("Emin GÜREŞÇİ", "https://profil.iuc.edu.tr/tr/p/emin.guresci"),
    ],
    "Ağ ve Sistem Destek Birim Sorumlusu": [("Güven ALTIN", "https://profil.iuc.edu.tr/tr/p/guven.altin")],
    "Ağ ve Sistem Destek Personeli": [
        ("Erhan ÇAĞLIYAN", "https://profil.iuc.edu.tr/tr/p/erhan.cagliyan"),
        ("Mehmet Nedret GEZEN", "https://profil.iuc.edu.tr/tr/p/mehmetnedret.gezen"),
        ("Bayittin GÜMÜŞAY", "https://profil.iuc.edu.tr/tr/p/bayittin.gumusay"),
        ("Aslıhan ÇELİK", "https://profil.iuc.edu.tr/tr/p/asli"),
        ("Oğuzhan TAŞKAN", "https://profil.iuc.edu.tr/tr/p/oguzhan.taskan"),
        ("Bilal TUTCAN", "https://profil.iuc.edu.tr/tr/p/bilal.tutcan"),
        ("Ercan ŞAHİN", "https://profil.iuc.edu.tr/tr/p/ercan.sahin"),
        ("Mehmet Mahsum ABAYAY", "https://profil.iuc.edu.tr/tr/p/mmabayay"),
    ],
    "Yardımcı Hizmetler Personeli": [("Ahmet Turan GÜNEŞ", "https://profil.iuc.edu.tr/tr/p/ahmet.gunes")],
}

PERSONNEL_SECTION_SLUGS = {
    "Başkanlık": "../yonetim/yonetim",
    "Başkanlık Sekreterliği": "baskanlik-sekreterligi",
    "İdari İşler Şube Müdürlüğü": "idari-isler-sube-mudurlugu",
    "Mali İşler Şube Müdürlüğü": "mali-isler-sube-mudurlugu",
    "Proje Geliştirme Yönetimi": "proje-gelistirme-yonetimi",
    "Ağ, Sistem ve Güvenlik Yönetimi": "ag,-sistem-ve-guvenlik-yonetimi",
    "İş Geliştirme Yönetimi": "is-gelistirme-yonetimi",
    "Teknik Hizmetler Yönetimi": "teknik-hizmetler-yonetimi",
}

FLOW_PNG = "SRÇ.023 - Flowchart.png"
FLOW_MMD = "src023-surec-akisi.mmd"
INTERACTION_PNG = "src023-surec-etkilesim.png"
INTERACTION_MMD = "src023-surec-etkilesim.mmd"

MAN2_BPS = [
    ("MAN.2.BP1", "Yönetim altyapısını belirle", "Kurumsal hedeflerle uyumlu rol, sorumluluk, karar, iletişim, planlama ve izleme altyapısını belirlemek."),
    ("MAN.2.BP2", "Yönetim altyapısını sağla", "Belirlenen yönetim altyapısını kurumun genel yapısı içinde erişilebilir ve kullanılabilir kılmak."),
    ("MAN.2.BP3", "Yönetim uygulamalarını belirle ve uygula", "Etkili süreç ve proje yönetimini destekleyen yönetim uygulamalarını belirlemek ve devreye almak."),
    ("MAN.2.BP4", "Yönetim uygulamalarını yürüt", "Belirlenen yönetim uygulamalarını tanımlı altyapı üzerinde işletmek."),
    ("MAN.2.BP5", "Etkinliği değerlendir", "Yönetim uygulamalarının kurumsal hedeflere ulaşmadaki etkinliğini değerlendirmek."),
    ("MAN.2.BP6", "İyi uygulamaların benimsenmesini destekle", "Etkili yönetim ve iyi uygulamaların benimsenmesini uygun yetki, iletişim ve bilgi yönetimi mekanizmalarıyla desteklemek."),
]

FLOW_LINES = [
    "%%{init: {'flowchart': {'htmlLabels': false}}}%%",
    "flowchart TD",
    'A["Kurumsal hedefler, mevzuat, süreç ve performans girdileri"] --> B["Yönetim altyapısı ve uygulamaları belirlenir"]',
    'B --> C["Kurumsal rol ve yetkiler ile süreç RACI yapıları doğrulanır"]',
    'C --> D["Yönetim uygulamaları süreçlerde yürütülür"]',
    'D --> E["RPR.001, FRM.001 ve doğal yönetim kayıtları hazırlanır"]',
    'E --> F{"Yıllık veya olağanüstü YGG gerekli mi?"}',
    'F -- "Hayır" --> D',
    'F -- "Evet" --> G["YGG girdileri ve gündemi hazırlanır"]',
    'G --> H["YGG gerçekleştirilir ve FRM.002 ile kaydedilir"]',
    'H --> I["Kararlar, sorumlular, hedef tarihler ve takip koordinatörleri atanır"]',
    'I --> J{"Karar türü"}',
    'J -- "Problem veya uygunsuzluk" --> K["SRÇ.017"]',
    'J -- "Değişiklik veya iyileştirme" --> L["SRÇ.018 ve gerekirse SRÇ.006"]',
    'J -- "Eğitim, altyapı, değerlendirme veya bilgi" --> M["İlgili destek süreci"]',
    'K --> N["Uygulama sonucu ve kanıt bağlantısı güncellenir"]',
    'L --> N',
    'M --> N',
    'N --> O["Takip koordinatörü sonucu doğrular ve aksiyonu kapatır"]',
    'O --> P["Açık aksiyonlar sonraki YGG girdisi olur"]',
    'P --> D',
]

INTERACTION_LINES = [
    "%%{init: {'flowchart': {'htmlLabels': false}}}%%",
    "flowchart LR",
    'A["341.1PR, organizasyon şeması ve görev tanımları"] --> Y["SRÇ.023 Organizasyonel Yönetim"]',
    'B["LST.006 Standart Süreç Envanteri"] --> Y',
    'C["RPR.001 ve FRM.001 değerlendirme sonuçları"] --> Y',
    'D["Kalite, müşteri, denetim, risk ve performans girdileri"] --> Y',
    'E["Proje sonuçları, öğrenilmiş dersler ve paydaş geri bildirimleri"] --> Y',
    'Y --> F["PRS.006 Organizasyonel Yönetim Prosedürü"]',
    'Y --> G["FRM.002 YGG Toplantı Tutanağı"]',
    'G --> H["SRÇ.017 Problem Çözüm"]',
    'G --> I["SRÇ.018 Değişiklik Talebi"]',
    'I --> J["SRÇ.006 Süreç İyileştirme"]',
    'G --> K["SRÇ.020 Eğitim"]',
    'G --> L["SRÇ.022 Altyapı"]',
    'G --> M["SRÇ.005 Süreç Değerlendirme"]',
    'G --> N["SRÇ.021 Bilgi Yönetimi"]',
]


def image(storage: bool, filename: str, alt: str, width: int = 900) -> str:
    if storage:
        return f'<p><ac:image ac:width="{width}"><ri:attachment ri:filename="{html.escape(filename)}" /></ac:image></p>'
    return f'<p style="text-align:center"><img class="diagram" src="attachments/{quote(filename)}" alt="{html.escape(alt)}" /></p>'


def web_link(label: str, url: str) -> str:
    return f'<a href="{html.escape(url, quote=True)}">{html.escape(label)}</a>'


def personnel_page_url(unit: str) -> str:
    if unit == "Başkanlık":
        return OFFICIAL_MANAGEMENT_PAGE_URL
    return f"{OFFICIAL_PERSONNEL_BASE_URL}/{PERSONNEL_SECTION_SLUGS[unit]}"


def lst013_template_body() -> str:
    placeholder = [[
        "<em>Kurumsal görev tanımı kodu / revizyonu</em>",
        "<em>Görev tanımı adı</em>",
        "<em>İlgili birim / yönetim</em>",
        "<em>Yetkili kaynak bağlantısı</em>",
        "<em>Resmî web sayfasında yayımlanan görevli personel</em>",
        "<em>Resmî yönetim / personel sayfası</em>",
        "<em>Doğrulandı / Personel eşleştirmesi yayımlanmamış / Gözden geçirilecek</em>",
    ]]
    return "".join([
        "<h2>0. Liste Hakkında</h2>",
        "<h3>0.1. Liste Üst Bilgisi</h3>", table(["Alan", "Değer"], [
            ["Kurum", "İstanbul Üniversitesi - Cerrahpaşa Bilgi İşlem Daire Başkanlığı"],
            ["Doküman Kodu", "LST.013.Ş"],
            ["Doküman Türü", "Liste / Kayıt Şablonu"],
            ["Kullanım Alanı", LST013], ["Durum", "Aktif"], ["Sürüm", "v1.0"],
            ["Yürürlük Tarihi", "15-02-2025"], ["Güncelleme Sıklığı", "Görev tanımı, organizasyon veya yayımlanan personel bilgisi değiştiğinde"],
        ]),
        "<h3>0.2. Şablonun Kullanım Amacı</h3>", p("BİDB'nin resmî görev tanımlarını ve resmî internet sayfasında yayımlanan görevli personel bilgilerini, içerikleri çoğaltmadan yetkili kaynak bağlantılarıyla ilişkilendirmek için kullanılır."),
        "<h3>0.3. Doküman Adlandırma Kuralı</h3>", p(LST013),
        "<h3>0.4. Şablon Sürüm Geçmişi</h3>", history("Görev Tanımları ve Görevli Personel Listesi Şablonu", REVIEWER, APPROVER),
        "<h2>1. Liste Özeti</h2>", table(["Alan", "Değer"], [
            ["Liste Kodu ve Adı", LST013], ["Birincil Süreç", SRC023],
            ["Destekleyen Süreç", "SRÇ.019 - İnsan Kaynakları Yönetimi Süreci"],
            ["Sorumlu", "İdari İşler Şube Müdürü"], ["Durum", "<em>Aktif</em>"], ["Sürüm", "<em>v1.0</em>"],
            ["Son Kaynak Kontrol Tarihi", "<em>GG-AA-YYYY</em>"],
        ]),
        "<h2>2. Kullanım Kuralları</h2>", table(["Kural", "Açıklama"], [
            ["Yetkili kaynak", "Görev tanımı içeriği listeye kopyalanmaz; resmî İÜC görev tanımı PDF bağlantısı kullanılır."],
            ["Personel bilgisi", "Yalnız resmî BİDB yönetim/personel sayfasında yayımlanan ad, görev ve profil bağlantısı gösterilir."],
            ["Görevlendirme kanıtı", "Web sayfasındaki personel bilgisi yön buldurucu kayıttır; resmî atama veya görevlendirme belgesinin yerine geçmez."],
            ["Güncellik", "Kaynak sayfada değişiklik görüldüğünde ilgili satır ve son kaynak kontrol tarihi güncellenir."],
            ["Uyuşmazlık", "Görev tanımı, personel sayfası, organizasyon yapısı veya LST.010 arasında uyuşmazlık varsa sessizce birleştirilmez; SRÇ.023/YGG ve gerekirse SRÇ.018 üzerinden ele alınır."],
        ]),
        "<h2>3. Görev Tanımları ve Görevli Personel Eşleştirmesi</h2>", table([
            "Görev Tanımı Kodu / Sürümü", "Görev Tanımı Adı", "İlgili Birim / Yönetim", "Resmî Görev Tanımı",
            "Web Sitesinde Yayımlanan Görevli Personel", "Resmî Yönetim / Personel Sayfası", "Durum / Not",
        ], placeholder, fixed=True),
        "<h2>4. Kaynak Kontrolü</h2>", table(["Kaynak", "Kontrol Tarihi", "Kontrol Eden", "Sonuç / Not"], [["<em>Resmî kaynak sayfası</em>", "<em>GG-AA-YYYY</em>", "<em>Rol / kişi</em>", "<em>Kontrol sonucu</em>"]]),
        "<h2>5. Sürüm Geçmişi</h2>", history("Görev Tanımları ve Görevli Personel Listesi", REVIEWER, APPROVER),
    ])


def lst013_body() -> str:
    rows: list[list[str]] = []
    for code, role, unit, role_url in ROLE_DEFINITIONS:
        people = PERSONNEL_BY_ROLE.get(role, [])
        personnel = "<br />".join(web_link(name, profile_url) for name, profile_url in people)
        if not personnel:
            personnel = "<em>Resmî sayfada personel eşleştirmesi yayımlanmamış</em>"
        status = "Doğrulandı" if people else "Görev tanımı doğrulandı; personel eşleştirmesi yayımlanmamış"
        rows.append([
            html.escape(code), html.escape(role), html.escape(unit), web_link("Görev tanımını görüntüle", role_url),
            personnel, web_link("Yönetim / personel sayfasını görüntüle", personnel_page_url(unit)), status,
        ])
    return "".join([
        "<h2>1. Liste Özeti</h2>", table(["Alan", "Değer"], [
            ["Liste Kodu ve Adı", LST013], ["Kullanım Amacı", "BİDB görev tanımlarını ve resmî web sayfasında yayımlanan görevli personeli yetkili kaynak bağlantılarıyla ilişkilendirmek"],
            ["Birincil Süreç", SRC023], ["Destekleyen Süreç", "SRÇ.019 - İnsan Kaynakları Yönetimi Süreci"],
            ["Sorumlu", "İdari İşler Şube Müdürü"], ["Durum", "Aktif"], ["Sürüm", "v1.0"],
            ["Son Kaynak Kontrol Tarihi", "15-07-2026"],
        ]),
        "<h2>2. Kullanım Kuralları</h2>", table(["Kural", "Açıklama"], [
            ["Yetkili kaynak", "Görev tanımlarının içeriği bu listede yeniden üretilmez. İÜC tarafından yayımlanan görev tanımı PDF'i esas alınır."],
            ["Personel kapsamı", "Ad ve görev bilgileri BİDB'nin resmî Yönetim ve Personelimiz sayfalarındaki yayımlanmış kayıtlardan alınır; e-posta ve dahili telefon bilgileri listeye taşınmaz."],
            ["Görevlendirme kanıtı", "Bu listedeki personel eşleştirmesi yön buldurucu bir görünüm sağlar; EBYS, KALSİS veya diğer resmî atama/görevlendirme kaydının yerine geçmez."],
            ["Sorumluluk ayrımı", "Görev tanımı ve yönetim altyapısı SRÇ.023; personel görevlendirme ve personel kayıtlarının doğrulanması SRÇ.019 kapsamında yönetilir."],
            ["Uyuşmazlık", "Görev tanımı, personel sayfası, organizasyon yapısı veya LST.010 arasında uyuşmazlık görüldüğünde konu YGG'de değerlendirilir ve gerekiyorsa SRÇ.018'e aktarılır."],
        ]),
        "<h2>3. Görev Tanımları ve Görevli Personel Eşleştirmesi</h2>", table([
            "Görev Tanımı Kodu / Sürümü", "Görev Tanımı Adı", "İlgili Birim / Yönetim", "Resmî Görev Tanımı",
            "Web Sitesinde Yayımlanan Görevli Personel", "Resmî Yönetim / Personel Sayfası", "Durum / Not",
        ], rows, fixed=True),
        "<h2>4. Kaynak Kontrolü</h2>", table(["Kaynak", "Kontrol Tarihi", "Kontrol Eden", "Sonuç / Not"], [
            [web_link("BİDB Görev Tanımları", OFFICIAL_ROLE_PAGE_URL), "15-07-2026", PREPARED_BY, f"{len(ROLE_DEFINITIONS)} görev tanımı adı, kod/sürüm bilgisi ve PDF bağlantısı doğrulandı."],
            [web_link("BİDB Personelimiz", f"{OFFICIAL_PERSONNEL_BASE_URL}/baskanlik-sekreterligi"), "15-07-2026", PREPARED_BY, "Yayımlanan personel-görev ve profil bağlantıları doğrulandı; yayımlanmayan eşleştirmeler açıkça işaretlendi."],
            [web_link("BİDB Yönetim", OFFICIAL_MANAGEMENT_PAGE_URL), "15-07-2026", PREPARED_BY, "Bilgi İşlem Daire Başkanı ve yönetim görevleri doğrulandı."],
        ]),
        "<h2>5. Sürüm Geçmişi</h2>", history("Görev Tanımları ve Görevli Personel Listesi", REVIEWER, APPROVER),
    ])


def process_body(storage: bool) -> str:
    related = "<br />".join([
        "SRÇ.002 - Kalite Güvencesi Süreci",
        "SRÇ.005 - Süreç Değerlendirme Süreci",
        "SRÇ.006 - Süreç İyileştirme Süreci",
        "SRÇ.007 - Proje Yönetimi Süreci",
        "SRÇ.008 - Risk Yönetimi Süreci",
        "SRÇ.017 - Problem Çözüm Yönetimi Süreci",
        "SRÇ.018 - Değişiklik Talebi Yönetimi Süreci",
        "SRÇ.020 - Eğitim Süreci",
        "SRÇ.021 - Bilgi Yönetimi Süreci",
        "SRÇ.022 - Altyapı Süreci",
        "SRÇ.026 - Denetim Süreci",
    ])
    mermaid = info_macro("Mermaid Kodu", FLOW_LINES) if storage else info_view("Mermaid Kodu", FLOW_LINES)
    activities = [
        ["F1", "Yönetim altyapısını belirle", "341.1PR, organizasyon şeması ve görev tanımlarıyla kurumsal yapı; LST.013 ile resmî görev tanımı ve yayımlanan personel bağlantıları; LST.010 ile süreçlere özgü rol, yetki ve RACI yapısı belirlenir. (MAN.2.BP1)", f"Kurumsal organizasyon kaynakları; {LST013}; süreç özel LST.010 kayıtları"],
        ["F2", "Yönetim altyapısını sağla", "Karar, iletişim, planlama, izleme, toplantı ve kayıt mekanizmaları yetkili sistemlerde kullanıma sunulur. (MAN.2.BP2)", f"{PRS006}; Confluence; yönetim ve süreç kayıtları"],
        ["F3", "Yönetim uygulamalarını belirle", "LST.006 kapsamındaki süreçlerin sahiplik, performans, değerlendirme, değişiklik, risk, bilgi ve YGG uygulamaları tanımlanır. (MAN.2.BP3)", f"{PRS006}; LST.007-LST.010; RPR.001"],
        ["F4", "Yönetim uygulamalarını yürüt", "Süreçler kendi kayıtlarıyla işletilir; yıllık veya tetikleyici durumda yönetim girdileri YGG gündeminde birleştirilir. (MAN.2.BP4)", "Doğal süreç kayıtları; FRM.002 YGG tutanağı"],
        ["F5", "Yönetim etkinliğini değerlendir", "RPR.001, FRM.001, kalite ve performans girdileri ile açık/kapalı YGG aksiyonları nitel olarak değerlendirilir. (MAN.2.BP5)", "RPR.001; FRM.001; FRM.002; LST.009 sonuçları"],
        ["F6", "Kararları yönlendir ve iyi uygulamaları destekle", "Kararlar türüne göre ilgili sürece aktarılır; yetki sınırları içinde kabul edilen iyi uygulamalar hedefli olarak duyurulur ve bilgi varlığına dönüştürülür. (MAN.2.BP6)", "Yönlendirilmiş aksiyon; SRÇ.021 bilgi kaydı; koşullu LST.012"],
    ]
    return "".join([
        "<h2>1. Süreç Bilgileri</h2>", table(["Alan", "Değer"], [
            ["Kurum", "İstanbul Üniversitesi - Cerrahpaşa Bilgi İşlem Daire Başkanlığı"],
            ["Süreç Kodu ve Adı", SRC023], ["Süreç Referansı", "ISO/IEC 15504-5:2006 MAN.2 - Organization management"],
            ["Süreç Sahibi", OWNER],
            ["Hedef Kitle", "Bilgi İşlem Daire Başkanı, İdari İşler Şube Müdürü, Proje Yöneticisi, Kalite Danışmanı, ilgili süreç sahipleri ve gündemle ilişkili uzmanlar"],
            ["Yayın ve Erişim Ortamı", "Confluence; ilgili doğal kayıtlar için Jira, Google Drive ve kurumsal sistem bağlantıları"],
            ["Durum", "Aktif"], ["Sürüm", "v1.0"], ["Yürürlük Tarihi", "15-02-2025"],
            ["Son Gözden Geçirme Tarihi", "15-07-2026"],
            ["Güncelleme Sıklığı", "Yılda en az bir kez veya önemli yönetim, mevzuat, performans, risk, hizmet ya da organizasyon değişikliğinde"],
        ]),
        "<h2>2. Amaç</h2>", p("Bu sürecin amacı; BİDB'nin standart süreç envanterinde yer alan süreçlerin kurumsal hedeflerle uyumlu biçimde yönetilmesi için gerekli yönetim altyapısını ve uygulamalarını kurmak, işletmek, etkinliğini değerlendirmek ve iyi uygulamaların benimsenmesini desteklemektir."),
        "<h3>2.1. Süreç Sonuçları</h3>", table(["Sonuç ID", "Süreç Sonucu"], [
            ["S1", "Uygun yönetim altyapısı için kurumsal kaynak ve sorumluluklar belirlenir ve kullanıma sunulur."],
            ["S2", "Etkili organizasyon ve proje yönetimini destekleyen iyi yönetim uygulamaları belirlenir ve uygulanır."],
            ["S3", "Yönetim uygulamalarının kurumsal hedeflere ulaşmadaki etkinliğini değerlendirecek bir temel sağlanır."],
        ]),
        "<h2>3. Kapsam</h2>", table(["Kapsam Öğesi", "Açıklama"], [
            ["Kapsama Dahil", "LST.006 içindeki güncel standart süreç setinin yönetim altyapısı, rol ve karar yapıları, yönetim uygulamaları, yıllık/olağanüstü YGG, karar ve aksiyon takibi, etkinlik değerlendirmesi ve iyi uygulamaların benimsenmesi"],
            ["Kapsam Dışı", "341.1PR ve diğer resmî kurumsal prosedürlerde tanımlanan genel idari, mali ve envanter dışı faaliyetlerin yeniden tanımlanması; genel iş yönlendirme yapısının değiştirilmesi"],
            ["Uygulama Alanı", "İÜC BİDB standart süreçleri, bunların yönetim kayıtları, süreç sahipleri ve ilgili destek rolleri"],
        ]),
        "<h2>4. Referanslar</h2>", table(["Referans", "Açıklama"], [
            ["ISO/IEC 15504-5:2006 MAN.2 - Organization management", "Süreç amacı, sonuçları ve MAN.2.BP1-BP6 temel uygulamaları"],
            ["ISO/IEC 15504-5:2006 - Process Assessment Model", "Süreç boyutu ve değerlendirme göstergeleri"],
            ["ISO/IEC 15504-5:2006 - Process Attributes", "PA 2.1, PA 2.2, PA 3.1 ve PA 3.2 süreç öznitelikleri ile genel uygulamalar"],
            [OFFICIAL_3411, "BİDB birim yapısı, genel sorumluluklar ve kurumsal iş yönlendirme yaklaşımı"],
            [web_link("İÜC BİDB Görev Tanımları", OFFICIAL_ROLE_PAGE_URL), "Yürürlükteki görev tanımı adları, kod/sürüm bilgileri ve resmî PDF bağlantıları"],
            [web_link("İÜC BİDB Yönetim ve Personel Sayfaları", f"{OFFICIAL_PERSONNEL_BASE_URL}/baskanlik-sekreterligi"), "Resmî internet sitesinde yayımlanan yönetim, personel ve görev eşleştirmeleri"],
        ]),
        "<h2>5. Terimler ve Kısaltmalar</h2>", table(["Terim / Kısaltma", "Açıklama"], [
            ["YGG", "Yönetim Gözden Geçirme"], ["Yönetim Altyapısı", "Rol, sorumluluk, karar, iletişim, planlama, izleme, toplantı ve kayıt mekanizmalarının bütünü"],
            ["İyi Uygulama", "Etkinliği veya uygunluğu kanıtlanan ve başka kapsamda benimsenmesi değerlendirilen yönetim ya da süreç uygulaması"],
            ["Takip Koordinatörü", "YGG aksiyonunun ilerlemesini izleyen ve tamamlanma sonucunu doğrulayan Proje Yöneticisi veya İdari İşler Şube Müdürü"],
        ]),
        "<h2>6. Süreç Aktivitesi</h2>", table(["Alan", "Açıklama"], [
            ["Süreç Başlatıcısı", "Yıllık Haziran-Temmuz YGG dönemi; önemli yönetim, mevzuat, performans, risk, hizmet veya organizasyon değişikliği; yönetim uygulamasında etkinlik ya da kaynak ihtiyacı"],
            ["Süreç Başlangıcı", "Yönetim altyapısı ve uygulamalarına ilişkin girdilerin, rollerin ve değerlendirme ihtiyacının belirlenmesi"],
            ["Süreç Bitişi", "Yönetim kararlarının ilgili süreçlere yönlendirilmesi, sorumlu ve hedef tarihlerinin atanması, takip edilmesi ve doğrulanarak kapatılması"],
            ["Ana Faaliyetler", "Yönetim altyapısını belirleme ve sağlama; yönetim uygulamalarını tanımlama ve yürütme; etkinliği değerlendirme; kararları yönlendirme; iyi uygulamaların benimsenmesini destekleme"],
            ["İlgili Süreçler", related],
        ]),
        "<h2>7. Roller ve Sorumluluklar</h2>", p(f"Kurumsal görev tanımları ve resmî web sayfasında yayımlanan görevli personel bağlantıları {LST013} içinde; süreçlere özgü rol, sorumluluk, yetki, yetkinlik ve RACI bilgileri LST.010 - Süreç Rol Yetki ve RACI Matrisi (SRÇ.023) içinde yönetilir."),
        "<h2>8. Araçlar ve Altyapı</h2>", table(["Tür", "Araç / Altyapı Bileşeni", "Kullanım Amacı", "Erişim ve Kullanım Koşulu", "Sorumlu Rol / Birim"], [
            ["Araç", "Confluence", "Süreç paketi, RPR.001, YGG gündem/tutanak ve karar bağlantılarının yayımlanması", "Kurumsal hesap ve sayfa yetkisi; uzaktan erişimde gerekli kurumsal erişim koşulları", "Proje Yöneticisi / Confluence Yöneticisi"],
            ["Araç", "Jira", "Teknik, proje ve süreç odaklı YGG aksiyonlarının doğal iş kayıtlarıyla izlenmesi", "Proje veya ekip bazlı yetkilendirme", "Proje Yöneticisi / Jira Yöneticisi"],
            ["Altyapı", "Google Drive", "YGG eki veya kaynak belgenin yetkili konumunda saklanması ve bağlantılanması", "Kurumsal hesap ve dosya/klasör yetkisi", "Belge Sahibi / İlgili Birim"],
            ["İletişim", "Kurumsal e-posta ve toplantı altyapısı", "Toplantı çağrısı, hedefli karar ve iyi uygulama bilgilendirmesi", "Kurumsal hesap ve ilgili dağıtım kapsamı", "İdari İşler Şube Müdürü / Proje Yöneticisi"],
            ["Altyapı", f"Kurumsal organizasyon, görev tanımı ve yetkilendirme kaynakları; {LST013}", "Kurumsal hiyerarşi, görev/yetki dayanağı ve resmî kaynaklara yönlendirme", "Yürürlükteki resmî kaynak bağlantıları; personel eşleştirmesi resmî atama kaydının yerine geçmez", "Bilgi İşlem Daire Başkanı / İdari İşler Şube Müdürlüğü"],
        ], fixed=True),
        "<h2>9. Süreç İş Ürünleri</h2>", p("Girdi ve çıktı iş ürünleri ile kalite kriterleri LST.008 - İş Ürünleri ve Kalite Kriterleri Listesi (SRÇ.023) dokümanında yönetilir."),
        "<h2>10. Süreç Akışı</h2>", image(storage, FLOW_PNG, "SRÇ.023 organizasyonel yönetim süreç akışı") + mermaid,
        "<h2>11. Süreç Faaliyetleri</h2>", table(["Faaliyet ID", "Faaliyet", "Açıklama", "Elde Edilen / Güncellenen İş Ürünü"], activities),
        "<h2>12. Ölçüm ve İzleme</h2>", p("Süreçte yalnızca planlanan YGG'nin Haziran-Temmuz döneminde gerçekleştirilme durumu ile YGG aksiyonlarının hedef tarihte tamamlanma oranı izlenir. Genel yönetim etkinliği RPR.001, FRM.001 ve YGG kararları üzerinden nitel olarak değerlendirilir."),
        "<h2>13. Uygulama ve Uyarlama Kuralları</h2>",
        "<h3>13.1. Yönetim Altyapısının İki Katmanı</h3>" + p(f"Kurumsal görev, yetki ve hiyerarşi için yürürlükteki organizasyon şeması, görev tanımları ve 341.1PR; resmî kaynaklara yönlendirme için {LST013}; süreçlere özgü RACI ilişkileri için LST.010 esas alınır. LST.013 içindeki personel görünümü resmî atama/görevlendirme kaydının yerine geçmez. Uyuşmazlık sessizce çözümlenmez; YGG'de değerlendirilir ve gerekiyorsa SRÇ.018'e aktarılır."),
        "<h3>13.2. Yönetim Gözden Geçirme</h3>" + p("YGG yılda bir kez Haziran-Temmuz döneminde yapılır. Önemli yönetim, mevzuat, performans, risk veya hizmet değişikliğinde olağanüstü YGG yapılabilir. Toplantıya Bilgi İşlem Daire Başkanı başkanlık eder; yalnızca gündemle ilişkili süreç sahipleri ve uzmanlar katılır."),
        "<h3>13.3. Aksiyon Takibi ve Kapanış</h3>" + p("Teknik, proje ve süreç odaklı aksiyonların takip koordinatörü Proje Yöneticisi; üst yönetimle ilişkili kurumsal ve idari aksiyonların takip koordinatörü İdari İşler Şube Müdürüdür. Karma aksiyonlarda koordinatörü Bilgi İşlem Daire Başkanı belirler. Uygulama sorumlusu sonucu ve bağlantıyı günceller; takip koordinatörü doğrulayarak kapatır."),
        "<h3>13.4. Karar Yönlendirme</h3>" + p("Problem ve uygunsuzluklar SRÇ.017'ye; değişiklik ve iyileştirme fırsatları SRÇ.018'e ve gerektiğinde SRÇ.006'ya; eğitim ihtiyaçları SRÇ.020'ye; altyapı ihtiyaçları SRÇ.022'ye; değerlendirme ihtiyaçları SRÇ.005'e; bilgi ve iyi uygulamalar SRÇ.021'e yönlendirilir."),
        "<h3>13.5. İyi Uygulama Yetkisi ve Yaygınlaştırma</h3>" + p("Mevcut yetki, kaynak ve süreç sınırları içindeki teknik veya operasyonel iyi uygulamaları Proje Yöneticisi; birden fazla birim, kurumsal rol/yetki, ek kaynak veya üst yönetim kararı gerektiren uygulamaları Bilgi İşlem Daire Başkanı onaylar. Hedefli bilgilendirme yapılır; kontrollü doküman değişikliği SRÇ.018 üzerinden yürütülür ve yayımlandığında LST.012'ye kaydedilir."),
        "<h2>14. Süreç Etkileşimleri</h2>", p("Sürecin kurumsal kaynaklar, diğer süreçler ve yönetim kayıtlarıyla etkileşimi LST.007 - Süreç Etkileşim Matrisi (SRÇ.023) dokümanında yönetilir."),
        "<h2>15. Sürüm Geçmişi</h2>", history("Organizasyonel Yönetim Süreci", REVIEWER, APPROVER),
    ])


def lst007_body(storage: bool) -> str:
    mermaid = info_macro("Mermaid Kodu", INTERACTION_LINES) if storage else info_view("Mermaid Kodu", INTERACTION_LINES)
    rows = [
        [f"341.1PR, organizasyon şeması, resmî görev/personel sayfaları ve {LST013}", "Kurumsal yapı, görev, yetki, yayımlanan görevli personel ve iş yönlendirme dayanağı", SRC023, "Girdi", "Bilgi İşlem Daire Başkanı / İdari İşler Şube Müdürü"],
        ["LST.006 - Standart Süreç Envanteri", "Yönetilecek standart süreç kapsamı", SRC023, "Girdi", "Kalite Danışmanı / Proje Yöneticisi"],
        ["RPR.001 - Süreç Performansları Raporu ve süreç özel FRM.001 kayıtları", "Süreç performansı ve değerlendirme sonuçları", SRC023, "Girdi", "Kalite Danışmanı"],
        ["SRÇ.002 / SRÇ.007 / SRÇ.008 / SRÇ.026 ve paydaş geri bildirimleri", "Kalite, müşteri, proje, risk, denetim ve öğrenilmiş ders girdileri", SRC023, "Girdi", "İlgili Süreç Sahipleri"],
        [SRC023, "Yönetim uygulama ve YGG kuralları", PRS006, "Çıktı", OWNER],
        [SRC023, "Resmî görev tanımı ve yayımlanan görevli personel bağlantılarının ortak görünümü", LST013, "Çıktı", "İdari İşler Şube Müdürü"],
        [SRC023, "YGG görüşmeleri, kararları, sorumlu ve takip bilgileri", "FRM.002 - Toplantı Tutanağı (Yönetim Gözden Geçirme - [Yıl])", "Çıktı", "İdari İşler Şube Müdürü / Proje Yöneticisi"],
        [SRC023, "Problem veya uygunsuzluk kararı", "SRÇ.017 - Problem Çözüm Yönetimi Süreci", "Çıktı", "Atanmış Sorumlu"],
        [SRC023, "Değişiklik veya iyileştirme kararı", "SRÇ.018 - Değişiklik Talebi Yönetimi Süreci / SRÇ.006 - Süreç İyileştirme Süreci", "Çıktı", "Atanmış Sorumlu"],
        [SRC023, "Eğitim, altyapı, değerlendirme veya bilgi ihtiyacı", "SRÇ.020 / SRÇ.022 / SRÇ.005 / SRÇ.021", "Çıktı", "Atanmış Sorumlu"],
    ]
    return "".join([
        "<h2>1. Liste Özeti</h2>", table(["Alan", "Değer"], [["Liste Kodu ve Adı", "LST.007 - Süreç Etkileşim Matrisi (SRÇ.023)"], ["Kullanım Amacı", "Organizasyonel Yönetim Sürecinin kurumsal kaynaklar, süreçler ve yönetim kayıtlarıyla etkileşimini göstermek"], ["Sorumlu", OWNER], ["Durum", "Aktif"], ["Sürüm", "v1.0"], ["Son Gözden Geçirme Tarihi", "15-07-2026"]]),
        "<h2>2. Etkileşim Matrisi</h2>", table(["Kaynak Süreç / Sistem / Doküman", "Etkileşim", "Hedef Süreç / Sistem / Doküman", "Yön", "Sorumlu"], rows),
        "<h2>3. Süreç Etkileşim Diyagramı</h2>", image(storage, INTERACTION_PNG, "SRÇ.023 süreç etkileşim diyagramı", 850) + mermaid,
        "<h2>4. Sürüm Geçmişi</h2>", history("Süreç Etkileşim Matrisi (SRÇ.023)", REVIEWER, APPROVER),
    ])


def lst008_body() -> str:
    return "".join([
        "<h2>1. Liste Özeti</h2>", table(["Alan", "Değer"], [["Liste Kodu ve Adı", "LST.008 - İş Ürünleri ve Kalite Kriterleri Listesi (SRÇ.023)"], ["Kullanım Amacı", "Organizasyonel Yönetim Sürecinin girdi ve çıktı iş ürünleri ile kabul kriterlerini tanımlamak"], ["Sorumlu", OWNER], ["Durum", "Aktif"], ["Sürüm", "v1.0"], ["Son Gözden Geçirme Tarihi", "15-07-2026"]]),
        "<h2>2. Girdi İş Ürünleri</h2>", table(["İş Ürünü", "Kaynak", "Kalite Kriteri", "İlgili BP"], [
            ["341.1PR - Bilgi İşlem Daire Başkanlığı Genel İşleyiş Prosedürü, yürürlükteki organizasyon şeması ve görev tanımları", "İÜC resmî kurumsal kaynakları", "Güncel sürüm/yayın bilgisi ve yetkili kaynak bağlantısı doğrulanmıştır.", "MAN.2.BP1-BP2"],
            ["LST.006 - Standart Süreç Envanteri ve süreç özel LST.010 kayıtları", "SRÇ.004 - Süreç Kurulumu Süreci", "Aktif süreç kapsamı, sahiplik ve RACI ilişkileri günceldir.", "MAN.2.BP1-BP3"],
            ["RPR.001 - Süreç Performansları Raporu ve süreç özel FRM.001 değerlendirme kayıtları", "SRÇ.005 - Süreç Değerlendirme Süreci", "Değerlendirme bağlantıları, etiket gerekçeleri ve güncel süreç sonuçları izlenebilirdir.", "MAN.2.BP4-BP5"],
            ["Kalite, müşteri, denetim, risk, proje, öğrenilmiş ders ve paydaş geri bildirim kayıtları", "İlgili süreçler ve doğal kaynak sistemler", "İlgili dönem, kaynak, sahip ve bağlantı bilgileri doğrulanabilir durumdadır.", "MAN.2.BP4-BP5"],
        ]),
        "<h2>3. Çıktı İş Ürünleri</h2>", table(["İş Ürünü", "Kullanım Amacı", "Kalite Kriteri", "İlgili BP"], [
            [PRS006, "Yönetim altyapısı, uygulamaları, YGG ve aksiyon kurallarını tanımlamak", "341.1PR'yi tekrar etmez; yönetim altyapısı, YGG, yetki, yönlendirme ve takip kurallarını kapsar.", "MAN.2.BP1-BP6"],
            [LST013, "Resmî görev tanımlarını ve web sitesinde yayımlanan görevli personeli yetkili kaynak bağlantılarıyla ilişkilendirmek", "Görev tanımı içeriğini çoğaltmaz; yürürlükteki PDF, yönetim/personel sayfası ve profil bağlantılarını gösterir; personel görünümünü resmî atama kanıtı olarak sunmaz.", "MAN.2.BP1-BP2"],
            ["FRM.002.Ş - Toplantı Tutanağı Şablonu", "YGG dahil yapılandırılmış toplantı kayıtlarına ortak format sağlamak", "Katılımcı, gündem, girdi, görüşme, karar/aksiyon, bağlantı ve takip alanlarını içerir.", "MAN.2.BP4-BP6"],
            ["FRM.002 - Toplantı Tutanağı (Yönetim Gözden Geçirme - [Yıl])", "Gerçek YGG görüşme, karar ve aksiyonlarını kaydetmek", "Her aksiyonda sorumlu rol, hedef tarih, ilgili süreç/kayıt, takip koordinatörü, durum ve kanıt bağlantısı bulunur.", "MAN.2.BP4-BP6"],
            ["Yönlendirilmiş yönetim kararı / aksiyon kaydı", "Kararı ilgili problem, değişiklik, iyileştirme, eğitim, altyapı, değerlendirme veya bilgi sürecinde yürütmek", "Kaynak YGG kararı, sorumlu, hedef tarih, hedef süreç ve sonuç bağlantısı izlenebilirdir.", "MAN.2.BP5-BP6"],
            ["FRM.001 - Süreç Gözden Geçirme Formu (SRÇ.023)", "BP ve PA/GP karşılama durumunu kanıtla izlemek", "Etiketler gerekçeli, kanıtlar erişilebilir ve aksiyon yönlendirmeleri açıktır.", "PA 2.1-PA 3.2"],
        ]),
        "<h2>4. Sürüm Geçmişi</h2>", history("İş Ürünleri ve Kalite Kriterleri Listesi (SRÇ.023)", REVIEWER, APPROVER),
    ])


def lst009_body() -> str:
    return "".join([
        "<h2>1. Liste Özeti</h2>", table(["Alan", "Değer"], [["Liste Kodu ve Adı", "LST.009 - Süreç Performans Ölçüm Seti (SRÇ.023)"], ["Kullanım Amacı", "Organizasyonel Yönetim Sürecinin YGG zamanlaması ve aksiyon tamamlama durumunu az sayıda uygulanabilir ölçümle izlemek"], ["Sorumlu", OWNER], ["Durum", "Aktif"], ["Sürüm", "v1.0"], ["Son Gözden Geçirme Tarihi", "15-07-2026"]]),
        "<h2>2. Hedef ve İzleme Matrisi</h2>", table(["Ölçüm", "Tanım / Hesaplama", "Hedef", "Sıklık", "Veri Kaynağı", "Sorumlu", "Sonuç Kullanımı"], [
            ["Planlanan YGG'nin döneminde gerçekleştirilme durumu", "YGG'nin Haziran-Temmuz döneminde gerçekleştirilmesi: Gerçekleşti / Gerçekleşmedi", "Gerçekleşti", "Yıllık", "FRM.002 - Toplantı Tutanağı (Yönetim Gözden Geçirme - [Yıl])", "İdari İşler Şube Müdürü", "Gecikme nedenini ve olağanüstü planlama ihtiyacını değerlendirmek"],
            ["YGG aksiyonlarının hedef tarihte tamamlanma oranı", "Hedef tarihinde kapatılan YGG aksiyonu / hedef tarihi dolan YGG aksiyonu x 100", "En az %90", "Üç aylık ve YGG öncesi", "FRM.002 Kararlar ve Aksiyonlar tablosu", "Proje Yöneticisi / İdari İşler Şube Müdürü", "Geciken aksiyonları sorumluya ve sonraki YGG gündemine taşımak"],
        ]),
        "<h2>3. Ölçüm Uygulama Kuralları</h2>", table(["Kural", "Açıklama"], [["Nitel etkinlik", "Yönetim uygulamalarının genel etkinliği ayrıca puanlanmaz; RPR.001, FRM.001 ve YGG kararlarıyla nitel değerlendirilir."], ["Doğal veri", "Ayrı ölçüm registerı oluşturulmaz; sonuç FRM.002 aksiyon kayıtlarından üretilir."], ["Kapsam", "Henüz hedef tarihi gelmemiş veya iptal gerekçesi yönetimce kabul edilmiş aksiyonlar paydada gösterilir ancak gecikmiş sayılmaz."]]),
        "<h2>4. Sürüm Geçmişi</h2>", history("Süreç Performans Ölçüm Seti (SRÇ.023)", REVIEWER, APPROVER),
    ])


def lst010_body() -> str:
    spec = {
        "process": SRC023, "name": "Organizasyonel Yönetim Süreci",
        "purpose": "SRÇ.023 rol, yetki, yetkinlik ve RACI yapısını tanımlamak", "owner": OWNER,
        "reviewer": REVIEWER, "approver": APPROVER,
        "raci_roles": ["BİD Başkanı", "İdari İşler Şube Müdürü", "Proje Yöneticisi", "Kalite Danışmanı", "İlgili Süreç Sahibi", "Aksiyon Sorumlusu"],
        "roles": [
            ["Bilgi İşlem Daire Başkanı", "Yönetim altyapısını, YGG'yi ve kurumsal kararları sahiplenmek", "YGG kararı vermek; kurumsal kaynak, rol ve yetki değişikliklerini onaylamak", "Kurumsal yönetim, kaynak ve karar yetkisi", "Süreç sahibi / YGG başkanı / onaylayan"],
            ["İdari İşler Şube Müdürü", "YGG hazırlığını ve üst yönetimle ilişkili kurumsal-idari aksiyon takibini koordine etmek", "Atanmış idari aksiyonların sonucunu doğrulayıp kapatmak", "İdari koordinasyon, kurumsal yazışma ve takip", "Gözden geçiren / idari takip koordinatörü"],
            ["Proje Yöneticisi", "Teknik, proje ve süreç girdilerini hazırlamak; ilgili YGG aksiyonlarını takip etmek", "Yetki sınırındaki teknik/operasyonel iyi uygulamaları onaylamak; atanmış aksiyonu doğrulayıp kapatmak", "Proje, süreç, teknik koordinasyon ve araç kullanımı", "Teknik takip koordinatörü"],
            ["Kalite Danışmanı", "RPR.001, FRM.001 ve standart/kalite girdilerini hazırlamak; yöntem uygunluğunu desteklemek", "Kalite ve süreç uygunluk görüşü vermek", "ISO/IEC 15504-5, süreç değerlendirme ve kalite yönetimi", "Hazırlayan / danışılan"],
            ["İlgili Süreç Sahibi", "Gündemle ilgili süreç girdisini ve uygulanabilirlik görüşünü sağlamak", "Kendi sürecinde uygulama ve kaynak görüşü vermek", "İlgili süreç ve operasyon bilgisi", "Danışılan / gündem katılımcısı"],
            ["Aksiyon Sorumlusu", "Atanan kararı uygulamak, sonucu ve kanıt bağlantısını güncellemek", "Onaylı aksiyon kapsamında uygulama yürütmek", "Atanan konuya ilişkin teknik veya idari yetkinlik", "Uygulayan"],
        ],
        "activities": [
            ["F1 Yönetim altyapısını belirle", "A", "R/C", "R/C", "R", "C", "I"],
            ["F2 Yönetim altyapısını sağla", "A", "R", "R", "C", "C", "I"],
            ["F3 Yönetim uygulamalarını belirle", "A", "C", "R", "R", "C", "I"],
            ["F4 Yönetim uygulamalarını ve YGG'yi yürüt", "A", "R", "R", "C", "C", "I"],
            ["F5 Etkinliği değerlendir", "A", "C", "R", "R", "C", "I"],
            ["F6 Kararları yönlendir ve iyi uygulamaları destekle", "A", "R/C", "R/C", "C", "C", "R"],
        ],
        "products": [
            [PRS006, "A", "C", "R", "R", "C", "I"],
            [LST013, "A", "R", "C", "C", "I", "I"],
            [FRM002_TEMPLATE, "A", "R", "C", "R", "C", "I"],
            ["FRM.002 - Toplantı Tutanağı (Yönetim Gözden Geçirme - [Yıl])", "A", "R", "R", "C", "C", "I"],
            ["Yönlendirilmiş yönetim kararı ve aksiyon kaydı", "A", "R/C", "R/C", "C", "C", "R"],
            ["LST.009 - Süreç Performans Ölçüm Seti (SRÇ.023)", "A", "R/C", "R/C", "R", "I", "I"],
            ["FRM.001 - Süreç Gözden Geçirme Formu (SRÇ.023)", "A", "C", "C", "R", "C", "I"],
        ],
        "authority": [
            ["SRÇ.023 ve PRS.006 yürürlük/onay kararı", "Kalite Danışmanı", "İdari İşler Şube Müdürü", "Bilgi İşlem Daire Başkanı", "Kontrollü doküman değişikliği SRÇ.018 üzerinden yürütülür."],
            ["YGG kararı", "İdari İşler Şube Müdürü / Proje Yöneticisi / Kalite Danışmanı", "İlgili Süreç Sahipleri", "Bilgi İşlem Daire Başkanı", "Yalnız gündemle ilgili katılımcıların görüşü alınır."],
            ["Teknik veya operasyonel iyi uygulama", "Proje Yöneticisi / İlgili Süreç Sahibi", "Kalite Danışmanı", "Proje Yöneticisi", "Mevcut yetki, kaynak ve süreç sınırları içinde kalmalıdır."],
            ["Kurumsal veya çok birimli iyi uygulama", "Proje Yöneticisi / İdari İşler Şube Müdürü", "İlgili Süreç Sahipleri", "Bilgi İşlem Daire Başkanı", "Birden fazla birim, rol/yetki, ek kaynak veya üst yönetim etkisinde uygulanır."],
            ["YGG aksiyonu kapanışı", "Aksiyon Sorumlusu", "Atanmış Takip Koordinatörü", "Atanmış Takip Koordinatörü", "Sonuç ve varsa kanıt bağlantısı doğrulanır; rutin başkan kapanış onayı aranmaz."],
        ],
    }
    return raci_body(spec)


def blank_review_body() -> str:
    return "".join([
        "<h2>1. Form Bilgileri</h2>", table(["Alan", "Değer"], [["Form Kodu ve Adı", "FRM.001 - Süreç Gözden Geçirme Formu (SRÇ.023)"], ["Süreç", SRC023], ["Değerlendirme Tarihi", "<em>GG-AA-YYYY</em>"], ["Değerlendiren", "<em>Rol / kişi</em>"], ["Durum", "Boş Form"], ["Sürüm", "v1.0"]]),
        "<h2>2. Durum Değerleri</h2>", table(["Durum", "Anlamı"], LABELS),
        "<h2>3. BP Takip Matrisi</h2>", table(["BP", "Standart Beklentisi", "Mevcut Karşılama", "Karşılayan Doküman / Kayıt", "Durum", "Eksik / Tamamlayıcı Aksiyon"], [[bp, expectation, "<em>Değerlendirme açıklaması</em>", "<em>Kanıt bağlantısı</em>", "<em>YOK / ZAYIF / DAĞINIK / VAR / KAPSAM DIŞI</em>", "<em>Aksiyon / gerekçe</em>"] for bp, _, expectation in MAN2_BPS]),
        "<h2>4. PA / GP Takip Matrisi</h2>", table(["PA", "GP", "Standart Beklentisi", "Mevcut Karşılama", "Karşılayan Doküman / Kayıt", "Durum", "Eksik / Tamamlayıcı Aksiyon"], [[pa, gp, expectation, "<em>Değerlendirme açıklaması</em>", "<em>Kanıt bağlantısı</em>", "<em>Etiket</em>", "<em>Aksiyon / gerekçe</em>"] for pa, gp, expectation in GPS]),
        "<h2>5. Öncelikli Tamamlama Listesi</h2>", table(["Öncelik", "Bulgu / Aksiyon", "Bulgu Türü", "İlgili BP / GP", "Hedef Süreç / İzleme Yeri"], [["<em>Yüksek / Orta / Düşük</em>", "<em>Bulgu veya aksiyon</em>", "<em>Uygunsuzluk / İyileştirme Fırsatı / Gözlem / Güçlü Uygulama</em>", "<em>BP / GP</em>", "<em>SRÇ.017 / SRÇ.018 / ilgili kayıt</em>"]]),
    ])


def assessment_body() -> str:
    statuses = {"MAN.2.BP1":"VAR", "MAN.2.BP2":"VAR", "MAN.2.BP3":"DAĞINIK", "MAN.2.BP4":"ZAYIF", "MAN.2.BP5":"ZAYIF", "MAN.2.BP6":"DAĞINIK"}
    bp_rows = []
    for code, _, expectation in MAN2_BPS:
        status = statuses[code]
        if status == "VAR":
            current = "Kurumsal kaynaklar ve süreç paketi içinde yönetim altyapısı tanımlanmış ve erişilebilir durumdadır."
            action = "Kurumsal kaynak, LST.013 ve süreç özel LST.010 uyumu işletim sırasında korunmalıdır."
        elif status == "DAĞINIK":
            current = "Yöntem, yetki ve yönlendirme kuralı tanımlıdır; benimsenme ve uygulama kanıtı henüz sistematik değildir."
            action = "İlk gerçek yönetim kararı ve iyi uygulama yönlendirmesinde doğal kanıtlar doğrulanmalıdır."
        else:
            current = "YGG ve etkinlik değerlendirme yöntemi tanımlıdır; henüz gerçekleştirilmiş YGG ve ölçüm sonucu bulunmamaktadır."
            action = "İlk gerçek YGG Haziran-Temmuz döneminde gerçekleştirilmeli ve aksiyon sonuçları izlenmelidir."
        bp_rows.append([code, expectation, current, f"{SRC023}; {PRS006}; LST.007-LST.010; {LST013}; FRM.002.Ş", status, action])
    gp_status = {
        "GP.2.1.1":"VAR", "GP.2.1.2":"DAĞINIK", "GP.2.1.3":"ZAYIF", "GP.2.1.4":"VAR", "GP.2.1.5":"VAR", "GP.2.1.6":"VAR",
        "GP.2.2.1":"VAR", "GP.2.2.2":"VAR", "GP.2.2.3":"DAĞINIK", "GP.2.2.4":"DAĞINIK",
        "GP.3.1.1":"VAR", "GP.3.1.2":"VAR", "GP.3.1.3":"VAR", "GP.3.1.4":"VAR", "GP.3.1.5":"VAR",
        "GP.3.2.1":"DAĞINIK", "GP.3.2.2":"DAĞINIK", "GP.3.2.3":"YOK", "GP.3.2.4":"DAĞINIK", "GP.3.2.5":"VAR", "GP.3.2.6":"ZAYIF",
    }
    evidence = f"{SRC023}; LST.007; LST.008; LST.009; LST.010; {LST013}; {PRS006}; {FRM002_TEMPLATE}"
    gp_rows = []
    for pa, gp, expectation in GPS:
        status = gp_status[gp]
        if status == "VAR":
            current, action = "Süreç paketi, roller, iş ürünleri, etkileşimler, altyapı ve kontrol kurallarıyla tanımlanmıştır.", "Tanımlı yapı korunmalı ve gerçek kayıtlarla sürdürülmelidir."
        elif status == "DAĞINIK":
            current, action = "Tanım vardır; gerçek YGG, görevlendirme, aksiyon veya gözden geçirme kanıtı henüz sistematik değildir.", "İlk gerçek işletim döneminde doğal yönetim kayıtları tamamlanmalıdır."
        elif status == "ZAYIF":
            current, action = "Yöntem tanımlıdır; gerçek performans ayarlama veya veri analizi henüz yapılmamıştır.", "İlk YGG ve ölçüm döneminde sonuç üretilmelidir."
        else:
            current, action = "Rol bazlı yetkinlik ve eğitim kanıtı henüz bulunmamaktadır.", "Gerçek ihtiyaç SRÇ.020 kapsamında değerlendirilmelidir."
        gp_rows.append([pa, gp, expectation, current, evidence, status, action])
    completion = [
        ["Yüksek", "İlk gerçek YGG'yi Haziran-Temmuz döneminde gerçekleştir ve FRM.002 ile kaydet.", "Gözlem", "MAN.2.BP4-BP5; GP.2.1.2; GP.3.2.1", "FRM.002 / LST.009 / FRM.001 Değerlendirme #1"],
        ["Orta", "İlk YGG aksiyonlarında konu türüne göre takip koordinatörü, sonuç ve kanıt bağlantısını doğrula.", "Gözlem", "MAN.2.BP4-BP6; GP.2.2.3-GP.2.2.4", "FRM.002 / ilgili hedef süreç"],
        ["Orta", "LST.013'teki kurumsal organizasyon/görev kaynakları ile süreç özel LST.010 kayıtlarını ilk YGG öncesinde uyuşmazlık açısından kontrol et.", "İyileştirme Fırsatı", "MAN.2.BP1-BP3; GP.2.1.6", "SRÇ.018 / YGG gündemi"],
        ["Düşük", "Rol bazlı yetkinlik ihtiyacı oluştuğunda SRÇ.020 kapsamında eğitim/katılım kanıtı oluştur.", "Gözlem", "GP.3.2.3", "SRÇ.020"],
    ]
    return "".join([
        "<h2>1. Değerlendirme Özeti</h2>", table(["Alan", "Değer"], [["Süreç", SRC023], ["Değerlendirme Kaydı", "Değerlendirme #1"], ["Değerlendirme Tarihi", "15-07-2026"], ["Değerlendiren", PREPARED_BY], ["Yaklaşım", "Sayısal puan ve tek toplam süreç etiketi kullanılmadan gerekçeli BP ve PA/GP etiketleri"], ["BP Dağılımı", "2 VAR, 2 DAĞINIK ve 2 ZAYIF"], ["PA/GP Dağılımı", "12 VAR, 6 DAĞINIK, 2 ZAYIF ve 1 YOK"]]),
        "<h2>2. Durum Değerleri</h2>", table(["Durum", "Anlamı"], LABELS),
        "<h2>3. BP Takip Matrisi</h2>", table(["BP", "Standart Beklentisi", "Mevcut Karşılama", "Karşılayan Doküman / Kayıt", "Durum", "Eksik / Tamamlayıcı Aksiyon"], bp_rows),
        "<h2>4. PA / GP Takip Matrisi</h2>", table(["PA", "GP", "Standart Beklentisi", "Mevcut Karşılama", "Karşılayan Doküman / Kayıt", "Durum", "Eksik / Tamamlayıcı Aksiyon"], gp_rows),
        "<h2>5. Öncelikli Tamamlama Listesi</h2>", table(["Öncelik", "Bulgu / Aksiyon", "Bulgu Türü", "İlgili BP / GP", "Hedef Süreç / İzleme Yeri"], completion),
        "<h2>6. Sonuç</h2>", p("Yönetim altyapısı ve YGG yöntemi dokümante edilmiştir. Değerlendirme henüz gerçek YGG, aksiyon izleme ve performans sonuçları oluşmadan yapıldığı için uygulama ve etkinlik alanları ihtiyatlı etiketlenmiştir; aynı Değerlendirme #1 kaydı doğal kanıtlar oluştukça güncellenecektir."),
    ])


def procedure_body() -> str:
    return "".join([
        "<h2>1. Prosedür Bilgileri</h2>", table(["Alan", "Değer"], [["Kurum", "İstanbul Üniversitesi - Cerrahpaşa Bilgi İşlem Daire Başkanlığı"], ["Prosedür Kodu ve Adı", PRS006], ["Prosedür Referansı", SRC023], ["Prosedür Sahibi", OWNER], ["Durum", "Aktif"], ["Sürüm", "v1.0"], ["Yürürlük Tarihi", "15-02-2025"], ["Son Gözden Geçirme Tarihi", "15-07-2026"]]),
        "<h2>2. Amaç</h2>", p("Bu prosedürün amacı; LST.006 kapsamındaki standart süreçler için yönetim altyapısının, yönetim uygulamalarının, Yönetim Gözden Geçirme toplantısının, karar/aksiyon takibinin, etkinlik değerlendirmesinin ve iyi uygulama benimseme kurallarının uygulanışını tanımlamaktır."),
        "<h2>3. Kapsam</h2>", p("Bu prosedür; BİDB standart süreçlerinin sahiplik, karar, iletişim, planlama, izleme, performans ve YGG uygulamalarına; YGG girdilerinin hazırlanmasına; kararların ilgili süreçlere yönlendirilmesine; aksiyonların takip ve kapanışına uygulanır."),
        "<h2>4. Kapsam Dışı</h2>", p("341.1PR ve ilgili resmî kurumsal prosedürlerde tanımlanan birim yapısı, genel idari ve mali sorumluluklar ile iş yönlendirme faaliyetleri bu prosedürde yeniden tanımlanmaz veya değiştirilmez."),
        "<h2>5. Referanslar</h2>", table(["Referans", "Açıklama"], [[SRC023, "MAN.2 kapsamı ve süreç faaliyetleri"], [OFFICIAL_3411, "BİDB birim yapısı, genel sorumluluklar ve iş yönlendirme dayanağı"], [LST013, "Resmî görev tanımı ve yayımlanan görevli personel bağlantılarının ortak görünümü"], ["LST.006 - Standart Süreç Envanteri", "Prosedürün uygulandığı güncel standart süreç kapsamı"], ["LST.010 - Süreç Rol Yetki ve RACI Matrisleri", "Süreçlere özgü rol, karar ve sorumluluk ilişkileri"], [FRM002_TEMPLATE, "YGG dahil yapılandırılmış toplantı kayıt formatı"], ["RPR.001 - Süreç Performansları Raporu", "YGG için kümülatif süreç performans girdisi"], ["PRS.XXX.Ş - Prosedür Tanımı Şablonu", "Bu prosedürün doküman yapısı"]]),
        "<h2>6. Terimler ve Kısaltmalar</h2>", table(["Terim / Kısaltma", "Açıklama"], [["YGG", "Yönetim Gözden Geçirme"], ["Olağanüstü YGG", "Önemli yönetim, mevzuat, performans, risk veya hizmet değişikliği nedeniyle yıllık dönem dışında yapılan YGG"], ["Takip Koordinatörü", "Aksiyon ilerlemesini izleyen ve sonucu doğrulayarak kapatan rol"], ["Doğal Kayıt", "İlgili süreç veya kaynak sistemde işin yürütülmesi sırasında oluşan gerçek kayıt"]]),
        "<h2>7. Roller ve Sorumluluklar</h2>", table(["Rol", "Sorumluluk", "Yetki"], [["Bilgi İşlem Daire Başkanı", "YGG'ye başkanlık etmek; yönetim ve kaynak kararlarını vermek", "Kurumsal ve çok birimli kararları onaylamak"], ["İdari İşler Şube Müdürü", "Toplantı hazırlığına ve kurumsal-idari aksiyon takibine katkı vermek", "Atanmış idari aksiyonların kapanışını doğrulamak"], ["Proje Yöneticisi", "Teknik/proje/süreç girdilerini ve aksiyonlarını koordine etmek", "Yetki sınırındaki teknik/operasyonel iyi uygulamaları onaylamak; atanmış aksiyonu kapatmak"], ["Kalite Danışmanı", "RPR.001, FRM.001, standart ve kalite girdilerini hazırlamak", "Kalite/süreç uygunluk görüşü vermek"], ["İlgili Süreç Sahibi / Uzman", "Gündem girdisi, uygulanabilirlik ve kaynak görüşü sağlamak", "Kendi görev alanında görüş ve uygulama kararı önermek"], ["Aksiyon Sorumlusu", "Kararı uygulamak, sonucu ve kanıt bağlantısını güncellemek", "Onaylı aksiyon kapsamındaki uygulamayı yürütmek"]]),
        "<h2>8. Genel İlkeler</h2>", table(["İlke", "Açıklama"], [["Tamamlayıcılık", "Bu prosedür 341.1PR'yi tekrar etmez veya değiştirmez; MAN.2 boşluklarını tamamlar."], ["Yetkili kaynağa bağlantı", "Görev tanımlarının içeriği LST.013'e kopyalanmaz; resmî PDF ve web sayfasına bağlantı verilir."], ["Personel görünümünün niteliği", "Resmî web sitesinde yayımlanan görevli personel bilgisi yönlendirici görünüm sağlar; EBYS/KALSİS atama veya görevlendirme kaydının yerine geçmez."], ["Gündemle ilgili katılım", "Tüm süreç sahipleri zorunlu katılımcı değildir; yalnız gündemle ilişkili roller toplantıya dahil edilir."], ["Doğal kanıt", "Mevcut ve erişilebilir kayıtlar kullanılır; eksik başlıklar için yapay kayıt üretilmez."], ["Tekrarsız kayıt", "Aksiyon ilgili hedef süreçte yürütülür; FRM.002 kaynak karar ve takip bağlantısını korur."], ["Asgari bürokrasi", "Takip koordinatörü rutin aksiyonu doğrulayarak kapatır; her kapanış için ayrıca başkan onayı aranmaz."], ["İzlenebilir değişiklik", "Kontrollü süreç veya doküman değişikliği SRÇ.018 üzerinden yürütülür."]]),
        "<h2>9. Prosedür Esasları</h2>", table(["Esas / Kural", "Açıklama", "Zorunluluk", "Not"], [["Yıllık dönem", "YGG Haziran-Temmuz döneminde, ilk çeyrek değerlendirmeleri ve güncel RPR.001 sonrasında yapılır.", "Zorunlu", "Yılda bir"], ["Olağanüstü toplantı", "Önemli yönetim, mevzuat, performans, risk veya hizmet değişikliğinde yapılabilir.", "Koşullu", "Bilgi İşlem Daire Başkanı kararı"], ["Toplantı kaydı", "YGG, FRM.002 kullanılarak kaydedilir.", "Zorunlu", "Gerçek toplantı olduğunda"], ["Aksiyon alanları", "Sorumlu rol, hedef tarih, ilgili süreç/kayıt, takip koordinatörü, durum ve kanıt/sonuç bağlantısı tutulur.", "Zorunlu", "Her karar aksiyon doğurmayabilir"], ["Açık aksiyon", "Tamamlanmayan aksiyon sonraki YGG girdisi olur.", "Zorunlu", "Hedef süreç kaydıyla ilişkilendirilir"], ["İyi uygulama", "Yetki sınırına göre Proje Yöneticisi veya Bilgi İşlem Daire Başkanı onaylar.", "Koşullu", "Değişiklik gerekiyorsa SRÇ.018"]]),
        "<h2>10. Uygulama / Strateji Matrisi</h2>", table(["Alan / Aşama", "Uygulama Kuralı", "Sorumlu", "Kayıt / Kanıt", "Not"], [["1. Girdileri hazırla", "Önceki kararlar; RPR.001/FRM.001; kalite/müşteri; denetim/risk/problem/değişiklik; proje/hizmet; kaynak/yetkinlik/altyapı; standart/mevzuat/organizasyon girdilerini derle. Görev ve yayımlanan personel bağlantıları için LST.013'ü kullan.", "İdari İşler Şube Müdürü / Proje Yöneticisi / Kalite Danışmanı", f"{LST013}; doğal kaynak bağlantıları", "Yalnız erişilebilir ve ilgili kayıtlar"], ["2. Gündem ve katılımı belirle", "Gündeme göre süreç sahibi, şube müdürü, uzman veya çalışan katılımını belirle.", "Bilgi İşlem Daire Başkanı / İdari İşler Şube Müdürü", "Toplantı çağrısı / FRM.002", "Tüm süreç sahipleri zorunlu değildir"], ["3. YGG'yi gerçekleştir", "Girdileri değerlendir, yönetim kararlarını ve öncelikleri belirle.", "Bilgi İşlem Daire Başkanı", "FRM.002", "Karar mercii YGG başkanıdır"], ["4. Aksiyonu tanımla", "Sorumlu, hedef tarih, hedef süreç/kayıt, takip koordinatörü ve beklenen sonucu ata.", "YGG Başkanı", "FRM.002 Kararlar ve Aksiyonlar", "Karma konuda koordinatörü başkan belirler"], ["5. İlgili sürece yönlendir", "Kararı problem, değişiklik/iyileştirme, eğitim, altyapı, değerlendirme veya bilgi sürecine aktar.", "Atanmış Sorumlu", "Hedef süreç kaydı", "Kaynak YGG kararı bağlanır"], ["6. Takip et", "Teknik işleri Proje Yöneticisi; kurumsal-idari işleri İdari İşler Şube Müdürü izler.", "Takip Koordinatörü", "FRM.002 durum alanı / hedef kayıt", "Karma konu başkan kararı"], ["7. Doğrula ve kapat", "Sorumlunun sonuç ve bağlantısını doğrula; uygun ise aksiyonu kapat.", "Takip Koordinatörü", "FRM.002 sonuç ve durum", "Rutin başkan kapanış onayı yok"], ["8. Sonraki döneme aktar", "Açık aksiyonları ve etkinlik sonuçlarını sonraki YGG girdisine al.", "İdari İşler Şube Müdürü / Proje Yöneticisi", "Sonraki YGG gündemi", "Süreklilik"]]),
        "<h2>11. Yayın, Erişim ve Bakım Kuralları</h2>", table(["Kural Alanı", "Kural", "Sorumlu", "Kayıt / Kanıt"], [["Yayın", "Onaylı süreç ve prosedür Confluence'ta yayımlanır; gerçek YGG tutanağı erişim sınıfına uygun alanda tutulur.", "Proje Yöneticisi", "Confluence sürümü"], ["Erişim", "YGG tutanağı ve eklerine yalnız görev ve gündem gereği erişim verilir.", "Belge Sahibi / Sistem Yöneticisi", "Kaynak sistem yetkileri"], ["Duyuru", "Karar ve iyi uygulamalar yalnız ilgili rol/personel ile hedefli paylaşılır.", "Takip Koordinatörü / Karar Sahibi", "Kurumsal e-posta veya doğal iletişim kaydı"], ["Doküman değişikliği", "Kontrollü değişiklik SRÇ.018 üzerinden uygulanır; yayımlandığında LST.012 kaydı oluşturulur.", "Proje Yöneticisi / Kalite Danışmanı", "SRÇ.018 / LST.012"], ["Bakım", "Prosedür yılda bir kez veya yönetim yaklaşımı değiştiğinde gözden geçirilir.", "Süreç Sahibi / Kalite Danışmanı", "FRM.001 / doküman sürümü"]]),
        "<h2>12. Kayıtlar ve Kanıtlar</h2>", table(["Kayıt / Kanıt", "Kullanım Amacı", "Saklama Yeri", "Sorumlu", "Not"], [[LST013, "Resmî görev tanımı ve yayımlanan görevli personel bağlantılarını ortak görünümde tutmak", "03 - Kayıtlar ve Listeler", "İdari İşler Şube Müdürü", "Personel görünümü resmî atama kanıtı değildir"], ["FRM.002 - Toplantı Tutanağı (Yönetim Gözden Geçirme - [Yıl])", "YGG girdileri, görüşmeleri, kararları ve aksiyonlarını kaydetmek", "Confluence / yetkili toplantı alanı", "İdari İşler Şube Müdürü / Proje Yöneticisi", "Gerçek toplantı olduğunda oluşturulur"], ["RPR.001 - Süreç Performansları Raporu", "Süreç sonuçlarını YGG'ye sunmak", "09 - Raporlar", "Kalite Danışmanı", "Kümülatif taslak"], ["Süreç özel FRM.001 kayıtları", "BP ve PA/GP değerlendirme sonuçlarını sağlamak", "91 - İç Denetimler / Süreç Gözden Geçirmeleri", "Kalite Danışmanı", "Değerlendirme #1 güncellenir"], ["Hedef süreç aksiyon kaydı", "YGG kararını uygulamak ve sonucu izlemek", "İlgili süreç / Jira / Confluence / doğal sistem", "Aksiyon Sorumlusu", "FRM.002'ye bağlantı verilir"], ["Hedefli bilgilendirme kaydı", "Karar veya iyi uygulamanın ilgili hedef kitleye iletildiğini göstermek", "Kurumsal e-posta / doğal iletişim kanalı", "Takip Koordinatörü", "Her YGG kararı için LST.012 kullanılmaz"]]),
        "<h2>13. Sürüm Geçmişi</h2>", history("Organizasyonel Yönetim Prosedürü", REVIEWER, APPROVER),
    ])


def frm002_template_body() -> str:
    return "".join([
        "<h2>0. Şablon Hakkında</h2>",
        "<h3>0.1. Şablon Üst Bilgisi</h3>", table(["Alan", "Değer"], [["Kurum", "İstanbul Üniversitesi - Cerrahpaşa Bilgi İşlem Daire Başkanlığı"], ["Doküman Kodu", "FRM.002.Ş"], ["Doküman Türü", "Form Şablonu"], ["Kullanım Alanı", "Yapılandırılmış toplantı tutanağı"], ["Durum", "Aktif"], ["Sürüm", "v1.0"], ["Yürürlük Tarihi", "15-02-2025"], ["Son Gözden Geçirme Tarihi", "15-07-2026"]]),
        "<h3>0.2. Kullanım Amacı</h3>", p("Bu şablon, Yönetim Gözden Geçirme toplantıları başta olmak üzere yapılandırılmış toplantıların bilgi, katılım, gündem, girdi, görüşme, karar, aksiyon ve bağlantılarını ortak formatta kaydetmek için kullanılır. Günlük veya operasyonel toplantılarda kullanılması zorunlu değildir."),
        "<h3>0.3. Adlandırma Kuralı</h3>", p("FRM.002 - Toplantı Tutanağı ([Toplantı Adı] - [Tarih veya Sıra]); YGG için FRM.002 - Toplantı Tutanağı (Yönetim Gözden Geçirme - [Yıl])"),
        "<h3>0.4. Şablon Sürüm Geçmişi</h3>", history("Toplantı Tutanağı Şablonu", REVIEWER, APPROVER),
        "<h2>1. Toplantı Bilgileri</h2>", table(["Alan", "Değer"], [["Toplantı Adı", "<em>Toplantı adı</em>"], ["Toplantı Türü", "<em>YGG / Proje / Süreç / Teknik / İdari / Diğer</em>"], ["Tarih ve Saat", "<em>GG-AA-YYYY / SS:DD</em>"], ["Yer / Bağlantı", "<em>Fiziksel yer veya çevrim içi bağlantı</em>"], ["Toplantı Başkanı", "<em>Rol / kişi</em>"], ["Tutanağı Hazırlayan", "<em>Rol / kişi</em>"], ["İlgili Süreç / Proje", "<em>Kod ve ad / bağlantı</em>"], ["Gizlilik / Erişim", "<em>Erişim sınıfı</em>"]]),
        "<h2>2. Katılımcılar</h2>", table(["Ad Soyad", "Rol / Birim", "Katılım Durumu", "Not"], [["<em>Katılımcı</em>", "<em>Rol / birim</em>", "<em>Katıldı / Katılmadı / Kısmi</em>", "<em>Not</em>"]]),
        "<h2>3. Gündem Maddeleri</h2>", table(["No", "Gündem Maddesi", "Sunum / Sorumlu", "Planlanan Süre"], [["<em>1</em>", "<em>Gündem maddesi</em>", "<em>Rol / kişi</em>", "<em>Süre</em>"]]),
        "<h2>4. Görüşülen Girdiler ve Belgeler</h2>", table(["Girdi / Belge", "Kaynak", "Bağlantı / Sürüm", "İlgili Gündem", "Not"], [["<em>Belge veya kayıt</em>", "<em>Kaynak süreç / sistem</em>", "<em>Bağlantı / sürüm</em>", "<em>Gündem no</em>", "<em>Not</em>"]]),
        "<h2>5. Görüşmeler ve Değerlendirmeler</h2>", table(["Gündem No", "Görüşme / Değerlendirme Özeti", "Görüş / Çekince", "Sonuç"], [["<em>No</em>", "<em>Tarafsız görüşme özeti</em>", "<em>Varsa ayrışan görüş</em>", "<em>Karar / bilgi / sonraki adım</em>"]]),
        "<h2>6. Kararlar ve Aksiyonlar</h2>", table(["Karar / Aksiyon No", "Karar / Aksiyon", "Tür", "Sorumlu Rol / Kişi", "Hedef Tarih", "İlgili Süreç / Kayıt", "Takip Koordinatörü", "Durum", "Sonuç / Kanıt Bağlantısı"], [["<em>K-01 / A-01</em>", "<em>Karar veya yapılacak iş</em>", "<em>Karar / Problem / Değişiklik / İyileştirme / Eğitim / Altyapı / Değerlendirme / Bilgi</em>", "<em>Rol / kişi</em>", "<em>GG-AA-YYYY</em>", "<em>Kod / kayıt / bağlantı</em>", "<em>Proje Yöneticisi / İdari İşler Şube Müdürü / diğer</em>", "<em>Açık / Devam Ediyor / Tamamlandı / Kapalı / İptal</em>", "<em>Sonuç ve bağlantı</em>"]], fixed=True),
        "<h2>7. Ekler ve Bağlantılar</h2>", table(["Ek / Bağlantı", "Açıklama", "Sahibi", "Erişim Koşulu"], [["<em>Dosya / sayfa / kayıt bağlantısı</em>", "<em>Açıklama</em>", "<em>Rol / birim</em>", "<em>Erişim koşulu</em>"]]),
        "<h2>8. Toplantı Sonucu ve Sonraki Gözden Geçirme</h2>", table(["Alan", "Değer"], [["Toplantı Sonucu", "<em>Genel sonuç</em>"], ["Açık Konular", "<em>Açık konu / yok</em>"], ["Sonraki Gözden Geçirme / Toplantı", "<em>Tarih, dönem veya tetikleyici</em>"], ["Dağıtım / Bilgilendirme", "<em>Hedef kitle ve kanal</em>"], ["Tutanak Durumu", "<em>Taslak / Gözden Geçirildi / Tamamlandı</em>"]]),
    ])


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
        row = "<tr>" + "".join(f'<td class="confluenceTd">{html.escape(x)}</td>' for x in cells) + "</tr>"
        section = section[:tbody.start(2)] + "".join(rows) + row + section[tbody.end(2):]
        return doc[:h.end()] + section + doc[end:]
    raise RuntimeError(f"Section not found: {heading_fragment}")


def update_lst001() -> Path:
    page = CONFLUENCE / LST001_REL
    storage = (page / "body.storage.xhtml").read_text(encoding="utf-8")
    storage = section_upsert(storage, "3. Süreç Dokümanları", "SRÇ.023", ["SRÇ.023", "Organizasyonel Yönetim Süreci", "MAN.2", OWNER, "Aktif", "v1.0", "15-02-2025", "01 - Süreç Dokümanları"])
    storage = section_upsert(storage, "4. Prosedürler", "PRS.006", ["PRS.006", "Organizasyonel Yönetim Prosedürü", "SRÇ.023", OWNER, "Aktif", "v1.0", "15-02-2025", "07 - Prosedürler"])
    storage = section_upsert(storage, "6. Şablonlar", "FRM.002.Ş", ["FRM.002.Ş", "Toplantı Tutanağı Şablonu", "FRM.002 toplantı tutanakları", "Aktif", "v1.0", "15-02-2025", "02 - Şablonlar"])
    storage = section_upsert(storage, "6. Şablonlar", "LST.013.Ş", ["LST.013.Ş", "Görev Tanımları ve Görevli Personel Listesi Şablonu", "LST.013 üretimi", "Aktif", "v1.0", "15-02-2025", "02 - Şablonlar"])
    storage = section_upsert(storage, "7. Genel Kayıt ve Listeler", "LST.013", ["LST.013", "Görev Tanımları ve Görevli Personel Listesi", "SRÇ.023 yönetim altyapısı / SRÇ.019 insan kaynakları desteği", "İdari İşler Şube Müdürü", "Aktif", "v1.0", "03 - Kayıtlar ve Listeler"])
    (page / "body.storage.xhtml").write_text(storage, encoding="utf-8")
    (page / "body.view.html").write_text(build_view("LST.001 - Aktif Dokümanlar Listesi", storage), encoding="utf-8")
    return page


def update_lst006() -> Path:
    page = CONFLUENCE / LST006_REL
    storage = (page / "body.storage.xhtml").read_text(encoding="utf-8")
    def replace_row(match: re.Match[str]) -> str:
        row = match.group(0)
        plain = html.unescape(re.sub(r"<[^>]+>", "", row))
        if "SRÇ.023" not in plain:
            return row
        cells = re.findall(r"(<td[^>]*>)(.*?)(</td>)", row, flags=re.I | re.S)
        values = ["MAN.2", "Organization management", "SRÇ.023", "Organizasyonel Yönetim Süreci", OWNER, "Aktif", "Süreç paketi yerelde oluşturulmuş; kullanıcı incelemesi ve kontrollü Confluence yayını beklenmektedir."]
        return "<tr>" + "".join(f"{a}{html.escape(v)}{c}" for (a, _, c), v in zip(cells, values)) + "</tr>"
    storage = re.sub(r"<tr[^>]*>.*?</tr>", replace_row, storage, flags=re.I | re.S)
    (page / "body.storage.xhtml").write_text(storage, encoding="utf-8")
    (page / "body.view.html").write_text(build_view("LST.006 - Standart Süreç Envanteri", storage), encoding="utf-8")
    return page


def update_parent_registers() -> list[Path]:
    proc = PAGE_ROOT / "07-prosedurler"
    items = []
    for child in sorted(proc.iterdir()):
        meta = child / "page.yaml"
        if not meta.exists():
            continue
        title = (yaml.safe_load(meta.read_text(encoding="utf-8")) or {}).get("title", "")
        m = re.match(r"(İÜC\.BİDB\.PRS\.\d{3})\s+-\s+(.+)", title)
        if m:
            items.append((m.group(1), m.group(2), title))
    body = parent_register_body("Prosedür", items)
    (proc / "body.storage.xhtml").write_text(body.rstrip() + "\n", encoding="utf-8")
    (proc / "body.view.html").write_text(build_view("07 - Prosedürler", body), encoding="utf-8")

    templates = PAGE_ROOT / "02-sablonlar"
    body = (templates / "body.storage.xhtml").read_text(encoding="utf-8")
    tbody = re.search(r"(<tbody[^>]*>)(.*?)(</tbody>)", body, flags=re.I | re.S)
    if not tbody:
        raise RuntimeError("Template register table missing")
    rows = re.findall(r"<tr[^>]*>.*?</tr>", tbody.group(2), flags=re.I | re.S)
    rows = [r for r in rows if not any(code in html.unescape(re.sub(r"<[^>]+>", "", r)) for code in ["FRM.002.Ş", "LST.013.Ş"])]
    additions = []
    for code, name, title in [
        ("FRM.002.Ş", "Toplantı Tutanağı Şablonu", FRM002_TEMPLATE),
        ("LST.013.Ş", "Görev Tanımları ve Görevli Personel Listesi Şablonu", LST013_TEMPLATE),
    ]:
        link = f'<ac:link><ri:page ri:content-title="{title}" /><ac:plain-text-link-body><![CDATA[İncele]]></ac:plain-text-link-body></ac:link>'
        additions.append("<tr>" + "".join(f'<td class="confluenceTd">{x}</td>' for x in [str(len(rows) + len(additions) + 1), code, name, "Aktif", link]) + "</tr>")
    body = body[:tbody.start(2)] + "".join(rows + additions) + body[tbody.end(2):]
    (templates / "body.storage.xhtml").write_text(body.rstrip() + "\n", encoding="utf-8")
    (templates / "body.view.html").write_text(build_view("02 - Şablonlar", body), encoding="utf-8")
    records = PAGE_ROOT / "03-kayitlar-ve-listeler"
    body = (records / "body.storage.xhtml").read_text(encoding="utf-8")
    tbody = re.search(r"(<tbody[^>]*>)(.*?)(</tbody>)", body, flags=re.I | re.S)
    if not tbody:
        raise RuntimeError("Records register table missing")
    rows = re.findall(r"<tr[^>]*>.*?</tr>", tbody.group(2), flags=re.I | re.S)
    rows = [r for r in rows if "LST.013" not in html.unescape(re.sub(r"<[^>]+>", "", r))]
    link = f'<ac:link><ri:page ri:space-key="SSSS" ri:content-title="{LST013}" /><ac:plain-text-link-body><![CDATA[İncele]]></ac:plain-text-link-body></ac:link>'
    row = "<tr>" + "".join(f'<td class="confluenceTd">{x}</td>' for x in [str(len(rows) + 1), "LST.013", "Görev Tanımları ve Görevli Personel Listesi", "Aktif", link]) + "</tr>"
    body = body[:tbody.start(2)] + "".join(rows) + row + body[tbody.end(2):]
    (records / "body.storage.xhtml").write_text(body.rstrip() + "\n", encoding="utf-8")
    (records / "body.view.html").write_text(build_view("03 - Kayıtlar ve Listeler", body), encoding="utf-8")
    return [proc, templates, records]


def append_section_row(doc: str, heading: str, key: str, cells: list[str], *, before_key: str | None = None) -> str:
    heads = list(re.finditer(r"<h2[^>]*>(.*?)</h2>", doc, flags=re.I | re.S))
    for i, h in enumerate(heads):
        title = html.unescape(re.sub(r"<[^>]+>", "", h.group(1))).strip()
        if title != heading:
            continue
        end = heads[i+1].start() if i+1 < len(heads) else len(doc)
        section = doc[h.end():end]
        tbody = re.search(r"(<tbody[^>]*>)(.*?)(</tbody>)", section, flags=re.I | re.S)
        if not tbody:
            raise RuntimeError(f"No table under {heading}")
        rows = [r for r in re.findall(r"<tr[^>]*>.*?</tr>", tbody.group(2), flags=re.I | re.S) if key not in html.unescape(re.sub(r"<[^>]+>", "", r))]
        row = "<tr>" + "".join(f'<td class="confluenceTd">{html.escape(x)}</td>' for x in cells) + "</tr>"
        if before_key:
            split = next((idx for idx, item in enumerate(rows) if before_key in html.unescape(re.sub(r"<[^>]+>", "", item))), len(rows))
            rows.insert(split, row)
        else:
            rows.append(row)
        section = section[:tbody.start(2)] + "".join(rows) + section[tbody.end(2):]
        return doc[:h.end()] + section + doc[end:]
    raise RuntimeError(f"Heading not found: {heading}")


def update_rpr001() -> Path:
    page = CONFLUENCE / RPR001_REL
    storage = html.unescape((page / "body.storage.xhtml").read_text(encoding="utf-8"))
    storage = storage.replace(
        "Şu aşamada SRÇ.001, SRÇ.004, SRÇ.005, SRÇ.006 ve SRÇ.021 değerlendirmeleri rapora alınmıştır.",
        "Şu aşamada SRÇ.001, SRÇ.004, SRÇ.005, SRÇ.006, SRÇ.021 ve SRÇ.023 değerlendirmeleri rapora alınmıştır.",
    )
    storage = storage.replace(
        "SRÇ.021 katalog gözden geçirme ve iyileştirme kanıtı henüz oluşmamıştır.",
        "SRÇ.021 katalog gözden geçirme ile SRÇ.023 YGG ve yönetim etkinliği kanıtları henüz oluşmamıştır.",
    )
    storage = append_section_row(storage, "4. Süreç Sonuç Özeti", "SRÇ.023", [SRC023, "MAN.2 BP1-BP6; PA 2.1-PA 3.2", "2 VAR; 2 DAĞINIK; 2 ZAYIF", "12 VAR; 6 DAĞINIK; 2 ZAYIF; 1 YOK", "", "FRM.001 - Süreç Gözden Geçirme Formu (SRÇ.023) - Değerlendirme #1", "Yönetim altyapısı, YGG yöntemi, karar yönlendirme ve takip kuralları tanımlı; gerçek YGG, aksiyon kapanışı ve performans kanıtları henüz oluşmamıştır."])
    storage = append_section_row(storage, "5. Etiket Dağılımları ve Eğilimler", "SRÇ.023", ["SRÇ.023", "2", "2", "2", "0", "12", "6", "2", "1"], before_key="Eğilim Yorumu")
    (page / "body.storage.xhtml").write_text(storage, encoding="utf-8")
    (page / "body.view.html").write_text(build_view("RPR.001 - Süreç Performansları Raporu", storage), encoding="utf-8")
    return page


def upsert_index(page_dirs: list[Path]) -> None:
    index = yaml.safe_load(INDEX_PATH.read_text(encoding="utf-8")) or {}
    pages = index.setdefault("pages", [])
    rels = {str(d.relative_to(CONFLUENCE)).replace("\\", "/") for d in page_dirs if (d / "page.yaml").exists()}
    pages[:] = [x for x in pages if x.get("relative_path") not in rels]
    for d in page_dirs:
        meta_path = d / "page.yaml"
        if not meta_path.exists():
            continue
        meta = yaml.safe_load(meta_path.read_text(encoding="utf-8")) or {}
        rel = meta["relative_path"]
        pages.append({"page_id": str(meta.get("page_id") or ""), "title": meta["title"], "parent_id": str(meta.get("parent_id") or ""), "depth": meta["depth"], "relative_path": rel, "slug": meta["slug"], "storage_file": f"{rel}/body.storage.xhtml", "view_file": f"{rel}/body.view.html"})
    pages.sort(key=lambda x: (int(x.get("depth") or 0), str(x.get("relative_path") or "")))
    index["total_page_count"] = len(pages)
    index["exported_at"] = datetime.now(timezone.utc).isoformat()
    INDEX_PATH.write_text(yaml.safe_dump(index, allow_unicode=True, sort_keys=False), encoding="utf-8")
    for d in [PAGE_ROOT / "02-sablonlar", PAGE_ROOT / "03-kayitlar-ve-listeler", PAGE_ROOT / "07-prosedurler", PAGE_ROOT / "91-ic-denetimler/surec-gozden-gecirmeleri", CONFLUENCE / SRC023_REL]:
        meta_path = d / "page.yaml"
        if not meta_path.exists():
            continue
        meta = yaml.safe_load(meta_path.read_text(encoding="utf-8")) or {}
        stable = str(meta.get("page_id") or f"local:{meta.get('relative_path')}")
        meta["children_count"] = sum(1 for x in pages if str(x.get("parent_id") or "") == stable)
        meta_path.write_text(yaml.safe_dump(meta, allow_unicode=True, sort_keys=False), encoding="utf-8")


def update_status_and_report() -> None:
    current = ROOT / "docs/CURRENT_STATUS.md"
    text = current.read_text(encoding="utf-8")
    marker = "- RPR.001 ve RPR.001.Ş üzerinde Etiket Dağılımları ve Eğilimler tablosunun süreçler satırda olacak biçimde çevrilmesi; Süreç Sonuç Özeti tablosuna ileride tanımlanmak üzere boş `SPICE Olgunluk Seviyesi` sütununun eklenmesi.\n"
    old_addition = "- SRÇ.023 Organizasyonel Yönetim paketinin süreç tanımı, LST.007-LST.010, boş FRM.001 ve Değerlendirme #1 ile yerelde oluşturulması; PRS.006 Organizasyonel Yönetim Prosedürü ile FRM.002.Ş Toplantı Tutanağı Şablonunun hazırlanması. Confluence yayını kullanıcı incelemesi ve onayına bırakılmıştır.\n"
    text = text.replace(old_addition, "")
    addition = "- SRÇ.023 Organizasyonel Yönetim paketinin süreç tanımı, LST.007-LST.010, boş FRM.001 ve Değerlendirme #1 ile yerelde oluşturulması; PRS.006 Organizasyonel Yönetim Prosedürü ile FRM.002.Ş Toplantı Tutanağı Şablonunun hazırlanması. Resmî görev tanımları ve yayımlanan görevli personel bağlantıları için LST.013.Ş ve 03 - Kayıtlar ve Listeler altında LST.013 eklenmiştir. Confluence yayını kullanıcı incelemesi ve onayına bırakılmıştır.\n"
    if addition not in text:
        text = text.replace(marker, marker + addition)
        current.write_text(text, encoding="utf-8")
    (ROOT / "reports/src023_organization_management_package_report.md").write_text("""# SRÇ.023 Organizasyonel Yönetim Paketi Yerel Raporu

Tarih: 15-07-2026

## Oluşturulan / Güncellenen Yapı

- SRÇ.023 süreç tanımı MAN.2 BP1-BP6 izlenebilirliğiyle oluşturuldu.
- Süreç özel LST.007, LST.008, LST.009, LST.010 ve boş FRM.001 hazırlandı.
- SRÇ.023 Değerlendirme #1 yalnızca gerekçeli etiket yaklaşımıyla oluşturuldu.
- PRS.006 Organizasyonel Yönetim Prosedürü 341.1PR'yi tekrar etmeyen tamamlayıcı yapı olarak hazırlandı.
- FRM.002.Ş Toplantı Tutanağı Şablonu oluşturuldu; gerçekleşmemiş YGG kaydı üretilmedi.
- LST.013.Ş ile LST.013 oluşturuldu; resmî görev tanımı PDF'leri, yönetim/personel sayfaları ve yayımlanan personel profilleri bağlantı üzerinden ilişkilendirildi.
- Personel görünümü resmî atama/görevlendirme kanıtı olarak kullanılmadı; web sayfasında eşleşmesi bulunmayan görevler açıkça işaretlendi.
- LST.001, LST.006, RPR.001 ve ilgili ana kayıt sayfaları güncellendi.

## Değerlendirme Özeti

- BP: 2 VAR, 2 DAĞINIK, 2 ZAYIF.
- PA/GP: 12 VAR, 6 DAĞINIK, 2 ZAYIF, 1 YOK.
- Gerçek YGG, aksiyon kapanışı ve ölçüm sonucu bulunmadığından uygulama alanları ihtiyatlı etiketlendi.

## Yayın Durumu

- Bu çalışma yalnızca yerel repository ve viewer için hazırlanmıştır.
- Confluence'a yazma yapılmamıştır; kullanıcı incelemesi ve kontrollü dry-run beklenmektedir.
""", encoding="utf-8")


def validate(page_dirs: list[Path]) -> None:
    process = (CONFLUENCE / SRC023_REL / "body.storage.xhtml").read_text(encoding="utf-8")
    heads = [html.unescape(re.sub(r"<[^>]+>", "", h)) for h in re.findall(r"<h2[^>]*>(.*?)</h2>", process, flags=re.S)]
    expected = ["1. Süreç Bilgileri", "2. Amaç", "3. Kapsam", "4. Referanslar", "5. Terimler ve Kısaltmalar", "6. Süreç Aktivitesi", "7. Roller ve Sorumluluklar", "8. Araçlar ve Altyapı", "9. Süreç İş Ürünleri", "10. Süreç Akışı", "11. Süreç Faaliyetleri", "12. Ölçüm ve İzleme", "13. Uygulama ve Uyarlama Kuralları", "14. Süreç Etkileşimleri", "15. Sürüm Geçmişi"]
    if heads != expected:
        raise RuntimeError(f"SRÇ.023 heading mismatch: {heads}")
    for bp, _, _ in MAN2_BPS:
        if bp not in process:
            raise RuntimeError(f"Missing BP trace: {bp}")
    if "341.1PR" not in process or any(x in process for x in ["26 süreç", "Soru Bankası"]):
        raise RuntimeError("Reference or forbidden expression validation failed")
    for d in page_dirs:
        for name in ["page.yaml", "body.storage.xhtml", "body.view.html"]:
            if not (d / name).exists():
                raise RuntimeError(f"Missing artifact: {d / name}")
    assessment = (CONFLUENCE / REVIEWS_REL / "frm-001-surec-gozden-gecirme-formu-src-023-degerlendirme-1/body.storage.xhtml").read_text(encoding="utf-8")
    if "2 VAR, 2 DAĞINIK ve 2 ZAYIF" not in assessment or "12 VAR, 6 DAĞINIK, 2 ZAYIF ve 1 YOK" not in assessment:
        raise RuntimeError("Assessment distribution mismatch")
    lst013 = (CONFLUENCE / LST013_REL / "body.storage.xhtml").read_text(encoding="utf-8")
    template = (CONFLUENCE / TEMPLATES_REL / "lst-013-s-gorev-tanimlari-ve-gorevli-personel-listesi-sablonu/body.storage.xhtml").read_text(encoding="utf-8")
    if len(re.findall(r"cdn\.iuc\.edu\.tr/.+?\.pdf", lst013)) != len(ROLE_DEFINITIONS):
        raise RuntimeError("LST.013 role definition link count mismatch")
    if any(token in lst013 for token in ["@iuc.edu.tr", "Dahili"]):
        raise RuntimeError("LST.013 contains excluded contact information")
    if "Yönetici Sekreteri" not in lst013 or "Maaş İşleri Personeli" not in lst013 or lst013.count("personel eşleştirmesi yayımlanmamış") < 2:
        raise RuntimeError("LST.013 unpublished personnel markers missing")
    if "Görev Tanımları ve Görevli Personel Eşleştirmesi" not in template:
        raise RuntimeError("LST.013 template structure mismatch")


def main() -> None:
    src = CONFLUENCE / SRC023_REL
    assets = src / "attachments"
    assets.mkdir(parents=True, exist_ok=True)
    (assets / FLOW_MMD).write_text("\n".join(FLOW_LINES) + "\n", encoding="utf-8")
    write_page(src, SRC023, "137265784", "01 - Süreç Dokümanları", 2, process_body(True), process_body(False))
    pages: list[Path] = [src]
    children = [
        ("lst-007-surec-etkilesim-matrisi-src-023", "LST.007 - Süreç Etkileşim Matrisi (SRÇ.023)", lst007_body(True), lst007_body(False)),
        ("lst-008-is-urunleri-ve-kalite-kriterleri-listesi-src-023", "LST.008 - İş Ürünleri ve Kalite Kriterleri Listesi (SRÇ.023)", lst008_body(), None),
        ("lst-009-surec-performans-olcum-seti-src-023", "LST.009 - Süreç Performans Ölçüm Seti (SRÇ.023)", lst009_body(), None),
        ("lst-010-surec-rol-yetki-ve-raci-matrisi-src-023", "LST.010 - Süreç Rol Yetki ve RACI Matrisi (SRÇ.023)", lst010_body(), None),
    ]
    for slug, title, storage, view in children:
        d = src / slug
        write_page(d, title, SRC023_ID, SRC023, 3, storage, view)
        pages.append(d)
        if "lst-007" in slug:
            a = d / "attachments"
            a.mkdir(exist_ok=True)
            (a / INTERACTION_MMD).write_text("\n".join(INTERACTION_LINES) + "\n", encoding="utf-8")
    blank = src / "frm-001-surec-gozden-gecirme-formu-src-023"
    write_page(blank, "FRM.001 - Süreç Gözden Geçirme Formu (SRÇ.023)", SRC023_ID, SRC023, 3, blank_review_body())
    pages.append(blank)
    assessment = CONFLUENCE / REVIEWS_REL / "frm-001-surec-gozden-gecirme-formu-src-023-degerlendirme-1"
    write_page(assessment, "FRM.001 - Süreç Gözden Geçirme Formu (SRÇ.023) - Değerlendirme #1", REVIEWS_ID, "Süreç Gözden Geçirmeleri", 3, assessment_body())
    pages.append(assessment)
    prs = CONFLUENCE / PROCEDURES_REL / "prs-006-organizasyonel-yonetim-proseduru"
    write_page(prs, PRS006, PROCEDURES_ID, "07 - Prosedürler", 2, procedure_body())
    pages.append(prs)
    frm_t = CONFLUENCE / TEMPLATES_REL / "frm-002-s-toplanti-tutanagi-sablonu"
    write_page(frm_t, FRM002_TEMPLATE, TEMPLATES_ID, "02 - Şablonlar", 2, frm002_template_body())
    pages.append(frm_t)
    lst013_t = CONFLUENCE / TEMPLATES_REL / "lst-013-s-gorev-tanimlari-ve-gorevli-personel-listesi-sablonu"
    write_page(lst013_t, LST013_TEMPLATE, TEMPLATES_ID, "02 - Şablonlar", 2, lst013_template_body())
    pages.append(lst013_t)
    lst013 = CONFLUENCE / LST013_REL
    write_page(lst013, LST013, "137265786", "03 - Kayıtlar ve Listeler", 2, lst013_body())
    pages.append(lst013)
    pages.extend([update_lst001(), update_lst006(), update_rpr001()])
    pages.extend(update_parent_registers())
    unique = list(dict.fromkeys(pages))
    upsert_index(unique)
    update_status_and_report()
    validate([d for d in unique if (d / "page.yaml").exists()])
    print(f"[DONE] SRÇ.023 package materialized: {len(unique)} page directories")


if __name__ == "__main__":
    main()
