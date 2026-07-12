#!/usr/bin/env python3
"""Rework SRÇ.001 according to the updated process definition template.

Changes performed locally in the exported Confluence tree:
- Rebuild İÜC.BİDB.SRÇ.001 - Dokümantasyon Süreci body.storage.xhtml/body.view.html.
- Convert LST.007 from a generic matrix into a SRÇ.001-specific interaction matrix.
- Move LST.007 under the SRÇ.001 process page.
- Update page.yaml and confluence/index.yaml metadata for affected pages.

After running this script, use:
  python scripts/build_local_viewer.py
  python scripts/publish_confluence_tree.py --dry-run
  python scripts/publish_confluence_tree.py
  python scripts/export_confluence_to_repo.py
  python scripts/build_local_viewer.py
"""
from __future__ import annotations

import html
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
CONFLUENCE_DIR = ROOT / "confluence"
ROOT_PAGE = CONFLUENCE_DIR / "pages/000-root-iuc-bidb-spice-2026-level-3"
SRC001_DIR = ROOT_PAGE / "01-surec-dokumanlari/iuc-bidb-src-001-dokumantasyon-sureci"
OLD_LST007_DIR = ROOT_PAGE / "03-kayitlar-ve-listeler/iuc-bidb-lst-007-surec-mimari-ve-etkilesim-matrisi"
NEW_LST007_DIR = SRC001_DIR / "iuc-bidb-lst-007-surec-mimari-ve-etkilesim-matrisi-iuc-bidb-src-001"
INDEX_PATH = CONFLUENCE_DIR / "index.yaml"
REPORT_PATH = ROOT / "reports/src001_rework_report.md"

CSS = (
    'body{margin:0;background:#fff;color:#172b4d;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;line-height:1.55}'
    '.confluence-page{max-width:1180px;margin:0 auto;padding:32px 24px 56px}'
    'h1,h2,h3{color:#0f172a;line-height:1.25}'
    'h1{margin-top:0;padding-bottom:12px;border-bottom:1px solid #d8dee4}'
    'table{width:100%;border-collapse:collapse;margin:16px 0;table-layout:auto}'
    'th,td{border:1px solid #c9d1d9;padding:8px 10px;vertical-align:top}'
    'th{background:#f6f8fa;font-weight:600;text-align:left}'
    'blockquote{margin:16px 0;padding:8px 16px;border-left:4px solid #c9d1d9;color:#57606a;background:#f6f8fa}'
)

