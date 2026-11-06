"""
Exercise 2 · Superposition and interference                 difficulty ★   ~20 min

Two states can give identical measurement statistics in one basis and opposite
statistics in another. That is the whole difference between a superposition and
classical uncertainty.

Implement:

1. `plus_minus_circuit(minus, basis)` - prepare |+⟩ (or |−⟩ when `minus` is True) and
   measure it in the given basis ('Z' or 'X'). Measuring in the X basis means rotating
   the X axis onto Z with a Hadamard before the Z measurement.

2. `interference_circuit()` - a ONE-qubit circuit that uses at least one Hadamard,
   never uses an X gate, and always measures 1. (Think about which gate turns the
   relative sign of |+⟩ into something a Z measurement can see.)

3. `distinguish(counts_z, counts_x)` - given counts from measuring an unknown
   |+⟩ or |−⟩ in Z and in X, return "+" or "-". Only one of the two dictionaries
   carries any information; figure out which.

Hints
- `qc.h(0)` then `qc.measure(0, 0)` measures in the X basis.
- H Z H = X.
"""

from __future__ import annotations

from qiskit import QuantumCircuit


def plus_minus_circuit(minus: bool, basis: str) -> QuantumCircuit:
    """1 qubit, 1 classical bit. Prepare |+> (or |-> if `minus`) and measure in `basis` ('Z' | 'X')."""
    raise NotImplementedError


def interference_circuit() -> QuantumCircuit:
    """1 qubit, 1 classical bit; contains an H gate, contains no X gate, measures 1 with certainty."""
    raise NotImplementedError


def distinguish(counts_z: dict[str, int], counts_x: dict[str, int]) -> str:
    """Return '+' if the unknown state was |+>, '-' if it was |->."""
    raise NotImplementedError
