

import streamlit as st
import plotly.graph_objects as go
from typing import Dict, Any

def display_verdict(result: Dict[str, Any]) -> None:
    
    prediction = result.get("prediction", "UNCERTAIN")
    confidence = result.get("confidence", 0.5)
    fake_prob = result.get("fake_probability", 0.5)
    processing_time = result.get("processing_time", 0)
    
    colors = {
        'FAKE': {
            'bg': '#fee2e2',
            'border': '#ef4444',
            'text': '#991b1b',
            'icon': '❌',
            'label': 'LIKELY FAKE NEWS'
        },
        'REAL': {
            'bg': '#d1fae5',
            'border': '#10b981',
            'text': '#065f46',
            'icon': '✅',
            'label': 'LIKELY AUTHENTIC'
        },
        'UNCERTAIN': {
            'bg': '#fef3c7',
            'border': '#f59e0b',
            'text': '#92400e',
            'icon': '⚠️',
            'label': 'UNCERTAIN - NEEDS VERIFICATION'
        }
    }
    
    color = colors.get(prediction, colors['UNCERTAIN'])
    
    st.markdown(f"""
    <div style="
        background: {color['bg']};
        border: 2px solid {color['border']};
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        margin: 20px 0;
    ">
        <span style="font-size: 3rem;">{color['icon']}</span>
        <h2 style="color: {color['text']}; margin: 10px 0;">{color['label']}</h2>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Confidence Score",
            value=f"{confidence * 100:.1f}%",
            delta=None
        )
        st.progress(confidence)
    
    with col2:
        st.metric(
            label="Fake Probability",
            value=f"{fake_prob * 100:.1f}%",
            delta=None
        )
        st.progress(fake_prob)
    
    with col3:
        st.metric(
            label="Processing Time",
            value=f"{processing_time:.2f}s",
            delta=None
        )
        cached = result.get("cached", False)
        if cached:
            st.caption("⚡ From cache")
        else:
            st.caption("🔄 Fresh analysis")
    
    _display_probability_gauge(fake_prob, color['border'])

def _display_probability_gauge(fake_prob: float, accent_color: str) -> None:
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=fake_prob * 100,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Fake News Probability", 'font': {'size': 18}},
        number={'suffix': '%', 'font': {'size': 40}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkgray"},
            'bar': {'color': accent_color, 'thickness': 0.3},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 30], 'color': '#d1fae5'},
                {'range': [30, 70], 'color': '#fef3c7'},
                {'range': [70, 100], 'color': '#fee2e2'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 70
            }
        }
    ))
    
    fig.update_layout(
        height=280,
        margin=dict(l=30, r=30, t=50, b=30),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    st.plotly_chart(fig, use_container_width=True)

def display_quick_verdict(result: Dict[str, Any]) -> None:
    
    prediction = result.get("prediction", "UNCERTAIN")
    fake_prob = result.get("fake_probability", 0.5)
    
    icons = {'FAKE': '❌', 'REAL': '✅', 'UNCERTAIN': '⚠️'}
    colors = {'FAKE': 'red', 'REAL': 'green', 'UNCERTAIN': 'orange'}
    
    st.markdown(
        f"<span style='color: {colors.get(prediction, 'gray')}'>"
        f"{icons.get(prediction, '❓')} {prediction} ({fake_prob*100:.0f}%)</span>",
        unsafe_allow_html=True
    )
