#!/usr/bin/env python3
"""Align SRÇ.004 support guides and lists with the active templates."""
from __future__ import annotations

import math
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from create_lst007_template_and_src001_matrix import (
    SRC001_EDGES,
    SRC001_NODES,
    mermaid,
    render_fallback_png,
    write_mermaid,
)
from create_src001_review_assessment_1 import clean, parse_table
from rework_src004_work_products_quality import CSS, e, t, table


ROOT = Path(__file__).resolve().parents[1]
CONFLUENCE = ROOT / "confluence"
INDEX_PATH = CONFLUENCE / "index.yaml"
PAGE_ROOT_REL = "pages/000-root-iuc-bidb-spice-2026-level-3"
PAGE_ROOT = CONFLUENCE / PAGE_ROOT_REL

SRC004_ID = "137265862"
SRC004_TITLE = "SRÇ.004 - Süreç Kurulumu Süreci"
SRC004_REL = f"{PAGE_ROOT_REL}/01-surec-dokumanlari/src-004-surec-kurulumu-sureci"

GUIDES_ID = "137265788"
GUIDES_TITLE = "05 - Kılavuzlar"
KLV002_TITLE = "KLV.002 - Süreç Uyarlama Kılavuzu"
KLV003_TITLE = "KLV.003 - Süreç Tasarımı Kontrol Kılavuzu"
KLV002_REL = f"{PAGE_ROOT_REL}/05-kilavuzlar/klv-002-surec-uyarlama-kilavuzu"
KLV003_REL = f"{PAGE_ROOT_REL}/05-kilavuzlar/klv-003-surec-tasarimi-kontrol-kilavuzu"

LISTS_ID = "137265786"
LISTS_TITLE = "03 - Kayıtlar ve Listeler"
LST006_TITLE = "LST.006 - Standart Süreç Envanteri"
LST006_REL = f"{PAGE_ROOT_REL}/03-kayitlar-ve-listeler/lst-006-standart-surec-envanteri"

LST007_TITLE = "LST.007 - Süreç Etkileşim Matrisi (SRÇ.004)"
LST007_SLUG = "lst-007-surec-etkilesim-matrisi-src-004"
LST007_REL = f"{SRC004_REL}/{LST007_SLUG}"
LST007_PNG = "src004-surec-etkilesim.png"
LST007_MMD = "src004-surec-etkilesim.mmd"

SRC001_ID = "137265842"
SRC001_TITLE = "SRÇ.001 - Dokümantasyon Süreci"
SRC001_REL = f"{PAGE_ROOT_REL}/01-surec-dokumanlari/src-001-dokumantasyon-sureci"
SRC001_LST007_TITLE = "LST.007 - Süreç Etkileşim Matrisi (SRÇ.001)"
SRC001_LST007_REL = f"{SRC001_REL}/lst-007-surec-etkilesim-matrisi-src-001"
SRC001_LST007_PNG = "src001-surec-etkilesim.png"
SRC001_LST007_MMD = "src001-surec-etkilesim.mmd"

REMOVED_RELS = {
    f"{PAGE_ROOT_REL}/91-ic-denetimler/surec-gozden-gecirmeleri/lst-004-surec-gozden-gecirme-matrisi-src-001",
    f"{PAGE_ROOT_REL}/91-ic-denetimler/surec-gozden-gecirmeleri/lst-004-surec-gozden-gecirme-matrisi-src-004",
    f"{PAGE_ROOT_REL}/03-kayitlar-ve-listeler/lst-007-surec-mimari-ve-etkilesim-matrisi",
}

PREPARED_BY = "Soner DEDEOĞLU - Kalite Danışmanı"
REVIEWED_BY = "Levent Bayezit - Proje Yöneticisi"
APPROVED_BY = "Mustafa Nusret SARISAKAL - Bilgi İşlem Daire Başkanı"
PROCESS_OWNER = APPROVED_BY

SRC001 = "SRÇ.001 - Dokümantasyon Süreci"
SRC005 = "SRÇ.005 - Süreç Değerlendirme Süreci"
SRC006 = "SRÇ.006 - Süreç İyileştirme Süreci"
SRC018 = "SRÇ.018 - Değişiklik Talebi Yönetimi Süreci"
SRC020 = "SRÇ.020 - Eğitim Süreci"
SRC025 = "SRÇ.025 - Ölçüm Süreci"
SRC_TEMPLATE = "SRÇ.XXX.Ş - Süreç Tanımı Şablonu"
PRS002 = "PRS.002 - Süreç Tasarım Prosedürü"
LST001 = "LST.001 - Aktif Dokümanlar Listesi"
LST008 = "LST.008 - İş Ürünleri ve Kalite Kriterleri Listesi (SRÇ.004)"
LST009 = "LST.009 - Süreç Performans Ölçüm Seti (SRÇ.004)"
LST010 = "LST.010 - Süreç Rol Yetki ve RACI Matrisi (SRÇ.004)"
LST012 = "LST.012 - Süreç Yaygınlaştırma ve Bilgilendirme Kaydı"
FRM001 = "FRM.001 - Süreç Gözden Geçirme Formu (SRÇ.004)"

REPORT = ROOT / "reports/src004_support_package_alignment_report.md"


def p(value: str) -> str:
    return f"<p>{e(value)}</p>"


def build_view(title: str, body: str) -> str:
    css = CSS + ".diagram{max-width:100%;height:auto;border:1px solid #c9d1d9;border-radius:6px;margin:16px 0}pre{background:#f6f8fa;padding:12px 16px;border-radius:6px;overflow:auto}"
    return f"""<!doctype html>
<html lang="tr"><head><meta charset="utf-8"><title>{e(title)}</title><style>{css}</style></head>
<body><main class="confluence-page"><h1>{e(title)}</h1>{body}</main></body></html>
"""


def page_metadata(page_dir: Path, title: str, slug: str, parent_id: str, parent_title: str, depth: int) -> dict[str, Any]:
    meta_path = page_dir / "page.yaml"
    existing = yaml.safe_load(meta_path.read_text(encoding="utf-8")) or {} if meta_path.exists() else {}
    rel = str(page_dir.relative_to(CONFLUENCE)).replace("\\", "/")
    existing.update({
        "space": "SSSS",
        "title": title,
        "parent_id": parent_id,
        "parent_title": parent_title,
        "depth": depth,
        "status": "active",
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "children_count": 0,
        "relative_path": rel,
        "slug": slug,
        "has_view_html": True,
        "view_file": "body.view.html",
        "storage_file": "body.storage.xhtml",
    })
    existing.setdefault("page_id", "")
    existing.setdefault("version", "")
    existing.setdefault("url", "")
    return existing


def write_page(page_dir: Path, title: str, slug: str, parent_id: str, parent_title: str, depth: int, storage: str, view_body: str | None = None) -> None:
    page_dir.mkdir(parents=True, exist_ok=True)
    (page_dir / "body.storage.xhtml").write_text(storage, encoding="utf-8")
    (page_dir / "body.view.html").write_text(build_view(title, view_body if view_body is not None else storage), encoding="utf-8")
    meta = page_metadata(page_dir, title, slug, parent_id, parent_title, depth)
    (page_dir / "page.yaml").write_text(yaml.safe_dump(meta, allow_unicode=True, sort_keys=False), encoding="utf-8")


def upsert_index(page_dirs: list[Path]) -> None:
    index = yaml.safe_load(INDEX_PATH.read_text(encoding="utf-8")) or {}
    pages = index.setdefault("pages", [])
    rels = {str(page_dir.relative_to(CONFLUENCE)).replace("\\", "/") for page_dir in page_dirs}
    pages[:] = [page for page in pages if page.get("relative_path") not in rels | REMOVED_RELS]
    for page_dir in page_dirs:
        meta = yaml.safe_load((page_dir / "page.yaml").read_text(encoding="utf-8")) or {}
        rel = meta["relative_path"]
        pages.append({
            "page_id": str(meta.get("page_id") or ""),
            "title": meta["title"],
            "parent_id": str(meta.get("parent_id") or ""),
            "depth": meta["depth"],
            "relative_path": rel,
            "slug": meta["slug"],
            "storage_file": f"{rel}/body.storage.xhtml",
            "view_file": f"{rel}/body.view.html",
        })

    def reorder_children(parent_id: str, rank: dict[str, int]) -> None:
        positions = [i for i, page in enumerate(pages) if str(page.get("parent_id") or "") == parent_id]
        ordered = sorted(
            (pages[i] for i in positions),
            key=lambda page: (rank.get(str(page.get("title") or ""), 999), str(page.get("title") or "")),
        )
        for position, page in zip(positions, ordered):
            pages[position] = page

    reorder_children(SRC004_ID, {
        FRM001: 1,
        LST007_TITLE: 2,
        LST008: 3,
        LST009: 4,
        LST010: 5,
    })
    index["total_page_count"] = len(pages)
    INDEX_PATH.write_text(yaml.safe_dump(index, allow_unicode=True, sort_keys=False), encoding="utf-8")

    parent_dirs = [
        PAGE_ROOT / "03-kayitlar-ve-listeler",
        PAGE_ROOT / "91-ic-denetimler/surec-gozden-gecirmeleri",
        CONFLUENCE / SRC004_REL,
    ]
    for parent_dir in parent_dirs:
        meta_path = parent_dir / "page.yaml"
        if not meta_path.exists():
            continue
        meta = yaml.safe_load(meta_path.read_text(encoding="utf-8")) or {}
        parent_page_id = str(meta.get("page_id") or "")
        meta["children_count"] = sum(1 for page in pages if str(page.get("parent_id") or "") == parent_page_id)
        meta_path.write_text(yaml.safe_dump(meta, allow_unicode=True, sort_keys=False), encoding="utf-8")


