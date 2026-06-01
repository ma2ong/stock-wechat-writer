#!/usr/bin/env python3
"""Generate social cards from an A-share recap article.

The visual system follows the Guizang social-card workflow at the interface
level: fixed platform ratios, one idea per card, Swiss-style typography, and
PNG outputs. It does not copy Guizang template code or image assets.
"""

from __future__ import annotations

import argparse
import html
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "output"
GUIZANG_TEMPLATE = ROOT / "third_party" / "guizang-social-card-skill" / "assets" / "template-swiss-card.html"

ACCENTS = {
    "ikb": (0, 87, 255),
    "safety-orange": (255, 90, 31),
    "lemon-yellow": (255, 214, 0),
}

INK = (17, 24, 39)
MUTED = (92, 99, 112)
PAPER = (247, 246, 241)
LINE = (214, 218, 226)
WHITE = (255, 255, 255)


@dataclass
class Article:
    date: str
    title: str
    body: str
    paragraphs: list[str]


@dataclass
class Card:
    slug: str
    kicker: str
    title: str
    bullets: list[str]
    footer: str = ""


def font_path() -> str:
    candidates = [
        Path(r"C:\Windows\Fonts\msyh.ttc"),
        Path(r"C:\Windows\Fonts\simhei.ttf"),
        Path(r"C:\Windows\Fonts\simsun.ttc"),
    ]
    for path in candidates:
        if path.exists():
            return str(path)
    return ""


FONT_PATH = font_path()


def font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    if FONT_PATH:
        return ImageFont.truetype(FONT_PATH, size=size)
    return ImageFont.load_default(size=size)


def parse_article(path: Path, date: str | None) -> Article:
    text = path.read_text(encoding="utf-8").lstrip("\ufeff")
    title_match = re.search(r"^#\s+(.+)$", text, re.M)
    title = title_match.group(1).strip() if title_match else path.stem
    paragraphs = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "数据来源" in line or "不构成投资建议" in line:
            continue
        paragraphs.append(line)
    if not date:
        date_match = re.search(r"(20\d{6})", path.stem)
        date = date_match.group(1) if date_match else datetime.now().strftime("%Y%m%d")
    return Article(date=date, title=title, body=text, paragraphs=paragraphs)


def choose_accent(article: Article, override: str) -> str:
    if override != "auto":
        return override
    text = article.title + "\n" + article.body
    if re.search(r"跌|退潮|破位|减仓|风险|撤", text):
        return "safety-orange"
    if re.search(r"大涨|涨停池|强势|爆发|修复", text):
        return "lemon-yellow"
    return "ikb"


def find_lines(article: Article, keywords: list[str], limit: int = 3) -> list[str]:
    hits = []
    for p in article.paragraphs:
        if any(k in p for k in keywords):
            hits.append(p)
        if len(hits) >= limit:
            break
    return hits


def clean_bullet(text: str, max_len: int = 44) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"。$", "", text)
    if len(text) <= max_len:
        return text
    return text[: max_len - 1] + "…"


def build_cards(article: Article) -> list[Card]:
    stats = find_lines(article, ["科创50", "涨停池", "全市场"], 3)
    outflow = find_lines(article, ["净流出", "跌停", "破位", "被砸"], 3)
    inflow = find_lines(article, ["煤炭", "软件", "传媒", "AI 应用", "资金"], 3)
    plan = find_lines(article, ["周二", "手里是", "空仓", "别追", "减"], 4)
    cover_title = article.title.replace("，", "\n", 1).replace(",", "\n", 1)

    cards = [
        Card(
            slug="cover",
            kicker="A股复盘",
            title=cover_title,
            bullets=[clean_bullet(p, 36) for p in article.paragraphs[:3]],
            footer=fmt_date(article.date),
        ),
        Card(
            slug="market-contrast",
            kicker="今天最反常",
            title="指数很差\n个股很活",
            bullets=[clean_bullet(p) for p in stats[:3]] or [clean_bullet(article.paragraphs[0])],
        ),
        Card(
            slug="sell-pressure",
            kicker="资金撤出",
            title="高位硬件\n先被卖",
            bullets=[clean_bullet(p) for p in outflow[:3]] or [clean_bullet(p) for p in article.paragraphs[2:5]],
        ),
        Card(
            slug="money-shift",
            kicker="资金去向",
            title="低位试错\n开始扩散",
            bullets=[clean_bullet(p) for p in inflow[:3]] or [clean_bullet(p) for p in article.paragraphs[5:8]],
        ),
        Card(
            slug="trade-plan",
            kicker="交易动作",
            title="别急追\n先筛选",
            bullets=[clean_bullet(p) for p in plan[:4]] or [clean_bullet(p) for p in article.paragraphs[-4:]],
        ),
    ]
    return cards


