"""
Scorecard for the take-home exercises.

    python grade.py                 # grade exercises/ (your implementations)
    python grade.py --solutions     # grade the reference solutions (should be 9/9)
    python grade.py 5 8             # only exercises 5 and 8

Each exercise is scored by the fraction of its autograder tests that pass.
"""

from __future__ import annotations

import os
import sys
from collections import defaultdict
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent
TITLES = {
    1: ("Qubits", "★"),
    2: ("Superposition & interference", "★"),
    3: ("Entanglement & CHSH", "★★"),
    4: ("Gates as matrices", "★"),
    5: ("Grover from scratch", "★★★"),
    6: ("Circuits, depth, wiring", "★★"),
    7: ("Noise, T1, error budget", "★★"),
    8: ("Bit-flip code", "★★"),
    9: ("Measuring advantage", "★★"),
}


class Collector:
    def __init__(self) -> None:
        self.passed: dict[int, int] = defaultdict(int)
        self.total: dict[int, int] = defaultdict(int)
        self.failures: dict[int, list[str]] = defaultdict(list)

    def pytest_runtest_logreport(self, report):
        if report.when != "call" and not (report.when == "setup" and report.failed):
            return
        name = Path(str(report.fspath)).stem  # test_ex05
        n = int(name.replace("test_ex", ""))
        self.total[n] += 1
        if report.passed:
            self.passed[n] += 1
        else:
            self.failures[n].append(report.nodeid.split("::", 1)[1])


def main(argv: list[str]) -> int:
    if "--solutions" in argv:
        os.environ["QLAB_SOLUTIONS"] = "1"
    picks = [int(a) for a in argv if a.isdigit()] or list(TITLES)
    files = [str(ROOT / "tests" / "takehome" / f"test_ex{n:02d}.py") for n in picks]
    col = Collector()
    pytest.main(
        ["-q", "-p", "no:cacheprovider", "-m", "exercises", "--no-header", "-o", "addopts=", *files],
        plugins=[col],
    )

    label = "reference solutions" if os.environ.get("QLAB_SOLUTIONS") == "1" else "exercises/"
    print(f"\n{'=' * 64}\n  SCORECARD  ({label})\n{'=' * 64}")
    score = 0.0
    for n in picks:
        title, stars = TITLES[n]
        p, t = col.passed[n], col.total[n]
        frac = p / t if t else 0.0
        score += frac
        bar = "█" * round(frac * 20) + "·" * (20 - round(frac * 20))
        print(f"  {n}. {title:30s} {stars:4s} {bar} {p:2d}/{t:<2d}")
        for f in col.failures[n][:3]:
            print(f"       ✗ {f}")
        if len(col.failures[n]) > 3:
            print(f"       … and {len(col.failures[n]) - 3} more")
    print(f"\n  Total: {score:.1f} / {len(picks)} exercises\n")
    return 0 if score == len(picks) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
