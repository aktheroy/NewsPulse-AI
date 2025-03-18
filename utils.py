import requests
from bs4 import BeautifulSoup
from newspaper import Article, Config
import time
import re
import json
from textblob import TextBlob
import yake
from gtts import gTTS
from deep_translator import GoogleTranslator
import os

class NewsAnalyzer:
    def __init__(self, company_name: str):
        self.company_name = company_name
        self.articles = []
        self.summarized_articles = []
        self.sentiment_distribution = {"Positive": 0, "Negative": 0, "Neutral": 0}
        
        # Newspaper3k configuration
        self.config = Config()
        self.config.request_timeout = 10
        self.config.browser_user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/89.0.4389.82 Safari/537.36"
        )
        
        # YAKE keyword extractor
        self.kw_extractor = yake.KeywordExtractor(lan="en", n=1, top=3)

    def scrape_news(self):
        """Main method to perform complete news scraping and analysis"""
        self._scrape_articles()
        self._process_articles()
        return self.generate_report()

    def _search_news(self) -> list[str]:
        """Search DuckDuckGo for news articles"""
        base_url = "https://duckduckgo.com/html/"
        params = {"q": f"{self.company_name} news", "kl": "us-en"}
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/91.0.4472.124 Safari/537.36"
        }

        try:
            response = requests.get(base_url, headers=headers, params=params)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            urls = set()

            for link in soup.select("a.result__a"):
                href = link.get("href", "")
                if match := re.search(r"(https?://[^\s\"']+)", href):
                    url = match.group(1)
                    if "duckduckgo.com" not in url:
                        urls.add(url)

            return list(urls)[:10]

        except requests.RequestException as e:
            print(f"Search failed: {str(e)}")
            return []

    def _scrape_article(self, url: str) -> dict:
        """Scrape individual article content"""
        article = Article(url, config=self.config)
        try:
            article.download()
            article.parse()
            article.nlp()
            return {
                "title": article.title,
                "summary": article.summary,
                "full_text": article.text,
                "url": url,
                "date": article.publish_date.strftime("%Y-%m-%d") if article.publish_date else None,
                "keywords": article.keywords,
                "authors": article.authors
            }
        except Exception as e:
            print(f"Scraping failed for {url}: {str(e)}")
            return {}

    def _scrape_articles(self):
        """Scrape and store articles"""
        urls = self._search_news()
        for url in urls:
            if article := self._scrape_article(url):
                self.articles.append(article)
                time.sleep(2)
        self.articles = self.articles[:10]

    def _analyze_sentiment(self, text: str) -> str:
        """Determine text sentiment"""
        analysis = TextBlob(text)
        if analysis.sentiment.polarity > 0.1:
            return "Positive"
        elif analysis.sentiment.polarity < -0.1:
            return "Negative"
        return "Neutral"

    def _process_articles(self):
        """Process all scraped articles for sentiment and topics"""
        for article in self.articles:
            title = article.get("title", "No Title")
            summary = article.get("summary", "No Summary")
            sentiment = self._analyze_sentiment(summary)
            topics = [kw[0] for kw in self.kw_extractor.extract_keywords(summary)]

            self.sentiment_distribution[sentiment] += 1
            self.summarized_articles.append({
                "Title": title,
                "Summary": summary,
                "Sentiment": sentiment,
                "Topics": topics
            })

    def _generate_comparisons(self) -> tuple:
        """Generate article comparisons and topic analysis"""
        comparisons = []
        for i in range(len(self.summarized_articles) - 1):
            for j in range(i + 1, len(self.summarized_articles)):
                art1 = self.summarized_articles[i]
                art2 = self.summarized_articles[j]
                comparisons.append({
                    "Comparison": f"{art1['Title']} vs {art2['Title']}",
                    "Sentiment": f"{art1['Sentiment']} vs {art2['Sentiment']}",
                    "Topics": f"{art1['Topics']} vs {art2['Topics']}"
                })

        topics = [set(art["Topics"]) for art in self.summarized_articles]
        common_topics = set.intersection(*topics) if topics else []
        return comparisons, {
            "common_topics": list(common_topics),
            "unique_topics": {art["Title"]: art["Topics"] for art in self.summarized_articles}
        }

    def _generate_hindi_audio(self, text: str) -> str:
        """Generate Hindi audio from text"""
        try:
            translated = GoogleTranslator(source='auto', target='hi').translate(text)
            tts = gTTS(translated, lang='hi')
            filename = f"{self.company_name}_summary.mp3"
            tts.save(filename)
            return filename
        except Exception as e:
            print(f"Audio generation error: {str(e)}")
            return ""

    def generate_report(self) -> dict:
        """Generate final analysis report with audio"""
        total_articles = len(self.summarized_articles)
        comparisons, topics = self._generate_comparisons()
        
        # Generate summary text
        sentiment_text = (f"Found {total_articles} articles. "
                         f"Positive: {self.sentiment_distribution['Positive']}, "
                         f"Negative: {self.sentiment_distribution['Negative']}, "
                         f"Neutral: {self.sentiment_distribution['Neutral']}.")

        # Generate audio
        audio_file = self._generate_hindi_audio(sentiment_text)

        return {
            "company": self.company_name,
            "summary": sentiment_text,
            "sentiment_distribution": self.sentiment_distribution,
            "comparative_analysis": comparisons,
            "topic_analysis": topics,
            "audio_file": audio_file,
            "articles": self.summarized_articles
        }
    
