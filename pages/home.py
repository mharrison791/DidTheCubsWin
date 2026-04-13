import streamlit as st
from datetime import date, timedelta
from utils import get_cubs_games, parse_game, build_linescore_html


def _hero_html(info: dict, game_num: int | None = None) -> str:
    label = f"Game {game_num} — " if game_num else ""
    status = info["status"]
    cubs_won = info.get("cubs_won", False)

    if status == "Final":
        badge_text = f"✓ {label}Cubs Win!" if cubs_won else f"✗ {label}Cubs Lose."
        top_color  = "#0E3386" if cubs_won else "#CC3433"
        badge_bg   = "#0E3386" if cubs_won else "#CC3433"
    else:
        badge_text = f"⏳ {label}{info['detailed_status']}"
        top_color  = "#c79a00"
        badge_bg   = "#c79a00"

    away_score = info["away_score"]
    home_score = info["home_score"]
    away_name  = info["away_name"]
    home_name  = info["home_name"]

    # Dim the losing team's score
    if status == "Final":
        away_color = "#3a3a5a" if home_score > away_score else "#e8e8f0"
        home_color = "#3a3a5a" if away_score > home_score else "#e8e8f0"
    else:
        away_color = "#e8e8f0"
        home_color = "#e8e8f0"

    loc         = "at Wrigley Field" if info["cubs_are_home"] else f"@ {info['opp_name']}"
    status_text = info["detailed_status"] if status != "Final" else "Final"

    return f"""
<div style="background:linear-gradient(135deg,#0E1A3A 0%,#0A0A1F 100%);
            border:1px solid #1e2d5a;border-radius:16px;padding:28px 36px;
            position:relative;overflow:hidden;margin-bottom:8px;">
  <div style="position:absolute;top:0;left:0;right:0;height:4px;
              background:linear-gradient(90deg,{top_color},{top_color}88);"></div>
  <div style="display:inline-block;background:{badge_bg};color:#fff;
              font-size:0.68rem;font-weight:700;letter-spacing:0.18em;
              text-transform:uppercase;padding:4px 12px;border-radius:4px;
              margin-bottom:20px;font-family:system-ui,sans-serif;">{badge_text}</div>
  <div style="display:flex;align-items:center;">
    <div style="flex:1;text-align:right;">
      <div style="font-family:system-ui,sans-serif;font-size:0.72rem;font-weight:700;
                  letter-spacing:0.12em;text-transform:uppercase;
                  color:#888;margin-bottom:6px;">{away_name}</div>
      <div style="font-size:5rem;font-weight:900;line-height:1;
                  color:{away_color};font-family:system-ui,sans-serif;">{away_score}</div>
    </div>
    <div style="font-family:system-ui,sans-serif;font-size:0.85rem;color:#2a2a4a;
                letter-spacing:0.08em;text-align:center;min-width:64px;padding-bottom:8px;">
      @<br><span style="font-size:0.62rem;color:#2a2a4a;">{status_text}</span>
    </div>
    <div style="flex:1;">
      <div style="font-family:system-ui,sans-serif;font-size:0.72rem;font-weight:700;
                  letter-spacing:0.12em;text-transform:uppercase;
                  color:#888;margin-bottom:6px;">{home_name}</div>
      <div style="font-size:5rem;font-weight:900;line-height:1;
                  color:{home_color};font-family:system-ui,sans-serif;">{home_score}</div>
    </div>
  </div>
  <div style="font-family:system-ui,sans-serif;font-size:0.72rem;color:#2a2a4a;
              margin-top:14px;letter-spacing:0.05em;">{loc}</div>
</div>"""


def _decisions_html(info: dict) -> str:
    winner = info.get("winner")
    loser  = info.get("loser")
    save   = info.get("save")

    if not (winner or loser or save):
        return ""

    def card(badge, badge_color, badge_bg, badge_border, label, name):
        return f"""
<div style="flex:1;background:#0D0D1A;border:1px solid #1a1a2e;border-radius:10px;
            padding:12px 16px;display:flex;align-items:center;gap:12px;">
  <div style="width:32px;height:32px;border-radius:8px;display:flex;align-items:center;
              justify-content:center;font-size:0.7rem;font-weight:800;letter-spacing:0.05em;
              background:{badge_bg};color:{badge_color};border:1px solid {badge_border};
              font-family:system-ui,sans-serif;flex-shrink:0;">{badge}</div>
  <div>
    <div style="font-family:system-ui,sans-serif;font-size:0.62rem;letter-spacing:0.12em;
                text-transform:uppercase;color:#444;">{label}</div>
    <div style="font-family:system-ui,sans-serif;font-size:0.88rem;font-weight:700;
                color:#ccc;margin-top:2px;">{name}</div>
  </div>
</div>"""

    cards = ""
    if winner:
        cards += card("W", "#6688ff", "rgba(14,51,134,0.3)", "#0E3386", "Win",  winner)
    if loser:
        cards += card("L", "#ff6b6b", "rgba(204,52,51,0.2)", "#CC3433", "Loss", loser)
    if save:
        cards += card("SV", "#ffc107", "rgba(255,193,7,0.15)", "#c79a00", "Save", save)

    return f'<div style="display:flex;gap:12px;margin-top:16px;margin-bottom:4px;">{cards}</div>'


def _render_game(info: dict, game_num: int | None = None):
    st.markdown(_hero_html(info, game_num), unsafe_allow_html=True)

    linescore = info.get("linescore", {})
    if linescore.get("innings"):
        st.html(build_linescore_html(linescore, info["home_name"], info["away_name"]))

    if info["status"] == "Final":
        decisions = _decisions_html(info)
        if decisions:
            st.markdown(decisions, unsafe_allow_html=True)


# ── Page ──────────────────────────────────────────────────────────────────────

st.markdown(
    '<p style="font-family:system-ui,sans-serif;font-size:0.68rem;letter-spacing:0.15em;'
    'text-transform:uppercase;color:#333;margin-bottom:2px;">Cubs Win Checker</p>',
    unsafe_allow_html=True,
)
st.title("⚾ Yesterday's Result")

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
if final_parsed:
    record = final_parsed[-1]["cubs_record"]
    st.markdown(
        f'<div style="display:inline-block;background:#0D0D1A;border:1px solid #1a1a2e;'
        f'border-radius:10px;padding:10px 20px;margin-bottom:8px;">'
        f'<span style="font-family:system-ui,sans-serif;font-size:0.62rem;letter-spacing:0.12em;'
        f'text-transform:uppercase;color:#444;">Season Record</span>'
        f'<span style="font-family:system-ui,sans-serif;font-size:1.1rem;font-weight:700;'
        f'color:#e8e8f0;margin-left:12px;">{record}</span></div>',
        unsafe_allow_html=True,
    )

if is_doubleheader:
    wins   = sum(1 for g in final_parsed if g["cubs_won"])
    losses = sum(1 for g in final_parsed if not g["cubs_won"])
    st.subheader(f"🎽 Doubleheader — Cubs went {wins}–{losses}")
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
