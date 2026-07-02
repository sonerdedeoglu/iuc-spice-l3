from html import escape
import re
import unicodedata

import markdown as markdown_library
from requests import HTTPError

from confluence_client import ConfluenceClient


class ConfluencePublisher:

    def __init__(self):
        self.client = ConfluenceClient()

    def publish(
        self,
        space_key,
        parent_id,
        title,
        body,
    ):
        page = self.client.find_page(
            space_key,
            title,
        )

        if page["size"] == 0:
            return self.client.create_page(
                space_key,
                parent_id,
                title,
                body,
            )

        return page["results"][0]

    def sync_structure(self, manifest):
        space_key = manifest["confluence"]["space"]
        root_page_id = manifest["confluence"]["root"]["page_id"]
        pages_by_code = {
            "ROOT": {
                "id": root_page_id,
            }
        }
        results = []

        for node in manifest["nodes"]:
            page, created = self.sync_node(
                space_key,
                pages_by_code,
                node,
            )

            pages_by_code[node["code"]] = page
            results.append(
                {
                    "code": node["code"],
                    "created": created,
                }
            )

        return results

    def sync_registers(self, manifest, registers):
        space_key = manifest["confluence"]["space"]
        root_page_id = manifest["confluence"]["root"]["page_id"]
        updated_registers = []

        for register in registers:
            node = self.find_node_by_code(
                manifest,
                register["code"],
            )

            page = self.find_child_by_title(
                root_page_id,
                node["title"],
            )

            if page is None:
                raise ValueError(f"{register['code']} page does not exist in Confluence")

            current_page = self.client.get_page(page["id"])
            updated_page = self.client.update_page(
                page["id"],
                space_key,
                current_page["title"],
                self.build_register_body(
                    register["paragraph"],
                    register["columns"],
                    register["rows"],
                ),
                current_page["version"]["number"] + 1,
            )

            self.ensure_label(
                page["id"],
                node["code"],
            )

            updated_registers.append(
                {
                    "code": node["code"],
                    "page": updated_page,
                }
            )

        return updated_registers

    def find_root_child_page(self, manifest, code):
        root_page_id = manifest["confluence"]["root"]["page_id"]
        node = self.find_node_by_code(
            manifest,
            code,
        )
        page = self.find_child_by_title(
            root_page_id,
            node["title"],
        )

        if page is None:
            raise ValueError(f"{code} page does not exist in Confluence")

        return page

    def upsert_child_page(self, space_key, parent_id, title, body):
        try:
            existing_page = self.find_child_by_title(
                parent_id,
                title,
            )

            if existing_page is None:
                return self.client.create_page(
                    space_key,
                    parent_id,
                    title,
                    body,
                )

            current_page = self.client.get_page(existing_page["id"])

            return self.client.update_page(
                existing_page["id"],
                space_key,
                current_page["title"],
                body,
                current_page["version"]["number"] + 1,
            )
        except Exception:
            print("[ERROR] Failed to upsert page")
            print(f"Title: {title}")
            print(f"Parent ID: {parent_id}")
            raise

    def import_templates(self, manifest, templates):
        space_key = manifest["confluence"]["space"]
        root_page_id = manifest["confluence"]["root"]["page_id"]
        root_02_node = self.find_node_by_code(
            manifest,
            "ROOT-02",
        )
        root_02_page = self.find_child_by_title(
            root_page_id,
            root_02_node["title"],
        )

        if root_02_page is None:
            raise ValueError("ROOT-02 page does not exist in Confluence")

        imported_templates = []

        for template in sorted(templates, key=lambda item: self.template_sort_key(item["title"])):
            title = self.normalize_text(template["title"])
            body = self.markdown_to_storage(
                template["content"],
                title,
            )
            page = self.upsert_child_page(
                space_key,
                root_02_page["id"],
                title,
                body,
            )

            metadata = self.extract_template_metadata(title)
            imported_templates.append(
                {
                    "title": title,
                    "code": metadata["code"],
                    "name": metadata["name"],
                    "page": page,
                }
            )

        return sorted(
            imported_templates,
            key=lambda item: self.template_sort_key(item["code"]),
        )

    def sync_template_register(self, manifest, templates):
        space_key = manifest["confluence"]["space"]
        rows = []

        for sequence_no, template in enumerate(
            sorted(templates, key=lambda item: self.template_sort_key(item["code"])),
            start=1,
        ):
            rows.append(
                [
                    sequence_no,
                    template["code"],
                    template["name"],
                    "Aktif",
                    self.build_page_link_cell(
                        template["title"],
                        space_key,
                    ),
                ]
            )

        registers = [
            {
                "code": "ROOT-02",
                "paragraph": "Bu sayfa, İÜC BİDB çalışmasında kullanılan doküman, kayıt ve form şablonları için kayıt tablosunu içerir.",
                "columns": [
                    "Sıra No",
                    "Şablon Kodu",
                    "Şablon Adı",
                    "Durum",
                    "Erişim Linki",
                ],
                "rows": rows,
            }
        ]

        return self.sync_registers(
            manifest,
            registers,
        )[0]

    def sync_node(self, space_key, pages_by_code, node):
        parent_code = node["parent"]
        parent_page = pages_by_code[parent_code]

        existing_page = self.find_child_by_title(
            parent_page["id"],
            node["title"],
        )

        if existing_page is not None:
            self.ensure_label(
                existing_page["id"],
                node["code"],
            )

            return existing_page, False

        created_page = self.client.create_page(
            space_key,
            parent_page["id"],
            node["title"],
            self.build_body(node),
        )

        self.ensure_label(
            created_page["id"],
            node["code"],
        )

        return created_page, True

    def find_child_by_title(self, parent_id, title):
        children = self.client.get_children(parent_id)

        for child in children["results"]:
            if child["title"] == title:
                return child

        return None

    def find_node_by_code(self, manifest, code):
        for node in manifest["nodes"]:
            if node["code"] == code:
                return node

        raise ValueError(f"Node does not exist in manifest: {code}")

    def ensure_label(self, page_id, label):
        try:
            self.client.add_label(page_id, label)
        except HTTPError as ex:
            if ex.response is None:
                raise

            if ex.response.status_code not in (400, 409):
                raise

    def build_register_body(self, paragraph, columns, rows):
        table_rows = []

        for row in rows:
            table_rows.append(
                "<tr>"
                + "".join(
                    self.build_table_cell(value)
                    for value in row
                )
                + "</tr>"
            )

        return "\n".join(
            [
                f"<p>{self.escape_cell(paragraph)}</p>",
                "<table>",
                "<thead>",
                "<tr>",
                *[f"<th>{self.escape_cell(column)}</th>" for column in columns],
                "</tr>",
                "</thead>",
                "<tbody>",
                *table_rows,
                "</tbody>",
                "</table>",
            ]
        )

    def escape_cell(self, value):
        return escape(str(value), quote=True)

    def build_table_cell(self, value):
        if isinstance(value, dict) and "storage" in value:
            return f"<td>{value['storage']}</td>"

        return f"<td>{self.escape_cell(value)}</td>"

    def build_page_link_cell(self, page_title, space_key):
        return {
            "storage": self.build_page_link(
                page_title,
                "İncele",
                space_key,
            )
        }

    def build_page_link(self, page_title, link_text, space_key):
        return (
            "<ac:link>"
            f'<ri:page ri:space-key="{self.escape_cell(space_key)}" '
            f'ri:content-title="{self.escape_cell(page_title)}" />'
            "<ac:plain-text-link-body>"
            f"<![CDATA[{self.cdata_text(link_text)}]]>"
            "</ac:plain-text-link-body>"
            "</ac:link>"
        )

    def cdata_text(self, value):
        return str(value).replace("]]>", "]]]]><![CDATA[>")

    def markdown_to_storage(self, content, title):
        markdown_text = self.remove_duplicate_h1(
            self.normalize_content(content),
            title,
        )
        body = markdown_library.markdown(
            markdown_text,
            extensions=[
                "extra",
                "fenced_code",
                "sane_lists",
                "tables",
            ],
        )

        if body.strip() == "":
            return "<p></p>"

        return body

    def remove_duplicate_h1(self, content, title):
        lines = content.split("\n")
        index = 0

        while index < len(lines) and lines[index].strip() == "":
            index += 1

        if index >= len(lines):
            return content

        h1 = re.match(r"^\s*#\s+(.+?)\s*#*\s*$", lines[index])

        if h1 is not None and self.normalize_text(h1.group(1)) == self.normalize_text(title):
            del lines[index]

            while index < len(lines) and lines[index].strip() == "":
                del lines[index]

            return "\n".join(lines)

        if (
            index + 1 < len(lines)
            and self.normalize_text(lines[index]) == self.normalize_text(title)
            and re.match(r"^\s*=+\s*$", lines[index + 1]) is not None
        ):
            del lines[index:index + 2]

            while index < len(lines) and lines[index].strip() == "":
                del lines[index]

            return "\n".join(lines)

        return content

    def extract_template_metadata(self, title):
        title = self.normalize_text(title)

        if " - " not in title:
            return {
                "code": title,
                "name": title,
            }

        code, name = title.split(" - ", 1)

        return {
            "code": self.normalize_text(code),
            "name": self.normalize_text(name),
        }

    def extract_document_metadata(self, title):
        return self.extract_template_metadata(title)

    def template_sort_key(self, value):
        text = self.normalize_text(value)
        match = re.search(r"ŞBL\.(\d+)", text)

        if match is None:
            return text

        return f"{text[:match.start()]}ŞBL.{int(match.group(1)):06d}{text[match.end():]}"

    def normalize_text(self, value):
        return unicodedata.normalize("NFC", str(value)).strip()

    def normalize_content(self, value):
        return unicodedata.normalize("NFC", str(value)).replace("\r\n", "\n").replace("\r", "\n")

    def build_folder_body(self):
        return "<p>Bu sayfa, alt dokümanların gruplanması amacıyla oluşturulmuştur.</p>"

    def build_body(self, node):
        return "<p></p>"
