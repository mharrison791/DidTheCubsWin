import streamlit as st
import requests
from datetime import date, timedelta, datetime, timezone

CUBS_TEAM_ID = 112
MLB_API_BASE = "https://statsapi.mlb.com/api/v1"

# ESPN team logo CDN — maps MLB team ID → ESPN abbreviation
_ESPN_ABBREV = {
    108: "laa", 109: "ari", 110: "bal", 111: "bos", 112: "chc",
    113: "cin", 114: "cle", 115: "col", 116: "det", 117: "hou",
    118: "kc",  119: "lad", 120: "wsh", 121: "nym", 133: "oak",
    134: "pit", 135: "sd",  136: "sea", 137: "sf",  138: "stl",
    139: "tb",  140: "tex", 141: "tor", 142: "min", 143: "phi",
    144: "atl", 145: "chw", 146: "mia", 147: "nyy", 158: "mil",
}

def team_logo_url(team_id: int) -> str:
    abbrev = _ESPN_ABBREV.get(team_id, "")
    if not abbrev:
        return ""
    return f"https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/{abbrev}.png&w=120&h=120&transparent=true"

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

# MLB team logos by team ID (ESPN CDN)
TEAM_LOGOS: dict[int, str] = {
    108: "https://a.espncdn.com/i/teamlogos/mlb/500/laa.png",
    109: "https://a.espncdn.com/i/teamlogos/mlb/500/ari.png",
    110: "https://a.espncdn.com/i/teamlogos/mlb/500/bal.png",
    111: "https://a.espncdn.com/i/teamlogos/mlb/500/bos.png",
    112: "https://a.espncdn.com/i/teamlogos/mlb/500/chc.png",
    113: "https://a.espncdn.com/i/teamlogos/mlb/500/cin.png",
    114: "https://a.espncdn.com/i/teamlogos/mlb/500/cle.png",
    115: "https://a.espncdn.com/i/teamlogos/mlb/500/col.png",
    116: "https://a.espncdn.com/i/teamlogos/mlb/500/det.png",
    117: "https://a.espncdn.com/i/teamlogos/mlb/500/hou.png",
    118: "https://a.espncdn.com/i/teamlogos/mlb/500/kc.png",
    119: "https://a.espncdn.com/i/teamlogos/mlb/500/lad.png",
    120: "https://a.espncdn.com/i/teamlogos/mlb/500/wsh.png",
    121: "https://a.espncdn.com/i/teamlogos/mlb/500/nym.png",
    133: "https://a.espncdn.com/i/teamlogos/mlb/500/oak.png",
    134: "https://a.espncdn.com/i/teamlogos/mlb/500/pit.png",
    135: "https://a.espncdn.com/i/teamlogos/mlb/500/sd.png",
    136: "https://a.espncdn.com/i/teamlogos/mlb/500/sea.png",
    137: "https://a.espncdn.com/i/teamlogos/mlb/500/sf.png",
    138: "https://a.espncdn.com/i/teamlogos/mlb/500/stl.png",
    139: "https://a.espncdn.com/i/teamlogos/mlb/500/tb.png",
    140: "https://a.espncdn.com/i/teamlogos/mlb/500/tex.png",
    141: "https://a.espncdn.com/i/teamlogos/mlb/500/tor.png",
    142: "https://a.espncdn.com/i/teamlogos/mlb/500/min.png",
    143: "https://a.espncdn.com/i/teamlogos/mlb/500/phi.png",
    144: "https://a.espncdn.com/i/teamlogos/mlb/500/atl.png",
    145: "https://a.espncdn.com/i/teamlogos/mlb/500/chw.png",
    146: "https://a.espncdn.com/i/teamlogos/mlb/500/mia.png",
    147: "https://a.espncdn.com/i/teamlogos/mlb/500/nyy.png",
    158: "https://a.espncdn.com/i/teamlogos/mlb/500/mil.png",
}


