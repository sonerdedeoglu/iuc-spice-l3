import argparse
from html import escape, unescape
from pathlib import Path
import re
import unicodedata

import yaml

from confluence_publisher import ConfluencePublisher


ROOT = Path(__file__).resolve().parent.parent
REPORT_PATH = ROOT / "reports" / "template_restructure_report.md"

ROOT_02_CODE = "ROOT-02"
ROOT_05_CODE = "ROOT-05"
ARCHIVE_PAGE_TITLE = "Arşiv - Kaldırılan Şablonlar"
REMOVED_PREFIX = "[KALDIRILDI] "

ROOT_02_REGISTER_PARAGRAPH = (
    "Bu sayfa, İÜC BİDB çalışmasında kullanılan doküman, kayıt ve form "
    "şablonları için kayıt tablosunu içerir."
)
ROOT_02_REGISTER_COLUMNS = [
    "Sıra No",
    "Şablon Kodu",
    "Şablon Adı",
    "Durum",
    "Erişim Linki",
]

KLV_004_TITLE = "İÜC.BİDB.KLV.004 - Dokümantasyon Deposu Oluşturma Kılavuzu"
KLV_004_NOTE = (
    "Bu kılavuz, İÜC BİDB SPICE 2026 Level 3 çalışmasında dokümantasyon "
    "deposu yapısının oluşturulması ve sürdürülmesi amacıyla kullanılır."
)

ACTIVE_TEMPLATE_MAPPINGS = [
    {
        "old_title": "İÜC.BİDB.ŞBL.001 - Süreç Tanımı Şablonu",
        "new_title": "İÜC.BİDB.SRÇ.XXX.Ş - Süreç Tanımı Şablonu",
    },
    {
        "old_title": "İÜC.BİDB.ŞBL.002 - Doküman Gözden Geçirme Kaydı Şablonu",
        "new_title": "İÜC.BİDB.LST.003.Ş - Doküman Gözden Geçirme Kaydı Şablonu",
    },
    {
        "old_title": "İÜC.BİDB.ŞBL.005 - Aktif Dokümanlar Listesi Şablonu",
        "new_title": "İÜC.BİDB.LST.001.Ş - Aktif Dokümanlar Listesi Şablonu",
    },
    {
        "old_title": "İÜC.BİDB.ŞBL.007 - Süreç Gözden Geçirme Matrisi Şablonu",
        "new_title": "İÜC.BİDB.FRM.001.Ş - Süreç Gözden Geçirme Formu Şablonu",
    },
    {
        "old_title": "İÜC.BİDB.ŞBL.008 - Prosedür Tanımı Şablonu",
        "new_title": "İÜC.BİDB.PRS.XXX.Ş - Prosedür Tanımı Şablonu",
    },
    {
        "old_title": "İÜC.BİDB.ŞBL.009 - Yaşam Döngüsü Doküman İhtiyaç Matrisi Şablonu",
        "new_title": "İÜC.BİDB.LST.005.Ş - Yaşam Döngüsü Doküman Üretim Matrisi Şablonu",
    },
    {
        "old_title": "İÜC.BİDB.ŞBL.010 - Kılavuz ve Talimat Tanımı Şablonu",
        "new_title": "İÜC.BİDB.KLV.XXX.Ş - Kılavuz ve Talimat Tanımı Şablonu",
    },
    {
        "old_title": "İÜC.BİDB.ŞBL.011 - Standart Süreç Envanteri Şablonu",
        "new_title": "İÜC.BİDB.LST.006.Ş - Standart Süreç Envanteri Şablonu",
    },
    {
        "old_title": "İÜC.BİDB.ŞBL.012 - Süreç Mimari ve Etkileşim Matrisi Şablonu",
        "new_title": "İÜC.BİDB.LST.007.Ş - Süreç Mimari ve Etkileşim Matrisi Şablonu",
    },
    {
        "old_title": "İÜC.BİDB.ŞBL.013 - İş Ürünleri ve Kalite Kriterleri Listesi Şablonu",
        "new_title": "İÜC.BİDB.LST.008.Ş - İş Ürünleri ve Kalite Kriterleri Listesi Şablonu",
    },
    {
        "old_title": "İÜC.BİDB.ŞBL.014 - Süreç Performans Ölçüm Seti Şablonu",
        "new_title": "İÜC.BİDB.LST.009.Ş - Süreç Performans Ölçüm Seti Şablonu",
    },
    {
        "old_title": "İÜC.BİDB.ŞBL.015 - Süreç Rol Yetki ve RACI Matrisi Şablonu",
        "new_title": "İÜC.BİDB.LST.010.Ş - Süreç Rol Yetki ve RACI Matrisi Şablonu",
    },
    {
        "old_title": "İÜC.BİDB.ŞBL.017 - Süreç Yaygınlaştırma ve Bilgilendirme Kaydı Şablonu",
        "new_title": "İÜC.BİDB.LST.012.Ş - Süreç Yaygınlaştırma ve Bilgilendirme Kaydı Şablonu",
    },
]

