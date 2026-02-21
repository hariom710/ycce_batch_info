import pandas as pd
import logging
from pathlib import Path
from typing import Optional
from app.core.config import EXCEL_FILE_PATH

logger = logging.getLogger(__name__)

class StudentDataManager:
    def __init__(self):
        self.df: Optional[pd.DataFrame] = None
        self._load_data()
    
    def _load_data(self) -> None:
        """Load and preprocess student data from Excel file."""
        try:
            if not EXCEL_FILE_PATH.exists():
                logger.error(f"Excel file not found: {EXCEL_FILE_PATH}")
                self.df = pd.DataFrame()
                return
            
            self.df = pd.read_excel(EXCEL_FILE_PATH)
            
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
        
        # Return the first match as dictionary
        return student_rows.iloc[0].to_dict()
    
    def is_data_loaded(self) -> bool:
        """Check if data is successfully loaded."""
        return not self.df.empty

# Global instance
student_data = StudentDataManager()
