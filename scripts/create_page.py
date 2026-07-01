from confluence_client import ConfluenceClient
from config import SPACE_KEY

ROOT_PAGE_ID = "137265781"

client = ConfluenceClient()

page = client.create_page(
    space_key=SPACE_KEY,
    parent_id=ROOT_PAGE_ID,
    title="00 - Genel Bilgiler",
    body="<p>Bu sayfa Python ile oluşturuldu.</p>",
)

print(page["id"])
print(page["title"])