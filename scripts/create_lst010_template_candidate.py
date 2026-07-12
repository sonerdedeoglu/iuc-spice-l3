#!/usr/bin/env python3
"""Create a local draft candidate for İÜC.BİDB.LST.010.Ş template.

The candidate is created as a new local Confluence page under `02 - Şablonlar`.
It does not replace the current published LST.010 template. If approved, the
candidate content can later be copied over the existing template page.
"""
from __future__ import annotations

import html
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
CONFLUENCE_DIR = ROOT / "confluence"
INDEX_PATH = CONFLUENCE_DIR / "index.yaml"
ROOT_PAGE = CONFLUENCE_DIR / "pages/000-root-iuc-bidb-spice-2026-level-3"
PARENT_DIR = ROOT_PAGE / "02-sablonlar"
PARENT_ID = "137265785"
PARENT_TITLE = "02 - Şablonlar"

TITLE = "TASLAK - İÜC.BİDB.LST.010.Ş - Süreç Rol Yetki ve RACI Matrisi Şablonu"
SLUG = "taslak-iuc-bidb-lst-010-s-surec-rol-yetki-ve-raci-matrisi-sablonu"
PAGE_DIR = PARENT_DIR / SLUG
RELATIVE_PATH = f"pages/000-root-iuc-bidb-spice-2026-level-3/02-sablonlar/{SLUG}"

CSS = """
body{margin:0;background:#fff;color:#172b4d;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;line-height:1.55}
.confluence-page{max-width:1100px;margin:0 auto;padding:32px 24px 56px}
h1,h2,h3,h4,h5,h6{margin:1.4em 0 .55em;line-height:1.25;color:#0f172a}
h1{margin-top:0;padding-bottom:12px;border-bottom:1px solid #d8dee4}
p{margin:0 0 12px}
table{width:100%;border-collapse:collapse;margin:16px 0;table-layout:auto}
th,td{border:1px solid #c9d1d9;padding:8px 10px;vertical-align:top}
th{background:#f6f8fa;font-weight:600;text-align:left}
blockquote{margin:16px 0;padding:8px 16px;border-left:4px solid #c9d1d9;color:#57606a;background:#f6f8fa}
""".strip()


def e(value: object) -> str:
    return html.escape(str(value), quote=False)


def p(text: str) -> str:
    return f"<p>{e(text)}</p>"


def table(headers: list[str], rows: list[list[str]]) -> str:
    head = "".join(f"<th>{e(h)}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>" for row in rows)
    return f'<table class="wrapped"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>'


def placeholder(text: str) -> str:
    return f"<em>{e(text)}</em>"


def version_history_rows() -> list[list[str]]:
    return [
        ["v0.1", "27-11-2024", "İlk taslak oluşturuldu.", "Soner DEDEOĞLU - Kalite Danışmanı", "-", "-"],
        ["v1.0", "02-01-2025", "Taslak onaylanıp yürürlüğe girdi", "Soner DEDEOĞLU - Kalite Danışmanı", "Levent BAYEZİT - Proje Yöneticisi", "Mustafa Nusret SARISAKAL - BİD Başkanı"],
    ]


def record_version_history_rows() -> list[list[str]]:
    return [
        ["v0.1", placeholder("GG-AA-YYYY"), placeholder("İlk Taslak"), placeholder("Rol / birim"), placeholder("Rol / birim"), placeholder("Rol / birim")],
        ["v1.0", placeholder("GG-AA-YYYY"), placeholder("Onaylı sürüm"), placeholder("Rol / birim"), placeholder("Rol / birim"), placeholder("Rol / birim")],
    ]


