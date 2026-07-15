#!/usr/bin/env python3
"""Rebuild only SRÇ.001 from scratch using the current process template.

Rules:
- Updates only SRÇ.001 storage/view artifacts and a local report.
- Does not change page metadata, publish to Confluence, or alter related records.
- Reads SRÇ.XXX.Ş h2 headings and preserves that order.
- Excludes 0. Şablon Hakkında.
- Uses process-specific text while preserving template-controlled sections.
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
SRC001_DIR = ROOT_PAGE / "01-surec-dokumanlari/src-001-dokumantasyon-sureci"
TEMPLATE_DIR = ROOT_PAGE / "02-sablonlar/src-xxx-s-surec-tanimi-sablonu"
INDEX_PATH = CONFLUENCE_DIR / "index.yaml"
REPORT_PATH = ROOT / "reports/src001_rework_report.md"
SRC001_TITLE = "SRÇ.001 - Dokümantasyon Süreci"
SRC001_CODE = "SRÇ.001"
PROCESS_OWNER = "Levent BAYEZİT - Proje Yöneticisi"
REVIEWER = "Levent BAYEZİT - Proje Yöneticisi"
APPROVER = "Mustafa Nusret SARISAKAL - BİD Başkanı"
PREPARER = "Soner DEDEOĞLU - Kalite Danışmanı"
FLOWCHART_FILENAME = unicodedata.normalize("NFD", "SRÇ.001 - Flowchart.png")

CSS = (
    'body{margin:0;background:#fff;color:#172b4d;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;line-height:1.55}'
    '.confluence-page{max-width:1180px;margin:0 auto;padding:32px 24px 56px}'
    'h1,h2,h3{color:#0f172a;line-height:1.25}'
    'h1{margin-top:0;padding-bottom:12px;border-bottom:1px solid #d8dee4}'
    'table{width:100%;border-collapse:collapse;margin:16px 0;table-layout:auto}'
    'th,td{border:1px solid #c9d1d9;padding:8px 10px;vertical-align:top}'
    'th{background:#f6f8fa;font-weight:600;text-align:left}'
)


def e(v: object) -> str:
    return html.escape(str(v), quote=False)


def read_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def strip_tags(value: str) -> str:
    value = re.sub(r"<[^>]+>", "", value)
    return re.sub(r"\s+", " ", html.unescape(value)).strip()


def norm(value: str) -> str:
    value = strip_tags(value)
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = value.lower()
    value = re.sub(r"^\s*\d+(?:\.\d+|\.n)?\s*[\.-]\s*", "", value)
    tr = str.maketrans({"ı":"i","ş":"s","ç":"c","ö":"o","ü":"u","ğ":"g"})
    return re.sub(r"\s+", " ", value.translate(tr)).strip()


def template_body() -> str:
    return (TEMPLATE_DIR / "body.storage.xhtml").read_text(encoding="utf-8")


def extract_h2_sections() -> list[str]:
    headings = [strip_tags(m) for m in re.findall(r"<h2[^>]*>(.*?)</h2>", template_body(), flags=re.I | re.S)]
    sections = [h for h in headings if h and not re.match(r"^\s*0\s*[\.-]", h)]
    if not sections or not sections[0].startswith("1."):
        raise RuntimeError(f"Şablondan beklenen h2 yapısı okunamadı: {sections[:3]}")
    return sections


def section_html(section_number: str) -> str:
    body = template_body()
    m = re.search(rf"<h2[^>]*>\s*{re.escape(section_number)}[^<]*</h2>(.*?)(?=<h2[^>]*>\s*\d+\s*[\.-]|\Z)", body, flags=re.I | re.S)
    return m.group(1) if m else ""


def first_table_headers(section_number: str) -> list[str]:
    sec = section_html(section_number)
    m = re.search(r"<table[^>]*>.*?<thead[^>]*>\s*<tr[^>]*>(.*?)</tr>", sec, flags=re.I | re.S)
    if not m:
        return []
    return [strip_tags(x) for x in re.findall(r"<th[^>]*>(.*?)</th>", m.group(1), flags=re.I | re.S)]


def load_pages() -> dict[str, str]:
    pages = {}
    for page in (read_yaml(INDEX_PATH).get("pages") or []):
        title = str(page.get("title") or "")
        page_id = str(page.get("page_id") or "")
        if title and page_id:
            pages[title] = page_id
    return pages


PAGES = load_pages()


def link(title: str) -> str:
    page_id = PAGES.get(title)
    return f'<a href="/pages/viewpage.action?pageId={page_id}">{e(title)}</a>' if page_id else e(title)


def p(text: str) -> str:
    return f"<p>{e(text)}</p>"


def table(headers: list[str], rows: list[list[str]]) -> str:
    head = "".join(f'<th class="confluenceTh">{e(h)}</th>' for h in headers)
    body = "".join("<tr>" + "".join(f'<td class="confluenceTd">{c}</td>' for c in row) + "</tr>" for row in rows)
    return f'<div class="table-wrap"><table class="wrapped confluenceTable"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def surec_bilgileri() -> str:
    return table(["Alan", "Değer"], [
        ["Kurum", "İstanbul Üniversitesi - Cerrahpaşa Bilgi İşlem Daire Başkanlığı"],
        ["Süreç Kodu ve Adı", f"{SRC001_CODE} - Dokümantasyon Süreci"],
        ["Süreç Referansı", "ISO/IEC 15504-5 SUP.7 - Documentation"],
        ["Süreç Sahibi", PROCESS_OWNER],
        ["Hedef Kitle", "Süreç sahipleri, doküman hazırlayan/gözden geçiren/onaylayan roller, proje ekipleri, kalite güvence ve ilgili BİDB personeli"],
        ["Yayın ve Erişim Ortamı", "Confluence ve Google Drive; uzaktan erişimde İÜC VPN ve kurumsal yetkilendirme"],
        ["Durum", "Aktif"],
        ["Sürüm", "v1.0"],
        ["Yürürlük Tarihi", "15-02-2025"],
        ["Son Gözden Geçirme Tarihi", "14-07-2026"],
    ])


def amac() -> str:
    return (
        p("Bu sürecin amacı, İÜC BİDB bünyesinde üretilen süreç, proje ve destek dokümanlarının yaşam döngüsü boyunca standart, izlenebilir, erişilebilir ve kontrollü biçimde yönetilmesini sağlamaktır.")
        + p("Süreç; dokümantasyon stratejisinin belirlenmesi, doküman standartlarının uygulanması, üretilecek dokümanların tanımlanması, dokümanların gözden geçirilmesi, onaylanması, yayımlanması, dağıtılması, güncellenmesi ve arşivlenmesi faaliyetlerini kapsar.")
        + "<h3>2.1. Süreç Sonuçları</h3>"
        + table(["Sonuç ID", "Süreç Sonucu"], [
            ["S1", "Ürün veya hizmet yaşam döngüsü boyunca üretilecek dokümantasyonu tanımlayan bir strateji geliştirilir."],
            ["S2", "Dokümantasyonun geliştirilmesinde uygulanacak standartlar belirlenir."],
            ["S3", "Süreç veya proje tarafından üretilecek dokümantasyon belirlenir."],
            ["S4", "Tüm dokümantasyonun içeriği ve amacı tanımlanır, gözden geçirilir ve onaylanır."],
            ["S5", "Dokümantasyon belirlenen standartlara uygun olarak geliştirilir ve erişilebilir kılınır."],
            ["S6", "Dokümantasyon tanımlanmış kriterlere uygun olarak sürdürülür."],
        ])
    )


def kapsam() -> str:
    return p("Bu süreç, İÜC BİDB süreç dokümantasyonu ile yazılım proje yaşam döngüsü dokümantasyonunda kullanılan kontrollü doküman ve kayıtların yönetimini kapsar.") + table(["Kapsam Öğesi", "Açıklama"], [
        ["Kapsama Dahil", "Süreç tanımları, şablonlar, kayıt listeleri, formlar, prosedürler, kılavuzlar/talimatlar, planlar, proje yaşam döngüsü dokümanları ve bunlara ait gözden geçirme/değişiklik/yaygınlaştırma kayıtları"],
        ["Kapsam Dışı", "Kurumsal dokümantasyon deposuna alınmayan kişisel notlar, geçici çalışma taslakları ve resmi doküman/kayıt niteliği taşımayan ara çıktılar"],
        ["Uygulama Alanı", "İÜC BİDB süreçleri, yazılım proje yaşam döngüsü faaliyetleri, destek süreçleri ve SPICE denetim hazırlık çalışmaları"],
    ])


def referanslar() -> str:
    return table(["Referans", "Açıklama"], [
        ["ISO/IEC 15504-5:2006 SUP.7 - Documentation", "Süreç amacı, sonuçları, BP1-BP8 temel uygulamaları ve ilişkili iş ürünleri"],
        ["ISO/IEC 15504-5:2006 - Process Assessment Model", "Süreç değerlendirme modelinin süreç boyutu ve değerlendirme göstergeleri"],
        ["ISO/IEC 15504-5:2006 - Process Attributes", "Süreç yetenek boyutunda Seviye 1-3 süreç öznitelikleri ve genel uygulamalar"],
    ])


def terimler() -> str:
    return table(["Terim / Kısaltma", "Açıklama"], [
        ["Doküman", "Kurumsal süreçlerin, projelerin veya destek faaliyetlerinin uygulanması için oluşturulan kontrollü yazılı bilgi"],
        ["Kayıt", "Bir faaliyetin gerçekleştiğini, kararın alındığını veya kontrolün yapıldığını gösteren kanıt niteliğindeki bilgi"],
        ["Repository", "Dokümanların yayımlandığı, erişime açıldığı ve saklandığı merkezi alan"],
        ["Şablon", "Belirli doküman türlerinin standart yapıda üretilmesi için kullanılan doküman kalıbı"],
        ["Gözden Geçirme", "Dokümanın kalite kriterlerine, şablonuna ve kullanım amacına uygunluğunun kontrol edilmesi"],
        ["Onay", "Dokümanın yürürlüğe alınmadan önce yetkili rol veya kişi tarafından kabul edilmesi"],
        ["Yayın", "Onaylanan dokümanın hedef kitle tarafından erişilebilir hale getirilmesi"],
        ["Bakım", "Dokümanın güncelliğinin, geçerliliğinin, erişilebilirliğinin ve izlenebilirliğinin sürdürülmesi"],
        ["SUP.7", "ISO/IEC 15504-5 içinde tanımlanan Documentation süreci"],
        ["SRÇ / LST / FRM / PRS / KLV", "Süreç, liste/kayıt, form, prosedür ve kılavuz/talimat dokümanı kod ön ekleri"],
    ])


def surec_aktivitesi() -> str:
    return table(["Alan", "Açıklama"], [
        ["Süreç Başlatıcısı", "Yeni doküman ihtiyacı, mevcut doküman değişiklik ihtiyacı, proje yaşam döngüsü aşaması, süreç gözden geçirme sonucu, denetim bulgusu veya iyileştirme ihtiyacı"],
        ["Süreç Başlangıcı", "Doküman ihtiyacının, değişiklik ihtiyacının veya bakım/gözden geçirme ihtiyacının belirlenmesi"],
        ["Süreç Bitişi", "Dokümanın onaylanması, yayımlanması, dağıtılması, güncellenmesi, pasife alınması veya arşivlenmesi"],
        ["Ana Faaliyetler", "Dokümantasyon stratejisinin uygulanması; doküman standardı ve şablon seçimi; doküman hazırlama; gözden geçirme; onay; yayın; dağıtım; değişiklik ve bakım takibi"],
        ["İlgili Süreçler", "<br />".join([
            link("SRÇ.002 - Kalite Güvencesi Süreci"),
            link("SRÇ.003 - Doğrulama Süreci"),
            link("SRÇ.004 - Süreç Kurulumu Süreci"),
            link("SRÇ.016 - Yapılandırma Yönetimi Süreci"),
            link("SRÇ.018 - Değişiklik Talebi Yönetimi Süreci"),
        ])],
    ])


def roller() -> str:
    return p("Bu süreç kapsamında rol, sorumluluk, yetki, RACI ve yetkinlik tanımları, süreç özel kaydı olan LST.010 - Süreç Rol Yetki ve RACI Matrisi (SRÇ.001) dokümanında yönetilir.")


def araclar_altyapi() -> str:
    return p("Dokümantasyon Sürecinin uygulanması için aşağıdaki araçlar ve altyapı bileşenleri kullanılır. Yetkilendirme ve erişim kontrolleri ilgili sistemin kurumsal kurallarına göre uygulanır.") + table(
        ["Tür", "Araç / Altyapı Bileşeni", "Kullanım Amacı", "Erişim ve Kullanım Koşulu", "Sorumlu Rol / Birim"],
        [
            ["Araç", "Confluence", "Kontrollü süreç, prosedür, kılavuz ve şablonların yayımlanması ve ortak erişimi", "Kurumsal kullanıcı hesabı ve atanmış okuma/yazma yetkisi; uzaktan erişimde VPN", "Doküman Sorumlusu / Confluence Yöneticisi"],
            ["Altyapı", "Google Drive", "Kontrollü kayıtların, eklerin, onaylı kopyaların ve arşivlerin saklanması", "Kurumsal hesap ve rol bazlı klasör yetkisi", "Repository Sorumlusu / Doküman Sorumlusu"],
            ["Araç", "Jira", "Dokümanla ilişkili görev, değişiklik, gözden geçirme ve aksiyonların izlenmesi", "Proje veya süreç bazlı yetkilendirme", "Proje Yöneticisi / Jira Yöneticisi"],
            ["Araç", "Bitbucket", "Kodla ilişkili teknik kayıtların ve sürüm kontrollü dokümantasyon kaynaklarının yönetilmesi", "Proje repository yetkisi ve tanımlı branch/değişiklik kuralları", "Yazılım Geliştirme Ekibi / Bitbucket Yöneticisi"],
            ["Altyapı", "İÜC VPN ve kurumsal kimlik/yetkilendirme altyapısı", "Kurum dışından Confluence ve diğer yetkili sistemlere güvenli erişim", "Geçerli kurumsal hesap, VPN yetkisi ve bilgi güvenliği kuralları", "İÜC BİDB Altyapı ve Erişim Yönetimi"],
        ],
    )


def is_urunleri() -> str:
    return p("Bu süreç kapsamında kullanılan girdi iş ürünleri ve üretilen çıktı iş ürünleri, süreç özel kaydı olan LST.008 - İş Ürünleri ve Kalite Kriterleri Listesi (SRÇ.001) dokümanında yönetilir.")


def surec_akisi(*, view: bool = False) -> str:
    lines = [
        "flowchart TD",
        "A[Doküman ihtiyacı veya değişiklik ihtiyacı belirlenir] --> B[Doküman türü, kodu ve kullanılacak şablon belirlenir]",
        "B --> C[Doküman taslağı hazırlanır veya mevcut doküman güncellenir]",
        "C --> D[Doküman kalite kriterlerine ve şablona göre gözden geçirilir]",
        "D --> E{Doküman uygun mu?}",
        "E -- Hayır --> F[Düzeltme yapılır]",
        "F --> D",
        "E -- Evet --> G[Yetkili rol tarafından onaylanır]",
        "G --> H[Doküman repository üzerinde yayımlanır]",
        "H --> I[Aktif Dokümanlar Listesi ve ilgili kayıtlar güncellenir]",
        "I --> J[Hedef kitle bilgilendirilir]",
        "J --> K[Periyodik gözden geçirme, bakım veya arşivleme ihtiyacı izlenir]",
        "K --> A",
    ]
    code = "<br />".join(f'<code class="language-mermaid">{e(line)}</code>' for line in lines)
    if view:
        return (
            f'<p class="process-flow-image" style="text-align:center"><img src="attachments/{quote(FLOWCHART_FILENAME)}" '
            f'alt="{e(SRC001_TITLE)} süreç akışı" style="max-width:100%;height:auto" /></p>'
            + '<div class="confluence-information-macro has-no-icon confluence-information-macro-information conf-macro output-block" data-hasbody="true" data-macro-name="info">'
            + '<p class="title">Mermaid Kodu</p><div class="confluence-information-macro-body">'
            + f'<p style="margin-left:40px">{code}</p></div></div>'
        )
    return (
        f'<p><ac:image ac:height="900"><ri:attachment ri:filename="{e(FLOWCHART_FILENAME)}" /></ac:image></p>'
        + '<ac:structured-macro ac:name="info" ac:schema-version="1">'
        + '<ac:parameter ac:name="icon">false</ac:parameter>'
        + '<ac:parameter ac:name="title">Mermaid Kodu</ac:parameter>'
        + f'<ac:rich-text-body><p style="margin-left:40px">{code}</p></ac:rich-text-body>'
        + '</ac:structured-macro>'
    )


def faaliyet_table(headers: list[str]) -> str:
    if not headers:
        headers = ["No", "Faaliyet", "Açıklama", "Sorumlu", "Girdi", "Çıktı / Kayıt"]
    activities = [
        {"no":"1", "faaliyet":"Dokümantasyon stratejisini ve kapsamını uygula", "aciklama":"Doküman yönetimi kapsamı ve kullanılacak standart yaklaşım belirlenir.", "sorumlu":"Süreç Sahibi", "girdi":"Yeni doküman/değişiklik ihtiyacı", "cikti":"Dokümantasyon yaklaşımı, PRS.001", "bp":"SUP.7.BP1"},
        {"no":"2", "faaliyet":"Doküman standardı ve şablonu belirle", "aciklama":"Doküman türü, kodu, adlandırması ve kullanılacak şablon belirlenir.", "sorumlu":"Doküman Hazırlayan", "girdi":"Doküman ihtiyacı, şablon seti", "cikti":"Seçilen şablon ve doküman kodu", "bp":"SUP.7.BP2, SUP.7.BP3"},
        {"no":"3", "faaliyet":"Üretilecek dokümanı tanımla", "aciklama":"Yaşam döngüsü aşamasına göre üretilecek doküman ve amacı belirlenir.", "sorumlu":"Süreç Sahibi / Proje Ekibi", "girdi":"LST.005, proje/süreç ihtiyacı", "cikti":"Doküman ihtiyacı kaydı", "bp":"SUP.7.BP4"},
        {"no":"4", "faaliyet":"Dokümanı hazırla veya güncelle", "aciklama":"Doküman ilgili şablona, yazım kurallarına ve kalite kriterlerine uygun biçimde hazırlanır.", "sorumlu":"Doküman Hazırlayan", "girdi":"Şablon, gereksinimler, mevcut doküman", "cikti":"Taslak veya güncellenmiş doküman", "bp":"SUP.7.BP5"},
        {"no":"5", "faaliyet":"Dokümanı gözden geçir ve onaylat", "aciklama":"Doküman kalite kriterlerine göre gözden geçirilir ve yetkili rol tarafından onaylanır.", "sorumlu":"Gözden Geçiren / Onaylayan", "girdi":"Taslak doküman", "cikti":"Gözden geçirme ve onay kaydı", "bp":"SUP.7.BP6"},
        {"no":"6", "faaliyet":"Dokümanı yayımla ve erişime aç", "aciklama":"Onaylanan doküman repository üzerinde yayımlanır ve ilgili hedef kitleye erişilebilir hale getirilir.", "sorumlu":"Doküman Sorumlusu", "girdi":"Onaylı doküman", "cikti":"Yayımlanmış doküman, LST.001", "bp":"SUP.7.BP7"},
        {"no":"7", "faaliyet":"Dokümanı sürdür ve arşivle", "aciklama":"Doküman değişiklik, periyodik gözden geçirme, pasife alma ve arşivleme kriterlerine göre yönetilir.", "sorumlu":"Süreç Sahibi / Doküman Sorumlusu", "girdi":"Değişiklik/gözden geçirme ihtiyacı", "cikti":"LST.002, LST.003, güncel doküman", "bp":"SUP.7.BP8"},
    ]
    rows = []
    for item in activities:
        row = []
        for h in headers:
            n = norm(h)
            if "no" in n or "adim" in n or "sira" in n:
                row.append(e(item["no"]))
            elif "faaliyet" in n or "aktivite" in n:
                row.append(e(item["faaliyet"]))
            elif "aciklama" in n or "tanim" in n:
                row.append(e(item["aciklama"]))
            elif "sorumlu" in n or "rol" in n:
                row.append(e(item["sorumlu"]))
            elif "girdi" in n:
                row.append(e(item["girdi"]))
            elif "cikti" in n or "kayit" in n or "urun" in n:
                row.append(e(item["cikti"]))
            elif "bp" in n or "standart" in n or "izlen" in n:
                row.append(e(item["bp"]))
            else:
                row.append("")
        rows.append(row)
    return table(headers, rows)


def surec_faaliyetleri() -> str:
    return faaliyet_table(first_table_headers("11."))


def olcum() -> str:
    return p("Bu süreç kapsamında takip edilecek süreç performansı ölçüm seti, süreç özel kaydı olan LST.009 - Süreç Performans Ölçüm Seti (SRÇ.001) dokümanında yönetilir.")


def uygulama_uyarlama() -> str:
    custom = [
        ("13.1. Doküman Türleri ve Kodlama Yaklaşımı", "SRÇ.001 kapsamında süreç, form, liste/kayıt, prosedür, kılavuz/talimat ve plan türündeki dokümanlar kurumsal kodlama yapısına uygun olarak yönetilir. Doküman kodu, dokümanın türünü ve ilgili olduğu süreci izlenebilir kılacak şekilde kullanılır."),
        ("13.2. Doküman Adlandırma", "Doküman adları, doküman kodu ve dokümanın açık adını içerecek şekilde kullanılır. Sürece özel kayıt ve listelerde ilgili süreç kodu parantez içinde belirtilir."),
        ("13.3. Yazım Standartları", "Dokümanlar ilgili şablon, yazım kuralları ve kalite kriterlerine uygun biçimde hazırlanır. Zorunlu alanlar boş bırakılmaz; kullanılmayan alanlar gerekçeli olarak yönetilir."),
        ("13.4. Sürüm Tipleri", "Taslak, gözden geçirilmiş, onaylı, aktif, pasif ve arşiv durumları dokümanın yaşam döngüsü içinde kullanılır. Değişiklikler sürüm ve değişiklik kayıtları ile izlenir."),
        ("13.5. Dokümanların Dağıtımı ve Erişimi", "Onaylanan dokümanlar repository üzerinde yayımlanır. Erişim ihtiyacı olan hedef kitleye uygun bağlantı, duyuru veya bilgilendirme yoluyla erişim sağlanır."),
        ("13.6. Doküman Bakımı ve Arşivleme", "Dokümanlar yılda en az bir kez veya ihtiyaç halinde gözden geçirilir. Geçerliliğini yitiren dokümanlar pasife alınır veya arşivlenir; aktif doküman listesi güncel tutulur."),
    ]
    parts = []
    for h, text in custom:
        parts.append(f"<h3>{e(h)}</h3>")
        parts.append(p(text))
    parts.append("<h3>13.7. Uyarlama Kuralları</h3>")
    parts.append(table(["Uyarlama Alanı", "Kural"], [
        ["Zorunlu Adımlar", "Doküman türü/kodu belirleme, uygun şablon kullanma, zorunlu meta alanları doldurma, gözden geçirme/onay ihtiyacını değerlendirme, onaylı dokümanı repository üzerinde yayımlama ve aktif doküman listesini güncelleme adımları uyarlanamaz."],
        ["Uyarlanabilir Adımlar", "Doküman kapsamı, detay seviyesi, gözden geçirme yöntemi, dağıtım kapsamı ve proje özel doküman seti; süreç sahibi ve proje ihtiyacına göre uyarlanabilir."],
        ["Onay Gerektiren Durumlar", "Şablondan sapma, zorunlu bölümün kullanılmaması, dokümanın kapsam dışı bırakılması, pasife alma/arşivleme veya kritik doküman değişiklikleri süreç sahibi/onaylayan rol kararı gerektirir."],
    ]))
    return "".join(parts)


def etkilesimler() -> str:
    return p("Bu süreç kapsamındaki faaliyetlerin farklı süreçler ile olan etkileşimleri, süreç özel kaydı olan LST.007 - Süreç Etkileşim Matrisi (SRÇ.001) dokümanında yönetilir.")


def surum() -> str:
    return table(["Sürüm", "Tarih", "Açıklama", "Hazırlayan / Güncelleyen", "Gözden Geçiren", "Onay"], [
        ["v0.1", "10 Jan 2025", "İlk taslak oluşturuldu.", PREPARER, "-", "-"],
        ["v1.0", "15 Feb 2025", "Dokümantasyon Süreci onaylanarak yürürlüğe girmiştir.", PREPARER, REVIEWER, APPROVER],
    ])


def content_for(heading: str) -> str:
    n = norm(heading)
    if "surec bilgileri" in n: return surec_bilgileri()
    if n == "amac" or n.endswith("amac"): return amac()
    if "kapsam" in n: return kapsam()
    if "referans" in n: return referanslar()
    if "terim" in n or "kisalt" in n: return terimler()
    if "surec aktivitesi" in n: return surec_aktivitesi()
    if "rol" in n or "sorumluluk" in n: return roller()
    if "arac" in n and "altyapi" in n: return araclar_altyapi()
    if "is" in n and "urun" in n: return is_urunleri()
    if "surec akisi" in n: return surec_akisi()
    if "surec faaliyet" in n: return surec_faaliyetleri()
    if "olcum" in n or "izleme" in n: return olcum()
    if "uygulama" in n or "uyarlama" in n: return uygulama_uyarlama()
    if "etkilesim" in n: return etkilesimler()
    if "surum" in n: return surum()
    raise RuntimeError(f"Şablon bölümü için SRÇ.001 içeriği tanımlı değil: {heading}")


def build_storage_body(sections: list[str]) -> str:
    parts = []
    for h in sections:
        parts.append(f"<h2>{e(h)}</h2>")
        parts.append(content_for(h))
    return "".join(parts) + "\n"


def build_view_html(storage: str) -> str:
    view_body = storage.replace(surec_akisi(), surec_akisi(view=True))
    return f"""<!doctype html>
