import os
import pytest
import numpy as np
import pandas as pd
from panqec.analysis import (
    get_subthreshold_fit_function, get_single_qubit_error_rate, Analysis,
    deduce_bias
)
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


def test_subthreshold_cubic_fit_function():
    C_0, C_1, C_2, C_3 = 0, 1, 2, 1
    log_p_L_th, log_p_th = np.log(0.5), np.log(0.5)

    subthreshold_fit_function = get_subthreshold_fit_function(order=3)

    p = 0.5
    L = 10
    log_p_L = subthreshold_fit_function(
        (np.log(p), L),
        log_p_L_th, log_p_th, C_0, C_1, C_2, C_3
    )
    assert log_p_L == np.log(0.5)


class TestGetSingleQubitErrorRates:

    def test_trivial(self):
        effective_error_list = []
        p_est, p_se = get_single_qubit_error_rate(effective_error_list)
        assert np.isnan(p_est) and np.isnan(p_se)

    def test_simple_example(self):
        effective_error_list = [
            [0, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 0, 0],
            [1, 0, 0, 1, 0, 0],
            [1, 0, 0, 1, 0, 0],
            [0, 0, 0, 1, 0, 0],
            [0, 0, 0, 1, 0, 0],
            [0, 0, 0, 1, 0, 0],
        ]

        n_results = len(effective_error_list)
        assert n_results == 7

        # Rate of any error occuring should be 3/4.
        p_est, p_se = get_single_qubit_error_rate(effective_error_list, i=0)
        assert np.isclose(p_est, (n_results - 1)/n_results)

        # Probability of each error type occuring should be based on count.
        p_x, p_x_se = get_single_qubit_error_rate(
            effective_error_list, i=0, error_type='X'
        )
        assert np.isclose(p_x, 1/n_results)

        p_y, p_y_se = get_single_qubit_error_rate(
            effective_error_list, i=0, error_type='Y'
        )
        assert np.isclose(p_y, 2/n_results)

        p_z, p_z_se = get_single_qubit_error_rate(
            effective_error_list, i=0, error_type='Z'
        )
        assert np.isclose(p_z, 3/n_results)

    def test_simple_example_on_2nd_qubit(self):
        effective_error_list = [
            [0, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0],
            [0, 1, 0, 0, 1, 0],
            [0, 1, 0, 0, 1, 0],
            [0, 0, 0, 0, 1, 0],
            [0, 0, 0, 0, 1, 0],
            [0, 0, 0, 0, 1, 0],
        ]

        # Rate of any error occuring should be 3/4.
        p_est, p_se = get_single_qubit_error_rate(effective_error_list, i=1)
        assert np.isclose(p_est, 6/7)
        assert np.isclose(p_se, np.sqrt((6/7)*(1 - (6/7))/(7 + 1)))

        # Probability of each error type occuring should be based on count.
        p_x, p_x_se = get_single_qubit_error_rate(
            effective_error_list, i=1, error_type='X'
        )
        assert np.isclose(p_x, 1/7)
        assert np.isclose(p_x_se, np.sqrt(p_x*(1 - p_x)/(7 + 1)))

        p_y, p_y_se = get_single_qubit_error_rate(
            effective_error_list, i=1, error_type='Y'
        )
        assert np.isclose(p_y, 2/7)

        p_z, p_z_se = get_single_qubit_error_rate(
            effective_error_list, i=1, error_type='Z'
        )
        assert np.isclose(p_z, 3/7)


class TestAnalysis:

    def test_analyse_toric_2d_results(self):
        results_path = os.path.join(DATA_DIR, 'toric')
        assert os.path.exists(results_path)
        analysis = Analysis(results_path)
        analysis.analyze()
        assert analysis.results.shape == (30, 24)
        assert set(analysis.results.columns) == set([
            'size', 'code', 'n', 'k', 'd', 'error_model', 'decoder',
            'probability', 'wall_time', 'n_trials', 'n_fail',
            'effective_error', 'success', 'codespace', 'bias', 'results_file',
            'p_est', 'p_se', 'p_word_est', 'p_word_se', 'single_qubit_p_est',
            'single_qubit_p_se', 'code_family', 'error_model_family'
        ])
        assert set(analysis.thresholds.columns).issuperset([
            'code_family', 'error_model', 'decoder',
            'p_th_fss', 'p_th_fss_left', 'p_th_fss_right'
        ])
        assert set(analysis.trunc_results).issuperset(analysis.results.columns)
        assert 'rescaled_p' in analysis.trunc_results

    def test_apply_overrides(self):
        analysis = Analysis()
        assert not analysis.overrides
        analysis.results = pd.DataFrame([
          {
            'code_family': 'Toric',
            'error_model': 'Deformed XZZX Pauli X0.0005Y0.0005Z0.9990',
            'decoder': 'BP-OSD decoder',
            'bias': 1000,
            'code': 'Toric 9x9x9',
            'probability': 0.18
          },
          {
            'code_family': 'Toric',
            'error_model': 'Deformed XZZX Pauli X0.0161Y0.0161Z0.9677',
            'decoder': 'BP-OSD decoder',
            'bias': 30,
            'code': 'Toric 9x9x9',
            'probability': 0.1
          },
          {
            'code_family': 'Toric',
            'error_model': 'Pauli X0.0000Y0.0000Z1.0000',
            'decoder': 'BP-OSD decoder',
            'bias': 'inf',
            'code': 'Toric 9x9x9',
            'probability': 0.204
          }
        ])
        analysis.overrides_spec = {
            'overrides': [
                {
                    'filters': {
                        'code_family': 'Toric',
                        'bias': 30,
                        'decoder': 'BP-OSD decoder'
                    },
                    'truncate': {
                        'probability': [0.1, 0.2]
                    }
                }
            ]
        }
        analysis.apply_overrides()
        assert analysis.overrides == {
            (
                'Toric', 'Deformed XZZX Pauli X0.0161Y0.0161Z0.9677',
                'BP-OSD decoder'
            ): {
                'probability': [0.1, 0.2]
            }
        }


@pytest.mark.parametrize('error_model,bias', [
    ('Deformed XZZX Pauli X0.0005Y0.0005Z0.9990', 1000),
    ('Deformed XZZX Pauli X0.0050Y0.0050Z0.9901', 100),
    ('Pauli X0.0000Y0.0000Z1.0000', 'inf'),
    ('Pauli X0.0455Y0.0455Z0.9091', 10),
    ('Deformed XZZX Pauli X0.1250Y0.1250Z0.7500', 3),
    ('Pauli X0.3333Y0.3333Z0.3333', 0.5),
])
def test_deduce_bias(error_model, bias):
    assert bias == deduce_bias(error_model)
