import numpy as np
import pytest
from qiskit.circuit.library import CXGate, CZGate, HGate, SGate, TGate, XGate, YGate, ZGate
from qiskit.quantum_info import Operator

from exercises.loader import load

ex = load("ex04_gates")
REF = {"X": XGate(), "Y": YGate(), "Z": ZGate(), "H": HGate(), "S": SGate(), "T": TGate()}


@pytest.mark.parametrize("name", list(REF))
def test_gate_matrices(name):
    assert np.allclose(ex.gate_matrix(name), Operator(REF[name]).data)


def test_identity_and_unitarity():
    assert np.allclose(ex.gate_matrix("I"), np.eye(2))
    for name in REF:
        assert ex.is_unitary(ex.gate_matrix(name))
    assert not ex.is_unitary(np.array([[1, 1], [0, 1]]))
    assert not ex.is_unitary(2 * np.eye(2))


def test_controlled_matches_qiskit_ordering():
    assert np.allclose(ex.controlled(ex.gate_matrix("X")), Operator(CXGate()).data)
    assert np.allclose(ex.controlled(ex.gate_matrix("Z")), Operator(CZGate()).data)
    assert ex.is_unitary(ex.controlled(ex.gate_matrix("H")))


def test_global_phase():
    H = ex.gate_matrix("H")
    assert ex.equal_up_to_global_phase(H, np.exp(1j * 0.7) * H)
    assert ex.equal_up_to_global_phase(-1j * ex.gate_matrix("X"), ex.gate_matrix("X"))
    assert not ex.equal_up_to_global_phase(ex.gate_matrix("X"), ex.gate_matrix("Z"))
    assert not ex.equal_up_to_global_phase(H, 2 * H), "a scale factor is not a phase"
