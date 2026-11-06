"""
Exercise 5 · Grover's search from scratch                   difficulty ★★★ ~90 min

Build Grover's algorithm for any number of qubits n and any marked bitstring,
without using Qiskit's ready-made `GroverOperator` or `PhaseOracle`.

1. `oracle(n, marked)` - a circuit on n qubits that multiplies the amplitude of
   |marked> by −1 and leaves every other basis state alone. `marked` is a string
   like "101" in Qiskit order (rightmost character = qubit 0).
2. `diffuser(n)` - the "inversion about the mean" operator 2|s><s| − I, where |s>
   is the uniform superposition.
3. `optimal_iterations(n)` - floor(π/4 · √(2^n)), at least 1.
4. `grover(n, marked, iterations=None)` - the full circuit WITH measurements, using
   the optimal number of iterations when none is given.

The grader checks the oracle and diffuser as matrices (so no shortcuts via
`initialize`), then runs your circuit and expects P(marked) > 0.9 for n = 3..6.

Hints
- A multi-controlled Z is H on the target, multi-controlled X (`qc.mcx`), H on the target.
- To mark a state with 0s in it, surround the multi-controlled Z with X gates on those qubits.
- The diffuser is H^⊗n, then "flip the phase of |00..0>", then H^⊗n. Flipping the phase
  of |00..0> is X^⊗n, multi-controlled Z, X^⊗n. The overall sign does not matter.
"""

from __future__ import annotations

from qiskit import QuantumCircuit


def oracle(n: int, marked: str) -> QuantumCircuit:
    raise NotImplementedError


def diffuser(n: int) -> QuantumCircuit:
    raise NotImplementedError


def optimal_iterations(n: int) -> int:
    raise NotImplementedError


def grover(n: int, marked: str, iterations: int | None = None) -> QuantumCircuit:
    """n qubits + n classical bits, measured at the end."""
    raise NotImplementedError
