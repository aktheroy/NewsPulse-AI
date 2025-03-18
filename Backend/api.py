from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

app = FastAPI()

class AnalysisRequest(BaseModel):
    company: str

# Dummy response data
dummy_response = {
    "Company": "Tesla",
    "Articles": [
        {
            "Title": "Tesla's New Model Breaks Sales Records",
            "Summary": "Tesla's latest EV sees record sales in Q3...",
            "Sentiment": "Positive",
            "Topics": ["Electric Vehicles", "Stock Market", "Innovation"]
        },
        {
            "Title": "Regulatory Scrutiny on Tesla's Self-Driving Tech",
            "Summary": "Regulators have raised concerns over Tesla’s self-driving software...",
            "Sentiment": "Negative",
            "Topics": ["Regulations", "Autonomous Vehicles"]
        }
    ],
    "Comparative Sentiment Score": {
        "Sentiment Distribution": {
            "Positive": 1,
            "Negative": 1,
            "Neutral": 0
        },
        "Coverage Differences": [
            {
                "Comparison": "Article 1 highlights Tesla's strong sales, while Article 2 discusses regulatory issues.",
                "Impact": "The first article boosts confidence in Tesla's market growth, while the second raises concerns about future regulatory hurdles."
            }
        ],
        "Topic Overlap": {
            "Common Topics": ["Electric Vehicles"],
            "Unique Topics in Article 1": ["Stock Market", "Innovation"],
            "Unique Topics in Article 2": ["Regulations", "Autonomous Vehicles"]
        }
    },
    "Final Sentiment Analysis": "Tesla’s latest news coverage is mostly positive. Potential stock growth expected.",
    "Audio": "/static/dummy_audio.wav"  # Create a dummy audio file for testing
}

@app.post("/analyze")
async def analyze(request: AnalysisRequest):
    # Dummy response for testing
    if request.company.strip() == "":
        raise HTTPException(status_code=400, detail="Company name required")
    
    # Simulate processing delay
    import time
    time.sleep(2)
    
    return dummy_response

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)