"""
2. SUPERPOSITION — and the part pop-science skips: interference.

"In superposition" means the state is a weighted sum of basis states with
complex amplitudes. It is NOT the same as a coin that is secretly heads or
tails (classical uncertainty). Three experiments here prove the difference:

  A. H|0>  -> 50/50 when measured        (looks like a coin...)
  B. H H|0> -> 0 every time               (...but a coin flipped twice is still 50/50)
  C. |+> and |->  look identical in Z, but H tells them apart perfectly

And a fourth that kills the "tries every answer at once" myth:
  D. H on n qubits makes 2^n amplitudes, but measuring returns ONE random
     bitstring. Algorithms win by making wrong answers cancel (interference).

Run:  python -m concepts.c02_superposition
"""

from __future__ import annotations

import numpy as np
from qiskit import QuantumCircuit

from qlab.backend import fmt_counts, header, probability, run_counts, section


def plus_state(measure: bool = True) -> QuantumCircuit:
    qc = QuantumCircuit(1, 1)
    qc.h(0)
    if measure:
        qc.measure(0, 0)
    return qc


def double_hadamard() -> QuantumCircuit:
    qc = QuantumCircuit(1, 1)
    qc.h(0)
    qc.h(0)  # the two paths to |1> have opposite signs and cancel
    qc.measure(0, 0)
    return qc


def plus_or_minus(minus: bool, read_in_x_basis: bool) -> QuantumCircuit:
    qc = QuantumCircuit(1, 1)
    if minus:
        qc.x(0)
    qc.h(0)  # |0>->|+>,  |1>->|->
    if read_in_x_basis:
        qc.h(0)  # rotate X-basis onto Z-basis before measuring
    qc.measure(0, 0)
    return qc


def uniform_superposition(n: int) -> QuantumCircuit:
    qc = QuantumCircuit(n, n)
    qc.h(range(n))
    qc.measure(range(n), range(n))
    return qc


def classical_coin_twice(shots: int, seed: int = 0) -> float:
    """Fraction of 'heads' after flipping a fair coin, then flipping it again."""
    rng = np.random.default_rng(seed)
    rng.integers(0, 2, shots)  # first flip: its result is irrelevant...
    second = rng.integers(0, 2, shots)  # ...because the second flip ignores it
    return float(np.mean(second == 0))


def run(save_plots: bool = True) -> dict:
    header(2, "Superposition", "Weighted sums of states — and why interference is the real story")
    shots = 2000
    res = {}

    section("A. Hadamard on |0>: looks like a fair coin")
    res["A"] = run_counts(plus_state(), shots)
    print(f"H|0> measured:      {fmt_counts(res['A'])}")

    section("B. Apply H twice: the 'coin' always lands on 0")
    res["B"] = run_counts(double_hadamard(), shots)
    coin = classical_coin_twice(shots)
    print(f"H H|0> measured:    {fmt_counts(res['B'])}    <- interference")
    print(f"classical coin x2:  heads {coin:.0%}                <- no interference")
    print("Math: H|+> = (H|0> + H|1>)/√2 = ½(|0>+|1>) + ½(|0>−|1>) = |0>. The two |1> paths cancel.")

    section("C. |+> vs |->: same Z statistics, different states")
    for minus in (False, True):
        label = "|->" if minus else "|+>"
        z = run_counts(plus_or_minus(minus, read_in_x_basis=False), shots)
        x = run_counts(plus_or_minus(minus, read_in_x_basis=True), shots)
        res[f"C{label}"] = (z, x)
        print(f"{label}  Z-basis: {fmt_counts(z):24s}  X-basis: {fmt_counts(x)}")
    print("The relative phase (+ or −) is invisible to one measurement but fully real.")

    section("D. 10 qubits in superposition = 1024 amplitudes, but ONE answer per shot")
    n = 10
    res["D"] = run_counts(uniform_superposition(n), shots=5)
    print(f"5 shots of H^⊗{n}|0>: {list(res['D'])}")
    print(
        "Each run returns a random bitstring. Reading out 'all answers at once' is impossible;\n"
        "useful algorithms (see #5) choreograph interference so the RIGHT answer is likely."
    )

    res["p0_double_h"] = probability(res["B"], "0")
    if save_plots:
        _plot(res, coin)
    return res


def _plot(res: dict, coin: float) -> None:
    import matplotlib.pyplot as plt

    from qlab.plotting import PALETTE, bar_counts, save

    fig, axes = plt.subplots(1, 4, figsize=(14, 3.2))
    bar_counts(axes[0], res["A"], "H|0⟩  →  50/50", PALETTE[0], ["0", "1"])
    bar_counts(axes[1], res["B"], "H H|0⟩  →  always 0", PALETTE[1], ["0", "1"])
    axes[2].bar(["0", "1"], [coin, 1 - coin], color=PALETTE[2], width=0.6)
    axes[2].set_title("Classical coin flipped twice")
    axes[2].set_ylabel("fraction")
    _z, x = res["C|->"]
    bar_counts(axes[3], x, "|−⟩ read in X basis → 1", PALETTE[4], ["0", "1"])
    fig.suptitle("2 · Superposition vs classical randomness", fontweight="bold")
    save(fig, "02_superposition_interference.png")


if __name__ == "__main__":
    run()
