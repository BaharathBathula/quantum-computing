"""Reference solution for exercise 7."""

from __future__ import annotations

import math
from collections.abc import Sequence

import numpy as np


def t1_from_decay(times: Sequence[float], p_excited: Sequence[float]) -> float:
    t = np.asarray(times, dtype=float)
    p = np.asarray(p_excited, dtype=float)
    keep = p > 0
    slope, _ = np.polyfit(t[keep], np.log(p[keep]), 1)  # log p = -t / T1
    return float(-1 / slope)


def error_free_probability(gate_error: float, n_gates: int) -> float:
    return (1 - gate_error) ** n_gates


def max_gates_for_success(gate_error: float, target: float = 0.5) -> int:
    if gate_error <= 0:
        return 10**12  # effectively unlimited
    if gate_error >= 1:
        return 0
    # (1-e)^N >= target  <=>  N <= log(target) / log(1-e)   (both logs negative)
    n = math.floor(math.log(target) / math.log(1 - gate_error) + 1e-12)
    return max(0, n)


def ghz_fidelity(counts: dict[str, int], n: int) -> float:
    total = sum(counts.values())
    return (counts.get("0" * n, 0) + counts.get("1" * n, 0)) / total if total else 0.0
