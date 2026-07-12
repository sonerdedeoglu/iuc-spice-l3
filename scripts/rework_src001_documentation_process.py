#!/usr/bin/env python3
"""Rebuild only İÜC.BİDB.SRÇ.001 from scratch using the current process template.

Rules:
- Updates only İÜC.BİDB.SRÇ.001 - Dokümantasyon Süreci.
- Does not move, rename or edit LST.007 or any other related document.
- Reads İÜC.BİDB.SRÇ.XXX.Ş h2 headings and preserves that order.
- Excludes 0. Şablon Hakkında.
- Preserves 12. Uygulama ve Uyarlama Kuralları sub-headings from the template.
- Produces Mermaid source blocks where diagrams are expected; PNG files are not generated.
"""
from __future__ import annotations

import html
import re
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
    'pre{background:#f6f8fa;border:1px solid #d8dee4;border-radius:6px;padding:12px;overflow:auto}'
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
    value = strip_tags(value).lower()
    value = re.sub(r"^\s*\d+(?:\.\d+)?\s*[\.-]\s*", "", value)
    tr = str.maketrans({"ı":"i","ş":"s","ç":"c","ö":"o","ü":"u","ğ":"g","İ":"i","Ş":"s","Ç":"c","Ö":"o","Ü":"u","Ğ":"g"})
    return re.sub(r"\s+", " ", value.translate(tr)).strip()


def template_body() -> str:
    return (TEMPLATE_DIR / "body.storage.xhtml").read_text(encoding="utf-8")


def extract_h2_sections() -> list[str]:
    headings = [strip_tags(m) for m in re.findall(r"<h2[^>]*>(.*?)</h2>", template_body(), flags=re.I | re.S)]
    sections = [h for h in headings if h and not re.match(r"^\s*0\s*[\.-]", h)]
    if not sections or not sections[0].startswith("1."):
        raise RuntimeError(f"Şablondan beklenen h2 yapısı okunamadı: {sections[:3]}")
    return sections


def extract_subheads_for_section(section_prefix: str) -> list[str]:
    body = template_body()
    m = re.search(rf"<h2[^>]*>\s*{re.escape(section_prefix)}[^<]*</h2>(.*?)(?=<h2[^>]*>\s*\d+\s*[\.-]|\Z)", body, flags=re.I | re.S)
    if not m:
        return []
    return [strip_tags(x) for x in re.findall(r"<h3[^>]*>(.*?)</h3>", m.group(1), flags=re.I | re.S)]


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


def mermaid(src: str) -> str:
    return f'<pre><code class="language-mermaid">{e(src.strip())}</code></pre>'


