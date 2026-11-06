"""
Exercise 9 · Measuring advantage                            difficulty ★★  ~40 min

1. `statevector_bytes(n)` - bytes needed to store an n-qubit state as complex128
   amplitudes. Must be exact for large n (use Python ints, not floats).

2. `max_qubits_in(memory_bytes)` - the largest n whose state fits in that much memory.

3. `xeb_fidelity(samples, ideal_probs, n)` - linear cross-entropy benchmarking:
       F = 2^n · ⟨p_ideal(x)⟩_{x ~ samples} − 1
   where the average is over the sampled bitstrings (weighted by their counts).
   An ideal device scores ≈ 1, uniform random guessing scores ≈ 0.

4. `grover_speedup(N)` - ratio of classical expected checks (N/2) to Grover's
   iteration count floor(π/4 · √N), as a float.

Hints
- Bitstrings in `samples` and `ideal_probs` use the same n-character format.
- Missing keys in `ideal_probs` mean probability 0.
"""

from __future__ import annotations


def statevector_bytes(n: int) -> int:
    raise NotImplementedError


def max_qubits_in(memory_bytes: int) -> int:
    raise NotImplementedError


def xeb_fidelity(samples: dict[str, int], ideal_probs: dict[str, float], n: int) -> float:
    raise NotImplementedError


def grover_speedup(N: int) -> float:
    raise NotImplementedError
