#!/usr/bin/env python3
"""Rework only İÜC.BİDB.SRÇ.001 according to the current process definition template.

Strict scope:
- Updates only İÜC.BİDB.SRÇ.001 - Dokümantasyon Süreci.
- Does not move, rename or edit LST.007 or any other related document.
- Reads the current İÜC.BİDB.SRÇ.XXX.Ş template and preserves its numbered h2 section order exactly.
- Excludes every template-only section whose heading starts with 0.
- Writes no unnumbered process metadata block before section 1; section 1 is the first body section.

After running this script:
  python scripts/build_local_viewer.py
"""
from __future__ import annotations

import html
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

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


def normalize_heading(value: str) -> str:
    value = strip_tags(value).lower()
    value = re.sub(r"^\s*\d+\s*[\.-]\s*", "", value)
    value = value.replace("ı", "i").replace("ş", "s").replace("ç", "c")
    value = value.replace("ö", "o").replace("ü", "u").replace("ğ", "g")
    return re.sub(r"\s+", " ", value).strip()


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
        if title:
            pages[title] = {"page_id": str(page.get("page_id") or ""), "title": title}
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


def section_surec_bilgileri() -> str:
    return table(
        ["Alan", "Değer"],
        [
            ["Kurum", "İstanbul Üniversitesi - Cerrahpaşa Bilgi İşlem Daire Başkanlığı"],
            ["Süreç Kodu ve Adı", f"{SRC001_CODE} - Dokümantasyon Süreci"],
            ["Süreç Referansı", "ISO/IEC 15504-5 SUP.7 - Documentation"],
            ["Süreç Sahibi", "Levent BAYEZİT - Proje Yöneticisi"],
            ["Durum", "Aktif"],
            ["Sürüm", "v1.0"],
            ["Yürürlük Tarihi", "29-06-2026"],
            ["Son Gözden Geçirme Tarihi", "01-07-2026"],
        ],
    )


def section_amac() -> str:
    return "".join(
        [
            p("Bu sürecin amacı, İÜC BİDB bünyesinde yürütülen süreçler, yazılım projeleri ve destek faaliyetleri sırasında üretilen doküman ve kayıtların standart biçimde geliştirilmesini, yayımlanmasını, erişilebilir tutulmasını, güncel kalmasını ve yaşam döngüsü boyunca kontrollü şekilde sürdürülmesini sağlamaktır."),
            p("Süreç; dokümantasyon stratejisinin belirlenmesi, doküman standartlarının uygulanması, üretilecek dokümanların tanımlanması, dokümanların gözden geçirilmesi, onaylanması, yayımlanması, dağıtılması ve bakımının yapılması için kurumsal kuralları tanımlar."),
        ]
    )


def section_kapsam() -> str:
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


def section_referanslar() -> str:
    return table(
        ["Referans", "Açıklama"],
        [
            ["ISO/IEC 15504-5 SUP.7 - Documentation", "Dokümantasyon sürecinin SPICE süreç referansı"],
            ["ISO/IEC 15504-5 Process Assessment Model", "Süreç amaç, çıktı ve base practice beklentilerinin esas alındığı standart kaynak"],
            ["İÜC BİDB SPICE 2026 Level 3 Dokümantasyon Yapısı", "Kurumsal süreç dokümantasyonu ve Confluence doküman ağacı"],
        ],
    )


def section_terimler() -> str:
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