def surec_bilgileri() -> str:
    return table(["Alan", "Değer"], [
        ["Kurum", "İstanbul Üniversitesi - Cerrahpaşa Bilgi İşlem Daire Başkanlığı"],
        ["Süreç Kodu ve Adı", f"{SRC001_CODE} - Dokümantasyon Süreci"],
        ["Süreç Referansı", "ISO/IEC 15504-5 SUP.7 - Documentation"],
        ["Süreç Sahibi", "Levent BAYEZİT - Proje Yöneticisi"],
        ["Durum", "Aktif"],
        ["Sürüm", "v1.0"],
        ["Yürürlük Tarihi", "29-06-2026"],
        ["Son Gözden Geçirme Tarihi", "01-07-2026"],
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


def aktivite_ozet() -> str:
    return table(["Alan", "Açıklama"], [
        ["Süreç Başlatıcısı", "Yeni doküman ihtiyacı, doküman değişiklik ihtiyacı, proje yaşam döngüsü aşaması, süreç gözden geçirme sonucu, denetim bulgusu veya iyileştirme ihtiyacı"],
        ["Başlangıç", "Doküman ihtiyacının veya mevcut dokümanda değişiklik/bakım ihtiyacının belirlenmesi"],
        ["Bitiş", "Dokümanın onaylanması, yayımlanması, dağıtılması, güncellenmesi, pasife alınması veya arşivlenmesi"],
        ["Temel Yaklaşım", "Dokümanlar ilgili şablon ve kalite kriterlerine göre hazırlanır; gözden geçirilir; yetkili rol tarafından onaylanır; repository üzerinden yayımlanır; değişiklik ve gözden geçirme kayıtlarıyla sürdürülür."],
    ])


def roller() -> str:
    return table(["Referans Kayıt", "Kullanım"], [
        [link("İÜC.BİDB.LST.010 - Süreç Rol Yetki ve RACI Matrisi (İÜC.BİDB.SRÇ.001)"), "SRÇ.001 kapsamındaki rol, sorumluluk, yetki, RACI ve yetkinlik gereksinimlerinin güncel kaydıdır. Roller süreç dokümanında tekrar tanımlanmaz; ilgili kayıt üzerinden yönetilir."],
    ])


def is_urunleri() -> str:
    return table(["İş Ürünü", "Amaç", "Kontrol / Kalite Kriteri", "İlgili Kayıt"], [
        [link("İÜC.BİDB.PRS.001 - Yazılım Projeleri Dokümantasyon Prosedürü"), "Dokümantasyon stratejisi ve uygulama kurallarını tanımlamak", "Onaylı, yürürlükte ve SRÇ.001 ile uyumlu olmalıdır", link("İÜC.BİDB.LST.001 - Aktif Dokümanlar Listesi")],
        [link("İÜC.BİDB.LST.001 - Aktif Dokümanlar Listesi"), "Aktif doküman envanterini izlemek", "Doküman kodu, ad, sürüm, durum ve erişim bilgisi güncel olmalıdır", link("İÜC.BİDB.LST.002 - Doküman Değişiklik Kaydı")],
        [link("İÜC.BİDB.LST.003 - Doküman Gözden Geçirme Kaydı"), "Gözden geçirme ve uygunluk kayıtlarını izlemek", "Gözden geçirme sonucu, sorumlu ve karar bilgisi içermelidir", link("İÜC.BİDB.LST.008 - İş Ürünleri ve Kalite Kriterleri Listesi (İÜC.BİDB.SRÇ.001)")],
        [link("İÜC.BİDB.LST.005 - Yaşam Döngüsü Doküman İhtiyaç Matrisi"), "Yaşam döngüsü aşamalarına göre üretilecek dokümanları belirlemek", "Aşama, doküman türü, sorumlu ve kullanım amacı net olmalıdır", link("İÜC.BİDB.LST.008 - İş Ürünleri ve Kalite Kriterleri Listesi (İÜC.BİDB.SRÇ.001)")],
        [link("İÜC.BİDB.FRM.001 - Süreç Gözden Geçirme Formu (İÜC.BİDB.SRÇ.001)"), "SRÇ.001 BP/GP uygunluğunu ve tamamlayıcı aksiyonları izlemek", "BP/GP, durum, kanıt ve aksiyon alanları dolu olmalıdır", link("İÜC.BİDB.LST.009 - Süreç Performans Ölçüm Seti (İÜC.BİDB.SRÇ.001)")],
    ])


def surec_akisi() -> str:
    code = """
flowchart TD
    A[Doküman ihtiyacı veya değişiklik ihtiyacı belirlenir] --> B[Doküman türü, kodu ve şablonu belirlenir]
    B --> C[Doküman taslağı hazırlanır veya mevcut doküman güncellenir]
    C --> D[Kalite kriterlerine göre gözden geçirme yapılır]
    D --> E{Uygun mu?}
    E -- Hayır --> F[Düzeltme yapılır]
    F --> D
    E -- Evet --> G[Yetkili rol tarafından onaylanır]
    G --> H[Repository üzerinde yayımlanır]
    H --> I[Aktif doküman listesi ve ilgili kayıtlar güncellenir]
    I --> J[Hedef kitle bilgilendirilir]
    J --> K[Periyodik gözden geçirme ve bakım yapılır]
"""
    return p("Aşağıdaki Mermaid kodu süreç akış diyagramının kaynak kodudur. PNG çıktısı ayrıca üretilerek dokümana görsel olarak eklenebilir.") + mermaid(code)


def faaliyetler() -> str:
    return table(["Adım", "Faaliyet", "SUP.7 İzlenebilirliği", "Çıktı / Kayıt"], [
        ["1", "Dokümantasyon yönetim stratejisini ve kapsamını belirle", "SUP.7.BP1", link("İÜC.BİDB.PRS.001 - Yazılım Projeleri Dokümantasyon Prosedürü")],
        ["2", "Doküman türü, kodlama, şablon ve yazım kurallarını uygula", "SUP.7.BP2", link("İÜC.BİDB.KLV.001 - Doküman Yazım Kuralları Talimatı")],
        ["3", "Doküman gereksinimlerini ve kalite kriterlerini belirle", "SUP.7.BP3", link("İÜC.BİDB.LST.008 - İş Ürünleri ve Kalite Kriterleri Listesi (İÜC.BİDB.SRÇ.001)")],
        ["4", "Yaşam döngüsünde üretilecek dokümanları belirle", "SUP.7.BP4", link("İÜC.BİDB.LST.005 - Yaşam Döngüsü Doküman İhtiyaç Matrisi")],
        ["5", "Dokümanı ilgili şablona göre hazırla veya güncelle", "SUP.7.BP5", "Taslak / güncellenmiş doküman"],
        ["6", "Dokümanı gözden geçir ve onaylat", "SUP.7.BP6", link("İÜC.BİDB.LST.003 - Doküman Gözden Geçirme Kaydı")],
        ["7", "Onaylanan dokümanı yayımla ve erişilebilir hale getir", "SUP.7.BP7", link("İÜC.BİDB.LST.001 - Aktif Dokümanlar Listesi")],
        ["8", "Dokümanı bakım, değişiklik ve arşivleme kriterlerine göre sürdür", "SUP.7.BP8", link("İÜC.BİDB.LST.002 - Doküman Değişiklik Kaydı")],
    ])


def olcum() -> str:
    return table(["Ölçüm / İzleme Alanı", "Yöntem", "Kayıt"], [
        ["Dokümanların şablona uygunluğu", "Gözden geçirme ve kalite kriteri kontrolü", link("İÜC.BİDB.LST.003 - Doküman Gözden Geçirme Kaydı")],
        ["Aktif doküman envanterinin güncelliği", "Aktif doküman listesi üzerinden dönemsel kontrol", link("İÜC.BİDB.LST.001 - Aktif Dokümanlar Listesi")],
        ["Doküman değişikliklerinin izlenebilirliği", "Değişiklik kayıtlarının kontrol edilmesi", link("İÜC.BİDB.LST.002 - Doküman Değişiklik Kaydı")],
        ["Süreç performansı", "SRÇ.001 performans göstergelerinin izlenmesi", link("İÜC.BİDB.LST.009 - Süreç Performans Ölçüm Seti (İÜC.BİDB.SRÇ.001)")],
        ["Süreç yaygınlaştırma durumu", "Bilgilendirme/yaygınlaştırma kayıtlarının kontrolü", link("İÜC.BİDB.LST.012 - Süreç Yaygınlaştırma ve Bilgilendirme Kaydı")],
    ])


def uygulama_uyarlama() -> str:
    subheads = extract_subheads_for_section("12.")
    if not subheads:
        subheads = ["12.1. Uygulama Kapsamı", "12.2. Uyarlama Kuralları", "12.3. İstisna Yönetimi", "12.4. Uygunluk Kontrolü"]
    parts: list[str] = []
    for sh in subheads:
        parts.append(f"<h3>{e(sh)}</h3>")
        n = norm(sh)
        if "kapsam" in n:
            parts.append(p("SRÇ.001, İÜC BİDB süreç dokümantasyonu ve yazılım proje dokümantasyonu için uygulanır. Her kontrollü doküman ilgili tür, kod, şablon, sahiplik, gözden geçirme, onay, yayın ve bakım kurallarına göre yönetilir."))
        elif "uyarl" in n:
            parts.append(table(["Uyarlama Alanı", "Kural"], [
                ["Doküman türü", "Doküman türü süreç veya proje ihtiyacına göre belirlenebilir; ancak kodlama, sahiplik ve onay alanları korunur."],
                ["Şablon kullanımı", "İlgili doküman türü için tanımlı şablon esas alınır; kullanılmayan bölüm varsa gerekçe dokümanda veya gözden geçirme kaydında belirtilir."],
                ["Proje dokümantasyonu", "Proje büyüklüğü ve yaşam döngüsü aşamasına göre LST.005 doküman ihtiyaç matrisi esas alınır."],
            ]))
        elif "istisna" in n or "sapma" in n:
            parts.append(p("Şablon, kodlama, onay veya yayın kurallarından sapma gerekiyorsa sapmanın gerekçesi süreç sahibi veya yetkili rol tarafından değerlendirilir. Kabul edilen istisna ilgili değişiklik/gözden geçirme kaydında izlenir."))
        elif "uygun" in n or "kontrol" in n or "gozden" in n:
            parts.append(p("Sürecin uygulanma uygunluğu LST.003, LST.008, LST.009 ve FRM.001 kayıtları üzerinden izlenir. Uygunsuzluk veya eksik kanıt tespit edilirse tamamlayıcı aksiyon açılır."))
        else:
            parts.append(p("Bu alt başlık kapsamında SRÇ.001 uygulaması, ilgili dokümantasyon kayıtları ve süreç sahibi sorumluluğunda yönetilir. Gereken kanıtlar ilgili liste, form veya prosedür kayıtlarına bağlanır."))
    return "".join(parts)


def etkilesimler() -> str:
    code = """
flowchart LR
    SR001[SRÇ.001 Dokümantasyon Süreci]
    SR002[SRÇ.002 Kalite Güvencesi]
    SR003[SRÇ.003 Doğrulama]
    SR004[SRÇ.004 Süreç Kurulumu]
    SR016[SRÇ.016 Yapılandırma Yönetimi]
    SR018[SRÇ.018 Değişiklik Talebi Yönetimi]
    SR025[SRÇ.025 Ölçüm]

    SR004 -->|Süreç dokümanı ihtiyacı| SR001
    SR001 -->|Doküman ve kayıtlar| SR002
    SR003 -->|Gözden geçirme / doğrulama sonucu| SR001
    SR016 <--> |Sürüm, baseline, repository| SR001
    SR018 -->|Doküman değişiklik talebi| SR001
    SR001 -->|Performans verisi| SR025
"""
    return table(["Etkileşim", "Açıklama", "Kayıt"], [
        ["SRÇ.004 ↔ SRÇ.001", "Süreç kurulumu sırasında üretilecek süreç dokümanları ve şablon uyumu yönetilir.", link("İÜC.BİDB.LST.007 - Süreç Mimari ve Etkileşim Matrisi")],
        ["SRÇ.002 ↔ SRÇ.001", "Doküman kalite kriterleri ve uygunsuzluk/tamamlayıcı aksiyonlar kalite güvence kapsamında izlenir.", link("İÜC.BİDB.LST.008 - İş Ürünleri ve Kalite Kriterleri Listesi (İÜC.BİDB.SRÇ.001)")],
        ["SRÇ.003 ↔ SRÇ.001", "Doküman gözden geçirme ve doğrulama sonuçları SRÇ.001 bakım faaliyetlerine girdi sağlar.", link("İÜC.BİDB.LST.003 - Doküman Gözden Geçirme Kaydı")],
        ["SRÇ.016 ↔ SRÇ.001", "Doküman sürümü, baseline, repository ve değişiklik kontrolü yapılandırma yönetimi ile uyumlu yürütülür.", link("İÜC.BİDB.LST.002 - Doküman Değişiklik Kaydı")],
        ["SRÇ.018 ↔ SRÇ.001", "Doküman değişiklik talepleri değerlendirilir ve uygun görülenler doküman bakım faaliyetine alınır.", link("İÜC.BİDB.LST.002 - Doküman Değişiklik Kaydı")],
    ]) + p("Aşağıdaki Mermaid kodu süreç etkileşim diyagramının kaynak kodudur. PNG çıktısı ayrıca üretilerek dokümana görsel olarak eklenebilir.") + mermaid(code)


def surum() -> str:
    return table(["Sürüm", "Tarih", "Açıklama", "Hazırlayan / Güncelleyen", "Onay"], [
        ["v1.0", "29-06-2026", "Dokümantasyon Süreci güncel süreç tanımı şablonuna göre sıfırdan oluşturuldu.", "Soner DEDEOĞLU - Kalite Danışmanı", "Levent BAYEZİT - Dokümantasyon Süreç Sahibi"],
    ])


def content_for(heading: str) -> str:
    n = norm(heading)
    if "surec bilgileri" in n: return surec_bilgileri()
    if n == "amac" or n.endswith("amac"): return amac()
    if "kapsam" in n: return kapsam()
    if "referans" in n: return referanslar()
    if "terim" in n or "kisalt" in n: return terimler()
    if "aktivite" in n: return aktivite_ozet()
    if "rol" in n or "sorumluluk" in n: return roller()
    if "is" in n and "urun" in n: return is_urunleri()
    if "akis" in n: return surec_akisi()
    if "faaliyet" in n: return faaliyetler()
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


def build_view_html(storage_body: str) -> str:
    return f"""<!doctype html>
<html lang="tr">
<head>
  <meta charset="utf-8">
  <title>{e(SRC001_TITLE)}</title>
  <style>{CSS}</style>
</head>
<body>
<main class="confluence-page">
<h1>{e(SRC001_TITLE)}</h1>
{storage_body}
</main>
</body>
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
    subheads = extract_subheads_for_section("12.")
    lines = [
        "# SRÇ.001 Süreç Tanımı Yeniden Oluşturma Raporu",
        "",
        "Kapsam: Yalnızca `İÜC.BİDB.SRÇ.001 - Dokümantasyon Süreci` sıfırdan oluşturuldu.",
        "",
        "## Uygulanan Şablon Bölümleri",
        *[f"- {s}" for s in sections],
        "",
        "## 12. Madde Alt Başlıkları",
        *[f"- {s}" for s in subheads],
        "",
        "## Kontroller",
        "- 0 numaralı şablon bölümleri SRÇ.001 içeriğine alınmadı.",
        "- SRÇ.001 gövdesi doğrudan 1. bölümle başlatıldı.",
        "- Eski SRÇ.001 gövdesi taşınmadı; içerik baştan oluşturuldu.",
        "- Mermaid kaynak kodları süreç akışı ve süreç etkileşimleri bölümlerine eklendi.",
        "- LST.007 veya diğer ilişkili dokümanlarda taşıma/yeniden adlandırma/değişiklik yapılmadı.",
        "",
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
    print("[DONE] SRÇ.001 süreç tanımı şablona göre sıfırdan oluşturuldu.")
    print(f"[REPORT] {REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
