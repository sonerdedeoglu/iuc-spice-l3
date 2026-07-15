#!/usr/bin/env python3
"""Refresh the existing SRÇ.001 and SRÇ.004 Assessment #1 pages in place.

The script intentionally preserves the directory, title, page_id, parent and page.yaml.
It updates only the assessment contents and creates an evidence/change report.
"""
from __future__ import annotations

import html
import re
from dataclasses import dataclass
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "confluence/pages/000-root-iuc-bidb-spice-2026-level-3"
REVIEWS = PAGES / "91-ic-denetimler/surec-gozden-gecirmeleri"
REPORT = ROOT / "reports/process_review_assessment_1_refresh_report.md"

SRC001_DIR = REVIEWS / (
    "frm-001-surec-gozden-gecirme-formu-"
    "src-001-degerlendirme-1"
)
SRC004_DIR = REVIEWS / (
    "frm-001-surec-gozden-gecirme-formu-"
    "src-004-degerlendirme-1"
)

CSS = """
body{margin:0;background:#fff;color:#172b4d;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;line-height:1.55}
.confluence-page{max-width:1180px;margin:0 auto;padding:32px 24px 56px}
h1,h2,h3,h4,h5,h6{margin:1.4em 0 .55em;line-height:1.25;color:#0f172a}
h1{margin-top:0;padding-bottom:12px;border-bottom:1px solid #d8dee4}
p{margin:0 0 12px} table{width:100%;border-collapse:collapse;margin:16px 0;table-layout:auto}
th,td{border:1px solid #c9d1d9;padding:8px 10px;vertical-align:top}
th{background:#f6f8fa;font-weight:600;text-align:left}
""".strip()


@dataclass(frozen=True)
class RowUpdate:
    value: str
    note: str
    evidence: str
    action: str


