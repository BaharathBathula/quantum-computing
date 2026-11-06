"""
5. QUANTUM ALGORITHMS — choreographed interference.

Four algorithms, smallest to most famous:
  A. Deutsch–Jozsa: is f constant or balanced? 1 quantum query vs up to 2^(n-1)+1.
  B. Grover search: find a marked item among N in ~(π/4)√N steps instead of ~N/2.
     Includes the CORRECTED 2-qubit circuit (the infographic's version returns 00).
     Also shows that running too many iterations makes it WORSE.
  C. Quantum Fourier Transform period finding — the engine inside Shor's algorithm.
  D. VQE (variational quantum eigensolver): a classical optimizer tunes a circuit
     to find a ground-state energy, the hybrid pattern used in chemistry today.

Run:  python -m concepts.c05_algorithms
"""

from __future__ import annotations

import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import QFTGate
from qiskit.quantum_info import SparsePauliOp, Statevector
from scipy.optimize import minimize

from qlab.backend import fmt_counts, header, probability, run_counts, section


# ---------------------------------------------------------------- A. Deutsch–Jozsa
def deutsch_jozsa(n: int, kind: str) -> QuantumCircuit:
    """kind: 'constant0', 'constant1', or 'balanced' (f(x) = x0 XOR x1 ... parity)."""
    qc = QuantumCircuit(n + 1, n)
    qc.x(n)
    qc.h(range(n + 1))
    if kind == "constant1":
        qc.x(n)
    elif kind == "balanced":
        for q in range(n):
            qc.cx(q, n)  # oracle: flips the ancilla when parity(x)=1
    qc.h(range(n))
    qc.measure(range(n), range(n))
    return qc


# ---------------------------------------------------------------- B. Grover
def grover_oracle(n: int, marked: str) -> QuantumCircuit:
    """Phase-flip the single basis state `marked` (string is q_{n-1}...q0)."""
    qc = QuantumCircuit(n, name="oracle")
    zeros = [q for q, b in enumerate(reversed(marked)) if b == "0"]
    if zeros:
        qc.x(zeros)
    qc.h(n - 1)
    qc.mcx(list(range(n - 1)), n - 1)  # multi-controlled Z = H·MCX·H
    qc.h(n - 1)
    if zeros:
        qc.x(zeros)
    return qc


def diffuser(n: int) -> QuantumCircuit:
    """Inversion about the mean: H X (MCZ) X H."""
    qc = QuantumCircuit(n, name="diffuser")
    qc.h(range(n))
    qc.x(range(n))
    qc.h(n - 1)
    qc.mcx(list(range(n - 1)), n - 1)
    qc.h(n - 1)
    qc.x(range(n))
    qc.h(range(n))
    return qc


def optimal_iterations(n: int) -> int:
    return int(np.floor(np.pi / 4 * np.sqrt(2**n)))


def grover(n: int, marked: str, iterations: int | None = None, measure: bool = True) -> QuantumCircuit:
    k = optimal_iterations(n) if iterations is None else iterations
    qc = QuantumCircuit(n, n if measure else 0)
    qc.h(range(n))
    for _ in range(k):
        qc.compose(grover_oracle(n, marked), inplace=True)
        qc.compose(diffuser(n), inplace=True)
    if measure:
        qc.measure(range(n), range(n))
    return qc


def grover_2q_fixed() -> QuantumCircuit:
    """The card-5 example written correctly, gate by gate (marks |11>)."""
    qc = QuantumCircuit(2, 2)
    qc.h([0, 1])  # superposition
    qc.cz(0, 1)  # oracle: phase-flip |11>
    qc.h([0, 1])  # diffuser: H X CZ X H
    qc.x([0, 1])
    qc.cz(0, 1)
    qc.x([0, 1])
    qc.h([0, 1])
    qc.measure([0, 1], [0, 1])
    return qc


def grover_success_curve(n: int, marked: str, max_iter: int) -> list[float]:
    return [
        Statevector(grover(n, marked, k, measure=False)).probabilities_dict().get(marked, 0.0)
        for k in range(max_iter + 1)
    ]


# ---------------------------------------------------------------- C. QFT period finding
def period_finding(n: int = 5, period: int = 4, offset: int = 3) -> QuantumCircuit:
    """Prepare a uniform superposition over x = offset + k*period, then inverse-QFT.
    Measurement lands on multiples of 2^n / period — the offset vanishes."""
    N = 2**n
    xs = [x for x in range(N) if x % period == offset % period]
    amps = np.zeros(N, dtype=complex)
    amps[xs] = 1 / np.sqrt(len(xs))
    qc = QuantumCircuit(n, n)
    qc.initialize(amps, range(n))
    qc.append(QFTGate(n).inverse(), range(n))
    qc.measure(range(n), range(n))
    return qc


# ---------------------------------------------------------------- D. VQE
HAMILTONIAN = SparsePauliOp.from_list(
    [("ZZ", 1.0), ("XI", 0.5), ("IX", 0.5)]
)  # transverse-field Ising, 2 spins


