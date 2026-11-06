import pytest
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Statevector
from qiskit.transpiler import CouplingMap

from exercises.loader import load

ex = load("ex06_circuits")


@pytest.mark.parametrize(
    "ops,expected",
    [
        ([], 0),
        ([(0,)], 1),
        ([(0,), (1,), (2,)], 1),
        ([(0,), (0,), (0,)], 3),
        ([(0,), (0, 1), (2,), (1, 2)], 3),
        ([(0, 1), (2, 3), (1, 2), (0,), (3,)], 2),
        ([(0, 1), (1, 2), (2, 3), (3, 4)], 4),
    ],
)
def test_depth(ops, expected):
    assert ex.depth(ops) == expected


def test_depth_agrees_with_qiskit_on_random_circuits():
    import random

    rng = random.Random(0)
    for _ in range(20):
        n, qc, ops = 5, QuantumCircuit(5), []
        for _ in range(25):
            if rng.random() < 0.5:
                q = rng.randrange(n)
                qc.h(q)
                ops.append((q,))
            else:
                a, b = rng.sample(range(n), 2)
                qc.cx(a, b)
                ops.append((a, b))
        assert ex.depth(ops) == qc.depth()


@pytest.mark.parametrize("n", [2, 4, 6])
def test_ghz_for_line_is_ghz_and_needs_no_swaps(n):
    qc = ex.ghz_for_line(n)
    p = Statevector(qc).probabilities_dict()
    assert p.get("0" * n, 0) == pytest.approx(0.5, abs=1e-9) and p.get("1" * n, 0) == pytest.approx(
        0.5, abs=1e-9
    )
    tq = transpile(
        qc,
        basis_gates=["rz", "sx", "x", "cz"],
        coupling_map=CouplingMap.from_line(n),
        initial_layout=list(range(n)),
        optimization_level=1,
        seed_transpiler=1,
    )
    assert tq.num_nonlocal_gates() == n - 1


def test_count_two_qubit_gates():
    qc = QuantumCircuit(3, 3)
    qc.h(0)
    qc.cx(0, 1)
    qc.cz(1, 2)
    qc.swap(0, 2)
    qc.barrier()
    qc.measure([0, 1, 2], [0, 1, 2])
    assert ex.count_two_qubit_gates(qc) == 3
