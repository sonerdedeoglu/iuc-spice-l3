#!/usr/bin/env python3
"""Create/replace LST.009 for SRÇ.001.

This script updates the existing SRÇ.001 child page:
LST.009 - Süreç Performans Ölçüm Seti (SRÇ.001)

Measurement count is intentionally kept low. Metrics are selected from values
that the institution can collect easily from Confluence lists/records.
"""
from __future__ import annotations

import html
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
ROOT_PAGE = ROOT / "confluence/pages/000-root-iuc-bidb-spice-2026-level-3"
PAGE_DIR = ROOT_PAGE / "01-surec-dokumanlari/src-001-dokumantasyon-sureci/lst-009-surec-performans-olcum-seti-src-001"

TITLE = "LST.009 - Süreç Performans Ölçüm Seti (SRÇ.001)"
PROCESS_CODE = "SRÇ.001"
PROCESS_NAME = "Dokümantasyon Süreci"
TEMPLATE_NAME = "LST.009.Ş - Süreç Performans Ölçüm Seti Şablonu"

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


def table(headers: list[str], rows: list[list[str]]) -> str:
    head = "".join(f"<th>{e(h)}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>" for row in rows)
    return f'<table class="wrapped"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>'


def load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def write_yaml(path: Path, data: dict[str, Any]) -> None:
    path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")


def measurement_rows() -> list[list[str]]:
    return [
        [
            "SRÇ.001-Ö01",
            "Aktif doküman envanteri güncelliği",
            "Aktif dokümanların LST.001 üzerinden izlenebilir ve güncel tutulduğunu görmek",
            "Aktif doküman listesinde yer alan kayıtların kod, ad, sürüm, durum ve erişim bilgisi açısından dolu olması kontrol edilir.",
            "LST.001 - Aktif Dokümanlar Listesi; Confluence aktif doküman sayfaları",
            "Aylık / süreç gözden geçirme öncesi",
            "%100 kayıt doluluğu; aktif dokümanların LST.001'de yer alması",
            "Doküman Sorumlusu",
            "SUP.7.BP7 / PA 2.1 GP.2.1.5",
            "Aktif",
        ],
        [
            "SRÇ.001-Ö02",
            "Doküman gözden geçirme kayıt tamlığı",
            "Yeni veya güncellenen dokümanların gözden geçirme kaydıyla desteklendiğini izlemek",
            "Gözden geçirme gerektiren dokümanlar için LST.003 kaydı bulunup bulunmadığı kontrol edilir.",
            "LST.003 - Doküman Gözden Geçirme Kaydı; ilgili doküman sürüm geçmişi",
            "Süreç gözden geçirme döneminde",
            "%90 ve üzeri kayıt tamlığı; kritik dokümanlarda %100",
            "Doküman Gözden Geçiren / Kalite Danışmanı",
            "SUP.7.BP6 / PA 2.1 GP.2.1.5",
            "Aktif",
        ],
        [
            "SRÇ.001-Ö03",
            "Doküman değişiklik kaydı tamlığı",
            "Doküman değişikliklerinin gerekçe, tarih, sorumlu ve etkilenen doküman bilgisiyle izlenmesini sağlamak",
            "Değişiklik yapılan dokümanlar için LST.002 kaydı ve doküman sürüm geçmişi tutarlılığı kontrol edilir.",
            "LST.002 - Doküman Değişiklik Kaydı; doküman sürüm geçmişi",
            "Süreç gözden geçirme döneminde",
            "%100 kayıt tamlığı",
            "Doküman Sorumlusu",
            "SUP.7.BP8 / PA 2.1 GP.2.1.5",
            "Aktif",
        ],
    ]


def data_collection_rows() -> list[list[str]]:
    return [
        [
            "SRÇ.001-Ö01",
            "Aktif doküman kayıt alanları ve aktif doküman sayfaları",
            "LST.001; Confluence doküman sayfaları",
            "Manuel liste kontrolü",
            "Eksiksiz kayıt sayısı / aktif doküman kayıt sayısı",
            "Doküman Sorumlusu",
            "LST.001 güncel kayıtları; Confluence sayfa listesi",
        ],
        [
            "SRÇ.001-Ö02",
            "Gözden geçirme gerektiren doküman sayısı ve kayıtlı gözden geçirme sayısı",
            "LST.003; doküman sürüm geçmişleri",
            "Manuel kayıt kontrolü",
            "Gözden geçirme kaydı olan doküman sayısı / gözden geçirme gerektiren doküman sayısı",
            "Doküman Gözden Geçiren / Kalite Danışmanı",
            "LST.003 kayıtları; doküman sürüm geçmişleri",
        ],
        [
            "SRÇ.001-Ö03",
            "Değişiklik yapılan doküman sayısı ve kayıtlı değişiklik sayısı",
            "LST.002; doküman sürüm geçmişleri",
            "Manuel kayıt kontrolü",
            "Değişiklik kaydı olan doküman sayısı / değişiklik yapılan doküman sayısı",
            "Doküman Sorumlusu",
            "LST.002 kayıtları; doküman sürüm geçmişleri",
        ],
    ]


