import streamlit as st
import requests
import plotly.graph_objects as go

# Set page config first
st.set_page_config(
    page_title="News Analyzer",
    page_icon="📈",
    layout="wide"
)

# Initialize session state
if "selected_company" not in st.session_state:
    st.session_state.selected_company = None
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = {}

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

def main():
    st.title("📈 Company News Sentiment Analyzer")
    
    left_col, right_col = st.columns([0.35, 0.65])
    
    with left_col:
        render_left_column()
        
    with right_col:
        render_right_column()

def render_left_column():
    st.subheader("🔍 Select Company")
    
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
    
    if st.button("Analyze News 📊", type="primary"):
        handle_company_selection(selected_company)
    
    st.markdown("---")
    st.subheader("🎧 Hindi Summary")
    
    # Audio player integration
    if st.session_state.analysis_result.get("Audio"):
        st.audio(st.session_state.analysis_result["Audio"], format="audio/wav")
    else:
        st.warning("No audio available yet")

def handle_company_selection(company):
    if not company:
        st.warning("Please select a company first!")
        return
    
    with st.spinner("Fetching and analyzing news articles..."):
        try:
            response = requests.post(
                "http://localhost:8000/analyze",
                json={"company": company}
            )
            response.raise_for_status()
            result = response.json()
            
            # Update session state
            st.session_state.selected_company = company
            st.session_state.analysis_result = result
            
        except requests.exceptions.RequestException as e:
            st.error(f"Error: {str(e)}")

def render_right_column():
    if not st.session_state.selected_company:
        st.info("👈 Select a company and click 'Analyze News' to begin")
        return
    
    result = st.session_state.analysis_result
    articles = result.get("Articles", [])
    
    st.subheader(f"📈 Analysis Report: {st.session_state.selected_company}")
    
    # Sentiment gauges
    pos_pct, neg_pct, neu_pct = calculate_sentiment_stats(articles)
    render_gauges(pos_pct, neg_pct, neu_pct)
    
    # Filter controls
    render_filter_controls(articles)
    
    # Article list
    render_article_list(articles)
    
    # Comparative analysis
    if "Comparative Sentiment Score" in result:
        st.subheader("📊 Comparative Analysis")
        with st.expander("Show Detailed Analysis"):
            comparative = result["Comparative Sentiment Score"]
            
            # Sentiment distribution
            st.markdown("#### Sentiment Distribution")
            st.write(comparative.get("Sentiment Distribution", {}))
            
            # Coverage differences
            st.markdown("#### Coverage Differences")
            for item in comparative.get("Coverage Differences", []):
                st.markdown(f"- **Comparison**: {item['Comparison']}")
                st.markdown(f"  **Impact**: {item['Impact']}")
            
            # Topic overlap
            st.markdown("#### Topic Overlap")
            st.write(comparative.get("Topic Overlap", {}))

def calculate_sentiment_stats(articles):
    total = len(articles)
    if total == 0:
        return 0, 0, 0
    
    sentiments = [a["Sentiment"] for a in articles]
    pos = sentiments.count("Positive")
    neg = sentiments.count("Negative")
    neu = sentiments.count("Neutral")
    
    return (
        round((pos / total) * 100, 1),
        round((neg / total) * 100, 1),
        round((neu / total) * 100, 1)
    )

def render_gauges(pos_pct, neg_pct, neu_pct):
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

def render_filter_controls(articles):
    sentiments = [a["Sentiment"] for a in articles]
    pos = sentiments.count("Positive")
    neg = sentiments.count("Negative")
    neu = sentiments.count("Neutral")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button(f"✅ Show Positive ({pos})", use_container_width=True):
            st.session_state.selected_sentiment = "Positive"
    
    with col2:
        if st.button(f"❌ Show Negative ({neg})", use_container_width=True):
            st.session_state.selected_sentiment = "Negative"
    
    with col3:
        if st.button(f"⚪ Show Neutral ({neu})", use_container_width=True):
            st.session_state.selected_sentiment = "Neutral"
    
    if st.session_state.get("selected_sentiment"):
        if st.button("Clear Filters 🧹", use_container_width=True):
            st.session_state.selected_sentiment = None

def render_article_list(articles):
    st.markdown("---")
    st.subheader("📰 Latest News Articles")
    
    filtered = [a for a in articles if a["Sentiment"] == st.session_state.get("selected_sentiment")] \
        if st.session_state.get("selected_sentiment") else articles
    
    for article in filtered:
        with st.expander(f"{article['Title']} - {article['Sentiment']}"):
            col1, col2 = st.columns([0.7, 0.3])
            
            with col1:
                st.write(article["Summary"])
            
            with col2:
                st.caption(f"**Topics:** {', '.join(article['Topics'])}")
                st.caption(f"**Sentiment:** {article['Sentiment']}")

if __name__ == "__main__":
    main()