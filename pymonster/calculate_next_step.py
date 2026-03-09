"""Modul zur Bewegungslogik des Beast

Diese Modul berechnet die Richtung der Bewegung und wandelt diese in
einen Server-Command um.
"""

import random
import numpy as np

from .game_state_manager_module import Game_state_manager
from .utils import get_beast_strings_from_server_message, Command
from .config import N, X_PLAYING_FIELD, Y_PLAYING_FIELD
from .beast_module import Beast


async def handle_beast_command_request(
    websocket, game_state_manager: Game_state_manager
):
    """
    Funktion für die Bewegungslogik des Beast.

    Args:
        websocket: Sender der Server-Informationen
        game_state_manager (Game_state_manager): Informationsträger für das ganze Feld
    """
    beast_info_message = await websocket.recv()
    beast_strings = get_beast_strings_from_server_message(beast_info_message)
    (beast_id, energy, environment_str) = beast_strings

    beast = game_state_manager.get_beast_from_id(beast_id)

    if beast is None:
        new_beast = Beast(beast_id, energy, environment_str, 0, 0, 1)
        game_state_manager.add_beast(new_beast)
        beast = new_beast
    else:
        game_state_manager.update_beast(beast_strings)

    # aktueller Zustand
    (field, enemies) = game_state_manager.get_gamestate(
        beast, Y_PLAYING_FIELD, X_PLAYING_FIELD
    )

    # biest infos
    beast_id = beast.get_id()
    energy = beast.get_energy()
    environment_grid = beast.get_environment()

    beast = game_state_manager.get_beast_from_id(beast_id)

    # nearest Objects im environment
    start_y, start_x = beast.get_beast_coordinates()

    nearest_predator = find_nearest_target(field, start_y, start_x, ">")
    food = find_nearest_target(field, start_y, start_x, "*")
    nearest_prey = find_nearest_target(field, start_y, start_x, "<")

    # Standard-Aktion: Erkunden
    action = Command.MOVE
    explore_moves = [
        (0, 1),
        (0, -1),
        (1, 0),
        (-1, 0),
        (1, 1),
        (-1, -1),
        (1, -1),
        (-1, 1),
    ]

    # Standard-Bewegung falls keine andere Logik greift
    d_x, d_y = random.choice(explore_moves)

    # --- Strategie-Prioritäten ---
    # 1. FLIEHEN (Höchste Priorität)
    if nearest_predator is not None:
        move_away = move_one_step(
            beast.get_beast_coordinates(), nearest_predator
        )

        # normale Gegenrichtung berechnen
        d_x = -move_away[1]
        d_y = -move_away[0]

        # verbesserte Ausweichlogik
        height, width = field.shape

        predator_left = field[start_y, (start_x - 1) % width] == ">"
        predator_right = field[start_y, (start_x + 1) % width] == ">"
        predator_up = field[(start_y - 1) % height, start_x] == ">"
        predator_down = field[(start_y + 1) % height, start_x] == ">"

        # horizontale Gefahr
        if d_y == 0:
            if (d_x == -1 and predator_left) or (d_x == 1 and predator_right):
                options = []
                if not predator_up:
                    options.append((0, -1))
                if not predator_down:
                    options.append((0, 1))

                if options:
                    d_x, d_y = random.choice(options)
                else:
                    d_x, d_y = random.choice(
                        [(1, 0), (-1, 0), (0, 1), (0, -1)]
                    )

        # vertikale Gefahr
        elif d_x == 0:
            if (d_y == -1 and predator_up) or (d_y == 1 and predator_down):
                options = []
                if not predator_left:
                    options.append((-1, 0))
                if not predator_right:
                    options.append((1, 0))

                if options:
                    d_x, d_y = random.choice(options)
                else:
                    d_x, d_y = random.choice(
                        [(1, 0), (-1, 0), (0, 1), (0, -1)]
                    )

        action = Command.MOVE

    # 2. TEILEN (Sichere Energie > 80) -- auf MINIMALE Energie gesetzt (40)
    elif energy > 40:
        safe_splits = []
        if environment_grid[3, 4] in (".", "*"):
            safe_splits.append((1, 0))
        if environment_grid[3, 2] in (".", "*"):
            safe_splits.append((-1, 0))
        if environment_grid[4, 3] in (".", "*"):
            safe_splits.append((0, 1))
        if environment_grid[2, 3] in (".", "*"):
            safe_splits.append((0, -1))

        if safe_splits:
            action = Command.SPLIT
            d_x, d_y = random.choice(safe_splits)

    # 3. FRESSEN
    elif food is not None:
        move_towards = move_one_step(beast.get_beast_coordinates(), food)
        d_x = move_towards[1]
        d_y = move_towards[0]

        if d_x == 0 and d_y == 0 and environment_grid[N, N] != "*":
            d_x, d_y = random.choice(explore_moves)

        action = Command.MOVE

    # 4. JAGEN
    elif nearest_prey is not None:
        move_towards = move_one_step(
            beast.get_beast_coordinates(), nearest_prey
        )
        d_x = move_towards[1]
        d_y = move_towards[0]
        action = Command.MOVE

    # 5. Befehl formatieren und an den Server senden
    server_command = f"{beast_id} {action.value} {d_x} {d_y}"
    await websocket.send(server_command)

    # 6. Antwort vom Server abwarten und verarbeiten
    server_response = await websocket.recv()

    if "ERROR" in server_response:
        print(
            f"Server-FEHLER für Biest {beast_id} nach Befehl '{server_command}': {server_response}"
        )
    else:
        new_beast_id_str, success_str = server_response.split("#")

        if success_str == "True":
            if action == Command.MOVE:
                beast.move(d_x, d_y)

            elif action == Command.SPLIT and new_beast_id_str != "None":
                new_beast_id = int(new_beast_id_str)
                new_beast_energy = energy / 2

                new_beast_x = beast.get_x_coordinate() + d_x
                new_beast_y = beast.get_y_coordinate() + d_y

                new_beast = Beast(
                    new_beast_id,
                    new_beast_energy,
                    "...",
                    new_beast_x,
                    new_beast_y,
                    beast.get_update_counter(),
                )
                game_state_manager.add_beast(new_beast)

                print(
                    f"Biest {beast_id} hat sich ERFOLGREICH geteilt! Neues Biest ID: {new_beast_id}"
                )


