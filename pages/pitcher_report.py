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
    render_nav,
)


def _stat_grid_html(items: list[tuple]) -> str:
    """Render dark stat cards. items = [(label, value), ...]"""
    cards = "".join(f"""
<div style="background:#0D0D1A;border:1px solid #1a1a2e;border-radius:10px;padding:14px 16px;text-align:center;">
  <div style="font-size:0.6rem;letter-spacing:0.14em;text-transform:uppercase;color:#999;
              font-family:system-ui,sans-serif;margin-bottom:10px;">{lbl}</div>
  <div style="font-size:1.5rem;font-weight:700;color:#e8e8f0;line-height:1;
              font-family:system-ui,sans-serif;">{val}</div>
</div>""" for lbl, val in items)
    return (
        f'<div style="display:grid;grid-template-columns:repeat({len(items)},1fr);'
        f'gap:10px;margin-bottom:12px;">{cards}</div>'
    )


def _section_label(text: str) -> str:
    return (
        f'<div style="font-family:system-ui,sans-serif;font-size:0.62rem;font-weight:700;'
        f'letter-spacing:0.16em;text-transform:uppercase;color:#999;'
        f'margin:20px 0 10px 0;">{text}</div>'
    )


def _divider_html() -> str:
    return '<div style="border-top:1px solid #1a1a2e;margin:24px 0;"></div>'


