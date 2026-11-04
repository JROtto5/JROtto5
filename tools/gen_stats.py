#!/usr/bin/env python3
"""Generate the neon stat cards for the JROtto5 profile README.

Writes:
  assets/stats.svg     "SYSTEM TELEMETRY" card: headline numbers + 53x7 heatmap
  assets/activity.svg  monthly contributions bar/area chart with peak callout

Data source (in priority order):
  --live            query `gh api graphql` for the last 12 months and refresh
                    tools/stats_data.json, then render
  --cal PATH        a JSON array of {date, contributionCount} (commit/PR totals
                    taken from --commits/--prs or the existing cache)
  (default)         tools/stats_data.json

Pure stdlib; output SVGs are self-contained (no fonts/images/scripts) so they
render inside GitHub's <img> sandbox.
"""
import argparse
import datetime as dt
import json
import os
import subprocess
import sys
from collections import OrderedDict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, "tools", "stats_data.json")
ASSETS = os.path.join(ROOT, "assets")

TEAL = "#2ef2c8"
PINK = "#ff2e63"
SANS = "'Segoe UI', 'Helvetica Neue', Arial, sans-serif"
MONO = "'DejaVu Sans Mono', Consolas, monospace"
MONTHS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]

QUERY = """
query($login: String!) {
  user(login: $login) {
    pullRequests { totalCount }
    merged: pullRequests(states: MERGED) { totalCount }
    issues { totalCount }
    issueComments { totalCount }
    repositoriesContributedTo(contributionTypes: [COMMIT, PULL_REQUEST, ISSUE, PULL_REQUEST_REVIEW]) { totalCount }
    contributionsCollection {
      totalCommitContributions
      totalPullRequestContributions
      totalIssueContributions
      totalPullRequestReviewContributions
      totalRepositoriesWithContributedCommits
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}
"""


# ---------------------------------------------------------------- data ----
def fetch_live(login):
    out = subprocess.run(
        ["gh", "api", "graphql", "-f", "query=" + QUERY, "-F", "login=" + login],
        check=True, capture_output=True, text=True,
    ).stdout
    u = json.loads(out)["data"]["user"]
    cc = u["contributionsCollection"]
    days = [d for w in cc["contributionCalendar"]["weeks"] for d in w["contributionDays"]]
    return {
        "login": login,
        "fetched": dt.date.today().isoformat(),
        "commits": cc["totalCommitContributions"],
        "prs": cc["totalPullRequestContributions"],
        "issues": cc["totalIssueContributions"],
        "reviews": cc["totalPullRequestReviewContributions"],
        "repos_with_commits": cc["totalRepositoriesWithContributedCommits"],
        "lifetime": {
            "prs": u["pullRequests"]["totalCount"],
            "merged": u["merged"]["totalCount"],
            "issues": u["issues"]["totalCount"],
            "comments": u["issueComments"]["totalCount"],
            "repos": u["repositoriesContributedTo"]["totalCount"],
        },
        "days": [{"date": d["date"], "contributionCount": d["contributionCount"]} for d in days],
    }


def load_data(args):
    if args.live:
        data = fetch_live(args.login)
        with open(CACHE, "w") as f:
            json.dump(data, f, indent=1)
        return data
    cache = {}
    if os.path.exists(CACHE):
        with open(CACHE) as f:
            cache = json.load(f)
    if args.cal:
        with open(args.cal) as f:
            days = json.load(f)
        data = {
            "login": args.login,
            "fetched": max(d["date"] for d in days),
            "commits": args.commits if args.commits is not None else cache.get("commits", 0),
            "prs": args.prs if args.prs is not None else cache.get("prs", 0),
            "days": days,
        }
        for k in ("issues", "reviews", "repos_with_commits", "lifetime"):
            if k in cache:
                data[k] = cache[k]
        with open(CACHE, "w") as f:
            json.dump(data, f, indent=1)
        return data
    if not cache:
        sys.exit("no data: run with --live or --cal PATH")
    return cache


