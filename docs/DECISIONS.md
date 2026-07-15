# Kalıcı Proje Kararları

Bu dosya, ChatGPT proje konuşmalarından ve mevcut repository durumundan 14 Temmuz 2026 tarihinde aktarılmış kalıcı kararları içerir. Repository'deki daha güncel ve doğrulanmış kayıtlarla uyuşmazlık olması hâlinde uyuşmazlık raporlanır; sessizce karar verilmez.

## Süreç kapsamı ve mimarisi

- Değerlendirme kapsamı, `LST.006 - Standart Süreç Envanteri` içinde tanımlanan güncel standart süreç setidir; resmî dokümanlarda sabit süreç sayısı yazılmaz.
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
- `LST.008` iş ürünü hücrelerinde doküman ve süreç adları kısaltılmadan, tam kurumsal kod ve adlarıyla yazılır. Diğer dokümanlardaki bağlamı açık kısaltmalar kabul edilebilir.
- `LST.009`: performans ölçümleri; Hedef ve İzleme Matrisi yaklaşımı içerir.
- `LST.010`: süreç rolleri, yetkiler ve RACI.
- `FRM.001`: süreç gözden geçirme kaydı.
- Eski `LST.004 - Süreç Gözden Geçirme Matrisi` yaklaşımı kullanılmaz. Boşa çıkan `LST.004` kodu kullanıcı onayıyla SRÇ.021 kapsamında `İÜC.BİDB.LST.004 - Bilgi Kataloğu` olarak yeniden tanımlanmıştır; eski legacy anlamına dönülmez.
- Süreçlere ilişkin değişiklik ihtiyaçları ve talepler `İÜC.BİDB.SRÇ.018 - Değişiklik Talebi Yönetimi Süreci` kapsamında yönetilir. SRÇ.004 için ayrıca süreç tasarım/değişiklik talep formu oluşturulmaz.
- Yeni prosedürler mevcut `İÜC.BİDB.PRS.XXX.Ş - Prosedür Tanımı Şablonu` kullanılarak hazırlanır. Süreç Tasarım Prosedürü, süreç dokümanlarının hazırlanmasında `İÜC.BİDB.SRÇ.XXX.Ş - Süreç Tanımı Şablonu`nu referans gösterir.
- `LST.009` ölçüm setlerinde, uygulamada düzenli olarak üretilebilecek ve izlenebilecek az sayıda anlamlı ölçüm kullanılır; yönetilemeyecek kadar çok ölçüm tanımlanmaz. Bu kural tüm süreçlerde uygulanır.
- Prosedür, politika, süreç, kılavuz ve benzeri resmî dokümanlarda standart süreç setinin sabit sayısı yazılmaz. Kapsam, `LST.006 - Standart Süreç Envanteri` içinde tanımlanan güncel standart süreç setine referans verilerek ifade edilir.
- Sürece özel `LST.007`, `LST.008`, `LST.009`, `LST.010` ve boş `FRM.001` sayfaları ilgili `SRÇ` süreç sayfasının altında tutulur. Doldurulmuş `FRM.001 - Değerlendirme #1` kaydı `91 - İç Denetimler / Süreç Gözden Geçirmeleri` altında tutulur.
- Plan ve raporlar tek bir genel şablona zorlanmaz; her doküman ihtiyaca göre kendi koduyla eşleşen özel bir şablona sahip olabilir. Süreç Kalite Planı için `İÜC.BİDB.PLN.001.Ş - Süreç Kalite Planı Şablonu`, Süreç Performansları Raporu için `İÜC.BİDB.RPR.001.Ş - Süreç Performansları Raporu Şablonu` kullanılır.
- `İÜC.BİDB.PLN.001 - Süreç Kalite Planı`, süreç değerlendirmelerinin yaklaşımını ve Ocak-Mart dönemine yayılan yıllık değerlendirme takvimini tanımlar; takip çizelgesi/register değildir.
- `İÜC.BİDB.RPR.001 - Süreç Performansları Raporu`, tamamlanan her süreçten sonra aynı doküman üzerinde güncellenen kümülatif rapordur. Çalışma boyunca v0.1 Taslak kalır; taslak güncellemeler sürüm geçmişinde tutulmaz. Tüm süreç çalışmaları tamamlandığında v1.0 Onaylı sürüm kaydı oluşturulur.
- RPR.001 ve RPR.001.Ş içindeki `5. Etiket Dağılımları ve Eğilimler` tablosunda süreçler satırlarda; BP ve PA/GP etiket göstergeleri sabit sütunlarda gösterilir. Gösterge açıklamaları tablonun `Eğilim Yorumu` satırında korunur. Böylece yeni süreçler eklendikçe tablo yatay değil dikey büyür.
- RPR.001 ve RPR.001.Ş içindeki `4. Süreç Sonuç Özeti` tablosunda `SPICE Olgunluk Seviyesi` sütunu ayrılmıştır. Hesaplama, değerlendirme ve gösterim yöntemi henüz tanımlanmadığı için hücreler boş bırakılır; hiçbir ara değer veya varsayımsal seviye yazılmaz.

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
- Süreç değerlendirmelerinde sayısal puan veya tek bir toplam süreç etiketi kullanılmaz; BP ve PA/GP sonuçları yalnızca gerekçeli etiketlerle gösterilir.
- Mevcut çalışma süresince her süreç için aynı `Değerlendirme #1` kaydı güncellenir; ayrı GAP kaydı veya `Değerlendirme #2` oluşturulmaz.
- FRM.001 içindeki `Öncelikli Tamamlama Listesi` tablosu `Öncelik`, `Bulgu / Aksiyon`, `Bulgu Türü`, `İlgili BP / GP` ve `Hedef Süreç / İzleme Yeri` sütunlarından oluşur. Tamamlanma tarihi yerine bulgunun yönlendirildiği süreç veya izlendiği kayıt gösterilir.
- Uygunsuzluklar önce SRÇ.017'ye, çözüm gerektirirse SRÇ.018'e; iyileştirme fırsatları doğrudan SRÇ.018'e yönlendirilir. Gözlemler değerlendirme kaydında, güçlü uygulamalar değerlendirme kaydı ve RPR.001'de tutulur.

