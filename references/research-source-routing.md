# Agent Reach 财经取材边界

Agent Reach 负责体检和选择新闻、网页、社区的当前可用后端，不替代行情与公告核验。

## 启动前体检

```bash
agent-reach doctor --json
```

旧版不支持 `--json` 时运行 `agent-reach doctor`。命令不存在或某渠道不可用时继续使用现有 `opencli`、MCP、浏览器和 Web 搜索，不阻断复盘。

## 三层信源

| 层级 | 内容 | 允许用途 |
|---|---|---|
| hard_fact | 交易所/巨潮公告、行情、成交额、代码名称、龙虎榜、官方原文 | 可以进入事实卡和正文 |
| verified_news | 财联社、证券时报、公司官方、可靠媒体并经交叉验证 | 可以解释催化，注明来源与时间 |
| lead_or_sentiment | 雪球、X、Reddit、小红书、微博、论坛讨论 | 只发现线索、争议和热度 |

`lead_or_sentiment` 不能单独证明上涨原因、资金身份、公司事实或交易结论。至少回到一条 `hard_fact` 或两条相互独立的 `verified_news` 后，才能升级。

## 路由规则

1. 读取 Agent Reach 体检中的 `active_backend`，再使用本机 `agent-reach` Skill 给出的当前命令。
2. 不复制固定后端顺序；平台接入方式变化时以体检结果为准。
3. 不自动读取浏览器 Cookie，不在文章、日志或仓库写入 Token、Cookie、代理地址。
4. 渠道失败时记录原因并降级，不把“未采到讨论”写成“市场没有讨论”。

## 事实卡字段

```json
{
  "claim": "待验证判断",
  "source_type": "hard_fact/verified_news/lead_or_sentiment",
  "source_url": "https://...",
  "active_backend": "实际后端",
  "retrieved_at": "ISO-8601",
  "verification_status": "verified/partial/lead_only"
}
```

任何 `lead_only` 内容只能留在调查笔记，不能进入定稿的确定性表述。

## 降级建议

- 雪球不可用：财联社、东方财富/同花顺公开页、证券时报和百度搜索。
- X/Reddit 不可用：公司官方、海外媒体、YouTube/RSS；不影响 A 股硬数据核验。
- 全网语义搜索不可用：官方网页、GitHub、Jina Reader、普通 Web 搜索。
- 小红书不可用：忽略消费端讨论或用微博/知乎补充，不能因此降低事实门槛。
