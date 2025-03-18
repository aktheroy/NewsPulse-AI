# app.py
import streamlit as st
import requests
import time
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
    
    # Combined selectbox and free text input
    selected_company = st.selectbox(
        "Type or select company:",
        options=companies,
        index=None,
        placeholder="Search companies...",
        key="company_select"
    )
    
    # Use text input if no selection from dropdown
    custom_company = st.text_input(
        "Or enter a different company:",
        placeholder="Type custom company name...",
        key="custom_company"
    )
    
    # Determine final company name
    company_name = custom_company if custom_company else selected_company
    
    if st.button("Analyze News 📊", type="primary"):
        handle_company_selection(company_name)
    
    st.markdown("---")
    st.subheader("🎧 Hindi Summary")
    
    # Audio player integration
    if st.session_state.analysis_result.get("audio_file"):
        st.audio(st.session_state.analysis_result["audio_file"], format="audio/mpeg")
    else:
        st.warning("No audio available yet")

def handle_company_selection(company):
    if not company:
        st.warning("Please select or enter a company first!")
        return
    
    with st.spinner("Fetching and analyzing news articles..."):
        try:
            # Correct API request format
            response = requests.post(
                "http://localhost:8000/analyze",
                json={"company_name": company}  # Ensure this matches the API expectation
            )
            
            # Add debug output
            st.write("API Response Status Code:", response.status_code)
            st.write("API Response Content:", response.text)
            
            response.raise_for_status()
            task_id = response.json().get("task_id")
            
            if task_id:
                # Poll for results with timeout
                max_retries = 10
                for _ in range(max_retries):
                    result_response = requests.get(f"http://localhost:8000/results/{task_id}")
                    if result_response.status_code == 200:
                        result = result_response.json().get("report", {})
                        st.session_state.analysis_result = result
                        st.session_state.selected_company = company
                        break
                    elif result_response.status_code == 202:
                        time.sleep(3)
                    else:
                        st.error("Analysis failed")
                        break
                else:
                    st.error("Analysis timed out")
                
        except requests.exceptions.HTTPError as e:
            st.error(f"API Error ({e.response.status_code}): {e.response.text}")
        except Exception as e:
            st.error(f"Error: {str(e)}")

def render_right_column():
    if not st.session_state.selected_company:
        st.info("👈 Select a company and click 'Analyze News' to begin")
        return
    
    result = st.session_state.analysis_result
    articles = result.get("articles", [])
    
    st.subheader(f"📈 Analysis Report: {st.session_state.selected_company}")
    
    # Sentiment gauges (default to 0)
    pos_pct, neg_pct, neu_pct = calculate_sentiment_stats(articles)
    render_gauges(pos_pct, neg_pct, neu_pct)
    
    # Filter controls
    render_filter_controls(articles)
    
    # Article list
    render_article_list(articles)
    
    # Comparative analysis
    st.subheader("📊 Comparative Analysis")
    with st.expander("Show Detailed Analysis"):
        # Sentiment distribution
        st.markdown("#### Sentiment Distribution")
        st.write(result.get("sentiment_distribution", {}))
        
        # Coverage differences
        st.markdown("#### Coverage Differences")
        comparisons = result.get("comparative_analysis", [])
        for item in comparisons:
            st.markdown(f"- **{item.get('Comparison', '')}**")
            st.markdown(f"  *Impact*: {item.get('Impact', '')}")
        
        # Topic overlap
        st.markdown("#### Topic Analysis")
        st.write(result.get("topic_analysis", {}))
        
def calculate_sentiment_stats(articles):
    total = len(articles)
    if total == 0:
        return 0, 0, 0  # Default to 0 values
    
    sentiments = [a.get("Sentiment", "Neutral") for a in articles]
    pos = sentiments.count("Positive")
    neg = sentiments.count("Negative")
    neu = sentiments.count("Neutral")
    
    return (
        round((pos / total) * 100, 1) if total > 0 else 0,
        round((neg / total) * 100, 1) if total > 0 else 0,
        round((neu / total) * 100, 1) if total > 0 else 0
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
    if not articles:
        return
    
    sentiments = [a.get("Sentiment", "Neutral") for a in articles]
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
    if not articles:
        st.warning("No articles found for analysis")
        return
    
    st.markdown("---")
    st.subheader("📰 Latest News Articles")
    
    filtered = [a for a in articles if a.get("Sentiment") == st.session_state.get("selected_sentiment")] \
        if st.session_state.get("selected_sentiment") else articles
    
    for article in filtered:
        with st.expander(f"{article.get('Title', 'Untitled')} - {article.get('Sentiment', 'Neutral')}"):
            col1, col2 = st.columns([0.7, 0.3])
            
            with col1:
                st.write(article.get("Summary", "No summary available"))
            
            with col2:
                st.caption(f"**Topics:** {', '.join(article.get('Topics', []))}")
                st.caption(f"**Date:** {article.get('date', 'Unknown')}")

if __name__ == "__main__":
    main()