def _render_pitcher(starter: dict, game_pk: int, season: int):
    stats = starter["stats"]
    ss    = starter["season_stats"]
    pid   = starter["id"]
    name  = starter["name"]

    era  = ss.get("era",    "—")
    w    = ss.get("wins",   "—")
    l    = ss.get("losses", "—")
    whip = ss.get("whip",   "—")

    # Pitcher header
    st.markdown(
        f'<div style="margin-bottom:16px;">'
        f'<div style="font-family:system-ui,sans-serif;font-size:1.4rem;font-weight:800;'
        f'color:#e8e8f0;letter-spacing:0.01em;margin-bottom:4px;">{name}</div>'
        f'<div style="font-family:system-ui,sans-serif;font-size:0.75rem;color:#aaa;'
        f'letter-spacing:0.06em;">{starter["team_name"]} &nbsp;·&nbsp; '
        f'Season: {w}–{l} &nbsp;·&nbsp; {era} ERA &nbsp;·&nbsp; {whip} WHIP</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Stat row 1: IP K BB ER H
    ip = stats.get("inningsPitched", "—")
    k  = stats.get("strikeOuts",     "—")
    bb = stats.get("baseOnBalls",    "—")
    er = stats.get("earnedRuns",     "—")
    h  = stats.get("hits",           "—")
    st.markdown(_stat_grid_html([("IP", ip), ("K", k), ("BB", bb), ("ER", er), ("H", h)]), unsafe_allow_html=True)

    # Stat row 2: Pitches Strike% HR BF
    pitches = stats.get("numberOfPitches", 0)
    strikes = stats.get("strikes",         0)
    hr      = stats.get("homeRuns",        "—")
    bf      = stats.get("battersFaced",    "—")
    strike_pct = (
        f"{round(int(strikes) / int(pitches) * 100)}%"
        if pitches and strikes else "—"
    )
    st.markdown(
        _stat_grid_html([
            ("Pitches", pitches or "—"),
            ("Strike%", strike_pct),
            ("HR",      hr),
            ("Batters", bf),
        ]),
        unsafe_allow_html=True,
    )

    st.markdown(_divider_html(), unsafe_allow_html=True)

    # Pitch data
    with st.spinner("Loading pitch data…"):
        try:
            usage = get_pitch_usage(game_pk, pid)
        except Exception:
            usage = {}

    # Performance summary
    summary = pitcher_summary(name, stats, usage)
    st.markdown(
        f'<div style="background:#0D0D1A;border:1px solid #1a1a2e;'
        f'border-left:3px solid #0E3386;border-radius:10px;padding:14px 18px;margin-bottom:4px;">'
        f'<p style="font-family:system-ui,sans-serif;font-size:0.88rem;color:#bbb;'
        f'line-height:1.65;margin:0;">{summary}</p></div>',
        unsafe_allow_html=True,
    )

    # Pitch usage table
    st.markdown(_section_label("Pitch Usage — Last Night"), unsafe_allow_html=True)
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
                opp_label  = f" vs {prev_opp}" if prev_opp else ""
                prev_label = f"{fmt_date(prev_date)}{opp_label}"
                st.markdown(_section_label(f"Pitch Comparison — Last Night vs {prev_label}"), unsafe_allow_html=True)
                st.html(build_pitch_comparison_html(usage, prev_usage, prev_label))
        elif not prev_pk:
            st.markdown(
                '<div style="font-family:system-ui,sans-serif;font-size:0.78rem;'
                'color:#999;font-style:italic;margin-top:8px;">No previous start found to compare.</div>',
                unsafe_allow_html=True,
            )


# ── Page ──────────────────────────────────────────────────────────────────────

yesterday = date.today() - timedelta(days=1)
season    = yesterday.year

st.markdown(
    f'<div style="font-family:system-ui,sans-serif;font-size:0.68rem;font-weight:700;'
    f'letter-spacing:0.16em;text-transform:uppercase;color:#888;margin-bottom:6px;">'
    f'{yesterday.strftime("%A, %B %d, %Y")} · Pitcher Report</div>'
    f'<div style="font-family:system-ui,sans-serif;font-size:2rem;font-weight:800;'
    f'color:#e8e8f0;letter-spacing:0.01em;margin-bottom:20px;">📋 Starting Pitchers</div>',
    unsafe_allow_html=True,
)
st.markdown('<div style="border-top:1px solid #1a1a2e;margin-bottom:24px;"></div>', unsafe_allow_html=True)

with st.spinner("Fetching game data…"):
    try:
        games = get_cubs_games(yesterday.strftime("%Y-%m-%d"))
    except Exception as e:
        st.error(f"Could not reach the MLB API: {e}")
        st.stop()

if not games:
    st.markdown(
        '<div style="background:#0D0D1A;border:1px solid #1a1a2e;border-left:3px solid #c79a00;'
        'border-radius:10px;padding:16px 20px;font-family:system-ui,sans-serif;'
        'font-size:0.9rem;color:#bbb;">🏖️ The Cubs did not play last night — no pitcher report available.</div>',
        unsafe_allow_html=True,
    )
    st.stop()

parsed      = [parse_game(g) for g in games]
final_games = [g for g in parsed if g["status"] == "Final"]

if not final_games:
    st.markdown(
        '<div style="background:#0D0D1A;border:1px solid #1a1a2e;border-left:3px solid #c79a00;'
        'border-radius:10px;padding:16px 20px;font-family:system-ui,sans-serif;'
        'font-size:0.9rem;color:#bbb;">⏳ No completed games found for yesterday.</div>',
        unsafe_allow_html=True,
    )
    st.stop()

is_doubleheader = len(parsed) > 1

if is_doubleheader:
    tab_labels = [f"Game {i+1}" for i in range(len(parsed))]
    tabs = st.tabs(tab_labels)
else:
    tabs = [st.container()]

for tab, info in zip(tabs, parsed):
    with tab:
        if info["status"] != "Final":
            st.markdown(
                f'<div style="background:#0D0D1A;border:1px solid #1a1a2e;border-left:3px solid #c79a00;'
                f'border-radius:10px;padding:14px 18px;margin-bottom:16px;font-family:system-ui,sans-serif;'
                f'font-size:0.85rem;color:#bbb;">⏳ Game status: {info["detailed_status"]} — data may be incomplete.</div>',
                unsafe_allow_html=True,
            )

        game_pk   = info["game_pk"]
        cubs_side = "home" if info["cubs_are_home"] else "away"
        opp_side  = "away" if info["cubs_are_home"] else "home"

        st.markdown(
            f'<div style="font-family:system-ui,sans-serif;font-size:0.75rem;color:#999;'
            f'letter-spacing:0.05em;margin-bottom:20px;">'
            f'{info["away_name"]} @ {info["home_name"]} &nbsp;·&nbsp; '
            f'Final: {info["away_score"]}–{info["home_score"]}</div>',
            unsafe_allow_html=True,
        )

        with st.spinner("Loading boxscore…"):
            try:
                boxscore = get_boxscore(game_pk)
            except Exception as e:
                st.error(f"Could not load boxscore: {e}")
                continue

        cubs_starter = get_starter(boxscore, cubs_side)
        opp_starter  = get_starter(boxscore, opp_side)

        # ── Cubs starter ──────────────────────────────────────────────────────
        st.markdown(
            '<div style="display:flex;align-items:center;gap:8px;margin-bottom:16px;">'
            '<span style="font-size:1rem;">🐻</span>'
            '<span style="font-family:system-ui,sans-serif;font-size:0.68rem;font-weight:700;'
            'letter-spacing:0.16em;text-transform:uppercase;color:#6688ff;">Cubs Starting Pitcher</span>'
            '</div>',
            unsafe_allow_html=True,
        )
        if cubs_starter["id"]:
            _render_pitcher(cubs_starter, game_pk, season)
        else:
            st.markdown(
                '<div style="background:#0D0D1A;border:1px solid #1a1a2e;border-left:3px solid #0E3386;'
                'border-radius:10px;padding:14px 18px;font-family:system-ui,sans-serif;'
                'font-size:0.85rem;color:#bbb;">No starting pitcher data available for the Cubs.</div>',
                unsafe_allow_html=True,
            )

        st.markdown(_divider_html(), unsafe_allow_html=True)

        # ── Opponent starter ──────────────────────────────────────────────────
        with st.expander(f"⚾ {info['opp_name']} Starting Pitcher"):
            if opp_starter["id"]:
                _render_pitcher(opp_starter, game_pk, season)
            else:
                st.markdown(
                    '<div style="font-family:system-ui,sans-serif;font-size:0.85rem;color:#bbb;">'
                    'No starting pitcher data available for the opponent.</div>',
                    unsafe_allow_html=True,
                )
