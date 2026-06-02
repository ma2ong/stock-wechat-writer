#!/usr/bin/env python3
"""Prepare and optionally generate recap cover/inline images via Baoyu.

The stock writing workflow owns the prompts and filenames. Baoyu Imagine
or the legacy baoyu-image-gen script is used only as an image backend.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "output"


@dataclass
class Backend:
    name: str
    script: Path


@dataclass
class Article:
    date: str
    title: str
    paragraphs: list[str]
    body: str


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
        m = re.search(r"(20\d{6})", path.stem)
        date = m.group(1) if m else datetime.now().strftime("%Y%m%d")
    return Article(date=date, title=title, paragraphs=paragraphs, body=text)


def baoyu_skill_roots() -> list[Path]:
    return [
        Path.home() / ".agents" / "skills" / "baoyu-skills" / "skills",
        Path.home() / ".codex" / "skills" / "baoyu-skills" / "skills",
        ROOT.parent / "baoyu-skills" / "skills",
    ]


def find_backend(choice: str) -> Backend | None:
    candidates = ["baoyu-imagine", "baoyu-image-gen"] if choice == "auto" else [choice]
    for root in baoyu_skill_roots():
        for name in candidates:
            script = root / name / "scripts" / "main.ts"
            if script.exists():
                return Backend(name=name, script=script)
    return None


def runtime_cmd() -> list[str] | None:
    bun = shutil.which("bun") or shutil.which("bun.cmd")
    if bun:
        return [bun]
    npx = shutil.which("npx") or shutil.which("npx.cmd")
    if npx:
        return [npx, "-y", "bun"]
    return None


def has_baoyu_preferences(name: str) -> bool:
    paths = [
        ROOT / ".baoyu-skills" / name / "EXTEND.md",
        Path.home() / ".baoyu-skills" / name / "EXTEND.md",
        Path(os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config"))) / "baoyu-skills" / name / "EXTEND.md",
    ]
    return any(p.exists() for p in paths)


def has_api_key() -> bool:
    keys = [
        "OPENAI_API_KEY",
        "AZURE_OPENAI_API_KEY",
        "OPENROUTER_API_KEY",
        "GOOGLE_API_KEY",
        "DASHSCOPE_API_KEY",
        "MINIMAX_API_KEY",
        "REPLICATE_API_TOKEN",
        "JIMENG_ACCESS_KEY_ID",
        "ARK_API_KEY",
    ]
    return any(os.environ.get(k) for k in keys)


def classify_mood(article: Article) -> str:
    text = article.title + "\n" + "\n".join(article.paragraphs[:8])
    if re.search(r"暴跌|跌5%|跌 5%|退潮|破位|风险|撤|被砸", text):
        return "risk_rotation"
    if re.search(r"大涨|涨停|反包|修复|爆发|强势", text):
        return "strong_rebound"
    if re.search(r"切换|换地方|轮动|扩散", text):
        return "rotation"
    return "mixed"


def key_lines(article: Article, limit: int = 5) -> list[str]:
    lines = []
    for p in article.paragraphs:
        if any(k in p for k in ["科创50", "涨停池", "资金", "煤炭", "软件", "传媒", "CPO", "半导体", "手里是", "空仓"]):
            lines.append(p)
        if len(lines) >= limit:
            break
    return lines or article.paragraphs[:limit]


def prompt_header(article: Article) -> str:
    evidence = "\n".join(f"- {line}" for line in key_lines(article))
    return f"""Article title: {article.title}
Date: {article.date}
Key market evidence:
{evidence}

Hard requirements:
- No text, no numbers, no stock tickers, no watermarks in the image.
- Do not render Chinese characters inside the image.
- The image is a visual mood layer for an A-share stock recap, not an infographic.
- Clean financial editorial style, suitable for WeChat and Xiaohongshu.
"""


def cover_prompt(article: Article) -> str:
    mood = classify_mood(article)
    mood_map = {
        "risk_rotation": "a tense market-rotation scene: one crowded red technology trading screen fading, another calmer low-position opportunity screen lighting up, a Chinese retail investor pausing before acting",
        "strong_rebound": "a sharp rebound scene: a Chinese retail investor watching a glowing market screen recover, energetic but not euphoric",
        "rotation": "a fast sector-rotation scene: capital flow lines moving between two market screens, a Chinese retail investor turning quickly to reassess positions",
        "mixed": "a mixed-market scene: a Chinese retail investor comparing two opposite market screens, uncertain but focused",
    }
    return f"""{prompt_header(article)}
Task: Generate the main article cover illustration.

