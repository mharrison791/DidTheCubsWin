import streamlit as st
import requests
from datetime import datetime

CUBS_TEAM_ID = 112
MLB_API_BASE = "https://statsapi.mlb.com/api/v1"

# ── Pitch type colours ────────────────────────────────────────────────────────
PITCH_COLORS = {
    "FF": "#e74c3c",  # Four-Seam Fastball
    "FA": "#d35400",  # Fastball (generic)
    "SI": "#c0392b",  # Sinker
    "FC": "#e67e22",  # Cutter
    "SL": "#3498db",  # Slider
    "ST": "#2471a3",  # Sweeper
    "SV": "#1a5276",  # Slurve
    "CU": "#8e44ad",  # Curveball
    "KC": "#6c3483",  # Knuckle Curve
    "CS": "#7d3c98",  # Slow Curve
    "CH": "#27ae60",  # Changeup
    "FS": "#1e8449",  # Splitter
    "FO": "#145a32",  # Forkball
    "KN": "#7f8c8d",  # Knuckleball
    "EP": "#bdc3c7",  # Eephus
    "SC": "#95a5a6",  # Screwball
}
# Pitch codes to skip (non-pitches or intentional balls)
SKIP_CODES = {"UN", "PO", "IN", "AB", "NP"}


def pitch_color(code: str) -> str:
    return PITCH_COLORS.get(code, "#aab7b8")


def ip_to_float(ip_str) -> float:
    """Convert MLB innings-pitched string ('6.2' = 6⅔) to a float."""
    try:
        parts = str(ip_str).split(".")
        return int(parts[0]) + (int(parts[1]) / 3 if len(parts) > 1 else 0)
    except (ValueError, IndexError):
        return 0.0


def fmt_date(date_str: str) -> str:
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").strftime("%b %d")
    except Exception:
        return date_str or "Prev Game"


# ── API calls (all cached) ────────────────────────────────────────────────────

@st.cache_data(ttl=300)
def get_cubs_games(date_str: str) -> list:
    """Return all Cubs games on the given date string (YYYY-MM-DD)."""
    resp = requests.get(
        f"{MLB_API_BASE}/schedule",
        params={"teamId": CUBS_TEAM_ID, "date": date_str, "sportId": 1,
                "hydrate": "linescore,decisions"},
        timeout=10,
    )
    resp.raise_for_status()
    dates = resp.json().get("dates", [])
    return dates[0].get("games", []) if dates else []


@st.cache_data(ttl=300)
def get_boxscore(game_pk: int) -> dict:
    resp = requests.get(f"{MLB_API_BASE}/game/{game_pk}/boxscore", timeout=15)
    resp.raise_for_status()
    return resp.json()


@st.cache_data(ttl=300)
def get_pitch_usage(game_pk: int, pitcher_id: int) -> dict:
    """Return {code: {description, count, speeds[]}} for a pitcher in a game."""
    resp = requests.get(f"{MLB_API_BASE}/game/{game_pk}/playByPlay", timeout=15)
    resp.raise_for_status()
    usage: dict = {}
    for play in resp.json().get("allPlays", []):
        if play.get("matchup", {}).get("pitcher", {}).get("id") != pitcher_id:
            continue
        for ev in play.get("playEvents", []):
            if not ev.get("isPitch"):
                continue
            ptype = (ev.get("details") or {}).get("type") or {}
            code = ptype.get("code", "UN")
            if code in SKIP_CODES:
                continue
            desc = ptype.get("description") or code
            speed = (ev.get("pitchData") or {}).get("startSpeed")
            if code not in usage:
                usage[code] = {"description": desc, "count": 0, "speeds": []}
            usage[code]["count"] += 1
            if speed:
                usage[code]["speeds"].append(speed)
    return usage


@st.cache_data(ttl=300)
def get_previous_game(pitcher_id: int, current_game_pk: int, season: int) -> tuple:
    """Return (game_pk, date_str, opponent_name) for the pitcher's prev start."""
    resp = requests.get(
        f"{MLB_API_BASE}/people/{pitcher_id}/stats",
        params={"stats": "gameLog", "season": season, "group": "pitching", "sportId": 1},
        timeout=10,
    )
    resp.raise_for_status()
    splits = resp.json().get("stats", [{}])[0].get("splits", [])

    # splits are chronological (oldest → newest); find current game index
    current_idx = next(
        (i for i, s in enumerate(splits)
         if s.get("game", {}).get("gamePk") == current_game_pk),
        None,
    )

    if current_idx is not None and current_idx > 0:
        prev = splits[current_idx - 1]
    elif current_idx is None and splits:
        prev = splits[-1]  # game not logged yet; use most recent
    else:
        return None, None, None

    return (
        prev.get("game", {}).get("gamePk"),
        prev.get("date", ""),
        prev.get("opponent", {}).get("name", ""),
    )