SRC001_UPDATES: dict[str, RowUpdate] = {
    "SUP.7.BP2": RowUpdate(
        "%95 - VAR",
        "Dokümanların geliştirilmesi, değiştirilmesi ve sürdürülmesi için KLV.001 ile yazım/sürüm kuralları; güncel SRÇ, PRS, KLV ve LST şablonlarıyla ortak yapı ve içerik standartları tanımlanmıştır. Süreç şablonuna hedef kitle, yayın/erişim, süreç sonuçları ve araçlar/altyapı alanları eklenmiştir.",
        "KLV.001; SRÇ.XXX.Ş; PRS.XXX.Ş; KLV.XXX.Ş; aktif LST şablon ailesi",
        "-",
    ),
    "SUP.7.BP3": RowUpdate(
        "%95 - VAR",
        "Format, başlık, tarih, tanımlayıcı, sürüm geçmişi, hazırlayan, gözden geçiren, onaylayan, amaç ve içerik alanlarına ek olarak hedef kitle ile yayın/erişim ortamı artık süreç şablonunda açıkça tanımlıdır. LST.012 gerçek yayın kaydında süreç ve hedef kitle birlikte izlenmektedir.",
        "KLV.001; SRÇ.XXX.Ş; SRÇ/PRS/KLV/LST şablon ailesi; LST.012",
        "-",
    ),
    "SUP.7.BP4": RowUpdate(
        "%85 - VAR",
        "Genel doküman envanteri, süreç özel doküman paketleri ve yaşam döngüsü doküman matrisiyle üretilecek dokümanlar belirlenmektedir. SRÇ.004 paketinin tamamlanması bu yapının ikinci süreçte uygulanabildiğini göstermiştir; proje özel SB matrisi ise hâlâ tamamlanmalıdır.",
        "LST.001; LST.005.Ş; SRÇ.001 ve SRÇ.004 süreç özel doküman paketleri; Soru Bankası Projesi / LST.005 (SB)",
        "-",
    ),
    "SUP.7.BP5": RowUpdate(
        "%90 - VAR",
        "SRÇ.001 doküman setine ek olarak SRÇ.004 süreç tanımı, prosedürü, kılavuzları ve süreç özel kayıtları güncel şablonlara göre geliştirilmiş, yerel olarak doğrulanmış ve Confluence'ta yayımlanmıştır.",
        "SRÇ.001; PRS.001; KLV.001; SRÇ.001 destek paketi; SRÇ.004 süreç tasarım paketi; Confluence ve Git geçmişi",
        "-",
    ),
    "SUP.7.BP7": RowUpdate(
        "%65 - DAĞINIK",
        "SRÇ.001 ve ilişkili destek dokümanları Confluence'ta yayımlanmış; yayın tarihi, süreç, hedef kitle, yöntem ve bağlantı LST.012 içinde gerçek kayıt olarak tutulmuştur. Bununla birlikte hedef kitleye ayrı duyuru/teslim ve gerektiğinde alındı teyidi henüz doğrulanmamıştır.",
        "Confluence sayfa ağacı; LST.001; LST.012; Confluence yayın geçmişi",
        "Hedef kitleye gerçek bilgilendirme yapılmalı; duyuru/teslim ve gerektiğinde alındı teyidi LST.012 veya doğal kaynak kaydıyla ilişkilendirilmelidir.",
    ),
    "SUP.7.BP8": RowUpdate(
        "%65 - DAĞINIK",
        "Sürüm geçmişi, Confluence revizyonları, Git kayıtları, arşivleme ve eski sayfaların kontrollü kaldırılmasıyla bakım uygulaması güçlenmiştir. LST.002 güncelliği ve SRÇ.016 ile formal yapılandırma/baseline bağı tamamlanmamıştır.",
        "LST.002; doküman sürüm geçmişleri; Arşiv - Kaldırılan Şablonlar; Confluence revizyon ve sayfa kaldırma raporları; Git geçmişi; SRÇ.016",
        "Son doküman ve şablon revizyonları LST.002'ye işlenmeli; kontrollü dokümanların SRÇ.016 kapsamındaki değişiklik/baseline kurallarıyla bağı açıklaştırılmalıdır.",
    ),
    "GP.2.1.5": RowUpdate(
        "%65 - DAĞINIK",
        "Süreç şablonu ve SRÇ.001 içinde araçlar, altyapı, kullanım amaçları, erişim koşulları ve sorumlu roller açıkça tanımlanmıştır. İnsan kaynağı ve zaman tahsisi ile fiili kullanım kayıtları formal değildir.",
        "SRÇ.001 Araçlar ve Altyapı bölümü; SRÇ.XXX.Ş; Confluence/repository altyapısı; LST.011",
        "SRÇ.001 için gerekli insan kaynağı ve zaman tahsisi ile kaynakların fiili kullanım durumu kayıt altına alınmalıdır.",
    ),
    "GP.2.1.6": RowUpdate(
        "%65 - DAĞINIK",
        "Süreç ve doküman arayüzleri LST.007'de, sorumluluklar LST.010'da ayrıntılıdır. LST.012'de Confluence yayını kaydedilmiştir; ancak ilgili taraflara ayrı bilgilendirme yapıldığı henüz doğrulanmamıştır.",
        "LST.007 (SRÇ.001); LST.010 (SRÇ.001); LST.012",
        "İlgili taraf iletişimleri ve süreç bilgilendirme faaliyeti LST.012 veya eşdeğer doğal kaynak kaydıyla kanıtlanmalıdır.",
    ),
    "GP.2.2.2": RowUpdate(
        "%90 - VAR",
        "Dokümantasyon, dağıtım, tanımlama, bileşen, onay ve erişim gereksinimleri aktif şablonlar ve doküman kontrol kurallarıyla tanımlıdır. Yenilenen LST.007, süreçlerin yanında prosedür, kılavuz, liste, şablon ve form bağımlılıklarını da göstermektedir.",
        "KLV.001; PRS.001; LST.001; LST.007 (SRÇ.001); aktif şablon ailesi",
        "-",
    ),
    "GP.2.2.3": RowUpdate(
        "%65 - DAĞINIK",
        "Kontrollü dokümanlar Confluence sayfa kimliği, sürüm geçmişi ve Git revizyonlarıyla izlenmektedir; eski dokümanlar kontrollü biçimde kaldırılmıştır. LST.002 ile formal değişiklik ve baseline ilişkisi henüz tam değildir.",
        "LST.001; doküman sürüm geçmişleri; Confluence sayfa kimlikleri ve revizyon geçmişi; Git geçmişi; eski sayfa kaldırma raporları; LST.002",
        "Kontrollü doküman kapsamı, değişiklik akışı, sürüm/baseline ilişkisi ve güncel revizyon durumu LST.002 ve SRÇ.016 ile tutarlı hale getirilmelidir.",
    ),
    "GP.3.1.1": RowUpdate(
        "%95 - VAR",
        "SRÇ.001 ile ortak dokümantasyon süreci; güncel süreç şablonu, PRS.002, KLV.002 ve KLV.003 ile standart süreçlerin tanımlanması, kontrolü ve uyarlanması için bütünsel yapıyı desteklemektedir.",
        "SRÇ.001; SRÇ.XXX.Ş; PRS.001; PRS.002; KLV.002; KLV.003",
        "-",
    ),
    "GP.3.1.2": RowUpdate(
        "%95 - VAR",
        "SRÇ.001 akışı ve LST.007, süreç sırasını ve diğer süreçlerle birlikte ilgili prosedür, kılavuz, liste, şablon ve form etkileşimlerini tutarlı Mermaid kaynak/görseliyle tanımlamaktadır.",
        "SRÇ.001 Süreç Akışı; LST.007 (SRÇ.001); Mermaid kaynakları ve PNG görselleri",
        "-",
    ),
    "GP.3.1.4": RowUpdate(
        "%90 - VAR",
        "Süreç şablonu ve SRÇ.001 içinde gerekli araç, altyapı, çalışma ortamı, kullanım amacı, erişim koşulu ve sorumlu rol ayrı bir bölümde tanımlanmıştır.",
        "SRÇ.001 Araçlar ve Altyapı bölümü; SRÇ.XXX.Ş; KLV.004; LST.011; Confluence/repository yapısı",
        "-",
    ),
    "GP.3.2.1": RowUpdate(
        "%65 - DAĞINIK",
        "SRÇ.001 ve destek dokümanları güncel yapıyla Confluence'ta yayımlanmış ve LST.012'de kaydedilmiştir. Belirli proje/bağlam için yapılan uyarlamanın ve standart sürece uygunluk doğrulamasının kaydı sınırlıdır.",
        "SRÇ.001; KLV.002; KLV.003; LST.012; Soru Bankası Projesi / LST.005 (SB)",
        "Soru Bankası Projesi için kullanılan SRÇ.001 uyarlamaları, gerekçeleri ve standart sürece uygunluk kontrolü kayıt altına alınmalıdır.",
    ),
    "GP.3.2.2": RowUpdate(
        "%65 - DAĞINIK",
        "Roller, sorumluluklar ve yetkiler LST.010 ile atanmış; süreç yayını LST.012'de hedef kitleyle birlikte kaydedilmiştir. Ayrı rol duyurusu ve kabul/teyit kanıtı henüz bulunmamaktadır.",
        "LST.010 (SRÇ.001); SRÇ.001 roller bölümü; LST.012",
        "Rol ve sorumluluklar ilgili kişilere duyurulmalı; iletişim ve gerektiğinde kabul/teyit kaydı LST.012 veya doğal kaynakta tutulmalıdır.",
    ),
    "GP.3.2.4": RowUpdate(
        "%65 - DAĞINIK",
        "Gerekli doküman ve bilgi kaynakları Confluence'ta yayımlanmış, araç ve erişim koşulları tanımlanmıştır. İnsan kaynağı tahsisi ve fiili kullanım kayıtları formal değildir.",
        "Confluence doküman alanı; SRÇ.001; PRS.001; LST.010; LST.011; LST.012",
        "Süreç için gerekli insan kaynağı ve bilgi kaynaklarının tahsisi ile fiili kullanım durumu kayıt altına alınmalıdır.",
    ),
    "GP.3.2.5": RowUpdate(
        "%80 - VAR",
        "Confluence, Git repository, yerel görüntüleyici ve VPN tabanlı çalışma ortamı fiilen kullanılmış; gerekli altyapı ve erişim koşulları SRÇ.001 içinde açıkça tanımlanmıştır. Altyapı destek/bakım kanıtları doğal kaynak sistemlerde tutulur.",
        "SRÇ.001 Araçlar ve Altyapı bölümü; Confluence; Git repository; yerel görüntüleyici; VPN; LST.011",
        "-",
    ),
}


