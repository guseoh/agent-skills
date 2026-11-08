"""Static validation for the three self-authored educational SVG fixtures.

This validates metadata and encoded example states, NOT visual layout or semantics
beyond these particular examples. No external dependencies required.
"""
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
NAME = "cs-learning-visualization"
SVG_NS = "{http://www.w3.org/2000/svg}"
CASES = ("heap-tree-array", "java-pass-by-value", "tcp-sliding-window")
MAX_SVG_BYTES = 256_000
FORBIDDEN_SVG_TAGS = {
    "script", "foreignobject", "image", "iframe", "animate",
    "animatetransform", "animatemotion", "set", "use", "feimage",
}
REMOTE_VALUE = re.compile(r"(?:https?://|file:|javascript:|data:|@import|@font-face|expression\\s*\\()", re.I)
LOCAL_URL = re.compile(r"^url\\(\\s*#[A-Za-z][A-Za-z0-9_-]*\\s*\\)$", re.I)


def parse_safe_svg(data: bytes) -> ET.Element:
    """Reject executable or resource-loading SVG content before reviewing fixtures."""
    assert len(data) <= MAX_SVG_BYTES, "oversized SVG"
    assert not re.search(rb"<!\\s*(?:DOCTYPE|ENTITY)\\b", data, re.I), "DTD/entity declarations forbidden"
    root = ET.fromstring(data)
    assert root.tag == SVG_NS + "svg", "not an SVG root"
    for el in root.iter():
        bare = el.tag.rsplit("}", 1)[-1].lower()
        assert bare not in FORBIDDEN_SVG_TAGS, f"unsafe SVG element: {bare}"
        for key, value in el.attrib.items():
            attr = key.rsplit("}", 1)[-1].lower()
            assert not (attr.startswith("on") or attr.endswith("href")), f"unsafe SVG attribute: {attr}"
            assert not REMOTE_VALUE.search(value), f"unsafe external resource in {attr}"
            if re.search(r"url\\s*\\(", value, re.I):
                assert LOCAL_URL.fullmatch(value.strip()), f"nonlocal paint reference: {attr}"
        if bare == "style":
            style = el.text or ""
            assert not REMOTE_VALUE.search(style), "unsafe SVG CSS"
            assert not re.search(r"url\\s*\\(", style, re.I), "SVG CSS resource loading forbidden"
    return root


def validate(name: str) -> None:
    source = ROOT / NAME / "examples" / f"{name}.svg"
    packaged = ROOT / "plugins" / NAME / "skills" / NAME / "examples" / f"{name}.svg"
    data = source.read_bytes()
    assert data == packaged.read_bytes(), f"{name}: source and packaged SVG differ"
    root = parse_safe_svg(data)
    assert root.attrib.get("role") == "img", f"{name}: role missing"
    assert root.attrib.get("aria-labelledby") == "viz-title viz-desc", f"{name}: accessibility labeling missing"
    assert root.attrib.get("data-example") == name, f"{name}: wrong example"
    assert len(root.attrib.get("viewBox", "").split()) == 4, f"{name}: invalid viewBox"
    titles = root.findall(SVG_NS + "title")
    descriptions = root.findall(SVG_NS + "desc")
    assert len(titles) == len(descriptions) == 1, f"{name}: title/description absent"
    assert (titles[0].text or "").strip() and (descriptions[0].text or "").strip(), f"{name}: empty description"
    style = root.find(SVG_NS + "style")
    assert style is not None and "prefers-color-scheme:dark" in (style.text or ""), f"{name}: dark theme missing"
    if name == "heap-tree-array":
        nodes = root.findall(f".//{SVG_NS}circle")
        arrays = [el for el in root.iter() if "data-array-index" in el.attrib]
        nodes_by_index = {int(n.attrib["data-index"]): int(n.attrib["data-value"]) for n in nodes}
        array_by_index = {int(a.attrib["data-array-index"]): int(a.attrib["data-value"]) for a in arrays}
        assert nodes_by_index == array_by_index == dict(enumerate((2, 4, 7, 9, 8, 11, 13))), "heap mapping changed"
        for i in range(1, len(nodes_by_index)):
            assert nodes_by_index[(i - 1) // 2] <= nodes_by_index[i], "min heap invariant failed"
    elif name == "java-pass-by-value":
        links = [el.attrib["data-reference"] for el in root.iter() if "data-reference" in el.attrib]
        assert links == ["member:A", "param:A", "member:A", "param:B"], "caller/parameter references changed"
        objects_a = [el for el in root.iter() if el.attrib.get("data-java-object") == "A"]
        objects_b = [el for el in root.iter() if el.attrib.get("data-java-object") == "B"]
        assert len(objects_a) == 2 and len(objects_b) == 1, "object identity annotations changed"
        assert objects_a[0].attrib["y"] == objects_a[1].attrib["y"], "unchanged object A moved vertically"
        assert int(objects_a[1].attrib["x"]) - int(objects_a[0].attrib["x"]) == 460, "unchanged object A moved relative to panel"
    elif name == "tcp-sliding-window":
        windows = [el.attrib["data-window"] for el in root.iter() if "data-window" in el.attrib]
        assert windows == ["1000-1399", "1200-1599"], "TCP sender window positions changed"
        slots = [(int(el.attrib["data-byte-start"]), el.attrib["data-state"])
                 for el in root.iter() if "data-byte-start" in el.attrib]
        starts = [1000, 1100, 1200, 1300, 1400, 1500]
        assert slots[:6] == list(zip(starts, ["sent"] * 4 + ["available"] * 2)), "TCP initial state changed"
        assert slots[6:] == list(zip(starts, ["acked"] * 2 + ["sent"] * 2 + ["available"] * 2)), "TCP post-ACK state changed"
    print("PASS:", name)


def main() -> int:
    for name in CASES:
        validate(name)
    source_gallery = ROOT / NAME / "examples/index.html"
    packaged_gallery = ROOT / "plugins" / NAME / "skills" / NAME / "examples/index.html"
    gallery = source_gallery.read_bytes()
    assert gallery == packaged_gallery.read_bytes(), "gallery out of sync"
    assert len(gallery) <= 32_000, "oversized gallery HTML"
    assert not re.search(rb"<\\s*(?:script|iframe|object|embed|base|link)\\b", gallery, re.I), "active gallery content"
    assert not re.search(rb"\\bon[a-z]+\\s*=", gallery, re.I), "gallery event-handler attribute"
    assert not re.search(rb"(?:https?://|file:|javascript:|data:|@import|@font-face|url\\s*\\()", gallery, re.I), "gallery resource-loading content"
    print("PASS: 3 SVG fixtures and gallery")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
