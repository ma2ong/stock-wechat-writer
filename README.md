# stock-wechat-writer

一键生成 A 股行情分析微信公众号文章的 Claude Code Skill。

## 功能

- 自动采集 A 股主要指数、板块涨跌、成交额
- 获取 DeepEar Lite 实时金融信号
- 抓取财联社/华尔街见闻/雪球实时新闻
- 按 vibe-writer-pro 写作规范输出公众号文章

## 触发

在 Claude Code 中直接说：

```
写今天的A股复盘
生成今日行情分析文章
写一篇A股收盘公众号文章
今日A股晚报
```

## 前置要求

- Python 环境：`pip install akshare yfinance requests loguru`
- 已安装 alphaear-deepear-lite skill（可选，降级可用）
- 已安装 alphaear-news skill（可选，降级可用）

## 安装

```bash
# 将整个目录复制到 Claude Code 全局 skills 目录
cp -r stock-wechat-writer ~/.claude/skills/
```

## 文件结构

```
stock-wechat-writer/
  SKILL.md                       # 主 skill 定义
  README.md                      # 本文档
  references/
    data_sources.md              # A股数据源详细说明
    writing_template.md          # 公众号文章模板和示例
```

## 数据来源

| 数据 | 来源 |
|------|------|
| 指数行情 | akshare (东方财富) |
| 板块涨跌 | akshare |
| 个股数据 | akshare / yfinance |
| 金融信号 | DeepEar Lite |
| 实时新闻 | 财联社 / 华尔街见闻 / 雪球 |

## 注意

- 仅限 Claude Code CLI 使用（需要 Python + 网络访问）
- 所有分析仅供参考，不构成投资建议
- 数据来自第三方，可能有延迟或错误
