"""
Exercise 8 · The 3-qubit bit-flip code                      difficulty ★★  ~60 min

Protect one logical qubit against a single bit flip (X error) on any physical qubit.

1. `decode_syndrome(s01, s12)` - the two parity checks are
       s01 = parity(d0, d1)      s12 = parity(d1, d2)
   Return the index (0, 1 or 2) of the qubit to flip back, or None when no flip is
   detected.

2. `bit_flip_code(theta, error_on)` - a Qiskit circuit that
     - prepares the logical state ry(theta)|0> on data qubit d0 and ENCODES it into d0 d1 d2,
     - applies an X error on data qubit `error_on` (or nothing when None),
     - extracts the two parities onto two ANCILLA qubits with CNOTs and measures them
       into a 2-bit classical register named "syn" (bit 0 = s01, bit 1 = s12),
     - applies the correction conditionally on the syndrome (`with qc.if_test(...)`),
     - DECODES back onto d0, undoes the preparation with ry(−theta), and measures d0 into
       a 1-bit classical register named "out".
   If everything works, "out" reads 0 in 100 % of shots, for any theta and any error.

   Register layout the grader expects: QuantumRegister(3, "d"), QuantumRegister(2, "a"),
   ClassicalRegister(2, "syn"), ClassicalRegister(1, "out"), in that order.

3. `logical_error_rate(counts)` - from counts whose keys look like "out syn" (e.g. "0 01"),
   return the fraction of shots where out == 1.

Hints
- Encoding: cx(d0, d1); cx(d0, d2). Decoding is the same two gates in reverse order.
- `with qc.if_test((syn, 0b01)): qc.x(data[0])` applies X when the register equals 1.
  Remember the register value is read as an integer with bit 1 (s12) as the MSB.
"""

from __future__ import annotations

from qiskit import QuantumCircuit


def decode_syndrome(s01: int, s12: int) -> int | None:
    raise NotImplementedError


def bit_flip_code(theta: float, error_on: int | None) -> QuantumCircuit:
    raise NotImplementedError


def logical_error_rate(counts: dict[str, int]) -> float:
    raise NotImplementedError