SRC004_UPDATES: dict[str, RowUpdate] = {
    "PIM.1.BP1": RowUpdate(
        "VAR",
        "Güncel standart süreç seti, her sürecin amacı/uygulanabilirliği ve SRÇ.004'ün süreç-doküman etkileşimleri tanımlanmış; Mermaid kaynak ve PNG tutarlılığı yerel olarak doğrulanmıştır.",
        "SRÇ.004; LST.006; LST.007 (SRÇ.004); SRÇ.004 bütünsel yerel gözden geçirme raporu",
        "-",
    ),
    "PIM.1.BP2": RowUpdate(
        "DAĞINIK",
        "SRÇ.004 ve destek paketi Confluence'ta yayımlanmış; süreç, hedef kitle, yöntem ve bağlantı LST.012'de gerçek yayın kaydı olarak tutulmuştur. Hedef kitleye ayrı duyuru/bilgilendirme henüz doğrulanmamıştır.",
        "SRÇ.004; Confluence yayını; LST.012; SRÇ.020",
        "Hedef kitleye gerçek bilgilendirme yapılmalı ve duyuru/katılım kaydı LST.012 veya doğal kaynakla ilişkilendirilmelidir.",
    ),
    "PIM.1.BP3": RowUpdate(
        "VAR",
        "SRÇ.004 süreç tanımı, PRS.002, KLV.002, KLV.003, süreç özel LST.007-LST.010 ve boş FRM.001 güncel şablonlarla uyumlu tek bir paket olarak tamamlanmış ve Confluence'ta yayımlanmıştır.",
        "SRÇ.004; PRS.002; KLV.002; KLV.003; SRÇ.004 altındaki LST.007-LST.010 ve boş FRM.001; Confluence yayını",
        "-",
    ),
    "PIM.1.BP4": RowUpdate(
        "VAR",
        "Standart süreçlerin beklenen performansı için yönetilebilir üç ölçüm; veri kaynağı, hesaplama, hedef/eşik, sıklık, sorumlu ve sapma yaklaşımıyla tanımlanmıştır. Gerçek sonuç verisi BP6 ve GP.3.2.6 kapsamında ayrı eksik olarak izlenmektedir.",
        "LST.009 (SRÇ.004)",
        "-",
    ),
    "PIM.1.BP5": RowUpdate(
        "VAR",
        "Süreç amacı ve zorunlu sonuçları koruyan uyarlama kuralları; gerekçe, etki, onay ve SRÇ.018 değişiklik yolu ile tutarlı biçimde tanımlanmış ve yayımlanmıştır.",
        "KLV.002; PRS.002; SRÇ.004; SRÇ.018",
        "-",
    ),
    "GP.2.1.1": RowUpdate(
        "VAR",
        "Süreç tasarım paketinin tamlığı, zamanında gözden geçirilmesi ve zamanında yayın/bilgilendirme için hedef ve eşikler tanımlıdır.",
        "LST.009 (SRÇ.004)",
        "-",
    ),
    "GP.2.1.5": RowUpdate(
        "DAĞINIK",
        "Gerekli insan rolleri, araçlar, altyapı, erişim koşulları ve bilgi kaynakları tanımlanmış; Confluence ve repository fiilen kullanılmıştır. Kurumsal erişim/yetkilendirme ve kaynak tahsis kayıtları paketle tekil olarak ilişkilendirilmemiştir.",
        "SRÇ.004 Araçlar ve Altyapı bölümü; LST.010 (SRÇ.004); LST.011; Confluence ve Git geçmişi",
        "Gerekli erişim, yetkilendirme ve kaynak tahsisi doğal kaynak sistem kayıtlarıyla doğrulanmalıdır.",
    ),
    "GP.2.1.6": RowUpdate(
        "DAĞINIK",
        "Süreç, doküman ve rol arayüzleri LST.007 ile LST.010'da ayrıntılı ve karşılıklı olarak tanımlanmıştır. Gerçek hedef kitle iletişimi henüz doğrulanmamıştır.",
        "LST.007 (SRÇ.004); LST.010 (SRÇ.004); LST.012",
        "Hedef kitle ve ilgili taraf iletişimi LST.012 veya eşdeğer doğal kaynak kaydıyla kanıtlanmalıdır.",
    ),
    "GP.2.2.2": RowUpdate(
        "VAR",
        "Aktif şablonlar, doküman kod/ad kuralları, repository yerleşimi, erişim/yayın yaklaşımı ve iş ürünü kalite kriterleri süreç paketi için tanımlanmıştır.",
        "LST.008 (SRÇ.004); aktif şablonlar; LST.011; SRÇ.001; KLV.003",
        "-",
    ),
    "GP.2.2.3": RowUpdate(
        "VAR",
        "SRÇ.004 paketi tanımlı sayfa kimlikleri ve parent yapısı korunarak yerelde ve Git'te kontrol edilmiş, ardından Confluence'ta yayımlanmıştır.",
        "SRÇ.004 süreç tasarım paketi; Confluence sayfa kimlikleri ve revizyon geçmişi; Git commit geçmişi; yerel doğrulama raporları",
        "-",
    ),
    "GP.2.2.4": RowUpdate(
        "DAĞINIK",
        "Paket aktif şablon, adlandırma, yerleşim, BP/GP izlenebilirliği ve görsel-kaynak tutarlılığı bakımından yerel olarak gözden geçirilmiş; kullanıcı incelemesindeki düzeltmeler uygulanarak yayımlanmıştır. Ayrı formal LST.003 bulgu/kapanış kaydı tamamlanmamıştır.",
        "KLV.003; bu FRM.001 Değerlendirme #1; SRÇ.004 bütünsel yerel gözden geçirme raporu; Confluence yayını",
        "Yetkili gözden geçirme, bulgu, düzeltme ve kapanış bilgileri LST.003 veya eşdeğer formal kayıtla tamamlanmalıdır.",
    ),
    "GP.3.1.1": RowUpdate(
        "VAR",
        "SRÇ.004 standart süreci ile PRS.002 uygulama adımları, kontrol kapıları, zorunlu tasarım paketi ve bakım yaklaşımı yayımlanmıştır.",
        "SRÇ.004; PRS.002; KLV.002; KLV.003",
        "-",
    ),
    "GP.3.1.2": RowUpdate(
        "VAR",
        "Süreçlerin ve ilgili dokümanların sırası, girdileri, çıktıları ve karşılıklı etkileşimleri LST.007 ile Mermaid diyagramında tutarlı biçimde tanımlanmıştır.",
        "LST.007 (SRÇ.004); SRÇ.004 Süreç Akışı; Mermaid kaynakları ve PNG görselleri",
        "-",
    ),
    "GP.3.1.3": RowUpdate(
        "VAR",
        "Standart süreci gerçekleştirecek roller; sorumluluk, yetki, asgari yetkinlik, vekâlet ve RACI boyutlarıyla tanımlanmıştır.",
        "LST.010 (SRÇ.004); SRÇ.004",
        "-",
    ),
    "GP.3.1.5": RowUpdate(
        "VAR",
        "Standart sürecin etkinlik ve uygunluğunu izlemek için üç sınırlı ölçüm, veri kaynakları, hedef/eşikler, sıklık, sorumlular ve sapma yaklaşımı tanımlanmıştır. Gerçek veri toplama GP.3.2.6 kapsamında ayrı izlenir.",
        "LST.009 (SRÇ.004); bu FRM.001 Değerlendirme #1",
        "-",
    ),
    "GP.3.2.1": RowUpdate(
        "DAĞINIK",
        "Tanımlı süreç paketi onaylı/aktif doküman yapısıyla Confluence'ta kullanıma sunulmuştur. Hedef kitle bilgilendirmesi ile belirli kurumsal/proje bağlamında kullanım ve uygunluk kanıtı henüz tamamlanmamıştır.",
        "SRÇ.004; PRS.002; Confluence yayını; LST.012",
        "Hedef kitle bilgilendirmesi tamamlanmalı ve ilk gerçek kullanım bağlamı/uygunluk kanıtı kaydedilmelidir.",
    ),
    "GP.3.2.2": RowUpdate(
        "DAĞINIK",
        "Süreç sahibi, gözden geçiren, onaylayan ve uygulama rolleri dokümanlarda ve RACI matrisinde atanmıştır. Hedef kitleye resmî rol/sorumluluk duyurusu henüz doğrulanmamıştır.",
        "SRÇ.004; LST.010 (SRÇ.004); LST.012",
        "Onaylanan rol, sorumluluk ve yetkiler hedef kitleye duyurulmalı ve iletişim kaydı LST.012 veya doğal kaynakta tutulmalıdır.",
    ),
    "GP.3.2.4": RowUpdate(
        "DAĞINIK",
        "Süreç tanımı, prosedür, kılavuzlar, şablonlar ve süreç özel kayıtlar Confluence'ta yayımlanarak bilgi kaynağı sağlanmıştır. İnsan kaynağı tahsisi ve hedef kitle kullanımı formal kayıtla doğrulanmamıştır.",
        "SRÇ.004 süreç tasarım paketi; Confluence yayını; LST.008; LST.010; LST.011",
        "Gerekli insan kaynağı tahsisi ve bilgi kaynaklarının hedef kitlece kullanıma sunulduğu doğrulanmalıdır.",
    ),
    "GP.3.2.5": RowUpdate(
        "DAĞINIK",
        "Confluence, Git repository, yerel görüntüleyici ve VPN tabanlı altyapı tanımlanmış ve paket oluşturma/yayınında fiilen kullanılmıştır. Kurumsal erişim, yetkilendirme, destek ve sürdürme kayıtları paketle ilişkilendirilmemiştir.",
        "SRÇ.004 Araçlar ve Altyapı bölümü; LST.011; Confluence; Git repository; yerel görüntüleyici; VPN",
        "Erişim, yetkilendirme, destek ve sürdürme kanıtları doğal kaynak sistemlerde doğrulanmalıdır.",
    ),
}

