#!/usr/bin/env python3
from __future__ import annotations

import html
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "confluence/pages/000-root-iuc-bidb-spice-2026-level-3/05-kilavuzlar/klv-001-dokuman-yazim-kurallari-talimati"
STORAGE_PATH = DOC_DIR / "body.storage.xhtml"
VIEW_PATH = DOC_DIR / "body.view.html"
PAGE_YAML = DOC_DIR / "page.yaml"

TITLE = "KLV.001 - Doküman Yazım Kuralları Talimatı"

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
code{background:#f6f8fa;padding:2px 4px;border-radius:4px}
pre{background:#f6f8fa;padding:12px 16px;border-radius:6px;overflow:auto}
""".strip()


def e(value: object) -> str:
    return html.escape(str(value), quote=False)


def p(text: str) -> str:
    return f"<p>{e(text)}</p>"


def ul(items: list[str]) -> str:
    return "<ul>" + "".join(f"<li>{item}</li>" for item in items) + "</ul>"


def table(headers: list[str], rows: list[list[str]]) -> str:
    head = "".join(f"<th>{e(h)}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>" for row in rows)
    return f'<table class="wrapped"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>'


def code_block(text: str) -> str:
    return f"<pre><code>{e(text)}</code></pre>"


def build_storage() -> str:
    parts: list[str] = []

    parts.append("<h2>1. Kılavuz / Talimat Bilgileri</h2>")
    parts.append(table(["Alan", "Değer"], [
        ["Kurum", "İstanbul Üniversitesi - Cerrahpaşa Bilgi İşlem Daire Başkanlığı"],
        ["Kılavuz / Talimat Kodu ve Adı", "KLV.001 - Doküman Yazım Kuralları Talimatı"],
        ["Kılavuz / Talimat Referansı", "SRÇ.001 - Dokümantasyon Süreci"],
        ["Kılavuz / Talimat Sahibi", "Proje Geliştirme Yönetimi"],
        ["Durum", "Onaylı"],
        ["Sürüm", "v1.0"],
        ["Yürürlük Tarihi", "15-02-2025"],
        ["Son Gözden Geçirme Tarihi", "15-02-2025"],
    ]))

    parts.append("<h2>2. Amaç</h2>")
    parts.append(p(
        "Bu talimatın amacı, İÜC BİDB SPICE 2026 Level 3 çalışması kapsamında hazırlanacak süreç, prosedür, kılavuz, talimat, şablon, form, liste, plan, politika ve kayıt dokümanlarında kullanılacak yazım, başlık, numaralandırma, tablo, sürüm ve yayın kurallarını tanımlamaktır."
    ))
    parts.append(p(
        "Talimat; dokümanların Confluence üzerinde okunabilir, yerel repository içinde izlenebilir, sürüm geçmişiyle takip edilebilir ve denetimde kanıt olarak sunulabilir yapıda hazırlanmasını sağlar."
    ))

    parts.append("<h2>3. Kapsam</h2>")
    parts.append(p("Bu talimat aşağıdaki doküman türleri için uygulanır:"))
    parts.append(ul([
        "süreç tanımı dokümanları,",
        "prosedürler,",
        "kılavuz ve talimatlar,",
        "şablonlar,",
        "formlar,",
        "kayıt ve liste dokümanları,",
        "politikalar,",
        "planlar,",
        "süreçlere bağlı değerlendirme, ölçüm ve kanıt dokümanları."
    ]))
    parts.append(p(
        "Talimat, hem Confluence üzerinde yönetilen dokümanları hem de repository içinde tutulan <code>body.storage.xhtml</code>, <code>body.view.html</code> ve <code>page.yaml</code> dosyalarını kapsar."
    ))

    parts.append("<h2>4. Kapsam Dışı</h2>")
    parts.append(p("Aşağıdaki içerikler bu talimatın kapsamı dışındadır:"))
    parts.append(ul([
        "geçici kişisel çalışma notları,",
        "resmi yazışma ve EBYS belgeleri,",
        "sistemlerin otomatik oluşturduğu ham log kayıtları,",
        "yayınlanmayan ara taslaklar,",
        "denetim kanıtı olarak kullanılmayacak kişisel veya geçici dosyalar."
    ]))

    parts.append("<h2>5. Referanslar</h2>")
    parts.append(table(["Referans", "Açıklama"], [
        ["SRÇ.001 - Dokümantasyon Süreci", "Doküman yönetiminin temel süreci"],
        ["PRS.001 - Yazılım Projeleri Dokümantasyon Prosedürü", "Yazılım projelerinde dokümantasyon stratejisi"],
        ["LST.001 - Aktif Dokümanlar Listesi", "Genel kullanıma açık aktif doküman envanteri"],
        ["SRÇ.XXX.Ş - Süreç Tanımı Şablonu", "Süreç dokümanları için yapı referansı"],
        ["PRS.XXX.Ş - Prosedür Tanımı Şablonu", "Prosedür dokümanları için yapı referansı"],
        ["KLV.XXX.Ş - Kılavuz ve Talimat Tanımı Şablonu", "Kılavuz ve talimat dokümanları için yapı referansı"],
        ["LST.008.Ş / LST.009.Ş / LST.010.Ş", "Liste ve matris dokümanları için güncel şablon ailesi"],
    ]))

    parts.append("<h2>6. Terimler ve Kısaltmalar</h2>")
    parts.append(table(["Terim / Kısaltma", "Açıklama"], [
        ["Doküman", "Süreç, prosedür, kılavuz, plan, politika veya benzeri yapıda yönetilen yazılı bilgi"],
        ["Şablon", "Belirli doküman türlerinin ortak yapıda hazırlanması için kullanılan boş veya yönlendirici doküman"],
        ["Kayıt", "Bir faaliyetin gerçekleştiğini, kararın alındığını veya kontrolün yapıldığını gösteren kanıt"],
        ["Storage", "Confluence sayfasının yayınlanabilir kaynak HTML/XHTML içeriği"],
        ["View", "Yerel inceleme için üretilmiş görüntülenebilir HTML dosyası"],
        ["page.yaml", "Confluence sayfa kimliği, başlık, parent ve dosya bilgilerini tutan metadata dosyası"],
        ["Publish", "Repository içeriğinin Confluence sayfalarına aktarılması"],
        ["Export", "Confluence içeriğinin repository’ye geri alınması"],
    ]))

    parts.append("<h2>7. Genel İlkeler</h2>")
    parts.append(table(["İlke", "Açıklama"], [
        ["Tutarlılık", "Aynı tür dokümanlarda aynı bilgi bölümü, başlık mantığı, tablo düzeni ve sürüm geçmişi yapısı kullanılır."],
        ["Gerektiği kadar yapı", "Süreç dokümanındaki tüm başlıklar prosedür, kılavuz veya liste dokümanlarına taşınmaz; her doküman kendi içerik ihtiyacına göre yapılandırılır."],
        ["Tekil kaynak", "Confluence yayın ortamıdır; repository ise kaynak, izleme ve otomasyon ortamıdır."],
        ["İzlenebilirlik", "Doküman kodu, adı, sürüm, tarih, durum ve sorumluluk bilgileri açıkça belirtilir."],
        ["Denetlenebilirlik", "Dokümanlar, denetimde kanıt olarak sunulabilecek açıklıkta ve sürüm geçmişiyle yönetilir."],
        ["Sadelik", "Başlık ve tablolar gereksiz detayla şişirilmez; kullanıcının uygulayacağı bilgi açık yazılır."],
        ["Manuel kontrol", "Otomasyonla üretilen dokümanlar yayın öncesinde yerel viewer veya Confluence üzerinden gözden geçirilir."],
    ]))

    parts.append("<h2>8. Doküman Türleri ve Temel Yapı Kuralları</h2>")
    parts.append(table(["Doküman Türü", "Temel Yapı Kuralı", "Not"], [
        ["Süreç Tanımı", "<code>1. Süreç Bilgileri</code> bölümüyle başlar.", "Süreç akışı, faaliyetler, ölçüm, etkileşim ve uyarlama bölümleri içerir."],
        ["Prosedür", "<code>1. Prosedür Bilgileri</code> bölümüyle başlar.", "Süreç şablonundaki tüm başlıkları almak zorunda değildir; prosedür esasları ve uygulama stratejisi öne çıkar."],
        ["Kılavuz / Talimat", "<code>1. Kılavuz / Talimat Bilgileri</code> bölümüyle başlar.", "Kural, örnek, format ve uygulama açıklamaları öne çıkar."],
        ["Liste / Matris", "<code>1. Liste Özeti</code> veya ilgili liste bilgi bölümüyle başlar.", "Liste şablonlarında <code>0. Liste Hakkında</code> bulunur; gerçek listelerde bulunmaz."],
        ["Form", "Form türüne göre özet veya değerlendirme bölümüyle başlar.", "Form şablonlarında kullanım açıklaması bulunur; doldurulmuş formlarda gereksiz şablon notları yer almaz."],
        ["Şablon", "<code>0. Şablon Hakkında</code> bölümüyle başlar.", "0. bölüm sadece şablonlarda kullanılır."],
    ]))

    parts.append("<h2>9. Şablon ve Gerçek Doküman Ayrımı</h2>")
    parts.append(p(
        "Şablon dokümanları ile şablondan üretilen gerçek dokümanlar aynı başlık setini birebir taşımak zorunda değildir. Şablonlarda kullanım amacı, adlandırma kuralı ve şablon sürüm geçmişi bulunur; gerçek dokümanlarda ise uygulanan içeriğe ait bilgi ve kayıtlar bulunur."
    ))
    parts.append(table(["Kural", "Şablon Dokümanı", "Gerçek Doküman"], [
        ["0. bölüm kullanımı", "Bulunur. Örn. <code>0. Şablon Hakkında</code>, <code>0. Liste Hakkında</code>", "Bulunmaz."],
        ["Bilgi bölümü", "Şablonun kullanım alanını açıklar.", "Dokümanın gerçek kodunu, adını, sahibini, durumunu ve sürümünü açıklar."],
        ["Yer tutucu", "Kullanılabilir.", "Mümkün olduğunca kullanılmaz; gerçek değer yazılır."],
        ["Sürüm geçmişi", "Şablonun geçmişini gösterir.", "Gerçek dokümanın geçmişini gösterir."],
        ["İçerik notları", "Kullanım notu olarak bulunabilir.", "Denetim dokümanlarında gereksiz kullanım notları kaldırılır."],
    ]))

    parts.append("<h2>10. Bilgi Bölümü Kuralları</h2>")
    parts.append(p("Gerçek dokümanlarda ilk ana bölüm doküman türüne göre adlandırılır. Bu bölüm özet bilgi tablosu içerir. Tablo gereksiz kişi ve onay detaylarıyla büyütülmez; ana izlenebilirlik bilgilerini verir. Hazırlayan, gözden geçiren ve onaylayan bilgileri sürüm geçmişinde izlenir."))
    parts.append(table(["Doküman Türü", "İlk Bölüm Başlığı", "Tablodaki Temel Alanlar"], [
        ["Süreç", "1. Süreç Bilgileri", "Kurum; süreç kodu ve adı; süreç referansı; süreç sahibi; durum; sürüm; yürürlük tarihi; son gözden geçirme tarihi"],
        ["Prosedür", "1. Prosedür Bilgileri", "Kurum; prosedür kodu ve adı; prosedür referansı; prosedür sahibi; durum; sürüm; yürürlük tarihi; son gözden geçirme tarihi"],
        ["Kılavuz / Talimat", "1. Kılavuz / Talimat Bilgileri", "Kurum; kılavuz/talimat kodu ve adı; referans; sahibi; durum; sürüm; yürürlük tarihi; son gözden geçirme tarihi"],
        ["Liste", "1. Liste Özeti", "Liste kodu; ilgili süreç; kullanım amacı; sorumlu; durum; sürüm; tarih bilgileri"],
    ]))

    parts.append("<h2>11. Başlık ve Numaralandırma Kuralları</h2>")
    parts.append(table(["Seviye", "Kullanım", "Örnek"], [
        ["H1", "Confluence sayfa başlığı / doküman adı için kullanılır.", "KLV.001 - Doküman Yazım Kuralları Talimatı"],
        ["H2", "Ana bölüm başlığıdır ve numaralandırılır.", "1. Kılavuz / Talimat Bilgileri"],
        ["H3", "Alt bölüm başlığıdır ve gerektiğinde ilgili H2 numarasını takip eder.", "10.1. Tarih Formatı"],
        ["H4", "Zorunlu olmadıkça kullanılmaz.", "Özel durum açıklaması"],
    ]))
    parts.append(p("Başlıklar kısa, açıklayıcı ve doküman türünün amacına uygun yazılır. Süreç dokümanındaki başlıklar diğer doküman türlerine otomatik olarak kopyalanmaz."))

    parts.append("<h2>12. Doküman Kodlama ve Adlandırma Kuralları</h2>")
    parts.append(table(["Doküman Türü", "Kod Formatı", "Adlandırma Örneği"], [
        ["Süreç", "SRÇ.XXX", "SRÇ.001 - Dokümantasyon Süreci"],
        ["Prosedür", "PRS.XXX", "PRS.001 - Yazılım Projeleri Dokümantasyon Prosedürü"],
        ["Kılavuz / Talimat", "KLV.XXX", "KLV.001 - Doküman Yazım Kuralları Talimatı"],
        ["Liste", "LST.XXX", "LST.001 - Aktif Dokümanlar Listesi"],
        ["Form", "FRM.XXX", "FRM.001 - Süreç Gözden Geçirme Formu"],
        ["Şablon", "[TÜR].XXX.Ş", "PRS.XXX.Ş - Prosedür Tanımı Şablonu"],
    ]))
    parts.append(p("Sürece veya projeye özel üretilen kayıt niteliğindeki dokümanlarda ilgili süreç kodu parantez içinde belirtilir."))

    parts.append("<h2>13. Tablo Kullanımı</h2>")
    parts.append(p("Tablolar; bilgi özeti, sorumluluk, matris, kontrol listesi, ölçüm ve izlenebilirlik gerektiren alanlarda kullanılır. Uzun açıklamalar tablo içine sıkıştırılmaz; gerektiğinde tablodan önce veya sonra açıklayıcı paragraf kullanılır."))
    parts.append(table(["Kural", "Açıklama"], [
        ["Başlık satırı", "Her tabloda açık başlık satırı bulunur."],
        ["Boş hücre", "Boş hücre bırakılmamalıdır; bilinmeyen alanlarda yer tutucu veya '-' kullanılır."],
        ["Uzun açıklama", "Uzun metinler tablo dışında paragraf olarak yazılır."],
        ["Denetim odaklılık", "Tablo alanları denetimde izlenebilir bilgi sağlayacak şekilde seçilir."],
        ["Aşırı detaydan kaçınma", "Aynı bilgi farklı tablolarda gereksiz tekrar edilmez."],
    ]))

    parts.append("<h2>14. Tarih, Sürüm ve Durum Kuralları</h2>")
    parts.append("<h3>14.1. Tarih Formatı</h3>")
    parts.append(p("Tüm tarih alanlarında <code>GG-AA-YYYY</code> formatı kullanılır."))
    parts.append(code_block("15-02-2025"))

    parts.append("<h3>14.2. Sürüm Formatı</h3>")
    parts.append(table(["Sürüm", "Kullanım"], [
        ["v0.1", "İlk taslak"],
        ["v0.2, v0.3", "Taslak revizyonları"],
        ["v1.0", "İlk onaylı yayın"],
        ["v1.1, v1.2", "Küçük güncellemeler"],
        ["v2.0", "Büyük yapısal değişiklik"],
    ]))

    parts.append("<h3>14.3. Durum Değerleri</h3>")
    parts.append(table(["Durum", "Kullanım"], [
        ["Taslak", "Hazırlanmakta olan doküman"],
        ["Gözden Geçirildi", "Gözden geçirme tamamlanmış, onay bekleyen doküman"],
        ["Onaylı", "Onaylanmış ve kullanıma hazır doküman"],
        ["Aktif", "Kullanımda olan geçerli doküman veya şablon"],
        ["Pasif", "Kullanımdan kaldırılmış doküman"],
        ["Arşiv", "Geçmiş kayıt amacıyla saklanan doküman"],
    ]))

    parts.append("<h2>15. Sürüm Geçmişi Kuralları</h2>")
    parts.append(p("Her gerçek dokümanda sürüm geçmişi son bölümde bulunur. Bu tabloda dokümanın hazırlanma, gözden geçirme ve onay bilgileri izlenir."))
    parts.append(table(["Alan", "Kural"], [
        ["Sürüm", "v0.1, v1.0 gibi sürüm değeri yazılır."],
        ["Tarih", "İlgili sürümün tarihi yazılır."],
        ["Açıklama", "Değişikliğin kısa açıklaması yazılır."],
        ["Hazırlayan / Güncelleyen", "Dokümanı hazırlayan veya güncelleyen rol/kişi yazılır."],
        ["Gözden Geçiren", "Gözden geçiren rol/kişi yazılır."],
        ["Onay", "Onaylayan rol/kişi yazılır."],
    ]))

    parts.append("<h2>16. Confluence ve Repository Kullanım Kuralları</h2>")
    parts.append(p("Dokümanlar Confluence üzerinde yayımlanır; repository ise kaynak yönetimi, yerel kontrol, otomasyon ve değişiklik izleme amacıyla kullanılır."))
    parts.append(table(["Dosya / İşlem", "Kullanım"], [
        ["body.storage.xhtml", "Confluence'a gönderilecek asıl sayfa içeriğidir."],
        ["body.view.html", "Yerel olarak görsel kontrol amacıyla kullanılan HTML dosyasıdır."],
        ["page.yaml", "Confluence sayfa kimliği, başlık, parent ve dosya bilgisini tutar."],
        ["viewer/pages.json", "Yerel viewer sayfa listesidir."],
        ["publish", "Repository içeriğini Confluence'a aktarır."],
        ["export", "Confluence içeriğini repository'ye geri alır."],
    ]))
    parts.append(p("Yayın öncesinde dry-run çıktısı kontrol edilir. Beklenmeyen sayfa güncellemesi varsa publish yapılmadan önce neden araştırılır."))

    parts.append("<h2>17. Local Viewer ve Kontrol Kuralları</h2>")
    parts.append(p("Otomasyonla üretilen veya güncellenen dokümanlar publish öncesinde yerel olarak kontrol edilir. Bunun için ilgili <code>body.view.html</code> dosyası veya local viewer kullanılır."))
    parts.append(code_block("python scripts/build_local_viewer.py\npython -m http.server 8080\nhttp://localhost:8080/viewer/"))
    parts.append(p("Storage içeriği değiştirildiğinde bazı durumlarda <code>body.view.html</code> dosyasının ayrıca yeniden üretilmesi gerekebilir. Görsel kontrol yalnızca <code>viewer/pages.json</code> üretimiyle sınırlı değildir."))

    parts.append("<h2>18. Publish, Export ve Commit Disiplini</h2>")
    parts.append(table(["Adım", "Kural"], [
        ["Taslak üretim", "Önce lokal dosyalar oluşturulur ve viewer üzerinden kontrol edilir."],
        ["Commit", "Onaylanan lokal değişiklikler anlamlı commit mesajı ile kaydedilir."],
        ["Dry-run", "Confluence publish öncesinde mutlaka dry-run çalıştırılır."],
        ["Publish", "Sadece beklenen sayfalar güncellenecekse publish yapılır."],
        ["Export", "Publish sonrası Confluence içeriği repository’ye geri alınır."],
        ["Metadata temizliği", "Sadece page.yaml timestamp veya rapor gürültüsü varsa commit’e dahil edilmez."],
        ["Final commit", "Publish sonrası anlamlı içerik farkları commitlenir ve push edilir."],
    ]))

    parts.append("<h2>19. İçerik Yazım ve Üslup Kuralları</h2>")
    parts.append(table(["Kural", "Açıklama"], [
        ["Dil", "Dokümanlar Türkçe yazılır."],
        ["Üslup", "Resmi, sade, uygulanabilir ve denetimde anlaşılır ifade kullanılır."],
        ["Kişi adı", "Zorunlu olmadıkça kişi adı yerine rol veya birim adı tercih edilir; onay ve sürüm geçmişinde kişi adı kullanılabilir."],
        ["Kısaltma", "İlk kullanımda açıklanır."],
        ["Belirsizlik", "Gerekirse, mümkünse gibi ifadeler yalnızca gerçekten koşullu durumlarda kullanılır."],
        ["Tekrar", "Aynı bilgi birden fazla bölümde gereksiz tekrarlanmaz."],
        ["Kanıt odaklılık", "Süreç, kayıt, ölçüm ve kontrol ifadeleri denetimde gösterilebilir kanıta bağlanır."],
    ]))

    parts.append("<h2>20. Görsel, Diyagram ve Kod Bloğu Kullanımı</h2>")
    parts.append(p("Görseller, diyagramlar ve kod blokları yalnızca içeriğin anlaşılmasını kolaylaştırdığı durumlarda kullanılır. Diyagram veya örnek kod kullanıldığında ilgili açıklama metinle desteklenir."))
    parts.append(table(["Kullanım", "Kural"], [
        ["Diyagram", "Kısa, okunabilir ve metinle desteklenmiş olmalıdır."],
        ["Kod bloğu", "Komut, dosya yolu veya sabit format göstermek için kullanılır."],
        ["Görsel", "Dokümanın ana kontrol bilgisini tek başına taşımamalıdır."],
        ["Mermaid", "Confluence ortamında destek yoksa alternatif görsel veya tablo kullanılmalıdır."],
    ]))

    parts.append("<h2>21. Sürüm Geçmişi</h2>")
    parts.append(table(["Sürüm", "Tarih", "Açıklama", "Hazırlayan/Güncelleyen", "Gözden Geçiren", "Onay"], [
        ["v0.1", "01-02-2025", "İlk taslak oluşturuldu.", "Asel GÜL - Yazılım/Program Analisti", "Soner DEDEOĞLU - Kalite Danışmanı", "-"],
        ["v1.0", "15-02-2025", "Talimat onaylanarak yürürlüğe alındı.", "Asel GÜL - Yazılım/Program Analisti", "Soner DEDEOĞLU - Kalite Danışmanı", "Levent BAYEZİT - Dokümantasyon Süreç Sahibi"],
    ]))

    return "".join(parts) + "\n"


def build_view(storage: str) -> str:
    return f"""<!doctype html>
<html lang="tr">
<head>
  <meta charset="utf-8">
  <title>{html.escape(TITLE)}</title>
  <style>{CSS}</style>
</head>
<body>
<main class="confluence-page">
<h1>{html.escape(TITLE)}</h1>
{storage}
</main>
</body>
</html>
"""


def main() -> None:
    storage = build_storage()
    STORAGE_PATH.write_text(storage, encoding="utf-8")
    VIEW_PATH.write_text(build_view(storage), encoding="utf-8")
    print(f"[DONE] Rebuilt {TITLE}")


if __name__ == "__main__":
    main()
