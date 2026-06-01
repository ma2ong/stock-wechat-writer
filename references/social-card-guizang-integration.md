# Guizang 图文生成接入说明

本项目已经接入 Guizang social card 的工作流思想：固定平台尺寸、Swiss 风格、一个页面一个观点、先提炼文章再生成图片。

当前仓库已经按用户要求复制 `guizang-social-card-skill` 的模板代码到：

```text
third_party/guizang-social-card-skill/
```

该目录保留上游 `LICENSE`、`README.md`、`SKILL.md` 和模板/参考文件。上游许可证为 AGPL-3.0，修改、分发或作为网络服务提供时必须遵守对应开源义务。

日常生成仍优先调用本仓库内置脚本：

```bash
python scripts/generate_social_cards.py \
  --article output/stock_review_YYYYMMDD.md \
  --date YYYYMMDD \
  --mode all
```

输出目录：

```text
output/social-cards-YYYYMMDD/
├── index.html
└── output/
    ├── xhs-01-cover.png
    ├── xhs-02-market-contrast.png
    ├── xhs-03-sell-pressure.png
    ├── xhs-04-money-shift.png
    ├── xhs-05-trade-plan.png
    ├── wechat-cover-21x9-YYYYMMDD.png
    ├── wechat-cover-1x1-YYYYMMDD.png
    └── wechat-cover-pair-preview-YYYYMMDD.png
```

脚本会额外生成：

```text
output/social-cards-YYYYMMDD/guizang-index.html
```

这份 HTML 使用复制进来的 Guizang Swiss seed template，可用于后续 Playwright 截图或人工微调。

## 使用场景

- 用户要求“生成小红书卡片”“生成图文组图”“生成公众号封面”。
- 复盘正文已经通过 `pre_publish_check.py`。
- 不需要 VoxFlow CLI、`voxflow login` 或外部 card skill。

## 写作到图文的链路

```text
A股复盘正文
→ pre_publish_check.py 事实与风险检查
→ generate_social_cards.py 生成小红书/公众号图文
→ 用户确认后再推公众号草稿箱或分发平台
```

## 视觉规则

- 小红书：`1080 x 1440`，5 张起步，必要时扩到 7 张。
- 公众号主封面：`2100 x 900`。
- 公众号方封面：`1080 x 1080`。
- 默认 Swiss 风格，金融复盘不使用装饰性卡通或复杂插画。
- 每张图只讲一个观点，正文里的解释不要硬塞进图片。

## 颜色规则

| 盘面类型 | Accent |
| --- | --- |
| 普通震荡 / 中性 | IKB Blue |
| 下跌 / 退潮 / 风险警示 | Safety Orange |
| 强修复 / 情绪高涨 | Lemon Yellow |

脚本默认 `--accent auto`，会根据文章里的“跌、退潮、破位、风险、撤”等词自动选择风险色。

## 内容压缩规则

- 标题只放当天最反常的矛盾或关键数字。
- 小红书每页最多 3-4 条短句。
- 不把公众号正文拆成逐段截图。
- 不写“前排/后排/核心/跟风”黑话，直接写动作：减、等、别追、低开拉回再看。

## 许可证边界

模板代码已经复制进 `third_party/`，因此必须保留 AGPL-3.0 许可证和上游署名。不要把该目录里的模板改成闭源版本，也不要移除许可证说明。