# Fixed pre-refresh baseline. Keeping it explicit makes the report repeatable when
# the in-place refresh script is run again on the same Assessment #1 pages.
SRC001_BASELINE = {
    "SUP.7.BP2": "%90 - VAR",
    "SUP.7.BP3": "%85 - VAR",
    "SUP.7.BP4": "%80 - VAR",
    "SUP.7.BP5": "%85 - VAR",
    "SUP.7.BP7": "%55 - DAĞINIK",
    "SUP.7.BP8": "%60 - DAĞINIK",
    "GP.2.1.5": "%60 - DAĞINIK",
    "GP.2.1.6": "%65 - DAĞINIK",
    "GP.2.2.2": "%75 - VAR",
    "GP.2.2.3": "%60 - DAĞINIK",
    "GP.3.1.1": "%90 - VAR",
    "GP.3.1.2": "%85 - VAR",
    "GP.3.1.4": "%70 - VAR",
    "GP.3.2.1": "%55 - DAĞINIK",
    "GP.3.2.2": "%60 - DAĞINIK",
    "GP.3.2.4": "%60 - DAĞINIK",
    "GP.3.2.5": "%70 - VAR",
}
SRC004_BASELINE = {
    "PIM.1.BP1": "ZAYIF",
    "PIM.1.BP2": "ZAYIF",
    "PIM.1.BP3": "ZAYIF",
    "PIM.1.BP4": "ZAYIF",
    "PIM.1.BP5": "ZAYIF",
    "GP.2.1.1": "ZAYIF",
    "GP.2.1.5": "ZAYIF",
    "GP.2.1.6": "ZAYIF",
    "GP.2.2.2": "ZAYIF",
    "GP.2.2.3": "ZAYIF",
    "GP.2.2.4": "YOK",
    "GP.3.1.1": "ZAYIF",
    "GP.3.1.2": "ZAYIF",
    "GP.3.1.3": "ZAYIF",
    "GP.3.1.5": "ZAYIF",
    "GP.3.2.1": "YOK",
    "GP.3.2.2": "ZAYIF",
    "GP.3.2.4": "ZAYIF",
    "GP.3.2.5": "ZAYIF",
}
SRC001_OLD_BP_SCORES = [85, 90, 85, 80, 85, 55, 55, 60]
SRC001_OLD_GP_SCORES = [75, 55, 40, 80, 60, 65, 85, 75, 60, 50, 90, 85, 75, 70, 55, 55, 60, 35, 60, 70, 40]
SRC004_OLD_COUNTS = {"VAR": 3, "DAĞINIK": 0, "ZAYIF": 18, "YOK": 6}