async def handle_beast_gone_INFO(
    websocket, game_state_manager: Game_state_manager
):
    """Verarbeitet die Information,
    wenn ein Biest aus der Simulation entfernt wird

    Args:
        websocket: Server-Information
        Game_state_manager (game_state_manager): Regelt das Spiel
    """
    beast_info_message = await websocket.recv()
    beast_strings = get_beast_strings_from_server_message(beast_info_message)

    beast_id = beast_strings[0]

    game_state_manager.delete_beast(beast_id)

    print(
        f"INFO: Biest {beast_id} ist gestorben und wurde aus dem Manager entfernt."
    )


async def handle_no_beasts_left(
    websocket, game_state_manager: Game_state_manager
):
    """Steuert was passiert wenn keine Beaster mehr vorhanden sind

    Args:
        websocket:
        Game_state_manager (game_state_manager): Regelt das Spiel
    """
    print("GAME OVER: Alle Biester sind verloren.")
    game_state_manager.beasts = []


def find_nearest_target(
    field: np.ndarray, start_y: int, start_x: int, target_symbol: str
) -> tuple[int, int] | None:
    """Findet das am wenigsten entfernte Symbol vom Biest

    Args:
        field (np.ndarray): feld vom gamestate
        start_y (int): y cord von dem biest
        start_x (int): x cord vom biest
        target_symbol (str): gesuchtes symbol
    Returns:
        nearest_target (tuple): cords des nearest_target
    """
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


def move_one_step(
    beast_cords_tuple: tuple, target_cords_tuple: tuple
) -> tuple:
    """Funktion welche sich einen Schritt an das übergebene Ziel annähert.
    (Diese Klasse wurde später verändert damit das Beast mehr als einen Schritt laufen konnte)

    Args:
        beast_cords_tuple (tuple): Koordinaten des Beast
        target_cords_tuple (tuple): Koordinaten des Ziels

    Returns:
        (way_y, way_x) (tuple): Bewegungsrichtung für das Biest
    """
    if beast_cords_tuple[1] < target_cords_tuple[1]:
        d_x = target_cords_tuple[1] - beast_cords_tuple[1]
    elif beast_cords_tuple[1] > target_cords_tuple[1]:
        d_x = -(beast_cords_tuple[1] - target_cords_tuple[1])
    else:
        d_x = 0

    if beast_cords_tuple[0] < target_cords_tuple[0]:
        d_y = target_cords_tuple[0] - beast_cords_tuple[0]
    elif beast_cords_tuple[0] > target_cords_tuple[0]:
        d_y = -(beast_cords_tuple[0] - target_cords_tuple[0])
    else:
        d_y = 0

    if d_y > 0:
        way_y = 1
    elif d_y < 0:
        way_y = -1
    else:
        way_y = 0

    if d_x > 0:
        way_x = 1
    elif d_x < 0:
        way_x = -1
    else:
        way_x = 0

    return (way_y, way_x)
