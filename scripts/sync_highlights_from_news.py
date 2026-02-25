#!/usr/bin/env python3
import re
from pathlib import Path


ROOT = Path("/Users/skmacair/work/shilicon.github.io")
NEWS_PATH = ROOT / "news/index.html"
HOME_PATH = ROOT / "index.html"
LIMIT = 3


def extract_news_items(news_html: str) -> list[str]:
    ul_match = re.search(r"<ul class=\"list stagger\">([\s\S]*?)</ul>", news_html)
    if not ul_match:
        raise RuntimeError("Could not find news list block in news/index.html")

    list_body = ul_match.group(1)
    items = re.findall(r"<li>\s*[\s\S]*?\s*</li>", list_body)
    if not items:
        raise RuntimeError("No news items found in news/index.html")
    return items[:LIMIT]


def format_home_list(items: list[str]) -> str:
    lines = ['          <ul class="list stagger" style="margin: 0;">']
    for item in items:
        block = item.strip().splitlines()
        for line in block:
            lines.append(f"            {line.strip()}")
    lines.append("          </ul>")
    return "\n".join(lines)


def sync():
    news_html = NEWS_PATH.read_text(encoding="utf-8")
    home_html = HOME_PATH.read_text(encoding="utf-8")
    items = extract_news_items(news_html)
    replacement = format_home_list(items)

    pattern = r"<!-- highlights:start -->[\s\S]*?<!-- highlights:end -->"
    block = f"<!-- highlights:start -->\n{replacement}\n          <!-- highlights:end -->"
    new_home, count = re.subn(pattern, block, home_html, count=1)
    if count != 1:
        raise RuntimeError("Could not find highlights markers in index.html")

    HOME_PATH.write_text(new_home, encoding="utf-8")
    print(f"Synced {len(items)} highlights from news.")


if __name__ == "__main__":
    sync()