def remove_legacy_pages() -> None:
    for rel in sorted(REMOVED_RELS):
        page_dir = CONFLUENCE / rel
        if page_dir.exists():
            shutil.rmtree(page_dir)
            print(f"[REMOVED] {page_dir.relative_to(ROOT)}")


def guide_info(title: str, reference: str) -> str:
    return table(["Alan", "Değer"], [
        [t("Kurum"), t("İstanbul Üniversitesi - Cerrahpaşa Bilgi İşlem Daire Başkanlığı")],
        [t("Kılavuz / Talimat Kodu ve Adı"), t(title)],
        [t("Kılavuz / Talimat Referansı"), t(reference)],
        [t("Kılavuz / Talimat Sahibi"), t(PROCESS_OWNER)],
        [t("Durum"), t("Aktif")],
        [t("Sürüm"), t("v1.0")],
        [t("Yürürlük Tarihi"), t("15-02-2025")],
        [t("Son Gözden Geçirme Tarihi"), t("15-02-2025")],
    ])


def guide_history(name: str) -> str:
    return table(
        ["Sürüm", "Tarih", "Açıklama", "Hazırlayan/Güncelleyen", "Gözden Geçiren", "Onay"],
        [
            [t("v0.1"), t("10-01-2025"), t("İlk taslak oluşturuldu."), t(PREPARED_BY), t("-"), t("-")],
            [t("v1.0"), t("15-02-2025"), t(f"{name} onaylanarak yürürlüğe alınmıştır."), t(PREPARED_BY), t(REVIEWED_BY), t(APPROVED_BY)],
        ],
    )


def klv002_body() -> str:
    parts = ["<h2>1. Kılavuz / Talimat Bilgileri</h2>", guide_info(KLV002_TITLE, f"{SRC004_TITLE}; ISO/IEC 15504-5:2006 PIM.1.BP5")]
    parts += [
        "<h2>2. Amaç</h2>",
        p("Standart süreçlerin amaç ve zorunlu sonuçları korunarak proje, ürün, hizmet veya organizasyonel bağlama göre hangi sınırlar içinde uyarlanabileceğini; uyarlama etkisinin nasıl değerlendirileceğini ve kararların nasıl izleneceğini tanımlamaktır."),
        "<h2>3. Kapsam</h2>",
        p("İÜC BİDB standart süreç setindeki süreçlerin faaliyet ayrıntısı, yöntem, görev dağılımı, uygulama sırası, iş ürünü biçimi, araç kullanımı ve koşullu kontrollerine ilişkin uyarlamaları kapsar."),
        "<h2>4. Kapsam Dışı</h2>",
        p("Süreç amacının veya zorunlu sonuçlarının kaldırılması, yetkisiz süreç kapsamı değişiklikleri, ayrı bir uyarlama/değişiklik formu oluşturulması ve proje ekiplerinin kayıt dışı kişisel çalışma tercihleri bu kılavuzun kapsamı dışındadır."),
        "<h2>5. Referanslar</h2>",
        table(["Referans", "Açıklama"], [
            [t("ISO/IEC 15504-5:2006 PIM.1.BP5 - Establish tailoring guidelines"), t("Uyarlama stratejisi ve sınırları için temel standart beklentisi")],
            [t(SRC004_TITLE), t("Uyarlama kılavuzunun üretildiği ve sürdürüldüğü ana süreç")],
            [t(PRS002), t("Süreç tasarım paketinin hazırlanması ve kontrol kapıları")],
            [t(SRC_TEMPLATE), t("Uyarlanan süreç tanımında korunacak güncel bölüm yapısı")],
            [t(SRC018), t("Tüm değişiklik ve taleplerin tekil olarak yönetildiği süreç")],
            [t(LST007_TITLE), t("Uyarlamanın süreç etkileşimlerine etkisini gösteren süreç özel kayıt")],
            [t(LST008), t("İş ürünleri ve kalite kriterleri üzerindeki etkinin kontrolü")],
            [t(LST010), t("Rol, yetki ve RACI etkisinin kontrolü")],
        ]),
        "<h2>6. Terimler ve Kısaltmalar</h2>",
        table(["Terim / Kısaltma", "Açıklama"], [
            [t("Süreç uyarlama"), t("Standart sürecin amacı ve zorunlu sonuçları korunarak belirli bir kullanım bağlamına göre kontrollü biçimde özelleştirilmesi")],
            [t("Uyarlama sınırı"), t("Uyarlanabilen alan ile değiştirilmesi veya kaldırılması yasak olan zorunlu alan arasındaki sınır")],
            [t("Uygulanabilirlik"), t("Bir süreç veya kontrolün belirli proje, ürün, hizmet ya da organizasyonel bağlamda kullanılıp kullanılmayacağı")],
            [t("Tanımlı süreç"), t("Standart süreçten seçilen veya uyarlanan ve belirli bağlamda uygulanmak üzere devreye alınan süreç")],
        ]),
        "<h2>7. Genel İlkeler</h2>",
        table(["İlke", "Açıklama"], [
            [t("Amaç ve sonuçlar korunur"), t("Uyarlama, süreç amacını veya zorunlu süreç sonuçlarını ortadan kaldıramaz.")],
            [t("Riskle orantılılık"), t("Uyarlama derecesi kullanım bağlamının büyüklüğü, riskleri, karmaşıklığı ve mevzuat/kurum gereksinimleriyle orantılıdır.")],
            [t("Kanıt korunur"), t("Denetim, izlenebilirlik, onay, ölçüm ve kalite kanıtı üreten kontroller gerekçesiz kaldırılamaz.")],
            [t("Etki birlikte değerlendirilir"), t("Faaliyet, iş ürünü, rol, ölçüm, araç ve süreç etkileşimleri birlikte ele alınır.")],
            [t("Tek değişiklik yolu"), t(f"Uyarlama nedeniyle oluşan değişiklik ve talepler yalnızca {SRC018} kapsamında yönetilir; ayrı form oluşturulmaz.")],
        ]),
        "<h2>8. Kural ve Uygulama Alanları</h2>",
        table(["Kural / Alan", "Açıklama", "Örnek", "Not"], [
            [t("Faaliyet ayrıntısı"), t("Faaliyetin alt adımları bağlama göre birleştirilebilir veya ayrıştırılabilir."), t("Küçük kapsamlı çalışmada iki ardışık kontrolün aynı toplantıda yürütülmesi"), t("Sorumluluk ve kanıt kaybolamaz.")],
            [t("Yöntem ve araç"), t("Aynı amacı ve izlenebilirliği sağlayan kurumsal araç/yöntem seçilebilir."), t("Kayıtların Jira veya uygun kurumsal sistemde tutulması"), t("Erişim ve saklama kuralları korunur.")],
            [t("Rol ataması"), t("Bir kişi birden fazla rolü üstlenebilir; hesap veren ve gerekli bağımsız gözden geçiren ayrımı korunur."), t("Süreç Mimarı ile Doküman Sorumlusunun aynı kişi olması"), t("Yetki çatışması kontrol edilir.")],
            [t("İş ürünü biçimi"), t("İçerik ve kalite kriterleri korunarak biçim veya saklama ortamı değiştirilebilir."), t("Ayrı dosya yerine kontrollü Confluence tablosu"), t("Aktif şablon alanları karşılanır.")],
            [t("Kapsam dışı kararı"), t("Yalnızca bağlamda uygulanmayan koşullu öğeler gerekçeli biçimde kapsam dışı bırakılabilir."), t("Eğitim ihtiyacı oluşmadığında eğitim kaydı beklenmemesi"), t(f"Gerekli değişiklik {SRC018} kapsamında izlenir.")],
        ]),
        "<h2>9. Uygulama Adımları / Talimatlar</h2>",
        table(["Adım", "Talimat / Uygulama Adımı", "Açıklama", "Örnek / Kanıt"], [
            [t("1"), t("Kullanım bağlamını belirle"), t("Kapsam, hedef, risk, karmaşıklık, paydaş, mevzuat ve kurumsal kısıtları belirle."), t("Proje/hizmet kapsamı ve risk kaydı")],
            [t("2"), t("Zorunlu öğeleri ayır"), t("Süreç amacı, sonuçları, zorunlu faaliyet ve kanıtları uyarlanabilir öğelerden ayır."), t(f"{SRC004_TITLE}; ilgili standart süreç bölümü")],
            [t("3"), t("Uyarlama etkisini değerlendir"), t("Faaliyet, iş ürünü, rol, ölçüm, araç, etkileşim ve yetki etkisini birlikte incele."), t(f"{LST007_TITLE}; {LST008}; {LST009}; {LST010}")],
            [t("4"), t("Karar ve onayı yönet"), t(f"Değişiklik veya talep niteliğindeki uyarlamayı {SRC018} kapsamında yetkili karara bağla."), t("SRÇ.018 talep, karar ve onay kaydı")],
            [t("5"), t("Tanımlı süreci güncelle"), t("Onaylanan uyarlamayı ilgili süreç dokümanı ve süreç özel kayıtlarına yansıt."), t(f"{SRC_TEMPLATE}; süreç özel LST kayıtları")],
            [t("6"), t("Uygulamayı ve kanıtı doğrula"), t("Uyarlanan sürecin amacını, sonuçlarını, sorumluluklarını ve izlenebilirliğini koruduğunu kontrol et."), t(f"{FRM001} veya numaralandırılmış değerlendirme kaydı")],
        ]),
        "<h2>10. Örnekler ve Formatlar</h2>",
        table(["Örnek Alanı", "Kullanım", "Örnek", "Açıklama"], [
            [t("Uyarlanabilir"), t("Faaliyet sırası"), t("Aynı kontrol çevrimindeki iki faaliyetin tek oturumda yürütülmesi"), t("Her iki faaliyetin çıktısı ve sorumlusu kayıtlı kalır.")],
            [t("Uyarlanabilir"), t("Kayıt ortamı"), t("Ayrı belge yerine yetkili Jira/Confluence kaydı"), t("Zorunlu alanlar, erişim ve geçmiş korunur.")],
            [t("Uyarlanamaz"), t("Süreç sonucu"), t("Zorunlu bir süreç sonucunun kaldırılması"), t("Standart süreç uyarlaması değildir; kapsam değişikliği ve yetkili karar gerektirir.")],
            [t("Uyarlanamaz"), t("Onay/kanıt"), t("Gözden geçirme veya onay kaydının tamamen kaldırılması"), t("Denetim ve izlenebilirlik gereksinimini ihlal eder.")],
        ]),
        "<h2>11. Kontrol ve Gözden Geçirme Kuralları</h2>",
        table(["Kontrol Alanı", "Kontrol Yöntemi", "Sıklık", "Sorumlu", "Kayıt / Kanıt"], [
            [t("Amaç ve sonuçların korunması"), t("Standart süreç ve tanımlı süreç karşılaştırması"), t("Her uyarlamada"), t("Süreç Sahibi / Süreç Mimarı"), t("SRÇ.018 kararı ve güncel süreç tanımı")],
            [t("Etkileşim ve iş ürünü etkisi"), t("LST.007-LST.010 çapraz kontrolü"), t("Her uyarlamada"), t("Süreç Mimarı / İlgili Süreç Sahibi"), t("Güncellenen süreç özel kayıtlar")],
            [t("Uygulama uygunluğu"), t("FRM.001 ile BP/PA-GP kanıt kontrolü"), t("Uyarlama sonrası ve planlı gözden geçirmede"), t("Gözden Geçiren"), t("Numaralandırılmış FRM.001 değerlendirme kaydı")],
            [t("Kılavuz güncelliği"), t("Şablon, standart ve süreç değişikliklerinin kontrolü"), t("Yılda en az bir kez ve değişiklikte"), t("SRÇ.004 Süreç Sahibi"), t("Sürüm geçmişi ve gözden geçirme kaydı")],
        ]),
        "<h2>12. Kayıtlar ve Kanıtlar</h2>",
        table(["Kayıt / Kanıt", "Kullanım Amacı", "Saklama Yeri", "Sorumlu", "Not"], [
            [t("SRÇ.018 talep ve karar kaydı"), t("Uyarlama gerekçesi, etki, karar ve onayı izlemek"), t("SRÇ.018 için tanımlı doğal kaynak sistem"), t("Değişiklik Yöneticisi / Süreç Sahibi"), t("Ayrı uyarlama formu oluşturulmaz.")],
            [t("Güncellenmiş süreç tanımı"), t("Onaylanan tanımlı süreci yürürlükte tutmak"), t("İlgili süreç alt sayfası / Confluence"), t("İlgili Süreç Sahibi"), t(f"{SRC_TEMPLATE} yapısı korunur.")],
            [t("Süreç özel LST.007-LST.010 kayıtları"), t("Etkileşim, iş ürünü, ölçüm ve rol etkisini göstermek"), t("İlgili süreç alt sayfası / Confluence"), t("Süreç Mimarı / İlgili Sorumlular"), t("Yalnızca etkilenen kayıtlar güncellenir.")],
            [t("Numaralandırılmış FRM.001 değerlendirmesi"), t("Uyarlama sonrası uygunluğu ve açıkları göstermek"), t("91 - İç Denetimler / Süreç Gözden Geçirmeleri"), t("Gözden Geçiren"), t("Boş form süreç altında kalır.")],
        ]),
        "<h2>13. Sürüm Geçmişi</h2>", guide_history("Süreç Uyarlama Kılavuzu"),
    ]
    return "".join(parts) + "\n"


