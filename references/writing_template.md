# 公众号写作模板

这份文件不是让你机械套格式，而是给你一些可拆可换的写作模块。

重点不是"写全"，而是"写准"。

每天先判断盘面类型，再选结构。不要连续多天使用同一套标题、同一套章节顺序、同一种开头方式。

## 结构选择器

| 当天盘面 | 文章主结构 |
|---|---|
| 强趋势分歧 | 谁抗住 → 谁掉队 → 明天看承接 |
| 主线切换 | 旧主线失效 → 新主线证据 → 切换确认点 |
| 情绪退潮 | 亏钱效应 → 龙头/妖股状态 → 回避条件 |
| 指数护盘 | 指数假象 → 市场宽度 → 护盘方向是否可持续 |
| 消息兑现 | 消息预期 → 价格背离 → 资金提前定价 |
| 缩量震荡 | 没机会的原因 → 等什么信号 → 风险提示 |

## 标准收盘复盘模板

仅在盘面普通、没有更好结构时使用。不要默认套用。

```markdown
# [日期]A股复盘｜[一句话主判断]

[第一段直接给结论。]
[第二段给关键数字：指数、成交额、宽度。]

## 先说结论
[今天真正重要的一件事是什么，直接说出来。]

## 为什么今天会这样走
[讲驱动：消息、资金、海外映射、产业逻辑。]

## 真正的主线是什么
[不要只写涨幅榜，要解释为什么它才是主线。]

## 哪些方向只是陪跑，哪些方向偏弱
[区分真强和假强。]

## 明天看什么
[只保留2-4个最关键观察点。]

## 最后一句话
[用一句短结论收住全文。]

## 风险提示
以上内容仅为市场复盘与信息整理，不构成任何投资建议。
```

## 开头写法模板

### 数字开头

`节后第一天，A股直接放量到3.25万亿。`

### 反直觉开头

`今天指数看着还行，但真正在科技线上的人都知道——下午那段，龙头基本没有承接。`

### 判断开头

`表面看是普涨，实则是资金重新回到科技线。`

## 主线段落怎么写

推荐结构：

1. 先说谁最强
2. 再说为什么是它强
3. 最后说这意味着什么

主线分析必须同时包含资金、情绪、图形、横向和纵向比较。只写“今天涨了/跌了/有利好”不合格。

## 明日展望怎么写

不要写成"后市值得期待"。

找到明天最容易产生分歧的那一个点，说清楚看多和看空各自的依据。不套句式，根据今天实际的盘面写。

## 标题

标题从核心判断里来，不是套模板。把今天最值得说的那件事，改成让人想点开的表达。可以用关键数字、直接点明主线切换、或者放大今天最反常的地方。

## 发稿前自查

**L1 硬性规则：**
1. 无禁用词（见 `references/ai-antipatterns.md`）
2. 数字全部具体（无"大幅""显著""明显"）
3. 无"首先其次最后"结构，无"！！"，无"……"

**L2 节奏：**
4. 开头直接给判断，不是导语
5. 每段不超过4行

**L3 内容：**
6. 主线判断有成交量或龙头支撑（不只靠涨幅榜）
7. 数字都能找到来源
8. 明日观察点是具体的、可验证的
9. 推荐方向前，已经同时看过资金、情绪、图形、均线、龙头/妖股结构和横向纵向强弱
10. 文章结构符合当天盘面，没有机械套用前几天格式
11. 出现操作建议时，必须有触发条件、点位/结构锚、风险位和失效信号
12. 触发风险否决项时，只能写观察/回避/等修复，不能写低吸、试错、买入或加仓

**L4 活人感：**
13. 有自己的立场，不只描述发生了什么
14. 有一句话可以单独截图转发

---

## HTML 排版模板（公众号正文用）

### 设计系统说明

来源：参考 `xiaohu-wechat-format` 仓库的 `ocean-card` 主题 + `focus-blue` 主题融合。

**色彩系统**

| 用途 | 颜色值 |
|------|--------|
| 页面背景 | `#f0f4f8` |
| 卡片背景 | `#ffffff` |
| 主文字 | `#3a4150` |
| 强调蓝 | `#1a3a5c`（深）/ `#4a7c9b`（中） |
| 上涨绿 | `#22c55e` |
| 数据蓝 | `#3b82f6` |
| 警示黄 | `#f59e0b` |
| 紫色辅助 | `#8b5cf6` |
| 跌幅红 | `#dc2626` |

**关键排版规则**

1. 微信不稳定支持 `display:flex`，多列布局一律用 `<table>` 代替
2. 列表项用 `<table>` 实现圆形徽章 + 文字的并排
3. 所有 CSS 必须内联（`style="..."`），不用 `<style>` 标签
4. 卡片阴影：`0 4px 16px rgba(58,65,80,0.06)`
5. 正文字号 15-16px，行高 1.75-1.85，letter-spacing 0.3-0.5px

