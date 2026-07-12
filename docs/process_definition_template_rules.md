# Süreç Tanımı Şablonu Uygulama Kuralları

Bu kurallar `İÜC.BİDB.SRÇ.XXX.Ş - Süreç Tanımı Şablonu` kullanılarak süreç tanımı dokümanı oluşturulurken uygulanır.

## Genel Kurallar

- Şablondaki `0. Şablon Hakkında` bölümü gerçek süreç dokümanlarına alınmaz.
- Gerçek süreç dokümanı `1. Süreç Bilgileri` bölümü ile başlar.
- Şablondaki ana başlık sırası korunur.
- Şablonda sabit metin olarak tanımlanan yönlendirme bölümleri tabloya çevrilmez.
- `SRÇ.XXX` kullanılan şablon ifadeleri gerçek süreçte ilgili süreç koduna dönüştürülür.

## Sabit Bölüm Kuralları

### 6. Süreç Aktivitesi

Bu bölümdeki tablo satır adları sabittir:

- Süreç Başlatıcısı
- Süreç Başlangıcı
- Süreç Bitişi
- Ana Faaliyetler
- İlgili Süreçler

Yalnızca açıklama hücreleri süreç özelinde doldurulur.

### 7. Roller ve Sorumluluklar

Tablo kullanılmaz. Sürece özel metin aşağıdaki yapıda verilir:

> Bu süreç kapsamında rol, sorumluluk, yetki, RACI ve yetkinlik tanımları, süreç özel kaydı olan `İÜC.BİDB.LST.010 - Süreç Rol Yetki ve RACI Matrisi (İÜC.BİDB.SRÇ.XXX)` dokümanında yönetilir.

### 8. Süreç İş Ürünleri

Tablo kullanılmaz. Sürece özel metin aşağıdaki yapıda verilir:

> Bu süreç kapsamında kullanılan girdi iş ürünleri ve üretilen çıktı iş ürünleri, süreç özel kaydı olan `İÜC.BİDB.LST.008 - İş Ürünleri ve Kalite Kriterleri Listesi (İÜC.BİDB.SRÇ.XXX)` dokümanında yönetilir.

### 9. Süreç Akışı

Bu bölümde süreç akış görseli yer alır. Görsel PNG olarak Confluence üzerinde eklenecektir. Script bu bölümü otomatik tablo veya Mermaid ile doldurmaz.

### 10. Süreç Faaliyetleri

Şablondaki tablo başlıkları birebir korunur. Satırlar süreç özelinde doldurulur.

### 11. Ölçüm ve İzleme

Tablo kullanılmaz. Sürece özel metin aşağıdaki yapıda verilir:

> Bu süreç kapsamında takip edilecek süreç performansı ölçüm seti, süreç özel kaydı olan `İÜC.BİDB.LST.009 - Süreç Performans Ölçüm Seti (İÜC.BİDB.SRÇ.XXX)` dokümanında yönetilir.

### 12. Uygulama ve Uyarlama Kuralları

Bu bölümde süreç özelinde serbest alt başlıklar tanımlanabilir. Son alt başlık `Uyarlama Kuralları` olmalıdır.

Uyarlama Kuralları altında şablondaki tablo yapısı korunur ve şu satırlar mutlaka yer alır:

- Zorunlu Adımlar
- Uyarlanabilir Adımlar
- Onay Gerektiren Durumlar

### 13. Süreç Etkileşimleri

Tablo kullanılmaz. Sürece özel metin aşağıdaki yapıda verilir:

> Bu süreç kapsamındaki faaliyetlerin farklı süreçler ile olan etkileşimleri, süreç özel kaydı olan `İÜC.BİDB.LST.007 - Süreç Etkileşim Matrisi (İÜC.BİDB.SRÇ.XXX)` dokümanında yönetilir.

### 14. Sürüm Geçmişi

Sürüm geçmişi tablosunda `Gözden Geçiren` sütunu yer alır.
