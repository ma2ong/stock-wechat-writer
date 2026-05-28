# Stock Recap XHS Card Recipes

Standard 7-page Xiaohongshu carousel for A股 daily recap.
Invoke from Step 8.5 of the stock-wechat-writer workflow.
Input data comes from the "事实卡片" produced in Step 2e of the same workflow.

## Style: Swiss International

Always use Swiss International mode. Never Editorial for stock recaps.
Content is quantified, decisive, data-driven — Swiss mood is correct.

## Color Rules

Pick one accent per card set based on the day's market character:

| Market character | Accent |
|------------------|--------|
| Neutral / mixed day (default) | IKB Blue (`ikb`) |
| Bearish, warning, strong selloff | Safety Orange (`safety-orange`) |
| Strong rally, sentiment surge | Lemon Yellow (`lemon-yellow`) |

Set accent on `<html data-accent="...">` and never mix two accents in one set.

## 7-Page Template

### P1 — Cover (S01 Accent Cover)

Hook = market type phrase (from the fact card's "核心结论" field).

Required elements:
- `.chrome-min`: "A股复盘 · Vol.NN" / "YYYY.MM.DD"
- `.t-cat`: market type phrase (e.g. "情绪退潮 · 防守轮动")
- `.h-statement` (2 lines max, 3-6 chars each): hook title distilled from the core judgment
- `.grow` spacer
- `.hr-accent`
- `.lead`: one sentence — the sharpest implication
- `.t-meta` row: 成交额 XXXXX亿 · 下跌 XXXX+家 · 涨停NN · 跌停NN

Title examples:
- "消息后\n第三天" (事件第N天验证)
- "政策落地\n谁受益" (政策催化)
- "3万亿\n成交量" (成交量异动)
- "科技退\n防守进" (主线切换)

### P2 — Index Data (custom ledger)

Show all 4 indexes with precise returns and points. No fabricated bars.

Required elements:
- `.chrome-min`: "四大指数" / "YYYY.MM.DD"
- `.t-cat`: "市场数据"
- `.h-xl`: "今日收盘"
- 4 flex rows (justify-content: space-between):
  - Left: index name (`.t-cat` 20px) + points (`.t-meta`)
  - Right: return % as large number (font-weight 200, font-size 88px, letter-spacing -.02em)
  - Color logic: largest decline → `var(--accent)`, near-flat → `var(--grey-3)`, others → `var(--ink)`
  - Dividers: `border-bottom: 1px solid var(--grey-2)` between rows
- Bottom: `border-top` + `.t-meta`: "全市场成交额 XXXXX亿 · 较上日±XX亿"

### P3 — Sector Strength (S02 Two Signals)

Two blocks: strong sectors (card-fill) and weak sectors (card-ink). Not a bar chart — no percentage fabrication.

Required elements:
- `.chrome-min`: "板块表现" / "行业分化"
- `.t-cat`: "今日行情"
- `.h-xl`: "强弱分化"
- `.stack.gap-6` with `flex:1`:
  - Top block `.card-fill`: "今日强势 · N板块" + overview line + numbered sector rows
  - Bottom block `.card-ink`: "今日弱势 · N板块" + overview line + numbered sector rows
- Each sector row: mono index ("01") + `.lead` sector name + optional `.t-meta` sub-note
- Maximum 5 sectors per block shown in detail; list remainder as one combined row

### P4 — Catalyst Check (custom)

Show only if there is an actual market-moving catalyst (华为/policy/Fed/earnings etc.).
Skip this page and use only 6 pages if the day has no major catalyst.

Required elements:
- `.chrome-min`: "催化剂复核" / "催化剂名称 · Day N"
- `.t-cat`: catalyst name
- `.h-xl`: short hook (5 chars max, 2 lines ok)
- `.body` (grey-3): one sentence summary — "消息点火后第N天，市场不再讲故事，只看资金行为。"
- `.hr-hairline`
- Two `.stack.gap-6` blocks with `flex:1`:
  - `.card-fill`: "资金仍在 · 存活核心" + `.h-md` stock names + `.body` chain description
  - `.card-ink`: "资金撤离 · 被淘汰分支" + `.h-md` sector names

### P5 — Main Line Matrix (S12 Matrix + hero-stat-bottom)

Maximum 4 cells (2×2 on xhs). One `.is-accent` cell for the best/most notable main line.

Required elements:
- `.chrome-min`: "主线筛选" / "NN条判断"
- `.t-cat`: "主线评级"
- `.h-xl`: "今日判断"
- `.matrix-fill` with 4 `.matrix-cell`s:
  - `.cell-nb`: "01"–"04"
  - `.cell-title`: main line name (2-4 chars)
  - Assessment text (22px, grey-3, line-height 1.45)
  - `.is-accent` on the best main line (if any genuinely stands out)
- `.hero-stat-bottom`:
  - Left: `.t-cat` + `.lead` (one conclusion sentence)
  - Right: `.num-mega` = number of main lines evaluated

### P6 — Tomorrow's Plan (custom pipeline)

3 scenario cards (card-fill). Always three scenarios: has tech/growth position, has defensive position, no position.

Required elements:
- `.chrome-min`: "明日操作" / "三种情况"
- `.t-cat`: "操作计划"
- `.h-xl`: "明日如何做"
- `.stack.gap-6` with `flex:1` (vertical column, cards stack top-to-bottom):
  - 3 `.card-fill` blocks, each with `flex:1`:
    - `.row.gap-6`: `.t-meta` (accent, "01"/"02"/"03") + `.h-md` (scenario name)
    - `.body` (grey-3): 3-4 sentences of specific, verifiable action

Scenario names adapt to the day:
- Scenario 01: "有科技仓" / "有主线仓" (growth/momentum position)
- Scenario 02: "有防守仓" / "有电力白酒" (defensive position type)
- Scenario 03: "空仓" (no position)

### P7 — Conclusion (custom ledger)

3 ledger items minimum. Each must have `.h-md` title + `.body` explanation (2-3 sentences). Add a 4th if the day had a particularly complex signal.

Required elements:
- `.chrome-min`: "今日复盘" / "YYYY.MM.DD"
- `.t-cat`: "复盘结论"
- `.h-xl`: "三个判断" (or "四个判断" if 4 items)
- `.stack` with `flex:1`:
  - 3-4 ledger items, each wrapped in `<div style="padding:var(--sp-7) 0; border-bottom:1px solid var(--grey-2)">` (last item omits border-bottom)
  - Each item: `.row.gap-6` with mono index (20px, accent) + `.stack.gap-4` with `.h-md` + `.body` (grey-3)
- Bottom strip: `border-top` + `.t-meta`: breadth stats summary (成交额 · 科创50变化 · 涨跌停数 · 下跌家数)

Judgment categories (pick the 3 most important):
- 市场情绪: overall sentiment direction
- 资金行为: money flow characterization
- 主线变化: main line status (strengthened / unchanged / weakened / reversed)
- 明日预判: tomorrow's likely scenario

## Output Naming

```
output/
└── xhs-cards-YYYYMMDD/
    ├── index.html
    └── output/
        ├── xhs-01-cover.png
        ├── xhs-02-index-data.png
        ├── xhs-03-sector-strength.png
        ├── xhs-04-catalyst-check.png    (omit if no catalyst)
        ├── xhs-05-mainline-matrix.png
        ├── xhs-06-tomorrow-plan.png
        └── xhs-07-conclusion.png
```

## Render Instructions

After building `index.html`, render via Playwright MCP:
1. Start HTTP server: `python -m http.server 7788` in the task folder (background)
2. Navigate: `http://localhost:7788/index.html`
3. Wait 2500ms for fonts to load
4. Screenshot each `#xhs-0N` element with `target` selector
5. Save to `output/xhs-cards-YYYYMMDD/output/xhs-0N-<name>.png`
6. Verify at least one image reads correctly via `Read` tool

## Minimum Checklist (before delivery)

- [ ] All index numbers are taken from the fact card, not approximated
- [ ] Strong/weak sector names match the fact card exactly
- [ ] No bar chart used (no fabricated percentages for sector performance)
- [ ] Catalyst page skipped if no major catalyst exists
- [ ] Main line matrix uses real judgments from Step 3, not generic labels
- [ ] Tomorrow's plan actions are specific and verifiable (not "值得期待")
- [ ] All 7 (or 6) images render at 1080×1440 px
