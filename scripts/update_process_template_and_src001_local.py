#!/usr/bin/env python3
"""Apply the approved local-only process-template and SRÇ.001 structure update.

This migration is intentionally idempotent and does not call Confluence. It updates
the exported Storage XHTML and the corresponding local-viewer HTML in place while
preserving the existing document content and version-history rows.
"""
from __future__ import annotations

import re
from html import unescape
from html.entities import codepoint2name
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "confluence/pages/000-root-iuc-bidb-spice-2026-level-3"
TEMPLATE_DIR = PAGES / "02-sablonlar/iuc-bidb-src-xxx-s-surec-tanimi-sablonu"
SRC001_DIR = PAGES / "01-surec-dokumanlari/iuc-bidb-src-001-dokumantasyon-sureci"
REPORT = ROOT / "reports/process_template_src001_local_update.md"
DATE = "14-07-2026"


def table(headers: list[str], rows: list[list[str]], view: bool) -> str:
    table_class = ' class="wrapped confluenceTable"' if view else ' class="wrapped"'
    cell_class = ' class="confluenceTh"' if view else ""
    data_class = ' class="confluenceTd"' if view else ""
    head = "".join(f"<th{cell_class}>{value}</th>" for value in headers)
    body = "".join(
        "<tr>" + "".join(f"<td{data_class}>{value}</td>" for value in row) + "</tr>"
        for row in rows
    )
    wrapper_start = '<div class="table-wrap">' if view else ""
    wrapper_end = "</div>" if view else ""
    return (
        f"{wrapper_start}<table{table_class}><thead><tr>{head}</tr></thead>"
        f"<tbody>{body}</tbody></table>{wrapper_end}"
    )


def heading_pattern(title: str) -> re.Pattern[str]:
    return re.compile(rf"<h2\b[^>]*>\s*{re.escape(title)}\s*</h2>", re.I)


def find_heading(body: str, level: int, title: str):
    pattern = re.compile(rf"<h{level}\b[^>]*>.*?</h{level}>", re.I | re.S)
    for match in pattern.finditer(body):
        text = unescape(re.sub(r"<[^>]+>", "", match.group(0)))
        if " ".join(text.split()) == title:
            return match
    return None


def insert_before_heading(body: str, title: str, fragment: str) -> str:
    match = find_heading(body, 2, title)
    if not match:
        raise RuntimeError(f"Başlık bulunamadı: {title}")
    return body[: match.start()] + fragment + body[match.start() :]


def insert_row_after_label(body: str, label: str, rows: str) -> str:
    encoded = "".join(
        f"&{codepoint2name[ord(char)]};" if ord(char) in codepoint2name else char
        for char in label
    )
    for variant in dict.fromkeys((label, encoded)):
        pattern = re.compile(
            rf"(<tr><td(?:\s+class=\"[^\"]+\")?>{re.escape(variant)}</td>.*?</tr>)",
            re.I | re.S,
        )
        body, count = pattern.subn(rf"\1{rows}", body, count=1)
        if count == 1:
            return body
    raise RuntimeError(f"Tablo satırı bulunamadı veya tekil değil: {label}")


def constrain_first_table_in_section(body: str, heading_title: str) -> str:
    heading = find_heading(body, 2, heading_title)
    if not heading:
        raise RuntimeError(f"Tablo düzeni için bölüm bulunamadı: {heading_title}")
    table_match = re.search(r"<table\b[^>]*>", body[heading.end() :], re.I)
    if not table_match:
        raise RuntimeError(f"Bölüm tablosu bulunamadı: {heading_title}")
    start = heading.end() + table_match.start()
    end = heading.end() + table_match.end()
    tag = body[start:end]
    style = "width:100%;table-layout:fixed;word-break:break-word;"
    if "table-layout:fixed" in tag:
        return body
    if re.search(r"\sstyle=\"", tag, re.I):
        tag = re.sub(r'(\sstyle=")', rf'\1{style}', tag, count=1, flags=re.I)
    else:
        tag = tag[:-1] + f' style="{style}">'
    return body[:start] + tag + body[end:]


