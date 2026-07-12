#!/usr/bin/env python3
"""Rework only İÜC.BİDB.SRÇ.001 according to the current process definition template.

Scope is deliberately limited:
- Updates only İÜC.BİDB.SRÇ.001 - Dokümantasyon Süreci.
- Does not move, rename or edit LST.007 or any other related document.
- Reads the current İÜC.BİDB.SRÇ.XXX.Ş template and preserves its numbered section order.
- Skips every template-only section whose heading starts with 0.

After running this script, use:
  python scripts/build_local_viewer.py
"""
from __future__ import annotations

import html
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
CONFLUENCE_DIR = ROOT / "confluence"
ROOT_PAGE = CONFLUENCE_DIR / "pages/000-root-iuc-bidb-spice-2026-level-3"
SRC001_DIR = ROOT_PAGE / "01-surec-dokumanlari/iuc-bidb-src-001-dokumantasyon-sureci"
TEMPLATE_DIR = ROOT_PAGE / "02-sablonlar/iuc-bidb-src-xxx-s-surec-tanimi-sablonu"
INDEX_PATH = CONFLUENCE_DIR / "index.yaml"
REPORT_PATH = ROOT / "reports/src001_rework_report.md"

SRC001_TITLE = "İÜC.BİDB.SRÇ.001 - Dokümantasyon Süreci"
SRC001_CODE = "İÜC.BİDB.SRÇ.001"

CSS = (
    'body{margin:0;background:#fff;color:#172b4d;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;line-height:1.55}'
    '.confluence-page{max-width:1180px;margin:0 auto;padding:32px 24px 56px}'
    'h1,h2,h3{color:#0f172a;line-height:1.25}'
    'h1{margin-top:0;padding-bottom:12px;border-bottom:1px solid #d8dee4}'
    'table{width:100%;border-collapse:collapse;margin:16px 0;table-layout:auto}'
    'th,td{border:1px solid #c9d1d9;padding:8px 10px;vertical-align:top}'
    'th{background:#f6f8fa;font-weight:600;text-align:left}'
)


def e(value: object) -> str:
    return html.escape(str(value), quote=False)


def read_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def write_yaml(path: Path, data: dict[str, Any]) -> None:
    path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")


def strip_tags(value: str) -> str:
    value = re.sub(r"<[^>]+>", "", value)
    return re.sub(r"\s+", " ", html.unescape(value)).strip()


def extract_template_sections() -> list[str]:
    template_body = (TEMPLATE_DIR / "body.storage.xhtml").read_text(encoding="utf-8")
    headings = [strip_tags(match) for match in re.findall(r"<h2[^>]*>(.*?)</h2>", template_body, flags=re.I | re.S)]
    sections = [heading for heading in headings if heading and not re.match(r"^\s*0\s*[\.-]", heading)]
    if not sections:
        raise RuntimeError("Şablondan numaralı bölüm başlıkları okunamadı.")
    if not sections[0].startswith("1."):
        raise RuntimeError(f"Şablonun ilk uygulama bölümü '1.' ile başlamıyor: {sections[0]}")
    return sections


def load_index_pages() -> dict[str, dict[str, str]]:
    data = read_yaml(INDEX_PATH)
    pages: dict[str, dict[str, str]] = {}
    for page in data.get("pages", []) or []:
        title = str(page.get("title") or "")
        if not title:
            continue
        pages[title] = {
            "page_id": str(page.get("page_id") or ""),
            "title": title,
        }
    return pages


PAGES = load_index_pages()


def link(title: str) -> str:
    page = PAGES.get(title)
    if not page or not page.get("page_id"):
        return e(title)
    return f'<a href="/pages/viewpage.action?pageId={page["page_id"]}">{e(title)}</a>'


def table(headers: list[str], rows: list[list[str]]) -> str:
    head = "".join(f'<th class="confluenceTh">{e(header)}</th>' for header in headers)
    body_rows = []
    for row in rows:
        cells = "".join(f'<td class="confluenceTd">{cell}</td>' for cell in row)
        body_rows.append(f"<tr>{cells}</tr>")
    body = "".join(body_rows)
    return f'<div class="table-wrap"><table class="wrapped confluenceTable"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def p(text: str) -> str:
    return f"<p>{e(text)}</p>"