SRC001_ACTIONS = [
    ["Yüksek", "SRÇ.001 için rol bazlı yetkinlikler tanımlanmalı; ilgili personele süreç eğitimi/bilgilendirmesi verilmeli ve kayıtları tutulmalıdır.", "GP 3.2.3", "Yeniden planlanmalı"],
    ["Yüksek", "LST.009 kapsamında gerçekleşen performans verileri toplanmalı, analiz edilmeli ve iyileştirme kararlarıyla ilişkilendirilmelidir.", "GP 3.2.6; GP 3.1.5; GP 2.1.2", "Yeniden planlanmalı"],
    ["Yüksek", "Performans sapmaları için neden, karar, sorumlu, yeniden planlama ve kapanış bilgilerini içeren sistematik izleme kaydı oluşturulmalıdır.", "GP 2.1.3", "Yeniden planlanmalı"],
    ["Yüksek", "SRÇ.001 ve temel destek dokümanları için gerçek gözden geçirme, bulgu, çözüm, kapanış ve yayın onayı kayıtları LST.003 üzerinden tamamlanmalıdır.", "SUP.7.BP6; GP 2.2.4", "Yeniden planlanmalı"],
    ["Orta", "Confluence yayın kaydını tamamlayacak hedef kitle bilgilendirmesi yapılmalı; duyuru/teslim ve gerektiğinde teyit kanıtı LST.012 ile ilişkilendirilmelidir.", "SUP.7.BP7; GP 2.1.6; GP 3.2.2", "Yeniden planlanmalı"],
    ["Orta", "Son doküman ve şablon revizyonları LST.002'ye işlenmeli; kontrollü dokümanların değişiklik, sürüm ve baseline ilişkisi SRÇ.016 ile uyumlu hale getirilmelidir.", "SUP.7.BP8; GP 2.2.3", "Yeniden planlanmalı"],
    ["Orta", "Soru Bankası Projesi için SRÇ.001 uyarlamaları, gerekçeleri ve standart sürece uygunluk kontrolü kayıt altına alınmalıdır.", "GP 3.2.1", "Yeniden planlanmalı"],
    ["Orta", "SRÇ.001 için gerekli insan kaynağı ve zaman tahsisi ile fiili kaynak kullanımı kayıt altına alınmalıdır.", "GP 2.1.5; GP 3.2.4", "Yeniden planlanmalı"],
]

