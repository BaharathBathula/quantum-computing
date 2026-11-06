"""Reference solution for exercise 3."""

from __future__ import annotations

import numpy as np
from qiskit import QuantumCircuit


def bell_state(kind: str) -> QuantumCircuit:
    qc = QuantumCircuit(2)
    if kind in ("psi+", "psi-"):
        qc.x(1)
    if kind in ("phi-", "psi-"):
        qc.x(0)
    qc.h(0)
    qc.cx(0, 1)
    return qc


def chsh_circuit(alice_angle: float, bob_angle: float) -> QuantumCircuit:
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.ry(-alice_angle, 0)
    qc.ry(-bob_angle, 1)
    qc.measure([0, 1], [0, 1])
    return qc


def correlation(counts: dict[str, int]) -> float:
    total = sum(counts.values())
    same = sum(c for k, c in counts.items() if k[0] == k[1])
    return (2 * same - total) / total


def chsh_angles() -> dict[str, float]:
    return {"a": 0.0, "a'": np.pi / 2, "b": np.pi / 4, "b'": -np.pi / 4}


def chsh_value(E: dict[tuple[str, str], float]) -> float:
    return E[("a", "b")] + E[("a", "b'")] + E[("a'", "b")] - E[("a'", "b'")]
