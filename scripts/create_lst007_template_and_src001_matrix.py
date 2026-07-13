#!/usr/bin/env python3
"""Create LST.007 template and SRÇ.001 Process Interaction Matrix pages.

The generated pages include:
- Mermaid source code (.mmd)
- A PNG diagram generated from the same interaction model when possible
- Local body.view.html with the PNG rendered for review
- Confluence storage with an attachment image reference

PNG generation strategy:
1. If `mmdc` (Mermaid CLI) exists, render the Mermaid file directly.
2. Otherwise, generate a simple fallback PNG from the same node/edge model with Pillow.
3. If Pillow is not available, keep the Mermaid source and show a warning.
"""
from __future__ import annotations

import html
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
CONFLUENCE_DIR = ROOT / "confluence"
INDEX_PATH = CONFLUENCE_DIR / "index.yaml"
ROOT_PAGE = CONFLUENCE_DIR / "pages/000-root-iuc-bidb-spice-2026-level-3"
TEMPLATE_PARENT = ROOT_PAGE / "02-sablonlar"
ARCHIVE_PARENT = TEMPLATE_PARENT / "arsiv-kaldirilan-sablonlar"
SRC001_PARENT = ROOT_PAGE / "01-surec-dokumanlari/iuc-bidb-src-001-dokumantasyon-sureci"

TEMPLATE_PARENT_ID = "137265785"
TEMPLATE_PARENT_TITLE = "02 - Şablonlar"
SRC001_PARENT_ID = "137265796"
SRC001_PARENT_TITLE = "İÜC.BİDB.SRÇ.001 - Dokümantasyon Süreci"

OLD_TEMPLATE_SLUG = "iuc-bidb-lst-007-s-surec-mimari-ve-etkilesim-matrisi-sablonu"
OLD_TEMPLATE_TITLE = "İÜC.BİDB.LST.007.Ş - Süreç Mimari ve Etkileşim Matrisi Şablonu"
ARCHIVED_TEMPLATE_SLUG = "kaldirildi-iuc-bidb-lst-007-s-surec-mimari-ve-etkilesim-matrisi-sablonu"
ARCHIVED_TEMPLATE_TITLE = "KALDIRILDI - İÜC.BİDB.LST.007.Ş - Süreç Mimari ve Etkileşim Matrisi Şablonu"

TEMPLATE_SLUG = "iuc-bidb-lst-007-s-surec-etkilesim-matrisi-sablonu"
TEMPLATE_TITLE = "İÜC.BİDB.LST.007.Ş - Süreç Etkileşim Matrisi Şablonu"
TEMPLATE_DIR = TEMPLATE_PARENT / TEMPLATE_SLUG

SRC001_SLUG = "iuc-bidb-lst-007-surec-etkilesim-matrisi-iuc-bidb-src-001"
SRC001_TITLE = "İÜC.BİDB.LST.007 - Süreç Etkileşim Matrisi (İÜC.BİDB.SRÇ.001)"
SRC001_DIR = SRC001_PARENT / SRC001_SLUG

CSS = """
body{margin:0;background:#fff;color:#172b4d;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;line-height:1.55}
.confluence-page{max-width:1120px;margin:0 auto;padding:32px 24px 56px}
h1,h2,h3,h4,h5,h6{margin:1.4em 0 .55em;line-height:1.25;color:#0f172a}
h1{margin-top:0;padding-bottom:12px;border-bottom:1px solid #d8dee4}
p{margin:0 0 12px}
table{width:100%;border-collapse:collapse;margin:16px 0;table-layout:auto}
th,td{border:1px solid #c9d1d9;padding:8px 10px;vertical-align:top}
th{background:#f6f8fa;font-weight:600;text-align:left}
pre{background:#f6f8fa;padding:12px 16px;border-radius:6px;overflow:auto}
.diagram{max-width:100%;border:1px solid #c9d1d9;border-radius:6px;margin:16px 0}
""".strip()

TEMPLATE_NODES = {
    "PROCESS": "Süreç",
    "INPUT": "Girdi Süreç / Kaynak",
    "OUTPUT": "Çıktı Süreç / Hedef",
    "RECORD": "Etkileşim Kaydı",
}
TEMPLATE_EDGES = [
    ("INPUT", "PROCESS", "Girdi / tetikleyici"),
    ("PROCESS", "OUTPUT", "Çıktı / yönlendirme"),
    ("PROCESS", "RECORD", "İzlenebilir kayıt"),
]

