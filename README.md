<p align="center">
  <img src="assets/banner.svg" alt="JROtto5: games, products, Linux" width="100%">
</p>

<p align="center">
  <b>I build games I actually want to play and products people actually use, and I finish them.</b><br>
  A 75k-line 3D shooter · live analytics apps · my own Linux distro · a short film rendered entirely from code.
</p>

<p align="center">
  <a href="#-flagship-dragon-front">🐉 Dragon Front</a> ·
  <a href="#-products">🚀 Products</a> ·
  <a href="#-linux">🐧 Linux</a> ·
  <a href="#-games--creative-code">🎨 Games & Creative Code</a> ·
  <a href="#-how-i-work">⚡ How I Work</a>
</p>

<p align="center">
  <a href="https://jrotto5.github.io/neon-spin/"><img src="https://img.shields.io/badge/▶_PLAY-NEON_SPIN-ff2e63?style=for-the-badge"></a>
  <a href="https://nfl-edge-kappa.vercel.app"><img src="https://img.shields.io/badge/●_LIVE-THE_EDGE_BOARD-2ef2c8?style=for-the-badge&labelColor=0b0b12"></a>
  <a href="https://github.com/JROtto5/sith-os"><img src="https://img.shields.io/badge/⬇_ISO-SITH_OS-8b5cf6?style=for-the-badge&labelColor=0b0b12"></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/JavaScript-0b0b12?style=for-the-badge&logo=javascript&logoColor=f7df1e">
  <img src="https://img.shields.io/badge/Three.js-0b0b12?style=for-the-badge&logo=threedotjs&logoColor=white">
  <img src="https://img.shields.io/badge/Python-0b0b12?style=for-the-badge&logo=python&logoColor=3776ab">
  <img src="https://img.shields.io/badge/TypeScript-0b0b12?style=for-the-badge&logo=typescript&logoColor=3178c6">
  <img src="https://img.shields.io/badge/Java-0b0b12?style=for-the-badge&logo=openjdk&logoColor=white">
  <img src="https://img.shields.io/badge/Postgres-0b0b12?style=for-the-badge&logo=postgresql&logoColor=4169e1">
  <img src="https://img.shields.io/badge/AWS-0b0b12?style=for-the-badge&logo=amazonwebservices&logoColor=ff9900">
  <img src="https://img.shields.io/badge/Vercel-0b0b12?style=for-the-badge&logo=vercel&logoColor=white">
  <img src="https://img.shields.io/badge/Arch_Linux-0b0b12?style=for-the-badge&logo=archlinux&logoColor=1793d1">
  <img src="https://img.shields.io/badge/KDE_Plasma-0b0b12?style=for-the-badge&logo=kde&logoColor=1d99f3">
  <img src="https://img.shields.io/badge/FFmpeg-0b0b12?style=for-the-badge&logo=ffmpeg&logoColor=5cb85c">
  <img src="https://img.shields.io/badge/Claude_API-0b0b12?style=for-the-badge&logo=anthropic&logoColor=d4a27f">
</p>

---

## 🐉 Flagship: Dragon Front

<p align="center">
  <img src="assets/dragon-front-keyart.jpg" alt="Dragon Front key art" width="100%">
</p>

**A Modern Warfare-style FPS that runs in the browser. I designed and built it from an empty folder, and I'm aiming it at Steam.**
Jade Dragons vs Crimson Tigers, 2049. Three.js plus plain ES modules, **no build step**, no engine.