---

### 完整 HTML 模板

```html
<!-- 微信公众号正文 · 股票复盘标准模板 -->
<div style="max-width:677px;margin:0 auto;padding:0 0 40px;background:#f0f4f8;font-family:'PingFang SC','Helvetica Neue',Arial,sans-serif;">

  <!-- ══ 标题卡片（深蓝渐变）══ -->
  <div style="background:linear-gradient(160deg,#1a3a5c 0%,#1e4976 50%,#1a3a5c 100%);padding:36px 28px 32px;margin-bottom:0;">
    <p style="font-size:11px;color:rgba(255,255,255,0.4);letter-spacing:3px;margin:0 0 14px;text-transform:uppercase;">A股复盘 · YYYY-MM-DD</p>
    <h1 style="font-size:26px;font-weight:800;color:#ffffff;line-height:1.45;margin:0 0 16px;letter-spacing:0.5px;">[标题第一行]<br>[标题第二行（可选）]</h1>
    <p style="font-size:14px;color:rgba(255,255,255,0.6);margin:0;line-height:1.7;border-top:1px solid rgba(255,255,255,0.12);padding-top:14px;">[副标题：一句核心判断]</p>
  </div>

  <!-- ══ 数据看板（4格，用 table 布局）══ -->
  <div style="background:#ffffff;margin:0 0 20px;padding:20px 20px 4px;box-shadow:0 4px 16px rgba(58,65,80,0.08);">
    <table style="width:100%;border-collapse:collapse;">
      <tr>
        <td style="width:25%;padding:0 6px 16px 0;vertical-align:top;">
          <div style="background:#f0f9f0;border-radius:10px;padding:12px 14px;border-top:3px solid #22c55e;">
            <p style="font-size:10px;color:#94a3b8;letter-spacing:1px;margin:0 0 6px;">[标签1]</p>
            <p style="font-size:20px;font-weight:700;color:#22c55e;margin:0;line-height:1;">[数值1]</p>
          </div>
        </td>
        <td style="width:25%;padding:0 6px 16px;vertical-align:top;">
          <div style="background:#eff6ff;border-radius:10px;padding:12px 14px;border-top:3px solid #3b82f6;">
            <p style="font-size:10px;color:#94a3b8;letter-spacing:1px;margin:0 0 6px;">[标签2]</p>
            <p style="font-size:20px;font-weight:700;color:#3b82f6;margin:0;line-height:1;">[数值2]</p>
          </div>
        </td>
        <td style="width:25%;padding:0 6px 16px;vertical-align:top;">
          <div style="background:#fffbeb;border-radius:10px;padding:12px 14px;border-top:3px solid #f59e0b;">
            <p style="font-size:10px;color:#94a3b8;letter-spacing:1px;margin:0 0 6px;">[标签3]</p>
            <p style="font-size:20px;font-weight:700;color:#f59e0b;margin:0;line-height:1;">[数值3]</p>
          </div>
        </td>
        <td style="width:25%;padding:0 0 16px 6px;vertical-align:top;">
          <div style="background:#faf5ff;border-radius:10px;padding:12px 14px;border-top:3px solid #8b5cf6;">
            <p style="font-size:10px;color:#94a3b8;letter-spacing:1px;margin:0 0 6px;">[标签4]</p>
            <p style="font-size:20px;font-weight:700;color:#8b5cf6;margin:0;line-height:1;">[数值4]</p>
          </div>
        </td>
      </tr>
    </table>
  </div>

  <!-- ══ 导语卡片（开篇判断）══ -->
  <div style="background:#ffffff;margin:0 0 20px;padding:28px 24px;box-shadow:0 4px 16px rgba(58,65,80,0.06);">
    <p style="font-size:16px;color:#3a4150;line-height:1.85;margin:0 0 16px;letter-spacing:0.3px;">[第一段：核心判断，反直觉角度]</p>
    <p style="font-size:16px;color:#3a4150;line-height:1.85;margin:0;letter-spacing:0.3px;">[第二段：补充说明或数字支撑]</p>
  </div>

  <!-- ══ Section 通用模块（复制后修改序号和标题）══ -->
  <div style="background:#ffffff;margin:0 0 20px;padding:28px 24px;box-shadow:0 4px 16px rgba(58,65,80,0.06);">

    <!-- Section 标题 -->
    <div style="margin:0 0 20px;">
      <p style="font-size:10px;color:#4a7c9b;letter-spacing:3px;font-weight:600;margin:0 0 6px;text-transform:uppercase;">Section 01</p>
      <h2 style="font-size:21px;font-weight:700;color:#1a3a5c;margin:0 0 8px;line-height:1.3;">[章节标题]</h2>
      <div style="width:40px;height:3px;background:#4a7c9b;border-radius:2px;"></div>
    </div>

    <!-- 正文段落 -->
    <p style="font-size:16px;color:#3a4150;line-height:1.85;margin:0 0 18px;letter-spacing:0.3px;">[正文段落]</p>

    <!-- 数据列表（带圆点） -->
    <div style="background:#f7fafd;border-radius:10px;padding:4px 16px;margin:0 0 20px;border:1px solid rgba(74,124,155,0.12);">
      <div style="padding:12px 0;border-bottom:1px solid rgba(74,124,155,0.08);">
        <span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#22c55e;margin-right:10px;vertical-align:middle;"></span>
        <span style="font-size:15px;color:#374151;vertical-align:middle;">[列表项1]</span>
      </div>
      <div style="padding:12px 0;border-bottom:1px solid rgba(74,124,155,0.08);">
        <span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#3b82f6;margin-right:10px;vertical-align:middle;"></span>
        <span style="font-size:15px;color:#374151;vertical-align:middle;">[列表项2]</span>
      </div>
      <div style="padding:12px 0;">
        <span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#f59e0b;margin-right:10px;vertical-align:middle;"></span>
        <span style="font-size:15px;color:#374151;vertical-align:middle;">[列表项3]</span>
      </div>
    </div>

    <!-- 引用/高亮块（蓝色左边框）-->
    <div style="background:#eff6ff;border-left:4px solid #3b82f6;border-radius:0 10px 10px 0;padding:16px 18px;margin:0;">
      <p style="font-size:14px;color:#1e40af;line-height:1.75;margin:0;font-style:italic;">[关键引用或核心数据说明]</p>
    </div>

  </div>

  <!-- ══ 观察点卡片（用于"早盘看什么"/"明天看什么"）══ -->
  <div style="background:#ffffff;margin:0 0 20px;padding:28px 24px;box-shadow:0 4px 16px rgba(58,65,80,0.06);">

    <div style="margin:0 0 20px;">
      <p style="font-size:10px;color:#4a7c9b;letter-spacing:3px;font-weight:600;margin:0 0 6px;text-transform:uppercase;">Section 02</p>
      <h2 style="font-size:21px;font-weight:700;color:#1a3a5c;margin:0 0 8px;line-height:1.3;">[章节标题]</h2>
      <div style="width:40px;height:3px;background:#4a7c9b;border-radius:2px;"></div>
    </div>

    <!-- 观察点1（深蓝）-->
    <div style="margin:0 0 16px;border-radius:10px;overflow:hidden;border:1px solid rgba(74,124,155,0.12);">
      <div style="background:#1a3a5c;padding:10px 18px;">
        <p style="font-size:11px;color:rgba(255,255,255,0.5);letter-spacing:2px;margin:0 0 2px;">观察点 01</p>
        <p style="font-size:15px;font-weight:700;color:#ffffff;margin:0;">[观察点标题]</p>
      </div>
      <div style="padding:16px 18px;background:#f9fbfd;">
        <p style="font-size:15px;color:#374151;line-height:1.8;margin:0;">[观察点内容]</p>
      </div>
    </div>

    <!-- 观察点2（紫色）-->
    <div style="margin:0 0 16px;border-radius:10px;overflow:hidden;border:1px solid rgba(139,92,246,0.15);">
      <div style="background:#5b21b6;padding:10px 18px;">
        <p style="font-size:11px;color:rgba(255,255,255,0.5);letter-spacing:2px;margin:0 0 2px;">观察点 02</p>
        <p style="font-size:15px;font-weight:700;color:#ffffff;margin:0;">[观察点标题]</p>
      </div>
      <div style="padding:16px 18px;background:#fdf9ff;">
        <p style="font-size:15px;color:#374151;line-height:1.8;margin:0;">[观察点内容]</p>
      </div>
    </div>

    <!-- 观察点3（灰色，用于"不担心"方向）-->
    <div style="border-radius:10px;overflow:hidden;border:1px solid rgba(148,163,184,0.2);">
      <div style="background:#64748b;padding:10px 18px;">
        <p style="font-size:11px;color:rgba(255,255,255,0.5);letter-spacing:2px;margin:0 0 2px;">暂不担心</p>
        <p style="font-size:15px;font-weight:700;color:#ffffff;margin:0;">[方向标题]</p>
      </div>
      <div style="padding:16px 18px;background:#f8fafc;">
        <p style="font-size:15px;color:#374151;line-height:1.8;margin:0;">[说明内容]</p>
      </div>
    </div>

  </div>

  <!-- ══ 编号判断列表（可验证观察点）══ -->
  <div style="background:#ffffff;margin:0 0 20px;padding:28px 24px;box-shadow:0 4px 16px rgba(58,65,80,0.06);">

    <div style="margin:0 0 20px;">
      <p style="font-size:10px;color:#4a7c9b;letter-spacing:3px;font-weight:600;margin:0 0 6px;text-transform:uppercase;">Section 03</p>
      <h2 style="font-size:21px;font-weight:700;color:#1a3a5c;margin:0 0 8px;line-height:1.3;">明天看什么（可验证的判断）</h2>
      <div style="width:40px;height:3px;background:#4a7c9b;border-radius:2px;"></div>
    </div>

    <!-- 用 table 实现编号徽章 + 文字并排（避免flex）-->
    <div style="padding:14px 0;border-bottom:1px solid #f0f4f8;">
      <table style="width:100%;border-collapse:collapse;">
        <tr>
          <td style="width:36px;vertical-align:top;padding-right:14px;">
            <div style="width:32px;height:32px;border-radius:50%;background:#1a3a5c;text-align:center;line-height:32px;font-size:14px;font-weight:700;color:#ffffff;">1</div>
          </td>
          <td style="vertical-align:top;">
            <p style="font-size:15px;color:#374151;line-height:1.8;margin:0;">[判断1：若……则……]</p>
          </td>
        </tr>
      </table>
    </div>

    <div style="padding:14px 0;border-bottom:1px solid #f0f4f8;">
      <table style="width:100%;border-collapse:collapse;">
        <tr>
          <td style="width:36px;vertical-align:top;padding-right:14px;">
            <div style="width:32px;height:32px;border-radius:50%;background:#5b21b6;text-align:center;line-height:32px;font-size:14px;font-weight:700;color:#ffffff;">2</div>
          </td>
          <td style="vertical-align:top;">
            <p style="font-size:15px;color:#374151;line-height:1.8;margin:0;">[判断2：若……则……]</p>
          </td>
        </tr>
      </table>
    </div>

    <div style="padding:14px 0;">
      <table style="width:100%;border-collapse:collapse;">
        <tr>
          <td style="width:36px;vertical-align:top;padding-right:14px;">
            <div style="width:32px;height:32px;border-radius:50%;background:#f59e0b;text-align:center;line-height:32px;font-size:14px;font-weight:700;color:#ffffff;">3</div>
          </td>
          <td style="vertical-align:top;">
            <p style="font-size:15px;color:#374151;line-height:1.8;margin:0;">[判断3：若……则……]</p>
          </td>
        </tr>
      </table>
    </div>

  </div>

  <!-- ══ 风险提示 ══ -->
  <div style="background:#ffffff;margin:0 0 20px;padding:16px 24px;box-shadow:0 4px 16px rgba(58,65,80,0.06);">
    <p style="font-size:13px;color:#94a3b8;line-height:1.7;margin:0;">⚠️ <strong style="color:#94a3b8;">风险提示：</strong>以上内容均为盘面分析，不构成任何投资建议。</p>
  </div>

  <!-- ══ 互动引导（结尾，深蓝底）══ -->
  <div style="background:linear-gradient(160deg,#1a3a5c 0%,#1e4976 100%);padding:28px 24px;text-align:center;">
    <p style="font-size:18px;font-weight:600;color:#ffffff;margin:0 0 10px;line-height:1.5;">[互动问题（开放性）]</p>
    <p style="font-size:14px;color:rgba(255,255,255,0.6);margin:0;line-height:1.7;">[引导留言的一句话]</p>
  </div>

</div>
```