SRC004_ACTIONS = [
    ["1", "SRÇ.004 ve rol/sorumlulukları hedef kitleye duyurmak; gerçek bilgilendirme ve gerektiğinde katılım/teyit kanıtını LST.012 ile ilişkilendirmek", "PIM.1.BP2; GP.2.1.6; GP.3.2.1; GP.3.2.2", "Süreç sahibi tarafından planlanacak"],
    ["2", "LST.009 için ilk gerçek veri toplama dönemini işletmek; sonuçları, sapmaları ve kararları kaydetmek", "PIM.1.BP6; GP.2.1.2; GP.2.1.3; GP.3.2.6", "İlk ölçüm dönemi sonunda"],
    ["3", "Yetkili gözden geçirme, bulgu, düzeltme ve kapanış bilgilerini LST.003 veya eşdeğer formal kayıtla tamamlamak", "GP.2.2.4", "Süreç sahibi tarafından planlanacak"],
    ["4", "Rol bazlı yetkinlik ihtiyacını doğrulamak; gerekiyorsa SRÇ.020 kapsamında eğitim ve katılım kaydı oluşturmak", "GP.3.2.3", "Kurumsal kullanım sırasında"],
    ["5", "İnsan kaynağı tahsisi ile erişim, yetkilendirme, destek ve sürdürme kanıtlarını doğal kaynak sistemlerde doğrulamak", "GP.2.1.5; GP.3.2.4; GP.3.2.5", "Süreç sahibi tarafından planlanacak"],
]


def esc(value: object) -> str:
    return html.escape(str(value), quote=False)


def clean(value: str) -> str:
    value = re.sub(r"<br\s*/?>", " ", value, flags=re.IGNORECASE)
    value = re.sub(r"<[^>]+>", " ", value, flags=re.DOTALL)
    return re.sub(r"\s+", " ", html.unescape(value)).strip()


def parse_table(block: str) -> tuple[list[str], list[list[str]]]:
    headers = [clean(x) for x in re.findall(r"<th[^>]*>(.*?)</th>", block, flags=re.DOTALL)]
    tbody = re.search(r"<tbody[^>]*>(.*?)</tbody>", block, flags=re.DOTALL)
    rows: list[list[str]] = []
    if tbody:
        for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", tbody.group(1), flags=re.DOTALL):
            rows.append(re.findall(r"<td[^>]*>(.*?)</td>", tr, flags=re.DOTALL))
    return headers, rows


def render_table(headers: list[str], rows: list[list[str]]) -> str:
    head = "".join(f"<th>{esc(h)}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>" for row in rows)
    return f'<table class="wrapped"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>'


def normalize_ref(row: list[str]) -> str | None:
    text = " ".join(clean(cell) for cell in row[:2])
    bp = re.search(r"(?:SUP\.7|PIM\.1)\.BP\d+", text, flags=re.IGNORECASE)
    if bp:
        return bp.group(0).upper()
    gp = re.search(r"GP[\.\s]+([23])\.([12])\.([1-6])", text, flags=re.IGNORECASE)
    if gp:
        return f"GP.{gp.group(1)}.{gp.group(2)}.{gp.group(3)}"
    return None


def update_summary(storage: str, values: dict[str, str]) -> str:
    for match in re.finditer(r"<table.*?</table>", storage, flags=re.DOTALL):
        headers, rows = parse_table(match.group(0))
        if headers != ["Alan", "Değer"]:
            continue
        labels = {clean(row[0]) for row in rows if row}
        if "Değerlendirilen Süreç" not in labels:
            continue
        for row in rows:
            if len(row) > 1 and clean(row[0]) in values:
                row[1] = esc(values[clean(row[0])])
        return storage[:match.start()] + render_table(headers, rows) + storage[match.end():]
    raise RuntimeError("Değerlendirme özet tablosu bulunamadı.")


def update_matrix(storage: str, updates: dict[str, RowUpdate]) -> tuple[str, list[tuple[str, str, str]]]:
    output: list[str] = []
    last = 0
    changes: list[tuple[str, str, str]] = []
    found: set[str] = set()
    for match in re.finditer(r"<table.*?</table>", storage, flags=re.DOTALL):
        output.append(storage[last:match.start()])
        headers, rows = parse_table(match.group(0))
        status_idx = headers.index("Durum") if "Durum" in headers else None
        note_idx = headers.index("Mevcut Karşılama") if "Mevcut Karşılama" in headers else None
        evidence_idx = headers.index("Karşılayan Doküman / Kayıt") if "Karşılayan Doküman / Kayıt" in headers else None
        action_idx = headers.index("Eksik / Tamamlayıcı Aksiyon") if "Eksik / Tamamlayıcı Aksiyon" in headers else None
        changed_table = False
        if None not in (status_idx, note_idx, evidence_idx, action_idx):
            for row in rows:
                ref = normalize_ref(row)
                if ref not in updates:
                    continue
                item = updates[ref]
                old = clean(row[status_idx])
                row[status_idx] = esc(item.value)
                row[note_idx] = esc(item.note)
                row[evidence_idx] = esc(item.evidence)
                row[action_idx] = esc(item.action)
                found.add(ref)
                changed_table = True
                if old != item.value:
                    changes.append((ref, old, item.value))
        output.append(render_table(headers, rows) if changed_table else match.group(0))
        last = match.end()
    output.append(storage[last:])
    missing = set(updates) - found
    if missing:
        raise RuntimeError(f"Değerlendirme satırları bulunamadı: {sorted(missing)}")
    return "".join(output), changes


def update_actions(storage: str, new_rows: list[list[str]]) -> str:
    for match in re.finditer(r"<table.*?</table>", storage, flags=re.DOTALL):
        headers, _rows = parse_table(match.group(0))
        if "Öncelik" in headers and any("Aksiyon" in h for h in headers):
            rows = [[esc(cell) for cell in row] for row in new_rows]
            return storage[:match.start()] + render_table(headers, rows) + storage[match.end():]
    raise RuntimeError("Öncelikli tamamlayıcı aksiyon tablosu bulunamadı.")


