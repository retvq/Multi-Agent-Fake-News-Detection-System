

import streamlit as st
from typing import Dict, Any, List
from datetime import datetime

def display_system_health(health_data: Dict[str, Any]) -> None:
    
    overall_status = health_data.get('overall_status', 'unknown')
    
    if overall_status == 'healthy':
        st.success("**System Status: Healthy** - All services operational")
    elif overall_status == 'degraded':
        st.warning("**System Status: Degraded** - Running with limited models")
    else:
        st.error("**System Status: Critical** - Service unavailable")
    
    st.subheader("Component Status")
    
    cols = st.columns(3)
    
    hf_data = health_data.get('huggingface', {})
    with cols[0]:
        _render_component_card(
            name="HuggingFace API",
            icon="HF",
            status=hf_data.get('status', 'unavailable'),
            quota=hf_data.get('quota', {}),
            last_success=hf_data.get('last_success'),
            success_rate=hf_data.get('success_rate', 0),
            avg_latency=hf_data.get('avg_latency', 0)
        )
    
    together_data = health_data.get('together', {})
    with cols[1]:
        _render_component_card(
            name="Together.ai API",
            icon="G",
            status=together_data.get('status', 'unavailable'),
            quota=together_data.get('quota', {}),
            last_success=together_data.get('last_success'),
            success_rate=together_data.get('success_rate', 0),
            avg_latency=together_data.get('avg_latency', 0)
        )
    
    with cols[2]:
        _render_component_card(
            name="Heuristic Analyzer",
            icon="H",
            status='healthy',
            quota=None,
            last_success=None,
            success_rate=100,
            avg_latency=0.001
        )

def _render_component_card(
    name: str,
    icon: str,
    status: str,
    quota: Dict[str, Any] = None,
    last_success: str = None,
    success_rate: float = 100,
    avg_latency: float = 0
) -> None:
    
    status_colors = {
        'healthy': ('#d1fae5', '#065f46', '+'),
        'unavailable': ('#f3f4f6', '#6b7280', 'o'),
        'error': ('#fee2e2', '#991b1b', 'x')
    }
    
    bg, text, badge = status_colors.get(status, status_colors['unavailable'])
    
    st.markdown(f, unsafe_allow_html=True)
    
    if quota:
        used = quota.get('used', 0)
        total = quota.get('total', 1)
        pct = quota.get('percentage', 0)
        
        st.caption(f"Quota: {used:,}/{total:,}")
        
        if pct >= 90:
            st.error("Quota almost exhausted!")
        elif pct >= 80:
            st.warning("High quota usage")
        
        st.progress(min(pct / 100, 1.0))
    
    if status == 'healthy':
        st.caption(f"Success rate: {success_rate:.1f}%")
        if avg_latency > 0:
            lat_str = f"{avg_latency * 1000:.0f}ms" if avg_latency < 1 else f"{avg_latency:.2f}s"
            st.caption(f"Avg latency: {lat_str}")

def display_quota_management(
    hf_quota: Dict[str, Any],
    together_quota: Dict[str, Any]
) -> None:
    
    st.subheader("API Quota Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### HuggingFace")
        _render_quota_card(hf_quota, "HuggingFace")
    
    with col2:
        st.markdown("### Gemini/Groq")
        _render_quota_card(together_quota, "Together.ai")

def _render_quota_card(quota: Dict[str, Any], name: str) -> None:
    
    used = quota.get('used', 0)
    total = quota.get('total', 1)
    remaining = quota.get('remaining', total)
    pct = quota.get('percentage', 0)
    reset_date = quota.get('reset_date', 'Unknown')
    
    if pct >= 90:
        st.error(f"Critical: {pct:.1f}% used")
    elif pct >= 80:
        st.warning(f"Warning: {pct:.1f}% used")
    elif pct >= 50:
        st.info(f"Moderate: {pct:.1f}% used")
    else:
        st.success(f"Healthy: {pct:.1f}% used")
    
    st.progress(min(pct / 100, 1.0))
    
    st.metric("Used Today", f"{used:,}")
    st.metric("Remaining", f"{remaining:,}")
    st.caption(f"Daily limit: {total:,}")
    st.caption(f"Resets: {reset_date}")

def display_error_log(errors: List[Dict[str, Any]]) -> None:
    
    st.subheader("Error Log")
    
    if not errors:
        st.info("No errors recorded in this session.")
        return
    
    col1, col2 = st.columns([1, 3])
    with col1:
        severity_filter = st.selectbox(
            "Filter by severity",
            ["All", "ERROR", "WARNING", "INFO"]
        )
    
    if severity_filter != "All":
        errors = [e for e in errors if e.get('severity') == severity_filter]
    
    for error in errors[:20]:
        timestamp = error.get('timestamp', 'Unknown')
        severity = error.get('severity', 'ERROR')
        message = error.get('message', 'Unknown error')
        component = error.get('component', 'Unknown')
        
        try:
            dt = datetime.fromisoformat(timestamp)
            timestamp = dt.strftime("%H:%M:%S")
        except:
            pass
        
        if severity == 'ERROR':
            st.error(f"**{timestamp}** [{component}] {message}")
        elif severity == 'WARNING':
            st.warning(f"**{timestamp}** [{component}] {message}")
        else:
            st.info(f"**{timestamp}** [{component}] {message}")

def display_performance_metrics(stats: Dict[str, Any]) -> None:
    
    st.subheader("Performance Metrics")
    
    latency = stats.get('latency', {})
    session = stats.get('session', {})
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        p50 = latency.get('p50', 0)
        st.metric("P50 Latency", f"{p50 * 1000:.0f}ms" if p50 < 1 else f"{p50:.2f}s")
    
    with col2:
        p95 = latency.get('p95', 0)
        st.metric("P95 Latency", f"{p95 * 1000:.0f}ms" if p95 < 1 else f"{p95:.2f}s")
    
    with col3:
        p99 = latency.get('p99', 0)
        st.metric("P99 Latency", f"{p99 * 1000:.0f}ms" if p99 < 1 else f"{p99:.2f}s")
    
    with col4:
        throughput = session.get('predictions_per_hour', 0)
        st.metric("Throughput", f"{throughput:.1f}/hr")
    
    st.caption(f"Session uptime: {session.get('uptime', 'Unknown')}")
