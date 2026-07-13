#!/usr/bin/env python3
"""Create SRÇ.001 Assessment #1 without changing the customized form structure.

Rules:
- Source form under SRÇ.001 is copied as-is.
- Headings, table headers, Turkish BP/GP descriptions and expected-content cells are preserved.
- Only evidence, assessment result, auditor note/current coverage and action cells are filled.
- Every BP/GP is evaluated individually against the exact ISO/IEC 15504-5:2006
  requirement loaded from resources/standards/spice_practices.yaml.
"""
from __future__ import annotations

import html
import re
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
CONFLUENCE_DIR = ROOT / "confluence"
INDEX_PATH = CONFLUENCE_DIR / "index.yaml"
STANDARD_PATH = ROOT / "resources/standards/spice_practices.yaml"
SRC_FORM_DIR = ROOT / "confluence/pages/000-root-iuc-bidb-spice-2026-level-3/01-surec-dokumanlari/iuc-bidb-src-001-dokumantasyon-sureci/iuc-bidb-frm-001-surec-gozden-gecirme-formu-iuc-bidb-src-001"
TARGET_PARENT_DIR = ROOT / "confluence/pages/000-root-iuc-bidb-spice-2026-level-3/91-ic-denetimler/surec-gozden-gecirmeleri"
TARGET_PARENT_ID = "137265917"
TARGET_PARENT_TITLE = "Süreç Gözden Geçirmeleri"
TARGET_SLUG = "iuc-bidb-frm-001-surec-gozden-gecirme-formu-iuc-bidb-src-001-degerlendirme-1"
TARGET_TITLE = "İÜC.BİDB.FRM.001 - Süreç Gözden Geçirme Formu (İÜC.BİDB.SRÇ.001) - Değerlendirme #1"
TARGET_DIR = TARGET_PARENT_DIR / TARGET_SLUG

CSS = """
body{margin:0;background:#fff;color:#172b4d;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;line-height:1.55}
.confluence-page{max-width:1180px;margin:0 auto;padding:32px 24px 56px}
h1,h2,h3,h4,h5,h6{margin:1.4em 0 .55em;line-height:1.25;color:#0f172a}
h1{margin-top:0;padding-bottom:12px;border-bottom:1px solid #d8dee4}
p{margin:0 0 12px} table{width:100%;border-collapse:collapse;margin:16px 0;table-layout:auto}
th,td{border:1px solid #c9d1d9;padding:8px 10px;vertical-align:top}
th{background:#f6f8fa;font-weight:600;text-align:left}
""".strip()

EXPECTED_BP_IDS = [f"SUP.7.BP{i}" for i in range(1, 9)]
EXPECTED_GP_IDS = [
    *[f"GP.2.1.{i}" for i in range(1, 7)],
    *[f"GP.2.2.{i}" for i in range(1, 5)],
    *[f"GP.3.1.{i}" for i in range(1, 6)],
    *[f"GP.3.2.{i}" for i in range(1, 7)],
]

