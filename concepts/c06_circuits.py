"""
6. QUANTUM CIRCUITS — programs for quantum computers.

A circuit is gates on wires, read left to right, ending in measurements.
This module shows the full life of a circuit:
  A. Build the circuit from the infographic (H, CNOT, Rz, X, measure)
  B. Step through it gate by gate and watch the state vector change
  C. Inspect its metrics: depth, size, two-qubit gate count
  D. Compile ("transpile") it for real hardware wiring: same algorithm,
     very different cost — circuit design matters
  E. Export to OpenQASM 3, the portable text format hardware accepts

Run:  python -m concepts.c06_circuits
"""

from __future__ import annotations

import numpy as np
from qiskit import QuantumCircuit, qasm3, transpile
from qiskit.quantum_info import Statevector
from qiskit.transpiler import CouplingMap

from qlab.backend import fmt_counts, header, run_counts, section

THETA = np.pi / 3


def infographic_circuit(theta: float = THETA, measure: bool = True) -> QuantumCircuit:
    qc = QuantumCircuit(2, 2 if measure else 0, name="card6")
    qc.h(0)
    qc.cx(0, 1)
    qc.rz(theta, 0)
    qc.x(1)
    if measure:
        qc.measure([0, 1], [0, 1])
    return qc


def step_through(qc: QuantumCircuit) -> list[tuple[str, dict[str, complex]]]:
    """State after each instruction (measurements skipped)."""
    steps = []
    state = Statevector.from_label("0" * qc.num_qubits)
    steps.append(("start", _amps(state)))
    for inst in qc.data:
        if inst.operation.name in ("measure", "barrier"):
            continue
        sub = QuantumCircuit(qc.num_qubits)
        sub.append(inst.operation, [qc.find_bit(q).index for q in inst.qubits])
        state = state.evolve(sub)
        qs = ",".join(str(qc.find_bit(q).index) for q in inst.qubits)
        steps.append((f"{inst.operation.name}({qs})", _amps(state)))
    return steps


def _amps(sv: Statevector) -> dict[str, complex]:
    return {k: complex(v) for k, v in sv.to_dict().items() if abs(v) > 1e-9}


def metrics(qc: QuantumCircuit) -> dict:
    return {
        "qubits": qc.num_qubits,
        "depth": qc.depth(),
        "size": qc.size(),
        "two_qubit_gates": qc.num_nonlocal_gates(),
        "ops": dict(qc.count_ops()),
    }


def ghz_fanout(n: int) -> QuantumCircuit:
    """GHZ written naively: qubit 0 talks to everyone (fine on paper, bad on a chain)."""
    qc = QuantumCircuit(n)
    qc.h(0)
    for t in range(1, n):
        qc.cx(0, t)
    return qc


def ghz_chain(n: int) -> QuantumCircuit:
    """Same state, but each CNOT only touches neighbours."""
    qc = QuantumCircuit(n)
    qc.h(0)
    for q in range(n - 1):
        qc.cx(q, q + 1)
    return qc


HW_BASIS = ["rz", "sx", "x", "cz"]  # native gates of IBM Heron processors


def compile_for_line(qc: QuantumCircuit, optimization_level: int = 1) -> QuantumCircuit:
    n = qc.num_qubits
    return transpile(
        qc,
        basis_gates=HW_BASIS,
        coupling_map=CouplingMap.from_line(n),
        initial_layout=list(range(n)),
        optimization_level=optimization_level,
        seed_transpiler=7,
    )


def run(save_plots: bool = True) -> dict:
    header(6, "Quantum circuits", "Gates on wires: the programs of quantum computing")
    res = {}

    section("A. The circuit")
    qc = infographic_circuit()
    print(qc.draw("text"))

    section("B. State vector after each gate")
    steps = step_through(qc)
    res["steps"] = steps
    for name, amps in steps:
        pretty = "  ".join(f"{a.real:+.3f}{a.imag:+.3f}j|{k}>" for k, a in amps.items())
        print(f"{name:10s} {pretty}")
    res["counts"] = run_counts(qc, 2000)
    print(f"measured: {fmt_counts(res['counts'])}   (Rz only adds phase, so probabilities stay 50/50)")

    section("C. Metrics")
    res["metrics"] = metrics(qc)
    print(res["metrics"])

    section("D. Compiling for real wiring (5 qubits in a line, native gates rz/sx/x/cz)")
    n = 5
    rows = {}
    for label, circ in (("fan-out GHZ", ghz_fanout(n)), ("chain GHZ", ghz_chain(n))):
        tq = compile_for_line(circ)
        rows[label] = {"logical": metrics(circ), "compiled": metrics(tq)}
        print(
            f"{label:12s} logical depth {circ.depth():2d}, 2q gates {circ.num_nonlocal_gates():2d}"
            f"  ->  compiled depth {tq.depth():2d}, 2q gates {tq.num_nonlocal_gates():2d}"
            f"  ops {dict(tq.count_ops())}"
        )
    res["compile"] = rows
    print(
        "Same quantum state; the fan-out version needs SWAPs (3 CZ-equivalents each) because\n"
        "qubit 0 isn't wired to qubit 4. On noisy hardware fewer 2-qubit gates = better results."
    )

    section("E. OpenQASM 3 export")
    qasm = qasm3.dumps(qc)
    res["qasm"] = qasm
    print(qasm)

    if save_plots:
        _plot(qc, rows)
    return res


def _plot(qc: QuantumCircuit, rows: dict) -> None:
    import matplotlib.pyplot as plt

    from qlab.plotting import PALETTE, save

    try:
        fig = qc.draw("mpl", style="clifford")
        save(fig, "06_circuit_diagram.png")
    except Exception as exc:  # pylatexenc missing etc.
        print(f"(skipping mpl circuit drawing: {exc})")

    fig, ax = plt.subplots(figsize=(6.5, 3.2))
    labels = list(rows)
    x = np.arange(len(labels))
    logical = [rows[k]["logical"]["two_qubit_gates"] for k in labels]
    compiled = [rows[k]["compiled"]["two_qubit_gates"] for k in labels]
    ax.bar(x - 0.18, logical, 0.36, label="as written", color=PALETTE[5])
    ax.bar(x + 0.18, compiled, 0.36, label="compiled for a line of qubits", color=PALETTE[2])
    ax.set_xticks(x, labels)
    ax.set_ylabel("two-qubit gates")
    ax.set_title("6 · Same state, different cost after compilation")
    ax.legend(fontsize=8)
    save(fig, "06_compilation_cost.png")


if __name__ == "__main__":
    run()
