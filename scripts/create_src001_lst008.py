#!/usr/bin/env python3
"""Create/replace LST.008 for İÜC.BİDB.SRÇ.001.

This script updates the existing SRÇ.001 child page:
İÜC.BİDB.LST.008 - İş Ürünleri ve Kalite Kriterleri Listesi (İÜC.BİDB.SRÇ.001)

It intentionally replaces the old local body content in place. The existing page_id is
preserved so Confluence publishing updates the same page instead of creating a duplicate.
"""
from __future__ import annotations

import html
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
ROOT_PAGE = ROOT / "confluence/pages/000-root-iuc-bidb-spice-2026-level-3"
SRC001_BODY = ROOT_PAGE / "01-surec-dokumanlari/iuc-bidb-src-001-dokumantasyon-sureci/body.storage.xhtml"
PAGE_DIR = ROOT_PAGE / "01-surec-dokumanlari/iuc-bidb-src-001-dokumantasyon-sureci/iuc-bidb-lst-008-is-urunleri-ve-kalite-kriterleri-listesi-iuc-bidb-src-001"
STANDARD_PATH = ROOT / "resources/standards/spice_practices.yaml"

TITLE = "İÜC.BİDB.LST.008 - İş Ürünleri ve Kalite Kriterleri Listesi (İÜC.BİDB.SRÇ.001)"
PROCESS_CODE = "İÜC.BİDB.SRÇ.001"
PROCESS_NAME = "Dokümantasyon Süreci"
TEMPLATE_NAME = "İÜC.BİDB.LST.008.Ş - İş Ürünleri ve Kalite Kriterleri Listesi Şablonu"

CSS = """
body{margin:0;background:#fff;color:#172b4d;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;line-height:1.55}
.confluence-page{max-width:1100px;margin:0 auto;padding:32px 24px 56px}
h1,h2,h3,h4,h5,h6{margin:1.4em 0 .55em;line-height:1.25;color:#0f172a}
h1{margin-top:0;padding-bottom:12px;border-bottom:1px solid #d8dee4}
p{margin:0 0 12px}
table{width:100%;border-collapse:collapse;margin:16px 0;table-layout:auto}
th,td{border:1px solid #c9d1d9;padding:8px 10px;vertical-align:top}
th{background:#f6f8fa;font-weight:600;text-align:left}
""".strip()


def e(value: object) -> str:
    return html.escape(str(value), quote=False)


def text_from_html(value: str) -> str:
    value = re.sub(r"<[^>]+>", "", value, flags=re.S)
    return re.sub(r"\s+", " ", html.unescape(value)).strip()


def table(headers: list[str], rows: list[list[str]]) -> str:
    head = "".join(f"<th>{e(h)}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>" for row in rows)
    return f'<table class="wrapped"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>'


def load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def write_yaml(path: Path, data: dict[str, Any]) -> None:
    path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")


def load_sup7_bps() -> list[dict[str, str]]:
    data = load_yaml(STANDARD_PATH)
    processes = data.get("processes") or []
    if isinstance(processes, dict):
        sup7 = processes.get("SUP.7") or processes.get("SUP7") or {}
    else:
        sup7 = next((p for p in processes if str(p.get("spice_code") or "") == "SUP.7"), {})
    bps = sup7.get("base_practices") or []
    result: list[dict[str, str]] = []
    for bp in bps:
        code = str(bp.get("id") or bp.get("code") or "").strip()
        title = str(bp.get("title") or "").strip()
        text = str(bp.get("text") or bp.get("description") or "").strip()
        if code:
            result.append({"code": code, "title": title, "text": text})
    if len(result) < 8:
        raise RuntimeError("SUP.7 base practice listesi standart YAML içinden beklenen şekilde okunamadı.")
    return result


