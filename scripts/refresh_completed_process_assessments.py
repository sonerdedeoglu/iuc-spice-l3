#!/usr/bin/env python3
"""Refresh all completed-process Assessment #1 pages and cumulative RPR.001.

This is a local-only maintenance script. It updates the existing Assessment #1
pages in place, uses only label-based results, and never calls Confluence.
"""
from __future__ import annotations

import html
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from create_src005_process_assessment_package import build_view


ROOT = Path(__file__).resolve().parents[1]
PAGE_ROOT = ROOT / "confluence/pages/000-root-iuc-bidb-spice-2026-level-3"
REVIEWS = PAGE_ROOT / "91-ic-denetimler/surec-gozden-gecirmeleri"
RPR_DIR = PAGE_ROOT / "09-raporlar/rpr-001-surec-performanslari-raporu"
REPORT = ROOT / "reports/completed_process_assessments_refresh_report.md"
CURRENT_STATUS = ROOT / "docs/CURRENT_STATUS.md"
LABELS = ("VAR", "DAĞINIK", "ZAYIF", "YOK", "KAPSAM DIŞI")
REPORT_DATE = "15-07-2026"


@dataclass(frozen=True)
class Update:
    status: str
    note: str
    evidence: str
    action: str
    reason: str


PROCESS = {
    "001": {
        "name": "SRÇ.001 - Dokümantasyon Süreci",
        "scope": "SUP.7 BP1-BP8; PA 2.1-PA 3.2",
        "summary": (
            "Doküman standartları, şablonlar, kontrollü yayın/bakım ve tekrar eden paket "
            "gözden geçirmeleri güçlüdür. Gerçek dönem performans verisi, hedef kitle "
            "bilgilendirmesi, yetkinlik/eğitim, kaynak tahsisi ve bağlama özgü uyarlama "
            "kanıtları geliştirilmelidir."
        ),
    },
    "004": {
        "name": "SRÇ.004 - Süreç Kurulumu Süreci",
        "scope": "PIM.1 BP1-BP6; PA 2.1-PA 3.2",
        "summary": (
            "Standart süreç mimarisi, süreç paketleri, uyarlama, rol ve ölçüm tanımları ile "
            "süreç kullanım verilerinin LST.006, FRM.001 ve RPR.001 üzerinde sürdürülmesi "
            "güçlüdür. Gerçek dönem performansı, hedef kitle bilgilendirmesi, yetkinlik ve "
            "kaynak tahsis kanıtları geliştirilmelidir."
        ),
    },
    "005": {
        "name": "SRÇ.005 - Süreç Değerlendirme Süreci",
        "scope": "PIM.2 BP1-BP8; PA 2.1-PA 3.2",
        "summary": (
            "Ortak değerlendirme yöntemi sekiz süreçte uygulanmış, sonuçlar Değerlendirme #1 "
            "kayıtları ve kümülatif RPR.001 üzerinde sürdürülmüştür. Bağımsız/formal doğrulama, "
            "yıllık takvim taahhütleri, eğitim ve gerçek dönem performans sonuçları tamamlanmalıdır."
        ),
    },
    "006": {
        "name": "SRÇ.006 - Süreç İyileştirme Süreci",
        "scope": "PIM.3 BP1-BP9; PA 2.1-PA 3.2",
        "summary": (
            "İyileştirme girdisi, ön analiz, öncelik, yetki, planlama, SRÇ.018 değişiklik "
            "gözden geçirmesiyle doğrulama ve yeniden kullanım kuralları tanımlıdır. Gerçek bir "
            "iyileştirmenin uygulanması ve sonucunun doğrulanması henüz oluşmadığından etiketler korunmuştur."
        ),
    },
    "021": {
        "name": "SRÇ.021 - Bilgi Yönetimi Süreci",
        "scope": "RIN.3 BP1-BP6; PA 2.1-PA 3.2",
        "summary": (
            "Kaynak sistem, bağlantı ağı, sahiplik, Bilgi Kataloğu yapısı ve bakım kuralları "
            "tanımlıdır. Katalog kapsamının diğer süreçlerle genişlemesi, ilk yıllık gözden "
            "geçirme, yaygınlaştırma ve gerçek performans kanıtları beklenmektedir."
        ),
    },
    "023": {
        "name": "SRÇ.023 - Organizasyonel Yönetim Süreci",
        "scope": "MAN.2 BP1-BP6; PA 2.1-PA 3.2",
        "summary": (
            "Yönetim altyapısı, rol ve yetki yaklaşımı, YGG yöntemi ve karar yönlendirme kuralları "
            "sonraki süreç paketlerinde uygulanmıştır. İlk gerçek YGG, aksiyon kapanışı ve yönetim "
            "uygulamalarının etkinlik değerlendirmesi henüz oluşmamıştır."
        ),
    },
    "024": {
        "name": "SRÇ.024 - Kalite Yönetimi Süreci",
        "scope": "MAN.4 BP1-BP8; PA 2.1-PA 3.2",
        "summary": (
            "Kalite hedefleri, yönetim döngüsü, uygunsuzluk yönlendirmesi ve proje müşteri "
            "memnuniyeti yöntemi tanımlıdır. Gerçek anket/RPR.002, yıllık hedef değerlendirmesi "
            "ve bağlı süreçlerin işletim kanıtları oluşmadığından etiketler korunmuştur."
        ),
    },
    "025": {
        "name": "SRÇ.025 - Ölçüm Süreci",
        "scope": "MAN.6 BP1-BP9; PA 2.1-PA 3.2",
        "summary": (
            "Ölçüm stratejisi, bilgi ihtiyacı, doğal kaynak, bağlam bilgisi, analiz ve bilgi ürünü "
            "yaklaşımı tanımlıdır. Ortak yöntemle gerçek dönem ölçümü, zamanında sunum, geri "
            "bildirim ve yıllık ölçüm gözden geçirmesi oluşmadığından etiketler korunmuştur."
        ),
    },
}


