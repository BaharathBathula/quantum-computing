"""
Regression tests for the code printed on the infographic cards.

Each test runs the card's circuit EXACTLY as printed (ported only from the
removed `execute()` API to `AerSimulator.run()`), records what it really
does, and checks the corrected version in this project does what the card
claimed. See CORRECTIONS.md for the full write-up.
"""

import pytest
from qiskit import QuantumCircuit

from qlab.backend import probability, run_counts


def test_cards_1_to_6_imports_no_longer_exist():
    with pytest.raises(ImportError):
        from qiskit import execute  # noqa: F401
    with pytest.raises(ImportError):
        from qiskit import Aer  # noqa: F401


def test_card4_h_then_x_is_not_all_ones():
    qc = QuantumCircuit(1, 1)
    qc.h(0)
    qc.x(0)
    qc.measure(0, 0)
    counts = run_counts(qc, 4000)
    assert probability(counts, "1") == pytest.approx(0.5, abs=0.05)  # card claims {'1': 1024}


def test_card5_printed_grover_does_not_find_11():
    qc = QuantumCircuit(2, 2)
    qc.h([0, 1])
    qc.cz(0, 1)
    qc.h([0, 1])
    qc.x([0, 1])
    qc.h([0, 1])
    qc.cz(0, 1)
    qc.h([0, 1])
    qc.x([0, 1])
    qc.measure([0, 1], [0, 1])
    assert run_counts(qc, 1024) == {"00": 1024}  # card claims {'11': ~1024}

    from concepts.c05_algorithms import grover_2q_fixed

    assert run_counts(grover_2q_fixed(), 1024) == {"11": 1024}


def test_card8_printed_code_returns_the_error_uncorrected():
    qc = QuantumCircuit(3, 3)
    qc.barrier()
    qc.x(1)  # inject error
    qc.cx(0, 1)  # "majority vote"
    qc.cx(2, 1)
    qc.measure([0, 1, 2], [0, 1, 2])
    assert run_counts(qc, 1024) == {"010": 1024}  # card claims mostly '000'

    from concepts.c08_error_correction import bit_flip_code, logical_error_rate

    assert logical_error_rate(run_counts(bit_flip_code(1), 1024)) == 0


def test_card7_single_qubit_circuit_cannot_output_two_bits():
    qc = QuantumCircuit(1, 1)
    qc.h(0)
    qc.measure(0, 0)
    assert set(run_counts(qc, 1000)) == {"0", "1"}  # card prints {'0': ~0.5, '11': ~0.5}
