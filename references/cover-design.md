# 股票复盘封面设计手册

## 设计原则

封面不是文章摘要，是情绪触发器。读者在公众号列表里 0.5 秒决定要不要点开，封面的作用是让人一眼感受到"今天行情怎样了"——不靠数字，靠画面。

**核心思路：用人物或场景插画传达市场情绪，不放指数点位，不放成交额。**

读者看到一个捂脸崩溃的人，比看到"-2.3%"感受更直接。

---

## 一、封面生成方式（插画优先）

### 方式 A：AI 插画生成（主推）

用 `image-generator` skill 生成情绪插画，输出尺寸 `1792×1024`（16:9 横版）。

插画根据当日行情情绪选择对应提示词（见第二章），不要在图里放任何数字和文字——文字叠加在后续 HTML 步骤完成。

### 方式 B：插画背景 + 文字叠加 HTML（推荐完整流程）

1. 用 image-generator 生成插画 → 保存为 `output/stock_review_YYYYMMDD_illus.png`
2. 用 md2wechat-skill 或 Playwright 把插画上传到微信素材库 → 获取 `wechat_url`
3. 把插画 url 作为 `<img>` 背景嵌入封面 HTML，叠加标题文字
4. Playwright 截图 900×500 → `output/stock_review_YYYYMMDD_cover.png`

**如果只有插画没有文字叠加，也可以直接用插画作封面**，微信草稿箱支持纯图片作 thumb。

---

## 二、市场情绪 → 插画提示词映射表

根据当日核心判断（Step 3 的核心结论）选择对应情绪，再使用下方提示词生成。

### 大涨（指数 +1.5% 以上，涨停家数 100+ ）

**情绪：亢奋、爆发、欢呼**

```
prompt: A joyful Chinese investor character jumping with excitement, arms raised high, 
celebrating in front of a glowing green stock screen, flat illustration style, 
warm golden and green color palette, confetti falling, bright and energetic mood, 
simple clean background, 16:9 landscape
```

中文备选描述（image-generator 如果支持中文）：
```
一个兴奋欢呼的中国投资者角色，双臂高举，背景是绿色上涨的股票屏幕，
扁平插画风格，温暖金绿配色，彩纸飘落，明亮有活力，简洁背景，横版16:9
```

---

### 小涨（指数 +0.5% ~ +1.5%）

**情绪：愉快、轻松、满意**

```
prompt: A relaxed and pleased Chinese investor character sitting comfortably, 
giving a thumbs up, soft smile, green candlestick chart in background, 
flat illustration style, soft blue and green tones, calm and positive atmosphere, 
16:9 landscape
```

---

### 震荡盘整（指数 -0.5% ~ +0.5%，方向不明）

**情绪：迷茫、困惑、挠头**

```
prompt: A confused Chinese investor character scratching their head, 
surrounded by floating question marks, stock chart going sideways in background, 
flat illustration style, muted grey and blue tones, uncertain and puzzled mood, 
simple clean background, 16:9 landscape
```

---

### 小跌（指数 -0.5% ~ -1.5%）

**情绪：担忧、皱眉、不安**

```
prompt: A worried Chinese investor character frowning while staring at a phone screen 
showing red numbers, sitting hunched over a desk, flat illustration style, 
cool blue and grey color palette, anxious and tense atmosphere, 
simple background, 16:9 landscape
```

---

### 大跌（指数 -1.5% 以上，跌停家数多）

**情绪：崩溃、沮丧、捂脸**

```
prompt: A devastated Chinese investor character sitting slumped with hands covering face, 
dramatic red falling arrows in background, tears or sweat drops, 
flat illustration style, dark red and grey color palette, 
gloomy and sorrowful mood, simple background, 16:9 landscape
```

---

### 暴跌（指数 -3% 以上，熔断级别）

**情绪：惊吓、崩溃、绝望**

```
prompt: A shocked Chinese investor character with wide open eyes and mouth, 
falling dramatically from a cliff of red candlesticks, 
flat illustration style, intense dark red and black palette, 
dramatic and chaotic atmosphere, 16:9 landscape
```

---

### 主线切换（板块大轮动，资金换场）

**情绪：困惑 + 紧迫，来不及反应**

```
prompt: A Chinese investor character running in panic between two glowing screens, 
one showing a fading sector going down, another showing a new sector rising, 
flat illustration style, split warm and cool tones left-right, 
hectic and fast-paced mood, 16:9 landscape
```

---

### 科技/AI 主线强势

**情绪：热血、冲劲、科技感**

```
prompt: A determined Chinese investor character riding a rocket made of circuit boards 
and microchips upward, AI and tech symbols floating around, 
flat illustration style, electric blue and gold palette, 
energetic futuristic mood, 16:9 landscape
```

