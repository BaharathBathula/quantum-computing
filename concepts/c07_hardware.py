"""
7. QUANTUM HARDWARE — where theory meets noise.

Uses a locally stored snapshot of a real IBM Heron chip (FakeFez, 156 qubits)
with its calibrated error rates, so you can see hardware effects without an
account:
  A. The chip's vital signs: T1, T2, gate errors, readout errors
  B. What compilation does to your circuit (native gates + physical qubits)
  C. Ideal vs noisy: GHZ fidelity drops as circuits grow
  D. Decoherence from first principles: measure T1 (energy loss) and T2
     (phase loss) with a custom noise model, and fit them back
  E. The hardware landscape (corrected from the infographic)
  F. Optional: run on a real IBM device (needs a free IBM Quantum account)

Run:  python -m concepts.c07_hardware          (add --real to submit to IBM)
"""

from __future__ import annotations

import statistics as st
import sys

import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer.noise import NoiseModel, thermal_relaxation_error
from scipy.optimize import curve_fit

from qlab.backend import (
    bit_probability,
    fake_device,
    fmt_counts,
    header,
    run_counts,
    run_on_device_model,
    section,
)

MODALITIES = [
    # (technology, examples, strengths, challenges)
    (
        "Superconducting",
        "IBM, Google, Rigetti",
        "fast gates (tens of ns), mature fabrication",
        "needs ~10–15 mK dilution fridges; short coherence",
    ),
    (
        "Trapped ions",
        "Quantinuum, IonQ",
        "highest gate fidelities, all-to-all connectivity",
        "slower gates (µs); scaling ion chains",
    ),
    (
        "Neutral atoms",
        "QuEra, Pasqal, Atom Computing",
        "hundreds–thousands of atoms, reconfigurable layouts",
        "slower cycles; atom loss",
    ),
    (
        "Photonic",
        "PsiQuantum, Xanadu",
        "photons barely decohere; telecom-compatible",
        "photon loss; deterministic 2-qubit gates are hard; detectors often cryogenic",
    ),
    ("Spin qubits", "Intel, Diraq", "tiny qubits, built in silicon fabs", "uniformity and wiring at scale"),
    (
        "Topological",
        "Microsoft (Majorana 1)",
        "error resistance built into the physics (in theory)",
        "earliest stage; still being experimentally validated",
    ),
]


def device_vitals() -> dict:
    b = fake_device()
    props = [b.qubit_properties(q) for q in range(b.num_qubits)]
    t1 = [p.t1 for p in props if p and p.t1]
    t2 = [p.t2 for p in props if p and p.t2]
    tgt = b.target

    def median_error(name):
        errs = [ip.error for ip in tgt[name].values() if ip is not None and ip.error is not None]
        return st.median(errs) if errs else float("nan")

    return {
        "name": b.name,
        "qubits": b.num_qubits,
        "native_gates": sorted(n for n in b.operation_names if n in ("cz", "ecr", "rz", "sx", "x")),
        "T1_us": st.median(t1) * 1e6,
        "T2_us": st.median(t2) * 1e6,
        "sx_error": median_error("sx"),
        "cz_error": median_error("cz"),
        "readout_error": median_error("measure"),
        "cz_time_ns": st.median(ip.duration for ip in tgt["cz"].values() if ip and ip.duration) * 1e9,
    }


def ghz(n: int) -> QuantumCircuit:
    qc = QuantumCircuit(n, n)
    qc.h(0)
    for q in range(n - 1):
        qc.cx(q, q + 1)
    qc.measure(range(n), range(n))
    return qc


def ghz_success(counts: dict[str, int], n: int) -> float:
    total = sum(counts.values())
    return (counts.get("0" * n, 0) + counts.get("1" * n, 0)) / total


def relaxation_noise(t1: float, t2: float, step: float) -> NoiseModel:
    """Every 'id' gate = waiting `step` seconds while energy and phase leak away."""
    nm = NoiseModel()
    nm.add_all_qubit_quantum_error(thermal_relaxation_error(t1, t2, step), ["id"])
    return nm