## SRÇ.006 süreç iyileştirme yaklaşımı

- İş ürünü, etkileşim ve kalite kriteri listelerinde İÜC.BİDB.FRM.001 için değerlendirme sıra numarası kullanılmaz. Genel referans `İÜC.BİDB.FRM.001 - Süreç Gözden Geçirme Formu (İlgili Süreç)` biçimindedir; `Değerlendirme #n` yalnızca gerçekleşmiş değerlendirme kayıtlarının sayfa adında kullanılır.
- SRÇ.006 Süreç Sahibi ve asıl iyileştirme onay mercii Bilgi İşlem Daire Başkanıdır. Gözden geçiren Proje Yöneticisi, onaylayan Bilgi İşlem Daire Başkanıdır.
- Proje Yöneticisi; Proje Geliştirme Yönetimi kapsamındaki, ilave bütçe gerektirmeyen, organizasyon yapısını değiştirmeyen ve kurum genelinde önemli etki oluşturmayan iyileştirmeleri rol bazlı genel yetki devri sınırları içinde onaylayabilir. Diğer iyileştirmeler Bilgi İşlem Daire Başkanı onayına sunulur.
- İyileştirme girdileri; SRÇ.005 süreç değerlendirmeleri, SRÇ.026 denetimleri, SRÇ.017 problem çözüm ve düzeltici faaliyet sonuçları, SRÇ.018 değişiklik talepleri, LST.009/RPR.001 performans sonuçları, SRÇ.008 risk değerlendirmeleri, kullanıcı ve paydaş geri bildirimleri, SRÇ.007 proje kapanış öğrenilmiş dersleri, SRÇ.002 müşteri memnuniyeti sonuçları ve Yönetim Gözden Geçirme toplantısı çıktılarıdır.
- İyileştirme adayı önce SRÇ.018 altında değişiklik kaydı olarak ön değerlendirme ve etki analizine alınır. Analiz sonucu iyileştirme fırsatı olarak sınıflandırılan kayıt; mevcut durum, kaynak kanıt, etkilenen süreçler, beklenen fayda, risk ve iyileştirme hedefiyle SRÇ.006 yaşam döngüsünde devam eder.
- `İÜC.BİDB.PRS.004 - Süreç İyileştirme ve Değişiklik Yönetimi Prosedürü`, SRÇ.006 ve SRÇ.018 tarafından ortak kullanılır; ön değerlendirme ve etki analizi alanlarını, iyileştirme sınıflandırmasını ve iki süreç arasındaki geçiş koşullarını tanımlar. Ayrı Süreç İyileştirme veya Süreç Değişikliği prosedürü oluşturulmaz.
- İyileştirme için `Etki` ve `Uygulama Önceliği` ayrı alanlardır. Her ikisi sayısal puan olmadan `Yüksek`, `Orta` veya `Düşük` etiketiyle gösterilir. Etki beklenen fayda/değişim büyüklüğünü; uygulama önceliği ele alınma sırasını ifade eder.
- Planlama uyarlaması: Tek süreçle sınırlı ve önemli kaynak gerektirmeyen iyileştirmeler SRÇ.018 değişiklik kaydı içinde planlanır. Yüksek etkili, birden fazla süreci etkileyen veya önemli kaynak gerektiren iyileştirmeler için `İÜC.BİDB.PLN.002 - Süreç İyileştirme Planı` hazırlanır.
- `İÜC.BİDB.PLN.002.Ş - Süreç İyileştirme Planı Şablonu` aktif şablon olarak hazır tutulur; uyarlama koşulu oluşmadan doldurulmuş PLN.002 planı oluşturulmaz.
- SRÇ.006 iyileştirme hedefini, planını, önceliğini, başarı ölçütlerini ve sonuç takibini yönetir. Süreç, doküman, araç veya uygulama üzerindeki gerçek değişiklikler SRÇ.018 kapsamında kontrollü olarak uygulanır.
- Uygulanan değişikliğin başarı ve etkisi SRÇ.018 içindeki `SUP.10.BP9 - Uygulanan değişikliğin gözden geçirilmesi` adımında değerlendirilir. Değerlendirme koşulları İÜC.BİDB.PRS.004 içinde tanımlanır; SRÇ.006 bu sonucu iyileştirme hedefinin gerçekleşme kanıtı olarak kullanır.
- İyileştirme sonucu ve öğrenilen dersler SRÇ.018 gözden geçirme çıktısında tutulur. Süreç kullanıcılarını etkileyen sonuçlar LST.012 ile yayımlanır; doğrulanmış önemli kazanımlar RPR.001 içinde özetlenir; sınırlı teknik değişikliklerde doğal ekip iletişim kaydı kanıt olarak kullanılabilir.
- RPR.001 iyileştirme başarısını yeniden değerlendirmez. Yalnızca SRÇ.018 SUP.10.BP9 sonucu ile doğrulanmış kazanımları yönetim görünürlüğü için kümülatif olarak raporlar.
- Tüm süreç dokümantasyonu tamamlandıktan sonra SRÇ.006-SRÇ.018-PRS.004 zincirini uçtan uca doğrulamak amacıyla bir veya iki seçilmiş süreç için örnek iyileştirme uygulaması yürütülür. Örnekler izlenebilir bir ihtiyaca dayanır; SRÇ.018 kaydı, gerekiyorsa PLN.002, değişiklik gözden geçirme sonucu, RPR.001 ve LST.012 bağlantılarıyla tamamlanır.

