import streamlit as st
from utils import TABLE_CSS

st.set_page_config(page_title="Cubs Win Checker", page_icon="⚾", layout="wide")

st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;600;700;900&family=JetBrains+Mono:wght@400;600&display=swap');

  /* ── App background ──────────────────────────────────────────── */
  .stApp,
  [data-testid="stAppViewContainer"],
  [data-testid="stMain"],
  [data-testid="stHeader"],
  [data-testid="stBottom"] {
      background-color: #0A0A0F !important;
  }

  /* ── Base text ───────────────────────────────────────────────── */
  .stApp, [data-testid="stMain"], .stMarkdown {
      color: #e8e8f0 !important;
  }

  /* ── Headings ────────────────────────────────────────────────── */
  h1, h2, h3, h4 {
      color: #e8e8f0 !important;
      font-family: 'Barlow Condensed', system-ui, sans-serif !important;
      letter-spacing: 0.02em !important;
  }
  h1 { font-size: 2rem !important; font-weight: 700 !important; }
  h2 { font-size: 1.4rem !important; font-weight: 700 !important; }
  h3 { font-size: 1.1rem !important; font-weight: 700 !important; }

  /* ── Main content padding ────────────────────────────────────── */
  [data-testid="stMainBlockContainer"] {
      padding-top: 2rem !important;
      max-width: 900px !important;
  }

  /* ── Divider ─────────────────────────────────────────────────── */
  [data-testid="stDivider"] hr, hr {
      border-color: #1a1a2e !important;
  }

  /* ── Caption ─────────────────────────────────────────────────── */
  [data-testid="stCaptionContainer"] p,
  .stCaption p {
      color: #555 !important;
      font-size: 0.78rem !important;
      letter-spacing: 0.04em !important;
  }

  /* ── Metric card ─────────────────────────────────────────────── */
  [data-testid="stMetric"] {
      background: #0D0D1A !important;
      border: 1px solid #1a1a2e !important;
      border-radius: 10px !important;
      padding: 12px 16px !important;
  }
  [data-testid="stMetricLabel"] > div {
      color: #555 !important;
      font-size: 0.65rem !important;
      letter-spacing: 0.12em !important;
      text-transform: uppercase !important;
      font-family: 'Barlow Condensed', system-ui, sans-serif !important;
  }
  [data-testid="stMetricValue"] > div {
      color: #e8e8f0 !important;
      font-family: 'Barlow Condensed', system-ui, sans-serif !important;
      font-size: 1.6rem !important;
      font-weight: 700 !important;
  }

  /* ── Alerts ──────────────────────────────────────────────────── */
  [data-testid="stAlertContainer"] {
      background: #0D0D1A !important;
      border-radius: 10px !important;
      border: 1px solid #1a1a2e !important;
      border-left: 3px solid #0E3386 !important;
  }
  [data-testid="stAlertContainer"] p,
  [data-testid="stAlertContainer"] span,
  [data-testid="stAlertContainer"] div {
      color: #e8e8f0 !important;
  }

  /* ── Spinner ─────────────────────────────────────────────────── */
  [data-testid="stSpinner"] p {
      color: #555 !important;
  }

  /* ── Expander ────────────────────────────────────────────────── */
  [data-testid="stExpander"] {
      background: #0D0D1A !important;
      border: 1px solid #1a1a2e !important;
      border-radius: 10px !important;
  }
  [data-testid="stExpander"] summary,
  [data-testid="stExpander"] p,
  [data-testid="stExpander"] span {
      color: #e8e8f0 !important;
  }
  [data-testid="stExpander"] svg {
      fill: #555 !important;
  }
  [data-testid="stExpander"] summary:hover {
      color: #e8e8f0 !important;
  }

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
      color: #555 !important;
      border-radius: 7px !important;
      font-family: 'Barlow Condensed', system-ui, sans-serif !important;
      font-size: 0.95rem !important;
      letter-spacing: 0.06em !important;
  }
  .stTabs [aria-selected="true"][data-baseweb="tab"] {
      background: #0E3386 !important;
      color: #fff !important;
  }
  .stTabs [data-baseweb="tab-border"],
  .stTabs [data-baseweb="tab-highlight"] {
      display: none !important;
  }

  /* ── Sidebar ─────────────────────────────────────────────────── */
  [data-testid="stSidebar"] {
      background: #0D0D1A !important;
      border-right: 1px solid #1a1a2e !important;
      box-shadow: none !important;
  }
  [data-testid="stSidebar"] > div:first-child {
      padding: 0 !important;
  }
  [data-testid="stSidebarNav"]::before {
      content: "⚾  Cubs Win Checker";
      display: block;
      color: #e8e8f0;
      font-size: 1.1rem;
      font-weight: 800;
      letter-spacing: 0.04em;
      font-family: 'Barlow Condensed', system-ui, sans-serif;
      padding: 1.5rem 1.25rem 1rem 1.25rem;
      border-bottom: 1px solid #1a1a2e;
      margin-bottom: 0.65rem;
  }
  [data-testid="stSidebarNav"] {
      padding: 0 0.75rem;
  }
  [data-testid="stSidebarNavLink"] {
      color: #555 !important;
      border-radius: 10px !important;
      padding: 0.55rem 0.9rem !important;
      margin-bottom: 4px;
      font-size: 0.9rem !important;
      font-weight: 600 !important;
      font-family: 'Barlow Condensed', system-ui, sans-serif !important;
      letter-spacing: 0.06em !important;
      transition: background 0.15s ease, color 0.15s ease !important;
  }
  [data-testid="stSidebarNavLink"]:hover {
      background-color: #1a1a2e !important;
      color: #aaa !important;
  }
  [data-testid="stSidebarNavLink"][aria-selected="true"] {
      background-color: #0E3386 !important;
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

  /* ── Sidebar generic text ────────────────────────────────────── */
  [data-testid="stSidebar"] p,
  [data-testid="stSidebar"] span,
  [data-testid="stSidebar"] label,
  [data-testid="stSidebar"] li {
      color: #555 !important;
  }

  /* ── Stat tables (linescore, pitch usage, pitch comparison) ──── */
  {TABLE_CSS}
</style>
""", unsafe_allow_html=True)

cubs_page    = st.Page("pages/cubs.py",    title="Did the Cubs Win?", icon="🐻")
my_team_page = st.Page("pages/my_team.py", title="Did My Team Win?",  icon="⚾")

pg = st.navigation([cubs_page, my_team_page])
pg.run()
