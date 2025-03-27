import streamlit as st
import requests
import base64
import plotly.graph_objects as go

# Set page config
st.set_page_config(
    page_title="News Analyzer",
    page_icon="🎓",
    layout="wide"
)

# Initialize session state
if "selected_company" not in st.session_state:
    st.session_state.update({
        "selected_company": None,
        "analysis_result": {},
        "selected_sentiment": None,
        "audio_bytes": None
    })

def create_gauge(value, title, color):
    """Create a Plotly gauge chart"""
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
    """Calculate sentiment percentages"""
    total = len(articles)
    if total == 0:
        return 0, 0, 0
    pos = sum(1 for a in articles if a.get("Sentiment") == "Positive")
    neg = sum(1 for a in articles if a.get("Sentiment") == "Negative")
    neu = total - pos - neg
    return (pos/total)*100, (neg/total)*100, (neu/total)*100

def render_article_list(articles):
    """Display articles with expandable details"""
    st.subheader("📰 Analyzed Articles")
    for article in articles:
        with st.expander(f"{article.get('Title', 'Untitled')} ({article.get('Sentiment', 'Unknown')})"):
            st.write(article.get("Summary", "No summary available"))
            if topics := article.get("Topics", []):
                st.caption(f"Topics: {', '.join(topics)}")

def handle_company_selection(company):
    """Process company selection with base64 audio handling"""
    st.session_state.update({
        "audio_bytes": None,
        "analysis_result": {},
        "selected_sentiment": None
    })

    if not company:
        st.warning("Please select or enter a company first!")
        return

    with st.spinner("Fetching and analyzing news articles..."):
        try:
            response = requests.post(
                "http://localhost:8000/analyze",
                json={"company_name": company}
            )

            if not response.ok:
                st.error(f"API Error: {response.status_code} - {response.text}")
                return

            result = response.json().get("report", {})
            
            # Decode base64 audio
            if result.get("Audio"):
                try:
                    st.session_state.audio_bytes = base64.b64decode(result["Audio"])
                except base64.binascii.Error as e:
                    st.error("Failed to decode audio data")
                    st.session_state.audio_bytes = None

            st.session_state.analysis_result = result
            st.session_state.selected_company = company

        except requests.exceptions.RequestException as e:
            st.error(f"Connection error: {str(e)}")

def render_left_column():
    """Left sidebar content"""
    st.subheader("🔍 Select Company")
    companies = [
        "Tesla", "Apple", "Microsoft", "Google", "Amazon", "Meta",
        "Netflix", "NVIDIA", "Samsung", "Sony", "Toyota", "Intel"
    ]

    selected = st.selectbox(
        "Type or select company:",
        options=companies,
        index=None,
        placeholder="Search companies...",
        key="company_select"
    )
    custom_company = st.text_input(
        "Or enter a different company:",
        placeholder="Type custom company name...",
        key="custom_company"
    )
    company = custom_company or selected

    if st.button("Analyze News 🧠", type="primary"):
        handle_company_selection(company)

    st.markdown("---")
    st.subheader("🎧 Hindi Summary")
    if st.session_state.audio_bytes:
        st.audio(st.session_state.audio_bytes, format="audio/mpeg")
    else:
        st.warning("No audio available yet")

    if st.session_state.analysis_result:
        st.markdown("---")
        st.subheader("Comparative Analysis")
        with st.expander("Show Detailed Analysis"):
            result = st.session_state.analysis_result
            st.markdown("#### Sentiment Distribution")
            st.write(result.get("Comparative Sentiment Score", {}).get("Sentiment Distribution", {}))
            st.markdown("#### Coverage Differences")
            for item in result.get("Comparative Sentiment Score", {}).get("Coverage Differences", []):
                st.markdown(f"- **{item.get('Comparison', '')}**")
                st.markdown(f"  *Impact*: {item.get('Impact', '')}")
            st.markdown("#### Topic Analysis")
            st.write(result.get("Comparative Sentiment Score", {}).get("Topic Overlap", {}))

def render_right_column():
    """Main content area"""
    if not st.session_state.selected_company:
        st.info("👈 Select a company and click 'Analyze News' to begin")
        return

    result = st.session_state.analysis_result
    articles = result.get("Articles", [])

    st.subheader(f"Analysis Report: {st.session_state.selected_company}")
    pos, neg, neu = calculate_sentiment_stats(articles)

    # Sentiment gauges
    cols = st.columns(3)
    with cols[0]:
        st.plotly_chart(create_gauge(pos, "Positive", "#4CAF50"), True)
    with cols[1]:
        st.plotly_chart(create_gauge(neg, "Negative", "#f44336"), True)
    with cols[2]:
        st.plotly_chart(create_gauge(neu, "Neutral", "#2196F3"), True)

    # Sentiment filters
    if articles:
        sentiments = [a.get("Sentiment", "Neutral") for a in articles]
        pos_count = sentiments.count("Positive")
        neg_count = sentiments.count("Negative")
        neu_count = len(articles) - pos_count - neg_count

        cols = st.columns(4)
        with cols[0]:
            if st.button(f"🟢 Positive ({pos_count})", use_container_width=True):
                st.session_state.selected_sentiment = "Positive"
        with cols[1]:
            if st.button(f"🔴 Negative ({neg_count})", use_container_width=True):
                st.session_state.selected_sentiment = "Negative"
        with cols[2]:
            if st.button(f"🔵 Neutral ({neu_count})", use_container_width=True):
                st.session_state.selected_sentiment = "Neutral"
        with cols[3]:
            if st.button("🧹 Clear Filters", use_container_width=True):
                st.session_state.selected_sentiment = None

    # Filtered articles
    filtered = [a for a in articles if not st.session_state.selected_sentiment or 
               a.get("Sentiment") == st.session_state.selected_sentiment]
    render_article_list(filtered)

def main():
    """Main app layout"""
    st.title("Company News Sentiment Analyzer")
    left, right = st.columns([0.35, 0.65])
    with left:
        render_left_column()
    with right:
        render_right_column()

if __name__ == "__main__":
    main()