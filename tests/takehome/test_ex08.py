import numpy as np
import pytest

from exercises.loader import load

ex = load("ex08_error_correction")


def test_decode_syndrome():
    assert ex.decode_syndrome(0, 0) is None
    assert ex.decode_syndrome(1, 0) == 0
    assert ex.decode_syndrome(1, 1) == 1
    assert ex.decode_syndrome(0, 1) == 2


def test_register_layout():
    qc = ex.bit_flip_code(0.3, None)
    assert [r.name for r in qc.qregs] == ["d", "a"] and [r.size for r in qc.qregs] == [3, 2]
    assert [r.name for r in qc.cregs] == ["syn", "out"] and [r.size for r in qc.cregs] == [2, 1]
    names = [inst.operation.name for inst in qc.data]
    assert "if_else" in names, "correction must be applied conditionally on the measured syndrome"


@pytest.mark.parametrize("theta", [0.0, np.pi, 1.1, np.pi / 2])
@pytest.mark.parametrize("error_on", [None, 0, 1, 2])
def test_any_single_flip_is_corrected(counts, theta, error_on):
    c = counts(ex.bit_flip_code(theta, error_on), 400)
    assert ex.logical_error_rate(c) == 0.0


def test_syndrome_points_at_the_flipped_qubit(counts):
    for error_on, expected_syn in ((0, "01"), (1, "11"), (2, "10")):
        c = counts(ex.bit_flip_code(0.0, error_on), 200)
        syns = {k.split()[1] for k in c}
        assert syns == {expected_syn}


def test_logical_error_rate():
    assert ex.logical_error_rate({"0 01": 900, "1 01": 100}) == pytest.approx(0.1)
    assert ex.logical_error_rate({"0 00": 50}) == 0.0
