"""Modul zur Speicherung der Beaster"""

import numpy as np
from .config import N


class Beast:
    n = N

    def __init__(
        self,
        beast_id: int,
        energy: float,
        environment: str | np.ndarray,
        x_coordinate: int,
        y_coordinate: int,
        update_counter: int,
    ):
        self.beast_id = beast_id
        self.energy = energy

        self.N = Beast.n

        self.environment = self.get_environment_from_str_or_ndarray(
            environment
        )
        self.x_coordinate = x_coordinate
        self.y_coordinate = y_coordinate
        self.N = Beast.n
        self.update_counter = update_counter

    def increment_update_counter(self):
        self.update_counter += 1

    def move(self, x_vector: int, y_vector: int):
        self.x_coordinate += x_vector
        self.y_coordinate += y_vector

    # getter
    def get_id(self) -> int:
        """Gibt die eindeutige ID des Biests zurück."""
        return self.beast_id

    def get_energy(self) -> float:
        """Gibt die aktuelle Energie des Biests zurück."""
        return self.energy

    def get_environment(self) -> np.ndarray:
        """Gibt die lokale Umgebung des Biests als NumPy-Array zurück."""
        return self.environment

    def get_x_coordinate(self) -> int:
        """Gibt die aktuelle x-Koordinate des Biests zurück."""
        return self.x_coordinate

    def get_y_coordinate(self) -> int:
        """Gibt die aktuelle y-Koordinate des Biests zurück."""
        return self.y_coordinate

    def get_update_counter(self) -> int:
        """Gibt die Anzahl der bisher durchgeführten Simulationsschritte zurück."""
        return self.update_counter

    def get_beast_coordinates(self) -> tuple[int, int]:
        """Gibt die Position des Biests als (y, x) Tupel zurück.

        Returns:
            tuple[int, int]: Ein Tupel bestehend aus (y-Koordinate, x-Koordinate).
        """
        return (self.get_y_coordinate(), self.get_x_coordinate())

    # setter
    def set_energy(self, new_energy: float):
        """Setzt die Energie des Biests auf einen neuen Wert.

        Args:
            new_energy (float): Der neue Energiewert. Darf nicht negativ sein.

        Raises:
            ValueError: Wenn die neue Energie kleiner als 0 ist.
        """
        if new_energy < 0:
            raise ValueError("Energy cannot be negative")
        self.energy = new_energy

    def set_environment(self, new_environment: str | np.ndarray):
        """Aktualisiert die lokale Umgebung des Biests.

        Args:
            new_environment (str | np.ndarray): Die neue Umgebung entweder als
                eindimensionaler String oder als NumPy-Array.
        """
        self.environment = self.get_environment_from_str_or_ndarray(
            new_environment
        )

    def set_x_coordinate(self, new_x: int):
        """Setzt die x-Koordinate des Biests auf einen neuen Wert.

        Args:
            new_x (int): Die neue x-Koordinate in der Simulation.
        """
        self.x_coordinate = new_x

    def set_y_coordinate(self, new_y: int):
        """Setzt die y-Koordinate des Biests auf einen neuen Wert.

        Args:
            new_y (int): Die neue y-Koordinate in der Simulation.
        """
        self.y_coordinate = new_y

    # Hilfsmethoden


def get_environment_from_str_or_ndarray(
    self, environment_to_set: str | np.ndarray
) -> np.ndarray:
    """Wandelt die Server-Umgebung in ein strukturiertes NumPy-Array um.

    Args:
        environment_to_set (str | np.ndarray): Die Daten der Umgebung
            vom Server (String) oder ein bereits existierendes Array.

    Returns:
        np.ndarray: Eine 2D-Matrix Größe: (2N+1)x(2N+1)

    Raises:
        ValueError: Wenn die Stringlänge nicht zur erwarteten Grid-Größe passt
            oder der Datentyp kein String oder  NumPy-Array ist.
    """
    if isinstance(environment_to_set, str):
        size = 2 * self.N + 1
        expected_len = size * size
        if len(environment_to_set) != expected_len:
            raise ValueError(
                f"String length {len(environment_to_set)} does not "
                f"match expected {expected_len} for grid {size}x{size}"
            )

        environment_2d = np.array(
            list(environment_to_set), dtype="<U1"
        ).reshape(size, size)

    elif isinstance(environment_to_set, np.ndarray):
        environment_2d = environment_to_set
    else:
        raise ValueError("given Environment is not a string or np.ndarray")

    return environment_2d
