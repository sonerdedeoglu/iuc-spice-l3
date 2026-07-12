import argparse
from datetime import date, timedelta
from html import escape, unescape
from pathlib import Path
import re
import unicodedata

import yaml

from confluence_publisher import ConfluencePublisher


ROOT = Path(__file__).resolve().parent.parent
SPICE_YAML_PATH = ROOT / "resources" / "standards" / "spice_practices.yaml"
REPORT_PATH = ROOT / "reports" / "process_review_forms_generation_report.md"
PREVIEW_DIR = ROOT / "reports" / "process_review_forms"

ROOT_01_CODE = "ROOT-01"
ROOT_91_CODE = "ROOT-91"
TARGET_PARENT_TITLE = "Süreç Gözden Geçirmeleri"
TEMPLATE_TITLE = "İÜC.BİDB.FRM.001.Ş - Süreç Gözden Geçirme Formu Şablonu"
FORM_CODE = "İÜC.BİDB.FRM.0041"
ASSESSOR = "Soner DEDEOĞLU - Kalite Danışmanı"
DEFAULT_OWNER = "SÜREÇ SAHİBİ"
FOLDER_PLACEHOLDER = "Bu sayfa, alt dokümanların gruplanması amacıyla oluşturulmuştur."

PROCESS_ORDER = [
    "İÜC.BİDB.SRÇ.001",
    "İÜC.BİDB.SRÇ.002",
    "İÜC.BİDB.SRÇ.003",
    "İÜC.BİDB.SRÇ.004",
    "İÜC.BİDB.SRÇ.005",
    "İÜC.BİDB.SRÇ.006",
    "İÜC.BİDB.SRÇ.007",
    "İÜC.BİDB.SRÇ.008",
    "İÜC.BİDB.SRÇ.009",
    "İÜC.BİDB.SRÇ.010",
    "İÜC.BİDB.SRÇ.011",
    "İÜC.BİDB.SRÇ.012",
    "İÜC.BİDB.SRÇ.013",
    "İÜC.BİDB.SRÇ.014",
    "İÜC.BİDB.SRÇ.015",
    "İÜC.BİDB.SRÇ.016",
    "İÜC.BİDB.SRÇ.017",
    "İÜC.BİDB.SRÇ.018",
    "İÜC.BİDB.SRÇ.019",
    "İÜC.BİDB.SRÇ.020",
    "İÜC.BİDB.SRÇ.021",
    "İÜC.BİDB.SRÇ.022",
    "İÜC.BİDB.SRÇ.023",
    "İÜC.BİDB.SRÇ.024",
    "İÜC.BİDB.SRÇ.025",
    "İÜC.BİDB.SRÇ.026",
]

REQUIRED_PA_2_1_IDS = [
    "GP.2.1.1",
    "GP.2.1.2",
    "GP.2.1.3",
    "GP.2.1.4",
    "GP.2.1.5",
    "GP.2.1.6",
]
REQUIRED_PA_2_2_IDS = [
    "GP.2.2.1",
    "GP.2.2.2",
    "GP.2.2.3",
    "GP.2.2.4",
]

SECTION_HEADING_PATTERN = re.compile(
    r"<h(?P<level>[1-6])\b[^>]*>.*?</h(?P=level)>",
    flags=re.I | re.S,
)
TABLE_ROW_PATTERN = re.compile(r"<tr\b.*?</tr>", flags=re.I | re.S)
TABLE_CELL_PATTERN = re.compile(
    r"<(?P<tag>td|th)\b[^>]*>(?P<body>.*?)</(?P=tag)>",
    flags=re.I | re.S,
)
CDATA_PATTERN = re.compile(r"<!\[CDATA\[(.*?)\]\]>", flags=re.S)

OWNER_LABELS = [
    "Süreç Sahibi",
    "Süreç sahibi",
    "Sahip",
    "Süreç Sorumlusu",
    "Sorumlu",
]


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Confluence güncellemesi yapmadan plan, rapor ve önizleme üretir.",
    )
    return parser.parse_args()


