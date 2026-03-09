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
    """Simples Biest-Objekt für Testzwecke, hält die wichtigsten Daten."""
    def __init__(self, beast_id, energy, environment_grid, x, y):
        self._id = beast_id
        self._energy = energy
        self._environment_grid = environment_grid
        self._x = x
        self._y = y

    def get_id(self): return self._id
    def get_energy(self): return self._energy
    def get_environment(self): return self._environment_grid
    def get_beast_coordinates(self) -> Tuple[int, int]: return (self._y, self._x)

# --- Originale Hilfsfunktionen ---

def move_one_step(
    beast_cords_tuple: tuple, target_cords_tuple: tuple
) -> tuple:
    """Berechnet den minimalen Schritt (way_y, way_x) in Richtung des Ziels."""
    d_x = target_cords_tuple[1] - beast_cords_tuple[1] if beast_cords_tuple[1] != target_cords_tuple[1] else 0
    if beast_cords_tuple[1] > target_cords_tuple[1]: d_x = -(beast_cords_tuple[1] - target_cords_tuple[1])

    d_y = target_cords_tuple[0] - beast_cords_tuple[0] if beast_cords_tuple[0] != target_cords_tuple[0] else 0
    if beast_cords_tuple[0] > target_cords_tuple[0]: d_y = -(beast_cords_tuple[0] - target_cords_tuple[0])

    way_y = 1 if d_y > 0 else (-1 if d_y < 0 else 0)
    way_x = 1 if d_x > 0 else (-1 if d_x < 0 else 0)

    return (way_y, way_x)


def find_nearest_target(
    field: np.ndarray, start_y: int, start_x: int, target_symbol: str
) -> Optional[Tuple[int, int]]:
    """Findet das nächste Ziel auf dem toroidalen Feld (mit Wrap-around)."""
    height, width = field.shape

    targets_y, targets_x = np.where(field == target_symbol)

    if targets_y.size == 0: return None

    min_dist = float("inf")
    nearest_target = None

    for ty, tx in zip(targets_y, targets_x):
        dy = ty - start_y
        if abs(dy) > height / 2: dy = dy - np.sign(dy) * height

        dx = tx - start_x
        if abs(dx) > width / 2: dx = dx - np.sign(dx) * width

        dist_sq = dy**2 + dx**2

        if dist_sq < min_dist:
            min_dist = dist_sq
            nearest_target = (ty, tx)

    return nearest_target

# --- Isolierte Entscheidungslogik (vollständig kopiert) ---

def calculate_next_action_sync(
    beast: Beast, field: np.ndarray, environment_grid: np.ndarray
) -> Tuple[Command, int, int]:
    """Simuliert die Strategie-Pipeline synchron."""
    
    start_y, start_x = beast.get_beast_coordinates()
    energy = beast.get_energy()

    # Die Strategie ignoriert das Symbol "=" (gleich starker Rivale)
    nearest_predator = find_nearest_target(field, start_y, start_x, ">")
    food = find_nearest_target(field, start_y, start_x, "*")
    nearest_prey = find_nearest_target(field, start_y, start_x, "<")

    action = Command.MOVE
    d_x, d_y = 1, 0

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

        # Horizontale Flucht
        if d_y == 0:
            if (d_x == -1 and predator_left) or (d_x == 1 and predator_right):
                options = []
                if not predator_up: options.append((0, -1))
                if not predator_down: options.append((0, 1))

                if options: d_x, d_y = options[0]
                else: d_x, d_y = 1, 0

        # Vertikale Flucht
        elif d_x == 0:
            if (d_y == -1 and predator_up) or (d_y == 1 and predator_down):
                options = []
                if not predator_left: options.append((-1, 0))
                if not predator_right: options.append((1, 0))

                if options: d_x, d_y = options[0]
                else: d_x, d_y = 0, 1

        action = Command.MOVE

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
        action = Command.MOVE

    # 4. JAGEN
    elif nearest_prey is not None:
        move_towards = move_one_step(
            beast.get_beast_coordinates(), nearest_prey
        )
        d_x = move_towards[1]
        d_y = move_towards[0]
        action = Command.MOVE

    return action, d_x, d_y

# --- Test Runner ---

def run_test(name: str, expected, actual):
    """Funktion, um Ergebnisse zu vergleichen und bei Fehlschlag abzubrechen."""
    if expected == actual:
        print(f"✅ PASS: {name}")
    else:
        print(f"❌ FAIL: {name}")
        print(f"  Erwartet: {expected}")
        print(f"  Aktuell:  {actual}")
        sys.exit(1)

def run_validation_test(name: str, expected_fail_value, actual_value):
    """Dieser Test soll absichtlich fehlschlagen, um die Test-Engine zu prüfen."""
    if expected_fail_value == actual_value:
        print(f"🔥 UNERWARTETER PASS: {name}")
        print(f"  Der Test sollte fehlschlagen, liefert aber True: {expected_fail_value} == {actual_value}")
        sys.exit(1)
    else:
        print(f"✅ PASS (Validation): {name} ist korrekt fehlgeschlagen.")

