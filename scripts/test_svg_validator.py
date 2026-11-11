"""Exercise arbitrary SVG CLI inputs and reject invalid accessibility/geometry."""
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / 'cs-learning-visualization/scripts/validate_svg.py'
VALID = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" role="img" aria-labelledby="t d"><title id="t">Title</title><desc id="d">Description</desc><rect width="10" height="10"/></svg>'

def main():
    with TemporaryDirectory() as directory:
        root = Path(directory)
        cases = [VALID, VALID.replace('100 100', '-1 100'), VALID.replace('100 100', 'nan 100'), VALID.replace('t d', 't missing'), VALID.replace('id="d"', 'id="t"'), VALID.replace('<rect', '<rect onload="evil()"'), VALID.replace('<rect width="10" height="10"/>', '<script/>')]
        for i, content in enumerate(cases):
            path = root / f'case-{i}.svg'
            path.write_text(content)
            result = subprocess.run([sys.executable, str(VALIDATOR), str(path)], capture_output=True, text=True)
            assert result.returncode == (0 if i == 0 else 1), (i, result.stdout, result.stderr)
        result = subprocess.run([sys.executable, str(VALIDATOR), str(root / 'missing.svg')], capture_output=True)
        assert result.returncode == 1
        result = subprocess.run([sys.executable, str(VALIDATOR), str(root / 'case-0.svg'), str(root / 'case-1.svg')], capture_output=True)
        assert result.returncode == 1
    print('PASS: arbitrary SVG CLI (valid, six invalid, missing, mixed batch)')

if __name__ == '__main__':
    main()
