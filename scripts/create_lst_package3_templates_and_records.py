#!/usr/bin/env python3
"""Package 3 generator for LST templates and records.

Creates/updates:
- LST.001.Ş, LST.003.Ş, LST.005.Ş, LST.006.Ş, LST.011.Ş, LST.012.Ş templates
- LST.001 active document list with document-type separated tables
- 03 - Kayıtlar ve Listeler / Soru Bankası Projesi
- LST.005 - Yaşam Döngüsü Doküman Üretim Matrisi (SB) draft record
- SRÇ.001 and PRS.001 references from old LST.005 naming to the new template/record naming
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
TEMPLATES = ROOT_PAGE / "02-sablonlar"
RECORDS = ROOT_PAGE / "03-kayitlar-ve-listeler"
SRC001 = ROOT_PAGE / "01-surec-dokumanlari/src-001-dokumantasyon-sureci"
PRS001 = ROOT_PAGE / "07-prosedurler/prs-001-yazilim-projeleri-dokumantasyon-proseduru"

TEMPLATE_PARENT_ID = "137265785"
TEMPLATE_PARENT_TITLE = "02 - Şablonlar"
RECORDS_PARENT_ID = "137265786"
RECORDS_PARENT_TITLE = "03 - Kayıtlar ve Listeler"

CSS = """
body{margin:0;background:#fff;color:#172b4d;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;line-height:1.55}
.confluence-page{max-width:1120px;margin:0 auto;padding:32px 24px 56px}
h1,h2,h3,h4,h5,h6{margin:1.4em 0 .55em;line-height:1.25;color:#0f172a}
h1{margin-top:0;padding-bottom:12px;border-bottom:1px solid #d8dee4}
p{margin:0 0 12px}
table{width:100%;border-collapse:collapse;margin:16px 0;table-layout:auto}
th,td{border:1px solid #c9d1d9;padding:8px 10px;vertical-align:top}
th{background:#f6f8fa;font-weight:600;text-align:left}
code{background:#f6f8fa;padding:2px 4px;border-radius:4px}
""".strip()

LST_TEMPLATES = [
    {
        "slug": "lst-001-s-aktif-dokumanlar-listesi-sablonu",
        "title": "LST.001.Ş - Aktif Dokümanlar Listesi Şablonu",
        "code": "LST.001.Ş",
        "purpose": "Genel kullanıma açık aktif dokümanların doküman türü bazında izlenmesi için kullanılır.",
        "sections": [
            ("3. Süreç Dokümanları", ["Doküman Kodu", "Doküman Adı", "Süreç Referansı", "Sahibi", "Durum", "Sürüm", "Yürürlük Tarihi", "Konum"]),
            ("4. Prosedürler", ["Doküman Kodu", "Doküman Adı", "İlgili Süreç", "Sahibi", "Durum", "Sürüm", "Yürürlük Tarihi", "Konum"]),
            ("5. Kılavuz ve Talimatlar", ["Doküman Kodu", "Doküman Adı", "İlgili Süreç / Kapsam", "Sahibi", "Durum", "Sürüm", "Yürürlük Tarihi", "Konum"]),
            ("6. Şablonlar", ["Şablon Kodu", "Şablon Adı", "Kullanım Alanı", "Durum", "Sürüm", "Yürürlük Tarihi", "Konum"]),
            ("7. Genel Kayıt ve Listeler", ["Doküman Kodu", "Doküman Adı", "Kullanım Alanı", "Sorumlu", "Durum", "Sürüm", "Konum"]),
            ("8. Politikalar", ["Doküman Kodu", "Doküman Adı", "Kapsam", "Sahibi", "Durum", "Sürüm", "Konum"]),
            ("9. Planlar", ["Doküman Kodu", "Doküman Adı", "Kapsam", "Sahibi", "Durum", "Sürüm", "Konum"]),
            ("10. Kapsam Dışı Dokümanlar", ["Doküman / Kayıt Grubu", "Kapsam Dışı Bırakma Nedeni", "Nerede İzlenir?"]),
        ],
    },
    {
        "slug": "lst-003-s-dokuman-gozden-gecirme-kaydi-sablonu",
        "title": "LST.003.Ş - Doküman Gözden Geçirme Kaydı Şablonu",
        "code": "LST.003.Ş",
        "purpose": "Dokümanların gözden geçirme bulguları, kararları ve aksiyonlarının izlenmesi için kullanılır.",
        "sections": [("3. Gözden Geçirme Kayıtları", ["Doküman Kodu", "Doküman Adı", "Gözden Geçirme Tarihi", "Gözden Geçiren", "Bulgular", "Karar", "Aksiyon", "Kapanış Durumu"])],
    },
    {
        "slug": "lst-005-s-yasam-dongusu-dokuman-uretim-matrisi-sablonu",
        "title": "LST.005.Ş - Yaşam Döngüsü Doküman Üretim Matrisi Şablonu",
        "code": "LST.005.Ş",
        "purpose": "Yazılım projesi yaşam döngüsü aşamalarında beklenen doküman ve kayıtların belirlenmesi için kullanılır.",
        "sections": [("3. Yaşam Döngüsü Doküman Üretim Matrisi", ["Yaşam Döngüsü Aşaması", "Beklenen Doküman / Kayıt", "Zorunluluk", "Kaynak Sistem / Yayın Ortamı", "Sorumlu Rol", "Gözden Geçirme / Onay", "Not"])],
    },
    {
        "slug": "lst-006-s-standart-surec-envanteri-sablonu",
        "title": "LST.006.Ş - Standart Süreç Envanteri Şablonu",
        "code": "LST.006.Ş",
        "purpose": "Kapsamdaki standart süreçlerinin kurumsal süreç kodlarıyla izlenmesi için kullanılır.",
        "sections": [("3. Standart Süreç Envanteri", ["Standart Süreç Kodu", "Standart Süreç Adı", "Kurumsal Süreç Kodu", "Kurumsal Süreç Adı", "Süreç Sahibi", "Durum", "Not"])],
    },
    {
        "slug": "lst-011-s-repository-yapisi-sablonu",
        "title": "LST.011.Ş - Repository Yapısı Şablonu",
        "code": "LST.011.Ş",
        "purpose": "Dokümantasyon repository klasör/sayfa yapısının tanımlanması için kullanılır.",
        "sections": [("3. Repository Yapısı", ["Alan / Klasör / Sayfa", "Kullanım Amacı", "İçerik Türü", "Sorumlu", "Not"])],
    },
    {
        "slug": "lst-012-s-surec-yayginlastirma-ve-bilgilendirme-kaydi-sablonu",
        "title": "LST.012.Ş - Süreç Yaygınlaştırma ve Bilgilendirme Kaydı Şablonu",
        "code": "LST.012.Ş",
        "purpose": "Süreç dokümanları ve ilgili değişiklikler için bilgilendirme/yaygınlaştırma kayıtlarının izlenmesi için kullanılır.",
        "sections": [("3. Yaygınlaştırma ve Bilgilendirme Kayıtları", ["Tarih", "Konu", "Hedef Kitle", "Yöntem", "Sorumlu", "Kanıt / Bağlantı", "Not"])],
    },
]

PROCESSES = [
    ("SRÇ.001", "Dokümantasyon Süreci", "SUP.7 Documentation"),
    ("SRÇ.002", "Kalite Güvencesi Süreci", "SUP.1 Quality assurance"),
    ("SRÇ.003", "Doğrulama Süreci", "SUP.2 Verification"),
    ("SRÇ.004", "Süreç Kurulumu Süreci", "PIM.1 Process establishment"),
    ("SRÇ.005", "Süreç Değerlendirme Süreci", "PIM.2 Process assessment"),
    ("SRÇ.006", "Süreç İyileştirme Süreci", "PIM.3 Process improvement"),
    ("SRÇ.007", "Proje Yönetimi Süreci", "MAN.3 Project management"),
    ("SRÇ.008", "Risk Yönetimi Süreci", "MAN.5 Risk management"),
    ("SRÇ.009", "Gereksinimlerin Toplanması Süreci", "ENG.1 Requirements elicitation"),
    ("SRÇ.010", "Yazılım Gereksinim Analizi Süreci", "ENG.4 Software requirements analysis"),
    ("SRÇ.011", "Yazılım Tasarımı Süreci", "ENG.5 Software design"),
    ("SRÇ.012", "Yazılım Geliştirme Süreci", "ENG.6 Software construction"),
    ("SRÇ.013", "Yazılım Entegrasyonu Süreci", "ENG.7 Software integration"),
    ("SRÇ.014", "Yazılım Test Süreci", "ENG.8 Software testing"),
    ("SRÇ.015", "Ürün Yayınlama / Sürüm Süreci", "SPL.2 Product release"),
    ("SRÇ.016", "Yapılandırma Yönetimi Süreci", "SUP.8 Configuration management"),
    ("SRÇ.017", "Problem Çözüm Yönetimi Süreci", "SUP.9 Problem resolution management"),
    ("SRÇ.018", "Değişiklik Talebi Yönetimi Süreci", "SUP.10 Change request management"),
    ("SRÇ.019", "İnsan Kaynakları Yönetimi Süreci", "RIN.1 Human resource management"),
    ("SRÇ.020", "Eğitim Süreci", "RIN.2 Training"),
    ("SRÇ.021", "Bilgi Yönetimi Süreci", "RIN.3 Knowledge management"),
    ("SRÇ.022", "Altyapı Süreci", "RIN.4 Infrastructure"),
    ("SRÇ.023", "Organizasyonel Yönetim Süreci", "MAN.2 Organization management"),
    ("SRÇ.024", "Kalite Yönetimi Süreci", "MAN.4 Quality management"),
    ("SRÇ.025", "Ölçüm Süreci", "MAN.6 Measurement"),
    ("SRÇ.026", "Denetim Süreci", "SUP.5 Audit"),
]


def e(value: object) -> str:
    return html.escape(str(value), quote=False)


def p(text: str) -> str:
    return f"<p>{e(text)}</p>"


def table(headers: list[str], rows: list[list[str]]) -> str:
    head = "".join(f"<th>{e(h)}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>" for row in rows)
    return f'<table class="wrapped"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>'


def view(title: str, storage: str) -> str:
    return f"""<!doctype html><html lang="tr"><head><meta charset="utf-8"><title>{e(title)}</title><style>{CSS}</style></head><body><main class="confluence-page"><h1>{e(title)}</h1>{storage}</main></body></html>\n"""


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def write_yaml(path: Path, data: dict[str, Any]) -> None:
    path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")


def page_meta(page_dir: Path, title: str, slug: str, parent_id: str, parent_title: str, depth: int, status: str = "active") -> dict[str, Any]:
    rel = str(page_dir.relative_to(CONFLUENCE_DIR)).replace("\\", "/")
    meta = load_yaml(page_dir / "page.yaml")
    meta.update({
        "title": title,
        "slug": slug,
        "relative_path": rel,
        "parent_id": parent_id,
        "parent_title": parent_title,
        "depth": depth,
        "status": status,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "has_view_html": True,
        "view_file": "body.view.html",
        "storage_file": "body.storage.xhtml",
    })
    meta.setdefault("page_id", "")
    meta.setdefault("space", "SSSS")
    meta.setdefault("version", "")
    meta.setdefault("url", "")
    meta.setdefault("children_count", 0)
    return meta


def write_page(page_dir: Path, title: str, slug: str, parent_id: str, parent_title: str, depth: int, storage: str) -> None:
    page_dir.mkdir(parents=True, exist_ok=True)
    (page_dir / "body.storage.xhtml").write_text(storage, encoding="utf-8")
    (page_dir / "body.view.html").write_text(view(title, storage), encoding="utf-8")
    write_yaml(page_dir / "page.yaml", page_meta(page_dir, title, slug, parent_id, parent_title, depth))


def list_template_storage(cfg: dict[str, Any]) -> str:
    parts: list[str] = []
    parts.append("<h2>0. Liste Hakkında</h2>")
    parts.append("<h3>0.1. Liste Üst Bilgisi</h3>")
    parts.append(table(["Alan", "Değer"], [
        ["Kurum", "İstanbul Üniversitesi - Cerrahpaşa Bilgi İşlem Daire Başkanlığı"],
        ["Doküman Kodu", cfg["code"]],
        ["Doküman Türü", "Liste / Matris Şablonu"],
        ["Kullanım Alanı", cfg["purpose"]],
        ["Durum", "Aktif"],
        ["Sürüm", "v1.0"],
        ["Yürürlük Tarihi", "15-02-2025"],
        ["Son Gözden Geçirme Tarihi", "15-02-2025"],
    ]))
    parts.append("<h3>0.2. Listenin Kullanım Amacı</h3>")
    parts.append(p(cfg["purpose"]))
    parts.append("<h3>0.3. Doküman Adlandırma Kuralı</h3>")
    parts.append(p(f"Bu şablondan üretilen gerçek dokümanlar {cfg['code'].replace('.Ş','')} - [Liste Adı] formatında adlandırılır. Sürece veya projeye özel kayıtlar için ilgili süreç/proje kodu parantez içinde gösterilir."))
    parts.append("<h3>0.4. Sürüm Geçmişi</h3>")
    parts.append(table(["Sürüm", "Tarih", "Açıklama", "Hazırlayan/Güncelleyen", "Gözden Geçiren", "Onay"], [["v0.1", "01-02-2025", "İlk taslak oluşturuldu.", "Soner DEDEOĞLU - Kalite Danışmanı", "-", "-"], ["v1.0", "15-02-2025", "Şablon onaylanarak yürürlüğe alındı.", "Soner DEDEOĞLU - Kalite Danışmanı", "Levent BAYEZİT - Dokümantasyon Süreç Sahibi", "Mustafa Nusret SARISAKAL - Bilgi İşlem Daire Başkanı"]]))
    parts.append("<h2>1. Liste Özeti</h2>")
    parts.append(table(["Alan", "Değer"], [["Liste Kodu ve Adı", "<em>Liste kodu ve adı</em>"], ["Kullanım Amacı", "<em>Listenin kullanım amacı</em>"], ["Sorumlu", "<em>Rol / birim</em>"], ["Durum", "<em>Taslak / Aktif</em>"], ["Sürüm", "<em>v1.0</em>"], ["Yürürlük Tarihi", "<em>GG-AA-YYYY</em>"]]))
    parts.append("<h2>2. Kullanım Değerleri</h2>")
    parts.append(table(["Alan", "Kullanım Kuralı"], [["Kapsam", "Listeye alınacak kayıtların kapsamı açık yazılır."], ["Kapsam Dışı", "Listeye alınmayacak kayıtlar ayrıca belirtilir."], ["Güncelleme", "Liste sorumlusu tarafından ihtiyaç halinde güncellenir."], ["Kanıt", "Liste satırları mümkünse gerçek doküman/sistem bağlantılarıyla ilişkilendirilir."]]))
    for title, headers in cfg["sections"]:
        parts.append(f"<h2>{e(title)}</h2>")
        parts.append(table(headers, [[f"<em>{e(h)}</em>" for h in headers]]))
    parts.append(f"<h2>{len(cfg['sections']) + 3}. Sürüm Geçmişi</h2>")
    parts.append(table(["Sürüm", "Tarih", "Açıklama", "Hazırlayan/Güncelleyen", "Gözden Geçiren", "Onay"], [["v0.1", "<em>GG-AA-YYYY</em>", "<em>İlk taslak</em>", "<em>Rol / kişi</em>", "<em>Rol / kişi</em>", "<em>Rol / kişi</em>"], ["v1.0", "<em>GG-AA-YYYY</em>", "<em>Onaylı sürüm</em>", "<em>Rol / kişi</em>", "<em>Rol / kişi</em>", "<em>Rol / kişi</em>"]]))
    return "".join(parts) + "\n"


def lst001_storage() -> str:
    parts: list[str] = []
    parts.append("<h2>1. Liste Özeti</h2>")
    parts.append(table(["Alan", "Değer"], [["Liste Kodu ve Adı", "LST.001 - Aktif Dokümanlar Listesi"], ["Kullanım Amacı", "Genel kullanıma açık aktif dokümanların doküman türü bazında izlenmesi"], ["Sorumlu", "Levent BAYEZİT - Dokümantasyon Süreç Sahibi"], ["Durum", "Onaylı"], ["Sürüm", "v1.0"], ["Yürürlük Tarihi", "15-02-2025"], ["Son Gözden Geçirme Tarihi", "15-02-2025"]]))
    parts.append("<h2>2. Kullanım Değerleri</h2>")
    parts.append(table(["Kural", "Açıklama"], [["Kapsam", "Bu liste genel kullanıma açık aktif süreç, prosedür, kılavuz, şablon, genel liste/kayıt, politika ve planları içerir."], ["Kapsam Dışı", "Süreçlere veya projelere özel kayıt niteliğindeki dokümanlar bu listeye alınmaz; ilgili süreç/proje altında izlenir."], ["Güncelleme", "Yeni genel doküman yayımlandığında veya aktif doküman durumu değiştiğinde güncellenir."], ["Şablon Kullanımı", "Liste, LST.001.Ş şablonuna göre düzenlenir."]]))
    parts.append("<h2>3. Süreç Dokümanları</h2>")
    parts.append(table(["Doküman Kodu", "Doküman Adı", "Süreç Referansı", "Sahibi", "Durum", "Sürüm", "Yürürlük Tarihi", "Konum"], [[code, name, ref, "İlgili Süreç Sahibi", "Aktif", "v1.0", "15-02-2025", "01 - Süreç Dokümanları"] for code, name, ref in PROCESSES]))
    parts.append("<h2>4. Prosedürler</h2>")
    parts.append(table(["Doküman Kodu", "Doküman Adı", "İlgili Süreç", "Sahibi", "Durum", "Sürüm", "Yürürlük Tarihi", "Konum"], [["PRS.001", "Yazılım Projeleri Dokümantasyon Prosedürü", "SRÇ.001", "Levent BAYEZİT - Proje Yöneticisi", "Onaylı", "v1.0", "15-02-2025", "07 - Prosedürler"]]))
    parts.append("<h2>5. Kılavuz ve Talimatlar</h2>")
    parts.append(table(["Doküman Kodu", "Doküman Adı", "İlgili Süreç / Kapsam", "Sahibi", "Durum", "Sürüm", "Yürürlük Tarihi", "Konum"], [["KLV.001", "Doküman Yazım Kuralları Talimatı", "SRÇ.001", "Proje Geliştirme Yönetimi", "Onaylı", "v1.0", "15-02-2025", "05 - Kılavuzlar"], ["KLV.002", "Süreç Uyarlama Kılavuzu", "Süreç uyarlama", "Dokümantasyon Süreç Sahibi", "Aktif", "v1.0", "15-02-2025", "05 - Kılavuzlar"], ["KLV.003", "Süreç Tasarımı Kontrol Kılavuzu", "Süreç tasarımı", "Dokümantasyon Süreç Sahibi", "Aktif", "v1.0", "15-02-2025", "05 - Kılavuzlar"], ["KLV.004", "Dokümantasyon Deposu Oluşturma Kılavuzu", "Dokümantasyon deposu", "Dokümantasyon Süreç Sahibi", "Aktif", "v1.0", "15-02-2025", "05 - Kılavuzlar"]]))
    templates = [
        ("SRÇ.XXX.Ş", "Süreç Tanımı Şablonu"), ("PRS.XXX.Ş", "Prosedür Tanımı Şablonu"), ("KLV.XXX.Ş", "Kılavuz ve Talimat Tanımı Şablonu"),
        ("FRM.001.Ş", "Süreç Gözden Geçirme Formu Şablonu"), ("LST.001.Ş", "Aktif Dokümanlar Listesi Şablonu"), ("LST.003.Ş", "Doküman Gözden Geçirme Kaydı Şablonu"), ("LST.005.Ş", "Yaşam Döngüsü Doküman Üretim Matrisi Şablonu"), ("LST.006.Ş", "Standart Süreç Envanteri Şablonu"), ("LST.007.Ş", "Süreç Etkileşim Matrisi Şablonu"), ("LST.008.Ş", "İş Ürünleri ve Kalite Kriterleri Listesi Şablonu"), ("LST.009.Ş", "Süreç Performans Ölçüm Seti Şablonu"), ("LST.010.Ş", "Süreç Rol Yetki ve RACI Matrisi Şablonu"), ("LST.011.Ş", "Repository Yapısı Şablonu"), ("LST.012.Ş", "Süreç Yaygınlaştırma ve Bilgilendirme Kaydı Şablonu"),
    ]
    parts.append("<h2>6. Şablonlar</h2>")
    parts.append(table(["Şablon Kodu", "Şablon Adı", "Kullanım Alanı", "Durum", "Sürüm", "Yürürlük Tarihi", "Konum"], [[code, name, "Doküman üretimi", "Aktif", "v1.0", "15-02-2025", "02 - Şablonlar"] for code, name in templates]))
    general_lists = [("LST.001", "Aktif Dokümanlar Listesi"), ("LST.002", "Doküman Değişiklik Kaydı"), ("LST.003", "Doküman Gözden Geçirme Kaydı"), ("LST.005", "Yaşam Döngüsü Doküman Üretim Matrisi"), ("LST.006", "Standart Süreç Envanteri"), ("LST.007", "Süreç Mimari ve Etkileşim Matrisi"), ("LST.011", "Repository Yapısı"), ("LST.012", "Süreç Yaygınlaştırma ve Bilgilendirme Kaydı")]
    parts.append("<h2>7. Genel Kayıt ve Listeler</h2>")
    parts.append(table(["Doküman Kodu", "Doküman Adı", "Kullanım Alanı", "Sorumlu", "Durum", "Sürüm", "Konum"], [[code, name, "Genel dokümantasyon yönetimi", "Dokümantasyon Süreç Sahibi", "Aktif", "v1.0", "03 - Kayıtlar ve Listeler"] for code, name in general_lists]))
    parts.append("<h2>8. Politikalar</h2>")
    parts.append(table(["Doküman Kodu", "Doküman Adı", "Kapsam", "Sahibi", "Durum", "Sürüm", "Konum"], [["-", "Henüz tanımlı genel politika yok", "-", "-", "-", "-", "06 - Politikalar"]]))
    parts.append("<h2>9. Planlar</h2>")
    parts.append(table(["Doküman Kodu", "Doküman Adı", "Kapsam", "Sahibi", "Durum", "Sürüm", "Konum"], [["-", "Henüz tanımlı genel plan yok", "-", "-", "-", "-", "08 - Planlar"]]))
    parts.append("<h2>10. Kapsam Dışı Dokümanlar</h2>")
    parts.append(table(["Doküman / Kayıt Grubu", "Kapsam Dışı Bırakma Nedeni", "Nerede İzlenir?"], [["Sürece özel LST.007 / LST.008 / LST.009 / LST.010 kayıtları", "Bu kayıtlar ilgili sürecin uygulama kanıtıdır; genel aktif doküman envanteri değildir.", "İlgili süreç sayfası altında"], ["Sürece özel FRM.001 gözden geçirme formları", "Süreç değerlendirme/gözden geçirme kaydıdır.", "İlgili süreç sayfası altında"], ["Proje özel doküman ve kayıtları", "Proje kanıtı olarak yönetilir; genel doküman listesine alınmaz.", "İlgili proje alanı / Soru Bankası Projesi sayfası altında"]]))
    parts.append("<h2>11. Sürüm Geçmişi</h2>")
    parts.append(table(["Sürüm", "Tarih", "Açıklama", "Hazırlayan/Güncelleyen", "Gözden Geçiren", "Onay"], [["v0.1", "01-02-2025", "İlk taslak oluşturuldu.", "Soner DEDEOĞLU - Kalite Danışmanı", "Levent BAYEZİT - Dokümantasyon Süreç Sahibi", "-"], ["v1.0", "15-02-2025", "Liste onaylanarak yürürlüğe alındı.", "Soner DEDEOĞLU - Kalite Danışmanı", "Levent BAYEZİT - Dokümantasyon Süreç Sahibi", "Mustafa Nusret SARISAKAL - Bilgi İşlem Daire Başkanı"]]))
    return "".join(parts) + "\n"


def sb_project_storage() -> str:
    return "".join(["<h2>1. Sayfa Amacı</h2>", p("Bu sayfa, Soru Bankası Projesi kapsamında üretilecek proje özel doküman ve kayıtların düzenlenmesi için oluşturulmuştur. Genel aktif doküman envanterine alınmayan proje özel kayıtlar bu alan altında izlenir."), "<h2>2. Kapsam</h2>", p("İlk aşamada LST.005 - Yaşam Döngüsü Doküman Üretim Matrisi (SB) taslak kaydı bu sayfa altında tutulacaktır.")]) + "\n"


def sb_lst005_storage() -> str:
    rows = [
        ["Talep / Başlangıç", "Proje talep kaydı, ön kapsam notu", "Zorunlu", "Jira / Confluence", "Proje Yöneticisi", "Proje Yöneticisi", "Taslak - gerçek proje kayıtlarıyla güncellenecek"],
        ["Planlama", "Proje planı, sprint/iş planı, risk listesi", "Zorunlu", "Confluence / Jira", "Proje Yöneticisi", "Proje Yöneticisi / Yönetim", "Taslak"],
        ["Analiz", "Gereksinim kaydı, kullanıcı hikayeleri, iş kuralları", "Zorunlu", "Jira / Confluence", "Analist", "Proje Yöneticisi / İş Birimi", "Taslak"],
        ["Tasarım", "Tasarım notu, veri modeli, mimari karar", "Koşullu", "Confluence / Bitbucket", "Teknik Ekip", "Teknik Sorumlu", "Taslak"],
        ["Geliştirme", "Commit, branch, pull request, code review", "Zorunlu / Kayıt", "Bitbucket / Jira", "Geliştirici", "Teknik Sorumlu", "Taslak"],
        ["Test", "Test senaryosu, test sonucu, hata kaydı", "Zorunlu", "Jira / Confluence", "Test Sorumlusu", "Proje Yöneticisi", "Taslak"],
        ["Yayına Alma", "Yayın planı, sürüm notu, deploy kaydı", "Zorunlu", "Confluence / Bamboo / Jira", "Proje Yöneticisi / Operasyon", "Proje Yöneticisi", "Taslak"],
        ["Bakım", "Bakım, destek ve değişiklik kayıtları", "Koşullu / Kayıt", "Jira / Confluence", "Proje Ekibi", "Süreç Sahibi", "Taslak"],
    ]
    return "".join(["<h2>1. Liste Özeti</h2>", table(["Alan", "Değer"], [["Liste Kodu ve Adı", "LST.005 - Yaşam Döngüsü Doküman Üretim Matrisi (SB)"], ["Proje", "Soru Bankası Projesi"], ["Kullanım Amacı", "Soru Bankası Projesi yaşam döngüsünde beklenen doküman ve kayıtları izlemek"], ["Durum", "Taslak"], ["Sürüm", "v0.1"], ["Tarih", "15-02-2025"]]), "<h2>2. Kullanım Değerleri</h2>", table(["Alan", "Değer"], [["Şablon", "LST.005.Ş - Yaşam Döngüsü Doküman Üretim Matrisi Şablonu"], ["Not", "Bu doküman taslak içeriklidir. Gerçek Soru Bankası Projesi kanıtlarıyla daha sonra güncellenecektir."], ["Kapsam", "Proje özel doküman ve kayıt ihtiyacı"]]), "<h2>3. Yaşam Döngüsü Doküman Üretim Matrisi</h2>", table(["Yaşam Döngüsü Aşaması", "Beklenen Doküman / Kayıt", "Zorunluluk", "Kaynak Sistem / Yayın Ortamı", "Sorumlu Rol", "Gözden Geçirme / Onay", "Not"], rows), "<h2>4. Sürüm Geçmişi</h2>", table(["Sürüm", "Tarih", "Açıklama", "Hazırlayan/Güncelleyen", "Gözden Geçiren", "Onay"], [["v0.1", "15-02-2025", "Taslak matris oluşturuldu.", "Soner DEDEOĞLU - Kalite Danışmanı", "-", "-"]])]) + "\n"


def update_refs(path: Path) -> None:
    for filename in ("body.storage.xhtml", "body.view.html"):
        pth = path / filename
        if not pth.exists():
            continue
        text = pth.read_text(encoding="utf-8")
        text = text.replace("LST.005 - Yaşam Döngüsü Doküman İhtiyaç Matrisi", "LST.005.Ş - Yaşam Döngüsü Doküman Üretim Matrisi Şablonu")
        text = text.replace("LST.005 - Yaşam Döngüsü Doküman Üretim Matrisi", "LST.005.Ş - Yaşam Döngüsü Doküman Üretim Matrisi Şablonu")
        text = text.replace("Yaşam Döngüsü Doküman İhtiyaç Matrisi", "Yaşam Döngüsü Doküman Üretim Matrisi Şablonu")
        pth.write_text(text, encoding="utf-8")


def update_index(page_dirs: list[Path]) -> None:
    index = load_yaml(INDEX_PATH)
    pages = index.setdefault("pages", [])
    rels = {str(p.relative_to(CONFLUENCE_DIR)).replace("\\", "/") for p in page_dirs}
    pages[:] = [p for p in pages if p.get("relative_path") not in rels]
    for page_dir in page_dirs:
        meta = load_yaml(page_dir / "page.yaml")
        rel = meta["relative_path"]
        pages.append({"page_id": str(meta.get("page_id") or ""), "title": meta["title"], "parent_id": str(meta.get("parent_id") or ""), "depth": meta.get("depth", 2), "relative_path": rel, "slug": meta["slug"], "storage_file": f"{rel}/body.storage.xhtml", "view_file": f"{rel}/body.view.html"})
    index["total_page_count"] = len(pages)
    write_yaml(INDEX_PATH, index)


def main() -> None:
    changed: list[Path] = []
    for cfg in LST_TEMPLATES:
        page_dir = TEMPLATES / cfg["slug"]
        write_page(page_dir, cfg["title"], cfg["slug"], TEMPLATE_PARENT_ID, TEMPLATE_PARENT_TITLE, 2, list_template_storage(cfg))
        changed.append(page_dir)
        print(f"[TEMPLATE] {cfg['title']}")

    lst001_dir = RECORDS / "lst-001-aktif-dokumanlar-listesi"
    write_page(lst001_dir, "LST.001 - Aktif Dokümanlar Listesi", "lst-001-aktif-dokumanlar-listesi", RECORDS_PARENT_ID, RECORDS_PARENT_TITLE, 2, lst001_storage())
    changed.append(lst001_dir)

    sb_dir = RECORDS / "soru-bankasi-projesi"
    write_page(sb_dir, "Soru Bankası Projesi", "soru-bankasi-projesi", RECORDS_PARENT_ID, RECORDS_PARENT_TITLE, 2, sb_project_storage())
    changed.append(sb_dir)
    sb_pid = load_yaml(sb_dir / "page.yaml").get("page_id", "")
    sb_lst005_dir = sb_dir / "lst-005-yasam-dongusu-dokuman-uretim-matrisi-sb"
    write_page(sb_lst005_dir, "LST.005 - Yaşam Döngüsü Doküman Üretim Matrisi (SB)", "lst-005-yasam-dongusu-dokuman-uretim-matrisi-sb", str(sb_pid), "Soru Bankası Projesi", 3, sb_lst005_storage())
    changed.append(sb_lst005_dir)

    update_refs(SRC001)
    update_refs(PRS001)
    changed.extend([SRC001, PRS001])
    update_index(changed)
    print("[DONE] Package 3 LST templates, LST.001, SB LST.005 draft and references generated.")


if __name__ == "__main__":
    main()
