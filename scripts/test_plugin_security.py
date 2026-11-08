"""Negative security tests: fixtures cannot execute code, load remote resources or escape the repo."""
from pathlib import Path
from tempfile import TemporaryDirectory

from check_learning_visuals import parse_safe_svg
from package_plugins import has_symlink_component

SVG_HEADER = '<svg xmlns="http://www.w3.org/2000/svg">'
ATTACK_SAMPLES = (
    '<svg xmlns="http://www.w3.org/2000/svg" onload="alert(1)"/>',
    SVG_HEADER + '<script>alert(1)</script></svg>',
    SVG_HEADER + '<foreignObject /></svg>',
    SVG_HEADER + '<image href="https://attacker.invalid/pixel" /></svg>',
    SVG_HEADER + '<rect fill="url(https://attacker.invalid/a.svg)" /></svg>',
    SVG_HEADER + '<style>@import url(https://attacker.invalid/a.css)</style></svg>',
    SVG_HEADER + '<rect style="background:url(data:text/html,abc)" /></svg>',
    '<!DOCTYPE svg [<!ENTITY x "evil">]>' + SVG_HEADER + '</svg>',
)


def main() -> None:
    parse_safe_svg((SVG_HEADER + '<rect fill="url(#local)" /></svg>').encode())
    for example in ATTACK_SAMPLES:
        try:
            parse_safe_svg(example.encode())
        except AssertionError:
            pass
        else:
            raise AssertionError("malicious SVG was accepted: " + example[:120])

    with TemporaryDirectory() as temporary:
        root = Path(temporary)
        safe = root / "safe"
        safe.mkdir()
        assert not has_symlink_component(safe / "any.svg", root)
        assert has_symlink_component(root.parent / "outside.svg", root)
        assert has_symlink_component(root / "safe" / ".." / "file.svg", root)
        other = root / "other"
        other.mkdir()
        link = safe / "linked"
        try:
            link.symlink_to(other, target_is_directory=True)
        except (OSError, NotImplementedError):
            print("SKIP: symlink creation is not available on this host")
        else:
            assert has_symlink_component(link / "output.svg", root), "symlink parent was not blocked"
    print("PASS: SVG security reject-list and plugin packaging traversal checks")


if __name__ == "__main__":
    main()