def append_row_to_section(body: str, heading_tag: str, row: str) -> str:
    heading = find_heading(body, 2, heading_tag) or find_heading(body, 3, heading_tag)
    if not heading:
        raise RuntimeError(f"Sürüm bölümü bulunamadı: {heading_tag}")
    tbody_end = body.find("</tbody>", heading.end())
    if tbody_end < 0:
        raise RuntimeError(f"Sürüm tablosu bulunamadı: {heading_tag}")
    return body[:tbody_end] + row + body[tbody_end:]


def renumber_after_new_section(body: str) -> str:
    if find_heading(body, 2, "8. Araçlar ve Altyapı"):
        return body
    replacements = dict([
        ("14. Sürüm Geçmişi", "15. Sürüm Geçmişi"),
        ("13. Süreç Etkileşimleri", "14. Süreç Etkileşimleri"),
        ("12. Uygulama ve Uyarlama Kuralları", "13. Uygulama ve Uyarlama Kuralları"),
        ("11. Ölçüm ve İzleme", "12. Ölçüm ve İzleme"),
        ("10. Süreç Faaliyetleri", "11. Süreç Faaliyetleri"),
        ("9. Süreç Akışı", "10. Süreç Akışı"),
        ("8. Süreç İş Ürünleri", "9. Süreç İş Ürünleri"),
    ])

    def replace_h2(match: re.Match[str]) -> str:
        tag = match.group(0)
        text = " ".join(unescape(re.sub(r"<[^>]+>", "", tag)).split())
        if text not in replacements:
            return tag
        opening = re.match(r"<h2\b[^>]*>", tag, re.I)
        if not opening:
            return tag
        return f"{opening.group(0)}{replacements[text]}</h2>"

    body = re.sub(r"<h2\b[^>]*>.*?</h2>", replace_h2, body, flags=re.I | re.S)
    body = re.sub(r"(?<!\d)12\.(\d+|N)\.", r"13.\1.", body)
    return body


def normalize_src001_headings(body: str) -> str:
    measurement_number = "12" if find_heading(body, 2, "8. Araçlar ve Altyapı") else "11"
    measurement_title = f"{measurement_number}. Ölçüm ve İzleme"
    headings = {
        "2. Amaç": ("2. Amaç", "2. Ama&ccedil;"),
        "7. Roller ve Sorumluluklar": ("7. Roller ve Sorumluluklar",),
        measurement_title: (
            measurement_title,
            f"{measurement_number}. &Ouml;l&ccedil;&uuml;m ve İzleme",
        ),
    }
    for clean, variants in headings.items():
        if heading_pattern(clean).search(body):
            continue
        replaced = False
        for variant in variants:
            marker = (
                '<p class="auto-cursor-target"><span style="font-size: 20.0px;'
                f'letter-spacing: -0.008em;">{variant}</span></p></div>'
            )
            if marker in body:
                body = body.replace(marker, f"</div><h2>{clean}</h2>", 1)
                replaced = True
                break
        if not replaced:
            raise RuntimeError(f"SRÇ.001 başlığı normalleştirilemedi: {clean}")
    return body


def template_outcomes(view: bool) -> str:
    return (
        "<h3>2.1. Süreç Sonuçları</h3>"
        "<p><strong>Kullanım Notu:</strong> Sürecin uygulanması sonucunda elde edilmesi "
        "beklenen sonuçlar, esas alınan süreç referansındaki sıra ve anlam korunarak yazılır.</p>"
        + table(
            ["Sonuç ID", "Süreç Sonucu"],
            [
                ["S1", "<em>Standart veya iç süreç referansındaki beklenen sonuç</em>"],
                ["S2", "<em>Standart veya iç süreç referansındaki beklenen sonuç</em>"],
                ["S...", "<em>İhtiyaç duyulan sayıda satır eklenir</em>"],
            ],
            view,
        )
    )