## SRÇ.019 insan kaynakları yönetimi yaklaşımı

- SRÇ.019 Süreç Sahibi ve onaylayanı Mustafa Nusret SARISAKAL - Bilgi İşlem Daire Başkanı; gözden geçireni Seçil NEBİLER - Şube Müdürüdür.
- Süreç, Personel Daire Başkanlığının yürürlükteki prosedürleriyle uyumlu tasarlanır. Personel Daire Başkanlığının yetkisindeki adımlar SRÇ.019 içinde yeniden tanımlanmaz; ilgili resmî prosedür ve kayıtlara yönlendirilir. BİDB'nin üstlenebileceği ihtiyaç, yetkinlik, ekip yapılanması, görev dağılımı, gelişim ve performans geri bildirimi sorumlulukları doğrulanmış kaynaklara göre tanımlanır.
- Personel Daire Başkanlığının KALSİS üzerinde tutulan güncel Genel Personel Hizmetleri, Personel Planlama ve İstihdam, Personel Görevlendirme, Personel Performans Değerlendirme ve Görev Tanımları Hazırlama prosedürleri temin edilinceye kadar SRÇ.019 çalışması beklemededir. Kaynaklar doğrulanmadan süreç paketi veya tamamlayıcı doküman üretilmez.

## Kurumsal kaynaklarla çakışma yönetimi

