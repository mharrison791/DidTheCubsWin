import streamlit as st

st.set_page_config(
    page_title="Did the Cubs Win?",
    page_icon="⚾",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
  /* ── Sidebar shell ─────────────────────────────────────────── */
  [data-testid="stSidebar"] {
      background: linear-gradient(160deg, #0E3386 0%, #09245e 100%) !important;
      border-right: none !important;
      box-shadow: 4px 0 24px rgba(0,0,0,0.35);
  }
  [data-testid="stSidebar"] > div:first-child {
      padding: 0 !important;
  }

  /* ── App title in sidebar ──────────────────────────────────── */
  [data-testid="stSidebarNav"]::before {
      content: "⚾  Cubs Win Checker";
      display: block;
      color: #FFFFFF;
      font-size: 1.45rem;
      font-weight: 800;
      letter-spacing: -0.01em;
      padding: 1.75rem 1.25rem 1rem 1.25rem;
      border-bottom: 1px solid rgba(255,255,255,0.15);
      margin-bottom: 0.65rem;
  }

  /* ── Nav link container ────────────────────────────────────── */
  [data-testid="stSidebarNav"] {
      padding: 0 0.75rem;
  }

  /* ── Nav links (default) ───────────────────────────────────── */
  [data-testid="stSidebarNavLink"] {
      color: #B8CCF0 !important;
      border-radius: 10px !important;
      padding: 0.55rem 0.9rem !important;
      margin-bottom: 4px;
      font-size: 0.95rem !important;
      font-weight: 500 !important;
      transition: background 0.15s ease, color 0.15s ease !important;
  }
  [data-testid="stSidebarNavLink"]:hover {
      background-color: rgba(255,255,255,0.10) !important;
      color: #FFFFFF !important;
  }

  /* ── Active page — red pill ────────────────────────────────── */
  [data-testid="stSidebarNavLink"][aria-selected="true"] {
      background-color: #CC3433 !important;
      color: #FFFFFF !important;
      font-weight: 700 !important;
      box-shadow: 0 2px 10px rgba(204,52,51,0.45);
  }

  /* ── Icons ─────────────────────────────────────────────────── */
  [data-testid="stSidebarNavLink"] svg { fill: #8AAEE0 !important; }
  [data-testid="stSidebarNavLink"][aria-selected="true"] svg { fill: #FFFFFF !important; }

  /* ── Generic sidebar text ──────────────────────────────────── */
  [data-testid="stSidebar"] p,
  [data-testid="stSidebar"] span,
  [data-testid="stSidebar"] label,
  [data-testid="stSidebar"] li,
  [data-testid="stSidebar"] .stMarkdown { color: #DDEAFF !important; }

  /* ── Collapse button ───────────────────────────────────────── */
  [data-testid="stSidebarCollapseButton"] {
      background: rgba(255,255,255,0.08) !important;
      border-radius: 8px !important;
  }
  [data-testid="stSidebarCollapseButton"] svg { fill: #B8CCF0 !important; }
  [data-testid="stSidebarCollapseButton"]:hover {
      background: rgba(255,255,255,0.18) !important;
  }
</style>
""", unsafe_allow_html=True)

cubs_page    = st.Page("pages/cubs.py",    title="Did the Cubs Win?", icon="🐻")
my_team_page = st.Page("pages/my_team.py", title="Did My Team Win?",  icon="⚾")

pg = st.navigation([cubs_page, my_team_page])
pg.run()
