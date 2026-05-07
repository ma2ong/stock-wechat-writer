# 股票复盘封面设计手册

## 设计原则

封面不是文章摘要，是情绪触发器。读者在公众号列表里 0.5 秒决定要不要点开，封面的作用是制造"这和今天有关"的感受。

**三要素：** 核心判断（大字）+ 金融氛围（配色/元素）+ 日期标注

---

## 一、HTML 模板结构

### 基础 CSS 规范

```html
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }

  body {
    width: 900px;
    height: 500px;
    overflow: hidden;
    font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
  }

  .cover {
    width: 900px;
    height: 500px;
    position: relative;
    /* 深色渐变——必选，禁止浅色背景 */
    background: linear-gradient(135deg, #0a0e1a 0%, #1a2744 60%, #0d1f3c 100%);
    display: flex;
    flex-direction: column;
    justify-content: center;
    padding: 60px 80px;
  }

  /* 装饰线或图案层（可选，用 rgba 半透明叠加） */
  .cover::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: radial-gradient(ellipse at 80% 20%, rgba(255,80,80,0.08) 0%, transparent 60%);
  }

  .date {
    font-size: 18px;
    color: rgba(255,255,255,0.5);
    letter-spacing: 2px;
    margin-bottom: 24px;
  }

  .headline {
    font-size: 52px;
    font-weight: 800;
    color: #ffffff;
    line-height: 1.25;
    margin-bottom: 20px;
    /* 关键词用红色或金色强调 */
  }

  .headline .highlight-red { color: #ff4d4f; }
  .headline .highlight-gold { color: #ffd666; }

  .subline {
    font-size: 22px;
    color: rgba(255,255,255,0.65);
    line-height: 1.6;
    max-width: 620px;
  }

  .account-tag {
    position: absolute;
    bottom: 36px;
    right: 60px;
    font-size: 16px;
    color: rgba(255,255,255,0.35);
    letter-spacing: 1px;
  }
</style>
</head>
<body>
<div class="cover">
  <div class="date">2026年5月7日 · A股复盘</div>
  <div class="headline">
    3.25万亿爆了<br>
    主线<span class="highlight-red">彻底换了</span>
  </div>
  <div class="subline">科技接棒消费，这不是脉冲，是风格切换</div>
  <div class="account-tag">硅基时刻</div>
</div>
</body>
</html>
```

---

## 二、配色方案（三选一）

### 方案 A：深蓝 + 红色强调（A股收涨日）
```css
background: linear-gradient(135deg, #0a0e1a 0%, #1a2744 60%, #0d1f3c 100%);
highlight: #ff4d4f;  /* 红色强调词 */
```

### 方案 B：深黑 + 金色强调（量能放大/主线明确日）
```css
background: linear-gradient(135deg, #0d0d0d 0%, #1a1a2e 60%, #16213e 100%);
highlight: #ffd666;  /* 金色强调词 */
```

### 方案 C：深绿 + 白色（跌势中的判断型文章）
```css
background: linear-gradient(135deg, #001a0d 0%, #003320 60%, #001a0d 100%);
highlight: #52c41a;  /* 绿色强调词 */
```

**禁止：** 白色或浅灰背景、PPT渐变色（蓝→紫）、过于鲜艳的纯色底

---

## 三、标题文字规则

| 规则 | 说明 |
|------|------|
| 最多2行 | 超过16字换行，不压行 |
| 强调1-3个词 | 用 highlight 色，不全部加色 |
| 字号52px+ | 小于这个尺寸在手机列表缩略图里看不清 |
| 不放完整数据 | 指数点位不放封面，只放"3.25万亿"这类圆整数字 |
| 不用引号 | 标题不加书名号或引号 |

---

## 四、Playwright 截图流程

```
1. 生成 HTML 文件 → output/cover-stock-YYYYMMDD.html
2. resize: width=900, height=500
3. navigate: file:///完整路径/cover-stock-YYYYMMDD.html
4. screenshot → output/cover-stock-YYYYMMDD.png
5. Read 工具查看图片，确认文字不截断、背景正确
```

**关键：每次截图前必须 resize，否则尺寸不对。**

---

## 五、快速生成模板（复制修改）

只需替换3个变量：`DATE`、`HEADLINE`（分两行）、`SUBLINE`

```
DATE    → 具体日期（如：2026年5月7日）
HEADLINE → 核心判断，最多16字，拆成2行
SUBLINE → 一句补充说明，最多25字
```

---

## 六、正文配图（可选）

如果文章需要正文配图（不是所有文章都需要）：

| 场景 | 方式 |
|------|------|
| 板块热度对比 | HTML 横向柱状图 → Playwright 截图 |
| 行情走势示意 | image-generator（氛围图，不要求精确数字） |
| 主线概念图 | image-generator（半导体晶圆/服务器/机器人等） |
| 截图说明数据 | 直接截 akshare 输出或行情软件 |

正文配图文件命名：`output/illus-stock-[描述]-YYYYMMDD.png`

不要在正文中堆配图——一篇复盘最多2张正文配图，优先封面。
