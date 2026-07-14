#!/usr/bin/env python3
"""Rebuild SRÇ.004 locally using the active process definition template.

The script updates only SRÇ.004 storage/view artifacts and a local report. It
does not change page metadata, publish to Confluence, or alter related records.
"""
from __future__ import annotations

import html
import re
import unicodedata
from pathlib import Path
from typing import Any
from urllib.parse import quote

import yaml


ROOT = Path(__file__).resolve().parents[1]
CONFLUENCE_DIR = ROOT / "confluence"
ROOT_PAGE = CONFLUENCE_DIR / "pages/000-root-iuc-bidb-spice-2026-level-3"
SRC004_DIR = ROOT_PAGE / "01-surec-dokumanlari/iuc-bidb-src-004-surec-kurulumu-sureci"
TEMPLATE_DIR = ROOT_PAGE / "02-sablonlar/iuc-bidb-src-xxx-s-surec-tanimi-sablonu"
INDEX_PATH = CONFLUENCE_DIR / "index.yaml"
REPORT_PATH = ROOT / "reports/src004_template_alignment_report.md"
SRC004_TITLE = "İÜC.BİDB.SRÇ.004 - Süreç Kurulumu Süreci"
SRC004_CODE = "İÜC.BİDB.SRÇ.004"
PROCESS_OWNER = "Mustafa Nusret SARISAKAL - Bilgi İşlem Daire Başkanı"
REVIEWER = "Levent Bayezit - Proje Yöneticisi"
APPROVER = "Mustafa Nusret SARISAKAL - Bilgi İşlem Daire Başkanı"
PREPARER = "Soner DEDEOĞLU - Kalite Danışmanı"
FLOWCHART_FILENAME = unicodedata.normalize("NFD", "İÜC.BİDB.SRÇ.004 - Flowchart.png")

CSS = (
    'body{margin:0;background:#fff;color:#172b4d;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;line-height:1.55}'
    '.confluence-page{max-width:1180px;margin:0 auto;padding:32px 24px 56px}'
    'h1,h2,h3{color:#0f172a;line-height:1.25}'
    'h1{margin-top:0;padding-bottom:12px;border-bottom:1px solid #d8dee4}'
    'table{width:100%;border-collapse:collapse;margin:16px 0;table-layout:auto}'
    'th,td{border:1px solid #c9d1d9;padding:8px 10px;vertical-align:top;overflow-wrap:anywhere}'
    'th{background:#f6f8fa;font-weight:600;text-align:left}'
)


def e(value: object) -> str:
    return html.escape(str(value), quote=False)


def read_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def strip_tags(value: str) -> str:
    value = re.sub(r"<[^>]+>", "", value)
    return re.sub(r"\s+", " ", html.unescape(value)).strip()


def norm(value: str) -> str:
    value = unicodedata.normalize("NFKD", strip_tags(value))
    value = "".join(ch for ch in value if not unicodedata.combining(ch)).lower()
    value = re.sub(r"^\s*\d+(?:\.\d+|\.n)?\s*[.-]\s*", "", value)
    value = value.translate(str.maketrans({"ı": "i", "ş": "s", "ç": "c", "ö": "o", "ü": "u", "ğ": "g"}))
    return re.sub(r"\s+", " ", value).strip()


def template_body() -> str:
    return (TEMPLATE_DIR / "body.storage.xhtml").read_text(encoding="utf-8")


def extract_h2_sections() -> list[str]:
    headings = [strip_tags(item) for item in re.findall(r"<h2[^>]*>(.*?)</h2>", template_body(), flags=re.I | re.S)]
    sections = [heading for heading in headings if heading and not re.match(r"^\s*0\s*[.-]", heading)]
    if len(sections) != 15 or not sections[0].startswith("1.") or not sections[-1].startswith("15."):
        raise RuntimeError(f"Şablondan beklenen 15 bölümlü yapı okunamadı: {sections}")
    return sections


def section_html(section_number: str) -> str:
    match = re.search(
        rf"<h2[^>]*>\s*{re.escape(section_number)}[^<]*</h2>(.*?)(?=<h2[^>]*>\s*\d+\s*[.-]|\Z)",
        template_body(),
        flags=re.I | re.S,
    )
    return match.group(1) if match else ""


