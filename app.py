import streamlit as st
import requests
from datetime import date, timedelta

CUBS_TEAM_ID = 112
MLB_API_BASE = "https://statsapi.mlb.com/api/v1"


# ── API helpers ──────────────────────────────────────────────────────────────

def get_cubs_games(game_date: date) -> list:
    """Return all Cubs games on a given date (handles doubleheaders)."""
    url = f"{MLB_API_BASE}/schedule"
    params = {
        "teamId": CUBS_TEAM_ID,
        "date": game_date.strftime("%Y-%m-%d"),
        "sportId": 1,
        "hydrate": "linescore,decisions",
    }
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    dates = data.get("dates", [])
    if not dates:
        return []
    return dates[0].get("games", [])


def get_cubs_record(season: int) -> str:
    """Fetch the Cubs' season record."""
    url = f"{MLB_API_BASE}/teams/{CUBS_TEAM_ID}/stats"
    params = {
        "stats": "season",
        "season": season,
    }
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    stats = data.get("stats", [])
    if stats:
        stat = stats[0].get("splits", [])[0].get("stat", {})
        wins = stat.get("wins", 0)
        losses = stat.get("losses", 0)
        return f"{wins}-{losses}"
    return "N/A"


# ── Parsing ──────────────────────────────────────────────────────────────────

def parse_game(game: dict) -> dict:
    """Extract the key fields from a scheduled game entry."""
    teams = game.get("teams", {})
    home = teams.get("home", {})
    away = teams.get("away", {})

    home_id = home.get("team", {}).get("id")
    cubs_are_home = home_id == CUBS_TEAM_ID

    home_name = home.get("team", {}).get("name", "Home")
    away_name = away.get("team", {}).get("name", "Away")
    home_score = home.get("score", 0)
    away_score = away.get("score", 0)

    cubs_score = home_score if cubs_are_home else away_score
    opp_score = away_score if cubs_are_home else home_score
    opp_name = away_name if cubs_are_home else home_name

    cubs_won = cubs_score > opp_score

    # Decisions
    decisions = game.get("decisions", {})
    winner = decisions.get("winner", {}).get("fullName")
    loser = decisions.get("loser", {}).get("fullName")
    save = decisions.get("save", {}).get("fullName")

    return {
        "game_pk": game.get("gamePk"),
        "status": game.get("status", {}).get("abstractGameState", ""),
        "detailed_status": game.get("status", {}).get("detailedState", ""),
        "cubs_are_home": cubs_are_home,
        "home_name": home_name,
        "away_name": away_name,
        "home_score": home_score,
        "away_score": away_score,
        "cubs_score": cubs_score,
        "opp_score": opp_score,
        "opp_name": opp_name,
        "cubs_won": cubs_won,
        "winner": winner,
        "loser": loser,
        "save": save,
        "linescore": game.get("linescore", {}),
    }


def build_linescore_html(linescore: dict, home_name: str, away_name: str) -> str:
    """Render the linescore as a self-contained HTML table (no scrollbar, grey R/H/E)."""
    innings = linescore.get("innings", [])
    num_innings = max(len(innings), 9)

    home_runs: list = [""] * num_innings
    away_runs: list = [""] * num_innings

    for inn in innings:
        idx = inn.get("num", 1) - 1
        if idx < num_innings:
            hr = inn.get("home", {}).get("runs")
            ar = inn.get("away", {}).get("runs")
            home_runs[idx] = str(hr) if hr is not None else "X"
            away_runs[idx] = str(ar) if ar is not None else "X"

    home_runs = [r if r != "" else "-" for r in home_runs]
    away_runs = [r if r != "" else "-" for r in away_runs]

    totals_home = linescore.get("teams", {}).get("home", {})
    totals_away = linescore.get("teams", {}).get("away", {})

    def td(val, extra_class=""):
        cls = f' class="{extra_class}"' if extra_class else ""
        return f"<td{cls}>{val}</td>"

    def row(team_name, runs, totals):
        cells = f'<td class="team">{team_name}</td>'
        cells += "".join(td(r) for r in runs)
        cells += td(totals.get("runs", ""), "rhe")
        cells += td(totals.get("hits", ""), "rhe")
        cells += td(totals.get("errors", ""), "rhe")
        return f"<tr>{cells}</tr>"

    inning_headers = "".join(f"<th>{i + 1}</th>" for i in range(num_innings))
    header_row = f'<tr><th class="team"></th>{inning_headers}<th class="rhe-h">R</th><th class="rhe-h">H</th><th class="rhe-h">E</th></tr>'
    away_row = row(away_name, away_runs, totals_away)
    home_row = row(home_name, home_runs, totals_home)

    return f"""
<style>
  .ls {{
    width: 100%;
    table-layout: fixed;
    border-collapse: collapse;
    font-size: 0.83rem;
    font-family: monospace;
  }}
  .ls th, .ls td {{
    text-align: center;
    padding: 5px 3px;
    border: 1px solid #e0e0e0;
    white-space: nowrap;
    overflow: hidden;
  }}
  .ls .team {{
    text-align: left;
    font-weight: 600;
    padding-left: 8px;
    width: 22%;
    text-overflow: ellipsis;
  }}
  .ls th {{
    background-color: #f0f0f0;
    font-weight: 600;
  }}
  .ls .rhe-h {{
    background-color: #c8c8c8;
    font-weight: 700;
  }}
  .ls .rhe {{
    background-color: #e0e0e0;
    font-weight: 700;
  }}
</style>
<table class="ls">
  <thead>{header_row}</thead>
  <tbody>{away_row}{home_row}</tbody>
</table>
"""