def klv003_body() -> str:
    parts = ["<h2>1. Kılavuz / Talimat Bilgileri</h2>", guide_info(KLV003_TITLE, f"{SRC004_TITLE}; {PRS002}")]
    parts += [
        "<h2>2. Amaç</h2>",
        p("Yeni veya güncellenen süreç tasarım paketlerinin güncel şablonlara, ISO/IEC 15504-5 beklentilerine, kurumsal adlandırma ve yerleşim kurallarına uygunluğunu yayın öncesinde sistematik olarak kontrol etmektir."),
        "<h2>3. Kapsam</h2>",
        p("Süreç kimliği ve kapsamından başlayarak süreç tanımı, süreç özel LST.007-LST.010 kayıtları, süreç altında tutulan boş FRM.001, İç Denetimler altında tutulan numaralandırılmış değerlendirmeler, Mermaid kaynak/PNG görselleri, rol-onay bilgileri ve repository yerleşimini kapsar."),
        "<h2>4. Kapsam Dışı</h2>",
        p("Süreçlerin günlük operasyonel yürütümü, gerçek uygulama verisi oluşmadan performans sonucu üretilmesi, değerlendirme puanının kanıtsız yükseltilmesi ve aktif Şablonlar sayfası dışında kalan arşiv şablonlarının kullanılması kapsam dışıdır."),
        "<h2>5. Referanslar</h2>",
        table(["Referans", "Açıklama"], [
            [t(SRC004_TITLE), t("Süreç tasarım ve bakım faaliyetlerinin ana süreci")],
            [t(PRS002), t("Tasarım adımları, kontrol kapıları ve sorumluluklar")],
            [t(SRC_TEMPLATE), t("Süreç tanımının güncel zorunlu bölüm yapısı")],
            [t(LST006_TITLE), t("Standart süreç kimliği, kurumsal kod, ad, sahiplik ve durum kontrolü")],
            [t(LST007_TITLE), t("SRÇ.004 girdi ve çıktı etkileşimlerinin süreç özel kaydı")],
            [t(LST008), t("Girdi/çıktı iş ürünleri ve kalite kriterleri")],
            [t(LST009), t("Az sayıda, üretilebilir performans ölçümü")],
            [t(LST010), t("Rol, yetki, yetkinlik ve RACI kayıtları")],
            [t(FRM001), t("Süreç altında saklanan yeniden kullanılabilir boş değerlendirme formu")],
            [t(SRC018), t("Kontrol bulgularından doğan tüm değişiklik ve taleplerin yönetimi")],
        ]),
        "<h2>6. Terimler ve Kısaltmalar</h2>",
        table(["Terim / Kısaltma", "Açıklama"], [
            [t("Süreç tasarım paketi"), t("SRÇ süreç tanımı ile süreç özel LST.007, LST.008, LST.009, LST.010 ve boş FRM.001 bütünüdür.")],
            [t("Kontrol kapısı"), t("Bir sonraki tasarım/yayın adımına geçmeden önce karşılanması gereken zorunlu doğrulama noktasıdır.")],
            [t("Boş FRM.001"), t("İlgili sürecin altında saklanan ve yeni değerlendirme başlatmak için kullanılan doldurulmamış formdur.")],
            [t("Numaralandırılmış değerlendirme"), t("91 - İç Denetimler / Süreç Gözden Geçirmeleri altında Değerlendirme #n adıyla saklanan doldurulmuş FRM.001 kaydıdır.")],
            [t("Aktif şablon"), t("02 - Şablonlar altında arşiv işareti taşımayan güncel doküman şablonudur.")],
        ]),
        "<h2>7. Genel İlkeler</h2>",
        table(["İlke", "Açıklama"], [
            [t("Aktif şablon tek kaynaktır"), t("Doküman adı, bölüm yapısı ve tablo başlıkları Şablonlar sayfasındaki aktif örnekten alınır.")],
            [t("Sabit süreç sayısı kullanılmaz"), t(f"Kapsam güncel {LST006_TITLE} üzerinden belirlenir; prosedür, kılavuz veya süreç metninde sabit toplam yazılmaz.")],
            [t("Tam ad kullanılır"), t("Doküman ve süreç referanslarında kodla birlikte güncel tam ad yazılır.")],
            [t("Kanıt uydurulmaz"), t("Yayın, duyuru, ölçüm, eğitim veya kullanım verisi oluşmadan tamamlanmış gibi gösterilmez.")],
            [t("Form ve kayıt ayrılır"), t("Boş FRM.001 süreç altında; doldurulmuş ve numaralandırılmış değerlendirmeler İç Denetimler altında tutulur.")],
            [t("Az sayıda ölçüm"), t("LST.009 yalnızca düzenli üretilebilen ve karar almaya yarayan sınırlı ölçümleri içerir.")],
            [t("Tek değişiklik yolu"), t(f"Kontrol bulgularından doğan değişiklik ve talepler {SRC018} kapsamında yönetilir.")],
        ]),
        "<h2>8. Kural ve Uygulama Alanları</h2>",
        table(["Kural / Alan", "Açıklama", "Örnek", "Not"], [
            [t("Sayfa yerleşimi"), t("Süreç tanımı ve süreç özel kayıtlar ilgili SRÇ sayfasının altında tutulur."), t("SRÇ.004 altında LST.007-LST.010 ve boş FRM.001"), t("Numaralandırılmış değerlendirmeler bunun istisnasıdır.")],
            [t("Değerlendirme yerleşimi"), t("Doldurulmuş FRM.001, İç Denetimler / Süreç Gözden Geçirmeleri altında saklanır."), t("... - Değerlendirme #1"), t("Yeni değerlendirme bir sonraki sıra numarasını alır.")],
            [t("Akış görseli"), t("Mermaid kaynak kodu ile aynı modelden üretilmiş PNG birlikte saklanır."), t("Süreç Akışı ve LST.007 etkileşim diyagramı"), t("Kaynak ve görsel tutarlı olmalıdır.")],
            [t("Sürüm ve roller"), t("Sürüm v1.0; hazırlayan, süreç sahibi, gözden geçiren ve onaylayan bilgileri yetkili kişilerle uyumlu olmalıdır."), t("SRÇ.004 sahibi/onaylayanı Mustafa Nusret SARISAKAL"), t("Her yeni süreç çalışmasında roller kullanıcıdan doğrulanır.")],
            [t("Referans kapsamı"), t("Süreç dokümanının Referanslar bölümünde yalnızca ilgili ISO/IEC 15504-5 üçlüsü ve sonradan onaylanacak kurumsal kaynaklar yer alır."), t("İlgili süreç bölümü; PAM; Process Attributes"), t("Destek dokümanları süreç referans listesine eklenmez.")],
        ]),
        "<h2>9. Uygulama Adımları / Talimatlar</h2>",
        table(["Adım", "Talimat / Uygulama Adımı", "Açıklama", "Örnek / Kanıt"], [
            [t("1"), t("Süreç kimliğini doğrula"), t("Standart kod, kurumsal kod, süreç adı, sahip ve durumu LST.006 üzerinden kontrol et."), t(LST006_TITLE)],
            [t("2"), t("Aktif şablonları belirle"), t("Arşivdekileri dışarıda bırakarak SRÇ/LST/FRM şablonlarının başlık ve tablo yapısını çıkar."), t("02 - Şablonlar sayfası")],
            [t("3"), t("Süreç tanımını kontrol et"), t("Amaç, sonuç, kapsam, üç standart referansı, ilgili süreçlerin alt alta yazımı, araçlar/altyapı, iş ürünleri, Mermaid akışı ve uyarlama kurallarını doğrula."), t(SRC004_TITLE)],
            [t("4"), t("Etkileşim kaydını kontrol et"), t("Girdi/çıktı matrisleri ile Mermaid kaynak ve PNG görselinin aynı ilişkileri gösterdiğini doğrula."), t(LST007_TITLE)],
            [t("5"), t("İş ürünü paketini kontrol et"), t("LST.008-LST.010 adlarını, yapılarını, kalite kriterlerini, ölçümleri, RACI ve tam doküman referanslarını doğrula."), t(f"{LST008}; {LST009}; {LST010}")],
            [t("6"), t("Boş formu kontrol et"), t("Süreç altındaki FRM.001 içinde tarih, puan, bulgu veya tamamlanmış aksiyon bulunmadığını doğrula."), t(FRM001)],
            [t("7"), t("Değerlendirme kaydını ayır"), t("Doldurulmuş formu İç Denetimler altında Değerlendirme #n adıyla sakla."), t("91 - İç Denetimler / Süreç Gözden Geçirmeleri")],
            [t("8"), t("Bütünsel tutarlılığı doğrula"), t("Ad, kod, sahiplik, faaliyet, iş ürünü, etkileşim, ölçüm, rol ve yerleşim ilişkilerini çapraz kontrol et."), t("Yerel doğrulama raporu ve görüntüleyici")],
            [t("9"), t("Onaya sun ve yayımla"), t("Yerel inceleme onayından sonra yetkili gözden geçirme/onay ve Confluence yayını yürütülür."), t("Onay ve Confluence sürüm kaydı")],
            [t("10"), t("Gerçek kullanım kanıtını işlet"), t("Yayın sonrası bilgilendirme, ölçüm ve kullanım kayıtlarını doğal kaynak sistemlerde oluştur."), t(f"{LST012}; doğal kaynak sistem kayıtları")],
        ]),
        "<h2>10. Örnekler ve Formatlar</h2>",
        table(["Örnek Alanı", "Kullanım", "Örnek", "Açıklama"], [
            [t("Süreç özel liste adı"), t("LST.007-LST.010"), t("LST.007 - Süreç Etkileşim Matrisi (SRÇ.004)"), t("Kod, güncel ad ve ilgili süreç kodu birlikte yazılır.")],
            [t("Boş form adı"), t("Süreç altındaki tekrar kullanılabilir form"), t(FRM001), t("Değerlendirme sıra numarası içermez.")],
            [t("Doldurulmuş form adı"), t("İç denetim kaydı"), t(f"{FRM001} - Değerlendirme #1"), t("Her yeni değerlendirmede sıra numarası artırılır.")],
            [t("Süreç sayısı ifadesi"), t("Kapsam tanımı"), t(f"Güncel standart süreç seti {LST006_TITLE} üzerinden belirlenir."), t("Sabit toplam kullanılmaz.")],
        ]),
        "<h2>11. Kontrol ve Gözden Geçirme Kuralları</h2>",
        table(["Kontrol Alanı", "Kontrol Yöntemi", "Sıklık", "Sorumlu", "Kayıt / Kanıt"], [
            [t("Şablon yapısı"), t("Başlık ve tablo başlıklarının aktif şablonla birebir karşılaştırılması"), t("Her yeni/güncellenen dokümanda"), t("Kalite Danışmanı / Doküman Sorumlusu"), t("Yapısal doğrulama sonucu")],
            [t("Adlandırma ve yerleşim"), t("Sayfa ağacı, tam ad ve parent kontrolü"), t("Her yayın öncesinde"), t("Doküman Sorumlusu"), t("Yerel görüntüleyici ve Confluence sayfa ağacı")],
            [t("BP ve PA/GP izlenebilirliği"), t("FRM.001 satırlarının ilgili standart beklentileriyle kontrolü"), t("Her değerlendirmede"), t("Gözden Geçiren / Kalite Danışmanı"), t("Numaralandırılmış FRM.001")],
            [t("Gerçek kanıt"), t("Yayın, duyuru, ölçüm ve kullanım kayıtlarının doğal kaynakta doğrulanması"), t("Değerlendirme ve denetim öncesinde"), t("Süreç Sahibi / Kanıt Sahibi"), t("Confluence, LST.012 ve doğal kaynak sistem")],
            [t("Kılavuz güncelliği"), t("Şablon, süreç ve repository değişikliklerinin kontrolü"), t("Yılda en az bir kez ve değişiklikte"), t("SRÇ.004 Süreç Sahibi"), t("Sürüm geçmişi")],
        ]),
        "<h2>12. Kayıtlar ve Kanıtlar</h2>",
        table(["Kayıt / Kanıt", "Kullanım Amacı", "Saklama Yeri", "Sorumlu", "Not"], [
            [t("Süreç tasarım paketi"), t("Süreç tanımı ve süreç özel kayıtların bütünlüğünü göstermek"), t("İlgili SRÇ sayfası / Confluence"), t("İlgili Süreç Sahibi / Süreç Mimarı"), t("Boş FRM.001 paket içinde kalır.")],
            [t("Numaralandırılmış FRM.001"), t("Belirli tarihteki kanıt durumunu ve açıkları göstermek"), t("91 - İç Denetimler / Süreç Gözden Geçirmeleri"), t("Gözden Geçiren"), t("Tarihsel kayıt değiştirilmez; yeni değerlendirme yeni numara alır.")],
            [t("Mermaid kaynak ve PNG"), t("Akış ve etkileşim modelinin yeniden üretilebilirliğini sağlamak"), t("İlgili sayfa ekleri / repository"), t("Süreç Mimarı / Doküman Sorumlusu"), t("Kaynak ve görsel aynı modeli temsil eder.")],
            [t("Yerel doğrulama raporu"), t("Yayın öncesi yapı, ad ve yerleşim kontrollerini kanıtlamak"), t("Repository / reports"), t("Kalite Danışmanı"), t("Confluence yayını öncesinde güncellenir.")],
            [t("SRÇ.018 kayıtları"), t("Kontrol bulgularından doğan değişiklik ve talepleri izlemek"), t("SRÇ.018 doğal kaynak sistemi"), t("Değişiklik Yöneticisi"), t("Ayrı değişiklik formu oluşturulmaz.")],
        ]),
        "<h2>13. Sürüm Geçmişi</h2>", guide_history("Süreç Tasarımı Kontrol Kılavuzu"),
    ]
    return "".join(parts) + "\n"


