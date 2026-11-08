"""Static validation for the three self-authored educational SVG fixtures.

This validates metadata and encoded example states, NOT visual layout or semantics
beyond these particular examples. No external dependencies required.
"""
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
NAME = "cs-learning-visualization"
SVG_NS = "{http://www.w3.org/2000/svg}"
CASES = ("heap-tree-array", "java-pass-by-value", "tcp-sliding-window")


def validate(name: str) -> None:
    source = ROOT / NAME / "examples" / f"{name}.svg"
    packaged = ROOT / "plugins" / NAME / "skills" / NAME / "examples" / f"{name}.svg"
    data = source.read_bytes()
    assert data == packaged.read_bytes(), f"{name}: source and packaged SVG differ"
    root = ET.fromstring(data)
    assert root.tag == SVG_NS + "svg", f"{name}: not SVG"
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
    unsafe_tags = {"script", "foreignObject", "image", "iframe", "animate"}
    for el in root.iter():
        bare = el.tag.rsplit("}", 1)[-1]
        assert bare not in unsafe_tags, f"{name}: disallowed tag {bare}"
        assert all(not k.endswith("href") for k in el.attrib), f"{name}: external references forbidden"

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
    assert source_gallery.read_bytes() == packaged_gallery.read_bytes(), "gallery out of sync"
    print("PASS: 3 SVG fixtures and gallery")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
