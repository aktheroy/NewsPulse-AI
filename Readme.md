# News Summarization & Sentiment Analysis Web App

## Project Overview
This web application extracts key details from multiple news articles related to a given company, performs sentiment analysis, conducts a comparative analysis, and generates a text-to-speech (TTS) output in Hindi. The tool allows users to input a company name and receive a structured sentiment report along with an audio summary.

## Features
- **News Extraction**: Scrapes at least 10 news articles using `BeautifulSoup`.
- **Sentiment Analysis**: Categorizes news articles as Positive, Negative, or Neutral using FinBERT.
- **Comparative Analysis**: Compares sentiment trends across articles.
- **Text-to-Speech (TTS)**: Converts summarized news to Hindi speech using `gTTS`.
- **User Interface**: Web-based UI built with Streamlit.

## Installation & Setup
### Prerequisites
- Python 3.10+
- Pip
- Hugging Face account (for deployment)

### Steps
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd news-summarization-app
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the backend API:
   ```bash
   uvicorn api:app --host 0.0.0.0 --port 8000
   ```
4. Run the Streamlit application:
   ```bash
   streamlit run app.py
   ```

## API Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/analyze` | `POST` | Fetches news articles, performs sentiment analysis, and generates comparative analysis & TTS |

### Example API Request
```json
{
    "company_name": "Tesla"
}
```

### Example API Response
```json
{
    "status": "success",
    "report": {
        "Company": "Tesla",
        "Articles": [
            {
                "Title": "Tesla's New Model Breaks Sales Records",
                "Summary": "Tesla's latest EV sees record sales in Q3...",
                "Sentiment": "Positive",
                "Topics": ["Electric Vehicles", "Stock Market", "Innovation"]
            }
        ],
        "Comparative Sentiment Score": {
            "Sentiment Distribution": {"Positive": 1, "Negative": 0, "Neutral": 0},
            "Coverage Differences": [],
            "Topic Overlap": {"Common Topics": ["Electric Vehicles"]}
        },
        "Final Sentiment Analysis": "Tesla’s latest news coverage is mostly positive.",
        "Audio": "Tesla_summary.mp3"
    }
}
```

## Models Used
- **Summarization**: Extracted via `BeautifulSoup`
- **Sentiment Analysis**: `FinBERT` (ProsusAI/finbert)
- **TTS**: `gTTS` for Hindi speech synthesis

## Deployment
1. Push your code to GitHub.
2. Deploy on Hugging Face Spaces:
   - Create a new Space.
   - Select `Streamlit` as the SDK.
   - Upload your repository files.
   - Set up dependencies (`requirements.txt`).
   - Run the app.
3. Provide the deployment link in the submission.

## Assumptions & Limitations
- The news scraping method only works with non-JS websites.
- Sentiment analysis may not be 100% accurate due to varying writing styles.
- TTS may not fully capture complex Hindi pronunciations.

## Folder Structure
```
/news-summarization-app
├── app.py  # Streamlit UI
├── api.py  # FastAPI backend
├── utils.py  # Utility functions for scraping, sentiment analysis, and TTS
├── requirements.txt  # Dependencies
├── README.md  # Documentation
```

## Future Improvements
- Support for additional languages in TTS.
- Advanced comparative analytics.
- More robust news extraction using NLP-based scraping.

## Author & Credits
- **Developer**: Arun Kumar Roy
- Credits to external libraries & APIs used.