def build_view(title: str, storage: str) -> str:
    return (
        '<!doctype html><html lang="tr"><head><meta charset="utf-8">'
        f"<title>{esc(title)}</title><style>{CSS}</style></head><body>"
        f'<main class="confluence-page"><h1>{esc(title)}</h1>{storage}</main>'
        "</body></html>\n"
    )


def assessment_dirs() -> set[str]:
    return {p.name for p in REVIEWS.iterdir() if p.is_dir() and "degerlendirme" in p.name}


def read_meta(page_dir: Path) -> dict[str, object]:
    return yaml.safe_load((page_dir / "page.yaml").read_text(encoding="utf-8"))


def process_page(
    page_dir: Path,
    summary_values: dict[str, str],
    updates: dict[str, RowUpdate],
    actions: list[list[str]],
) -> tuple[list[tuple[str, str, str]], dict[str, object], dict[str, object]]:
    before_meta = read_meta(page_dir)
    storage_path = page_dir / "body.storage.xhtml"
    storage = storage_path.read_text(encoding="utf-8")
    storage = update_summary(storage, summary_values)
    storage, changes = update_matrix(storage, updates)
    storage = update_actions(storage, actions)
    storage_path.write_text(storage, encoding="utf-8")
    (page_dir / "body.view.html").write_text(
        build_view(str(before_meta["title"]), storage), encoding="utf-8"
    )
    after_meta = read_meta(page_dir)
    if before_meta != after_meta:
        raise RuntimeError(f"page.yaml değiştirildi: {page_dir}")
    return changes, before_meta, after_meta


def score_from(value: str) -> int:
    match = re.search(r"%(\d+)", value)
    if not match:
        raise ValueError(value)
    return int(match.group(1))


def extract_scores(page_dir: Path) -> tuple[list[int], list[int]]:
    storage = (page_dir / "body.storage.xhtml").read_text(encoding="utf-8")
    bp: list[int] = []
    gp: list[int] = []
    for match in re.finditer(r"<table.*?</table>", storage, flags=re.DOTALL):
        headers, rows = parse_table(match.group(0))
        if "Durum" not in headers:
            continue
        idx = headers.index("Durum")
        for row in rows:
            ref = normalize_ref(row)
            if not ref or idx >= len(row) or "%" not in clean(row[idx]):
                continue
            (bp if ".BP" in ref else gp).append(score_from(clean(row[idx])))
    return bp, gp


def counts(page_dir: Path) -> dict[str, int]:
    result = {"VAR": 0, "DAĞINIK": 0, "ZAYIF": 0, "YOK": 0}
    storage = (page_dir / "body.storage.xhtml").read_text(encoding="utf-8")
    for match in re.finditer(r"<table.*?</table>", storage, flags=re.DOTALL):
        headers, rows = parse_table(match.group(0))
        if "Durum" not in headers:
            continue
        idx = headers.index("Durum")
        for row in rows:
            if normalize_ref(row) and idx < len(row):
                value = clean(row[idx])
                if value in result:
                    result[value] += 1
    return result