- İÜC/BİDB internet sitesi, KALSİS veya diğer resmî kurumsal kaynaklarda yayımlanan prosedür, politika, görev tanımı, organizasyon yapısı, iş akışı ve kayıtlar; SPICE kapsamında oluşturduğumuz süreçlerle karşılaştırılır.
- Kurumsal kaynak ile proje dokümanı arasında kapsam, rol, sorumluluk, yetki, onay, iş akışı, kayıt, doküman adı veya uygulama kuralı bakımından uyuşmazlık görüldüğünde sessizce birleştirme, üzerine yazma veya önceliklendirme yapılmaz.
- Çakışan iki yaklaşım, dayanakları, etkilenen dokümanlar ve olası seçenekler kullanıcıya açıkça sunulur. Uygulanacak yaklaşım kullanıcı kararıyla belirlenmeden ilgili içerik kesinleştirilmez.
- Resmî kurumsal kaynakta güncel olduğu açıkça doğrulanan bilgi referans olarak korunur; bunun mevcut proje kararını değiştirip değiştirmeyeceğine yine kullanıcı karar verir.

## SRÇ.023 organizasyonel yönetim yaklaşımı

- Süreç Sahibi Mustafa Nusret SARISAKAL - Bilgi İşlem Daire Başkanı; gözden geçiren Seçil NEBİLER - İdari İşler Şube Müdürü; onaylayan Mustafa Nusret SARISAKAL - Bilgi İşlem Daire Başkanıdır.
- SRÇ.023 kapsamı, İÜC.BİDB.LST.006 - Standart Süreç Envanterinde yer alan süreçlerin yönetim altyapısı, yönetim uygulamaları ve bunların etkinliğinin değerlendirilmesiyle sınırlıdır. BİDB'nin idari, mali ve envanter dışındaki genel kurumsal faaliyetleri SRÇ.023 içinde yeniden tanımlanmaz; 341.1PR ve ilgili kurumsal prosedürlerde bırakılır.
- Yönetim Gözden Geçirme toplantısının yönetim mekanizması, gündemi, kararları ve karar takibi SRÇ.023 kapsamında yürütülür. SRÇ.002; kalite sonuçları, müşteri memnuniyeti, kalite güvence bulguları ve ilgili kalite girdilerini toplantıya sağlar. Toplantı kararları bulgu ve ihtiyaç türüne göre SRÇ.006, SRÇ.017 veya SRÇ.018'e yönlendirilir.
- Yönetim Gözden Geçirme toplantısı yılda bir kez Haziran-Temmuz döneminde yapılır. Yılın ilk üç ayında tamamlanan süreç değerlendirmeleri ve güncel RPR.001 toplantının temel girdileridir. Önemli yönetim, mevzuat, performans, risk veya hizmet değişikliklerinde olağanüstü Yönetim Gözden Geçirme toplantısı yapılabilir.
- Yönetim Gözden Geçirmenin toplantı başkanı ve karar mercii Bilgi İşlem Daire Başkanıdır. İlgili süreç sahipleri, Proje Yöneticisi ve Kalite Danışmanı çekirdek katılımcılardır; gündeme göre ilgili şube müdürü, uzman veya süreç çalışanı katılır. Tüm süreç sahiplerinin her toplantıya zorunlu katılımı aranmaz; yalnızca gündemle ilişkili süreç sahipleri toplantıya dâhil edilir.
- BİDB Yönetim Gözden Geçirme toplantıları için yapılandırılmış, genel amaçlı bir Toplantı Tutanağı şablonu hazırlanır ve YGG kayıtları bu formatta tutulur. Diğer süreçlerdeki günlük veya operasyonel toplantı notlarının bu şablonu kullanması zorunlu değildir; Proje Yöneticisinin Confluence'ta tuttuğu serbest formatlı toplantı notları doğal kayıt olarak kullanılmaya devam eder.
- Genel toplantı tutanağı şablonunun kodu `İÜC.BİDB.FRM.002.Ş - Toplantı Tutanağı Şablonu`dur. Gerçek kayıtlar `İÜC.BİDB.FRM.002 - Toplantı Tutanağı ([Toplantı Adı] - [Tarih veya Sıra])` biçiminde adlandırılır; yıllık YGG kaydı için `İÜC.BİDB.FRM.002 - Toplantı Tutanağı (Yönetim Gözden Geçirme - [Yıl])` kullanılır.
- FRM.002.Ş genel yapısı; Toplantı Bilgileri, Katılımcılar, Gündem Maddeleri, Görüşülen Girdiler ve Belgeler, Görüşmeler ve Değerlendirmeler, Kararlar ve Aksiyonlar, Ekler ve Bağlantılar ile Toplantı Sonucu ve Sonraki Gözden Geçirme bölümlerinden oluşur. YGG'ye özgü zorunlu gündem ve girdiler genel formda değil Organizasyonel Yönetim Prosedüründe tanımlanır.
- YGG girdileri altı başlıkta yönetilir: önceki YGG kararları ve açık aksiyonlar; RPR.001 süreç performansları, süreç değerlendirmeleri, kalite ve müşteri memnuniyeti sonuçları; denetim, risk, problem, değişiklik ve iyileştirme sonuçları; proje/hizmet performansı, öğrenilmiş dersler ve paydaş geri bildirimleri; kaynak, yetkinlik, eğitim ve altyapı ihtiyaçları; standart, mevzuat, organizasyon ve kurumsal hedef değişiklikleri. Yalnızca ilgili dönemde oluşan ve erişilebilen doğal kayıtlar gündeme alınır; eksik başlıklar için yapay kayıt üretilmez.
- YGG kararları ve ihtiyaçları türüne göre ilgili sürece yönlendirilir: problem ve uygunsuzluklar SRÇ.017'ye; değişiklik ve iyileştirme fırsatları SRÇ.018'e, gerekli sınıflandırmanın ardından SRÇ.006'ya; eğitim ve yetkinlik ihtiyaçları SRÇ.020'ye; altyapı ihtiyaçları SRÇ.022'ye; süreç değerlendirme ihtiyaçları SRÇ.005'e; bilgi ve iyi uygulamalar SRÇ.021'e aktarılır. FRM.002 içindeki her karar ve aksiyonda sorumlu rol, hedef tarih, ilgili süreç veya kayıt ve durum bilgisi bulunur.
- YGG aksiyonlarının takip koordinasyonu konu türüne göre atanır. Teknik, proje ve süreç odaklı aksiyonları Proje Yöneticisi; üst yönetimle ilişkili kurumsal ve idari aksiyonları İdari İşler Şube Müdürü takip eder. Aksiyonun asıl uygulama sorumlusu ayrıca kararda belirtilir. Tamamlanma bilgisi ilgili sorumlu tarafından sağlanır; açık kalan aksiyonlar bir sonraki YGG'nin girdisi olur.
- YGG aksiyonunun uygulama sorumlusu, tamamlanma bilgisini ve varsa ilgili kayıt veya bağlantıyı FRM.002'de günceller. Atanmış takip koordinatörü sonucu doğrulayarak aksiyonu kapatır; Bilgi İşlem Daire Başkanının her rutin aksiyon için ayrıca kapanış onayı vermesi gerekmez. Karma nitelikli aksiyonların takip koordinatörünü YGG sırasında Bilgi İşlem Daire Başkanı belirler.
- SRÇ.023 için LST.009'da iki temel ölçüm tutulur: planlanan YGG'nin Haziran-Temmuz döneminde gerçekleştirilme durumu ve YGG aksiyonlarının hedef tarihte tamamlanma oranı. Yönetim uygulamalarının genel etkinliği ayrıca puanlanmaz; RPR.001, FRM.001 süreç değerlendirmeleri ve YGG kararları üzerinden nitel olarak değerlendirilir.
- YGG kararları ve benimsenmesine karar verilen iyi uygulamalar Confluence'taki FRM.002 toplantı tutanağında kayıtlı tutulur ve yalnızca ilgili rol ve personele hedefli olarak duyurulur. Kontrollü bir süreç veya doküman değişikliği gerektiren kararlar SRÇ.018 üzerinden yürütülür ve değişen doküman yayımlandığında LST.012'ye yaygınlaştırma kaydı eklenir; her YGG kararı ayrıca LST.012'ye kaydedilmez.
- Yönetim altyapısı iki katmanlı tanımlanır. Kurumsal görev, yetki ve hiyerarşi için İÜC'nin yürürlükteki organizasyon şeması, görev tanımları ve 341.1PR esas alınır; SPICE süreçlerine özgü sorumluluk, karar, danışma ve bilgilendirme ilişkileri LST.010 RACI matrislerinde gösterilir. İki yapı arasında uyuşmazlık görülürse LST.010 kendiliğinden üstün sayılmaz; konu YGG'de değerlendirilir ve gerekiyorsa SRÇ.018 üzerinden düzeltilir.
- İyi uygulama kabul yetkisi etki alanına göre kullanılır. Mevcut yetki, kaynak ve süreç sınırları içindeki teknik veya operasyonel uygulamalar Proje Yöneticisi tarafından onaylanabilir. Birden fazla birimi, kurumsal rol ve yetki yapısını, ek kaynak tahsisini veya üst yönetim kararını etkileyen uygulamalar Bilgi İşlem Daire Başkanı tarafından onaylanır. Kontrollü doküman değişikliği gereken her iki durumda da uygulama SRÇ.018 üzerinden yürütülür.
- SRÇ.023 için ayrı bir Organizasyonel Yönetim Prosedürü oluşturulur.
- Kurumun yürürlükteki `341.1PR - Bilgi İşlem Daire Başkanlığı Genel İşleyiş Prosedürü`, hem SRÇ.023 süreç tanımının hem de yeni Organizasyonel Yönetim Prosedürünün referans listesinde gösterilir.
- Yeni prosedür 341.1PR'de tanımlanan birim yapısı, genel sorumluluklar ve kurumsal iş yönlendirme akışını tekrar etmez veya değiştirmez. MAN.2 kapsamında yönetim altyapısı, yazılım yönetim uygulamaları, etkinlik değerlendirmesi ve iyi uygulamaların benimsenmesi için tamamlayıcı kuralları tanımlar.
- BİDB görev tanımlarını ve görevli personel görünümünü ortak bağlantı kaydında yönetmek için `İÜC.BİDB.LST.013 - Görev Tanımları ve Görevli Personel Listesi` ile `İÜC.BİDB.LST.013.Ş - Görev Tanımları ve Görevli Personel Listesi Şablonu` kullanılır. Dolu liste `03 - Kayıtlar ve Listeler` altında tutulur; birincil süreci SRÇ.023, destekleyen süreci SRÇ.019'dur.
- LST.013 resmî görev tanımı metinlerini çoğaltmaz; İÜC/BİDB sitesindeki yürürlükteki görev tanımı PDF'lerine, yönetim/personel sayfalarına ve yayımlanmış personel profillerine bağlantı verir.
- BİDB internet sitesindeki personel eşleştirmesi yönlendirici görünüm sağlar; EBYS/KALSİS atama veya görevlendirme kaydının yerine geçmez. Görev tanımı ve bağlantı yapısının bakımı SRÇ.023 kapsamında, resmî personel atama/görevlendirme doğrulaması ise kaynakları temin edildiğinde SRÇ.019 kapsamında ele alınır.
- Resmî sayfalar ile süreç RACI kayıtları arasında uyuşmazlık görülürse sessizce birleştirme yapılmaz; konu YGG'de değerlendirilir ve gerekiyorsa SRÇ.018'e yönlendirilir.

