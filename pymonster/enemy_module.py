"""Modul zur Speicherung der Enemies."""


class Enemy:
    def __init__(self, y, x):
        self.x_coordinate = x
        self.y_coordinate = y
        self.min_energy_from_last_round = None
        self.max_energy_from_last_round = None
        self.min_energy_from_this_round = None
        self.max_energy_from_this_round = None

    def get_x(self) -> int:
        """Gibt die aktuelle x-Koordinate des Biests zurück."""
        return self.x_coordinate

    def get_y(self) -> int:
        """Gibt die aktuelle y-Koordinate des Biests zurück."""
        return self.y_coordinate

    def get_min_energy_from_this_round(self) -> float:
        """Gibt die minimale Energie zurück, die in dieser Runde erreicht wurde."""
        return self.min_energy_from_this_round

    def get_max_energy_from_this_round(self) -> float:
        """Gibt die maximale Energie zurück, die in dieser Runde erreicht wurde."""
        return self.max_energy_from_this_round

    def get_min_energy_from_last_round(self) -> float:
        """Gibt die minimale Energie aus der vorherigen Simulationsrunde zurück."""
        return self.min_energy_from_last_round

    def get_max_energy_from_last_round(self) -> float:
        """Gibt die maximale Energie aus der vorherigen Simulationsrunde zurück."""
        return self.max_energy_from_last_round

    def set_x(self, x: int):
        """Setzt die x-Koordinate des Biests.

        Args:
            x (int): Die neue x-Koordinate.
        """
        self.x_coordinate = x

    def set_y(self, y: int):
        """Setzt die y-Koordinate des Biests.

        Args:
            y (int): Die neue y-Koordinate.
        """
        self.y_coordinate = y

    def set_min_energy_from_this_round(self, min_energy: int):
        """Aktualisiert die minimale Energie für die aktuelle Runde.

        Args:
            min_energy (int): Der neue Minimalwert der Energie.
        """
        self.min_energy_from_this_round = min_energy

    def set_max_energy_from_this_round(self, max_energy: int):
        """Aktualisiert die maximale Energie für die aktuelle Runde.

        Args:
            max_energy (int): Der neue Maximalwert der Energie.
        """
        self.max_energy_from_this_round = max_energy

    def set_min_energy_from_last_round(self, min_energy: int):
        """Setzt den Minimalwert der Energie aus der letzten Runde.

        Args:
            min_energy (int): Der Minimalwert der vorherigen Runde.
        """
        self.min_energy_from_last_round = min_energy

    def set_max_energy_from_last_round(self, max_energy: int):
        """Setzt den Maximalwert der Energie aus der letzten Runde.

        Args:
            max_energy (int): Der Maximalwert der vorherigen Runde.
        """
        self.max_energy_from_last_round = max_energy

    def update_values(
        self,
        relation: str,
        energy_value: int,
        beast_update_counter,
        current_Update,
    ):
        # values that come from already updated beasts may only be narrowed by
        # updated beasts because they are trustworthy

        # values taht come from beasts not yet updated may only be narrowed by
        # not updated beasts because they are not trustworthy
        if beast_update_counter < current_Update:
            match relation:
                case "<":
                    if (
                        self.get_max_energy_from_last_round() is None
                        or energy_value < self.get_max_energy_from_last_round()
                    ):
                        self.set_max_energy_from_last_round(energy_value - 1)
                case ">":
                    if (
                        self.get_min_energy_from_last_round() is None
                        or energy_value > self.get_min_energy_from_last_round()
                    ):
                        self.set_min_energy_from_last_round(energy_value + 1)
                case "=":
                    self.set_min_energy_from_last_round(energy_value)
                    self.set_max_energy_from_last_round(energy_value)
        else:
            match relation:
                case "<":
                    if (
                        self.get_max_energy_from_this_round() is None
                        or energy_value < self.get_max_energy_from_this_round()
                    ):
                        self.set_max_energy_from_this_round(energy_value - 1)
                case ">":
                    if (
                        self.get_min_energy_from_this_round() is None
                        or energy_value > self.get_min_energy_from_this_round()
                    ):
                        self.set_min_energy_from_this_round(energy_value + 1)
                case "=":
                    self.set_min_energy_from_this_round(energy_value)
                    self.set_max_energy_from_this_round(energy_value)

    def get_symbol(self, beast_energy: int) -> str:
        max_energy = self.get_max_energy_from_this_round()
        min_energy = self.get_min_energy_from_this_round()
        max_energy_last_round = self.get_max_energy_from_last_round()
        min_energy_last_round = self.get_min_energy_from_last_round()

        if (
            max_energy is not None
            and min_energy is not None
            and max_energy == beast_energy
            and min_energy == beast_energy
        ):
            return "="
        elif max_energy is not None and max_energy < beast_energy:
            return "<"
        elif min_energy is not None and min_energy > beast_energy:
            return ">"
        elif min_energy is None and max_energy is None:
            if (
                max_energy_last_round is not None
                and min_energy_last_round is not None
                and max_energy_last_round == beast_energy
                and min_energy_last_round == beast_energy
            ):
                return "S"
            elif (
                max_energy_last_round is not None
                and max_energy_last_round < beast_energy
            ):
                return "K"
            elif (
                min_energy_last_round is not None
                and min_energy_last_round > beast_energy
            ):
                return "G"
        return "?"
