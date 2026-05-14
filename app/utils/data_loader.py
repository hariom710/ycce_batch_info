import logging
import time
from threading import Lock

import pandas as pd

from app.core.config import EXCEL_FILE_PATH, GOOGLE_SHEET_EXPORT_URL

logger = logging.getLogger(__name__)

CACHE_DURATION = 300

_cached_df = pd.DataFrame()
_cache_loaded_at = 0.0
_cache_lock = Lock()


def process_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare spreadsheet data for searching and API responses."""
    if df.empty:
        return pd.DataFrame()

    processed_df = df.copy()
    processed_df["Students Full Name"] = (
        processed_df["Students Full Name"].astype(str).str.lower().str.strip()
    )
    processed_df["DoB"] = pd.to_datetime(
        processed_df["DoB"],
        errors="coerce",
    ).dt.strftime("%Y-%m-%d")

    processed_df["search_text"] = processed_df.apply(
        lambda row: " ".join(
            [str(value).lower() for value in row.values if pd.notna(value)]
        ),
        axis=1,
    )

    return processed_df


def fetch_data() -> pd.DataFrame:
    """Fetch student data from Google Sheets first, then local Excel fallback."""
    try:
        logger.info("Loading student data from Google Sheet...")
        return pd.read_excel(GOOGLE_SHEET_EXPORT_URL, sheet_name=0)
    except Exception as e:
        logger.warning(f"Could not load Google Sheet data: {e}")

    if not EXCEL_FILE_PATH.exists():
        logger.error(f"Excel file not found: {EXCEL_FILE_PATH}")
        return pd.DataFrame()

    try:
        logger.info(f"Loading student data from local file: {EXCEL_FILE_PATH}")
        return pd.read_excel(EXCEL_FILE_PATH)
    except Exception as e:
        logger.error(f"Could not load local Excel data: {e}")
        return pd.DataFrame()


def load_data() -> pd.DataFrame:
    """Return cached data, refreshing it when the cache expires."""
    global _cached_df, _cache_loaded_at

    now = time.time()
    if not _cached_df.empty and now - _cache_loaded_at < CACHE_DURATION:
        return _cached_df

    with _cache_lock:
        now = time.time()
        if not _cached_df.empty and now - _cache_loaded_at < CACHE_DURATION:
            return _cached_df

        try:
            df = process_dataframe(fetch_data())
        except Exception as e:
            logger.error(f"Error processing student data: {e}")
            df = pd.DataFrame()

        if df.empty and not _cached_df.empty:
            logger.warning("Data refresh failed. Using previous cached data.")
            return _cached_df

        _cached_df = df
        _cache_loaded_at = now
        logger.info(f"Loaded {len(_cached_df)} student records")

        return _cached_df


def clean_value(value):
    """Convert spreadsheet empty values into JSON-safe values."""
    if pd.isna(value):
        return None
    if isinstance(value, str):
        return value.strip()
    return value


def clean_student_record(student: dict) -> dict:
    """Remove internal fields and clean values before returning JSON."""
    student.pop("search_text", None)

    return {
        key: clean_value(value)
        for key, value in student.items()
    }
