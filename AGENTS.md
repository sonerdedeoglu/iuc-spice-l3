# İÜC BİDB SPICE 2026 Level 3 — Codex Çalışma Talimatları

## Proje amacı

Bu repository, İstanbul Üniversitesi-Cerrahpaşa Bilgi İşlem Daire Başkanlığının ISO/IEC 15504-5:2006 tabanlı SPICE Seviye 3 hazırlık çalışmasını yönetir. Değerlendirme kapsamı 26 süreçtir.

## Başlangıçta okunacak dosyalar

Her görevde önce şu dosyaları oku:

1. `docs/PROJECT_CONTEXT.md`
2. `docs/CURRENT_STATUS.md`
3. `docs/DECISIONS.md`
4. `docs/CONFLUENCE_WORKFLOW.md`
5. Görevle ilgili `reports/` raporları ve `confluence/pages/**/page.yaml` metadata dosyaları

ChatGPT sohbet geçmişini çalışma kaynağı sayma. Kalıcı kararlar repository içindeki dosyalardır.

## Yetkili standart kaynağı

- BP, outcome, PA ve GP çalışmaları için öncelikle `resources/standards/spice_practices.yaml` kullan.
- Bu YAML, `reports/spice_practices_validation_report.md` ile 26 süreç ve PA/GP kapsamı açısından doğrulanmıştır.
- İnternetten farklı ISO/IEC 15504 sürümü, Automotive SPICE veya başka bir süreç modeli kullanma.
- Standart metninin PDF üzerinden yorumlanması gerekiyorsa ve lisanslı PDF yerelde yoksa durumu kullanıcıya bildir; standart içeriği tahmin etme.
- Yeni BP, GP, outcome veya zorunluluk uydurma.

## Zorunlu çalışma yöntemi

İçeriği yalnızca sohbet yanıtı olarak üretme. Değişiklikleri doğrudan yerel repository üzerinde uygula.

Her içerik değişikliğinde şu sıra izlenir:

1. İlgili güncel şablonu incele.
2. Aynı türdeki güncel ve onaylı örnek dokümanı incele.
3. İlgili `page.yaml`, storage XHTML ve view HTML dosyalarını birlikte değerlendir.
4. Başlık sırasını, tabloları, Confluence makrolarını ve numaralandırmayı koru.
5. Yalnızca görev kapsamındaki dosyaları değiştir.
6. Yerel doğrulama ve diff kontrolü yap.
7. Confluence yazma işleminden önce mutlaka dry-run çalıştır ve raporu incele.
8. Kullanıcı açıkça onaylamadan Confluence'a toplu yazma yapma.
9. Yayın sonrası Confluence sonucunu doğrula, export ve viewer dosyalarını yeniden üret.
10. Git status ve diff kontrolünden sonra commit/push yap.

## Doküman bütünlüğü

