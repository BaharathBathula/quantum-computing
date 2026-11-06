# Interview guide

How to use this repository to screen and interview for quantum-adjacent roles:
quantum software engineers, research engineers, scientific-computing and data
engineers who will work next to a quantum team, and university or bootcamp
applicants.

Everything here runs offline with no cloud account, so the same material works in
Lagos, Bengaluru, São Paulo or Munich, on a laptop, in a browser, or inside the
provided Docker image.

## Three formats

| Format | Time | Material | What it tells you |
|---|---|---|---|
| **Phone screen** | 30 min | Question bank below, pick 5 | Conceptual grounding; can they explain, not just recite |
| **Take-home** | 2–4 h | `exercises/` + `python grade.py` | Can they turn physics into correct, tested code |
| **Pairing session** | 60 min | One concept module + the Quantum Lab | How they read, question and extend unfamiliar code |

### Take-home logistics

1. Send the candidate the repository (or the zip) and this instruction:
   > Implement the functions in `exercises/`. Run `python grade.py` to see your score.
   > Submit your `exercises/` folder. Use any resources you like, but write the code yourself.
2. Grade with `python grade.py` on their submission. CI-style, the autograder is in `tests/takehome/`.
3. Read the code, not just the score. The rubric below is what separates candidates
   with the same score.

The reference solutions live in `exercises/solutions/`. Delete that folder from the
copy you send out, or send only `exercises/ex0*.py` and `tests/takehome/`.

## Exercise map

| # | Exercise | Level | Time | Core skill probed | Strong signal |
|---|---|---|---|---|---|
| 1 | Qubits | ★ | 20 min | Complex amplitudes, Born rule, seeded simulation | Handles the global-phase convention without being told twice |
| 2 | Superposition | ★ | 20 min | Basis changes; knowing which data carries information | `distinguish` ignores the Z counts entirely |
| 3 | Entanglement & CHSH | ★★ | 45 min | Bell states, correlation functions, choosing measurement angles | Derives the angles from E = cos(a−b) instead of guessing |
| 4 | Gates as matrices | ★ | 25 min | Linear algebra, Qiskit's little-endian qubit order | Gets `controlled()` right on the first try; knows why the ordering matters |
| 5 | Grover from scratch | ★★★ | 90 min | Oracles, multi-controlled gates, amplitude amplification | Builds the oracle for any marked string, not just all-ones; explains overshoot |
| 6 | Circuits & wiring | ★★ | 45 min | Scheduling (depth), hardware connectivity, circuit introspection | Depth algorithm is O(gates), not a search; explains why fan-out costs SWAPs |
| 7 | Noise & error budget | ★★ | 40 min | Curve fitting, probability, logs with the inequality in the right direction | Drops p ≤ 0 before the log fit; handles `gate_error = 0` |
| 8 | Bit-flip code | ★★ | 60 min | Syndrome extraction, mid-circuit measurement, dynamic circuits | Correction via `if_test`; can say why you never measure the data qubits |
| 9 | Measuring advantage | ★★ | 40 min | Big integers, benchmarking statistics (XEB) | Uses Python ints for 2^100; explains what F_XEB ≈ 0 means |

A junior candidate should complete 1, 2, 4 and most of 9. A mid-level candidate should
complete everything except possibly 5. A senior candidate completes all nine and their
code reads like the reference solutions or better.

## Code-reading rubric (apply to any submission)

Score each line 0–2. Twelve or more out of sixteen is a strong submission.

| Criterion | 0 | 1 | 2 |
|---|---|---|---|
| Correctness | Autograder mostly fails | Passes with hacks (hard-coded values, catching all exceptions) | Passes for the right reasons |
| Physics in the code | Magic numbers | Comments name the gates | Docstrings explain *why* (e.g. "X on the zero bits turns the MCZ into an oracle for this string") |
| Edge cases | Ignored | Some handled | `theta = 0`, empty counts, `gate_error = 0`, n = 1 all handled |
| Numerical care | Floats where ints were needed, `==` on floats | Tolerances used | Tolerances chosen and justified; big integers where needed |
| Qiskit fluency | Fights the API | Uses it | Uses `Statevector`, `Operator`, `if_test`, registers idiomatically |
| Efficiency | Exponential where linear exists | Fine | Depth in one pass; no `Operator()` of a 10-qubit circuit |
| Tests of their own | None | Ran the grader | Added a test for a case the grader doesn't cover |
| Communication | No notes | Notes | A short README of decisions and what they'd do with more time |

## Phone-screen question bank

Each question maps to a concept module; the "listen for" column is the answer a strong
candidate gives in their own words. Run the module live if the conversation needs a
number.

### 1 · Qubits
- **Q:** A qubit has infinitely many states. How many bits can I get out of one? *Listen for:* one; Holevo bound; the extra structure shows up only through interference across many qubits.
- **Q:** What's the difference between a global phase and a relative phase? *Listen for:* global is unobservable; relative decides interference and shows up after a basis change.