# Scores are conservative and evidence-based. A score of 70 or more is VAR.
EVAL: dict[str, dict[str, Any]] = {
    "SUP.7.BP1": {"pct": 85, "evidence": ["İÜC.BİDB.SRÇ.001", "İÜC.BİDB.PRS.001", "İÜC.BİDB.LST.005.Ş", "Soru Bankası Projesi / İÜC.BİDB.LST.005 (SB)"], "note": "Standart; neyin, hangi organizasyonel yapı içinde ve ürün/hizmet yaşam döngüsünün hangi aşamalarında dokümante edileceğini kapsayan bir strateji ister. SRÇ.001 kurumsal yaklaşımı, PRS.001 yazılım projesi stratejisini, LST.005.Ş ise yaşam döngüsü doküman üretimini tanımlar. SB kaydı henüz taslak olsa da strateji seviyesi büyük ölçüde karşılanmaktadır.", "action": "-"},
    "SUP.7.BP2": {"pct": 90, "evidence": ["İÜC.BİDB.KLV.001", "İÜC.BİDB.SRÇ.XXX.Ş", "İÜC.BİDB.PRS.XXX.Ş", "İÜC.BİDB.KLV.XXX.Ş", "LST şablon ailesi"], "note": "Standart, dokümanların geliştirilmesi, değiştirilmesi ve sürdürülmesi için standartlar kurulmasını ister. KLV.001 ile yazım/sürüm kuralları; güncel şablon ailesi ile yapı ve içerik standartları tanımlanmıştır.", "action": "-"},
    "SUP.7.BP3": {"pct": 85, "evidence": ["İÜC.BİDB.KLV.001", "SRÇ/PRS/KLV/LST şablonları", "İÜC.BİDB.LST.001", "Doküman sürüm geçmişleri"], "note": "Standart; format, başlık, tarih, tanımlayıcı, sürüm geçmişi, hazırlayan, gözden geçiren, onaylayan, içerik ana hatları, amaç ve dağıtım bilgilerini ister. Bu alanların büyük bölümü şablonlarda ve KLV.001'de bulunur. Dağıtım hedef kitlesi bilgisi her dokümanda aynı açıklıkta değildir.", "action": "-"},
    "SUP.7.BP4": {"pct": 80, "evidence": ["İÜC.BİDB.LST.001", "İÜC.BİDB.LST.005.Ş", "Soru Bankası Projesi / LST.005 (SB)", "SRÇ.001 alt kayıtları"], "note": "Standart, belirli bir yaşam döngüsü geliştirmesinde üretilecek dokümanların belirlenmesini ister. Genel doküman envanteri ve yaşam döngüsü matrisi vardır; proje özel matrisin gerçek kanıtlarla tamamlanması gerekmektedir.", "action": "-"},
    "SUP.7.BP5": {"pct": 85, "evidence": ["İÜC.BİDB.SRÇ.001", "İÜC.BİDB.PRS.001", "İÜC.BİDB.KLV.001", "İÜC.BİDB.LST.001", "SRÇ.001 altındaki LST.007/LST.008/LST.009/LST.010", "Confluence ve Git geçmişi"], "note": "Standart, dokümanların gerekli süreç noktalarında belirlenmiş standart ve politikalara göre geliştirilmesini ister. SRÇ.001 doküman seti üretilmiştir; proje yaşam döngüsü boyunca üretimin sürekliliği SB örneğinde henüz tam kanıtlanmamıştır.", "action": "-"},
    "SUP.7.BP6": {"pct": 55, "evidence": ["SRÇ.001 altındaki özelleştirilmiş FRM.001", "İÜC.BİDB.LST.003.Ş", "Doküman sürüm geçmişleri", "Confluence revizyon geçmişi"], "note": "Standart, dağıtım öncesi gözden geçirme ve yayın öncesi yetkilendirme ister; ayrıca doğrulama/validasyon ve paydaş katılımını not eder. Form ve onay yapısı vardır fakat son revizyonlar için sistematik gerçek LST.003 kayıtları ve bağımsız doğrulama/paydaş kanıtları yetersizdir.", "action": "SRÇ.001, PRS.001, KLV.001, LST.001 ve LST.007 için gerçek gözden geçirme/onay kayıtları LST.003 içinde tamamlanmalı; gerekli paydaş doğrulaması ilişkilendirilmelidir."},
    "SUP.7.BP7": {"pct": 55, "evidence": ["Confluence sayfa ağacı", "İÜC.BİDB.LST.001", "İÜC.BİDB.PRS.001", "Publish raporları"], "note": "Standart, belirlenmiş dağıtım yöntemleri ve medya üzerinden belirli hedef kitlelere dağıtımı ve gerektiğinde teslim teyidini ister. Confluence fiili yayın ortamıdır; ancak hedef kitle, duyuru/teslim ve gerektiğinde alındı teyidi kayıtları sistematik değildir.", "action": "Doküman türü bazında hedef kitle ve dağıtım yöntemi netleştirilmeli; kritik yayınlar için LST.012 veya eşdeğer iletişim/teslim kayıtları tutulmalıdır."},
    "SUP.7.BP8": {"pct": 60, "evidence": ["İÜC.BİDB.LST.002", "Doküman sürüm geçmişleri", "Arşiv - Kaldırılan Şablonlar", "Git commit geçmişi", "İÜC.BİDB.SRÇ.016"], "note": "Standart, dokümanların belirlenmiş stratejiye göre sürdürülmesini; kontrollü/baseline dokümanlarda SUP.8 ile bağlantıyı ister. Sürümleme ve arşiv vardır fakat LST.002 güncelliği ve formal yapılandırma/baseline bağlantısı tam değildir.", "action": "Son doküman ve şablon revizyonları LST.002'ye işlenmeli; kontrollü dokümanların SRÇ.016 kapsamındaki değişiklik/baseline kurallarıyla bağı açıklaştırılmalıdır."},

    "GP.2.1.1": {"pct": 75, "evidence": ["İÜC.BİDB.LST.009 (SRÇ.001)", "İÜC.BİDB.SRÇ.001"], "note": "Standart; kalite, çevrim/frekans, kaynak kullanımı ve süreç sınırları gibi performans amaçlarını; kapsam, varsayım ve kısıtları ister. LST.009 üç temel ölçüm hedefi tanımlar. Kaynak kullanımı ile varsayım/kısıt boyutu sınırlı kalmıştır.", "action": "-"},
    "GP.2.1.2": {"pct": 55, "evidence": ["İÜC.BİDB.SRÇ.001 faaliyetleri", "İÜC.BİDB.LST.009", "FRM.001 değerlendirme yapısı"], "note": "Standart; performans planı, çevrim, kilometre taşları, tahminler, görevler, takvim, iş ürünü gözden geçirmeleri ve fiili izlemeyi birlikte ister. Faaliyetler ve ölçüm seti tanımlıdır; periyotlu uygulama planı, kilometre taşı ve gerçekleşen ölçüm kayıtları yetersizdir.", "action": "Süreç performans çevrimi, ölçüm periyodu, sorumlular, kilometre taşları ve gerçekleşen ölçüm sonuçları kayıt altına alınmalıdır."},
    "GP.2.1.3": {"pct": 40, "evidence": ["FRM.001 değerlendirme kayıtları", "Confluence/Git revizyon geçmişi"], "note": "Standart, performans sorunlarının belirlenmesini, hedef sapmalarında aksiyon alınmasını ve plan/takvimin ayarlanmasını ister. Revizyonlar yapılmış olsa da performans sapması, karar, yeniden planlama ve kapanış kayıtları sistematik değildir.", "action": "Performans sapmaları için neden, karar, aksiyon, sorumlu, yeniden planlama ve kapanış bilgilerini içeren izleme kaydı oluşturulmalıdır."},
    "GP.2.1.4": {"pct": 80, "evidence": ["İÜC.BİDB.LST.010 (SRÇ.001)", "İÜC.BİDB.SRÇ.001 roller bölümü"], "note": "Standart; yürütme ve doğrulama sorumlulukları/yetkileri ile gerekli deneyim, bilgi ve becerilerin tanımlanmasını ister. RACI ve yetkiler güçlüdür; yetkinlik beklentileri daha sınırlı ayrıntıdadır.", "action": "-"},
    "GP.2.1.5": {"pct": 60, "evidence": ["Confluence/repository altyapısı", "İÜC.BİDB.KLV.004", "İÜC.BİDB.LST.011", "İÜC.BİDB.PRS.001"], "note": "Standart, insan ve altyapı kaynaklarının ve gerekli bilginin belirlenmesini, tahsis edilmesini ve kullanılmasını ister. Araçlar ve bilgi alanları mevcuttur; insan kaynağı tahsisi ve kullanım kayıtları formal değildir.", "action": "SRÇ.001 için gerekli insan kaynağı, zaman, araç ve bilgi kaynakları ile bunların tahsis/kullanım durumu kayıt altına alınmalıdır."},
    "GP.2.1.6": {"pct": 65, "evidence": ["İÜC.BİDB.LST.007 (SRÇ.001)", "İÜC.BİDB.LST.010 (SRÇ.001)", "İÜC.BİDB.LST.012.Ş"], "note": "Standart, ilgili tarafların belirlenmesini, sorumlulukların atanmasını, arayüzlerin yönetilmesini ve etkili iletişimi ister. Etkileşim ve RACI tanımlıdır; iletişimin fiilen yürütüldüğünü gösteren yaygınlaştırma/iletişim kayıtları sınırlıdır.", "action": "İlgili taraf iletişimleri ve süreç yaygınlaştırma faaliyetleri LST.012 veya eşdeğer kayıtla kanıtlanmalıdır."},

    "GP.2.2.1": {"pct": 85, "evidence": ["İÜC.BİDB.LST.008 (SRÇ.001)", "Şablon ailesi", "KLV.001"], "note": "Standart; iş ürünü içerik/yapı gereksinimleri, kalite kriterleri ve gözden geçirme/onay kriterlerini ister. LST.008 ve şablonlar bu beklentiyi büyük ölçüde karşılar.", "action": "-"},
    "GP.2.2.2": {"pct": 75, "evidence": ["İÜC.BİDB.KLV.001", "İÜC.BİDB.PRS.001", "İÜC.BİDB.LST.001", "İÜC.BİDB.LST.007"], "note": "Standart; dağıtım, tanımlama, bileşenler, izlenebilirlik/bağımlılıklar ve onay gereksinimlerini ister. Doküman kontrol kuralları ve etkileşimler vardır; bağımlılıkların tüm iş ürünlerinde tekil izlenebilirliği sınırlıdır.", "action": "-"},
    "GP.2.2.3": {"pct": 60, "evidence": ["İÜC.BİDB.LST.001", "Doküman sürüm geçmişleri", "Confluence erişim yapısı", "Git geçmişi", "İÜC.BİDB.LST.002"], "note": "Standart; kontrollü iş ürünlerinin belirlenmesi, değişiklik kontrolü, sürüm/configuration ilişkisi, erişim ve revizyon durumunun görülebilmesini ister. Tanımlama, sürüm ve erişim vardır; değişiklik kontrolü ve configuration/baseline ilişkisi tam değildir.", "action": "Kontrollü doküman kapsamı, değişiklik akışı, sürüm/baseline ilişkisi ve güncel revizyon durumu LST.002 ve SRÇ.016 ile tutarlı hale getirilmelidir."},
    "GP.2.2.4": {"pct": 50, "evidence": ["SRÇ.001 altındaki FRM.001", "İÜC.BİDB.LST.003.Ş", "Confluence revizyon geçmişi"], "note": "Standart, iş ürünlerinin planlı düzenlemelere göre gereksinimlere karşı gözden geçirilmesini ve bulguların çözülmesini ister. Gözden geçirme yapısı vardır; planlı inceleme, bulgu ve kapanış kayıtları yeterince sistematik değildir.", "action": "İş ürünü bazında planlı gözden geçirme, bulgu, sorumlu, çözüm ve kapanış bilgileri LST.003 gerçek kayıtlarında tutulmalıdır."},

    "GP.3.1.1": {"pct": 90, "evidence": ["İÜC.BİDB.SRÇ.001", "İÜC.BİDB.SRÇ.XXX.Ş", "İÜC.BİDB.KLV.002", "İÜC.BİDB.KLV.003", "İÜC.BİDB.PRS.001"], "note": "Standart süreç; temel süreç öğelerini, yayılım bağlamını, uygulama rehberini ve uyarlama kılavuzlarını içermelidir. SRÇ.001 ve destek dokümanları bu yapıyı güçlü biçimde sağlar.", "action": "-"},
    "GP.3.1.2": {"pct": 85, "evidence": ["İÜC.BİDB.LST.007 (SRÇ.001)", "SRÇ.001 süreç akışı ve etkileşimler bölümü"], "note": "Standart, süreç sırası ve diğer süreçlerle etkileşimin bütünleşik sistem olarak belirlenmesini ister. Akış ve etkileşim matrisi mevcuttur.", "action": "-"},
    "GP.3.1.3": {"pct": 75, "evidence": ["İÜC.BİDB.LST.010 (SRÇ.001)", "SRÇ.001 roller bölümü"], "note": "Standart, standart süreci yürütecek rolleri ve yetkinlikleri ister. Roller/RACI tanımlıdır; yetkinliklerin rol bazında ayrıntılı tanımı sınırlıdır.", "action": "-"},
    "GP.3.1.4": {"pct": 70, "evidence": ["İÜC.BİDB.KLV.004", "İÜC.BİDB.LST.011", "Confluence/repository yapısı", "İÜC.BİDB.SRÇ.022"], "note": "Standart, tesis, araç, ağ, yöntem ve çalışma ortamı gereksinimlerini ister. Dokümantasyon altyapısı ve repository yapısı tanımlıdır; çalışma ortamı gereksinimleri kısmen dolaylıdır.", "action": "-"},
    "GP.3.1.5": {"pct": 55, "evidence": ["İÜC.BİDB.LST.009 (SRÇ.001)", "SRÇ.001 altındaki FRM.001", "91 - İç Denetimler"], "note": "Standart, etkinlik/uygunluk izleme yöntemleri, kriter/veri, süreç karakteristikleri, iç denetim ve yönetim gözden geçirme ihtiyacı ile süreç değişikliklerini ister. Yöntemler tanımlı; gerçekleşen veri, iç denetim ve yönetim gözden geçirme kanıtı sınırlıdır.", "action": "LST.009 ölçüm sonuçları dönemsel işlenmeli; iç denetim ve yönetim gözden geçirme kayıtlarıyla süreç değişikliği kararları ilişkilendirilmelidir."},

    "GP.3.2.1": {"pct": 55, "evidence": ["İÜC.BİDB.SRÇ.001", "İÜC.BİDB.KLV.002", "İÜC.BİDB.KLV.003", "Soru Bankası Projesi / LST.005 (SB)"], "note": "Standart, tanımlı sürecin standart süreçten bağlama göre seçilip/uyarlanmasını ve uygunluğunun doğrulanmasını ister. Standart süreç ve uyarlama rehberi vardır; belirli kullanım bağlamında uygulanmış uyarlama ve uygunluk doğrulama kaydı sınırlıdır.", "action": "Soru Bankası Projesi için kullanılan SRÇ.001 uyarlamaları, gerekçeleri ve standart sürece uygunluk kontrolü kayıt altına alınmalıdır."},
    "GP.3.2.2": {"pct": 60, "evidence": ["İÜC.BİDB.LST.010 (SRÇ.001)", "SRÇ.001 roller bölümü", "İÜC.BİDB.LST.012.Ş"], "note": "Standart, rollerin, sorumlulukların ve yetkilerin atanmasını ve duyurulmasını ister. Atama/RACI vardır; fiili iletişim ve kabul kanıtı sınırlıdır.", "action": "Rol ve sorumlulukların ilgili kişilere duyurulduğunu gösteren LST.012 veya eşdeğer iletişim kaydı oluşturulmalıdır."},
    "GP.3.2.3": {"pct": 35, "evidence": ["İÜC.BİDB.LST.010 (SRÇ.001)", "İÜC.BİDB.SRÇ.020 - Eğitim Süreci"], "note": "Standart, atanmış personel için uygun yetkinliklerin belirlenmesini ve süreci uygulayanlara uygun eğitimin sunulmasını ister. Rol tanımları vardır; SRÇ.001'e özel yetkinlik matrisi, eğitim planı ve eğitim kayıtları bulunmamaktadır.", "action": "SRÇ.001 rollerine gerekli yetkinlikler tanımlanmalı; ilgili personele eğitim/bilgilendirme verilmeli ve kayıtları tutulmalıdır."},
    "GP.3.2.4": {"pct": 60, "evidence": ["Confluence doküman alanı", "İÜC.BİDB.PRS.001", "İÜC.BİDB.LST.010", "İÜC.BİDB.LST.011"], "note": "Standart, gerekli insan kaynağı ve bilginin sağlanmasını, tahsis edilmesini ve kullanılmasını ister. Bilgi ve araçlar erişilebilirdir; insan kaynağı tahsis/kullanım kanıtları formal değildir.", "action": "Süreç için gerekli insan kaynağı ve bilgi kaynaklarının tahsisi ile fiili kullanım durumu kayıt altına alınmalıdır."},
    "GP.3.2.5": {"pct": 70, "evidence": ["Confluence/repository yapısı", "İÜC.BİDB.KLV.004", "İÜC.BİDB.LST.011", "İÜC.BİDB.SRÇ.022"], "note": "Standart, gerekli altyapı ve çalışma ortamının mevcut, desteklenen, kullanılan ve sürdürülen olmasını ister. Ortam mevcuttur ve kullanılmaktadır; bakım desteği kanıtı sınırlı olsa da temel beklenti karşılanmaktadır.", "action": "-"},
    "GP.3.2.6": {"pct": 40, "evidence": ["İÜC.BİDB.LST.009 (SRÇ.001)", "SRÇ.001 değerlendirme kayıtları"], "note": "Standart, davranış/uygunluk/etkinliği anlamak için verinin belirlenmesini, toplanmasını, analiz edilmesini ve sonuçların sürekli iyileştirmede kullanılmasını ister. Ölçüler tanımlıdır; gerçekleşen veri, analiz ve iyileştirme geri beslemesi henüz yeterli değildir.", "action": "LST.009 ölçümleri için gerçekleşen veriler toplanmalı, analiz edilmeli ve iyileştirme kararlarına bağlanmalıdır."},
}