def first_table_headers(section_number: str) -> list[str]:
    section = section_html(section_number)
    match = re.search(r"<table[^>]*>.*?<thead[^>]*>\s*<tr[^>]*>(.*?)</tr>", section, flags=re.I | re.S)
    if not match:
        return []
    return [strip_tags(item) for item in re.findall(r"<th[^>]*>(.*?)</th>", match.group(1), flags=re.I | re.S)]


def load_pages() -> dict[str, str]:
    result: dict[str, str] = {}
    for page in read_yaml(INDEX_PATH).get("pages", []) or []:
        title = str(page.get("title") or "")
        page_id = str(page.get("page_id") or "")
        if title and page_id:
            result[title] = page_id
    return result


PAGES = load_pages()


def link(title: str) -> str:
    page_id = PAGES.get(title)
    if not page_id:
        return e(title)
    return f'<a href="/pages/viewpage.action?pageId={page_id}">{e(title)}</a>'


def p(text: str) -> str:
    return f"<p>{e(text)}</p>"


def table(headers: list[str], rows: list[list[str]], *, fixed: bool = False) -> str:
    head = "".join(f'<th class="confluenceTh">{e(header)}</th>' for header in headers)
    body = "".join(
        "<tr>" + "".join(f'<td class="confluenceTd">{cell}</td>' for cell in row) + "</tr>"
        for row in rows
    )
    style = ' style="width:100%;table-layout:fixed;"' if fixed else ""
    return (
        f'<div class="table-wrap"><table class="wrapped confluenceTable"{style}>'
        f"<thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>"
    )


def surec_bilgileri() -> str:
    return table(["Alan", "Değer"], [
        ["Kurum", "İstanbul Üniversitesi - Cerrahpaşa Bilgi İşlem Daire Başkanlığı"],
        ["Süreç Kodu ve Adı", f"{SRC004_CODE} - Süreç Kurulumu Süreci"],
        ["Süreç Referansı", "ISO/IEC 15504-5 PIM.1 - Process establishment"],
        ["Süreç Sahibi", PROCESS_OWNER],
        ["Hedef Kitle", "Süreç sahipleri ve sorumluları, proje ekipleri, kalite güvence, süreç değerlendirme/iyileştirme rolleri ve ilgili BİDB personeli"],
        ["Yayın ve Erişim Ortamı", "Confluence ve Google Drive; uzaktan erişimde İÜC VPN ve kurumsal yetkilendirme"],
        ["Durum", "Aktif"],
        ["Sürüm", "v1.0"],
        ["Yürürlük Tarihi", "15-02-2025"],
        ["Son Gözden Geçirme Tarihi", "14-07-2026"],
        ["Güncelleme Sıklığı", "Yılda en az bir kez veya süreç mimarisi, standart, organizasyon ya da araçlarda önemli değişiklik olduğunda"],
    ])


def amac() -> str:
    return (
        p("Bu sürecin amacı, İÜC BİDB'nin iş faaliyetlerine uygulanan tüm yaşam döngüsü süreçleri için kurumsal standart süreç setini kurmak ve sürdürmektir. Süreç; süreç mimarisini, her sürecin amacı ve uygulanabilirliğini, ayrıntılı faaliyetlerini, iş ürünlerini, performans beklentilerini, uyarlama yaklaşımını ve kullanım verisinin yönetimini bütüncül biçimde tanımlar.")
        + "<h3>2.1. Süreç Sonuçları</h3>"
        + table(["Sonuç ID", "Süreç Sonucu"], [
            ["S1", "Her sürecin uygulanabilirlik bilgisiyle birlikte tanımlanmış ve sürdürülen standart bir süreç seti oluşturulur."],
            ["S2", "Standart süreçlerin ayrıntılı görevleri, faaliyetleri, ilişkili iş ürünleri ve beklenen performans özellikleri tanımlanır."],
            ["S3", "Standart sürecin proje, ürün veya hizmet ihtiyaçlarına göre kontrollü biçimde uyarlanmasına ilişkin strateji geliştirilir."],
            ["S4", "Standart süreçlerin belirli proje ve hizmetlerde kullanımına ilişkin bilgi ve veriler oluşturulur ve sürdürülür."],
        ])
    )