def load_inventory_rows() -> list[list[str]]:
    path = CONFLUENCE / LST006_REL / "body.storage.xhtml"
    storage = path.read_text(encoding="utf-8")
    for block in re.findall(r"<table.*?</table>", storage, flags=re.DOTALL):
        headers, rows = parse_table(block)
        if "Standart Süreç Kodu" not in headers:
            continue
        if headers == ["Standart Süreç Kodu", "Standart Süreç Adı", "Kurumsal Süreç Kodu", "Kurumsal Süreç Adı", "Süreç Sahibi", "Durum", "Not"]:
            return [[clean(cell) for cell in row] for row in rows]
        if "No" in headers and "Çalışma Adı / Türkçe Ad" in headers:
            index = {header: i for i, header in enumerate(headers)}
            output: list[list[str]] = []
            for row in rows:
                standard_code = clean(row[index["Standart Süreç Kodu"]])
                standard_name = clean(row[index["Standart Süreç Adı"]])
                corporate_code = clean(row[index["Kurumsal Süreç Kodu"]])
                corporate_name = clean(row[index["Çalışma Adı / Türkçe Ad"]])
                if corporate_code == "SRÇ.001":
                    owner, status, note = "Levent BAYEZİT - Proje Yöneticisi", "Aktif", "Süreç paketi oluşturulmuş ve süreç özel kayıtlarıyla yönetilmektedir."
                elif corporate_code == "SRÇ.004":
                    owner, status, note = PROCESS_OWNER, "Aktif", "Süreç paketi güncel aktif şablonlara göre yerelde tamamlanmaktadır."
                elif corporate_code == "SRÇ.005":
                    owner, status, note = PROCESS_OWNER, "Aktif", "Süreç paketi oluşturulmuş, Confluence'ta yayımlanmış ve süreç özel kayıtlarıyla yönetilmektedir."
                elif corporate_code == "SRÇ.006":
                    owner, status, note = PROCESS_OWNER, "Aktif", "Süreç paketi oluşturulmuş, Confluence'ta yayımlanmış ve süreç özel kayıtlarıyla yönetilmektedir."
                else:
                    owner, status, note = "İlgili süreç çalışmasında belirlenecek", "Taslak", "Süreç sahibi, kapsamı ve süreç özel paketi ilgili süreç çalışmasında doğrulanacaktır."
                output.append([standard_code, standard_name, corporate_code, corporate_name, owner, status, note])
            return output
    raise RuntimeError("LST.006 envanter tablosu bulunamadı")


