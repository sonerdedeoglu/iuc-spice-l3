#!/usr/bin/env python3
"""Create local draft candidates for PRS.XXX.Ş and KLV.XXX.Ş templates.

The candidates are created as new local Confluence pages under `02 - Şablonlar`.
They do not replace the current published templates. If approved, they can later
be promoted and the existing active templates can be archived.
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

TEMPLATES = [
    {
        "kind": "PRS",
        "title": "TASLAK - İÜC.BİDB.PRS.XXX.Ş - Prosedür Tanımı Şablonu",
        "active_title": "İÜC.BİDB.PRS.XXX.Ş - Prosedür Tanımı Şablonu",
        "slug": "taslak-iuc-bidb-prs-xxx-s-prosedur-tanimi-sablonu",
        "document_code": "İÜC.BİDB.PRS.XXX.Ş",
        "usage": "Prosedür Tanımı",
        "name_example": "İÜC.BİDB.PRS.XXX - Prosedür Adı",
        "purpose": "Bu şablon, kurum genelinde uygulanacak prosedürlerin amaç, kapsam, referans, rol, sorumluluk, uygulama adımı, kayıt ve gözden geçirme bilgilerinin standart yapıda tanımlanması için kullanılır.",
        "note": "Prosedür dokümanları, bir süreç veya yönetim alanında uyulması gereken kuralları ve uygulama esaslarını tanımlar; günlük operasyon kaydı yerine normatif doküman olarak yönetilir.",
        "section_6": "Genel Esaslar",
        "section_6_desc": "Prosedürün uygulanmasında geçerli olan temel prensipler, zorunlu kurallar, politika bağlantıları ve genel yaklaşım bu bölümde tanımlanır.",
        "section_8": "Prosedür Adımları",
        "section_8_headers": ["Adım", "Uygulama Adımı", "Açıklama", "Sorumlu Rol", "Kayıt / Kanıt"],
        "section_8_rows": [
            ["1", "<em>Prosedür adımı</em>", "<em>Adımın nasıl uygulanacağı</em>", "<em>Rol / birim</em>", "<em>Kayıt veya kanıt</em>"],
            ["2", "<em>Prosedür adımı</em>", "<em>Adımın nasıl uygulanacağı</em>", "<em>Rol / birim</em>", "<em>Kayıt veya kanıt</em>"],
        ],
    },
    {
        "kind": "KLV",
        "title": "TASLAK - İÜC.BİDB.KLV.XXX.Ş - Kılavuz ve Talimat Tanımı Şablonu",
        "active_title": "İÜC.BİDB.KLV.XXX.Ş - Kılavuz ve Talimat Tanımı Şablonu",
        "slug": "taslak-iuc-bidb-klv-xxx-s-kilavuz-ve-talimat-tanimi-sablonu",
        "document_code": "İÜC.BİDB.KLV.XXX.Ş",
        "usage": "Kılavuz ve Talimat Tanımı",
        "name_example": "İÜC.BİDB.KLV.XXX - Kılavuz / Talimat Adı",
        "purpose": "Bu şablon, kurum genelinde kullanılacak kılavuz ve talimatların amaç, kapsam, uygulama kuralları, adımlar, örnekler, kayıtlar ve gözden geçirme bilgilerinin standart yapıda tanımlanması için kullanılır.",
        "note": "Kılavuz ve talimat dokümanları, prosedürlerde belirlenen kuralların nasıl uygulanacağını açıklayan destekleyici dokümanlardır.",
        "section_6": "Kullanım Esasları",
        "section_6_desc": "Kılavuz veya talimatın hangi koşullarda, kimler tarafından ve hangi sınırlar içinde kullanılacağı bu bölümde tanımlanır.",
        "section_8": "Talimat / Uygulama Adımları",
        "section_8_headers": ["Adım", "Talimat / Uygulama Adımı", "Açıklama", "Kullanıcı / Sorumlu Rol", "Kayıt / Kanıt"],
        "section_8_rows": [
            ["1", "<em>Uygulama adımı</em>", "<em>Adımın nasıl uygulanacağı</em>", "<em>Rol / kullanıcı</em>", "<em>Kayıt veya kanıt</em>"],
            ["2", "<em>Uygulama adımı</em>", "<em>Adımın nasıl uygulanacağı</em>", "<em>Rol / kullanıcı</em>", "<em>Kayıt veya kanıt</em>"],
        ],
    },
]


def e(value: object) -> str:
    return html.escape(str(value), quote=False)


def p(text: str) -> str:
    return f"<p>{e(text)}</p>"


def placeholder(text: str) -> str:
    return f"<em>{e(text)}</em>"


def table(headers: list[str], rows: list[list[str]]) -> str:
    head = "".join(f"<th>{e(h)}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>" for row in rows)
    return f'<table class="wrapped"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>'


def template_version_history_rows() -> list[list[str]]:
    return [
        ["v0.1", "27-11-2024", "İlk taslak oluşturuldu.", "Soner DEDEOĞLU - Kalite Danışmanı", "-", "-"],
        ["v1.0", "02-01-2025", "Taslak onaylanıp yürürlüğe girdi", "Soner DEDEOĞLU - Kalite Danışmanı", "Levent BAYEZİT - Proje Yöneticisi", "Mustafa Nusret SARISAKAL - BİD Başkanı"],
    ]


def record_version_history_rows() -> list[list[str]]:
    return [
        ["v0.1", placeholder("GG-AA-YYYY"), placeholder("İlk Taslak"), placeholder("Rol / birim"), placeholder("Rol / birim"), placeholder("Rol / birim")],
        ["v1.0", placeholder("GG-AA-YYYY"), placeholder("Onaylı sürüm"), placeholder("Rol / birim"), placeholder("Rol / birim"), placeholder("Rol / birim")],
    ]


def build_storage(cfg: dict[str, Any]) -> str:
    parts: list[str] = []

    parts.append("<h2>0. Şablon Hakkında</h2>")
    parts.append("<h3>0.1. Doküman Üst Bilgisi</h3>")
    parts.append(table(["Alan", "Değer"], [
        ["Kurum", "İstanbul Üniversitesi - Cerrahpaşa Bilgi İşlem Daire Başkanlığı"],
        ["Doküman Kodu", cfg["document_code"]],
        ["Doküman Türü", "Doküman Şablonu"],
        ["Kullanım Alanı", cfg["usage"]],
        ["Durum", "Aktif"],
        ["Sürüm", "v1.0"],
        ["Yürürlük Tarihi", "02-01-2025"],
        ["Son Gözden Geçirme Tarihi", "01-02-2026"],
        ["Güncelleme Sıklığı", "Yılda bir kez, doküman yapısı değiştiğinde veya süreç ihtiyacı oluştuğunda"],
    ]))

    parts.append("<h3>0.2. Şablonun Kullanım Amacı</h3>")
    parts.append(p(cfg["purpose"]))
    parts.append(p(cfg["note"]))

    parts.append("<h3>0.3. Doküman Adlandırma Kuralı</h3>")
    parts.append(p("Bu şablon kullanılarak oluşturulan dokümanlar aşağıdaki formatta adlandırılır:"))
    parts.append(f"<blockquote>{e(cfg['name_example'])}</blockquote>")
    parts.append(p("XXX bölümü kurum doküman kodlama yapısına göre belirlenir. Doküman adı, içeriğin amacını açık ve kısa şekilde ifade eder."))

    parts.append("<h3>0.4. Sürüm Geçmişi</h3>")
    parts.append(table(["Sürüm", "Tarih", "Açıklama", "Hazırlayan / Güncelleyen", "Gözden Geçiren", "Onay"], template_version_history_rows()))

    parts.append("<h2>1. Doküman Bilgileri</h2>")
    parts.append(table(["Alan", "Değer"], [
        ["Doküman Kodu", placeholder("İÜC.BİDB." + cfg["kind"] + ".XXX")],
        ["Doküman Adı", placeholder("Doküman adı")],
        ["Doküman Türü", cfg["usage"].replace(" Tanımı", "")],
        ["İlgili Süreç / Kapsam", placeholder("İlgili süreç, yönetim alanı veya kullanım kapsamı")],
        ["Yürürlük Tarihi", placeholder("GG-AA-YYYY")],
        ["Son Gözden Geçirme Tarihi", placeholder("GG-AA-YYYY")],
        ["Hazırlayan", placeholder("Rol / kişi")],
        ["Gözden Geçiren", placeholder("Rol / kişi")],
        ["Onaylayan", placeholder("Rol / kişi")],
        ["Durum", placeholder("Taslak / Aktif / Pasif / Arşiv")],
    ]))

    parts.append("<h2>2. Amaç</h2>")
    parts.append(p("Bu bölümde dokümanın hangi ihtiyacı karşılamak için hazırlandığı, hangi sonucu sağlamayı hedeflediği ve kurum içinde hangi amaçla kullanılacağı açıklanır."))

    parts.append("<h2>3. Kapsam</h2>")
    parts.append(p("Bu bölümde dokümanın uygulanacağı birimler, süreçler, sistemler, projeler, kullanıcı grupları ve kapsam dışı durumlar tanımlanır."))

    parts.append("<h2>4. Referanslar</h2>")
    parts.append(table(["Referans", "Açıklama"], [
        [placeholder("İlgili süreç / prosedür / kılavuz / standart"), placeholder("Referansın bu dokümanla ilişkisi")],
        [placeholder("İlgili kayıt / liste / sistem"), placeholder("Referansın bu dokümanla ilişkisi")],
    ]))

    parts.append("<h2>5. Terimler ve Kısaltmalar</h2>")
    parts.append(table(["Terim / Kısaltma", "Açıklama"], [
        [placeholder("Terim"), placeholder("Açıklama")],
        [placeholder("Kısaltma"), placeholder("Açıklama")],
    ]))

    parts.append(f"<h2>6. {e(cfg['section_6'])}</h2>")
    parts.append(p(cfg["section_6_desc"]))
    parts.append(table(["Kural / Esas", "Açıklama", "Zorunluluk", "Not"], [
        [placeholder("Kural veya esas"), placeholder("Açıklama"), placeholder("Zorunlu / Koşullu / Opsiyonel"), placeholder("Not")],
        [placeholder("Kural veya esas"), placeholder("Açıklama"), placeholder("Zorunlu / Koşullu / Opsiyonel"), placeholder("Not")],
    ]))

    parts.append("<h2>7. Roller ve Sorumluluklar</h2>")
    parts.append(table(["Rol", "Sorumluluk", "Yetki", "İlgili Kayıt / Kanıt"], [
        [placeholder("Rol adı"), placeholder("Sorumluluk açıklaması"), placeholder("Yetki açıklaması"), placeholder("Kayıt / kanıt")],
        [placeholder("Rol adı"), placeholder("Sorumluluk açıklaması"), placeholder("Yetki açıklaması"), placeholder("Kayıt / kanıt")],
    ]))

    parts.append(f"<h2>8. {e(cfg['section_8'])}</h2>")
    parts.append(table(cfg["section_8_headers"], cfg["section_8_rows"]))

    parts.append("<h2>9. Kayıtlar ve Kanıtlar</h2>")
    parts.append(table(["Kayıt / Kanıt", "Kullanım Amacı", "Saklama Yeri", "Sorumlu", "Not"], [
        [placeholder("Kayıt / kanıt adı"), placeholder("Ne için kullanılır?"), placeholder("Confluence / Drive / Jira / sistem"), placeholder("Rol"), placeholder("Not")],
        [placeholder("Kayıt / kanıt adı"), placeholder("Ne için kullanılır?"), placeholder("Confluence / Drive / Jira / sistem"), placeholder("Rol"), placeholder("Not")],
    ]))

    parts.append("<h2>10. Kontrol ve Gözden Geçirme</h2>")
    parts.append(table(["Kontrol Alanı", "Kontrol Yöntemi", "Sıklık", "Sorumlu", "Kayıt / Kanıt"], [
        [placeholder("Kontrol alanı"), placeholder("Gözden geçirme / doğrulama / onay kontrolü"), placeholder("Periyot"), placeholder("Rol"), placeholder("Kayıt / kanıt")],
        [placeholder("Kontrol alanı"), placeholder("Gözden geçirme / doğrulama / onay kontrolü"), placeholder("Periyot"), placeholder("Rol"), placeholder("Kayıt / kanıt")],
    ]))

    parts.append("<h2>11. Uygulama ve Uyarlama Kuralları</h2>")
    parts.append("<h3>11.1. Zorunlu Adımlar</h3>")
    parts.append(p("Bu bölümde dokümanın uygulanmasında her durumda yerine getirilmesi gereken zorunlu adımlar tanımlanır."))
    parts.append("<h3>11.2. Uyarlanabilir Adımlar</h3>")
    parts.append(p("Bu bölümde proje, süreç, kapsam veya kurum ihtiyacına göre uyarlanabilecek adımlar tanımlanır."))
    parts.append("<h3>11.3. Onay Gerektiren Durumlar</h3>")
    parts.append(p("Bu bölümde dokümanın uygulanması veya uyarlanması sırasında ek onay gerektiren durumlar tanımlanır."))

    parts.append("<h2>12. Sürüm Geçmişi</h2>")
    parts.append(table(["Sürüm", "Tarih", "Açıklama", "Hazırlayan/Güncelleyen", "Gözden Geçiren", "Onay"], record_version_history_rows()))

    return "".join(parts) + "\n"


def build_view(title: str, storage: str) -> str:
    return f"""<!doctype html>