UPDATES: dict[str, dict[str, Update]] = {
    "001": {
        "SUP.7.BP6": Update(
            "VAR",
            "Tamamlanan süreç paketleri yerel viewer üzerinde gözden geçirilmiş, kullanıcı düzeltmeleri uygulanmış, yayın yetkilendirmesinden sonra kontrollü Confluence aktarımı yapılmış ve canlı doğrulama raporları oluşturulmuştur. Bu tekrar eden kontrol zinciri dağıtım öncesi gözden geçirme ve yetkilendirmeyi fiilen karşılamaktadır.",
            "SRÇ.001, SRÇ.004, SRÇ.005, SRÇ.006, SRÇ.021 ve SRÇ.023 paket doğrulama raporları; Confluence revizyon geçmişi; Git geçmişi",
            "-",
            "Birden çok süreç paketinde dağıtım öncesi gözden geçirme, düzeltme, yetkilendirme ve yayın sonrası doğrulama kanıtlandı.",
        ),
        "GP.2.2.4": Update(
            "VAR",
            "Süreç ve destek dokümanları aktif şablon, adlandırma, yerleşim, BP/GP izlenebilirliği ve görsel-kaynak tutarlılığı açısından tekrar eden biçimde gözden geçirilmiş; kullanıcı incelemesindeki düzeltmeler uygulanmış ve kontrollü yayınlardan sonra canlı görünüm doğrulanmıştır.",
            "Tamamlanan süreç paketlerinin yerel ve Confluence doğrulama raporları; Değerlendirme #1 kayıtları; Git geçmişi",
            "-",
            "Sekiz süreç paketinde ortak kontrol yaklaşımı uygulanmış, yayımlanan paketler için canlı doğrulama kayıtları oluşmuştur.",
        ),
        "GP.3.1.5": Update(
            "VAR",
            "Süreç özel LST.009 setleri ile az sayıda ölçüm yaklaşımı tanımlanmış; SRÇ.025 ve PRS.009 bilgi ihtiyacı, doğal veri kaynağı, analiz ve kullanım için ortak ölçüm yöntemini tamamlamıştır. Gerçek sonuç toplama GP.3.2.6 kapsamında ayrı izlenmektedir.",
            "LST.009 (SRÇ.001); SRÇ.025 - Ölçüm Süreci; PRS.009 - Ölçüm ve Analiz Prosedürü; RPR.001",
            "-",
            "SRÇ.025 ve PRS.009 ile standart süreçlerin etkinlik ve uygunluğunu izleyecek ortak yöntem kurulmuştur.",
        ),
    },
    "004": {
        "PIM.1.BP6": Update(
            "VAR",
            "Standart süreçlerin kullanımına ilişkin durum LST.006 üzerinde; süreç tanım ve destek paketleri ilgili SRÇ sayfalarında; değerlendirme sonuçları Değerlendirme #1 kayıtları ile kümülatif RPR.001 üzerinde sürdürülmektedir. Sekiz tamamlanmış süreç paketi bu veri yapısında izlenmektedir.",
            "LST.006 - Standart Süreç Envanteri; sekiz süreç paketi; sekiz Değerlendirme #1 kaydı; RPR.001 - Süreç Performansları Raporu",
            "-",
            "Standart süreçlerin kullanım/durum verisi artık tek bir taslak yerine sekiz süreç paketi ve kümülatif değerlendirme kayıtları üzerinden sürdürülmektedir.",
        ),
        "GP.2.1.2": Update(
            "DAĞINIK",
            "Süreç kurulumunun ilerlemesi LST.006, süreç paketleri, Değerlendirme #1 kayıtları ve RPR.001 ile sekiz tamamlanmış süreç üzerinden izlenmektedir. Ancak LST.009 için ilk gerçek dönem sonuçları ve plan-sapma kayıtları henüz oluşmamıştır.",
            "LST.006; tamamlanan süreç paketleri; Değerlendirme #1 kayıtları; RPR.001; LST.009 (SRÇ.004)",
            "İlk gerçek ölçüm döneminde takvim, gerçekleşme, sapma ve yeniden planlama bilgileri kaydedilmelidir.",
            "Kurulum ilerlemesi artık fiilen izleniyor; dönemsel performans ve sapma yönetimi henüz tamamlanmadı.",
        ),
        "GP.3.2.6": Update(
            "DAĞINIK",
            "Standart süreçlerin kurulma ve değerlendirme verileri LST.006, Değerlendirme #1 kayıtları ve RPR.001 içinde toplanıp süreç bazında karşılaştırılmaktadır. Süreç özel LST.009 ölçümlerinin gerçek dönem analizi henüz yapılmamıştır.",
            "LST.006; sekiz Değerlendirme #1 kaydı; RPR.001; süreç özel LST.009 kayıtları",
            "İlk gerçek dönemde LST.009 sonuçları toplanmalı, analiz edilmeli ve kurulum kararlarıyla ilişkilendirilmelidir.",
            "Kümülatif değerlendirme verisi mevcut ve analiz edilebilir; gerçek dönem LST.009 performansı henüz yoktur.",
        ),
    },
    "005": {
        "GP.3.2.6": Update(
            "DAĞINIK",
            "Sekiz tamamlanmış sürecin BP ve PA/GP etiket verileri Değerlendirme #1 kayıtlarında toplanmış, süreç bazında analiz edilmiş ve RPR.001 içinde kümülatif olarak karşılaştırılmıştır. Yıllık takvim performansı ve LST.009 ölçüm sonuçları henüz oluşmamıştır.",
            "Sekiz Değerlendirme #1 kaydı; RPR.001 - Süreç Performansları Raporu; PLN.001; LST.009 (SRÇ.005)",
            "İlk yıllık değerlendirme döneminde takvim, kayıt tamlığı ve bulgu yönlendirme ölçümleri hesaplanmalıdır.",
            "Değerlendirme verisi sekiz süreç için fiilen toplanmış ve kümülatif raporda analiz edilmiştir.",
        ),
    },
    "006": {},
    "021": {},
    "023": {
        "MAN.2.BP4": Update(
            "DAĞINIK",
            "Tanımlı yönetim uygulamaları; süreç sahipliği, gözden geçirme/onay rolleri, teknik-operasyonel yetki sınırı ve kalite/ölçüm sorumluluklarının SRÇ.024 ile SRÇ.025 paketlerinde uygulanmasıyla işletilmeye başlanmıştır. Yıllık YGG ve dönemsel yönetim uygulaması henüz gerçekleştirilmemiştir.",
            "SRÇ.023; PRS.006; LST.010 (SRÇ.023); SRÇ.024 ve SRÇ.025 süreç/rol paketleri",
            "İlk gerçek YGG Haziran-Temmuz döneminde FRM.002 ile yürütülmeli ve karar/aksiyonlar ilgili süreçlere yönlendirilmelidir.",
            "Yönetim uygulamalarının rol ve yetki kuralları sonraki iki süreç paketinde kullanılmıştır; gerçek YGG henüz yoktur.",
        ),
    },
    "024": {},
    "025": {},
}

