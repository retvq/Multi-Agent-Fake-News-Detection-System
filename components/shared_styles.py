SHARED_CSS = """
<style>
    .stApp {
        background-color: #f4f6f8 !important;
    }
    
    .main-header {
        color: #1a1a1a !important;
        -webkit-text-fill-color: #1a1a1a !important;
        font-size: 2.2rem;
        font-weight: 700;
        text-align: left;
        margin-bottom: 0.5rem;
        margin-top: 0;
    }
    
    .logo-symbol {
        font-size: 5rem;
        color: #00838f;
        margin-bottom: 0.3rem;
        display: inline-block;
        animation: spin-slow 2.5s cubic-bezier(0, 0.5, 0.2, 1) forwards;
        filter: drop-shadow(0 0 10px rgba(0, 131, 143, 0.4));
    }
    
    @keyframes spin-slow {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    .sidebar-logo {
        display: inline-block;
        animation: spin-slow-sidebar 2.5s cubic-bezier(0, 0.5, 0.2, 1) forwards;
    }
    
    @keyframes spin-slow-sidebar {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    .sub-header {
        text-align: left;
        color: #666;
        font-size: 1.1rem;
        margin-bottom: 1.5rem;
    }
    
    .sidebar-branding {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: #00838f;
        font-weight: 600;
        font-size: 1.1rem;
        padding: 0.5rem 0;
    }
    
    .stButton > button[kind="primary"] {
        background-color: #00838f !important;
        border-color: #00838f !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        background-color: #006064 !important;
        border-color: #006064 !important;
    }
    
    .stProgress > div > div {
        background-color: #00838f !important;
    }
    
    .verdict-fake {
        background: rgba(220, 38, 38, 0.15);
        color: #dc2626;
        border: 1px solid rgba(220, 38, 38, 0.3);
        box-shadow: 0 0 15px rgba(220, 38, 38, 0.2);
        padding: 20px;
        border-radius: 16px;
        text-align: center;
    }
    
    .verdict-real {
        background: rgba(22, 163, 74, 0.15);
        color: #16a34a;
        border: 1px solid rgba(22, 163, 74, 0.3);
        box-shadow: 0 0 15px rgba(22, 163, 74, 0.2);
        padding: 20px;
        border-radius: 16px;
        text-align: center;
    }
    
    .verdict-uncertain {
        background: rgba(234, 179, 8, 0.15);
        color: #ca8a04;
        border: 1px solid rgba(234, 179, 8, 0.3);
        box-shadow: 0 0 15px rgba(234, 179, 8, 0.2);
        padding: 20px;
        border-radius: 16px;
        text-align: center;
    }
    
    .info-card {
        background: rgba(0, 131, 143, 0.03);
        border: 1px solid rgba(0, 131, 143, 0.1);
        border-radius: 12px;
        padding: 16px;
        margin: 8px 0;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
"""

def inject_styles():
    import streamlit as st
    st.markdown(SHARED_CSS, unsafe_allow_html=True)

def render_sidebar_branding():
    import streamlit as st
    st.markdown("""
    <div class="sidebar-branding">
        <span class="sidebar-logo" style="font-size: 1.8rem;">⊹</span>
        <span>Fake News Detector</span>
    </div>
    """, unsafe_allow_html=True)