def team_logo_url(team_id: int | None) -> str:
    """Return ESPN logo URL for a team by MLB team ID, or empty string if unknown."""
    return TEAM_LOGOS.get(team_id or 0, "")


# MLB team primary/secondary brand colors by team ID
TEAM_COLORS: dict[int, dict] = {
    108: {"primary": "#BA0021", "secondary": "#003263"},  # Angels
    109: {"primary": "#A71930", "secondary": "#E3D4AD"},  # Diamondbacks
    110: {"primary": "#DF4601", "secondary": "#000000"},  # Orioles
    111: {"primary": "#BD3039", "secondary": "#0C2340"},  # Red Sox
    112: {"primary": "#0E3386", "secondary": "#CC3433"},  # Cubs
    113: {"primary": "#C6011F", "secondary": "#000000"},  # Reds
    114: {"primary": "#00385D", "secondary": "#E31937"},  # Guardians
    115: {"primary": "#33006F", "secondary": "#C4CED4"},  # Rockies
    116: {"primary": "#0C2340", "secondary": "#FA4616"},  # Tigers
    117: {"primary": "#002D62", "secondary": "#EB6E1F"},  # Astros
    118: {"primary": "#004687", "secondary": "#C09A5B"},  # Royals
    119: {"primary": "#005A9C", "secondary": "#EF3E42"},  # Dodgers
    120: {"primary": "#AB0003", "secondary": "#14225A"},  # Nationals
    121: {"primary": "#002D72", "secondary": "#FF5910"},  # Mets
    133: {"primary": "#003831", "secondary": "#EFB21E"},  # Athletics
    134: {"primary": "#27251F", "secondary": "#FDB827"},  # Pirates
    135: {"primary": "#2F241D", "secondary": "#FFC425"},  # Padres
    136: {"primary": "#0C2C56", "secondary": "#005C5C"},  # Mariners
    137: {"primary": "#FD5A1E", "secondary": "#27251F"},  # Giants
    138: {"primary": "#C41E3A", "secondary": "#0C2340"},  # Cardinals
    139: {"primary": "#092C5C", "secondary": "#8FBCE6"},  # Rays
    140: {"primary": "#003278", "secondary": "#C0111F"},  # Rangers
    141: {"primary": "#134A8E", "secondary": "#1D2D5C"},  # Blue Jays
    142: {"primary": "#002B5C", "secondary": "#D31145"},  # Twins
    143: {"primary": "#E81828", "secondary": "#002D72"},  # Phillies
    144: {"primary": "#CE1141", "secondary": "#13274F"},  # Braves
    145: {"primary": "#27251F", "secondary": "#C4CED4"},  # White Sox
    146: {"primary": "#00A3E0", "secondary": "#EF3340"},  # Marlins
    147: {"primary": "#003087", "secondary": "#E4002C"},  # Yankees
    158: {"primary": "#12284B", "secondary": "#FFC52F"},  # Brewers
}

ALL_MLB_TEAMS: list[tuple[int, str]] = sorted([
    (108, "Los Angeles Angels"),
    (109, "Arizona Diamondbacks"),
    (110, "Baltimore Orioles"),
    (111, "Boston Red Sox"),
    (112, "Chicago Cubs"),
    (113, "Cincinnati Reds"),
    (114, "Cleveland Guardians"),
    (115, "Colorado Rockies"),
    (116, "Detroit Tigers"),
    (117, "Houston Astros"),
    (118, "Kansas City Royals"),
    (119, "Los Angeles Dodgers"),
    (120, "Washington Nationals"),
    (121, "New York Mets"),
    (133, "Oakland Athletics"),
    (134, "Pittsburgh Pirates"),
    (135, "San Diego Padres"),
    (136, "Seattle Mariners"),
    (137, "San Francisco Giants"),
    (138, "St. Louis Cardinals"),
    (139, "Tampa Bay Rays"),
    (140, "Texas Rangers"),
    (141, "Toronto Blue Jays"),
    (142, "Minnesota Twins"),
    (143, "Philadelphia Phillies"),
    (144, "Atlanta Braves"),
    (145, "Chicago White Sox"),
    (146, "Miami Marlins"),
    (147, "New York Yankees"),
    (158, "Milwaukee Brewers"),
], key=lambda x: x[1])


