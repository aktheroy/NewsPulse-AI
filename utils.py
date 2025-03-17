import feedparser
from newspaper import Article
from bs4 import BeautifulSoup
from transformers import pipeline
import spacy
from collections import defaultdict
import random

# Initialize models
sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
nlp = spacy.load("en_core_web_sm")

def get_news_links(company, num_articles=10):
    """Fetch news URLs using Google News RSS feed"""
    rss_url = f"https://news.google.com/rss/search?q={company}"
    feed = feedparser.parse(rss_url)
    return [entry.link for entry in feed.entries[:num_articles]]

def scrape_article(url):
    """Extract article content using newspaper3k with BeautifulSoup fallback"""
    try:
        article = Article(url)
        article.download()
        article.parse()
        return {
            "title": article.title,
            "text": article.text,
            "published": article.publish_date,
            "url": url
        }
    except:
        # Fallback to BeautifulSoup
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            return {
                "title": soup.title.string if soup.title else "",
                "text": ' '.join(p.get_text() for p in soup.find_all('p')),
                "published": None,
                "url": url
            }
        except:
            return None

def analyze_sentiment(text):
    """Analyze sentiment with neutral threshold"""
    result = sentiment_analyzer(text[:512])[0]  # Truncate to model limit
    label = result['label'].replace("LABEL_", "").capitalize()
    score = result['score']
    
    # Add neutral classification
    if 0.4 <= score <= 0.6:
        return "Neutral"
    return label

def extract_topics(text):
    """Extract key topics using spaCy NER"""
    doc = nlp(text)
    entities = [ent.text for ent in doc.ents if ent.label_ in ['ORG', 'PRODUCT', 'GPE']]
    return list(set(entities))[:5]  # Return top 5 unique entities

def generate_comparative_analysis(articles):
    """Generate comparative analysis report"""
    # Sentiment distribution
    sentiment_counts = defaultdict(int)
    for article in articles:
        sentiment_counts[article['sentiment']] += 1
    
    # Topic analysis
    all_topics = defaultdict(int)
    for article in articles:
        for topic in article['topics']:
            all_topics[topic] += 1
    
    # Coverage differences
    comparisons = []
    if len(articles) >= 2:
        comparisons.append({
            "Comparison": f"{articles[0]['title']} focuses on {', '.join(articles[0]['topics'][:2])} "
                          f"while {articles[1]['title']} discusses {', '.join(articles[1]['topics'][:2])}",
            "Impact": "This contrast shows differing aspects of company coverage"
        })
    
    # Topic overlap analysis
    topic_counts = defaultdict(list)
    for idx, article in enumerate(articles):
        for topic in article['topics']:
            topic_counts[topic].append(idx+1)
    
    common_topics = [topic for topic, articles in topic_counts.items() if len(articles) > 1]
    unique_topics = {
        f"Article {i+1}": list(set(art['topics']) - set(common_topics))
        for i, art in enumerate(articles)
    }
    
    return {
        "Sentiment Distribution": dict(sentiment_counts),
        "Coverage Differences": comparisons,
        "Topic Overlap": {
            "Common Topics": common_topics,
            **unique_topics
        }
    }

def generate_full_report(company):
    """Generate complete analysis report"""
    # Step 1: News Extraction
    urls = get_news_links(company)
    articles = []
    
    for url in urls:
        article_data = scrape_article(url)
        if article_data and article_data['text']:
            # Step 2: Sentiment Analysis
            article_data['sentiment'] = analyze_sentiment(article_data['text'])
            # Step 3: Topic Extraction
            article_data['topics'] = extract_topics(article_data['text'])
            articles.append({
                "Title": article_data['title'],
                "Summary": ' '.join(article_data['text'].split()[:100]) + '...',  # Simple summary
                "Sentiment": article_data['sentiment'],
                "Topics": article_data['topics']
            })
    
    # Step 4: Comparative Analysis
    comparative = generate_comparative_analysis(articles)
    
    # Final sentiment conclusion
    dominant_sentiment = max(comparative['Sentiment Distribution'], 
                           key=comparative['Sentiment Distribution'].get)
    final_analysis = (
        f"{company}'s news coverage is predominantly {dominant_sentiment.lower()}. "
        f"Key topics include {', '.join(comparative['Topic Overlap']['Common Topics'][:3])}."
    )
    
    return {
        "Company": company,
        "Articles": articles[:10],  # Ensure max 10 articles
        "Comparative Sentiment Score": comparative,
        "Final Sentiment Analysis": final_analysis
    }

# Example usage
if __name__ == "__main__":
    report = generate_full_report("Tesla")
    print(report)