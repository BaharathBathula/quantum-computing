# Curriculum: Quantum Computing in Nine Sessions

A course-in-a-box for universities, bootcamps, teacher-training programmes and
self-study groups anywhere. Everything runs on a laptop with no internet after
setup and no cloud account; the interactive lab is a single HTML file that opens
on a phone. Licence: MIT for the code; this document and the exercises may be
reused and adapted under the same terms with attribution.

| | |
|---|---|
| **Level** | Final-year undergraduate, early graduate, or working software engineers |
| **Prerequisites** | Linear algebra (vectors, matrices, complex numbers), Python basics, probability basics |
| **Length** | 9 sessions × 2 h (plus 2–4 h self-study each) — fits a half-semester, a 3-week bootcamp block, or 9 weekly meetups |
| **Format** | Each session: 30 min concept → 40 min live demo → 40 min lab → 10 min wrap-up |
| **Assessment** | Autograded exercises (`python grade.py`), one group project, one oral exam |
| **Languages** | Lab UI in English, Español, Português, Français, Deutsch, हिन्दी, 中文, 日本語 (more via `CONTRIBUTING.md`) |

## Setup for instructors (once, ~15 min)

```bash
pip install -e ".[dev]"           # or: docker build -t quantum-computing .
python run_all.py                 # all nine demos + figures in outputs/
pytest                            # must be green
python grade.py --solutions       # must be 9/9
```

Low-bandwidth classrooms: install once on one machine, then distribute the project
folder and the `pip wheel` cache on USB sticks. The lab (`web/quantum-lab.html`)
needs no server: open it directly from the file, or online at
https://baharathbathula.github.io/quantum-computing/. The only files that load from the
internet are two web fonts, and the page works without them.

Hardware access is optional: session 7 includes `--real` for IBM's free tier, but the
stored calibration snapshot teaches the same lessons offline.

## Session plan

Each session lists the learning objectives (what students can *do* afterwards), the
live demo, the lab task, a discussion prompt, and the exercise to assign.

### Session 1 · Qubits
- **Objectives:** write any single-qubit state as amplitudes and as a Bloch point; compute measurement probabilities; explain why one qubit yields at most one bit.
- **Demo:** `python -m concepts.c01_qubits`. Point out the NumPy simulator agreeing with Qiskit.
- **Lab:** Quantum Lab §1. Students find (θ, φ) for |i⟩ and for a state with P(1) = 0.9.
- **Discuss:** "A qubit holds infinite information." Where is that sentence right, and where is it wrong?
- **Assign:** Exercise 1 (★).

### Session 2 · Superposition and interference
- **Objectives:** predict H·H|0⟩; distinguish |+⟩ from |−⟩; explain interference as the source of quantum speed-ups.
- **Demo:** `c02_superposition` experiments A–D. Run D twice to show different bitstrings.
- **Lab:** Lab §2. Students build a 3-slot circuit that always gives 1 without using X.
- **Discuss:** rewrite the sentence "quantum computers try every answer at once" so that it is true.
- **Assign:** Exercise 2 (★).

### Session 3 · Entanglement
- **Objectives:** build all four Bell states; compute the CHSH value; state the no-signaling principle; describe teleportation's classical channel.
- **Demo:** `c03_entanglement`. Show Alice's reduced density matrix = I/2.
- **Lab:** Lab §3. Students find two angles where Alice and Bob *never* agree, then run CHSH three times and discuss the spread.
- **Discuss:** why do journalists say "instant communication" and why is it wrong?
- **Assign:** Exercise 3 (★★). Optional reading: the 2022 Nobel Prize citation (Aspect, Clauser, Zeilinger).

### Session 4 · Gates
- **Objectives:** verify unitarity; use gate identities (HXH = Z, T² = S); explain universality.
- **Demo:** `c04_gates`, especially the infographic's H→X bug.
- **Lab:** Lab §4. Students find a three-gate sequence that returns to |0⟩ and one that lands on |−i⟩.
- **Discuss:** why is T "expensive" in fault-tolerant computing and H "cheap"?
- **Assign:** Exercise 4 (★).

### Session 5 · Algorithms
- **Objectives:** run Deutsch–Jozsa, Grover, QFT period finding and VQE; explain each one's source of advantage; state the Grover iteration count.
- **Demo:** `c05_algorithms`. Show the overshoot curve.
- **Lab:** Lab §5. Students step through oracle/diffuser by hand for N = 4 and verify against the bars.
- **Discuss:** which of the four algorithms could matter for industry in five years, and why?
- **Assign:** Exercise 5 (★★★). Give two weeks.

