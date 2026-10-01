"""Print a version's CHANGELOG.md entry as plain text for the Comfy Registry.

The registry's "Updates" section shows the changelog as one plain-text
paragraph (no Markdown, newlines collapse), so each table is reduced to its
first column: "Added: A; B. Fixed: C. Full changelog: <url>".

Usage: registry_changelog.py [version]   (defaults to pyproject.toml's version)
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def plain(cell):
    cell = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", cell)  # [text](url) -> text
    return cell.replace("\\|", "|").replace("`", "").replace("**", "").strip()


def main():
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    version = sys.argv[1] if len(sys.argv) > 1 else re.search(r'^version\s*=\s*"([^"]+)"', pyproject, re.M).group(1)
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    section = re.search(rf"^## \[{re.escape(version)}\][^\n]*\n(.*?)(?=^## \[|\Z)", changelog, re.M | re.S)
    if not section:
        print(
            f"::warning::CHANGELOG.md has no '## [{version}]' section; publishing without a changelog", file=sys.stderr
        )
        return

    groups, in_table = [], False  # [(heading, [first-column cells])]
    for line in section.group(1).splitlines():
        if line.startswith("### "):
            groups.append((line[4:].strip(), []))
            in_table = False
        elif line.startswith("|"):
            if not in_table:
                in_table = True  # the first row of every table is its header
            elif groups and not re.match(r"^\|[\s:|-]+$", line):  # skip the |---| separator
                groups[-1][1].append(plain(re.split(r"(?<!\\)\|", line)[1]))
        else:
            in_table = False
    parts = [f"{heading}: {'; '.join(items)}." for heading, items in groups if items]

    repo = re.search(r'^Repository\s*=\s*"([^"]+)"', pyproject, re.M)
    if repo:
        parts.append(f"Full changelog: {repo.group(1)}/blob/master/CHANGELOG.md")
    print(" ".join(parts))


if __name__ == "__main__":
    main()
