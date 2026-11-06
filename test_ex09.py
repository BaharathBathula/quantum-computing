import math

import numpy as np
import pytest
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

from exercises.loader import load

ex = load("ex09_advantage")


def test_statevector_bytes_exact():
    assert ex.statevector_bytes(1) == 32
    assert ex.statevector_bytes(30) == 16 * 2**30
    assert ex.statevector_bytes(100) == 16 * 2**100  # exact big integer, no float rounding
    assert isinstance(ex.statevector_bytes(100), int)


def test_max_qubits_in():
    assert ex.max_qubits_in(16 * 2**30) == 30
    assert ex.max_qubits_in(16 * 2**30 - 1) == 29
    assert ex.max_qubits_in(8e9) == 28


def test_xeb_ideal_vs_uniform():
    n = 6
    rng = np.random.default_rng(2)
    qc = QuantumCircuit(n)
    for layer in range(6):
        for q in range(n):
            qc.r(np.pi / 2, rng.choice([0, np.pi / 2, np.pi / 4]), q)
        for q in range(layer % 2, n - 1, 2):
            qc.cz(q, q + 1)
    probs = Statevector(qc).probabilities_dict()
    keys = list(probs)
    p = np.array([probs[k] for k in keys])
    ideal_samples = dict(zip(keys, np.random.default_rng(3).multinomial(20000, p)))
    uniform_samples = dict(
        zip(keys, np.random.default_rng(4).multinomial(20000, np.full(len(keys), 1 / len(keys))))
    )
    f_ideal, f_uniform = ex.xeb_fidelity(ideal_samples, probs, n), ex.xeb_fidelity(uniform_samples, probs, n)
    assert f_ideal > 0.8 and abs(f_uniform) < 0.15 and f_ideal > f_uniform


def test_xeb_handles_missing_keys():
    assert ex.xeb_fidelity({"00": 10, "11": 10}, {"00": 1.0}, 2) == pytest.approx(4 * 0.5 - 1)


def test_grover_speedup():
    assert ex.grover_speedup(16) == pytest.approx(8 / 3)
    assert ex.grover_speedup(10**6) == pytest.approx(500_000 / math.floor(math.pi / 4 * 1000))