def extract_src001_activity_rows() -> list[dict[str, str]]:
    """Read activity rows from SRÇ.001 section 10 and return dictionaries by column name.

    The LST.008 output matrix must use activity names that exist in the parent
    process document's `10. Süreç Faaliyetleri` list. This parser scans h2
    headings by their rendered text, so Confluence span/style markup does not
    break the lookup.
    """
    body = SRC001_BODY.read_text(encoding="utf-8")

    h2_matches = list(re.finditer(r"<h2[^>]*>(.*?)</h2>", body, flags=re.I | re.S))
    section_start = None
    section_end = None

    for index, match in enumerate(h2_matches):
        heading_text = text_from_html(match.group(1))
        if heading_text.startswith("10.") and "Süreç Faaliyetleri" in heading_text:
            section_start = match.end()
            section_end = h2_matches[index + 1].start() if index + 1 < len(h2_matches) else len(body)
            break

    if section_start is None or section_end is None:
        found = [text_from_html(m.group(1)) for m in h2_matches]
        raise RuntimeError(
            "SRÇ.001 içinden '10. Süreç Faaliyetleri' bölümü okunamadı. "
            f"Bulunan h2 başlıkları: {found}"
        )

    section = body[section_start:section_end]
    table_match = re.search(r"<table[^>]*>(.*?)</table>", section, flags=re.I | re.S)
    if not table_match:
        raise RuntimeError("SRÇ.001 10. Süreç Faaliyetleri bölümünde tablo bulunamadı.")

    table_html = table_match.group(1)
    header_match = re.search(r"<thead[^>]*>.*?<tr[^>]*>(.*?)</tr>.*?</thead>", table_html, flags=re.I | re.S)
    if not header_match:
        raise RuntimeError("SRÇ.001 10. Süreç Faaliyetleri tablosunun başlıkları okunamadı.")

    headers = [
        text_from_html(h)
        for h in re.findall(r"<th[^>]*>(.*?)</th>", header_match.group(1), flags=re.I | re.S)
    ]

    rows: list[dict[str, str]] = []
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", table_html, flags=re.I | re.S):
        if "<th" in tr.lower():
            continue

        cells = [
            text_from_html(td)
            for td in re.findall(r"<td[^>]*>(.*?)</td>", tr, flags=re.I | re.S)
        ]

        if not cells:
            continue

        row = {headers[i]: cells[i] for i in range(min(len(headers), len(cells)))}
        rows.append(row)

    if not rows:
        raise RuntimeError("SRÇ.001 10. Süreç Faaliyetleri tablosundan satır okunamadı.")

    return rows


def activity_by_bp(bp_code: str, fallback: str) -> str:
    rows = extract_src001_activity_rows()
    for row in rows:
        if any(bp_code in value for value in row.values()):
            for key in ("Faaliyet", "Süreç Faaliyeti", "Aktivite"):
                if key in row and row[key]:
                    return row[key]
            for key, value in row.items():
                if "faaliyet" in key.lower() or "aktivite" in key.lower():
                    return value
    return fallback


def activity_by_keyword(keyword: str, fallback: str) -> str:
    keyword_lower = keyword.lower()
    rows = extract_src001_activity_rows()
    for row in rows:
        joined = " ".join(row.values()).lower()
        if keyword_lower in joined:
            for key in ("Faaliyet", "Süreç Faaliyeti", "Aktivite"):
                if key in row and row[key]:
                    return row[key]
            for key, value in row.items():
                if "faaliyet" in key.lower() or "aktivite" in key.lower():
                    return value
    return fallback


