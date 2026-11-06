"""Reference solution for exercise 9."""

from __future__ import annotations

import math


def statevector_bytes(n: int) -> int:
    return 16 * (1 << n)


def max_qubits_in(memory_bytes: int) -> int:
    n = 0
    while statevector_bytes(n + 1) <= memory_bytes:
        n += 1
    return n


def xeb_fidelity(samples: dict[str, int], ideal_probs: dict[str, float], n: int) -> float:
    total = sum(samples.values())
    mean_p = sum(ideal_probs.get(k, 0.0) * c for k, c in samples.items()) / total
    return (2**n) * mean_p - 1


def grover_speedup(N: int) -> float:
    return (N / 2) / max(1, math.floor(math.pi / 4 * math.sqrt(N)))
