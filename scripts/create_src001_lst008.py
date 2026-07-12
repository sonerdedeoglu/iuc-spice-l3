#!/usr/bin/env python3
"""Create/replace LST.008 for İÜC.BİDB.SRÇ.001.

This script updates the existing SRÇ.001 child page:
İÜC.BİDB.LST.008 - İş Ürünleri ve Kalite Kriterleri Listesi (İÜC.BİDB.SRÇ.001)

It intentionally replaces the old local body content in place. The existing page_id is
preserved so Confluence publishing updates the same page instead of creating a duplicate.
"""
from __future__ import annotations

import html
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
ROOT_PAGE = ROOT / "confluence/pages/000-root-iuc-bidb-spice-2026-level-3"
PAGE_DIR = ROOT_PAGE / "01-surec-dokumanlari/iuc-bidb-src-001-dokumantasyon-sureci/iuc-bidb-lst-008-is-urunleri-ve-kalite-kriterleri-listesi-iuc-bidb-src-001"
STANDARD_PATH = ROOT / "resources/standards/spice_practices.yaml"

TITLE = "İÜC.BİDB.LST.008 - İş Ürünleri ve Kalite Kriterleri Listesi (İÜC.BİDB.SRÇ.001)"
PROCESS_CODE = "İÜC.BİDB.SRÇ.001"
PROCESS_NAME = "Dokümantasyon Süreci"
PROCESS_REF = "SUP.7 - Documentation"
TEMPLATE_NAME = "İÜC.BİDB.LST.008.Ş - İş Ürünleri ve Kalite Kriterleri Listesi Şablonu"

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


def p(text: str) -> str:
    return f"<p>{e(text)}</p>"


def table(headers: list[str], rows: list[list[str]]) -> str:
    head = "".join(f"<th>{e(h)}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>" for row in rows)
    return f'<table class="wrapped"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>'


def load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def write_yaml(path: Path, data: dict[str, Any]) -> None:
    path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")


def link(text: str) -> str:
    return e(text)


def load_sup7_bps() -> list[dict[str, str]]:
    data = load_yaml(STANDARD_PATH)
    processes = data.get("processes") or {}
    sup7 = processes.get("SUP.7") or processes.get("SUP7") or {}
    bps = sup7.get("base_practices") or []
    result: list[dict[str, str]] = []
    for bp in bps:
        code = str(bp.get("id") or bp.get("code") or "").strip()
        title = str(bp.get("title") or "").strip()
        text = str(bp.get("text") or bp.get("description") or "").strip()
        if code:
            result.append({"code": code, "title": title, "text": text})
    if len(result) < 8:
        raise RuntimeError("SUP.7 base practice listesi standart YAML içinden beklenen şekilde okunamadı.")
    return result


def bp_title(code: str) -> str:
    for bp in load_sup7_bps():
        if bp["code"] == code:
            return bp["title"] or code
    return code