BASELINE = {
    "001": (Counter({"VAR": 5, "DAĞINIK": 3}), Counter({"VAR": 9, "DAĞINIK": 9, "ZAYIF": 3})),
    "004": (Counter({"VAR": 4, "DAĞINIK": 1, "YOK": 1}), Counter({"VAR": 10, "DAĞINIK": 7, "ZAYIF": 1, "YOK": 3})),
    "005": (Counter({"VAR": 6, "DAĞINIK": 2}), Counter({"VAR": 11, "DAĞINIK": 7, "ZAYIF": 2, "YOK": 1})),
    "006": (Counter({"VAR": 4, "DAĞINIK": 2, "ZAYIF": 3}), Counter({"VAR": 11, "DAĞINIK": 7, "ZAYIF": 2, "YOK": 1})),
    "021": (Counter({"VAR": 2, "DAĞINIK": 3, "ZAYIF": 1}), Counter({"VAR": 12, "DAĞINIK": 6, "ZAYIF": 2, "YOK": 1})),
    "023": (Counter({"VAR": 2, "DAĞINIK": 2, "ZAYIF": 2}), Counter({"VAR": 12, "DAĞINIK": 6, "ZAYIF": 2, "YOK": 1})),
    "024": (Counter({"VAR": 3, "DAĞINIK": 2, "ZAYIF": 3}), Counter({"VAR": 12, "DAĞINIK": 6, "ZAYIF": 3})),
    "025": (Counter({"VAR": 3, "DAĞINIK": 4, "ZAYIF": 2}), Counter({"VAR": 12, "DAĞINIK": 6, "ZAYIF": 3})),
}

OLD_STATUS = {
    ("001", "SUP.7.BP6"): "DAĞINIK",
    ("001", "GP.2.2.4"): "DAĞINIK",
    ("001", "GP.3.1.5"): "DAĞINIK",
    ("004", "PIM.1.BP6"): "YOK",
    ("004", "GP.2.1.2"): "ZAYIF",
    ("004", "GP.3.2.6"): "YOK",
    ("005", "GP.3.2.6"): "ZAYIF",
    ("023", "MAN.2.BP4"): "ZAYIF",
}