def lst006_body(rows: list[list[str]]) -> str:
    return "".join([
        "<h2>1. Liste Özeti</h2>",
        table(["Alan", "Değer"], [
            [t("Liste Kodu ve Adı"), t(LST006_TITLE)],
            [t("Kullanım Amacı"), t("Güncel standart süreç setini kurumsal süreç kodu, ad, sahiplik ve durum bilgileriyle izlemek")],
            [t("Sorumlu"), t("SRÇ.004 Süreç Sahibi / Kalite Danışmanı")],
            [t("Durum"), t("Aktif")],
            [t("Sürüm"), t("v1.0")],
            [t("Son Gözden Geçirme Tarihi"), t("15-02-2025")],
        ]),
        "<h2>2. Kullanım Değerleri</h2>",
        table(["Alan", "Kullanım Kuralı"], [
            [t("Kapsam"), t("Liste, güncel çalışma kapsamındaki standart süreçleri ve kurumsal eşleştirmelerini içerir.")],
            [t("Kapsam Dışı"), t("Süreç olmayan şablon, prosedür, kılavuz, form ve proje özel kayıtları envantere süreç satırı olarak alınmaz.")],
            [t("Güncelleme"), t("Süreç kodu, adı, sahibi, kapsamı veya durumu değiştiğinde ilgili satır güncellenir.")],
            [t("Kanıt"), t("Süreç satırları, oluşturuldukça ilgili SRÇ sayfası ve süreç özel doküman paketiyle ilişkilendirilir.")],
        ]),
        "<h2>3. Standart Süreç Envanteri</h2>",
        table(["Standart Süreç Kodu", "Standart Süreç Adı", "Kurumsal Süreç Kodu", "Kurumsal Süreç Adı", "Süreç Sahibi", "Durum", "Not"], [[t(cell) for cell in row] for row in rows]),
        "<h2>4. Sürüm Geçmişi</h2>",
        table(["Sürüm", "Tarih", "Açıklama", "Hazırlayan/Güncelleyen", "Gözden Geçiren", "Onay"], [
            [t("v0.1"), t("01-02-2025"), t("İlk taslak oluşturuldu."), t(PREPARED_BY), t("-"), t("-")],
            [t("v1.0"), t("15-02-2025"), t("Standart Süreç Envanteri onaylanarak yürürlüğe alınmıştır."), t(PREPARED_BY), t(REVIEWED_BY), t(APPROVED_BY)],
        ]),
    ]) + "\n"


LST007_NODES = {
    "SRC001": "SRÇ.001\nDokümantasyon",
    "SRC005": "SRÇ.005\nSüreç Değerlendirme",
    "SRC006": "SRÇ.006\nSüreç İyileştirme",
    "SRC018": "SRÇ.018\nDeğişiklik Talebi",
    "TEMPLATES": "Aktif Şablonlar\nSRÇ / LST / FRM",
    "SRC004": "SRÇ.004\nSüreç Kurulumu",
    "SRC020": "SRÇ.020\nEğitim",
    "SRC025": "SRÇ.025\nÖlçüm",
    "PRS002": "PRS.002\nSüreç Tasarım Prosedürü",
    "KLV002": "KLV.002\nSüreç Uyarlama Kılavuzu",
    "KLV003": "KLV.003\nSüreç Tasarımı Kontrol Kılavuzu",
    "LST006": "LST.006\nStandart Süreç Envanteri",
    "LST007": "LST.007\nSüreç Etkileşim Matrisi",
    "LST008": "LST.008\nİş Ürünleri ve Kalite Kriterleri",
    "LST009": "LST.009\nPerformans Ölçüm Seti",
    "LST010": "LST.010\nRol Yetki ve RACI Matrisi",
    "FRM001": "FRM.001\nSüreç Gözden Geçirme Formu",
    "LST012": "LST.012\nYaygınlaştırma ve Bilgilendirme",
}
LST007_EDGES = [
    ("SRC001", "SRC004", "doküman ve şablon kuralları"),
    ("SRC005", "SRC004", "değerlendirme bulguları"),
    ("SRC006", "SRC004", "iyileştirme ihtiyacı"),
    ("SRC018", "SRC004", "onaylı değişiklik talebi"),
    ("TEMPLATES", "SRC004", "zorunlu doküman yapısı"),
    ("SRC004", "PRS002", "tasarım yöntemi"),
    ("SRC004", "KLV002", "uyarlama kuralları"),
    ("SRC004", "KLV003", "tasarım kontrol kuralları"),
    ("SRC004", "LST006", "süreç envanteri"),
    ("SRC004", "LST007", "etkileşim kaydı"),
    ("SRC004", "LST008", "iş ürünleri ve kalite kriterleri"),
    ("SRC004", "LST009", "ölçüm seti"),
    ("SRC004", "LST010", "rol ve RACI kaydı"),
    ("SRC004", "FRM001", "boş gözden geçirme formu"),
    ("SRC004", "LST012", "yayın ve bilgilendirme kaydı"),
    ("SRC004", "SRC001", "onaylı süreç varlıkları"),
    ("SRC004", "SRC005", "değerlendirme paketi ve kanıt"),
    ("SRC004", "SRC006", "performans ve kullanım bulguları"),
    ("SRC004", "SRC020", "eğitim / bilgilendirme ihtiyacı"),
    ("SRC004", "SRC025", "ölçüm tanımı ve veri ihtiyacı"),
]


