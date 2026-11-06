"""
Shared execution helpers so every concept module runs circuits the same way.

Qiskit 2.x note: `from qiskit import Aer, execute` (used throughout the
infographic) was removed in Qiskit 1.0. The modern pattern is:

    sim = AerSimulator()
    counts = sim.run(transpile(qc, sim), shots=1024).result().get_counts()
"""

from __future__ import annotations

import contextlib
import itertools
from functools import lru_cache

from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

SEED = 1234  # fixed base seed -> every run of the project prints the same numbers
_calls = itertools.count()  # each run gets its own (still reproducible) seed


def simulator(noise_model=None, seed: int = SEED) -> AerSimulator:
    return AerSimulator(noise_model=noise_model, seed_simulator=seed)


def run_counts(
    qc: QuantumCircuit,
    shots: int = 1024,
    *,
    noise_model=None,
    backend=None,
    seed: int | None = None,
    optimization_level: int = 0,
) -> dict[str, int]:
    """Run a circuit and return measurement counts.

    optimization_level=0 by default: run *exactly* the circuit you wrote.
    (Higher levels would, for example, cancel H·H before it ever runs, which
    hides the very interference effect some demos are about.)
    """
    seed = SEED + next(_calls) if seed is None else seed
    sim = backend if backend is not None else simulator(noise_model, seed)
    if backend is not None:
        with contextlib.suppress(Exception):  # non-Aer backends have no such option
            sim.set_options(seed_simulator=seed)
    tqc = transpile(qc, sim, optimization_level=optimization_level, seed_transpiler=seed)
    return sim.run(tqc, shots=shots).result().get_counts()


def probability(counts: dict[str, int], outcome: str) -> float:
    total = sum(counts.values())
    return counts.get(outcome, 0) / total if total else 0.0


def bit_probability(counts: dict[str, int], bit: int, value: str = "1") -> float:
    """P(classical bit `bit` == value). Bit 0 is the rightmost character."""
    total = sum(counts.values())
    hit = sum(c for k, c in counts.items() if k.replace(" ", "")[::-1][bit] == value)
    return hit / total if total else 0.0


@lru_cache(maxsize=1)
def fake_device():
    """A snapshot of a real IBM Heron device (156 qubits) with its calibrated
    noise: gate errors, readout errors, T1/T2. Runs locally — no account needed."""
    from qiskit_ibm_runtime.fake_provider import FakeFez

    return FakeFez()


@lru_cache(maxsize=1)
def noisy_device_simulator():
    return AerSimulator.from_backend(fake_device(), seed_simulator=SEED)


def run_on_device_model(
    qc: QuantumCircuit, shots: int = 2000, optimization_level: int = 1
) -> tuple[dict[str, int], QuantumCircuit]:
    """Compile for the real chip's native gates + wiring, then simulate with its noise."""
    sim = noisy_device_simulator()
    tqc = transpile(qc, sim, optimization_level=optimization_level, seed_transpiler=SEED)
    return sim.run(tqc, shots=shots).result().get_counts(), tqc


def header(number: int, title: str, tagline: str) -> None:
    line = "=" * 72
    print(f"\n{line}\n  {number}. {title.upper()}\n  {tagline}\n{line}")


def section(title: str) -> None:
    print(f"\n--- {title} " + "-" * max(0, 66 - len(title)))


def fmt_counts(counts: dict[str, int], top: int = 8) -> str:
    items = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:top]
    return "  ".join(f"{k}: {v}" for k, v in items)
