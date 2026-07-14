# Kalıcı Proje Kararları

Bu dosya, ChatGPT proje konuşmalarından ve mevcut repository durumundan 14 Temmuz 2026 tarihinde aktarılmış kalıcı kararları içerir. Repository'deki daha güncel ve doğrulanmış kayıtlarla uyuşmazlık olması hâlinde uyuşmazlık raporlanır; sessizce karar verilmez.

## Süreç kapsamı ve mimarisi

- Değerlendirme kapsamı 26 süreçtir.
- Çekirdek/koşullu süreç ayrımı yapılmaz.
- Tüm süreçlerden denetim kanıtı toplanır.
- PIM.1 → PIM.2 → PIM.3, ortak süreç tanımlama/değerlendirme/iyileştirme döngüsüdür.
- Kontrollü süreç uyarlamasına izin verilir; amaç ve zorunlu süreç sonuçları korunur.
- Süreç kullanım verileri mevcut ilgili kayıtlarda tutulur; ayrıca merkezi bir register oluşturulmaz.

## Doküman seti

- Ortak set: `SRÇ`, `LST.007`, `LST.008`, `LST.009`, `LST.010`, `FRM.001`.
- `LST.007`: süreç etkileşimleri.
- `LST.008`: iş ürünleri ve kalite kriterleri.
- `LST.009`: performans ölçümleri; Hedef ve İzleme Matrisi yaklaşımı içerir.
- `LST.010`: süreç rolleri, yetkiler ve RACI.
- `FRM.001`: süreç gözden geçirme kaydı.
- `LST.004` yeni yaklaşımda kullanılmaz. Repository'deki mevcut `LST.004` sayfaları legacy kayıttır; açık onay olmadan silinmez veya taşınmaz.

## İçerik ve sürümleme

- Şablonlara yalnızca zorunlu eksikler eklenir; ana başlıklar ve numaralandırma gereksiz yere değiştirilmez.
- Mevcut sürüm geçmişi silinmez veya yeniden yazılmaz; revizyon yeni satır olarak eklenir.
- Süreç Bilgileri tablosunda `Hedef Kitle` ile `Yayın ve Erişim Ortamı` alanları bulunur.
- Amaç bölümünün altında `Süreç Sonuçları` alt bölümü bulunur.
- Kurumsal süreç dokümanında “Soru Bankası” adı kullanılmaz.
- Süreçler yılda en az bir kez ve tetikleyici durumlarda ayrıca gözden geçirilir.
- Yeni süreç ve revizyonların duyurusu e-posta ile yapılır.
- Eğitim kayıtları SRÇ.020 kapsamında tutulur.

## Yayın ve onay

- Hazırlayan: Kalite Danışmanı
- Gözden Geçiren: Süreç Sahibi
- Onaylayan: Bilgi İşlem Daire Başkanı
- Yayımlayan: Proje Geliştirme Yönetimi — Proje Yöneticisi
- Ana yayın/erişim ortamları Confluence ve Google Drive'dır.

## Kanıt yaklaşımı

- Referans proje Soru Bankası Projesidir.
- Kanıtlar gerçek kaynak sistemlerden alınır.
- Geçmiş tarihli sahte kayıt oluşturulmaz.
- Eksiklerin kapatılması güncel revizyon, tamamlayıcı kayıt, matris, review kaydı veya açık GAP aksiyonu ile yapılır.
- GAP durumları: `VAR`, `ZAYIF`, `DAĞINIK`, `YOK`, `KAPSAM DIŞI`.

## Teknik çalışma zinciri

Zorunlu zincir:

`Yerel repo → yerel doğrulama → Git diff → Confluence dry-run → kontrollü yayın → Confluence doğrulama → export/viewer → Git commit/push`

- Confluence yazma işlemi öncesi dry-run zorunludur.
- Alakasız dosyalara dokunulmaz.
- ChatGPT konuşmaları taslak üretim ortamı değil, kararların aktarıldığı kaynaklardan biridir; asıl çalışma repository üzerinde yapılır.