ARCHIVE_TEMPLATE_MAPPINGS = [
    {
        "old_title": "İÜC.BİDB.ŞBL.003 - Doküman Değişiklik Talebi Şablonu",
        "reason": "SUP.10 kapsamında genel değişiklik formu olarak ele alınacaktır.",
    },
    {
        "old_title": "İÜC.BİDB.ŞBL.004 - Doküman Yayın Kaydı Şablonu",
        "reason": "Aktif Dokümanlar Listesi iyileştirmesi kapsamında yönetilecektir.",
    },
    {
        "old_title": "İÜC.BİDB.ŞBL.006 - Doküman Değişiklik Kaydı Şablonu",
        "reason": "Doküman revizyonları her dokümanın sürüm geçmişi ve aktif doküman listesi üzerinden izlenmektedir.",
    },
]

KLV_TEMPLATE_MAPPING = {
    "old_title": "İÜC.BİDB.ŞBL.016 - Repository Yapısı Şablonu",
    "new_title": KLV_004_TITLE,
    "reason": "Repository yapısı şablon niteliğinden çıkarılarak kılavuz doküman olarak yönetilecektir.",
}

REGISTER_TITLES = [
    "İÜC.BİDB.FRM.001.Ş - Süreç Gözden Geçirme Formu Şablonu",
    "İÜC.BİDB.KLV.XXX.Ş - Kılavuz ve Talimat Tanımı Şablonu",
    "İÜC.BİDB.LST.001.Ş - Aktif Dokümanlar Listesi Şablonu",
    "İÜC.BİDB.LST.003.Ş - Doküman Gözden Geçirme Kaydı Şablonu",
    "İÜC.BİDB.LST.005.Ş - Yaşam Döngüsü Doküman Üretim Matrisi Şablonu",
    "İÜC.BİDB.LST.006.Ş - Standart Süreç Envanteri Şablonu",
    "İÜC.BİDB.LST.007.Ş - Süreç Mimari ve Etkileşim Matrisi Şablonu",
    "İÜC.BİDB.LST.008.Ş - İş Ürünleri ve Kalite Kriterleri Listesi Şablonu",
    "İÜC.BİDB.LST.009.Ş - Süreç Performans Ölçüm Seti Şablonu",
    "İÜC.BİDB.LST.010.Ş - Süreç Rol Yetki ve RACI Matrisi Şablonu",
    "İÜC.BİDB.LST.012.Ş - Süreç Yaygınlaştırma ve Bilgilendirme Kaydı Şablonu",
    "İÜC.BİDB.PRS.XXX.Ş - Prosedür Tanımı Şablonu",
    "İÜC.BİDB.SRÇ.XXX.Ş - Süreç Tanımı Şablonu",
]

RI_PAGE_TAG_PATTERN = re.compile(r"<ri:page\b[^>]*/?>", flags=re.I | re.S)
CONTENT_TITLE_PATTERN = re.compile(
    r"(?P<prefix>\bri:content-title=)(?P<quote>[\"'])(?P<title>.*?)(?P=quote)",
    flags=re.I | re.S,
)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Plan and report changes without updating Confluence.",
    )
    return parser.parse_args()


