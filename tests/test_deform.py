import pytest
import numpy as np
from panqec.bpauli import bcommute
from panqec.codes import Toric3DCode, StabilizerCode
from panqec.error_models import PauliErrorModel
from panqec.error_models import (
    DeformedXZZXErrorModel
)
from panqec.decoders import (
    DeformedSweepMatchDecoder, DeformedSweepDecoder3D,
    DeformedToric3DMatchingDecoder, FoliatedMatchingDecoder
)


@pytest.fixture
def code():
    return Toric3DCode(3, 4, 5)


@pytest.fixture
def rng():
    np.random.seed(0)
    return np.random


class TestDeformedXZZXErrorModel:

    @pytest.mark.parametrize(
        'noise, original, deformed',
        [
            ((1, 0, 0), 'X', 'Z'),
            ((0, 0, 1), 'Z', 'X'),
            ((0, 1, 0), 'Y', 'Y'),
        ]
    )
    def test_max_noise(self, code, rng, noise, original, deformed):
        error_model = DeformedXZZXErrorModel(*noise)
        error = error_model.generate(code, error_rate=1, rng=rng)
        pauli = code.from_bsf(error)
        for edge in code.qubit_coordinates:
            if code.qubit_axis(edge) == 'z':
                assert pauli[edge] == deformed
            else:
                assert pauli[edge] == original

    def test_original_all_X_becomes_Z_on_deformed_axis(self, code):
        error_model = DeformedXZZXErrorModel(1, 0, 0)
        error = error_model.generate(code, error_rate=1)
        pauli = code.from_bsf(error)

        for edge in code.qubit_index:
            if code.qubit_axis(edge) == 'z':
                assert pauli[edge] == 'Z'
            else:
                assert pauli[edge] == 'X'

    def test_original_all_Z_becomes_X_on_deformed_axis(self, code):
        error_model = DeformedXZZXErrorModel(0, 0, 1)
        error = error_model.generate(code, error_rate=1)
        pauli = code.from_bsf(error)

        for edge in code.qubit_index:
            if code.qubit_axis(edge) == 'z':
                assert pauli[edge] == 'X'
            else:
                assert pauli[edge] == 'Z'

    def test_all_Y_deformed_is_still_all_Y(self, code):
        error_model = DeformedXZZXErrorModel(0, 1, 0)
        error = error_model.generate(code, error_rate=1)
        pauli = code.from_bsf(error)

        for edge in code.qubit_index:
            assert pauli[edge] == 'Y'

    def test_label(self, code):
        error_model = DeformedXZZXErrorModel(1, 0, 0)
        assert error_model.label == 'Deformed XZZX Pauli X1.0000Y0.0000Z0.0000'