## Teknik çalışma zinciri

Zorunlu zincir:

`Yerel repo → yerel doğrulama → Git diff → Confluence dry-run → kontrollü yayın → Confluence doğrulama → export/viewer → Git commit/push`

- Confluence yazma işlemi öncesi dry-run zorunludur.
- Alakasız dosyalara dokunulmaz.
- ChatGPT konuşmaları taslak üretim ortamı değil, kararların aktarıldığı kaynaklardan biridir; asıl çalışma repository üzerinde yapılır.

## SRÇ.021 bilgi yönetimi yaklaşımı

- Confluence bilgi ağının başlangıç noktasıdır; Jira, Bitbucket ve Google Drive dahil kaynak sistemlerdeki asıl bilgiler kopyalanmaz, doğrulanmış bağlantılarla erişilebilir kılınır.
- LST.004 Bilgi Kataloğu Proje Yöneticisi tarafından sürdürülür; Kalite Danışmanı standart/kalite bilgisinde ana katkı rolüdür; ilgili uzman/birim alanı katalog bakım sorumluluğu doğurmaz.
- Katalogda yalnızca doğrulanmış hedef bağlantıları kullanılır; diğer süreçler tamamlandıkça katalog yaşayan kayıt olarak genişletilir.
- Rutin katalog ekleri ayrı resmî onay veya LST.012 kaydı gerektirmez. Hedef kitleyi etkileyen süreç dokümanı ve önemli değişiklikler uygun kurumsal kanaldan duyurulur; süreç dokümanı yaygınlaştırması LST.012'de izlenir.
- Katalog yılda bir kez ve olay bazlı tetikleyicilerde gözden geçirilir. LST.009'da yalnızca geçerli bağlantı oranı ve yıllık gözden geçirme tamamlama oranı izlenir; kayıt sayısı performans göstergesi değildir.
- Standart veya mevzuat değişikliğinin süreç etkisi ihtimali varsa konu SRÇ.018'e aktarılır.