def mermaid_code() -> str:
    lines = [
        "flowchart LR",
        '  subgraph INPUTS["Girdiler"]',
        "    direction TB",
        '    SRC001["SRÇ.001 Dokümantasyon Süreci"]',
        '    SRC005["SRÇ.005 Süreç Değerlendirme Süreci"]',
        '    SRC006["SRÇ.006 Süreç İyileştirme Süreci"]',
        '    SRC018["SRÇ.018 Değişiklik Talebi Yönetimi Süreci"]',
        '    TEMPLATES["Aktif Şablonlar: SRÇ.XXX.Ş / LST.007-LST.010.Ş / FRM.001.Ş"]',
        "  end",
        '  SRC004["SRÇ.004 Süreç Kurulumu Süreci"]',
        '  subgraph ASSETS["Üretilen / Güncellenen Dokümanlar"]',
        "    direction TB",
        '    PRS002["PRS.002 Süreç Tasarım Prosedürü"]',
        '    KLV002["KLV.002 Süreç Uyarlama Kılavuzu"]',
        '    KLV003["KLV.003 Süreç Tasarımı Kontrol Kılavuzu"]',
        '    LST006["LST.006 Standart Süreç Envanteri"]',
        '    LST007["LST.007 Süreç Etkileşim Matrisi"]',
        '    LST008["LST.008 İş Ürünleri ve Kalite Kriterleri"]',
        '    LST009["LST.009 Süreç Performans Ölçüm Seti"]',
        '    LST010["LST.010 Süreç Rol Yetki ve RACI Matrisi"]',
        '    FRM001["FRM.001 Süreç Gözden Geçirme Formu"]',
        '    LST012["LST.012 Yaygınlaştırma ve Bilgilendirme Kaydı"]',
        "  end",
        '  subgraph TARGETS["İlişkili Süreç Yönlendirmeleri"]',
        "    direction TB",
        '    SRC020["SRÇ.020 Eğitim Süreci"]',
        '    SRC025["SRÇ.025 Ölçüm Süreci"]',
        "  end",
    ]
    for source, target, label in LST007_EDGES:
        lines.append(f'  {source} -->|"{label}"| {target}')
    return "\n".join(lines) + "\n"


def render_interaction_png(target: Path) -> None:
    """Render a readable audit-oriented PNG from the same interaction model."""
    from PIL import Image, ImageDraw, ImageFont

    width, height = 1800, 1120
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 34)
        node_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 27)
        legend_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 22)
        legend_bold = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 22)
    except OSError:
        title_font = node_font = legend_font = legend_bold = ImageFont.load_default()

    draw.text((70, 34), "SRÇ.004 Süreç Etkileşimleri", fill=(15, 23, 42), font=title_font)

    boxes = {
        "SRC001": (70, 125, 470, 235),
        "SRC005": (70, 310, 470, 420),
        "SRC006": (70, 495, 470, 605),
        "SRC018": (70, 680, 470, 790),
        "SRC004": (700, 350, 1110, 520),
        "SRC020": (1330, 245, 1730, 355),
        "SRC025": (1330, 560, 1730, 670),
    }
    labels = {
        "SRC001": "SRÇ.001\nDokümantasyon Süreci",
        "SRC005": "SRÇ.005\nSüreç Değerlendirme",
        "SRC006": "SRÇ.006\nSüreç İyileştirme",
        "SRC018": "SRÇ.018\nDeğişiklik Talebi",
        "SRC004": "SRÇ.004\nSüreç Kurulumu Süreci",
        "SRC020": "SRÇ.020\nEğitim Süreci",
        "SRC025": "SRÇ.025\nÖlçüm Süreci",
    }

    def center(box: tuple[int, int, int, int]) -> tuple[float, float]:
        x1, y1, x2, y2 = box
        return ((x1 + x2) / 2, (y1 + y2) / 2)

    def arrowhead(end: tuple[float, float], start: tuple[float, float], color: tuple[int, int, int]) -> None:
        angle = math.atan2(end[1] - start[1], end[0] - start[0])
        size = 18
        left = (end[0] - size * math.cos(angle - 0.55), end[1] - size * math.sin(angle - 0.55))
        right = (end[0] - size * math.cos(angle + 0.55), end[1] - size * math.sin(angle + 0.55))
        draw.polygon([end, left, right], fill=color)

    def edge(source: str, target_name: str, number: str, bidirectional: bool = False) -> None:
        source_box, target_box = boxes[source], boxes[target_name]
        sx, sy = center(source_box)
        tx, ty = center(target_box)
        if sx < tx:
            start, end = (source_box[2], sy), (target_box[0], ty)
        else:
            start, end = (source_box[0], sy), (target_box[2], ty)
        color = (71, 85, 105)
        draw.line([start, end], fill=color, width=5)
        arrowhead(end, start, color)
        if bidirectional:
            arrowhead(start, end, color)
        mx, my = (start[0] + end[0]) / 2, (start[1] + end[1]) / 2
        draw.ellipse((mx - 22, my - 22, mx + 22, my + 22), fill="white", outline=(37, 99, 235), width=3)
        bbox = draw.textbbox((0, 0), number, font=legend_bold)
        draw.text((mx - (bbox[2] - bbox[0]) / 2, my - (bbox[3] - bbox[1]) / 2 - 2), number, fill=(30, 64, 175), font=legend_bold)

    edge("SRC001", "SRC004", "1", bidirectional=True)
    edge("SRC005", "SRC004", "2", bidirectional=True)
    edge("SRC006", "SRC004", "3", bidirectional=True)
    edge("SRC018", "SRC004", "4")
    edge("SRC004", "SRC020", "5")
    edge("SRC004", "SRC025", "6")

    for key, box in boxes.items():
        x1, y1, x2, y2 = box
        fill = (224, 242, 254) if key == "SRC004" else (245, 248, 255)
        outline = (3, 105, 161) if key == "SRC004" else (30, 64, 175)
        draw.rounded_rectangle(box, radius=18, fill=fill, outline=outline, width=4)
        lines = labels[key].split("\n")
        line_heights = [draw.textbbox((0, 0), line, font=node_font)[3] for line in lines]
        total = sum(line_heights) + 8 * (len(lines) - 1)
        y = (y1 + y2 - total) / 2 - 3
        for line, line_height in zip(lines, line_heights):
            bbox = draw.textbbox((0, 0), line, font=node_font)
            draw.text(((x1 + x2 - (bbox[2] - bbox[0])) / 2, y), line, fill=(15, 23, 42), font=node_font)
            y += line_height + 8

    legend = [
        ("1", "Doküman/şablon kuralları ↔ onaylı süreç varlıkları"),
        ("2", "Değerlendirme bulguları ↔ değerlendirme paketi ve kanıt"),
        ("3", "İyileştirme ihtiyacı ↔ performans ve kullanım bulguları"),
        ("4", "Onaylı değişiklik veya yeni süreç talebi → SRÇ.004"),
        ("5", "SRÇ.004 → eğitim ve bilgilendirme ihtiyacı"),
        ("6", "SRÇ.004 → ölçüm tanımı ve veri ihtiyacı"),
    ]
    draw.rounded_rectangle((70, 865, 1730, 1065), radius=16, fill=(248, 250, 252), outline=(203, 213, 225), width=2)
    for i, (number, description) in enumerate(legend):
        col, row = i // 3, i % 3
        x, y = 105 + col * 815, 895 + row * 52
        draw.text((x, y), number, fill=(30, 64, 175), font=legend_bold)
        draw.text((x + 38, y), description, fill=(51, 65, 85), font=legend_font)

    target.parent.mkdir(parents=True, exist_ok=True)
    image.save(target)


def diagram_fragment(code: str, png_name: str, view: bool) -> str:
    mermaid_lines = "<br />".join(f'<code class="language-mermaid">{e(line)}</code>' for line in code.rstrip().splitlines())
    image = (
        f'<p><img class="diagram" src="attachments/{e(png_name)}" alt="{e(png_name)}" /></p>'
        if view
        else f'<p><ac:image ac:width="1000"><ri:attachment ri:filename="{e(png_name)}" /></ac:image></p>'
    )
    mermaid_box = (
        '<div class="confluence-information-macro has-no-icon confluence-information-macro-information conf-macro output-block" data-hasbody="true" data-macro-name="info">'
        '<p class="title">Mermaid Kodu</p><div class="confluence-information-macro-body">'
        f'<p style="margin-left:40px">{mermaid_lines}</p></div></div>'
        if view
        else '<ac:structured-macro ac:name="info" ac:schema-version="1">'
        '<ac:parameter ac:name="icon">false</ac:parameter>'
        '<ac:parameter ac:name="title">Mermaid Kodu</ac:parameter>'
        f'<ac:rich-text-body><p style="margin-left:40px">{mermaid_lines}</p></ac:rich-text-body>'
        '</ac:structured-macro>'
    )
    return "<h2>3. Süreç Etkileşim Diyagramı</h2>" + image + mermaid_box


