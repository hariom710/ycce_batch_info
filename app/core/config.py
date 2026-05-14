import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
EXCEL_FILE_PATH = BASE_DIR / "students.xlsx"
GOOGLE_SHEET_ID = os.getenv(
    "GOOGLE_SHEET_ID",
    "13k6CW19B9SBSlY0hqcsplM4LU1fORk2m9SocIM7YuRo",
)
GOOGLE_SHEET_EXPORT_URL = os.getenv(
    "GOOGLE_SHEET_EXPORT_URL",
    f"https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}/export?format=xlsx",
)

# Render deployment settings
PORT = int(os.getenv("PORT", 8000))
HOST = os.getenv("HOST", "0.0.0.0")