def run_all_tests():
    print(); print()
    print("--- Pymonster Strategie-Logik-Tests (14 Szenarien) ---")
    print("-" * 65)

    # --- Setup ---
    test_field = np.full((Y_PLAYING_FIELD, X_PLAYING_FIELD), ".")
    env_grid = np.full((2*N+1, 2*N+1), "#")
    beast_full_energy = Beast(1, 100, np.full((2*N+1, 2*N+1), "."), 5, 5)
    beast_low_energy = Beast(1, 20, env_grid, 5, 5)
    
    # --- Basis-Tests T1 bis T13 (mit T13 als Validation Check) ---
    
    run_test("T1: Helper: move_one_step", (1, -1), move_one_step((5, 10), (10, 5)))
    test_field[9, 0] = "*"; run_test("T2: Helper: find_nearest_target (Wrap-around, nah)", (9, 0), find_nearest_target(test_field, 0, 0, "*")); test_field[9, 0] = "."
    test_field[5, 7] = ">"; run_test("T3: Strategie: FLIEHEN (Basis-Flucht)", (Command.MOVE, -1, 0), calculate_next_action_sync(beast_full_energy, test_field, beast_full_energy.get_environment())); test_field[5, 7] = "."
    env_grid_split = np.full((2*N+1, 2*N+1), "#"); env_grid_split[N, N+1] = "."
    run_test("T4: Strategie: TEILEN", (Command.SPLIT, 1, 0), calculate_next_action_sync(Beast(1, 60, env_grid_split, 5, 5), test_field, env_grid_split))
    test_field[6, 5] = "*"; test_field[5, 6] = "<"; run_test("T5: Strategie: FRESSEN", (Command.MOVE, 0, 1), calculate_next_action_sync(beast_low_energy, test_field, env_grid)); test_field[6, 5] = "."; test_field[5, 6] = "."
    test_field[5, 6] = "<"; run_test("T6: Strategie: JAGEN", (Command.MOVE, 1, 0), calculate_next_action_sync(beast_low_energy, test_field, env_grid)); test_field[5, 6] = "."
    run_test("T7: Strategie: ERKUNDEN", (Command.MOVE, 1, 0), calculate_next_action_sync(beast_low_energy, test_field, env_grid))
    test_field[5, 4] = ">"; test_field[5, 6] = ">"; run_test("T8: FLIEHEN (Horizontal blockiert)", (Command.MOVE, 0, -1), calculate_next_action_sync(beast_full_energy, test_field, beast_full_energy.get_environment())); test_field[5, 4] = "."; test_field[5, 6] = "."
    test_field[6, 5] = ">"; test_field[4, 5] = ">"; run_test("T9: FLIEHEN (Vertikal blockiert)", (Command.MOVE, -1, 0), calculate_next_action_sync(beast_full_energy, test_field, beast_full_energy.get_environment())); test_field[6, 5] = "."; test_field[4, 5] = "."
    test_field[6, 6] = ">"; run_test("T10: FLIEHEN (Diagonale Flucht)", (Command.MOVE, -1, -1), calculate_next_action_sync(beast_full_energy, test_field, beast_full_energy.get_environment())); test_field[6, 6] = "."
    run_test("T11: TEILEN (Kein sicherer Ort)", (Command.MOVE, 1, 0), calculate_next_action_sync(Beast(1, 60, env_grid, 5, 5), test_field, env_grid))
    test_field = np.full((10, 10), "."); test_field[5, 5] = "*"; run_test("T12: Helper: find_nearest_target (Wrap-around, Gegner mittig)", (5, 5), find_nearest_target(test_field, 0, 0, "*")); test_field[5, 5] = "."

    # ------------------------------------------------------------------
    # --- NEUER TEST: T14 (FELD-SICHERHEIT: Ignorieren des '=' Rivalen) ---
    # ------------------------------------------------------------------
    # Testet, ob das Biest einen '=' Rivalen ignoriert (da es nicht im Suchpfad ist) und 
    # stattdessen ERKUNDEN wählt, um den tödlichen Kampf zu vermeiden.
    test_field[6, 5] = "=" # Rival 1 Einheit unten
    run_test(
        "T14: Feld-Sicherheit (Ignorieren des '=' Rivalen)",
        (Command.MOVE, 1, 0), # Muss ERKUNDEN (Default) wählen
        calculate_next_action_sync(beast_low_energy, test_field, env_grid)
    )
    test_field[6, 5] = "."

    # ------------------------------------------------------------------
    # --- T15: VALIDATION CHECK (MUSS FEHLSCHLAGEN!) ---
    # ------------------------------------------------------------------
    # Neu nummeriert als T15
    test_field = np.full((Y_PLAYING_FIELD, X_PLAYING_FIELD), ".")
    env_grid = np.full((2*N+1, 2*N+1), "#")
    beast = Beast(1, 20, env_grid, 5, 5)
    actual_result = calculate_next_action_sync(beast, test_field, env_grid)
    expected_failure = (Command.SPLIT, 1, 0) 
    
    run_validation_test(
        "T15: VALIDATION CHECK (Sollte absichtlich fehlschlagen)",
        expected_failure,
        actual_result
    )


    print("-" * 65)
    
    print("T15: Validation PASS - Fehlschlag erwartet")
    print()


if __name__ == "__main__":
    random.seed(42)
    np.seterr(all='ignore')
    run_all_tests()