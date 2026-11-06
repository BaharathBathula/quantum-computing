"""
Generate and execute notebooks/tour.ipynb: all nine concepts with figures inline.

    python notebooks/make_tour.py        # writes tour.ipynb, then executes it in place
"""

from __future__ import annotations

import sys
from pathlib import Path

import nbformat
from nbclient import NotebookClient
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

ROOT = Path(__file__).resolve().parent.parent
OUT = Path(__file__).resolve().parent / "tour.ipynb"

CONCEPTS = [
    ("c01_qubits", "Qubits", "Amplitudes, the Born rule, Bloch vectors, and what one measurement can and cannot tell you."),
    ("c02_superposition", "Superposition", "H·H|0⟩ returns to 0 every time. A coin flipped twice does not. That difference is interference."),
    ("c03_entanglement", "Entanglement", "Bell states, the CHSH test (S ≈ 2.83 > 2), no-signaling, and teleportation."),
    ("c04_gates", "Quantum gates", "Unitary matrices, gate identities, and the infographic's H→X bug."),
    ("c05_algorithms", "Quantum algorithms", "Deutsch–Jozsa, Grover (with the overshoot curve), QFT period finding, VQE."),
    ("c06_circuits", "Quantum circuits", "Gate-by-gate state evolution, metrics, compiling for real wiring, OpenQASM 3."),
    ("c07_hardware", "Quantum hardware", "A real IBM Heron calibration snapshot, ideal vs noisy GHZ, measuring T1 and T2."),
    ("c08_error_correction", "Quantum error correction", "A working bit-flip code, the phase-flip code, and threshold behaviour."),
    ("c09_advantage", "Quantum advantage", "The 2ⁿ memory wall, measured simulation time, and cross-entropy benchmarking."),
]


def build() -> nbformat.NotebookNode:
    nb = new_notebook()
    nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
    nb.cells.append(
        new_markdown_cell(
            "# Quantum Computing in 9 Concepts — guided tour\n\n"
            "This notebook runs every concept module of the project and shows its figures inline. "
            "Each section is one `python -m concepts.cNN_...` command; the code lives in `concepts/`, "
            "and every printed claim is asserted in `tests/`.\n\n"
            "Run time: about one minute on a laptop. No cloud account needed."
        )
    )
    nb.cells.append(
        new_code_cell(
            "import sys, warnings\n"
            "from pathlib import Path\n"
            "ROOT = Path.cwd().parent if Path.cwd().name == 'notebooks' else Path.cwd()\n"
            "sys.path.insert(0, str(ROOT))\n"
            "warnings.filterwarnings('ignore', category=DeprecationWarning)\n"
            "from IPython.display import Image, display\n"
            "import qiskit, qiskit_aer\n"
            "print('qiskit', qiskit.__version__, '· qiskit-aer', qiskit_aer.__version__)"
        )
    )
    for i, (mod, title, blurb) in enumerate(CONCEPTS, start=1):
        nb.cells.append(new_markdown_cell(f"## {i}. {title}\n\n{blurb}"))
        nb.cells.append(
            new_code_cell(
                f"from concepts import {mod}\n"
                f"result = {mod}.run(save_plots=True)\n"
                f"for png in sorted((ROOT / 'outputs').glob('{i:02d}_*.png')):\n"
                f"    display(Image(filename=str(png), width=900))"
            )
        )
    nb.cells.append(
        new_markdown_cell(
            "## Where next\n\n"
            "- `CORRECTIONS.md` — what the infographic gets wrong, with evidence.\n"
            "- `exercises/` and `python grade.py` — nine autograded take-home exercises.\n"
            "- `web/quantum-lab.html` — the same experiments, interactive, in eight languages.\n"
            "- `CURRICULUM.md` — a nine-session course built on this code."
        )
    )
    return nb


def main(argv: list[str]) -> int:
    nb = build()
    OUT.parent.mkdir(exist_ok=True)
    nbformat.write(nb, OUT)
    if "--no-execute" not in argv:
        client = NotebookClient(nb, timeout=600, kernel_name="python3", resources={"metadata": {"path": str(ROOT)}})
        client.execute()
        nbformat.write(nb, OUT)
    print(f"wrote {OUT.relative_to(ROOT)} ({len(nb.cells)} cells)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
