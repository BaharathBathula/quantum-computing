"""
Exercise 7 · Noise, T1 and the error budget                difficulty ★★  ~40 min

1. `t1_from_decay(times, p_excited)` - a qubit was prepared in |1> and measured after
   waiting `times[i]` seconds; `p_excited[i]` is the fraction still found in |1>.
   The physics says p(t) = exp(−t / T1). Return the fitted T1 in seconds.
   (`scipy.optimize.curve_fit` or a linear fit of log p both work; data are noisy.)

2. `error_free_probability(gate_error, n_gates)` - if each gate independently fails with
   probability `gate_error`, the probability that none of `n_gates` gates fails.

3. `max_gates_for_success(gate_error, target)` - the largest number of gates whose
   error-free probability is still at least `target` (e.g. 0.5). Return an int ≥ 0.

4. `ghz_fidelity(counts, n)` - from counts of an n-qubit GHZ experiment, the fraction of
   shots that returned all-zeros or all-ones.

Hints
- Avoid taking log of zero: drop points with p ≤ 0 before a log-linear fit.
- For max_gates, solve (1 − e)^N ≥ target with logarithms; mind the direction of the
  inequality (both logs are negative), and handle gate_error = 0.
"""

from __future__ import annotations

from collections.abc import Sequence


def t1_from_decay(times: Sequence[float], p_excited: Sequence[float]) -> float:
    raise NotImplementedError


def error_free_probability(gate_error: float, n_gates: int) -> float:
    raise NotImplementedError


def max_gates_for_success(gate_error: float, target: float = 0.5) -> int:
    raise NotImplementedError


def ghz_fidelity(counts: dict[str, int], n: int) -> float:
    raise NotImplementedError
