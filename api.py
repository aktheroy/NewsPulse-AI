from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uuid
import json
import os
from utils import NewsAnalyzer 


class CompanyRequest(BaseModel):
    company_name: str

app = FastAPI(title="News Sentiment Analysis API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for analysis tasks
tasks = {}

@app.post("/analyze", status_code=status.HTTP_202_ACCEPTED)
async def start_analysis(request: CompanyRequest):
    """Endpoint to initiate news analysis for a company"""
    try:
        task_id = str(uuid.uuid4())
        analyzer = NewsAnalyzer(request.company_name)
        
        # Store task immediately
        tasks[task_id] = {
            "status": "pending",
            "company": request.company_name,
            "result": None
        }
        
        # Run analysis (consider using background tasks for production)
        report = analyzer.scrape_news()
        
        # Update task status
        tasks[task_id] = {
            "status": "completed",
            "company": request.company_name,
            "result": report
        }
        
        return {"task_id": task_id, "status": "Analysis started"}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )

@app.get("/results/{task_id}")
async def get_results(task_id: str):
    """Endpoint to retrieve analysis results"""
    task = tasks.get(task_id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    if task["status"] == "pending":
        return JSONResponse(
            status_code=status.HTTP_202_ACCEPTED,
            content={"status": "Analysis in progress"}
        )
    
    return {
        "status": "completed",
        "company": task["company"],
        "report": task["result"]
    }

@app.get("/audio/{task_id}")
async def get_audio(task_id: str):
    """Endpoint to retrieve generated audio file"""
    task = tasks.get(task_id)
    
    if not task or task["status"] != "completed":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found or not complete"
        )
    
    audio_path = task["result"].get("audio_file")
    
    if not audio_path or not os.path.exists(audio_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audio file not available"
        )
    
    return FileResponse(
        audio_path,
        media_type="audio/mpeg",
        filename=f"{task['company']}_analysis.mp3"
    )

@app.get("/status")
async def health_check():
    """Service health check endpoint"""
    return {"status": "ok", "version": "1.0.0"}