def section_surec_ozeti() -> str:
    return table(
        ["Alan", "Açıklama"],
        [
            ["Süreç Başlatıcısı", "Yeni doküman ihtiyacı, doküman değişiklik ihtiyacı, proje yaşam döngüsü aşaması, süreç gözden geçirme sonucu, denetim bulgusu veya iyileştirme ihtiyacı"],
            ["Süreç Başlangıcı", "Doküman ihtiyacının, değişiklik ihtiyacının veya bakım/gözden geçirme ihtiyacının belirlenmesi"],
            ["Süreç Bitişi", "Dokümanın onaylanması, yayımlanması, dağıtılması, güncellenmesi, pasife alınması veya arşivlenmesi"],
            ["Ana Faaliyetler", "Dokümantasyon stratejisi ve standartlarının uygulanması; doküman gereksinimlerinin belirlenmesi; doküman üretimi; gözden geçirme; onay; yayın; dağıtım; bakım ve değişiklik yönetimi"],
            ["İlgili Süreçler", ", ".join([
                link("İÜC.BİDB.SRÇ.002 - Kalite Güvencesi Süreci"),
                link("İÜC.BİDB.SRÇ.003 - Doğrulama Süreci"),
                link("İÜC.BİDB.SRÇ.004 - Süreç Kurulumu Süreci"),
                link("İÜC.BİDB.SRÇ.016 - Yapılandırma Yönetimi Süreci"),
                link("İÜC.BİDB.SRÇ.018 - Değişiklik Talebi Yönetimi Süreci"),
            ])],
        ],
    )


def section_roller() -> str:
    return table(
        ["Referans Kayıt", "Kullanım"],
        [
            [link("İÜC.BİDB.LST.010 - Süreç Rol Yetki ve RACI Matrisi (İÜC.BİDB.SRÇ.001)"), "SRÇ.001 kapsamındaki rol, sorumluluk, yetki, RACI ve yetkinlik gereksinimlerinin güncel kaydıdır. Roller ve sorumluluklar bu süreç dokümanında tekrar yazılmaz; ilgili kayıt üzerinden yönetilir."],
        ],
    )


def section_girdiler() -> str:
    return table(
        ["Girdi", "Kaynak", "Kullanım Amacı"],
        [
            ["Yeni doküman ihtiyacı", "Süreç sahibi, proje ekibi, kalite güvence, yönetim veya denetim sonucu", "Üretilecek dokümanın türünü, kapsamını ve önceliğini belirlemek"],
            ["Doküman değişiklik ihtiyacı", "Kullanıcılar, süreç sahipleri, proje ekibi, denetim veya gözden geçirme kaydı", "Mevcut dokümanın güncellenmesini veya pasife alınmasını başlatmak"],
            ["Yaşam döngüsü doküman ihtiyacı", link("İÜC.BİDB.LST.005 - Yaşam Döngüsü Doküman İhtiyaç Matrisi"), "Proje veya süreç aşamasında hangi dokümanların üretileceğini belirlemek"],
            ["Doküman türü ve kodlama yapısı", "Dokümantasyon süreci ve ilgili şablonlar", "Dokümanın sınıflandırılmasını ve izlenebilirliğini sağlamak"],
            ["Şablonlar", "02 - Şablonlar", "Dokümanın standart biçimde hazırlanmasını sağlamak"],
            ["Gözden geçirme görüşleri", link("İÜC.BİDB.LST.003 - Doküman Gözden Geçirme Kaydı"), "Dokümanın uygunluğunu değerlendirmek ve düzeltmeleri izlemek"],
            ["Onay kararı", "Yetkili onaylayan rol / süreç sahibi", "Dokümanın yürürlüğe alınmasını sağlamak"],
            ["Repository bilgisi", link("İÜC.BİDB.LST.011 - Repository Yapısı"), "Dokümanın yayımlanacağı ve saklanacağı alanı belirlemek"],
        ],
    )


