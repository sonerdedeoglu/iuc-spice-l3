# Confluence Çalışma Akışı

## Ön koşullar

- İÜC VPN bağlantısı açık olmalıdır.
- `.env` içinde `CONFLUENCE_URL`, `USERNAME` ve `PASSWORD` yerel olarak tanımlı olmalıdır.
- `.venv` içindeki bağımlılıklar hazır olmalıdır.
- Repository çalışma ağacındaki mevcut kullanıcı değişiklikleri korunmalıdır.

Gizli değerleri terminal çıktısına, rapora veya sohbete kopyalama.

## Salt okunur bağlantı kontrolü

```bash
.venv/bin/python scripts/test_connection.py
```

Bu script kullanıcı adını ekrana yazabilir. Çıktıyı paylaşırken kullanıcı adını maskele.

## Confluence'tan yerel export

```bash
.venv/bin/python scripts/export_confluence_to_repo.py
```

Beklenen sonuçlar:

- `confluence/index.yaml`
- `confluence/pages/**/page.yaml`
- `body.storage.xhtml`
- `body.view.html`
- `reports/confluence_export_report.md`

Exporttan sonra sayfa sayısı, kök sayfa ve uyarılar kontrol edilir.

## Yerel viewer üretimi

```bash
.venv/bin/python scripts/build_local_viewer.py
```

Beklenen çıktı: `viewer/pages.json`.

## Yayın önizlemesi

```bash
.venv/bin/python scripts/publish_confluence_tree.py --dry-run
```

`reports/confluence_tree_publish_report.md` incelenmeden gerçek yayın yapılmaz. Beklenmeyen `CREATE`, `UPDATE` veya `MOVE` varsa yayın durdurulur ve neden araştırılır.

## Gerçek yayın

Yalnızca dry-run sonucu incelendikten ve kullanıcı açıkça onayladıktan sonra:

```bash
.venv/bin/python scripts/publish_confluence_tree.py
```

Toplu yazma yapan görev scriptleri için de aynı kural geçerlidir. Script `--dry-run` desteklemiyorsa önce kodu incelenir ve gerekirse dry-run desteği eklenir.

## Yayın sonrası doğrulama

1. Hedef Confluence sayfalarının sürümü, başlığı, parent bilgisi ve görünümü kontrol edilir.
2. Confluence yeniden export edilir.
3. Viewer yeniden üretilir.
4. İlgili raporlar okunur.
5. `git status` ve `git diff` ile yalnızca beklenen dosyaların değiştiği doğrulanır.
6. Sonuç doğrulandıktan sonra commit/push yapılır.

## Geri dönüş ve güvenlik

- Mevcut sayfa içerikleri exportta bulunduğu için yayın öncesi diff geri dönüş dayanağıdır.
- Sayfa silme desteklenmiş olsa bile açık kullanıcı onayı olmadan silme yapılmaz.
- Page ID veya parent ID tahmin edilmez; `page.yaml` ya da canlı Confluence verisinden alınır.
- Aynı sayfaya birden fazla script ile eşzamanlı yazma yapılmaz.