def derive(data):
    days = sorted(data["days"], key=lambda d: d["date"])
    counts = [d["contributionCount"] for d in days]
    longest = run = 0
    for c in counts:
        run = run + 1 if c else 0
        longest = max(longest, run)
    # current streak: today may still be empty without breaking the streak
    i = len(counts) - 1
    if i >= 0 and counts[i] == 0:
        i -= 1
    current = 0
    while i >= 0 and counts[i]:
        current += 1
        i -= 1
    peak_i = max(range(len(counts)), key=lambda k: counts[k])
    return {
        "days": days,
        "total": sum(counts),
        "active": sum(1 for c in counts if c),
        "longest": longest,
        "current": current,
        "max_day": counts[peak_i],
        "max_day_date": days[peak_i]["date"],
    }


# ---------------------------------------------------------- helpers -------
def fmt(n):
    return f"{n:,}"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def common_defs(w, h):
    return f"""
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#07070d"/>
      <stop offset="0.55" stop-color="#120a1c"/>
      <stop offset="1" stop-color="#1a0610"/>
    </linearGradient>
    <linearGradient id="tp" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{TEAL}"/>
      <stop offset="0.5" stop-color="#ffffff"/>
      <stop offset="1" stop-color="{PINK}"/>
    </linearGradient>
    <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
      <path d="M40 0H0V40" fill="none" stroke="{TEAL}" stroke-opacity="0.06"/>
    </pattern>
    <filter id="glow" x="-30%" y="-60%" width="160%" height="220%">
      <feGaussianBlur stdDeviation="5" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="glowS" x="-100%" y="-100%" width="300%" height="300%">
      <feGaussianBlur stdDeviation="2.4" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>"""


def common_css():
    return f"""
      .k {{ font: 600 14px {MONO}; letter-spacing: 3px; fill: {TEAL}; }}
      .kp {{ font: 600 14px {MONO}; letter-spacing: 3px; fill: {PINK}; }}
      .lbl {{ font: 600 12px {MONO}; letter-spacing: 3px; fill: #8a8aa0; }}
      .sub {{ font: 600 12px {MONO}; letter-spacing: 2px; fill: #6f6f86; }}
      .blink {{ animation: blink 1.1s steps(1) infinite; }}
      @keyframes blink {{ 50% {{ opacity: 0; }} }}
      .in {{ animation: in .9s cubic-bezier(.2,.8,.2,1) both; }}
      @keyframes in {{ from {{ opacity: 0; transform: translateY(14px); }} to {{ opacity: 1; transform: none; }} }}
      .fade {{ animation: fade 1.2s ease-out both; }}
      @keyframes fade {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}"""


def frame(w, h, left, right, foot_l, foot_r):
    return f"""  <rect width="{w}" height="{h}" fill="url(#bg)"/>
  <rect width="{w}" height="{h}" fill="url(#grid)"/>
  <path d="M0 36H{w}" stroke="{TEAL}" stroke-opacity="0.35"/>
  <path d="M0 {h-34}H{w}" stroke="{PINK}" stroke-opacity="0.5"/>
  <text x="40" y="24" class="k">{left}</text>
  <text x="{w-40}" y="24" class="k" text-anchor="end">{right}</text>
  <text x="40" y="{h-12}" class="k">{foot_l}<tspan class="blink">_</tspan></text>
  <text x="{w-40}" y="{h-12}" class="kp" text-anchor="end">{foot_r}</text>
"""


# ------------------------------------------------------------ stats.svg ---
LEVELS = ["#17141f", "#0f4a43", "#1f9e88", TEAL, "#c45cff", PINK]


def quantile_levels(counts):
    nz = sorted(c for c in counts if c)
    if not nz:
        return (lambda c: 0), [0, 0, 0, 0]
    qs = [nz[min(len(nz) - 1, int(len(nz) * p))] for p in (0.25, 0.5, 0.75, 0.9)]

    def level(c):
        if c == 0:
            return 0
        for i, q in enumerate(qs):
            if c <= q:
                return i + 1
        return 5
    return level, qs