def kapsam() -> str:
    return p("Bu süreç, LST.006 içinde tanımlanan İÜC BİDB standart süreç setinin kurulması, tanımlanması, yayımlanması, uygulanmasının desteklenmesi ve güncelliğinin sürdürülmesini kapsar.") + table(
        ["Kapsam Öğesi", "Açıklama"],
        [
            ["Kapsama Dahil", "Standart süreç seti ve uygulanabilirlik bilgisi; süreç mimarisi ve etkileşimleri; süreç amaçları, sonuçları, faaliyetleri ve iş ürünleri; performans beklentileri; uyarlama kuralları; süreç kullanım verileri; süreç repository yapısı ve yaygınlaştırma faaliyetleri"],
            ["Kapsam Dışı", "Tekil projelerin günlük yürütümü, proje planlarının operasyonel yönetimi, yazılım geliştirme faaliyetinin kendisi ve resmi süreç varlığı niteliği taşımayan kişisel çalışma notları"],
            ["Uygulama Alanı", "İÜC BİDB yaşam döngüsü, destek, yönetim, süreç iyileştirme ve kaynak/altyapı süreçlerinin tamamı; çekirdek veya koşullu süreç ayrımı yapılmaz"],
        ],
    )


def referanslar() -> str:
    return table(["Referans", "Açıklama"], [
        ["ISO/IEC 15504-5:2006 PIM.1 - Process establishment", "Süreç amacı, sonuçları, BP1-BP6 temel uygulamaları ve ilişkili iş ürünleri"],
        ["ISO/IEC 15504-5:2006 - Process Assessment Model", "Süreç değerlendirme modelinin süreç boyutu ve değerlendirme göstergeleri"],
        ["ISO/IEC 15504-5:2006 - Process Attributes", "Süreç yetenek boyutunda Seviye 1-3 süreç öznitelikleri ve genel uygulamalar"],
    ])


def terimler() -> str:
    return table(["Terim / Kısaltma", "Açıklama"], [
        ["PIM.1", "ISO/IEC 15504-5 içindeki Process establishment süreci"],
        ["Standart süreç seti", "Kurumda kullanılacak süreçlerin amaç, kapsam, sonuç, faaliyet, iş ürünü, rol, etkileşim ve uygulanabilirlik bilgileriyle tanımlanmış bütünü"],
        ["Süreç mimarisi", "Süreçlerin gruplandırılmasını, ilişkilerini ve kurumsal yapı içindeki konumlarını gösteren yapı"],
        ["Uygulanabilirlik", "Bir sürecin hangi proje, ürün, hizmet veya organizasyonel bağlamda uygulanacağını gösteren bilgi"],
        ["Süreç uyarlama", "Standart sürecin amacı ve zorunlu sonuçları korunarak belirli ihtiyaçlara göre kontrollü biçimde özelleştirilmesi"],
        ["Tanımlı süreç", "Standart süreçten seçilerek veya uyarlanarak belirli bir bağlamda uygulanmak üzere devreye alınan süreç"],
        ["Süreç repository", "Süreç tanımları, kayıtları, ölçüm verileri, gözden geçirme sonuçları ve süreç varlıklarının saklandığı kontrollü alan"],
        ["BP", "Base Practice; süreç amacının gerçekleştirilmesi için beklenen temel uygulama"],
        ["PA / GP", "Process Attribute / Generic Practice; süreç yetenek seviyesinin yönetim, tanım ve yaygınlaştırma beklentileri"],
    ])


def surec_aktivitesi() -> str:
    return table(["Alan", "Açıklama"], [
        ["Süreç Başlatıcısı", "Yeni süreç ihtiyacı, mevcut süreç değişikliği, standart veya organizasyon değişikliği, süreç değerlendirme/iyileştirme sonucu ya da periyodik gözden geçirme"],
        ["Süreç Başlangıcı", "Süreç kurulum veya güncelleme ihtiyacının kapsamı, sahibi ve uygulanabilirlik etkisiyle birlikte belirlenmesi"],
        ["Süreç Bitişi", "Süreç varlıklarının hazırlanması, gözden geçirilmesi ve onaylanması; yayımlanması, hedef kitleye duyurulması ve kullanım/izleme kayıtlarına bağlanması"],
        ["Ana Faaliyetler", "Süreç mimarisini tanımlama; kurumsal kullanımı destekleme; standart süreçleri tanımlama ve sürdürme; performans beklentilerini belirleme; uyarlama kılavuzlarını oluşturma; süreç kullanım verisini sürdürme"],
        ["İlgili Süreçler", "<br />".join([
            link("İÜC.BİDB.SRÇ.001 - Dokümantasyon Süreci"),
            link("İÜC.BİDB.SRÇ.005 - Süreç Değerlendirme Süreci"),
            link("İÜC.BİDB.SRÇ.006 - Süreç İyileştirme Süreci"),
            link("İÜC.BİDB.SRÇ.020 - Eğitim Süreci"),
            link("İÜC.BİDB.SRÇ.025 - Ölçüm Süreci"),
        ])],
    ])


