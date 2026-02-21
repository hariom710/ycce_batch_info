from pydantic import BaseModel
from typing import Optional, Dict, Any

class StudentResponse(BaseModel):
    student_data: Dict[str, Any]

class SearchResponse(BaseModel):
    suggestions: list[str]
    count: int