def section_ciktilar() -> str:
    return table(
        ["Çıktı / Kayıt / Doküman", "Açıklama", "Saklama Yeri"],
        [
            [link("İÜC.BİDB.PRS.001 - Yazılım Projeleri Dokümantasyon Prosedürü"), "Yazılım projeleri için dokümantasyon stratejisi ve doküman yönetim kurallarını tanımlar.", "07 - Prosedürler"],
            [link("İÜC.BİDB.LST.001 - Aktif Dokümanlar Listesi"), "Aktif doküman envanterini ve erişim bilgisini gösterir.", "SRÇ.001 altı"],
            [link("İÜC.BİDB.LST.002 - Doküman Değişiklik Kaydı"), "Doküman değişikliklerinin tarih, kapsam, gerekçe ve sorumluluk bilgileriyle izlenmesini sağlar.", "03 - Kayıtlar ve Listeler"],
            [link("İÜC.BİDB.LST.003 - Doküman Gözden Geçirme Kaydı"), "Dokümanların gözden geçirilme ve uygunluk kayıtlarını içerir.", "03 - Kayıtlar ve Listeler"],
            [link("İÜC.BİDB.LST.005 - Yaşam Döngüsü Doküman İhtiyaç Matrisi"), "Yaşam döngüsü aşamalarına göre doküman üretim ihtiyaçlarını gösterir.", "03 - Kayıtlar ve Listeler"],
            [link("İÜC.BİDB.LST.008 - İş Ürünleri ve Kalite Kriterleri Listesi (İÜC.BİDB.SRÇ.001)"), "SRÇ.001 iş ürünleri ve kalite kriterlerini tanımlar.", "SRÇ.001 altı"],
            [link("İÜC.BİDB.LST.009 - Süreç Performans Ölçüm Seti (İÜC.BİDB.SRÇ.001)"), "SRÇ.001 performans ölçüm göstergelerini ve izleme yöntemini tanımlar.", "SRÇ.001 altı"],
            [link("İÜC.BİDB.LST.010 - Süreç Rol Yetki ve RACI Matrisi (İÜC.BİDB.SRÇ.001)"), "SRÇ.001 rol, sorumluluk, yetki, RACI ve yetkinlik kayıtlarını içerir.", "SRÇ.001 altı"],
            [link("İÜC.BİDB.FRM.001 - Süreç Gözden Geçirme Formu (İÜC.BİDB.SRÇ.001)"), "SRÇ.001 BP/GP gözden geçirme ve tamamlayıcı aksiyon kayıtlarını içerir.", "SRÇ.001 altı"],
        ],
    )


def section_faaliyetler() -> str:
    return table(
        ["Adım", "Faaliyet", "Standart İzlenebilirliği", "Temel Çıktı / Kayıt"],
        [
            ["1", "Dokümantasyon yönetim stratejisini ve kapsamını belirle", "SUP.7.BP1", link("İÜC.BİDB.PRS.001 - Yazılım Projeleri Dokümantasyon Prosedürü")],
            ["2", "Doküman türü, kodlama, şablon ve yazım kurallarını uygula", "SUP.7.BP2", link("İÜC.BİDB.KLV.001 - Doküman Yazım Kuralları Talimatı")],
            ["3", "Doküman gereksinimlerini belirle", "SUP.7.BP3", link("İÜC.BİDB.LST.008 - İş Ürünleri ve Kalite Kriterleri Listesi (İÜC.BİDB.SRÇ.001)")],
            ["4", "Yaşam döngüsünde üretilecek dokümanları belirle", "SUP.7.BP4", link("İÜC.BİDB.LST.005 - Yaşam Döngüsü Doküman İhtiyaç Matrisi")],
            ["5", "Dokümanı ilgili şablona göre hazırla", "SUP.7.BP5", "Taslak / güncellenmiş doküman"],
            ["6", "Dokümanı gözden geçir ve onaylat", "SUP.7.BP6", link("İÜC.BİDB.LST.003 - Doküman Gözden Geçirme Kaydı")],
            ["7", "Onaylanan dokümanı repository üzerinden yayımla ve erişilebilir hale getir", "SUP.7.BP7", link("İÜC.BİDB.LST.001 - Aktif Dokümanlar Listesi")],
            ["8", "Dokümanı değişiklik, gözden geçirme ve arşivleme kriterlerine göre sürdür", "SUP.7.BP8", link("İÜC.BİDB.LST.002 - Doküman Değişiklik Kaydı")],
        ],
    )