def load_manifest():
    with open(ROOT / "manifest.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def normalize_text(value):
    return unicodedata.normalize("NFC", str(value)).strip()


def normalize_key(value):
    value = normalize_text(value).casefold()
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def find_node_by_code(manifest, code):
    for node in manifest["nodes"]:
        if node["code"] == code:
            return node

    raise ValueError(f"Node does not exist in manifest: {code}")


def get_page_record(client, page_id, parent_id=None, depth=0):
    page = client.get_page(page_id)

    return {
        "id": str(page["id"]),
        "title": normalize_text(page["title"]),
        "body": page.get("body", {}).get("storage", {}).get("value", ""),
        "version_number": page["version"]["number"],
        "parent_id": str(parent_id) if parent_id is not None else None,
        "depth": depth,
        "children": [],
    }


def find_root_child_page(client, manifest, code):
    root_page_id = str(manifest["confluence"]["root"]["page_id"])
    node = find_node_by_code(manifest, code)
    expected_title = normalize_text(node["title"])

    for child in client.get_children(root_page_id).get("results", []):
        if normalize_text(child["title"]) == expected_title:
            return get_page_record(
                client,
                child["id"],
                root_page_id,
                1,
            )

    raise ValueError(f"{code} page does not exist under configured root page")


def get_direct_children(client, page_id):
    children = []

    for child in client.get_children(page_id).get("results", []):
        children.append(
            {
                "id": str(child["id"]),
                "title": normalize_text(child["title"]),
                "version_number": child.get("version", {}).get("number"),
                "parent_id": str(page_id),
            }
        )

    return children


def index_by_title(pages):
    return {
        normalize_text(page["title"]): page
        for page in pages
    }


def crawl_page_tree(client, root_page_id):
    pages_by_id = {}

    def crawl(page_id, parent_id=None, depth=0):
        page = get_page_record(
            client,
            page_id,
            parent_id,
            depth,
        )
        pages_by_id[page["id"]] = page

        for child in client.get_children(page["id"]).get("results", []):
            child_id = str(child["id"])
            page["children"].append(child_id)

        for child_id in page["children"]:
            if child_id not in pages_by_id:
                crawl(child_id, page["id"], depth + 1)

    crawl(str(root_page_id))
    return pages_by_id


def find_pages_in_space(client, space_key, title):
    result = client.find_page(
        space_key,
        title,
    )

    return [
        {
            "id": str(page["id"]),
            "title": normalize_text(page["title"]),
        }
        for page in result.get("results", [])
        if normalize_text(page["title"]) == normalize_text(title)
    ]


def build_plan(publisher, manifest):
    client = publisher.client
    space_key = manifest["confluence"]["space"]
    root_page_id = str(manifest["confluence"]["root"]["page_id"])
    root_02_page = find_root_child_page(
        client,
        manifest,
        ROOT_02_CODE,
    )
    root_05_page = find_root_child_page(
        client,
        manifest,
        ROOT_05_CODE,
    )
    root_02_children = get_direct_children(
        client,
        root_02_page["id"],
    )
    root_05_children = get_direct_children(
        client,
        root_05_page["id"],
    )
    root_02_children_by_title = index_by_title(root_02_children)
    root_05_children_by_title = index_by_title(root_05_children)
    pages_by_id = crawl_page_tree(
        client,
        root_page_id,
    )
    tree_titles = {}

    for page in pages_by_id.values():
        tree_titles.setdefault(page["title"], []).append(page)

    plan = {
        "space_key": space_key,
        "root_page_id": root_page_id,
        "root_02_page": root_02_page,
        "root_05_page": root_05_page,
        "root_02_children_by_title": root_02_children_by_title,
        "root_05_children_by_title": root_05_children_by_title,
        "renames": [],
        "archives": [],
        "already_active": [],
        "already_archived": [],
        "klv_action": None,
        "archive_page": root_02_children_by_title.get(ARCHIVE_PAGE_TITLE),
        "archive_page_create": False,
        "register_rows": build_register_rows(publisher, space_key),
        "conflicts": [],
        "warnings": [],
        "links_updated": [],
        "links_manual_review": [],
    }

    plan_archive_page(
        client,
        space_key,
        plan,
    )
    plan_active_template_renames(
        client,
        space_key,
        plan,
        root_02_children_by_title,
    )
    plan_archived_templates(
        client,
        space_key,
        plan,
        root_02_children_by_title,
        tree_titles,
    )
    plan_klv_004(
        client,
        space_key,
        plan,
        root_02_children_by_title,
        root_05_children_by_title,
        tree_titles,
    )
    detect_unmapped_legacy_templates(
        plan,
        root_02_children,
    )

    link_report = analyze_internal_links(
        pages_by_id,
        active_link_title_map(),
        archived_old_titles(),
    )
    plan["links_updated"] = link_report["updated"]
    plan["links_manual_review"] = link_report["manual_review"]

    return plan


def plan_archive_page(client, space_key, plan):
    if plan["archive_page"] is not None:
        return

    existing_archive_pages = find_pages_in_space(
        client,
        space_key,
        ARCHIVE_PAGE_TITLE,
    )

    if existing_archive_pages:
        plan["conflicts"].append(
            f"Archive page title exists outside ROOT-02: {ARCHIVE_PAGE_TITLE}"
        )
        return

    plan["archive_page_create"] = True


def plan_active_template_renames(client, space_key, plan, root_02_children_by_title):
    for mapping in ACTIVE_TEMPLATE_MAPPINGS:
        old_title = normalize_text(mapping["old_title"])
        new_title = normalize_text(mapping["new_title"])
        old_page = root_02_children_by_title.get(old_title)
        target_page = root_02_children_by_title.get(new_title)
        target_pages = find_pages_in_space(
            client,
            space_key,
            new_title,
        )

        if old_page is not None:
            conflicting_pages = [
                page
                for page in target_pages
                if page["id"] != old_page["id"]
            ]

            if conflicting_pages:
                plan["conflicts"].append(
                    f"Cannot rename {old_title}; target title already exists: {new_title}"
                )
                continue

            plan["renames"].append(
                {
                    "old_title": old_title,
                    "new_title": new_title,
                    "page_id": old_page["id"],
                }
            )
            continue

        if target_page is not None:
            plan["already_active"].append(
                {
                    "title": new_title,
                    "page_id": target_page["id"],
                }
            )
            continue

        if target_pages:
            plan["conflicts"].append(
                f"Target active template title exists outside ROOT-02: {new_title}"
            )
            continue

        plan["conflicts"].append(
            f"Active template source and target are missing: {old_title} -> {new_title}"
        )


def plan_archived_templates(
    client,
    space_key,
    plan,
    root_02_children_by_title,
    tree_titles,
):
    for mapping in ARCHIVE_TEMPLATE_MAPPINGS:
        plan_archive_action(
            client,
            space_key,
            plan,
            root_02_children_by_title,
            tree_titles,
            mapping["old_title"],
            mapping["reason"],
        )


def plan_klv_004(
    client,
    space_key,
    plan,
    root_02_children_by_title,
    root_05_children_by_title,
    tree_titles,
):
    old_title = normalize_text(KLV_TEMPLATE_MAPPING["old_title"])
    target_title = normalize_text(KLV_TEMPLATE_MAPPING["new_title"])
    old_page = root_02_children_by_title.get(old_title)
    target_page = root_05_children_by_title.get(target_title)
    target_pages = find_pages_in_space(
        client,
        space_key,
        target_title,
    )

    if old_page is None:
        if target_page is not None:
            plan["warnings"].append(
                f"{target_title} already exists under ROOT-05; source template is not under ROOT-02."
            )
        else:
            plan["conflicts"].append(
                f"KLV.004 source template and target page are missing: {old_title}"
            )

        note_already_archived(
            plan,
            old_title,
            tree_titles,
        )
        return

    if target_pages and (
        target_page is None
        or any(page["id"] != target_page["id"] for page in target_pages)
    ):
        plan["conflicts"].append(
            f"Cannot create/update KLV.004; target title exists outside ROOT-05: {target_title}"
        )
        return

    plan["klv_action"] = {
        "source_page_id": old_page["id"],
        "old_title": old_title,
        "new_title": target_title,
        "target_page_id": target_page["id"] if target_page else None,
        "action": "update" if target_page else "create",
    }
    plan_archive_action(
        client,
        space_key,
        plan,
        root_02_children_by_title,
        tree_titles,
        old_title,
        KLV_TEMPLATE_MAPPING["reason"],
    )


def plan_archive_action(
    client,
    space_key,
    plan,
    root_02_children_by_title,
    tree_titles,
    old_title,
    reason,
):
    old_title = normalize_text(old_title)
    old_page = root_02_children_by_title.get(old_title)
    archived_title = archived_title_for(old_title)

    if old_page is None:
        archived_page = root_02_children_by_title.get(archived_title)

        if archived_page is not None:
            plan["already_archived"].append(
                {
                    "title": archived_title,
                    "page_id": archived_page["id"],
                }
            )
            return

        note_already_archived(
            plan,
            old_title,
            tree_titles,
        )
        return

    archived_title_pages = find_pages_in_space(
        client,
        space_key,
        archived_title,
    )
    conflicting_pages = [
        page
        for page in archived_title_pages
        if page["id"] != old_page["id"]
    ]

    if conflicting_pages:
        plan["conflicts"].append(
            f"Cannot archive {old_title}; archived title already exists: {archived_title}"
        )
        return

    plan["archives"].append(
        {
            "old_title": old_title,
            "archived_title": archived_title,
            "page_id": old_page["id"],
            "reason": reason,
        }
    )


def note_already_archived(plan, old_title, tree_titles):
    matching_tree_pages = tree_titles.get(old_title, [])

    if matching_tree_pages:
        for page in matching_tree_pages:
            plan["already_archived"].append(
                {
                    "title": old_title,
                    "page_id": page["id"],
                }
            )
        return

    plan["warnings"].append(
        f"Archive source page was not found: {old_title}"
    )


def detect_unmapped_legacy_templates(plan, root_02_children):
    mapped_old_titles = {
        normalize_text(mapping["old_title"])
        for mapping in ACTIVE_TEMPLATE_MAPPINGS
    }
    mapped_old_titles.update(
        normalize_text(mapping["old_title"])
        for mapping in ARCHIVE_TEMPLATE_MAPPINGS
    )
    mapped_old_titles.add(normalize_text(KLV_TEMPLATE_MAPPING["old_title"]))

    for page in root_02_children:
        title = normalize_text(page["title"])

        if not title.startswith("İÜC.BİDB.ŞBL."):
            continue

        if title in mapped_old_titles:
            continue

        plan["conflicts"].append(
            f"Unmapped legacy template page under ROOT-02: {title}"
        )


def archived_title_for(title):
    title = normalize_text(title)

    if title.startswith(REMOVED_PREFIX):
        return title

    return f"{REMOVED_PREFIX}{title}"


def active_link_title_map():
    return {
        normalize_text(mapping["old_title"]): normalize_text(mapping["new_title"])
        for mapping in ACTIVE_TEMPLATE_MAPPINGS
    }


def archived_old_titles():
    titles = {
        normalize_text(mapping["old_title"])
        for mapping in ARCHIVE_TEMPLATE_MAPPINGS
    }
    titles.add(normalize_text(KLV_TEMPLATE_MAPPING["old_title"]))
    return titles


def build_register_rows(publisher, space_key):
    rows = []

    for sequence_no, title in enumerate(REGISTER_TITLES, start=1):
        code, name = split_code_and_name(title)
        rows.append(
            [
                sequence_no,
                code,
                name,
                "Aktif",
                publisher.build_page_link_cell(
                    title,
                    space_key,
                ),
            ]
        )

    return rows


def split_code_and_name(title):
    title = normalize_text(title)

    if " - " not in title:
        return title, title

    code, name = title.split(" - ", 1)
    return normalize_text(code), normalize_text(name)


def analyze_internal_links(pages_by_id, active_title_map, archived_titles):
    report = {
        "updated": [],
        "manual_review": [],
    }

    for page in pages_by_id.values():
        for old_title in extract_internal_link_titles(page["body"]):
            if old_title in active_title_map:
                report["updated"].append(
                    {
                        "source_page_id": page["id"],
                        "source_page_title": page["title"],
                        "old_title": old_title,
                        "new_title": active_title_map[old_title],
                    }
                )
                continue

            if old_title in archived_titles:
                report["manual_review"].append(
                    {
                        "source_page_id": page["id"],
                        "source_page_title": page["title"],
                        "old_title": old_title,
                        "reason": "Old template was archived or removed.",
                    }
                )

    return report


def extract_internal_link_titles(body):
    titles = []

    for tag_match in RI_PAGE_TAG_PATTERN.finditer(body):
        attr_match = CONTENT_TITLE_PATTERN.search(tag_match.group(0))

        if attr_match is None:
            continue

        titles.append(normalize_text(unescape(attr_match.group("title"))))

    return titles


def replace_internal_link_titles(body, active_title_map):
    replacement_count = 0

    def replace_tag(tag_match):
        nonlocal replacement_count
        tag = tag_match.group(0)

        def replace_title(attr_match):
            nonlocal replacement_count
            current_title = normalize_text(unescape(attr_match.group("title")))

            if current_title not in active_title_map:
                return attr_match.group(0)

            replacement_count += 1
            quote = attr_match.group("quote")
            new_title = escape(active_title_map[current_title], quote=True)
            return f"{attr_match.group('prefix')}{quote}{new_title}{quote}"

        return CONTENT_TITLE_PATTERN.sub(
            replace_title,
            tag,
            count=1,
        )

    updated_body = RI_PAGE_TAG_PATTERN.sub(
        replace_tag,
        body,
    )
    return updated_body, replacement_count


def build_archive_body(current_body, reason):
    notice = (
        f"<p>{escape('Bu şablon aktif şablon listesinden kaldırılmıştır. Gerekçe: ' + reason, quote=True)}</p>"
    )

    if "Bu şablon aktif şablon listesinden kaldırılmıştır." in current_body:
        return current_body

    return "\n".join(
        [
            notice,
            current_body,
        ]
    )


def build_klv_004_body(source_body):
    body = source_body
    body = body.replace(
        escape(KLV_TEMPLATE_MAPPING["old_title"], quote=True),
        escape(KLV_004_TITLE, quote=True),
    )
    body = body.replace(
        "İÜC.BİDB.ŞBL.016",
        "İÜC.BİDB.KLV.004",
    )
    body = body.replace(
        "Repository Yapısı Şablonu",
        "Dokümantasyon Deposu Oluşturma Kılavuzu",
    )

    note = f"<p>{escape(KLV_004_NOTE, quote=True)}</p>"

    if KLV_004_NOTE in unescape(body):
        return body

    return "\n".join(
        [
            note,
            body,
        ]
    )


def build_root_02_register_body(publisher, plan):
    return publisher.build_register_body(
        ROOT_02_REGISTER_PARAGRAPH,
        ROOT_02_REGISTER_COLUMNS,
        plan["register_rows"],
    )


def apply_plan(publisher, manifest, plan):
    client = publisher.client
    space_key = plan["space_key"]

    if plan["archive_page_create"]:
        client.create_page(
            space_key,
            plan["root_02_page"]["id"],
            ARCHIVE_PAGE_TITLE,
            "<p>Bu sayfa, kaldırılan şablonların kayıt altında tutulması amacıyla oluşturulmuştur.</p>",
        )

    for rename in plan["renames"]:
        current_page = client.get_page(rename["page_id"])
        client.update_page(
            rename["page_id"],
            space_key,
            rename["new_title"],
            current_page.get("body", {}).get("storage", {}).get("value", ""),
            current_page["version"]["number"] + 1,
        )
        print(f"[RENAME] {rename['old_title']} -> {rename['new_title']}")

    if plan["klv_action"] is not None:
        apply_klv_004_action(
            client,
            space_key,
            plan,
        )
        print(f"[CREATE/UPDATE] {KLV_004_TITLE}")

    for archive in plan["archives"]:
        current_page = client.get_page(archive["page_id"])
        current_body = current_page.get("body", {}).get("storage", {}).get("value", "")
        client.update_page(
            archive["page_id"],
            space_key,
            archive["archived_title"],
            build_archive_body(
                current_body,
                archive["reason"],
            ),
            current_page["version"]["number"] + 1,
        )
        print(f"[ARCHIVE] {archive['old_title']}")

    apply_internal_link_updates(
        client,
        space_key,
        manifest["confluence"]["root"]["page_id"],
        active_link_title_map(),
    )

    current_root_02_page = client.get_page(plan["root_02_page"]["id"])
    client.update_page(
        plan["root_02_page"]["id"],
        space_key,
        current_root_02_page["title"],
        build_root_02_register_body(
            publisher,
            plan,
        ),
        current_root_02_page["version"]["number"] + 1,
    )
    print("[UPDATE] ROOT-02 Register")


def apply_klv_004_action(client, space_key, plan):
    action = plan["klv_action"]
    source_page = client.get_page(action["source_page_id"])
    source_body = source_page.get("body", {}).get("storage", {}).get("value", "")
    new_body = build_klv_004_body(source_body)

    if action["target_page_id"] is None:
        client.create_page(
            space_key,
            plan["root_05_page"]["id"],
            KLV_004_TITLE,
            new_body,
        )
        return

    target_page = client.get_page(action["target_page_id"])
    client.update_page(
        action["target_page_id"],
        space_key,
        KLV_004_TITLE,
        new_body,
        target_page["version"]["number"] + 1,
    )


def apply_internal_link_updates(client, space_key, root_page_id, active_title_map):
    pages_by_id = crawl_page_tree(
        client,
        root_page_id,
    )

    for page in pages_by_id.values():
        updated_body, replacement_count = replace_internal_link_titles(
            page["body"],
            active_title_map,
        )

        if replacement_count == 0 or updated_body == page["body"]:
            continue

        current_page = client.get_page(page["id"])
        client.update_page(
            page["id"],
            space_key,
            current_page["title"],
            updated_body,
            current_page["version"]["number"] + 1,
        )


def print_dry_run(plan):
    for rename in plan["renames"]:
        print(f"[DRY-RUN RENAME] {rename['old_title']} -> {rename['new_title']}")

    for archive in plan["archives"]:
        print(f"[DRY-RUN ARCHIVE] {archive['old_title']}")

    if plan["klv_action"] is not None:
        print(f"[DRY-RUN CREATE/UPDATE] {KLV_004_TITLE}")

    print("[DRY-RUN UPDATE] ROOT-02 Register")
    print(f"[DONE] Dry-run report written to {relative_report_path()}")


def write_report(plan, dry_run):
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        build_report(
            plan,
            dry_run,
        ),
        encoding="utf-8",
    )