PAGES = {
    "SRC001": {"id": "137265842", "title": "İÜC.BİDB.SRÇ.001 - Dokümantasyon Süreci"},
    "SRC002": {"id": "137265860", "title": "İÜC.BİDB.SRÇ.002 - Kalite Güvencesi Süreci"},
    "SRC003": {"id": "137265861", "title": "İÜC.BİDB.SRÇ.003 - Doğrulama Süreci"},
    "SRC004": {"id": "137265862", "title": "İÜC.BİDB.SRÇ.004 - Süreç Kurulumu Süreci"},
    "SRC007": {"id": "137265865", "title": "İÜC.BİDB.SRÇ.007 - Proje Yönetimi Süreci"},
    "SRC016": {"id": "137265874", "title": "İÜC.BİDB.SRÇ.016 - Yapılandırma Yönetimi Süreci"},
    "SRC018": {"id": "137265876", "title": "İÜC.BİDB.SRÇ.018 - Değişiklik Talebi Yönetimi Süreci"},
    "SRC020": {"id": "137265878", "title": "İÜC.BİDB.SRÇ.020 - Eğitim Süreci"},
    "SRC021": {"id": "137265879", "title": "İÜC.BİDB.SRÇ.021 - Bilgi Yönetimi Süreci"},
    "SRC025": {"id": "137265883", "title": "İÜC.BİDB.SRÇ.025 - Ölçüm Süreci"},
    "LST001": {"id": "137265902", "title": "İÜC.BİDB.LST.001 - Aktif Dokümanlar Listesi"},
    "LST002": {"id": "137265903", "title": "İÜC.BİDB.LST.002 - Doküman Değişiklik Kaydı"},
    "LST003": {"id": "137265904", "title": "İÜC.BİDB.LST.003 - Doküman Gözden Geçirme Kaydı"},
    "LST005": {"id": "137265905", "title": "İÜC.BİDB.LST.005 - Yaşam Döngüsü Doküman İhtiyaç Matrisi"},
    "LST007": {"id": "137265907", "title": "İÜC.BİDB.LST.007 - Süreç Mimari ve Etkileşim Matrisi (İÜC.BİDB.SRÇ.001)"},
    "LST008": {"id": "137265843", "title": "İÜC.BİDB.LST.008 - İş Ürünleri ve Kalite Kriterleri Listesi (İÜC.BİDB.SRÇ.001)"},
    "LST009": {"id": "137265844", "title": "İÜC.BİDB.LST.009 - Süreç Performans Ölçüm Seti (İÜC.BİDB.SRÇ.001)"},
    "LST010": {"id": "137265845", "title": "İÜC.BİDB.LST.010 - Süreç Rol Yetki ve RACI Matrisi (İÜC.BİDB.SRÇ.001)"},
    "LST011": {"id": "137265911", "title": "İÜC.BİDB.LST.011 - Repository Yapısı"},
    "LST012": {"id": "137265912", "title": "İÜC.BİDB.LST.012 - Süreç Yaygınlaştırma ve Bilgilendirme Kaydı"},
    "KLV001": {"id": "137265913", "title": "İÜC.BİDB.KLV.001 - Doküman Yazım Kuralları Talimatı"},
    "KLV002": {"id": "137265914", "title": "İÜC.BİDB.KLV.002 - Süreç Uyarlama Kılavuzu"},
    "KLV003": {"id": "137265915", "title": "İÜC.BİDB.KLV.003 - Süreç Tasarımı Kontrol Kılavuzu"},
    "KLV004": {"id": "137266057", "title": "İÜC.BİDB.KLV.004 - Dokümantasyon Deposu Oluşturma Kılavuzu"},
    "PRS001": {"id": "137265916", "title": "İÜC.BİDB.PRS.001 - Yazılım Projeleri Dokümantasyon Prosedürü"},
}


def e(value: object) -> str:
    return html.escape(str(value), quote=False)


def link(key: str) -> str:
    item = PAGES[key]
    return f'<a href="/pages/viewpage.action?pageId={item["id"]}">{e(item["title"])}</a>'


def table(headers: list[str], rows: list[list[str]]) -> str:
    head = "".join(f"<th>{e(h)}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>" for row in rows)
    return f'<table class="wrapped"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>'


def read_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def write_yaml(path: Path, data: dict[str, Any]) -> None:
    path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")


def view_html(title: str, storage_body: str) -> str:
    return f"""<!doctype html>
<html lang="tr">
<head>
  <meta charset="utf-8">
  <title>{e(title)}</title>
  <style>{CSS}</style>
</head>
<body>
<main class="confluence-page">
<h1>{e(title)}</h1>
{storage_body}
</main>
</body>
</html>
"""