EVIDENCE_HEADERS = {"Kanıt", "Karşılayan Doküman / Kayıt"}
RESULT_HEADERS = {"Değerlendirme Sonucu", "Durum"}
NOTE_HEADERS = {"Denetçi Notu", "Mevcut Karşılama"}
ACTION_HEADERS = {"Eksik / Tamamlayıcı Aksiyon"}


def esc(value: object) -> str:
    return html.escape(str(value), quote=False)


def clean(value: str) -> str:
    return html.unescape(re.sub(r"<.*?>", "", value, flags=re.DOTALL)).strip()


def status(pct: int) -> str:
    if pct == 0:
        return "YOK"
    if pct <= 40:
        return "ZAYIF"
    if pct < 70:
        return "DAĞINIK"
    return "VAR"


def ul(items: list[str]) -> str:
    return "<ul>" + "".join(f"<li>{esc(item)}</li>" for item in items) + "</ul>"


def load_standard_ids() -> set[str]:
    data = yaml.safe_load(STANDARD_PATH.read_text(encoding="utf-8")) or {}
    ids: set[str] = set()

    def walk(obj: Any) -> None:
        if isinstance(obj, dict):
            item_id = obj.get("id")
            if isinstance(item_id, str):
                ids.add(item_id)
            for value in obj.values():
                walk(value)
        elif isinstance(obj, list):
            for item in obj:
                walk(item)

    walk(data)
    return ids