SRC001_NODES = {
    "SRC004": "SRÇ.004\nSüreç Kurulumu",
    "SRC001": "SRÇ.001\nDokümantasyon Süreci",
    "PRS001": "PRS.001\nYazılım Projesi\nDokümantasyon Stratejisi",
    "KLV001": "KLV.001\nDoküman Yazım\nKuralları",
    "LST001": "LST.001\nAktif Dokümanlar",
    "LST002": "LST.002\nDeğişiklik Kaydı",
    "LST003": "LST.003\nGözden Geçirme Kaydı",
    "LST008": "LST.008\nİş Ürünleri ve\nKalite Kriterleri",
    "LST009": "LST.009\nPerformans Ölçüm Seti",
    "LST010": "LST.010\nRACI Matrisi",
    "SRC002": "SRÇ.002\nKalite Güvencesi",
    "SRC005": "SRÇ.005\nSüreç Değerlendirme",
    "PROJECTS": "Yazılım Projeleri\nDoküman/Kayıt Seti",
    "ALL": "Diğer Süreçler\nve Dokümanlar",
}
SRC001_EDGES = [
    ("SRC004", "SRC001", "süreç yapısı / doküman ihtiyacı"),
    ("SRC001", "PRS001", "proje dokümantasyon stratejisi"),
    ("SRC001", "KLV001", "yazım ve format kuralları"),
    ("SRC001", "LST001", "aktif doküman envanteri"),
    ("SRC001", "LST002", "değişiklik izleme"),
    ("SRC001", "LST003", "gözden geçirme izleme"),
    ("SRC001", "LST008", "iş ürünü / kalite kriteri"),
    ("SRC001", "LST009", "ölçüm ve izleme"),
    ("SRC001", "LST010", "rol ve yetki"),
    ("PRS001", "PROJECTS", "yaşam döngüsü doküman/kayıt seti"),
    ("KLV001", "ALL", "ortak yazım standardı"),
    ("SRC001", "SRC002", "doküman gözden geçirme kanıtları"),
    ("SRC001", "SRC005", "değerlendirme kanıtları"),
]


def e(value: object) -> str:
    return html.escape(str(value), quote=False)


def p(text: str) -> str:
    return f"<p>{e(text)}</p>"


def table(headers: list[str], rows: list[list[str]]) -> str:
    head = "".join(f"<th>{e(h)}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>" for row in rows)
    return f'<table class="wrapped"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>'


def mermaid(nodes: dict[str, str], edges: list[tuple[str, str, str]]) -> str:
    lines = ["flowchart LR"]
    for key, label in nodes.items():
        lines.append(f'  {key}["{label}"]')
    for source, target, label in edges:
        lines.append(f'  {source} -->|"{label}"| {target}')
    return "\n".join(lines) + "\n"


def write_mermaid(page_dir: Path, filename: str, content: str) -> Path:
    assets = page_dir / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    path = assets / filename
    path.write_text(content, encoding="utf-8")
    return path


def render_png_with_mmdc(mmd_path: Path, png_path: Path) -> bool:
    if not shutil.which("mmdc"):
        return False
    try:
        subprocess.run(["mmdc", "-i", str(mmd_path), "-o", str(png_path), "-b", "white"], check=True)
        return png_path.exists()
    except Exception:
        return False


