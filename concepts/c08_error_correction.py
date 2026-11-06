"""
8. QUANTUM ERROR CORRECTION — protecting fragile qubits with redundancy.

You can't copy an unknown qubit (no-cloning) or look at it without
disturbing it. QEC gets around both: spread one LOGICAL qubit across
several PHYSICAL qubits, then measure only PARITIES (the "syndrome"),
which reveal where an error is without revealing the data.

  A. 3-qubit bit-flip code done properly: encode → error → syndrome on
     ancillas → conditional correction → decode. Every single X error is
     fixed, for |0>, |1> AND an arbitrary superposition.
     (The infographic's version always returns the error 010 — see CORRECTIONS.md.)
  B. Its blind spot: a phase (Z) error passes straight through.
  C. The phase-flip code fixes Z errors by working in the X basis —
     the idea that Shor's 9-qubit code and surface codes build on.
  D. Below threshold, more qubits = fewer logical errors: repetition codes
     of distance 1, 3, 5, 7 under noise.

Run:  python -m concepts.c08_error_correction
"""

from __future__ import annotations

from math import comb

import numpy as np
from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister
from qiskit_aer.noise import NoiseModel, pauli_error

from qlab.backend import header, run_counts, section


def bit_flip_code(
    error_on: int | None, theta: float = 0.0, phase_error: bool = False, basis: str = "Z"
) -> QuantumCircuit:
    """Full 3-qubit repetition code with 2 syndrome ancillas.

    theta: logical state ry(theta)|0> to protect.
    error_on: data qubit (0, 1, 2) that suffers the error, or None.
    basis='Z' -> bit-flip code (fixes X errors). basis='X' -> phase-flip code (fixes Z errors).
    Output bit 'out' = logical qubit after decoding, rotated back so the ideal answer is 0.
    """
    data = QuantumRegister(3, "d")
    anc = QuantumRegister(2, "a")
    syn = ClassicalRegister(2, "syn")
    out = ClassicalRegister(1, "out")
    qc = QuantumCircuit(data, anc, syn, out)

    qc.ry(theta, data[0])  # the logical state to protect
    qc.cx(data[0], data[1])  # encode: a|0>+b|1> -> a|000>+b|111>
    qc.cx(data[0], data[2])
    if basis == "X":
        qc.h(data)  # ...or a|+++>+b|--->
    qc.barrier()

    if error_on is not None:  # the noise event
        (qc.z if phase_error else qc.x)(data[error_on])
    qc.barrier()

    if basis == "X":
        qc.h(data)
    qc.cx(data[0], anc[0])  # syndrome bit 0 = parity(d0, d1)
    qc.cx(data[1], anc[0])
    qc.cx(data[1], anc[1])  # syndrome bit 1 = parity(d1, d2)
    qc.cx(data[2], anc[1])
    qc.measure(anc, syn)  # measures parities only — data untouched

    # syn value (bit1 bit0): 01 -> d0 flipped, 11 -> d1 flipped, 10 -> d2 flipped
    with qc.if_test((syn, 0b01)):
        qc.x(data[0])
    with qc.if_test((syn, 0b11)):
        qc.x(data[1])
    with qc.if_test((syn, 0b10)):
        qc.x(data[2])

    qc.cx(data[0], data[2])  # decode back onto data[0]
    qc.cx(data[0], data[1])
    qc.ry(-theta, data[0])  # undo the preparation: ideal result is |0>
    qc.measure(data[0], out[0])
    return qc


def logical_error_rate(counts: dict[str, int]) -> float:
    """Fraction of shots where the decoded logical qubit came out wrong (out bit = 1).
    Counts keys look like 'out syn', e.g. '0 01'."""
    total = sum(counts.values())
    wrong = sum(c for k, c in counts.items() if k.split()[0] == "1")
    return wrong / total


def repetition_memory(d: int, logical_one: bool = False) -> QuantumCircuit:
    """Store a classical-like logical bit in d qubits, let noise hit each, read all out."""
    qc = QuantumCircuit(d, d)
    if logical_one:
        qc.x(range(d))
    for q in range(d):
        qc.id(q)  # each idle step may flip the qubit
    qc.measure(range(d), range(d))
    return qc


def flip_noise(p: float) -> NoiseModel:
    nm = NoiseModel()
    nm.add_all_qubit_quantum_error(pauli_error([("X", p), ("I", 1 - p)]), ["id"])
    return nm