class TestDeformedDecoder:

    def test_decode_trivial(self, code):
        error_model = DeformedXZZXErrorModel(0.1, 0.2, 0.7)
        error_rate = 0.1
        decoder = DeformedSweepMatchDecoder(code, error_model, error_rate)

        syndrome = np.zeros(code.stabilizer_matrix.shape[0], dtype=np.uint)
        correction = decoder.decode(syndrome)
        assert np.all(correction == 0)
        assert issubclass(correction.dtype.type, np.integer)

    def test_decode_single_X_on_undeformed_axis(self, code):
        error_model = DeformedXZZXErrorModel(0.1, 0.2, 0.7)
        error_rate = 0.1
        decoder = DeformedSweepMatchDecoder(code, error_model, error_rate)

        # Single-qubit X error on undeformed edge.
        error = code.to_bsf({
            (0, 1, 0): 'X'
        })
        assert np.any(error != 0)

        # Calculate the syndrome and make sure it's nontrivial.
        syndrome = bcommute(code.stabilizer_matrix, error)
        assert np.any(syndrome != 0)

        # Total error should be in code space.
        correction = decoder.decode(syndrome)
        total_error = (error + correction) % 2
        assert np.all(bcommute(code.stabilizer_matrix, total_error) == 0)

    @pytest.mark.parametrize(
        'operator, location',
        [
            ['X', (0, 0, 0, 0)],
            ['Y', (0, 1, 0, 0)],
            ['Z', (0, 0, 1, 0)],
            ['X', (1, 0, 0, 1)],
            ['Y', (1, 0, 2, 0)],
            ['Z', (1, 2, 0, 0)],
            ['X', (2, 0, 0, 2)],
            ['Y', (2, 1, 1, 0)],
            ['Z', (2, 0, 2, 0)],
        ]
    )
    def test_decode_single_qubit_error(
        self, code, operator, location
    ):
        noise_direction = (0.1, 0.2, 0.7)
        error_model = DeformedXZZXErrorModel(*noise_direction)
        error_rate = 0.1
        decoder = DeformedSweepMatchDecoder(code, error_model, error_rate)

        # Single-qubit X error on undeformed edge.
        error = code.to_bsf({
            (0, 1, 0): 'X'
        })
        assert np.any(error != 0)

        # Calculate the syndrome and make sure it's nontrivial.
        syndrome = bcommute(code.stabilizer_matrix, error)
        assert np.any(syndrome != 0)

        # Total error should be in code space.
        correction = decoder.decode(syndrome)
        total_error = (error + correction) % 2
        assert np.all(bcommute(code.stabilizer_matrix, total_error) == 0)

    def test_deformed_pymatching_weights_nonuniform(self, code):
        error_model = DeformedXZZXErrorModel(0.1, 0.2, 0.7)
        probability = 0.1
        decoder = DeformedSweepMatchDecoder(code, error_model, probability)
        assert decoder.matcher.error_model.direction == (0.1, 0.2, 0.7)
        matching = decoder.matcher.get_matcher()
        assert matching.matching_graph.distance(0, 0) == 0
        n_nodes = matching.matching_graph.get_num_nodes()
        distance_matrix = np.zeros((n_nodes, n_nodes))
        for i, j, edge in matching.matching_graph.get_edges():
            distance_matrix[i, j] = edge.weight
            distance_matrix[j, i] = edge.weight
        n_vertices = int(np.product(code.size))
        assert distance_matrix.shape == (n_vertices, n_vertices)

        # The index of the origin vertex.
        origin_index = [
            index
            for index, location in enumerate(code.stabilizer_coordinates)
            if location == (0, 0, 0)
            and code.stabilizer_type(location) == 'vertex'
        ][0]

        # Distances from the origin vertex.
        origin_distances = np.zeros(code.size)

        for index, coordinate in enumerate(code.stabilizer_index):
            if code.stabilizer_type(coordinate) == 'vertex':
                location = tuple(
                    (np.array(coordinate)/2).astype(int).tolist()
                )
                origin_distances[location] = distance_matrix[
                    origin_index, index
                ]

        assert origin_distances[0, 0, 0] == 0

        # Distances in the undeformed direction should be equal.
        assert origin_distances[1, 0, 0] == origin_distances[0, 1, 0]

        # Distances in the deformed direction should be different.
        assert origin_distances[0, 1, 0] != origin_distances[0, 0, 1]

    def test_equal_XZ_bias_deformed_pymatching_weights_uniform(self, code):
        error_model = DeformedXZZXErrorModel(0.4, 0.2, 0.4)
        print(f'{error_model.direction=}')
        probability = 0.1
        decoder = DeformedSweepMatchDecoder(code, error_model, probability)
        assert decoder.matcher.error_model.direction == (0.4, 0.2, 0.4)
        matching = decoder.matcher.get_matcher()
        assert matching.matching_graph.distance(0, 0) == 0
        n_nodes = matching.matching_graph.get_num_nodes()
        distance_matrix = np.zeros((n_nodes, n_nodes))
        for i, j, edge in matching.matching_graph.get_edges():
            distance_matrix[i, j] = edge.weight
            distance_matrix[j, i] = edge.weight
        n_vertices = int(np.product(code.size))
        assert distance_matrix.shape == (n_vertices, n_vertices)

        # Distances from the origin vertex.
        origin_distances = distance_matrix[0].reshape(code.size)
        assert origin_distances[0, 0, 0] == 0

        # Distances in the undeformed direction should be equal.
        assert origin_distances[0, 1, 0] == origin_distances[0, 0, 1]

        # Distances in the deformed direction should be different.
        assert origin_distances[1, 0, 0] == origin_distances[0, 0, 1]


class TestDeformedSweepDecoder3D:

    @pytest.mark.parametrize(
        'noise_direction, expected_edge_probs',
        [
            [(0.9, 0, 0.1), (0.81818, 0.090909, 0.090909)],
            [(0.1, 0, 0.9), (0.05263, 0.47368, 0.47368)],
            [(1/3, 1/3, 1/3), (0.3333, 0.3333, 0.3333)],
            [(0, 0, 1), (0, 0.5, 0.5)],
        ]
    )
    def test_get_edge_probabilities(
        self, code, noise_direction, expected_edge_probs
    ):
        error_model = DeformedXZZXErrorModel(*noise_direction)
        error_rate = 0.5
        decoder = DeformedSweepDecoder3D(code, error_model, error_rate)
        print(decoder.get_edge_probabilities())
        np.testing.assert_allclose(
            decoder.get_edge_probabilities(),
            expected_edge_probs,
            rtol=0.01
        )

    def test_decode_trivial(self, code):
        error_model = DeformedXZZXErrorModel(1/3, 1/3, 1/3)
        error_rate = 0.5
        decoder = DeformedSweepDecoder3D(code, error_model, error_rate)
        n = code.n
        error = np.zeros(2*n, dtype=np.uint)
        syndrome = bcommute(code.stabilizer_matrix, error)
        correction = decoder.decode(syndrome)
        total_error = (correction + error) % 2
        assert np.all(bcommute(code.stabilizer_matrix, total_error) == 0)
        assert issubclass(correction.dtype.type, np.integer)

    def test_all_3_faces_active(self, code):
        error_pauli = dict()
        sites = [
            (3, 2, 2), (2, 4, 3)
        ]
        for site in sites:
            error_pauli[site] = 'Z'
        error = code.to_bsf(error_pauli)
        error_model = DeformedXZZXErrorModel(1/3, 1/3, 1/3)
        error_rate = 0.5
        decoder = DeformedSweepDecoder3D(code, error_model, error_rate)
        syndrome = bcommute(code.stabilizer_matrix, error)
        correction = decoder.decode(syndrome)
        total_error = (error + correction) % 2
        assert np.all(bcommute(code.stabilizer_matrix, total_error) == 0)


