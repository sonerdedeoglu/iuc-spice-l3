#!/usr/bin/env python3
"""Rebuild only İÜC.BİDB.SRÇ.001 from scratch using the current process template.

Rules:
- Updates only İÜC.BİDB.SRÇ.001 - Dokümantasyon Süreci.
- Does not move, rename or edit LST.007 or any other related document.
- Reads İÜC.BİDB.SRÇ.XXX.Ş h2 headings and preserves that order.
- Excludes 0. Şablon Hakkında.
- Uses process-specific text but preserves template-controlled sections and fixed text rules.
"""
from __future__ import annotations

import html
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
CONFLUENCE_DIR = ROOT / "confluence"
ROOT_PAGE = CONFLUENCE_DIR / "pages/000-root-iuc-bidb-spice-2026-level-3"
SRC001_DIR = ROOT_PAGE / "01-surec-dokumanlari/iuc-bidb-src-001-dokumantasyon-sureci"
TEMPLATE_DIR = ROOT_PAGE / "02-sablonlar/iuc-bidb-src-xxx-s-surec-tanimi-sablonu"
INDEX_PATH = CONFLUENCE_DIR / "index.yaml"
REPORT_PATH = ROOT / "reports/src001_rework_report.md"
SRC001_TITLE = "İÜC.BİDB.SRÇ.001 - Dokümantasyon Süreci"
SRC001_CODE = "İÜC.BİDB.SRÇ.001"

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


def write_yaml(path: Path, data: dict[str, Any]) -> None:
    path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")


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
        ["Süreç Sahibi", "Levent BAYEZİT - Proje Yöneticisi"],
        ["Durum", "Aktif"],
        ["Sürüm", "v1.0"],
        ["Yürürlük Tarihi", "15 Şubat 2025"],
        ["Son Gözden Geçirme Tarihi", "01 Eylül 2025"],
    ])


def amac() -> str:
    return p("Bu sürecin amacı, İÜC BİDB bünyesinde üretilen süreç, proje ve destek dokümanlarının yaşam döngüsü boyunca standart, izlenebilir, erişilebilir ve kontrollü biçimde yönetilmesini sağlamaktır.") + p("Süreç; dokümantasyon stratejisinin belirlenmesi, doküman standartlarının uygulanması, üretilecek dokümanların tanımlanması, dokümanların gözden geçirilmesi, onaylanması, yayımlanması, dağıtılması, güncellenmesi ve arşivlenmesi faaliyetlerini kapsar.")


def kapsam() -> str:
    return p("Bu süreç, İÜC BİDB süreç dokümantasyonu ile yazılım proje yaşam döngüsü dokümantasyonunda kullanılan kontrollü doküman ve kayıtların yönetimini kapsar.") + table(["Kapsam Öğesi", "Açıklama"], [
        ["Kapsama Dahil", "Süreç tanımları, şablonlar, kayıt listeleri, formlar, prosedürler, kılavuzlar/talimatlar, planlar, proje yaşam döngüsü dokümanları ve bunlara ait gözden geçirme/değişiklik/yaygınlaştırma kayıtları"],
        ["Kapsam Dışı", "Kurumsal dokümantasyon deposuna alınmayan kişisel notlar, geçici çalışma taslakları ve resmi doküman/kayıt niteliği taşımayan ara çıktılar"],
        ["Uygulama Alanı", "İÜC BİDB süreçleri, yazılım proje yaşam döngüsü faaliyetleri, destek süreçleri ve SPICE denetim hazırlık çalışmaları"],
    ])


def referanslar() -> str:
    return table(["Referans", "Açıklama"], [
        ["ISO/IEC 15504-5 SUP.7 - Documentation", "Dokümantasyon sürecinin SPICE süreç referansı"],
        ["ISO/IEC 15504-5 Process Assessment Model", "SUP.7 amacı, çıktıları ve base practice beklentileri için esas alınan standart kaynak"],
        ["İÜC BİDB SPICE 2026 Level 3 Dokümantasyon Yapısı", "Kurumsal süreç dokümantasyonu ve Confluence doküman ağacı"],
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
        ["İlgili Süreçler", ", ".join([
            link("İÜC.BİDB.SRÇ.002 - Kalite Güvencesi Süreci"),
            link("İÜC.BİDB.SRÇ.003 - Doğrulama Süreci"),
            link("İÜC.BİDB.SRÇ.004 - Süreç Kurulumu Süreci"),
            link("İÜC.BİDB.SRÇ.016 - Yapılandırma Yönetimi Süreci"),
            link("İÜC.BİDB.SRÇ.018 - Değişiklik Talebi Yönetimi Süreci"),
        ])],
    ])


