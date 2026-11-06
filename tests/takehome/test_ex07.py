import numpy as np
import pytest

from exercises.loader import load

ex = load("ex07_hardware")


def test_t1_fit_recovers_known_value():
    rng = np.random.default_rng(0)
    T1 = 120e-6
    t = np.linspace(0, 400e-6, 25)
    p = np.exp(-t / T1) + rng.normal(0, 0.01, t.size)
    assert ex.t1_from_decay(t, p) == pytest.approx(T1, rel=0.1)


def test_t1_fit_tolerates_zero_points():
    t = np.array([0, 1, 2, 3, 50], dtype=float)
    p = np.array([1.0, np.exp(-1), np.exp(-2), np.exp(-3), 0.0])
    assert ex.t1_from_decay(t, p) == pytest.approx(1.0, rel=0.05)


def test_error_free_probability():
    assert ex.error_free_probability(0.0, 1000) == pytest.approx(1.0)
    assert ex.error_free_probability(0.01, 100) == pytest.approx(0.99**100)
    assert ex.error_free_probability(0.5, 3) == pytest.approx(0.125)


def test_max_gates_for_success():
    e = 0.0039
    n = ex.max_gates_for_success(e, 0.5)
    assert isinstance(n, int)
    assert (1 - e) ** n >= 0.5 > (1 - e) ** (n + 1)
    assert ex.max_gates_for_success(0.5, 0.5) == 1
    assert ex.max_gates_for_success(0.9, 0.5) == 0
    assert ex.max_gates_for_success(0.0, 0.5) > 1_000_000


def test_ghz_fidelity():
    assert ex.ghz_fidelity({"000": 450, "111": 450, "010": 100}, 3) == pytest.approx(0.9)
    assert ex.ghz_fidelity({"01": 10}, 2) == 0.0