def roller() -> str:
    return p("Bu süreç kapsamında rol, sorumluluk, yetki, RACI ve yetkinlik tanımları, süreç özel kaydı olan İÜC.BİDB.LST.010 - Süreç Rol Yetki ve RACI Matrisi (İÜC.BİDB.SRÇ.004) dokümanında yönetilir.")


def araclar_altyapi() -> str:
    return p("Süreç Kurulumu Sürecinin uygulanması ve süreç varlıklarının kontrollü biçimde sürdürülmesi için aşağıdaki araçlar ve altyapı bileşenleri kullanılır.") + table(
        ["Tür", "Araç / Altyapı Bileşeni", "Kullanım Amacı", "Erişim ve Kullanım Koşulu", "Sorumlu Rol / Birim"],
        [
            ["Araç", "Confluence", "Onaylı süreç tanımlarının, şablonların, kılavuzların ve ilişkili kayıt bağlantılarının yayımlanması", "Kurumsal hesap ve atanmış okuma/yazma yetkisi; uzaktan erişimde VPN", "Proje Geliştirme Yönetimi / Confluence Yöneticisi"],
            ["Altyapı", "Google Drive", "Kontrollü kayıtların, eklerin, onaylı kopyaların ve arşivlerin saklanması", "Kurumsal hesap ve rol bazlı klasör yetkisi", "Repository Sorumlusu / Proje Geliştirme Yönetimi"],
            ["Araç", "Jira", "Süreç kurulum, değişiklik, değerlendirme ve iyileştirme aksiyonlarının izlenmesi", "Proje veya süreç bazlı yetkilendirme", "Süreç Sahibi / Jira Yöneticisi"],
            ["Araç", "Bitbucket", "Sürüm kontrollü süreç kaynaklarının, otomasyon betiklerinin ve değişiklik geçmişinin yönetilmesi", "Repository yetkisi ve tanımlı branch/değişiklik kuralları", "Proje Geliştirme Yönetimi / Bitbucket Yöneticisi"],
            ["İletişim", "Kurumsal e-posta", "Yeni süreçlerin ve süreç revizyonlarının hedef kitleye duyurulması", "Kurumsal e-posta hesabı ve tanımlı dağıtım grupları", "Süreç Sahibi / Yayımlayan"],
            ["Altyapı", "İÜC VPN ve kurumsal kimlik/yetkilendirme altyapısı", "Kurum dışından süreç repository ve kayıt sistemlerine güvenli erişim", "Geçerli kurumsal hesap, VPN yetkisi ve bilgi güvenliği kuralları", "İÜC BİDB Altyapı ve Erişim Yönetimi"],
        ],
        fixed=True,
    )


def is_urunleri() -> str:
    return p("Bu süreç kapsamında kullanılan girdi iş ürünleri ve üretilen çıktı iş ürünleri, süreç özel kaydı olan İÜC.BİDB.LST.008 - İş Ürünleri ve Kalite Kriterleri Listesi (İÜC.BİDB.SRÇ.004) dokümanında yönetilir.")