def validate_standard() -> None:
    ids = load_standard_ids()
    missing = [identifier for identifier in EXPECTED_BP_IDS + EXPECTED_GP_IDS if identifier not in ids]
    if missing:
        raise RuntimeError(f"Standart YAML içinde beklenen BP/GP kimlikleri eksik: {missing}")
    missing_eval = [identifier for identifier in EXPECTED_BP_IDS + EXPECTED_GP_IDS if identifier not in EVAL]
    if missing_eval:
        raise RuntimeError(f"Değerlendirmesi tanımlanmamış BP/GP var: {missing_eval}")


def parse_table(table_html: str) -> tuple[list[str], list[list[str]]]:
    headers = [clean(h) for h in re.findall(r"<th[^>]*>(.*?)</th>", table_html, flags=re.DOTALL)]
    tbody = re.search(r"<tbody[^>]*>(.*?)</tbody>", table_html, flags=re.DOTALL)
    rows: list[list[str]] = []
    if tbody:
        for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", tbody.group(1), flags=re.DOTALL):
            rows.append(re.findall(r"<td[^>]*>(.*?)</td>", tr, flags=re.DOTALL))
    return headers, rows


def render_table(headers: list[str], rows: list[list[str]]) -> str:
    head = "".join(f"<th>{esc(h)}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>" for row in rows)
    return f'<table class="wrapped"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>'


