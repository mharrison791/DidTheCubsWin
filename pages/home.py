import streamlit as st
from datetime import date, timedelta, datetime, timezone
from utils import (
    get_cubs_games,
    get_next_cubs_game,
    parse_game,
    build_linescore_html,
    team_logo_url,
    render_nav,
)


def _render_game(info: dict, game_num: int | None = None, show_record: bool = False):
    label  = f"Game {game_num} — " if game_num else ""
    status = info["status"]

    if status == "Final":
        if info["cubs_won"]:
            st.markdown(
                f"""<div style="background-color:#d4edda;border:1px solid #c3e6cb;border-radius:0.375rem;padding:1rem 1.25rem;display:flex;align-items:center;gap:1rem;">
                  <span style="font-size:1.3rem;font-weight:700;color:#155724;">✅ {label}Cubs win!</span>
                  <img src="https://cdn.dribbble.com/userupload/21006334/file/original-de1dba822571c54c70632d4f7d765d87.gif"
                       style="height:60px;width:auto;border-radius:4px;" alt="Fly the W">
                </div>""",
                unsafe_allow_html=True,
            )
        else:
            st.error(f"### ❌ {label}Cubs lose.")
    else:
        st.warning(f"### ⏳ {label}{info['detailed_status']}")

    away_logo = team_logo_url(info.get("away_id"))
    home_logo = team_logo_url(info.get("home_id"))

    def _score_card(name, score, logo_url):
        logo = f'<img src="{logo_url}" style="height:52px;width:auto;margin-bottom:6px;" alt="{name}">' if logo_url else ""
        return (
            f'<div style="text-align:center;padding:8px 0;">'
            f'{logo}'
            f'<div style="font-size:0.85rem;color:#555;font-weight:600;margin-bottom:4px;">{name}</div>'
            f'<div style="font-size:2.8rem;font-weight:800;line-height:1;">{score}</div>'
            f'</div>'
        )

    col1, col2, col3 = st.columns([2, 1, 2])
    with col1:
        st.html(_score_card(info["away_name"], info["away_score"], away_logo))
    with col2:
        st.markdown(
            "<div style='text-align:center;padding-top:2rem;font-size:1.4rem'>vs</div>",
            unsafe_allow_html=True,
        )
    with col3:
        st.html(_score_card(info["home_name"], info["home_score"], home_logo))

    linescore = info.get("linescore", {})
    if linescore.get("innings"):
        st.markdown("**Linescore**")
        st.html(build_linescore_html(
            linescore, info["home_name"], info["away_name"],
            info.get("home_id"), info.get("away_id"),
        ))

    if status == "Final":
        d1, d2, d3 = st.columns(3)
        if info["winner"]: d1.markdown(f"**W:** {info['winner']}")
        if info["loser"]:  d2.markdown(f"**L:** {info['loser']}")
        if info["save"]:   d3.markdown(f"**SV:** {info['save']}")

    if show_record and info.get("cubs_record"):
        st.markdown(
            f"<div style='font-size:1.4rem;font-weight:800;color:#0E3386;margin-top:0.5rem;'>"
            f"Season Record: {info['cubs_record']}</div>",
            unsafe_allow_html=True,
        )


# ── Page ──────────────────────────────────────────────────────────────────────

st.title("⚾ Did the Cubs Win Last Night?")
render_nav()

yesterday = date.today() - timedelta(days=1)
st.caption(f"Checking results for **{yesterday.strftime('%A, %B %d, %Y')}**")
st.divider()

with st.spinner("Fetching game data..."):
    try:
        games = get_cubs_games(yesterday.strftime("%Y-%m-%d"))
    except Exception as e:
        st.error(f"Could not reach the MLB API: {e}")
        st.stop()

if not games:
    st.info("🏖️ The Cubs did not play last night.")
    st.stop()

parsed = [parse_game(g) for g in games]
is_doubleheader = len(parsed) > 1

final_parsed = [g for g in parsed if g["status"] == "Final"]

if is_doubleheader:
    wins   = sum(1 for g in final_parsed if g["cubs_won"])
    losses = sum(1 for g in final_parsed if not g["cubs_won"])
    st.subheader(f"🎽 Doubleheader Day! — Cubs went {wins}–{losses}")
    st.divider()

last_final_idx = max((i for i, g in enumerate(parsed) if g["status"] == "Final"), default=None)
for i, info in enumerate(parsed):
    _render_game(info, game_num=(i + 1) if is_doubleheader else None, show_record=(i == last_final_idx))
    if is_doubleheader and i < len(parsed) - 1:
        st.divider()

if final_parsed and all(g["cubs_won"] for g in final_parsed):
    st.balloons()

# ── Tomorrow's game ────────────────────────────────────────────────────────────

st.divider()
st.markdown("#### Tomorrow")
tomorrow = date.today() + timedelta(days=1)
try:
    next_game = get_next_cubs_game(tomorrow.strftime("%Y-%m-%d"))
except Exception:
    next_game = None

if next_game:
    opp_logo_url = team_logo_url(next_game["opp_id"])
    loc_word = "vs" if next_game["cubs_are_home"] else "@"

    # Parse game time to Central Time
    time_display = ""
    game_time_utc = next_game.get("game_time_utc", "")
    if game_time_utc:
        try:
            gt = datetime.fromisoformat(game_time_utc.replace("Z", "+00:00"))
            offset_hours = -5 if 3 <= gt.month <= 11 else -6
            ct = gt + timedelta(hours=offset_hours)
            tz_label = "CDT" if offset_hours == -5 else "CST"
            time_display = ct.strftime("%I:%M %p").lstrip("0") + f" {tz_label}"
        except Exception:
            pass

    logo_tag = (
        f'<img src="{opp_logo_url}" style="height:36px;width:auto;vertical-align:middle;margin-right:8px;" alt="">'
        if opp_logo_url else ""
    )
    time_tag = f' <span style="color:#666;font-size:0.9rem;">· {time_display}</span>' if time_display else ""
    st.markdown(
        f'<div style="font-size:1.1rem;font-weight:600;">'
        f'{logo_tag}Cubs {loc_word} {next_game["opp_name"]}{time_tag}'
        f'</div>',
        unsafe_allow_html=True,
    )
else:
    st.markdown("🏖️ Off Day")
