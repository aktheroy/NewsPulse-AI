import streamlit as st
import random
import plotly.graph_objects as go
from typing import List, Dict, Tuple, Union

COMPANIES = [
    "Tesla", "Apple", "Microsoft", "Google",
    "Amazon", "Meta", "Netflix", "NVIDIA",
    "Samsung", "Sony", "Toyota", "Intel"
]

TOPICS = ["Finance", "Technology", "Regulation", "Innovation"]
SAMPLE_ARTICLE_COUNT = 10

# Set page config first (PEP8: imports first, then code)
st.set_page_config(
    page_title="News Analyzer",
    page_icon="📈",
    layout="wide"
)

# Initialize session state
if "selected_company" not in st.session_state:
    st.session_state.selected_company = None
if "articles" not in st.session_state:
    st.session_state.articles = []
if "selected_sentiment" not in st.session_state:
    st.session_state.selected_sentiment = None


def create_gauge(value: float, title: str, color: str) -> go.Figure:
    """Create a Plotly gauge chart with consistent styling.
    
    Args:
        value (float): Percentage value to display
        title (str): Chart title
        color (str): Color code for the gauge
        
    Returns:
        plotly.graph_objs._figure.Figure: Configured gauge figure
    """
    return go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=value,
            number={"suffix": "%"},
            domain={"x": [0, 1], "y": [0, 1]},
            title={"text": title},
            gauge={
                "axis": {
                    "range": [0, 100],
                    "tickwidth": 1,
                    "tickcolor": "White",

                },
                "bar": {"color": color},
                "bgcolor": "white",
                "borderwidth": 1,
                "bordercolor": "gray",
                "steps": [{"range": [0, 100], "color": "#0E1117"}]
            }
        )
    ).update_layout(
        margin=dict(t=30, b=10),
        height=250
    )


def main():
    """Main application function handling UI layout and logic."""
    st.title("Company News Sentiment Analyzer ")
    
    left_col, right_col = st.columns([0.35, 0.65])
    
    with left_col:
        render_left_column()
        
    with right_col:
        render_right_column()


def render_left_column():
    """Handles left column components."""
    st.subheader("Select Company 🔍")
    
    companies = [
        "Tesla", "Apple", "Microsoft", "Google",
        "Amazon", "Meta", "Netflix", "NVIDIA",
        "Samsung", "Sony", "Toyota", "Intel"
    ]
    
    selected_company = st.selectbox(
        "Type or select company:",
        options=companies,
        index=None,
        placeholder="Search companies..."
    )
    
    if st.button("Analyze News", type="primary"):
        handle_company_selection(selected_company)
    
    st.markdown("---")
    st.subheader("🎧 Hindi Summary")
    st.warning("Text-to-Speech feature coming soon!")


def handle_company_selection(company):
    """Process company selection and generate sample articles."""
    if company:
        st.session_state.selected_company = company
        generate_sample_articles()
    else:
        st.warning("Please select a company first!")


def generate_sample_articles():
    """Generate dummy articles for demonstration purposes."""
    sentiments = ["Positive", "Negative", "Neutral"]
    company = st.session_state.selected_company
    
    st.session_state.articles = [
        {
            "title": f"{company} News {i+1}",
            "summary": f"Sample summary {i+1} about {company}",
            "sentiment": random.choice(sentiments),
            "topics": random.sample(
                ["Finance", "Technology", "Regulation", "Innovation"], 2
            )
        } 
        for i in range(10)
    ]


def render_right_column():
    """Handles right column components."""
    if not st.session_state.selected_company:
        st.info("👈 Select a company and click 'Analyze News' to begin")
        return
    
    st.subheader(f" Analysis Report: {st.session_state.selected_company}")
    
    pos_pct, neg_pct, neu_pct, pos, neg, neu = calculate_sentiment_stats()
    render_gauges(pos_pct, neg_pct, neu_pct)
    render_filter_controls(pos, neg, neu)
    render_article_list()


def calculate_sentiment_stats() -> Tuple[float, float, float, int, int, int]:
    """Calculate sentiment distribution percentages and counts."""
    sentiments = [a["sentiment"] for a in st.session_state.articles]
    total = len(sentiments)
    
    pos = sentiments.count("Positive")
    neg = sentiments.count("Negative")
    neu = sentiments.count("Neutral")
    
    pos_pct = (pos / total * 100) if total > 0 else 0
    neg_pct = (neg / total * 100) if total > 0 else 0
    neu_pct = (neu / total * 100) if total > 0 else 0
    
    return pos_pct, neg_pct, neu_pct, pos, neg, neu


def render_gauges(pos_pct, neg_pct, neu_pct):
    """Render sentiment gauge charts."""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.plotly_chart(
            create_gauge(pos_pct, "Positive Sentiment", "#4CAF50"),
            use_container_width=True
        )
    
    with col2:
        st.plotly_chart(
            create_gauge(neg_pct, "Negative Sentiment", "#f44336"),
            use_container_width=True
        )
    
    with col3:
        st.plotly_chart(
            create_gauge(neu_pct, "Neutral Sentiment", "#2196F3"),
            use_container_width=True
        )


def render_filter_controls(pos, neg, neu):
    """Render sentiment filter controls."""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button(f"🟢 Show Positive ({pos})", use_container_width=True):
            st.session_state.selected_sentiment = "Positive"
    
    with col2:
        if st.button(f"🔴 Show Negative ({neg})", use_container_width=True):
            st.session_state.selected_sentiment = "Negative"
    
    with col3:
        if st.button(f"🔵 Show Neutral ({neu})", use_container_width=True):
            st.session_state.selected_sentiment = "Neutral"
    

def render_article_list():
    """Render filtered article list."""
    st.markdown("---")
    st.subheader("📰 Latest News Articles")
    
    filtered_articles = get_filtered_articles()
    
    for article in filtered_articles:
        with st.expander(f"{article['title']} - {article['sentiment']}"):
            render_article_details(article)


def get_filtered_articles() -> List[Dict]:
    """Get articles based on current filter selection."""
    try:
        if st.session_state.selected_sentiment:
            return [
                a for a in st.session_state.articles 
                if a.get("sentiment") == st.session_state.selected_sentiment
            ]
        return st.session_state.articles
    except Exception as e:
        st.error(f"Error filtering articles: {str(e)}")
        return []


def render_article_details(article):
    """Render article details in expander."""
    col1, col2 = st.columns([0.7, 0.3])
    
    with col1:
        st.write(article["summary"])
    
    with col2:
        st.caption(f"**Topics:** {', '.join(article['topics'])}")
        st.caption(f"**Sentiment:** {article['sentiment']}")


if __name__ == "__main__":
    main()