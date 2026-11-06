"""
Exercise 1 · Qubits                                         difficulty ★   ~20 min

A qubit state is |ψ⟩ = α|0⟩ + β|1⟩. Up to a global phase it can always be written
    |ψ⟩ = cos(θ/2)|0⟩ + e^{iφ} sin(θ/2)|1⟩
which is the point (θ, φ) on the Bloch sphere.

Implement the three functions below using only `numpy` (no Qiskit needed).

Hints
- `np.exp(1j * phi)` is e^{iφ}.
- Bloch coordinates: x = 2 Re(α* β), y = 2 Im(α* β), z = |α|² − |β|².
- A measurement in the Z basis gives 1 with probability |β|².

The autograder compares you against Qiskit's `Statevector`, so the global phase
convention matters: keep α real and non-negative.
"""

from __future__ import annotations

import numpy as np


def amplitudes(theta: float, phi: float) -> tuple[complex, complex]:
    """Return (alpha, beta) for the Bloch-sphere point (theta, phi), with alpha real >= 0."""
    raise NotImplementedError


def bloch_vector(alpha: complex, beta: complex) -> np.ndarray:
    """Return the unit vector (x, y, z) on the Bloch sphere for the state alpha|0> + beta|1>."""
    raise NotImplementedError


def measure_many(alpha: complex, beta: complex, shots: int, seed: int = 0) -> dict[str, int]:
    """Simulate `shots` independent Z-basis measurements of fresh copies of the state.

    Return counts like {"0": 237, "1": 763}. Use `np.random.default_rng(seed)` so the
    grader can check the distribution (it allows statistical slack).
    """
    raise NotImplementedError
