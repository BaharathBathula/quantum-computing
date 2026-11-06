"""
9. QUANTUM ADVANTAGE — when a quantum computer beats the best classical method.

  A. Why classical simulation hits a wall: memory for 2^n amplitudes, and
     measured simulation time on THIS machine as qubits grow.
  B. Query advantage you can count: Grover's √N vs classical N.
  C. How advantage is actually measured: linear cross-entropy benchmarking
     (XEB) on random circuits — the method behind Google's 2019 claim —
     comparing an ideal device, a noisy IBM Heron model, and random guessing.
  D. An honest timeline of claims and counter-claims.

Run:  python -m concepts.c09_advantage
"""

from __future__ import annotations

import time

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Statevector
from qiskit_aer import AerSimulator

from qlab.backend import header, noisy_device_simulator, run_counts, section

BYTES_PER_AMPLITUDE = 16  # complex128


def statevector_bytes(n: int) -> int:
    return BYTES_PER_AMPLITUDE * 2 ** int(n)  # Python int: no overflow at large n


def human_bytes(b: float) -> str:
    original = b
    for unit in ("B", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB"):
        if b < 1024:
            return f"{b:,.0f} {unit}"
        b /= 1024
    return f"{float(original):.1e} bytes"


def random_circuit(n: int, cycles: int, seed: int = 0, measure: bool = True) -> QuantumCircuit:
    """Google-style random circuit: random √X/√Y/√W layer, then CZ brickwork."""
    rng = np.random.default_rng(seed)
    qc = QuantumCircuit(n, n if measure else 0)
    for c in range(cycles):
        for q in range(n):
            phi = rng.choice([0, np.pi / 2, np.pi / 4])  # √X, √Y, √W
            qc.r(np.pi / 2, phi, q)
        for q in range(c % 2, n - 1, 2):
            qc.cz(q, q + 1)
    if measure:
        qc.measure(range(n), range(n))
    return qc


def time_statevector(ns, cycles: int = 8, repeats: int = 2) -> list[tuple[int, float]]:
    sim = AerSimulator(method="statevector", max_parallel_threads=0)
    out = []
    for n in ns:
        tqc = transpile(random_circuit(n, cycles), sim, optimization_level=0)
        best = min(_timed(sim, tqc) for _ in range(repeats))
        out.append((n, best))
    return out


def _timed(sim, tqc) -> float:
    t0 = time.perf_counter()
    sim.run(tqc, shots=1).result()
    return time.perf_counter() - t0


def xeb_fidelity(samples: dict[str, int], ideal_probs: dict[str, float], n: int) -> float:
    """F_XEB = 2^n * <p_ideal(x)>_samples - 1.   ~1 ideal device, ~0 pure noise."""
    total = sum(samples.values())
    mean_p = sum(ideal_probs.get(k, 0.0) * c for k, c in samples.items()) / total
    return 2**n * mean_p - 1


def xeb_experiment(n: int = 8, cycles: int = 10, shots: int = 4000, seed: int = 11) -> dict:
    qc = random_circuit(n, cycles, seed)
    ideal = Statevector(random_circuit(n, cycles, seed, measure=False)).probabilities_dict()
    ideal_samples = run_counts(qc, shots)
    sim = noisy_device_simulator()
    noisy_samples = (
        sim.run(transpile(qc, sim, optimization_level=1, seed_transpiler=3), shots=shots)
        .result()
        .get_counts()
    )
    rng = np.random.default_rng(seed)
    uniform = {}
    for x in rng.integers(0, 2**n, shots):
        k = format(int(x), f"0{n}b")
        uniform[k] = uniform.get(k, 0) + 1
    return {
        "n": n,
        "cycles": cycles,
        "ideal": xeb_fidelity(ideal_samples, ideal, n),
        "noisy": xeb_fidelity(noisy_samples, ideal, n),
        "uniform": xeb_fidelity(uniform, ideal, n),
    }


TIMELINE = [
    ("1994", "Shor's algorithm: factoring in polynomial time on a quantum computer — the theoretical spark."),
    ("1996", "Grover's algorithm: quadratic speed-up for unstructured search."),
    (
        "2019",
        "Google Sycamore (53 qubits) sampled random circuits in ~200 s and claimed ~10,000 years "
        "classically. IBM countered that a supercomputer with enough disk could do it in ~2.5 days.",
    ),
    (
        "2022",
        "Tensor-network methods reproduced the 2019 sampling task classically on GPUs in hours, "
        "showing that advantage claims are a moving target as classical algorithms improve.",
    ),
    (
        "2024",
        "Google Willow (105 qubits): logical error rates fell as the surface code grew — "
        "the 'below threshold' result module 8 illustrates.",
    ),
    (
        "Oct 2025",
        "Google 'Quantum Echoes' (OTOC on Willow, published in Nature): ~13,000× faster than the "
        "best classical algorithm on a top supercomputer, and pitched as verifiable.",
    ),
    (
        "2026",
        "IBM expects partners to show early quantum advantage on its hardware this year and "
        "targets a large-scale fault-tolerant machine by 2029.",
    ),
]


def run(save_plots: bool = True) -> dict:
    header(9, "Quantum advantage", "Beating the best classical method — on specific tasks")
    res = {}

    section("A. The classical wall: memory to store an n-qubit state")
    for n in (10, 20, 30, 40, 50, 53, 60, 100):
        print(f"  {n:3d} qubits -> {human_bytes(statevector_bytes(n)):>16s}")
    print(
        "A laptop tops out near 30 qubits; ~50 qubits needs more memory than any supercomputer has\n"
        "(clever tensor-network methods dodge this for some circuits — which is why claims get contested)."
    )

    section("A2. Measured on this machine: statevector simulation time")
    timings = time_statevector(range(12, 25, 2))
    res["timings"] = timings
    for n, t in timings:
        print(f"  {n:2d} qubits: {t * 1000:9.1f} ms")
    ns = np.array([n for n, t in timings if n >= 18])
    ts = np.array([t for n, t in timings if n >= 18])
    slope, _ = np.polyfit(ns, np.log2(ts), 1)
    res["growth_per_qubit"] = 2**slope
    print(f"Each extra qubit multiplies runtime by ~{2**slope:.2f}× (ideal: 2×).")

    section("B. Counting queries: Grover vs classical search")
    for N in (16, 1_000, 1_000_000, 10**12):
        print(f"  N={N:>16,}: classical ~{N // 2:>16,} checks   Grover ~{int(np.pi / 4 * np.sqrt(N)):>10,}")
    print("Quadratic, not exponential — and error-correction overhead eats much of it in practice.")

    section("C. Cross-entropy benchmarking on random circuits (the 2019 method)")
    x = xeb_experiment()
    res["xeb"] = x
    print(f"{x['n']} qubits, {x['cycles']} cycles:")
    print(f"  ideal quantum device   F_XEB = {x['ideal']:+.3f}")
    print(f"  IBM Heron noise model  F_XEB = {x['noisy']:+.3f}")
    print(f"  random guessing        F_XEB = {x['uniform']:+.3f}")
    print(
        "A device 'wins' if it reaches a positive F_XEB at a size no classical computer can\n"
        "reproduce in reasonable time. Noise drags F_XEB toward 0 — hence module 8."
    )

    section("D. Timeline (claims are task-specific and get challenged)")
    for when, what in TIMELINE:
        print(f"  {when:9s} {what}")

    if save_plots:
        _plot(res)
    return res


def _plot(res: dict) -> None:
    import matplotlib.pyplot as plt

    from qlab.plotting import MUTED, PALETTE, save

    fig, axes = plt.subplots(1, 3, figsize=(15, 3.6))
    ns = np.arange(10, 61)
    axes[0].semilogy(ns, [float(statevector_bytes(n)) for n in ns], color=PALETTE[5])
    for label, b in (("16 GB laptop", 16e9), ("1 PB", 1e15)):
        axes[0].axhline(b, ls="--", color=MUTED, lw=1)
        axes[0].text(11, b * 1.6, label, color=MUTED, fontsize=8)
    axes[0].set_xlabel("qubits")
    axes[0].set_ylabel("bytes for the state vector")
    axes[0].set_title("Memory doubles with every qubit")

    t = res["timings"]
    axes[1].semilogy([n for n, _ in t], [s for _, s in t], marker="o", color=PALETTE[0])
    axes[1].set_xlabel("qubits")
    axes[1].set_ylabel("seconds (this machine)")
    axes[1].set_title(f"Simulation time ×{res['growth_per_qubit']:.1f} per qubit")

    x = res["xeb"]
    vals = [x["ideal"], x["noisy"], x["uniform"]]
    bars = axes[2].bar(
        ["ideal\ndevice", "noisy\nHeron model", "random\nguessing"],
        vals,
        color=[PALETTE[5], PALETTE[0], MUTED],
        width=0.6,
    )
    for b, v in zip(bars, vals):
        axes[2].text(b.get_x() + b.get_width() / 2, max(v, 0), f"{v:+.2f}", ha="center", va="bottom")
    axes[2].axhline(0, color=MUTED, lw=0.8)
    axes[2].set_ylabel("F_XEB")
    axes[2].set_title(f"Cross-entropy benchmark ({x['n']} qubits)")
    fig.suptitle("9 · Quantum advantage", fontweight="bold")
    save(fig, "09_advantage.png")


if __name__ == "__main__":
    run()
