#!/usr/bin/env python3
"""Create SRÇ.001 review assessment #1 from the customized SRÇ.001 FRM.001 form.

Important design rule:
- The SRÇ.001 form under the process page is treated as the process-specific form template.
- This script copies that form structure to 91 - İç Denetimler / Süreç Gözden Geçirmeleri.
- It fills only the tables that match the existing customized form headers.
- It does not change the SRÇ.001 form template itself.
- PA/GP rows are generated from resources/standards/spice_practices.yaml.
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
INDEX_PATH = CONFLUENCE_DIR / "index.yaml"
STANDARD_PATH = ROOT / "resources/standards/spice_practices.yaml"

SRC_FORM_DIR = ROOT / "confluence/pages/000-root-iuc-bidb-spice-2026-level-3/01-surec-dokumanlari/iuc-bidb-src-001-dokumantasyon-sureci/iuc-bidb-frm-001-surec-gozden-gecirme-formu-iuc-bidb-src-001"
TARGET_PARENT_DIR = ROOT / "confluence/pages/000-root-iuc-bidb-spice-2026-level-3/91-ic-denetimler/surec-gozden-gecirmeleri"
TARGET_PARENT_ID = "137265917"
TARGET_PARENT_TITLE = "Süreç Gözden Geçirmeleri"
TARGET_SLUG = "iuc-bidb-frm-001-surec-gozden-gecirme-formu-iuc-bidb-src-001-degerlendirme-1"
TARGET_TITLE = "İÜC.BİDB.FRM.001 - Süreç Gözden Geçirme Formu (İÜC.BİDB.SRÇ.001) - Değerlendirme #1"
TARGET_DIR = TARGET_PARENT_DIR / TARGET_SLUG

CSS = """
body{margin:0;background:#fff;color:#172b4d;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;line-height:1.55}
.confluence-page{max-width:1180px;margin:0 auto;padding:32px 24px 56px}
h1,h2,h3,h4,h5,h6{margin:1.4em 0 .55em;line-height:1.25;color:#0f172a}
h1{margin-top:0;padding-bottom:12px;border-bottom:1px solid #d8dee4}
p{margin:0 0 12px}
table{width:100%;border-collapse:collapse;margin:16px 0;table-layout:auto}
th,td{border:1px solid #c9d1d9;padding:8px 10px;vertical-align:top}
th{background:#f6f8fa;font-weight:600;text-align:left}
""".strip()

SCALE_ROWS = [
    ["YOK", "%0: Kanıt yok veya beklenti hiç karşılanmıyor."],
    ["ZAYIF", "%0-%40: Kısmi başlangıç kanıtı var; uygulama yetersiz."],
    ["DAĞINIK", "%40-%70: Kanıt var ancak sistematik, tamamlanmış veya tutarlı değil."],
    ["VAR", "%70-%100: Beklenti kanıtlarla büyük ölçüde karşılanıyor."],
]

BP_EVAL = {
    "SUP.7.BP1": {
        "pct": 90,
        "current": "Dokümantasyon stratejisi SRÇ.001 ana süreç dokümanı ile kurulmuş; yazılım projelerine özel uygulama PRS.001 ile ayrıştırılmıştır. LST.005 şablonu ve Soru Bankası taslak kaydı proje düzeyi doküman üretimine bağlanmıştır.",
        "evidence": ["SRÇ.001 - Dokümantasyon Süreci", "PRS.001 - Yazılım Projeleri Dokümantasyon Prosedürü", "LST.005.Ş - Yaşam Döngüsü Doküman Üretim Matrisi Şablonu", "Soru Bankası Projesi / LST.005 (SB)"],
        "action": "-",
    },
    "SUP.7.BP2": {
        "pct": 95,
        "current": "Doküman yazım, başlık, tablo, sürüm ve şablon kullanımı kuralları tanımlanmış; süreç, prosedür, kılavuz, form ve LST şablon ailesi güncellenmiştir.",
        "evidence": ["KLV.001 - Doküman Yazım Kuralları Talimatı", "SRÇ.XXX.Ş", "PRS.XXX.Ş", "KLV.XXX.Ş", "FRM.001.Ş", "LST.001.Ş / LST.003.Ş / LST.005.Ş / LST.007.Ş / LST.008.Ş / LST.009.Ş / LST.010.Ş / LST.011.Ş / LST.012.Ş"],
        "action": "-",
    },
    "SUP.7.BP3": {
        "pct": 85,
        "current": "SRÇ.001 için iş ürünleri, kalite kriterleri, genel doküman envanteri ve proje özel doküman üretim ihtiyacı ayrı yapılarda tanımlanmıştır.",
        "evidence": ["LST.008 - İş Ürünleri ve Kalite Kriterleri Listesi (SRÇ.001)", "LST.001 - Aktif Dokümanlar Listesi", "PRS.001", "LST.005.Ş"],
        "action": "-",
    },
    "SUP.7.BP4": {
        "pct": 90,
        "current": "Genel aktif dokümanlar, SRÇ.001’e özel kayıtlar ve proje özel doküman üretimi ayrı sayfa/kayıt yapılarıyla izlenebilir hale getirilmiştir.",
        "evidence": ["LST.001 - Aktif Dokümanlar Listesi", "SRÇ.001 altındaki FRM.001 / LST.007 / LST.008 / LST.009 / LST.010", "Soru Bankası Projesi / LST.005 (SB)"],
        "action": "-",
    },
    "SUP.7.BP5": {
        "pct": 95,
        "current": "SRÇ.001 kapsamında ana süreç dokümanı, destek prosedürü, yazım talimatı, şablonlar ve süreç kayıtları oluşturulmuş ve Confluence/repository yapısında yayımlanabilir hale getirilmiştir.",
        "evidence": ["SRÇ.001", "PRS.001", "KLV.001", "LST.001", "LST.007", "LST.008", "LST.009", "LST.010", "Confluence publish/export ve Git commit kayıtları"],
        "action": "-",
    },
    "SUP.7.BP6": {
        "pct": 65,
        "current": "Gözden geçirme pratiği uygulanıyor; SRÇ.001 süreç bazlı FRM.001 özelleştirildi. Ancak LST.003 gerçek gözden geçirme kayıtlarının son revizyonları kapsayacak şekilde sistematik doldurulması gerekiyor.",
        "evidence": ["SRÇ.001 altındaki FRM.001 süreç bazlı form", "Bu değerlendirme #1", "LST.003.Ş - Doküman Gözden Geçirme Kaydı Şablonu", "Confluence düzenleme kayıtları"],
        "action": "SRÇ.001, PRS.001, KLV.001, LST.001 ve LST.007 için LST.003 gerçek gözden geçirme kayıtları oluşturulmalı.",
    },
    "SUP.7.BP7": {
        "pct": 90,
        "current": "Dokümanlar Confluence sayfa ağacında yayımlanmış; LST.001 doküman türü bazında konum ve durum bilgisi sağlamaktadır.",
        "evidence": ["Confluence sayfa ağacı", "LST.001 - Aktif Dokümanlar Listesi", "publish_confluence_tree.py raporları"],
        "action": "-",
    },
    "SUP.7.BP8": {
        "pct": 60,
        "current": "Bakım ve arşivleme yaklaşımı kullanılıyor; eski şablonlar arşive alınmış ve sürüm geçmişleri tutulmuştur. Ancak LST.002 gerçek değişiklik kayıtları son revizyonların tamamını kapsayacak olgunlukta değildir.",
        "evidence": ["LST.002 - Doküman Değişiklik Kaydı", "Doküman sürüm geçmişleri", "Arşiv - Kaldırılan Şablonlar", "Git commit geçmişi"],
        "action": "Son şablon ve doküman revizyonları için LST.002 değişiklik kayıtları tamamlanmalı.",
    },
}

GP_EVAL_DEFAULT = {
    "pct": 75,
    "current": "SRÇ.001 kapsamında süreç tanımı, şablonlar, roller, ölçüm ve kayıt yapıları oluşturulmuştur. Uygulama kanıtları oluşmuş, dönemsel kayıt birikimi devam etmektedir.",
    "evidence": ["SRÇ.001", "LST.007", "LST.008", "LST.009", "LST.010", "FRM.001"],
    "action": "-",
}

GP_OVERRIDES = {
    "GP 2.1.6": {"pct": 75, "current": "Aksiyonlar FRM.001 değerlendirme yapısında izlenebilir; kapanış kayıtlarının LST.002/LST.003 ile ilişkilendirilmesi güçlendirilmelidir.", "evidence": ["FRM.001", "LST.002", "LST.003.Ş"], "action": "Aksiyon kapanışları LST.002 ve LST.003 gerçek kayıtlarıyla ilişkilendirilmeli."},
    "GP 3.2.4": {"pct": 65, "current": "Süreç yayımlanmış ve dokümanlar oluşturulmuştur; ancak LST.012 gerçek yaygınlaştırma/bilgilendirme kayıtları henüz tamamlanmamıştır.", "evidence": ["LST.012.Ş", "Confluence sayfa ağacı", "publish/export kayıtları"], "action": "LST.012 gerçek yaygınlaştırma ve bilgilendirme kayıtları doldurulmalı."},
    "GP 3.2.6": {"pct": 65, "current": "FRM.001 ve LST.009 ile performans izlenebilir; dönemsel ölçüm veri seti sınırlıdır.", "evidence": ["FRM.001", "LST.009"], "action": "LST.009 ölçüm sonuçları dönemsel olarak işlenmeli ve FRM.001 aksiyonlarıyla bağlanmalı."},
}


def e(value: object) -> str:
    return html.escape(str(value), quote=False)


def strip_tags(text: str) -> str:
    return html.unescape(re.sub(r"<.*?>", "", text, flags=re.DOTALL)).strip()


def status(pct: int) -> str:
    if pct == 0:
        return "YOK"
    if pct <= 40:
        return "ZAYIF"
    if pct < 70:
        return "DAĞINIK"
    return "VAR"


def status_text(pct: int) -> str:
    return f"%{pct} - {status(pct)}"


def ul(items: list[str]) -> str:
    return "<ul>" + "".join(f"<li>{e(item)}</li>" for item in items) + "</ul>"


def table(headers: list[str], rows: list[list[str]]) -> str:
    head = "".join(f"<th>{e(h)}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>" for row in rows)
    return f'<table class="wrapped"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>'


def load_standard() -> dict[str, Any]:
    return yaml.safe_load(STANDARD_PATH.read_text(encoding="utf-8")) or {}


def iter_dicts(obj: Any):
    if isinstance(obj, dict):
        yield obj
        for value in obj.values():
            yield from iter_dicts(value)
    elif isinstance(obj, list):
        for item in obj:
            yield from iter_dicts(item)


def title_of(item: dict[str, Any]) -> str:
    return str(item.get("title") or item.get("name") or item.get("practice") or item.get("description") or "").strip()


def standard_bp_rows() -> list[tuple[str, str]]:
    data = load_standard()
    rows: list[tuple[str, str]] = []
    for item in iter_dicts(data):
        item_id = str(item.get("id") or "")
        if item_id.startswith("SUP.7.BP"):
            rows.append((item_id, title_of(item)))
    rows = sorted(set(rows), key=lambda x: int(re.search(r"BP(\d+)", x[0]).group(1)))
    if len(rows) != 8:
        raise RuntimeError(f"SUP.7 BP sayısı beklenen 8 değil: {rows}")
    return rows


def standard_gp_rows() -> list[tuple[str, str, str]]:
    data = load_standard()
    rows: list[tuple[str, str, str]] = []
    current_pa = ""

    def walk(obj: Any, pa_hint: str = ""):
        if isinstance(obj, dict):
            local_pa = pa_hint
            obj_id = str(obj.get("id") or "")
            if obj_id.startswith("PA_") or obj_id.startswith("PA "):
                local_pa = obj_id.replace("_", " ")
            if obj_id.startswith("GP ") or obj_id.startswith("GP."):
                rows.append((local_pa, obj_id.replace("GP.", "GP "), title_of(obj)))
            for key, value in obj.items():
                key_pa = local_pa
                if str(key).startswith("PA_"):
                    key_pa = str(key).replace("_", " ")
                walk(value, key_pa)
        elif isinstance(obj, list):
            for item in obj:
                walk(item, pa_hint)

    walk(data)
    wanted = {"PA 2 1", "PA 2 2", "PA 3 1", "PA 3 2"}
    cleaned: list[tuple[str, str, str]] = []
    seen: set[tuple[str, str]] = set()
    for pa, gp, title in rows:
        pa = pa.replace("PA ", "PA ").replace("_", " ")
        # Normalize PA_2_1 -> PA 2.1 style.
        m = re.search(r"PA\s*(\d+)\s*(?:\.|\s)(\d+)", pa)
        pa_norm = f"PA {m.group(1)}.{m.group(2)}" if m else pa
        if pa_norm not in {"PA 2.1", "PA 2.2", "PA 3.1", "PA 3.2"}:
            continue
        key = (pa_norm, gp)
        if key not in seen:
            cleaned.append((pa_norm, gp, title))
            seen.add(key)
    if not cleaned:
        raise RuntimeError("Standart YAML içinde PA 2.1/2.2/3.1/3.2 Generic Practice bulunamadı.")
    def gp_sort(row: tuple[str, str, str]) -> tuple[int, int, int]:
        pa, gp, _ = row
        pm = re.search(r"PA (\d+)\.(\d+)", pa)
        gm = re.search(r"GP\s*(\d+)\.(\d+)\.(\d+)", gp)
        return (int(pm.group(1)), int(pm.group(2)), int(gm.group(3)) if gm else 0)
    return sorted(cleaned, key=gp_sort)


def summary_rows(bp_avg: int, gp_avg: int) -> list[list[str]]:
    overall = round((bp_avg + gp_avg) / 2)
    return [
        ["Değerlendirilen Süreç", "İÜC.BİDB.SRÇ.001 - Dokümantasyon Süreci"],
        ["Standart Süreç Referansı", "ISO/IEC 15504-5 SUP.7 - Documentation"],
        ["Değerlendirme No", "Değerlendirme #1"],
        ["Değerlendirme Tarihi", "13-07-2026"],
        ["Değerlendiren", "Soner DEDEOĞLU - Kalite Danışmanı"],
        ["Genel Sonuç", f"BP ortalaması %{bp_avg}, PA/GP ortalaması %{gp_avg}; genel durum %{overall} - {status(overall)}"],
    ]


def bp_rows() -> list[list[str]]:
    rows = []
    for bp_id, expectation in standard_bp_rows():
        ev = BP_EVAL[bp_id]
        rows.append([bp_id, e(expectation), e(ev["current"]), ul(ev["evidence"]), status_text(ev["pct"]), e("-" if status(ev["pct"]) == "VAR" else ev["action"])])
    return rows


def gp_rows() -> list[list[str]]:
    rows = []
    for pa, gp, expectation in standard_gp_rows():
        ev = {**GP_EVAL_DEFAULT, **GP_OVERRIDES.get(gp, {})}
        rows.append([pa, gp, e(expectation), e(ev["current"]), ul(ev["evidence"]), status_text(ev["pct"]), e("-" if status(ev["pct"]) == "VAR" else ev["action"])])
    return rows


def action_rows(bp_data: list[list[str]], gp_data: list[list[str]]) -> list[list[str]]:
    rows: list[list[str]] = []
    for row in bp_data:
        source = row[0]
        durum = row[4]
        action = row[5]
        if not durum.endswith("VAR") and action != "-":
            rows.append(["Orta", action, source, "31-07-2026"])
    for row in gp_data:
        source = row[1]
        durum = row[5]
        action = row[6]
        if not durum.endswith("VAR") and action != "-":
            rows.append(["Orta", action, source, "31-07-2026"])
    return rows


def replace_table_by_headers(storage: str, expected_headers: list[str], rows: list[list[str]]) -> str:
    tables = list(re.finditer(r"<table.*?</table>", storage, flags=re.DOTALL))
    for match in tables:
        block = match.group(0)
        headers = [strip_tags(h) for h in re.findall(r"<th[^>]*>(.*?)</th>", block, flags=re.DOTALL)]
        if headers == expected_headers:
            return storage[:match.start()] + table(expected_headers, rows) + storage[match.end():]
    raise RuntimeError(f"Beklenen tablo başlıkları bulunamadı: {' | '.join(expected_headers)}")


def build_view(storage: str) -> str:
    return f"""<!doctype html><html lang="tr"><head><meta charset="utf-8"><title>{e(TARGET_TITLE)}</title><style>{CSS}</style></head><body><main class="confluence-page"><h1>{e(TARGET_TITLE)}</h1>{storage}</main></body></html>\n"""


def write_page_yaml() -> None:
    rel = str(TARGET_DIR.relative_to(CONFLUENCE_DIR)).replace("\\", "/")
    meta = yaml.safe_load((TARGET_DIR / "page.yaml").read_text(encoding="utf-8")) if (TARGET_DIR / "page.yaml").exists() else {}
    meta.update({
        "page_id": "",
        "space": "SSSS",
        "title": TARGET_TITLE,
        "parent_id": TARGET_PARENT_ID,
        "parent_title": TARGET_PARENT_TITLE,
        "version": "",
        "url": "",
        "depth": 3,
        "status": "active",
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "children_count": 0,
        "relative_path": rel,
        "slug": TARGET_SLUG,
        "has_view_html": True,
        "view_file": "body.view.html",
        "storage_file": "body.storage.xhtml",
    })
    (TARGET_DIR / "page.yaml").write_text(yaml.safe_dump(meta, allow_unicode=True, sort_keys=False), encoding="utf-8")


def update_index() -> None:
    index = yaml.safe_load(INDEX_PATH.read_text(encoding="utf-8")) or {}
    pages = index.setdefault("pages", [])
    rel = str(TARGET_DIR.relative_to(CONFLUENCE_DIR)).replace("\\", "/")
    pages[:] = [p for p in pages if p.get("relative_path") != rel]
    pages.append({
        "page_id": "",
        "title": TARGET_TITLE,
        "parent_id": TARGET_PARENT_ID,
        "depth": 3,
        "relative_path": rel,
        "slug": TARGET_SLUG,
        "storage_file": f"{rel}/body.storage.xhtml",
        "view_file": f"{rel}/body.view.html",
    })
    index["total_page_count"] = len(pages)
    INDEX_PATH.write_text(yaml.safe_dump(index, allow_unicode=True, sort_keys=False), encoding="utf-8")


def main() -> None:
    if not (SRC_FORM_DIR / "body.storage.xhtml").exists():
        raise RuntimeError("Önce Confluence export alınmalı; SRÇ.001 altındaki özelleştirilmiş FRM.001 localde bulunamadı.")

    storage = (SRC_FORM_DIR / "body.storage.xhtml").read_text(encoding="utf-8")
    storage = storage.replace("İÜC.BİDB.FRM.001 - Süreç Gözden Geçirme Formu (İÜC.BİDB.SRÇ.001)", TARGET_TITLE)

    bp_data = bp_rows()
    gp_data = gp_rows()
    bp_avg = round(sum(BP_EVAL[row[0]]["pct"] for row in bp_data) / len(bp_data))
    gp_avg = round(sum(int(re.search(r"%(\d+)", row[5]).group(1)) for row in gp_data) / len(gp_data))

    storage = replace_table_by_headers(storage, ["Alan", "Değer"], summary_rows(bp_avg, gp_avg))
    storage = replace_table_by_headers(storage, ["Durum", "Anlamı"], SCALE_ROWS)
    storage = replace_table_by_headers(storage, ["BP", "Standart Beklentisi", "Mevcut Karşılama", "Karşılayan Doküman / Kayıt", "Durum", "Eksik / Tamamlayıcı Aksiyon"], bp_data)
    storage = replace_table_by_headers(storage, ["PA", "GP", "Standart Beklentisi", "Mevcut Karşılama", "Karşılayan Doküman / Kayıt", "Durum", "Eksik / Tamamlayıcı Aksiyon"], gp_data)
    storage = replace_table_by_headers(storage, ["Öncelik", "Aksiyon", "İlgili BP / GP", "Hedef Kapanış"], action_rows(bp_data, gp_data))

    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    (TARGET_DIR / "body.storage.xhtml").write_text(storage, encoding="utf-8")
    (TARGET_DIR / "body.view.html").write_text(build_view(storage), encoding="utf-8")
    write_page_yaml()
    update_index()
    print(f"[DONE] Created {TARGET_TITLE}")


if __name__ == "__main__":
    main()