def find_ref(row: list[str]) -> str | None:
    for cell in row:
        text = clean(cell)
        m = re.search(r"SUP\.7\.BP[1-8]|GP\.[23]\.[12]\.[1-6]", text)
        if m:
            return m.group(0)
    return None


def fill_assessment_table(headers: list[str], rows: list[list[str]]) -> tuple[list[list[str]], int]:
    header_index = {header: i for i, header in enumerate(headers)}
    evidence_idx = next((header_index[h] for h in EVIDENCE_HEADERS if h in header_index), None)
    result_idx = next((header_index[h] for h in RESULT_HEADERS if h in header_index), None)
    note_idx = next((header_index[h] for h in NOTE_HEADERS if h in header_index), None)
    action_idx = next((header_index[h] for h in ACTION_HEADERS if h in header_index), None)

    if evidence_idx is None or result_idx is None or note_idx is None:
        return rows, 0

    changed = 0
    new_rows = deepcopy(rows)
    for row in new_rows:
        ref = find_ref(row)
        if ref not in EVAL:
            continue
        ev = EVAL[ref]
        row[evidence_idx] = ul(ev["evidence"])
        row[result_idx] = esc(f"%{ev['pct']} - {status(ev['pct'])}")
        row[note_idx] = esc(ev["note"])
        if action_idx is not None:
            row[action_idx] = esc("-" if status(ev["pct"]) == "VAR" else ev["action"])
        elif status(ev["pct"]) != "VAR":
            row[note_idx] += f"<p><strong>Tamamlayıcı aksiyon:</strong> {esc(ev['action'])}</p>"
        changed += 1
    return new_rows, changed