def plain(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", value))).strip()


def section_bounds(document: str, heading: str) -> tuple[int, int]:
    heads = list(re.finditer(r"<h2[^>]*>(.*?)</h2>", document, flags=re.I | re.S))
    for index, match in enumerate(heads):
        if plain(match.group(1)) == heading:
            end = heads[index + 1].start() if index + 1 < len(heads) else len(document)
            return match.end(), end
    raise RuntimeError(f"Section not found: {heading}")


def cells(row: str) -> list[str]:
    return re.findall(r"<(?:th|td)[^>]*>(.*?)</(?:th|td)>", row, flags=re.I | re.S)


def replace_cell(row: str, index: int, value: str, *, raw: bool = False) -> str:
    matches = list(re.finditer(r"(<(?:th|td)[^>]*>)(.*?)(</(?:th|td)>)", row, flags=re.I | re.S))
    if index >= len(matches):
        raise RuntimeError(f"Cell index {index} missing in row: {plain(row)[:80]}")
    match = matches[index]
    content = value if raw else html.escape(value)
    return row[:match.start(2)] + content + row[match.end(2):]


def replace_keyed_row_cells(document: str, heading: str, key_index: int, key: str, values: dict[int, str]) -> str:
    start, end = section_bounds(document, heading)
    section = document[start:end]
    for match in re.finditer(r"<tr[^>]*>.*?</tr>", section, flags=re.I | re.S):
        row = match.group(0)
        row_cells = cells(row)
        actual_key = re.sub(r"\s+", ".", plain(row_cells[key_index])) if key_index < len(row_cells) else ""
        expected_key = re.sub(r"\s+", ".", key)
        if actual_key == expected_key:
            for index in sorted(values, reverse=True):
                row = replace_cell(row, index, values[index])
            section = section[:match.start()] + row + section[match.end():]
            return document[:start] + section + document[end:]
    raise RuntimeError(f"Row not found under {heading}: {key}")


def update_summary_field(document: str, field: str, value: str) -> str:
    return replace_keyed_row_cells(document, "1. Değerlendirme Özeti", 0, field, {1: value})


def has_summary_field(document: str, field: str) -> bool:
    start, end = section_bounds(document, "1. Değerlendirme Özeti")
    for row in re.findall(r"<tr[^>]*>.*?</tr>", document[start:end], flags=re.I | re.S):
        row_cells = cells(row)
        if row_cells and plain(row_cells[0]) == field:
            return True
    return False


def upsert_summary_note(document: str, value: str) -> str:
    for field in ("Değerlendirme Sonucu", "Genel Not"):
        if has_summary_field(document, field):
            return update_summary_field(document, field, value)
    start, end = section_bounds(document, "1. Değerlendirme Özeti")
    section = document[start:end]
    body = re.search(r"(<tbody[^>]*>)(.*?)(</tbody>)", section, flags=re.I | re.S)
    if not body:
        raise RuntimeError("Assessment summary table body missing")
    row = (
        '<tr><td class="confluenceTd">Genel Not</td>'
        f'<td class="confluenceTd">{html.escape(value)}</td></tr>'
    )
    section = section[:body.end(2)] + row + section[body.end(2):]
    return document[:start] + section + document[end:]


def status_from_cell(value: str) -> str:
    normalized = plain(value).upper()
    for label in LABELS:
        if normalized == label or normalized.endswith(f"- {label}"):
            return label
    raise RuntimeError(f"Unknown status value: {normalized}")


def assessment_distributions(document: str) -> tuple[Counter[str], Counter[str]]:
    output: list[Counter[str]] = []
    for heading, status_index in (("3. BP Takip Matrisi", 4), ("4. PA / GP Takip Matrisi", 5)):
        start, end = section_bounds(document, heading)
        section = document[start:end]
        count: Counter[str] = Counter()
        for row in re.findall(r"<tr[^>]*>.*?</tr>", section, flags=re.I | re.S):
            row_cells = cells(row)
            if len(row_cells) > status_index and plain(row_cells[0]) not in {"BP", "PA"}:
                count[status_from_cell(row_cells[status_index])] += 1
        output.append(count)
    return output[0], output[1]


def assessment_pa_distributions(code: str, document: str) -> tuple[dict[str, Counter[str]], dict[str, Counter[str]]]:
    after = {pa: Counter() for pa in ("PA 1.1 (BP)", "PA 2.1", "PA 2.2", "PA 3.1", "PA 3.2")}
    keyed_rows: list[tuple[str, str, str]] = []
    for heading, key_index, status_index in (
        ("3. BP Takip Matrisi", 0, 4),
        ("4. PA / GP Takip Matrisi", 1, 5),
    ):
        start, end = section_bounds(document, heading)
        for row in re.findall(r"<tr[^>]*>.*?</tr>", document[start:end], flags=re.I | re.S):
            row_cells = cells(row)
            if len(row_cells) <= status_index:
                continue
            key = re.sub(r"\s+", ".", plain(row_cells[key_index]))
            if heading.startswith("3.") and re.fullmatch(r"[A-Z]+\.\d+\.BP\d+", key):
                pa = "PA 1.1 (BP)"
            elif heading.startswith("4.") and re.fullmatch(r"GP\.\d\.\d\.\d", key):
                pa = plain(row_cells[0])
            else:
                continue
            status = status_from_cell(row_cells[status_index])
            after[pa][status] += 1
            keyed_rows.append((pa, key, status))
    before = {pa: Counter(counts) for pa, counts in after.items()}
    for pa, key, current in keyed_rows:
        previous = OLD_STATUS.get((code, key))
        if previous:
            before[pa][current] -= 1
            before[pa][previous] += 1
    return before, after


def remove_src001_obsolete_priority(document: str) -> str:
    start, end = section_bounds(document, "5. Öncelikli Tamamlama Listesi")
    section = document[start:end]
    body = re.search(r"(<tbody[^>]*>)(.*?)(</tbody>)", section, flags=re.I | re.S)
    if not body:
        raise RuntimeError("SRÇ.001 priority table body missing")
    retained = []
    for row in re.findall(r"<tr[^>]*>.*?</tr>", body.group(2), flags=re.I | re.S):
        if "SUP.7.BP6; GP 2.2.4" not in plain(row):
            retained.append(row)
    for number, row in enumerate(retained, start=1):
        retained[number - 1] = replace_cell(row, 0, str(number))
    section = section[:body.start(2)] + "".join(retained) + section[body.end(2):]
    return document[:start] + section + document[end:]


def review_dir(code: str) -> Path:
    path = REVIEWS / f"frm-001-surec-gozden-gecirme-formu-src-{code}-degerlendirme-1"
    if not (path / "body.storage.xhtml").exists():
        raise RuntimeError(f"Assessment #1 not found: SRÇ.{code}")
    return path


def format_distribution(count: Counter[str]) -> str:
    return "; ".join(f"{count[label]} {label}" for label in LABELS if count[label])


def format_summary_distribution(count: Counter[str]) -> str:
    values = [f"{count[label]} {label}" for label in LABELS if count[label]]
    if len(values) < 2:
        return values[0] if values else "-"
    return ", ".join(values[:-1]) + " ve " + values[-1]


def refresh_assessment(code: str) -> tuple[Counter[str], Counter[str], Counter[str], Counter[str]]:
    page = review_dir(code)
    storage_path = page / "body.storage.xhtml"
    document = storage_path.read_text(encoding="utf-8")
    before_bp, before_gp = assessment_distributions(document)
    document = update_summary_field(document, "Değerlendirme Tarihi", REPORT_DATE)
    document = upsert_summary_note(document, PROCESS[code]["summary"])
    for key, update in UPDATES[code].items():
        if key.startswith("GP."):
            document = replace_keyed_row_cells(
                document, "4. PA / GP Takip Matrisi", 1, key,
                {3: update.note, 4: update.evidence, 5: update.status, 6: update.action},
            )
        else:
            document = replace_keyed_row_cells(
                document, "3. BP Takip Matrisi", 0, key,
                {2: update.note, 3: update.evidence, 4: update.status, 5: update.action},
            )
    if code == "001":
        document = remove_src001_obsolete_priority(document)
    after_bp, after_gp = assessment_distributions(document)
    if has_summary_field(document, "BP Dağılımı"):
        document = update_summary_field(document, "BP Dağılımı", format_summary_distribution(after_bp))
    for field in ("PA / GP Dağılımı", "PA/GP Dağılımı"):
        if has_summary_field(document, field):
            document = update_summary_field(document, field, format_summary_distribution(after_gp))
    storage_path.write_text(document.strip() + "\n", encoding="utf-8")
    title = f"FRM.001 - Süreç Gözden Geçirme Formu (SRÇ.{code}) - Değerlendirme #1"
    (page / "body.view.html").write_text(build_view(title, document.strip()), encoding="utf-8")
    return before_bp, before_gp, after_bp, after_gp


def table_parts(document: str, heading: str) -> tuple[int, int, list[str], list[list[str]]]:
    start, end = section_bounds(document, heading)
    match = re.search(r"<table[^>]*>.*?</table>", document[start:end], flags=re.I | re.S)
    if not match:
        raise RuntimeError(f"Table missing under {heading}")
    table_start, table_end = start + match.start(), start + match.end()
    table_html = match.group(0)
    rows = [cells(row) for row in re.findall(r"<tr[^>]*>.*?</tr>", table_html, flags=re.I | re.S)]
    if len(rows) < 2:
        raise RuntimeError(f"Incomplete table under {heading}")
    return table_start, table_end, rows[0], rows[1:]


def render_table(headers: list[str], rows: list[list[str]]) -> str:
    head = "".join(f'<th class="confluenceTh">{cell}</th>' for cell in headers)
    body = "".join(
        "<tr>" + "".join(f'<td class="confluenceTd">{cell}</td>' for cell in row) + "</tr>"
        for row in rows
    )
    return f'<table class="wrapped confluenceTable"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>'


def replace_section_content(document: str, heading: str, content: str) -> str:
    start, end = section_bounds(document, heading)
    return document[:start] + content + document[end:]


def refresh_rpr(results: dict[str, tuple[Counter[str], Counter[str], Counter[str], Counter[str]]]) -> None:
    path = RPR_DIR / "body.storage.xhtml"
    document = path.read_text(encoding="utf-8")
    document = replace_keyed_row_cells(document, "1. Rapor Bilgileri", 0, "Son Güncelleme", {1: REPORT_DATE})

    table_start, table_end, headers, rows = table_parts(document, "4. Süreç Sonuç Özeti")
    row_map = {plain(row[0])[:7]: row for row in rows}
    refreshed_rows: list[list[str]] = []
    for code in PROCESS:
        key = f"SRÇ.{code}"
        if key not in row_map:
            raise RuntimeError(f"RPR.001 summary row missing: {key}")
        _, _, bp, gp = results[code]
        refreshed_rows.append([
            html.escape(PROCESS[code]["name"]), html.escape(PROCESS[code]["scope"]),
            html.escape(format_distribution(bp)), html.escape(format_distribution(gp)), "",
            html.escape(f"FRM.001 - Süreç Gözden Geçirme Formu (SRÇ.{code}) - Değerlendirme #1"),
            html.escape(PROCESS[code]["summary"]),
        ])
    document = document[:table_start] + render_table(headers, refreshed_rows) + document[table_end:]

    table_start, table_end, headers, rows = table_parts(document, "5. Etiket Dağılımları ve Eğilimler")
    trend_rows: list[list[str]] = []
    for code in PROCESS:
        _, _, bp, gp = results[code]
        trend_rows.append([
            f"SRÇ.{code}", str(bp["VAR"]), str(bp["DAĞINIK"]), str(bp["ZAYIF"]), str(bp["YOK"]),
            str(gp["VAR"]), str(gp["DAĞINIK"]), str(gp["ZAYIF"]), str(gp["YOK"]),
        ])
    trend_rows.append([
        "Eğilim Yorumu",
        "Yeterli, tutarlı ve izlenebilir biçimde karşılanan temel uygulamalar.",
        "Kanıtı bulunan ancak sistematikliği veya tamamlanması güçlendirilmesi gereken temel uygulamalar.",
        "Başlangıç düzeyinde tanım veya kanıtı bulunan temel uygulamalar.",
        "Yeterli tanım veya kullanılabilir kanıtı bulunmayan temel uygulamalar.",
        "Yeterli, tutarlı ve izlenebilir biçimde karşılanan genel uygulamalar.",
        "Kanıtı bulunan ancak sistematikliği veya tamamlanması güçlendirilmesi gereken genel uygulamalar.",
        "Başlangıç düzeyinde tanım veya kanıtı bulunan genel uygulamalar.",
        "Yeterli tanım veya kullanılabilir kanıtı bulunmayan genel uygulamalar.",
    ])
    document = document[:table_start] + render_table(headers, trend_rows) + document[table_end:]

    findings = render_table(
        ["Bulgu", "Tür", "Kaynak", "Yönlendirme / Durum", "Açıklama"],
        [
            ["Gerçek dönem performans verisi ve analiz sonuçlarının henüz oluşmaması", "Gözlem", "SRÇ.001, SRÇ.004, SRÇ.005, SRÇ.006, SRÇ.021, SRÇ.023, SRÇ.024 ve SRÇ.025 değerlendirmeleri", "İlgili Değerlendirme #1 kayıtlarında izleniyor", "Süreç özel LST.009 ölçümleri gerçek dönemlerde işletilmelidir."],
            ["Formal gözden geçirme, bulgu ve kapanış kayıtlarının süreç paketlerinde aynı olgunlukta olmaması", "Gözlem", "SRÇ.004, SRÇ.005, SRÇ.006, SRÇ.021, SRÇ.023, SRÇ.024 ve SRÇ.025 / GP.2.2.4", "İlgili Değerlendirme #1 kayıtlarında izleniyor", "Yetkili gözden geçiren doğrulaması ve kapanış bilgileri doğal kayıtlarla tamamlanmalıdır."],
            ["Rol bazlı yetkinlik ve eğitim/katılım kanıtlarının eksikliği", "Gözlem", "PA 3.2 / GP.3.2.3 sonuçları", "SRÇ.020 ihtiyacı değerlendirilecek", "Gerçek ihtiyaç oluştuğunda eğitim ve katılım kayıtları oluşturulmalıdır."],
            ["Hedef kitle ve rol/sorumluluk bilgilendirmelerinin doğrulanmaması", "Gözlem", "Tamamlanan süreçlerin GP.2.1.6 ve GP.3.2.2 sonuçları", "LST.012 veya doğal kaynak kayıtlarıyla tamamlanacak", "Confluence yayın kaydı ile gerçek bilgilendirme kanıtı ayrıştırılmalıdır."],
        ],
    )
    document = replace_section_content(document, "6. Önemli Bulgular", findings)

    opportunities = render_table(
        ["Fırsat", "Beklenen Fayda", "İlgili Süreç", "Yönlendirme"],
        [
            ["Süreç özel LST.009 tanımlarının gerçek dönem verileriyle işletilmesi", "Tanımlı yöntemlerin fiilî performans ve karar kanıtına dönüşmesi", "Tamamlanan tüm süreçler", "İlgili Değerlendirme #1; gerektiğinde SRÇ.018"],
            ["Paket gözden geçirme ve kapanış kanıtlarının ortak doğal kayıt yaklaşımıyla güçlendirilmesi", "GP.2.2.4 sonuçlarının tutarlı ve doğrulanabilir olması", "SRÇ.004, SRÇ.005, SRÇ.006, SRÇ.021, SRÇ.023, SRÇ.024 ve SRÇ.025", "İlgili Değerlendirme #1; gerektiğinde SRÇ.018"],
            ["Süreç değerlendirme sonuçlarının SRÇ.002 kalite yaklaşımına düzenli girdi sağlaması", "Kalite güvencesi ve süreç iyileştirmenin ortak veriyle yürütülmesi", "SRÇ.002 / SRÇ.005", "SRÇ.002 çalışmasında ele alınacak"],
        ],
    )
    document = replace_section_content(document, "7. İyileştirme Fırsatları", opportunities)

    strengths = render_table(
        ["Güçlü Uygulama", "Kaynak", "Koruma / Yaygınlaştırma Önerisi"],
        [
            ["Güncel süreç şablonu ve süreç özel LST.007-LST.010/FRM.001 paket yapısı", "Sekiz tamamlanmış süreç paketi", "Sıradaki tüm süreçlerde aynı aktif şablon ailesi kullanılmalı."],
            ["Mermaid kaynak ve PNG görsellerinin birlikte saklanması", "Tamamlanan süreçlerin süreç akışı ve LST.007 sayfaları", "Yeni süreçlerde aynı görsel-kaynak düzeni korunmalı."],
            ["Sayısal puan yerine gerekçeli etiket kullanılması", "PLN.001, PRS.003 ve sekiz Değerlendirme #1 kaydı", "Etiket sözlüğü, kanıt açıklaması ve tamamlayıcı aksiyon birlikte kullanılmalı."],
            ["Değerlendirmelerin aynı Değerlendirme #1 kaydı ve kümülatif RPR.001 üzerinde sürdürülmesi", "SRÇ.005; sekiz Değerlendirme #1 kaydı; RPR.001", "Her tamamlanan süreç ve kanıt değişiminde aynı kayıtlar güncellenmeli."],
            ["Yerel viewer, kontrollü yayın ve yayın sonrası doğrulama zinciri", "Repository çalışma akışı ve paket doğrulama raporları", "Her süreç paketi yayınında aynı doğrulama zinciri uygulanmalı."],
        ],
    )
    document = replace_section_content(document, "8. Güçlü Uygulamalar", strengths)
    path.write_text(document.strip() + "\n", encoding="utf-8")
    (RPR_DIR / "body.view.html").write_text(
        build_view("RPR.001 - Süreç Performansları Raporu", document.strip()), encoding="utf-8"
    )


def refresh_status() -> None:
    text = CURRENT_STATUS.read_text(encoding="utf-8")
    line = (
        "- SRÇ.001, SRÇ.004, SRÇ.005, SRÇ.006, SRÇ.021, SRÇ.023, SRÇ.024 ve SRÇ.025 "
        "Değerlendirme #1 kayıtları 15 Temmuz 2026 tarihinde güncel kanıtlarla yeniden "
        "değerlendirilmiş; sonuçlar kümülatif RPR.001 ile hizalanmıştır.\n"
    )
    if line not in text:
        marker = "## Bilinen riskler ve açık noktalar"
        if marker not in text:
            raise RuntimeError("CURRENT_STATUS insertion point missing")
        text = text.replace(marker, line + "\n" + marker)
        CURRENT_STATUS.write_text(text, encoding="utf-8")


def write_report(results: dict[str, tuple[Counter[str], Counter[str], Counter[str], Counter[str]]]) -> None:
    lines = [
        "# Tamamlanan Süreç Değerlendirmeleri Yenileme Raporu", "", f"Tarih: {REPORT_DATE}", "",
        "## Kapsam", "",
        "Mevcut Değerlendirme #1 kayıtları yerinde güncellenmiştir; yeni değerlendirme numarası oluşturulmamıştır. Sonuçlarda yalnız VAR, DAĞINIK, ZAYIF, YOK ve KAPSAM DIŞI etiketleri kullanılmış; sayısal puan üretilmemiştir.", "",
        "## Süreç Bazında PA Sonuçları", "",
    ]
    for code in results:
        document = (review_dir(code) / "body.storage.xhtml").read_text(encoding="utf-8")
        before_pa, after_pa = assessment_pa_distributions(code, document)
        lines += [f"### {PROCESS[code]['name']}", ""]
        for pa in ("PA 1.1 (BP)", "PA 2.1", "PA 2.2", "PA 3.1", "PA 3.2"):
            lines.append(f"- {pa}: {format_distribution(before_pa[pa])} → {format_distribution(after_pa[pa])}")
        lines.append("")
    lines += ["", "## Değişen Etiketler", ""]
    changes = 0
    for code in PROCESS:
        for key, update in UPDATES[code].items():
            page = review_dir(code) / "body.storage.xhtml"
            # The previous label is derived from the declared change rationale below.
            before = OLD_STATUS[(code, key)]
            lines.append(f"- **SRÇ.{code} / {key}: {before} → {update.status}.** {update.reason}")
            changes += 1
    lines += ["", "## Etiketi Değişmeyen Süreçler", ""]
    lines += [
        "- **SRÇ.006:** Gerçek bir süreç iyileştirmesi, SRÇ.018 değişiklik gözden geçirmesi ve doğrulanmış kazanım henüz yoktur.",
        "- **SRÇ.021:** Bilgi Kataloğunun yıllık gözden geçirmesi, kapsam genişletmesi ve gerçek performans sonuçları henüz yoktur.",
        "- **SRÇ.024:** Gerçek kalite döngüsü, müşteri anketi/RPR.002 ve YGG hedef değerlendirmesi henüz yoktur.",
        "- **SRÇ.025:** Gerçek ölçüm dönemi, bilgi ürünü sunumu, geri bildirim ve yıllık ölçüm değerlendirmesi henüz yoktur.",
        "", "## Diğer Düzeltmeler", "",
        "- Sekiz değerlendirmede değerlendirme tarihi 15-07-2026 olarak güncellendi.",
        "- Eski değerlendirme özetlerinde kalan yüzde/ortalama ifadeleri kaldırıldı; yalnız etiketli yaklaşım korundu.",
        "- SRÇ.001 öncelik listesindeki artık VAR olarak değerlendirilen formal kontrol maddesi çıkarıldı ve sıra numaraları yenilendi.",
        "- RPR.001 Süreç Sonuç Özeti ve Etiket Dağılımları tabloları sekiz Değerlendirme #1 kaydıyla eşitlendi.",
        "- SPICE Olgunluk Seviyesi hücreleri proje kararı gereği boş bırakıldı.",
        "", f"Toplam etiket değişikliği: **{changes}**. Etiket düşüşü: **0**.",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def verify(results: dict[str, tuple[Counter[str], Counter[str], Counter[str], Counter[str]]]) -> None:
    for code in PROCESS:
        page = review_dir(code)
        storage = (page / "body.storage.xhtml").read_text(encoding="utf-8")
        view = (page / "body.view.html").read_text(encoding="utf-8")
        if "Değerlendirme #2" in storage or "%" in plain(update_summary_value(storage)):
            raise RuntimeError(f"SRÇ.{code} assessment numbering/scoring rule violated")
        if REPORT_DATE not in storage or PROCESS[code]["summary"] not in html.unescape(storage):
            raise RuntimeError(f"SRÇ.{code} summary/date not refreshed")
        if plain(storage) not in plain(view):
            raise RuntimeError(f"SRÇ.{code} view is not aligned")
        expected_bp, expected_gp = results[code][2], results[code][3]
        actual_bp, actual_gp = assessment_distributions(storage)
        if actual_bp != expected_bp or actual_gp != expected_gp:
            raise RuntimeError(f"SRÇ.{code} distribution mismatch")

    rpr = (RPR_DIR / "body.storage.xhtml").read_text(encoding="utf-8")
    if rpr.count("<tbody>") != rpr.count("</tbody>"):
        raise RuntimeError("RPR.001 table bodies are unbalanced")
    for code, (_, _, bp, gp) in results.items():
        if format_distribution(bp) not in rpr or format_distribution(gp) not in rpr:
            raise RuntimeError(f"RPR.001 distribution missing: SRÇ.{code}")
    if "SPICE Olgunluk Seviyesi" not in rpr:
        raise RuntimeError("RPR.001 maturity placeholder was removed")


def update_summary_value(document: str) -> str:
    start, end = section_bounds(document, "1. Değerlendirme Özeti")
    for row in re.findall(r"<tr[^>]*>.*?</tr>", document[start:end], flags=re.I | re.S):
        row_cells = cells(row)
        if len(row_cells) > 1 and plain(row_cells[0]) in {"Değerlendirme Sonucu", "Genel Not"}:
            return row_cells[1]
    raise RuntimeError("Assessment result summary missing")


def main() -> None:
    results = {code: refresh_assessment(code) for code in PROCESS}
    refresh_rpr(results)
    refresh_status()
    write_report(results)
    verify(results)
    for code, (before_bp, before_gp, after_bp, after_gp) in results.items():
        print(
            f"[UPDATED] SRÇ.{code} | BP {format_distribution(before_bp)} -> {format_distribution(after_bp)} | "
            f"PA/GP {format_distribution(before_gp)} -> {format_distribution(after_gp)}"
        )
    print(f"[REPORT] {REPORT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
