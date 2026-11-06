"""
3. ENTANGLEMENT — correlations no classical model can reproduce.

Three honest demonstrations:
  A. Bell pair (|00>+|11>)/√2: outcomes always agree.
     (Agreement alone is easy classically — two envelopes with matching cards.)
  B. No-signaling: Alice's qubit ALONE is perfectly random whatever Bob does.
     Entanglement cannot send messages faster than light.
  C. CHSH Bell test: measure in rotated bases. Any classical "hidden card"
     model obeys S <= 2. Quantum mechanics reaches S = 2√2 ≈ 2.83.
     This, not plain agreement, is what makes entanglement non-classical.
Plus D. Teleportation using a mid-circuit measurement and classical feed-forward.

Run:  python -m concepts.c03_entanglement
"""

from __future__ import annotations

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import DensityMatrix, Statevector, partial_trace

from qlab.backend import bit_probability, fmt_counts, header, run_counts, section

TSIRELSON = 2 * np.sqrt(2)
CLASSICAL_BOUND = 2.0


def bell_pair(kind: str = "phi+", measure: bool = True) -> QuantumCircuit:
    """The four Bell states: phi+, phi-, psi+, psi-."""
    qc = QuantumCircuit(2, 2 if measure else 0)
    if kind in ("psi+", "psi-"):
        qc.x(1)
    if kind in ("phi-", "psi-"):
        qc.x(0)
    qc.h(0)
    qc.cx(0, 1)
    if measure:
        qc.measure([0, 1], [0, 1])
    return qc


def ghz(n: int, measure: bool = True) -> QuantumCircuit:
    qc = QuantumCircuit(n, n if measure else 0)
    qc.h(0)
    for q in range(n - 1):
        qc.cx(q, q + 1)
    if measure:
        qc.measure(range(n), range(n))
    return qc


def reduced_state_of_alice() -> np.ndarray:
    rho = DensityMatrix(Statevector(bell_pair(measure=False)))
    return partial_trace(rho, [1]).data  # trace out Bob (qubit 1)


def chsh_circuit(alice_angle: float, bob_angle: float) -> QuantumCircuit:
    """Measure each qubit along an axis in the X–Z plane at the given angle."""
    qc = bell_pair(measure=False)
    qc.ry(-alice_angle, 0)  # rotating by -angle then measuring Z == measuring along `angle`
    qc.ry(-bob_angle, 1)
    qc.measure_all()
    return qc


def correlation(counts: dict[str, int]) -> float:
    """E = P(same) - P(different)."""
    total = sum(counts.values())
    same = sum(c for k, c in counts.items() if k[0] == k[1])
    return (2 * same - total) / total


CHSH_ANGLES = {"a": 0.0, "a'": np.pi / 2, "b": np.pi / 4, "b'": -np.pi / 4}


def chsh(shots: int = 4000) -> tuple[float, dict]:
    A = CHSH_ANGLES
    E = {}
    for a in ("a", "a'"):
        for b in ("b", "b'"):
            E[(a, b)] = correlation(run_counts(chsh_circuit(A[a], A[b]), shots))
    S = E[("a", "b")] + E[("a", "b'")] + E[("a'", "b")] - E[("a'", "b'")]
    return S, E


def chsh_exact() -> float:
    A = CHSH_ANGLES
    # For |Phi+>, E(a, b) = cos(a - b)
    return (
        np.cos(A["a"] - A["b"])
        + np.cos(A["a"] - A["b'"])
        + np.cos(A["a'"] - A["b"])
        - np.cos(A["a'"] - A["b'"])
    )


def teleport(theta: float) -> QuantumCircuit:
    """Teleport ry(theta)|0> from qubit 0 to qubit 2. Returns circuit; bit 2 holds Bob's readout."""
    qc = QuantumCircuit(3, 3)
    qc.ry(theta, 0)  # the unknown state to send
    qc.h(1)
    qc.cx(1, 2)  # Alice (q1) and Bob (q2) share a Bell pair
    qc.barrier()
    qc.cx(0, 1)
    qc.h(0)  # Alice's Bell-basis measurement...
    qc.measure(0, 0)
    qc.measure(1, 1)
    with qc.if_test((qc.clbits[1], 1)):  # ...and 2 classical bits sent to Bob
        qc.x(2)
    with qc.if_test((qc.clbits[0], 1)):
        qc.z(2)
    qc.measure(2, 2)
    return qc


