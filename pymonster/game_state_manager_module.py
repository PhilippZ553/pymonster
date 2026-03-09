import numpy as np
from .beast_module import Beast
from .enemy_module import Enemy


class Game_state_manager:
    def __init__(self):
        self.beasts = []

    def add_beast(self, new_beast: Beast):
        self.beasts.append(new_beast)

    def delete_beast(self, ID: int):
        self.beasts = [beast for beast in self.beasts if beast.get_id() != ID]

    def update_beast(self, beast_strings):
        # store beaststrings in variables
        (beast_id, beast_energy, beast_environment) = beast_strings
        # update the beast with the right id
        beast = self.get_beast_from_id(beast_id)
        if beast is None:
            raise ValueError(f"Beast with ID {beast_id} not found.")
        beast.set_energy(beast_energy)
        beast.set_environment(beast_environment)
        beast.increment_update_counter()
        # add beast to the end of the list so when beasts are
        # iterated over they do not overwrite newer views
        self.beasts.remove(beast)
        self.beasts.append(beast)

    def get_beast_from_id(self, beast_id: int) -> Beast:
        # iterate over beasts and return the one matching the id
        for beast in self.beasts:
            if beast.get_id() == beast_id:
                return beast

    def get_enemy_from_coordinates(
        self, enemies: list, y: int, x: int
    ) -> Enemy:
        for enemy in enemies:
            if enemy.get_y() == y and enemy.get_x() == x:
                return enemy
        return None

    def get_gamestate(
        self, current_beast: Beast, y_dimension: int, x_dimension: int
    ):
        enemies = []

        # get palyingfield as an empty 2darray
        playing_field = get_empty_playing_field(y_dimension, x_dimension)
        # get dimensions of playingfield2 and store in variables
        playing_field_height, playing_field_width = playing_field.shape

        # iterate over all beasts
        for beast in self.beasts:
            # get the view of the beast and its dimensions
            beast_view = beast.get_environment()
            beast_view_height, beast_view_width = beast_view.shape
            # get the coordinates of the beast
            beast_x = beast.get_x_coordinate()
            beast_y = beast.get_y_coordinate()

            # iterate over every cell of beastview
            for y in range(beast_view_height):
                for x in range(beast_view_width):
                    # calculate correlating Position on playing field
                    # for every cell in beastview
                    correlating_field_y = (
                        beast_y + y - beast_view_height // 2
                    ) % playing_field_height
                    correlating_field_x = (
                        beast_x + x - beast_view_width // 2
                    ) % playing_field_width

                    # check if a beast that was already updated this turn overwrites
                    # an enemy painted by an beast not yet updated this round
                    playing_field_cell_content = playing_field[
                        correlating_field_y
                    ][correlating_field_x]
                    if beast.get_update_counter() == self.beasts[
                        -1
                    ].get_update_counter() and (
                        playing_field_cell_content == ">"
                        or playing_field_cell_content == "<"
                        or playing_field_cell_content == "="
                    ):
                        # check if enemy at these cords has only values from last turn
                        enemy_to_check = self.get_enemy_from_coordinates(
                            enemies, correlating_field_y, correlating_field_x
                        )
                        if (
                            enemy_to_check.get_max_energy_from_this_round
                            is None
                            and enemy_to_check.get_min_energy_from_this_round
                            is None
                        ):
                            enemies.remove(enemy_to_check)

                    # save the content of beast_view-cell into playing_field-cell
                    playing_field[correlating_field_y, correlating_field_x] = (
                        beast_view[y, x]
                    )

                    # check if there is one of our beasts alive at these
                    # coordinates and insert "B"
                    for b in self.beasts:
                        if (
                            b.get_x_coordinate() == correlating_field_x
                            and b.get_y_coordinate() == correlating_field_y
                        ):
                            playing_field[
                                correlating_field_y, correlating_field_x
                            ] = "B"

                    # check if there was an enemy saved
                    just_inserted = playing_field[
                        correlating_field_y, correlating_field_x
                    ]
                    if (
                        just_inserted == ">"
                        or just_inserted == "<"
                        or just_inserted == "="
                    ):
                        # try to get enemy for current cords
                        enemy = self.get_enemy_from_coordinates(
                            enemies, correlating_field_y, correlating_field_x
                        )
                        # if there is no enemy at these cordiantes create him
                        if enemy is None:
                            enemy = Enemy(
                                correlating_field_y, correlating_field_x
                            )
                            enemies.append(enemy)
                        # update enemys values
                        enemy.update_values(
                            just_inserted,
                            beast.get_energy(),
                            beast.get_update_counter(),
                            self.beasts[-1].get_update_counter(),
                        )

                    # check if there was food saved and replace it with "F" if
                    # it was a beastview from last round
                    if (
                        just_inserted == "*"
                        and beast.get_update_counter()
                        < self.beasts[-1].get_update_counter()
                    ):
                        playing_field[
                            correlating_field_y, correlating_field_x
                        ] = "F"

        # print the correlating "<" , ">", "=", etc matching our beasts energy level
        # iterate over enemies and compare their energy level to current_beast
        for enemy in enemies:
            playing_field[enemy.get_y()][enemy.get_x()] = enemy.get_symbol(
                current_beast.get_energy()
            )
        return (playing_field, enemies)


# Hilfsmethoden:


def get_empty_playing_field(y: int, x: int) -> np.ndarray:
    x_dimension = x
    y_dimension = y
    playing_field = np.full((y_dimension, x_dimension), " ", dtype="<U1")
    return playing_field
