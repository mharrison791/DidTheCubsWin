import streamlit as st
from datetime import date, timedelta
from utils import (
    CUBS_TEAM_ID,
    fmt_date,
    get_cubs_games,
    parse_game,
    get_boxscore,
    get_starter,
    get_pitch_usage,
    get_previous_game,
    pitcher_summary,
    build_pitch_usage_html,
    build_pitch_comparison_html,
)


# ── Pitcher section renderer ──────────────────────────────────────────────────

def _render_pitcher(starter: dict, game_pk: int, season: int):
    stats  = starter["stats"]
    ss     = starter["season_stats"]
    pid    = starter["id"]
    name   = starter["name"]

    # Name + season context
    era  = ss.get("era", "—")
    w    = ss.get("wins", "—")
    l    = ss.get("losses", "—")
    whip = ss.get("whip", "—")
    st.markdown(f"### {name}")
    st.caption(
        f"{starter['team_name']} · "
        f"Season: {w}–{l}, {era} ERA, {whip} WHIP"
    )

    # Game stat metrics — row 1
    ip      = stats.get("inningsPitched", "—")
    k       = stats.get("strikeOuts", "—")
    bb      = stats.get("baseOnBalls", "—")
    er      = stats.get("earnedRuns", "—")
    h       = stats.get("hits", "—")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("IP", ip)
    c2.metric("K",  k)
    c3.metric("BB", bb)
    c4.metric("ER", er)
    c5.metric("H",  h)

    # Game stat metrics — row 2
    pitches = stats.get("numberOfPitches", 0)
    strikes = stats.get("strikes", 0)
    hr      = stats.get("homeRuns", "—")
    bf      = stats.get("battersFaced", "—")

    strike_pct = (
        f"{round(int(strikes) / int(pitches) * 100)}%"
        if pitches and strikes else "—"
    )
    c6, c7, c8, c9 = st.columns(4)
    c6.metric("Pitches", pitches or "—")
    c7.metric("Strike%", strike_pct)
    c8.metric("HR",      hr)
    c9.metric("Batters Faced", bf)

    st.divider()

    # Pitch data
    with st.spinner("Loading pitch data…"):
        try:
            usage = get_pitch_usage(game_pk, pid)
        except Exception:
            usage = {}

    # Performance summary
    summary = pitcher_summary(name, stats, usage)
    st.info(summary)

    # Pitch usage table
    st.markdown("**Pitch Usage — Last Night**")
    st.html(build_pitch_usage_html(usage))

    # Previous game comparison
    if usage:
        with st.spinner("Loading previous start…"):
            try:
                prev_pk, prev_date, prev_opp = get_previous_game(pid, game_pk, season)
            except Exception:
                prev_pk = None

        if prev_pk and prev_pk != game_pk:
            with st.spinner("Loading previous pitch data…"):
                try:
                    prev_usage = get_pitch_usage(prev_pk, pid)
                except Exception:
                    prev_usage = {}

            if prev_usage:
                date_label = fmt_date(prev_date)
                opp_label  = f" vs {prev_opp}" if prev_opp else ""
                prev_label = f"{date_label}{opp_label}"
                st.markdown(f"**Pitch Comparison — Last Night vs {prev_label}**")
                st.html(build_pitch_comparison_html(usage, prev_usage, prev_label))
        elif not prev_pk:
            st.caption("*No previous start found to compare.*")


# ── Page ──────────────────────────────────────────────────────────────────────

st.title("📋 Pitcher Report")

yesterday = date.today() - timedelta(days=1)
season    = yesterday.year
st.caption(f"Starting pitchers for **{yesterday.strftime('%A, %B %d, %Y')}**")
st.divider()

with st.spinner("Fetching game data…"):
    try:
        games = get_cubs_games(yesterday.strftime("%Y-%m-%d"))
    except Exception as e:
        st.error(f"Could not reach the MLB API: {e}")
        st.stop()

if not games:
    st.info("🏖️ The Cubs did not play last night — no pitcher report available.")
    st.stop()

parsed = [parse_game(g) for g in games]
final_games = [g for g in parsed if g["status"] == "Final"]

if not final_games:
    st.warning("No completed games found for yesterday.")
    st.stop()

is_doubleheader = len(parsed) > 1

# Game selector for doubleheaders
if is_doubleheader:
    tab_labels = [f"Game {i+1}" for i in range(len(parsed))]
    tabs = st.tabs(tab_labels)
else:
    tabs = [st.container()]

for tab, info in zip(tabs, parsed):
    with tab:
        if info["status"] != "Final":
            st.warning(f"Game status: {info['detailed_status']} — data may be incomplete.")

        game_pk  = info["game_pk"]
        cubs_side = "home" if info["cubs_are_home"] else "away"
        opp_side  = "away" if info["cubs_are_home"] else "home"
        matchup   = (
            f"{info['away_name']} @ {info['home_name']}  ·  "
            f"Final: {info['away_score']}–{info['home_score']}"
        )
        st.caption(matchup)

        with st.spinner("Loading boxscore…"):
            try:
                boxscore = get_boxscore(game_pk)
            except Exception as e:
                st.error(f"Could not load boxscore: {e}")
                continue

        cubs_starter = get_starter(boxscore, cubs_side)
        opp_starter  = get_starter(boxscore, opp_side)

        # ── Cubs starter ──────────────────────────────────────────────────────
        st.subheader("🐻 Cubs Starting Pitcher")
        if cubs_starter["id"]:
            _render_pitcher(cubs_starter, game_pk, season)
        else:
            st.info("No starting pitcher data available for the Cubs.")

        st.divider()

        # ── Opponent starter (collapsible) ────────────────────────────────────
        with st.expander(f"⚾ {info['opp_name']} Starting Pitcher"):
            if opp_starter["id"]:
                _render_pitcher(opp_starter, game_pk, season)
            else:
                st.info("No starting pitcher data available for the opponent.")
