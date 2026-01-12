

import streamlit as st
import pandas as pd
from typing import Dict, Any, List

def display_model_scores(model_scores: List[Dict[str, Any]]) -> None:
    
    if not model_scores:
        st.info("No model scores available.")
        return
    
    model_names = {
        'heuristic': ('Heuristic', 'Rule-based pattern detection'),
        'huggingface': ('HuggingFace', 'Sentiment-based classifier'),
        'gemini': ('Gemini', 'LLM-based analysis'),
        'groq': ('Groq', 'LLM fallback')
    }
    
    st.caption(f"Analyzed by {len(model_scores)} model(s)")
    
    cols = st.columns([3, 2, 2, 1.5, 1])
    with cols[0]:
        st.markdown("**Model**")
    with cols[1]:
        st.markdown("**Fake Probability**")
    with cols[2]:
        st.markdown("**Confidence**")
    with cols[3]:
        st.markdown("**Time**")
    with cols[4]:
        st.markdown("**Weight**")
    
    st.divider()
    
    sorted_scores = sorted(
        model_scores,
        key=lambda x: x.get('fake_probability', 0),
        reverse=True
    )
    
    for score in sorted_scores:
        model_name = score.get('model_name', 'unknown')
        fake_prob = score.get('fake_probability', 0.5)
        confidence = score.get('confidence', 0.5)
        proc_time = score.get('processing_time', 0)
        weight = score.get('weight', 0.1)
        
        display_info = model_names.get(model_name, (model_name.title(), 'Unknown model'))
        
        cols = st.columns([3, 2, 2, 1.5, 1])
        
        with cols[0]:
            st.markdown(f"**{display_info[0]}**")
            st.caption(display_info[1])
        
        with cols[1]:
            color = _get_probability_color(fake_prob)
            st.markdown(
                f"<span style='color: {color}; font-weight: bold;'>"
                f"{fake_prob * 100:.1f}%</span>",
                unsafe_allow_html=True
            )
            st.progress(fake_prob)
        
        with cols[2]:
            st.markdown(f"{confidence * 100:.1f}%")
            st.progress(confidence)
        
        with cols[3]:
            if proc_time < 0.001:
                st.markdown("<1ms")
            elif proc_time < 1:
                st.markdown(f"{proc_time * 1000:.0f}ms")
            else:
                st.markdown(f"{proc_time:.2f}s")
        
        with cols[4]:
            st.markdown(f"{weight * 100:.0f}%")
        
        st.divider()

def display_model_scores_compact(model_scores: List[Dict[str, Any]]) -> None:
    
    if not model_scores:
        return
    
    df = pd.DataFrame(model_scores)
    
    df['Fake %'] = df['fake_probability'].apply(lambda x: f"{x * 100:.1f}%")
    df['Conf %'] = df['confidence'].apply(lambda x: f"{x * 100:.1f}%")
    df['Time'] = df['processing_time'].apply(
        lambda x: f"{x * 1000:.0f}ms" if x < 1 else f"{x:.2f}s"
    )
    df['Weight'] = df.get('weight', pd.Series([0.1] * len(df))).apply(
        lambda x: f"{x * 100:.0f}%"
    )
    
    model_icons = {'heuristic': '', 'huggingface': '', 'gemini': '', 'groq': ''}
    df['Model'] = df['model_name'].apply(
        lambda x: x.title()
    )
    
    display_df = df[['Model', 'Fake %', 'Conf %', 'Time', 'Weight']]
    
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )

def _get_probability_color(prob: float) -> str:
    
    if prob >= 0.7:
        return '#ef4444'
    elif prob >= 0.3:
        return '#f59e0b'
    else:
        return '#10b981'

def display_model_agreement(model_scores: List[Dict[str, Any]]) -> None:
    
    if len(model_scores) < 2:
        return
    
    probs = [s.get('fake_probability', 0.5) for s in model_scores]
    min_prob, max_prob = min(probs), max(probs)
    spread = max_prob - min_prob
    
    if spread < 0.1:
        st.success("**High Agreement** - All models closely agree")
    elif spread < 0.3:
        st.info("**Moderate Agreement** - Some variation between models")
    else:
        st.warning("**Low Agreement** - Models have diverging opinions")
    
    st.caption(f"Probability spread: {min_prob*100:.0f}% - {max_prob*100:.0f}% (Δ{spread*100:.0f}%)")
