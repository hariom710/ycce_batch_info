import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
EXCEL_FILE_PATH = BASE_DIR / "students.xlsx"

# Render deployment settings
PORT = int(os.getenv("PORT", 8000))
HOST = os.getenv("HOST", "0.0.0.0")
