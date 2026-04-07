import streamlit as st

st.set_page_config(
    page_title="Cubs Win Checker",
    page_icon="⚾",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
  [data-testid="stSidebar"],
  [data-testid="stSidebarCollapseButton"] {
      display: none !important;
  }
</style>
""", unsafe_allow_html=True)

home_page    = st.Page("pages/home.py",           title="Home",           icon="🏠")
pitcher_page = st.Page("pages/pitcher_report.py", title="Pitcher Report", icon="⚾")

pg = st.navigation([home_page, pitcher_page], position="hidden")
pg.run()
