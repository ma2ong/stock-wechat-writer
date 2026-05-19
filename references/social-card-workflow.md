# 多平台精美卡片工作流

这份规则用于把已经写好的 A股复盘文章，二次生成小红书 / 小绿书 / 即刻 / X 可发布的静态卡片。

核心原则：卡片只消费已经核验过的复盘内容，不重新发明事实。

---

## 一、是否可以使用 card skill

可以。

`VoxFlowStudio/skills` 的 `card` skill 适合做设计规范、布局方法、字体资产和本地渲染参考，不必强依赖 VoxFlow 云端服务。

- 小红书 / 小绿书图文卡片
- 即刻长图 / 信息卡
- X / Twitter 方图或竖图
- 金句卡、观点卡、数据卡、复盘摘要卡
- 文章拆解成 3-7 张 carousel cards

它的技术路线是：

```text
复盘正文 / 事实卡片
→ 提炼卡片大纲
→ HTML/CSS 固定画布
→ Playwright 渲染
→ PNG 导出
```

这条路线适合财经复盘，因为文字、数字、股票代码都由 HTML 文本承载，比纯 AI 生图更可控。

默认采用**本地离线模式**：

```text
opencli 负责平台资料/发布辅助
card skill 负责设计规范和 render-cards.mjs
本地 HTML/CSS 负责卡片实现
Playwright 负责导出 PNG
```

不需要 `voxflow login`，也不需要把正文上传到 VoxFlow。

VoxFlow CLI 只作为可选增强：如果以后要用它的云端模板、账号额度或视频能力，再单独登录。

---

## 二、并入位置

不要把 card skill 放到写作前，也不要替代公众号正文。

正确位置：

```text
行情采集
→ 事实卡片
→ 复盘正文
→ pre_publish_check.py
→ 公众号 HTML / 草稿箱
→ 多平台卡片
```

只有 `pre_publish_check.py` 通过后，才能进入卡片生成。

原因：

- A股内容最怕事实错，卡片传播更快，错误扩散更严重。
- card skill 有研究扩展能力，但在股票复盘场景里默认关闭扩展研究，只从已核验文章和事实卡片抽取内容。
- 如果卡片需要补新数据，必须回到 `data_sources.md` 的采集流程重新核对。

---

## 三、平台比例

| 平台 | 默认比例 | 适用内容 |
|---|---|---|
| 小红书 / 小绿书 | `3:4` 或 `4:5` | 复盘拆解、主线解释、风险提醒 |
| 即刻 | `1:1` | 单观点、短链路分析、图文摘要 |
| X / Twitter | `1:1` 或 `16:9` | 单结论、数据卡、英文/双语摘要 |
| 视频封面 / Story | `9:16` | 竖版封面、短视频预告 |

默认推荐：

- 公众号复盘拆卡：`3:4`，5 张。
- 盘中快评：`1:1`，1-3 张。
- 重大事件专题：`3:4`，7 张。

---

## 四、A股复盘卡片结构

### 3 张短卡

```text
1. 今日结论：一句话讲清市场核心矛盾
2. 为什么：主线、资金、情绪、代表个股
3. 明天看什么：触发条件、风险位、回避条件
```

### 5 张标准卡

```text
1. 封面：今天市场真正的主线
2. 指数与情绪：指数、成交额、市场宽度
3. 主线拆解：谁是真主线，谁只是跟风
4. 个股样本：2-4 个已核验标的，只写事实和条件
5. 明天计划：观察点、失效条件、风险提示
```

### 7 张专题卡

```text
1. 封面：核心判断
2. 背景：消息/政策/业绩催化
3. 传导：产业链怎么映射到板块
4. 盘面：成交额、涨停梯队、龙头承接
5. 分歧：哪些方向不能追
6. 计划：什么条件能做，什么条件回避
7. 免责声明与互动问题
```

---

## 五、设计方向

财经卡片优先用这些 card skill 风格：

| 场景 | 推荐组合 |
|---|---|
| 日常复盘 | `quiet-report + data-poster + big-number` |
| 重大新闻 / 业绩爆点 | `newsroom-paper + newsroom-poster + stamp-label` |
| 强观点 / 反直觉判断 | `bold-editorial + swiss-poster + scale-contrast` |
| 深度专题 | `magazine-eink + image-led-magazine + annotation` |
| 小红书友好版本 | `social-notebook + field-notes + receipt-form` |

禁用：

- AI 紫蓝渐变、赛博发光、机器人手、虚假数据粒子。
- 只做标题大字，没有有用信息。
- 每张卡都用同一种三栏布局。
- 未核验数字、未核验股票代码、无来源龙虎榜。

---

## 六、执行命令：本地离线模式

安装 card skill：

```bash
npx -y skills add VoxFlowStudio/skills --skill card --yes --global
```

本地 HTML/Playwright 渲染使用 card skill 自带 helper：

```bash
node C:\Users\Administrator\.agents\skills\card\scripts\render-cards.mjs \
  --input cards\stock-review-YYYYMMDD \
  --output cards\stock-review-YYYYMMDD\exports \
  --ratio 3:4
```

如果 Playwright 缺失：

```bash
npm install -D playwright
npx playwright install chromium
```

如果只是用本地静态卡片，不执行：

```bash
voxflow status
voxflow login
```

## 七、opencli 在卡片流程里的位置

`opencli` 不是渲染器，不能替代 Playwright 导出 PNG。

它负责三类事：

1. 平台素材调研：看小红书 / 即刻 / X 同类内容怎么表达。
2. 平台文案适配：生成不同平台的标题、正文、话题标签。
3. 发布或保存草稿：在用户明确要求时，把 PNG 和正文发到平台。

常用命令：

```bash
# 小红书同类内容调研
opencli xiaohongshu search "A股复盘 科技主线" --limit 20 -f yaml

# 小红书发布图文笔记，建议先 draft=true
opencli xiaohongshu publish "正文内容" \
  --title "20字内标题" \
  --images "cards\stock-review-YYYYMMDD\exports\card-01.png,cards\stock-review-YYYYMMDD\exports\card-02.png" \
  --topics "A股复盘,股票,财经" \
  --draft true \
  -f yaml

# 即刻发布文字动态；如需带图，先确认当前 opencli jike 是否支持图片参数
opencli jike create "今日A股复盘：核心判断..." -f yaml

# X / Twitter 发图文
opencli twitter post "A股复盘：核心判断..." \
  --images "cards\stock-review-YYYYMMDD\exports\card-01.png" \
  -f yaml
```

发布类命令是写操作，必须在用户明确要求后执行；默认只生成本地 PNG。

---

## 八、发稿前检查

卡片生成前必须确认：

- [ ] 原始复盘正文已通过 `pre_publish_check.py`
- [ ] 所有股票代码和简称来自已核验正文
- [ ] 卡片里的数字没有新增，或新增数字已写入事实卡片来源
- [ ] 每张卡有一个清晰视觉锚点
- [ ] 至少一张卡包含具体信息，而不是全套金句
- [ ] 导出 PNG 后检查无文字溢出、遮挡、错别字

卡片生成失败时，不影响公众号正文发布；卡片是分发增强，不是主稿必需项。