- Kurumsal süreç kodlarında `SRÇ` kullan; dosya sluglarında mevcut `src` biçimini değiştirme.
- Kullanıcı açıkça istemedikçe sürüm numarası, sayfa başlığı, doküman kodu veya klasör yolunu değiştirme. Süreç dokümanları için kullanıcı tarafından onaylanan temel sürüm `v1.0`dır.
- Her süreç dokümanı üzerinde çalışmaya başlamadan önce süreç sahibi, gözden geçiren ve onaycıyı kullanıcıya sor; rol ve kişi bilgilerini tahmin etme.
- Süreç dokümanlarında hazırlayan `Soner DEDEOĞLU - Kalite Danışmanı`dır. Sürüm geçmişi `v0.1 / 10 Jan 2025 / İlk taslak oluşturuldu.` ile `v1.0 / 15 Feb 2025 / [Süreç adı] süreci onaylanarak yürürlüğe girmiştir.` satırlarından oluşur; v1.0 rol alanlarını kullanıcıdan doğrula.
- Süreç `Referanslar` bölümünü ilgili ISO/IEC 15504-5 süreç bölümü, `ISO/IEC 15504-5 Process Assessment Model` ve `ISO/IEC 15504-5 Process Attributes` ile sınırla. İÜC Bilgi İşlem kaynaklarını yalnızca kullanıcı belirlediğinde ekle.
- `Süreç Aktivitesi / İlgili Süreçler` alanında her süreci ayrı satırda göster.
- `Süreç Akışı` bölümüne SRÇ.001 biçiminde PNG alanı ve Mermaid kod bloğu koy. PNG, Mermaid Online Editor üzerinden ayrıca dışa aktarılıp eklenecektir.
- Sayfa ID, süreç sahibi, rol, tarih veya kurumsal kodu tahmin etme; repository ya da Confluence kaynağından doğrula.
- Eski `LST.004` yaklaşımı yeni çalışmalar için kullanılmaz. Mevcut legacy sayfaları açık onay olmadan silme veya taşıma.
- Süreç etkileşimleri `LST.007`, iş ürünleri ve kalite kriterleri `LST.008`, performans ölçümleri `LST.009`, roller ve RACI `LST.010`, süreç gözden geçirme kayıtları `FRM.001` ile yönetilir.
- Kurumsal süreç tasarım dokümanlarında referans proje adı olan “Soru Bankası” kullanılmaz; proje düzeyindeki kanıt kayıtlarında kullanılabilir.

## Ortak süreç doküman seti

Bir süreç için hedeflenen ortak set:

- `İÜC.BİDB.SRÇ.XXX` — Süreç Tanımı
- `İÜC.BİDB.LST.007` — Süreç Etkileşim Matrisi
- `İÜC.BİDB.LST.008` — İş Ürünleri ve Kalite Kriterleri Listesi
- `İÜC.BİDB.LST.009` — Süreç Performans Ölçüm Seti
- `İÜC.BİDB.LST.010` — Süreç Rol, Yetki ve RACI Matrisi
- `İÜC.BİDB.FRM.001` — Süreç Gözden Geçirme Formu

## Yayın ve onay rolleri

- Hazırlayan: Kalite Danışmanı
- Gözden Geçiren: İlgili Süreç Sahibi
- Onaylayan: Bilgi İşlem Daire Başkanı
- Yayımlayan: Proje Geliştirme Yönetimi — Proje Yöneticisi

Rol alanlarında repository/Confluence'daki daha güncel kayıt varsa güncel kayıt esas alınır; uyuşmazlık raporlanır.

## Kanıt ve etik kuralları

- Kanıtları mümkün olduğunca gerçek kaynak sistemlerde göster.
- Geçmiş tarihli sahte kayıt veya geriye dönük kanıt üretme.
- Eksikleri güncel revizyon, tamamlayıcı kayıt, matris, review kaydı veya açık GAP aksiyonu ile kapat.
- GAP durum sözlüğü: `VAR`, `ZAYIF`, `DAĞINIK`, `YOK`, `KAPSAM DIŞI`.
- Proje düzeyi denetim kanıtları belirlenen tek referans proje olan Soru Bankası Projesinden toplanır.

## Güvenlik

- `.env` içeriğini, parolayı, tokenı, API anahtarını veya VPN bilgisini çıktı olarak gösterme ya da commit etme.
- `CONFLUENCE_URL`, `USERNAME` ve `PASSWORD` değerlerini loglara veya raporlara kopyalama.
- `.migration-inbox/` yalnızca yerel aktarım alanıdır ve Git'e eklenmez.
- Telif durumu doğrulanmamış ISO standardı PDF'ini repository'ye ekleme veya GitHub'a push etme.

## Temel doğrulama komutları

Komutları repository kökünden ve mevcut `.venv` ile çalıştır:

```bash
.venv/bin/python scripts/export_confluence_to_repo.py
.venv/bin/python scripts/build_local_viewer.py
.venv/bin/python scripts/publish_confluence_tree.py --dry-run
```

Göreve özel scriptlerde `--dry-run` varsa önce onu kullan. Dry-run desteklemeyen ve Confluence'a yazabilen scriptleri kodunu incelemeden çalıştırma.