def src001_body() -> str:
    upper = table(
        ["Alan", "Değer"],
        [
            ["Kurum", "İstanbul Üniversitesi - Cerrahpaşa Bilgi İşlem Daire Başkanlığı"],
            ["Doküman Kodu", "İÜC.BİDB.SRÇ.001"],
            ["Doküman Türü", "Süreç"],
            ["Kullanım Alanı", "Süreç Tanımı"],
            ["Süreç ID", "İÜC.BİDB.SRÇ.001"],
            ["Süreç Adı", "Dokümantasyon Süreci"],
            ["Süreç Referansı", "ISO/IEC 15504-5 SUP.7 - Documentation"],
            ["Süreç Sahibi", "Levent BAYEZİT - Proje Yöneticisi"],
            ["Durum", "Aktif"],
            ["Sürüm", "v1.0"],
            ["Yürürlük Tarihi", "29-06-2026"],
            ["Son Gözden Geçirme Tarihi", "01-07-2026"],
            ["Güncelleme Sıklığı", "Yılda bir veya ihtiyaç halinde"],
        ],
    )

    refs = table(
        ["Referans", "Açıklama"],
        [
            ["ISO/IEC 15504-5 SUP.7 - Documentation", "Dokümantasyon sürecinin SPICE süreç referansı"],
            [link("PRS001"), "Yazılım projelerinde dokümantasyon stratejisi, doküman üretimi ve kontrol kuralları"],
            [link("LST001"), "Aktif doküman envanteri ve erişim listesi"],
            [link("LST002"), "Doküman değişikliklerinin izlenmesi"],
            [link("LST003"), "Doküman gözden geçirme kayıtlarının izlenmesi"],
            [link("LST005"), "Yaşam döngüsü aşamalarına göre doküman ihtiyaçlarının belirlenmesi"],
            [link("LST007"), "SRÇ.001 süreç etkileşimlerinin yönetilmesi"],
            [link("LST008"), "SRÇ.001 iş ürünleri ve kalite kriterlerinin yönetilmesi"],
            [link("LST009"), "SRÇ.001 performans ölçümlerinin yönetilmesi"],
            [link("LST010"), "SRÇ.001 rol, yetki, RACI ve yetkinlik kayıtlarının yönetilmesi"],
            [link("LST011"), "Dokümantasyon repository yapısının izlenmesi"],
            [link("LST012"), "Süreç yaygınlaştırma ve bilgilendirme kayıtları"],
            [link("KLV001"), "Doküman yazım kuralları"],
            [link("KLV002"), "Süreç uyarlama yaklaşımı"],
            [link("KLV003"), "Süreç tasarım kontrol yaklaşımı"],
            [link("KLV004"), "Dokümantasyon deposu oluşturma yaklaşımı"],
        ],
    )

    terms = table(
        ["Terim / Kısaltma", "Açıklama"],
        [
            ["Doküman", "Kurumsal süreçlerin, yazılım projelerinin veya destek faaliyetlerinin uygulanması için oluşturulan kontrollü yazılı bilgi"],
            ["Kayıt", "Bir faaliyetin gerçekleştiğini, bir kararın alındığını veya bir kontrolün yapıldığını gösteren kanıt niteliğindeki bilgi"],
            ["Repository", "Dokümanların yayımlandığı, erişime açıldığı ve saklandığı merkezi alan"],
            ["Şablon", "Belirli doküman türlerinin standart yapıda üretilmesi için kullanılan doküman kalıbı"],
            ["Gözden Geçirme", "Dokümanın belirlenen kalite kriterlerine ve kullanım amacına uygunluğunun kontrol edilmesi"],
            ["Onay", "Dokümanın yürürlüğe alınmadan önce yetkili rol veya kişi tarafından kabul edilmesi"],
            ["Yayın", "Onaylanan dokümanın ilgili hedef kitle tarafından erişilebilir hale getirilmesi"],
            ["Bakım", "Dokümanın güncelliğinin, geçerliliğinin ve erişilebilirliğinin sürdürülmesi"],
            ["SUP.7", "ISO/IEC 15504-5 içinde tanımlanan Documentation süreci"],
            ["SRÇ", "Süreç dokümanı kod ön eki"],
            ["LST", "Liste / kayıt dokümanı kod ön eki"],
            ["FRM", "Form dokümanı kod ön eki"],
            ["PRS", "Prosedür dokümanı kod ön eki"],
            ["KLV", "Kılavuz / talimat dokümanı kod ön eki"],
        ],
    )

    summary = table(
        ["Alan", "Açıklama"],
        [
            ["Süreç Başlatıcısı", "Yeni doküman ihtiyacı, doküman değişiklik ihtiyacı, proje yaşam döngüsü aşaması, süreç kurulumu, dönemsel gözden geçirme veya denetim/iyileştirme ihtiyacı"],
            ["Süreç Başlangıcı", "Doküman ihtiyacının veya doküman değişiklik ihtiyacının belirlenmesi"],
            ["Süreç Bitişi", "Dokümanın yayımlanması, güncellenmesi, pasife alınması, arşivlenmesi veya ilgili kayıtların güncellenmesi"],
            ["Ana Faaliyetler", "Dokümantasyon stratejisini belirleme; doküman standartlarını ve gereksinimlerini tanımlama; üretilecek dokümanları belirleme; doküman geliştirme; gözden geçirme ve onaylama; yayınlama ve dağıtma; bakım ve değişiklik yönetimi"],
            ["İlgili Süreçler", f"{link('SRC002')}, {link('SRC003')}, {link('SRC004')}, {link('SRC007')}, {link('SRC016')}, {link('SRC018')}, {link('SRC020')}, {link('SRC021')}, {link('SRC025')}"],
        ],
    )

    roles = table(
        ["Referans Kayıt", "Kullanım"],
        [
            [link("LST010"), "SRÇ.001 kapsamındaki rol, sorumluluk, yetki, RACI ve yetkinlik bilgilerinin güncel kaydıdır. Bu süreç dokümanında rol tanımları tekrar edilmez; güncel sorumluluk matrisi LST.010 üzerinden yönetilir."],
        ],
    )

    inputs = table(
        ["Girdi", "Kaynak", "Kullanım Amacı"],
        [
            ["Yeni doküman ihtiyacı", "Süreç sahibi, proje ekibi, yönetim, denetim veya süreç kurulumu faaliyeti", "Üretilecek dokümanın türünün, kapsamının ve sorumlusunun belirlenmesi"],
            ["Doküman değişiklik ihtiyacı", "Kullanıcılar, süreç sahipleri, proje ekibi, gözden geçirme veya değişiklik yönetimi süreci", "Mevcut dokümanın güncellenmesi, pasife alınması veya arşivlenmesi"],
            ["Yaşam döngüsü doküman ihtiyacı", link("LST005"), "Yazılım proje yaşam döngüsü aşamalarında hangi dokümanın üretileceğinin belirlenmesi"],
            ["Doküman türü ve kod yapısı", f"{link('LST001')} ve {link('KLV001')}", "Dokümanın kurumsal sınıflandırma, kodlama ve adlandırma yapısına uygun hazırlanması"],
            ["Şablonlar", "02 - Şablonlar alanı", "Dokümanın standart içerik yapısına göre hazırlanması"],
            ["Gözden geçirme görüşleri", f"{link('LST003')} ve {link('SRC003')}", "Dokümanın kalite kriterlerine ve kullanım amacına uygunluğunun kontrol edilmesi"],
            ["Onay kararı", "Süreç sahibi / yetkili onay rolü", "Dokümanın yürürlüğe alınması veya revizyon ihtiyacının belirlenmesi"],
            ["Repository bilgisi", f"{link('LST011')} ve {link('KLV004')}", "Dokümanın yayımlanacağı alanın ve erişim linkinin belirlenmesi"],
        ],
    )

    outputs = table(
        ["Çıktı / Kayıt / Doküman", "Açıklama", "Saklama Yeri"],
        [
            [link("PRS001"), "Yazılım projeleri ve süreç dokümantasyonu için dokümantasyon yaklaşımını tanımlar.", "07 - Prosedürler"],
            [link("LST001"), "Aktif doküman envanterini, sahiplik ve erişim bilgisini gösterir.", "SRÇ.001 altı"],
            [link("LST002"), "Doküman değişikliklerinin kayıt altına alınmasını sağlar.", "03 - Kayıtlar ve Listeler"],
            [link("LST003"), "Doküman gözden geçirme kayıtlarını izler.", "03 - Kayıtlar ve Listeler"],
            [link("LST005"), "Yaşam döngüsü aşamalarında üretilecek doküman ihtiyaçlarını gösterir.", "03 - Kayıtlar ve Listeler"],
            [link("LST007"), "SRÇ.001'in diğer süreçlerle etkileşimlerini tanımlar.", "SRÇ.001 altı"],
            [link("LST008"), "SRÇ.001 iş ürünlerini ve kalite kriterlerini tanımlar.", "SRÇ.001 altı"],
            [link("LST009"), "SRÇ.001 performans ölçümlerini tanımlar.", "SRÇ.001 altı"],
            [link("LST010"), "SRÇ.001 rol, yetki, RACI ve yetkinlik kaydını yönetir.", "SRÇ.001 altı"],
            [link("LST011"), "Dokümantasyon repository yapısını gösterir.", "03 - Kayıtlar ve Listeler"],
            [link("LST012"), "Süreç yaygınlaştırma ve bilgilendirme kayıtlarını izler.", "03 - Kayıtlar ve Listeler"],
        ],
    )

    activities = table(
        ["No", "Faaliyet", "Açıklama", "İlgili BP", "Kayıt / Kanıt"],
        [
            ["1", "Dokümantasyon ihtiyacını belirleme", "Süreç, proje veya destek faaliyeti kapsamında üretilecek/güncellenecek doküman ihtiyacı belirlenir.", "SUP.7.BP1, SUP.7.BP4", f"{link('LST001')}, {link('LST005')}, {link('LST007')}"] ,
            ["2", "Doküman standardını ve gereksinimlerini belirleme", "Doküman türü, kodu, şablonu, zorunlu üst bilgileri, gözden geçirme ve onay beklentileri belirlenir.", "SUP.7.BP2, SUP.7.BP3", f"{link('KLV001')}, {link('LST008')}"] ,
            ["3", "Dokümanı hazırlama", "Doküman ilgili şablona ve yazım kurallarına uygun olarak hazırlanır veya güncellenir.", "SUP.7.BP5", "İlgili süreç/doküman şablonu"],
            ["4", "Dokümanı gözden geçirme", "Doküman içerik, format, izlenebilirlik ve kalite kriterleri açısından gözden geçirilir.", "SUP.7.BP6", f"{link('LST003')}, {link('SRC003')}"] ,
            ["5", "Dokümanı onaylama", "Uygun bulunan doküman yetkili rol veya kişi tarafından onaylanır.", "SUP.7.BP6", f"{link('LST001')}, onay bilgileri"],
            ["6", "Dokümanı yayımlama ve erişime açma", "Onaylı doküman repository yapısına uygun alanda yayımlanır ve erişim bilgisi kayıt altına alınır.", "SUP.7.BP7", f"{link('LST001')}, {link('LST011')}, {link('KLV004')}"] ,
            ["7", "Dokümanı yaygınlaştırma", "Gerekli hedef kitleler bilgilendirilir; bilgilendirme kaydı tutulur.", "SUP.7.BP7", link("LST012")],
            ["8", "Dokümanı sürdürme", "Doküman dönemsel gözden geçirme, değişiklik talebi veya iyileştirme ihtiyacına göre güncellenir, pasife alınır veya arşivlenir.", "SUP.7.BP8", f"{link('LST002')}, {link('LST003')}, {link('LST001')}"] ,
        ],
    )

    controls = table(
        ["Kontrol Alanı", "Kontrol Yaklaşımı", "Kanıt / Kayıt"],
        [
            ["İş ürünleri ve kalite kriterleri", "SRÇ.001 kapsamında üretilen doküman/kayıtların kalite beklentileri LST.008 üzerinden izlenir.", link("LST008")],
            ["Performans ölçümü", "Süreç performansı LST.009'da tanımlanan ölçümlerle izlenir.", link("LST009")],
            ["Rol ve sorumluluklar", "Süreç rol, yetki ve sorumlulukları LST.010 üzerinden yönetilir.", link("LST010")],
            ["Süreç etkileşimleri", "SRÇ.001'in diğer süreçlerle arayüzleri LST.007 üzerinden yönetilir.", link("LST007")],
            ["Süreç gözden geçirme", "Sürecin BP ve PA/GP bazlı gözden geçirmesi FRM.001 ile kayıt altına alınır.", "İÜC.BİDB.FRM.001 - Süreç Gözden Geçirme Formu (İÜC.BİDB.SRÇ.001)"],
        ],
    )

    return f"""{upper}
<blockquote><p><strong>Kullanım Notu</strong><br/>Bu doküman, İÜC BİDB dokümantasyon yönetimi faaliyetlerinin ISO/IEC 15504-5 SUP.7 beklentileriyle uyumlu biçimde tanımlanması, uygulanması ve izlenmesi için hazırlanmıştır.</p></blockquote>
<hr/>
<h2>1. Amaç</h2>
<p>Bu sürecin amacı, İÜC BİDB bünyesinde yürütülen süreçler, yazılım projeleri ve destek faaliyetleri sırasında üretilen doküman ve kayıt bilgilerinin geliştirilmesi, gözden geçirilmesi, onaylanması, yayımlanması, erişilebilir tutulması ve yaşam döngüsü boyunca güncel olarak sürdürülmesidir.</p>
<p>Dokümantasyon Süreci; doküman yönetimi stratejisini, kullanılacak doküman standartlarını, üretilecek dokümanların belirlenmesini, doküman içerik ve kalite beklentilerini, onay/yayın/dağıtım yaklaşımını ve bakım kurallarını tanımlar.</p>

<h2>2. Kapsam</h2>
{table(["Kapsam Öğesi", "Açıklama"], [
    ["Kapsama Dahil", "Süreç dokümanları, şablonlar, kayıt listeleri, formlar, politikalar, kılavuzlar/talimatlar, prosedürler, planlar, yazılım proje dokümantasyonu ve bunlara ilişkin gözden geçirme/onay/yayın/bakım kayıtları"],
    ["Kapsam Dışı", "Kurumsal dokümantasyon yapısına dahil olmayan kişisel çalışma notları, geçici taslaklar ve resmi kayıt niteliği taşımayan çalışma kopyaları"],
    ["Uygulama Alanı", "İÜC BİDB süreçleri, yazılım projeleri, proje yönetimi, analiz, tasarım, geliştirme, test, yayın, bakım, değişiklik ve problem çözümü faaliyetleri"],
])}

<h2>3. Referanslar</h2>
{refs}

<h2>4. Terimler ve Kısaltmalar</h2>
{terms}

<h2>5. Süreç Özeti</h2>
{summary}

<h2>6. Roller ve Sorumluluklar</h2>
<p>Bu bölümde süreç rol tanımları tekrar yazılmaz. Sürece ait rol, sorumluluk, yetki, RACI ve yetkinlik bilgileri ilgili süreç için oluşturulan referans kayıt üzerinden yönetilir.</p>
{roles}

<h2>7. Süreç Girdileri</h2>
{inputs}

<h2>8. Süreç Çıktıları</h2>
{outputs}

<h2>9. Süreç Faaliyetleri</h2>
{activities}

<h2>10. Süreç Kontrolleri ve İzleme</h2>
{controls}
"""