def fill_all_matrices(storage: str) -> tuple[str, set[str]]:
    output: list[str] = []
    last = 0
    filled_refs: set[str] = set()
    for match in re.finditer(r"<table.*?</table>", storage, flags=re.DOTALL):
        output.append(storage[last:match.start()])
        block = match.group(0)
        headers, rows = parse_table(block)
        new_rows, changed = fill_assessment_table(headers, rows)
        if changed:
            for row in new_rows:
                ref = find_ref(row)
                if ref in EVAL:
                    filled_refs.add(ref)
            output.append(render_table(headers, new_rows))
        else:
            output.append(block)
        last = match.end()
    output.append(storage[last:])
    return "".join(output), filled_refs


def build_view(storage: str) -> str:
    return f"""<!doctype html><html lang="tr"><head><meta charset="utf-8"><title>{esc(TARGET_TITLE)}</title><style>{CSS}</style></head><body><main class="confluence-page"><h1>{esc(TARGET_TITLE)}</h1>{storage}</main></body></html>\n"""


def write_page_yaml() -> None:
    rel = str(TARGET_DIR.relative_to(CONFLUENCE_DIR)).replace("\\", "/")
    meta = {
        "page_id": "", "space": "SSSS", "title": TARGET_TITLE,
        "parent_id": TARGET_PARENT_ID, "parent_title": TARGET_PARENT_TITLE,
        "version": "", "url": "", "depth": 3, "status": "active",
        "exported_at": datetime.now(timezone.utc).isoformat(), "children_count": 0,
        "relative_path": rel, "slug": TARGET_SLUG, "has_view_html": True,
        "view_file": "body.view.html", "storage_file": "body.storage.xhtml",
    }
    (TARGET_DIR / "page.yaml").write_text(yaml.safe_dump(meta, allow_unicode=True, sort_keys=False), encoding="utf-8")