def src001_outcomes(view: bool) -> str:
    rows = [
        ["S1", "Ürün veya hizmet yaşam döngüsü boyunca üretilecek dokümantasyonu tanımlayan bir strateji geliştirilir."],
        ["S2", "Dokümantasyonun geliştirilmesinde uygulanacak standartlar belirlenir."],
        ["S3", "Süreç veya proje tarafından üretilecek dokümantasyon belirlenir."],
        ["S4", "Tüm dokümantasyonun içeriği ve amacı tanımlanır, gözden geçirilir ve onaylanır."],
        ["S5", "Dokümantasyon belirlenen standartlara uygun olarak geliştirilir ve erişilebilir kılınır."],
        ["S6", "Dokümantasyon tanımlanmış kriterlere uygun olarak sürdürülür."],
    ]
    return "<h3>2.1. Süreç Sonuçları</h3>" + table(
        ["Sonuç ID", "Süreç Sonucu"], rows, view
    )


def template_tools(view: bool) -> str:
    rows = [
        ["<em>Araç / Altyapı / Çalışma Ortamı</em>", "<em>Kullanılan sistem, platform veya ortam</em>", "<em>Süreçteki kullanım amacı</em>", "<em>Yetki, erişim ve asgari kullanım koşulu</em>", "<em>Sorumlu rol veya birim</em>"],
        ["<em>...</em>", "<em>...</em>", "<em>...</em>", "<em>...</em>", "<em>...</em>"],
    ]
    return (
        "<h2>8. Araçlar ve Altyapı</h2>"
        "<p>Bu bölümde sürecin uygulanması için gerekli araçlar, altyapı bileşenleri ve "
        "çalışma ortamları ile bunların kullanım ve erişim koşulları tanımlanır.</p>"
        + table(
            ["Tür", "Araç / Altyapı Bileşeni", "Kullanım Amacı", "Erişim ve Kullanım Koşulu", "Sorumlu Rol / Birim"],
            rows,
            view,
        )
    )


def src001_tools(view: bool) -> str:
    rows = [
        ["Araç", "Confluence", "Kontrollü süreç, prosedür, kılavuz ve şablonların yayımlanması ve ortak erişimi", "Kurumsal kullanıcı hesabı ve atanmış okuma/yazma yetkisi; uzaktan erişimde VPN", "Doküman Sorumlusu / Confluence Yöneticisi"],
        ["Altyapı", "Google Drive", "Kontrollü kayıtların, eklerin, onaylı kopyaların ve arşivlerin saklanması", "Kurumsal hesap ve rol bazlı klasör yetkisi", "Repository Sorumlusu / Doküman Sorumlusu"],
        ["Araç", "Jira", "Dokümanla ilişkili görev, değişiklik, gözden geçirme ve aksiyonların izlenmesi", "Proje veya süreç bazlı yetkilendirme", "Proje Yöneticisi / Jira Yöneticisi"],
        ["Araç", "Bitbucket", "Kodla ilişkili teknik kayıtların ve sürüm kontrollü dokümantasyon kaynaklarının yönetilmesi", "Proje repository yetkisi ve tanımlı branch/değişiklik kuralları", "Yazılım Geliştirme Ekibi / Bitbucket Yöneticisi"],
        ["Altyapı", "İÜC VPN ve kurumsal kimlik/yetkilendirme altyapısı", "Kurum dışından Confluence ve diğer yetkili sistemlere güvenli erişim", "Geçerli kurumsal hesap, VPN yetkisi ve bilgi güvenliği kuralları", "İÜC BİDB Altyapı ve Erişim Yönetimi"],
    ]
    return (
        "<h2>8. Araçlar ve Altyapı</h2>"
        "<p>Dokümantasyon Sürecinin uygulanması için aşağıdaki araçlar ve altyapı "
        "bileşenleri kullanılır. Yetkilendirme ve erişim kontrolleri ilgili sistemin "
        "kurumsal kurallarına göre uygulanır.</p>"
        + table(
            ["Tür", "Araç / Altyapı Bileşeni", "Kullanım Amacı", "Erişim ve Kullanım Koşulu", "Sorumlu Rol / Birim"],
            rows,
            view,
        )
    )


