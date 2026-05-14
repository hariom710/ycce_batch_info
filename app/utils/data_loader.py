import pandas as pd
import logging
from typing import Optional
from app.core.config import EXCEL_FILE_PATH, GOOGLE_SHEET_EXPORT_URL

logger = logging.getLogger(__name__)

class StudentDataManager:
    def __init__(self):
        self.df: Optional[pd.DataFrame] = None
        self._load_data()
    
    def _load_data(self) -> None:
        """Load and preprocess student data from Google Sheets or local Excel file."""
        try:
            self.df = self._read_student_data()
            
            # Preprocess data
            self.df['Students Full Name'] = self.df['Students Full Name'].str.lower().str.strip()
            self.df['DoB'] = pd.to_datetime(self.df['DoB'], errors='coerce').dt.strftime('%Y-%m-%d')
            
            # Create search index for faster lookups
            self.df['search_text'] = self.df.apply(
                lambda row: ' '.join([str(val).lower() for val in row.values if pd.notna(val)]), 
                axis=1
            )
            
            logger.info(f"Loaded {len(self.df)} student records")
            
        except Exception as e:
            logger.error(f"Error loading student data: {e}")
            self.df = pd.DataFrame()

    def _read_student_data(self) -> pd.DataFrame:
        """Read student records from the configured Google Sheet, then local fallback."""
        try:
            logger.info("Loading student data from Google Sheet...")
            return pd.read_excel(GOOGLE_SHEET_EXPORT_URL, sheet_name=0)
        except Exception as e:
            logger.warning(f"Could not load Google Sheet data: {e}")

        if not EXCEL_FILE_PATH.exists():
            logger.error(f"Excel file not found: {EXCEL_FILE_PATH}")
            return pd.DataFrame()

        logger.info(f"Loading student data from local file: {EXCEL_FILE_PATH}")
        return pd.read_excel(EXCEL_FILE_PATH)
    
    def search_students(self, query: str, limit: int = 10) -> list[str]:
        """Search students by name with optimized filtering."""
        if self.df.empty or not query:
            return []
        
        query = query.lower().strip()
        
        # Use vectorized string operations for better performance
        mask = self.df['search_text'].str.contains(query, na=False, regex=False)
        results = self.df[mask]['Students Full Name'].head(limit).tolist()
        
        return results
    
    def get_student_by_name(self, name: str) -> Optional[dict]:
        """Get full student details by name."""
        if self.df.empty or not name:
            return None
        
        name = name.lower().strip()
        student_rows = self.df[self.df['Students Full Name'] == name]
        
        if student_rows.empty:
            return None
        
        student = student_rows.iloc[0].to_dict()
        student.pop('search_text', None)

        return {
            key: self._clean_value(value)
            for key, value in student.items()
        }

    def _clean_value(self, value):
        """Convert spreadsheet empty values into JSON-safe values."""
        if pd.isna(value):
            return None
        if isinstance(value, str):
            return value.strip()
        return value
    
    def is_data_loaded(self) -> bool:
        """Check if data is successfully loaded."""
        return not self.df.empty

# Global instance
student_data = StudentDataManager()
