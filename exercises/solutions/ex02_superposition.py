"""Reference solution for exercise 2."""

from __future__ import annotations

from qiskit import QuantumCircuit


def plus_minus_circuit(minus: bool, basis: str) -> QuantumCircuit:
    qc = QuantumCircuit(1, 1)
    if minus:
        qc.x(0)
    qc.h(0)
    if basis.upper() == "X":
        qc.h(0)
    qc.measure(0, 0)
    return qc


def interference_circuit() -> QuantumCircuit:
    qc = QuantumCircuit(1, 1)
    qc.h(0)
    qc.z(0)  # |+> -> |->
    qc.h(0)  # |-> -> |1>
    qc.measure(0, 0)
    return qc


def distinguish(counts_z: dict[str, int], counts_x: dict[str, int]) -> str:
    # Z counts are 50/50 for both states; only the X-basis counts carry information.
    return "+" if counts_x.get("0", 0) >= counts_x.get("1", 0) else "-"