def build_report(plan, dry_run):
    lines = [
        "# Template Restructure Report",
        "",
        "## Summary",
        "",
        f"- Mode: {'dry-run' if dry_run else 'normal'}",
        f"- Planned renames: {len(plan['renames'])}",
        f"- Planned archives: {len(plan['archives'])}",
        f"- Planned KLV.004 action: {'yes' if plan['klv_action'] else 'no'}",
        f"- ROOT-02 register rows: {len(plan['register_rows'])}",
        f"- Link replacements planned: {len(plan['links_updated'])}",
        f"- Links requiring manual review: {len(plan['links_manual_review'])}",
        f"- Conflicts: {len(plan['conflicts'])}",
        "",
        "## Planned renames",
        "",
    ]
    add_rename_lines(lines, plan["renames"])
    lines.extend(
        [
            "",
            "## Planned archives",
            "",
        ]
    )
    add_archive_lines(lines, plan["archives"])
    lines.extend(
        [
            "",
            "## Planned KLV.004 creation/update",
            "",
        ]
    )
    add_klv_lines(lines, plan)
    lines.extend(
        [
            "",
            "## Register preview",
            "",
        ]
    )
    add_register_preview(lines, plan["register_rows"])
    lines.extend(
        [
            "",
            "## Conflicts",
            "",
        ]
    )
    add_simple_list(lines, plan["conflicts"], "No conflicts detected.")
    lines.extend(
        [
            "",
            "## Links updated",
            "",
        ]
    )
    add_link_update_lines(lines, plan["links_updated"])
    lines.extend(
        [
            "",
            "## Links requiring manual review",
            "",
        ]
    )
    add_manual_link_lines(lines, plan["links_manual_review"])
    lines.extend(
        [
            "",
            "## Warnings",
            "",
        ]
    )
    add_simple_list(lines, plan["warnings"], "No warnings.")

    return "\n".join(lines) + "\n"