def build_storage() -> str:
    bp = {item["code"]: item for item in load_sup7_bps()}
    parts: list[str] = []

    parts.append("<h2>1. Liste Özeti</h2>")
    parts.append(table(["Alan", "Değer"], [
        ["İlgili Süreç", f"{PROCESS_CODE} - {PROCESS_NAME}"],
        ["Liste Kapsamı", "SRÇ.001 kapsamında kullanılan girdi iş ürünleri, üretilen çıktı iş ürünleri ve bu iş ürünlerine uygulanacak kalite kriterleri"],
        ["Liste Tarihi", "01-09-2025"],
        ["Listeyi Hazırlayan", "Soner DEDEOĞLU - Kalite Danışmanı"],
        ["Listeyi Gözden Geçiren", "Levent BAYEZİT - Proje Yöneticisi"],
        ["Listeyi Onaylayan", "Mustafa Nusret SARISAKAL - BİD Başkanı"],
        ["Genel Not", "Bu liste, Dokümantasyon Süreci için iş ürünlerinin tekil ve izlenebilir şekilde yönetilmesi amacıyla oluşturulmuştur."],
    ]))

    parts.append("<h2>2. Kullanım Değerleri</h2>")
    parts.append(table(["Değer", "Anlamı"], [
        ["Girdi", "Sürecin yürütülmesi için başka süreç, proje, sistem veya kayıttan alınan iş ürünü."],
        ["Çıktı", "Süreç faaliyeti sonucunda üretilen, güncellenen veya yayımlanan iş ürünü."],
        ["Zorunlu", "Süreç kapsamında beklenen ve yokluğu gerekçelendirilmesi gereken iş ürünü."],
        ["Koşullu", "Belirli proje/süreç koşullarında beklenen iş ürünü."],
        ["Opsiyonel", "Süreç olgunluğunu destekleyen ancak her durumda zorunlu olmayan iş ürünü."],
        ["Uygun", "İş ürünü tanımlı kalite kriterlerini karşılıyor."],
        ["Eksik", "İş ürünü var ancak tanımlı kalite kriterlerinden biri veya daha fazlası eksik."],
        ["Yok", "Beklenen iş ürünü henüz oluşturulmamış veya erişilebilir değildir."],
        ["Kapsam Dışı", "İlgili süreç veya proje bağlamında uygulanmıyor."],
    ]))

    parts.append("<h2>3. Girdi İş Ürünleri Matrisi</h2>")
    parts.append(table(["Girdi İş Ürünü", "Kaynak Süreç / Kaynak Doküman", "Kullanım Amacı", "Zorunluluk", "Durum / Not"], [
        ["Yeni doküman veya değişiklik ihtiyacı", "Süreç sahipleri, proje ekibi, kalite güvence, denetim/gözden geçirme sonuçları", "Doküman oluşturma, güncelleme, pasife alma veya arşivleme faaliyetini başlatmak", "Zorunlu", "İhtiyaç kaynağı ve gerekçesi ilgili kayıt veya talep üzerinden izlenebilir olmalıdır."],
        ["Yaşam döngüsü doküman ihtiyacı", "İÜC.BİDB.LST.005 - Yaşam Döngüsü Doküman İhtiyaç Matrisi", "Proje veya süreç aşamasında üretilecek dokümanları belirlemek", "Zorunlu", "Süreç/proje aşaması ile beklenen doküman türü ilişkilendirilmiş olmalıdır."],
        ["Süreç tanımı ve uygulama kuralları", "İÜC.BİDB.SRÇ.001 - Dokümantasyon Süreci", "Doküman yönetim faaliyetlerini şablon ve süreç kurallarına göre yürütmek", "Zorunlu", "Güncel ve aktif süreç dokümanı kullanılmalıdır."],
        ["Doküman şablonları", "02 - Şablonlar", "Dokümanların standart biçimde hazırlanmasını sağlamak", "Zorunlu", "İlgili doküman türü için geçerli aktif şablon kullanılmalıdır."],
        ["Doküman yazım ve tasarım kuralları", "İÜC.BİDB.KLV.001 - Doküman Yazım Kuralları Talimatı; İÜC.BİDB.KLV.003 - Süreç Tasarımı Kontrol Kılavuzu", "Dokümanların biçim, içerik ve kalite beklentilerine uygun hazırlanmasını sağlamak", "Zorunlu", "Kılavuzlar aktif ve erişilebilir olmalıdır."],
        ["Repository ve yayın yapısı", "İÜC.BİDB.LST.011 - Repository Yapısı", "Dokümanın yayımlanacağı, erişileceği ve saklanacağı alanı belirlemek", "Zorunlu", "Repository konumu ve erişim yaklaşımı tanımlı olmalıdır."],
        ["Gözden geçirme geri bildirimleri", "İÜC.BİDB.LST.003 - Doküman Gözden Geçirme Kaydı", "Dokümanın uygunluğunu değerlendirmek ve düzeltmeleri izlemek", "Koşullu", "Gözden geçirme gereken dokümanlarda kayıt oluşturulmalıdır."],
        ["Onay kararı", "Süreç sahibi / yetkili onaylayan", "Dokümanın yürürlüğe alınmasını sağlamak", "Zorunlu", "Onay bilgisi doküman veya ilgili kayıt üzerinden izlenebilir olmalıdır."],
    ]))

    parts.append("<h2>4. Çıktı İş Ürünleri Matrisi</h2>")
    parts.append(table(["Çıktı İş Ürünü", "Üreten Faaliyet", "Kullanım Amacı", "Zorunluluk", "Saklama Yeri / Kayıt", "Durum / Not"], [
        ["İÜC.BİDB.PRS.001 - Yazılım Projeleri Dokümantasyon Prosedürü", bp_title("SUP.7.BP1"), "Dokümantasyon yönetim stratejisi ve yazılım projeleri için doküman yönetim kurallarını tanımlamak", "Zorunlu", "07 - Prosedürler", "Aktif ve onaylı prosedür olarak yönetilir."],
        ["Doküman şablonları", bp_title("SUP.7.BP2"), "Doküman türlerine göre standart yapı ve kullanım kurallarını sağlamak", "Zorunlu", "02 - Şablonlar", "Aktif şablonlar kullanılmalı, kaldırılan şablonlar arşiv altında tutulmalıdır."],
        ["İÜC.BİDB.LST.008 - İş Ürünleri ve Kalite Kriterleri Listesi (İÜC.BİDB.SRÇ.001)", bp_title("SUP.7.BP3"), "SRÇ.001 iş ürünlerini ve kalite kriterlerini tanımlamak", "Zorunlu", "SRÇ.001 alt sayfası", "Bu doküman SRÇ.001 iş ürünü kontrolünün ana kaydıdır."],
        ["İÜC.BİDB.LST.005 - Yaşam Döngüsü Doküman İhtiyaç Matrisi", bp_title("SUP.7.BP4"), "Yaşam döngüsü aşamalarına göre üretilecek dokümanları belirlemek", "Zorunlu", "03 - Kayıtlar ve Listeler", "Doküman ihtiyacının yaşam döngüsü izlenebilirliğini destekler."],
        ["Hazırlanmış veya güncellenmiş doküman", bp_title("SUP.7.BP5"), "Süreç, proje veya destek faaliyeti kapsamında kullanılacak kontrollü dokümanı oluşturmak", "Zorunlu", "İlgili süreç/proje doküman alanı", "İlgili şablon ve yazım kurallarına uygun hazırlanmalıdır."],
        ["İÜC.BİDB.LST.003 - Doküman Gözden Geçirme Kaydı", bp_title("SUP.7.BP6"), "Doküman gözden geçirme, uygunluk ve düzeltme kayıtlarını izlemek", "Zorunlu", "03 - Kayıtlar ve Listeler", "Gözden geçirme sonucu, tarih ve sorumlu bilgisi içermelidir."],
        ["İÜC.BİDB.LST.001 - Aktif Dokümanlar Listesi", bp_title("SUP.7.BP7"), "Onaylı ve aktif doküman envanterini yönetmek", "Zorunlu", "SRÇ.001 alt sayfası", "Aktif dokümanların kod, ad, sürüm, durum ve erişim bilgilerini içermelidir."],
        ["İÜC.BİDB.LST.002 - Doküman Değişiklik Kaydı", bp_title("SUP.7.BP8"), "Doküman değişikliklerini, bakım kayıtlarını ve pasife alma/arşivleme kararlarını izlemek", "Zorunlu", "03 - Kayıtlar ve Listeler", "Değişiklik gerekçesi, tarih, sorumlu ve etkilenen doküman bilgisi içermelidir."],
        ["İÜC.BİDB.LST.012 - Süreç Yaygınlaştırma ve Bilgilendirme Kaydı", bp_title("SUP.7.BP7"), "Yayımlanan veya güncellenen dokümanlar hakkında ilgili tarafların bilgilendirildiğini izlemek", "Koşullu", "03 - Kayıtlar ve Listeler", "Yaygınlaştırma gereken dokümanlar için hedef kitle ve bilgilendirme tarihi izlenir."],
        ["İÜC.BİDB.FRM.001 - Süreç Gözden Geçirme Formu (İÜC.BİDB.SRÇ.001)", "Süreç gözden geçirme", "SRÇ.001 BP/GP uygunluk durumunu ve tamamlayıcı aksiyonları izlemek", "Zorunlu", "SRÇ.001 alt sayfası", "BP/GP durumları ve aksiyon kayıtları güncel tutulmalıdır."],
    ]))

    parts.append("<h2>5. Kalite Kriterleri Kontrol Matrisi</h2>")
    parts.append(table(["İş Ürünü", "Kalite Kriteri", "Kontrol Sorusu", "Kontrol Yöntemi", "Kontrol Sorumlusu", "Kabul Ölçütü", "Uygunsuzluk / Tamamlayıcı Aksiyon"], [
        ["PRS.001", "Dokümantasyon stratejisi tanımlı olmalı", "Dokümantasyon yönetim yaklaşımı, kapsamı ve sorumlulukları tanımlı mı?", "Doküman gözden geçirme", "Süreç Sahibi / Kalite Danışmanı", "Strateji ve uygulama kuralları açık, onaylı ve erişilebilir olmalıdır.", "Eksikse prosedür revize edilir ve onaya sunulur."],
        ["Şablonlar", "Geçerli şablon kullanılmalı", "Doküman türü için aktif şablon kullanılmış mı?", "Şablon kontrolü", "Doküman Hazırlayan / Gözden Geçiren", "Doküman aktif şablon yapısına uygun olmalıdır.", "Yanlış şablon kullanılmışsa doküman güncel şablona göre düzeltilir."],
        ["LST.005", "Yaşam döngüsü doküman ihtiyacı izlenebilir olmalı", "Doküman ihtiyacı yaşam döngüsü aşaması ile ilişkilendirilmiş mi?", "Liste kontrolü", "Süreç Sahibi", "Aşama, doküman türü ve sorumluluk bilgisi tanımlı olmalıdır.", "Eksik ilişki varsa matris güncellenir."],
        ["Hazırlanmış/güncellenmiş doküman", "Zorunlu alanlar ve içerik tamamlanmış olmalı", "Doküman kodu, adı, durum, sürüm, tarih, sahiplik ve içerik alanları dolu mu?", "Doküman kalite kontrolü", "Gözden Geçiren", "Zorunlu alanlar dolu ve içerik kullanılabilir olmalıdır.", "Eksik alanlar tamamlanır."],
        ["LST.003", "Gözden geçirme kaydı izlenebilir olmalı", "Gözden geçirme sonucu, tarih, sorumlu ve karar bilgisi var mı?", "Kayıt kontrolü", "Kalite Güvence / Süreç Sahibi", "Gözden geçirme kararı ve varsa aksiyonlar kayıt altına alınmış olmalıdır.", "Kayıt eksikse tamamlanır."],
        ["LST.001", "Aktif doküman envanteri güncel olmalı", "Aktif dokümanın kodu, adı, sürümü, durumu ve erişim bilgisi listede var mı?", "Liste kontrolü", "Doküman Sorumlusu", "Aktif dokümanlar tekil ve güncel listelenmelidir.", "Eksik kayıt eklenir veya güncellenir."],
        ["LST.002", "Değişiklik kayıtları izlenebilir olmalı", "Değişikliğin gerekçesi, tarihi, sorumlusu ve etkilenen doküman bilgisi var mı?", "Kayıt kontrolü", "Doküman Sorumlusu", "Değişiklik kayıtları doküman geçmişiyle tutarlı olmalıdır.", "Eksik değişiklik kaydı tamamlanır."],
        ["LST.012", "Yaygınlaştırma kayıtları gerektiğinde tutulmalı", "Yayımlanan/güncellenen doküman için hedef kitle bilgilendirilmiş mi?", "Kayıt kontrolü", "Süreç Sahibi", "Bilgilendirme gereken durumlarda hedef kitle ve tarih kaydı bulunmalıdır.", "Eksikse bilgilendirme ve kayıt tamamlanır."],
        ["FRM.001", "BP/GP uygunluk izlenebilirliği sağlanmalı", "SRÇ.001 BP/GP durumu, kanıt ve aksiyon bilgileri formda izleniyor mu?", "Form kontrolü", "Kalite Danışmanı", "BP/GP satırları güncel kanıt ve durum bilgisi içermelidir.", "Eksikse form güncellenir ve aksiyon kapatma takibi yapılır."],
    ]))

    parts.append("<h2>6. Sürüm Geçmişi</h2>")
    parts.append(table(["Sürüm", "Tarih", "Açıklama", "Hazırlayan/Güncelleyen", "Gözden Geçiren", "Onay"], [
        ["v1.0", "01-09-2025", "Dokümantasyon Süreci iş ürünleri ve kalite kriterleri listesi oluşturuldu.", "Soner DEDEOĞLU - Kalite Danışmanı", "Levent BAYEZİT - Proje Yöneticisi", "Mustafa Nusret SARISAKAL - BİD Başkanı"],
    ]))

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


def update_page_yaml() -> None:
    path = PAGE_DIR / "page.yaml"
    meta = load_yaml(path) if path.exists() else {}
    meta.update({
        "title": TITLE,
        "status": "active",
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "template": TEMPLATE_NAME,
        "document_code": "İÜC.BİDB.LST.008",
        "document_type": "Liste",
        "related_process": PROCESS_CODE,
        "storage_file": "body.storage.xhtml",
        "view_file": "body.view.html",
    })
    write_yaml(path, meta)


def main() -> None:
    if not PAGE_DIR.exists():
        raise FileNotFoundError(f"Expected existing LST.008 page directory not found: {PAGE_DIR}")
    storage = build_storage()
    (PAGE_DIR / "body.storage.xhtml").write_text(storage, encoding="utf-8")
    (PAGE_DIR / "body.view.html").write_text(build_view(storage), encoding="utf-8")
    update_page_yaml()
    print("[DONE] SRÇ.001 LST.008 created/replaced in existing page directory.")
    print(f"[PATH] {PAGE_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
