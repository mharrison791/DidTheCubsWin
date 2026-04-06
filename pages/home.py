import streamlit as st
from datetime import date, timedelta
from utils import get_cubs_games, parse_game, build_linescore_html


def _render_game(info: dict, game_num: int | None = None):
    label  = f"Game {game_num} — " if game_num else ""
    status = info["status"]

    if status == "Final":
        if info["cubs_won"]:
            st.success(f"### ✅ {label}Cubs win!")
        else:
            st.error(f"### ❌ {label}Cubs lose.")
    else:
        st.warning(f"### ⏳ {label}{info['detailed_status']}")

    col1, col2, col3 = st.columns([2, 1, 2])
    with col1:
        st.metric(info["away_name"], info["away_score"])
    with col2:
        st.markdown(
            "<div style='text-align:center;padding-top:1rem;font-size:1.4rem'>vs</div>",
            unsafe_allow_html=True,
        )
    with col3:
        st.metric(info["home_name"], info["home_score"])

    linescore = info.get("linescore", {})
    if linescore.get("innings"):
        st.markdown("**Linescore**")
        st.html(build_linescore_html(linescore, info["home_name"], info["away_name"]))

    if status == "Final":
        d1, d2, d3 = st.columns(3)
        if info["winner"]: d1.markdown(f"**W:** {info['winner']}")
        if info["loser"]:  d2.markdown(f"**L:** {info['loser']}")
        if info["save"]:   d3.markdown(f"**SV:** {info['save']}")

    loc = "at Wrigley Field" if info["cubs_are_home"] else f"@ {info['opp_name']}"
    st.caption(loc)


# ── Page ──────────────────────────────────────────────────────────────────────

st.title("⚾ Did the Cubs Win Last Night?")

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
    st.caption(f"Season record: **{final_parsed[-1]['cubs_record']}**")

if is_doubleheader:
    wins   = sum(1 for g in final_parsed if g["cubs_won"])
    losses = sum(1 for g in final_parsed if not g["cubs_won"])
    st.subheader(f"🎽 Doubleheader Day! — Cubs went {wins}–{losses}")
    st.divider()

for i, info in enumerate(parsed):
    _render_game(info, game_num=(i + 1) if is_doubleheader else None)
    if is_doubleheader and i < len(parsed) - 1:
        st.divider()

if final_parsed and all(g["cubs_won"] for g in final_parsed):
    st.balloons()