def build_stats(data, s):
    W, H = 1200, 470
    days = s["days"]
    level, qs = quantile_levels([d["contributionCount"] for d in days])

    first = dt.date.fromisoformat(days[0]["date"])
    start = first - dt.timedelta(days=(first.weekday() + 1) % 7)  # back to Sunday
    cell, gap = 16, 4
    pitch = cell + gap
    gx, gy = 96, 252
    ncols = ((dt.date.fromisoformat(days[-1]["date"]) - start).days // 7) + 1

    # ---- headline numbers
    stats = [
        ("CONTRIBUTIONS", fmt(s["total"]), f"{s['active']} ACTIVE DAYS", TEAL),
        ("COMMITS", fmt(data["commits"]), f"PEAK {s['max_day']} / DAY", "#ffffff"),
        ("PULL REQUESTS", fmt(data["prs"]), f"~{round(data['prs'] / 52)} / WEEK", "#ffffff"),
        ("LONGEST STREAK", f"{s['longest']}D", f"CURRENT {s['current']}D", PINK),
    ]
    colw = (W - 80) / 4
    tiles = []
    for i, (lab, val, sub, col) in enumerate(stats):
        x = 40 + i * colw
        delay = 0.15 + i * 0.18
        divider = "" if i == 0 else f'<path d="M{x:.0f} 62V168" stroke="{TEAL}" stroke-opacity="0.18"/>'
        tx = x + (0 if i == 0 else 28)
        fill = "url(#tp)" if col == "#ffffff" else col
        tiles.append(f"""  {divider}
  <g class="in" style="animation-delay:{delay:.2f}s">
    <text x="{tx:.0f}" y="80" class="lbl">{lab}</text>
    <g filter="url(#glow)"><text x="{tx:.0f}" y="140" class="num" fill="{fill}">{val}</text></g>
    <text x="{tx:.0f}" y="166" class="sub">{sub}</text>
  </g>""")

    # ---- heatmap
    rects, glows = [], []
    by_date = {d["date"]: d["contributionCount"] for d in days}
    month_labels = []
    last_month = None
    for col in range(ncols):
        for row in range(7):
            day = start + dt.timedelta(days=col * 7 + row)
            key = day.isoformat()
            if key not in by_date:
                continue
            c = by_date[key]
            lv = level(c)
            x, y = gx + col * pitch, gy + row * pitch
            delay = 0.6 + col * 0.018
            r = (f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="3" '
                 f'fill="{LEVELS[lv]}" style="animation-delay:{delay:.2f}s"'
                 + (' class="fade"' if lv else '')
                 + f'><title>{key}: {c}</title></rect>')
            (glows if lv == 5 else rects).append(r)
            if row == 0 or day.day == 1:
                pass
        top = start + dt.timedelta(days=col * 7)
        ref = top + dt.timedelta(days=6) if top.day > 24 else top
        m = ref.month
        if m != last_month:
            month_labels.append((col, m, ref.year if m == 1 else None))
            last_month = m
    ml = []
    for idx, (col, m, yr) in enumerate(month_labels):
        nxt = month_labels[idx + 1][0] if idx + 1 < len(month_labels) else ncols
        if nxt - col < 2:
            continue
        label = MONTHS[m - 1] + (f" '{str(yr)[2:]}" if yr else "")
        ml.append(f'<text x="{gx + col * pitch}" y="{gy - 12}" class="lbl">{label}</text>')
    daylab = "".join(
        f'<text x="{gx - 14}" y="{gy + r * pitch + 12}" class="sub" text-anchor="end">{t}</text>'
        for r, t in ((1, "MON"), (3, "WED"), (5, "FRI"))
    )
    grid_w = ncols * pitch - gap
    grid_h = 7 * pitch - gap

    # ---- legend
    ly = gy + grid_h + 24
    lx = gx + grid_w - 46  # leave room for MORE
    legend = [f'<text x="{lx - 6 * 20 - 10}" y="{ly + 11}" class="sub" text-anchor="end">LESS</text>']
    for i, c in enumerate(LEVELS):
        f = ' filter="url(#glowS)"' if i == 5 else ""
        legend.append(f'<rect x="{lx - (6 - i) * 20 + 4}" y="{ly}" width="{cell - 2}" height="{cell - 2}" rx="3" fill="{c}"{f}/>')
    legend.append(f'<text x="{lx + 10}" y="{ly + 11}" class="sub">MORE</text>')
    qtxt = f'QUANTILE BUCKETS · 1-{qs[0]} · -{qs[1]} · -{qs[2]} · -{qs[3]} · {qs[3] + 1}+'
    legend.append(f'<text x="{gx}" y="{ly + 11}" class="sub">{qtxt}</text>')

    css = common_css() + f"""
      .num {{ font: 800 50px {SANS}; letter-spacing: 2px; }}
      .scan {{ animation: scan 9s linear infinite; }}
      @keyframes scan {{ from {{ transform: translateX(0); }} to {{ transform: translateX({grid_w + 172}px); }} }}
      .hot {{ animation: hot 2.8s ease-in-out infinite; }}
      @keyframes hot {{ 0%,100% {{ opacity: 1; }} 50% {{ opacity: .72; }} }}"""

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <title>JROtto5 - GitHub telemetry, last 12 months</title>
  <defs>{common_defs(W, H)}
    <linearGradient id="beam" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{TEAL}" stop-opacity="0"/>
      <stop offset="0.8" stop-color="{TEAL}" stop-opacity="0.16"/>
      <stop offset="1" stop-color="#ffffff" stop-opacity="0.5"/>
    </linearGradient>
    <clipPath id="gclip"><rect x="{gx - 4}" y="{gy - 4}" width="{grid_w + 8}" height="{grid_h + 8}"/></clipPath>
    <style>{css}
    </style>
  </defs>
{frame(W, H, "// SYSTEM TELEMETRY · GITHUB", "LAST 12 MONTHS", "&gt; uptime nominal", f"SYNC {data['fetched']}")}
{chr(10).join(tiles)}
  <path d="M40 196H{W - 40}" stroke="{TEAL}" stroke-opacity="0.18" stroke-dasharray="2 6"/>
  <text x="40" y="222" class="k">// CONTRIBUTION MATRIX</text>
  <text x="{W - 40}" y="222" class="lbl" text-anchor="end">53 WK × 7 D · {fmt(s['total'])} EVENTS</text>
  {''.join(ml)}
  {daylab}
  <g>
    {''.join(rects)}
  </g>
  <g filter="url(#glowS)"><g class="hot">
    {''.join(glows)}
  </g></g>
  <g clip-path="url(#gclip)">
    <rect class="scan" x="{gx - 90}" y="{gy - 4}" width="80" height="{grid_h + 8}" fill="url(#beam)"/>
  </g>
  {''.join(legend)}
</svg>
"""
    return svg


# --------------------------------------------------------- activity.svg ---
def build_activity(data, s):
    W, H = 1200, 340
    monthly = OrderedDict()
    span = OrderedDict()
    for d in s["days"]:
        k = d["date"][:7]
        monthly[k] = monthly.get(k, 0) + d["contributionCount"]
        span[k] = span.get(k, 0) + 1
    keys = list(monthly)
    vals = [monthly[k] for k in keys]
    peak = max(range(len(vals)), key=lambda i: vals[i])

    px0, px1 = 96, W - 40
    py0, py1 = 92, 250  # chart top / baseline
    n = len(keys)
    slot = (px1 - px0) / n
    bw = slot * 0.56
    vmax = max(vals) * 1.12 or 1

    def yv(v):
        return py1 - (py1 - py0) * v / vmax

    # nice gridlines
    step = 1000 if vmax > 3000 else 500 if vmax > 1200 else 100
    gl = []
    v = step
    while v < vmax:
        y = yv(v)
        gl.append(f'<path d="M{px0} {y:.1f}H{px1}" stroke="{TEAL}" stroke-opacity="0.08"/>'
                  f'<text x="{px0 - 12}" y="{y + 4:.1f}" class="sub" text-anchor="end">{fmt(v)}</text>')
        v += step
    gl.append(f'<text x="{px0 - 12}" y="{py1 + 4}" class="sub" text-anchor="end">0</text>')

    bars, labels, pts = [], [], []
    for i, (k, v) in enumerate(zip(keys, vals)):
        cx = px0 + slot * (i + 0.5)
        y = yv(v)
        yr, mo = int(k[:4]), int(k[5:])
        full = dt.date(yr + (mo == 12), mo % 12 + 1, 1) - dt.timedelta(days=1)
        partial = span[k] < full.day - 1
        is_peak = i == peak
        fill = "url(#barP)" if is_peak else "url(#barT)"
        op = ' fill-opacity="0.45"' if partial else ""
        delay = 0.1 + i * 0.07
        bars.append(f'<rect class="grow" style="animation-delay:{delay:.2f}s" x="{cx - bw / 2:.1f}" y="{y:.1f}" '
                    f'width="{bw:.1f}" height="{py1 - y:.1f}" rx="3" fill="{fill}"{op}>'
                    f'<title>{k}: {v}</title></rect>')
        lab = MONTHS[mo - 1]
        cls = "kp" if is_peak else "lbl"
        labels.append(f'<text x="{cx:.1f}" y="{py1 + 22}" class="{cls}" text-anchor="middle">{lab}</text>')
        if mo == 1 or i == 0:
            labels.append(f'<text x="{cx:.1f}" y="{py1 + 38}" class="sub" text-anchor="middle">{yr}</text>')
        if partial and i == n - 1:
            labels.append(f'<text x="{cx:.1f}" y="{py1 + 38}" class="sub" text-anchor="middle">MTD</text>')
        if v and not is_peak:
            t = fmt(v)
            cw = len(t) * 8 + 10
            labels.append(f'<rect x="{cx - cw / 2:.1f}" y="{y - 27:.1f}" width="{cw}" height="17" rx="3" '
                          f'fill="#0a0912" fill-opacity="0.85" stroke="{TEAL}" stroke-opacity="0.25"/>'
                          f'<text x="{cx:.1f}" y="{y - 14:.1f}" class="val" text-anchor="middle">{t}</text>')
        pts.append((cx, y))

    # monotone cubic (Fritsch-Carlson) through bar tops: no overshoot
    def tangents(p):
        n_ = len(p)
        d = [(p[i + 1][1] - p[i][1]) / (p[i + 1][0] - p[i][0]) for i in range(n_ - 1)]
        m = [d[0]] + [0 if d[i - 1] * d[i] <= 0 else (d[i - 1] + d[i]) / 2 for i in range(1, n_ - 1)] + [d[-1]]
        for i in range(n_ - 1):
            if d[i] == 0:
                m[i] = m[i + 1] = 0
                continue
            a_, b_ = m[i] / d[i], m[i + 1] / d[i]
            h = a_ * a_ + b_ * b_
            if h > 9:
                t = 3 / h ** 0.5
                m[i], m[i + 1] = t * a_ * d[i], t * b_ * d[i]
        return m

    tg = tangents(pts)

    def seg(i):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        dx = (x1 - x0) / 3
        return f" C{x0 + dx:.1f} {y0 + tg[i] * dx:.1f} {x1 - dx:.1f} {y1 - tg[i + 1] * dx:.1f} {x1:.1f} {y1:.1f}"

    last_partial = span[keys[-1]] < 27
    solid_n = n - 1 if last_partial else n
    line = f"M{pts[0][0]:.1f} {pts[0][1]:.1f}" + "".join(seg(i) for i in range(solid_n - 1))
    tail = (f"M{pts[-2][0]:.1f} {pts[-2][1]:.1f}" + seg(n - 2)) if last_partial else ""
    area = (f"M{pts[0][0]:.1f} {pts[0][1]:.1f}" + "".join(seg(i) for i in range(n - 1))
            + f" L{pts[-1][0]:.1f} {py1} L{pts[0][0]:.1f} {py1} Z")
    dots = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="#07070d" stroke="{TEAL}" stroke-width="1.6"/>'
                   for i, (x, y) in enumerate(pts) if i != peak)

    pxk, pyk = pts[peak]
    pk = keys[peak]
    pk_label = f"PEAK · {MONTHS[int(pk[5:]) - 1]} {pk[:4]}"
    callout_x = pxk - 18
    callout = f"""
  <g class="in" style="animation-delay:1.3s">
    <circle cx="{pxk:.1f}" cy="{pyk:.1f}" r="11" fill="none" stroke="{PINK}" stroke-opacity="0.5" class="ping"/>
    <circle cx="{pxk:.1f}" cy="{pyk:.1f}" r="5" fill="{PINK}" filter="url(#glowS)"/>
    <path d="M{pxk:.1f} {pyk - 10:.1f}V{py0 - 24}H{callout_x - 8:.1f}" fill="none" stroke="{PINK}" stroke-opacity="0.8" stroke-dasharray="3 3"/>
    <text x="{callout_x - 16:.1f}" y="{py0 - 34}" class="kp" text-anchor="end">{pk_label}</text>
    <g filter="url(#glow)"><text x="{callout_x - 16:.1f}" y="{py0 - 4}" class="big" text-anchor="end">{fmt(vals[peak])}</text></g>
  </g>"""

    total = s["total"]
    avg = round(total / max(1, len(s["days"])) * 30.4)
    css = common_css() + f"""
      .val {{ font: 600 12px {MONO}; letter-spacing: 1px; fill: #c9c9d6; }}
      .big {{ font: 800 30px {SANS}; letter-spacing: 2px; fill: {PINK}; }}
      .grow {{ transform-box: fill-box; transform-origin: 50% 100%; animation: grow 1s cubic-bezier(.2,.8,.2,1) both; }}
      @keyframes grow {{ from {{ transform: scaleY(0); }} to {{ transform: scaleY(1); }} }}
      .draw {{ stroke-dasharray: 3000; animation: draw 2.4s ease-out .4s both; }}
      @keyframes draw {{ from {{ stroke-dashoffset: 3000; }} to {{ stroke-dashoffset: 0; }} }}
      .ping {{ transform-box: fill-box; transform-origin: center; animation: ping 2.2s ease-out infinite; }}
      @keyframes ping {{ 0% {{ transform: scale(.6); opacity: 1; }} 100% {{ transform: scale(2.2); opacity: 0; }} }}"""

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <title>JROtto5 - monthly contributions, last 12 months</title>
  <defs>{common_defs(W, H)}
    <linearGradient id="barT" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{TEAL}" stop-opacity="0.55"/>
      <stop offset="1" stop-color="{TEAL}" stop-opacity="0.06"/>
    </linearGradient>
    <linearGradient id="barP" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{PINK}" stop-opacity="0.85"/>
      <stop offset="1" stop-color="{PINK}" stop-opacity="0.1"/>
    </linearGradient>
    <linearGradient id="area" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{TEAL}" stop-opacity="0.22"/>
      <stop offset="1" stop-color="{TEAL}" stop-opacity="0"/>
    </linearGradient>
    <style>{css}
    </style>
  </defs>
{frame(W, H, "// ACTIVITY.LOG · CONTRIBUTIONS / MONTH", "LAST 12 MONTHS", "&gt; throughput rising", f"AVG {fmt(avg)} / MO · TOTAL {fmt(total)}")}
  {''.join(gl)}
  <path d="M{px0} {py1}H{px1}" stroke="{TEAL}" stroke-opacity="0.4"/>
  {''.join(bars)}
  <path class="fade" style="animation-delay:.8s" d="{area}" fill="url(#area)"/>
  <g filter="url(#glowS)"><path class="draw" d="{line}" fill="none" stroke="{TEAL}" stroke-width="2.4" stroke-linejoin="round"/></g>
  <path class="fade" style="animation-delay:2.4s" d="{tail}" fill="none" stroke="{TEAL}" stroke-opacity="0.6" stroke-width="1.8" stroke-dasharray="4 5"/>
  {dots}
  {''.join(labels)}
  {callout}
</svg>
"""
    return svg


# -------------------------------------------------------- breakdown.svg ---
def build_breakdown(data, s):
    import math
    W, H = 1200, 440
    lt = data["lifetime"]
    axes = [  # GitHub's activity-overview orientation
        ("CODE REVIEW", data.get("reviews", 0), 0, -1),
        ("ISSUES", data.get("issues", 0), 1, 0),
        ("PULL REQUESTS", data["prs"], 0, 1),
        ("COMMITS", data["commits"], -1, 0),
    ]
    tot = sum(a[1] for a in axes) or 1
    cx, cy, R = 300, 230, 110
    smax = math.sqrt(max(a[1] for a in axes) / tot) or 1

    rings = []
    for f in (0.25, 0.5, 0.75, 1.0):
        r = R * f
        rings.append(f'<path d="M{cx} {cy - r}L{cx + r} {cy}L{cx} {cy + r}L{cx - r} {cy}Z" fill="none" '
                     f'stroke="{TEAL}" stroke-opacity="{0.08 if f < 1 else 0.3}"/>')
    rings.append(f'<path d="M{cx} {cy - R}V{cy + R}M{cx - R} {cy}H{cx + R}" stroke="{TEAL}" stroke-opacity="0.18"/>')

    pts, marks, labs = [], [], []
    for i, (name, v, dx, dy) in enumerate(axes):
        share = v / tot
        r = max(6, R * math.sqrt(share) / smax)
        x, y = cx + dx * r, cy + dy * r
        pts.append((x, y))
        marks.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.5" fill="{PINK if i % 2 else TEAL}" filter="url(#glowS)"/>')
        pct = f"{share * 100:.1f}%" if share < 0.1 else f"{share * 100:.0f}%"
        if dy:  # top / bottom
            ty = cy + dy * (R + 30)
            anchor, tx = "middle", cx
            l1y, l2y = (ty - 16, ty) if dy < 0 else (ty - 4, ty + 12)
        else:
            tx = cx + dx * (R + 22)
            anchor = "start" if dx > 0 else "end"
            l1y, l2y = cy - 6, cy + 12
        labs.append(f'<text x="{tx}" y="{l1y:.0f}" class="lbl" text-anchor="{anchor}">{name}</text>'
                    f'<text x="{tx}" y="{l2y:.0f}" class="val" text-anchor="{anchor}">'
                    f'<tspan class="pc">{pct}</tspan> · {fmt(v)}</text>')
    poly = "M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + "Z"

    # merged gauge
    gx, gy, gr = 690, 230, 92
    rate = lt["merged"] / lt["prs"] if lt["prs"] else 0
    circ = 2 * math.pi * gr
    on = circ * rate
    ticks = "".join(
        f'<path d="M{gx + (gr + 14) * math.cos(a):.1f} {gy + (gr + 14) * math.sin(a):.1f}'
        f'L{gx + (gr + 20) * math.cos(a):.1f} {gy + (gr + 20) * math.sin(a):.1f}" stroke="{TEAL}" stroke-opacity="0.35"/>'
        for a in (k * math.pi / 20 for k in range(40)))
    gauge = f"""
  <g class="in" style="animation-delay:.5s">
    {ticks}
    <circle cx="{gx}" cy="{gy}" r="{gr}" fill="none" stroke="#1d1a2a" stroke-width="14"/>
    <circle cx="{gx}" cy="{gy}" r="{gr}" fill="none" stroke="#3a2140" stroke-opacity="0.9" stroke-width="14"
      stroke-dasharray="{circ - on:.1f} {circ:.1f}" stroke-dashoffset="{-on:.1f}" transform="rotate(-90 {gx} {gy})"/>
    <g filter="url(#glowS)"><circle class="arc" cx="{gx}" cy="{gy}" r="{gr}" fill="none" stroke="url(#ring)" stroke-width="14"
      stroke-linecap="round" stroke-dasharray="{on:.1f} {circ:.1f}" transform="rotate(-90 {gx} {gy})"/></g>
    <g filter="url(#glow)"><text x="{gx}" y="{gy + 8}" class="gnum" text-anchor="middle">{rate * 100:.0f}%</text></g>
    <text x="{gx}" y="{gy + 34}" class="lbl" text-anchor="middle">PRS MERGED</text>
    <text x="{gx}" y="{gy + gr + 46}" class="val" text-anchor="middle">{fmt(lt['merged'])} / {fmt(lt['prs'])} PRS</text>
  </g>"""

    # lifetime panel
    px, pw = 860, 300
    rows = [
        ("PRS OPENED", fmt(lt["prs"]), TEAL),
        ("PRS MERGED", fmt(lt["merged"]), PINK),
        ("COMMENTS", fmt(lt["comments"]), TEAL),
        ("ISSUES OPENED", fmt(lt["issues"]), TEAL),
        ("REPOS CONTRIBUTED", fmt(lt["repos"]), PINK),
    ]
    panel = [f'<rect x="{px}" y="80" width="{pw}" height="310" rx="6" fill="#0a0912" fill-opacity="0.6" '
             f'stroke="{TEAL}" stroke-opacity="0.25"/>',
             f'<path d="M{px} 80h18M{px} 80v18M{px + pw} 390h-18M{px + pw} 390v-18" stroke="{PINK}" stroke-width="2"/>',
             f'<text x="{px + 20}" y="110" class="k">// LIFETIME</text>']
    for i, (lab, val, col) in enumerate(rows):
        y = 154 + i * 52
        panel.append(f'<g class="in" style="animation-delay:{0.3 + i * 0.12:.2f}s">'
                     f'<text x="{px + 20}" y="{y}" class="lbl">{lab}</text>'
                     f'<text x="{px + pw - 20}" y="{y + 2}" class="pnum" fill="{col}" text-anchor="end">{val}</text>'
                     + (f'<path d="M{px + 20} {y + 18}H{px + pw - 20}" stroke="{TEAL}" stroke-opacity="0.1"/>' if i < len(rows) - 1 else "")
                     + '</g>')

    css = common_css() + f"""
      .val {{ font: 600 13px {MONO}; letter-spacing: 1px; fill: #c9c9d6; }}
      .pc {{ fill: #ffffff; font-weight: 700; }}
      .gnum {{ font: 800 46px {SANS}; letter-spacing: 1px; fill: #ffffff; }}
      .pnum {{ font: 800 24px {SANS}; letter-spacing: 1px; }}
      .radar {{ transform-origin: {cx}px {cy}px; animation: pop 1.1s cubic-bezier(.2,.8,.2,1) .2s both; }}
      @keyframes pop {{ from {{ transform: scale(0); opacity: 0; }} to {{ transform: scale(1); opacity: 1; }} }}
      .pulse {{ animation: pulse 3.2s ease-in-out infinite; }}
      @keyframes pulse {{ 0%,100% {{ fill-opacity: .16; }} 50% {{ fill-opacity: .3; }} }}
      .arc {{ animation: arc 1.8s cubic-bezier(.2,.8,.2,1) .5s both; }}
      @keyframes arc {{ from {{ stroke-dashoffset: {on:.1f}; }} to {{ stroke-dashoffset: 0; }} }}"""

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <title>JROtto5 - activity breakdown</title>
  <defs>{common_defs(W, H)}
    <linearGradient id="ring" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{TEAL}"/>
      <stop offset="1" stop-color="{PINK}"/>
    </linearGradient>
    <linearGradient id="rfill" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{TEAL}"/>
      <stop offset="1" stop-color="{PINK}"/>
    </linearGradient>
    <style>{css}
    </style>
  </defs>
{frame(W, H, "// ACTIVITY.OVERVIEW · BREAKDOWN", "LAST 12 MONTHS · LIFETIME", f"&gt; {data.get('repos_with_commits', 0)} repos with commits this year", "SQRT-SCALED SHARES")}
  {''.join(rings)}
  <g class="radar">
    <path class="pulse" d="{poly}" fill="url(#rfill)" fill-opacity="0.2"/>
    <g filter="url(#glowS)"><path d="{poly}" fill="none" stroke="{TEAL}" stroke-width="2.2" stroke-linejoin="round"/></g>
    {''.join(marks)}
  </g>
  {''.join(labs)}
  <path d="M520 90V376" stroke="{TEAL}" stroke-opacity="0.15" stroke-dasharray="2 6"/>
  {gauge}
  {''.join(panel)}
</svg>
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--live", action="store_true", help="fetch fresh data via gh api graphql")
    ap.add_argument("--cal", help="path to a JSON array of {date, contributionCount}")
    ap.add_argument("--commits", type=int)
    ap.add_argument("--prs", type=int)
    ap.add_argument("--login", default="JROtto5")
    args = ap.parse_args()

    data = load_data(args)
    s = derive(data)
    os.makedirs(ASSETS, exist_ok=True)
    outs = [("stats.svg", build_stats(data, s)), ("activity.svg", build_activity(data, s))]
    if "lifetime" in data:
        outs.append(("breakdown.svg", build_breakdown(data, s)))
    else:
        print("skip breakdown.svg: no issues/reviews/lifetime data (run --live)")
    for name, svg in outs:
        path = os.path.join(ASSETS, name)
        with open(path, "w") as f:
            f.write(svg)
        print("wrote", path)
    print(f"total={s['total']} commits={data['commits']} prs={data['prs']} active={s['active']} "
          f"longest={s['longest']} current={s['current']} max={s['max_day']}")


if __name__ == "__main__":
    main()
