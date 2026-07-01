from pathlib import Path
from dotenv import load_dotenv
import os
import yaml

ROOT = Path(__file__).resolve().parent.parent

load_dotenv(ROOT / ".env")

with open(ROOT / "spice.yaml", "r", encoding="utf-8") as f:
    CONFIG = yaml.safe_load(f)

CONFLUENCE_URL = os.getenv("CONFLUENCE_URL")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

SPACE_KEY = CONFIG["confluence"]["space"]
ROOT_PAGE = CONFIG["confluence"]["root_page"]