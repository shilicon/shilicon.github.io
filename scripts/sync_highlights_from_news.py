#!/usr/bin/env python3
import re
from pathlib import Path


ROOT = Path("/Users/skmacair/work/shilicon.github.io")
NEWS_PATH = ROOT / "news/index.html"
HOME_PATH = ROOT / "index.html"
LIMIT = 3
ABBREVIATIONS = {"mr.", "mrs.", "ms.", "dr.", "prof.", "sr.", "jr.", "e.g.", "i.e."}


def extract_news_items(news_html: str) -> list[str]:
    ul_match = re.search(r"<ul class=\"list stagger\">([\s\S]*?)</ul>", news_html)
    if not ul_match:
        raise RuntimeError("Could not find news list block in news/index.html")

    list_body = ul_match.group(1)
    items = re.findall(r"<li>\s*[\s\S]*?\s*</li>", list_body)
    if not items:
        raise RuntimeError("No news items found in news/index.html")
    return items[:LIMIT]


def first_sentence(text: str) -> str:
    clean = re.sub(r"\s+", " ", text).strip()
    for punct in re.finditer(r"[.!?]", clean):
        idx = punct.start()
        candidate = clean[: idx + 1].strip()
        last_word = candidate.split()[-1].lower() if candidate.split() else ""
        if punct.group() == "." and last_word in ABBREVIATIONS:
            continue
        tail = clean[idx + 1 :]
        if re.match(r"^\s+[A-Z\"']", tail) or not tail.strip():
            return candidate
    return clean


def trim_item_to_first_sentence(item_html: str) -> str:
    meta_match = re.search(
        r"(<div class=\"meta\">)([\s\S]*?)(</div>)",
        item_html,
        flags=re.IGNORECASE,
    )
    if not meta_match:
        return item_html
    trimmed = first_sentence(meta_match.group(2))
    return item_html[: meta_match.start(2)] + trimmed + item_html[meta_match.end(2) :]


def format_home_list(items: list[str]) -> str:
    lines = ['          <ul class="list stagger" style="margin: 0;">']
    for item in items:
        block = trim_item_to_first_sentence(item).strip().splitlines()
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