def add_rename_lines(lines, renames):
    if not renames:
        lines.append("No renames planned.")
        return

    for rename in renames:
        lines.append(
            f"- {markdown_text(rename['old_title'])} -> {markdown_text(rename['new_title'])}"
        )


def add_archive_lines(lines, archives):
    if not archives:
        lines.append("No archives planned.")
        return

    for archive in archives:
        lines.append(
            f"- {markdown_text(archive['old_title'])} -> {markdown_text(archive['archived_title'])}"
        )
        lines.append(f"  Gerekçe: {markdown_text(archive['reason'])}")


def add_klv_lines(lines, plan):
    action = plan["klv_action"]

    if action is None:
        lines.append("No KLV.004 creation/update planned.")
        return

    lines.append(f"- Action: {action['action']}")
    lines.append(f"- Source: {markdown_text(action['old_title'])}")
    lines.append(f"- Target: {markdown_text(action['new_title'])}")


def add_register_preview(lines, rows):
    lines.append("| Sıra No | Şablon Kodu | Şablon Adı | Durum | Erişim Linki |")
    lines.append("|---:|---|---|---|---|")

    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                markdown_text(storage_text(cell))
                for cell in row
            )
            + " |"
        )


def add_link_update_lines(lines, links):
    if not links:
        lines.append("No internal links will be updated.")
        return

    for link in links:
        lines.append(
            f"- {markdown_text(link['source_page_title'])}: "
            f"{markdown_text(link['old_title'])} -> {markdown_text(link['new_title'])}"
        )