Scene:
{mood_map[mood]}.

Style:
flat editorial illustration, modern Chinese financial media, refined composition,
strong silhouette, clean background, restrained red/orange and dark ink accents,
large empty safe area on the left for overlaid title text, 16:9 landscape.
"""


def inline_prompt(article: Article, index: int) -> str:
    return f"""{prompt_header(article)}
Task: Generate inline article image #{index}.

Scene:
An abstract financial flow visualization. Capital leaves an overheated hardware
cluster and moves toward lower-position sectors. Use visual metaphors such as
flowing ribbons, layered market screens, heat/cool contrast, and a cautious
investor checking risk.

Style:
clean editorial illustration, no chart labels, no words, no numbers, no ticker
symbols, usable as a mid-article mood image, 16:9 landscape.
"""


def write_prompts(article: Article, out_dir: Path, inline_count: int) -> list[dict]:
    prompt_dir = out_dir / "prompts"
    prompt_dir.mkdir(parents=True, exist_ok=True)
    tasks = []

    cover_file = prompt_dir / "cover.md"
    cover_file.write_text(cover_prompt(article), encoding="utf-8")
    tasks.append(
        {
            "id": "cover",
            "promptFiles": [str(cover_file.relative_to(out_dir))],
            "image": "cover-16x9.png",
            "ar": "16:9",
            "quality": "2k",
        }
    )

    for i in range(1, inline_count + 1):
        prompt_file = prompt_dir / f"inline-{i:02d}.md"
        prompt_file.write_text(inline_prompt(article, i), encoding="utf-8")
        tasks.append(
            {
                "id": f"inline-{i:02d}",
                "promptFiles": [str(prompt_file.relative_to(out_dir))],
                "image": f"inline-{i:02d}.png",
                "ar": "16:9",
                "quality": "2k",
            }
        )
    return tasks


def write_batch(out_dir: Path, tasks: list[dict], provider: str | None, model: str | None) -> Path:
    normalized = []
    for task in tasks:
        item = dict(task)
        if provider:
            item["provider"] = provider
        if model:
            item["model"] = model
        normalized.append(item)
    batch = {"jobs": 1, "tasks": normalized}
    batch_path = out_dir / "baoyu-batch.json"
    batch_path.write_text(json.dumps(batch, ensure_ascii=False, indent=2), encoding="utf-8")
    return batch_path


def run_backend(backend: Backend, batch_path: Path, cwd: Path) -> int:
    cmd_prefix = runtime_cmd()
    if not cmd_prefix:
        print("blocked: bun/npx not found. Prompt files and batch file were generated.")
        return 2
    if not (has_baoyu_preferences(backend.name) or has_api_key()):
        print(f"blocked: {backend.name} preferences/API key not found. Prompt files and batch file were generated.")
        return 2
    cmd = [*cmd_prefix, str(backend.script), "--batchfile", str(batch_path), "--json"]
    print("running:", " ".join(cmd))
    return subprocess.run(cmd, cwd=cwd).returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate cover and inline images via Baoyu backend.")
    parser.add_argument("--article", required=True, type=Path)
    parser.add_argument("--date")
    parser.add_argument("--mode", choices=["cover", "inline", "all"], default="all")
    parser.add_argument("--inline-count", type=int, default=1)
    parser.add_argument("--backend", choices=["auto", "baoyu-imagine", "baoyu-image-gen"], default="auto")
    parser.add_argument("--provider")
    parser.add_argument("--model")
    parser.add_argument("--dry-run", action="store_true", help="Write prompts and batch file only")
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()

    article = parse_article(args.article, args.date)
    out_dir = args.output_dir or DEFAULT_OUTPUT / f"article-images-{article.date}"
    out_dir.mkdir(parents=True, exist_ok=True)

    inline_count = 0 if args.mode == "cover" else max(0, args.inline_count)
    tasks = write_prompts(article, out_dir, inline_count if args.mode != "cover" else 0)
    if args.mode == "inline":
        tasks = [task for task in tasks if task["id"].startswith("inline")]
    batch_path = write_batch(out_dir, tasks, args.provider, args.model)

    backend = find_backend(args.backend)
    print(f"output: {out_dir}")
    print(f"batch: {batch_path}")
    print(f"backend: {backend.name if backend else 'not found'}")

    if args.dry_run:
        return 0
    if not backend:
        print("blocked: baoyu backend script not found. Use --dry-run output or install baoyu-skills.")
        return 2
    return run_backend(backend, batch_path, out_dir)


if __name__ == "__main__":
    raise SystemExit(main())
