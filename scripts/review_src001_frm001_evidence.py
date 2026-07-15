#!/usr/bin/env python3
from __future__ import annotations

import html
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "confluence/pages/000-root-iuc-bidb-spice-2026-level-3/01-surec-dokumanlari/src-001-dokumantasyon-sureci/frm-001-surec-gozden-gecirme-formu-src-001"
STORAGE = DOC_DIR / "body.storage.xhtml"
VIEW = DOC_DIR / "body.view.html"
TITLE = "FRM.001 - Süreç Gözden Geçirme Formu (SRÇ.001)"

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


def e(v: object) -> str:
    return html.escape(str(v), quote=False)


def ul(items: list[str]) -> str:
    return "<ul>" + "".join(f"<li>{e(i)}</li>" for i in items) + "</ul>"


def table(headers: list[str], rows: list[list[str]]) -> str:
    head = "".join(f"<th>{e(h)}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>" for row in rows)
    return f'<table class="wrapped"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>'


def durum(pct: int) -> str:
    if pct == 0:
        return "YOK"
    if pct <= 40:
        return "ZAYIF"
    if pct < 70:
        return "DAĞINIK"
    return "VAR"


def d(pct: int) -> str:
    return f"%{pct} - {durum(pct)}"


BP = [
    ["SUP.7.BP1", "Dokümantasyon yönetim stratejisini geliştir", 90,
     "Dokümantasyon stratejisi SRÇ.001 ana süreci ile kurulmuş, yazılım projelerine özel uygulama PRS.001 ile ayrıştırılmıştır.",
     ["SRÇ.001 - Dokümantasyon Süreci", "PRS.001 - Yazılım Projeleri Dokümantasyon Prosedürü", "LST.005.Ş - Yaşam Döngüsü Doküman Üretim Matrisi Şablonu", "Soru Bankası Projesi / LST.005 (SB) taslak kaydı"],
     "-"],
    ["SUP.7.BP2", "Doküman standartlarını oluştur", 95,
     "Yazım, başlık, tablo, sürüm ve şablon kullanımı kuralları tanımlanmış; ana doküman türleri için şablon ailesi güncellenmiştir.",
     ["KLV.001 - Doküman Yazım Kuralları Talimatı", "SRÇ.XXX.Ş", "PRS.XXX.Ş", "KLV.XXX.Ş", "LST.001.Ş, LST.003.Ş, LST.005.Ş, LST.007.Ş, LST.008.Ş, LST.009.Ş, LST.010.Ş"],
     "-"],
    ["SUP.7.BP3", "Doküman gereksinimlerini belirle", 85,
     "SRÇ.001 için iş ürünleri, kalite kriterleri ve genel/proje özel doküman gereksinimleri ayrı yapılarda tanımlanmıştır.",
     ["LST.008 - İş Ürünleri ve Kalite Kriterleri Listesi (SRÇ.001)", "LST.001 - Aktif Dokümanlar Listesi", "PRS.001", "LST.005.Ş"],
     "-"],
    ["SUP.7.BP4", "Üretilecek dokümanları tanımla", 90,
     "Genel aktif dokümanlar, süreç özel kayıtlar ve proje özel dokümanlar ayrı yerlerde izlenebilir hale getirilmiştir.",
     ["LST.001 - Aktif Dokümanlar Listesi", "SRÇ.001 altındaki LST.007/LST.008/LST.009/LST.010/FRM.001", "Soru Bankası Projesi / LST.005 (SB)"],
     "-"],
    ["SUP.7.BP5", "Dokümanları geliştir", 95,
     "SRÇ.001 kapsamında ana süreç dokümanı, destek prosedürü, yazım talimatı, şablonlar ve süreç kayıtları oluşturulmuştur.",
     ["SRÇ.001", "PRS.001", "KLV.001", "LST.001", "LST.007", "LST.008", "LST.009", "LST.010", "Confluence publish/export ve Git commit kayıtları"],
     "-"],
    ["SUP.7.BP6", "Dokümanları kontrol et", 65,
     "Gözden geçirme pratiği uygulanıyor; ancak LST.003 gerçek kayıtlarının son revizyonları kapsayacak şekilde sistematik doldurulması gerekiyor.",
     ["Bu FRM.001 gözden geçirme formu", "LST.003.Ş - Doküman Gözden Geçirme Kaydı Şablonu", "Doküman sürüm geçmişi alanları", "Confluence düzenleme kayıtları"],
     "SRÇ.001, PRS.001, KLV.001, LST.001 ve LST.007 için LST.003 gerçek gözden geçirme kayıtları oluşturulmalı."],
    ["SUP.7.BP7", "Dokümanları dağıt", 90,
     "Dokümanlar Confluence sayfa ağacında yayımlanmış, LST.001 ile genel doküman konumları görünür hale getirilmiştir.",
     ["Confluence sayfa ağacı", "LST.001 - Aktif Dokümanlar Listesi", "publish_confluence_tree.py raporları"],
     "-"],
    ["SUP.7.BP8", "Dokümanları sürdür", 60,
     "Bakım ve arşivleme yaklaşımı kullanılıyor; ancak LST.002 gerçek değişiklik kayıtlarının son revizyonları kapsayacak şekilde tamamlanması gerekiyor.",
     ["LST.002 - Doküman Değişiklik Kaydı", "Doküman sürüm geçmişleri", "Arşiv - Kaldırılan Şablonlar", "Git commit geçmişi"],
     "Son şablon ve doküman revizyonları için LST.002 değişiklik kayıtları tamamlanmalı."],
]

