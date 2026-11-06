"""Pick the candidate's exercise module, or the reference solution when QLAB_SOLUTIONS=1."""

from __future__ import annotations

import importlib
import os


def load(name: str):
    """`load("ex05_algorithms")` -> module. Set QLAB_SOLUTIONS=1 to grade the solutions."""
    package = "exercises.solutions" if os.environ.get("QLAB_SOLUTIONS") == "1" else "exercises"
    return importlib.import_module(f"{package}.{name}")