def fmt_date(date: str) -> str:
    if re.fullmatch(r"\d{8}", date):
        return f"{date[:4]}.{date[4:6]}.{date[6:]}"
    return date


def short_title(title: str) -> str:
    title = re.sub(r"[#，,。！？!?:：].*$", "", title).strip()
    title = re.sub(r"\s+", "", title)
    if len(title) <= 10:
        return title
    for token in ["科创50", "涨停池", "科技硬件", "资金换向", "主线切换"]:
        if token in title:
            return token
    return title[:10]


def text_size(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.ImageFont) -> tuple[int, int]:
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0], box[3] - box[1]


def wrap_text(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.ImageFont, width: int, max_lines: int | None = None) -> list[str]:
    lines: list[str] = []
    for para in text.split("\n"):
        current = ""
        for ch in para:
            probe = current + ch
            if text_size(draw, probe, fnt)[0] <= width:
                current = probe
            else:
                if current:
                    lines.append(current)
                current = ch
                if max_lines and len(lines) >= max_lines:
                    lines[-1] = lines[-1].rstrip("，。；") + "…"
                    return lines
        if current:
            lines.append(current)
        if max_lines and len(lines) >= max_lines:
            return lines[:max_lines]
    return lines


def draw_label(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, accent: tuple[int, int, int]) -> None:
    x, y = xy
    fnt = font(26)
    draw.line((x, y + 13, x + 74, y + 13), fill=accent, width=6)
    draw.text((x + 96, y), text.upper(), fill=MUTED, font=fnt)


def draw_wrapped(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    fnt: ImageFont.ImageFont,
    fill: tuple[int, int, int],
    width: int,
    line_gap: int,
    max_lines: int | None = None,
) -> int:
    x, y = xy
    lines = wrap_text(draw, text, fnt, width, max_lines)
    line_h = text_size(draw, "国", fnt)[1] + line_gap
    for line in lines:
        draw.text((x, y), line, fill=fill, font=fnt)
        y += line_h
    return y


def render_xhs_card(card: Card, article: Article, idx: int, accent: tuple[int, int, int], out: Path) -> None:
    w, h = 1080, 1440
    img = Image.new("RGB", (w, h), PAPER)
    draw = ImageDraw.Draw(img)

    margin = 82
    draw.rectangle((0, 0, w, 24), fill=accent)
    draw.text((margin, 72), card.kicker, fill=MUTED, font=font(28))
    draw.text((w - margin - 180, 72), fmt_date(article.date), fill=MUTED, font=font(24))

    title_font = font(96 if idx == 1 else 82)
    y = 170
    y = draw_wrapped(draw, (margin, y), card.title, title_font, INK, w - margin * 2, 16, max_lines=3)
    y += 34
    draw.line((margin, y, margin + 160, y), fill=accent, width=10)
    y += 62

    body_font = font(34)
    for n, bullet in enumerate(card.bullets[:4], start=1):
        block_top = y
        draw.text((margin, y + 3), f"{n:02d}", fill=accent, font=font(30))
        y = draw_wrapped(draw, (margin + 72, y), bullet, body_font, INK, w - margin * 2 - 72, 14, max_lines=3)
        y += 36
        draw.line((margin + 72, y, w - margin, y), fill=LINE, width=2)
        y += 34
        if y > h - 210:
            break
        if y - block_top < 90:
            y += 12

    footer = card.footer or "内容仅作复盘参考，不构成投资建议"
    draw.line((margin, h - 142, w - margin, h - 142), fill=LINE, width=2)
    draw.text((margin, h - 106), footer, fill=MUTED, font=font(24))
    draw.text((w - margin - 150, h - 106), f"{idx:02d}/{5:02d}", fill=MUTED, font=font(24))
    img.save(out)