def surec_akisi(*, view: bool = False) -> str:
    lines = [
        "flowchart TD",
        "A[Yeni süreç veya süreç değişikliği ihtiyacı belirlenir] --> B[Süreç mimarisi ve uygulanabilirlik tanımlanır]",
        "B --> C[Standart süreç ve ilişkili süreç varlıkları hazırlanır veya güncellenir]",
        "C --> D[Performans beklentileri ve ölçüm yaklaşımı belirlenir]",
        "D --> E[Uyarlama kuralları tanımlanır]",
        "E --> F[Süreç tanımı gözden geçirilir]",
        "F --> G{Süreç uygun mu?}",
        "G -- Hayır --> C",
        "G -- Evet --> H[Süreç onaylanır ve yayımlanır]",
        "H --> I[Kurumsal kullanım ve yaygınlaştırma desteklenir]",
        "I --> J[Süreç kullanım ve performans verileri sürdürülür]",
        "J --> K[Değerlendirme ve iyileştirme sonuçları izlenir]",
        "K --> A",
    ]
    mermaid = "<br />".join(f'<code class="language-mermaid">{e(line)}</code>' for line in lines)
    if view:
        return (
            f'<p class="process-flow-image" style="text-align:center"><img src="attachments/{quote(FLOWCHART_FILENAME)}" '
            f'alt="{e(SRC004_TITLE)} süreç akışı" style="max-width:100%;height:auto" /></p>'
            + '<div class="confluence-information-macro has-no-icon confluence-information-macro-information conf-macro output-block" data-hasbody="true" data-macro-name="info">'
            + '<p class="title">Mermaid Kodu</p><div class="confluence-information-macro-body">'
            + f'<p style="margin-left:40px">{mermaid}</p></div></div>'
        )
    return (
        f'<p><ac:image ac:height="900"><ri:attachment ri:filename="{e(FLOWCHART_FILENAME)}" /></ac:image></p>'
        + '<ac:structured-macro ac:name="info" ac:schema-version="1">'
        + '<ac:parameter ac:name="icon">false</ac:parameter>'
        + '<ac:parameter ac:name="title">Mermaid Kodu</ac:parameter>'
        + f'<ac:rich-text-body><p style="margin-left:40px">{mermaid}</p></ac:rich-text-body>'
        + '</ac:structured-macro>'
    )


ACTIVITIES = [
    {"id": "F1", "name": "Süreç mimarisini tanımla", "detail": "Standart süreç seti, her sürecin amacı, uygulanabilirliği ve süreçler arası etkileşimler tanımlanır ve sürdürülür. (PIM.1.BP1)", "product": "İÜC.BİDB.LST.006 - Standart Süreç Envanteri; İÜC.BİDB.LST.007 - Süreç Etkileşim Matrisi (İÜC.BİDB.SRÇ.004)"},
    {"id": "F2", "name": "Süreçlerin kurumsal kullanımını destekle", "detail": "Standart süreçlerin amaçlarına uygun olarak organizasyon genelinde erişimi, duyurusu, bilgilendirilmesi ve gerektiğinde eğitimi desteklenir. (PIM.1.BP2)", "product": "Yayımlanmış süreç varlıkları; e-posta duyurusu; SRÇ.020 eğitim kaydı"},
    {"id": "F3", "name": "Standart süreçleri tanımla ve sürdür", "detail": "Her standart sürecin amacı, sonuçları, kapsamı, faaliyetleri, rolleri, iş ürünleri, etkileşimleri ve uygulama kuralları güncel şablona göre tanımlanır. (PIM.1.BP3)", "product": "İlgili SRÇ süreç tanımı; süreç özel İÜC.BİDB.LST.007, İÜC.BİDB.LST.008 ve İÜC.BİDB.LST.010 kayıtları"},
    {"id": "F4", "name": "Performans beklentilerini belirle", "detail": "Standart süreçlerin uygulanmasında beklenen performans hedefleri, ölçümler, veri kaynakları ve izleme sıklıkları belirlenir. (PIM.1.BP4)", "product": "LST.009 Süreç Performans Ölçüm Seti"},
    {"id": "F5", "name": "Süreç uyarlama kılavuzlarını oluştur", "detail": "Standart süreçlerin proje, ürün veya hizmet ihtiyaçlarına göre hangi sınırlar içinde uyarlanabileceği ve onay koşulları belirlenir. (PIM.1.BP5)", "product": "KLV.002 Süreç Uyarlama Kılavuzu; uyarlama kararı/kaydı"},
    {"id": "F6", "name": "Süreç kullanım verisini sürdür", "detail": "Standart süreçlerin belirli proje ve hizmetlerde kullanımına ilişkin bilgiler mevcut ilgili kayıt ve sistemlerde tutulur, gözden geçirilir ve iyileştirme döngüsüne aktarılır. Ayrı bir merkezi register oluşturulmaz. (PIM.1.BP6)", "product": "Süreç kullanım ve performans kayıtları; değerlendirme ve analiz sonuçları"},
]


