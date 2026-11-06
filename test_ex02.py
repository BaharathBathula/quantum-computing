import pytest

from exercises.loader import load

ex = load("ex02_superposition")


@pytest.mark.parametrize("minus", [False, True])
def test_z_basis_is_fifty_fifty(counts, minus):
    c = counts(ex.plus_minus_circuit(minus, "Z"), 2000)
    assert c.get("1", 0) / 2000 == pytest.approx(0.5, abs=0.05)


@pytest.mark.parametrize("minus,expect", [(False, "0"), (True, "1")])
def test_x_basis_is_deterministic(counts, minus, expect):
    assert counts(ex.plus_minus_circuit(minus, "X"), 500) == {expect: 500}


def test_interference_circuit(counts):
    qc = ex.interference_circuit()
    names = [inst.operation.name for inst in qc.data]
    assert qc.num_qubits == 1 and "h" in names and "x" not in names
    assert counts(qc, 500) == {"1": 500}


def test_distinguish():
    assert ex.distinguish({"0": 498, "1": 502}, {"0": 1000}) == "+"
    assert ex.distinguish({"0": 503, "1": 497}, {"1": 1000}) == "-"
    assert ex.distinguish({"1": 1000}, {"0": 980, "1": 20}) == "+"  # Z counts are a red herring
