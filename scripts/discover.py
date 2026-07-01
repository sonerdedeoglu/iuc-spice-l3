from confluence_client import ConfluenceClient
from config import SPACE_KEY, ROOT_PAGE

client = ConfluenceClient()

page = client.find_page(
    SPACE_KEY,
    ROOT_PAGE,
)

print(page)