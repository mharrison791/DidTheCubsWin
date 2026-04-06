import streamlit as st
import requests
from datetime import date, timedelta

CUBS_TEAM_ID = 112
MLB_API_BASE = "https://statsapi.mlb.com/api/v1"


def get_cubs_game(game_date: date):
    url = f"{MLB_API_BASE}/schedule"
    params = {
        "teamId": CUBS_TEAM_ID,
        "date": game_date.strftime("%Y-%m-%d"),
        "sportId": 1,
        "hydrate": "linescore",
    }
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    dates = data.get("dates", [])
    if not dates:
        return None

    games = dates[0].get("games", [])
    if not games:
        return None

    return games[0]


def parse_result(game):
    status = game.get("status", {}).get("abstractGameState", "")
    teams = game.get("teams", {})
    home = teams.get("home", {})
    away = teams.get("away", {})

    home_team = home.get("team", {}).get("name", "Home")
    away_team = away.get("team", {}).get("name", "Away")
    home_score = home.get("score", 0)
    away_score = away.get("score", 0)

    cubs_are_home = home.get("team", {}).get("id") == CUBS_TEAM_ID
    cubs_score = home_score if cubs_are_home else away_score
    opp_score = away_score if cubs_are_home else home_score
    opp_name = away_team if cubs_are_home else home_team

    return {
        "status": status,
        "cubs_score": cubs_score,
        "opp_score": opp_score,
        "opp_name": opp_name,
        "cubs_are_home": cubs_are_home,
        "home_team": home_team,
        "away_team": away_team,
        "home_score": home_score,
        "away_score": away_score,
    }


st.set_page_config(page_title="Did the Cubs Win?", page_icon="⚾")
st.title("Did the Cubs Win Last Night?")

yesterday = date.today() - timedelta(days=1)
st.caption(f"Checking {yesterday.strftime('%A, %B %d, %Y')}")

with st.spinner("Checking the score..."):
    try:
        game = get_cubs_game(yesterday)
    except requests.RequestException as e:
        st.error(f"Could not reach the MLB API: {e}")
        st.stop()

if game is None:
    st.info("The Cubs did not play last night.")
    st.stop()

result = parse_result(game)
status = result["status"]

if status != "Final":
    st.warning(f"The game status is **{status}** — it may not be finished yet.")
    st.write(
        f"{result['away_team']} {result['away_score']} — "
        f"{result['home_team']} {result['home_score']}"
    )
    st.stop()

cubs_won = result["cubs_score"] > result["opp_score"]

if cubs_won:
    st.success("## YES! The Cubs won!")
    st.balloons()
else:
    st.error("## No. The Cubs lost.")

col1, col2, col3 = st.columns(3)
col1.metric("Cubs", result["cubs_score"])
col2.write("")
col3.metric(result["opp_name"], result["opp_score"])

location = "at home" if result["cubs_are_home"] else f"at {result['opp_name']}"
st.caption(f"Final score — Cubs {location}")
