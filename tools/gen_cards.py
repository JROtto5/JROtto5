#!/usr/bin/env python3
"""Neon repo cards for the profile README (self-hosted alternative to pin cards).
Reads live star/fork counts with `gh api`; writes assets/cards/<repo>.svg."""
import json, os, subprocess, textwrap
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEAL, PINK = "#2ef2c8", "#ff2e63"
LANG = {"TypeScript": "#3178c6", "JavaScript": "#f1e05a", "HTML": "#e34c26", "Shell": "#89e051", "Python": "#3572A5"}
CARDS = [
  ("dragon-front", "DRAGON FRONT", "Browser FPS with my own authoritative netcode server: 94k lines, 20 maps, campaign, Steamworks.", "Three.js · Node netcode", "JavaScript", "◆ FLAGSHIP", PINK),
  ("dot-universe", "DOT UNIVERSE", "Roguelike shooter + idle game on one account, with cross-game progression and global leaderboards.", "Next.js · Phaser 3 · Supabase", "TypeScript", "▶ PLAY", TEAL),
  ("nfl-edge", "THE EDGE BOARD", "Sports forecasting with ~30 measured signals, its own power ratings and a public, auto-graded track record.", "Vercel · cron · web push", "JavaScript", "● LIVE", PINK),
  ("draft-war-room", "DRAFT WAR ROOM", "Fantasy decision cockpit: Monte Carlo odds, start/sit consensus, waiver radar, live injuries.", "Zero-build PWA · Vercel · MIT", "JavaScript", "● LIVE", PINK),
  ("sith-os", "SITH OS", "My own Arch Linux distro: archiso + Calamares installer, ~240 packages, themed from boot to terminal.", "archiso · KDE Plasma · Calamares", "Shell", "⬡ DISTRO", TEAL),
  ("neon-spin", "NEON SPIN", "Idle/incremental game in one HTML file: up to 7 reels, 40 upgrades, 39 achievements, prestige.", "Vanilla JS · GitHub Pages", "HTML", "▶ PLAY", TEAL),
]
def esc(s): return s.replace("&", "&amp;").replace("<", "&lt;")
def stats(repo):
    if repo == "dragon-front": return 0, 0
    try:
        d = json.loads(subprocess.run(["gh", "api", f"repos/JROtto5/{repo}", "--jq", "{s:.stargazers_count,f:.forks_count}"], capture_output=True, text=True, timeout=30).stdout)
        return d["s"], d["f"]
    except Exception: return 0, 0
def card(repo, title, desc, stack, lang, tag, accent):
    s, f = stats(repo)
    lines = textwrap.wrap(desc, 58)[:3]
    W, H = 560, 190
    body = "".join(f'<text x="28" y="{86 + i*21}" class="d">{esc(l)}</text>' for i, l in enumerate(lines))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0a0a12"/><stop offset="1" stop-color="#140b1f"/></linearGradient>
<filter id="g" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<pattern id="grid" width="28" height="28" patternUnits="userSpaceOnUse"><path d="M28 0H0V28" fill="none" stroke="{accent}" stroke-opacity=".06"/></pattern>
<style>.t{{font:800 24px 'Segoe UI','Helvetica Neue',Arial,sans-serif;letter-spacing:3px;fill:#fff}}
.d{{font:400 15px 'Segoe UI','Helvetica Neue',Arial,sans-serif;fill:#b9bccb}}
.m{{font:700 12px 'DejaVu Sans Mono',Consolas,monospace;letter-spacing:2px}}
.edge{{animation:e 4s ease-in-out infinite}}@keyframes e{{0%,100%{{stroke-opacity:.5}}50%{{stroke-opacity:1}}}}</style></defs>
<path d="M14 1H{W-1}V{H-15}L{W-15} {H-1}H1V15Z" fill="url(#bg)"/>
<path d="M14 1H{W-1}V{H-15}L{W-15} {H-1}H1V15Z" fill="url(#grid)"/>
<path class="edge" d="M14 1H{W-1}V{H-15}L{W-15} {H-1}H1V15Z" fill="none" stroke="{accent}" stroke-width="1.6" filter="url(#g)"/>
<rect x="28" y="26" width="4" height="26" fill="{accent}" filter="url(#g)"/>
<text x="42" y="48" class="t">{esc(title)}</text>
<text x="{W-28}" y="44" class="m" text-anchor="end" fill="{accent}">{esc(tag)}</text>
{body}
<path d="M28 {H-52}H{W-28}" stroke="#ffffff" stroke-opacity=".08"/>
<circle cx="34" cy="{H-29}" r="6" fill="{LANG.get(lang, '#888')}"/>
<text x="48" y="{H-25}" class="m" fill="#d6d8e2">{esc(lang.upper())}</text>
<text x="{48 + len(lang)*10 + 18}" y="{H-25}" class="m" fill="#7d8196">{esc(stack.upper())}</text>
<text x="{W-28}" y="{H-25}" class="m" text-anchor="end" fill="{accent}">{'CASE STUDY →' if repo=='dragon-front' else (f'★ {s}  ' if s>=10 else '') + 'OPEN →'}</text>
</svg>'''
for c in CARDS:
    open(os.path.join(ROOT, "assets", "cards", f"{c[0]}.svg"), "w").write(card(*c))
    print("wrote", c[0])