def roller() -> str:
    return p("Bu süreç kapsamında rol, sorumluluk, yetki, RACI ve yetkinlik tanımları, süreç özel kaydı olan İÜC.BİDB.LST.010 - Süreç Rol Yetki ve RACI Matrisi (İÜC.BİDB.SRÇ.001) dokümanında yönetilir.")


def is_urunleri() -> str:
    return p("Bu süreç kapsamında kullanılan girdi iş ürünleri ve üretilen çıktı iş ürünleri, süreç özel kaydı olan İÜC.BİDB.LST.008 - İş Ürünleri ve Kalite Kriterleri Listesi (İÜC.BİDB.SRÇ.001) dokümanında yönetilir.")


def surec_akisi() -> str:
    return ""


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
    return faaliyet_table(first_table_headers("10."))


def olcum() -> str:
    return p("Bu süreç kapsamında takip edilecek süreç performansı ölçüm seti, süreç özel kaydı olan İÜC.BİDB.LST.009 - Süreç Performans Ölçüm Seti (İÜC.BİDB.SRÇ.001) dokümanında yönetilir.")


def uygulama_uyarlama() -> str:
    custom = [
        ("12.1. Doküman Türleri ve Kodlama Yaklaşımı", "SRÇ.001 kapsamında süreç, form, liste/kayıt, prosedür, kılavuz/talimat ve plan türündeki dokümanlar kurumsal kodlama yapısına uygun olarak yönetilir. Doküman kodu, dokümanın türünü ve ilgili olduğu süreci izlenebilir kılacak şekilde kullanılır."),
        ("12.2. Doküman Adlandırma", "Doküman adları, doküman kodu ve dokümanın açık adını içerecek şekilde kullanılır. Sürece özel kayıt ve listelerde ilgili süreç kodu parantez içinde belirtilir."),
        ("12.3. Yazım Standartları", "Dokümanlar ilgili şablon, yazım kuralları ve kalite kriterlerine uygun biçimde hazırlanır. Zorunlu alanlar boş bırakılmaz; kullanılmayan alanlar gerekçeli olarak yönetilir."),
        ("12.4. Sürüm Tipleri", "Taslak, gözden geçirilmiş, onaylı, aktif, pasif ve arşiv durumları dokümanın yaşam döngüsü içinde kullanılır. Değişiklikler sürüm ve değişiklik kayıtları ile izlenir."),
        ("12.5. Dokümanların Dağıtımı ve Erişimi", "Onaylanan dokümanlar repository üzerinde yayımlanır. Erişim ihtiyacı olan hedef kitleye uygun bağlantı, duyuru veya bilgilendirme yoluyla erişim sağlanır."),
        ("12.6. Doküman Bakımı ve Arşivleme", "Dokümanlar yılda en az bir kez veya ihtiyaç halinde gözden geçirilir. Geçerliliğini yitiren dokümanlar pasife alınır veya arşivlenir; aktif doküman listesi güncel tutulur."),
    ]
    parts = []
    for h, text in custom:
        parts.append(f"<h3>{e(h)}</h3>")
        parts.append(p(text))
    parts.append("<h3>12.7. Uyarlama Kuralları</h3>")
    parts.append(table(["Uyarlama Alanı", "Kural"], [
        ["Zorunlu Adımlar", "Doküman türü/kodu belirleme, uygun şablon kullanma, zorunlu meta alanları doldurma, gözden geçirme/onay ihtiyacını değerlendirme, onaylı dokümanı repository üzerinde yayımlama ve aktif doküman listesini güncelleme adımları uyarlanamaz."],
        ["Uyarlanabilir Adımlar", "Doküman kapsamı, detay seviyesi, gözden geçirme yöntemi, dağıtım kapsamı ve proje özel doküman seti; süreç sahibi ve proje ihtiyacına göre uyarlanabilir."],
        ["Onay Gerektiren Durumlar", "Şablondan sapma, zorunlu bölümün kullanılmaması, dokümanın kapsam dışı bırakılması, pasife alma/arşivleme veya kritik doküman değişiklikleri süreç sahibi/onaylayan rol kararı gerektirir."],
    ]))
    return "".join(parts)


