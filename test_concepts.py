"""Each concept's central claim, checked against simulation."""

import numpy as np
import pytest
from qiskit.quantum_info import Statevector

from concepts import (
    c01_qubits,
    c02_superposition,
    c03_entanglement,
    c04_gates,
    c05_algorithms,
    c06_circuits,
    c07_hardware,
    c08_error_correction,
    c09_advantage,
)
from qlab.backend import bit_probability, probability, run_counts


# 1 ---------------------------------------------------------------- qubits
@pytest.mark.parametrize("theta,phi", [(0, 0), (np.pi, 0), (np.pi / 2, 0), (1.0, 2.0), (2.5, -1.2)])
def test_qubit_normalised_and_on_bloch_sphere(theta, phi):
    a, b = c01_qubits.amplitudes(theta, phi)
    assert abs(a) ** 2 + abs(b) ** 2 == pytest.approx(1)
    assert np.linalg.norm(c01_qubits.bloch_vector(a, b)) == pytest.approx(1)


def test_plus_state_points_along_x():
    a, b = c01_qubits.amplitudes(np.pi / 2, 0)
    assert np.allclose(c01_qubits.bloch_vector(a, b), [1, 0, 0])


def test_measurement_probability_matches_born_rule():
    counts = run_counts(c01_qubits.prepare(2 * np.pi / 3, measure=True), 6000)
    assert bit_probability(counts, 0) == pytest.approx(0.75, abs=0.03)


# 2 ---------------------------------------------------------------- superposition
def test_double_hadamard_interferes_to_zero():
    assert run_counts(c02_superposition.double_hadamard(), 1000) == {"0": 1000}


def test_plus_and_minus_distinguishable_only_in_x_basis():
    for minus in (False, True):
        z = run_counts(c02_superposition.plus_or_minus(minus, False), 2000)
        assert probability(z, "1") == pytest.approx(0.5, abs=0.05)
        x = run_counts(c02_superposition.plus_or_minus(minus, True), 500)
        assert x == {("1" if minus else "0"): 500}


# 3 ---------------------------------------------------------------- entanglement
@pytest.mark.parametrize(
    "kind,allowed",
    [("phi+", {"00", "11"}), ("phi-", {"00", "11"}), ("psi+", {"01", "10"}), ("psi-", {"01", "10"})],
)
def test_bell_states_only_produce_correlated_outcomes(kind, allowed):
    assert set(run_counts(c03_entanglement.bell_pair(kind), 2000)) == allowed


def test_no_signaling_reduced_state_is_maximally_mixed():
    assert np.allclose(c03_entanglement.reduced_state_of_alice(), np.eye(2) / 2)


def test_chsh_violates_classical_bound():
    assert c03_entanglement.chsh_exact() == pytest.approx(2 * np.sqrt(2))
    S, _ = c03_entanglement.chsh(shots=4000)
    assert S > 2.6


@pytest.mark.parametrize("theta", [0.0, 0.8, np.pi / 2, 2.2, np.pi])
def test_teleportation_preserves_statistics(theta):
    counts = run_counts(c03_entanglement.teleport(theta), 4000)
    assert bit_probability(counts, 2) == pytest.approx(np.sin(theta / 2) ** 2, abs=0.035)


# 4 ---------------------------------------------------------------- gates
def test_all_gates_unitary_and_identities_hold():
    for g in c04_gates.GATE_LIBRARY.values():
        assert c04_gates.is_unitary(c04_gates.matrix(g))
    assert all(c04_gates.identities().values())


def test_cnot_truth_table():
    assert c04_gates.cnot_truth_table() == {"00": "00", "01": "11", "10": "10", "11": "01"}


def test_hzh_is_deterministic_one():
    assert run_counts(c04_gates.phase_kickback_demo(), 500) == {"1": 500}


# 5 ---------------------------------------------------------------- algorithms
def test_deutsch_jozsa():
    assert run_counts(c05_algorithms.deutsch_jozsa(4, "constant1"), 200) == {"0000": 200}
    assert "0000" not in run_counts(c05_algorithms.deutsch_jozsa(4, "balanced"), 200)


def test_fixed_two_qubit_grover_finds_11():
    assert run_counts(c05_algorithms.grover_2q_fixed(), 1024) == {"11": 1024}


@pytest.mark.parametrize("n,marked", [(3, "101"), (4, "0110"), (5, "11100")])
def test_grover_general(n, marked):
    p = Statevector(c05_algorithms.grover(n, marked, measure=False)).probabilities_dict()[marked]
    assert p > 0.9