# ── Parsing ───────────────────────────────────────────────────────────────────

def parse_game(game: dict) -> dict:
    teams = game.get("teams", {})
    home, away = teams.get("home", {}), teams.get("away", {})
    home_id = home.get("team", {}).get("id")
    cubs_are_home = home_id == CUBS_TEAM_ID
    cubs_side = home if cubs_are_home else away

    lr = cubs_side.get("leagueRecord", {})
    cubs_record = f"{lr.get('wins','?')}-{lr.get('losses','?')}" if lr else None

    home_score = home.get("score", 0)
    away_score = away.get("score", 0)
    cubs_score = home_score if cubs_are_home else away_score
    opp_score  = away_score if cubs_are_home else home_score

    home_name = home.get("team", {}).get("name", "Home")
    away_name = away.get("team", {}).get("name", "Away")
    opp_name  = away_name if cubs_are_home else home_name

    decisions = game.get("decisions", {})
    return {
        "game_pk":         game.get("gamePk"),
        "status":          game.get("status", {}).get("abstractGameState", ""),
        "detailed_status": game.get("status", {}).get("detailedState", ""),
        "cubs_are_home":   cubs_are_home,
        "home_name":       home_name,
        "away_name":       away_name,
        "home_score":      home_score,
        "away_score":      away_score,
        "cubs_score":      cubs_score,
        "opp_score":       opp_score,
        "opp_name":        opp_name,
        "cubs_won":        cubs_score > opp_score,
        "cubs_record":     cubs_record,
        "winner":          decisions.get("winner", {}).get("fullName"),
        "loser":           decisions.get("loser",  {}).get("fullName"),
        "save":            decisions.get("save",   {}).get("fullName"),
        "linescore":       game.get("linescore", {}),
    }


def get_starter(boxscore: dict, side: str) -> dict:
    """Return starter info dict for 'home' or 'away' side."""
    team = boxscore.get("teams", {}).get(side, {})
    pitchers = team.get("pitchers", [])
    if not pitchers:
        return {"id": None, "name": "Unknown", "stats": {}, "season_stats": {}, "team_name": ""}
    pid = pitchers[0]
    player = team.get("players", {}).get(f"ID{pid}", {})
    return {
        "id":           pid,
        "name":         player.get("person", {}).get("fullName", "Unknown"),
        "stats":        player.get("stats", {}).get("pitching", {}),
        "season_stats": player.get("seasonStats", {}).get("pitching", {}),
        "team_name":    team.get("team", {}).get("name", ""),
        "jersey":       player.get("jerseyNumber", ""),
    }


# ── Text generation ───────────────────────────────────────────────────────────

def pitcher_summary(name: str, stats: dict, usage: dict) -> str:
    ip   = stats.get("inningsPitched", "0.0")
    h    = int(stats.get("hits", 0))
    er   = int(stats.get("earnedRuns", 0))
    bb   = int(stats.get("baseOnBalls", 0))
    k    = int(stats.get("strikeOuts", 0))
    hr   = int(stats.get("homeRuns", 0))
    n    = int(stats.get("numberOfPitches", 0))
    strikes = int(stats.get("strikes", 0))
    ip_f = ip_to_float(ip)
    qs   = ip_f >= 6 and er <= 3

    # Opening clause
    if ip_f >= 7:
        sentence = f"{name} delivered a gem, working {ip} innings"
    elif ip_f >= 6:
        sentence = f"{name} went {ip} innings"
    elif ip_f >= 5:
        sentence = f"{name} gave the Cubs {ip} innings"
    else:
        sentence = f"{name} was limited to {ip} innings"

    # Earned runs
    if er == 0:
        sentence += " without allowing an earned run"
    elif er == 1:
        sentence += " allowing just 1 earned run"
    else:
        sentence += f" allowing {er} earned runs"

    # Hits + walks
    if h == 0:
        sentence += " on no hits"
    else:
        sentence += f" on {h} hit{'s' if h > 1 else ''}"
    if bb:
        sentence += f" and {bb} walk{'s' if bb > 1 else ''}"

    # Strikeouts
    if k >= 10:
        sentence += f", racking up a dominant {k} strikeouts"
    elif k >= 7:
        sentence += f", fanning {k} batters"
    elif k:
        sentence += f", striking out {k}"
    sentence += "."

    # Efficiency
    if n and strikes:
        sentence += f" Threw {n} pitches ({round(strikes / n * 100)}% strikes)."

    # Badges
    if qs:
        sentence += " ✅ Quality start."
    if hr:
        sentence += f" Surrendered {hr} home run{'s' if hr > 1 else ''}."

    # Primary pitch
    if usage:
        total = sum(v["count"] for v in usage.values())
        top = max(usage.items(), key=lambda x: x[1]["count"])
        pct = round(top[1]["count"] / total * 100)
        sentence += f" Leaned primarily on the {top[1]['description'].lower()} ({pct}%)."

    return sentence


