"""
`qlab` command-line entry point (installed by `pip install -e .`).

    qlab run            run all 9 concepts and save figures to outputs/
    qlab run 3 5 8      run a subset
    qlab test           run the project's own test-suite
    qlab grade          grade the take-home exercises in exercises/
    qlab lab            print the path of the interactive Quantum Lab page
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    cmd, rest = (args[0], args[1:]) if args else ("help", [])
    if cmd == "run":
        return subprocess.call([sys.executable, str(ROOT / "run_all.py"), *rest], cwd=ROOT)
    if cmd == "test":
        return subprocess.call([sys.executable, "-m", "pytest", *rest], cwd=ROOT)
    if cmd == "grade":
        return subprocess.call([sys.executable, str(ROOT / "grade.py"), *rest], cwd=ROOT)
    if cmd == "lab":
        print(ROOT / "web" / "quantum-lab.html")
        return 0
    print(__doc__.strip())
    return 0 if cmd in ("help", "-h", "--help") else 2


if __name__ == "__main__":
    sys.exit(main())
