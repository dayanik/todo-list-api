import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

db_name = os.getenv("DATABASE_URL", "db.sqlite3")

DATABASE_URL = f'sqlite+aiosqlite:///{BASE_DIR / db_name}'
