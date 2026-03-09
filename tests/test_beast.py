import pytest
import numpy as np
from speicher.beast_module import Beast

n = 7


def test_beast_initialization_and_getters():
    env = np.full((n, n), " ")  # 7x7 Feld
    beast = Beast(
        beast_id=1,
        energy=10,
        environment=env,
        x_coordinate=3,
        y_coordinate=3,
        update_counter=0,
    )

    # Prüfen, ob Werte korrekt gesetzt sind
    assert beast.get_id() == 1
    assert beast.get_energy() == 10
    assert beast.get_x_coordinate() == 3
    assert beast.get_y_coordinate() == 3
    assert beast.get_update_counter() == 0
    # Prüfen, ob "B" in der Mitte gesetzt wurde
    assert beast.get_environment() is env


def test_setters():
    env = np.full((n, n), " ")
    beast = Beast(1, 10, env, 0, 0, 0)

    # test environment setter
    # for ndarray
    new_env = np.full((n, n), "o")
    beast.set_environment(new_env)
    assert beast.get_environment() is new_env
    # for string

    # abhänging von n machen
    new_env = np.full((n, n), "o")
    env_str = "ooooooooooooooooooooooooooooooooooooooooooooooooo"
    beast.set_environment(env_str)
    assert np.array_equal(beast.get_environment(), new_env)

    # positive Energie setzen
    beast.set_energy(5)
    assert beast.get_energy() == 5

    # negative Energie soll Fehler auslösen
    with pytest.raises(ValueError):
        beast.set_energy(-1)

    beast.set_x_coordinate(50)
    assert beast.get_x_coordinate() == 50

    beast.set_y_coordinate(13)
    assert beast.get_y_coordinate() == 13


def test_move():
    env = np.full((7, 7), " ")
    beast = Beast(1, 10, env, 3, 3, 0)

    beast.move(2, -1)
    assert beast.get_x_coordinate() == 5
    assert beast.get_y_coordinate() == 2


def test_increment_update_counter():
    env = np.full((7, 7), " ")
    beast = Beast(1, 10, env, 0, 0, 0)

    beast.increment_update_counter()
    assert beast.get_update_counter() == 1


def test_get_beast_coordinates():
    env = np.full((7, 7), " ")
    beast = Beast(1, 10, env, 3, 1, 0)

    # check if correct tupel with correct coordiantes is returned
    assert beast.get_beast_coordinates() == (
        beast.get_y_coordinate(),
        beast.get_x_coordinate(),
    )