### Session 6 · Circuits
- **Objectives:** read and write circuits; compute depth; compile for a hardware coupling map; export OpenQASM 3.
- **Demo:** `c06_circuits` — fan-out vs chain GHZ after compilation (13 vs 4 CZ).
- **Lab:** Lab §6. Students build a circuit where only q0 and q2 are entangled.
- **Discuss:** what should a compiler optimise for on today's hardware?
- **Assign:** Exercise 6 (★★).

### Session 7 · Hardware
- **Objectives:** define T1, T2, gate and readout errors; compute an error budget; compare qubit technologies with current facts.
- **Demo:** `c07_hardware`. Fit T1/T2 live. If internet allows, `--real` on IBM's free tier.
- **Lab:** Lab §7. Students find the gate error needed to run 10,000 CZ gates at 90 % success.
- **Discuss:** each student picks one company from the table and reports one 2025–26 result.
- **Assign:** Exercise 7 (★★).

### Session 8 · Error correction
- **Objectives:** explain syndrome measurement; implement the bit-flip code; describe threshold behaviour; state what the surface code adds.
- **Demo:** `c08_error_correction`. Show the phase error slipping through, then the X-basis fix.
- **Lab:** Lab §8. Students flip two qubits and explain why the decoder gets it wrong.
- **Discuss:** Google's 2024 "below threshold" result — what exactly was demonstrated?
- **Assign:** Exercise 8 (★★).

### Session 9 · Advantage
- **Objectives:** reason about 2ⁿ memory; describe XEB; give a fair account of advantage claims from 2019 to 2026.
- **Demo:** `c09_advantage`. Time the statevector simulation on the classroom machine.
- **Lab:** Lab §9. Students find the smallest n that doesn't fit on their own laptop.
- **Discuss (debate):** "Quantum advantage has been achieved." Two teams, 10 minutes each, judged on use of evidence.
- **Assign:** Exercise 9 (★★) and the group project.

## Group project (2–3 weeks, teams of 3)

Pick one:

1. **Shor's 9-qubit code.** Extend `c08` so that any single-qubit X, Z or Y error is corrected. Deliver tests like `tests/test_concepts.py`.
2. **Factor 15.** Replace `period_finding`'s prepared state with modular exponentiation and recover the factors from the measured period.
3. **Noise-aware compilation study.** For GHZ-n on the Heron snapshot, find the layout that maximises fidelity; report a plot.
4. **Translate and localise the lab** into a language not yet supported, with a native-speaker review, and submit it upstream.
5. **A tenth concept.** Quantum key distribution (BB84) as a module, a lab panel, an exercise and a page in `CORRECTIONS.md` style on what popular explanations get wrong.

Rubric: correctness (tests), physics explanation (README of the project), code quality
(ruff clean, idiomatic Qiskit), presentation (10 min).

## Oral exam (15 min per student)

Use the phone-screen bank in `INTERVIEW_GUIDE.md`: three questions from different
sessions, one of which asks the student to predict the output of a module before
running it.

## Mapping to existing courses

| Programme | Fits as |
|---|---|
| CS / Physics BSc | Elective "Introduction to Quantum Computing", 5 ECTS / 3 US credits |
| MSc Data Science or Engineering | Module inside "Advanced Computing Paradigms" |
| Coding bootcamp | 3-week capstone block |
| Teacher training (secondary) | Sessions 1–4 and 8, with the lab as the student-facing tool |
| Corporate upskilling | Sessions 1, 2, 5, 7, 9 as a 2-day workshop |

## Adapting for your country or institution

- **Language:** the lab's UI strings are plain JSON files (`web/i18n/`). Translating one
  takes a native speaker an afternoon.
- **Hardware:** if your institution has access to another vendor's devices, session 7's
  `run_on_real_ibm` is 15 lines; swapping in another provider's SDK is a good student task.
- **Accessibility:** the lab works with keyboard navigation and screen readers (ARIA labels
  on all controls), respects reduced-motion settings, and renders in light and dark mode.
- **Attribution:** keep the licence file and the corrections list; add your institution to
  the README's "Adopters" section via a pull request so others can find you.