def update_index() -> None:
    index = yaml.safe_load(INDEX_PATH.read_text(encoding="utf-8")) or {}
    pages = index.setdefault("pages", [])
    rel = str(TARGET_DIR.relative_to(CONFLUENCE_DIR)).replace("\\", "/")
    pages[:] = [p for p in pages if p.get("relative_path") != rel]
    pages.append({"page_id": "", "title": TARGET_TITLE, "parent_id": TARGET_PARENT_ID,
                  "depth": 3, "relative_path": rel, "slug": TARGET_SLUG,
                  "storage_file": f"{rel}/body.storage.xhtml", "view_file": f"{rel}/body.view.html"})
    index["total_page_count"] = len(pages)
    INDEX_PATH.write_text(yaml.safe_dump(index, allow_unicode=True, sort_keys=False), encoding="utf-8")


def main() -> None:
    validate_standard()
    source = SRC_FORM_DIR / "body.storage.xhtml"
    if not source.exists():
        raise RuntimeError("Özelleştirilmiş SRÇ.001 FRM.001 localde bulunamadı. Önce Confluence export alınmalı.")

    storage = source.read_text(encoding="utf-8")
    storage = storage.replace("İÜC.BİDB.FRM.001 - Süreç Gözden Geçirme Formu (İÜC.BİDB.SRÇ.001)", TARGET_TITLE)
    storage, filled = fill_all_matrices(storage)

    expected = set(EXPECTED_BP_IDS + EXPECTED_GP_IDS)
    missing = sorted(expected - filled)
    if missing:
        raise RuntimeError(
            "Form yapısı korunarak doldurma yapılamadı. Aşağıdaki BP/GP satırları formda bulunamadı: "
            + ", ".join(missing)
        )

    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    (TARGET_DIR / "body.storage.xhtml").write_text(storage, encoding="utf-8")
    (TARGET_DIR / "body.view.html").write_text(build_view(storage), encoding="utf-8")
    write_page_yaml()
    update_index()
    print(f"[DONE] Exact-standard assessment created without changing form structure: {TARGET_TITLE}")


if __name__ == "__main__":
    main()
