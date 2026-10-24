"""KhetPlan entry point: landing page first, then the farm planning dashboard.

Run:  streamlit run app.py
  /     landing page (landing.py)
  /app  dashboard with voice input, 3D twin, what-if lab, risk lab and report (dashboard.py)
"""
import streamlit as st

pages = [
    st.Page("landing.py", title="KhetPlan", icon="🌱", default=True),
    st.Page("dashboard.py", title="KhetPlan · Farm digital twin", icon="🌱", url_path="app"),
]
st.navigation(pages, position="hidden").run()