def load_manifest():
    with open(ROOT / "manifest.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_spice_source():
    with open(SPICE_YAML_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def normalize_text(value):
    return unicodedata.normalize("NFC", str(value)).strip()


def normalize_key(value):
    value = normalize_text(value).casefold()
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def clean_storage_text(storage, preserve_lines=False):
    storage = re.sub(r"<br\s*/?>", "\n", str(storage), flags=re.I)
    storage = re.sub(r"</(p|tr|h[1-6]|li)>", "\n", storage, flags=re.I)
    storage = CDATA_PATTERN.sub(r"\1", storage)
    storage = re.sub(r"<[^>]+>", " ", storage)
    text = unescape(storage).replace("\xa0", " ")

    if preserve_lines:
        lines = [
            re.sub(r"[ \t]+", " ", line).strip()
            for line in text.splitlines()
        ]
        return "\n".join(line for line in lines if line).strip()

    return re.sub(r"\s+", " ", text).strip()


def validate_spice_source(data):
    missing = []
    processes = data.get("processes")

    if not isinstance(processes, list):
        missing.append("processes listesi bulunamadı.")
        processes = []

    if len(processes) != 26:
        missing.append(f"Süreç sayısı 26 olmalıdır; bulunan sayı: {len(processes)}.")

    processes_by_code = {}

    for process in processes:
        code = normalize_text(process.get("corporate_code", ""))

        if not code:
            missing.append("corporate_code alanı boş olan süreç var.")
            continue

        if code in processes_by_code:
            missing.append(f"Tekrarlı süreç kodu var: {code}.")

        processes_by_code[code] = process

    ordered_processes = []

    for code in PROCESS_ORDER:
        process = processes_by_code.get(code)

        if process is None:
            missing.append(f"Süreç YAML içinde bulunamadı: {code}.")
            continue

        ordered_processes.append(process)
        validate_process(process, missing)

    gp_2_1 = extract_required_generic_practices(
        data,
        "PA_2_1",
        REQUIRED_PA_2_1_IDS,
        missing,
    )
    gp_2_2 = extract_required_generic_practices(
        data,
        "PA_2_2",
        REQUIRED_PA_2_2_IDS,
        missing,
    )

    return {
        "valid": not missing,
        "missing": missing,
        "processes": ordered_processes,
        "gp_2_1": gp_2_1,
        "gp_2_2": gp_2_2,
    }


def validate_process(process, missing):
    code = normalize_text(process.get("corporate_code", ""))
    required_fields = [
        "corporate_code",
        "corporate_name",
        "spice_code",
        "spice_name",
        "base_practices",
    ]

    for field in required_fields:
        if field not in process or process[field] in ("", None, []):
            missing.append(f"{code}: {field} alanı eksik veya boş.")

    practices = process.get("base_practices")

    if not isinstance(practices, list) or not practices:
        missing.append(f"{code}: En az bir base_practices kaydı olmalıdır.")
        return

    for practice in practices:
        practice_id = normalize_text(practice.get("id", ""))

        for field in ("id", "title", "text"):
            if field not in practice or practice[field] in ("", None):
                missing.append(f"{code}: BP kaydında {field} alanı eksik: {practice_id or 'ID yok'}.")


def extract_required_generic_practices(data, attribute_key, required_ids, missing):
    attribute = data.get("generic_practices", {}).get(attribute_key)

    if not isinstance(attribute, dict):
        missing.append(f"generic_practices.{attribute_key} bulunamadı.")
        return []

    practices = attribute.get("practices")

    if not isinstance(practices, list):
        missing.append(f"generic_practices.{attribute_key}.practices listesi bulunamadı.")
        return []

    practices_by_id = {
        normalize_text(practice.get("id", "")): practice
        for practice in practices
    }
    ordered = []

    for practice_id in required_ids:
        practice = practices_by_id.get(practice_id)

        if practice is None:
            missing.append(f"{attribute_key} içinde GP eksik: {practice_id}.")
            continue

        for field in ("id", "title", "text"):
            if field not in practice or practice[field] in ("", None):
                missing.append(f"{practice_id}: {field} alanı eksik veya boş.")

        ordered.append(practice)

    return ordered


def find_root_child_page(publisher, manifest, root_code):
    page = publisher.find_root_child_page(
        manifest,
        root_code,
    )
    return publisher.client.get_page(page["id"])


def find_page_by_exact_title(client, space_key, title):
    result = client.find_page(
        space_key,
        title,
    )

    matches = [
        page
        for page in result.get("results", [])
        if normalize_text(page.get("title", "")) == normalize_text(title)
    ]

    if not matches:
        return None

    if len(matches) > 1:
        raise ValueError(f"Confluence içinde aynı başlığa sahip birden fazla sayfa bulundu: {title}")

    return client.get_page(matches[0]["id"])


def find_child_by_title(publisher, parent_id, title):
    page = publisher.find_child_by_title(
        parent_id,
        title,
    )

    if page is None:
        return None

    return publisher.client.get_page(page["id"])


def get_children(client, page_id):
    return [
        {
            "id": str(child["id"]),
            "title": normalize_text(child["title"]),
        }
        for child in client.get_children(page_id).get("results", [])
    ]


def find_process_page(process, root_01_children, client):
    code = normalize_text(process["corporate_code"])
    expected_title = f"{code} - {normalize_text(process['corporate_name'])}"

    for child in root_01_children:
        if child["title"] == expected_title:
            return client.get_page(child["id"])

    for child in root_01_children:
        if child["title"].startswith(f"{code} - ") or child["title"] == code:
            return client.get_page(child["id"])

    return None


def inspect_process_documentation(process, root_01_children, client):
    page = find_process_page(
        process,
        root_01_children,
        client,
    )

    if page is None:
        return {
            "corporate_code": process["corporate_code"],
            "status": "NOT_FOUND",
            "page_title": "",
            "page_id": "",
            "children": [],
            "owner": DEFAULT_OWNER,
            "owner_found": False,
        }

    body = page.get("body", {}).get("storage", {}).get("value", "")
    text = clean_storage_text(body)
    status = determine_documentation_status(text)
    owner = extract_process_owner(body)

    return {
        "corporate_code": process["corporate_code"],
        "status": status,
        "page_title": normalize_text(page["title"]),
        "page_id": str(page["id"]),
        "children": get_children(client, page["id"]),
        "owner": owner or DEFAULT_OWNER,
        "owner_found": owner is not None,
    }


def determine_documentation_status(text):
    normalized = normalize_key(text)
    placeholder = normalize_key(FOLDER_PLACEHOLDER)

    if not normalized:
        return "PLACEHOLDER_ONLY"

    if normalized == placeholder:
        return "PLACEHOLDER_ONLY"

    return "DOCUMENTED"


def extract_process_owner(body):
    owner = extract_process_owner_from_tables(body)

    if owner:
        return owner

    return extract_process_owner_from_lines(body)


def extract_process_owner_from_tables(body):
    label_keys = {normalize_key(label) for label in OWNER_LABELS}

    for row_match in TABLE_ROW_PATTERN.finditer(body):
        cells = [
            clean_storage_text(cell_match.group("body"))
            for cell_match in TABLE_CELL_PATTERN.finditer(row_match.group(0))
        ]

        if len(cells) < 2:
            continue

        if normalize_key(cells[0]).rstrip(":") in label_keys:
            value = clean_owner_value(cells[1])

            if value:
                return value

    return None


def extract_process_owner_from_lines(body):
    labels = "|".join(re.escape(label) for label in OWNER_LABELS)
    pattern = re.compile(
        rf"^(?:{labels})\s*[:：-]\s*(?P<value>.+)$",
        flags=re.I,
    )

    for line in clean_storage_text(body, preserve_lines=True).splitlines():
        match = pattern.search(line)

        if match is None:
            continue

        value = clean_owner_value(match.group("value"))

        if value:
            return value

    return None


def clean_owner_value(value):
    value = normalize_text(value)
    value = re.sub(r"\s*\|\s*.*$", "", value).strip()

    if not value:
        return ""

    if normalize_key(value) in {"-", "—", "değerlendirilecek", "süreç sahibi", "süreç sorumlusu"}:
        return ""

    if value.startswith("<") and value.endswith(">"):
        return ""

    return value


def remove_section_zero(template_body):
    matches = list(SECTION_HEADING_PATTERN.finditer(template_body))

    for index, match in enumerate(matches):
        heading_text = clean_storage_text(match.group(0))

        if not is_section_zero_heading(heading_text):
            continue

        start_level = int(match.group("level"))
        end = len(template_body)

        for next_match in matches[index + 1:]:
            next_level = int(next_match.group("level"))
            next_heading_text = clean_storage_text(next_match.group(0))

            if (
                not is_section_zero_heading(next_heading_text)
                and (
                    next_level <= start_level
                    or is_numbered_nonzero_heading(next_heading_text)
                )
            ):
                end = next_match.start()
                break

        stripped = template_body[:match.start()] + template_body[end:]
        return remove_leading_empty_blocks(stripped).strip(), {
            "removed": True,
            "heading": heading_text,
        }

    return template_body.strip(), {
        "removed": False,
        "heading": "",
    }


def is_section_zero_heading(text):
    return re.match(r"^\s*0(?:[\.\s:-]|$)", normalize_text(text)) is not None


def is_numbered_nonzero_heading(text):
    return re.match(r"^\s*[1-9](?:[\.\s:-]|$)", normalize_text(text)) is not None


def remove_leading_empty_blocks(body):
    body = re.sub(r"^\s*(<p>\s*(?:&nbsp;|\s)*</p>\s*)+", "", body, flags=re.I)
    return body


def generate_weekday_dates(count):
    current = date(2025, 8, 10) + timedelta(days=1)
    end_date = date(2025, 12, 10)
    dates = []

    while len(dates) < count and current <= end_date:
        if current.weekday() < 5:
            dates.append(current.strftime("%d.%m.%Y"))

        current += timedelta(days=1)

    if len(dates) != count:
        raise ValueError("Gerekli sayıda hafta içi değerlendirme tarihi üretilemedi.")

    return dates


def build_generation_items(
    publisher,
    validation,
    template_body,
    section_zero_result,
    documentation_by_code,
    dates,
):
    items = []

    for index, process in enumerate(validation["processes"]):
        code = normalize_text(process["corporate_code"])
        title = build_form_title(process)
        documentation = documentation_by_code[code]
        owner = documentation["owner"]
        evaluation_date = dates[index]
        body = build_form_body(
            template_body,
            process,
            validation["gp_2_1"],
            validation["gp_2_2"],
            documentation,
            evaluation_date,
            owner,
        )
        items.append(
            {
                "sequence_no": index + 1,
                "process": process,
                "title": title,
                "body": body,
                "date": evaluation_date,
                "documentation": documentation,
                "bp_count": len(process.get("base_practices", [])),
                "preview_path": write_preview_file(code, body),
                "section_zero_removed": section_zero_result["removed"],
            }
        )

    return items


def build_form_title(process):
    return f"{FORM_CODE} - Süreç Gözden Geçirme Matrisi ({normalize_text(process['corporate_code'])})"


def build_form_body(template_body, process, gp_2_1, gp_2_2, documentation, evaluation_date, owner):
    template_part = replace_template_placeholders(
        template_body,
        placeholder_values(process, documentation, evaluation_date, owner),
    )
    generated_part = build_generated_assessment_content(
        process,
        gp_2_1,
        gp_2_2,
        documentation,
        evaluation_date,
        owner,
    )

    if clean_storage_text(template_part):
        return "\n".join(
            [
                template_part,
                generated_part,
            ]
        ).strip()

    return generated_part


def placeholder_values(process, documentation, evaluation_date, owner):
    assessed_process = f"{normalize_text(process['corporate_code'])} - {normalize_text(process['corporate_name'])}"
    process_reference = f"{normalize_text(process['spice_code'])} - {normalize_text(process['spice_name'])}"
    form_name = f"Süreç Gözden Geçirme Matrisi ({normalize_text(process['corporate_code'])})"
    scope = build_evaluation_scope(process)

    return {
        "Süreç Kodu": process["corporate_code"],
        "Süreç ID": process["corporate_code"],
        "Süreç Adı": process["corporate_name"],
        "Süreç Referansı": process_reference,
        "Standart Süreç Kodu": process["spice_code"],
        "Standart Süreç Adı": process["spice_name"],
        "Doküman Kodu": FORM_CODE,
        "Form Kodu": FORM_CODE,
        "Doküman Adı": form_name,
        "Form Adı": form_name,
        "Değerlendirilen Süreç": assessed_process,
        "Süreç Durumu": "Aktif",
        "Süreç Sürümü": "v1.0",
        "Değerlendirme Kapsamı": scope,
        "Değerlendirme Tarihi": evaluation_date,
        "Değerlendirmeyi Yapan": ASSESSOR,
        "Değerlendirmeyi Onaylayan": owner,
        "Değerlendirme Sonucu": build_evaluation_result(documentation["status"]),
        "Hazırlayan": ASSESSOR,
        "Gözden Geçiren": owner,
        "Onaylayan": owner,
        "Tarih": evaluation_date,
        "Sürüm": "v1.0",
        "Durum": "Aktif",
    }


def replace_template_placeholders(body, values):
    updated = body

    for placeholder, value in sorted(values.items(), key=lambda item: len(item[0]), reverse=True):
        updated = replace_status_placeholder_macro(
            updated,
            placeholder,
            value,
        )
        replacement = escape(str(value), quote=True)
        escaped_placeholder = escape(f"<{placeholder}>", quote=True)
        double_escaped_placeholder = escape(escaped_placeholder, quote=True)
        updated = re.sub(
            rf"<code\b[^>]*>\s*{re.escape(escaped_placeholder)}\s*</code>",
            replacement,
            updated,
            flags=re.I | re.S,
        )
        updated = updated.replace(escaped_placeholder, replacement)
        updated = updated.replace(double_escaped_placeholder, replacement)

    return updated


def replace_status_placeholder_macro(body, placeholder, value):
    placeholder_pattern = re.escape(escape(placeholder, quote=True))
    pattern = re.compile(
        r"<ac:structured-macro\b(?=[^>]*\bac:name=[\"']status[\"']).*?"
        r"<ac:parameter\b(?=[^>]*\bac:name=[\"']title[\"'])[^>]*>\s*"
        + placeholder_pattern
        + r"\s*</ac:parameter>.*?</ac:structured-macro>",
        flags=re.I | re.S,
    )
    return pattern.sub(
        escape(str(value), quote=True),
        body,
    )


def build_generated_assessment_content(process, gp_2_1, gp_2_2, documentation, evaluation_date, owner):
    return "\n".join(
        [
            "<h1>1. Değerlendirme Özeti</h1>",
            build_summary_table(process, documentation, evaluation_date, owner),
            "<h1>2. Mevcut Dokümantasyon Durumu</h1>",
            build_documentation_table(documentation),
            "<h1>3. PA 1.1 Temel Uygulamalar (BP)</h1>",
            build_practice_table(process.get("base_practices", [])),
            "<h1>4. PA 2.1 Genel Uygulamalar (GP)</h1>",
            build_practice_table(gp_2_1),
            "<h1>5. PA 2.2 Genel Uygulamalar (GP)</h1>",
            build_practice_table(gp_2_2),
        ]
    )


def build_summary_table(process, documentation, evaluation_date, owner):
    rows = [
        ["Değerlendirilen Süreç", f"{process['corporate_code']} - {process['corporate_name']}"],
        ["Süreç Referansı", f"{process['spice_code']} - {process['spice_name']}"],
        ["Süreç Durumu", "Aktif"],
        ["Süreç Sürümü", "v1.0"],
        ["Değerlendirme Kapsamı", build_evaluation_scope(process)],
        ["Değerlendirme Tarihi", evaluation_date],
        ["Değerlendirmeyi Yapan", ASSESSOR],
        ["Değerlendirmeyi Onaylayan", owner],
        ["Değerlendirme Sonucu", build_evaluation_result(documentation["status"])],
    ]

    return build_key_value_table(rows)


def build_documentation_table(documentation):
    child_titles = [child["title"] for child in documentation["children"]]
    related_documents = ", ".join(child_titles) if child_titles else "İlgili alt doküman bulunamadı."
    page_reference = documentation["page_title"] or "Süreç sayfası bulunamadı."
    rows = [
        ["Dokümantasyon Durumu", documentation_status_text(documentation["status"])],
        ["Süreç Sayfası", page_reference],
        ["İlgili Alt Dokümanlar", related_documents],
    ]

    return build_key_value_table(rows)


def documentation_status_text(status):
    if status == "DOCUMENTED":
        return "Dokümantasyon mevcut"

    if status == "PLACEHOLDER_ONLY":
        return "Yalnızca yer tutucu içerik mevcut"

    if status == "NOT_FOUND":
        return "Süreç sayfası bulunamadı"

    return "Dokümantasyon durumu değerlendirilecek"


def build_key_value_table(rows):
    table_rows = []

    for key, value in rows:
        table_rows.append(
            "<tr>"
            f"<th>{escape(str(key), quote=True)}</th>"
            f"<td>{escape(str(value), quote=True)}</td>"
            "</tr>"
        )

    return "\n".join(
        [
            "<table>",
            "<tbody>",
            *table_rows,
            "</tbody>",
            "</table>",
        ]
    )


def build_practice_table(practices):
    rows = []

    for sequence_no, practice in enumerate(practices, start=1):
        rows.append(
            "<tr>"
            f"<td>{sequence_no}</td>"
            f"<td>{escape(str(practice.get('id', '')), quote=True)}</td>"
            f"<td>{escape(str(practice.get('title', '')), quote=True)}</td>"
            f"<td>{escape(str(practice.get('text', '')), quote=True)}</td>"
            "<td>Değerlendirilecek</td>"
            "<td>Değerlendirilecek</td>"
            "<td>Değerlendirilecek</td>"
            "</tr>"
        )

    return "\n".join(
        [
            "<table>",
            "<thead>",
            "<tr>",
            "<th>No</th>",
            "<th>Referans</th>",
            "<th>Uygulama / Pratik</th>",
            "<th>Beklenen İçerik</th>",
            "<th>Kanıt</th>",
            "<th>Değerlendirme Sonucu</th>",
            "<th>Açıklama</th>",
            "</tr>",
            "</thead>",
            "<tbody>",
            *rows,
            "</tbody>",
            "</table>",
        ]
    )


def build_evaluation_scope(process):
    bp_count = len(process.get("base_practices", []))
    return (
        f"PA 1.1 (BP.1 - BP.{bp_count}) / "
        "PA 2.1 (GP.2.1.1 - GP.2.1.6) / "
        "PA 2.2 (GP.2.2.1 - GP.2.2.4)"
    )


def build_evaluation_result(status):
    if status == "DOCUMENTED":
        return (
            "Mevcut dokümantasyon üzerinden ön değerlendirme yapılmıştır. "
            "Süreç dokümantasyonu mevcuttur; içerik ve kanıt seti SPICE "
            "değerlendirme kapsamına göre gözden geçirilecektir."
        )

    return (
        "Mevcut dokümantasyon henüz tamamlanmamıştır. Süreç dokümanı ve "
        "ilişkili kanıt setleri oluşturulduktan sonra değerlendirme güncellenecektir."
    )


def write_preview_file(process_code, body):
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    path = PREVIEW_DIR / f"{safe_process_filename(process_code)}_preview.xhtml"
    path.write_text(body, encoding="utf-8")
    return path


def safe_process_filename(process_code):
    replacements = {
        "İ": "I",
        "Ü": "U",
        "Ç": "C",
        "Ş": "S",
        "Ğ": "G",
        "Ö": "O",
        "ı": "i",
        "ü": "u",
        "ç": "c",
        "ş": "s",
        "ğ": "g",
        "ö": "o",
    }
    safe = normalize_text(process_code)

    for source, target in replacements.items():
        safe = safe.replace(source, target)

    safe = safe.replace(".", "-")
    safe = re.sub(r"[^A-Za-z0-9_-]+", "-", safe)
    return safe.strip("-")


def upsert_target_parent(publisher, space_key, root_91_page):
    existing = publisher.find_child_by_title(
        root_91_page["id"],
        TARGET_PARENT_TITLE,
    )

    if existing is not None:
        current = publisher.client.get_page(existing["id"])
        return current

    return publisher.client.create_page(
        space_key,
        root_91_page["id"],
        TARGET_PARENT_TITLE,
        "<p>Bu sayfa, süreç gözden geçirme formlarının gruplanması amacıyla oluşturulmuştur.</p>",
    )


def upsert_generated_forms(publisher, space_key, parent_page, items):
    updated_pages = []

    for item in items:
        publisher.upsert_child_page(
            space_key,
            parent_page["id"],
            item["title"],
            item["body"],
        )
        updated_pages.append(item["title"])
        print(f"[UPSERT] {item['title']}")

    return updated_pages


def write_report(context):
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        build_report(context),
        encoding="utf-8",
    )


def build_report(context):
    lines = [
        "# Süreç Gözden Geçirme Formları Üretim Raporu",
        "",
        "## Özet",
        "",
        f"- Çalışma modu: {'Ön izleme' if context['dry_run'] else 'Normal'}",
        f"- Üretilecek / üretilen form sayısı: {len(context.get('items', []))}",
        f"- Hedef üst sayfa: {TARGET_PARENT_TITLE}",
        f"- Rapor dosyası: {relative_path(REPORT_PATH)}",
        "",
        "## Kullanılan Şablon",
        "",
        f"- Şablon sayfası: {TEMPLATE_TITLE}",
        f"- Şablon sayfa ID: {context.get('template_page_id', '') or 'Okunmadı'}",
        "",
        "## Kullanılan SPICE Kaynağı",
        "",
        f"- YAML dosyası: {relative_path(SPICE_YAML_PATH)}",
        "- PDF bu script içinde okunmamıştır.",
        "",
        "## YAML Doğrulama Sonucu",
        "",
    ]
    add_validation_section(lines, context)
    lines.extend(
        [
            "",
            "## 0. Bölüm Kaldırma Kontrolü",
            "",
        ]
    )
    add_section_zero_section(lines, context)
    lines.extend(
        [
            "",
            "## Üretilecek / Üretilen Sayfalar",
            "",
        ]
    )
    add_generated_pages_section(lines, context.get("items", []))
    lines.extend(
        [
            "",
            "## Tarih Ataması",
            "",
        ]
    )
    add_date_section(lines, context.get("items", []))
    lines.extend(
        [
            "",
            "## Süreç Dokümantasyon Durumu",
            "",
        ]
    )
    add_documentation_status_section(lines, context.get("items", []))
    lines.extend(
        [
            "",
            "## Süreç Sahibi Tespiti",
            "",
        ]
    )
    add_owner_section(lines, context.get("items", []))
    lines.extend(
        [
            "",
            "## BP Özetleri",
            "",
        ]
    )
    add_bp_summary_section(lines, context.get("items", []))
    lines.extend(
        [
            "",
            "## GP Özetleri",
            "",
        ]
    )
    add_gp_summary_section(lines, context)
    lines.extend(
        [
            "",
            "## Eksik / Hatalı Veri",
            "",
        ]
    )
    add_missing_section(lines, context)
    lines.extend(
        [
            "",
            "## Oluşturulan / Güncellenen Sayfalar",
            "",
        ]
    )
    add_updated_pages_section(lines, context)
    lines.extend(
        [
            "",
            "## Uyarılar",
            "",
        ]
    )
    add_warnings_section(lines, context)

    return "\n".join(lines) + "\n"


def add_validation_section(lines, context):
    validation = context.get("validation")

    if validation is None:
        lines.append("- Doğrulama çalıştırılmadı.")
        return

    lines.append(f"- Sonuç: {'Başarılı' if validation['valid'] else 'Başarısız'}")
    lines.append(f"- Süreç sayısı: {len(validation.get('processes', []))}")
    lines.append(f"- PA 2.1 GP sayısı: {len(validation.get('gp_2_1', []))}")
    lines.append(f"- PA 2.2 GP sayısı: {len(validation.get('gp_2_2', []))}")


def add_section_zero_section(lines, context):
    result = context.get("section_zero_result")

    if not result:
        lines.append("- Şablon okunmadığı için kontrol yapılmadı.")
        return

    lines.append(f"- 0. bölüm kaldırıldı: {'Evet' if result['removed'] else 'Hayır'}")

    if result["heading"]:
        lines.append(f"- Kaldırılan başlık: {result['heading']}")


def add_generated_pages_section(lines, items):
    if not items:
        lines.append("- Üretilecek sayfa bulunmuyor.")
        return

    for item in items:
        lines.append(f"- {item['title']}")


def add_date_section(lines, items):
    if not items:
        lines.append("- Tarih ataması yapılmadı.")
        return

    for item in items:
        lines.append(f"- {item['process']['corporate_code']}: {item['date']}")


def add_documentation_status_section(lines, items):
    if not items:
        lines.append("- Dokümantasyon durumu incelenmedi.")
        return

    for item in items:
        documentation = item["documentation"]
        lines.append(
            f"- {item['process']['corporate_code']}: {documentation['status']} "
            f"({documentation['page_title'] or 'Süreç sayfası bulunamadı'})"
        )


def add_owner_section(lines, items):
    if not items:
        lines.append("- Süreç sahibi tespiti yapılmadı.")
        return

    for item in items:
        documentation = item["documentation"]
        source = "Confluence sayfasından tespit edildi" if documentation["owner_found"] else "Varsayılan değer kullanıldı"
        lines.append(
            f"- {item['process']['corporate_code']}: {documentation['owner']} ({source})"
        )


def add_bp_summary_section(lines, items):
    if not items:
        lines.append("- BP özeti yok.")
        return

    for item in items:
        lines.append(
            f"- {item['process']['corporate_code']}: {item['bp_count']} BP"
        )


def add_gp_summary_section(lines, context):
    validation = context.get("validation") or {}
    lines.append(f"- PA 2.1: {len(validation.get('gp_2_1', []))} GP doğrulandı.")
    lines.append(f"- PA 2.2: {len(validation.get('gp_2_2', []))} GP doğrulandı.")


def add_missing_section(lines, context):
    validation = context.get("validation")

    if validation is None:
        lines.append("- Doğrulama sonucu yok.")
        return

    if not validation["missing"]:
        lines.append("- Eksik veya hatalı veri bulunmadı.")
        return

    for item in validation["missing"]:
        lines.append(f"- {item}")


def add_updated_pages_section(lines, context):
    updated_pages = context.get("updated_pages", [])

    if not updated_pages:
        lines.append("- Normal modda güncellenen sayfa yok.")
        return

    for title in updated_pages:
        lines.append(f"- {title}")


def add_warnings_section(lines, context):
    warnings = context.get("warnings", [])

    if not warnings:
        lines.append("- Uyarı yok.")
        return

    for warning in warnings:
        lines.append(f"- {warning}")


def relative_path(path):
    return str(path.relative_to(ROOT))


def print_dry_run_summary(parent_page, items, validation):
    parent_state = "mevcut" if parent_page is not None else "oluşturulacak"
    print(f"[DRY-RUN] Hedef üst sayfa: {TARGET_PARENT_TITLE} ({parent_state})")
    print(f"[VALIDATION] YAML doğrulaması başarılı: 26 süreç, {len(validation['gp_2_1'])} PA 2.1 GP, {len(validation['gp_2_2'])} PA 2.2 GP")

    for item in items:
        print(
            f"[DRY-RUN UPSERT] {item['title']} | "
            f"BP: {item['bp_count']} | "
            f"Tarih: {item['date']} | "
            f"Dokümantasyon: {item['documentation']['status']}"
        )

    print(f"[DONE] Dry-run raporu yazıldı: {relative_path(REPORT_PATH)}")


def build_context(dry_run, validation):
    return {
        "dry_run": dry_run,
        "validation": validation,
        "template_page_id": "",
        "section_zero_result": None,
        "items": [],
        "updated_pages": [],
        "warnings": [],
    }


def main():
    args = parse_args()
    spice_data = load_spice_source()
    validation = validate_spice_source(spice_data)
    context = build_context(args.dry_run, validation)

    if not validation["valid"]:
        write_report(context)
        print(f"[ERROR] YAML doğrulaması başarısız. Rapor yazıldı: {relative_path(REPORT_PATH)}")
        raise SystemExit(1)

    manifest = load_manifest()
    publisher = ConfluencePublisher()
    client = publisher.client
    space_key = manifest["confluence"]["space"]
    root_01_page = find_root_child_page(
        publisher,
        manifest,
        ROOT_01_CODE,
    )
    root_91_page = find_root_child_page(
        publisher,
        manifest,
        ROOT_91_CODE,
    )
    template_page = find_page_by_exact_title(
        client,
        space_key,
        TEMPLATE_TITLE,
    )

    if template_page is None:
        context["validation"]["missing"].append(f"Canlı Confluence şablon sayfası bulunamadı: {TEMPLATE_TITLE}")
        write_report(context)
        print(f"[ERROR] Canlı şablon sayfası bulunamadı. Rapor yazıldı: {relative_path(REPORT_PATH)}")
        raise SystemExit(1)

    context["template_page_id"] = str(template_page["id"])
    stripped_template_body, section_zero_result = remove_section_zero(
        template_page.get("body", {}).get("storage", {}).get("value", ""),
    )
    context["section_zero_result"] = section_zero_result
    root_01_children = get_children(
        client,
        root_01_page["id"],
    )
    documentation_by_code = {
        normalize_text(process["corporate_code"]): inspect_process_documentation(
            process,
            root_01_children,
            client,
        )
        for process in validation["processes"]
    }
    dates = generate_weekday_dates(len(validation["processes"]))
    target_parent_page = find_child_by_title(
        publisher,
        root_91_page["id"],
        TARGET_PARENT_TITLE,
    )
    items = build_generation_items(
        publisher,
        validation,
        stripped_template_body,
        section_zero_result,
        documentation_by_code,
        dates,
    )
    context["items"] = items

    if args.dry_run:
        write_report(context)
        print_dry_run_summary(
            target_parent_page,
            items,
            validation,
        )
        return

    parent_page = upsert_target_parent(
        publisher,
        space_key,
        root_91_page,
    )
    context["updated_pages"] = upsert_generated_forms(
        publisher,
        space_key,
        parent_page,
        items,
    )
    write_report(context)
    print("[DONE] 26 süreç gözden geçirme formu üretildi.")


if __name__ == "__main__":
    main()
