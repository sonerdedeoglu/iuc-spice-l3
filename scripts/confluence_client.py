import requests
from requests.auth import HTTPBasicAuth

from config import (
    CONFLUENCE_URL,
    USERNAME,
    PASSWORD,
)


class ConfluenceClient:

    def __init__(self):
        self.base_url = CONFLUENCE_URL
        self.auth = HTTPBasicAuth(USERNAME, PASSWORD)

    def get(self, path, params=None):
        response = requests.get(
            f"{self.base_url}{path}",
            params=params,
            auth=self.auth,
            verify=False,
            timeout=30,
        )

        response.raise_for_status()

        return response.json()

    def post(self, path, payload):
        response = requests.post(
            f"{self.base_url}{path}",
            json=payload,
            auth=self.auth,
            verify=False,
            timeout=30,
            headers={
                "Content-Type": "application/json",
            },
        )

        response.raise_for_status()

        return response.json()

    def find_page(self, space_key, title):
        return self.get(
            "/rest/api/content",
            {
                "spaceKey": space_key,
                "title": title,
                "expand": "version",
            },
        )

    def create_page(self, space_key, parent_id, title, body):
        payload = {
            "type": "page",
            "title": title,
            "space": {
                "key": space_key,
            },
            "ancestors": [
                {
                    "id": str(parent_id),
                }
            ],
            "body": {
                "storage": {
                    "value": body,
                    "representation": "storage",
                }
            },
        }

        return self.post(
            "/rest/api/content",
            payload,
        )

    def add_label(self, page_id, label):
        payload = [
            {
                "prefix": "global",
                "name": label,
            }
        ]

        return self.post(
            f"/rest/api/content/{page_id}/label",
            payload,
        )

    def get_children(self, page_id):
        return self.get(
            f"/rest/api/content/{page_id}/child/page",
            {
                "expand": "version",
                "limit": 1000,
            },
        )
