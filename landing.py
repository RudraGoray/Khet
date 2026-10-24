"""Landing page: a full-screen scroll story in front of the dashboard. "Launch KhetPlan" opens dashboard.py."""
import streamlit as st

from khetplan.data import DatasetError, default_dataset
from khetplan.landing_view import landing_payload, render_landing

st.set_page_config(page_title="KhetPlan · Your farm, simulated", page_icon="🌱", layout="wide", initial_sidebar_state="collapsed")
S = st.session_state

# The page is one component iframe pinned to the viewport; it scrolls inside itself.
st.markdown(
    """<style>
header[data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stSidebar"],
[data-testid="stSidebarCollapsedControl"], #MainMenu, footer { display: none !important; }
.stApp, .stMain { background: #F7F6EF; overflow: hidden; }
.block-container { padding: 0 !important; max-width: none !important; }
iframe[title*="khetplan_landing"] { position: fixed; inset: 0; width: 100vw !important; height: 100vh !important;
  height: 100dvh !important; border: 0; z-index: 999990; background: #F7F6EF; }
</style>""",
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def _payload(version: str):
    return landing_payload(default_dataset())


try:
    data = _payload(default_dataset().version)
except (DatasetError, OSError, ValueError):
    data = {"ok": False}

value = render_landing(data)
if value and value.get("action") == "launch" and value.get("nonce") != S.get("landing_nonce"):
    S.landing_nonce = value.get("nonce")
    st.switch_page("dashboard.py")