def lst007_body() -> str:
    upper = table(
        ["Alan", "Değer"],
        [
            ["Kurum", "İstanbul Üniversitesi - Cerrahpaşa Bilgi İşlem Daire Başkanlığı"],
            ["Doküman Kodu", "İÜC.BİDB.LST.007"],
            ["Doküman Türü", "Kayıt Listesi / Matris"],
            ["İlişkili Süreç", "İÜC.BİDB.SRÇ.001 - Dokümantasyon Süreci"],
            ["Süreç Referansı", "ISO/IEC 15504-5 SUP.7 - Documentation"],
            ["Doküman Sahibi", "Levent BAYEZİT - Proje Yöneticisi"],
            ["Hazırlayan", "Soner DEDEOĞLU - Kalite Danışmanı"],
            ["Durum", "Aktif"],
            ["Sürüm", "v1.0"],
            ["Yürürlük Tarihi", "01-09-2025"],
            ["Güncelleme Sıklığı", "Yılda bir veya süreç değişikliğinde"],
        ],
    )
    matrix = table(
        ["İlişkili Süreç", "Etkileşim Yönü", "SRÇ.001'e Gelen Girdi", "SRÇ.001'den Çıkan Çıktı", "Kullanım Amacı", "Kanıt / Kayıt", "Sorumlu Rol", "Sıklık / Tetikleyici"],
        [
            [link("SRC002"), "Çift yönlü", "Kalite kriteri, uygunsuzluk, kalite güvence geri bildirimi", "Güncel doküman, gözden geçirme/onay kayıtları", "Dokümanların kalite beklentilerine uygunluğunu güvence altına almak", f"{link('LST003')}, {link('LST008')}", "Süreç Sahibi / Kalite Danışmanı", "Dönemsel veya uygunsuzluk oluştuğunda"],
            [link("SRC003"), "Girdi alır", "Doğrulama/gözden geçirme sonucu", "Güncellenmiş veya onaylanmış doküman", "Dokümanların yayımdan önce kontrol edilmesini sağlamak", link("LST003"), "Gözden Geçiren", "Doküman yayın veya revizyon öncesi"],
            [link("SRC004"), "Çift yönlü", "Yeni süreç kurulum ihtiyacı, süreç mimarisi, süreç şablonu", "Süreç dokümanı, süreç özel listeler ve kayıtlar", "Yeni süreçlerin standart dokümantasyon yapısına göre kurulmasını sağlamak", f"{link('LST007')}, {link('KLV003')}", "Süreç Sahibi / Süreç Kurulum Sorumlusu", "Yeni süreç kurulumu veya süreç revizyonu"],
            [link("SRC007"), "Girdi alır", "Proje yaşam döngüsü aşaması ve proje doküman ihtiyacı", "Proje doküman şablonu, doküman ihtiyaç matrisi ve aktif doküman kaydı", "Projelerde ihtiyaç duyulan dokümanların yaşam döngüsüyle uyumlu üretilmesini sağlamak", f"{link('PRS001')}, {link('LST005')}", "Proje Yöneticisi / Süreç Sahibi", "Proje başlangıcı ve aşama geçişlerinde"],
            [link("SRC016"), "Çift yönlü", "Baseline, yapılandırma kontrolü, repository gereksinimi", "Kontrollü doküman, sürüm bilgisi ve erişim linki", "Dokümanların kontrollü yapılandırma öğesi olarak yönetilmesini sağlamak", f"{link('LST001')}, {link('LST011')}, {link('KLV004')}", "Doküman Yöneticisi / Konfigürasyon Sorumlusu", "Doküman yayın, değişiklik ve arşiv işlemlerinde"],
            [link("SRC018"), "Girdi alır", "Doküman değişiklik talebi", "Güncellenmiş doküman ve değişiklik kaydı", "Doküman değişikliklerinin izlenebilir şekilde yönetilmesini sağlamak", link("LST002"), "Süreç Sahibi", "Değişiklik talebi oluştuğunda"],
            [link("SRC020"), "Çıktı verir", "Süreç yaygınlaştırma ihtiyacı", "Bilgilendirme içeriği ve süreç duyurusu", "Dokümantasyon sürecinin ilgili personele duyurulmasını sağlamak", link("LST012"), "Süreç Sahibi / Eğitim Sorumlusu", "Yeni yayın veya önemli revizyon sonrasında"],
            [link("SRC021"), "Çıktı verir", "Kurumsal bilgi yönetimi ihtiyacı", "Erişilebilir güncel doküman ve kayıt seti", "Dokümanların kurumsal bilgi varlığı olarak saklanmasını sağlamak", f"{link('LST001')}, {link('LST011')}", "Doküman Yöneticisi", "Sürekli"],
            [link("SRC025"), "Çift yönlü", "Ölçüm tanımı ve ölçüm ihtiyacı", "Dokümantasyon süreci ölçüm sonuçları", "Sürecin performansının izlenmesini ve iyileştirilmesini sağlamak", link("LST009"), "Süreç Sahibi / Ölçüm Sorumlusu", "Dönemsel ölçüm dönemlerinde"],
        ],
    )
    return f"""{upper}
<h2>1. Amaç</h2>
<p>Bu matris, İÜC.BİDB.SRÇ.001 - Dokümantasyon Süreci'nin diğer süreçlerle olan girdi/çıktı, sorumluluk, kayıt ve tetikleyici ilişkilerini süreç özelinde tanımlamak için kullanılır.</p>

<h2>2. Süreç Etkileşim Matrisi</h2>
{matrix}

<h2>3. Kullanım ve Bakım</h2>
<p>Bu matris, SRÇ.001 süreç tanımı, ilişkili süreçler, doküman repository yapısı veya süreç mimarisi değiştiğinde gözden geçirilir. Etkileşimlerde ortaya çıkan yeni kayıt veya doküman ihtiyaçları LST.001, LST.008, LST.009 ve LST.010 kayıtlarıyla birlikte güncellenir.</p>
"""


