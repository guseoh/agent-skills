"""Check or refresh the four Skills-only plugin bundles from canonical skill files.

No network access, Git operations or local plugin installation.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAMES = ("wiki-capture", "reverse-engineering", "backend-architecture-review", "tech-article-curation")
SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="fail when plugin files are out of sync")
    mode.add_argument("--sync", action="store_true", help="copy root skill sources into plugin packages")
    args = parser.parse_args()

    errors: list[str] = []
    catalog_file = ROOT / ".agents/plugins/marketplace.json"
    catalog = json.loads(catalog_file.read_text(encoding="utf-8"))
    entries = catalog.get("plugins", [])
    by_name = {item.get("name"): item for item in entries}
    if len(entries) != len(NAMES) or set(by_name) != set(NAMES):
        errors.append("marketplace must contain four distinct canonical plugins")

    for name in NAMES:
        source = ROOT / name / "SKILL.md"
        target = ROOT / "plugins" / name / "skills" / name / "SKILL.md"
        manifest_path = ROOT / "plugins" / name / "plugin.json"
        if any(path.is_symlink() for path in (source, target, manifest_path)):
            errors.append(f"{name}: symlinks are not allowed")
            continue
        content = source.read_bytes()
        if args.sync:
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.exists() or target.read_bytes() != content:
                target.write_bytes(content)
                print(f"Synced {target.relative_to(ROOT)}")
        if not target.is_file() or target.read_bytes() != content:
            errors.append(f"{name}: packaged skill differs from canonical SKILL.md")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if (manifest.get("$schema") != SCHEMA or manifest.get("name") != name
                or not manifest.get("version") or not manifest.get("description")):
            errors.append(f"{name}: incomplete plugin manifest")
        entry = by_name.get(name, {})
        if (entry.get("source") != {"source": "local", "path": f"./plugins/{name}"}
                or entry.get("policy") != {"installation": "AVAILABLE", "authentication": "ON_INSTALL"}):
            errors.append(f"{name}: marketplace reference is incorrect")

    for error in errors:
        print("ERROR:", error)
    print(f"Plugin package verification: {len(NAMES)} packages; {len(errors)} issue(s)")
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
