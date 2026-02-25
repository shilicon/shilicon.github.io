#!/usr/bin/env python3
import re
from pathlib import Path


ROOT = Path("/Users/skmacair/work/shilicon.github.io")
BIB_PATH = ROOT / "publications/publications.bib"
HTML_PATH = ROOT / "publications/index.html"


MONTH_MAP = {
    "jan": 1,
    "january": 1,
    "feb": 2,
    "february": 2,
    "mar": 3,
    "march": 3,
    "apr": 4,
    "april": 4,
    "may": 5,
    "jun": 6,
    "june": 6,
    "jul": 7,
    "july": 7,
    "aug": 8,
    "august": 8,
    "sep": 9,
    "sept": 9,
    "september": 9,
    "oct": 10,
    "october": 10,
    "nov": 11,
    "november": 11,
    "dec": 12,
    "december": 12,
}


def parse_month(raw: str) -> int | None:
    if not raw:
        return None
    val = raw.strip().lower().replace(".", "")
    if val.isdigit():
        month_num = int(val)
        return month_num if 1 <= month_num <= 12 else None
    return MONTH_MAP.get(val)


def parse_entries(bib_text: str):
    entries = []
    pattern = r"@(\w+)\s*\{\s*([^,]+),([\s\S]*?)\n\}\s*"
    for file_index, match in enumerate(re.finditer(pattern, bib_text)):
        body = match.group(3)
        fields = {}
        for field in re.finditer(r"\n\s*([a-zA-Z]+)\s*=\s*\{([\s\S]*?)\}\s*,?", body):
            key = field.group(1).lower()
            val = re.sub(r"\s+", " ", field.group(2).replace("\n", " ").strip())
            fields[key] = val

        title = fields.get("title", "Untitled")
        title = title.replace("{$\\{SmartNIC-accelerated\\}$}", "SmartNIC-accelerated")
        title = title.replace("$\\{$", "").replace("$\\}$", "")
        title = title.replace("\\{", "{").replace("\\}", "}")
        title = re.sub(r"\$+", "", title).strip()

        year = fields.get("year", "n/a")
        try:
            year_int = int(year)
        except ValueError:
            year_int = -1

        month_num = parse_month(fields.get("month", ""))
        entries.append(
            {
                "title": title,
                "authors": fields.get("author", "Unknown authors"),
                "venue": fields.get("journal")
                or fields.get("booktitle")
                or fields.get("publisher")
                or fields.get("organization")
                or "Unspecified venue",
                "year": year,
                "year_int": year_int,
                "month_num": month_num,
                "file_index": file_index,
            }
        )
    return entries


def build_list_html(entries) -> str:
    items = []
    for entry in entries:
        items.append(
            "          <li>\n"
            f"            <strong>{entry['title']}</strong>\n"
            f"            <div class=\"meta\">{entry['authors']}</div>\n"
            f"            <div class=\"meta\">{entry['venue']} · {entry['year']}</div>\n"
            "          </li>"
        )
    return "<ul class=\"list stagger publication-list\">\n" + "\n".join(items) + "\n        </ul>"


def main():
    bib_text = BIB_PATH.read_text(encoding="utf-8")
    entries = parse_entries(bib_text)
    entries.sort(
        key=lambda e: (
            -e["year_int"],
            0 if e["month_num"] is not None else 1,
            -(e["month_num"] or 0),
            e["file_index"],
        )
    )

    html = HTML_PATH.read_text(encoding="utf-8")
    new_list = build_list_html(entries)
    html = re.sub(
        r"<ul class=\"list stagger publication-list\">[\s\S]*?</ul>",
        new_list,
        html,
        count=1,
    )
    HTML_PATH.write_text(html, encoding="utf-8")
    print(f"Synced {len(entries)} publications.")


if __name__ == "__main__":
    main()
