import streamlit as st

st.set_page_config(
    page_title="HR Attrition Analytics",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── SHARED STYLES ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
  /* Font & base */
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

  /* Hide default Streamlit chrome */
  #MainMenu, footer, header { visibility: hidden; }
  .block-container { padding-top: 2rem; padding-bottom: 2rem; }

  /* Metric cards */
  [data-testid="metric-container"] {
    background: #1a1a2e;
    border: 1px solid #2a2a4a;
    border-radius: 12px;
    padding: 1rem 1.25rem;
  }
  [data-testid="metric-container"] label {
    color: #8888aa !important;
    font-size: 0.78rem !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
  }
  [data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-size: 1.8rem !important;
    font-weight: 800 !important;
    color: #f0f0f5 !important;
  }
  [data-testid="metric-container"] [data-testid="stMetricDelta"] {
    font-size: 0.8rem !important;
  }

  /* Sidebar */
  [data-testid="stSidebar"] {
    background: #111118;
    border-right: 1px solid #2a2a3a;
  }

  /* Section headers */
  .section-header {
    font-size: 1.4rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    color: #f0f0f5;
    margin-bottom: 0.25rem;
  }
  .section-sub {
    font-size: 0.875rem;
    color: #8888aa;
    margin-bottom: 1.5rem;
  }

  /* Accent pill */
  .pill {
    display: inline-block;
    padding: 0.2rem 0.75rem;
    border-radius: 100px;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
  }
  .pill-red    { background: rgba(239,68,68,0.15);  color: #ef4444; }
  .pill-green  { background: rgba(16,185,129,0.15); color: #10b981; }
  .pill-yellow { background: rgba(245,158,11,0.15); color: #f59e0b; }
  .pill-purple { background: rgba(124,58,237,0.15); color: #7c3aed; }

  /* Finding box */
  .finding-box {
    background: #1a1a2e;
    border: 1px solid #2a2a3a;
    border-left: 3px solid #e84393;
    border-radius: 8px;
    padding: 0.875rem 1.25rem;
    margin-bottom: 0.75rem;
    font-size: 0.9rem;
    color: #c0c0d8;
    line-height: 1.6;
  }

  /* Risk score display */
  .risk-score-display {
    text-align: center;
    padding: 2rem;
    border-radius: 16px;
    border: 2px solid;
    margin-bottom: 1.5rem;
  }
  .risk-score-number {
    font-size: 4rem;
    font-weight: 900;
    letter-spacing: -0.04em;
    line-height: 1;
  }
  .risk-score-label {
    font-size: 1rem;
    font-weight: 700;
    margin-top: 0.5rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
  }
</style>
""", unsafe_allow_html=True)

# ── SIDEBAR NAV ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🎯 HR Analytics")
    st.markdown("<span style='color:#8888aa;font-size:0.8rem'>Employee Retention Intelligence</span>",
                unsafe_allow_html=True)
    st.divider()
    st.markdown("""
<div style='font-size:0.78rem;color:#8888aa;line-height:1.7'>
  Analyzes attrition patterns across <b style='color:#c0c0d8'>1,470 employees</b>
  to identify flight risk, quantify financial impact, and model the ROI of
  retention programs.<br><br>
  Use the <b style='color:#c0c0d8'>Dashboard</b> for an executive overview,
  the <b style='color:#c0c0d8'>Risk Calculator</b> to score any employee profile,
  or the <b style='color:#c0c0d8'>ROI Modeler</b> to build a business case for
  retention investment.
</div>
""", unsafe_allow_html=True)
    st.divider()

    page = st.radio(
        "Navigate",
        ["📊 Executive Dashboard", "🎯 Risk Calculator", "💰 ROI Scenario Modeler"],
        label_visibility="collapsed",
    )

    st.divider()
    st.markdown("<span style='color:#8888aa;font-size:0.75rem'>Dataset: IBM HR Analytics<br/>1,470 employees · 35 features</span>",
                unsafe_allow_html=True)
# ── ROUTE ─────────────────────────────────────────────────────────────────────
if page == "📊 Executive Dashboard":
    from pages_src.dashboard import show
elif page == "🎯 Risk Calculator":
    from pages_src.risk_calculator import show
else:
    from pages_src.roi_modeler import show

show()
