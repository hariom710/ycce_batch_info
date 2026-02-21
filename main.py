from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import pandas as pd
from fastapi import Request

# uvicorn main:app --reload --port 8080

# Initialize FastAPI app
app = FastAPI()

# Serve static files (CSS, JS, images)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Load Jinja2 templates for rendering HTML
templates = Jinja2Templates(directory="templates")

# Load student data from the Excel file
excel_file_path = 'students.xlsx'  # Path to your students.xlsx file
df = pd.read_excel(excel_file_path)

# Optionally, clean or preprocess data if needed
df['Students Full Name'] = df['Students Full Name'].str.lower()  # Standardize case for easy search
df['DoB'] = pd.to_datetime(df['DoB']).dt.strftime('%Y-%m-%d')  # Format DoB to remove time

class SearchResponse(BaseModel):
    suggestions: list

@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    """
    Serve the index.html page when visiting the root URL.
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/search")
async def search_students(query: str):
    """
    Endpoint to search students based on the query.
    """
    query = query.lower()  # Convert to lowercase for case-insensitive search
    # Search across all relevant columns
    suggestions = df[df.apply(lambda row: row.astype(str).str.contains(query).any(), axis=1)]['Students Full Name'].tolist()
    return {"suggestions": suggestions}

@app.get("/details/{name}")
async def student_details(name: str):
    """
    Endpoint to get the full details of the selected student.
    """
    name = name.lower()  # Standardize case
    student_data = df[df['Students Full Name'].str.lower() == name].iloc[0]  # Get the student by name
    if student_data.empty:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Return student data as a dictionary for easy rendering in frontend
    return student_data.to_dict()
