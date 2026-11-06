import numpy as np
import pytest
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

from exercises.loader import load

ex = load("ex01_qubits")


@pytest.mark.parametrize(
    "theta,phi", [(0, 0), (np.pi, 0), (np.pi / 2, 0), (np.pi / 2, np.pi / 2), (1.1, 2.3), (2.7, -0.4)]
)
def test_amplitudes_match_qiskit(theta, phi):
    a, b = ex.amplitudes(theta, phi)
    qc = QuantumCircuit(1)
    qc.ry(theta, 0)
    qc.rz(phi, 0)
    ref = Statevector(qc).data
    ref = (
        ref * np.exp(-1j * np.angle(ref[0])) if abs(ref[0]) > 1e-12 else ref * np.exp(-1j * np.angle(ref[1]))
    )
    if abs(ref[0]) < 1e-12:  # |1>: only |b| is meaningful
        assert abs(a) < 1e-9 and abs(abs(b) - 1) < 1e-9
    else:
        assert np.allclose([a, b], ref, atol=1e-9)
    assert abs(a) ** 2 + abs(b) ** 2 == pytest.approx(1)


@pytest.mark.parametrize("theta,phi", [(0.3, 0.0), (1.9, 1.2), (np.pi / 2, np.pi), (2.5, 4.0)])
def test_bloch_vector_is_unit_and_matches_angles(theta, phi):
    a, b = ex.amplitudes(theta, phi)
    v = np.asarray(ex.bloch_vector(a, b), dtype=float)
    assert v.shape == (3,)
    assert np.linalg.norm(v) == pytest.approx(1)
    expected = [np.sin(theta) * np.cos(phi), np.sin(theta) * np.sin(phi), np.cos(theta)]
    assert np.allclose(v, expected, atol=1e-9)


def test_measure_many_distribution_and_determinism():
    a, b = ex.amplitudes(2 * np.pi / 3, 0.0)  # P(1) = 0.75
    c = ex.measure_many(a, b, 4000, seed=1)
    assert set(c) <= {"0", "1"} and sum(c.values()) == 4000
    assert c.get("1", 0) / 4000 == pytest.approx(0.75, abs=0.03)
    assert ex.measure_many(a, b, 4000, seed=1) == c, "same seed must give the same counts"
    assert ex.measure_many(1, 0, 50) == {"0": 50, "1": 0} or ex.measure_many(1, 0, 50) == {"0": 50}
