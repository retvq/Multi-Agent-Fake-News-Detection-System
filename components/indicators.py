

import streamlit as st
from typing import Dict, Any, List

INDICATOR_INFO = {
    'emotional_language': {
        'icon': '',
        'name': 'Emotional Language',
        'description': 'Detects sensationalist and emotionally charged words',
        'tooltip': 'High scores indicate excessive use of shocking, alarming, or exaggerated language'
    },
    'clickbait_patterns': {
        'icon': '',
        'name': 'Clickbait Patterns',
        'description': 'Identifies clickbait phrases and attention-grabbing patterns',
        'tooltip': 'Phrases like "you won\'t believe" or "doctors hate this" are strong indicators'
    },
    'excessive_punctuation': {
        'icon': '',
        'name': 'Excessive Punctuation',
        'description': 'Detects overuse of exclamation marks and question marks',
        'tooltip': 'Multiple !!! or ??? often indicate sensationalized content'
    },
    'caps_ratio': {
        'icon': '',
        'name': 'ALL CAPS Usage',
        'description': 'Measures the ratio of uppercase text',
        'tooltip': 'Excessive capitalization is often used to convey urgency or alarm'
    }
}

def display_indicators(indicator_details: List[Dict[str, Any]]) -> None:
    
    if not indicator_details:
        st.info("No detection indicators available.")
        return
    
    cols = st.columns(2)
    
    for idx, indicator in enumerate(indicator_details):
        col = cols[idx % 2]
        
        with col:
            _render_indicator_card(indicator)

def _render_indicator_card(indicator: Dict[str, Any]) -> None:
    
    name = indicator.get('name', 'Unknown')
    score = indicator.get('score', 0.0)
    severity = indicator.get('severity', 'LOW')
    description = indicator.get('description', '')
    matches = indicator.get('matches', [])
    
    key = name.lower().replace(' ', '_')
    info = INDICATOR_INFO.get(key, {
        'icon': '',
        'name': name,
        'description': description,
        'tooltip': ''
    })
    
    severity_colors = {
        'LOW': ('#d1fae5', '#065f46', 'L'),
        'MEDIUM': ('#fef3c7', '#92400e', 'M'),
        'HIGH': ('#fee2e2', '#991b1b', 'H')
    }
    bg_color, text_color, badge = severity_colors.get(severity, severity_colors['LOW'])
    
    st.markdown(f, unsafe_allow_html=True)
    
    st.progress(score)
    st.caption(f"Score: {score * 100:.1f}%")
    
    if matches and len(matches) > 0:
        with st.expander("View detected patterns"):
            for match in matches[:5]:
                st.code(match, language=None)

def display_indicators_compact(indicators: Dict[str, float]) -> None:
    
    if not indicators:
        return
    
    cols = st.columns(len(indicators))
    
    for idx, (name, score) in enumerate(indicators.items()):
        key = name.lower().replace(' ', '_')
        info = INDICATOR_INFO.get(key, {'icon': '', 'name': name})
        
        with cols[idx]:
            st.metric(
                label=f"{info['icon']} {info.get('name', name)[:15]}",
                value=f"{score * 100:.0f}%"
            )
            
            color = 'red' if score >= 0.7 else 'orange' if score >= 0.4 else 'green'
            st.markdown(
                f"<div style='height: 4px; background: {color}; "
                f"width: {score * 100}%; border-radius: 2px;'></div>",
                unsafe_allow_html=True
            )

def display_indicator_summary(indicators: Dict[str, float]) -> None:
    
    if not indicators:
        return
    
    avg_score = sum(indicators.values()) / len(indicators)
    high_count = sum(1 for s in indicators.values() if s >= 0.5)
    
    st.markdown("### Indicator Summary")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Average Score", f"{avg_score * 100:.0f}%")
    
    with col2:
        st.metric("High Flags", f"{high_count}/{len(indicators)}")
    
    with col3:
        risk = "High" if avg_score >= 0.5 else "Medium" if avg_score >= 0.3 else "Low"
        st.metric("Risk Level", risk)
