

import streamlit as st
import asyncio
import json
import os
from datetime import datetime
import logging

from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from core.config import Config
from core.ensemble import EnsemblePredictor
from core.cache import CacheManager
from core.metrics import MetricsTracker

from utils.validators import validate_text_length, get_character_count_display

from components.verdict_display import display_verdict
from components.model_scores import display_model_scores, display_model_agreement
from components.indicators import display_indicators, display_indicator_summary

st.set_page_config(
    page_title="Fake News Detection AI",
    page_icon="⊹",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "# Fake News Detection AI\nProduction-grade multi-model analysis system."
    }
)

from components.shared_styles import inject_styles
inject_styles()

def init_session_state():
    
    
    if 'config' not in st.session_state:
        try:
            st.session_state.config = Config.from_secrets(st.secrets)
        except Exception as e:
            logger.warning(f"Could not load secrets, using defaults: {e}")
            st.session_state.config = Config()
    
    if 'ensemble' not in st.session_state:
        st.session_state.ensemble = EnsemblePredictor(st.session_state.config)
    
    if 'cache_manager' not in st.session_state:
        st.session_state.cache_manager = CacheManager(
            cache_file="cache.json",
            ttl_hours=st.session_state.config.cache_ttl_hours
        )
    
    if 'metrics_tracker' not in st.session_state:
        st.session_state.metrics_tracker = MetricsTracker()
    
    if 'predictions_history' not in st.session_state:
        st.session_state.predictions_history = []
    
    if 'total_predictions' not in st.session_state:
        st.session_state.total_predictions = 0
    
    if 'session_start_time' not in st.session_state:
        st.session_state.session_start_time = datetime.now()
    
    if 'current_result' not in st.session_state:
        st.session_state.current_result = None

init_session_state()

def render_sidebar():
    
    
    with st.sidebar:
        st.markdown('''
        <div class="sidebar-branding">
            <span class="sidebar-logo" style="font-size: 1.8rem;">⊹</span>
            <span>Fake News Detector</span>
        </div>
        ''', unsafe_allow_html=True)
        
        st.divider()
        
        st.metric("Total Analyses", st.session_state.total_predictions)
        
        cache_stats = st.session_state.cache_manager.stats()
        st.metric("Cache Hit Rate", f"{cache_stats['hit_rate']:.1%}")
        st.caption(f"Cached entries: {cache_stats['total_entries']}")
        
        st.markdown("---")
        
        st.subheader("Active Models")
        active_models = st.session_state.config.get_active_models()
        for model in active_models:
            st.markdown(f"• {model.title()}")
        
        if len(active_models) == 1:
            st.warning("Running in heuristic-only mode. Add API keys for full functionality.")
        
        st.markdown("---")
        
        st.subheader("Quota Usage")
        
        if st.session_state.config.has_hf_key():
            hf_usage = st.session_state.ensemble.hf_client.get_quota_usage()
            st.progress(
                hf_usage['percentage'] / 100,
                text=f"HuggingFace: {hf_usage['used']}/{hf_usage['total']}"
            )
        else:
            st.caption("HuggingFace: No API key")
        
        if st.session_state.config.has_gemini_key():
            gemini_usage = st.session_state.ensemble.gemini_client.get_quota_usage()
            st.progress(
                gemini_usage['percentage'] / 100,
                text=f"Gemini: {gemini_usage['used']}/{gemini_usage['total']}"
            )
        else:
            st.caption("Gemini: No API key")
        
        if st.session_state.config.has_groq_key():
            groq_usage = st.session_state.ensemble.groq_client.get_quota_usage()
            st.progress(
                groq_usage['percentage'] / 100,
                text=f"Groq: {groq_usage['used']}/{groq_usage['total']}"
            )
        else:
            st.caption("Groq: No API key (fallback)")
        
        st.markdown("---")
        
        st.subheader("Session")
        session_info = st.session_state.metrics_tracker.get_session_info()
        st.caption(f"Uptime: {session_info['uptime']}")
        st.caption(f"Rate: {session_info['predictions_per_hour']:.1f}/hr")

render_sidebar()

st.markdown('<div class="logo-symbol">⊹</div>', unsafe_allow_html=True)
st.markdown('<h1 class="main-header">Fake News Detection AI</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Production-grade multi-model analysis powered by AI ensemble</p>', unsafe_allow_html=True)

st.markdown('''
<div class="info-card">
    <strong>How it works:</strong> Paste any news article text below. 
    Our AI ensemble analyzes it using multiple models and highlights 
    potential misinformation indicators.
</div>
''', unsafe_allow_html=True)

st.header("Analyze News Article")

