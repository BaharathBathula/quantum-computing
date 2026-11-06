"""Reference solution for exercise 1."""

from __future__ import annotations

import numpy as np


def amplitudes(theta: float, phi: float) -> tuple[complex, complex]:
    return complex(np.cos(theta / 2)), complex(np.exp(1j * phi) * np.sin(theta / 2))


def bloch_vector(alpha: complex, beta: complex) -> np.ndarray:
    cross = np.conj(alpha) * beta
    return np.array([2 * cross.real, 2 * cross.imag, abs(alpha) ** 2 - abs(beta) ** 2])


def measure_many(alpha: complex, beta: complex, shots: int, seed: int = 0) -> dict[str, int]:
    p1 = abs(beta) ** 2
    ones = int(np.sum(np.random.default_rng(seed).random(shots) < p1))
    return {"0": shots - ones, "1": ones}