def build_storage() -> str:
    parts: list[str] = []

    parts.append("<h2>0. Liste Hakkında</h2>")
    parts.append("<h3>0.1. Liste Üst Bilgisi</h3>")
    parts.append(table(["Alan", "Değer"], [
        ["Kurum", "İstanbul Üniversitesi - Cerrahpaşa Bilgi İşlem Daire Başkanlığı"],
        ["Doküman Kodu", "İÜC.BİDB.LST.010.Ş"],
        ["Doküman Türü", "Liste Şablonu"],
        ["Kullanım Alanı", "Süreç Rol Yetki ve RACI Matrisi"],
        ["Durum", "Aktif"],
        ["Sürüm", "v1.0"],
        ["Yürürlük Tarihi", "02-01-2025"],
        ["Son Gözden Geçirme Tarihi", "01-02-2026"],
        ["Güncelleme Sıklığı", "Yılda bir kez, süreç değişikliği olduğunda veya rol/yetki/RACI ihtiyacı değiştiğinde"],
    ]))

    parts.append("<h3>0.2. Listenin Kullanım Amacı</h3>")
    parts.append(p("Bu liste, bir sürecin yürütülmesinde rol alan tarafların sorumluluk, yetki, RACI ve yetkinlik bilgilerinin tekil ve izlenebilir biçimde yönetilmesi için kullanılır."))
    parts.append(p("Liste, süreç tanımı dokümanındaki genel rol açıklamalarını tekrar etmez; sürece özel rol, yetki, RACI ve yetkinlik kayıtlarını tek yerde yönetir."))

    parts.append("<h3>0.3. Doküman Adlandırma Kuralı</h3>")
    parts.append(p("Bu şablon kullanılarak oluşturulan dosyalar aşağıdaki formatta adlandırılır:"))
    parts.append("<blockquote>İÜC.BİDB.LST.010 - Süreç Rol Yetki ve RACI Matrisi (İÜC.BİDB.SRÇ.XXX)</blockquote>")
    parts.append(p("Parantez içindeki kod, SPICE süreç kodu değil, kurum içinde kullanılan standart süreç kodudur."))

    parts.append("<h3>0.4. Sürüm Geçmişi</h3>")
    parts.append(table(["Sürüm", "Tarih", "Açıklama", "Hazırlayan / Güncelleyen", "Gözden Geçiren", "Onay"], version_history_rows()))

    parts.append("<h2>1. Liste Özeti</h2>")
    parts.append(table(["Alan", "Değer"], [
        ["İlgili Süreç", placeholder("İÜC.BİDB.SRÇ.XXX - Süreç Adı")],
        ["Liste Kapsamı", placeholder("Rol, yetki, RACI, yetkinlik ve onay kapsamı")],
        ["Liste Tarihi", placeholder("GG-AA-YYYY")],
        ["Listeyi Hazırlayan", placeholder("Rol / kişi")],
        ["Listeyi Gözden Geçiren", placeholder("Rol / kişi")],
        ["Listeyi Onaylayan", placeholder("Rol / kişi")],
        ["Genel Not", placeholder("Liste kapsamına ilişkin kısa açıklama")],
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
    parts.append(table([
        "Rol", "Rolün Süreçteki Amacı", "Asgari Yetkinlik / Bilgi", "Vekil / Alternatif Rol", "Durum / Not"
    ], [
        [placeholder("Rol adı"), placeholder("Süreçteki amacı"), placeholder("Gerekli bilgi, deneyim veya yetkinlik"), placeholder("Vekil rol / kişi"), placeholder("Durum veya açıklama")],
        [placeholder("Rol adı"), placeholder("Süreçteki amacı"), placeholder("Gerekli bilgi, deneyim veya yetkinlik"), placeholder("Vekil rol / kişi"), placeholder("Durum veya açıklama")],
    ]))

    parts.append("<h2>4. Süreç Faaliyetleri RACI Matrisi</h2>")
    parts.append(table([
        "Faaliyet Kodu", "Süreç Faaliyeti", "Responsible", "Accountable", "Consulted", "Informed", "Açıklama / Not"
    ], [
        [placeholder("F1"), placeholder("Süreç faaliyet adı"), placeholder("Rol"), placeholder("Rol"), placeholder("Rol"), placeholder("Rol"), placeholder("Not")],
        [placeholder("F2"), placeholder("Süreç faaliyet adı"), placeholder("Rol"), placeholder("Rol"), placeholder("Rol"), placeholder("Rol"), placeholder("Not")],
    ]))

    parts.append("<h2>5. İş Ürünleri RACI Matrisi</h2>")
    parts.append(table([
        "İş Ürünü", "İlgili Faaliyet", "Responsible", "Accountable", "Consulted", "Informed", "Açıklama / Not"
    ], [
        [placeholder("İş ürünü adı"), placeholder("F1 / F2 / ..."), placeholder("Rol"), placeholder("Rol"), placeholder("Rol"), placeholder("Rol"), placeholder("Not")],
        [placeholder("İş ürünü adı"), placeholder("F1 / F2 / ..."), placeholder("Rol"), placeholder("Rol"), placeholder("Rol"), placeholder("Rol"), placeholder("Not")],
    ]))

    parts.append("<h2>6. Yetki ve Onay Matrisi</h2>")
    parts.append(table([
        "Yetki / Karar Alanı", "Yetkili Rol", "Onay Gerektirir mi?", "Onaylayan Rol", "Kayıt / Kanıt", "Açıklama / Not"
    ], [
        [placeholder("Yetki veya karar alanı"), placeholder("Yetkili rol"), placeholder("Evet / Hayır / Koşullu"), placeholder("Onaylayan rol"), placeholder("Kayıt veya kanıt"), placeholder("Not")],
        [placeholder("Yetki veya karar alanı"), placeholder("Yetkili rol"), placeholder("Evet / Hayır / Koşullu"), placeholder("Onaylayan rol"), placeholder("Kayıt veya kanıt"), placeholder("Not")],
    ]))

    parts.append("<h2>7. Sürüm Geçmişi</h2>")
    parts.append(table(["Sürüm", "Tarih", "Açıklama", "Hazırlayan/Güncelleyen", "Gözden Geçiren", "Onay"], record_version_history_rows()))

    return "".join(parts) + "\n"


def build_view(storage: str) -> str:
    return f"""<!doctype html>
<html lang=\"tr\">
<head>
  <meta charset=\"utf-8\">
  <title>{e(TITLE)}</title>
  <style>{CSS}</style>
</head>
<body>
<main class=\"confluence-page\">
<h1>{e(TITLE)}</h1>
{storage}
</main>
</body>
</html>
"""


def page_yaml() -> dict[str, Any]:
    return {
        "page_id": "",
        "space": "SSSS",
        "title": TITLE,
        "parent_id": PARENT_ID,
        "parent_title": PARENT_TITLE,
        "version": "",
        "url": "",
        "depth": 2,
        "status": "draft",
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "children_count": 0,
        "relative_path": RELATIVE_PATH,
        "slug": SLUG,
        "has_view_html": True,
        "view_file": "body.view.html",
        "storage_file": "body.storage.xhtml",
    }


def update_index() -> None:
    index = yaml.safe_load(INDEX_PATH.read_text(encoding="utf-8")) or {}
    pages = index.setdefault("pages", [])
    existing = next((p for p in pages if p.get("relative_path") == RELATIVE_PATH), None)
    entry = {
        "page_id": "",
        "title": TITLE,
        "parent_id": PARENT_ID,
        "depth": 2,
        "relative_path": RELATIVE_PATH,
        "slug": SLUG,
        "storage_file": f"{RELATIVE_PATH}/body.storage.xhtml",
        "view_file": f"{RELATIVE_PATH}/body.view.html",
    }
    if existing:
        existing.update(entry)
    else:
        insert_at = len(pages)
        for i, p in enumerate(pages):
            if p.get("relative_path") == "pages/000-root-iuc-bidb-spice-2026-level-3/02-sablonlar/iuc-bidb-lst-010-s-surec-rol-yetki-ve-raci-matrisi-sablonu":
                insert_at = i + 1
                break
        pages.insert(insert_at, entry)
        index["total_page_count"] = int(index.get("total_page_count", len(pages) - 1)) + 1
    INDEX_PATH.write_text(yaml.safe_dump(index, allow_unicode=True, sort_keys=False), encoding="utf-8")


def main() -> None:
    PAGE_DIR.mkdir(parents=True, exist_ok=True)
    storage = build_storage()
    (PAGE_DIR / "body.storage.xhtml").write_text(storage, encoding="utf-8")
    (PAGE_DIR / "body.view.html").write_text(build_view(storage), encoding="utf-8")
    (PAGE_DIR / "page.yaml").write_text(yaml.safe_dump(page_yaml(), allow_unicode=True, sort_keys=False), encoding="utf-8")
    update_index()
    print(f"[DONE] Created local draft page: {TITLE}")
    print(f"[PATH] {PAGE_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
