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
        "slug": "taslak-iuc-bidb-prs-xxx-s-prosedur-tanimi-sablonu",
        "document_code": "İÜC.BİDB.PRS.XXX.Ş",
        "usage": "Prosedür Tanımı",
        "name_example": "İÜC.BİDB.PRS.XXX - Prosedür Adı",
        "purpose": "Bu şablon, kurum genelinde uygulanacak prosedürlerin amaç, kapsam, kapsam dışı durumlar, referanslar, roller, ilkeler, uygulama esasları, yayın/erişim/bakım kuralları ve sürüm geçmişi bilgilerinin standart yapıda tanımlanması için kullanılır.",
        "note": "Prosedür dokümanları süreç şablonu gibi süreç akışı veya uyarlama matrisi içermek zorunda değildir; prosedürün gerçek uygulama içeriğini taşıyacak sade ve normatif yapı kullanılır.",
        "sections": [
            {"title": "1. Doküman Bilgileri", "type": "info"},
            {"title": "2. Amaç", "type": "paragraph", "text": "Bu bölümde prosedürün hangi ihtiyacı karşılamak için hazırlandığı ve kurum içinde hangi amacı gerçekleştirdiği açıklanır."},
            {"title": "3. Kapsam", "type": "paragraph_list", "text": "Bu bölümde prosedürün uygulanacağı süreçler, projeler, birimler, doküman türleri, sistemler ve faaliyetler tanımlanır.", "items": ["<em>Kapsama dahil faaliyet / alan</em>", "<em>Kapsama dahil faaliyet / alan</em>"]},
            {"title": "4. Kapsam Dışı", "type": "paragraph_list", "text": "Bu bölümde prosedürün uygulanmadığı doküman, kayıt, faaliyet veya istisna durumları tanımlanır.", "items": ["<em>Kapsam dışı durum</em>", "<em>Kapsam dışı durum</em>"]},
            {"title": "5. Referanslar", "type": "reference"},
            {"title": "6. Terimler ve Kısaltmalar", "type": "terms"},
            {"title": "7. Roller ve Sorumluluklar", "type": "roles"},
            {"title": "8. Genel İlkeler", "type": "principles", "headers": ["İlke", "Açıklama"]},
            {"title": "9. Prosedür Esasları", "type": "custom_table", "intro": "Bu bölümde prosedürün ana uygulama yaklaşımı, sınıflandırmaları, zorunluluk seviyeleri ve karar kuralları tanımlanır.", "headers": ["Esas / Kural", "Açıklama", "Zorunluluk", "Not"]},
            {"title": "10. Uygulama / Strateji Matrisi", "type": "custom_table", "intro": "Bu bölümde prosedürün temel uygulama adımları veya strateji matrisi tablo halinde verilir. Yaşam döngüsü, doküman sınıflandırması, yayın ortamı veya erişim stratejisi gibi kapsamlar bu bölümde yönetilebilir.", "headers": ["Alan / Aşama", "Uygulama Kuralı", "Sorumlu", "Kayıt / Kanıt", "Not"]},
            {"title": "11. Yayın, Erişim ve Bakım Kuralları", "type": "custom_table", "intro": "Bu bölümde prosedür kapsamındaki yayın ortamı, erişim, dağıtım, bakım ve arşivleme kuralları tanımlanır.", "headers": ["Kural Alanı", "Kural", "Sorumlu", "Kayıt / Kanıt"]},
            {"title": "12. Kayıtlar ve Kanıtlar", "type": "records"},
            {"title": "13. Sürüm Geçmişi", "type": "record_history"},
        ],
    },
    {
        "kind": "KLV",
        "title": "TASLAK - İÜC.BİDB.KLV.XXX.Ş - Kılavuz ve Talimat Tanımı Şablonu",
        "slug": "taslak-iuc-bidb-klv-xxx-s-kilavuz-ve-talimat-tanimi-sablonu",
        "document_code": "İÜC.BİDB.KLV.XXX.Ş",
        "usage": "Kılavuz ve Talimat Tanımı",
        "name_example": "İÜC.BİDB.KLV.XXX - Kılavuz / Talimat Adı",
        "purpose": "Bu şablon, kurum genelinde kullanılacak kılavuz ve talimatların amaç, kapsam, kapsam dışı durumlar, referanslar, terimler, genel ilkeler, kural/adım tabloları, örnekler, kayıtlar ve sürüm geçmişi bilgilerinin standart yapıda tanımlanması için kullanılır.",
        "note": "Kılavuz ve talimat dokümanları süreç akışı veya RACI gibi süreç dokümanı bölümleri içermek zorunda değildir; kullanıcıyı yönlendiren kural, örnek ve uygulama açıklamalarını taşıyacak esnek yapı kullanılır.",
        "sections": [
            {"title": "1. Doküman Bilgileri", "type": "info"},
            {"title": "2. Amaç", "type": "paragraph", "text": "Bu bölümde kılavuz veya talimatın hangi ihtiyacı karşılamak için hazırlandığı ve kullanıcıya hangi konuda yönlendirme sağladığı açıklanır."},
            {"title": "3. Kapsam", "type": "paragraph_list", "text": "Bu bölümde kılavuz veya talimatın uygulanacağı doküman türleri, kullanıcı grupları, sistemler, süreçler veya faaliyetler tanımlanır.", "items": ["<em>Kapsama dahil alan</em>", "<em>Kapsama dahil alan</em>"]},
            {"title": "4. Kapsam Dışı", "type": "paragraph_list", "text": "Bu bölümde kılavuz veya talimatın uygulanmadığı durumlar ve istisnalar tanımlanır.", "items": ["<em>Kapsam dışı durum</em>", "<em>Kapsam dışı durum</em>"]},
            {"title": "5. Referanslar", "type": "reference"},
            {"title": "6. Terimler ve Kısaltmalar", "type": "terms"},
            {"title": "7. Genel İlkeler", "type": "principles", "headers": ["İlke", "Açıklama"]},
            {"title": "8. Kural ve Uygulama Alanları", "type": "custom_table", "intro": "Bu bölümde kılavuz veya talimatın temel kural alanları ve uygulama başlıkları tanımlanır. Örneğin başlık kuralları, tablo kullanımı, tarih/sürüm kuralları veya sistem kullanım adımları bu bölümde ele alınabilir.", "headers": ["Kural / Alan", "Açıklama", "Örnek", "Not"]},
            {"title": "9. Uygulama Adımları / Talimatlar", "type": "custom_table", "intro": "Bu bölümde kullanıcı tarafından izlenecek adımlar veya talimatlar tablo halinde tanımlanır.", "headers": ["Adım", "Talimat / Uygulama Adımı", "Açıklama", "Örnek / Kanıt"]},
            {"title": "10. Örnekler ve Formatlar", "type": "custom_table", "intro": "Bu bölümde dosya adı, başlık, tablo, kod bloğu, görsel veya diğer format örnekleri verilebilir.", "headers": ["Örnek Alanı", "Kullanım", "Örnek", "Açıklama"]},
            {"title": "11. Kontrol ve Gözden Geçirme Kuralları", "type": "custom_table", "intro": "Bu bölümde kılavuz veya talimatın uygulanırken nasıl kontrol edileceği ve ne zaman gözden geçirileceği tanımlanır.", "headers": ["Kontrol Alanı", "Kontrol Yöntemi", "Sıklık", "Sorumlu", "Kayıt / Kanıt"]},
            {"title": "12. Kayıtlar ve Kanıtlar", "type": "records"},
            {"title": "13. Sürüm Geçmişi", "type": "record_history"},
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


def bullet_list(items: list[str]) -> str:
    return "<ul>" + "".join(f"<li>{item}</li>" for item in items) + "</ul>"


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


def render_section(section: dict[str, Any], cfg: dict[str, Any]) -> str:
    title = section["title"]
    kind = section["type"]
    parts: list[str] = [f"<h2>{e(title)}</h2>"]

    if kind == "info":
        parts.append(table(["Alan", "Değer"], [
            ["Doküman Kodu", placeholder("İÜC.BİDB." + cfg["kind"] + ".XXX")],
            ["Doküman Adı", placeholder("Doküman adı")],
            ["Doküman Türü", cfg["usage"].replace(" Tanımı", "")],
            ["İlişkili Süreç / Kapsam", placeholder("İlgili süreç, yönetim alanı veya kullanım kapsamı")],
            ["Süreç Referansı", placeholder("Varsa standart / süreç referansı")],
            ["Doküman Sahibi", placeholder("Rol / birim")],
            ["Hazırlayan", placeholder("Rol / kişi")],
            ["Gözden Geçiren", placeholder("Rol / kişi")],
            ["Onaylayan", placeholder("Rol / kişi")],
            ["Onay Tarihi", placeholder("GG-AA-YYYY")],
            ["Durum", placeholder("Taslak / Gözden Geçirildi / Onaylı / Aktif / Pasif / Arşiv")],
            ["Sürüm", placeholder("v0.1 / v1.0 / v1.1")],
            ["Yürürlük Tarihi", placeholder("GG-AA-YYYY")],
            ["Son Gözden Geçirme Tarihi", placeholder("GG-AA-YYYY")],
            ["Güncelleme Sıklığı", placeholder("Yılda bir veya ihtiyaç halinde")],
        ]))
    elif kind == "paragraph":
        parts.append(p(section["text"]))
    elif kind == "paragraph_list":
        parts.append(p(section["text"]))
        parts.append(bullet_list(section["items"]))
    elif kind == "reference":
        parts.append(table(["Referans", "Açıklama"], [
            [placeholder("İlgili süreç / prosedür / kılavuz / standart"), placeholder("Referansın bu dokümanla ilişkisi")],
            [placeholder("İlgili kayıt / liste / sistem"), placeholder("Referansın bu dokümanla ilişkisi")],
        ]))
    elif kind == "terms":
        parts.append(table(["Terim / Kısaltma", "Açıklama"], [
            [placeholder("Terim"), placeholder("Açıklama")],
            [placeholder("Kısaltma"), placeholder("Açıklama")],
        ]))
    elif kind == "roles":
        parts.append(table(["Rol", "Sorumluluk", "Yetki"], [
            [placeholder("Rol adı"), placeholder("Sorumluluk açıklaması"), placeholder("Yetki açıklaması")],
            [placeholder("Rol adı"), placeholder("Sorumluluk açıklaması"), placeholder("Yetki açıklaması")],
        ]))
    elif kind == "principles":
        parts.append(table(section["headers"], [
            [placeholder("İlke"), placeholder("Açıklama")],
            [placeholder("İlke"), placeholder("Açıklama")],
        ]))
    elif kind == "custom_table":
        parts.append(p(section["intro"]))
        parts.append(table(section["headers"], [[placeholder(header) for header in section["headers"]] for _ in range(2)]))
    elif kind == "records":
        parts.append(table(["Kayıt / Kanıt", "Kullanım Amacı", "Saklama Yeri", "Sorumlu", "Not"], [
            [placeholder("Kayıt / kanıt adı"), placeholder("Ne için kullanılır?"), placeholder("Confluence / Drive / Jira / sistem"), placeholder("Rol"), placeholder("Not")],
            [placeholder("Kayıt / kanıt adı"), placeholder("Ne için kullanılır?"), placeholder("Confluence / Drive / Jira / sistem"), placeholder("Rol"), placeholder("Not")],
        ]))
    elif kind == "record_history":
        parts.append(table(["Sürüm", "Tarih", "Açıklama", "Hazırlayan/Güncelleyen", "Gözden Geçiren", "Onay"], record_version_history_rows()))
    else:
        raise ValueError(f"Unknown section type: {kind}")

    return "".join(parts)


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

    for section in cfg["sections"]:
        parts.append(render_section(section, cfg))

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
