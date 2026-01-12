

import streamlit as st
from datetime import datetime

from components.system_health import (
    display_system_health,
    display_quota_management,
    display_error_log,
    display_performance_metrics
)
from components.shared_styles import inject_styles, render_sidebar_branding

st.set_page_config(
    page_title="Monitoring - Fake News Detection",
    page_icon="⊹",
    layout="wide"
)

inject_styles()

with st.sidebar:
    render_sidebar_branding()

st.markdown('<div class="logo-symbol">⊹</div>', unsafe_allow_html=True)
st.markdown('<h1 class="main-header">System Monitoring</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Real-time system health and performance monitoring</p>', unsafe_allow_html=True)

if 'ensemble' not in st.session_state:
    st.warning("System not initialized. Please visit the main page first.")
    st.stop()

st.header("System Health")

health_data = st.session_state.ensemble.get_system_health()

display_system_health(health_data)

st.header("API Quota Management")

col1, col2 = st.columns(2)

with col1:
    st.subheader("HuggingFace API")
    
    if st.session_state.config.has_hf_key():
        hf_quota = st.session_state.ensemble.hf_client.get_quota_usage()
        
        used = hf_quota['used']
        total = hf_quota['total']
        pct = hf_quota['percentage']
        remaining = hf_quota['remaining']
        
        if pct >= 90:
            st.error(f"Critical: {pct:.1f}% used")
        elif pct >= 80:
            st.warning(f"Warning: {pct:.1f}% used")
        elif pct >= 50:
            st.info(f"Moderate: {pct:.1f}% used")
        else:
            st.success(f"Healthy: {pct:.1f}% used")
        
        st.progress(min(pct / 100, 1.0))
        
        mcol1, mcol2 = st.columns(2)
        with mcol1:
            st.metric("Used Today", f"{used:,}")
        with mcol2:
            st.metric("Remaining", f"{remaining:,}")
        
        st.caption(f"Daily limit: {total:,}")
        st.caption(f"Resets: {hf_quota['reset_date']}")
    else:
        st.info("No API key configured")
        st.caption("Add HF_API_KEY to .streamlit/secrets.toml")

with col2:
    st.subheader("Gemini API (Primary LLM)")
    
    if st.session_state.config.has_gemini_key():
        gemini_quota = st.session_state.ensemble.gemini_client.get_quota_usage()
        
        used = gemini_quota['used']
        total = gemini_quota['total']
        pct = gemini_quota['percentage']
        remaining = gemini_quota['remaining']
        
        if pct >= 90:
            st.error(f"Critical: {pct:.1f}% used")
        elif pct >= 80:
            st.warning(f"Warning: {pct:.1f}% used")
        elif pct >= 50:
            st.info(f"Moderate: {pct:.1f}% used")
        else:
            st.success(f"Healthy: {pct:.1f}% used")
        
        st.progress(min(pct / 100, 1.0))
        
        mcol1, mcol2 = st.columns(2)
        with mcol1:
            st.metric("Used Today", f"{used:,}")
        with mcol2:
            st.metric("Remaining", f"{remaining:,}")
        
        st.caption(f"Daily limit: {total:,}")
        st.caption(f"Resets: {gemini_quota['reset_date']}")
    else:
        st.info("No API key configured")
        st.caption("Add GEMINI_API_KEY to .streamlit/secrets.toml")

st.subheader("Groq API (Fallback LLM)")

if st.session_state.config.has_groq_key():
    groq_quota = st.session_state.ensemble.groq_client.get_quota_usage()
    
    used = groq_quota['used']
    total = groq_quota['total']
    pct = groq_quota['percentage']
    remaining = groq_quota['remaining']
    
    col1, col2 = st.columns(2)
    
    with col1:
        if pct >= 90:
            st.error(f"Critical: {pct:.1f}% used")
        elif pct >= 80:
            st.warning(f"Warning: {pct:.1f}% used")
        else:
            st.success(f"Healthy: {pct:.1f}% used")
        
        st.progress(min(pct / 100, 1.0))
    
    with col2:
        st.metric("Used/Remaining", f"{used:,} / {remaining:,}")
        st.caption(f"Daily limit: {total:,}")
else:
    st.info("No API key configured (fallback disabled)")

st.header("Cache Management")

if 'cache_manager' in st.session_state:
    cache_stats = st.session_state.cache_manager.stats()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Entries", cache_stats['total_entries'])
    with col2:
        st.metric("Hit Rate", f"{cache_stats['hit_rate']:.1%}")
    with col3:
        st.metric("Memory Size", f"{cache_stats.get('size_bytes', 0) / 1024:.1f} KB")
    
    if st.button("Clear Cache", type="secondary"):
        st.session_state.cache_manager.clear()
        st.success("Cache cleared!")
        st.rerun()
else:
    st.info("Cache manager not initialized.")

st.header("Recent Errors")

if 'metrics_tracker' in st.session_state:
    errors = st.session_state.metrics_tracker.get_recent_errors(limit=10)
    
    if errors:
        for error in errors:
            with st.expander(f"{error['timestamp']} - {error['component']}"):
                st.code(error['message'])
    else:
        st.success("No errors recorded this session.")
else:
    st.info("Metrics tracker not initialized.")

st.divider()
st.caption("System monitoring data is session-specific and resets on page refresh.")