def meta_table() -> str:
    return table(
        ["Alan", "Değer"],
        [
            ["Kurum", "İstanbul Üniversitesi - Cerrahpaşa Bilgi İşlem Daire Başkanlığı"],
            ["Doküman Kodu", SRC001_CODE],
            ["Doküman Türü", "Süreç"],
            ["Kullanım Alanı", "Süreç Tanımı"],
            ["Süreç ID", SRC001_CODE],
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


def content_amac() -> str:
    return "".join(
        [
            p("Bu sürecin amacı, İÜC BİDB bünyesinde yürütülen süreçler, yazılım projeleri ve destek faaliyetleri sırasında üretilen doküman ve kayıtların standart biçimde geliştirilmesini, yayımlanmasını, erişilebilir tutulmasını, güncel kalmasını ve yaşam döngüsü boyunca kontrollü şekilde sürdürülmesini sağlamaktır."),
            p("Süreç; doküman stratejisinin belirlenmesi, doküman standartlarının uygulanması, üretilecek dokümanların tanımlanması, dokümanların gözden geçirilmesi, onaylanması, yayımlanması, dağıtılması ve bakımının yapılması için kurumsal kuralları tanımlar."),
        ]
    )


def content_kapsam() -> str:
    return "".join(
        [
            p("Bu süreç, İÜC BİDB kurumsal süreç dokümantasyonu ve yazılım proje dokümantasyonu kapsamında kullanılan dokümanların oluşturulması, gözden geçirilmesi, onaylanması, yayımlanması, dağıtılması, güncellenmesi ve arşivlenmesi faaliyetlerini kapsar."),
            table(
                ["Kapsam Öğesi", "Açıklama"],
                [
                    ["Kapsama Dahil", "Süreç tanımları, şablonlar, kayıt listeleri, formlar, prosedürler, kılavuzlar, planlar, proje yaşam döngüsü dokümanları ve bu dokümanlara ilişkin değişiklik/gözden geçirme kayıtları"],
                    ["Kapsam Dışı", "Kurumsal dokümantasyon yapısına dahil olmayan kişisel çalışma notları, geçici taslaklar ve resmi doküman/kayıt niteliği taşımayan ara çalışmalar"],
                    ["Uygulama Alanı", "İÜC BİDB süreçleri, yazılım proje yaşam döngüsü faaliyetleri, destek süreçleri ve denetim hazırlık çalışmaları"],
                ],
            ),
        ]
    )


def content_referanslar() -> str:
    return table(
        ["Referans", "Açıklama"],
        [
            ["ISO/IEC 15504-5 SUP.7 - Documentation", "Dokümantasyon sürecinin SPICE süreç referansı"],
            [link("İÜC.BİDB.PRS.001 - Yazılım Projeleri Dokümantasyon Prosedürü"), "Yazılım projeleri için dokümantasyon stratejisi, doküman üretimi ve kontrol kuralları"],
            [link("İÜC.BİDB.LST.001 - Aktif Dokümanlar Listesi"), "Aktif doküman envanteri ve erişim kayıtları"],
            [link("İÜC.BİDB.LST.002 - Doküman Değişiklik Kaydı"), "Doküman değişikliklerinin izlenmesi"],
            [link("İÜC.BİDB.LST.003 - Doküman Gözden Geçirme Kaydı"), "Doküman gözden geçirme kayıtlarının izlenmesi"],
            [link("İÜC.BİDB.LST.005 - Yaşam Döngüsü Doküman İhtiyaç Matrisi"), "Yaşam döngüsü aşamalarına göre doküman ihtiyaçlarının belirlenmesi"],
            [link("İÜC.BİDB.LST.007 - Süreç Mimari ve Etkileşim Matrisi"), "Süreçler arası etkileşimlerin yönetilmesi"],
            [link("İÜC.BİDB.LST.008 - İş Ürünleri ve Kalite Kriterleri Listesi (İÜC.BİDB.SRÇ.001)"), "SRÇ.001 iş ürünleri ve kalite kriterleri"],
            [link("İÜC.BİDB.LST.009 - Süreç Performans Ölçüm Seti (İÜC.BİDB.SRÇ.001)"), "SRÇ.001 performans ölçümleri"],
            [link("İÜC.BİDB.LST.010 - Süreç Rol Yetki ve RACI Matrisi (İÜC.BİDB.SRÇ.001)"), "SRÇ.001 rol, sorumluluk, yetki, RACI ve yetkinlik kayıtları"],
            [link("İÜC.BİDB.LST.011 - Repository Yapısı"), "Dokümantasyon repository yapısı"],
            [link("İÜC.BİDB.LST.012 - Süreç Yaygınlaştırma ve Bilgilendirme Kaydı"), "Süreç yaygınlaştırma ve bilgilendirme kayıtları"],
            [link("İÜC.BİDB.KLV.001 - Doküman Yazım Kuralları Talimatı"), "Doküman yazım kuralları"],
            [link("İÜC.BİDB.KLV.002 - Süreç Uyarlama Kılavuzu"), "Süreç uyarlama yaklaşımı"],
            [link("İÜC.BİDB.KLV.003 - Süreç Tasarımı Kontrol Kılavuzu"), "Süreç tasarım kontrol yaklaşımı"],
            [link("İÜC.BİDB.KLV.004 - Dokümantasyon Deposu Oluşturma Kılavuzu"), "Dokümantasyon deposu oluşturma yaklaşımı"],
        ],
    )


def content_terimler() -> str:
    return table(
        ["Terim / Kısaltma", "Açıklama"],
        [
            ["Doküman", "Kurumsal süreçlerin, yazılım projelerinin veya destek faaliyetlerinin uygulanması için oluşturulan kontrollü yazılı bilgi"],
            ["Kayıt", "Bir faaliyetin gerçekleştiğini, bir kararın alındığını veya bir kontrolün yapıldığını gösteren kanıt niteliğindeki bilgi"],
            ["Repository", "Dokümanların yayımlandığı, erişime açıldığı ve saklandığı merkezi alan"],
            ["Şablon", "Belirli doküman türlerinin standart yapıda üretilmesi için kullanılan doküman kalıbı"],
            ["Gözden Geçirme", "Dokümanın belirlenen kalite kriterlerine, şablonuna ve kullanım amacına uygunluğunun kontrol edilmesi"],
            ["Onay", "Dokümanın yürürlüğe alınmadan önce yetkili rol veya kişi tarafından kabul edilmesi"],
            ["Yayın", "Onaylanan dokümanın ilgili hedef kitle tarafından erişilebilir hale getirilmesi"],
            ["Bakım", "Dokümanın güncelliğinin, geçerliliğinin, erişilebilirliğinin ve izlenebilirliğinin sürdürülmesi"],
            ["SUP.7", "ISO/IEC 15504-5 içinde tanımlanan Documentation süreci"],
            ["SRÇ", "Süreç dokümanı kod ön eki"],
            ["LST", "Liste / kayıt dokümanı kod ön eki"],
            ["FRM", "Form dokümanı kod ön eki"],
            ["PRS", "Prosedür dokümanı kod ön eki"],
            ["KLV", "Kılavuz / talimat dokümanı kod ön eki"],
        ],
    )


def content_ozet() -> str:
    return table(
        ["Alan", "Açıklama"],
        [
            ["Süreç Başlatıcısı", "Yeni doküman ihtiyacı, doküman değişiklik ihtiyacı, proje yaşam döngüsü aşaması, süreç kurulumu, denetim/gözden geçirme bulgusu veya periyodik bakım ihtiyacı"],
            ["Süreç Başlangıcı", "Doküman ihtiyacının, doküman değişiklik ihtiyacının veya gözden geçirme ihtiyacının belirlenmesi"],
            ["Süreç Bitişi", "Dokümanın onaylanması, yayımlanması, ilgili kayıtların güncellenmesi ve gerekli taraflara duyurulması"],
            ["Ana Faaliyetler", "Dokümantasyon stratejisini belirleme, standartları uygulama, doküman gereksinimlerini belirleme, doküman üretme, gözden geçirme, onaylama, yayımlama, dağıtma ve bakım"],
            ["İlgili Süreçler", f'{link("İÜC.BİDB.SRÇ.002 - Kalite Güvencesi Süreci")}, {link("İÜC.BİDB.SRÇ.003 - Doğrulama Süreci")}, {link("İÜC.BİDB.SRÇ.004 - Süreç Kurulumu Süreci")}, {link("İÜC.BİDB.SRÇ.016 - Yapılandırma Yönetimi Süreci")}, {link("İÜC.BİDB.SRÇ.018 - Değişiklik Talebi Yönetimi Süreci")}'],
        ],
    )


def content_roller() -> str:
    return "".join(
        [
            p("Bu süreç kapsamında rol, sorumluluk, yetki, RACI ve yetkinlik bilgileri süreç dokümanı içinde tekrar edilmez. Güncel kayıt ilgili süreç için oluşturulan LST.010 dokümanında yönetilir."),
            table(
                ["Referans Kayıt", "Kullanım"],
                [
                    [link("İÜC.BİDB.LST.010 - Süreç Rol Yetki ve RACI Matrisi (İÜC.BİDB.SRÇ.001)"), "Süreç rollerinin, sorumluluklarının, yetkilerinin, RACI bilgilerinin ve yetkinlik gereksinimlerinin güncel kaydıdır."],
                ],
            ),
        ]
    )


def content_girdiler() -> str:
    return table(
        ["Girdi", "Kaynak", "Kullanım Amacı"],
        [
            ["Yeni doküman ihtiyacı", "Süreç sahibi, proje ekibi, proje yaşam döngüsü aşaması, yönetim veya denetim çalışması", "Üretilecek dokümanın belirlenmesi"],
            ["Doküman değişiklik ihtiyacı", "Kullanıcılar, süreç sahipleri, proje ekibi, kalite güvence veya gözden geçirme faaliyeti", "Mevcut dokümanın güncellenmesi"],
            ["Yaşam döngüsü doküman ihtiyacı", link("İÜC.BİDB.LST.005 - Yaşam Döngüsü Doküman İhtiyaç Matrisi"), "Proje yaşam döngüsünde hangi aşamada hangi dokümanın üretileceğinin belirlenmesi"],
            ["Şablonlar", "02 - Şablonlar", "Dokümanların standart biçimde hazırlanması"],
            ["Doküman yazım ve repository kuralları", f'{link("İÜC.BİDB.KLV.001 - Doküman Yazım Kuralları Talimatı")}, {link("İÜC.BİDB.KLV.004 - Dokümantasyon Deposu Oluşturma Kılavuzu")}', "Dokümanın biçim, içerik, saklama ve yayın kurallarına uygun hazırlanması"],
            ["Gözden geçirme görüşleri", "Gözden geçiren rol / kalite danışmanı", "Dokümanın uygunluğunun değerlendirilmesi"],
            ["Onay kararı", "Yetkili onaylayan rol", "Dokümanın yürürlüğe alınması"],
            ["Repository bilgisi", link("İÜC.BİDB.LST.011 - Repository Yapısı"), "Dokümanın yayımlanacağı ve erişilebilir tutulacağı alanın belirlenmesi"],
        ],
    )


def content_ciktilar() -> str:
    return table(
        ["Çıktı / Kayıt / Doküman", "Açıklama", "Saklama Yeri"],
        [
            [link("İÜC.BİDB.PRS.001 - Yazılım Projeleri Dokümantasyon Prosedürü"), "Yazılım projeleri için dokümantasyon stratejisini ve uygulama kurallarını tanımlar.", "07 - Prosedürler"],
            [link("İÜC.BİDB.LST.001 - Aktif Dokümanlar Listesi"), "Aktif doküman envanterini, durumunu ve erişim bilgisini gösterir.", "SRÇ.001 süreç klasörü"],
            [link("İÜC.BİDB.LST.002 - Doküman Değişiklik Kaydı"), "Doküman değişikliklerini ve sürüm geçişlerini izler.", "03 - Kayıtlar ve Listeler"],
            [link("İÜC.BİDB.LST.003 - Doküman Gözden Geçirme Kaydı"), "Doküman gözden geçirme kayıtlarını izler.", "03 - Kayıtlar ve Listeler"],
            [link("İÜC.BİDB.LST.008 - İş Ürünleri ve Kalite Kriterleri Listesi (İÜC.BİDB.SRÇ.001)"), "SRÇ.001 iş ürünlerini ve kalite kriterlerini tanımlar.", "SRÇ.001 süreç klasörü"],
            [link("İÜC.BİDB.LST.009 - Süreç Performans Ölçüm Seti (İÜC.BİDB.SRÇ.001)"), "SRÇ.001 performans ölçümlerini ve izleme yaklaşımını tanımlar.", "SRÇ.001 süreç klasörü"],
            [link("İÜC.BİDB.LST.010 - Süreç Rol Yetki ve RACI Matrisi (İÜC.BİDB.SRÇ.001)"), "SRÇ.001 rol, sorumluluk, yetki ve yetkinlik kayıtlarını yönetir.", "SRÇ.001 süreç klasörü"],
            [link("İÜC.BİDB.FRM.001 - Süreç Gözden Geçirme Formu (İÜC.BİDB.SRÇ.001)"), "SRÇ.001 BP/GP karşılamalarının gözden geçirilmesi için kullanılır.", "SRÇ.001 süreç klasörü"],
        ],
    )


def content_faaliyetler() -> str:
    return table(
        ["Adım", "Faaliyet", "Açıklama", "İlgili SUP.7 BP"],
        [
            ["1", "Dokümantasyon ihtiyacını ve stratejisini belirleme", "Ürün, hizmet, süreç veya proje yaşam döngüsünde hangi dokümantasyonun gerekli olduğu belirlenir.", "SUP.7.BP1"],
            ["2", "Doküman standartlarını ve şablonları uygulama", "Kodlama, biçim, üst bilgi, sürüm, onay ve kayıt kuralları uygulanır.", "SUP.7.BP2"],
            ["3", "Doküman gereksinimlerini belirleme", "Dokümanın amacı, kapsamı, içeriği, sahibi, gözden geçiren/onaylayan rolleri ve dağıtım ihtiyacı belirlenir.", "SUP.7.BP3"],
            ["4", "Üretilecek dokümanları belirleme", "Yaşam döngüsü ve süreç ihtiyacına göre üretilecek dokümanlar LST.001/LST.005 üzerinden izlenir.", "SUP.7.BP4"],
            ["5", "Dokümanı hazırlama", "Doküman ilgili şablon, yazım kuralları ve süreç gereksinimlerine uygun olarak hazırlanır.", "SUP.7.BP5"],
            ["6", "Dokümanı gözden geçirme ve onaylama", "Doküman yayımlanmadan önce gözden geçirilir, gerekli düzeltmeler yapılır ve yetkili rol tarafından onaylanır.", "SUP.7.BP6"],
            ["7", "Dokümanı yayımlama ve dağıtma", "Onaylı doküman repository üzerinde erişilebilir hale getirilir ve ilgili taraflara duyurulur.", "SUP.7.BP7"],
            ["8", "Dokümanı sürdürme", "Dokümanın güncelliği, erişilebilirliği, değişiklikleri, gözden geçirme kayıtları ve arşivleme ihtiyacı yönetilir.", "SUP.7.BP8"],
        ],
    )


def content_is_urunleri() -> str:
    return table(
        ["Referans Kayıt", "Kullanım"],
        [
            [link("İÜC.BİDB.LST.008 - İş Ürünleri ve Kalite Kriterleri Listesi (İÜC.BİDB.SRÇ.001)"), "SRÇ.001 kapsamında üretilen veya kontrol edilen iş ürünleri ile kalite kriterlerinin güncel kaydıdır."],
            [link("İÜC.BİDB.LST.001 - Aktif Dokümanlar Listesi"), "Aktif dokümanların durum, sürüm, sahiplik ve erişim bilgilerini izlemek için kullanılır."],
            [link("İÜC.BİDB.LST.002 - Doküman Değişiklik Kaydı"), "Doküman değişikliklerinin ve sürüm geçişlerinin kayıt altına alınması için kullanılır."],
            [link("İÜC.BİDB.LST.003 - Doküman Gözden Geçirme Kaydı"), "Doküman gözden geçirme sonuçlarının kayıt altına alınması için kullanılır."],
        ],
    )


def content_performans() -> str:
    return "".join(
        [
            p("Sürecin performansı, SRÇ.001 için tanımlanan ölçüm seti üzerinden izlenir. Ölçüm tanımları, veri kaynağı, ölçüm sıklığı, hedef değer ve değerlendirme yöntemi ilgili kayıt üzerinde yönetilir."),
            table(
                ["Referans Kayıt", "Kullanım"],
                [[link("İÜC.BİDB.LST.009 - Süreç Performans Ölçüm Seti (İÜC.BİDB.SRÇ.001)"), "SRÇ.001 performans hedefleri, ölçüm tanımları ve izleme kayıtları"]],
            ),
        ]
    )


def content_etkilesimler() -> str:
    return table(
        ["İlişkili Süreç", "Etkileşim"],
        [
            [link("İÜC.BİDB.SRÇ.002 - Kalite Güvencesi Süreci"), "Doküman kalite kriterlerinin, gözden geçirme sonuçlarının ve uygunsuzlukların yönetilmesi"],
            [link("İÜC.BİDB.SRÇ.003 - Doğrulama Süreci"), "Dokümanların yayımlanmadan önce gözden geçirilmesi ve doğrulanması"],
            [link("İÜC.BİDB.SRÇ.004 - Süreç Kurulumu Süreci"), "Süreç dokümanlarının kurulması, şablonların kullanılması ve süreç mimarisine uyumun sağlanması"],
            [link("İÜC.BİDB.SRÇ.016 - Yapılandırma Yönetimi Süreci"), "Sürüm, baseline, kontrollü doküman ve repository yönetimi"],
            [link("İÜC.BİDB.SRÇ.018 - Değişiklik Talebi Yönetimi Süreci"), "Doküman değişiklik taleplerinin alınması ve değerlendirilmesi"],
        ],
    )


def content_gozden_gecirme() -> str:
    return table(
        ["Faaliyet", "Kayıt / Kanıt", "Sıklık / Tetikleyici"],
        [
            ["Doküman gözden geçirme", link("İÜC.BİDB.LST.003 - Doküman Gözden Geçirme Kaydı"), "Yılda bir veya ihtiyaç halinde"],
            ["Süreç gözden geçirme", link("İÜC.BİDB.FRM.001 - Süreç Gözden Geçirme Formu (İÜC.BİDB.SRÇ.001)"), "Süreç değerlendirme / iç denetim / iyileştirme ihtiyacında"],
            ["Doküman değişikliği", link("İÜC.BİDB.LST.002 - Doküman Değişiklik Kaydı"), "Değişiklik ihtiyacı oluştuğunda"],
            ["Yaygınlaştırma", link("İÜC.BİDB.LST.012 - Süreç Yaygınlaştırma ve Bilgilendirme Kaydı"), "Yeni yayın, değişiklik veya süreç duyurusu sonrasında"],
        ],
    )


def fallback_section(section_title: str) -> str:
    return "".join(
        [
            p(f"Bu bölüm, güncel süreç tanımı şablonundaki '{section_title}' bölüm yapısı korunarak SRÇ.001 kapsamında değerlendirilmiştir."),
            table(
                ["Referans", "Açıklama"],
                [[link("İÜC.BİDB.PRS.001 - Yazılım Projeleri Dokümantasyon Prosedürü"), "SRÇ.001 uygulama yaklaşımı ve dokümantasyon yönetimi kuralları"]],
            ),
        ]
    )


def content_for_section(section_title: str) -> str:
    normalized = re.sub(r"^\s*\d+\s*[\.-]\s*", "", section_title).strip().lower()
    if "amaç" in normalized:
        return content_amac()
    if "kapsam" in normalized:
        return content_kapsam()
    if "referans" in normalized:
        return content_referanslar()
    if "terim" in normalized or "kısalt" in normalized:
        return content_terimler()
    if "süreç özeti" in normalized or normalized == "özet":
        return content_ozet()
    if "rol" in normalized or "sorumluluk" in normalized:
        return content_roller()
    if "girdi" in normalized:
        return content_girdiler()
    if "çıktı" in normalized:
        return content_ciktilar()
    if "faaliyet" in normalized or "akış" in normalized:
        return content_faaliyetler()
    if "iş ürün" in normalized or "kayıt" in normalized or "doküman set" in normalized:
        return content_is_urunleri()
    if "performans" in normalized or "ölç" in normalized or "izleme" in normalized:
        return content_performans()
    if "etkileşim" in normalized or "arayüz" in normalized or "ilişkili süreç" in normalized:
        return content_etkilesimler()
    if "gözden" in normalized or "güncelle" in normalized or "bakım" in normalized or "sürdür" in normalized:
        return content_gozden_gecirme()
    return fallback_section(section_title)


def build_src001_body(sections: list[str]) -> str:
    body = [meta_table()]
    for section in sections:
        if re.match(r"^\s*0\s*[\.-]", section):
            continue
        body.append(f"<h2>{e(section)}</h2>")
        body.append(content_for_section(section))
    return "\n".join(body) + "\n"


def build_view_html(title: str, storage_body: str) -> str:
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


def update_page_yaml() -> None:
    page_yaml_path = SRC001_DIR / "page.yaml"
    metadata = read_yaml(page_yaml_path)
    metadata.update(
        {
            "title": SRC001_TITLE,
            "document_code": SRC001_CODE,
            "document_type": "Süreç",
            "process_reference": "ISO/IEC 15504-5 SUP.7 - Documentation",
            "process_owner": "Levent BAYEZİT - Proje Yöneticisi",
            "status": "active",
            "version_label": "v1.0",
            "storage_file": "body.storage.xhtml",
            "view_file": "body.view.html",
        }
    )
    write_yaml(page_yaml_path, metadata)


def write_report(sections: list[str]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# SRÇ.001 Süreç Tanımı Yeniden Düzenleme Raporu",
        "",
        f"Zaman: {datetime.now(timezone.utc).isoformat()}",
        "Kapsam: Yalnızca İÜC.BİDB.SRÇ.001 - Dokümantasyon Süreci",
        "LST.007 veya diğer ilişkili dokümanlar bu çalışmada değiştirilmemiştir.",
        "Şablondaki 0 numaralı bölüm süreç dokümanına alınmamıştır.",
        "",
        "## Kullanılan Şablon Bölümleri",
    ]
    lines.extend(f"- {section}" for section in sections)
    lines.append("")
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    sections = extract_template_sections()
    storage_body = build_src001_body(sections)
    (SRC001_DIR / "body.storage.xhtml").write_text(storage_body, encoding="utf-8")
    (SRC001_DIR / "body.view.html").write_text(build_view_html(SRC001_TITLE, storage_body), encoding="utf-8")
    update_page_yaml()
    write_report(sections)
    print("[DONE] SRÇ.001 güncel süreç tanımı şablonuna göre yeniden düzenlendi.")
    print("[INFO] 0 numaralı şablon bölümü dahil edilmedi.")
    print("[INFO] LST.007 ve diğer ilişkili dokümanlar değiştirilmedi.")
    print(f"[REPORT] {REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