# ── Rendering ────────────────────────────────────────────────────────────────

def render_game(info: dict, game_num: int | None = None):
    """Render a single game result with box score."""
    label = f"Game {game_num}" if game_num else ""
    status = info["status"]
    cubs_won = info["cubs_won"]

    # Header
    if status == "Final":
        if cubs_won:
            st.markdown(f"<div style='background-color: #d4edda; color: #155724; padding: 10px; border-radius: 5px; border: 1px solid #c3e6cb;'>### ✅ {label} — Cubs win! <span style='background-color: white; border: 1px solid #ddd; padding: 2px 5px; margin-left: 10px; display: inline-block;'><span style='color: navy; font-weight: bold;'>W</span></span></div>", unsafe_allow_html=True)
        else:
            st.error(f"### ❌ {label} — Cubs lose.")
    else:
        st.warning(
            f"### ⏳ {label} — {info['detailed_status']}"
        )

    # Score summary
    col1, col2, col3 = st.columns([2, 1, 2])
    with col1:
        st.metric(info["away_name"], info["away_score"])
    with col2:
        st.markdown("<div style='text-align:center;padding-top:1rem;font-size:1.4rem'>vs</div>", unsafe_allow_html=True)
    with col3:
        st.metric(info["home_name"], info["home_score"])

    # Linescore table
    linescore = info.get("linescore", {})
    if linescore.get("innings"):
        st.markdown("**Linescore**")
        st.html(build_linescore_html(linescore, info["home_name"], info["away_name"]))

    # Decisions
    if status == "Final":
        dec_col1, dec_col2, dec_col3 = st.columns(3)
        if info["winner"]:
            dec_col1.markdown(f"**W:** {info['winner']}")
        if info["loser"]:
            dec_col2.markdown(f"**L:** {info['loser']}")
        if info["save"]:
            dec_col3.markdown(f"**SV:** {info['save']}")

    # Location note
    location = "at Wrigley Field" if info["cubs_are_home"] else f"@ {info['opp_name']}"
    st.caption(location)


# ── Main app ─────────────────────────────────────────────────────────────────

st.set_page_config(page_title="Did the Cubs Win?", page_icon="⚾", layout="centered")
st.title("⚾ Did the Cubs Win Last Night?")

yesterday = date.today() - timedelta(days=1)
season = 2023  # Use 2023 for testing as 2026 data may not be available
st.caption(f"Checking results for **{yesterday.strftime('%A, %B %d, %Y')}**")

# Fetch and display season record
try:
    record = get_cubs_record(season)
    st.caption(f"Season record: {record}")
except requests.RequestException:
    st.caption("Season record: Unable to fetch")

st.divider()

with st.spinner("Fetching game data..."):
    try:
        games = get_cubs_games(yesterday)
    except requests.RequestException as e:
        st.error(f"Could not reach the MLB API: {e}")
        st.stop()

if not games:
    st.info("🏖️ The Cubs did not play last night.")
    st.stop()

parsed = [parse_game(g) for g in games]
is_doubleheader = len(parsed) > 1

if is_doubleheader:
    wins = sum(1 for g in parsed if g["status"] == "Final" and g["cubs_won"])
    losses = sum(1 for g in parsed if g["status"] == "Final" and not g["cubs_won"])
    st.subheader(f"🎽 Doubleheader Day!  —  Cubs went {wins}–{losses}")
    st.divider()

for i, info in enumerate(parsed):
    render_game(info, game_num=(i + 1) if is_doubleheader else None)
    if is_doubleheader and i < len(parsed) - 1:
        st.divider()
