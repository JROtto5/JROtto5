#!/usr/bin/env bash
# Daily profile grind: (1) refresh the stat cards from the GitHub API and push the profile repo,
# (2) run a headless Claude scout that prepares open-source contribution drafts LOCALLY.
# Nothing is ever posted, opened or pushed to other people's repos automatically: every PR, issue
# comment and promo post waits for johnr's explicit OK.
set -u
REPO="$HOME/dev/JROtto5"; OUT="$HOME/dev/oss-grind"; DAY=$(date +%F)
mkdir -p "$OUT/work"
exec >>"$OUT/grind.log" 2>&1
echo "== $DAY $(date +%T) start"

# 1. stats refresh (deterministic, own repo only)
cd "$REPO" && git pull -q --rebase \
  && python3 tools/gen_stats.py --live && python3 tools/gen_cards.py \
  && if ! git diff --quiet -- assets tools/stats_data.json; then
       git add assets/stats.svg assets/activity.svg assets/breakdown.svg assets/cards tools/stats_data.json
       git commit -qm "stats: daily refresh $DAY" && git push -q && echo "stats pushed"
     else echo "stats unchanged"; fi

# 2. OSS scout (local drafts only)
cd "$OUT"
timeout 2700 claude -p --permission-mode bypassPermissions --model claude-opus-5-5 "$(cat "$REPO/tools/oss-scout-prompt.md")

Today is $DAY. Write the brief to $OUT/$DAY.md and any prepared work under $OUT/work/." \
  </dev/null >"$OUT/$DAY.session.log" 2>&1
echo "scout exit $?"
notify-send -a "OSS grind" "Daily brief ready" "$OUT/$DAY.md" 2>/dev/null || true
echo "== done $(date +%T)"