def target_rows() -> list[list[str]]:
    return [
        [
            "SRÇ.001-Ö01",
            "%100 kayıt doluluğu ve aktif dokümanların LST.001'de yer alması",
            "Aylık / süreç gözden geçirme öncesi",
            "Süreç gözden geçirme toplantısı; FRM.001; LST.001",
            "Uygun / Eksik kayıt var / İzleniyor",
            "Eksik alanlar tamamlanır, aktif doküman listesi güncellenir.",
            "Kolay toplanabilir temel envanter ölçümüdür.",
        ],
        [
            "SRÇ.001-Ö02",
            "%90 ve üzeri kayıt tamlığı; kritik dokümanlarda %100",
            "Süreç gözden geçirme döneminde",
            "FRM.001; LST.003; ilgili doküman sürüm geçmişi",
            "Uygun / Sapma / İzleniyor",
            "Eksik gözden geçirme kayıtları tamamlanır veya gerekçelendirilir.",
            "Başlangıç seviyesi için düşük operasyonel yük oluşturur.",
        ],
        [
            "SRÇ.001-Ö03",
            "%100 kayıt tamlığı",
            "Süreç gözden geçirme döneminde",
            "FRM.001; LST.002; ilgili doküman sürüm geçmişi",
            "Uygun / Sapma / İzleniyor",
            "Eksik değişiklik kaydı tamamlanır, gerekirse doküman sürüm geçmişi düzeltilir.",
            "Değişiklik izlenebilirliği için minimum ama kritik ölçümdür.",
        ],
    ]


def build_storage() -> str:
    parts: list[str] = []
    parts.append("<h2>1. Liste Özeti</h2>")
    parts.append(table(["Alan", "Değer"], [
        ["İlgili Süreç", f"{PROCESS_CODE} - {PROCESS_NAME}"],
        ["Liste Kapsamı", "SRÇ.001 kapsamında performans ölçümleri, veri kaynakları, hedef/eşikler ve izleme sorumlulukları"],
        ["Liste Tarihi", "15-02-2025"],
        ["Listeyi Hazırlayan", "Soner DEDEOĞLU - Kalite Danışmanı"],
        ["Listeyi Gözden Geçiren", "Levent BAYEZİT - Proje Yöneticisi"],
        ["Listeyi Onaylayan", "Mustafa Nusret SARISAKAL - BİD Başkanı"],
        ["Genel Not", "Ölçüm sayısı başlangıç seviyesinde minimum tutulmuştur. Kurum ihtiyaç duyarsa ilerleyen dönemlerde ölçüm sayısını artırabilir."],
    ]))

    parts.append("<h2>2. Kullanım Değerleri</h2>")
    parts.append(table(["Değer", "Anlamı"], [
        ["Ölçüm ID", "Sürece özel tekil ölçüm kimliği. Bu listede SRÇ.001-Ö01, SRÇ.001-Ö02 formatı kullanılır."],
        ["Veri Kaynağı", "Ölçümün elde edileceği kayıt, liste, sistem, rapor veya toplantı çıktısı."],
        ["Hedef", "Ölçüm için beklenen sayısal veya nitel başarı değeri."],
        ["Eşik", "Sapma değerlendirmesinde kullanılacak asgari/kritik sınır."],
        ["Sıklık", "Ölçümün hangi periyotta toplanacağı ve değerlendirileceği."],
        ["Aktif", "Ölçüm ilgili süreç için yürürlükte ve izleniyor."],
        ["Askıda", "Ölçüm tanımlı ancak veri toplama henüz başlamamış veya geçici olarak durdurulmuş."],
        ["Kapsam Dışı", "Ölçüm ilgili süreç veya proje bağlamında uygulanmıyor."],
    ]))

    parts.append("<h2>3. Performans Ölçüm Matrisi</h2>")
    parts.append(table(["Ölçüm ID", "Ölçüm Adı", "Ölçüm Amacı", "Hesaplama / Ölçüm Tanımı", "Veri Kaynağı", "Sıklık", "Hedef / Eşik", "Sorumlu", "İlgili BP / GP", "Durum"], measurement_rows()))

    parts.append("<h2>4. Veri Toplama ve Hesaplama Matrisi</h2>")
    parts.append(table(["Ölçüm ID", "Veri Alanı", "Veri Kaynağı", "Toplama Yöntemi", "Hesaplama Yöntemi", "Veri Sahibi", "Kayıt / Kanıt"], data_collection_rows()))

    parts.append("<h2>5. Hedef ve İzleme Matrisi</h2>")
    parts.append(table(["Ölçüm ID", "Hedef / Eşik", "İzleme Sıklığı", "Raporlama / Gözden Geçirme Yeri", "Sapma Durumu", "Tamamlayıcı Aksiyon Yaklaşımı", "Açıklama / Not"], target_rows()))

    parts.append("<h2>6. Sürüm Geçmişi</h2>")
    parts.append(table(["Sürüm", "Tarih", "Açıklama", "Hazırlayan/Güncelleyen", "Gözden Geçiren", "Onay"], [
        ["v1.0", "15-02-2025", "Dokümantasyon Süreci performans ölçüm seti oluşturuldu.", "Soner DEDEOĞLU - Kalite Danışmanı", "Levent BAYEZİT - Proje Yöneticisi", "Mustafa Nusret SARISAKAL - BİD Başkanı"],
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
        "document_code": "LST.009",
        "document_type": "Liste",
        "related_process": PROCESS_CODE,
        "storage_file": "body.storage.xhtml",
        "view_file": "body.view.html",
    })
    write_yaml(path, meta)


def main() -> None:
    if not PAGE_DIR.exists():
        raise FileNotFoundError(f"Expected existing LST.009 page directory not found: {PAGE_DIR}")
    storage = build_storage()
    (PAGE_DIR / "body.storage.xhtml").write_text(storage, encoding="utf-8")
    (PAGE_DIR / "body.view.html").write_text(build_view(storage), encoding="utf-8")
    update_page_yaml()
    print("[DONE] SRÇ.001 LST.009 created/replaced in existing page directory.")
    print(f"[PATH] {PAGE_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
