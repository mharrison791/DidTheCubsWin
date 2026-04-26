import streamlit as st
from datetime import date, timedelta
from utils import (
    get_cubs_games, parse_game, build_linescore_html, team_logo_url,
    get_boxscore, get_starter, get_pitch_usage, get_previous_game,
    pitcher_summary, build_pitch_usage_html, build_pitch_comparison_html, fmt_date,
)


# ── Shared helpers ─────────────────────────────────────────────────────────────

def _section_label(text: str) -> str:
    return (
        f'<div style="font-family:system-ui,sans-serif;font-size:0.62rem;font-weight:700;'
        f'letter-spacing:0.16em;text-transform:uppercase;color:#999;'
        f'margin:20px 0 10px 0;">{text}</div>'
    )

def _divider_html() -> str:
    return '<div style="border-top:1px solid #1a1a2e;margin:28px 0;"></div>'


# ── Game result ────────────────────────────────────────────────────────────────

def _hero_html(info: dict, game_num: int | None = None) -> str:
    label  = f"Game {game_num} — " if game_num else ""
    status = info["status"]

    if status == "Final":
        badge_text = f"✓ {label}Cubs Win!" if info["cubs_won"] else f"✗ {label}Cubs Lose."
        top_color  = "#0E3386" if info["cubs_won"] else "#CC3433"
        badge_bg   = "#0E3386" if info["cubs_won"] else "#CC3433"
    else:
        badge_text = f"⏳ {label}{info['detailed_status']}"
        top_color  = "#c79a00"
        badge_bg   = "#c79a00"

    away_score   = info["away_score"]
    home_score   = info["home_score"]
    away_team_id = info.get("away_team_id")
    home_team_id = info.get("home_team_id")

    if status == "Final":
        away_color        = "#3a3a5a" if home_score > away_score else "#e8e8f0"
        home_color        = "#3a3a5a" if away_score > home_score else "#e8e8f0"
        away_logo_opacity = "0.3"    if home_score > away_score else "1"
        home_logo_opacity = "0.3"    if away_score > home_score else "1"
    else:
        away_color = home_color = "#e8e8f0"
        away_logo_opacity = home_logo_opacity = "1"

    loc         = "at Wrigley Field" if info["cubs_are_home"] else f"@ {info['opp_name']}"
    status_text = info["detailed_status"] if status != "Final" else "Final"

    def logo_img(team_id, opacity):
        url = team_logo_url(team_id) if team_id else ""
        return f'<img src="{url}" style="width:60px;height:60px;object-fit:contain;margin-bottom:10px;opacity:{opacity};" />' if url else ""

    return f"""
<style>
  .hero-card {{
    background: linear-gradient(135deg, #0E1A3A 0%, #0A0A1F 100%);
    border: 1px solid #1e2d5a; border-radius: 16px;
    padding: 32px 40px; position: relative; overflow: hidden; margin-bottom: 4px;
  }}
  .hero-stripe {{ position:absolute;top:0;left:0;right:0;height:4px;background:linear-gradient(90deg,{top_color},{top_color}88); }}
  .hero-badge {{
    display:inline-block;background:{badge_bg};color:#fff;font-size:0.68rem;font-weight:700;
    letter-spacing:0.18em;text-transform:uppercase;padding:4px 12px;border-radius:4px;
    margin-bottom:24px;font-family:system-ui,sans-serif;
  }}
  .hero-teams {{ display:flex;align-items:center; }}
  .hero-team {{ flex:1; }}
  .hero-team-inner {{ display:flex;flex-direction:column; }}
  .hero-team.right .hero-team-inner {{ align-items:flex-end; }}
  .hero-team-name {{ font-family:system-ui,sans-serif;font-size:0.72rem;font-weight:700;letter-spacing:0.14em;text-transform:uppercase;color:#888;margin-bottom:8px; }}
  .hero-score {{ font-size:6rem;font-weight:900;line-height:1;font-family:system-ui,sans-serif; }}
  .hero-sep {{ font-family:system-ui,sans-serif;font-size:0.88rem;color:#667;letter-spacing:0.1em;text-align:center;min-width:72px;padding-bottom:12px;line-height:1.8; }}
  .hero-sep .status-text {{ font-size:0.62rem;color:#667;display:block; }}
  .hero-loc {{ font-family:system-ui,sans-serif;font-size:0.72rem;color:#888;margin-top:16px;letter-spacing:0.05em; }}
</style>
<div class="hero-card">
  <div class="hero-stripe"></div>
  <div class="hero-badge">{badge_text}</div>
  <div class="hero-teams">
    <div class="hero-team right"><div class="hero-team-inner">
      {logo_img(away_team_id, away_logo_opacity)}
      <div class="hero-team-name">{info["away_name"]}</div>
      <div class="hero-score" style="color:{away_color}">{away_score}</div>
    </div></div>
    <div class="hero-sep">@<span class="status-text">{status_text}</span></div>
    <div class="hero-team"><div class="hero-team-inner">
      {logo_img(home_team_id, home_logo_opacity)}
      <div class="hero-team-name">{info["home_name"]}</div>
      <div class="hero-score" style="color:{home_color}">{home_score}</div>
    </div></div>
  </div>
  <div class="hero-loc">{loc}</div>
</div>"""