class TestDeformedToric3DMatchingDecoder:

    def test_decode_trivial(self, code):
        error_model = DeformedXZZXErrorModel(1/3, 1/3, 1/3)
        error_rate = 0.5
        decoder = DeformedToric3DMatchingDecoder(code, error_model, error_rate)
        n = code.n
        error = np.zeros(2*n, dtype=np.uint)
        syndrome = bcommute(code.stabilizer_matrix, error)
        correction = decoder.decode(syndrome)
        total_error = (correction + error) % 2
        assert np.all(bcommute(code.stabilizer_matrix, total_error) == 0)
        assert issubclass(correction.dtype.type, np.integer)


class XNoiseOnYZEdgesOnly(PauliErrorModel):
    """X noise applied on y and z edges only."""

    def __init__(self):
        super(XNoiseOnYZEdgesOnly, self).__init__(1, 0, 0)

    def generate(
        self, code: StabilizerCode, error_rate: float, rng=None
    ) -> np.ndarray:
        error = super(XNoiseOnYZEdgesOnly, self).generate(
            code, error_rate, rng=rng
        )
        for index, location in enumerate(code.qubit_coordinates):
            if code.qubit_axis(location) == 'x':
                error[index] = 0
        return error


class TestMatchingXNoiseOnYZEdgesOnly:

    def test_decode(self, code):
        for seed in range(5):
            rng = np.random.default_rng(seed=seed)
            error_rate = 0.5
            error_model = XNoiseOnYZEdgesOnly()
            decoder = DeformedToric3DMatchingDecoder(
                code, error_model, error_rate
            )
            error = error_model.generate(
                code, error_rate=error_rate, rng=rng
            )
            assert any(error), 'Error should be non-trivial'
            syndrome = bcommute(code.stabilizer_matrix, error)
            correction = decoder.decode(syndrome)
            assert any(correction), 'Correction should be non-trivial'
            total_error = (correction + error) % 2
            assert np.all(
                bcommute(code.stabilizer_matrix, total_error) == 0
            ), 'Total error should be in code space'

            # Error and correction as objects.
            error_pauli = code.from_bsf(error)
            correction_pauli = code.from_bsf(correction)

            x_edges = [
                edge for edge in code.qubit_index
                if code.qubit_axis(edge) == 'x'
            ]
            y_edges = [
                edge for edge in code.qubit_index
                if code.qubit_axis(edge) == 'y'
            ]
            z_edges = [
                edge for edge in code.qubit_index
                if code.qubit_axis(edge) == 'z'
            ]

            assert np.all(
                edge not in error_pauli
                or error_pauli[edge] == 'I'
                for edge in x_edges
            ), 'No errors should be on x edges'

            assert np.all(
                edge not in correction_pauli
                or correction_pauli[edge] == 'I'
                for edge in x_edges
            ), 'No corrections should be on x edges'

            assert np.any([
                correction_pauli[edge] != 'I'
                for edge in y_edges + z_edges
                if edge in correction_pauli
            ]), 'Non-trivial corrections should be on the y and z edges'


class TestFoliatedDecoderXNoiseOnYZEdgesOnly:

    def test_decode(self, code):
        for seed in range(5):
            rng = np.random.default_rng(seed=seed)
            error_rate = 0.5
            error_model = XNoiseOnYZEdgesOnly()
            decoder = FoliatedMatchingDecoder(code, error_model, error_rate)
            error = error_model.generate(
                code, error_rate=error_rate, rng=rng
            )
            assert any(error), 'Error should be non-trivial'
            syndrome = bcommute(code.stabilizer_matrix, error)
            correction = decoder.decode(syndrome)
            assert any(correction), 'Correction should be non-trivial'
            total_error = (correction + error) % 2
            assert np.all(
                bcommute(code.stabilizer_matrix, total_error) == 0
            ), 'Total error should be in code space'

            # Error and correction as objects.
            error_pauli = code.from_bsf(error)
            correction_pauli = code.from_bsf(correction)

            x_edges, y_edges, z_edges = [
                [
                    edge for edge in code.qubit_coordinates
                    if code.qubit_axis(edge) == axis
                ]
                for axis in ['x', 'y', 'z']
            ]

            assert np.all(
                edge not in error_pauli or
                error_pauli[edge] == 'I'
                for edge in x_edges
            ), 'No errors should be on x edges'

            assert np.all(
                edge not in correction_pauli or
                correction_pauli[edge] == 'I'
                for edge in y_edges
            ), 'No corrections should be on x edges'

            assert np.any([
                correction_pauli[edge] != 'I'
                for edge in y_edges + z_edges
                if edge in correction_pauli
            ]), 'Non-trivial corrections should be on the y and z edges'