def render_fallback_png(nodes: dict[str, str], edges: list[tuple[str, str, str]], png_path: Path) -> bool:
    try:
        from PIL import Image, ImageDraw, ImageFont
    except Exception:
        print(f"[WARN] PNG oluşturulamadı. Mermaid CLI veya Pillow bulunamadı: {png_path}")
        return False

    width = 1600
    height = max(720, 130 + 92 * len(nodes))
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("Arial.ttf", 24)
        small = ImageFont.truetype("Arial.ttf", 17)
    except Exception:
        font = ImageFont.load_default()
        small = ImageFont.load_default()

    keys = list(nodes.keys())
    cols = [130, 575, 1020]
    positions: dict[str, tuple[int, int]] = {}
    for i, key in enumerate(keys):
        col = i % 3
        row = i // 3
        positions[key] = (cols[col], 70 + row * 145)

    for source, target, label in edges:
        if source not in positions or target not in positions:
            continue
        x1, y1 = positions[source]
        x2, y2 = positions[target]
        start = (x1 + 340, y1 + 45) if x1 < x2 else (x1, y1 + 45)
        end = (x2, y2 + 45) if x1 < x2 else (x2 + 340, y2 + 45)
        draw.line([start, end], fill=(80, 80, 80), width=3)
        mx, my = (start[0] + end[0]) // 2, (start[1] + end[1]) // 2
        draw.text((mx - 90, my - 22), label[:42], fill=(80, 80, 80), font=small)

    for key, label in nodes.items():
        x, y = positions[key]
        draw.rounded_rectangle([x, y, x + 340, y + 90], radius=14, outline=(30, 64, 175), width=3, fill=(245, 248, 255))
        for j, line in enumerate(label.split("\n")):
            draw.text((x + 18, y + 14 + j * 24), line, fill=(15, 23, 42), font=font)

    img.save(png_path)
    return True


def render_png(page_dir: Path, mmd_name: str, png_name: str, nodes: dict[str, str], edges: list[tuple[str, str, str]]) -> None:
    mmd_path = page_dir / "assets" / mmd_name
    png_path = page_dir / "assets" / png_name
    if render_png_with_mmdc(mmd_path, png_path):
        print(f"[PNG] Mermaid CLI: {png_path.relative_to(ROOT)}")
        return
    if render_fallback_png(nodes, edges, png_path):
        print(f"[PNG] Fallback renderer: {png_path.relative_to(ROOT)}")


def ac_image(filename: str) -> str:
    return f'<p><ac:image ac:alt="{e(filename)}"><ri:attachment ri:filename="{e(filename)}" /></ac:image></p>'


def local_image(filename: str) -> str:
    return f'<p><img class="diagram" src="assets/{e(filename)}" alt="{e(filename)}" /></p>'


def code_block(code: str) -> str:
    return f'<pre><code class="language-mermaid">{e(code)}</code></pre>'


