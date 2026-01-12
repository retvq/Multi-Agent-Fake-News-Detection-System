import streamlit as st
from components.shared_styles import inject_styles, render_sidebar_branding

st.set_page_config(
    page_title="About - Fake News Detection",
    page_icon="⊹",
    layout="wide"
)

inject_styles()

with st.sidebar:
    render_sidebar_branding()

st.markdown('<div class="logo-symbol">⊹</div>', unsafe_allow_html=True)
st.markdown('<h1 class="main-header">About This System</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Learn how the Fake News Detection AI works</p>', unsafe_allow_html=True)

st.header("System Overview")

st.markdown("A production-grade multi-model AI system for detecting misinformation in news articles.")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**Accuracy**: Multi-model ensemble with weighted aggregation")

with col2:
    st.markdown("**Performance**: Sub-3 second analysis with intelligent caching")

with col3:
    st.markdown("**Reliability**: Graceful degradation and fallback chain")

st.header("How It Works")

with st.expander("Model Ensemble", expanded=True):
    st.markdown("""
    | Model | Weight | Description |
    |-------|--------|-------------|
    | HuggingFace Sentiment | 40% | Sentiment-based detection |
    | Gemini/Groq LLM | 35% | Large language model reasoning |
    | Heuristic Analyzer | 25% | Rule-based pattern detection |
    """)

with st.expander("Heuristic Indicators"):
    st.markdown("""
    - **Emotional Language**: Sensationalist words
    - **Clickbait Patterns**: Attention-grabbing phrases
    - **Excessive Punctuation**: Overuse of ! and ?
    - **ALL CAPS Usage**: Excessive capitalization
    """)

with st.expander("Confidence Scoring"):
    st.markdown("""
    - High Confidence (>80%): Strong indicators, models agree
    - Medium Confidence (60-80%): Some disagreement
    - Low Confidence (<60%): Uncertain result
    """)

with st.expander("Caching System"):
    st.markdown("Results cached for 24 hours for instant retrieval.")

st.header("Classification Thresholds")

st.markdown("""
| Fake Probability | Classification |
|------------------|----------------|
| >= 70% | LIKELY FAKE |
| 31% - 69% | UNCERTAIN |
| <= 30% | LIKELY REAL |
""")

st.header("Limitations")

st.warning("AI can make mistakes. Always verify with trusted sources.")

st.header("FAQ")

with st.expander("What types of content can I analyze?"):
    st.markdown("News articles, social media posts, blog posts (50-5000 characters)")

with st.expander("Is my data stored?"):
    st.markdown("Text is cached locally for 24 hours. No data shared with third parties.")

with st.expander("What if APIs are unavailable?"):
    st.markdown("System falls back to heuristic-only mode which always works.")

st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.caption("Version: 2.0.0")

with col2:
    st.caption("Last Updated: January 2026")

with col3:
    st.caption("License: MIT")
