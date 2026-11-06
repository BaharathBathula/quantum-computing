"""
4. QUANTUM GATES — unitary matrices that rotate the state.

Every gate is a unitary matrix U (U†U = I), so every gate is reversible.
Single-qubit gates are rotations of the Bloch sphere; CNOT is the
standard two-qubit entangler. {H, T, CNOT} is a universal set: any quantum
computation can be approximated with just those three.

Includes the corrected version of the infographic's card-4 demo:
    H then X then measure  ->  ~50/50, NOT {'1': 1024}
because X|+> = |+> (the |+> state is an eigenstate of X).

Run:  python -m concepts.c04_gates
"""

from __future__ import annotations

import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import CXGate, HGate, RXGate, SGate, TGate, XGate, YGate, ZGate
from qiskit.quantum_info import Operator

from qlab.backend import bit_probability, fmt_counts, header, run_counts, section

GATE_LIBRARY = {
    "X  (NOT, bit flip)": XGate(),
    "Y  (bit + phase flip)": YGate(),
    "Z  (phase flip)": ZGate(),
    "H  (Hadamard)": HGate(),
    "S  (√Z, 90° phase)": SGate(),
    "T  (√S, 45° phase)": TGate(),
}


def matrix(gate) -> np.ndarray:
    return Operator(gate).data


def is_unitary(m: np.ndarray) -> bool:
    return np.allclose(m.conj().T @ m, np.eye(m.shape[0]))


def identities() -> dict[str, bool]:
    X, Y, Z, H, S, T = (matrix(g) for g in (XGate(), YGate(), ZGate(), HGate(), SGate(), TGate()))
    return {
        "H·H = I": np.allclose(H @ H, np.eye(2)),
        "H·X·H = Z  (H swaps X and Z axes)": np.allclose(H @ X @ H, Z),
        "S·S = Z": np.allclose(S @ S, Z),
        "T·T = S": np.allclose(T @ T, S),
        "X·Y = iZ": np.allclose(X @ Y, 1j * Z),
    }


def cnot_truth_table() -> dict[str, str]:
    table = {}
    for inp in ("00", "01", "10", "11"):  # string is q1 q0 ; q0 is control
        qc = QuantumCircuit(2, 2)
        for i, bit in enumerate(reversed(inp)):
            if bit == "1":
                qc.x(i)
        qc.cx(0, 1)
        qc.measure([0, 1], [0, 1])
        table[inp] = next(iter(run_counts(qc, 1)))
    return table


def card4_circuit(with_h: bool) -> QuantumCircuit:
    """The infographic's example: (H) -> X -> measure."""
    qc = QuantumCircuit(1, 1)
    if with_h:
        qc.h(0)
    qc.x(0)
    qc.measure(0, 0)
    return qc


def phase_kickback_demo() -> QuantumCircuit:
    """H Z H = X: a phase flip becomes a visible bit flip."""
    qc = QuantumCircuit(1, 1)
    qc.h(0)
    qc.z(0)
    qc.h(0)
    qc.measure(0, 0)
    return qc


def rx_sweep(thetas, shots: int = 1000) -> list[float]:
    out = []
    for th in thetas:
        qc = QuantumCircuit(1, 1)
        qc.rx(th, 0)
        qc.measure(0, 0)
        out.append(bit_probability(run_counts(qc, shots), 0))
    return out


def run(save_plots: bool = True) -> dict:
    header(4, "Quantum gates", "Unitary, reversible building blocks")
    res = {}

    section("Gate matrices (all unitary)")
    for name, g in GATE_LIBRARY.items():
        m = matrix(g)
        flat = "  ".join(f"[{m[i, 0]:.2f}, {m[i, 1]:.2f}]" for i in range(2))
        print(f"{name:24s} {flat:52s} unitary={is_unitary(m)}")
    print(f"{'CNOT (4x4)':24s} unitary={is_unitary(matrix(CXGate()))}")

    section("Identities the infographic implies but never shows")
    res["identities"] = identities()
    for k, v in res["identities"].items():
        print(f"  {'✓' if v else '✗'} {k}")

    section("CNOT truth table (q0 = control)")
    res["cnot"] = cnot_truth_table()
    for inp, out in res["cnot"].items():
        print(f"  in {inp} -> out {out}")

    section("Card 4, corrected")
    res["x_only"] = run_counts(card4_circuit(with_h=False), 1024)
    res["h_then_x"] = run_counts(card4_circuit(with_h=True), 1024)
    res["hzh"] = run_counts(phase_kickback_demo(), 1024)
    print(f"X alone         -> {fmt_counts(res['x_only'])}")
    print(f"H then X        -> {fmt_counts(res['h_then_x'])}   (infographic claims {{'1': 1024}})")
    print("Why: H|0> = |+>, and X|+> = |+>. Flipping an equal superposition changes nothing.")
    print(f"H then Z then H -> {fmt_counts(res['hzh'])}   (this is the deterministic '1' they wanted)")

    section("Rotations are continuous: Rx(θ) gives P(1) = sin²(θ/2)")
    thetas = np.linspace(0, 2 * np.pi, 9)
    res["rx"] = (thetas, rx_sweep(thetas))
    for th, p in zip(*res["rx"]):
        print(f"  θ={np.degrees(th):5.0f}°  P(1)={p:.3f}  theory={np.sin(th / 2) ** 2:.3f}")
    print(f"Rx(π) equals X up to a global phase: {np.allclose(matrix(RXGate(np.pi)), -1j * matrix(XGate()))}")

    if save_plots:
        _plot(res)
    return res


def _plot(res: dict) -> None:
    import matplotlib.pyplot as plt

    from qlab.plotting import MUTED, PALETTE, bar_counts, save

    fig, axes = plt.subplots(1, 3, figsize=(14, 3.4))
    bar_counts(axes[0], res["h_then_x"], "H → X → measure: 50/50", PALETTE[4], ["0", "1"])
    bar_counts(axes[1], res["hzh"], "H → Z → H: always 1", PALETTE[0], ["0", "1"])
    th, p = res["rx"]
    fine = np.linspace(0, 2 * np.pi, 200)
    axes[2].plot(np.degrees(fine), np.sin(fine / 2) ** 2, color=MUTED, lw=1.5, label="sin²(θ/2)")
    axes[2].scatter(np.degrees(th), p, color=PALETTE[4], zorder=3, label="simulated")
    axes[2].set_xlabel("θ (degrees)")
    axes[2].set_ylabel("P(1)")
    axes[2].set_title("Rx(θ) sweep")
    axes[2].legend(fontsize=8)
    fig.suptitle("4 · Quantum gates", fontweight="bold")
    save(fig, "04_gates.png")


if __name__ == "__main__":
    run()
