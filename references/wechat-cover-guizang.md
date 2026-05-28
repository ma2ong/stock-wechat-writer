# WeChat Cover — Guizang Style

Replaces the hand-coded 900×500 dark gradient approach in `cover-design.md`.
Use this when you want a polished, on-brand cover pair instead of the custom HTML template.

## When to Use This vs. the Original Template

| Situation | Use |
|-----------|-----|
| Need a fast cover, no design system installed | Original dark-gradient HTML template (cover-design.md) |
| Want consistent Guizang branding, 21:9+1:1 pair | This guide (Guizang Swiss cover) |
| Daily recap — default | This guide |

## Style: Swiss International

Same rules as `xhs-card-recipes.md`. One accent per day type:
- Neutral day: IKB Blue
- Bearish/warning: Safety Orange
- Strong rally: Lemon Yellow

## 21:9 Main Cover (2100×900)

Use **S01 Accent Cover wide variant** or **custom text-only layout**.

Required elements:
- `.chrome-min`: "A股复盘" / "YYYY.MM.DD"
- `.t-cat` (left-aligned): market type phrase (≤6 chars)
- `.h-xl` (1 line, ≤14 chars): article title shortened to core object + action
- `.grow`
- `.hr-accent` (96px width)
- `.lead`: one-sentence strongest takeaway (≤20 chars preferred)
- `.t-meta` right-aligned: 成交额 XXXXX亿 · Vol.NN

Example layout:
```
A股复盘                          2026.05.27
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
情绪退潮 · 防守轮动

消息后第三天

———————

科技从叙事进入淘汰赛                成交额 32,599亿 · Vol.05
```

## 1:1 Square Cover (1080×1080)

Short title only. No images. Use `.h-statement` or `.h-xl` centered.

Short title derivation (apply in order, stop when ≤10 chars):
1. Take the 21:9 title
2. Remove modifiers, keep core object + action
3. If still >10 chars: take only the core object (noun)
4. If still >10 chars: truncate at last semantic unit

Examples:
- "消息后第三天，科技进入淘汰赛" → "消息后第三天" (6 chars) ✓
- "3万亿成交量突破，科技继续领涨" → "3万亿成交" (5 chars) ✓
- "防守轮动接棒" → "防守轮动" (4 chars) ✓

Required elements:
- `.h-statement` (centered): short title (≤10 chars, 1-2 lines)
- `.t-meta` (bottom, centered): "A股 · YYYY.MM.DD"

## Render Instructions

Build both covers in one `index.html` using the Swiss seed template.
Include a `.pair-preview` section so the 21:9 and 1:1 can be reviewed together.

File naming:
```
output/
├── wechat-cover-YYYYMMDD.html          # source
├── wechat-cover-21x9-YYYYMMDD.png      # 2100×900
├── wechat-cover-1x1-YYYYMMDD.png       # 1080×1080
└── wechat-cover-pair-preview.png       # optional, for visual QA
```

Render sequence (same as XHS):
1. HTTP server on 7788
2. Wait 2500ms for fonts
3. Screenshot `#wechat-21x9` → wechat-cover-21x9-YYYYMMDD.png
4. Screenshot `#wechat-1x1` → wechat-cover-1x1-YYYYMMDD.png

## Checklist

- [ ] 21:9 title is the article title (or a shortened version ≤14 chars)
- [ ] 1:1 short title ≤10 chars, readable as thumbnail
- [ ] Accent matches the day's market character
- [ ] No images on the 1:1 square cover
- [ ] Date is correct
- [ ] Both render at exact dimensions (2100×900 and 1080×1080)