#!/usr/bin/env python3
"""Create/replace LST.010 for SRÇ.001.

This script updates the existing SRÇ.001 child page:
LST.010 - Süreç Rol Yetki ve RACI Matrisi (SRÇ.001)

It follows the active LST.010 template structure and uses SRÇ.001 section
`10. Süreç Faaliyetleri` as the source for activity codes/names.
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
SRC001_BODY = ROOT_PAGE / "01-surec-dokumanlari/src-001-dokumantasyon-sureci/body.storage.xhtml"
PAGE_DIR = ROOT_PAGE / "01-surec-dokumanlari/src-001-dokumantasyon-sureci/lst-010-surec-rol-yetki-ve-raci-matrisi-src-001"

TITLE = "LST.010 - Süreç Rol Yetki ve RACI Matrisi (SRÇ.001)"
PROCESS_CODE = "SRÇ.001"
PROCESS_NAME = "Dokümantasyon Süreci"
TEMPLATE_NAME = "LST.010.Ş - Süreç Rol Yetki ve RACI Matrisi Şablonu"

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


def extract_src001_activity_rows() -> list[dict[str, str]]:
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
        raise RuntimeError("SRÇ.001 içinden '10. Süreç Faaliyetleri' bölümü okunamadı. " f"Bulunan h2 başlıkları: {found}")

    section = body[section_start:section_end]
    table_match = re.search(r"<table[^>]*>(.*?)</table>", section, flags=re.I | re.S)
    if not table_match:
        raise RuntimeError("SRÇ.001 10. Süreç Faaliyetleri bölümünde tablo bulunamadı.")
    table_html = table_match.group(1)
    header_match = re.search(r"<thead[^>]*>.*?<tr[^>]*>(.*?)</tr>.*?</thead>", table_html, flags=re.I | re.S)
    if not header_match:
        raise RuntimeError("SRÇ.001 10. Süreç Faaliyetleri tablosunun başlıkları okunamadı.")
    headers = [text_from_html(h) for h in re.findall(r"<th[^>]*>(.*?)</th>", header_match.group(1), flags=re.I | re.S)]

    rows: list[dict[str, str]] = []
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", table_html, flags=re.I | re.S):
        if "<th" in tr.lower():
            continue
        cells = [text_from_html(td) for td in re.findall(r"<td[^>]*>(.*?)</td>", tr, flags=re.I | re.S)]
        if not cells:
            continue
        rows.append({headers[i]: cells[i] for i in range(min(len(headers), len(cells)))})
    if not rows:
        raise RuntimeError("SRÇ.001 10. Süreç Faaliyetleri tablosundan satır okunamadı.")
    return rows


def activity_code(row: dict[str, str], fallback_index: int) -> str:
    for value in row.values():
        match = re.search(r"\bF\s*([0-9]+)\b", value, flags=re.I)
        if match:
            return f"F{int(match.group(1))}"
    return f"F{fallback_index}"


def activity_name(row: dict[str, str]) -> str:
    preferred_keys = ["Süreç Faaliyeti", "Faaliyet", "Faaliyet Adı", "Aktivite"]
    for key in preferred_keys:
        if row.get(key):
            return row[key]
    for key, value in row.items():
        if "faaliyet" in key.lower() or "aktivite" in key.lower():
            return value
    values = [v for v in row.values() if v]
    return values[1] if len(values) > 1 else (values[0] if values else "")


def activities() -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    for index, row in enumerate(extract_src001_activity_rows(), start=1):
        code = activity_code(row, index)
        if not re.fullmatch(r"F[0-9]+", code):
            continue
        result.append({"code": code, "name": activity_name(row)})
    if len(result) < 1:
        raise RuntimeError(f"SRÇ.001 faaliyet kodları okunamadı; okunan faaliyetler: {result}")
    return sorted(result, key=lambda item: int(item["code"][1:]))


def role_rows() -> list[list[str]]:
    return [
        ["Süreç Sahibi", "Dokümantasyon Süreci'nin kurum içinde uygulanmasını ve sürdürülmesini sahiplenmek", "Süreç yönetimi, dokümantasyon kuralları ve kurumsal yayın yapısı bilgisi", "Proje Yöneticisi", "SRÇ.001'in nihai süreç sorumluluğunu taşır."],
        ["Doküman Hazırlayan", "Yeni dokümanları ve doküman güncellemelerini tanımlı şablonlara göre hazırlamak", "İlgili süreç/proje bilgisi, doküman yazım kuralları ve şablon kullanımı bilgisi", "İlgili süreç temsilcisi", "Doküman içeriğini hazırlar veya günceller."],
        ["Doküman Gözden Geçiren", "Dokümanların içerik, biçim, izlenebilirlik ve kalite kriterlerine uygunluğunu değerlendirmek", "Doküman gözden geçirme, kalite kriteri kontrolü ve süreç bilgisi", "Kalite Danışmanı", "Gözden geçirme kayıtlarını oluşturur veya doğrular."],
        ["Onaylayan", "Yürürlüğe alınacak dokümanlar için nihai onayı vermek", "Yetki sınırları, süreç sahipliği ve kurumsal karar mekanizması bilgisi", "Yetkilendirilmiş vekil", "Onay kararının izlenebilir olmasını sağlar."],
        ["Doküman Sorumlusu", "Aktif doküman listesi, değişiklik kayıtları ve arşiv kayıtlarını güncel tutmak", "Confluence/repository kullanımı, doküman kodlama ve kayıt yönetimi bilgisi", "Süreç Sahibi", "Doküman envanteri ve değişiklik kayıtlarından sorumludur."],
        ["Kalite Danışmanı", "Süreç dokümantasyon yapısını SPICE hazırlık hedefleri ve kalite yaklaşımı ile uyumlu hale getirmek", "SPICE süreç modeli, süreç dokümantasyonu, kalite güvence ve denetim hazırlığı bilgisi", "Kalite Güvence Temsilcisi", "Şablon, kontrol ve uygunluk yaklaşımını destekler."],
        ["İlgili Paydaş", "Doküman içeriği, yaygınlaştırma veya uygulama açısından görüş vermek ve bilgilendirilmek", "Kendi görev alanına ilişkin süreç/proje bilgisi", "İlgili birim temsilcisi", "İhtiyaç halinde danışılan veya bilgilendirilen roldür."],
    ]


def activity_raci_rows() -> list[list[str]]:
    mapping = {
        "F1": ["Kalite Danışmanı / Süreç Sahibi", "Süreç Sahibi", "Doküman Sorumlusu / İlgili Paydaş", "Onaylayan"],
        "F2": ["Kalite Danışmanı / Doküman Sorumlusu", "Süreç Sahibi", "Doküman Hazırlayan / Doküman Gözden Geçiren", "İlgili Paydaş"],
        "F3": ["Doküman Hazırlayan / Kalite Danışmanı", "Süreç Sahibi", "Doküman Gözden Geçiren", "Doküman Sorumlusu"],
        "F4": ["Süreç Sahibi / Doküman Sorumlusu", "Süreç Sahibi", "Kalite Danışmanı / İlgili Paydaş", "Onaylayan"],
        "F5": ["Doküman Hazırlayan", "Süreç Sahibi", "Kalite Danışmanı / İlgili Paydaş", "Doküman Sorumlusu"],
        "F6": ["Doküman Gözden Geçiren", "Süreç Sahibi", "Kalite Danışmanı / Onaylayan", "Doküman Hazırlayan"],
        "F7": ["Doküman Sorumlusu", "Süreç Sahibi", "Kalite Danışmanı", "İlgili Paydaş"],
        "F8": ["Doküman Sorumlusu", "Süreç Sahibi", "Kalite Danışmanı / Doküman Gözden Geçiren", "İlgili Paydaş"],
    }
    rows: list[list[str]] = []
    for activity in activities():
        r, a, c, i = mapping.get(activity["code"], ["Süreç Sahibi", "Süreç Sahibi", "Kalite Danışmanı", "İlgili Paydaş"])
        rows.append([activity["code"], activity["name"], r, a, c, i, "RACI ataması SRÇ.001 faaliyet kodu ile izlenir."])
    return rows


def work_product_raci_rows() -> list[list[str]]:
    return [
        ["PRS.001 - Yazılım Projeleri Dokümantasyon Prosedürü", "F1", "Kalite Danışmanı / Süreç Sahibi", "Süreç Sahibi", "Doküman Sorumlusu / İlgili Paydaş", "Onaylayan", "Dokümantasyon yönetim stratejisini destekleyen prosedürdür."],
        ["Doküman şablonları", "F2", "Kalite Danışmanı / Doküman Sorumlusu", "Süreç Sahibi", "Doküman Hazırlayan / Doküman Gözden Geçiren", "İlgili Paydaş", "Aktif şablonlar ve kaldırılan şablonlar kontrollü yönetilir."],
        ["KLV.001 - Doküman Yazım Kuralları Talimatı", "F2", "Kalite Danışmanı / Doküman Sorumlusu", "Süreç Sahibi", "Doküman Gözden Geçiren", "Doküman Hazırlayan", "Doküman yazım ve biçim kurallarını tanımlar."],
        ["LST.008 - İş Ürünleri ve Kalite Kriterleri Listesi (SRÇ.001)", "F3", "Kalite Danışmanı", "Süreç Sahibi", "Doküman Gözden Geçiren", "Doküman Sorumlusu", "İş ürünleri ve kalite kriterleri için ana izleme kaydıdır."],
        ["LST.005 - Yaşam Döngüsü Doküman İhtiyaç Matrisi", "F3", "Doküman Sorumlusu / Süreç Sahibi", "Süreç Sahibi", "Kalite Danışmanı / İlgili Paydaş", "Onaylayan", "Yaşam döngüsü aşamalarındaki doküman ihtiyacını tanımlar."],
        ["Hazırlanmış veya güncellenmiş doküman", "F4", "Doküman Hazırlayan", "Süreç Sahibi", "Kalite Danışmanı / İlgili Paydaş", "Doküman Sorumlusu", "İlgili şablon ve kurallara göre hazırlanır."],
        ["LST.003 - Doküman Gözden Geçirme Kaydı", "F5", "Doküman Gözden Geçiren", "Süreç Sahibi", "Kalite Danışmanı / Onaylayan", "Doküman Hazırlayan", "Gözden geçirme sonucu ve aksiyonları izler."],
        ["LST.001 - Aktif Dokümanlar Listesi", "F6", "Doküman Sorumlusu", "Süreç Sahibi", "Kalite Danışmanı", "İlgili Paydaş", "Aktif doküman envanterini izler."],
        ["LST.002 - Doküman Değişiklik Kaydı", "F7", "Doküman Sorumlusu", "Süreç Sahibi", "Kalite Danışmanı / Doküman Gözden Geçiren", "İlgili Paydaş", "Değişiklik, bakım ve arşiv kayıtlarını izler."],
        ["LST.012 - Süreç Yaygınlaştırma ve Bilgilendirme Kaydı", "F6", "Doküman Sorumlusu", "Süreç Sahibi", "Kalite Danışmanı", "İlgili Paydaş", "Yaygınlaştırma ve bilgilendirme kayıtlarını izler."],
        ["FRM.001 - Süreç Gözden Geçirme Formu (SRÇ.001)", "F5", "Kalite Danışmanı", "Süreç Sahibi", "Doküman Gözden Geçiren", "Onaylayan", "SRÇ.001 BP/GP uygunluk ve aksiyon takibini destekler."],
    ]


def authority_rows() -> list[list[str]]:
    return [
        ["Dokümantasyon stratejisi ve prosedür yaklaşımı", "Süreç Sahibi", "Evet", "Onaylayan", "PRS.001 / Sürüm geçmişi / onay bilgisi", "Strateji ve prosedür değişiklikleri onaya tabidir."],
        ["Şablon oluşturma veya şablon güncelleme", "Doküman Sorumlusu / Kalite Danışmanı", "Evet", "Süreç Sahibi", "Şablon sayfası / sürüm geçmişi", "Aktif şablon değişiklikleri izlenebilir olmalıdır."],
        ["Doküman hazırlama veya güncelleme", "Doküman Hazırlayan", "Koşullu", "Süreç Sahibi", "Hazırlanan/güncellenen doküman", "Yeni yayın veya kritik güncelleme onay gerektirir."],
        ["Doküman gözden geçirme", "Doküman Gözden Geçiren", "Hayır", "-", "LST.003 - Doküman Gözden Geçirme Kaydı", "Gözden geçirme sonucu kayıt altına alınır."],
        ["Doküman yayımlama ve erişime açma", "Doküman Sorumlusu", "Evet", "Süreç Sahibi", "LST.001 / Confluence yayın kaydı", "Yalnız onaylı dokümanlar aktif alanda yayımlanır."],
        ["Doküman pasife alma veya arşivleme", "Doküman Sorumlusu", "Evet", "Süreç Sahibi", "LST.002 / arşiv sayfası", "Pasife alma gerekçesi izlenebilir olmalıdır."],
    ]


def build_storage() -> str:
    # Keep regenerated records on the SRÇ.006 reference structure.
    from align_lst010_to_src006_structure import process_body, src001
    return process_body(src001())

    parts: list[str] = []
    parts.append("<h2>1. Liste Özeti</h2>")
    parts.append(table(["Alan", "Değer"], [
        ["İlgili Süreç", f"{PROCESS_CODE} - {PROCESS_NAME}"],
        ["Liste Kapsamı", "SRÇ.001 kapsamında rol, yetki, RACI, yetkinlik ve onay bilgilerinin yönetimi"],
        ["Liste Tarihi", "15-02-2025"],
        ["Listeyi Hazırlayan", "Soner DEDEOĞLU - Kalite Danışmanı"],
        ["Listeyi Gözden Geçiren", "Levent BAYEZİT - Proje Yöneticisi"],
        ["Listeyi Onaylayan", "Mustafa Nusret SARISAKAL - BİD Başkanı"],
        ["Genel Not", "Bu liste, SRÇ.001 faaliyetleri ve iş ürünleri için rol/yetki/RACI izlenebilirliğini sağlar."],
    ]))
    parts.append("<h2>2. Kullanım Değerleri</h2>")
    parts.append(table(["Değer", "Anlamı"], [
        ["R", "Responsible / Sorumlu: Faaliyeti veya iş ürününü fiilen gerçekleştiren rol."],
        ["A", "Accountable / Hesap Veren-Onaylayan: Sonuçtan nihai olarak sorumlu olan ve karar/onay veren rol."],
        ["C", "Consulted / Danışılan: Faaliyet veya iş ürünü için görüşü alınan rol."],
        ["I", "Informed / Bilgilendirilen: Faaliyet veya sonuç hakkında bilgilendirilen rol."],
        ["Yetkili", "İlgili karar, onay, yayın, değişiklik veya erişim işlemini yapma yetkisi bulunan rol."],
        ["Destek", "Faaliyetin yürütülmesine katkı sağlayan ancak ana sorumlu olmayan rol."],
        ["Kapsam Dışı", "İlgili rolün süreç faaliyeti veya iş ürünü bağlamında görevi yoktur."],
    ]))
    parts.append("<h2>3. Rol ve Yetkinlik Matrisi</h2>")
    parts.append(table(["Rol", "Rolün Süreçteki Amacı", "Asgari Yetkinlik / Bilgi", "Vekil / Alternatif Rol", "Durum / Not"], role_rows()))
    parts.append("<h2>4. Süreç Faaliyetleri RACI Matrisi</h2>")
    parts.append(table(["Faaliyet Kodu", "Süreç Faaliyeti", "Responsible", "Accountable", "Consulted", "Informed", "Açıklama / Not"], activity_raci_rows()))
    parts.append("<h2>5. İş Ürünleri RACI Matrisi</h2>")
    parts.append(table(["İş Ürünü", "İlgili Faaliyet", "Responsible", "Accountable", "Consulted", "Informed", "Açıklama / Not"], work_product_raci_rows()))
    parts.append("<h2>6. Yetki ve Onay Matrisi</h2>")
    parts.append(table(["Yetki / Karar Alanı", "Yetkili Rol", "Onay Gerektirir mi?", "Onaylayan Rol", "Kayıt / Kanıt", "Açıklama / Not"], authority_rows()))
    parts.append("<h2>7. Sürüm Geçmişi</h2>")
    parts.append(table(["Sürüm", "Tarih", "Açıklama", "Hazırlayan/Güncelleyen", "Gözden Geçiren", "Onay"], [
        ["v1.0", "15-02-2025", "Dokümantasyon Süreci rol, yetki ve RACI matrisi oluşturuldu.", "Soner DEDEOĞLU - Kalite Danışmanı", "Levent BAYEZİT - Proje Yöneticisi", "Mustafa Nusret SARISAKAL - BİD Başkanı"],
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
        "document_code": "LST.010",
        "document_type": "Liste",
        "related_process": PROCESS_CODE,
        "storage_file": "body.storage.xhtml",
        "view_file": "body.view.html",
    })
    write_yaml(path, meta)


def main() -> None:
    if not PAGE_DIR.exists():
        raise FileNotFoundError(f"Expected existing LST.010 page directory not found: {PAGE_DIR}")
    storage = build_storage()
    (PAGE_DIR / "body.storage.xhtml").write_text(storage, encoding="utf-8")
    (PAGE_DIR / "body.view.html").write_text(build_view(storage), encoding="utf-8")
    update_page_yaml()
    print("[DONE] SRÇ.001 LST.010 created/replaced in existing page directory.")
    print(f"[PATH] {PAGE_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
