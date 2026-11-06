"""The from-scratch NumPy simulator must agree with Qiskit, gate for gate."""

import numpy as np
import pytest
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

from qlab import StateVector
from qlab.statevector import rx, ry, rz


def qiskit_amps(qc: QuantumCircuit) -> np.ndarray:
    return Statevector(qc).data


def test_starts_in_all_zeros():
    sv = StateVector(3)
    assert sv.probabilities_dict() == {"000": 1.0}


@pytest.mark.parametrize("gate", ["h", "x", "y", "z", "s", "t"])
@pytest.mark.parametrize("target", [0, 1, 2])
def test_single_qubit_gates_match_qiskit(gate, target):
    ours = StateVector(3).h(0).h(1).h(2).t(1)  # a non-trivial starting state
    getattr(ours, gate)(target)
    qc = QuantumCircuit(3)
    qc.h([0, 1, 2])
    qc.t(1)
    getattr(qc, gate)(target)
    assert np.allclose(ours.amps, qiskit_amps(qc))


@pytest.mark.parametrize("control,target", [(0, 1), (1, 0), (0, 2), (2, 0), (1, 2), (2, 1)])
def test_cnot_and_cz_match_qiskit(control, target):
    for name in ("cx", "cz"):
        ours = StateVector(3).h(0).h(1).h(2).t(0).s(2)
        getattr(ours, name)(control, target)
        qc = QuantumCircuit(3)
        qc.h([0, 1, 2])
        qc.t(0)
        qc.s(2)
        getattr(qc, name)(control, target)
        assert np.allclose(ours.amps, qiskit_amps(qc)), name


def test_rotations_match_qiskit():
    ours = StateVector(2).apply(rx(0.3), 0).apply(ry(1.1), 1).apply(rz(-0.7), 0)
    qc = QuantumCircuit(2)
    qc.rx(0.3, 0)
    qc.ry(1.1, 1)
    qc.rz(-0.7, 0)
    assert np.allclose(ours.amps, qiskit_amps(qc))


def test_random_circuits_match_qiskit():
    rng = np.random.default_rng(0)
    for _ in range(25):
        n = int(rng.integers(2, 6))
        ours, qc = StateVector(n), QuantumCircuit(n)
        for _ in range(30):
            kind = rng.choice(["h", "x", "t", "s", "cx", "cz", "ry"])
            if kind in ("cx", "cz"):
                c, t = rng.choice(n, 2, replace=False)
                getattr(ours, kind)(int(c), int(t))
                getattr(qc, kind)(int(c), int(t))
            elif kind == "ry":
                q, th = int(rng.integers(n)), float(rng.uniform(0, 6.28))
                ours.apply(ry(th), q)
                qc.ry(th, q)
            else:
                q = int(rng.integers(n))
                getattr(ours, kind)(q)
                getattr(qc, kind)(q)
        assert np.allclose(ours.amps, qiskit_amps(qc))
        assert np.isclose(np.sum(ours.probabilities()), 1.0)


def test_bell_state_and_sampling():
    sv = StateVector(2, seed=1).h(0).cx(0, 1)
    assert sv.probabilities_dict() == pytest.approx({"00": 0.5, "11": 0.5})
    counts = sv.sample_counts(2000)
    assert set(counts) == {"00", "11"}


def test_measurement_collapses_entangled_partner():
    for seed in range(10):
        sv = StateVector(2, seed=seed).h(0).cx(0, 1)
        a = sv.measure(0)
        b = sv.measure(1)
        assert a == b  # measuring one Bell qubit fixes the other
