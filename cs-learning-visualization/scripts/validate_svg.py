"""Static SVG structure and resource checks, not a complete sanitizer or visual QA."""
from pathlib import Path
import argparse
import math
import re
import xml.etree.ElementTree as ET

SVG_NS = "{http://www.w3.org/2000/svg}"
MAX_SVG_BYTES = 256_000
FORBIDDEN_SVG_TAGS = {
    "script", "foreignobject", "image", "iframe", "animate",
    "animatetransform", "animatemotion", "set", "use", "feimage",
}
REMOTE_VALUE = re.compile(r"(?:https?://|file:|javascript:|data:|@import|@font-face|expression\s*\()", re.I)
LOCAL_URL = re.compile(r"^url\(\s*#[A-Za-z][A-Za-z0-9_-]*\s*\)$", re.I)


def parse_safe_svg(data: bytes) -> ET.Element:
    """Reject executable or resource-loading SVG content before reviewing fixtures."""
    assert len(data) <= MAX_SVG_BYTES, "oversized SVG"
    assert not re.search(rb"<!\s*(?:DOCTYPE|ENTITY)\b", data, re.I), "DTD/entity declarations forbidden"
    root = ET.fromstring(data)
    assert root.tag == SVG_NS + "svg", "not an SVG root"
    for el in root.iter():
        bare = el.tag.rsplit("}", 1)[-1].lower()
        assert bare not in FORBIDDEN_SVG_TAGS, f"unsafe SVG element: {bare}"
        for key, value in el.attrib.items():
            attr = key.rsplit("}", 1)[-1].lower()
            assert not (attr.startswith("on") or attr.endswith("href")), f"unsafe SVG attribute: {attr}"
            assert not REMOTE_VALUE.search(value), f"unsafe external resource in {attr}"
            if re.search(r"url\s*\(", value, re.I):
                assert LOCAL_URL.fullmatch(value.strip()), f"nonlocal paint reference: {attr}"
        if bare == "style":
            style = el.text or ""
            assert not REMOTE_VALUE.search(style), "unsafe SVG CSS"
            # SVGs legitimately use local paint markers (url(#arrow)).
            # Accept those identifiers but no CSS remote/dynamic resource URLs.
            css_refs = re.findall(r"url\s*\([^)]*\)", style, re.I)
            assert len(css_refs) == len(re.findall(r"url\s*\(", style, re.I)), "malformed SVG CSS URL"
            assert all(LOCAL_URL.fullmatch(ref) for ref in css_refs), "nonlocal SVG CSS resource"
    return root



def validate_svg(path: Path) -> None:
    # Bound the read as well as parsing; reject symlinks to avoid accidental inputs.
    if path.is_symlink():
        raise ValueError("symlink input is not supported")
    with path.open("rb") as stream:
        root = parse_safe_svg(stream.read(MAX_SVG_BYTES + 1))
    values = [float(v) for v in root.attrib.get("viewBox", "").replace(",", " ").split()]
    if len(values) != 4 or not all(math.isfinite(v) for v in values) or min(values[2:]) <= 0:
        raise ValueError("viewBox must contain four finite numbers with positive width/height")
    if root.attrib.get("role") != "img":
        raise ValueError("role=img required")
    ids = [el.attrib["id"] for el in root.iter() if "id" in el.attrib]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate SVG ids")
    labels = root.attrib.get("aria-labelledby", "").split()
    title = root.find(SVG_NS + "title")
    desc = root.find(SVG_NS + "desc")
    for el in (title, desc):
        if el is None or not "".join(el.itertext()).strip() or not el.attrib.get("id") or el.attrib["id"] not in labels:
            raise ValueError("nonempty title/desc must be referenced by aria-labelledby")
    if any(label not in ids for label in labels):
        raise ValueError("aria-labelledby references missing ids")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()
    failed = False
    for path in args.paths:
        try:
            validate_svg(path)
        except (AssertionError, ValueError, OSError, ET.ParseError) as exc:
            print(f"FAIL: {path}: {exc}")
            failed = True
        else:
            print(f"PASS: {path} (static checks only)")
    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
