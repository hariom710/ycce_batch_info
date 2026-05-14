from fastapi import APIRouter, HTTPException, Query
from app.models.student import SearchResponse, StudentResponse
from app.utils.data_loader import clean_student_record, load_data

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
        df = load_data()
        if df.empty:
            raise HTTPException(
                status_code=503, 
                detail="Student data is not available. Please check the data file."
            )
        
        query = query.lower().strip()
        mask = df['search_text'].str.contains(query, na=False, regex=False)
        suggestions = df[mask]['Students Full Name'].head(10).tolist()
        
        return SearchResponse(
            suggestions=suggestions,
            count=len(suggestions)
        )
        
    except HTTPException:
        raise
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
        df = load_data()
        if df.empty:
            raise HTTPException(
                status_code=503,
                detail="Student data is not available. Please check the data file."
            )
        
        name = name.lower().strip()
        student_rows = df[df['Students Full Name'] == name]
        
        if student_rows.empty:
            raise HTTPException(
                status_code=404,
                detail=f"Student '{name}' not found"
            )

        student_info = clean_student_record(student_rows.iloc[0].to_dict())
        
        return StudentResponse(student_data=student_info)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while fetching student details: {str(e)}"
        )
