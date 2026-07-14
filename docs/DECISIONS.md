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

- Doküman adları ve doküman yapıları için `02 - Şablonlar` altındaki aktif (arşivlenmemiş) şablon sayfaları tek doğruluk kaynağıdır. `Arşiv - Kaldırılan Şablonlar` altındaki eski ad ve yapılar yeni veya güncellenen dokümanlarda kullanılmaz.
- Ortak set: `SRÇ`, `LST.007`, `LST.008`, `LST.009`, `LST.010`, `FRM.001`.
- `LST.007`: süreç etkileşimleri.
- `LST.008`: iş ürünleri ve kalite kriterleri.
- `LST.009`: performans ölçümleri; Hedef ve İzleme Matrisi yaklaşımı içerir.
- `LST.010`: süreç rolleri, yetkiler ve RACI.
- `FRM.001`: süreç gözden geçirme kaydı.
- `LST.004` yeni yaklaşımda kullanılmaz. Repository'deki mevcut `LST.004` sayfaları legacy kayıttır; açık onay olmadan silinmez veya taşınmaz.
- Süreçlere ilişkin değişiklik ihtiyaçları ve talepler `İÜC.BİDB.SRÇ.018 - Değişiklik Talebi Yönetimi Süreci` kapsamında yönetilir. SRÇ.004 için ayrıca süreç tasarım/değişiklik talep formu oluşturulmaz.
- Yeni prosedürler mevcut `İÜC.BİDB.PRS.XXX.Ş - Prosedür Tanımı Şablonu` kullanılarak hazırlanır. Süreç Tasarım Prosedürü, süreç dokümanlarının hazırlanmasında `İÜC.BİDB.SRÇ.XXX.Ş - Süreç Tanımı Şablonu`nu referans gösterir.
- `LST.009` ölçüm setlerinde, uygulamada düzenli olarak üretilebilecek ve izlenebilecek az sayıda anlamlı ölçüm kullanılır; yönetilemeyecek kadar çok ölçüm tanımlanmaz. Bu kural tüm süreçlerde uygulanır.
- Prosedür, politika, süreç, kılavuz ve benzeri resmî dokümanlarda standart süreç setinin sabit sayısı yazılmaz. Kapsam, `LST.006 - Standart Süreç Envanteri` içinde tanımlanan güncel standart süreç setine referans verilerek ifade edilir.
- Sürece özel `LST.008`, `LST.009`, `LST.010` ve `FRM.001` sayfaları ilgili `SRÇ` süreç sayfasının altında tutulur. Ortak kayıt niteliğindeki `LST.007` merkezi kayıt alanında kalır.

## İçerik ve sürümleme

- Şablonlara yalnızca zorunlu eksikler eklenir; ana başlıklar ve numaralandırma gereksiz yere değiştirilmez.
- Süreç dokümanlarının sürümü `v1.0` olarak kullanılır. Hazırlayan bilgisi `Soner DEDEOĞLU - Kalite Danışmanı`dır.
- Her süreç üzerinde çalışmaya başlamadan önce süreç sahibi, gözden geçiren ve onaycı kullanıcıdan ayrıca doğrulanır; bu bilgiler tahmin edilmez.
- Süreç dokümanlarının sürüm geçmişi iki satırdan oluşur: `v0.1 / 10 Jan 2025 / İlk taslak oluşturuldu.` ve `v1.0 / 15 Feb 2025 / [Süreç adı] süreci onaylanarak yürürlüğe girmiştir.`. Hazırlayan her iki satırda `Soner DEDEOĞLU - Kalite Danışmanı`; v0.1 gözden geçiren ve onay alanları `-`; v1.0 gözden geçiren ilgili süreç sahibi, onay alanı doğrulanan onaycıdır.
- Süreç Bilgileri tablosunda `Hedef Kitle` ile `Yayın ve Erişim Ortamı` alanları bulunur.
- Amaç bölümünün altında `Süreç Sonuçları` alt bölümü bulunur.
- `Referanslar` bölümünde yalnızca ilgili ISO/IEC 15504-5 süreç bölümü, `ISO/IEC 15504-5 Process Assessment Model` ve `ISO/IEC 15504-5 Process Attributes` bölümü bulunur. İÜC Bilgi İşlem kaynakları kullanıcı tarafından belirlendikçe ayrıca eklenir.
- `Süreç Aktivitesi / İlgili Süreçler` alanında süreçler ayrı satırlarda gösterilir.
- `Süreç Akışı` bölümünde SRÇ.001 ile aynı yapıda PNG akış görseli alanı ve `Mermaid Kodu` bloğu bulunur. PNG dosyası Mermaid kodundan `https://www.mermaidonline.live/editor` kullanılarak dışa aktarılır.
- Süreç tanımı şablonunda `Roller ve Sorumluluklar` bölümünden sonra `Araçlar ve Altyapı` bölümü bulunur. Bu bölüm araç, altyapı/çalışma ortamı, kullanım amacı, erişim koşulu ve sorumlu rol/birim bilgilerini içerir.
- SRÇ.001 Dokümantasyon Sürecinde kodla ilişkili teknik kayıtlar ve sürüm kontrollü dokümantasyon kaynakları için kurumsal araç adı olarak `Bitbucket` kullanılır.
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