def add_manual_link_lines(lines, links):
    if not links:
        lines.append("No links require manual review.")
        return

    for link in links:
        lines.append(
            f"- {markdown_text(link['source_page_title'])}: "
            f"{markdown_text(link['old_title'])} ({markdown_text(link['reason'])})"
        )


def add_simple_list(lines, items, empty_text):
    if not items:
        lines.append(empty_text)
        return

    for item in items:
        lines.append(f"- {markdown_text(item)}")


def storage_text(value):
    if isinstance(value, dict) and "storage" in value:
        return "İncele"

    return value


def markdown_text(value):
    return normalize_text(value).replace("\n", " ")


def relative_report_path():
    return str(REPORT_PATH.relative_to(ROOT))


def main():
    args = parse_args()
    manifest = load_manifest()
    publisher = ConfluencePublisher()
    plan = build_plan(
        publisher,
        manifest,
    )

    write_report(
        plan,
        args.dry_run,
    )

    if args.dry_run:
        print_dry_run(plan)
        return

    if plan["conflicts"]:
        print(f"[ERROR] Conflicts detected. Report written to {relative_report_path()}")
        raise SystemExit(1)

    apply_plan(
        publisher,
        manifest,
        plan,
    )
    print(f"[DONE] Template restructuring complete. Report written to {relative_report_path()}")


if __name__ == "__main__":
    main()
