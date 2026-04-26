import streamlit as st

st.set_page_config(page_title="Cubs Win Checker", page_icon="⚾", layout="wide")

st.markdown("""
<style>
  /* ── App background ──────────────────────────────────────────── */
  .stApp,
  [data-testid="stAppViewContainer"],
  [data-testid="stMain"],
  [data-testid="stHeader"],
  [data-testid="stBottom"] {
      background-color: #0A0A0F !important;
  }

  /* Hide Streamlit's top decoration bar */
  [data-testid="stHeader"] { display: none !important; }

  /* ── Main content: constrain width, pad top ──────────────────── */
  [data-testid="stMainBlockContainer"] {
      padding-top: 2.5rem !important;
      padding-left: 2.5rem !important;
      max-width: 860px !important;
  }

  /* ── Base text ───────────────────────────────────────────────── */
  .stApp, [data-testid="stMain"] { color: #e8e8f0 !important; }
  p, span, div { color: inherit; }

  /* ── Alerts (st.error only, for real errors) ─────────────────── */
  [data-testid="stAlertContainer"] {
      background: #0D0D1A !important;
      border-radius: 10px !important;
      border: 1px solid #1a1a2e !important;
      border-left: 3px solid #CC3433 !important;
  }
  [data-testid="stAlertContainer"] p,
  [data-testid="stAlertContainer"] span { color: #e8e8f0 !important; }

  /* ── Spinner ─────────────────────────────────────────────────── */
  [data-testid="stSpinner"] p { color: #444 !important; }

  /* ── Expander ────────────────────────────────────────────────── */
  [data-testid="stExpander"] {
      background: #0D0D1A !important;
      border: 1px solid #1a1a2e !important;
      border-radius: 10px !important;
  }
  [data-testid="stExpander"] summary,
  [data-testid="stExpander"] p,
  [data-testid="stExpander"] span { color: #e8e8f0 !important; }
  [data-testid="stExpander"] svg { fill: #555 !important; }

  /* ── Tabs ────────────────────────────────────────────────────── */
  .stTabs [data-baseweb="tab-list"] {
      background: #0D0D1A !important;
      border-radius: 10px !important;
      border: 1px solid #1a1a2e !important;
      gap: 4px !important;
      padding: 4px !important;
  }
  .stTabs [data-baseweb="tab"] {
      background: transparent !important;
      color: #aaa !important;
      border-radius: 7px !important;
      font-size: 0.9rem !important;
  }
  .stTabs [aria-selected="true"][data-baseweb="tab"] {
      background: #0E3386 !important;
      color: #fff !important;
  }
  .stTabs [data-baseweb="tab-border"],
  .stTabs [data-baseweb="tab-highlight"] { display: none !important; }

  /* ── Sidebar ─────────────────────────────────────────────────── */
  [data-testid="stSidebar"] {
      background: #0D0D1A !important;
      border-right: 1px solid #1a1a2e !important;
      box-shadow: none !important;
  }
  [data-testid="stSidebar"] > div:first-child { padding: 0 !important; }

  [data-testid="stSidebarNav"]::before {
      content: "⚾  Cubs Win Checker";
      display: block;
      color: #e8e8f0;
      font-size: 1.05rem;
      font-weight: 800;
      letter-spacing: 0.03em;
      font-family: system-ui, sans-serif;
      padding: 1.5rem 1.25rem 1rem 1.25rem;
      border-bottom: 1px solid #1a1a2e;
      margin-bottom: 0.65rem;
  }
  [data-testid="stSidebarNav"] { padding: 0 0.75rem; }

  [data-testid="stSidebarNavLink"] {
      color: #aaa !important;
      border-radius: 10px !important;
      padding: 0.55rem 0.9rem !important;
      margin-bottom: 4px !important;
      font-size: 0.9rem !important;
      font-weight: 600 !important;
      font-family: system-ui, sans-serif !important;
      letter-spacing: 0.04em !important;
      transition: background 0.15s ease, color 0.15s ease !important;
  }
  [data-testid="stSidebarNavLink"]:hover {
      background: #1a1a2e !important;
      color: #aaa !important;
  }
  [data-testid="stSidebarNavLink"][aria-selected="true"] {
      background: #0E3386 !important;
      color: #fff !important;
      font-weight: 700 !important;
      box-shadow: 0 2px 12px rgba(14,51,134,0.35) !important;
  }
  [data-testid="stSidebarNavLink"] svg { fill: #444 !important; }
  [data-testid="stSidebarNavLink"][aria-selected="true"] svg { fill: #fff !important; }

  [data-testid="stSidebarCollapseButton"] {
      background: #1a1a2e !important;
      border-radius: 8px !important;
  }
  [data-testid="stSidebarCollapseButton"] svg { fill: #555 !important; }
  [data-testid="stSidebarCollapseButton"]:hover { background: #0E3386 !important; }
</style>
""", unsafe_allow_html=True)

cubs_page    = st.Page("pages/cubs.py",    title="Did the Cubs Win?", icon="🐻")
my_team_page = st.Page("pages/my_team.py", title="Did My Team Win?",  icon="⚾")

pg = st.navigation([cubs_page, my_team_page])
pg.run()