def surec_faaliyetleri() -> str:
    headers = first_table_headers("11.") or ["Faaliyet ID", "Faaliyet", "Faaliyetin Nasıl Yürütüldüğü", "Elde Edilen / Güncellenen İş Ürünü"]
    rows: list[list[str]] = []
    for item in ACTIVITIES:
        row: list[str] = []
        for header in headers:
            key = norm(header)
            if "id" in key or "no" == key or "sira" in key:
                row.append(e(item["id"]))
            elif "faaliyet" in key and "nasil" not in key:
                row.append(e(item["name"]))
            elif "nasil" in key or "aciklama" in key or "yurut" in key:
                row.append(e(item["detail"]))
            elif "urun" in key or "cikti" in key or "kayit" in key:
                row.append(e(item["product"]))
            else:
                row.append("")
        rows.append(row)
    return table(headers, rows)


def olcum() -> str:
    return p("Bu süreç kapsamında takip edilecek süreç performansı ölçüm seti, süreç özel kaydı olan İÜC.BİDB.LST.009 - Süreç Performans Ölçüm Seti (İÜC.BİDB.SRÇ.004) dokümanında yönetilir.")


def uygulama_uyarlama() -> str:
    sections = [
        ("13.1. Standart Süreç Seti ve Uygulanabilirlik", "LST.006 içinde yer alan süreçlerin tamamı standart süreç setinde tutulur. Çekirdek veya koşullu süreç ayrımı yapılmaz; her süreç için uygulanabilirlik ve kullanım bağlamı kayıt altına alınır."),
        ("13.2. Süreç Tanımlama ve Bakım", "Her süreç güncel süreç tanımı şablonuna ve ilişkili ortak kayıt setine göre tanımlanır. Süreçler yılda en az bir kez ve standart, organizasyon, teknoloji, araç veya değerlendirme sonucu değiştiğinde ayrıca gözden geçirilir."),
        ("13.3. Yaygınlaştırma ve Kullanım Desteği", "Yeni süreçler ve revizyonlar kurumsal e-posta ile duyurulur; Confluence ve Google Drive üzerinden erişime açılır. Yetkinlik veya uygulama ihtiyacı oluştuğunda eğitim ve katılım kayıtları SRÇ.020 kapsamında yönetilir."),
        ("13.4. Performans Beklentileri", "Her süreç için performans göstergeleri, hedefler, veri kaynakları, izleme sıklığı ve sorumlular LST.009 kayıtlarında tanımlanır; sonuçlar süreç değerlendirme ve iyileştirme faaliyetlerine girdi sağlar."),
        ("13.5. Süreç Kullanım Verisi", "Süreç kullanım bilgileri proje, hizmet, değerlendirme, ölçüm ve ilgili operasyon kayıtlarında tutulur. Aynı veriyi tekrarlayan ayrı bir merkezi kullanım registerı oluşturulmaz."),
        ("13.6. Değişiklik ve Gözden Geçirme", "Süreç mimarisi, amaç, sonuç, faaliyet, iş ürünü, rol, araç veya uyarlama kuralındaki değişiklikler etki değerlendirmesi, gözden geçirme ve onay adımlarından geçirilir; sürüm ve yayın kayıtları SRÇ.001 kurallarına göre yönetilir."),
    ]
    parts: list[str] = []
    for heading, text in sections:
        parts.append(f"<h3>{e(heading)}</h3>")
        parts.append(p(text))
    parts.append("<h3>13.7. Uyarlama Kuralları</h3>")
    parts.append(table(["Kural", "Açıklama"], [
        ["Zorunlu Adımlar", "Süreç amacı ve zorunlu süreç sonuçları, süreç sahibi, temel faaliyetler, ilgili iş ürünleri, gözden geçirme/onay, yayın ve izlenebilirlik gereksinimleri korunur."],
        ["Uyarlanabilir Adımlar", "Faaliyetlerin ayrıntı seviyesi, kullanılan yöntem, görev dağılımı, iş ürünü biçimi ve uygulama sırası; proje, ürün veya hizmetin büyüklük, risk ve karmaşıklığına göre uyarlanabilir."],
        ["Onay Gerektiren Durumlar", "Bir sürecin uygulanmaması, zorunlu sonuç veya kontrolün kaldırılması, standart süreç mimarisinden sapma ya da ortak doküman setinin değiştirilmesi süreç sahibi ve onaylayan rol kararı gerektirir."],
    ]))
    return "".join(parts)