def main() -> None:
    dirs_before = assessment_dirs()

    _actual_src001_changes, src001_before, src001_after = process_page(
        SRC001_DIR,
        {
            "Değerlendirme Kapsamı": "PA 1.1: SUP.7 (BP1-BP8) | PA 2.1: GP 2.1.1-GP 2.1.6 | PA 2.2: GP 2.2.1-GP 2.2.4 | PA 3.1: GP 3.1.1-GP 3.1.5 | PA 3.2: GP 3.2.1-GP 3.2.6",
            "Değerlendirme Tarihi": "14-07-2026",
            "Değerlendirmeyi Onaylayan": "Mustafa Nusret SARISAKAL - BİD Başkanı",
            "Değerlendirme Sonucu": (
                "SRÇ.001 Dokümantasyon Süreci; güncel şablon ailesi, hedef kitle ve yayın/erişim "
                "gereksinimleri, araçlar/altyapı tanımları, süreç ve doküman etkileşimleri ile "
                "Confluence/Git kontrollü yayın ve bakım kanıtları bakımından güçlenmiştir. BP "
                "karşılama ortalaması %79, PA/GP karşılama ortalaması %68 ve birleşik gösterge %74 - "
                "VAR'dır. Buna karşılık formal gözden geçirme/onay kayıtları, hedef kitleye ayrı "
                "bilgilendirme, performans sapması ve gerçek ölçüm sonuçları, bağlama özgü uyarlama, "
                "yetkinlik/eğitim ve insan kaynağı tahsis kanıtları tamamlanmamıştır."
            ),
        },
        SRC001_UPDATES,
        SRC001_ACTIONS,
    )
    _actual_src004_changes, src004_before, src004_after = process_page(
        SRC004_DIR,
        {
            "Süreç Durumu": "Aktif",
            "Değerlendirme Sonucu": (
                "SRÇ.004 - Süreç Kurulumu Süreci; süreç mimarisi, standart süreç "
                "tanımı, performans beklentileri, uyarlama kuralları, rol/RACI, iş ürünü ve kontrol "
                "yapıları tamamlanıp Confluence'ta yayımlanmış aktif bir süreç paketidir. PIM.1 BP "
                "dağılımı 4 VAR, 1 DAĞINIK ve 1 YOK; PA/GP dağılımı 10 VAR, 7 DAĞINIK, 1 "
                "ZAYIF ve 3 YOK'tur. Hedef kitleye gerçek duyuru, ilk performans ve kullanım verileri, formal "
                "bulgu/kapanış kaydı, yetkinlik/eğitim ve erişim-kaynak tahsis kanıtları hâlâ "
                "tamamlanmalıdır."
            ),
        },
        SRC004_UPDATES,
        SRC004_ACTIONS,
    )

    dirs_after = assessment_dirs()
    if dirs_before != dirs_after:
        raise RuntimeError("Değerlendirme dizin seti değişti; yeni doküman oluşturulmamalıydı.")
    if src001_before["page_id"] != src001_after["page_id"] or src004_before["page_id"] != src004_after["page_id"]:
        raise RuntimeError("Mevcut Confluence sayfa kimliklerinden biri değişti.")

    src001_new_bp, src001_new_gp = extract_scores(SRC001_DIR)
    src004_new_counts = counts(SRC004_DIR)
    src001_changes = [
        (ref, SRC001_BASELINE[ref], item.value)
        for ref, item in SRC001_UPDATES.items()
        if SRC001_BASELINE[ref] != item.value
    ]
    src004_changes = [
        (ref, SRC004_BASELINE[ref], item.value)
        for ref, item in SRC004_UPDATES.items()
        if SRC004_BASELINE[ref] != item.value
    ]
    old_bp_avg = round(sum(SRC001_OLD_BP_SCORES) / len(SRC001_OLD_BP_SCORES))
    new_bp_avg = round(sum(src001_new_bp) / len(src001_new_bp))
    old_gp_avg = round(sum(SRC001_OLD_GP_SCORES) / len(SRC001_OLD_GP_SCORES))
    new_gp_avg = round(sum(src001_new_gp) / len(src001_new_gp))
    old_total = round((sum(SRC001_OLD_BP_SCORES) / len(SRC001_OLD_BP_SCORES) + sum(SRC001_OLD_GP_SCORES) / len(SRC001_OLD_GP_SCORES)) / 2)
    new_total = round((sum(src001_new_bp) / len(src001_new_bp) + sum(src001_new_gp) / len(src001_new_gp)) / 2)

    lines = [
        "# Süreç Gözden Geçirmeleri - Değerlendirme #1 Yenileme Raporu",
        "",
        "- Yenileme tarihi: 14-07-2026",
        "- Yeni Değerlendirme #2 oluşturulmadı.",
        f"- SRÇ.001 sayfa kimliği korundu: {src001_after['page_id']}",
        f"- SRÇ.004 sayfa kimliği korundu: {src004_after['page_id']}",
        "- Değerlendirme başlıkları, parent bilgileri ve sayfa dizinleri korundu.",
        "",
        "## SRÇ.001 değişen puanlar",
        "",
        "| BP / GP | Eski | Yeni |",
        "|---|---:|---:|",
        *[f"| {ref} | {old} | {new} |" for ref, old, new in src001_changes],
        "",
        "### SRÇ.001 toplu göstergeler",
        "",
        f"- BP ortalaması: %{old_bp_avg} → %{new_bp_avg}",
        f"- PA/GP ortalaması: %{old_gp_avg} → %{new_gp_avg}",
        f"- Birleşik gösterge: %{old_total} - {'VAR' if old_total >= 70 else 'DAĞINIK'} → %{new_total} - {'VAR' if new_total >= 70 else 'DAĞINIK'}",
        "- Puanı değişmeden kanıt/notu güncellenen satır: GP.2.1.6 (%65 - DAĞINIK).",
        "- Değerlendirme tarihi: 13-02-2026 → 14-07-2026.",
        "- Değerlendirme kapsamındaki yazım hatası: GP 2.2.1-GP 2.1.4 → GP 2.2.1-GP 2.2.4.",
        "- Değerlendirmeyi onaylayan: Levent BAYEZİT - Süreç Sahibi → Mustafa Nusret SARISAKAL - BİD Başkanı.",
        "",
        "## SRÇ.004 değişen durumlar",
        "",
        "| BP / GP | Eski | Yeni |",
        "|---|---|---|",
        *[f"| {ref} | {old} | {new} |" for ref, old, new in src004_changes],
        "",
        "### SRÇ.004 toplu göstergeler",
        "",
        "- Süreç durumu: Taslak → Aktif",
        "- Tüm BP/GP dağılımı: "
        f"{SRC004_OLD_COUNTS['VAR']} VAR, {SRC004_OLD_COUNTS['DAĞINIK']} DAĞINIK, "
        f"{SRC004_OLD_COUNTS['ZAYIF']} ZAYIF, {SRC004_OLD_COUNTS['YOK']} YOK → "
        f"{src004_new_counts['VAR']} VAR, {src004_new_counts['DAĞINIK']} DAĞINIK, "
        f"{src004_new_counts['ZAYIF']} ZAYIF, {src004_new_counts['YOK']} YOK",
        "- BP6, GP.2.1.3, GP.3.2.3 ve GP.3.2.6; gerçek kullanım, sapma, yetkinlik/eğitim veya ölçüm verisi bulunmadığı için YOK olarak korundu.",
        "- GP.2.1.2, izleme sonucu bulunmadığı için ZAYIF olarak korundu.",
        "",
        "## Kanıta dayalı sınırlar",
        "",
        "- LST.012, Confluence yayınını doğruluyor; hedef kitleye ayrı duyuru yapıldığını doğrulamıyor.",
        "- LST.009 ölçüm tanımları mevcut; gerçek sonuç ve analiz verisi henüz yok.",
        "- Rol ve yetkinlik tanımları mevcut; eğitim/katılım ve kurumsal erişim-yetkilendirme kanıtları henüz yok.",
        "",
    ]
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"[DONE] SRÇ.001 değişen puan sayısı: {len(src001_changes)}")
    print(f"[DONE] SRÇ.004 değişen durum sayısı: {len(src004_changes)}")
    print(f"[DONE] Rapor: {REPORT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
