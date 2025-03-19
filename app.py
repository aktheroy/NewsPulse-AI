import streamlit as st
import requests
import time
import plotly.graph_objects as go

# Set page config first
st.set_page_config(
    page_title="News Analyzer",
    page_icon="🎓",
    layout="wide"
)

# Initialize session state
if "selected_company" not in st.session_state:
    st.session_state.selected_company = None
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = {}
if "selected_sentiment" not in st.session_state:
    st.session_state.selected_sentiment = None

def create_gauge(value, title, color):
    """Create a Plotly gauge chart with consistent styling"""
    return go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=value,
            number={"suffix": "%"},
            domain={"x": [0, 1], "y": [0, 1]},
            title={"text": title},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "darkgray"},
                "bar": {"color": color},
                "bgcolor": "white",
                "borderwidth": 2,
                "bordercolor": "gray",
                "steps": [{"range": [0, 100], "color": "lightgray"}]
            }
        )
    ).update_layout(margin=dict(t=30, b=10), height=250)

def calculate_sentiment_stats(articles):
    """Calculate sentiment statistics from articles"""
    pos = sum(1 for a in articles if a.get("Sentiment") == "Positive")
    neg = sum(1 for a in articles if a.get("Sentiment") == "Negative")
    neu = sum(1 for a in articles if a.get("Sentiment") == "Neutral")
    total = len(articles)
    pos_pct = (pos / total) * 100 if total > 0 else 0
    neg_pct = (neg / total) * 100 if total > 0 else 0
    neu_pct = (neu / total) * 100 if total > 0 else 0
    return pos_pct, neg_pct, neu_pct

def render_article_list(articles):
    """Render the list of articles"""
    st.subheader("📰 Analyzed Articles")
    for article in articles:
        with st.expander(f"{article.get('Title', 'Untitled')} ({article.get('Sentiment', 'Unknown')})"):
            st.write(article.get("Summary", "No summary available"))
            topics = article.get("Topics", [])
            if topics:
                st.caption(f"Topics: {', '.join(topics)}")

def render_left_column():
    st.subheader("🔍 Select Company")
    companies = [
        "Tesla", "Apple", "Microsoft", "Google",
        "Amazon", "Meta", "Netflix", "NVIDIA",
        "Samsung", "Sony", "Toyota", "Intel",
        "IBM", "Facebook", "Twitter", "Alphabet",
        "Ford", "General Motors", "IBM","Boeing", 
        "SpaceX","Alibaba","Tencent","Baidu","JD.com",
        "Huawei","Xiaomi","NIO","BYD","Volkswagen",
        "BMW","Mercedes-Benz","Audi","Porsche","Ford",
        "General Motors","Nissan","Honda","Hyundai",
        "Kia","Renault","Peugeot","Fiat Chrysler",
        "Ferrari","Lamborghini","Maserati","McLaren",
        "Rolls-Royce","Bentley","Bugatti","Jaguar",
        "Land Rover","Mini","Lotus","Aston Martin",
        "tata","Mahindra","Maruti Suzuki","Hero MotoCorp",
        "Bajaj Auto","TVS Motor","Royal Enfield","Yamaha",
        "Suzuki","Kawasaki","Harley-Davidson","Ducati",
        "KTM","BMW Motorrad","Triumph","Aprilia",
    ]
    selected_company = st.selectbox("Type or select company:", options=companies, index=None, placeholder="Search companies...", key="company_select")
    custom_company = st.text_input("Or enter a different company:", placeholder="Type custom company name...", key="custom_company")
    company_name = custom_company if custom_company else selected_company
    if st.button("Analyze News 🧠", type="primary"):
        handle_company_selection(company_name)
    st.markdown("---")
    st.subheader("🎧 Hindi Summary")
    if st.session_state.analysis_result.get("Audio"):
        st.audio(st.session_state.analysis_result["Audio"], format="audio/mpeg")
    else:
        st.warning("No audio available yet")

