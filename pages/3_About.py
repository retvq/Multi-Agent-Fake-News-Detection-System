

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

st.markdown()

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown()

with col2:
    st.markdown()

with col3:
    st.markdown()

st.header("How It Works")

with st.expander("Model Ensemble", expanded=True):
    st.markdown()

with st.expander("Heuristic Indicators"):
    st.markdown()

with st.expander("Confidence Scoring"):
    st.markdown()

with st.expander("Caching System"):
    st.markdown()

st.header("Classification Thresholds")

st.markdown()

st.header("Limitations")

st.warning()

st.header("Frequently Asked Questions")

with st.expander("What types of content can I analyze?"):
    st.markdown()

with st.expander("How accurate is the system?"):
    st.markdown()

with st.expander("Is my data stored or shared?"):
    st.markdown()

with st.expander("What if the APIs are unavailable?"):
    st.markdown()

with st.expander("How do I add my own API keys?"):
    st.markdown()

st.header("Technical Specifications")

with st.expander("View Technical Details"):
    st.markdown()

st.header("Feedback")

st.markdown()

st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.caption("Version: 2.0.0")

with col2:
    st.caption("Last Updated: January 2026")

with col3:
    st.caption("License: MIT")
