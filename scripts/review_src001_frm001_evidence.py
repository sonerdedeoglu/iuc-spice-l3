#!/usr/bin/env python3
"""Rebuild SRÇ.001 FRM.001 with evidence-based process review results.

The evaluation follows the agreed status scale:
- 0%: YOK
- >0% and <=40%: ZAYIF
- >40% and <70%: DAĞINIK
- >=70%: VAR

The form structure is kept aligned with the approved FRM.001 real-record format:
1. Değerlendirme Özeti
2. Durum Değerleri
3. BP Takip Matrisi
4. PA / GP Takip Matrisi
5. Öncelikli Tamamlama Listesi
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
SRC001_DIR = ROOT / "confluence/pages/000-root-iuc-bidb-spice-2026-level-3/01-surec-dokumanlari/iuc-bidb-src-001-dokumantasyon-sureci"
FRM_DIR = SRC001_DIR / "iuc-bidb-frm-001-surec-gozden-gecirme-formu-iuc-bidb-src-001"
STANDARD_PATH = ROOT / "resources/standards/spice_practices.yaml"

TITLE = "İÜC.BİDB.FRM.001 - Süreç Gözden Geçirme Formu (İÜC.BİDB.SRÇ.001)"
PARENT_ID = "137265796"
PARENT_TITLE = "İÜC.BİDB.SRÇ.001 - Dokümantasyon Süreci"
SLUG = "iuc-bidb-frm-001-surec-gozden-gecirme-formu-iuc-bidb-src-001"

CSS = """
body{margin:0;background:#fff;color:#172b4d;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;line-height:1.55}
.confluence-page{max-width:1180px;margin:0 auto;padding:32px 24px 56px}
h1,h2,h3,h4,h5,h6{margin:1.4em 0 .55em;line-height:1.25;color:#0f172a}
h1{margin-top:0;padding-bottom:12px;border-bottom:1px solid #d8dee4}
p{margin:0 0 12px}
table{width:100%;border-collapse:collapse;margin:16px 0;table-layout:auto}
th,td{border:1px solid #c9d1d9;padding:8px 10px;vertical-align:top}
th{background:#f6f8fa;font-weight:600;text-align:left}
code{background:#f6f8fa;padding:2px 4px;border-radius:4px}
.status-var{font-weight:700;color:#166534}.status-daginik{font-weight:700;color:#92400e}.status-zayif{font-weight:700;color:#991b1b}.status-yok{font-weight:700;color:#7f1d1d}
""".strip()

BP_ROWS = [
    {
        "id": "SUP.7.BP1",
        "pct": 90,
        "evidence": [
            "İÜC.BİDB.SRÇ.001 - Dokümantasyon Süreci: dokümantasyon sürecinin amaç, kapsam, faaliyet ve iş ürünü yapısı",
            "İÜC.BİDB.PRS.001 - Yazılım Projeleri Dokümantasyon Prosedürü: yazılım projeleri için dokümantasyon stratejisi",
            "İÜC.BİDB.LST.005.Ş - Yaşam Döngüsü Doküman Üretim Matrisi Şablonu",
            "Soru Bankası Projesi / İÜC.BİDB.LST.005 - Yaşam Döngüsü Doküman Üretim Matrisi (SB): taslak proje uygulama kaydı",
        ],
        "summary": "Dokümantasyon yönetim stratejisi kurumsal süreçte tanımlanmış, yazılım projelerine özel strateji PRS.001 ile ayrıştırılmış, LST.005 şablonu ve SB taslağıyla proje düzeyine indirgenmiştir.",
        "action": "-",
    },
    {
        "id": "SUP.7.BP2",
        "pct": 95,
        "evidence": [
            "İÜC.BİDB.KLV.001 - Doküman Yazım Kuralları Talimatı",
            "İÜC.BİDB.SRÇ.XXX.Ş - Süreç Tanımı Şablonu",
            "İÜC.BİDB.PRS.XXX.Ş - Prosedür Tanımı Şablonu",
            "İÜC.BİDB.KLV.XXX.Ş - Kılavuz ve Talimat Tanımı Şablonu",
            "LST.001.Ş, LST.003.Ş, LST.005.Ş, LST.006.Ş, LST.007.Ş, LST.008.Ş, LST.009.Ş, LST.010.Ş, LST.011.Ş, LST.012.Ş şablon ailesi",
        ],
        "summary": "Doküman yazım, başlık, tablo, sürüm, şablon ve liste standartları KLV.001 ile tanımlanmış; ana doküman türleri için güncel şablon ailesi oluşturulmuştur.",
        "action": "-",
    },
    {
        "id": "SUP.7.BP3",
        "pct": 85,
        "evidence": [
            "İÜC.BİDB.LST.008 - İş Ürünleri ve Kalite Kriterleri Listesi (İÜC.BİDB.SRÇ.001)",
            "İÜC.BİDB.LST.001 - Aktif Dokümanlar Listesi",
            "İÜC.BİDB.PRS.001 - yazılım projelerinde beklenen doküman/kayıt ihtiyacını tanımlayan yaşam döngüsü stratejisi",
            "İÜC.BİDB.LST.005.Ş - proje yaşam döngüsüne göre doküman üretim matrisi şablonu",
        ],
        "summary": "SRÇ.001 için iş ürünleri ve kalite kriterleri tanımlanmış; genel aktif doküman envanteri ve proje yaşam döngüsü doküman ihtiyacı için ayrı izleme yapısı kurulmuştur.",
        "action": "-",
    },
    {
        "id": "SUP.7.BP4",
        "pct": 90,
        "evidence": [
            "İÜC.BİDB.LST.001 - Aktif Dokümanlar Listesi: genel aktif dokümanların tür bazında ayrılmış envanteri",
            "SRÇ.001 altındaki LST.007, LST.008, LST.009, LST.010 ve FRM.001 kayıtları",
            "Soru Bankası Projesi altında İÜC.BİDB.LST.005 - Yaşam Döngüsü Doküman Üretim Matrisi (SB) taslağı",
        ],
        "summary": "Üretilecek genel dokümanlar LST.001 ile, SRÇ.001’e özel kayıtlar süreç altında, proje özel doküman üretimi ise SB proje alanında ayrıştırılmıştır.",
        "action": "-",
    },
    {
        "id": "SUP.7.BP5",
        "pct": 95,
        "evidence": [
            "SRÇ.001 ana süreç dokümanı ve bağlı FRM/LST kayıtları",
            "PRS.001 ve KLV.001 gerçek dokümanları",
            "LST.001, LST.007, LST.008, LST.009, LST.010 gerçek kayıtları",
            "Confluence publish/export akışı ve repository commit kayıtları",
        ],
        "summary": "SRÇ.001 kapsamında gerekli ana dokümanlar, destekleyici prosedür/kılavuzlar ve süreç kayıtları oluşturulmuş ve Confluence üzerinden yayımlanabilir hale getirilmiştir.",
        "action": "-",
    },
    {
        "id": "SUP.7.BP6",
        "pct": 65,
        "evidence": [
            "Bu FRM.001 gözden geçirme formu: BP ve PA/GP bazında güncel değerlendirme",
            "İÜC.BİDB.LST.003.Ş - Doküman Gözden Geçirme Kaydı Şablonu",
            "Doküman sürüm geçmişi tabloları ve Confluence üzerinde yapılan gözden geçirme/düzeltme kayıtları",
        ],
        "summary": "Gözden geçirme pratiği fiilen uygulanıyor ve FRM.001 ile süreç bazında kayıt altına alınıyor; ancak LST.003 gerçek gözden geçirme kayıtlarının sistematik dolu hali henüz yeterince olgun değil.",
        "action": "SRÇ.001, PRS.001, KLV.001, LST.001 ve LST.007 için LST.003 gerçek gözden geçirme satırları oluşturulmalı; Confluence düzenleme kayıtlarıyla ilişkilendirilmeli.",
    },
    {
        "id": "SUP.7.BP7",
        "pct": 90,
        "evidence": [
            "Confluence sayfa ağacı: süreç dokümanları, şablonlar, kayıtlar/listeler ve proje alanı",
            "İÜC.BİDB.LST.001 - Aktif Dokümanlar Listesi: genel aktif dokümanların konum bilgisi",
            "publish_confluence_tree.py publish raporları",
        ],
        "summary": "Dokümanların yayın ve dağıtım yaklaşımı Confluence sayfa ağacı ve LST.001 konum bilgisiyle görünür durumdadır; repository-publish akışıyla yayın kontrolü sağlanmaktadır.",
        "action": "-",
    },
    {
        "id": "SUP.7.BP8",
        "pct": 60,
        "evidence": [
            "İÜC.BİDB.LST.002 - Doküman Değişiklik Kaydı",
            "Dokümanların sürüm geçmişi bölümleri",
            "Arşiv - Kaldırılan Şablonlar alanı",
            "Git commit geçmişi ve Confluence export/publish raporları",
        ],
        "summary": "Bakım ve arşivleme yaklaşımı kullanılmakta; eski şablonların arşive alınması ve sürüm geçmişleri kanıt oluşturuyor. Ancak LST.002 gerçek değişiklik kaydı tüm son revizyonları kapsayacak şekilde henüz tamamlanmış değil.",
        "action": "Son şablon ve doküman revizyonları için LST.002 değişiklik kayıtları tamamlanmalı; pasif/arşiv kararları LST.001 kapsam dışı notlarıyla ilişkilendirilmeli.",
    },
]

PA_ROWS = [
    ("PA 2.1", "GP 2.1.1", 90, "SRÇ.001, PRS.001 ve bağlı LST kayıtlarıyla sürecin performans hedefleri ve işleyişi belirlenmiştir.", "-"),
    ("PA 2.1", "GP 2.1.2", 85, "LST.010 RACI matrisi ve SRÇ.001 roller bölümü ile sorumluluklar tanımlanmıştır.", "-"),
    ("PA 2.1", "GP 2.1.3", 80, "Confluence, repository, Drive/Jira/Bitbucket/Bamboo kaynak sistem yaklaşımı PRS.001 ve KLV.001 içinde tanımlanmıştır.", "-"),
    ("PA 2.1", "GP 2.1.4", 85, "SRÇ.001 faaliyetleri ve PRS.001 yazılım proje stratejisi, sürecin uygulama akışını yönetilebilir hale getirmiştir.", "-"),
    ("PA 2.1", "GP 2.1.5", 85, "LST.009 ölçüm seti ve bu FRM.001 gözden geçirme formu ile izleme ve değerlendirme yapılmaktadır.", "-"),
    ("PA 2.1", "GP 2.1.6", 75, "Gözden geçirme sonucu aksiyonlar bu formda belirlenmektedir; aksiyon kapanışlarının LST.002/LST.003 ile ilişkilendirilmesi güçlendirilmelidir.", "Aksiyon kapanışları LST.002 ve LST.003 kayıtlarıyla izlenmeli."),
    ("PA 2.2", "GP 2.2.1", 90, "LST.008 ile süreç iş ürünleri ve kalite kriterleri tanımlıdır.", "-"),
    ("PA 2.2", "GP 2.2.2", 85, "LST.001, LST.007, LST.008, LST.009, LST.010 ve FRM.001 ile iş ürünleri dokümante edilmiştir.", "-"),
    ("PA 2.2", "GP 2.2.3", 75, "Confluence/repository yapısı ve LST.001 konum bilgileri iş ürünlerinin kontrolünü desteklemektedir.", "-"),
    ("PA 2.2", "GP 2.2.4", 80, "Confluence erişim/yayın yapısı ve aktif doküman listesi, iş ürünlerinin görünür ve erişilebilir olmasını sağlamaktadır.", "-"),
    ("PA 3.1", "GP 3.1.1", 90, "SRÇ.001 ana süreç tanımı, şablonlar ve PRS/KLV destek dokümanları ile standart süreç tanımlanmıştır.", "-"),
    ("PA 3.1", "GP 3.1.2", 85, "Süreç uygulama sırası, faaliyetleri, iş ürünleri, etkileşimleri ve ölçümleri bağlı listelerle tanımlanmıştır.", "-"),
    ("PA 3.1", "GP 3.1.3", 80, "LST.010 RACI, PRS.001 ve KLV.001 ile yetkinlik/sorumluluk beklentileri görünürdür.", "-"),
    ("PA 3.1", "GP 3.1.4", 85, "Confluence sayfa ağacı, şablon ailesi ve repository otomasyonu süreç altyapısını desteklemektedir.", "-"),
    ("PA 3.1", "GP 3.1.5", 75, "LST.009 ve FRM.001 ile izleme yaklaşımı tanımlanmıştır; düzenli periyodik veri birikimi daha da güçlendirilebilir.", "Periyodik ölçüm sonuçları LST.009 üzerinden dönemsel olarak işlenmeli."),
    ("PA 3.2", "GP 3.2.1", 85, "SRÇ.001, PRS.001, KLV.001 ve bağlı kayıtlar süreç uygulamasının kurumsal biçimde yayımlanmasını desteklemektedir.", "-"),
    ("PA 3.2", "GP 3.2.2", 80, "LST.010 ve SRÇ.001 roller/sorumluluklar bölümü ile uygulama sorumlulukları atanmıştır.", "-"),
    ("PA 3.2", "GP 3.2.3", 70, "Confluence/repository altyapısı ve kaynak sistemler hazırdır; kurum içi yaygın kullanım kanıtları sınırlıdır.", "-"),
    ("PA 3.2", "GP 3.2.4", 65, "Süreç uygulanıyor ve dokümanlar yayımlanıyor; ancak LST.012 gerçek yaygınlaştırma/bilgilendirme kayıtları henüz tamamlanmamıştır.", "LST.012 gerçek bilgilendirme/yaygınlaştırma kayıtları doldurulmalı."),
    ("PA 3.2", "GP 3.2.5", 70, "İş ürünleri üretilmiş ve publish/export kayıtları oluşmuştur; kurumsal periyodik kullanım kanıtı biriktirme devam etmelidir.", "-"),
    ("PA 3.2", "GP 3.2.6", 65, "Süreç performansı FRM.001 ve LST.009 ile izlenebilir; düzenli dönemsel ölçüm veri seti henüz sınırlıdır.", "LST.009 ölçüm sonuçları dönemsel olarak işlenmeli ve FRM.001 kapanış aksiyonlarıyla bağlanmalı."),
]


def status(pct: int) -> str:
    if pct == 0:
        return "YOK"
    if pct <= 40:
        return "ZAYIF"
    if pct < 70:
        return "DAĞINIK"
    return "VAR"


def status_html(pct: int) -> str:
    st = status(pct)
    cls = {"VAR": "status-var", "DAĞINIK": "status-daginik", "ZAYIF": "status-zayif", "YOK": "status-yok"}[st]
    return f'<span class="{cls}">{st}</span>'


def e(value: object) -> str:
    return html.escape(str(value), quote=False)


def p(text: str) -> str:
    return f"<p>{e(text)}</p>"


def ul(items: list[str]) -> str:
    return "<ul>" + "".join(f"<li>{e(item)}</li>" for item in items) + "</ul>"


def table(headers: list[str], rows: list[list[str]]) -> str:
    head = "".join(f"<th>{e(h)}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>" for row in rows)
    return f'<table class="wrapped"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>'


def load_standard() -> dict[str, Any]:
    if not STANDARD_PATH.exists():
        return {}
    return yaml.safe_load(STANDARD_PATH.read_text(encoding="utf-8")) or {}


def standard_titles() -> dict[str, str]:
    data = load_standard()
    result: dict[str, str] = {}
    for process in data.get("processes", []):
        if process.get("id") == "SUP.7":
            for bp in process.get("base_practices", []):
                result[bp.get("id", "")] = bp.get("title", "")
    gps = data.get("generic_practices", {})
    for pa_value in gps.values():
        for gp in pa_value if isinstance(pa_value, list) else pa_value.get("practices", []):
            result[gp.get("id", "")] = gp.get("title", "")
    return result


def build_storage() -> str:
    titles = standard_titles()
    bp_total = round(sum(row["pct"] for row in BP_ROWS) / len(BP_ROWS))
    pa_total = round(sum(row[2] for row in PA_ROWS) / len(PA_ROWS))
    overall = round((bp_total + pa_total) / 2)

    parts: list[str] = []
    parts.append("<h2>1. Değerlendirme Özeti</h2>")
    parts.append(table(["Alan", "Değer"], [
        ["Değerlendirilen Süreç", "İÜC.BİDB.SRÇ.001 - Dokümantasyon Süreci"],
        ["Standart Süreç Referansı", "ISO/IEC 15504-5 SUP.7 - Documentation"],
        ["Değerlendirme Tarihi", "13-07-2026"],
        ["Değerlendiren", "Soner DEDEOĞLU - Kalite Danışmanı"],
        ["BP Ortalama Durumu", f"%{bp_total} - {status_html(bp_total)}"],
        ["PA/GP Ortalama Durumu", f"%{pa_total} - {status_html(pa_total)}"],
        ["Genel Sonuç", f"%{overall} - {status_html(overall)}"],
    ]))
    parts.append(p("SRÇ.001 için ana süreç dokümanı, destekleyici prosedür/kılavuzlar, şablon ailesi ve süreç alt kayıtları büyük ölçüde oluşturulmuştur. Mevcut kanıtlar BP seviyesinde güçlüdür. İyileştirme ihtiyacı özellikle gözden geçirme/değişiklik kayıtlarının sistematik doldurulması ve yaygınlaştırma/ölçüm kayıtlarının dönemsel olarak biriktirilmesi alanındadır."))

    parts.append("<h2>2. Durum Değerleri</h2>")
    parts.append(table(["Yüzde Aralığı", "Durum", "Kullanım"], [
        ["%0", status_html(0), "Kanıt yok veya beklenti hiç karşılanmıyor."],
        ["%0 - %40", '<span class="status-zayif">ZAYIF</span>', "Kısmi/başlangıç düzeyi kanıt var; uygulama yetersiz."],
        ["%40 - %70", '<span class="status-daginik">DAĞINIK</span>', "Kanıt var ancak sistematik, tamamlanmış veya tutarlı değil."],
        ["%70 - %100", '<span class="status-var">VAR</span>', "Beklenti kanıtlarla büyük ölçüde karşılanıyor."],
    ]))

    parts.append("<h2>3. BP Takip Matrisi</h2>")
    bp_rows: list[list[str]] = []
    for row in BP_ROWS:
        bp_rows.append([
            row["id"],
            e(titles.get(row["id"], row["id"])),
            f"%{row['pct']} - {status_html(row['pct'])}",
            ul(row["evidence"]),
            e(row["summary"]),
            e(row["action"] if status(row["pct"]) != "VAR" else "-"),
        ])
    parts.append(table(["BP", "Standart Beklentisi", "Durum", "Nokta Atışı Kanıtlar", "Mevcut Karşılama Durumu", "Eksik / Tamamlayıcı Aksiyon"], bp_rows))

    parts.append("<h2>4. PA / GP Takip Matrisi</h2>")
    pa_rows: list[list[str]] = []
    for pa, gp, pct, summary, action in PA_ROWS:
        pa_rows.append([
            pa,
            gp,
            e(titles.get(gp, gp)),
            f"%{pct} - {status_html(pct)}",
            e(summary),
            e(action if status(pct) != "VAR" else "-"),
        ])
    parts.append(table(["PA", "GP", "Standart Beklentisi", "Durum", "Kanıta Dayalı Değerlendirme", "Eksik / Tamamlayıcı Aksiyon"], pa_rows))

    parts.append("<h2>5. Öncelikli Tamamlama Listesi</h2>")
    actions: list[list[str]] = []
    for row in BP_ROWS:
        if status(row["pct"]) != "VAR":
            actions.append([row["id"], e(row["action"]), "Yüksek" if row["pct"] < 60 else "Orta", "Dokümantasyon Süreç Sahibi / Kalite Danışmanı", "Açık"])
    for pa, gp, pct, summary, action in PA_ROWS:
        if status(pct) != "VAR":
            actions.append([gp, e(action), "Yüksek" if pct < 60 else "Orta", "Dokümantasyon Süreç Sahibi / Kalite Danışmanı", "Açık"])
    parts.append(table(["Kaynak", "Aksiyon", "Öncelik", "Sorumlu", "Durum"], actions))

    return "".join(parts) + "\n"


def build_view(storage: str) -> str:
    return f"""<!doctype html><html lang="tr"><head><meta charset="utf-8"><title>{e(TITLE)}</title><style>{CSS}</style></head><body><main class="confluence-page"><h1>{e(TITLE)}</h1>{storage}</main></body></html>\n"""


def page_meta() -> dict[str, Any]:
    rel = str(FRM_DIR.relative_to(CONFLUENCE_DIR)).replace("\\", "/")
    meta = yaml.safe_load((FRM_DIR / "page.yaml").read_text(encoding="utf-8")) if (FRM_DIR / "page.yaml").exists() else {}
    meta.update({
        "title": TITLE,
        "slug": SLUG,
        "relative_path": rel,
        "parent_id": PARENT_ID,
        "parent_title": PARENT_TITLE,
        "depth": 3,
        "status": "active",
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


def update_index() -> None:
    index = yaml.safe_load(INDEX_PATH.read_text(encoding="utf-8")) or {}
    pages = index.setdefault("pages", [])
    rel = str(FRM_DIR.relative_to(CONFLUENCE_DIR)).replace("\\", "/")
    pages[:] = [p for p in pages if p.get("relative_path") != rel]
    meta = yaml.safe_load((FRM_DIR / "page.yaml").read_text(encoding="utf-8"))
    pages.append({
        "page_id": str(meta.get("page_id") or ""),
        "title": TITLE,
        "parent_id": PARENT_ID,
        "depth": 3,
        "relative_path": rel,
        "slug": SLUG,
        "storage_file": f"{rel}/body.storage.xhtml",
        "view_file": f"{rel}/body.view.html",
    })
    index["total_page_count"] = len(pages)
    INDEX_PATH.write_text(yaml.safe_dump(index, allow_unicode=True, sort_keys=False), encoding="utf-8")


def main() -> None:
    FRM_DIR.mkdir(parents=True, exist_ok=True)
    storage = build_storage()
    (FRM_DIR / "body.storage.xhtml").write_text(storage, encoding="utf-8")
    (FRM_DIR / "body.view.html").write_text(build_view(storage), encoding="utf-8")
    (FRM_DIR / "page.yaml").write_text(yaml.safe_dump(page_meta(), allow_unicode=True, sort_keys=False), encoding="utf-8")
    update_index()
    print(f"[DONE] Rebuilt evidence-based review: {TITLE}")


if __name__ == "__main__":
    main()
