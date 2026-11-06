# Corrections to the "9 Quantum Computing Concepts" infographic

The infographic is a good map of the field, but its code samples were written
for an old Qiskit and several print results the circuits cannot produce. Every
item below was checked by running the circuit as printed on Qiskit 2.6.2 /
Aer 0.18.2; the bugs are locked in as regression tests in
`tests/test_infographic_claims.py`.

## Code that doesn't run or gives the wrong answer

| Card | What it says | What actually happens | Fix in this project |
|---|---|---|---|
| 1–6 | `from qiskit import QuantumCircuit, Aer, execute` | `ImportError`. `Aer` and `execute` were removed in Qiskit 1.0 (2024). Every sample on cards 1–6 fails on line one. | `from qiskit_aer import AerSimulator` then `sim.run(transpile(qc, sim)).result()` — see `qlab/backend.py` |
| 4 | H → X → measure prints `{'1': 1024}` | **~50/50.** H\|0⟩ = \|+⟩, and \|+⟩ is an eigenstate of X, so X does nothing visible. | `c04_gates.py` shows X alone → all 1s, and H → Z → H → all 1s (a phase flip made visible) |
| 5 | 2-qubit Grover prints `{'11': ~1024}` | **Returns `00` every time.** The diffuser gates are in the wrong order (H X H CZ H X instead of H X CZ X H). | `grover_2q_fixed()` returns `11` 1024/1024, plus a general n-qubit Grover |
| 7 | `service.backend("ibm_qasm_simulator")`; reads `result.quasi_dists`; 1-qubit circuit prints `{'0': ~0.5, '11': ~0.5}` | IBM retired its cloud simulators (and `ibm_oslo`) in 2024; `quasi_dists` was the V1 Sampler API, now removed; a 1-qubit circuit can't output the 2-bit string `11`. `SamplerV2` itself is deprecated as of qiskit-ibm-runtime 0.50. | Local runs on `FakeFez` (IBM Heron snapshot); real runs via `least_busy()` + `executor_sampler.Sampler` (`c07_hardware.py --real`) |
| 8 | 3-qubit bit-flip code; "most outcomes are 000 → error corrected" | **Always `010` — the error is never corrected.** There's no syndrome extraction onto ancillas and no correction step; the CNOTs just write parities onto a data qubit. | `bit_flip_code()` with 2 ancillas, mid-circuit measurement and `if_test` correction: 0% logical errors for every single X error on \|0⟩, \|1⟩ and a superposition |

## Concept statements worth sharpening

| Card | Claim | More accurate |
|---|---|---|
| 1 | "A qubit holds more information than a classical bit" | A qubit's state has continuous parameters, but you can extract **at most one classical bit** from it (Holevo bound). Advantage comes from interference across many qubits. |
| 1, 2 | "0, 1, or both at the same time"; "explores many solutions in parallel" | A superposition is a weighted sum with complex amplitudes. Measuring returns **one** outcome. Algorithms win by making wrong answers cancel through interference, not by reading out every branch. (`c02_superposition.py`, experiments B–D) |
| 3 | "Measuring one qubit instantly determines the other… links distant qubits instantly" | The correlation is real, but **no information travels**: Alice's qubit alone is perfectly random whatever Bob does (no-signaling). And matching outcomes alone are classically explainable — the non-classical part is the **CHSH violation** (S ≈ 2.83 > 2). (`c03_entanglement.py`) |
| 3 | Entanglement enables teleportation | True, but teleportation also needs **two classical bits** sent at light speed or slower. (`teleport()` uses mid-circuit measurement + feed-forward) |
| 5 | Shor solves factoring "exponentially faster" | Faster than any **known** classical algorithm (superpolynomially vs. the number field sieve); not proven to be exponentially faster than every possible classical algorithm. Grover's speed-up is quadratic, not exponential. |
| 7 | Topological examples: "Microsoft (Majorana), Quantinuum" | **Quantinuum is trapped-ion** (it's the former Honeywell Quantum Solutions, which the same card lists separately under ion traps). Topological qubits are Microsoft's effort and remain early-stage. |
| 7 | Photonic: "room temp, easy to scale" | Photons don't need cryogenic qubits, but leading photonic approaches use cryogenically cooled single-photon detectors, and photon loss makes scaling far from easy. |
| 9 | Google 2019: "first time a quantum computer outperformed the best supercomputer on a specific, **practical** task" | Random-circuit sampling was chosen because it's hard classically, **not** because it's useful. IBM disputed the 10,000-year figure (~2.5 days with more disk), and 2022 tensor-network simulations reproduced the task on GPUs in hours. Google's Oct 2025 "Quantum Echoes" result (Nature) is pitched as the first **verifiable** advantage. |

## How to see each fix yourself

```bash
pytest tests/test_infographic_claims.py -v     # the printed code, run as-is
python -m concepts.c04_gates                   # card 4 corrected
python -m concepts.c05_algorithms              # card 5 corrected
python -m concepts.c08_error_correction        # card 8 corrected
```