def etkilesimler() -> str:
    return p("Bu süreç kapsamındaki faaliyetlerin farklı süreçler ile olan etkileşimleri, süreç özel kaydı olan İÜC.BİDB.LST.007 - Süreç Etkileşim Matrisi (İÜC.BİDB.SRÇ.004) dokümanında yönetilir.")


def version_table() -> str:
    return table(
        ["Sürüm", "Tarih", "Açıklama", "Hazırlayan / Güncelleyen", "Gözden Geçiren", "Onay"],
        [
            ["v0.1", "10 Jan 2025", "İlk taslak oluşturuldu.", PREPARER, "-", "-"],
            ["v1.0", "15 Feb 2025", "Süreç Kurulumu Süreci onaylanarak yürürlüğe girmiştir.", PREPARER, REVIEWER, APPROVER],
        ],
    )


def content_for(heading: str) -> str:
    key = norm(heading)
    if "surec bilgileri" in key:
        return surec_bilgileri()
    if key == "amac" or key.endswith("amac"):
        return amac()
    if "kapsam" in key:
        return kapsam()
    if "referans" in key:
        return referanslar()
    if "terim" in key or "kisalt" in key:
        return terimler()
    if "surec aktivitesi" in key:
        return surec_aktivitesi()
    if "rol" in key or "sorumluluk" in key:
        return roller()
    if "arac" in key and "altyapi" in key:
        return araclar_altyapi()
    if "is" in key and "urun" in key:
        return is_urunleri()
    if "surec akisi" in key:
        return surec_akisi()
    if "surec faaliyet" in key:
        return surec_faaliyetleri()
    if "olcum" in key or "izleme" in key:
        return olcum()
    if "uygulama" in key or "uyarlama" in key:
        return uygulama_uyarlama()
    if "etkilesim" in key:
        return etkilesimler()
    if "surum" in key:
        return version_table()
    raise RuntimeError(f"Şablon bölümü için SRÇ.004 içeriği tanımlı değil: {heading}")


def build_storage_body(sections: list[str]) -> str:
    parts: list[str] = []
    for heading in sections:
        parts.append(f"<h2>{e(heading)}</h2>")
        parts.append(content_for(heading))
    return "".join(parts) + "\n"


def build_view_html(storage: str) -> str:
    view_body = storage.replace(surec_akisi(), surec_akisi(view=True))
    return f'''<!doctype html>
<html lang="tr">
<head><meta charset="utf-8"><title>{e(SRC004_TITLE)}</title><style>{CSS}</style></head>
<body><main class="confluence-page"><h1>{e(SRC004_TITLE)}</h1>{view_body}</main></body>
</html>
'''


