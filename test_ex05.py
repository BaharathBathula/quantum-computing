import numpy as np
import pytest
from qiskit.quantum_info import Operator

from exercises.loader import load

ex = load("ex05_algorithms")


@pytest.mark.parametrize("n,marked", [(2, "11"), (2, "01"), (3, "101"), (3, "000"), (4, "0110")])
def test_oracle_is_a_phase_flip_on_the_marked_state(n, marked):
    qc = ex.oracle(n, marked)
    assert qc.num_qubits == n
    m = Operator(qc).data
    expected = np.eye(2**n, dtype=complex)
    expected[int(marked, 2), int(marked, 2)] = -1
    phase = m[0, 0] if int(marked, 2) != 0 else m[1, 1]  # allow a global phase
    assert np.allclose(m, phase * expected, atol=1e-9)


@pytest.mark.parametrize("n", [2, 3, 4])
def test_diffuser_is_reflection_about_uniform_state(n):
    N = 2**n
    s = np.full((N, 1), 1 / np.sqrt(N), dtype=complex)
    expected = 2 * s @ s.conj().T - np.eye(N)
    m = Operator(ex.diffuser(n)).data
    phase = m[0, 0] / expected[0, 0]
    assert np.allclose(m, phase * expected, atol=1e-9)


def test_optimal_iterations():
    assert ex.optimal_iterations(2) == 1
    assert ex.optimal_iterations(4) == 3
    assert ex.optimal_iterations(5) == 4
    assert ex.optimal_iterations(8) == 12


@pytest.mark.parametrize("n,marked", [(3, "110"), (4, "1001"), (5, "01110"), (6, "101010")])
def test_grover_finds_marked_item(counts, n, marked):
    qc = ex.grover(n, marked)
    assert qc.num_clbits == n
    c = counts(qc, 1000)
    assert c.get(marked, 0) / 1000 > 0.9


def test_too_many_iterations_overshoot(counts):
    n, marked = 4, "1010"
    good = counts(ex.grover(n, marked, 3), 1000).get(marked, 0)
    worse = counts(ex.grover(n, marked, 6), 1000).get(marked, 0)
    assert worse < good