def build_storage() -> str:
    parts: list[str] = []
    parts.append("<h2>1. Liste Özeti</h2>")
    parts.append(table(["Alan", "Değer"], [
        ["İlgili Süreç", f"{PROCESS_CODE} - {PROCESS_NAME}"],
        ["Liste Kapsamı", "SRÇ.001 kapsamında kullanılan girdi iş ürünleri, üretilen çıktı iş ürünleri ve bu iş ürünlerine uygulanacak kalite kriterleri"],
        ["Liste Tarihi", "01-09-2025"],
        ["Listeyi Hazırlayan", "Soner DEDEOĞLU - Kalite Danışmanı"],
        ["Listeyi Gözden Geçiren", "Levent BAYEZİT - Proje Yöneticisi"],
        ["Listeyi Onaylayan", "Mustafa Nusret SARISAKAL - BİD Başkanı"],
        ["Genel Not", "Bu liste, Dokümantasyon Süreci için iş ürünlerinin tekil ve izlenebilir şekilde yönetilmesi amacıyla oluşturulmuştur."],
    ]))
    parts.append("<h2>2. Kullanım Değerleri</h2>")
    parts.append(table(["Değer", "Anlamı"], [
        ["Girdi", "Sürecin yürütülmesi için başka süreç, proje, sistem veya kayıttan alınan iş ürünü."],
        ["Çıktı", "Süreç faaliyeti sonucunda üretilen, güncellenen veya yayımlanan iş ürünü."],
        ["Zorunlu", "Süreç kapsamında beklenen ve yokluğu gerekçelendirilmesi gereken iş ürünü."],
        ["Koşullu", "Belirli proje/süreç koşullarında beklenen iş ürünü."],
        ["Opsiyonel", "Süreç olgunluğunu destekleyen ancak her durumda zorunlu olmayan iş ürünü."],
        ["Uygun", "İş ürünü tanımlı kalite kriterlerini karşılıyor."],
        ["Eksik", "İş ürünü var ancak tanımlı kalite kriterlerinden biri veya daha fazlası eksik."],
        ["Yok", "Beklenen iş ürünü henüz oluşturulmamış veya erişilebilir değildir."],
        ["Kapsam Dışı", "İlgili süreç veya proje bağlamında uygulanmıyor."],
    ]))
    parts.append("<h2>3. Girdi İş Ürünleri Matrisi</h2>")
    parts.append(table(["Girdi İş Ürünü", "Kaynak Süreç / Kaynak Doküman", "Kullanım Amacı", "Zorunluluk", "Durum / Not"], [
        ["Yeni doküman veya değişiklik ihtiyacı", "Süreç sahipleri, proje ekibi, kalite güvence, denetim/gözden geçirme sonuçları", "Doküman oluşturma, güncelleme, pasife alma veya arşivleme faaliyetini başlatmak", "Zorunlu", "İhtiyaç kaynağı ve gerekçesi ilgili kayıt veya talep üzerinden izlenebilir olmalıdır."],
        ["Yaşam döngüsü doküman ihtiyacı", "İÜC.BİDB.LST.005 - Yaşam Döngüsü Doküman İhtiyaç Matrisi", "Proje veya süreç aşamasında üretilecek dokümanları belirlemek", "Zorunlu", "Süreç/proje aşaması ile beklenen doküman türü ilişkilendirilmiş olmalıdır."],
        ["Süreç tanımı ve uygulama kuralları", "İÜC.BİDB.SRÇ.001 - Dokümantasyon Süreci", "Doküman yönetim faaliyetlerini şablon ve süreç kurallarına göre yürütmek", "Zorunlu", "Güncel ve aktif süreç dokümanı kullanılmalıdır."],
        ["Doküman şablonları", "02 - Şablonlar", "Dokümanların standart biçimde hazırlanmasını sağlamak", "Zorunlu", "İlgili doküman türü için geçerli aktif şablon kullanılmalıdır."],
        ["Doküman yazım ve tasarım kuralları", "İÜC.BİDB.KLV.001 - Doküman Yazım Kuralları Talimatı; İÜC.BİDB.KLV.003 - Süreç Tasarımı Kontrol Kılavuzu", "Dokümanların biçim, içerik ve kalite beklentilerine uygun hazırlanmasını sağlamak", "Zorunlu", "Kılavuzlar aktif ve erişilebilir olmalıdır."],
        ["Repository ve yayın yapısı", "İÜC.BİDB.LST.011 - Repository Yapısı", "Dokümanın yayımlanacağı, erişileceği ve saklanacağı alanı belirlemek", "Zorunlu", "Repository konumu ve erişim yaklaşımı tanımlı olmalıdır."],
        ["Gözden geçirme geri bildirimleri", "İÜC.BİDB.LST.003 - Doküman Gözden Geçirme Kaydı", "Dokümanın uygunluğunu değerlendirmek ve düzeltmeleri izlemek", "Koşullu", "Gözden geçirme gereken dokümanlarda kayıt oluşturulmalıdır."],
        ["Onay kararı", "Süreç sahibi / yetkili onaylayan", "Dokümanın yürürlüğe alınmasını sağlamak", "Zorunlu", "Onay bilgisi doküman veya ilgili kayıt üzerinden izlenebilir olmalıdır."],
    ]))
    parts.append("<h2>4. Çıktı İş Ürünleri Matrisi</h2>")
    parts.append(table(["Çıktı İş Ürünü", "Üreten Faaliyet", "Kullanım Amacı", "Zorunluluk", "Saklama Yeri / Kayıt", "Durum / Not"], [
        ["İÜC.BİDB.PRS.001 - Yazılım Projeleri Dokümantasyon Prosedürü", activity_by_bp("SUP.7.BP1", "Dokümantasyon stratejisini ve kapsamını uygula"), "Dokümantasyon yönetim stratejisi ve yazılım projeleri için doküman yönetim kurallarını tanımlamak", "Zorunlu", "07 - Prosedürler", "Aktif ve onaylı prosedür olarak yönetilir."],
        ["Doküman şablonları", activity_by_bp("SUP.7.BP2", "Doküman standardı ve şablonu belirle"), "Doküman türlerine göre standart yapı ve kullanım kurallarını sağlamak", "Zorunlu", "02 - Şablonlar", "Aktif şablonlar kullanılmalı, kaldırılan şablonlar arşiv altında tutulmalıdır."],
        ["İÜC.BİDB.LST.008 - İş Ürünleri ve Kalite Kriterleri Listesi (İÜC.BİDB.SRÇ.001)", activity_by_bp("SUP.7.BP3", "Doküman standardı ve şablonu belirle"), "SRÇ.001 iş ürünlerini ve kalite kriterlerini tanımlamak", "Zorunlu", "SRÇ.001 alt sayfası", "Bu doküman SRÇ.001 iş ürünü kontrolünün ana kaydıdır."],
        ["İÜC.BİDB.LST.005 - Yaşam Döngüsü Doküman İhtiyaç Matrisi", activity_by_bp("SUP.7.BP4", "Üretilecek dokümanı tanımla"), "Yaşam döngüsü aşamalarına göre üretilecek dokümanları belirlemek", "Zorunlu", "03 - Kayıtlar ve Listeler", "Doküman ihtiyacının yaşam döngüsü izlenebilirliğini destekler."],
        ["Hazırlanmış veya güncellenmiş doküman", activity_by_bp("SUP.7.BP5", "Dokümanı hazırla veya güncelle"), "Süreç, proje veya destek faaliyeti kapsamında kullanılacak kontrollü dokümanı oluşturmak", "Zorunlu", "İlgili süreç/proje doküman alanı", "İlgili şablon ve yazım kurallarına uygun hazırlanmalıdır."],
        ["İÜC.BİDB.LST.003 - Doküman Gözden Geçirme Kaydı", activity_by_bp("SUP.7.BP6", "Dokümanı gözden geçir ve onaylat"), "Doküman gözden geçirme, uygunluk ve düzeltme kayıtlarını izlemek", "Zorunlu", "03 - Kayıtlar ve Listeler", "Gözden geçirme sonucu, tarih ve sorumlu bilgisi içermelidir."],
        ["İÜC.BİDB.LST.001 - Aktif Dokümanlar Listesi", activity_by_bp("SUP.7.BP7", "Dokümanı yayımla ve erişime aç"), "Onaylı ve aktif doküman envanterini yönetmek", "Zorunlu", "SRÇ.001 alt sayfası", "Aktif dokümanların kod, ad, sürüm, durum ve erişim bilgilerini içermelidir."],
        ["İÜC.BİDB.LST.002 - Doküman Değişiklik Kaydı", activity_by_bp("SUP.7.BP8", "Dokümanı sürdür ve arşivle"), "Doküman değişikliklerini, bakım kayıtlarını ve pasife alma/arşivleme kararlarını izlemek", "Zorunlu", "03 - Kayıtlar ve Listeler", "Değişiklik gerekçesi, tarih, sorumlu ve etkilenen doküman bilgisi içermelidir."],
        ["İÜC.BİDB.LST.012 - Süreç Yaygınlaştırma ve Bilgilendirme Kaydı", activity_by_keyword("yay", "Dokümanı yayımla ve erişime aç"), "Yayımlanan veya güncellenen dokümanlar hakkında ilgili tarafların bilgilendirildiğini izlemek", "Koşullu", "03 - Kayıtlar ve Listeler", "Yaygınlaştırma gereken dokümanlar için hedef kitle ve bilgilendirme tarihi izlenir."],
        ["İÜC.BİDB.FRM.001 - Süreç Gözden Geçirme Formu (İÜC.BİDB.SRÇ.001)", activity_by_keyword("gözden", "Dokümanı gözden geçir ve onaylat"), "SRÇ.001 BP/GP uygunluk durumunu ve tamamlayıcı aksiyonları izlemek", "Zorunlu", "SRÇ.001 alt sayfası", "BP/GP durumları ve aksiyon kayıtları güncel tutulmalıdır."],
    ]))
    parts.append("<h2>5. Kalite Kriterleri Kontrol Matrisi</h2>")
    parts.append(table(["İş Ürünü", "Kalite Kriteri", "Kontrol Sorusu", "Kontrol Yöntemi", "Kontrol Sorumlusu", "Kabul Ölçütü", "Uygunsuzluk / Tamamlayıcı Aksiyon"], [
        ["PRS.001", "Dokümantasyon stratejisi tanımlı olmalı", "Dokümantasyon yönetim yaklaşımı, kapsamı ve sorumlulukları tanımlı mı?", "Doküman gözden geçirme", "Süreç Sahibi / Kalite Danışmanı", "Strateji ve uygulama kuralları açık, onaylı ve erişilebilir olmalıdır.", "Eksikse prosedür revize edilir ve onaya sunulur."],
        ["Şablonlar", "Geçerli şablon kullanılmalı", "Doküman türü için aktif şablon kullanılmış mı?", "Şablon kontrolü", "Doküman Hazırlayan / Gözden Geçiren", "Doküman aktif şablon yapısına uygun olmalıdır.", "Yanlış şablon kullanılmışsa doküman güncel şablona göre düzeltilir."],
        ["LST.005", "Yaşam döngüsü doküman ihtiyacı izlenebilir olmalı", "Doküman ihtiyacı yaşam döngüsü aşaması ile ilişkilendirilmiş mi?", "Liste kontrolü", "Süreç Sahibi", "Aşama, doküman türü ve sorumluluk bilgisi tanımlı olmalıdır.", "Eksik ilişki varsa matris güncellenir."],
        ["Hazırlanmış/güncellenmiş doküman", "Zorunlu alanlar ve içerik tamamlanmış olmalı", "Doküman kodu, adı, durum, sürüm, tarih, sahiplik ve içerik alanları dolu mu?", "Doküman kalite kontrolü", "Gözden Geçiren", "Zorunlu alanlar dolu ve içerik kullanılabilir olmalıdır.", "Eksik alanlar tamamlanır."],
        ["LST.003", "Gözden geçirme kaydı izlenebilir olmalı", "Gözden geçirme sonucu, tarih, sorumlu ve karar bilgisi var mı?", "Kayıt kontrolü", "Kalite Güvence / Süreç Sahibi", "Gözden geçirme kararı ve varsa aksiyonlar kayıt altına alınmış olmalıdır.", "Kayıt eksikse tamamlanır."],
        ["LST.001", "Aktif doküman envanteri güncel olmalı", "Aktif dokümanın kodu, adı, sürümü, durumu ve erişim bilgisi listede var mı?", "Liste kontrolü", "Doküman Sorumlusu", "Aktif dokümanlar tekil ve güncel listelenmelidir.", "Eksik kayıt eklenir veya güncellenir."],
        ["LST.002", "Değişiklik kayıtları izlenebilir olmalı", "Değişikliğin gerekçesi, tarihi, sorumlusu ve etkilenen doküman bilgisi var mı?", "Kayıt kontrolü", "Doküman Sorumlusu", "Değişiklik kayıtları doküman geçmişiyle tutarlı olmalıdır.", "Eksik değişiklik kaydı tamamlanır."],
        ["LST.012", "Yaygınlaştırma kayıtları gerektiğinde tutulmalı", "Yayımlanan/güncellenen doküman için hedef kitle bilgilendirilmiş mi?", "Kayıt kontrolü", "Süreç Sahibi", "Bilgilendirme gereken durumlarda hedef kitle ve tarih kaydı bulunmalıdır.", "Eksikse bilgilendirme ve kayıt tamamlanır."],
        ["FRM.001", "BP/GP uygunluk izlenebilirliği sağlanmalı", "SRÇ.001 BP/GP durumu, kanıt ve aksiyon bilgileri formda izleniyor mu?", "Form kontrolü", "Kalite Danışmanı", "BP/GP satırları güncel kanıt ve durum bilgisi içermelidir.", "Eksikse form güncellenir ve aksiyon kapatma takibi yapılır."],
    ]))
    parts.append("<h2>6. Sürüm Geçmişi</h2>")
    parts.append(table(["Sürüm", "Tarih", "Açıklama", "Hazırlayan/Güncelleyen", "Gözden Geçiren", "Onay"], [
        ["v1.0", "01-09-2025", "Dokümantasyon Süreci iş ürünleri ve kalite kriterleri listesi oluşturuldu.", "Soner DEDEOĞLU - Kalite Danışmanı", "Levent BAYEZİT - Proje Yöneticisi", "Mustafa Nusret SARISAKAL - BİD Başkanı"],
    ]))
    return "".join(parts) + "\n"