def validate(storage: str, sections: list[str]) -> None:
    rendered_headings = [strip_tags(item) for item in re.findall(r"<h2[^>]*>(.*?)</h2>", storage, flags=re.I | re.S)]
    if rendered_headings != sections:
        raise RuntimeError(f"SRÇ.004 başlık sırası şablonla eşleşmiyor: {rendered_headings}")
    required = [
        "2.1. Süreç Sonuçları", "8. Araçlar ve Altyapı", "PIM.1.BP1", "PIM.1.BP6",
        "İÜC.BİDB.LST.007", "İÜC.BİDB.LST.008", "İÜC.BİDB.LST.009", "İÜC.BİDB.LST.010",
        "ISO/IEC 15504-5:2006 - Process Assessment Model",
        "ISO/IEC 15504-5:2006 - Process Attributes",
        "flowchart TD", PROCESS_OWNER, REVIEWER, APPROVER,
        FLOWCHART_FILENAME,
    ]
    plain = html.unescape(storage)
    missing = [item for item in required if item not in plain]
    if missing:
        raise RuntimeError(f"SRÇ.004 zorunlu içerik eksik: {missing}")
    active_content = plain.split("<h2>15. Sürüm Geçmişi</h2>", 1)[0]
    if "LST.004" in active_content or "Soru Bankası" in active_content:
        raise RuntimeError("SRÇ.004 içinde legacy LST.004 veya proje adı bulundu.")
    if len(re.findall(r"<td[^>]*>S[1-4]</td>", storage)) != 4:
        raise RuntimeError("PIM.1 süreç sonuçlarının tamamı bulunamadı.")
    if len(re.findall(r"PIM\.1\.BP[1-6]", storage)) < 6:
        raise RuntimeError("PIM.1 BP1-BP6 izlenebilirliği eksik.")
    reference_section = active_content.split("<h2>4. Referanslar</h2>", 1)[1].split("<h2>5.", 1)[0]
    if len(re.findall(r"<tr>", reference_section)) != 4:
        raise RuntimeError("Referanslar bölümü başlık dahil tam üç referans içermelidir.")
    history_section = plain.split("<h2>15. Sürüm Geçmişi</h2>", 1)[1]
    if len(re.findall(r"<td[^>]*>v(?:0\.1|1\.0)</td>", history_section)) != 2:
        raise RuntimeError("SRÇ.004 sürüm geçmişi v0.1 ve v1.0 satırlarından oluşmalıdır.")
    if not (SRC004_DIR / "attachments" / FLOWCHART_FILENAME).exists():
        raise RuntimeError(f"SRÇ.004 süreç akış PNG dosyası bulunamadı: {FLOWCHART_FILENAME}")


def write_report(old_sections: list[str], new_sections: list[str]) -> None:
    lines = [
        "# SRÇ.004 Güncel Şablona Uyum Raporu", "", "Tarih: 14-07-2026", "",
        "## Kapsam", "",
        "- Yalnızca SRÇ.004 storage XHTML ve yerel view HTML yeniden oluşturuldu.",
        "- Confluence sayfa metadata bilgileri ve ilişkili kayıt sayfaları değiştirilmedi.",
        "- Süreç üst bilgisi v1.0 / Aktif olarak güncellendi.",
        "- Süreç sahibi, gözden geçiren ve onaycı kullanıcı tarafından doğrulanan bilgilerle yazıldı.", "",
        "## Eski Ana Başlıklar", "", *[f"- {item}" for item in old_sections], "",
        "## Yeni Ana Başlıklar", "", *[f"- {item}" for item in new_sections], "",
        "## Standart ve Karar Kontrolleri", "",
        "- PIM.1 amacı ve dört süreç sonucu işlendi.",
        "- PIM.1.BP1-BP6, Süreç Faaliyetleri tablosunda izlenebilir kılındı.",
        "- LST.006 içinde tanımlanan standart süreç setinin tamamı kapsamda tutuldu; çekirdek/koşullu ayrımı yapılmadı.",
        "- Kontrollü uyarlamada süreç amacı ve zorunlu sonuçların korunması şartı yazıldı.",
        "- Süreç kullanım verisi için yeni merkezi register oluşturulmadı.",
        "- Legacy LST.004 referansları yeni dokümana taşınmadı.",
        "- Araçlar ve Altyapı bölümü Confluence, Google Drive, Jira, Bitbucket, kurumsal e-posta ve İÜC VPN ile dolduruldu.",
        "- Referanslar yalnızca ilgili ISO/IEC 15504-5 süreç bölümü, Process Assessment Model ve Process Attributes ile sınırlandı.",
        "- İlgili süreçler alt alta gösterildi.",
        "- Süreç Akışı bölümüne SRÇ.001 biçiminde PNG görseli ve Mermaid kod bloğu birlikte eklendi.", "",
    ]
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    old_storage = (SRC004_DIR / "body.storage.xhtml").read_text(encoding="utf-8")
    old_sections = [strip_tags(item) for item in re.findall(r"<h2[^>]*>(.*?)</h2>", old_storage, flags=re.I | re.S)]
    sections = extract_h2_sections()
    storage = build_storage_body(sections)
    validate(storage, sections)
    (SRC004_DIR / "body.storage.xhtml").write_text(storage, encoding="utf-8")
    (SRC004_DIR / "body.view.html").write_text(build_view_html(storage), encoding="utf-8")
    write_report(old_sections, sections)
    print("[DONE] SRÇ.004 güncel süreç tanımı şablonuna göre yerelde oluşturuldu.")
    print(f"[REPORT] {REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
