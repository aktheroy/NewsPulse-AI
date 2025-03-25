import requests, re
import time, base64
from io import BytesIO
from bs4 import BeautifulSoup
from newspaper import Article, Config
from transformers import BertTokenizer, BertForSequenceClassification, pipeline
from keybert import KeyBERT
from gtts import gTTS
from deep_translator import GoogleTranslator
from collections import defaultdict


class NewsAnalyzer:
    def __init__(self, company_name: str):
        self.company_name = company_name
        self.articles = []
        self.sentiment_distribution = {
            "Positive": 0, "Negative": 0, "Neutral": 0}

        # Newspaper3k configuration
        self.config = Config()
        self.config.request_timeout = 10
        self.config.browser_user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/91.0.4472.124 Safari/537.36"
        )

        # Load FinBERT Model
        self.tokenizer = BertTokenizer.from_pretrained('ProsusAI/finbert')
        self.model = BertForSequenceClassification.from_pretrained(
            'ProsusAI/finbert')
        self.nlp = pipeline("sentiment-analysis",
                            model=self.model, tokenizer=self.tokenizer)

        # Load KeyBERT Model
        self.kw_model = KeyBERT()

    def scrape_process(self):
        """Main method to perform complete news scraping and analysis"""
        urls = self._search_news()
        self._scrape_articles(urls)
        self._process_articles()
        analysis = self._generate_comparative_analysis()
        # Generate audio bytes directly
        audio_bytes = self._generate_audio(analysis["Final Sentiment Analysis"])
        analysis["Audio"] = audio_bytes  # Store bytes instead of filename
        
        return analysis

    def _search_news(self):
        base_url = "https://duckduckgo.com/html/"
        params = {"q": f"{self.company_name} news", "kl": "us-en"}
        headers = {"User-Agent": self.config.browser_user_agent}

        try:
            response = requests.get(base_url, headers=headers, params=params)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            urls = set()

            for link in soup.select("a.result__a"):
                href = link.get("href", "")
                match = re.search(r"(https?://[^\s\"']+)", href)
                if match:
                    url = match.group(1)
                    if "duckduckgo.com" not in url and not re.search(r"\.js$", url):
                        urls.add(url)

            return list(urls)[:10]
        except requests.RequestException as e:
            print(f"Search failed: {str(e)}")
            return []

    def _scrape_articles(self, urls):
        """Scrape and store articles with title, summary, and topics"""
        for url in urls:
            article_data = self._scrape_article(url)
            if article_data:
                self.articles.append(article_data)
                time.sleep(2)

    def _scrape_article(self, url):
        """Scrapes a single article and extracts title, summary, and topics"""
        try:
            article = Article(url, config=self.config)
            article.download()
            article.parse()
            article.nlp()
            topics = self._extract_topics(article.summary)
            return {
                "Title": article.title,
                "Summary": article.summary,
                "Content": article.text,
                "Topics": topics
            } if article.text else None
        except Exception as e:
            print(f"Failed to scrape {url}: {str(e)}")
            return None

    def _extract_topics(self, text):
        """Extracts key topics from text using KeyBERT"""
        keywords = self.kw_model.extract_keywords(
            text, keyphrase_ngram_range=(1, 2), stop_words='english', top_n=5)
        return [kw[0] for kw in keywords]

    def _process_articles(self):
        """Process each article for sentiment analysis"""
        for article in self.articles:
            sentiment = self._analyze_sentiment(article["Summary"][:512])
            article["Sentiment"] = sentiment
            self.sentiment_distribution[sentiment] += 1

    def _analyze_sentiment(self, text):
        """Determine text sentiment using FinBERT"""
        result = self.nlp(text)[0]
        label = result['label'].capitalize()
        return label if label in self.sentiment_distribution else "Neutral"

    def _generate_comparative_analysis(self):
        """Generates comparative analysis of the articles"""
        comparisons = []
        topic_sets = [set(article["Topics"]) for article in self.articles]
        common_topics = set.intersection(*topic_sets) if topic_sets else set()

        for i in range(len(self.articles) - 1):
            for j in range(i + 1, len(self.articles)):
                art1, art2 = self.articles[i], self.articles[j]
                comparisons.append({
                    "Comparison": f"{art1['Title']} vs {art2['Title']}",
                    "Impact": f"{art1['Title']} discusses {art1['Sentiment'].lower()} news, whereas {art2['Title']} focuses on {art2['Sentiment'].lower()} coverage."
                })

        topic_overlap = {
            "Common Topics": list(common_topics),
            "Unique Topics per Article": {art["Title"]: list(set(art["Topics"]) - common_topics) for art in self.articles}
        }

        return {
            "Company": self.company_name,
            "Articles": self.articles,
            "Comparative Sentiment Score": {
                "Sentiment Distribution": self.sentiment_distribution,
                "Coverage Differences": comparisons,
                "Topic Overlap": topic_overlap
            },
            "Final Sentiment Analysis": f"{self.company_name}'s latest news coverage is mostly {max(self.sentiment_distribution, key=self.sentiment_distribution.get).lower()}."
        }
    
    def _generate_audio(self, text):
        """Converts text to Hindi speech using in-memory buffer"""
        try:
            hindi_text = GoogleTranslator(source='auto', target='hi').translate(text)
            audio_buffer = BytesIO()
            tts = gTTS(text=hindi_text, lang='hi')
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            
            # Convert to base64 for JSON serialization
            return base64.b64encode(audio_buffer.read()).decode('utf-8')
        
        except Exception as e:
            print(f"Audio generation failed: {str(e)}")
            return None