def build_template_storage(mermaid_code: str) -> str:
    return "".join([
        "<h2>0. Liste Hakkında</h2>",
        "<h3>0.1. Liste Üst Bilgisi</h3>",
        table(["Alan", "Değer"], [
            ["Kurum", "İstanbul Üniversitesi - Cerrahpaşa Bilgi İşlem Daire Başkanlığı"],
            ["Doküman Kodu", "İÜC.BİDB.LST.007.Ş"],
            ["Doküman Türü", "Liste / Matris Şablonu"],
            ["Kullanım Alanı", "Süreç etkileşimlerinin Mermaid kodu, PNG görseli ve matrislerle tanımlanması"],
            ["Durum", "Aktif"],
            ["Sürüm", "v1.0"],
            ["Yürürlük Tarihi", "15-02-2025"],
            ["Son Gözden Geçirme Tarihi", "15-02-2025"],
        ]),
        "<h3>0.2. Listenin Kullanım Amacı</h3>",
        p("Bu şablon, süreçler arasındaki girdi, çıktı, kayıt ve yönlendirme etkileşimlerinin hem görsel diyagram hem de matris yapısıyla tanımlanması için kullanılır."),
        "<h3>0.3. Doküman Adlandırma Kuralı</h3>",
        p("Bu şablondan üretilen gerçek listeler İÜC.BİDB.LST.007 - Süreç Etkileşim Matrisi (İÜC.BİDB.SRÇ.XXX) formatında adlandırılır."),
        "<h3>0.4. Sürüm Geçmişi</h3>",
        table(["Sürüm", "Tarih", "Açıklama", "Hazırlayan/Güncelleyen", "Gözden Geçiren", "Onay"], [
            ["v0.1", "01-02-2025", "İlk taslak oluşturuldu.", "Soner DEDEOĞLU - Kalite Danışmanı", "-", "-"],
            ["v1.0", "15-02-2025", "Şablon onaylanarak yürürlüğe alındı.", "Soner DEDEOĞLU - Kalite Danışmanı", "Levent BAYEZİT - Dokümantasyon Süreç Sahibi", "Mustafa Nusret SARISAKAL - Bilgi İşlem Daire Başkanı"],
        ]),
        "<h2>1. Liste Özeti</h2>",
        table(["Alan", "Değer"], [["Liste Kodu ve Adı", "<em>İÜC.BİDB.LST.007 - Süreç Etkileşim Matrisi (İÜC.BİDB.SRÇ.XXX)</em>"], ["İlgili Süreç", "<em>İÜC.BİDB.SRÇ.XXX - Süreç Adı</em>"], ["Kullanım Amacı", "<em>Süreç etkileşimlerini görsel ve matris yapısıyla izlemek</em>"], ["Sorumlu", "<em>Rol / birim</em>"], ["Durum", "<em>Taslak / Aktif</em>"], ["Sürüm", "<em>v1.0</em>"]]),
        "<h2>2. Kullanım Değerleri</h2>",
        table(["Alan", "Kullanım Kuralı"], [["Mermaid Kodu", "Diyagramın kaynak kodu bu bölümde saklanır."], ["PNG Görsel", "Mermaid kodundan üretilmiş görsel, hızlı okuma ve denetim sunumu için kullanılır."], ["Girdi Matrisi", "Sürece gelen etkileşimler tablo halinde açıklanır."], ["Çıktı Matrisi", "Süreçten çıkan etkileşimler tablo halinde açıklanır."], ["Etkileşim Notları", "Varsa özel uygulama ve sınırlamalar yazılır."]]),
        "<h2>3. Süreç Etkileşim Diyagramı</h2>",
        "<h3>3.1. Mermaid Kodu</h3>",
        code_block(mermaid_code),
        "<h3>3.2. PNG Görsel</h3>",
        ac_image("lst007-template-surec-etkilesim.png"),
        "<h2>4. Girdi Etkileşimleri Matrisi</h2>",
        table(["Kaynak Süreç / Kaynak", "Etkileşim Türü", "Girdi / Tetikleyici", "Kayıt / Kanıt", "Açıklama"], [["<em>Kaynak süreç</em>", "<em>Girdi / bilgi / kayıt</em>", "<em>Girdi adı</em>", "<em>Kayıt</em>", "<em>Açıklama</em>"]]),
        "<h2>5. Çıktı Etkileşimleri Matrisi</h2>",
        table(["Hedef Süreç / Hedef", "Etkileşim Türü", "Çıktı / Yönlendirme", "Kayıt / Kanıt", "Açıklama"], [["<em>Hedef süreç</em>", "<em>Çıktı / bilgi / kayıt</em>", "<em>Çıktı adı</em>", "<em>Kayıt</em>", "<em>Açıklama</em>"]]),
        "<h2>6. Etkileşim Notları</h2>",
        p("Bu bölümde sürece özgü etkileşim varsayımları, sınırlamalar ve denetim açıklamaları yazılır."),
        "<h2>7. Sürüm Geçmişi</h2>",
        table(["Sürüm", "Tarih", "Açıklama", "Hazırlayan/Güncelleyen", "Gözden Geçiren", "Onay"], [["v0.1", "<em>GG-AA-YYYY</em>", "<em>İlk taslak</em>", "<em>Rol / kişi</em>", "<em>Rol / kişi</em>", "<em>Rol / kişi</em>"], ["v1.0", "<em>GG-AA-YYYY</em>", "<em>Onaylı sürüm</em>", "<em>Rol / kişi</em>", "<em>Rol / kişi</em>", "<em>Rol / kişi</em>"]]),
    ]) + "\n"


