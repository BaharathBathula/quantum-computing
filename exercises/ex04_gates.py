"""
Exercise 4 · Gates as matrices                              difficulty ★   ~25 min

Work directly with 2×2 and 4×4 NumPy matrices.

1. `gate_matrix(name)` - return the matrix for 'I', 'X', 'Y', 'Z', 'H', 'S', 'T'.
2. `is_unitary(m)` - True when m† m = I (within floating-point tolerance).
3. `controlled(u)` - the 4×4 matrix of "apply u to the target when the control is |1>".
   Use Qiskit's ordering: the CONTROL is qubit 0 (the least-significant bit), so basis
   order is |q1 q0> = |00>, |01>, |10>, |11> and the control is set in |01> and |11>.
4. `equal_up_to_global_phase(a, b)` - True when a = e^{iφ} b for some φ.

Hints
- controlled(X) must equal Qiskit's `Operator(CXGate()).data`.
- For global phase: find the largest entry of b, compute the phase ratio, and compare.
"""

from __future__ import annotations

import numpy as np


def gate_matrix(name: str) -> np.ndarray:
    """2x2 complex matrix for one of I, X, Y, Z, H, S, T."""
    raise NotImplementedError


def is_unitary(m: np.ndarray, tol: float = 1e-9) -> bool:
    raise NotImplementedError


def controlled(u: np.ndarray) -> np.ndarray:
    """4x4 matrix: control = qubit 0 (LSB), target = qubit 1."""
    raise NotImplementedError


def equal_up_to_global_phase(a: np.ndarray, b: np.ndarray, tol: float = 1e-9) -> bool:
    raise NotImplementedError
