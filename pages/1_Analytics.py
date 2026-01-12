

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
from components.shared_styles import inject_styles, render_sidebar_branding

st.set_page_config(
    page_title="Analytics - Fake News Detection",
    page_icon="⊹",
    layout="wide"
)

inject_styles()

with st.sidebar:
    render_sidebar_branding()

st.markdown('<div class="logo-symbol">⊹</div>', unsafe_allow_html=True)
st.markdown('<h1 class="main-header">Analytics & History</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">View your session statistics and prediction history</p>', unsafe_allow_html=True)

if 'metrics_tracker' not in st.session_state:
    st.warning("No session data available. Please analyze some articles first.")
    st.info("Go to the main page to start analyzing articles.")
    st.stop()

st.header("Session Statistics")

stats = st.session_state.metrics_tracker.get_prediction_stats()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Analyses",
        stats['total_predictions'],
        help="Total number of articles analyzed this session"
    )

with col2:
    st.metric(
        "Average Confidence",
        f"{stats['avg_confidence'] * 100:.1f}%",
        help="Average confidence across all predictions"
    )

with col3:
    st.metric(
        "Cache Hit Rate",
        f"{stats['cache_hit_rate']:.1f}%",
        help="Percentage of queries served from cache"
    )

with col4:
    st.metric(
        "Avg Processing Time",
        f"{stats['avg_latency']:.2f}s",
        help="Average time to complete an analysis"
    )

if stats['total_predictions'] > 0:
    st.header("Prediction Distribution")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = go.Figure(data=[go.Pie(
            labels=['Fake', 'Real', 'Uncertain'],
            values=[
                stats['fake_count'],
                stats['real_count'],
                stats['uncertain_count']
            ],
            hole=0.4,
            marker_colors=['#ef4444', '#10b981', '#f59e0b']
        )])
        
        fig.update_layout(
            title="Verdict Distribution",
            showlegend=True,
            height=350
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = go.Figure(data=[
            go.Bar(
                x=['Fake', 'Real', 'Uncertain'],
                y=[stats['fake_count'], stats['real_count'], stats['uncertain_count']],
                marker_color=['#ef4444', '#10b981', '#f59e0b']
            )
        ])
        
        fig.update_layout(
            title="Prediction Counts",
            xaxis_title="Verdict",
            yaxis_title="Count",
            height=350
        )
        
        st.plotly_chart(fig, use_container_width=True)

st.header("Model Usage")

model_usage = st.session_state.metrics_tracker.get_model_usage()

if model_usage:
    models = list(model_usage.keys())
    counts = list(model_usage.values())
    
    model_names = {
        'heuristic': 'Heuristic',
        'huggingface': 'HuggingFace',
        'gemini': 'Gemini',
        'groq': 'Groq'
    }
    
    display_names = [model_names.get(m, m) for m in models]
    
    fig = go.Figure(data=[
        go.Bar(
            x=display_names,
            y=counts,
            marker_color=['#3b82f6', '#8b5cf6', '#ec4899', '#10b981'][:len(models)]
        )
    ])
    
    fig.update_layout(
        title="Model Usage Breakdown",
        xaxis_title="Model",
        yaxis_title="Times Used",
        height=300
    )
    
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No model usage data yet.")

st.header("Recent Predictions")

recent = st.session_state.metrics_tracker.get_recent_predictions(limit=10)

if recent:
    df = pd.DataFrame(recent)
    
    df['Time'] = pd.to_datetime(df['timestamp']).dt.strftime('%H:%M:%S')
    df['Verdict'] = df['prediction'].apply(
        lambda x: f"[{'FAKE' if x == 'FAKE' else 'REAL' if x == 'REAL' else '?'}] {x}"
    )
    df['Fake %'] = df['fake_probability'].apply(lambda x: f"{x * 100:.0f}%")
    df['Conf %'] = df['confidence'].apply(lambda x: f"{x * 100:.0f}%")
    df['Latency'] = df['processing_time'].apply(
        lambda x: f"{x * 1000:.0f}ms" if x < 1 else f"{x:.2f}s"
    )
    df['Cached'] = df['cached'].apply(lambda x: "Yes" if x else "No")
    df['Preview'] = df['text_preview'].apply(lambda x: x[:50] + "..." if len(x) > 50 else x)
    
    display_df = df[['Time', 'Verdict', 'Fake %', 'Conf %', 'Latency', 'Cached', 'Preview']]
    
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )
    
    with st.expander("View Full Details"):
        for i, pred in enumerate(recent[:5]):
            st.markdown(f"**{i+1}. {pred['prediction']}** ({pred['fake_probability']*100:.0f}% fake)")
            st.caption(pred['text_preview'])
            st.caption(f"Models: {', '.join(pred['models_used'])}")
            st.divider()
else:
    st.info("No predictions recorded yet. Analyze some articles to see history here.")

st.header("Performance Metrics")

latency = st.session_state.metrics_tracker.get_latency_percentiles()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("P50 Latency", f"{latency['p50'] * 1000:.0f}ms")
with col2:
    st.metric("P95 Latency", f"{latency['p95'] * 1000:.0f}ms")
with col3:
    st.metric("P99 Latency", f"{latency['p99'] * 1000:.0f}ms")

if len(list(st.session_state.metrics_tracker.predictions)) > 3:
    latencies = [p.processing_time for p in st.session_state.metrics_tracker.predictions]
    
    fig = go.Figure(data=[go.Histogram(
        x=latencies,
        nbinsx=20,
        marker_color='#3b82f6'
    )])
    
    fig.update_layout(
        title="Latency Distribution",
        xaxis_title="Processing Time (seconds)",
        yaxis_title="Count",
        height=300
    )
    
    st.plotly_chart(fig, use_container_width=True)

if len(list(st.session_state.metrics_tracker.predictions)) > 3:
    st.header("Confidence Distribution")
    
    confidences = [p.confidence for p in st.session_state.metrics_tracker.predictions]
    
    fig = go.Figure(data=[go.Histogram(
        x=confidences,
        nbinsx=10,
        marker_color='#10b981'
    )])
    
    fig.update_layout(
        title="Confidence Score Distribution",
        xaxis_title="Confidence",
        yaxis_title="Count",
        height=300
    )
    
    st.plotly_chart(fig, use_container_width=True)

st.divider()
session_info = st.session_state.metrics_tracker.get_session_info()
st.caption(f"Session started: {session_info['session_start']} | Uptime: {session_info['uptime']}")