def render_wechat(article: Article, accent: tuple[int, int, int], out_dir: Path) -> None:
    date = fmt_date(article.date)
    subtitle = "资金在换地方，仓位别太满"
    for p in article.paragraphs:
        if "钱" in p or "资金" in p:
            subtitle = clean_bullet(p, 24)
            break

    wide = Image.new("RGB", (2100, 900), PAPER)
    d = ImageDraw.Draw(wide)
    d.rectangle((0, 0, 40, 900), fill=accent)
    d.text((130, 90), "A股复盘", fill=MUTED, font=font(36))
    d.text((1750, 90), date, fill=MUTED, font=font(34))
    d.line((130, 165, 1970, 165), fill=LINE, width=2)
    y = draw_wrapped(d, (130, 260), article.title, font(104), INK, 1700, 18, max_lines=2)
    d.line((130, y + 54, 300, y + 54), fill=accent, width=12)
    d.text((130, y + 106), subtitle, fill=INK, font=font(46))
    d.text((130, 780), "内容仅作复盘参考，不构成投资建议", fill=MUTED, font=font(28))
    wide_path = out_dir / f"wechat-cover-21x9-{article.date}.png"
    wide.save(wide_path)

    square = Image.new("RGB", (1080, 1080), PAPER)
    d = ImageDraw.Draw(square)
    d.rectangle((0, 0, 1080, 34), fill=accent)
    st = short_title(article.title)
    lines = wrap_text(d, st, font(112), 780, max_lines=2)
    total_h = len(lines) * 132
    y = (1080 - total_h) // 2 - 30
    for line in lines:
        tw, _ = text_size(d, line, font(112))
        d.text(((1080 - tw) // 2, y), line, fill=INK, font=font(112))
        y += 132
    d.text((390, 940), f"A股 · {date}", fill=MUTED, font=font(30))
    square.save(out_dir / f"wechat-cover-1x1-{article.date}.png")

    preview = Image.new("RGB", (2400, 1280), WHITE)
    preview.paste(wide.resize((1400, 600)), (80, 120))
    preview.paste(square.resize((600, 600)), (1680, 120))
    ImageDraw.Draw(preview).text((80, 800), "WeChat cover pair preview", fill=MUTED, font=font(34))
    preview.save(out_dir / f"wechat-cover-pair-preview-{article.date}.png")


def write_preview_html(out_root: Path, image_paths: list[Path]) -> None:
    rels = [p.relative_to(out_root).as_posix() for p in image_paths]
    cards = "\n".join(
        f'<figure><img src="{html.escape(src)}"><figcaption>{html.escape(Path(src).name)}</figcaption></figure>'
        for src in rels
    )
    (out_root / "index.html").write_text(
        f"""<!doctype html>
<html lang="zh-CN">
<meta charset="utf-8">
<title>Stock Recap Social Cards</title>
<style>
body{{margin:0;padding:40px;background:#f3f4f6;font-family:Arial,'Microsoft YaHei',sans-serif;color:#111827}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:28px;align-items:start}}
figure{{margin:0;background:white;padding:14px;border:1px solid #e5e7eb}}
img{{width:100%;height:auto;display:block}}
figcaption{{font-size:13px;color:#6b7280;margin-top:10px}}
</style>
<main class="grid">{cards}</main>
""",
        encoding="utf-8",
    )


def esc(text: str) -> str:
    return html.escape(text).replace("\n", "<br>")


def guizang_xhs_section(card: Card, article: Article, idx: int) -> str:
    bullet_html = "\n".join(
        f"""
        <div class="card-fill">
          <div class="row gap-6">
            <p class="t-meta">{n:02d}</p>
            <p class="body">{esc(bullet)}</p>
          </div>
        </div>"""
        for n, bullet in enumerate(card.bullets[:4], start=1)
    )
    return f"""
    <section class="poster xhs" id="xhs-{idx:02d}">
      <div class="content stack gap-9">
        <div class="chrome-min">
          <span>{esc(card.kicker)}</span>
          <span>{esc(fmt_date(article.date))}</span>
        </div>
        <div class="stack gap-7">
          <p class="t-cat">A股复盘 · {idx:02d}/05</p>
          <h1 class="h-statement">{esc(card.title)}</h1>
        </div>
        <div class="stack gap-5">
          {bullet_html}
        </div>
        <div class="grow"></div>
        <hr class="hr-accent">
        <p class="t-meta">{esc(card.footer or "内容仅作复盘参考，不构成投资建议")}</p>
      </div>
    </section>"""


def guizang_wechat_sections(article: Article) -> str:
    subtitle = "资金在换地方，仓位别太满"
    for p in article.paragraphs:
        if "钱" in p or "资金" in p:
            subtitle = clean_bullet(p, 24)
            break
    st = short_title(article.title)
    date = fmt_date(article.date)
    return f"""
    <section class="poster wide" id="wechat-21x9">
      <div class="content stack gap-9">
        <div class="chrome-min">
          <span>A股复盘</span>
          <span>{esc(date)}</span>
        </div>
        <div class="grow"></div>
        <div class="stack gap-7">
          <p class="t-cat">市场复盘</p>
          <h1 class="h-xl">{esc(article.title)}</h1>
        </div>
        <hr class="hr-accent">
        <p class="lead">{esc(subtitle)}</p>
        <div class="grow"></div>
        <p class="t-meta">内容仅作复盘参考，不构成投资建议</p>
      </div>
    </section>

    <section class="poster square" id="wechat-1x1">
      <div class="content stack gap-9" style="align-items:center;text-align:center">
        <div class="grow"></div>
        <h1 class="h-statement">{esc(st)}</h1>
        <div class="grow"></div>
        <p class="t-meta">A股 · {esc(date)}</p>
      </div>
    </section>"""


def write_guizang_html(out_root: Path, article: Article, cards: list[Card], accent_name: str) -> Path | None:
    if not GUIZANG_TEMPLATE.exists():
        return None
    template = GUIZANG_TEMPLATE.read_text(encoding="utf-8")
    template = re.sub(
        r'<html lang="zh-CN" data-accent="[^"]+"',
        f'<html lang="zh-CN" data-accent="{accent_name}"',
        template,
        count=1,
    )
    posters = "\n".join(guizang_xhs_section(card, article, idx) for idx, card in enumerate(cards, start=1))
    posters += "\n" + guizang_wechat_sections(article)
    rendered = re.sub(r"\s*<!-- POSTERS_HERE -->.*?</main>", "\n" + posters + "\n  </main>", template, flags=re.S)
    out_path = out_root / "guizang-index.html"
    out_path.write_text(rendered, encoding="utf-8")
    return out_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate stock recap social cards.")
    parser.add_argument("--article", required=True, type=Path, help="Markdown recap article path")
    parser.add_argument("--date", help="YYYYMMDD, defaults to date in article filename")
    parser.add_argument("--mode", choices=["all", "xhs", "wechat"], default="all")
    parser.add_argument("--accent", choices=["auto", *ACCENTS.keys()], default="auto")
    parser.add_argument("--output-dir", type=Path, help="Output root, defaults to output/social-cards-YYYYMMDD")
    args = parser.parse_args()

    article = parse_article(args.article, args.date)
    accent_name = choose_accent(article, args.accent)
    accent = ACCENTS[accent_name]
    out_root = args.output_dir or DEFAULT_OUTPUT / f"social-cards-{article.date}"
    cards_dir = out_root / "output"
    cards_dir.mkdir(parents=True, exist_ok=True)

    image_paths: list[Path] = []
    cards = build_cards(article)
    if args.mode in {"all", "xhs"}:
        for idx, card in enumerate(cards, start=1):
            out = cards_dir / f"xhs-{idx:02d}-{card.slug}.png"
            render_xhs_card(card, article, idx, accent, out)
            image_paths.append(out)

    if args.mode in {"all", "wechat"}:
        render_wechat(article, accent, cards_dir)
        image_paths.extend(sorted(cards_dir.glob(f"wechat-cover-*-{article.date}.png")))

    write_preview_html(out_root, image_paths)
    guizang_html = write_guizang_html(out_root, article, cards, accent_name)
    print(f"generated: {out_root}")
    if guizang_html:
        print(f"- {guizang_html}")
    for path in image_paths:
        print(f"- {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