def _decisions_html(info: dict) -> str:
    winner = info.get("winner")
    loser  = info.get("loser")
    save   = info.get("save")
    if not (winner or loser or save):
        return ""

    def card(badge, color, bg, border, label, name):
        return (
            f'<div style="flex:1;background:#0D0D1A;border:1px solid #1a1a2e;border-radius:10px;'
            f'padding:14px 18px;display:flex;align-items:center;gap:12px;">'
            f'<div style="width:34px;height:34px;border-radius:8px;flex-shrink:0;display:flex;'
            f'align-items:center;justify-content:center;font-size:0.72rem;font-weight:800;'
            f'background:{bg};color:{color};border:1px solid {border};font-family:system-ui,sans-serif;">{badge}</div>'
            f'<div><div style="font-family:system-ui,sans-serif;font-size:0.6rem;letter-spacing:0.14em;'
            f'text-transform:uppercase;color:#999;">{label}</div>'
            f'<div style="font-family:system-ui,sans-serif;font-size:0.9rem;font-weight:700;'
            f'color:#ccc;margin-top:3px;">{name}</div></div></div>'
        )

    cards = ""
    if winner: cards += card("W",  "#6688ff", "rgba(14,51,134,0.3)",  "#0E3386", "Win",  winner)
    if loser:  cards += card("L",  "#ff6b6b", "rgba(204,52,51,0.2)",  "#CC3433", "Loss", loser)
    if save:   cards += card("SV", "#ffc107", "rgba(255,193,7,0.15)", "#c79a00", "Save", save)

    return (
        f'<div style="margin-top:8px;">'
        f'<div style="font-family:system-ui,sans-serif;font-size:0.62rem;font-weight:700;'
        f'letter-spacing:0.16em;text-transform:uppercase;color:#999;margin-bottom:10px;">Pitcher Decisions</div>'
        f'<div style="display:flex;gap:12px;">{cards}</div></div>'
    )


def _render_game(info: dict, game_num: int | None = None):
    st.html(_hero_html(info, game_num))
    linescore = info.get("linescore", {})
    if linescore.get("innings"):
        st.markdown(_section_label("Linescore"), unsafe_allow_html=True)
        st.html(build_linescore_html(linescore, info["home_name"], info["away_name"]))
    if info["status"] == "Final":
        decisions = _decisions_html(info)
        if decisions:
            st.markdown(decisions, unsafe_allow_html=True)


# ── Pitcher report ─────────────────────────────────────────────────────────────

def _stat_grid_html(items: list[tuple]) -> str:
    cards = "".join(
        f'<div style="background:#0D0D1A;border:1px solid #1a1a2e;border-radius:10px;padding:14px 16px;text-align:center;">'
        f'<div style="font-size:0.6rem;letter-spacing:0.14em;text-transform:uppercase;color:#999;'
        f'font-family:system-ui,sans-serif;margin-bottom:10px;">{lbl}</div>'
        f'<div style="font-size:1.5rem;font-weight:700;color:#e8e8f0;line-height:1;'
        f'font-family:system-ui,sans-serif;">{val}</div></div>'
        for lbl, val in items
    )
    return (
        f'<div style="display:grid;grid-template-columns:repeat({len(items)},1fr);'
        f'gap:10px;margin-bottom:12px;">{cards}</div>'
    )


