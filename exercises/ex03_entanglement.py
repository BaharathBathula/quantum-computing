"""
Exercise 3 · Entanglement and the CHSH test                difficulty ★★  ~45 min

Part A. Build any of the four Bell states on demand.
    phi+ = (|00> + |11>)/√2      phi- = (|00> − |11>)/√2
    psi+ = (|01> + |10>)/√2      psi- = (|01> − |10>)/√2

Part B. The CHSH quantity. Alice measures along angle a or a', Bob along b or b'
(angles in the X–Z plane; measuring along angle t means `ry(-t)` then a Z measurement).
From the four correlation values E(a,b) = P(same) − P(different), compute
    S = E(a,b) + E(a,b') + E(a',b) − E(a',b').
Any local hidden-variable model has |S| ≤ 2. Choose angles that make a Bell pair
reach S ≈ 2√2.

Hints
- Starting from |00>, `x` on the right qubits before `h` + `cx` moves you between Bell states.
- For |phi+>, E(a, b) = cos(a − b). Pick angles so three cosines are +1/√2 and one is −1/√2.
"""

from __future__ import annotations

from qiskit import QuantumCircuit


def bell_state(kind: str) -> QuantumCircuit:
    """2 qubits, no measurement. kind in {'phi+', 'phi-', 'psi+', 'psi-'}."""
    raise NotImplementedError


def chsh_circuit(alice_angle: float, bob_angle: float) -> QuantumCircuit:
    """|phi+>, then measure qubit 0 along alice_angle and qubit 1 along bob_angle (2 classical bits)."""
    raise NotImplementedError


def correlation(counts: dict[str, int]) -> float:
    """E = P(outcomes equal) − P(outcomes differ) from 2-bit counts like {'00': 480, '11': 500, ...}."""
    raise NotImplementedError


def chsh_angles() -> dict[str, float]:
    """Return {'a': ..., "a'": ..., 'b': ..., "b'": ...} in radians, chosen so that S = 2√2 for |phi+>."""
    raise NotImplementedError


def chsh_value(E: dict[tuple[str, str], float]) -> float:
    """Combine E[(a,b)], E[(a,b')], E[(a',b)], E[(a',b')] into S."""
    raise NotImplementedError