def section_izleme_olcme() -> str:
    return table(
        ["İzleme / Ölçüm Alanı", "Yöntem", "Kayıt"],
        [
            ["Dokümanların şablona uygunluğu", "Gözden geçirme ve kalite kriteri kontrolü", link("İÜC.BİDB.LST.003 - Doküman Gözden Geçirme Kaydı")],
            ["Aktif doküman envanterinin güncelliği", "Aktif doküman listesi üzerinden dönemsel kontrol", link("İÜC.BİDB.LST.001 - Aktif Dokümanlar Listesi")],
            ["Doküman değişikliklerinin izlenebilirliği", "Değişiklik kayıtlarının kontrol edilmesi", link("İÜC.BİDB.LST.002 - Doküman Değişiklik Kaydı")],
            ["Süreç performansı", "SRÇ.001 performans göstergelerinin izlenmesi", link("İÜC.BİDB.LST.009 - Süreç Performans Ölçüm Seti (İÜC.BİDB.SRÇ.001)")],
            ["Süreç yaygınlaştırma durumu", "Bilgilendirme/yaygınlaştırma kayıtlarının kontrolü", link("İÜC.BİDB.LST.012 - Süreç Yaygınlaştırma ve Bilgilendirme Kaydı")],
        ],
    )


def section_iliskili_dokumanlar() -> str:
    return table(
        ["Doküman / Kayıt", "İlişki"],
        [
            [link("İÜC.BİDB.PRS.001 - Yazılım Projeleri Dokümantasyon Prosedürü"), "Dokümantasyon yönetim prosedürü"],
            [link("İÜC.BİDB.LST.001 - Aktif Dokümanlar Listesi"), "Aktif doküman envanteri"],
            [link("İÜC.BİDB.LST.002 - Doküman Değişiklik Kaydı"), "Değişiklik izleme kaydı"],
            [link("İÜC.BİDB.LST.003 - Doküman Gözden Geçirme Kaydı"), "Gözden geçirme kaydı"],
            [link("İÜC.BİDB.LST.005 - Yaşam Döngüsü Doküman İhtiyaç Matrisi"), "Yaşam döngüsü doküman ihtiyacı"],
            [link("İÜC.BİDB.LST.007 - Süreç Mimari ve Etkileşim Matrisi"), "Süreç etkileşim kaydı"],
            [link("İÜC.BİDB.LST.008 - İş Ürünleri ve Kalite Kriterleri Listesi (İÜC.BİDB.SRÇ.001)"), "İş ürünü ve kalite kriterleri"],
            [link("İÜC.BİDB.LST.009 - Süreç Performans Ölçüm Seti (İÜC.BİDB.SRÇ.001)"), "Performans ölçüm seti"],
            [link("İÜC.BİDB.LST.010 - Süreç Rol Yetki ve RACI Matrisi (İÜC.BİDB.SRÇ.001)"), "Rol, yetki, RACI ve yetkinlik kaydı"],
            [link("İÜC.BİDB.LST.011 - Repository Yapısı"), "Dokümantasyon repository yapısı"],
            [link("İÜC.BİDB.LST.012 - Süreç Yaygınlaştırma ve Bilgilendirme Kaydı"), "Yaygınlaştırma kaydı"],
            [link("İÜC.BİDB.KLV.001 - Doküman Yazım Kuralları Talimatı"), "Doküman yazım kuralları"],
            [link("İÜC.BİDB.KLV.003 - Süreç Tasarımı Kontrol Kılavuzu"), "Süreç tasarım kontrol desteği"],
        ],
    )


def section_surumu_gecmisi() -> str:
    return table(
        ["Sürüm", "Tarih", "Açıklama", "Hazırlayan / Güncelleyen", "Onay"],
        [
            ["v1.0", "29-06-2026", "Dokümantasyon Süreci güncel süreç tanımı şablonuna göre düzenlendi.", "Soner DEDEOĞLU - Kalite Danışmanı", "Levent BAYEZİT - Dokümantasyon Süreç Sahibi"],
        ],
    )