def get_team_colors(team_id: int) -> dict:
    """Return {'primary': hex, 'secondary': hex} for a team."""
    return TEAM_COLORS.get(team_id, {"primary": "#333333", "secondary": "#666666"})


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
def get_team_games(team_id: int, date_str: str) -> list:
    """Return all games for team_id on the given date string (YYYY-MM-DD)."""
    resp = requests.get(
        f"{MLB_API_BASE}/schedule",
        params={"teamId": team_id, "date": date_str, "sportId": 1,
                "hydrate": "linescore,decisions"},
        timeout=10,
    )
    resp.raise_for_status()
    dates = resp.json().get("dates", [])
    return dates[0].get("games", []) if dates else []


@st.cache_data(ttl=300)
def get_cubs_games(date_str: str) -> list:
    """Return all Cubs games on the given date string (YYYY-MM-DD)."""
    return get_team_games(CUBS_TEAM_ID, date_str)


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


@st.cache_data(ttl=300)
def get_next_team_game(team_id: int, date_str: str) -> dict | None:
    """Return info about a team's game on date_str, or None if off day."""
    resp = requests.get(
        f"{MLB_API_BASE}/schedule",
        params={"teamId": team_id, "date": date_str, "sportId": 1},
        timeout=10,
    )
    resp.raise_for_status()
    dates = resp.json().get("dates", [])
    games = dates[0].get("games", []) if dates else []
    if not games:
        return None
    game = games[0]
    teams = game.get("teams", {})
    home, away = teams.get("home", {}), teams.get("away", {})
    home_id = home.get("team", {}).get("id")
    team_is_home = home_id == team_id
    opp = away if team_is_home else home
    return {
        "opp_name":      opp.get("team", {}).get("name", "Unknown"),
        "opp_id":        opp.get("team", {}).get("id"),
        "team_is_home":  team_is_home,
        "game_time_utc": game.get("gameDate", ""),
    }


@st.cache_data(ttl=300)
def get_next_cubs_game(date_str: str) -> dict | None:
    """Return info about the Cubs' game on date_str, or None if off day."""
    return get_next_team_game(CUBS_TEAM_ID, date_str)


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

    home_name    = home.get("team", {}).get("name", "Home")
    away_name    = away.get("team", {}).get("name", "Away")
    opp_name     = away_name if cubs_are_home else home_name
    home_team_id = home.get("team", {}).get("id")
    away_team_id = away.get("team", {}).get("id")

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
        "home_team_id":    home_team_id,
        "away_team_id":    away_team_id,
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
        sentence = f"{name} gave the offense {ip} innings"
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

