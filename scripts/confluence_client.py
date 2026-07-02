import warnings

warnings.filterwarnings(
    "ignore",
    message="urllib3 v2 only supports OpenSSL*",
    category=Warning,
    module="urllib3",
)

import requests
import urllib3
from requests.auth import HTTPBasicAuth

from config import (
    CONFLUENCE_URL,
    USERNAME,
    PASSWORD,
)


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

try:
    warnings.filterwarnings(
        "ignore",
        category=urllib3.exceptions.NotOpenSSLWarning,
    )
except AttributeError:
    pass


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

        try:
            response.raise_for_status()
        except requests.HTTPError:
            print("HTTP method: POST")
            print(f"Request URL: {response.url}")
            print(f"Status code: {response.status_code}")
            print(response.text)
            raise

        return response.json()

    def put(self, path, payload):
        response = requests.put(
            f"{self.base_url}{path}",
            json=payload,
            auth=self.auth,
            verify=False,
            timeout=30,
            headers={
                "Content-Type": "application/json",
            },
        )

        try:
            response.raise_for_status()
        except requests.HTTPError:
            print("HTTP method: PUT")
            print(f"Request URL: {response.url}")
            print(f"Status code: {response.status_code}")
            print(response.text)
            raise

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

    def get_page(self, page_id):
        return self.get(
            f"/rest/api/content/{page_id}",
            {
                "expand": "version,body.storage",
            },
        )

    def update_page(self, page_id, space_key, title, body, version_number):
        payload = {
            "id": str(page_id),
            "type": "page",
            "title": title,
            "space": {
                "key": space_key,
            },
            "body": {
                "storage": {
                    "value": body,
                    "representation": "storage",
                }
            },
            "version": {
                "number": version_number,
            },
        }

        return self.put(
            f"/rest/api/content/{page_id}",
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
