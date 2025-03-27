from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from Backend.utils import NewsAnalyzer
import uvicorn

app = FastAPI()


class RequestModel(BaseModel):
    company_name: str


@app.post("/analyze")
async def analyze_news(request: RequestModel):
    try:
        analyzer = NewsAnalyzer(request.company_name)
        report = analyzer.scrape_process()
        return {"status": "success", "report": report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
