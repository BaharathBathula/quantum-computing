"""Reference solution for exercise 5."""

from __future__ import annotations

import numpy as np
from qiskit import QuantumCircuit


def _mcz(qc: QuantumCircuit, n: int) -> None:
    """Multi-controlled Z on all n qubits (phase-flips |11..1>)."""
    if n == 1:
        qc.z(0)
        return
    qc.h(n - 1)
    qc.mcx(list(range(n - 1)), n - 1)
    qc.h(n - 1)


def oracle(n: int, marked: str) -> QuantumCircuit:
    qc = QuantumCircuit(n, name="oracle")
    zeros = [q for q, bit in enumerate(reversed(marked)) if bit == "0"]
    if zeros:
        qc.x(zeros)
    _mcz(qc, n)
    if zeros:
        qc.x(zeros)
    return qc


def diffuser(n: int) -> QuantumCircuit:
    qc = QuantumCircuit(n, name="diffuser")
    qc.h(range(n))
    qc.x(range(n))
    _mcz(qc, n)
    qc.x(range(n))
    qc.h(range(n))
    return qc


def optimal_iterations(n: int) -> int:
    return max(1, int(np.floor(np.pi / 4 * np.sqrt(2**n))))


def grover(n: int, marked: str, iterations: int | None = None) -> QuantumCircuit:
    k = optimal_iterations(n) if iterations is None else iterations
    qc = QuantumCircuit(n, n)
    qc.h(range(n))
    for _ in range(k):
        qc.compose(oracle(n, marked), inplace=True)
        qc.compose(diffuser(n), inplace=True)
    qc.measure(range(n), range(n))
    return qc