def _render_pitcher(starter: dict, game_pk: int, season: int):
    stats = starter["stats"]
    ss    = starter["season_stats"]
    pid   = starter["id"]
    name  = starter["name"]

    st.markdown(
        f'<div style="margin-bottom:16px;">'
        f'<div style="font-family:system-ui,sans-serif;font-size:1.4rem;font-weight:800;'
        f'color:#e8e8f0;margin-bottom:4px;">{name}</div>'
        f'<div style="font-family:system-ui,sans-serif;font-size:0.75rem;color:#aaa;">'
        f'{starter["team_name"]} &nbsp;·&nbsp; '
        f'Season: {ss.get("wins","—")}–{ss.get("losses","—")} &nbsp;·&nbsp; '
        f'{ss.get("era","—")} ERA &nbsp;·&nbsp; {ss.get("whip","—")} WHIP</div></div>',
        unsafe_allow_html=True,
    )

    ip = stats.get("inningsPitched","—"); k  = stats.get("strikeOuts","—")
    bb = stats.get("baseOnBalls","—");   er = stats.get("earnedRuns","—")
    h  = stats.get("hits","—")
    st.markdown(_stat_grid_html([("IP",ip),("K",k),("BB",bb),("ER",er),("H",h)]), unsafe_allow_html=True)

    pitches = stats.get("numberOfPitches", 0); strikes = stats.get("strikes", 0)
    hr = stats.get("homeRuns","—");            bf = stats.get("battersFaced","—")
    strike_pct = f"{round(int(strikes)/int(pitches)*100)}%" if pitches and strikes else "—"
    st.markdown(_stat_grid_html([("Pitches",pitches or "—"),("Strike%",strike_pct),("HR",hr),("Batters",bf)]), unsafe_allow_html=True)

    st.markdown(_divider_html(), unsafe_allow_html=True)

    with st.spinner("Loading pitch data…"):
        try:    usage = get_pitch_usage(game_pk, pid)
        except: usage = {}

    summary = pitcher_summary(name, stats, usage)
    st.markdown(
        f'<div style="background:#0D0D1A;border:1px solid #1a1a2e;border-left:3px solid #0E3386;'
        f'border-radius:10px;padding:14px 18px;margin-bottom:4px;">'
        f'<p style="font-family:system-ui,sans-serif;font-size:0.88rem;color:#bbb;line-height:1.65;margin:0;">'
        f'{summary}</p></div>',
        unsafe_allow_html=True,
    )

    st.markdown(_section_label("Pitch Usage — Last Night"), unsafe_allow_html=True)
    st.html(build_pitch_usage_html(usage))

    if usage:
        with st.spinner("Loading previous start…"):
            try:    prev_pk, prev_date, prev_opp = get_previous_game(pid, game_pk, season)
            except: prev_pk = None

        if prev_pk and prev_pk != game_pk:
            with st.spinner("Loading previous pitch data…"):
                try:    prev_usage = get_pitch_usage(prev_pk, pid)
                except: prev_usage = {}
            if prev_usage:
                prev_label = fmt_date(prev_date) + (f" vs {prev_opp}" if prev_opp else "")
                st.markdown(_section_label(f"Pitch Comparison — Last Night vs {prev_label}"), unsafe_allow_html=True)
                st.html(build_pitch_comparison_html(usage, prev_usage, prev_label))


def _render_pitcher_section(info: dict, season: int):
    game_pk   = info["game_pk"]
    cubs_side = "home" if info["cubs_are_home"] else "away"
    opp_side  = "away" if info["cubs_are_home"] else "home"

    with st.spinner("Loading boxscore…"):
        try:
            boxscore = get_boxscore(game_pk)
        except Exception as e:
            st.error(f"Could not load boxscore: {e}")
            return

    cubs_starter = get_starter(boxscore, cubs_side)
    opp_starter  = get_starter(boxscore, opp_side)

    # Cubs starter
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
            'border-radius:10px;padding:14px 18px;font-family:system-ui,sans-serif;font-size:0.85rem;color:#bbb;">'
            'No starting pitcher data available for the Cubs.</div>',
            unsafe_allow_html=True,
        )

    st.markdown(_divider_html(), unsafe_allow_html=True)

    # Opponent starter (collapsible)
    with st.expander(f"⚾ {info['opp_name']} Starting Pitcher"):
        if opp_starter["id"]:
            _render_pitcher(opp_starter, game_pk, season)
        else:
            st.markdown(
                '<div style="font-family:system-ui,sans-serif;font-size:0.85rem;color:#bbb;">'
                'No starting pitcher data available for the opponent.</div>',
                unsafe_allow_html=True,
            )