---

## 三、插画风格统一要求

所有封面插画必须满足：

| 要求 | 说明 |
|------|------|
| 风格 | flat illustration（扁平插画），不用写实/照片风 |
| 人物 | 中国投资者角色，面部表情夸张清晰，小图也能看懂 |
| 文字 | 插画本身不含任何文字、数字——文字在后续叠加 |
| 尺寸 | 生成时指定 1792×1024（image-generator 的 16:9 参数）|
| 配色 | 随情绪走：上涨=暖色/绿，下跌=冷色/红灰，震荡=中性灰蓝 |
| 背景 | 简洁，不要复杂纹理，确保标题文字叠加后清晰 |

---

## 四、文字叠加 HTML 模板（可选，插画做背景）

如果需要在插画上叠加标题，使用以下 HTML 结构：

```html
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { width: 900px; height: 500px; overflow: hidden; }

  .cover {
    width: 900px; height: 500px;
    position: relative;
    font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
  }

  /* 插画背景 */
  .cover-bg {
    position: absolute; inset: 0;
    width: 100%; height: 100%;
    object-fit: cover;
  }

  /* 半透明遮罩（确保文字可读）*/
  .cover-overlay {
    position: absolute; inset: 0;
    background: linear-gradient(
      to right,
      rgba(10,14,26,0.82) 0%,
      rgba(10,14,26,0.60) 50%,
      rgba(10,14,26,0.15) 100%
    );
  }

  /* 文字区（左侧 60%）*/
  .cover-text {
    position: absolute;
    left: 60px; top: 50%;
    transform: translateY(-50%);
    max-width: 520px;
  }

  .cover-date {
    font-size: 14px;
    color: rgba(255,255,255,0.45);
    letter-spacing: 3px;
    margin-bottom: 18px;
  }

  .cover-headline {
    font-size: 46px;
    font-weight: 800;
    color: #ffffff;
    line-height: 1.25;
    margin-bottom: 16px;
  }

  .cover-headline .red   { color: #ff4d4f; }
  .cover-headline .green { color: #52c41a; }
  .cover-headline .gold  { color: #ffd666; }

  .cover-subline {
    font-size: 18px;
    color: rgba(255,255,255,0.65);
    line-height: 1.6;
  }

  .cover-tag {
    position: absolute;
    bottom: 28px; right: 40px;
    font-size: 13px;
    color: rgba(255,255,255,0.3);
    letter-spacing: 1px;
  }
</style>
</head>
<body>
<div class="cover">
  <img class="cover-bg" src="[插画图片URL或本地路径]" alt="">
  <div class="cover-overlay"></div>
  <div class="cover-text">
    <div class="cover-date">2026年X月X日 · A股复盘</div>
    <div class="cover-headline">
      [标题第一行]<br>
      <span class="red">[强调词]</span>[标题第二行]
    </div>
    <div class="cover-subline">[副标题，一句核心判断]</div>
  </div>
  <div class="cover-tag">硅基时刻</div>
</div>
</body>
</html>
```

**遮罩方向规则：**
- 上涨日：渐变从左到右（文字在左，人物在右）
- 下跌日：可改为从右到左（人物沮丧在左，文字靠右）

---

## 五、纯插画封面（最简流程）

不需要文字叠加时，直接用 image-generator 生成的插画作为封面：

```
1. image-generator 生成插画 → 本地 PNG
2. 上传到微信素材库（push_stock_review_draft.py 自动处理）
3. 推送草稿箱时 --cover 指向该 PNG
```

适用场景：赶时间，或标题已经很短、插画信息量足够时。

---

## 六、Playwright 截图流程（文字叠加版）

```
1. image-generator 生成插画 → output/stock_review_YYYYMMDD_illus.png
2. 将插画路径填入 HTML 模板 <img src="...">
   （file:// 被拦时，先启动 python -m http.server 18508）
3. resize: width=900, height=500
4. navigate: http://localhost:18508/stock_review_YYYYMMDD_cover.html
5. screenshot → output/stock_review_YYYYMMDD_cover.png
6. Read 工具验证：人物清晰、文字可读、遮罩不过重
```

---

## 七、正文配图（可选）

如果文章需要正文配图：

| 场景 | 方式 |
|------|------|
| 板块热度对比 | HTML 横向柱状图 → Playwright 截图 |
| 行情走势示意 | image-generator（氛围图，不要求精确数字）|
| 主线概念图 | image-generator（芯片/服务器/机器人等）|
| 截图说明数据 | 直接截 akshare 输出或行情软件 |

正文配图文件命名：`output/illus-stock-[描述]-YYYYMMDD.png`

每篇最多 2 张正文配图，优先封面，不强制堆图。