def lst007_body(code: str, view: bool) -> str:
    inputs = [
        (SRC001, "Doküman ve şablon kuralları", "Güncel doküman yapısı, adlandırma ve yayın kuralları", f"{SRC_TEMPLATE}; aktif LST/FRM şablonları", "Süreç varlıklarının ortak yapıda hazırlanmasını sağlar."),
        (SRC005, "Değerlendirme girdisi", "BP ve PA/GP bulguları ile kanıt açıkları", "Numaralandırılmış FRM.001 değerlendirme kaydı", "Yeni süreç veya bakım ihtiyacını tetikler."),
        (SRC006, "İyileştirme girdisi", "Önceliklendirilmiş süreç iyileştirme ihtiyacı", "İyileştirme kararı ve aksiyon kaydı", "Standart süreç setinin bakımına girdi sağlar."),
        (SRC018, "Değişiklik girdisi", "Onaylı süreç değişikliği veya yeni süreç talebi", "SRÇ.018 talep, karar ve onay kaydı", "Tüm değişiklik ve talepler tek süreç üzerinden alınır."),
        ("ISO/IEC 15504-5 ve kurumsal gereksinimler", "Standart / kurumsal girdi", "Süreç amacı, sonuç, BP/PA-GP ve organizasyonel ihtiyaç", "İlgili standart bölümü ve yetkili kurumsal karar", "Süreç tasarım kapsamını ve zorunlu beklentileri belirler."),
        ("Aktif süreç ve kayıt şablonları", "Doküman yapısı", "SRÇ.XXX.Ş, LST.007.Ş, LST.008.Ş, LST.009.Ş, LST.010.Ş ve FRM.001.Ş yapıları", "02 - Şablonlar altındaki aktif sayfalar", "Arşivdeki kaldırılmış şablonlar kullanılmaz."),
        (PRS002, "Tasarım yöntemi", "Tasarım adımları, sorumluluklar ve kontrol kapıları", PRS002, "Süreç paketinin hazırlanma yöntemini belirler."),
        (KLV002_TITLE, "Uyarlama kuralı", "Uyarlanabilir alanlar, sınırlar ve onay koşulları", KLV002_TITLE, "Süreç amacı ve zorunlu sonuçların korunmasını sağlar."),
        (KLV003_TITLE, "Kontrol kuralı", "Şablon, yerleşim, kanıt ve yayın öncesi kontrol noktaları", KLV003_TITLE, "Süreç tasarım paketinin bütünsel kontrolünde kullanılır."),
        (LST006_TITLE, "Envanter girdisi", "Standart/kurumsal süreç kimliği, sahiplik ve durum", LST006_TITLE, "Tasarlanacak veya güncellenecek sürecin kimliğini doğrular."),
    ]
    outputs = [
        (SRC001, "Dokümantasyon çıktısı", "Onaylanan süreç varlıkları ve yayın ihtiyacı", f"{SRC004_TITLE}; süreç özel kayıtlar", "Kontrollü yayın ve doküman yönetimi için aktarılır."),
        (SRC005, "Değerlendirme çıktısı", "Değerlendirilebilir süreç paketi ve izlenebilir kanıtlar", f"{LST007_TITLE}; {LST008}; {LST009}; {LST010}; {FRM001}", "Süreç yetenek değerlendirmesinin kanıt temelini oluşturur."),
        (SRC006, "İyileştirme çıktısı", "Performans, kullanım ve değerlendirme bulguları", f"{LST009}; numaralandırılmış FRM.001", "İyileştirme önceliklerinin belirlenmesini destekler."),
        (SRC020, "Eğitim / bilgilendirme yönlendirmesi", "Yeni veya değişen süreç için öğrenme ihtiyacı", f"{LST010}; {LST012}", "Yalnızca gerçek ihtiyaç oluştuğunda eğitim sürecini tetikler."),
        (SRC025, "Ölçüm yönlendirmesi", "Ölçüm tanımı, veri kaynağı, hedef/eşik ve analiz ihtiyacı", LST009, "Süreç performans verisinin doğal kaynaklardan toplanmasını destekler."),
        (PRS002, "Prosedür çıktısı", "Süreç tasarım yöntemi ve kontrol kapıları", PRS002, "Süreç paketlerinin ortak yöntemle hazırlanmasını sağlar."),
        (KLV002_TITLE, "Kılavuz çıktısı", "Uyarlama sınırları ve uygulama adımları", KLV002_TITLE, "PIM.1.BP5 beklentisini destekler."),
        (KLV003_TITLE, "Kılavuz çıktısı", "Yayın öncesi süreç tasarım kontrol kuralları", KLV003_TITLE, "Aktif şablon ve yerleşim kontrollerini tanımlar."),
        (LST006_TITLE, "Ortak envanter çıktısı", "Standart süreç kimliği, kurumsal eşleştirme, sahiplik ve durum", LST006_TITLE, "Güncel standart süreç setini izler."),
        (LST007_TITLE, "Süreç özel kayıt", "SRÇ.004 girdi ve çıktı etkileşimleri", LST007_TITLE, "Mermaid kaynak, PNG ve matrisleri birlikte tutar."),
        (LST008, "Süreç özel kayıt", "Girdi/çıktı iş ürünleri ve kalite kriterleri", LST008, "Süreç iş ürünlerinin beklenen kalitesini tanımlar."),
        (LST009, "Süreç özel kayıt", "Az sayıda yönetilebilir performans ölçümü", LST009, "Veri kaynağı, hesaplama, hedef/eşik ve sorumluları tanımlar."),
        (LST010, "Süreç özel kayıt", "Rol, yetki, yetkinlik ve RACI bilgileri", LST010, "Faaliyet ve iş ürünü sorumluluklarını belirler."),
        (FRM001, "Süreç özel form", "Yeni değerlendirmelerde kullanılacak boş BP/PA-GP formu", FRM001, "Doldurulmuş kopyalar İç Denetimler altında numaralandırılır."),
        (LST012, "Yayın kaydı", "Onay sonrası gerçek yaygınlaştırma ve bilgilendirme kanıtı", LST012, "Yalnızca gerçek yayın ve duyuru sonrasında güncellenir."),
    ]
    return "".join([
        "<h2>1. Liste Özeti</h2>",
        table(["Alan", "Değer"], [
            [t("Liste Kodu ve Adı"), t(LST007_TITLE)],
            [t("İlgili Süreç"), t(SRC004_TITLE)],
            [t("Kullanım Amacı"), t("Süreç Kurulumu Sürecinin girdi, çıktı, kayıt ve yönlendirme etkileşimlerini görsel ve matris yapısıyla izlemek")],
            [t("Sorumlu"), t(PROCESS_OWNER)],
            [t("Durum"), t("Aktif")],
            [t("Sürüm"), t("v1.0")],
        ], view),
        "<h2>2. Kullanım Değerleri</h2>",
        table(["Alan", "Kullanım Kuralı"], [
            [t("Mermaid Kodu"), t("Diyagramın kaynak kodu bu bölümde saklanır.")],
            [t("PNG Görsel"), t("Mermaid koduyla aynı etkileşim modelinden üretilen görsel kullanılır.")],
            [t("Girdi Matrisi"), t("SRÇ.004'e gelen süreç, standart, karar ve bilgi etkileşimleri açıklanır.")],
            [t("Çıktı Matrisi"), t("SRÇ.004'ten diğer süreç ve hedeflere giden varlık ve yönlendirmeler açıklanır.")],
            [t("Etkileşim Notları"), t("Özel uygulama, sınır ve kanıt kuralları yazılır.")],
        ], view),
        diagram_fragment(code, LST007_PNG, view),
        "<h2>4. Girdi Etkileşimleri Matrisi</h2>",
        table(["Kaynak Süreç / Kaynak", "Etkileşim Türü", "Girdi / Tetikleyici", "Kayıt / Kanıt", "Açıklama"], [[t(cell) for cell in row] for row in inputs], view),
        "<h2>5. Çıktı Etkileşimleri Matrisi</h2>",
        table(["Hedef Süreç / Hedef", "Etkileşim Türü", "Çıktı / Yönlendirme", "Kayıt / Kanıt", "Açıklama"], [[t(cell) for cell in row] for row in outputs], view),
        "<h2>6. Etkileşim Notları</h2>",
        p("Bu matris, SRÇ.004'ün süreç tasarım ve bakım bağlamındaki temel arayüzlerini gösterir; ilişkili süreçlerin operasyonel akışlarını tekrar tanımlamaz."),
        p(f"Değişiklik ve talepler {SRC018} kapsamında; doldurulmuş değerlendirmeler 91 - İç Denetimler / Süreç Gözden Geçirmeleri altında; süreç özel tasarım varlıkları ise {SRC004_TITLE} altında yönetilir."),
        "<h2>7. Sürüm Geçmişi</h2>",
        table(["Sürüm", "Tarih", "Açıklama", "Hazırlayan/Güncelleyen", "Gözden Geçiren", "Onay"], [
            [t("v0.1"), t("01-02-2025"), t("İlk taslak oluşturuldu."), t(PREPARED_BY), t(REVIEWED_BY), t("-")],
            [t("v1.0"), t("15-02-2025"), t("SRÇ.004 Süreç Etkileşim Matrisi onaylanarak yürürlüğe alınmıştır."), t(PREPARED_BY), t(REVIEWED_BY), t(APPROVED_BY)],
        ], view),
    ]) + "\n"