---

### 各模块使用说明

| 模块 | 使用场景 | 颜色规则 |
|------|---------|---------|
| 标题卡片 | 每篇必用，标题+副标题 | 深蓝渐变，不换色 |
| 数据看板 | 有4项关键数字时用 | 绿=涨/正 蓝=量 黄=中性 紫=特殊 |
| Section | 每个段落用一个序号 | Section 01/02/03 顺序排列 |
| 数据列表 | 列出3-5项指标时用 | 圆点颜色与数据含义对应 |
| 引用块 | 重要数据或核心结论 | 蓝色左边框，淡蓝底 |
| 观察点卡片 | "今天看什么""明天看什么" | 主要=深蓝，次要=紫，弱势=灰 |
| 编号列表 | 可验证的具体判断 | 1=深蓝 2=紫 3=黄 |
| 风险提示 | 每篇必须有，放在互动前 | 灰色，不抢眼 |
| 互动引导 | 每篇必须有，放在最后 | 深蓝底，和标题呼应 |

### 禁止事项

- **不用 `display:flex`**：微信渲染引擎对 flex 支持不稳定，多列布局全部用 `<table>`
- **不用 `<style>` 标签**：微信会过滤，所有样式必须写在 `style=""` 属性里
- **不用 `position:absolute/fixed`**：会破坏微信文章流式布局
- **数字卡片文字过长时缩小字号**：长数字（如"3.14万亿"）用 `font-size:18px`，避免溢出
