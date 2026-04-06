import streamlit as st

st.set_page_config(page_title="Cubs Dashboard", page_icon="⚾", layout="centered")

# Cubs blue sidebar — #0E3386 (primary) / #CC3433 (red accent)
st.markdown("""
<style>
  /* Sidebar background */
  [data-testid="stSidebar"] {
      background-color: #0E3386 !important;
  }

  /* Page nav links (default state) */
  [data-testid="stSidebar"] [data-testid="stSidebarNavLink"] {
      color: #B8CCF0 !important;
      border-radius: 6px;
  }
  [data-testid="stSidebar"] [data-testid="stSidebarNavLink"]:hover {
      background-color: rgba(255,255,255,0.12) !important;
      color: #FFFFFF !important;
  }

  /* Active / selected nav link */
  [data-testid="stSidebar"] [data-testid="stSidebarNavLink"][aria-selected="true"] {
      background-color: #CC3433 !important;
      color: #FFFFFF !important;
      font-weight: 700;
  }

  /* Nav link icons */
  [data-testid="stSidebar"] [data-testid="stSidebarNavLink"] svg {
      fill: #B8CCF0 !important;
  }
  [data-testid="stSidebar"] [data-testid="stSidebarNavLink"][aria-selected="true"] svg {
      fill: #FFFFFF !important;
  }

  /* Any plain text / markdown inside the sidebar */
  [data-testid="stSidebar"] p,
  [data-testid="stSidebar"] span,
  [data-testid="stSidebar"] label,
  [data-testid="stSidebar"] li,
  [data-testid="stSidebar"] .stMarkdown {
      color: #DDEAFF !important;
  }

  /* Sidebar headers */
  [data-testid="stSidebar"] h1,
  [data-testid="stSidebar"] h2,
  [data-testid="stSidebar"] h3 {
      color: #FFFFFF !important;
  }

  /* Collapse / expand arrow button */
  [data-testid="stSidebarCollapseButton"] svg {
      fill: #B8CCF0 !important;
  }
</style>
""", unsafe_allow_html=True)

home_page    = st.Page("pages/home.py",           title="Home",           icon="🏠")
pitcher_page = st.Page("pages/pitcher_report.py", title="Pitcher Report", icon="⚾")

pg = st.navigation([home_page, pitcher_page])
pg.run()
