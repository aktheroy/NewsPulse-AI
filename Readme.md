# NewsPulse AI

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-orange)
![FastAPI](https://img.shields.io/badge/FastAPI-0.95%2B-green)
![HuggingFace](https://img.shields.io/badge/Deployed-HuggingFace_Spaces-yellow)

A web application that analyzes news sentiment for companies and generates Hindi audio summaries.

## Features

- 🗞️ News extraction from 10+ sources
- 📊 Sentiment analysis (Positive/Negative/Neutral)
- 🔍 Comparative news coverage analysis
- 🔊 text-to-speech summary
- 📈 Interactive visualizations
- 🌐 API-driven architecture

## 🌟 Demo
https://github.com/user-attachments/assets/3242518f-9cb6-4095-82c3-c00e824cba4d

## Installation

```bash
git clone https://github.com/aktheroy/news-analyzer.git
cd news-analyzer

# Install backend dependencies
pip install -r requirements.txt

## Requirements

## API Development

### Endpoints
- `POST /analyze`
  ```json
  {
    "company_name": "Tesla"
  }
  ```

### Example Usage
```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{"company_name": "Tesla"}'
```

## Deployment

1. **Hugging Face Spaces Setup**
   - Create new Space with Docker template
   - Minimum hardware: CPU Basic
   - Add required files:
     - `Dockerfile`
     - `frontend/`
     - `backend/`
     - `requirements.txt`

2. **Environment Variables**
   ```env
   NEWS_API_TIMEOUT=10
   TTS_LANGUAGE=hi
   ```

## Usage

1. Start backend:
```bash
uvicorn api:app --reload
```

2. Start frontend:
```bash
streamlit run app.py
```
## Documentation

### Model Architecture
| Component          | Technology Used       |
|--------------------|-----------------------|
| News Extraction    | BeautifulSoup         |
| Sentiment Analysis | FinBERT               |
| Topic Extraction   | KeyBERT               |
| summarization      | *******               |
| Text-to-Speech     | ****                  |

### Assumptions
- English news articles only
- DuckDuckGo as primary news source
- Limited to 10 recent articles

### Limitations
- News availability depends on search results
- Translation accuracy varies
- Real-time news might not be immediate

## Evaluation Metrics

| Metric       | Target                          |
|--------------|---------------------------------|
| Accuracy     | 85% sentiment classification    |
| Latency      | <10s response time              |
| Scalability  | 50+ concurrent requests         |

## Submission

- GitHub Repository: [news-analyzer](https://github.com/aktheroy/news-analyzer)
- HuggingFace Space: [live-demo](https://huggingface.co/spaces/aktheroy/NewsPulse-AI)

## License

[MIT License](LICENSE)

---

**Note**: This application is for educational purposes only. News data accuracy depends on third-party sources.

For support, contact [aktheroy@gmail.com](mailto:aktheroy@gmail.com)