# ── HTML builders ─────────────────────────────────────────────────────────────

def build_linescore_html(linescore: dict, home_name: str, away_name: str) -> str:
    innings = linescore.get("innings", [])
    n = max(len(innings), 9)
    home_r = [""] * n
    away_r = [""] * n

    for inn in innings:
        idx = inn.get("num", 1) - 1
        if idx < n:
            hr = inn.get("home", {}).get("runs")
            ar = inn.get("away", {}).get("runs")
            home_r[idx] = str(hr) if hr is not None else "X"
            away_r[idx] = str(ar) if ar is not None else "X"

    home_r = [r or "-" for r in home_r]
    away_r = [r or "-" for r in away_r]
    th  = linescore.get("teams", {}).get("home", {})
    ta  = linescore.get("teams", {}).get("away", {})

    def td(v, cls=""):
        return f'<td{" class=\"" + cls + "\"" if cls else ""}>{v}</td>'

    def row(name, runs, tot):
        c = f'<td class="team">{name}</td>'
        c += "".join(td(r) for r in runs)
        c += td(tot.get("runs",""), "rhe") + td(tot.get("hits",""), "rhe") + td(tot.get("errors",""), "rhe")
        return f"<tr>{c}</tr>"

    hdrs = "".join(f"<th>{i+1}</th>" for i in range(n))
    hrow = f'<tr><th class="team"></th>{hdrs}<th class="rhe-h">R</th><th class="rhe-h">H</th><th class="rhe-h">E</th></tr>'
    return f"""
<style>
  .ls{{width:100%;table-layout:fixed;border-collapse:collapse;font-size:.83rem;font-family:monospace}}
  .ls th,.ls td{{text-align:center;padding:8px 4px;border:1px solid #1a1a2e;white-space:nowrap;overflow:hidden}}
  .ls .team{{text-align:left;font-weight:600;padding-left:10px;width:22%;text-overflow:ellipsis;color:#bbb}}
  .ls th{{background:#111127;font-weight:700;color:#444;font-size:.68rem;letter-spacing:.1em;text-transform:uppercase}}
  .ls td{{color:#bbb;background:#0D0D1A}}
  .ls .rhe-h{{background:#0A0A1F;font-weight:700;color:#444}}
  .ls .rhe{{background:#111127;font-weight:700;color:#e8e8f0}}
  .ls tr:last-child td{{border-top:1px solid #1e2d5a}}
</style>
<table class="ls">
  <thead>{hrow}</thead>
  <tbody>{row(away_name, away_r, ta)}{row(home_name, home_r, th)}</tbody>
</table>"""


