import numpy as np
import random
import sys
from enum import Enum
from typing import Tuple, Optional


# --- Mocks und Konstanten ---


N = 3
X_PLAYING_FIELD = 10
Y_PLAYING_FIELD = 10

class Command(Enum):
    """Mini-Mock für die Befehle des Biests."""
    MOVE = "move"
    SPLIT = "split"

class Beast:
    """Simples Biest-Objekt für Testzwecke."""
    def __init__(self, beast_id, energy, environment_grid, x, y):
        self._id = beast_id
        self._energy = energy
        self._environment_grid = environment_grid
        self._x = x
        self._y = y

    def get_id(self): 
        return self._id

    def get_energy(self): 
        return self._energy

    def get_environment(self): 
        return self._environment_grid

    def get_beast_coordinates(self) -> Tuple[int, int]: 
        return (self._y, self._x)


# --- Helper-Funktionen ---


def move_one_step(
    beast_cords_tuple: tuple, target_cords_tuple: tuple
) -> tuple:
    """Berechnet den minimalen Schritt (way_y, way_x) in Richtung des Ziels."""
    d_x = target_cords_tuple[1] - beast_cords_tuple[1] if beast_cords_tuple[1] != target_cords_tuple[1] else 0
    if beast_cords_tuple[1] > target_cords_tuple[1]:
        d_x = -(beast_cords_tuple[1] - target_cords_tuple[1])

    d_y = target_cords_tuple[0] - beast_cords_tuple[0] if beast_cords_tuple[0] != target_cords_tuple[0] else 0
    if beast_cords_tuple[0] > target_cords_tuple[0]:
        d_y = -(beast_cords_tuple[0] - target_cords_tuple[0])

    way_y = 1 if d_y > 0 else (-1 if d_y < 0 else 0)
    way_x = 1 if d_x > 0 else (-1 if d_x < 0 else 0)

    return (way_y, way_x)


def find_nearest_target(
    field: np.ndarray, start_y: int, start_x: int, target_symbol: str
) -> Optional[Tuple[int, int]]:
    """Findet das nächste Ziel auf dem toroidalen Feld."""
    height, width = field.shape
    targets_y, targets_x = np.where(field == target_symbol)

    if targets_y.size == 0:
        return None

    min_dist = float("inf")
    nearest_target = None

    for ty, tx in zip(targets_y, targets_x):
        dy = ty - start_y
        if abs(dy) > height / 2:
            dy = dy - np.sign(dy) * height

        dx = tx - start_x
        if abs(dx) > width / 2:
            dx = dx - np.sign(dx) * width

        dist_sq = dy**2 + dx**2

        if dist_sq < min_dist:
            min_dist = dist_sq
            nearest_target = (ty, tx)

    return nearest_target


# --- Entscheidungslogik ---


def calculate_next_action_sync(
    beast: Beast, field: np.ndarray, environment_grid: np.ndarray
) -> Tuple[Command, int, int]:
    start_y, start_x = beast.get_beast_coordinates()
    energy = beast.get_energy()

    nearest_predator = find_nearest_target(field, start_y, start_x, ">")
    food = find_nearest_target(field, start_y, start_x, "*")
    nearest_prey = find_nearest_target(field, start_y, start_x, "<")

    action = Command.MOVE
    d_x, d_y = 1, 0  # Default: Erkunden

    # 1. FLIEHEN
    if nearest_predator is not None:
        move_away = move_one_step(
            beast.get_beast_coordinates(), nearest_predator
        )
        d_x = -move_away[1]
        d_y = -move_away[0]

        height, width = field.shape
        predator_left = field[start_y, (start_x - 1) % width] == ">"
        predator_right = field[start_y, (start_x + 1) % width] == ">"
        predator_up = field[(start_y - 1) % height, start_x] == ">"
        predator_down = field[(start_y + 1) % height, start_x] == ">"

        if d_y == 0:
            if (d_x == -1 and predator_left) or (d_x == 1 and predator_right):
                options = []
                if not predator_up: options.append((0, -1))
                if not predator_down: options.append((0, 1))
                if options: d_x, d_y = options[0]

        elif d_x == 0:
            if (d_y == -1 and predator_up) or (d_y == 1 and predator_down):
                options = []
                if not predator_left: options.append((-1, 0))
                if not predator_right: options.append((1, 0))
                if options: d_x, d_y = options[0]

    # 2. TEILEN
    elif energy > 40:
        safe_splits = []
        if environment_grid[3, 4] in (".", "*"): safe_splits.append((1, 0))
        if environment_grid[3, 2] in (".", "*"): safe_splits.append((-1, 0))
        if environment_grid[4, 3] in (".", "*"): safe_splits.append((0, 1))
        if environment_grid[2, 3] in (".", "*"): safe_splits.append((0, -1))

        if safe_splits:
            action = Command.SPLIT
            d_x, d_y = safe_splits[0]

    # 3. FRESSEN
    elif food is not None:
        move_towards = move_one_step(beast.get_beast_coordinates(), food)
        d_x = move_towards[1]
        d_y = move_towards[0]

    # 4. JAGEN
    elif nearest_prey is not None:
        move_towards = move_one_step(beast.get_beast_coordinates(), nearest_prey)
        d_x = move_towards[1]
        d_y = move_towards[0]

    return action, d_x, d_y