def t1_experiment(n_steps: int, nm: NoiseModel) -> QuantumCircuit:
    qc = QuantumCircuit(1, 1)
    qc.x(0)  # excite to |1>
    for _ in range(n_steps):
        qc.id(0)  # wait
    qc.measure(0, 0)
    return qc


def ramsey_experiment(n_steps: int) -> QuantumCircuit:
    qc = QuantumCircuit(1, 1)
    qc.h(0)  # put on the equator
    for _ in range(n_steps):
        qc.id(0)
    qc.h(0)  # interfere: P(0)=1 if phase survived
    qc.measure(0, 0)
    return qc


def measure_t1_t2(t1=100e-6, t2=80e-6, step=4e-6, max_steps=60, shots=3000) -> dict:
    nm = relaxation_noise(t1, t2, step)
    steps = np.arange(0, max_steps + 1, 5)
    times = steps * step
    p1 = np.array(
        [bit_probability(run_counts(t1_experiment(k, nm), shots, noise_model=nm), 0) for k in steps]
    )
    pr = np.array(
        [bit_probability(run_counts(ramsey_experiment(k), shots, noise_model=nm), 0) for k in steps]
    )  # P(1) in Ramsey = (1 - e^{-t/T2})/2
    (fit_t1,), _ = curve_fit(lambda t, T: np.exp(-t / T), times, p1, p0=[50e-6])
    (fit_t2,), _ = curve_fit(lambda t, T: 0.5 * (1 - np.exp(-t / T)), times, pr, p0=[50e-6])
    return {
        "times": times,
        "p1": p1,
        "ramsey": pr,
        "T1_set": t1,
        "T2_set": t2,
        "T1_fit": fit_t1,
        "T2_fit": fit_t2,
    }


def run_on_real_ibm(qc: QuantumCircuit, shots: int = 1000):  # pragma: no cover - needs network + account
    """Submit to the least-busy real IBM device.
    One-time setup:  QiskitRuntimeService.save_account(channel="ibm_quantum_platform", token="...")"""
    from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
    from qiskit_ibm_runtime import QiskitRuntimeService
    from qiskit_ibm_runtime.executor_sampler import Sampler  # non-deprecated client-side sampler

    service = QiskitRuntimeService()
    backend = service.least_busy(operational=True, simulator=False)
    isa = generate_preset_pass_manager(backend=backend, optimization_level=1).run(qc)
    result = Sampler(mode=backend).run([isa], shots=shots).result()
    reg = qc.cregs[0].name
    return backend.name, getattr(result[0].data, reg).get_counts()