def update_src001_lst007() -> Path:
    page_dir = CONFLUENCE / SRC001_LST007_REL
    storage_path = page_dir / "body.storage.xhtml"
    if not storage_path.exists():
        raise RuntimeError("SRÇ.001 süreç özel LST.007 sayfası bulunamadı")

    code = mermaid(SRC001_NODES, SRC001_EDGES)
    write_mermaid(page_dir, SRC001_LST007_MMD, code)
    assets_png = page_dir / "assets" / SRC001_LST007_PNG
    attachments_png = page_dir / "attachments" / SRC001_LST007_PNG
    if not assets_png.exists():
        render_fallback_png(SRC001_NODES, SRC001_EDGES, assets_png)
    attachments_png.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(assets_png, attachments_png)

    storage = storage_path.read_text(encoding="utf-8")
    pattern = r"<h2[^>]*>3\..*?</h2>.*?(?=<h2[^>]*>4\.)"
    if not re.search(pattern, storage, flags=re.DOTALL):
        raise RuntimeError("SRÇ.001 LST.007 içinde 3. bölüm bulunamadı")
    new_storage = re.sub(pattern, diagram_fragment(code, SRC001_LST007_PNG, view=False), storage, count=1, flags=re.DOTALL)
    view_body = re.sub(pattern, diagram_fragment(code, SRC001_LST007_PNG, view=True), storage, count=1, flags=re.DOTALL)
    storage_path.write_text(new_storage, encoding="utf-8")
    (page_dir / "body.view.html").write_text(build_view(SRC001_LST007_TITLE, view_body), encoding="utf-8")
    print(f"[UPDATED] {SRC001_LST007_TITLE}")
    return page_dir


def validate_headings(storage: str, expected: list[str]) -> None:
    actual = [clean(item) for item in re.findall(r"<h2[^>]*>(.*?)</h2>", storage, flags=re.DOTALL)]
    if actual != expected:
        raise RuntimeError(f"Bölüm yapısı uyuşmuyor: {actual}")


def validate_outputs() -> None:
    guide_headings = [
        "1. Kılavuz / Talimat Bilgileri", "2. Amaç", "3. Kapsam", "4. Kapsam Dışı",
        "5. Referanslar", "6. Terimler ve Kısaltmalar", "7. Genel İlkeler",
        "8. Kural ve Uygulama Alanları", "9. Uygulama Adımları / Talimatlar",
        "10. Örnekler ve Formatlar", "11. Kontrol ve Gözden Geçirme Kuralları",
        "12. Kayıtlar ve Kanıtlar", "13. Sürüm Geçmişi",
    ]
    checks = [
        (CONFLUENCE / KLV002_REL / "body.storage.xhtml", guide_headings),
        (CONFLUENCE / KLV003_REL / "body.storage.xhtml", guide_headings),
        (CONFLUENCE / LST006_REL / "body.storage.xhtml", ["1. Liste Özeti", "2. Kullanım Değerleri", "3. Standart Süreç Envanteri", "4. Sürüm Geçmişi"]),
        (CONFLUENCE / LST007_REL / "body.storage.xhtml", ["1. Liste Özeti", "2. Kullanım Değerleri", "3. Süreç Etkileşim Diyagramı", "4. Girdi Etkileşimleri Matrisi", "5. Çıktı Etkileşimleri Matrisi", "6. Etkileşim Notları", "7. Sürüm Geçmişi"]),
        (CONFLUENCE / SRC001_LST007_REL / "body.storage.xhtml", ["1. Liste Özeti", "2. Kullanım Değerleri", "3. Süreç Etkileşim Diyagramı", "4. Girdi Etkileşimleri Matrisi", "5. Çıktı Etkileşimleri Matrisi", "6. Etkileşim Notları", "7. Sürüm Geçmişi"]),
    ]
    forbidden = ["ŞBL.001", "ŞBL.007", "ŞBL.010", "ŞBL.011", "ŞBL.012", "ŞBL.013", "ŞBL.014", "ŞBL.015", "Süreç Mimari ve Etkileşim Matrisi", "26 süreç", "LST.004"]
    for path, headings in checks:
        storage = path.read_text(encoding="utf-8")
        validate_headings(storage, headings)
        for phrase in forbidden:
            if phrase in storage:
                raise RuntimeError(f"{path} içinde eski/sabit ifade bulundu: {phrase}")
    if not (CONFLUENCE / LST007_REL / "attachments" / LST007_PNG).exists():
        raise RuntimeError("SRÇ.004 LST.007 PNG görseli oluşturulamadı")
    if not (CONFLUENCE / SRC001_LST007_REL / "attachments" / SRC001_LST007_PNG).exists():
        raise RuntimeError("SRÇ.001 LST.007 PNG görseli oluşturulamadı")

    for rel, png_name in ((LST007_REL, LST007_PNG), (SRC001_LST007_REL, SRC001_LST007_PNG)):
        storage = (CONFLUENCE / rel / "body.storage.xhtml").read_text(encoding="utf-8")
        section = re.search(r"<h2[^>]*>3\..*?(?=<h2[^>]*>4\.)", storage, flags=re.DOTALL)
        if not section or section.group(0).find("<ac:image") > section.group(0).find("<ac:structured-macro"):
            raise RuntimeError(f"{rel} içinde diyagram bilgi kutusunun üstünde değil")
        if png_name not in section.group(0) or "Mermaid Kodu" not in section.group(0):
            raise RuntimeError(f"{rel} içinde PNG veya Mermaid bilgi kutusu eksik")

    src004_code = (CONFLUENCE / LST007_REL / "assets" / LST007_MMD).read_text(encoding="utf-8")
    for node in ("TEMPLATES", "PRS002", "KLV002", "LST008", "LST009", "LST010", "FRM001"):
        if node not in src004_code:
            raise RuntimeError(f"SRÇ.004 Mermaid modelinde doküman düğümü eksik: {node}")

    index = yaml.safe_load(INDEX_PATH.read_text(encoding="utf-8")) or {}
    indexed_rels = {str(page.get("relative_path") or "") for page in index.get("pages", [])}
    for rel in REMOVED_RELS:
        if (CONFLUENCE / rel).exists() or rel in indexed_rels:
            raise RuntimeError(f"Eski sayfa yerel paketten tamamen kaldırılmadı: {rel}")


def write_report() -> None:
    REPORT.write_text("\n".join([
        "# SRÇ.004 Destek Paketi Uyum Raporu", "", "Tarih: 14-07-2026", "",
        "- KLV.002 ve KLV.003 aktif KLV.XXX.Ş bölüm/tablo yapısına göre yeniden oluşturuldu.",
        "- KLV.002 içinde tüm değişiklik ve talepler SRÇ.018'e yönlendirildi; ayrı uyarlama/değişiklik formu oluşturulmadı.",
        "- KLV.003 süreç tasarım paketi, boş FRM.001 ve numaralandırılmış değerlendirme yerleşimini açıkça tanımlıyor.",
        "- LST.006 aktif şablon yapısına taşındı; SRÇ.004 sahiplik ve durum kaydı güncellendi; sabit süreç sayısı metni kullanılmadı.",
        "- SRÇ.004 LST.007 etkileşim matrisi süreçlerin yanında prosedür, kılavuz, şablon, liste ve form ilişkilerini de içerecek biçimde genişletildi.",
        "- SRÇ.001 ve SRÇ.004 LST.007 sayfalarında diyagram üstte, Mermaid Kodu Confluence bilgi kutusu altta olacak şekilde ortak yerleşim uygulandı.",
        "- İki PNG, aynı sayfalarda saklanan Mermaid kodları kullanılarak Mermaid Online Editor üzerinden dışa aktarıldı.",
        "- Eski SRÇ.001/SRÇ.004 LST.004 sayfaları ile merkezi eski Süreç Mimari ve Etkileşim Matrisi yerel paket ve indeksten kaldırıldı.",
        "- Confluence'a yayın yapılmadı; gerçek yaygınlaştırma/ölçüm kanıtı ve Değerlendirme #2 üretilmedi.", "",
    ]), encoding="utf-8")


def main() -> None:
    inventory_rows = load_inventory_rows()
    remove_legacy_pages()

    klv002_dir = CONFLUENCE / KLV002_REL
    klv003_dir = CONFLUENCE / KLV003_REL
    lst006_dir = CONFLUENCE / LST006_REL
    lst007_dir = CONFLUENCE / LST007_REL

    write_page(klv002_dir, KLV002_TITLE, klv002_dir.name, GUIDES_ID, GUIDES_TITLE, 2, klv002_body())
    write_page(klv003_dir, KLV003_TITLE, klv003_dir.name, GUIDES_ID, GUIDES_TITLE, 2, klv003_body())
    write_page(lst006_dir, LST006_TITLE, lst006_dir.name, LISTS_ID, LISTS_TITLE, 2, lst006_body(inventory_rows))

    code = mermaid_code()
    storage = lst007_body(code, view=False)
    view = lst007_body(code, view=True)
    write_page(lst007_dir, LST007_TITLE, LST007_SLUG, SRC004_ID, SRC004_TITLE, 3, storage, view)
    write_mermaid(lst007_dir, LST007_MMD, code)
    attachments = lst007_dir / "attachments"
    attachments.mkdir(parents=True, exist_ok=True)
    if not (lst007_dir / "assets" / LST007_PNG).exists():
        render_interaction_png(lst007_dir / "assets" / LST007_PNG)
    shutil.copy2(lst007_dir / "assets" / LST007_PNG, attachments / LST007_PNG)
    print(f"[PNG] SRÇ.004 etkileşim görseli korundu: {(attachments / LST007_PNG).relative_to(ROOT)}")

    update_src001_lst007()

    upsert_index([klv002_dir, klv003_dir, lst006_dir, lst007_dir])
    validate_outputs()
    write_report()
    print("[DONE] SRÇ.004 destek paketi aktif şablonlarla uyumlaştırıldı.")
    print(f"[REPORT] {REPORT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
