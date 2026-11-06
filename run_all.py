"""
Run all 9 concept modules in order, save every figure to outputs/,
and write outputs/summary.md with the key numbers.

    python run_all.py            # everything (~1 minute)
    python run_all.py 3 5 8      # just concepts 3, 5 and 8
    python run_all.py --no-plots
"""

from __future__ import annotations

import sys
import time
import warnings
from pathlib import Path

warnings.filterwarnings("ignore", category=DeprecationWarning)

from concepts import (  # noqa: E402
    c01_qubits,
    c02_superposition,
    c03_entanglement,
    c04_gates,
    c05_algorithms,
    c06_circuits,
    c07_hardware,
    c08_error_correction,
    c09_advantage,
)

MODULES = {
    1: ("Qubits", c01_qubits),
    2: ("Superposition", c02_superposition),
    3: ("Entanglement", c03_entanglement),
    4: ("Quantum gates", c04_gates),
    5: ("Quantum algorithms", c05_algorithms),
    6: ("Quantum circuits", c06_circuits),
    7: ("Quantum hardware", c07_hardware),
    8: ("Quantum error correction", c08_error_correction),
    9: ("Quantum advantage", c09_advantage),
}


def headline(i: int, r: dict) -> str:
    """One line per concept for the summary table."""
    try:
        if i == 1:
            return f"120° state measured P(1) = {r['tilted_p1']:.3f} (theory 0.750)"
        if i == 2:
            return f"H·H|0⟩ gives 0 with probability {r['p0_double_h']:.3f} (interference)"
        if i == 3:
            return f"CHSH S = {r['chsh_S']:.3f} > 2 (classical limit)"
        if i == 4:
            t = sum(r["h_then_x"].values())
            return f"H→X→measure gives P(1) = {r['h_then_x'].get('1', 0) / t:.2f}, not 1.00"
        if i == 5:
            e, ex = r["vqe"]
            return f"Grover 2q finds |11⟩ {r['grover_2q'].get('11', 0)}/1024 · VQE error {abs(e - ex):.1e}"
        if i == 6:
            c = r["compile"]
            return (
                f"GHZ-5 on a line: fan-out {c['fan-out GHZ']['compiled']['two_qubit_gates']} CZ "
                f"vs chain {c['chain GHZ']['compiled']['two_qubit_gates']} CZ"
            )
        if i == 7:
            d = r["decoherence"]
            return (
                f"T1 fit {d['T1_fit'] * 1e6:.0f} µs, T2 fit {d['T2_fit'] * 1e6:.0f} µs · "
                f"GHZ-12 on Heron model {r['ghz_rows'][-1][2]:.2f}"
            )
        if i == 8:
            ps, curves = r["threshold"]
            k = ps.index(0.1)
            return f"at p=0.10: d=1 → {curves[1][k]:.3f}, d=7 → {curves[7][k]:.4f} logical error"
        if i == 9:
            x = r["xeb"]
            return f"XEB ideal {x['ideal']:+.2f} · noisy {x['noisy']:+.2f} · random {x['uniform']:+.2f}"
    except Exception as exc:  # summary must never crash the run
        return f"(summary unavailable: {exc})"
    return ""


def main(argv: list[str]) -> int:
    plots = "--no-plots" not in argv
    picks = [int(a) for a in argv if a.isdigit()] or list(MODULES)
    rows = []
    t_all = time.perf_counter()
    for i in picks:
        name, mod = MODULES[i]
        t0 = time.perf_counter()
        result = mod.run(save_plots=plots)
        rows.append((i, name, headline(i, result), time.perf_counter() - t0))

    out = Path(__file__).parent / "outputs"
    out.mkdir(exist_ok=True)
    lines = ["# Run summary", "", "| # | Concept | Key result | Time |", "|---|---|---|---|"]
    lines += [f"| {i} | {n} | {h} | {t:.1f}s |" for i, n, h, t in rows]
    (out / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("\n" + "=" * 72 + "\n  SUMMARY\n" + "=" * 72)
    for i, n, h, _t in rows:
        print(f"{i}. {n:26s} {h}")
    print(f"\nDone in {time.perf_counter() - t_all:.0f}s. Figures + summary.md in {out}/")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
