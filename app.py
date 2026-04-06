import streamlit as st

st.set_page_config(page_title="Cubs Dashboard", page_icon="⚾", layout="centered")

home_page    = st.Page("pages/home.py",           title="Home",           icon="🏠")
pitcher_page = st.Page("pages/pitcher_report.py", title="Pitcher Report", icon="⚾")

pg = st.navigation([home_page, pitcher_page])
pg.run()