## LST.010 ortak yapı kararı

- Aktif `İÜC.BİDB.LST.010.Ş - Süreç Rol Yetki ve RACI Matrisi Şablonu` ile süreç özel LST.010 kayıtlarında `İÜC.BİDB.SRÇ.006` altındaki LST.010 sayfası yapısal referanstır.
- Ortak bölüm sırası: Liste Özeti, Kullanım Değerleri, Rol ve Yetkinlik Matrisi, Süreç Faaliyetleri RACI Matrisi, İş Ürünleri RACI Matrisi, Yetki ve Onay Matrisi, Sürüm Geçmişidir.
- Rol matrisi `Rol / Sorumluluk / Yetki / Asgari Yetkinlik / Süreçteki Konum`; yetki matrisi `Karar-Onay / Hazırlayan / Gözden Geçiren / Onaylayan / Yetki Sınırı-Kural` sütunlarını kullanır.
- Faaliyet ve iş ürünü RACI tabloları Responsible/Accountable/Consulted/Informed metin sütunları yerine süreç rollerinin sütunlarda, faaliyet ve iş ürünlerinin satırlarda gösterildiği çapraz matris biçimindedir. Rol sütunları ilgili sürece göre uyarlanır.
- İş ürünleri RACI matrisinde dokümanlar mümkün olduğunda tam kurumsal kod ve adlarıyla yazılır.
