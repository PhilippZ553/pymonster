import pytest
from speicher.enemy_module import Enemy


def test_enemy_initialization():
    e = Enemy(3, 5)
    assert e.get_x() == 5
    assert e.get_y() == 3
    assert e.get_min_energy_from_this_round() is None
    assert e.get_max_energy_from_this_round() is None
    assert e.get_min_energy_from_last_round() is None
    assert e.get_max_energy_from_last_round() is None


def test_enemy_setters_and_getters():
    e = Enemy(1, 2)
    e.set_x(10)
    e.set_y(20)
    e.set_min_energy_from_this_round(5)
    e.set_max_energy_from_this_round(15)
    e.set_min_energy_from_last_round(7)
    e.set_max_energy_from_last_round(17)

    assert e.get_x() == 10
    assert e.get_y() == 20
    assert e.get_min_energy_from_this_round() == 5
    assert e.get_max_energy_from_this_round() == 15
    assert e.get_min_energy_from_last_round() == 7
    assert e.get_max_energy_from_last_round() == 17


def test_update_values_last_round():
    e = Enemy(0, 0)

    # check larger
    relation = ">"
    energy_value = 10
    e.update_values(
        relation, energy_value, beast_update_counter=0, current_Update=1
    )
    assert e.get_min_energy_from_last_round() == energy_value + 1

    # check smaller
    relation = "<"
    energy_value = 10
    e.update_values(
        relation, energy_value, beast_update_counter=0, current_Update=1
    )
    assert e.get_max_energy_from_last_round() == energy_value - 1

    # check even
    relation = "="
    energy_value = 10
    e.update_values(
        relation, energy_value, beast_update_counter=0, current_Update=1
    )
    assert (
        e.get_max_energy_from_last_round() == energy_value
        and e.get_min_energy_from_last_round() == energy_value
    )


def test_update_values_this_round():
    e = Enemy(0, 0)

    # check larger
    relation = ">"
    energy_value = 10
    e.update_values(
        relation, energy_value, beast_update_counter=1, current_Update=1
    )
    assert e.get_min_energy_from_this_round() == energy_value + 1

    # check smaller
    relation = "<"
    energy_value = 10
    e.update_values(
        relation, energy_value, beast_update_counter=1, current_Update=1
    )
    assert e.get_max_energy_from_this_round() == energy_value - 1

    # check even
    relation = "="
    energy_value = 10
    e.update_values(
        relation, energy_value, beast_update_counter=1, current_Update=1
    )
    assert (
        e.get_max_energy_from_this_round() == energy_value
        and e.get_min_energy_from_this_round() == energy_value
    )


def test_get_symbol_current_round_equal():
    e = Enemy(0, 0)
    e.set_min_energy_from_this_round(10)
    e.set_max_energy_from_this_round(10)
    assert e.get_symbol(10) == "="


def test_get_symbol_current_round_less_than_beast():
    e = Enemy(0, 0)
    e.set_max_energy_from_this_round(5)
    assert e.get_symbol(10) == "<"


def test_get_symbol_current_round_greater_than_beast():
    e = Enemy(0, 0)
    e.set_min_energy_from_this_round(15)
    assert e.get_symbol(10) == ">"


def test_get_symbol_last_round_variants():
    e = Enemy(0, 0)
    e.set_min_energy_from_last_round(10)
    e.set_max_energy_from_last_round(10)
    assert e.get_symbol(10) == "S"

    e = Enemy(0, 0)
    e.set_max_energy_from_last_round(5)
    assert e.get_symbol(10) == "K"

    e = Enemy(0, 0)
    e.set_min_energy_from_last_round(15)
    assert e.get_symbol(10) == "G"


def test_get_symbol_unknown_case():
    e = Enemy(0, 0)
    assert e.get_symbol(10) == "?"

    e.set_max_energy_from_last_round(15)
    e.set_min_energy_from_last_round(5)
    assert e.get_symbol(10) == "?"

    e.set_max_energy_from_this_round(15)
    e.set_min_energy_from_this_round(5)
    assert e.get_symbol(10) == "?"

    e.set_max_energy_from_this_round(15)
    e.set_max_energy_from_last_round(5)
    e.set_min_energy_from_last_round(3)
    assert e.get_symbol(10) == "?"

    e.set_min_energy_from_this_round(1)
    e.set_max_energy_from_last_round(5)
    e.set_min_energy_from_last_round(3)
    assert e.get_symbol(10) == "?"
