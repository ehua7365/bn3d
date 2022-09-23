from typing import Tuple, Dict, List
import numpy as np
from panqec.codes import StabilizerCode

Operator = Dict[Tuple, str]  # Location to pauli ('X','Y','Z')
Coordinates = List[Tuple]  # List of locations


class Quasi2DCode(StabilizerCode):
    dimension = 3

    @property
    def label(self) -> str:
        return 'Quasi 2D {}x{}x{}'.format(*self.size)

    def _is_in_hole(self, x, y, z):
        Lx, Ly, Lz = self.size

        return ((x > 2 and x < 2*Lx-2)
                and (y >= 1 and y < 2*Ly-2)
                and (z >= 1 and z < 2*Lz-2))

    def get_qubit_coordinates(self) -> Coordinates:
        coordinates: Coordinates = []
        Lx, Ly, Lz = self.size

        # Qubits along e_x
        for x in range(1, 2*Lx, 2):
            for y in range(0, 2*Ly, 2):
                for z in range(0, 2*Lz, 2):
                    if not self._is_in_hole(x, y, z):
                        coordinates.append((x, y, z))

        # Qubits along e_y
        for x in range(2, 2*Lx, 2):
            for y in range(1, 2*Ly-1, 2):
                for z in range(0, 2*Lz, 2):
                    if not self._is_in_hole(x, y, z):
                        coordinates.append((x, y, z))

        # Qubits along e_z
        for x in range(2, 2*Lx, 2):
            for y in range(0, 2*Ly, 2):
                for z in range(1, 2*Lz-1, 2):
                    if not self._is_in_hole(x, y, z):
                        coordinates.append((x, y, z))

        return coordinates

    def get_stabilizer_coordinates(self) -> Coordinates:
        coordinates: Coordinates = []
        Lx, Ly, Lz = self.size

        # Vertices
        for x in range(2, 2*Lx, 2):
            for y in range(0, 2*Ly, 2):
                for z in range(0, 2*Lz, 2):
                    if not self._is_in_hole(x, y, z):
                        coordinates.append((x, y, z))

        # Faces in xy plane
        for x in range(1, 2*Lx+1, 2):
            for y in range(1, 2*Ly-1, 2):
                for z in range(0, 2*Lz, 2):
                    if not self._is_in_hole(x, y, z):
                        coordinates.append((x, y, z))

        # Faces in yz plane
        for x in range(2, 2*Lx, 2):
            for y in range(1, 2*Ly-1, 2):
                for z in range(1, 2*Lz-1, 2):
                    if not self._is_in_hole(x, y, z):
                        coordinates.append((x, y, z))

        # Faces in xz plane
        for x in range(1, 2*Lx+1, 2):
            for y in range(0, 2*Ly, 2):
                for z in range(1, 2*Lz-1, 2):
                    if not self._is_in_hole(x, y, z):
                        coordinates.append((x, y, z))

        return coordinates

    def stabilizer_type(self, location: Tuple) -> str:
        if not self.is_stabilizer(location):
            raise ValueError(f"Invalid coordinate {location}"
                             "for a stabilizer")

        x, y, z = location
        if x % 2 == 0 and y % 2 == 0:
            return 'vertex'
        else:
            return 'face'

    def get_stabilizer(self, location, deformed_axis=None) -> Operator:
        if not self.is_stabilizer(location):
            raise ValueError(f"Invalid coordinate {location}"
                             "for a stabilizer")

        if self.stabilizer_type(location) == 'vertex':
            pauli = 'Z'
        else:
            pauli = 'X'

        deformed_pauli = {'X': 'Z', 'Z': 'X'}[pauli]

        x, y, z = location

        if self.stabilizer_type(location) == 'vertex':
            delta: List[Tuple] = [(1, 0, 0), (-1, 0, 0), (0, 1, 0),
                                  (0, -1, 0), (0, 0, 1), (0, 0, -1)]
        else:
            # Face in xy-plane.
            if z % 2 == 0:
                delta = [(-1, 0, 0), (1, 0, 0),
                         (0, -1, 0), (0, 1, 0)]
            # Face in yz-plane.
            elif (x % 2 == 0):
                delta = [(0, -1, 0), (0, 1, 0),
                         (0, 0, -1), (0, 0, 1)]
            # Face in zx-plane.
            elif (y % 2 == 0):
                delta = [(-1, 0, 0), (1, 0, 0),
                         (0, 0, -1), (0, 0, 1)]

        operator: Operator = dict()
        for d in delta:
            qubit_location = tuple(np.add(location, d))

            if self.is_qubit(qubit_location):
                is_deformed = (self.qubit_axis(qubit_location)
                               == deformed_axis)
                operator[qubit_location] = (deformed_pauli if is_deformed
                                            else pauli)

        return operator

    def qubit_axis(self, location) -> str:
        x, y, z = location

        if (z % 2 == 0) and (x % 2 == 1) and (y % 2 == 0):
            axis = 'x'
        elif (z % 2 == 0) and (x % 2 == 0) and (y % 2 == 1):
            axis = 'y'
        elif (z % 2 == 1) and (x % 2 == 0) and (y % 2 == 0):
            axis = 'z'
        else:
            raise ValueError(f'Location {location} does not correspond'
                             'to a qubit')

        return axis

    def get_logicals_x(self) -> List[Operator]:
        """The unique logical X operator."""

        Lx, Ly, Lz = self.size
        logicals = []

        # X operators along x edges in x direction.
        operator: Operator = dict()
        for x in range(1, 2*Lx+1, 2):
            operator[(x, 0, 0)] = 'X'
        logicals.append(operator)

        return logicals

    def get_logicals_z(self) -> List[Operator]:
        """The unique logical Z operator."""

        Lx, Ly, Lz = self.size
        logicals = []

        # X operators along x edges in x direction.
        operator: Operator = dict()
        for y in range(0, 2*Ly, 2):
            for z in range(0, 2*Lz, 2):
                operator[(1, y, z)] = 'Z'
        logicals.append(operator)

        return logicals

    def stabilizer_representation(
        self, location: Tuple, rotated_picture=False, json_file=None
    ) -> Dict:
        representation = super().stabilizer_representation(location,
                                                           rotated_picture)

        x, y, z = location
        if not rotated_picture and self.stabilizer_type(location) == 'face':
            if z % 2 == 0:  # xy plane
                representation['params']['normal'] = [0, 0, 1]
            elif x % 2 == 0:  # yz plane
                representation['params']['normal'] = [1, 0, 0]
            else:  # xz plane
                representation['params']['normal'] = [0, 1, 0]

        if rotated_picture and self.stabilizer_type(location) == 'face':
            if z % 2 == 0:
                representation['params']['normal'] = [0, 0, 1]
            elif x % 2 == 0:
                representation['params']['normal'] = [1, 0, 0]
            else:
                representation['params']['normal'] = [0, 1, 0]

        return representation
