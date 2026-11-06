"""Check basic Markdown structure and local links without executing embedded code."""
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote, urlsplit


def check(path: Path, root: Path) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    errors = []
    start = 0
    if lines and lines[0] == "---":
        try:
            start = lines.index("---", 1) + 1
        except ValueError:
            return ["unclosed frontmatter"]
    fence = None
    headings = 0
    for number, line in enumerate(lines[start:], start + 1):
        match = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if match:
            marker, suffix = match.groups()
            if fence is None:
                fence = marker
            elif marker[0] == fence[0] and len(marker) >= len(fence) and not suffix.strip():
                fence = None
            continue
        if fence:
            continue
        if line.startswith("# "):
            headings += 1
        for raw in re.findall(r"\]\(([^\s)]+)\)", line):
            target = raw.strip("<>")
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc or target.startswith("#"):
                continue
            resolved = (path.parent / unquote(parsed.path)).resolve()
            if not resolved.is_relative_to(root) or not resolved.is_file():
                errors.append(f"line {number}: missing/outside local link {target}")
    if fence:
        errors.append("unclosed code fence")
    if headings != 1:
        errors.append(f"expected one H1, found {headings}")
    return errors


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    tracked = subprocess.check_output(
        ["git", "ls-files", "-z", "--", "*.md"], cwd=root
    ).decode("utf-8").split("\0")
    problems = []
    paths = [root / value for value in tracked if value]
    for path in paths:
        problems.extend(f"{path.relative_to(root)}: {error}" for error in check(path, root))
    for problem in problems:
        print(problem, file=sys.stderr)
    print(f"Checked {len(paths)} Markdown files: {len(problems)} issue(s)")
    return int(bool(problems))


if __name__ == "__main__":
    raise SystemExit(main())
