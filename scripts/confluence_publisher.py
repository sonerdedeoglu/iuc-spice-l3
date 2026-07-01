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

    def ensure_label(self, page_id, label):
        try:
            self.client.add_label(page_id, label)
        except HTTPError as ex:
            if ex.response is None:
                raise

            if ex.response.status_code not in (400, 409):
                raise

    def build_body(self, node):
        return "<p></p>"