<html lang=\"tr\">
<head>
  <meta charset=\"utf-8\">
  <title>{e(title)}</title>
  <style>{CSS}</style>
</head>
<body>
<main class=\"confluence-page\">
<h1>{e(title)}</h1>
{storage}
</main>
</body>
</html>
"""


def page_yaml(cfg: dict[str, Any], rel: str) -> dict[str, Any]:
    return {
        "page_id": "",
        "space": "SSSS",
        "title": cfg["title"],
        "parent_id": PARENT_ID,
        "parent_title": PARENT_TITLE,
        "version": "",
        "url": "",
        "depth": 2,
        "status": "draft",
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "children_count": 0,
        "relative_path": rel,
        "slug": cfg["slug"],
        "has_view_html": True,
        "view_file": "body.view.html",
        "storage_file": "body.storage.xhtml",
    }


def update_index(entries: list[dict[str, Any]]) -> None:
    index = yaml.safe_load(INDEX_PATH.read_text(encoding="utf-8")) or {}
    pages = index.setdefault("pages", [])
    for entry in entries:
        existing = next((p for p in pages if p.get("relative_path") == entry["relative_path"]), None)
        if existing:
            existing.update(entry)
        else:
            pages.append(entry)
            index["total_page_count"] = int(index.get("total_page_count", len(pages) - 1)) + 1
    INDEX_PATH.write_text(yaml.safe_dump(index, allow_unicode=True, sort_keys=False), encoding="utf-8")


def main() -> None:
    index_entries: list[dict[str, Any]] = []
    for cfg in TEMPLATES:
        page_dir = PARENT_DIR / cfg["slug"]
        rel = f"pages/000-root-iuc-bidb-spice-2026-level-3/02-sablonlar/{cfg['slug']}"
        page_dir.mkdir(parents=True, exist_ok=True)
        storage = build_storage(cfg)
        (page_dir / "body.storage.xhtml").write_text(storage, encoding="utf-8")
        (page_dir / "body.view.html").write_text(build_view(cfg["title"], storage), encoding="utf-8")
        (page_dir / "page.yaml").write_text(yaml.safe_dump(page_yaml(cfg, rel), allow_unicode=True, sort_keys=False), encoding="utf-8")
        index_entries.append({
            "page_id": "",
            "title": cfg["title"],
            "parent_id": PARENT_ID,
            "depth": 2,
            "relative_path": rel,
            "slug": cfg["slug"],
            "storage_file": f"{rel}/body.storage.xhtml",
            "view_file": f"{rel}/body.view.html",
        })
        print(f"[DONE] Created local draft page: {cfg['title']}")
        print(f"[PATH] {page_dir.relative_to(ROOT)}")
    update_index(index_entries)


if __name__ == "__main__":
    main()