def ansatz(params) -> QuantumCircuit:
    qc = QuantumCircuit(2)
    qc.ry(params[0], 0)
    qc.ry(params[1], 1)
    qc.cx(0, 1)
    qc.ry(params[2], 0)
    qc.ry(params[3], 1)
    return qc


def energy(params) -> float:
    return float(Statevector(ansatz(params)).expectation_value(HAMILTONIAN).real)


def vqe(seed: int = 3) -> tuple[float, float, int]:
    rng = np.random.default_rng(seed)
    best = None
    for _ in range(4):  # a few random restarts avoid local minima
        r = minimize(
            energy, rng.uniform(-np.pi, np.pi, 4), method="COBYLA", options={"maxiter": 400, "rhobeg": 0.5}
        )
        if best is None or r.fun < best.fun:
            best = r
    exact = float(np.linalg.eigvalsh(HAMILTONIAN.to_matrix()).min())
    return best.fun, exact, best.nfev


def run(save_plots: bool = True) -> dict:
    header(5, "Quantum algorithms", "Interference that makes right answers likely")
    res = {}

    section("A. Deutsch–Jozsa (n=4): constant or balanced in ONE query")
    for kind in ("constant0", "constant1", "balanced"):
        c = run_counts(deutsch_jozsa(4, kind), 500)
        res[f"dj_{kind}"] = c
        verdict = "constant" if set(c) == {"0000"} else "balanced"
        print(f"{kind:10s} -> {fmt_counts(c):14s} => {verdict}")
    print("Classically you may need 2^(n-1)+1 = 9 queries to be certain.")

    section("B. Grover search")
    res["grover_2q"] = run_counts(grover_2q_fixed(), 1024)
    print(f"2-qubit, marked |11>, corrected circuit -> {fmt_counts(res['grover_2q'])}")
    n, marked = 5, "10110"
    k = optimal_iterations(n)
    res["grover_5q"] = run_counts(grover(n, marked), 2000)
    p = probability(res["grover_5q"], marked)
    print(f"5-qubit (N=32), marked {marked}, {k} iterations -> P(success)={p:.3f}")
    print(f"Queries: Grover {k} vs classical average {2**n // 2} (worst {2**n - 1}).")
    curve = grover_success_curve(n, marked, 3 * k)
    res["grover_curve"] = curve
    print("Success probability by iteration (too many iterations overshoots!):")
    print("  " + "  ".join(f"{i}:{q:.2f}" for i, q in enumerate(curve)))

    section("C. QFT period finding (core of Shor's algorithm)")
    pf = run_counts(period_finding(5, period=4, offset=3), 2000)
    res["period"] = pf
    peaks = sorted(int(b, 2) for b in pf)
    print(f"Hidden period 4 over N=32 with offset 3 -> outcomes {peaks}")
    print("All are multiples of 32/4 = 8. From the spacing we recover the period: 32/8 = 4.")
    print("Shor factors N by finding the period of a^x mod N exactly this way.")

    section("D. VQE: hybrid quantum–classical optimisation")
    e, exact, nfev = vqe()
    res["vqe"] = (e, exact)
    print(
        f"H = ZZ + 0.5·XI + 0.5·IX     VQE energy {e:.5f}   exact {exact:.5f}   "
        f"error {abs(e - exact):.1e}   ({nfev} circuit evaluations)"
    )

    if save_plots:
        _plot(res, n, marked, k)
    return res


def _plot(res: dict, n: int, marked: str, k: int) -> None:
    import matplotlib.pyplot as plt

    from qlab.plotting import MUTED, PALETTE, bar_counts, save

    fig, axes = plt.subplots(1, 3, figsize=(14, 3.4))
    bar_counts(
        axes[0], res["grover_2q"], "Grover 2-qubit (fixed): finds |11⟩", PALETTE[3], ["00", "01", "10", "11"]
    )
    curve = res["grover_curve"]
    axes[1].plot(range(len(curve)), curve, marker="o", color=PALETTE[3])
    axes[1].axvline(k, ls="--", color=MUTED, lw=1)
    axes[1].text(k + 0.2, 0.05, f"optimal = {k}", color=MUTED, fontsize=8)
    axes[1].set_xlabel("Grover iterations")
    axes[1].set_ylabel(f"P(find {marked})")
    axes[1].set_title(f"Grover N={2**n}: overshoot is real")
    pf = res["period"]
    xs = list(range(2**5))
    total = sum(pf.values())
    axes[2].bar(xs, [pf.get(format(x, "05b"), 0) / total for x in xs], color=PALETTE[0])
    axes[2].set_xlabel("measured integer")
    axes[2].set_ylabel("probability")
    axes[2].set_title("QFT reveals period 4 (peaks every 8)")
    fig.suptitle("5 · Quantum algorithms", fontweight="bold")
    save(fig, "05_algorithms.png")


if __name__ == "__main__":
    run()
