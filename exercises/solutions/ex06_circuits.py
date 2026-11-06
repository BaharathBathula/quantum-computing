"""Reference solution for exercise 6."""

from __future__ import annotations

from qiskit import QuantumCircuit


def depth(ops: list[tuple[int, ...]]) -> int:
    level: dict[int, int] = {}
    for op in ops:
        layer = max((level.get(q, 0) for q in op), default=0) + 1
        for q in op:
            level[q] = layer
    return max(level.values(), default=0)


def ghz_for_line(n: int) -> QuantumCircuit:
    qc = QuantumCircuit(n)
    qc.h(0)
    for q in range(n - 1):
        qc.cx(q, q + 1)
    return qc


def count_two_qubit_gates(qc: QuantumCircuit) -> int:
    return sum(
        1 for inst in qc.data if len(inst.qubits) >= 2 and inst.operation.name not in ("barrier", "measure")
    )
