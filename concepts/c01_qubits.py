"""
1. QUBITS — the basic unit of quantum information.

A qubit's state is |psi> = alpha|0> + beta|1>, with complex alpha, beta and
|alpha|^2 + |beta|^2 = 1. Measuring gives 0 with probability |alpha|^2 and 1
with probability |beta|^2 — and only ever ONE of them.

Any qubit state can be written (up to an unobservable global phase) as
    |psi> = cos(theta/2)|0> + e^{i*phi} sin(theta/2)|1>
which is a point on the Bloch sphere at polar angle theta, azimuth phi.

Run:  python -m concepts.c01_qubits
"""

from __future__ import annotations

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

from qlab import StateVector
from qlab.backend import bit_probability, fmt_counts, header, run_counts, section


def prepare(theta: float, phi: float = 0.0, measure: bool = False) -> QuantumCircuit:
    """Circuit that rotates |0> to the Bloch-sphere point (theta, phi)."""
    qc = QuantumCircuit(1, 1 if measure else 0)
    qc.ry(theta, 0)  # tilt away from the north pole
    qc.rz(phi, 0)  # spin around the vertical axis (adds relative phase)
    if measure:
        qc.measure(0, 0)
    return qc


def amplitudes(theta: float, phi: float = 0.0) -> tuple[complex, complex]:
    """(alpha, beta) with the global phase removed so alpha is real and >= 0."""
    a, b = Statevector(prepare(theta, phi)).data
    g = np.exp(-1j * np.angle(a)) if abs(a) > 1e-12 else 1.0
    return complex(a * g), complex(b * g)


def bloch_vector(alpha: complex, beta: complex) -> np.ndarray:
    """(x, y, z) on the Bloch sphere from amplitudes."""
    x = 2 * (np.conj(alpha) * beta).real
    y = 2 * (np.conj(alpha) * beta).imag
    z = abs(alpha) ** 2 - abs(beta) ** 2
    return np.array([x, y, z])


NAMED_STATES = {
    "|0>  (north pole)": (0.0, 0.0),
    "|1>  (south pole)": (np.pi, 0.0),
    "|+>  (equator, +x)": (np.pi / 2, 0.0),
    "|i>  (equator, +y)": (np.pi / 2, np.pi / 2),
    "tilted 120°": (2 * np.pi / 3, 0.0),
}


def run(save_plots: bool = True) -> dict:
    header(1, "Qubits", "The basic unit of quantum information")

    section("State, amplitudes, probabilities, Bloch vector")
    rows = {}
    for name, (theta, phi) in NAMED_STATES.items():
        a, b = amplitudes(theta, phi)
        vec = bloch_vector(a, b)
        p0, p1 = abs(a) ** 2, abs(b) ** 2
        rows[name] = {"alpha": a, "beta": b, "P0": p0, "P1": p1, "bloch": vec}
        print(
            f"{name:20s} alpha={a.real:+.3f}{a.imag:+.3f}j  beta={b.real:+.3f}{b.imag:+.3f}j  "
            f"P(0)={p0:.3f} P(1)={p1:.3f}  bloch=({vec[0]:+.2f},{vec[1]:+.2f},{vec[2]:+.2f})"
        )
        assert abs(p0 + p1 - 1) < 1e-12, "normalisation |alpha|^2+|beta|^2 must be 1"

    section("Measurement gives ONE bit, at random, with those probabilities")
    theta = 2 * np.pi / 3  # P(1) = sin^2(60°) = 0.75
    counts = run_counts(prepare(theta, measure=True), shots=4000)
    p1 = bit_probability(counts, 0)
    print(f"tilted 120° state, 4000 shots -> {fmt_counts(counts)}   P(1)≈{p1:.3f} (theory 0.750)")

    section("Same thing, no Qiskit: the from-scratch NumPy simulator")
    from qlab.statevector import ry

    sv = StateVector(1, seed=7).apply(ry(theta), 0)
    print(f"state vector: {sv}")
    print(f"sampled 4000: {sv.sample_counts(4000)}")
    outcome = sv.measure(0)
    print(f"measure once -> {outcome}; state AFTER measurement: {sv}   (collapsed)")

    section("Reality check")
    print(
        "A qubit has infinitely many possible states, but measuring it yields at most\n"
        "ONE classical bit (Holevo's bound). The power comes from how amplitudes\n"
        "interfere across many qubits — not from storing extra bits in one qubit."
    )

    if save_plots:
        _plot(rows)
    return {"states": rows, "tilted_counts": counts, "tilted_p1": p1}


def _plot(rows: dict) -> None:
    import matplotlib.pyplot as plt
    from qiskit.visualization import plot_bloch_vector

    from qlab.plotting import save

    fig = plt.figure(figsize=(13, 3.2))
    for i, (name, r) in enumerate(rows.items(), start=1):
        ax = fig.add_subplot(1, len(rows), i, projection="3d")
        plot_bloch_vector(r["bloch"], ax=ax, title=name.split("(")[0].strip())
    fig.suptitle("1 · Qubit states on the Bloch sphere", fontweight="bold")
    save(fig, "01_qubits_bloch.png")


if __name__ == "__main__":
    run()