def add_process_info_rows(body: str, view: bool, target: str) -> str:
    if "Hedef Kitle" in body:
        return body
    td = ' class="confluenceTd"' if view else ""
    if target == "template":
        audience = "<em>Süreci uygulayan, yöneten, gözden geçiren ve süreç çıktılarından yararlanan roller</em>"
        publication = "<em>Onaylı kurumsal yayın ve erişim ortamları</em>"
    else:
        audience = "Süreç sahipleri, doküman hazırlayan/gözden geçiren/onaylayan roller, proje ekipleri, kalite güvence ve ilgili BİDB personeli"
        publication = "Confluence ve Google Drive; uzaktan erişimde İÜC VPN ve kurumsal yetkilendirme"
    rows = (
        f"<tr><td{td}>Hedef Kitle</td><td{td}>{audience}</td></tr>"
        f"<tr><td{td}>Yayın ve Erişim Ortamı</td><td{td}>{publication}</td></tr>"
    )
    return insert_row_after_label(body, "Süreç Sahibi", rows)


def update_src001_metadata(body: str) -> str:
    td = r'(?:\s+class="[^"]+")?'

    def replace_value(current: str, label: str, value: str) -> str:
        encoded = "".join(
            f"&{codepoint2name[ord(char)]};" if ord(char) in codepoint2name else char
            for char in label
        )
        for variant in dict.fromkeys((label, encoded)):
            pattern = re.compile(
                rf"(<tr><td{td}>{re.escape(variant)}</td><td{td}>).*?(</td></tr>)",
                re.I | re.S,
            )
            updated, count = pattern.subn(rf"\g<1>{value}\2", current, count=1)
            if count == 1:
                return updated
        raise RuntimeError(f"SRÇ.001 üst bilgi alanı güncellenemedi: {label}")

    body = replace_value(body, "Sürüm", "v1.1")
    body = replace_value(body, "Son Gözden Geçirme Tarihi", DATE)
    return body


def transform_template(body: str, view: bool) -> str:
    body = add_process_info_rows(body, view, "template")
    if "2.1. Süreç Sonuçları" not in body:
        body = insert_before_heading(body, "3. Kapsam", template_outcomes(view))
    body = renumber_after_new_section(body)
    if "8. Araçlar ve Altyapı" not in body:
        body = insert_before_heading(body, "9. Süreç İş Ürünleri", template_tools(view))
    body = constrain_first_table_in_section(body, "8. Araçlar ve Altyapı")
    if "Araçlar ve Altyapı bölümü eklendi" not in body:
        td = ' class="confluenceTd"' if view else ""
        row = (
            f"<tr><td{td}>v1.1</td><td{td}>{DATE}</td>"
            f"<td{td}>Hedef Kitle, Yayın ve Erişim Ortamı, Süreç Sonuçları ile Araçlar ve Altyapı bölümü eklendi.</td>"
            f"<td{td}>Soner DEDEOĞLU - Kalite Danışmanı</td><td{td}>-</td></tr>"
        )
        body = append_row_to_section(body, "0.4. Sürüm Geçmişi", row)
    return body


def transform_src001(body: str, view: bool) -> str:
    body = normalize_src001_headings(body)
    body = add_process_info_rows(body, view, "src001")
    body = update_src001_metadata(body)
    if "2.1. Süreç Sonuçları" not in body:
        body = insert_before_heading(body, "3. Kapsam", src001_outcomes(view))
    body = renumber_after_new_section(body)
    if "8. Araçlar ve Altyapı" not in body:
        body = insert_before_heading(body, "9. Süreç İş Ürünleri", src001_tools(view))
    body = constrain_first_table_in_section(body, "8. Araçlar ve Altyapı")
    if "Araçlar ve Altyapı bölümü eklenerek" not in body:
        td = ' class="confluenceTd"' if view else ""
        row = (
            f"<tr><td{td}>v1.1</td><td{td}>{DATE}</td>"
            f"<td{td}>Süreç tanımı güncel şablonla hizalandı; süreç sonuçları, hedef kitle, yayın ve erişim ortamı ile Araçlar ve Altyapı bölümü eklenerek bölüm numaraları güncellendi.</td>"
            f"<td{td}>Soner DEDEOĞLU - Kalite Danışmanı</td>"
            f"<td{td}>Levent BAYEZİT - Süreç Sahibi</td>"
            f"<td{td}>Onay bekliyor</td></tr>"
        )
        body = append_row_to_section(body, "15. Sürüm Geçmişi", row)
    return body


