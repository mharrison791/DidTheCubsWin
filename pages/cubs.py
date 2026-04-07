import streamlit as st
from datetime import date, timedelta
from utils import (
    CUBS_TEAM_ID,
    FLY_THE_W_GIF,
    get_team_games,
    parse_game,
    get_team_colors,
    render_game_result,
    render_pitcher_section,
    render_next_game,
)

CUBS_PRIMARY = "#0E3386"

st.title("🐻 Did the Cubs Win Last Night?")

yesterday = date.today() - timedelta(days=1)
season    = yesterday.year
st.caption(f"Checking results for **{yesterday.strftime('%A, %B %d, %Y')}**")
st.divider()

with st.spinner("Fetching game data..."):
    try:
        games = get_team_games(CUBS_TEAM_ID, yesterday.strftime("%Y-%m-%d"))
    except Exception as e:
        st.error(f"Could not reach the MLB API: {e}")
        st.stop()

if not games:
    st.info("🏖️ The Cubs did not play last night.")
    st.stop()

parsed       = [parse_game(g, CUBS_TEAM_ID) for g in games]
is_dh        = len(parsed) > 1
final_parsed = [g for g in parsed if g["status"] == "Final"]

if is_dh:
    wins   = sum(1 for g in final_parsed if g["team_won"])
    losses = sum(1 for g in final_parsed if not g["team_won"])
    st.subheader(f"🎽 Doubleheader Day! — Cubs went {wins}–{losses}")
    st.divider()

last_final_idx = max(
    (i for i, g in enumerate(parsed) if g["status"] == "Final"), default=None
)

for i, info in enumerate(parsed):
    render_game_result(
        info,
        game_num=(i + 1) if is_dh else None,
        show_record=(i == last_final_idx),
        primary_color=CUBS_PRIMARY,
        win_gif_url=FLY_THE_W_GIF,
    )
    if is_dh and i < len(parsed) - 1:
        st.divider()

if final_parsed and all(g["team_won"] for g in final_parsed):
    st.balloons()

# ── Pitcher Report ─────────────────────────────────────────────────────────────
if final_parsed:
    st.divider()
    if is_dh:
        tabs = st.tabs([f"Game {i+1}" for i in range(len(final_parsed))])
        for tab, info in zip(tabs, final_parsed):
            with tab:
                render_pitcher_section(
                    info, season,
                    section_header="🐻 Cubs Starting Pitcher",
                    header_color=CUBS_PRIMARY,
                )
    else:
        render_pitcher_section(
            final_parsed[0], season,
            section_header="🐻 Cubs Starting Pitcher",
            header_color=CUBS_PRIMARY,
        )

# ── Tomorrow ───────────────────────────────────────────────────────────────────
st.divider()
render_next_game(CUBS_TEAM_ID, "Cubs")
