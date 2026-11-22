# STATUS — news-image-20261122

## Entry (built, NOT submitted)
- Competition: news-image-20261122 — "Sum up 22 November's world news in one image", $100, top 50 paid ($20/$12/$6/$2 x7/$1.20 x40)
- Deadline: 24 Nov 2026 07:00 WIB
- Repo: https://github.com/wahyunp26-source/news-image-20261122
- Commit: b8eed873e3251b9ffe8a61870ddc26a6197814c2 (branch master, pushed)
- Repo created: 2026-11-22T02:36:39Z (after opening 2026-11-22T00:00:00Z)
- Repo public: yes. About set: description + homepage https://make.fun/c/news-image-20261122 + topic `makefun`
- owner.json: {"wallet":"wQUy3YoX5DoUSaAsXycrZT21NTih6BRwE6N4ossmy9S"} (verified in HEAD)
- LICENSE: MIT, SPDX-License-Identifier first line
- README badges: new format (badge/news-image-20261122.svg, /rank.svg, /reward.svg)

## Rendered image
- entry.png: 1024 x 1024, 41,287 bytes (limit 1 MiB)
- sha256: 20be31bb63c83cd9617880471d1ba2fc3de1ad09b88a4ec8a96a6efc78e6bf49
- Program: main.py, pure Python stdlib, no network, no randomness
- Determinism: two runs in clean venv produce identical sha256 (verified)
- Grader-style run: exit 0

## Kit check (local, no transcripts — parent bundles at submit)
- Kit: ~/workspace/makefun/news-image-20261122-kit-work/news-image-20261122-kit/ (fresh 22 Nov 09:30)
- check --worktree: 4 pass (competition_open, snapshot, license_osi, entrypoint), 1 fail (transcripts_present — expected, no bundle given), rest skipped / at-submission
- Repo-side items verified directly on GitHub: public, owner.json in HEAD, commit pushed, created after open

## Leaderboard bar observed (curl, 22 Nov ~09:30 WIB)
- Field: 2,698 entries
- Rank 1: 0.987907 (klencho, 12W-0L, 249,654 bytes)
- Rank 7 bar: 0.985964
- Rank 50 bar: 0.982336
- Our 21 Nov v2 scored 0.984508 (rank 127/4,887) — that level would sit around rank 60-70 in this field

## Design
- "THE SUNDAY GLOBE" newspaper front page: masthead + 8 illustrated panels + 24 briefs = 32 stories, 6 regions
- Panels: COP31 new draft at dawn / Iran hits US bases in Bahrain / Peru quake M6.7 / Sparta II ablaze / Kryvyi Rih missile / Sinaloa kingpin seized / Nepal PM in Delhi / Basra plant fire
- All stories verified against live web sources 22 Nov (Reuters/AP via search): COP31 revised text tabled early 22 Nov, no deal adopted; Iran struck two US sites in Bahrain; Peru 152 homes uninhabitable; Sparta II crew of 16 evacuated; Kryvyi Rih 2 killed, 60 wounded in 400-drone barrage; El Chapo Isidro captured, 11 killed; Balendra Shah arrives Delhi 22 Nov; Basra Hartha fire 4 dead, 35 hurt
- Style: rich flat-cartoon scenes (busy v1 style that scored best), hand-drawn 5x7 bitmap font, clean regular type
- Revision: v1 render inspected visually; genuine 2nd revision fixed briefs/footer collision, Kryvyi bursts (were sun-like), COP31 second flag (was Ukraine colours), helicopter shape

## Self-evaluation (honest)
- Can it reach top 7? Probably not. Top 7 needs ~0.986+, and our best-ever news-image score is 0.984508 (21 Nov v2, rank 127). The field's top entries pack 35-52 stories with denser drawn panels; this entry has 32 stories and a hand-made pixel font that is less polished than the best raster-style entries.
- Can it reach top 50 (0.982336 bar)? Plausibly yes — it is in the same band as our 21 Nov v2 (0.984508) with the same busy front-page pattern, real verified 22 Nov stories, and the strongest consensus stories (COP31, Bahrain, Peru, Sparta II) featured as large panels. Expectation: rank ~50-150, i.e. borderline paid place.
- Gap to top 7: illustration polish (hand-coded flat shapes vs the top entries' richer rendered art) and story density (32 vs 35-52). Closing that gap would need a fundamentally richer renderer, not a tweak.

## Session
- Builder session id: 1327e3d4-abbb-4f42-a151-c809466e3855
- Quota for this competition: 0/3 used. NOT submitted — awaiting user decision.