| | |
|---|---|
| 🎮 **Modes** | 10-mission story **campaign** with cutscenes · Domination, Hardpoint, S&D, CTF, Gun Game, Infected, Gunfight 2v2 · **Ranked** seasons · **Dynasty Defense** co-op horde with Titan bosses · **Ground War**: 20v20, five flags, vehicles |
| 🌐 **Online** | My own **authoritative Node match server** (5k lines): binary delta-snapshot netcode, client prediction and lag compensation, host migration, server browser, parties, spectator/caster mode, bot backfill and a packaged dedicated server |
| 🗺️ **World** | **17 maps** (Forbidden Court, Neon Kowloon, Great Wall Pass, Yangtze Front…) built for boost movement and verticality |
| 🔫 **Arsenal** | 28 guns · gunsmith with attachments and camos · classes · perks · killstreaks (Sky Lantern, Dragon's Breath, guided Dragon Missile) · 40 levels plus prestige |
| 🤖 **AI** | Squad-level bot director (attack/defend orders) · per-bot LOD (frustum + distance tiers) so 40 fighters keep the frame rate up |
| ✨ **Rendering** | Custom post pipeline (GTAO, bloom, SMAA, color grade) · procedural PBR textures · HDRI lighting · per-map weather (thunderstorms, blossom storms) |
| 🕹️ **Platforms** | Full gamepad support with aim assist and rumble · Steamworks, Workshop and Steam Input wired up · Steam Deck mode · touch controls for phones |
| 🧪 **Quality** | Headless bots that play matches and screenshot them · map validators · perf harnesses that measure 40-combatant frame times · a tracked bug list and release checklist |
| 📜 **Licensing** | Every third-party asset is logged with its source and license (CC0 / CC BY with in-game credits); procedural or first-party art where no clean source existed |
| 📈 **Scale** | **1,190+ commits · 250+ modules · 75k+ lines of JS** · 30+ design docs (art bible, balance, campaign scripts, store page) |

<p align="center">
  <img src="assets/dragon-front-kowloon.jpg" width="49%" alt="Neon Kowloon in a thunderstorm">
  <img src="assets/dragon-front-groundwar.jpg" width="49%" alt="Ground War on Yangtze Front">
  <img src="assets/dragon-front-menu.jpg" width="98.5%" alt="Main menu">
</p>

<sub>🔒 Source is private while it heads to Steam. I'm happy to demo it live or walk through the architecture.</sub>

---

## 🚀 Products

<table>
<tr>
<td width="62%" valign="top">

### 📊 [The Edge Board](https://nfl-edge-kappa.vercel.app) · `live`
A live NFL + college football analytics app, installable on your phone.
- **~30 measured signals**: weather, role-weighted injuries, line movement, rest, live in-game pace vs the live line
- **Weighted stacking**: agreeing signals are scored by evidence weight, and conflicting ones are shown, never hidden
- **Its own model**: Massey-style power ratings blended with a matchup model and adjusted for injuries
- **Honest track record**: every call is frozen the moment it appears and graded at the final, with closing-line value and a per-signal self-audit. Losses are published right next to wins.
- When nothing clears the bar, it says **"nothing worth betting"** instead of ranking the least-bad option

<sub>JS · Vercel serverless + cron grading · PWA with web push alerts</sub>

</td>
<td width="38%" valign="top">
<img src="assets/edge-picks.jpg" width="100%" alt="Edge Picks: graded track record">
</td>
</tr>
</table>

<p align="center">
  <img src="assets/edge-board-desk.jpg" width="66%" alt="The Edge Board: weekly board">
  <img src="assets/edge-power.jpg" width="32%" alt="Power Poll: model ratings">
</p>

### 🏈 [Draft War Room](https://github.com/JROtto5/draft-war-room)
A superflex fantasy cockpit that grew from a draft tool into a whole-season command center: Monte Carlo survival odds and title odds, a start/sit consensus across Sleeper, ESPN and CBS, a waiver radar, trade sims, and live injury feeds. **MIT licensed, 100+ commits, zero-build static PWA** that auto-deploys to Vercel.

<p align="center"><img src="assets/draft-war-room.jpg" width="100%" alt="Draft War Room season command center"></p>

| Project | What it is | Stack |
|---|---|---|
| ✂️ **Clipper** 🔒 | Paste a video link and get back vertical, captioned highlight Shorts. Claude picks the moments from the transcript, FFmpeg renders them, and the YouTube API uploads them as drafts. Cached, idempotent re-runs, and it runs on an autopilot timer. | Python · Claude API · FFmpeg · YouTube Data API |
| 🏢 **Day job** | Production compliance and remediation tooling: customer-facing dashboards, reporting pipelines, serverless AWS services and Postgres data packages. | Python · TypeScript · AWS SAM · Postgres |

---

## 🐧 Linux

### [SITH OS: *The Dark Side of Linux*](https://github.com/JROtto5/sith-os)
My own **Arch Linux distribution**, built with `archiso`: an installable live ISO with a Calamares graphical installer, **~190 curated packages, 178 config files and 10 custom commands**.
Themed end to end: GRUB → Plymouth → SDDM → KDE Plasma → Kitty, plus four named virtual desktops (KORRIBAN, MALACHOR, DROMUND, EXEGOL).

I daily-drive Arch on a 4-monitor RTX 5070 Ti rig and write my own **Plasma 6 widgets** (a custom system-stats plasmoid that replaced conky) and **KWin effect patches**. I also debug the kernel/driver/compositor stack when it breaks, and on bleeding-edge NVIDIA it breaks.

---

## 🎨 Games & Creative Code

<table>
<tr>
<td width="50%" valign="top">

### 🎬 LUMEN: a short film written in Python
A **4-minute animated short** where every frame comes from code (pycairo + numpy, 1080p/24fps). It has a timeline-driven scene system, generated dialogue, a mixed score and SFX, and subtitles. A tiny robot lighthouse keeper gives up its own heart to light the lamp.

<img src="assets/lumen.gif" width="100%" alt="LUMEN lighthouse in a storm">
<img src="assets/lumen-still.jpg" width="100%" alt="LUMEN still">

</td>
<td width="50%" valign="top">

### 🎰 [NEON SPIN](https://github.com/JROtto5/neon-spin) · [**▶ play it**](https://jrotto5.github.io/neon-spin/)
A neon idle slot-machine empire: 3→5 animated reels, a luck system, 13 generators, 30+ upgrades and 30+ achievements. **One self-contained HTML file, zero dependencies.**

<a href="https://jrotto5.github.io/neon-spin/"><img src="assets/neon-spin.jpg" width="100%" alt="NEON SPIN"></a>

### ⛏️ Minecraft modding
**[Cyclea](https://github.com/JROtto5/cyclea)** is a Fabric 26.2 client mod, and its repo also documents how to build Fabric mods **without Loom**. **[OttoPack](https://github.com/JROtto5/ottopack)** is the exploration and performance modpack built around it.

</td>
</tr>
</table>

---

## ⚡ How I Work

```yaml
ships:   fast. Plain modules, no build step unless one earns its place
tests:   bots that play my game and screenshot it so I don't ship blind
data:    if a number is on screen, you can see the sample behind it
honesty: my betting model publishes its losses too
ai:      I run parallel coding agents as a daily workflow, then review everything they ship
linux:   when the driver breaks, I'm the one reading dmesg
```

<p align="center">
  <img src="https://img.shields.io/badge/Open_to-game_dev_·_product_engineering_·_Linux-ff2e63?style=for-the-badge">
</p>

<!-- CONTACT: add your LinkedIn / email / portfolio link here -->
