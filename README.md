# İÜC BİDB SPICE 2026 Level 3

Bu repository, İstanbul Üniversitesi-Cerrahpaşa Bilgi İşlem Daire Başkanlığının 26 süreçlik SPICE Seviye 3 hazırlık dokümantasyonunu ve Confluence senkronizasyon araçlarını içerir.

## Başlangıç

Yeni bir çalışma öncesinde:

1. `AGENTS.md` talimatlarını okuyun.
2. `docs/PROJECT_CONTEXT.md` ve `docs/CURRENT_STATUS.md` dosyalarını inceleyin.
3. Confluence işlemleri için `docs/CONFLUENCE_WORKFLOW.md` akışını izleyin.

## Temel dizinler

- `confluence/pages/`: Confluence sayfa exportları ve metadata
- `scripts/`: export, publish, doğrulama ve içerik üretim araçları
- `reports/`: dry-run, audit, normalizasyon ve doğrulama raporları
- `resources/standards/`: işlenebilir SPICE standart verisi
- `viewer/`: yerel Confluence görüntüleyicisi
- `docs/`: kalıcı proje bağlamı ve kararları

## Güvenlik

`.env`, parola, token ve VPN bilgileri Git'e eklenmez. Confluence'a gerçek yayın yapılmadan önce dry-run zorunludur.