def update_page(folder: Path, title: str, storage_body: str, metadata_updates: dict[str, Any]) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "body.storage.xhtml").write_text(storage_body.strip() + "\n", encoding="utf-8")
    (folder / "body.view.html").write_text(view_html(title, storage_body), encoding="utf-8")
    meta = read_yaml(folder / "page.yaml")
    meta.update(metadata_updates)
    meta["title"] = title
    meta["storage_file"] = "body.storage.xhtml"
    meta["view_file"] = "body.view.html"
    write_yaml(folder / "page.yaml", meta)


def move_lst007_if_needed() -> None:
    if OLD_LST007_DIR.exists():
        if NEW_LST007_DIR.exists():
            shutil.rmtree(NEW_LST007_DIR)
        OLD_LST007_DIR.rename(NEW_LST007_DIR)
    elif not NEW_LST007_DIR.exists():
        NEW_LST007_DIR.mkdir(parents=True)


def update_index() -> None:
    if not INDEX_PATH.exists():
        return
    data = read_yaml(INDEX_PATH)
    pages = data.get("pages", []) or []
    old_path = "pages/000-root-iuc-bidb-spice-2026-level-3/03-kayitlar-ve-listeler/iuc-bidb-lst-007-surec-mimari-ve-etkilesim-matrisi"
    new_path = "pages/000-root-iuc-bidb-spice-2026-level-3/01-surec-dokumanlari/iuc-bidb-src-001-dokumantasyon-sureci/iuc-bidb-lst-007-surec-mimari-ve-etkilesim-matrisi-iuc-bidb-src-001"
    updated_lst007 = False
    for page in pages:
        if page.get("relative_path") == old_path or page.get("page_id") == PAGES["LST007"]["id"]:
            page.update({
                "page_id": PAGES["LST007"]["id"],
                "title": PAGES["LST007"]["title"],
                "parent_id": PAGES["SRC001"]["id"],
                "depth": 3,
                "relative_path": new_path,
                "slug": NEW_LST007_DIR.name,
                "storage_file": f"{new_path}/body.storage.xhtml",
                "view_file": f"{new_path}/body.view.html",
            })
            updated_lst007 = True
    if not updated_lst007:
        pages.append({
            "page_id": PAGES["LST007"]["id"],
            "title": PAGES["LST007"]["title"],
            "parent_id": PAGES["SRC001"]["id"],
            "depth": 3,
            "relative_path": new_path,
            "slug": NEW_LST007_DIR.name,
            "storage_file": f"{new_path}/body.storage.xhtml",
            "view_file": f"{new_path}/body.view.html",
        })
    data["pages"] = pages
    data["total_page_count"] = len(pages)
    data["exported_at"] = datetime.now(timezone.utc).isoformat()
    write_yaml(INDEX_PATH, data)


