import requests
from requests.auth import HTTPBasicAuth

from config import (
    CONFLUENCE_URL,
    USERNAME,
    PASSWORD,
)

print(f"URL      : {CONFLUENCE_URL}")
print(f"Username : {USERNAME}")

url = f"{CONFLUENCE_URL}/rest/api/space"

try:
    response = requests.get(
        url,
        auth=HTTPBasicAuth(USERNAME, PASSWORD),
        timeout=30,
        verify=False,
    )

    print(f"HTTP Status : {response.status_code}")
    print(response.text[:500])

except Exception as ex:
    print(ex)