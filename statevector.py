"""
A from-scratch statevector simulator in ~100 lines of NumPy.

Why this exists: Qiskit hides the linear algebra. This file shows that a
quantum simulator is "just" a vector of 2**n complex numbers and a way to
multiply small matrices into it. The tests check it against Qiskit gate by
gate, so you can trust it as a reference.

Bit ordering matches Qiskit (little-endian): qubit 0 is the RIGHTMOST
character of a bitstring, so the state |q2 q1 q0>.
"""

from __future__ import annotations

import numpy as np

SQ2 = 1 / np.sqrt(2)

GATES: dict[str, np.ndarray] = {
    "I": np.eye(2, dtype=complex),
    "X": np.array([[0, 1], [1, 0]], dtype=complex),
    "Y": np.array([[0, -1j], [1j, 0]], dtype=complex),
    "Z": np.array([[1, 0], [0, -1]], dtype=complex),
    "H": SQ2 * np.array([[1, 1], [1, -1]], dtype=complex),
    "S": np.array([[1, 0], [0, 1j]], dtype=complex),
    "T": np.array([[1, 0], [0, np.exp(1j * np.pi / 4)]], dtype=complex),
}


def rx(theta: float) -> np.ndarray:
    c, s = np.cos(theta / 2), np.sin(theta / 2)
    return np.array([[c, -1j * s], [-1j * s, c]], dtype=complex)


def ry(theta: float) -> np.ndarray:
    c, s = np.cos(theta / 2), np.sin(theta / 2)
    return np.array([[c, -s], [s, c]], dtype=complex)


def rz(theta: float) -> np.ndarray:
    return np.array([[np.exp(-1j * theta / 2), 0], [0, np.exp(1j * theta / 2)]], dtype=complex)


class StateVector:
    """n-qubit pure state, starting in |00...0>."""

    def __init__(self, n_qubits: int, seed: int | None = None):
        if n_qubits < 1:
            raise ValueError("need at least one qubit")
        self.n = n_qubits
        self.amps = np.zeros(2**n_qubits, dtype=complex)
        self.amps[0] = 1.0
        self.rng = np.random.default_rng(seed)

    # ---- core trick: view the 2**n vector as an n-dimensional 2x2x...x2 tensor
    def _axis(self, qubit: int) -> int:
        # tensor axis 0 is the most significant qubit (n-1); qubit q lives on axis n-1-q
        return self.n - 1 - qubit

    def apply(self, gate: np.ndarray, target: int) -> StateVector:
        """Apply a 2x2 unitary to one qubit."""
        psi = self.amps.reshape([2] * self.n)
        ax = self._axis(target)
        psi = np.tensordot(gate, psi, axes=([1], [ax]))  # contracted axis moves to front
        psi = np.moveaxis(psi, 0, ax)
        self.amps = psi.reshape(-1)
        return self

    def controlled(self, gate: np.ndarray, control: int, target: int) -> StateVector:
        """Apply `gate` to `target` only in the branch where `control` is |1>."""
        if control == target:
            raise ValueError("control and target must differ")
        psi = self.amps.reshape([2] * self.n).copy()
        idx = [slice(None)] * self.n
        idx[self._axis(control)] = 1
        branch = psi[tuple(idx)]  # sub-tensor where control == 1 (one fewer axis)
        t_ax = self._axis(target) - (1 if self._axis(target) > self._axis(control) else 0)
        branch = np.moveaxis(np.tensordot(gate, branch, axes=([1], [t_ax])), 0, t_ax)
        psi[tuple(idx)] = branch
        self.amps = psi.reshape(-1)
        return self

    # convenience wrappers
    def h(self, q):
        return self.apply(GATES["H"], q)

    def x(self, q):
        return self.apply(GATES["X"], q)

    def y(self, q):
        return self.apply(GATES["Y"], q)

    def z(self, q):
        return self.apply(GATES["Z"], q)

    def s(self, q):
        return self.apply(GATES["S"], q)

    def t(self, q):
        return self.apply(GATES["T"], q)

    def cx(self, c, t):
        return self.controlled(GATES["X"], c, t)

    def cz(self, c, t):
        return self.controlled(GATES["Z"], c, t)

    # ---- reading the state out
    def probabilities(self) -> np.ndarray:
        return np.abs(self.amps) ** 2

    def probabilities_dict(self, tol: float = 1e-12) -> dict[str, float]:
        p = self.probabilities()
        return {format(i, f"0{self.n}b"): float(v) for i, v in enumerate(p) if v > tol}

    def sample_counts(self, shots: int) -> dict[str, int]:
        """Measure `shots` fresh copies of the state (the state itself is untouched)."""
        outcomes = self.rng.choice(2**self.n, size=shots, p=self.probabilities())
        values, freq = np.unique(outcomes, return_counts=True)
        return {format(int(v), f"0{self.n}b"): int(f) for v, f in zip(values, freq)}

    def measure(self, qubit: int) -> int:
        """Projective measurement of one qubit: returns 0/1 and COLLAPSES the state."""
        psi = self.amps.reshape([2] * self.n)
        ax = self._axis(qubit)
        p1 = float(np.sum(np.abs(np.take(psi, 1, axis=ax)) ** 2))
        outcome = int(self.rng.random() < p1)
        mask = np.zeros(2)
        mask[outcome] = 1
        shape = [1] * self.n
        shape[ax] = 2
        psi = psi * mask.reshape(shape)
        self.amps = psi.reshape(-1) / np.sqrt(p1 if outcome else 1 - p1)
        return outcome

    def __repr__(self) -> str:
        terms = [
            f"({a.real:+.3f}{a.imag:+.3f}j)|{format(i, f'0{self.n}b')}>"
            for i, a in enumerate(self.amps)
            if abs(a) > 1e-9
        ]
        return " ".join(terms)
