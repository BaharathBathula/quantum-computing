"""Reference solution for exercise 8."""

from __future__ import annotations

from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister


def decode_syndrome(s01: int, s12: int) -> int | None:
    return {(0, 0): None, (1, 0): 0, (1, 1): 1, (0, 1): 2}[(s01, s12)]


def bit_flip_code(theta: float, error_on: int | None) -> QuantumCircuit:
    d, a = QuantumRegister(3, "d"), QuantumRegister(2, "a")
    syn, out = ClassicalRegister(2, "syn"), ClassicalRegister(1, "out")
    qc = QuantumCircuit(d, a, syn, out)

    qc.ry(theta, d[0])
    qc.cx(d[0], d[1])
    qc.cx(d[0], d[2])
    qc.barrier()
    if error_on is not None:
        qc.x(d[error_on])
    qc.barrier()
    qc.cx(d[0], a[0])
    qc.cx(d[1], a[0])  # a0 = parity(d0, d1)
    qc.cx(d[1], a[1])
    qc.cx(d[2], a[1])  # a1 = parity(d1, d2)
    qc.measure(a, syn)
    with qc.if_test((syn, 0b01)):  # s01=1, s12=0 -> d0
        qc.x(d[0])
    with qc.if_test((syn, 0b11)):  # both -> d1
        qc.x(d[1])
    with qc.if_test((syn, 0b10)):  # s12 only -> d2
        qc.x(d[2])
    qc.cx(d[0], d[2])
    qc.cx(d[0], d[1])
    qc.ry(-theta, d[0])
    qc.measure(d[0], out[0])
    return qc


def logical_error_rate(counts: dict[str, int]) -> float:
    total = sum(counts.values())
    return sum(c for k, c in counts.items() if k.split()[0] == "1") / total if total else 0.0