def write_report() -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        "# SRÇ.001 Dokümantasyon Süreci Yeniden Düzenleme Raporu\n\n"
        "Yapılan işlemler:\n\n"
        "- SRÇ.001 süreç tanımı yeni süreç şablonu yapısına göre yeniden oluşturuldu.\n"
        "- LST.007 genel matris yapısından SRÇ.001 özel süreç etkileşim matrisi haline getirildi.\n"
        "- LST.007, SRÇ.001 süreç klasörü altına taşındı.\n"
        "- page.yaml ve confluence/index.yaml kayıtları güncellendi.\n\n",
        encoding="utf-8",
    )


def main() -> None:
    update_page(
        SRC001_DIR,
        PAGES["SRC001"]["title"],
        src001_body(),
        {
            "page_id": PAGES["SRC001"]["id"],
            "space": "SSSS",
            "parent_id": "137265784",
            "parent_title": "01 - Süreç Dokümanları",
            "depth": 2,
            "status": "active",
            "relative_path": str(SRC001_DIR.relative_to(CONFLUENCE_DIR)).replace("\\", "/"),
            "slug": SRC001_DIR.name,
        },
    )
    move_lst007_if_needed()
    update_page(
        NEW_LST007_DIR,
        PAGES["LST007"]["title"],
        lst007_body(),
        {
            "page_id": PAGES["LST007"]["id"],
            "space": "SSSS",
            "parent_id": PAGES["SRC001"]["id"],
            "parent_title": PAGES["SRC001"]["title"],
            "depth": 3,
            "status": "active",
            "relative_path": str(NEW_LST007_DIR.relative_to(CONFLUENCE_DIR)).replace("\\", "/"),
            "slug": NEW_LST007_DIR.name,
            "document_code": "İÜC.BİDB.LST.007",
            "related_process_code": "İÜC.BİDB.SRÇ.001",
            "related_process_name": "Dokümantasyon Süreci",
            "spice_reference": "SUP.7 - Documentation",
        },
    )
    update_index()
    write_report()
    print("[DONE] SRÇ.001 süreç tanımı ve LST.007 etkileşim matrisi güncellendi.")
    print(f"[REPORT] {REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
