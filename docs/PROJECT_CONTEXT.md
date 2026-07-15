# Proje Bağlamı

## Kimlik

- Proje: İÜC BİDB SPICE 2026 Level 3
- Repository kodu: `IUC-SPICE-2026`
- Kurum: İstanbul Üniversitesi-Cerrahpaşa
- Birim: Bilgi İşlem Daire Başkanlığı
- Confluence alanı: `SSSS`
- Confluence kök sayfası: `İÜC BİDB SPICE 2026 Level 3`
- Confluence kök sayfa ID: `137265781`
- GitHub repository: `sonerdedeoglu/iuc-spice-l3`

## Hedef ve kapsam

Projenin hedefi, 26 süreç için SPICE Seviye 3 hazırlık dokümantasyonunu, kanıt yapısını, süreç değerlendirmesini ve iyileştirme takibini kurmaktır.

ChatGPT proje kararlarında değerlendirme dönemi 2026 Ağustos ayının ilk haftası olarak belirtilmiştir. Bu tarih planlama kararlarında kullanılmadan önce kullanıcıyla yeniden doğrulanmalıdır.

Hedefler:

- BP ve PA 1.1: `%85` üzeri
- PA 2.1 ve PA 2.2: `%85` üzeri
- PA 3.1 ve PA 3.2: `%50` üzeri

Rating sözlüğü:

- `N`: 0–15
- `P`: >15–50
- `L`: >50–85
- `F`: >85–100

## Süreç yönetim omurgası

- PIM.1: 26 süreçlik standart süreç setini ve süreç mimarisini kurar.
- PIM.2: Süreçleri BP ve PA/GP bazında değerlendirir, GAP çıkarır.
- PIM.3: GAP'leri iyileştirme aksiyonuna dönüştürür, sonucu doğrular ve paylaşır.

Çalışma sırası süreç ihtiyacına göre değişebilmekle birlikte ortak altyapı sırası şöyledir:

1. PIM.1 — Process Establishment
2. PIM.2 — Process Assessment
3. PIM.3 — Process Improvement

SUP.7 dokümantasyon kontrol omurgası, SUP.8 ise yapılandırma/baseline omurgasıdır.

## Sistemler ve bilgi kaynakları

- Confluence: onaylı süreç dokümanlarının ana yayın ve erişim ortamı
- Google Drive: kontrollü doküman ve kayıt deposu
- GitHub/local repository: otomasyon, export, doğrulama ve değişiklik geçmişi
- Jira, Bitbucket ve Bamboo: proje kanıt kaynakları; erişim ve kapsam ayrıca doğrulanmalıdır
- Referans proje: Soru Bankası Projesi

Kurumsal süreç dokümanları projeden bağımsız hazırlanır. Soru Bankası adı yalnızca proje uygulaması ve denetim kanıtı bağlamında kullanılır.

## Standart kaynağı

Repository'deki çalıştırılabilir/işlenebilir kaynak:

- `resources/standards/spice_practices.yaml`
- Doğrulama raporu: `reports/spice_practices_validation_report.md`

ChatGPT projesinde ayrıca `ISO-IEC 15504-5 (2006) - Process Assessment - Part 5 - An Exemplar Process Assessment Model.pdf` kaynağı bulunmaktadır. PDF repository'de yoktur. Lisans ve paylaşım durumu doğrulanmadan Git'e eklenmemelidir.

## Dil ve biçim

- Varsayılan dil: Türkçe (`tr-TR`)
- Kurumsal kodlarda Türkçe `SRÇ` biçimi korunur.
- Confluence storage XHTML, sayfa metadata dosyaları ve yerel view HTML çıktıları birlikte yönetilir.
- Mevcut şablon yapısı, makrolar, tablo düzeni ve sürüm geçmişi korunur.