def build_pitch_usage_html(usage: dict) -> str:
    if not usage:
        return "<p><em>Pitch data not available for this game.</em></p>"
    total = sum(v["count"] for v in usage.values())
    rows = ""
    for code, data in sorted(usage.items(), key=lambda x: x[1]["count"], reverse=True):
        cnt  = data["count"]
        pct  = round(cnt / total * 100) if total else 0
        spds = data["speeds"]
        velo = f"{sum(spds)/len(spds):.1f} mph" if spds else "—"
        col  = pitch_color(code)
        desc = data["description"]
        rows += f"""<tr>
          <td class="pn"><span class="pd" style="background:{col}"></span>{desc} <span class="pc">({code})</span></td>
          <td class="pv">{cnt}</td>
          <td class="pb"><div class="bw"><div class="bf" style="width:{pct}%;background:{col}"></div>
            <span class="bl">{pct}%</span></div></td>
          <td class="pvl">{velo}</td></tr>"""
    return f"""
<style>
  .pu{{width:100%;border-collapse:collapse;font-size:.85rem}}
  .pu th{{text-align:left;padding:8px 10px;background:#111127;font-weight:700;
          border-bottom:1px solid #1a1a2e;color:#444;font-size:.68rem;letter-spacing:.1em;text-transform:uppercase}}
  .pu td{{padding:8px 10px;border-bottom:1px solid #1a1a2e;vertical-align:middle;background:#0D0D1A;color:#bbb}}
  .pd{{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:6px;vertical-align:middle}}
  .pc{{color:#333;font-size:.75rem}}
  .pv{{text-align:right;width:50px;font-variant-numeric:tabular-nums;color:#e8e8f0}}
  .pb{{width:140px}}
  .bw{{position:relative;background:#1a1a2e;border-radius:3px;height:18px}}
  .bf{{height:100%;border-radius:3px;opacity:.85}}
  .bl{{position:absolute;right:4px;top:1px;font-size:.75rem;font-weight:600;color:#e8e8f0}}
  .pvl{{text-align:right;color:#444;font-size:.8rem;width:80px}}
</style>
<table class="pu">
  <thead><tr><th>Pitch</th><th style="text-align:right">Count</th><th>Usage</th><th style="text-align:right">Avg Velo</th></tr></thead>
  <tbody>{rows}</tbody>
</table>"""


def build_pitch_comparison_html(now: dict, prev: dict, prev_label: str) -> str:
    if not now:
        return "<p><em>No pitch data available.</em></p>"
    all_codes = sorted(
        set(list(now.keys()) + list(prev.keys())),
        key=lambda c: now.get(c, {}).get("count", 0), reverse=True
    )
    total_now  = sum(v["count"] for v in now.values())
    total_prev = sum(v["count"] for v in prev.values()) if prev else 0
    rows = ""
    for code in all_codes:
        n_data = now.get(code, {})
        p_data = prev.get(code, {}) if prev else {}
        desc   = n_data.get("description") or p_data.get("description") or code
        col    = pitch_color(code)
        cnt_n  = n_data.get("count", 0)
        cnt_p  = p_data.get("count", 0) if p_data else None
        pct_n  = round(cnt_n  / total_now  * 100) if total_now  else 0
        pct_p  = round(cnt_p  / total_prev * 100) if (total_prev and cnt_p is not None) else None

        if pct_p is not None:
            delta = pct_n - pct_p
            if delta > 2:
                badge = f'<span style="color:#27ae60;font-size:.75rem">▲{delta}pp</span>'
            elif delta < -2:
                badge = f'<span style="color:#e74c3c;font-size:.75rem">▼{abs(delta)}pp</span>'
            else:
                badge = f'<span style="color:#999;font-size:.75rem">{delta:+d}pp</span>'
            prev_cell = f'{cnt_p}&thinsp;({pct_p}%)&nbsp;{badge}'
        else:
            prev_cell = '<span style="color:#bbb">—</span>'

        rows += f"""<tr>
          <td class="cpn"><span class="cpd" style="background:{col}"></span>{desc}</td>
          <td class="cpv">{cnt_n}&thinsp;({pct_n}%)</td>
          <td class="cpv">{prev_cell}</td></tr>"""
    return f"""
<style>
  .cp{{width:100%;border-collapse:collapse;font-size:.85rem}}
  .cp th{{padding:8px 10px;background:#111127;border-bottom:1px solid #1a1a2e;font-weight:700;
          font-size:.68rem;letter-spacing:.1em;text-transform:uppercase;color:#444}}
  .cp td{{padding:8px 10px;border-bottom:1px solid #1a1a2e;vertical-align:middle;
          background:#0D0D1A;color:#bbb}}
  .cpd{{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:5px;vertical-align:middle}}
  .cpv{{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap;color:#e8e8f0}}
</style>
<table class="cp">
  <thead><tr>
    <th>Pitch</th>
    <th style="text-align:right">Last Night</th>
    <th style="text-align:right">{prev_label}</th>
  </tr></thead>
  <tbody>{rows}</tbody>
</table>"""