def majority_failure(counts: dict[str, int], d: int, logical_one: bool = False) -> float:
    total = sum(counts.values())
    bad = 0
    for k, c in counts.items():
        ones = k.count("1")
        decoded_one = ones > d // 2
        if decoded_one != logical_one:
            bad += c
    return bad / total


def analytic_failure(p: float, d: int) -> float:
    return sum(comb(d, k) * p**k * (1 - p) ** (d - k) for k in range((d + 1) // 2, d + 1))


def run(save_plots: bool = True) -> dict:
    header(8, "Quantum error correction", "Redundancy + parity checks, without looking at the data")
    res = {}
    shots = 1000

    section("A. Bit-flip code: every single X error is corrected")
    table = {}
    for theta, label in ((0.0, "|0>"), (np.pi, "|1>"), (1.1, "ry(1.1)|0>")):
        for err in (None, 0, 1, 2):
            c = run_counts(bit_flip_code(err, theta), shots)
            table[(label, err)] = logical_error_rate(c)
        print(
            f"logical {label:11s} "
            + "  ".join(
                f"{'no error' if e is None else f'X on d{e}'}: {table[(label, e)]:.0%} wrong"
                for e in (None, 0, 1, 2)
            )
        )
    res["bitflip_table"] = table

    section("B. ...but a phase (Z) error slips through the bit-flip code")
    theta = np.pi / 2  # needs a superposition to make phase matter
    zfail = logical_error_rate(run_counts(bit_flip_code(1, theta, phase_error=True), shots))
    res["bitflip_vs_z"] = zfail
    print(f"Z error on d1, logical ry(π/2)|0>: {zfail:.0%} wrong")

    section("C. Phase-flip code (same idea in the X basis) fixes Z errors")
    pf = {
        e: logical_error_rate(run_counts(bit_flip_code(e, theta, phase_error=True, basis="X"), shots))
        for e in (None, 0, 1, 2)
    }
    res["phaseflip_table"] = pf
    print("  ".join(f"{'no error' if e is None else f'Z on d{e}'}: {v:.0%} wrong" for e, v in pf.items()))
    print(
        "Shor's 9-qubit code nests both codes to fix any single-qubit error; surface codes\n"
        "generalise the parity-check idea to a 2D grid that scales."
    )

    section("D. Threshold behaviour: distance-d repetition code under noise")
    ps = [0.01, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5]
    curves = {}
    for d in (1, 3, 5, 7):
        curves[d] = [
            majority_failure(run_counts(repetition_memory(d), 4000, noise_model=flip_noise(p)), d) for p in ps
        ]
        print(f"d={d}: " + "  ".join(f"p={p:.2f}→{f:.4f}" for p, f in zip(ps, curves[d])))
    res["threshold"] = (ps, curves)
    print(
        "Below p=0.5 (this code's threshold), each step up in distance suppresses errors further.\n"
        "Real codes also have to cope with faulty syndrome measurements, which pushes practical\n"
        "thresholds down to roughly 1% for the surface code."
    )

    if save_plots:
        _plot(res)
    return res


def _plot(res: dict) -> None:
    import matplotlib.pyplot as plt

    from qlab.plotting import MUTED, PALETTE, save

    ps, curves = res["threshold"]
    fig, ax = plt.subplots(figsize=(7, 4))
    fine = np.linspace(0.005, 0.5, 200)
    for i, (d, ys) in enumerate(curves.items()):
        ax.plot(fine, [analytic_failure(p, d) for p in fine], color=PALETTE[i], lw=1.2)
        seen = [
            (p, y) for p, y in zip(ps, ys) if y > 0
        ]  # 0 failures in 4000 shots: nothing to plot on a log axis
        ax.scatter(
            [p for p, _ in seen],
            [y for _, y in seen],
            color=PALETTE[i],
            s=22,
            zorder=3,
            label=f"d = {d}" + (" (unprotected)" if d == 1 else ""),
        )
    ax.plot(fine, fine, ls="--", color=MUTED, lw=1)
    ax.set_yscale("log")
    ax.set_ylim(1e-5, 1)
    ax.set_xlabel("physical error probability p")
    ax.set_ylabel("logical error probability")
    ax.set_title("8 · More qubits, fewer logical errors (below threshold)")
    ax.text(0.01, 1.3e-5, "dots = simulated (4000 shots), lines = exact formula", color=MUTED, fontsize=8)
    ax.legend(fontsize=8)
    save(fig, "08_error_correction_threshold.png")


if __name__ == "__main__":
    run()