def build_view(storage: str) -> str:
    return f"""<!doctype html>
<html lang=\"tr\">
<head><meta charset=\"utf-8\"><title>{e(TITLE)}</title><style>{CSS}</style></head>
<body><main class=\"confluence-page\"><h1>{e(TITLE)}</h1>{storage}</main></body>
</html>
"""


def update_page_yaml() -> None:
    path = PAGE_DIR / "page.yaml"
    meta = load_yaml(path) if path.exists() else {}
    meta.update({
        "title": TITLE,
        "status": "active",
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "template": TEMPLATE_NAME,
        "document_code": "İÜC.BİDB.LST.008",
        "document_type": "Liste",
        "related_process": PROCESS_CODE,
        "storage_file": "body.storage.xhtml",
        "view_file": "body.view.html",
    })
    write_yaml(path, meta)


def main() -> None:
    if not PAGE_DIR.exists():
        raise FileNotFoundError(f"Expected existing LST.008 page directory not found: {PAGE_DIR}")
    storage = build_storage()
    (PAGE_DIR / "body.storage.xhtml").write_text(storage, encoding="utf-8")
    (PAGE_DIR / "body.view.html").write_text(build_view(storage), encoding="utf-8")
    update_page_yaml()
    print("[DONE] SRÇ.001 LST.008 created/replaced in existing page directory.")
    print(f"[PATH] {PAGE_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