def build_src001_storage(mermaid_code: str) -> str:
    return "".join([
        "<h2>1. Liste Özeti</h2>",
        table(["Alan", "Değer"], [["Liste Kodu ve Adı", "İÜC.BİDB.LST.007 - Süreç Etkileşim Matrisi (İÜC.BİDB.SRÇ.001)"], ["İlgili Süreç", "İÜC.BİDB.SRÇ.001 - Dokümantasyon Süreci"], ["Kullanım Amacı", "Dokümantasyon Süreci’nin diğer süreç, prosedür, kılavuz, liste ve proje dokümantasyonu bileşenleriyle etkileşimini göstermek"], ["Sorumlu", "Levent BAYEZİT - Dokümantasyon Süreç Sahibi"], ["Durum", "Onaylı"], ["Sürüm", "v1.0"], ["Yürürlük Tarihi", "15-02-2025"], ["Son Gözden Geçirme Tarihi", "15-02-2025"]]),
        "<h2>2. Kullanım Değerleri</h2>",
        table(["Alan", "Değer"], [["Diyagram Kaynağı", "Mermaid kodu"], ["Görsel Çıktı", "src001-surec-etkilesim.png"], ["Etkileşim Kapsamı", "SRÇ.001’in dokümantasyon yönetimi çıktıları ve bu çıktıların desteklediği süreç/dokümanlar"], ["Kapsam Dışı", "Tüm süreçlerin ayrıntılı operasyonel veri akışları"], ["Güncelleme Sıklığı", "Süreç mimarisi veya dokümantasyon yapısı değiştiğinde"]]),
        "<h2>3. Süreç Etkileşim Diyagramı</h2>",
        "<h3>3.1. Mermaid Kodu</h3>",
        code_block(mermaid_code),
        "<h3>3.2. PNG Görsel</h3>",
        ac_image("src001-surec-etkilesim.png"),
        "<h2>4. Girdi Etkileşimleri Matrisi</h2>",
        table(["Kaynak Süreç / Kaynak", "Etkileşim Türü", "Girdi / Tetikleyici", "Kayıt / Kanıt", "Açıklama"], [
            ["İÜC.BİDB.SRÇ.004 - Süreç Kurulumu Süreci", "Süreç yapısı / ihtiyaç", "Süreç dokümantasyon ihtiyacı", "Süreç tanımı ve ilgili alt kayıtlar", "SRÇ.001, süreç dokümanlarının ve bağlı kayıtların ortak yönetim yaklaşımını sağlar."],
            ["Yazılım Projeleri", "Proje dokümantasyon ihtiyacı", "Proje yaşam döngüsünde oluşan doküman/kayıt gereksinimi", "Jira / Confluence / Bitbucket / Bamboo / Drive kayıtları", "PRS.001 aracılığıyla yazılım projeleri için özel stratejiye dönüştürülür."],
            ["İÜC.BİDB.SRÇ.002 - Kalite Güvencesi Süreci", "Gözden geçirme girdisi", "Doküman kalite gözden geçirme ihtiyacı", "LST.003 ve ilgili gözden geçirme kayıtları", "Kalite kontrolleri dokümantasyon kayıtlarına yansıtılır."],
            ["İÜC.BİDB.SRÇ.005 - Süreç Değerlendirme Süreci", "Değerlendirme girdisi", "Süreç doküman ve kayıt kanıtı ihtiyacı", "FRM.001, LST.008, LST.009, LST.010", "Süreç değerlendirmelerinde kullanılacak dokümantasyon kanıtları SRÇ.001 çıktılarıyla desteklenir."],
        ]),
        "<h2>5. Çıktı Etkileşimleri Matrisi</h2>",
        table(["Hedef Süreç / Hedef", "Etkileşim Türü", "Çıktı / Yönlendirme", "Kayıt / Kanıt", "Açıklama"], [
            ["İÜC.BİDB.PRS.001 - Yazılım Projeleri Dokümantasyon Prosedürü", "Prosedür yönlendirmesi", "Yazılım projeleri dokümantasyon stratejisi", "PRS.001", "SRÇ.001’in genel dokümantasyon yaklaşımı yazılım projelerine özel hale getirilir."],
            ["İÜC.BİDB.KLV.001 - Doküman Yazım Kuralları Talimatı", "Kılavuz / talimat", "Doküman yazım, başlık, tablo, sürüm ve yayın kuralları", "KLV.001", "Tüm doküman türleri için ortak yazım standardı sağlar."],
            ["İÜC.BİDB.LST.001 - Aktif Dokümanlar Listesi", "Envanter çıktısı", "Genel aktif doküman envanteri", "LST.001", "Genel kullanıma açık dokümanların güncel durumunu izler."],
            ["İÜC.BİDB.LST.002 - Doküman Değişiklik Kaydı", "Değişiklik izleme", "Doküman değişikliklerinin kaydı", "LST.002", "Doküman değişikliklerinin izlenebilirliğini destekler."],
            ["İÜC.BİDB.LST.003 - Doküman Gözden Geçirme Kaydı", "Gözden geçirme izleme", "Doküman gözden geçirme kayıtları", "LST.003", "Doküman kontrolleri ve onay öncesi değerlendirmeleri izler."],
            ["SRÇ.001 alt kayıtları", "Süreç kanıtı", "LST.008, LST.009, LST.010 ve FRM.001", "İlgili süreç alt kayıtları", "SRÇ.001’in iş ürünü, ölçüm, RACI ve gözden geçirme kanıtlarını sağlar."],
            ["Diğer süreç dokümanları", "Ortak dokümantasyon yapısı", "Şablon, yazım kuralı ve kayıt yönetimi yaklaşımı", "Şablonlar ve ilgili süreç kayıtları", "Tüm süreçlerin tutarlı doküman yapısında hazırlanmasını destekler."],
        ]),
        "<h2>6. Etkileşim Notları</h2>",
        p("SRÇ.001, diğer süreçlerin operasyonel akışını tekrar tanımlamaz. Bu matris yalnızca dokümantasyon yönetimi açısından oluşan girdi, çıktı, kayıt ve yönlendirme etkileşimlerini gösterir."),
        p("PRS.001 ve KLV.001, SRÇ.001’in uzantısı niteliğindedir. PRS.001 yazılım projeleri özelinde stratejiyi; KLV.001 ise dokümanların yazım ve biçim kurallarını tanımlar."),
        "<h2>7. Sürüm Geçmişi</h2>",
        table(["Sürüm", "Tarih", "Açıklama", "Hazırlayan/Güncelleyen", "Gözden Geçiren", "Onay"], [["v0.1", "01-02-2025", "İlk taslak oluşturuldu.", "Soner DEDEOĞLU - Kalite Danışmanı", "Levent BAYEZİT - Dokümantasyon Süreç Sahibi", "-"], ["v1.0", "15-02-2025", "Matris onaylanarak yürürlüğe alındı.", "Soner DEDEOĞLU - Kalite Danışmanı", "Levent BAYEZİT - Dokümantasyon Süreç Sahibi", "Mustafa Nusret SARISAKAL - Bilgi İşlem Daire Başkanı"]]),
    ]) + "\n"