def test_grover_overshoots():
    curve = c05_algorithms.grover_success_curve(4, "1010", 6)
    k = c05_algorithms.optimal_iterations(4)
    assert curve[k] > 0.9 and curve[2 * k] < curve[k]


def test_qft_period_finding_peaks_at_multiples():
    counts = run_counts(c05_algorithms.period_finding(5, period=4, offset=3), 2000)
    assert {int(b, 2) for b in counts} <= {0, 8, 16, 24}


def test_vqe_reaches_ground_state():
    e, exact, _ = c05_algorithms.vqe()
    assert e == pytest.approx(exact, abs=1e-3)


# 6 ---------------------------------------------------------------- circuits
def test_compiled_circuit_respects_hardware():
    tq = c06_circuits.compile_for_line(c06_circuits.ghz_fanout(5))
    assert set(tq.count_ops()) <= set(c06_circuits.HW_BASIS)
    for inst in tq.data:
        if inst.operation.num_qubits == 2:
            a, b = (tq.find_bit(q).index for q in inst.qubits)
            assert abs(a - b) == 1, "two-qubit gates only between neighbours on a line"


def test_chain_ghz_cheaper_than_fanout_after_compilation():
    fan = c06_circuits.compile_for_line(c06_circuits.ghz_fanout(5)).num_nonlocal_gates()
    chain = c06_circuits.compile_for_line(c06_circuits.ghz_chain(5)).num_nonlocal_gates()
    assert chain < fan


def test_compiled_ghz_still_makes_ghz():
    tq = c06_circuits.compile_for_line(c06_circuits.ghz_fanout(4), optimization_level=1)
    tq.measure_all()
    counts = run_counts(tq, 1000)
    assert set(counts) == {"0000", "1111"}


def test_qasm3_export():
    from qiskit import qasm3

    text = qasm3.dumps(c06_circuits.infographic_circuit())
    assert text.startswith("OPENQASM 3.0;") and "cx q[0], q[1];" in text


# 7 ---------------------------------------------------------------- hardware
def test_noise_degrades_ghz():
    counts, _ = c07_hardware.run_on_device_model(c07_hardware.ghz(6))
    assert c07_hardware.ghz_success(counts, 6) < 0.99


def test_t1_t2_recovered_from_simulated_experiments():
    d = c07_hardware.measure_t1_t2(shots=2000)
    assert d["T1_fit"] == pytest.approx(d["T1_set"], rel=0.15)
    assert d["T2_fit"] == pytest.approx(d["T2_set"], rel=0.15)


# 8 ---------------------------------------------------------------- error correction
@pytest.mark.parametrize("theta", [0.0, np.pi, 1.1])
@pytest.mark.parametrize("err", [None, 0, 1, 2])
def test_bit_flip_code_corrects_any_single_x_error(theta, err):
    counts = run_counts(c08_error_correction.bit_flip_code(err, theta), 500)
    assert c08_error_correction.logical_error_rate(counts) == 0


@pytest.mark.parametrize("err", [None, 0, 1, 2])
def test_phase_flip_code_corrects_any_single_z_error(err):
    qc = c08_error_correction.bit_flip_code(err, np.pi / 2, phase_error=True, basis="X")
    assert c08_error_correction.logical_error_rate(run_counts(qc, 500)) == 0


def test_bit_flip_code_cannot_fix_phase_errors():
    qc = c08_error_correction.bit_flip_code(1, np.pi / 2, phase_error=True)
    assert c08_error_correction.logical_error_rate(run_counts(qc, 500)) > 0.9


def test_more_distance_fewer_logical_errors_below_threshold():
    p = 0.1
    rates = [
        c08_error_correction.majority_failure(
            run_counts(
                c08_error_correction.repetition_memory(d),
                6000,
                noise_model=c08_error_correction.flip_noise(p),
            ),
            d,
        )
        for d in (1, 3, 5)
    ]
    assert rates[0] > rates[1] > rates[2]
    assert rates[1] == pytest.approx(c08_error_correction.analytic_failure(p, 3), abs=0.01)


# 9 ---------------------------------------------------------------- advantage
def test_statevector_memory():
    assert c09_advantage.statevector_bytes(30) == 16 * 2**30
    assert c09_advantage.human_bytes(c09_advantage.statevector_bytes(30)) == "16 GiB"


def test_xeb_orders_ideal_noisy_random():
    x = c09_advantage.xeb_experiment(n=6, cycles=8, shots=3000)
    assert x["ideal"] > x["noisy"] > x["uniform"]
    assert abs(x["uniform"]) < 0.15