def handle_company_selection(company):
    if not company:
        st.warning("Please select or enter a company first!")
        return
    with st.spinner("Fetching and analyzing news articles..."):
        try:
            response = requests.post("http://localhost:8000/analyze", json={"company_name": company})
            if response.status_code != 200:
                st.error(f"API Error: {response.status_code} - {response.text}")
                return
            result = response.json().get("report", {})
            st.session_state.analysis_result = result
            st.session_state.selected_company = company
        except requests.exceptions.RequestException as e:
            st.error(f"Error connecting to API: {str(e)}")
            
def calculate_sentiment_stats(articles):
    total = len(articles)
    if total == 0:
        return 0, 0, 0

    sentiments = [a.get("Sentiment", "Neutral") for a in articles]
    pos = sentiments.count("Positive")
    neg = sentiments.count("Negative")
    neu = sentiments.count("Neutral")

    return (
        round((pos / total) * 100, 1),
        round((neg / total) * 100, 1),
        round((neu / total) * 100, 1)
    )


def render_right_column():
    if not st.session_state.selected_company:
        st.info("👈 Select a company and click 'Analyze News' to begin")
        return
    result = st.session_state.analysis_result
    articles = result.get("Articles", [])
    st.subheader(f" Analysis Report: {st.session_state.selected_company}")
    pos_pct, neg_pct, neu_pct = calculate_sentiment_stats(articles)
    render_gauges(pos_pct, neg_pct, neu_pct)
    render_filter_controls(articles)
    filtered_articles = filter_articles_by_sentiment(articles, st.session_state.selected_sentiment)
    render_article_list(filtered_articles)
    st.subheader("Comparative Analysis")
    with st.expander("Show Detailed Analysis"):
        st.markdown("#### Sentiment Distribution")
        st.write(result.get("Comparative Sentiment Score", {}).get("Sentiment Distribution", {}))
        st.markdown("#### Coverage Differences")
        comparisons = result.get("Comparative Sentiment Score", {}).get("Coverage Differences", [])
        for item in comparisons:
            st.markdown(f"- **{item.get('Comparison', '')}**")
            st.markdown(f"  *Impact*: {item.get('Impact', '')}")
        st.markdown("#### Topic Analysis")
        st.write(result.get("Comparative Sentiment Score", {}).get("Topic Overlap", {}))

def render_filter_controls(articles):
    if not articles:
        return
    sentiments = [a.get("Sentiment", "Neutral") for a in articles]
    pos = sentiments.count("Positive")
    neg = sentiments.count("Negative")
    neu = sentiments.count("Neutral")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button(f"🟢 Positive ({pos})", use_container_width=True):
            st.session_state.selected_sentiment = "Positive"
    with col2:
        if st.button(f"🔴 Show Negative ({neg})", use_container_width=True):
            st.session_state.selected_sentiment = "Negative"
    with col3:
        if st.button(f"🔵 Show Neutral ({neu})", use_container_width=True):
            st.session_state.selected_sentiment = "Neutral"
    if st.session_state.get("selected_sentiment"):
        if st.button("Clear Filters 🧹", use_container_width=True):
            st.session_state.selected_sentiment = None

def filter_articles_by_sentiment(articles, sentiment):
    """Filter articles based on the selected sentiment"""
    if not sentiment:
        return articles
    return [article for article in articles if article.get("Sentiment") == sentiment]

def render_gauges(pos_pct, neg_pct, neu_pct):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.plotly_chart(create_gauge(pos_pct, "Positive Sentiment", "#4CAF50"), use_container_width=True)
    with col2:
        st.plotly_chart(create_gauge(neg_pct, "Negative Sentiment", "#f44336"), use_container_width=True)
    with col3:
        st.plotly_chart(create_gauge(neu_pct, "Neutral Sentiment", "#2196F3"), use_container_width=True)

def main():
    st.title("Company News Sentiment Analyzer")
    left_col, right_col = st.columns([0.35, 0.65])
    with left_col:
        render_left_column()
    with right_col:
        render_right_column()

if __name__ == "__main__":
    main()