<html lang="tr">
<head><meta charset="utf-8"><title>{e(SRC001_TITLE)}</title><style>{CSS}</style></head>
<body><main class="confluence-page"><h1>{e(SRC001_TITLE)}</h1>{view_body}</main></body>
</html>
"""


def write_report(sections: list[str]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# SRÇ.001 Süreç Tanımı Yeniden Oluşturma Raporu", "",
        "Kapsam: Yalnızca `SRÇ.001 - Dokümantasyon Süreci` oluşturuldu.", "",
        "## Uygulanan Şablon Bölümleri", *[f"- {s}" for s in sections], "",
        "## Kontroller",
        "- 0 numaralı şablon bölümleri SRÇ.001 içeriğine alınmadı.",
        "- 6. Süreç Aktivitesi sabit satırları korundu.",
        "- 7, 9, 12 ve 14. maddelerde şablon metin yapısı korundu.",
        "- 8. Araçlar ve Altyapı bölümü süreç özel kayıtlarla dolduruldu.",
        "- 4. Referanslar üç ISO/IEC 15504-5 referansıyla sınırlandı.",
        "- 6. Süreç Aktivitesi içindeki ilgili süreçler alt alta gösterildi.",
        "- 10. Süreç Akışına PNG görseli ve Mermaid kod bloğu birlikte eklendi.",
        "- 11. Süreç Faaliyetleri tablo başlıkları şablondan okundu.",
        "- 13. madde süreç özel alt başlıklarla dolduruldu ve Uyarlama Kuralları tablosu eklendi.",
        "- Süreç sürümü v1.0 olarak ve sürüm geçmişi v0.1/v1.0 satırlarıyla standartlaştırıldı.",
        "- Süreç sahibi, gözden geçiren ve onaycı doğrulanan bilgilerle yazıldı.", "",
    ]
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    sections = extract_h2_sections()
    storage = build_storage_body(sections)
    if re.search(r"<h2>\s*0\s*[\.-]", storage):
        raise RuntimeError("0 numaralı bölüm SRÇ.001 gövdesine dahil edildi.")
    if not storage.lstrip().startswith("<h2>1."):
        raise RuntimeError("SRÇ.001 gövdesi 1. bölümle başlamıyor.")
    required = [
        "ISO/IEC 15504-5:2006 - Process Assessment Model",
        "ISO/IEC 15504-5:2006 - Process Attributes",
        "flowchart TD", FLOWCHART_FILENAME, PROCESS_OWNER, REVIEWER, APPROVER,
        "10 Jan 2025", "15 Feb 2025",
    ]
    plain_storage = html.unescape(storage)
    missing = [item for item in required if item not in plain_storage]
    if missing:
        raise RuntimeError(f"SRÇ.001 zorunlu içerik eksik: {missing}")
    reference_section = plain_storage.split("<h2>4. Referanslar</h2>", 1)[1].split("<h2>5.", 1)[0]
    if len(re.findall(r"<tr>", reference_section)) != 4:
        raise RuntimeError("SRÇ.001 Referanslar bölümü başlık dahil tam üç referans içermelidir.")
    history_section = plain_storage.split("<h2>15. Sürüm Geçmişi</h2>", 1)[1]
    if len(re.findall(r"<td[^>]*>v(?:0\.1|1\.0)</td>", history_section)) != 2:
        raise RuntimeError("SRÇ.001 sürüm geçmişi v0.1 ve v1.0 satırlarından oluşmalıdır.")
    if not (SRC001_DIR / "attachments" / FLOWCHART_FILENAME).exists():
        raise RuntimeError(f"SRÇ.001 süreç akış PNG dosyası bulunamadı: {FLOWCHART_FILENAME}")
    (SRC001_DIR / "body.storage.xhtml").write_text(storage, encoding="utf-8")
    (SRC001_DIR / "body.view.html").write_text(build_view_html(storage), encoding="utf-8")
    write_report(sections)
    print("[DONE] SRÇ.001 süreç tanımı düzeltme kurallarına göre oluşturuldu.")
    print(f"[REPORT] {REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
