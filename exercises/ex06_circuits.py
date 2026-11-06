"""
Exercise 6 · Circuits, depth and hardware wiring            difficulty ★★  ~45 min

1. `depth(ops)` - compute the depth of a circuit given as a list of operations, each a
   tuple of the qubit indices it touches, e.g. [(0,), (0, 1), (2,), (1, 2)]. Depth is
   the length of the longest chain of operations that must run one after another
   (two operations on disjoint qubits can run in the same layer). Do NOT use Qiskit.

2. `ghz_for_line(n)` - a circuit preparing the n-qubit GHZ state (|0..0> + |1..1>)/√2
   using ONLY CNOTs between neighbouring qubits (i, i+1). The grader transpiles your
   circuit for a linear chain and checks it needs exactly n − 1 two-qubit gates: a
   fan-out design (all CNOTs from qubit 0) would need SWAPs and fail.

3. `count_two_qubit_gates(qc)` - the number of operations acting on 2 or more qubits.
   (Measurements and barriers don't count. Hint: `qc.data`, `instruction.qubits`.)

Hints
- For depth, keep an array `level[q]` = number of layers qubit q is already busy for.
"""

from __future__ import annotations

from qiskit import QuantumCircuit


def depth(ops: list[tuple[int, ...]]) -> int:
    raise NotImplementedError


def ghz_for_line(n: int) -> QuantumCircuit:
    """n qubits, no measurements, only nearest-neighbour CNOTs."""
    raise NotImplementedError


def count_two_qubit_gates(qc: QuantumCircuit) -> int:
    raise NotImplementedError