def run(save_plots: bool = True) -> dict:
    header(3, "Entanglement", "Correlations stronger than any classical system")
    res = {}

    section("A. Bell pair: outcomes always agree")
    for kind in ("phi+", "phi-", "psi+", "psi-"):
        counts = run_counts(bell_pair(kind), 2000)
        res[kind] = counts
        print(f"{kind:5s} {fmt_counts(counts)}")
    print("phi± give only 00/11, psi± give only 01/10.")
    res["ghz5"] = run_counts(ghz(5), 2000)
    print(f"GHZ-5 (5-qubit cat state): {fmt_counts(res['ghz5'])}")

    section("B. No-signaling: Alice's half alone is pure noise")
    rho_a = reduced_state_of_alice()
    res["rho_alice"] = rho_a
    print("Alice's reduced density matrix:\n", np.round(rho_a.real, 3))
    print(
        "= I/2, a maximally mixed qubit. Nothing Bob does changes Alice's local statistics,\n"
        "so entanglement transmits no information on its own (the infographic's 'instantly'\n"
        "describes correlation, not communication)."
    )

    section("C. CHSH Bell test — the actual proof of non-classicality")
    S, E = chsh()
    res["chsh_S"], res["chsh_E"] = S, E
    for (a, b), e in E.items():
        print(f"  E({a},{b}) = {e:+.3f}")
    print(f"S measured = {S:.3f}   exact = {chsh_exact():.3f}   classical limit = {CLASSICAL_BOUND}")
    print(f"S > 2 -> no local hidden-variable model can explain this. (Max possible: {TSIRELSON:.3f})")

    section("D. Teleportation (uses entanglement + 2 classical bits)")
    tele = {}
    for theta in (0.0, np.pi / 3, np.pi / 2, 2 * np.pi / 3, np.pi):
        counts = run_counts(teleport(theta), 4000)
        got = bit_probability(counts, 2)
        want = np.sin(theta / 2) ** 2
        tele[theta] = (got, want)
        print(f"theta={np.degrees(theta):5.0f}°  Bob P(1)={got:.3f}  expected {want:.3f}")
    res["teleport"] = tele
    print("Bob only gets the state after Alice's 2 classical bits arrive -> no faster-than-light.")

    if save_plots:
        _plot(res)
    return res


def _plot(res: dict) -> None:
    import matplotlib.pyplot as plt

    from qlab.plotting import MUTED, PALETTE, bar_counts, save

    fig, axes = plt.subplots(1, 3, figsize=(14, 3.4))
    bar_counts(axes[0], res["phi+"], "Bell |Φ+⟩: only 00 and 11", PALETTE[2], ["00", "01", "10", "11"])
    ax = axes[1]
    vals = [CLASSICAL_BOUND, res["chsh_S"], TSIRELSON]
    bars = ax.bar(
        ["classical\nlimit", "measured", "quantum\nmax 2√2"],
        vals,
        color=[MUTED, PALETTE[2], PALETTE[0]],
        width=0.6,
    )
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v, f"{v:.2f}", ha="center", va="bottom")
    ax.axhline(2, ls="--", color=MUTED, lw=1)
    ax.set_title("CHSH Bell test: S > 2")
    ax.set_ylim(0, 3.2)
    ax = axes[2]
    th = np.linspace(0, np.pi, 100)
    ax.plot(np.degrees(th), np.sin(th / 2) ** 2, color=MUTED, lw=1.5, label="original state P(1)")
    pts = res["teleport"]
    ax.scatter(
        [np.degrees(t) for t in pts],
        [g for g, _ in pts.values()],
        color=PALETTE[0],
        zorder=3,
        label="Bob's teleported qubit",
    )
    ax.set_xlabel("θ of state ry(θ)|0⟩ (degrees)")
    ax.set_ylabel("P(1)")
    ax.set_title("Teleportation reproduces the state")
    ax.legend(loc="upper left", fontsize=8)
    fig.suptitle("3 · Entanglement", fontweight="bold")
    save(fig, "03_entanglement.png")


if __name__ == "__main__":
    run()
