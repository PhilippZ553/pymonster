import pytest
import numpy as np
import logging

from speicher.game_state_manager_module import (
    Game_state_manager,
    get_empty_playing_field,
)
from speicher.beast_module import Beast
from speicher.enemy_module import Enemy

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ---------------------------------------------------
# Hilfsfunktion zur einfachen Environment-Erstellung
# ---------------------------------------------------
def make_env(symbol="."):
    """Erstellt ein 3x3 np.ndarray-Environment mit dem angegebenen Symbol."""
    return np.full((3, 3), symbol, dtype="<U1")


# ---------------------------------------------------
# Grundlegende Tests
# ---------------------------------------------------


def test_add_and_get_beast():
    gsm = Game_state_manager()
    b = Beast(1, 10, make_env("."), 2, 2, 0)
    gsm.add_beast(b)

    assert len(gsm.beasts) == 1
    assert gsm.get_beast_from_id(1) is b


def test_delete_beast():
    gsm = Game_state_manager()
    b1 = Beast(1, 10, make_env("."), 0, 0, 0)
    b2 = Beast(2, 20, make_env("."), 1, 1, 0)
    gsm.add_beast(b1)
    gsm.add_beast(b2)

    gsm.delete_beast(1)
    assert len(gsm.beasts) == 1
    assert gsm.beasts[0].get_id() == 2


def test_update_beast_changes_energy_and_env():
    gsm = Game_state_manager()
    b = Beast(3, 5, make_env("."), 1, 1, 0)
    gsm.add_beast(b)

    new_env = make_env("X")
    gsm.update_beast([3, 42, new_env])

    updated = gsm.get_beast_from_id(3)
    assert updated.get_energy() == 42
    assert (updated.get_environment() == new_env).all()
    assert updated.get_update_counter() == 1
    # beast sollte am Ende der Liste stehen
    assert gsm.beasts[-1] is b


def test_update_beast_raises_for_invalid_id():
    gsm = Game_state_manager()
    with pytest.raises(ValueError, match="not found"):
        gsm.update_beast([99, 50, make_env()])


def test_get_enemy_from_coordinates():
    gsm = Game_state_manager()
    e1 = Enemy(1, 2)
    e2 = Enemy(3, 4)
    result = gsm.get_enemy_from_coordinates([e1, e2], 3, 4)
    assert result is e2
    assert gsm.get_enemy_from_coordinates([e1, e2], 10, 10) is None


def test_get_empty_playing_field_shape_and_content():
    arr = get_empty_playing_field(4, 5)
    assert arr.shape == (4, 5)
    assert np.all(arr == " ")


# ---------------------------------------------------
# Tests für get_gamestate
# ---------------------------------------------------


def test_get_gamestate_places_beast_and_enemy_correctly():
    gsm = Game_state_manager()

    # Beast sieht einen Gegner (">") in seiner Environment
    env = np.array(
        [
            [" ", ">", " "],
            [" ", " ", " "],
            [" ", " ", " "],
        ]
    )
    b = Beast(1, 10, env, x_coordinate=1, y_coordinate=1, update_counter=0)
    gsm.add_beast(b)

    # Gleiches Beast ist auch das aktuelle (zum Vergleich der Energien)
    result = gsm.get_gamestate(current_beast=b, y_dimension=5, x_dimension=5)[
        0
    ]
    logger.info(f"Spielfeld:\n{result}")
    # Das Spielfeld sollte 5x5 groß sein
    assert result.shape == (5, 5)
    # "B" sollte an Position (1,1) sein
    assert result[1, 1] == "B"
    # ">" sollte an Position (0,1) sein
    assert result[0, 1] == ">"


def test_get_gamestate_with_multiple_beasts_and_overlap():
    gsm = Game_state_manager()

    # Beast 1 (älterer Stand)
    env1 = np.array(
        [
            [" ", "*", " "],
            [" ", " ", " "],
            [" ", " ", " "],
        ]
    )
    b1 = Beast(1, 5, env1, 2, 1, 0)
    gsm.add_beast(b1)

    # Beast 2 (neuerer Stand, sollte "übermalen")
    env2 = np.array(
        [
            [" ", ">", " "],
            [" ", " ", " "],
            [" ", " ", " "],
        ]
    )
    b2 = Beast(2, 20, env2, 2, 2, 1)
    gsm.add_beast(b2)

    field = gsm.get_gamestate(current_beast=b2, y_dimension=5, x_dimension=5)[
        0
    ]
    logger.info(f"Spielfeld:\n{field}")

    # "B" sollte an Position (2,2) sein
    assert field[2, 2] == "B"
    # ">" sollte an Position (1,2) sein
    assert field[1, 2] == "B"
    # "F" sollte an Postion (0, 2) sein
    assert field[0, 2] == "F"


def test_get_gamestate_enemy_symbol_changes_by_energy():
    gsm = Game_state_manager()

    env2 = np.array(
        [
            [" ", " ", " "],
            [" ", " ", " "],
            [" ", "<", " "],
        ]
    )

    beast_high_energy = Beast(2, 10, env2, 2, 4, 1)
    gsm.add_beast(beast_high_energy)

    env = np.array(
        [
            [" ", ">", " "],
            [" ", " ", " "],
            [" ", " ", " "],
        ]
    )
    beast_low_energy = Beast(1, 5, env, 2, 1, 1)
    gsm.add_beast(beast_low_energy)

    # für high energy beast
    result = gsm.get_gamestate(
        current_beast=beast_high_energy, y_dimension=5, x_dimension=5
    )
    field = result[0]
    enemies = result[1]
    for enemy in enemies:
        logger.info(
            f"Enemy at x: {enemy.get_x()} and <: {enemy.get_y()} has minE: {enemy.get_min_energy_from_this_round()} and maxE: {enemy.get_max_energy_from_this_round()}"
        )
    logger.info(f"Spielfeld:\n{field}")
    assert field[0, 2] == "<"
    result = gsm.get_gamestate(
        current_beast=beast_low_energy, y_dimension=5, x_dimension=5
    )
    field = result[0]
    enemies = result[1]
    for enemy in enemies:
        logger.info(
            f"Enemy at x: {enemy.get_x()} and <: {enemy.get_y()} has minE: {enemy.get_min_energy_from_this_round()} and maxE: {enemy.get_max_energy_from_this_round()}"
        )
    logger.info(f"Spielfeld:\n{field}")
    assert field[0, 2] == ">"