GP = [
    ["PA 2.1", "GP 2.1.1", "Süreç performans hedeflerini belirle", 90, "SRÇ.001, PRS.001 ve bağlı LST kayıtlarıyla süreç performansı yönetilebilir hale getirilmiştir.", ["SRÇ.001", "PRS.001", "LST.009"], "-"],
    ["PA 2.1", "GP 2.1.2", "Süreç performansını planla ve izle", 85, "RACI, faaliyetler ve ölçüm seti ile planlama/izleme yapısı kurulmuştur.", ["SRÇ.001", "LST.009", "LST.010"], "-"],
    ["PA 2.1", "GP 2.1.3", "Süreç performansı için kaynakları sağla", 80, "Confluence, repository ve kaynak sistem yaklaşımı tanımlanmıştır.", ["PRS.001", "KLV.001", "Confluence/repository yapısı"], "-"],
    ["PA 2.1", "GP 2.1.4", "Sorumlulukları ata", 85, "Roller ve sorumluluklar LST.010 ve süreç dokümanı ile atanmıştır.", ["LST.010", "SRÇ.001"], "-"],
    ["PA 2.1", "GP 2.1.5", "Süreç performansını izle", 85, "LST.009 ve FRM.001 ile izleme ve değerlendirme yapılmaktadır.", ["LST.009", "FRM.001"], "-"],
    ["PA 2.1", "GP 2.1.6", "Uyumsuzlukları ve aksiyonları yönet", 75, "Aksiyonlar FRM.001 içinde tanımlanıyor; kapanışların LST.002/LST.003 ile ilişkilendirilmesi güçlendirilmeli.", ["FRM.001", "LST.002", "LST.003.Ş"], "-"],

    ["PA 2.2", "GP 2.2.1", "İş ürünü gereksinimlerini belirle", 90, "LST.008 ile iş ürünleri ve kalite kriterleri tanımlıdır.", ["LST.008"], "-"],
    ["PA 2.2", "GP 2.2.2", "İş ürünlerini dokümante et ve kontrol et", 85, "Süreç iş ürünleri ve kayıtları oluşturulmuştur.", ["SRÇ.001", "LST.001", "LST.007", "LST.008", "LST.009", "LST.010"], "-"],
    ["PA 2.2", "GP 2.2.3", "İş ürünlerini gözden geçir ve ayarla", 75, "Confluence/repository yapısı kontrolü destekliyor; LST.003 gerçek kayıtları güçlendirilmeli.", ["Confluence", "Git", "LST.003.Ş"], "-"],
    ["PA 2.2", "GP 2.2.4", "İş ürünlerine erişimi ve dağıtımı sağla", 80, "Confluence ve LST.001 ile erişim/konum bilgisi görünürdür.", ["Confluence", "LST.001"], "-"],

    ["PA 3.1", "GP 3.1.1", "Standart süreci tanımla", 90, "SRÇ.001 ve destek dokümanlarıyla standart süreç tanımlıdır.", ["SRÇ.001", "PRS.001", "KLV.001"], "-"],
    ["PA 3.1", "GP 3.1.2", "Standart sürecin sırasını ve etkileşimlerini tanımla", 85, "Faaliyetler ve etkileşimler LST.007 ile desteklenmiştir.", ["SRÇ.001", "LST.007"], "-"],
    ["PA 3.1", "GP 3.1.3", "Gerekli yetkinlik ve rolleri tanımla", 80, "LST.010 ve süreç dokümanı roller açısından yeterlidir.", ["LST.010", "SRÇ.001"], "-"],
    ["PA 3.1", "GP 3.1.4", "Altyapı ve çalışma ortamını tanımla", 85, "Confluence, repository ve publish/export akışı destek altyapıyı oluşturur.", ["KLV.001", "PRS.001", "publish/export kayıtları"], "-"],
    ["PA 3.1", "GP 3.1.5", "İzleme ve uygunluk yöntemlerini belirle", 75, "LST.009 ve FRM.001 ile izleme yöntemi tanımlıdır; dönemsel veri birikimi sürdürülecek.", ["LST.009", "FRM.001"], "-"],

    ["PA 3.2", "GP 3.2.1", "Tanımlı süreci uygula", 85, "SRÇ.001 ve bağlı dokümanlar yayımlanmış ve uygulanabilir durumdadır.", ["SRÇ.001", "PRS.001", "KLV.001"], "-"],
    ["PA 3.2", "GP 3.2.2", "Rolleri ve sorumlulukları uygula", 80, "RACI ve süreç sorumlulukları uygulanabilir biçimde tanımlanmıştır.", ["LST.010"], "-"],
    ["PA 3.2", "GP 3.2.3", "Kaynak ve bilgi kullanımını sağla", 70, "Kaynak sistemler ve dokümantasyon alanları hazırdır; kurum içi kullanım kanıtları birikmeye devam etmelidir.", ["PRS.001", "KLV.001", "Confluence"], "-"],
    ["PA 3.2", "GP 3.2.4", "Tanımlı süreci yaygınlaştır", 65, "Süreç yayımlanmıştır; ancak LST.012 gerçek yaygınlaştırma/bilgilendirme kayıtları henüz tamamlanmamıştır.", ["LST.012.Ş", "Confluence"], "LST.012 gerçek yaygınlaştırma ve bilgilendirme kayıtları doldurulmalı."],
    ["PA 3.2", "GP 3.2.5", "Süreç iş ürünlerini üret ve kontrol et", 70, "İş ürünleri üretilmiş ve publish/export kayıtları oluşmuştur; düzenli kullanım kanıtı biriktirme sürdürülmeli.", ["LST.001", "LST.007", "LST.008", "LST.009", "LST.010"], "-"],
    ["PA 3.2", "GP 3.2.6", "Süreç performansını analiz et ve iyileştir", 65, "FRM.001 ve LST.009 ile analiz yapılabilir; dönemsel ölçüm veri seti sınırlıdır.", ["FRM.001", "LST.009"], "LST.009 ölçüm sonuçları dönemsel olarak işlenmeli ve FRM.001 aksiyonlarıyla bağlanmalı."],
]