# ── Page ──────────────────────────────────────────────────────────────────────

yesterday = date.today() - timedelta(days=1)
season    = yesterday.year

st.markdown(
    f'<div style="font-family:system-ui,sans-serif;font-size:0.68rem;font-weight:700;'
    f'letter-spacing:0.16em;text-transform:uppercase;color:#888;margin-bottom:6px;">'
    f'{yesterday.strftime("%A, %B %d, %Y")} · Yesterday\'s Result</div>'
    f'<div style="font-family:system-ui,sans-serif;font-size:2rem;font-weight:800;'
    f'color:#e8e8f0;letter-spacing:0.01em;margin-bottom:20px;">⚾ Did the Cubs Win?</div>',
    unsafe_allow_html=True,
)
st.markdown(_divider_html(), unsafe_allow_html=True)

with st.spinner("Fetching game data..."):
    try:
        games = get_cubs_games(yesterday.strftime("%Y-%m-%d"))
    except Exception as e:
        st.error(f"Could not reach the MLB API: {e}")
        st.stop()

if not games:
    st.markdown(
        '<div style="background:#0D0D1A;border:1px solid #1a1a2e;border-left:3px solid #c79a00;'
        'border-radius:10px;padding:16px 20px;font-family:system-ui,sans-serif;font-size:0.9rem;color:#bbb;">'
        '🏖️ The Cubs did not play last night.</div>',
        unsafe_allow_html=True,
    )
    st.stop()

parsed          = [parse_game(g) for g in games]
is_doubleheader = len(parsed) > 1
final_parsed    = [g for g in parsed if g["status"] == "Final"]

if final_parsed:
    record = final_parsed[-1]["cubs_record"]
    st.markdown(
        f'<div style="display:inline-block;background:#0D0D1A;border:1px solid #1a1a2e;'
        f'border-radius:10px;padding:10px 20px;margin-bottom:20px;">'
        f'<span style="font-family:system-ui,sans-serif;font-size:0.6rem;font-weight:700;'
        f'letter-spacing:0.14em;text-transform:uppercase;color:#999;">Season Record</span>'
        f'<span style="font-family:system-ui,sans-serif;font-size:1.1rem;font-weight:700;'
        f'color:#e8e8f0;margin-left:14px;">{record}</span></div>',
        unsafe_allow_html=True,
    )

if is_doubleheader:
    wins   = sum(1 for g in final_parsed if g["cubs_won"])
    losses = sum(1 for g in final_parsed if not g["cubs_won"])
    st.markdown(
        f'<div style="font-family:system-ui,sans-serif;font-size:1.1rem;font-weight:700;'
        f'color:#e8e8f0;margin-bottom:16px;">🎽 Doubleheader — Cubs went {wins}–{losses}</div>',
        unsafe_allow_html=True,
    )
    tab_labels = [f"Game {i+1}" for i in range(len(parsed))]
    tabs = st.tabs(tab_labels)
else:
    tabs = [st.container()]

for tab, info in zip(tabs, parsed):
    with tab:
        # ── Game result ────────────────────────────────────────────
        _render_game(info, game_num=None)

        if info["status"] == "Final":
            # ── Pitcher report ─────────────────────────────────────
            st.markdown(_divider_html(), unsafe_allow_html=True)
            st.markdown(
                '<div style="font-family:system-ui,sans-serif;font-size:0.68rem;font-weight:700;'
                'letter-spacing:0.16em;text-transform:uppercase;color:#888;margin-bottom:20px;">'
                '📋 Pitcher Report</div>',
                unsafe_allow_html=True,
            )
            _render_pitcher_section(info, season)

if final_parsed and all(g["cubs_won"] for g in final_parsed):
    st.balloons()
