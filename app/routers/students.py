from fastapi import APIRouter, HTTPException, Query
from typing import List
from app.models.student import SearchResponse, StudentResponse
from app.utils.data_loader import student_data

router = APIRouter(prefix="/api", tags=["students"])

@router.get("/search", response_model=SearchResponse)
async def search_students(
    query: str = Query(..., min_length=1, description="Search query for student names")
) -> SearchResponse:
    """
    Search for students by name or partial name.
    Returns up to 10 matching student names.
    """
    try:
        if not student_data.is_data_loaded():
            raise HTTPException(
                status_code=503, 
                detail="Student data is not available. Please check the data file."
            )
        
        suggestions = student_data.search_students(query)
        
        return SearchResponse(
            suggestions=suggestions,
            count=len(suggestions)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while searching: {str(e)}"
        )

@router.get("/student/{name}", response_model=StudentResponse)
async def get_student_details(name: str) -> StudentResponse:
    """
    Get detailed information for a specific student by name.
    """
    try:
        if not student_data.is_data_loaded():
            raise HTTPException(
                status_code=503,
                detail="Student data is not available. Please check the data file."
            )
        
        student_info = student_data.get_student_by_name(name)
        
        if not student_info:
            raise HTTPException(
                status_code=404,
                detail=f"Student '{name}' not found"
            )
        
        return StudentResponse(student_data=student_info)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while fetching student details: {str(e)}"
        )
