# Baoyu 生图后端接入

`stock-wechat-writer` 的生图后端接入 Baoyu 系列脚本，用于生成：

- 公众号封面底图
- 文中情绪图 / 资金流向图

`baoyu-image-gen` 已迁移到 `baoyu-imagine`。当前接入策略是兼容两者：

1. 优先使用 `baoyu-imagine`
2. 找不到时回退到 `baoyu-image-gen`
3. 如果本机没有 API 配置，只生成 prompt 和 batch 文件，不阻塞发稿

## 命令

```bash
python scripts/generate_article_images.py \
  --article output/stock_review_YYYYMMDD.md \
  --date YYYYMMDD \
  --mode all
```

只生成 prompt，不实际调用 API：

```bash
python scripts/generate_article_images.py \
  --article output/stock_review_YYYYMMDD.md \
  --date YYYYMMDD \
  --mode all \
  --dry-run
```

指定提供商：

```bash
python scripts/generate_article_images.py \
  --article output/stock_review_YYYYMMDD.md \
  --date YYYYMMDD \
  --provider dashscope \
  --model qwen-image-2.0-pro
```

## 输出

```text
output/article-images-YYYYMMDD/
├── prompts/
│   ├── cover.md
│   └── inline-01.md
├── baoyu-batch.json
├── cover-16x9.png       # API 配置齐全时生成
└── inline-01.png        # API 配置齐全时生成
```

## 视觉规则

- 图片中禁止出现文字、数字、股票代码、水印。
- 图片只做情绪和场景表达，不做数据图表。
- 封面底图必须给标题叠加区留干净空间。
- 文中图只在文章确实需要情绪转换、资金流向解释或风险提示时生成。
- 复盘图文卡片仍走 `generate_social_cards.py`，不要把生图后端生成的插画硬塞进每张卡片。

## 与公众号封面关系

优先级：

1. Guizang/HTML 封面：稳定、文字精准，适合日常默认
2. Baoyu 生成封面底图：适合需要情绪插画时
3. 旧深色渐变封面：兜底

Baoyu 生成的 `cover-16x9.png` 可以作为 `cover-design.md` 里的插画背景，再叠加标题。
