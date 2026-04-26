import streamlit as st
from datetime import date, timedelta
from utils import (
    ALL_MLB_TEAMS,
    get_team_colors,
    get_team_games,
    parse_game,
    render_game_result,
    render_pitcher_section,
    render_hitter_section,
    render_next_game,
)

st.markdown(
    '<div style="font-family:system-ui,sans-serif;font-size:2rem;font-weight:800;'
    'color:#e8e8f0;letter-spacing:0.01em;margin-bottom:20px;">⚾ Did My Team Win?</div>',
    unsafe_allow_html=True,
)

# ── Team selector ──────────────────────────────────────────────────────────────
selected = st.selectbox(
    "Select your team",
    options=ALL_MLB_TEAMS,
    format_func=lambda x: x[1],
    index=None,
    placeholder="Select a team...",
    label_visibility="collapsed",
)

if selected is None:
    st.info("👆 Choose a team above to see last night's result.")
    st.stop()

team_id, team_name = selected
colors  = get_team_colors(team_id)
primary = colors["primary"]

yesterday = date.today() - timedelta(days=1)
season    = yesterday.year
st.markdown(
    f'<div style="font-family:system-ui,sans-serif;font-size:0.68rem;color:#888;'
    f'letter-spacing:0.1em;margin-bottom:12px;">{yesterday.strftime("%A, %B %d, %Y")}</div>',
    unsafe_allow_html=True,
)
st.markdown('<div style="border-top:1px solid #1a1a2e;margin-bottom:24px;"></div>', unsafe_allow_html=True)

with st.spinner("Fetching game data..."):
    try:
        games = get_team_games(team_id, yesterday.strftime("%Y-%m-%d"))
    except Exception as e:
        st.error(f"Could not reach the MLB API: {e}")
        st.stop()

if not games:
    st.info(f"🏖️ The {team_name} did not play last night.")
    st.stop()

parsed       = [parse_game(g, team_id) for g in games]
is_dh        = len(parsed) > 1
final_parsed = [g for g in parsed if g["status"] == "Final"]

if is_dh:
    wins   = sum(1 for g in final_parsed if g["team_won"])
    losses = sum(1 for g in final_parsed if not g["team_won"])
    st.markdown(
        f'<div style="font-family:system-ui,sans-serif;font-size:1.1rem;font-weight:700;'
        f'color:#e8e8f0;margin-bottom:16px;">🎽 Doubleheader — {team_name} went {wins}–{losses}</div>',
        unsafe_allow_html=True,
    )

last_final_idx = max(
    (i for i, g in enumerate(parsed) if g["status"] == "Final"), default=None
)

for i, info in enumerate(parsed):
    render_game_result(
        info,
        game_num=(i + 1) if is_dh else None,
        show_record=(i == last_final_idx),
        primary_color=primary,
        win_gif_url=None,
    )
    if is_dh and i < len(parsed) - 1:
        st.markdown('<div style="border-top:1px solid #1a1a2e;margin:24px 0;"></div>', unsafe_allow_html=True)

# ── Hitters & Pitcher Report ───────────────────────────────────────────────────
if final_parsed:
    st.markdown('<div style="border-top:1px solid #1a1a2e;margin:24px 0;"></div>', unsafe_allow_html=True)
    if is_dh:
        tabs = st.tabs([f"Game {i+1}" for i in range(len(final_parsed))])
        for tab, info in zip(tabs, final_parsed):
            with tab:
                render_hitter_section(
                    info,
                    section_header=f"🏏 {team_name} Hitters",
                    header_color=primary,
                )
                st.divider()
                render_pitcher_section(
                    info, season,
                    section_header=f"⚾ {team_name} Starting Pitcher",
                    header_color=primary,
                )
    else:
        render_hitter_section(
            final_parsed[0],
            section_header=f"🏏 {team_name} Hitters",
            header_color=primary,
        )
        st.divider()
        render_pitcher_section(
            final_parsed[0], season,
            section_header=f"⚾ {team_name} Starting Pitcher",
            header_color=primary,
        )

# ── Tomorrow ───────────────────────────────────────────────────────────────────
st.markdown('<div style="border-top:1px solid #1a1a2e;margin:24px 0;"></div>', unsafe_allow_html=True)
render_next_game(team_id, team_name)