def run(save_plots: bool = True, real: bool = False) -> dict:
    header(7, "Quantum hardware", "Physical qubits, real noise, real constraints")
    res = {}

    section("A. Vital signs of an IBM Heron chip (calibration snapshot)")
    v = device_vitals()
    res["vitals"] = v
    print(f"device {v['name']}  ·  {v['qubits']} qubits  ·  native gates {v['native_gates']}")
    print(f"median T1 {v['T1_us']:.0f} µs   median T2 {v['T2_us']:.0f} µs   CZ time {v['cz_time_ns']:.0f} ns")
    print(
        f"median errors: single-qubit {v['sx_error']:.1e}   CZ {v['cz_error']:.1e}   "
        f"readout {v['readout_error']:.1e}"
    )
    half_life = np.log(2) / v["cz_error"]
    print(
        f"=> about {v['T2_us'] * 1e3 / v['cz_time_ns']:.0f} CZ durations fit inside one T2, but at a "
        f"{v['cz_error']:.2%} CZ error rate a circuit\n   has <50% chance of being error-free after "
        f"~{half_life:.0f} CZ gates. Gate errors, not coherence time, are the binding limit."
    )

    section("B. Compilation onto the chip")
    bell = ghz(2)
    counts, tqc = run_on_device_model(bell)
    used = sorted({tqc.find_bit(q).index for inst in tqc.data for q in inst.qubits})
    print(f"Bell circuit compiled -> ops {dict(tqc.count_ops())}, physical qubits {used}")
    print(f"noisy Bell counts: {fmt_counts(counts)}  (01/10 shouldn't exist — that's noise)")
    res["bell_noisy"] = counts

    section("C. Ideal vs noisy as circuits grow (GHZ-n)")
    rows = []
    for n in (2, 4, 6, 8, 10, 12):
        ideal = ghz_success(run_counts(ghz(n), 2000), n)
        noisy = ghz_success(run_on_device_model(ghz(n))[0], n)
        rows.append((n, ideal, noisy))
        print(f"GHZ-{n:<2d}  ideal P(all-0 or all-1) = {ideal:.3f}   on noisy chip = {noisy:.3f}")
    res["ghz_rows"] = rows

    section("D. Decoherence: measure T1 and T2 yourself")
    d = measure_t1_t2()
    res["decoherence"] = d
    print(f"T1 set {d['T1_set'] * 1e6:.0f} µs -> fitted {d['T1_fit'] * 1e6:.1f} µs  (|1> decays to |0>)")
    print(
        f"T2 set {d['T2_set'] * 1e6:.0f} µs -> fitted {d['T2_fit'] * 1e6:.1f} µs  (superposition loses phase)"
    )

    section("E. Hardware landscape")
    for tech, ex, plus, minus in MODALITIES:
        print(f"{tech:16s} {ex:30s} + {plus}\n{'':47s} − {minus}")
    print(
        "Correction: Quantinuum (formerly Honeywell Quantum Solutions) is a trapped-ion company,\n"
        "not topological; the topological effort is Microsoft's."
    )

    if real:
        section("F. Real IBM hardware")
        name, real_counts = run_on_real_ibm(ghz(2))
        print(f"{name}: {fmt_counts(real_counts)}")
        res["real"] = (name, real_counts)

    if save_plots:
        _plot(res)
    return res


def _plot(res: dict) -> None:
    import matplotlib.pyplot as plt

    from qlab.plotting import MUTED, PALETTE, save

    fig, axes = plt.subplots(1, 2, figsize=(12, 3.6))
    rows = res["ghz_rows"]
    ns = [r[0] for r in rows]
    axes[0].plot(ns, [r[1] for r in rows], marker="o", color=MUTED, label="ideal simulator")
    axes[0].plot(ns, [r[2] for r in rows], marker="o", color=PALETTE[0], label="IBM Heron noise model")
    axes[0].set_ylim(0, 1.05)
    axes[0].set_xlabel("GHZ size (qubits)")
    axes[0].set_ylabel("P(correct outcome)")
    axes[0].set_title("Noise grows with circuit size")
    axes[0].legend(fontsize=8)
    d = res["decoherence"]
    t = d["times"] * 1e6
    fine = np.linspace(0, t.max(), 200)
    axes[1].scatter(t, d["p1"], color=PALETTE[2], s=18, label="T1: P(still |1⟩)")
    axes[1].plot(fine, np.exp(-fine / (d["T1_fit"] * 1e6)), color=PALETTE[2], lw=1.2)
    axes[1].scatter(t, d["ramsey"], color=PALETTE[1], s=18, label="T2 (Ramsey): P(1)")
    axes[1].plot(fine, 0.5 * (1 - np.exp(-fine / (d["T2_fit"] * 1e6))), color=PALETTE[1], lw=1.2)
    axes[1].set_xlabel("waiting time (µs)")
    axes[1].set_ylabel("probability")
    axes[1].set_title(f"Fitted T1={d['T1_fit'] * 1e6:.0f} µs, T2={d['T2_fit'] * 1e6:.0f} µs")
    axes[1].legend(fontsize=8)
    fig.suptitle("7 · Quantum hardware", fontweight="bold")
    save(fig, "07_hardware_noise.png")


if __name__ == "__main__":
    run(real="--real" in sys.argv)