article_text = st.text_area(
    "Paste article text here:",
    height=200,
    max_chars=st.session_state.config.max_text_length,
    placeholder="Enter or paste the news article you want to analyze...\n\nMinimum 50 characters required for accurate analysis.",
    help="Paste the full text of the news article. The system analyzes text patterns, not URLs."
)

col1, col2 = st.columns(2)
with col1:
    article_url = st.text_input(
        "Article URL (optional)",
        placeholder="https://example.com/article",
        help="For reference only - not used in analysis"
    )
with col2:
    source_name = st.text_input(
        "Source Name (optional)",
        placeholder="e.g., CNN, BBC, Fox News",
        help="For reference only - not used in analysis"
    )

char_count = len(article_text) if article_text else 0
display_text, status = get_character_count_display(
    article_text,
    st.session_state.config.max_text_length
)

if status == "empty":
    st.caption(display_text)
elif status == "short":
    st.warning(display_text)
elif status == "valid":
    st.success(display_text)
else:
    st.error(display_text)

is_valid, validation_msg = validate_text_length(
    article_text,
    st.session_state.config.min_text_length,
    st.session_state.config.max_text_length
)

analyze_clicked = st.button(
    "Analyze Article",
    type="primary",
    disabled=not is_valid,
    use_container_width=True
)

if analyze_clicked and is_valid:
    cached_result = st.session_state.cache_manager.get(article_text)
    
    if cached_result:
        st.info("**Retrieved from cache** - Instant result!")
        result = cached_result
        result['cached'] = True
        st.session_state.current_result = result
    else:
        with st.spinner("Analyzing with AI models..."):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                start_time = datetime.now()
                
                status_text.text("Running heuristic analysis...")
                progress_bar.progress(20)
                
                status_text.text("Querying HuggingFace models...")
                progress_bar.progress(40)
                
                status_text.text("Querying Gemini/Groq LLM...")
                progress_bar.progress(60)
                
                result = asyncio.run(
                    st.session_state.ensemble.predict(article_text)
                )
                
                status_text.text("Aggregating results...")
                progress_bar.progress(80)
                
                result['cached'] = False
                
                st.session_state.cache_manager.set(article_text, result)
                
                progress_bar.progress(100)
                status_text.text("Analysis complete!")
                
                st.session_state.current_result = result
                
            except Exception as e:
                logger.error(f"Analysis failed: {e}")
                st.error(f"Analysis failed: {str(e)}")
                st.info("**Troubleshooting tips:**\n- Check your internet connection\n- Verify API keys in settings\n- Try with shorter text")
                st.session_state.metrics_tracker.record_error(e, "ensemble")
                st.stop()
    
    st.session_state.metrics_tracker.record_prediction(result, article_text)
    st.session_state.predictions_history.insert(0, result)
    st.session_state.total_predictions += 1

if st.session_state.current_result:
    result = st.session_state.current_result
    
    st.divider()
    st.header("Analysis Results")
    
    display_verdict(result)
    
    with st.expander("Model Scores Breakdown", expanded=True):
        model_scores = result.get('model_scores', [])
        display_model_scores(model_scores)
        display_model_agreement(model_scores)
    
    with st.expander("Detection Indicators", expanded=True):
        indicator_details = result.get('indicator_details', [])
        indicators = result.get('indicators', {})
        
        if indicator_details:
            display_indicators(indicator_details)
        elif indicators:
            display_indicator_summary(indicators)
        else:
            st.info("No detailed indicators available.")
    
    with st.expander("Detailed Explanation"):
        st.write(result.get('explanation', 'No explanation available.'))
        
        prediction = result.get('prediction', 'UNCERTAIN')
        
        if prediction == 'FAKE':
            st.warning("This article shows signs of potential misinformation. Verify with trusted sources before sharing.")
        elif prediction == 'UNCERTAIN':
            st.info("Results are inconclusive. Cross-reference with other reliable sources.")
        else:
            st.success("This article appears authentic, but always verify important claims independently.")
    
    st.divider()
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        st.download_button(
            label="Download Report (JSON)",
            data=json.dumps(result, indent=2, default=str),
            file_name=f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    
    with col2:
        if st.button("New Analysis"):
            st.session_state.current_result = None
            st.rerun()
    
    st.caption(
        f"Analysis completed in {result.get('processing_time', 0):.2f}s | "
        f"Models used: {', '.join(result.get('models_used', []))} | "
        f"{'Cached' if result.get('cached') else 'Fresh analysis'} | "
        f"{result.get('timestamp', 'N/A')}"
    )

st.divider()
st.caption("Disclaimer: This tool provides AI-assisted analysis. Always verify information through multiple trusted sources.")