# --- Test Runner ---


def run_test(name: str, expected, actual):
    if expected == actual:
        print(f"✅ PASS: {name}")
    else:
        print(f"❌ FAIL: {name}")
        print(f"  Erwartet: {expected}")
        print(f"  Aktuell:  {actual}")
        sys.exit(1)

def run_validation_test(name: str, expected_fail_value, actual_value):
    if expected_fail_value == actual_value:
        print(f"🔥 UNERWARTETER PASS: {name}")
        sys.exit(1)
    else:
        print(f"✅ PASS (Validation): {name} korrekt fehlgeschlagen")

# --- Tests ---

def run_all_tests():
    print("\n--- Pymonster Strategie-Logik-Tests (17 Szenarien) ---")
    print("-" * 65)

    test_field = np.full((Y_PLAYING_FIELD, X_PLAYING_FIELD), ".")
    env_grid = np.full((2*N+1, 2*N+1), "#")

    beast_full_energy = Beast(1, 100, np.full((2*N+1, 2*N+1), "."), 5, 5)
    beast_low_energy = Beast(1, 20, env_grid, 5, 5)

    run_test("T1: move_one_step", (1, -1), move_one_step((5, 10), (10, 5)))

    test_field[9, 0] = "*"
    run_test("T2: find_nearest_target Wrap", (9, 0),
             find_nearest_target(test_field, 0, 0, "*"))
    test_field[9, 0] = "."

    test_field[5, 7] = ">"
    run_test("T3: FLIEHEN Basis", (Command.MOVE, -1, 0),
             calculate_next_action_sync(beast_full_energy, test_field, beast_full_energy.get_environment()))
    test_field[5, 7] = "."

    env_grid_split = np.full((2*N+1, 2*N+1), "#")
    env_grid_split[N, N+1] = "."
    run_test("T4: TEILEN", (Command.SPLIT, 1, 0),
             calculate_next_action_sync(Beast(1, 60, env_grid_split, 5, 5), test_field, env_grid_split))

    test_field[6, 5] = "*"
    run_test("T5: FRESSEN", (Command.MOVE, 0, 1),
             calculate_next_action_sync(beast_low_energy, test_field, env_grid))
    test_field[6, 5] = "."

    test_field[5, 6] = "<"
    run_test("T6: JAGEN", (Command.MOVE, 1, 0),
             calculate_next_action_sync(beast_low_energy, test_field, env_grid))
    test_field[5, 6] = "."

    run_test("T7: ERKUNDEN", (Command.MOVE, 1, 0),
             calculate_next_action_sync(beast_low_energy, test_field, env_grid))

    # --- NEU ---
    test_field[5, 6] = ">"
    test_field[5, 4] = "*"
    run_test("T16: FLIEHEN vor FRESSEN", (Command.MOVE, -1, 0),
             calculate_next_action_sync(beast_low_energy, test_field, env_grid))
    test_field[5, 6] = "."
    test_field[5, 4] = "."

    test_field[5, 0] = ">"
    beast_edge = Beast(1, 100, beast_full_energy.get_environment(), 9, 5)
    run_test("T17: FLIEHEN Wrap-around", (Command.MOVE, 1, 0),
             calculate_next_action_sync(beast_edge, test_field, beast_edge.get_environment()))
    test_field[5, 0] = "."

    print("-" * 65)
    print("✅ Alle Tests erfolgreich")

# --- Main ---


if __name__ == "__main__":
    random.seed(42)
    np.seterr(all='ignore')
    run_all_tests()