### 2 · Superposition
- **Q:** H on |0⟩ gives 50/50. H twice gives always 0. A coin flipped twice is still 50/50. What's going on? *Listen for:* amplitudes add with signs; the two paths to |1⟩ cancel.
- **Q:** "A quantum computer tries all answers at once." Push back on that sentence. *Listen for:* one outcome per measurement; algorithms must arrange cancellation of wrong answers.

### 3 · Entanglement
- **Q:** Alice and Bob share a Bell pair. Can Alice send Bob a message by choosing what to measure? *Listen for:* no; Bob's local statistics are I/2 whatever Alice does; no-signaling.
- **Q:** Two envelopes with matching cards also "always agree". What experiment separates entanglement from that? *Listen for:* CHSH / Bell test; S ≤ 2 classically, 2√2 quantum.
- **Q:** Teleportation sends a qubit. Why isn't that faster than light? *Listen for:* two classical bits must travel first.

### 4 · Gates
- **Q:** Why must every gate be unitary? *Listen for:* preserves norm / probabilities; reversible; measurement is the only non-unitary step.
- **Q:** H then X then measure: what do you see? *Listen for:* 50/50; X|+⟩ = |+⟩. (The infographic this project corrects got this wrong.)
- **Q:** Name a universal gate set. *Listen for:* {H, T, CNOT} or {Clifford + T}; why T is the expensive one in fault-tolerant settings.

### 5 · Algorithms
- **Q:** Walk me through one Grover iteration geometrically. *Listen for:* oracle = reflection about the "bad" states; diffuser = reflection about the uniform state; two reflections = rotation by 2θ.
- **Q:** What happens if you run Grover for twice the optimal number of iterations? *Listen for:* overshoot; probability goes back down; it's periodic.
- **Q:** Is Grover an exponential speed-up? *Listen for:* no, quadratic; Shor's is superpolynomial over the best known classical.
- **Q:** What role does the QFT play in Shor's algorithm? *Listen for:* period finding; peaks at multiples of N/period.

### 6 · Circuits
- **Q:** Two circuits produce the same state. Why might one run much better on hardware? *Listen for:* connectivity, SWAP insertion, two-qubit gate count, depth vs coherence time.
- **Q:** What is circuit depth and why do we care? *Listen for:* critical path; must fit inside T2; parallelism.

### 7 · Hardware
- **Q:** T1 vs T2? *Listen for:* energy relaxation vs dephasing; T2 ≤ 2T1.
- **Q:** CZ error 0.4 %, 84 ns, T2 88 µs. What limits you first? *Listen for:* gate errors: ~175 gates to 50 % success, long before T2 runs out.
- **Q:** Pick two qubit technologies and compare one strength and one weakness each. *Listen for:* concrete, current facts (speed vs fidelity vs connectivity vs scale).

### 8 · Error correction
- **Q:** No-cloning says you can't copy a qubit. How can a repetition code work? *Listen for:* it entangles, not copies; syndrome measures parities, never the data.
- **Q:** What does "below threshold" mean? *Listen for:* adding qubits reduces logical error only when physical error is under the threshold; Willow 2024 showed it experimentally.
- **Q:** What does a bit-flip code miss? *Listen for:* phase (Z) errors; need a phase-flip code or Shor/surface codes for both.

### 9 · Advantage
- **Q:** Why is ~50 qubits a classical wall? *Listen for:* 2^n amplitudes × 16 bytes; 16 PiB at 50; but tensor networks exploit structure.
- **Q:** What was contested about Google's 2019 claim and how was it settled? *Listen for:* IBM's 2.5-day disk-based estimate; 2022 GPU tensor-network reproductions; moving target.
- **Q:** What would convince you a 2026 advantage claim is real? *Listen for:* verifiable output, a useful task, and classical baselines that experts had time to attack.

## Pairing session script (60 min)

1. (10 min) Candidate runs `python run_all.py 3` and explains the CHSH output.
2. (15 min) Ask them to change `CHSH_ANGLES` to something classical-looking and predict S before running.
3. (20 min) Open `concepts/c08_error_correction.py`. Ask: "Make this code survive a Z error." Watch whether they reach for the X basis.
4. (10 min) Open the Quantum Lab, section 5. Ask them to predict the amplitude bars after one more oracle step.
5. (5 min) Ask what they'd fix or test next in this repository. Good candidates find something real.

## Anti-patterns to watch for

- Circuits that cheat the grader with `qc.initialize(...)` for Grover (the matrix checks catch this).
- `optimization_level=3` on demonstration circuits: it cancels H·H before it ever runs.
- Claiming entanglement from agreement alone.
- Describing superposition as "both at once" with no mention of interference.
- Treating the 2019 "10,000 years" figure as settled fact.

## For candidates who are reading this

That's fine. Knowing what's being evaluated doesn't make the exercises easier; it tells
you what good work looks like. Do them properly and you'll be ready for a conversation
with anyone.
