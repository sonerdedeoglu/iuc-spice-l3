#!/usr/bin/env python3
from __future__ import annotations

import html
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "confluence/pages/000-root-iuc-bidb-spice-2026-level-3/07-prosedurler/prs-001-yazilim-projeleri-dokumantasyon-proseduru"
STORAGE_PATH = DOC_DIR / "body.storage.xhtml"
VIEW_PATH = DOC_DIR / "body.view.html"

TITLE = "PRS.001 - Yazılım Projeleri Dokümantasyon Prosedürü"

CSS = """
body{margin:0;background:#fff;color:#172b4d;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;line-height:1.55}
.confluence-page{max-width:1100px;margin:0 auto;padding:32px 24px 56px}
h1,h2,h3,h4,h5,h6{margin:1.4em 0 .55em;line-height:1.25;color:#0f172a}
h1{margin-top:0;padding-bottom:12px;border-bottom:1px solid #d8dee4}
p{margin:0 0 12px}
table{width:100%;border-collapse:collapse;margin:16px 0;table-layout:auto}
th,td{border:1px solid #c9d1d9;padding:8px 10px;vertical-align:top}
th{background:#f6f8fa;font-weight:600;text-align:left}
code{background:#f6f8fa;padding:2px 4px;border-radius:4px}
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


def build_storage() -> str:
    parts: list[str] = []

    parts.append("<h2>1. Prosedür Bilgileri</h2>")
    parts.append(table(["Alan", "Değer"], [
        ["Kurum", "İstanbul Üniversitesi - Cerrahpaşa Bilgi İşlem Daire Başkanlığı"],
        ["Prosedür Kodu ve Adı", "PRS.001 - Yazılım Projeleri Dokümantasyon Prosedürü"],
        ["Prosedür Referansı", "SRÇ.001 - Dokümantasyon Süreci"],
        ["Prosedür Sahibi", "Levent BAYEZİT - Proje Yöneticisi"],
        ["Durum", "Onaylı"],
        ["Sürüm", "v1.0"],
        ["Yürürlük Tarihi", "15-02-2025"],
        ["Son Gözden Geçirme Tarihi", "15-02-2025"],
    ]))

    parts.append("<h2>2. Amaç</h2>")
    parts.append(p("Bu prosedürün amacı, İÜC BİDB tarafından yürütülen yazılım projelerinde üretilecek doküman ve kayıtların proje yaşam döngüsüne göre nasıl belirleneceğini, nerede tutulacağını, kim tarafından oluşturulacağını, hangi durumda gözden geçirileceğini ve denetim kanıtı olarak nasıl izleneceğini tanımlamaktır."))
    parts.append(p("Bu prosedür, SRÇ.001 - Dokümantasyon Süreci içinde tanımlanan kurumsal dokümantasyon yaklaşımını tekrar etmez; bu yaklaşımın yazılım projelerine özel uygulanma stratejisini belirler."))

    parts.append("<h2>3. Kapsam</h2>")
    parts.append(p("Bu prosedür, İÜC BİDB yazılım projelerinde proje başlangıcından bakım ve kapanış aşamasına kadar oluşan doküman ve kayıtları kapsar."))
    parts.append(ul([
        "proje yönetimi dokümanları ve kayıtları,",
        "gereksinim, analiz ve tasarım dokümanları,",
        "geliştirme, kod inceleme ve yapılandırma kayıtları,",
        "test, doğrulama ve kabul kayıtları,",
        "yayına alma, sürüm ve dağıtım kayıtları,",
        "değişiklik talebi, problem çözümü ve bakım kayıtları,",
        "toplantı, karar, onay ve izleme kayıtları."
    ]))

    parts.append("<h2>4. Kapsam Dışı</h2>")
    parts.append(p("Aşağıdaki içerikler bu prosedürün kapsamı dışındadır:"))
    parts.append(ul([
        "yazılım projeleri dışındaki kurumsal idari dokümanlar,",
        "kişisel çalışma notları ve geçici taslaklar,",
        "resmi yazışma ve EBYS belgeleri,",
        "denetim kanıtı olarak kullanılmayacak ham sistem logları,",
        "proje dışında oluşan operasyonel kayıtlar."
    ]))

    parts.append("<h2>5. Referanslar</h2>")
    parts.append(table(["Referans", "Açıklama"], [
        ["SRÇ.001 - Dokümantasyon Süreci", "Kurumsal dokümantasyon yönetimi süreci"],
        ["KLV.001 - Doküman Yazım Kuralları Talimatı", "Doküman yazım, başlık, tablo, sürüm ve yayın kuralları"],
        ["LST.001 - Aktif Dokümanlar Listesi", "Genel kullanıma açık aktif doküman envanteri"],
        ["LST.005 - Yaşam Döngüsü Doküman İhtiyaç Matrisi", "Yazılım proje yaşam döngüsüne göre beklenen doküman/kayıt ihtiyacı"],
        ["Jira / Confluence / Bitbucket / Bamboo / Drive", "Yazılım proje doküman ve kayıtlarının tutulduğu kaynak sistemler"],
    ]))

    parts.append("<h2>6. Terimler ve Kısaltmalar</h2>")
    parts.append(table(["Terim / Kısaltma", "Açıklama"], [
        ["Doküman", "Proje faaliyetlerini tanımlayan, yönlendiren veya destekleyen yazılı bilgi"],
        ["Kayıt", "Bir faaliyetin gerçekleştiğini, kararın alındığını veya kontrolün yapıldığını gösteren kanıt"],
        ["Kaynak Sistem", "Kayıt veya dokümanın doğal olarak üretildiği ve izlendiği sistem"],
        ["Zorunlu Doküman", "İlgili proje türü veya yaşam döngüsü aşamasında üretilmesi beklenen temel doküman"],
        ["Koşullu Doküman", "Proje kapsamı, risk, mevzuat, entegrasyon veya teknik karmaşıklığa göre üretilen doküman"],
        ["Yardımcı Doküman", "Çalışmayı kolaylaştıran ancak her durumda zorunlu olmayan destekleyici doküman"],
        ["BTT", "Bilgi Teknolojileri Temsilcisi"],
    ]))

    parts.append("<h2>7. Genel İlkeler</h2>")
    parts.append(table(["İlke", "Açıklama"], [
        ["Yaşam döngüsü temelli planlama", "Doküman ve kayıt ihtiyacı proje yaşam döngüsü aşamalarına göre belirlenir."],
        ["Gerektiği kadar dokümantasyon", "Her projede aynı ağırlıkta dokümantasyon zorunlu değildir; kapsam, risk ve denetim ihtiyacına göre yeterli doküman üretilir."],
        ["Kaynak sistemde izleme", "Kayıtlar mümkün olduğunca doğal olarak oluştukları sistemde tutulur; gereksiz kopyalama yapılmaz."],
        ["Tekil kaynak", "Bir doküman veya kayıt için geçerli kaynak sistem açık olmalıdır."],
        ["İzlenebilirlik", "Proje dokümanları, iş kayıtları, değişiklikler, testler, sürümler ve kararlar birbirleriyle ilişkilendirilebilir olmalıdır."],
        ["Şablon kullanımı", "Uygun şablon varsa doküman ilgili şablon kullanılarak hazırlanır."],
        ["Denetim kanıtı üretme", "Doküman ve kayıtlar denetimde gösterilebilir, erişilebilir ve açıklanabilir olmalıdır."],
    ]))

    parts.append("<h2>8. Roller ve Sorumluluklar</h2>")
    parts.append(table(["Rol", "Sorumluluk", "Yetki / Katkı"], [
        ["Proje Yöneticisi", "Proje dokümantasyon ihtiyacını belirler, temel proje dokümanlarının hazırlanmasını ve güncel tutulmasını sağlar.", "Doküman üretimini başlatır, yayın ve erişim düzenlemelerini koordine eder."],
        ["Proje Ekibi", "Kendi faaliyet alanına ait analiz, tasarım, geliştirme, test, bakım ve karar kayıtlarını üretir.", "Jira, Confluence, Bitbucket veya Drive üzerinde sorumlu olduğu kayıtları oluşturur ve günceller."],
        ["Analist", "Gereksinim, analiz, kapsam ve iş kuralı dokümanlarının hazırlanmasına katkı verir.", "Gereksinim ve analiz kayıtlarını ilişkilendirir."],
        ["Geliştirici", "Kod, commit, branch, pull request, code review ve teknik not kayıtlarını oluşturur.", "Bitbucket ve Jira kayıtlarını güncel tutar."],
        ["Test Sorumlusu", "Test senaryoları, test sonuçları, hata kayıtları ve doğrulama kanıtlarının oluşturulmasını sağlar.", "Test kayıtlarını Jira, Confluence veya Drive üzerinde izler."],
        ["Repository / Sistem Yöneticisi", "Confluence, Drive, Jira, Bitbucket ve Bamboo üzerinde erişim ve yayın ortamlarını yönetir.", "Yayın, erişim ve arşivleme düzenlemelerini uygular."],
        ["Kalite Danışmanı", "Dokümantasyon yapısının süreç, denetim ve kanıt beklentileriyle uyumunu gözden geçirir.", "Gözden geçirme görüşü, düzeltme önerisi ve denetim hazırlık yönlendirmesi verir."],
        ["BTT / İş Birimi Temsilcisi", "İş birimi görüşü, kabul, doğrulama ve karar süreçlerine katkı sağlar.", "Yetki verilen proje dokümanlarına erişir ve görüş bildirir."],
    ]))

    parts.append("<h2>9. Yazılım Projesi Dokümantasyon Stratejisi</h2>")
    parts.append(p("Yazılım projelerinde dokümantasyon stratejisi, proje yaşam döngüsünde oluşan kararların, gereksinimlerin, teknik çıktıların, testlerin, değişikliklerin ve sürüm kayıtlarının izlenebilir şekilde yönetilmesine dayanır."))
    parts.append(p("Proje dokümantasyonu yalnızca ayrı doküman dosyalarından oluşmaz. Jira kayıtları, Confluence sayfaları, Bitbucket commit/pull request kayıtları, Bamboo build/deploy kayıtları, Drive dosyaları, toplantı kayıtları ve e-posta onayları proje dokümantasyon setinin parçası olarak kabul edilir."))
    parts.append(table(["Strateji Unsuru", "Uygulama Kuralı"], [
        ["Doküman ihtiyacının belirlenmesi", "Proje başlangıcında kapsam, risk, yaşam döngüsü aşaması ve denetim beklentisi dikkate alınarak beklenen doküman/kayıt ihtiyacı belirlenir."],
        ["Kaynak sistem seçimi", "Her doküman veya kayıt için doğal kaynak sistem belirlenir. Örneğin iş takibi Jira’da, kod kayıtları Bitbucket’ta, süreç dokümanları Confluence’ta tutulur."],
        ["Şablon kullanımı", "Kurumsal şablon varsa kullanılır; yoksa doküman KLV.001’deki yazım kurallarına uygun hazırlanır."],
        ["Kayıtların ilişkilendirilmesi", "Gereksinim, görev, commit, test, hata, değişiklik ve sürüm kayıtları mümkün olduğunca birbirine bağlanır."],
        ["Gözden geçirme", "Normatif dokümanlar ve kritik proje dokümanları yayımlanmadan veya esas alınmadan önce gözden geçirilir."],
        ["Güncellik", "Proje ilerledikçe güncelliğini kaybeden dokümanlar revize edilir veya geçersizliği açık hale getirilir."],
    ]))

    parts.append("<h2>10. Doküman ve Kayıt Sınıflandırması</h2>")
    parts.append(table(["Sınıf", "Açıklama", "Örnek"], [
        ["Zorunlu Doküman / Kayıt", "Proje türü veya yaşam döngüsü aşaması gereği üretilmesi beklenen temel kanıt.", "Proje planı, gereksinim kaydı, test sonucu, sürüm kaydı"],
        ["Koşullu Doküman / Kayıt", "Proje kapsamı, risk, entegrasyon, güvenlik, mevzuat veya teknik karmaşıklığa göre üretilir.", "Mimari karar kaydı, entegrasyon tasarımı, güvenlik değerlendirmesi"],
        ["Yardımcı Doküman", "Çalışmayı kolaylaştırır ancak her durumda zorunlu değildir.", "Teknik not, kullanım notu, geçiş kontrol listesi"],
        ["Sistem Kaydı", "Kaynak sistemde otomatik veya iş akışı sonucu oluşur.", "Jira issue, Bitbucket commit, Bamboo build log"],
        ["Onay / Karar Kaydı", "Karar, kabul, yönlendirme veya onay bilgisini gösterir.", "Toplantı notu, e-posta onayı, Jira yorumu"],
    ]))

    parts.append("<h2>11. Yaşam Döngüsü Dokümantasyon Stratejisi</h2>")
    parts.append(p("Aşağıdaki tablo yazılım projelerinde beklenen temel dokümantasyon yaklaşımını gösterir. Detaylı ve güncel doküman ihtiyacı LST.005 - Yaşam Döngüsü Doküman İhtiyaç Matrisi içinde sürdürülebilir."))
    parts.append(table([
        "Yaşam Döngüsü Aşaması",
        "Beklenen Doküman / Kayıt",
        "Zorunluluk",
        "Kaynak Sistem / Yayın Ortamı",
        "Sorumlu Rol",
        "Gözden Geçirme / Onay"
    ], [
        ["Talep / Başlangıç", "Talep kaydı, ön değerlendirme, kapsam notu", "Zorunlu / Koşullu", "Jira / Confluence", "Proje Yöneticisi", "Proje Yöneticisi"],
        ["Planlama", "Proje planı, kaynak planı, risk listesi, iletişim yaklaşımı", "Zorunlu", "Confluence / Drive", "Proje Yöneticisi", "Proje Yöneticisi / Yönetim"],
        ["Analiz", "Gereksinim kaydı, analiz notu, iş kuralı, karar kaydı", "Zorunlu", "Jira / Confluence", "Analist / Proje Ekibi", "Proje Yöneticisi / İş Birimi"],
        ["Tasarım", "Tasarım dokümanı, mimari karar, veri modeli, entegrasyon notu", "Koşullu / Zorunlu", "Confluence / Bitbucket", "Teknik Ekip", "Teknik Sorumlu / Proje Yöneticisi"],
        ["Geliştirme", "Commit, branch, pull request, code review, teknik not", "Zorunlu / Kayıt", "Bitbucket / Jira", "Geliştirici", "Teknik Sorumlu"],
        ["Test", "Test senaryosu, test sonucu, hata kaydı, doğrulama kanıtı", "Zorunlu", "Jira / Confluence / Drive", "Test Sorumlusu", "Proje Yöneticisi / Test Sorumlusu"],
        ["Yayına Alma", "Yayın planı, sürüm notu, deployment kaydı, kontrol listesi", "Zorunlu", "Confluence / Jira / Bamboo / Drive", "Proje Yöneticisi / Operasyon", "Proje Yöneticisi"],
        ["İşletim / Bakım", "Bakım kaydı, destek kaydı, izleme ve müdahale notları", "Koşullu / Kayıt", "Jira / Confluence", "Destek / Proje Ekibi", "Süreç Sahibi"],
        ["Değişiklik Yönetimi", "Değişiklik talebi, etki analizi, uygulama ve doğrulama kaydı", "Zorunlu / Koşullu", "Jira / Confluence", "Proje Yöneticisi / İlgili Ekip", "Proje Yöneticisi"],
        ["Problem Çözümü", "Problem kaydı, kök neden analizi, çözüm ve doğrulama kaydı", "Koşullu / Kayıt", "Jira / Confluence", "Destek / Geliştirme Ekibi", "Süreç Sahibi"],
        ["Kapanış / Arşiv", "Kapanış notu, son durum özeti, arşiv kaydı", "Koşullu", "Confluence / Drive", "Proje Yöneticisi", "Proje Yöneticisi / Yönetim"],
    ]))

    parts.append("<h2>12. Kaynak Sistem ve Yayın Ortamı Kuralları</h2>")
    parts.append(table(["Kaynak / Ortam", "Kullanım Amacı", "Kural"], [
        ["Jira", "İş takibi, görev, hata, değişiklik, talep ve iş akışı kayıtları", "Proje faaliyet kayıtları mümkün olduğunca Jira üzerinde izlenir."],
        ["Confluence", "Proje dokümanları, toplantı notları, karar kayıtları, süreç ve kılavuz dokümanları", "Okunabilir ve paylaşıma açık proje dokümantasyonu için kullanılır."],
        ["Bitbucket", "Kod, branch, commit, pull request ve code review kayıtları", "Kodla ilişkili teknik kayıtların ana kaynağıdır."],
        ["Bamboo", "Build, deployment ve otomasyon kayıtları", "Yayın ve derleme kanıtları için kullanılır."],
        ["Drive", "Dosya, toplantı kaydı, video, çıktı ve ek kanıt saklama", "Confluence veya sistem kayıtlarına ek olarak dosya saklama amacıyla kullanılır."],
        ["E-posta", "Onay, karar veya dış paydaş yazışması", "Sadece ilgili karar veya onay başka sistemde izlenemiyorsa kanıt olarak referanslanır."],
    ]))

    parts.append("<h2>13. Şablon Kullanımı ve Doküman Üretim Kuralları</h2>")
    parts.append(table(["Kural", "Açıklama"], [
        ["Şablon önceliği", "Kurumsal şablon varsa doküman ilgili şablonla hazırlanır."],
        ["0. bölüm ayrımı", "Şablon dokümanlarındaki 0. bölüm gerçek dokümana taşınmaz."],
        ["Gerçek doküman başlangıcı", "Gerçek prosedür dokümanları 1. Prosedür Bilgileri bölümüyle başlar."],
        ["Süreç kayıtları", "Sürece özel kayıt niteliğindeki listeler ilgili süreç dokümanı altında tutulur."],
        ["Genel dokümanlar", "Genel kullanıma açık prosedür, kılavuz, şablon, politika, plan ve genel listeler LST.001 içinde izlenir."],
        ["Yazım kuralları", "Dokümanlar KLV.001’de belirtilen başlık, tablo, tarih, sürüm ve yayın kurallarına uygun hazırlanır."],
    ]))

    parts.append("<h2>14. Gözden Geçirme ve Onay Kuralları</h2>")
    parts.append(table(["Doküman / Kayıt Türü", "Gözden Geçirme Kuralı", "Onay Kuralı"], [
        ["Süreç, prosedür, kılavuz, politika ve plan", "Yayımlanmadan önce içerik, biçim ve uygulanabilirlik açısından gözden geçirilir.", "Yetkili süreç sahibi veya yönetim rolü tarafından onaylanır."],
        ["Şablonlar", "Kullanıma alınmadan önce doküman yapısı ve kullanım amacı açısından kontrol edilir.", "Dokümantasyon süreç sahibi veya yetkili rol tarafından onaylanır."],
        ["Proje yönetimi dokümanları", "Proje kapsamı, risk ve etki düzeyine göre gözden geçirilir.", "Proje Yöneticisi veya ilgili yönetim rolü tarafından onaylanır."],
        ["Sistem kayıtları", "Kaynak sistemdeki iş akışı, durum, yorum veya ilişkilendirme ile kontrol edilir.", "Ayrı onay dokümanı gerekmeyebilir."],
        ["Toplantı / karar kayıtları", "Kararın açık ve izlenebilir olması kontrol edilir.", "Toplantı katılımcı mutabakatı, e-posta veya sistem yorumu yeterli olabilir."],
    ]))

    parts.append("<h2>15. Yayın, Erişim ve Dağıtım Kuralları</h2>")
    parts.append(table(["Kural Alanı", "Uygulama"], [
        ["Yayın", "Genel süreç ve prosedür dokümanları Confluence üzerinde yayımlanır. Gerekli durumlarda Drive üzerinde dosya çıktısı tutulabilir."],
        ["Erişim", "Erişim yetkileri hedef kullanıcı grubuna göre verilir. Proje özel dokümanlarında proje ekibi ve ilgili paydaşlar esas alınır."],
        ["Dağıtım", "Yayımlanan dokümanların bağlantısı ilgili ekip veya paydaşlarla paylaşılır. Gereksiz dosya çoğaltma yapılmaz."],
        ["Gizlilik", "Hassas proje bilgileri yalnızca yetkili kullanıcılarla paylaşılır."],
        ["Denetim erişimi", "Denetim döneminde gerekli kanıtlar ilgili kaynak sistem üzerinden gösterilebilir olmalıdır."],
    ]))

    parts.append("<h2>16. Bakım, Güncelleme ve Arşivleme Kuralları</h2>")
    parts.append(table(["Durum", "Uygulama Kuralı"], [
        ["Güncelleme ihtiyacı", "Proje kapsamı, süreç, araç, şablon veya denetim beklentisi değiştiğinde ilgili doküman güncellenir."],
        ["Sürümleme", "Anlamlı doküman değişiklikleri sürüm geçmişine işlenir."],
        ["Pasif doküman", "Kullanımdan kaldırılan doküman pasif veya arşiv durumu ile ayrılır."],
        ["Arşiv", "Eski şablon ve geçersiz dokümanlar arşiv alanında saklanabilir."],
        ["Kayıtların korunması", "Denetim kanıtı niteliğindeki kayıtlar kaynak sistemde veya belirlenen saklama alanında korunur."],
    ]))

    parts.append("<h2>17. Kayıtlar ve Kanıtlar</h2>")
    parts.append(table(["Kayıt / Kanıt", "Kullanım Amacı", "Kaynak / Saklama Yeri"], [
        ["LST.001 - Aktif Dokümanlar Listesi", "Genel aktif doküman envanterini izlemek", "Confluence / Drive"],
        ["LST.002 - Doküman Değişiklik Kaydı", "Doküman değişikliklerini izlemek", "Confluence / Drive"],
        ["LST.003 - Doküman Gözden Geçirme Kaydı", "Gözden geçirme kayıtlarını izlemek", "Confluence / Drive"],
        ["LST.005 - Yaşam Döngüsü Doküman İhtiyaç Matrisi", "Proje yaşam döngüsüne göre doküman ihtiyacını izlemek", "Confluence / Drive"],
        ["Jira kayıtları", "Görev, hata, değişiklik, talep ve iş akışı kanıtları", "Jira"],
        ["Confluence sayfaları", "Proje dokümanları, toplantı notları ve karar kayıtları", "Confluence"],
        ["Bitbucket kayıtları", "Kod, commit, branch, pull request ve code review kanıtları", "Bitbucket"],
        ["Bamboo kayıtları", "Build ve deployment kanıtları", "Bamboo"],
        ["Drive dosyaları", "Toplantı kayıtları, ek dokümanlar ve çıktı dosyaları", "Drive"],
        ["E-posta kayıtları", "Gerektiğinde karar, onay veya dış paydaş yazışması kanıtı", "E-posta"],
    ]))

    parts.append("<h2>18. Sürüm Geçmişi</h2>")
    parts.append(table(["Sürüm", "Tarih", "Açıklama", "Hazırlayan/Güncelleyen", "Gözden Geçiren", "Onay"], [
        ["v0.1", "01-02-2025", "İlk taslak oluşturuldu.", "Levent BAYEZİT - Proje Yöneticisi", "Soner DEDEOĞLU - Kalite Danışmanı", "-"],
        ["v1.0", "15-02-2025", "Prosedür onaylanarak yürürlüğe alındı.", "Levent BAYEZİT - Proje Yöneticisi", "Soner DEDEOĞLU - Kalite Danışmanı", "Mustafa Nusret SARISAKAL - Bilgi İşlem Daire Başkanı"],
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
