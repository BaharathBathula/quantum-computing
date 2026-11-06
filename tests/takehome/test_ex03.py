import numpy as np
import pytest
from qiskit.quantum_info import Statevector

from exercises.loader import load

ex = load("ex03_entanglement")

BELL = {
    "phi+": [1, 0, 0, 1],
    "phi-": [1, 0, 0, -1],
    "psi+": [0, 1, 1, 0],
    "psi-": [0, 1, -1, 0],
}


@pytest.mark.parametrize("kind", list(BELL))
def test_bell_states(kind):
    sv = Statevector(ex.bell_state(kind))
    target = np.array(BELL[kind], dtype=complex) / np.sqrt(2)
    assert abs(abs(np.vdot(target, sv.data)) - 1) < 1e-9, f"{kind} is not the expected state (up to phase)"


def test_correlation():
    assert ex.correlation({"00": 500, "11": 500}) == pytest.approx(1.0)
    assert ex.correlation({"01": 300, "10": 700}) == pytest.approx(-1.0)
    assert ex.correlation({"00": 250, "11": 250, "01": 250, "10": 250}) == pytest.approx(0.0)


def test_chsh_value_formula():
    E = {("a", "b"): 0.7, ("a", "b'"): 0.7, ("a'", "b"): 0.7, ("a'", "b'"): -0.7}
    assert ex.chsh_value(E) == pytest.approx(2.8)


def test_chsh_angles_reach_tsirelson(counts):
    A = ex.chsh_angles()
    assert set(A) == {"a", "a'", "b", "b'"}
    E = {}
    for a in ("a", "a'"):
        for b in ("b", "b'"):
            E[(a, b)] = ex.correlation(counts(ex.chsh_circuit(A[a], A[b]), 4000))
    S = ex.chsh_value(E)
    assert abs(S) > 2.6, f"S={S:.3f}: angles do not violate the classical bound strongly enough"