def build_storage() -> str:
    bp_avg = round(sum(r[2] for r in BP) / len(BP))
    gp_avg = round(sum(r[3] for r in GP) / len(GP))
    overall = round((bp_avg + gp_avg) / 2)

    parts = []
    parts.append("<h2>1. Değerlendirme Özeti</h2>")
    parts.append(table(["Alan", "Değer"], [
        ["Değerlendirilen Süreç", "SRÇ.001 - Dokümantasyon Süreci"],
        ["Standart Süreç Referansı", "ISO/IEC 15504-5 SUP.7 - Documentation"],
        ["Değerlendirme Tarihi", "13-07-2026"],
        ["Değerlendiren", "Soner DEDEOĞLU - Kalite Danışmanı"],
        ["Genel Sonuç", f"BP ortalaması %{bp_avg}, PA/GP ortalaması %{gp_avg}; genel durum %{overall} - {durum(overall)}"],
    ]))

    parts.append("<h2>2. Durum Değerleri</h2>")
    parts.append(table(["Durum", "Anlamı"], [
        ["YOK", "%0: Kanıt yok veya beklenti hiç karşılanmıyor."],
        ["ZAYIF", "%0-%40: Kısmi başlangıç kanıtı var; uygulama yetersiz."],
        ["DAĞINIK", "%40-%70: Kanıt var ancak sistematik, tamamlanmış veya tutarlı değil."],
        ["VAR", "%70-%100: Beklenti kanıtlarla büyük ölçüde karşılanıyor."],
    ]))

    parts.append("<h2>3. BP Takip Matrisi</h2>")
    parts.append(table(
        ["BP", "Standart Beklentisi", "Mevcut Karşılama", "Karşılayan Doküman / Kayıt", "Durum", "Eksik / Tamamlayıcı Aksiyon"],
        [[bp, exp, e(summary), ul(evs), d(pct), e("-" if durum(pct) == "VAR" else action)] for bp, exp, pct, summary, evs, action in BP]
    ))

    parts.append("<h2>4. PA / GP Takip Matrisi</h2>")
    parts.append(table(
        ["PA", "GP", "Standart Beklentisi", "Mevcut Karşılama", "Karşılayan Doküman / Kayıt", "Durum", "Eksik / Tamamlayıcı Aksiyon"],
        [[pa, gp, exp, e(summary), ul(evs), d(pct), e("-" if durum(pct) == "VAR" else action)] for pa, gp, exp, pct, summary, evs, action in GP]
    ))

    actions = []
    for bp, exp, pct, summary, evs, action in BP:
        if durum(pct) != "VAR":
            actions.append(["Yüksek" if pct < 60 else "Orta", e(action), bp, "31-07-2026"])
    for pa, gp, exp, pct, summary, evs, action in GP:
        if durum(pct) != "VAR":
            actions.append(["Yüksek" if pct < 60 else "Orta", e(action), gp, "31-07-2026"])

    parts.append("<h2>5. Öncelikli Tamamlama Listesi</h2>")
    parts.append(table(["Öncelik", "Aksiyon", "İlgili BP / GP", "Hedef Kapanış"], actions))

    return "".join(parts) + "\n"


def build_view(storage: str) -> str:
    return f"""<!doctype html>
<html lang="tr">
<head>
  <meta charset="utf-8">
  <title>{e(TITLE)}</title>
  <style>{CSS}</style>
</head>
<body>
<main class="confluence-page">
<h1>{e(TITLE)}</h1>
{storage}
</main>
</body>
</html>
"""


def main() -> None:
    storage = build_storage()
    STORAGE.write_text(storage, encoding="utf-8")
    VIEW.write_text(build_view(storage), encoding="utf-8")
    print("[DONE] FRM.001 şablon yapısı korunarak kanıta dayalı değerlendirme işlendi.")


if __name__ == "__main__":
    main()