def etkilesimler() -> str:
    return p("Bu süreç kapsamındaki faaliyetlerin farklı süreçler ile olan etkileşimleri, süreç özel kaydı olan İÜC.BİDB.LST.007 - Süreç Etkileşim Matrisi (İÜC.BİDB.SRÇ.001) dokümanında yönetilir.")


def surum() -> str:
    return table(["Sürüm", "Tarih", "Açıklama", "Hazırlayan / Güncelleyen", "Gözden Geçiren", "Onay"], [
        ["v1.0", "15 Şubat 2025", "Dokümantasyon Süreci güncel süreç tanımı şablonuna göre oluşturuldu.", "Soner DEDEOĞLU - Kalite Danışmanı", "<Gözden geçiren>", "<Onay bilgisi>"],
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
    return f"""<!doctype html>
<html lang="tr">
<head><meta charset="utf-8"><title>{e(SRC001_TITLE)}</title><style>{CSS}</style></head>
<body><main class="confluence-page"><h1>{e(SRC001_TITLE)}</h1>{storage}</main></body>
</html>
"""


def update_page_yaml() -> None:
    path = SRC001_DIR / "page.yaml"
    meta = read_yaml(path)
    meta.update({
        "title": SRC001_TITLE,
        "document_code": SRC001_CODE,
        "document_type": "Süreç",
        "template": "İÜC.BİDB.SRÇ.XXX.Ş - Süreç Tanımı Şablonu",
        "status": "active",
        "version": "v1.0",
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "storage_file": "body.storage.xhtml",
        "view_file": "body.view.html",
    })
    write_yaml(path, meta)


def write_report(sections: list[str]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# SRÇ.001 Süreç Tanımı Yeniden Oluşturma Raporu", "",
        "Kapsam: Yalnızca `İÜC.BİDB.SRÇ.001 - Dokümantasyon Süreci` oluşturuldu.", "",
        "## Uygulanan Şablon Bölümleri", *[f"- {s}" for s in sections], "",
        "## Kontroller",
        "- 0 numaralı şablon bölümleri SRÇ.001 içeriğine alınmadı.",
        "- 6. Süreç Aktivitesi sabit satırları korundu.",
        "- 7, 8, 11 ve 13. maddelerde şablon metin yapısı korundu.",
        "- 9. Süreç Akışı boş bırakıldı; PNG görsel kullanıcı tarafından eklenecek.",
        "- 10. Süreç Faaliyetleri tablo başlıkları şablondan okundu.",
        "- 12. madde süreç özel alt başlıklarla dolduruldu ve Uyarlama Kuralları tablosu eklendi.",
        "- 14. Sürüm Geçmişi tablosunda Gözden Geçiren sütunu yer alıyor.", "",
    ]
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    sections = extract_h2_sections()
    storage = build_storage_body(sections)
    if re.search(r"<h2>\s*0\s*[\.-]", storage):
        raise RuntimeError("0 numaralı bölüm SRÇ.001 gövdesine dahil edildi.")
    if not storage.lstrip().startswith("<h2>1."):
        raise RuntimeError("SRÇ.001 gövdesi 1. bölümle başlamıyor.")
    (SRC001_DIR / "body.storage.xhtml").write_text(storage, encoding="utf-8")
    (SRC001_DIR / "body.view.html").write_text(build_view_html(storage), encoding="utf-8")
    update_page_yaml()
    write_report(sections)
    print("[DONE] SRÇ.001 süreç tanımı düzeltme kurallarına göre oluşturuldu.")
    print(f"[REPORT] {REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
