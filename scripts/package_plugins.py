"""Verify or sync canonical skill folders and Skills-only plugin bundles.

No network requests, Git changes or local plugin installation.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAMES = (
    "wiki-capture",
    "reverse-engineering",
    "backend-architecture-review",
    "tech-article-curation",
    "cs-learning-visualization",
    "concept-learning",
)
EXTRAS = {
    "concept-learning": (
        "references/topic-context.md",
        "references/source-and-visual-guidance.md",
        "references/response-quality-gate.md",
        "references/research-first-workflow.md",
        "references/response-modes.md",
        "references/teaching-rules.md",
        "references/subject-guidance.md",
        "references/quality-cases.md",
        "references/project-instructions.md",
    ),
    "cs-learning-visualization": (
        "examples/heap-tree-array.svg",
        "examples/java-pass-by-value.svg",
        "examples/tcp-sliding-window.svg",
        "examples/index.html",
    ),
}
SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"


def has_symlink_component(path: Path, trusted_root: Path = ROOT) -> bool:
    """Reject symlinked parent directories as well as symlinked leaf files.

    Without inspecting parents, --sync could follow a symlinked skills/ folder
    and write outside the repository even when target.is_symlink() is False.
    """
    try:
        components = path.relative_to(trusted_root).parts
    except ValueError:
        return True
    if ".." in components:
        return True
    current = trusted_root
    for part in components:
        current = current / part
        if current.is_symlink():
            return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="fail if plugin files differ from canonical sources")
    mode.add_argument("--sync", action="store_true", help="refresh plugin copies from canonical sources")
    args = parser.parse_args()

    errors: list[str] = []
    catalog_path = ROOT / ".agents/plugins/marketplace.json"
    if has_symlink_component(catalog_path):
        print("ERROR: marketplace path traverses a symlink")
        return 1
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    entries = catalog.get("plugins", [])
    by_name = {entry.get("name"): entry for entry in entries}
    if len(entries) != len(NAMES) or set(by_name) != set(NAMES):
        errors.append(f"marketplace must contain {len(NAMES)} distinct canonical plugins")

    for name in NAMES:
        package_root = ROOT / "plugins" / name
        manifest_path = package_root / "plugin.json"
        for subpath in ("SKILL.md", *EXTRAS.get(name, ())):
            source = ROOT / name / subpath
            target = package_root / "skills" / name / subpath
            if any(has_symlink_component(p) for p in (source, target, manifest_path)):
                errors.append(f"{name}/{subpath}: symlinks are not allowed")
                continue
            if not source.is_file():
                errors.append(f"{name}/{subpath}: missing canonical file")
                continue
            content = source.read_bytes()
            if args.sync:
                target.parent.mkdir(parents=True, exist_ok=True)
                if not target.is_file() or target.read_bytes() != content:
                    target.write_bytes(content)
                    print(f"Synced {target.relative_to(ROOT)}")
            if not target.is_file() or target.read_bytes() != content:
                errors.append(f"{name}/{subpath}: plugin copy differs from canonical source")
        if has_symlink_component(manifest_path):
            errors.append(f"{name}: manifest path traverses a symlink")
            continue
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            errors.append(f"{name}: missing or invalid plugin manifest")
            continue
        if (manifest.get("$schema") != SCHEMA or manifest.get("name") != name
                or not manifest.get("version") or not manifest.get("description")):
            errors.append(f"{name}: incomplete plugin manifest")
        entry = by_name.get(name, {})
        if (entry.get("source") != {"source": "local", "path": f"./plugins/{name}"}
                or entry.get("policy") != {"installation": "AVAILABLE", "authentication": "ON_INSTALL"}):
            errors.append(f"{name}: incorrect marketplace reference")

    for error in errors:
        print("ERROR:", error)
    print(f"Plugin package verification: {len(NAMES)} packages; {len(errors)} issue(s)")
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