def build_linescore_html(
    linescore: dict,
    home_name: str,
    away_name: str,
    home_id: int | None = None,
    away_id: int | None = None,
) -> str:
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

    def _logo_tag(team_id):
        url = team_logo_url(team_id)
        if not url:
            return ""
        return f'<img src="{url}" style="height:18px;width:auto;vertical-align:middle;margin-right:4px;" alt="">'

    def row(name, runs, tot, team_id=None):
        logo = _logo_tag(team_id)
        c = f'<td class="team">{logo}{name}</td>'
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
  .ls th{{background:#111127;font-weight:700;color:#999;font-size:.68rem;letter-spacing:.1em;text-transform:uppercase}}
  .ls td{{color:#bbb;background:#0D0D1A}}
  .ls .rhe-h{{background:#0A0A1F;font-weight:700;color:#999}}
  .ls .rhe{{background:#111127;font-weight:700;color:#e8e8f0}}
  .ls tr:last-child td{{border-top:1px solid #1e2d5a}}
</style>
<table class="ls">
  <thead>{hrow}</thead>
  <tbody>{row(away_name, away_r, ta, away_id)}{row(home_name, home_r, th, home_id)}</tbody>
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
          border-bottom:1px solid #1a1a2e;color:#999;font-size:.68rem;letter-spacing:.1em;text-transform:uppercase}}
  .pu td{{padding:8px 10px;border-bottom:1px solid #1a1a2e;vertical-align:middle;background:#0D0D1A;color:#bbb}}
  .pd{{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:6px;vertical-align:middle}}
  .pc{{color:#999;font-size:.75rem}}
  .pv{{text-align:right;width:50px;font-variant-numeric:tabular-nums;color:#e8e8f0}}
  .pb{{width:140px}}
  .bw{{position:relative;background:#1a1a2e;border-radius:3px;height:18px}}
  .bf{{height:100%;border-radius:3px;opacity:.85}}
  .bl{{position:absolute;right:4px;top:1px;font-size:.75rem;font-weight:600;color:#e8e8f0}}
  .pvl{{text-align:right;color:#999;font-size:.8rem;width:80px}}
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
            now_cell  = f'{cnt_n}&thinsp;({pct_n}%)&nbsp;{badge}'
            prev_cell = f'{cnt_p}&thinsp;({pct_p}%)'
        else:
            now_cell  = f'{cnt_n}&thinsp;({pct_n}%)'
            prev_cell = '<span style="color:#bbb">—</span>'

        rows += f"""<tr>
          <td class="cpn"><span class="cpd" style="background:{col}"></span>{desc}</td>
          <td class="cpv">{now_cell}</td>
          <td class="cpv">{prev_cell}</td></tr>"""
    return f"""
<style>
  .cp{{width:100%;border-collapse:collapse;font-size:.85rem}}
  .cp th{{padding:8px 10px;background:#111127;border-bottom:1px solid #1a1a2e;font-weight:700;
          font-size:.68rem;letter-spacing:.1em;text-transform:uppercase;color:#999}}
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


# ── Rendering helpers ─────────────────────────────────────────────────────────

FLY_THE_W_GIF = "https://cdn.dribbble.com/userupload/21006334/file/original-de1dba822571c54c70632d4f7d765d87.gif"


def hitter_summary(boxscore: dict, side: str) -> str:
    """Generate a narrative summary of hitter performance for one side."""
    team     = boxscore.get("teams", {}).get(side, {})
    batter_ids = team.get("batters", [])
    players  = team.get("players", {})
    team_name = team.get("team", {}).get("name", "The team")

    rows = []
    for pid in batter_ids:
        p     = players.get(f"ID{pid}", {})
        stats = p.get("stats", {}).get("batting", {})
        if not stats:
            continue
        ab  = int(stats.get("atBats", 0))
        h   = int(stats.get("hits", 0))
        hr  = int(stats.get("homeRuns", 0))
        rbi = int(stats.get("rbi", 0))
        bb  = int(stats.get("baseOnBalls", 0))
        k   = int(stats.get("strikeOuts", 0))
        d   = int(stats.get("doubles", 0))
        t   = int(stats.get("triples", 0))
        sb  = int(stats.get("stolenBases", 0))
        if ab + bb == 0:
            continue
        name = p.get("person", {}).get("fullName", "Unknown")
        rows.append(dict(name=name, ab=ab, h=h, hr=hr, rbi=rbi, bb=bb, k=k, d=d, t=t, sb=sb))

    if not rows:
        return "No batting data available for this game."

    tot_ab  = sum(r["ab"]  for r in rows)
    tot_h   = sum(r["h"]   for r in rows)
    tot_hr  = sum(r["hr"]  for r in rows)
    tot_rbi = sum(r["rbi"] for r in rows)
    tot_k   = sum(r["k"]   for r in rows)

    # Team summary sentence
    extras = []
    if tot_hr == 1:
        extras.append("1 home run")
    elif tot_hr > 1:
        extras.append(f"{tot_hr} home runs")
    if tot_rbi:
        extras.append(f"{tot_rbi} RBI")

    summary = f"**{team_name}** went **{tot_h}-for-{tot_ab}**"
    if extras:
        summary += " with " + " and ".join(extras)
    summary += f", striking out {tot_k} time{'s' if tot_k != 1 else ''}."

    # Notable individual performers
    def _score(r):
        return r["h"] * 2 + r["hr"] * 3 + r["rbi"] * 2 + r["bb"]

    notable = sorted(
        [r for r in rows if r["h"] >= 2 or r["hr"] >= 1 or r["rbi"] >= 2],
        key=_score, reverse=True,
    )[:4]

    sentences = [summary]
    for r in notable:
        highlights = []
        if r["hr"] == 1:
            highlights.append("a home run")
        elif r["hr"] > 1:
            highlights.append(f"{r['hr']} home runs")
        if r["d"] >= 2:
            highlights.append(f"{r['d']} doubles")
        elif r["d"] == 1 and not r["hr"]:
            highlights.append("a double")
        if r["t"]:
            highlights.append("a triple")
        if r["rbi"] >= 2:
            highlights.append(f"{r['rbi']} RBI")
        if r["sb"]:
            highlights.append("a stolen base")

        hit_str = f"{r['h']}-for-{r['ab']}" if r["ab"] else None
        if hit_str and highlights:
            sentence = f"{r['name']} went {hit_str} with {', '.join(highlights)}."
        elif hit_str and r["h"] >= 2:
            sentence = f"{r['name']} went {hit_str}."
        elif highlights:
            sentence = f"{r['name']} contributed {', '.join(highlights)}."
        else:
            continue
        sentences.append(sentence)

    # Fallback if no standouts
    if len(sentences) == 1:
        best = max(rows, key=lambda r: (r["h"], r["rbi"], r["hr"]))
        if best["h"] > 0:
            sentences.append(
                f"The offense was quiet — {best['name']} led with "
                f"{best['h']} hit{'s' if best['h'] > 1 else ''}."
            )
        else:
            sentences.append("It was a tough night at the plate — no batter recorded a hit.")

    return " ".join(sentences)


def render_hitter_section(
    info: dict,
    section_header: str = "Hitters",
    header_color: str = "#0E3386",
) -> None:
    """Render the hitter narrative section."""
    team_side = "home" if info["team_is_home"] else "away"

    st.markdown(
        f"<h3 style='color:{header_color};margin-top:0;'>{section_header}</h3>",
        unsafe_allow_html=True,
    )

    with st.spinner("Loading batting data…"):
        try:
            boxscore = get_boxscore(info["game_pk"])
        except Exception as e:
            st.error(f"Could not load boxscore: {e}")
            return

    st.info(hitter_summary(boxscore, team_side))


def render_game_result(
    info: dict,
    game_num: int | None = None,
    show_record: bool = False,
    primary_color: str = "#0E3386",
    win_gif_url: str | None = FLY_THE_W_GIF,
) -> None:
    """Render the game result banner, score display, linescore, and decisions."""
    label     = f"Game {game_num} — " if game_num else ""
    status    = info["status"]
    team_name = info["home_name"] if info["team_is_home"] else info["away_name"]

    if status == "Final":
        if info["team_won"]:
            bg     = f"{primary_color}20"
            border = f"{primary_color}55"
            gif_html = (
                f'<img src="{win_gif_url}" style="height:60px;width:auto;border-radius:4px;" alt="Win">'
                if win_gif_url else ""
            )
            st.markdown(
                f'<div style="background-color:{bg};border:1px solid {border};border-radius:0.375rem;'
                f'padding:1rem 1.25rem;display:flex;align-items:center;gap:1rem;">'
                f'<span style="font-size:1.3rem;font-weight:700;color:{primary_color};">✅ {label}{team_name} win!</span>'
                f'{gif_html}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.error(f"### ❌ {label}{team_name} lose.")
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

    if show_record and info.get("team_record"):
        st.markdown(
            f"<div style='font-size:1.4rem;font-weight:800;color:{primary_color};margin-top:0.5rem;'>"
            f"Season Record: {info['team_record']}</div>",
            unsafe_allow_html=True,
        )


def _render_pitcher_stats(starter: dict, game_pk: int, season: int) -> None:
    """Render detailed stats for a single starting pitcher."""
    stats = starter["stats"]
    ss    = starter["season_stats"]
    pid   = starter["id"]
    name  = starter["name"]

    era  = ss.get("era", "—")
    w    = ss.get("wins", "—")
    l    = ss.get("losses", "—")
    whip = ss.get("whip", "—")
    st.markdown(f"### {name}")
    st.caption(f"{starter['team_name']} · Season: {w}–{l}, {era} ERA, {whip} WHIP")

    ip = stats.get("inningsPitched", "—")
    k  = stats.get("strikeOuts", "—")
    bb = stats.get("baseOnBalls", "—")
    er = stats.get("earnedRuns", "—")
    h  = stats.get("hits", "—")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("IP", ip); c2.metric("K", k); c3.metric("BB", bb)
    c4.metric("ER", er); c5.metric("H", h)

    pitches = stats.get("numberOfPitches", 0)
    strikes = stats.get("strikes", 0)
    hr      = stats.get("homeRuns", "—")
    bf      = stats.get("battersFaced", "—")
    strike_pct = (
        f"{round(int(strikes) / int(pitches) * 100)}%"
        if pitches and strikes else "—"
    )
    c6, c7, c8, c9 = st.columns(4)
    c6.metric("Pitches", pitches or "—"); c7.metric("Strike%", strike_pct)
    c8.metric("HR", hr); c9.metric("Batters Faced", bf)

    st.divider()

    with st.spinner("Loading pitch data…"):
        try:
            usage = get_pitch_usage(game_pk, pid)
        except Exception:
            usage = {}

    st.info(pitcher_summary(name, stats, usage))
    st.markdown("**Pitch Usage — Last Night**")
    st.html(build_pitch_usage_html(usage))

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


def render_pitcher_section(
    info: dict,
    season: int,
    section_header: str = "Starting Pitcher",
    header_color: str = "#0E3386",
) -> None:
    """Render the starting pitcher section for the team side only."""
    game_pk   = info["game_pk"]
    team_side = "home" if info["team_is_home"] else "away"

    st.markdown(
        f"<h3 style='color:{header_color};margin-top:0;'>{section_header}</h3>",
        unsafe_allow_html=True,
    )

    with st.spinner("Loading boxscore…"):
        try:
            boxscore = get_boxscore(game_pk)
        except Exception as e:
            st.error(f"Could not load boxscore: {e}")
            return

    starter = get_starter(boxscore, team_side)
    if starter["id"]:
        _render_pitcher_stats(starter, game_pk, season)
    else:
        st.info("No starting pitcher data available.")


def render_next_game(team_id: int, team_name: str) -> None:
    """Render the tomorrow's game section."""
    st.markdown("#### Tomorrow")
    tomorrow = date.today() + timedelta(days=1)
    try:
        next_game = get_next_team_game(team_id, tomorrow.strftime("%Y-%m-%d"))
    except Exception:
        next_game = None

    if next_game:
        opp_logo_url = team_logo_url(next_game["opp_id"])
        loc_word = "vs" if next_game["team_is_home"] else "@"
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
            f'{logo_tag}{team_name} {loc_word} {next_game["opp_name"]}{time_tag}'
            f'</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown("🏖️ Off Day")