def build_view(title: str, storage: str, png_name: str) -> str:
    local = storage.replace(ac_image(png_name), local_image(png_name))
    return f"""<!doctype html>
<html lang="tr"><head><meta charset="utf-8"><title>{e(title)}</title><style>{CSS}</style></head>
<body><main class="confluence-page"><h1>{e(title)}</h1>{local}</main></body></html>
"""


def page_yaml(page_dir: Path, title: str, slug: str, parent_id: str, parent_title: str, status: str, depth: int) -> dict[str, Any]:
    rel = str(page_dir.relative_to(CONFLUENCE_DIR)).replace("\\", "/")
    existing = yaml.safe_load((page_dir / "page.yaml").read_text(encoding="utf-8")) if (page_dir / "page.yaml").exists() else {}
    existing.update({
        "title": title,
        "slug": slug,
        "relative_path": rel,
        "parent_id": parent_id,
        "parent_title": parent_title,
        "status": status,
        "depth": depth,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "storage_file": "body.storage.xhtml",
        "view_file": "body.view.html",
        "has_view_html": True,
    })
    existing.setdefault("page_id", "")
    existing.setdefault("space", "SSSS")
    existing.setdefault("version", "")
    existing.setdefault("url", "")
    existing.setdefault("children_count", 0)
    return existing


def write_page(page_dir: Path, title: str, slug: str, parent_id: str, parent_title: str, status: str, depth: int, storage: str, png_name: str) -> None:
    page_dir.mkdir(parents=True, exist_ok=True)
    (page_dir / "body.storage.xhtml").write_text(storage, encoding="utf-8")
    (page_dir / "body.view.html").write_text(build_view(title, storage, png_name), encoding="utf-8")
    (page_dir / "page.yaml").write_text(yaml.safe_dump(page_yaml(page_dir, title, slug, parent_id, parent_title, status, depth), allow_unicode=True, sort_keys=False), encoding="utf-8")