def update_file(path: Path, target: str) -> None:
    original = path.read_text(encoding="utf-8")
    view = path.name == "body.view.html"
    updated = transform_template(original, view) if target == "template" else transform_src001(original, view)
    if updated != original:
        path.write_text(updated, encoding="utf-8")
        print(f"[UPDATED] {path.relative_to(ROOT)}")
    else:
        print(f"[UNCHANGED] {path.relative_to(ROOT)}")


def validate() -> None:
    for folder, target in ((TEMPLATE_DIR, "Şablon"), (SRC001_DIR, "SRÇ.001")):
        storage = (folder / "body.storage.xhtml").read_text(encoding="utf-8")
        headings = re.findall(r"<h2[^>]*>(.*?)</h2>", storage, re.I | re.S)
        clean = [unescape(re.sub(r"<[^>]+>", "", item)).strip() for item in headings]
        expected = [
            "1. Süreç Bilgileri", "2. Amaç", "3. Kapsam", "4. Referanslar",
            "5. Terimler ve Kısaltmalar", "6. Süreç Aktivitesi",
            "7. Roller ve Sorumluluklar", "8. Araçlar ve Altyapı",
            "9. Süreç İş Ürünleri", "10. Süreç Akışı", "11. Süreç Faaliyetleri",
            "12. Ölçüm ve İzleme", "13. Uygulama ve Uyarlama Kuralları",
            "14. Süreç Etkileşimleri", "15. Sürüm Geçmişi",
        ]
        actual = [item for item in clean if not item.startswith("0.")]
        if actual != expected:
            raise RuntimeError(f"{target} başlık sırası hatalı: {actual}")
        for required in ("Hedef Kitle", "Yayın ve Erişim Ortamı", "2.1. Süreç Sonuçları"):
            if required not in storage:
                raise RuntimeError(f"{target} zorunlu içerik eksik: {required}")
    src = (SRC001_DIR / "body.storage.xhtml").read_text(encoding="utf-8")
    for required in ("Confluence", "Google Drive", "Jira", "Bitbucket", "İÜC VPN"):
        if required not in src:
            raise RuntimeError(f"SRÇ.001 araç/altyapı kaydı eksik: {required}")


def write_report() -> None:
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(
        "\n".join([
            "# Süreç Şablonu ve SRÇ.001 Yerel Güncelleme Raporu", "",
            f"Tarih: {DATE}", "",
            "## Kapsam", "",
            "- Süreç Bilgileri tablosuna Hedef Kitle ile Yayın ve Erişim Ortamı eklendi.",
            "- Amaç bölümüne 2.1 Süreç Sonuçları eklendi.",
            "- 8. Araçlar ve Altyapı bölümü eklendi; sonraki bölümler 9-15 olarak numaralandırıldı.",
            "- SRÇ.001 içine SUP.7 süreç sonuçları ve Confluence, Google Drive, Jira, Bitbucket ve İÜC VPN kayıtları eklendi.",
            "- Mevcut sürüm geçmişi korundu; v1.1 satırı eklendi.",
            "- Confluence üzerinde herhangi bir değişiklik yapılmadı.", "",
        ]) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    for folder, target in ((TEMPLATE_DIR, "template"), (SRC001_DIR, "src001")):
        update_file(folder / "body.storage.xhtml", target)
        update_file(folder / "body.view.html", target)
    validate()
    write_report()
    print(f"[REPORT] {REPORT.relative_to(ROOT)}")
    print("[DONE] Yerel güncelleme tamamlandı; Confluence'a yazılmadı.")


if __name__ == "__main__":
    main()