def section_default_for_heading(heading: str) -> str:
    normalized = normalize_heading(heading)

    if "surec bilgileri" in normalized:
        return section_surec_bilgileri()
    if normalized == "amac" or normalized.endswith(" amac"):
        return section_amac()
    if "kapsam" in normalized:
        return section_kapsam()
    if "referans" in normalized:
        return section_referanslar()
    if "terim" in normalized or "kisalt" in normalized:
        return section_terimler()
    if "surec ozeti" in normalized or normalized == "ozet":
        return section_surec_ozeti()
    if "rol" in normalized or "sorumluluk" in normalized:
        return section_roller()
    if "girdi" in normalized:
        return section_girdiler()
    if "cikti" in normalized or "urun" in normalized and "is" in normalized:
        return section_ciktilar()
    if "faaliyet" in normalized or "akis" in normalized or "isleyis" in normalized or "uygulama" in normalized:
        return section_faaliyetler()
    if "izleme" in normalized or "olc" in normalized or "performans" in normalized or "kontrol" in normalized:
        return section_izleme_olcme()
    if "iliskili" in normalized or "dokuman" in normalized and "kayit" in normalized:
        return section_iliskili_dokumanlar()
    if "surum" in normalized or "degisiklik gecmisi" in normalized:
        return section_surumu_gecmisi()

    raise RuntimeError(
        "SRÇ.001 içerik eşlemesi yapılamayan şablon bölümü var: "
        f"{heading}. Scripti bu başlığa göre güncelleyin."
    )


def build_storage_body(sections: list[str]) -> str:
    body_parts: list[str] = []
    for heading in sections:
        body_parts.append(f"<h2>{e(heading)}</h2>")
        body_parts.append(section_default_for_heading(heading))
    return "".join(body_parts) + "\n"


def build_view_html(storage_body: str) -> str:
    return f"""<!doctype html>
<html lang="tr">
<head>
  <meta charset="utf-8">
  <title>{e(SRC001_TITLE)}</title>
  <style>{CSS}</style>
</head>
<body>
<main class="confluence-page">
<h1>{e(SRC001_TITLE)}</h1>
{storage_body}
</main>
</body>
</html>
"""


def update_page_yaml() -> None:
    page_yaml = SRC001_DIR / "page.yaml"
    metadata = read_yaml(page_yaml)
    metadata.update(
        {
            "title": SRC001_TITLE,
            "document_code": SRC001_CODE,
            "document_type": "Süreç",
            "template": "İÜC.BİDB.SRÇ.XXX.Ş - Süreç Tanımı Şablonu",
            "status": "active",
            "version": "v1.0",
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "storage_file": "body.storage.xhtml",
            "view_file": "body.view.html",
        }
    )
    write_yaml(page_yaml, metadata)


def write_report(sections: list[str]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# SRÇ.001 Süreç Tanımı Yeniden Düzenleme Raporu",
        "",
        "Kapsam: Yalnızca `İÜC.BİDB.SRÇ.001 - Dokümantasyon Süreci` güncellendi.",
        "",
        "## Uygulanan Şablon Bölümleri",
    ]
    for section in sections:
        lines.append(f"- {section}")
    lines.extend(
        [
            "",
            "## Kontroller",
            "- 0 numaralı şablon bölümleri SRÇ.001 içeriğine alınmadı.",
            "- SRÇ.001 gövdesi doğrudan `1.` numaralı şablon bölümüyle başlatıldı.",
            "- LST.007 veya diğer ilişkili dokümanlarda taşıma/yeniden adlandırma/değişiklik yapılmadı.",
            "- Referanslar bölümünde süreç içinde üretilen kayıtlar yerine standart/kurumsal referanslar tutuldu; süreç çıktı ve kayıtları ilgili doküman/kayıt bölümlerinde verildi.",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    sections = extract_template_sections()
    storage_body = build_storage_body(sections)

    if re.search(r"<h2>\s*0\s*[\.-]", storage_body):
        raise RuntimeError("0 numaralı bölüm yanlışlıkla SRÇ.001 gövdesine dahil edildi.")
    if not storage_body.lstrip().startswith("<h2>1."):
        raise RuntimeError("SRÇ.001 gövdesi doğrudan 1. bölümle başlamıyor.")

    (SRC001_DIR / "body.storage.xhtml").write_text(storage_body, encoding="utf-8")
    (SRC001_DIR / "body.view.html").write_text(build_view_html(storage_body), encoding="utf-8")
    update_page_yaml()
    write_report(sections)

    print("[DONE] SRÇ.001 süreç tanımı güncel şablon yapısına göre yeniden düzenlendi.")
    print(f"[REPORT] {REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