def archive_old_template() -> None:
    old_dir = TEMPLATE_PARENT / OLD_TEMPLATE_SLUG
    if not old_dir.exists():
        return
    archive_id = yaml.safe_load((ARCHIVE_PARENT / "page.yaml").read_text(encoding="utf-8")).get("page_id", "")
    target = ARCHIVE_PARENT / ARCHIVED_TEMPLATE_SLUG
    if target.exists():
        shutil.rmtree(target)
    shutil.move(str(old_dir), str(target))
    meta = page_yaml(target, ARCHIVED_TEMPLATE_TITLE, ARCHIVED_TEMPLATE_SLUG, str(archive_id), "Arşiv - Kaldırılan Şablonlar", "archived", 3)
    (target / "page.yaml").write_text(yaml.safe_dump(meta, allow_unicode=True, sort_keys=False), encoding="utf-8")
    for filename in ("body.storage.xhtml", "body.view.html"):
        pth = target / filename
        if pth.exists():
            text = pth.read_text(encoding="utf-8").replace(OLD_TEMPLATE_TITLE, ARCHIVED_TEMPLATE_TITLE)
            pth.write_text(text, encoding="utf-8")
    print(f"[ARCHIVED] {target.relative_to(ROOT)}")


def update_index(paths: list[Path]) -> None:
    index = yaml.safe_load(INDEX_PATH.read_text(encoding="utf-8")) or {}
    pages = index.setdefault("pages", [])
    rels = {str(p.relative_to(CONFLUENCE_DIR)).replace("\\", "/") for p in paths}
    pages[:] = [p for p in pages if p.get("relative_path") not in rels]
    for page_dir in paths:
        meta = yaml.safe_load((page_dir / "page.yaml").read_text(encoding="utf-8"))
        rel = meta["relative_path"]
        pages.append({
            "page_id": str(meta.get("page_id") or ""),
            "title": meta["title"],
            "parent_id": str(meta.get("parent_id") or ""),
            "depth": meta.get("depth", 2),
            "relative_path": rel,
            "slug": meta["slug"],
            "storage_file": f"{rel}/body.storage.xhtml",
            "view_file": f"{rel}/body.view.html",
        })
    index["total_page_count"] = len(pages)
    INDEX_PATH.write_text(yaml.safe_dump(index, allow_unicode=True, sort_keys=False), encoding="utf-8")


def main() -> None:
    archive_old_template()

    template_mermaid = mermaid(TEMPLATE_NODES, TEMPLATE_EDGES)
    src001_mermaid = mermaid(SRC001_NODES, SRC001_EDGES)

    write_page(TEMPLATE_DIR, TEMPLATE_TITLE, TEMPLATE_SLUG, TEMPLATE_PARENT_ID, TEMPLATE_PARENT_TITLE, "active", 2, build_template_storage(template_mermaid), "lst007-template-surec-etkilesim.png")
    write_page(SRC001_DIR, SRC001_TITLE, SRC001_SLUG, SRC001_PARENT_ID, SRC001_PARENT_TITLE, "active", 3, build_src001_storage(src001_mermaid), "src001-surec-etkilesim.png")

    write_mermaid(TEMPLATE_DIR, "lst007-template-surec-etkilesim.mmd", template_mermaid)
    write_mermaid(SRC001_DIR, "src001-surec-etkilesim.mmd", src001_mermaid)
    render_png(TEMPLATE_DIR, "lst007-template-surec-etkilesim.mmd", "lst007-template-surec-etkilesim.png", TEMPLATE_NODES, TEMPLATE_EDGES)
    render_png(SRC001_DIR, "src001-surec-etkilesim.mmd", "src001-surec-etkilesim.png", SRC001_NODES, SRC001_EDGES)

    paths = [TEMPLATE_DIR, SRC001_DIR]
    archived = ARCHIVE_PARENT / ARCHIVED_TEMPLATE_SLUG
    if archived.exists():
        paths.append(archived)
    update_index(paths)
    print(f"[DONE] Created {TEMPLATE_TITLE}")
    print(f"[DONE] Created {SRC001_TITLE}")


if __name__ == "__main__":
    main()
