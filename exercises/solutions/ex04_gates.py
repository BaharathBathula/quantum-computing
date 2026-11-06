"""Reference solution for exercise 4."""

from __future__ import annotations

import numpy as np

_S2 = 1 / np.sqrt(2)
_GATES = {
    "I": np.eye(2, dtype=complex),
    "X": np.array([[0, 1], [1, 0]], dtype=complex),
    "Y": np.array([[0, -1j], [1j, 0]], dtype=complex),
    "Z": np.array([[1, 0], [0, -1]], dtype=complex),
    "H": _S2 * np.array([[1, 1], [1, -1]], dtype=complex),
    "S": np.array([[1, 0], [0, 1j]], dtype=complex),
    "T": np.array([[1, 0], [0, np.exp(1j * np.pi / 4)]], dtype=complex),
}


def gate_matrix(name: str) -> np.ndarray:
    return _GATES[name.upper()].copy()


def is_unitary(m: np.ndarray, tol: float = 1e-9) -> bool:
    m = np.asarray(m, dtype=complex)
    return m.shape[0] == m.shape[1] and bool(np.allclose(m.conj().T @ m, np.eye(m.shape[0]), atol=tol))


def controlled(u: np.ndarray) -> np.ndarray:
    # Basis order |q1 q0>: index 0=|00>, 1=|01>, 2=|10>, 3=|11>. Control q0 is set in indices 1 and 3.
    out = np.eye(4, dtype=complex)
    u = np.asarray(u, dtype=complex)
    out[1, 1], out[1, 3] = u[0, 0], u[0, 1]
    out[3, 1], out[3, 3] = u[1, 0], u[1, 1]
    return out


def equal_up_to_global_phase(a: np.ndarray, b: np.ndarray, tol: float = 1e-9) -> bool:
    a, b = np.asarray(a, dtype=complex), np.asarray(b, dtype=complex)
    if a.shape != b.shape:
        return False
    idx = np.unravel_index(np.argmax(np.abs(b)), b.shape)
    if abs(b[idx]) < tol:
        return bool(np.allclose(a, b, atol=tol))
    phase = a[idx] / b[idx]
    return abs(abs(phase) - 1) < 1e-6 and bool(np.allclose(a, phase * b, atol=tol))
