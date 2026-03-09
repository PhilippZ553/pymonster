"""
Modul für Hilfsfunktionen/-klassen:

Klassen: Command

Funktionen:  print_and_flush, get_beast_strings_from_server_message,
get_password_string_from_file
"""

from enum import Enum
import sys


class Command(Enum):
    """
    Repräsentiert die request und response Commands von Biest und Server
    """

    BEAST_COMMAND_REQUEST = "BEAST_COMMAND_REQUEST"
    BEAST_GONE_INFO = "BEAST_GONE_INFO"
    NO_BEASTS_LEFT_INFO = "NO_BEASTS_LEFT_INFO"
    SHUTDOWN_INFO = "SHUTDOWN_INFO"
    MOVE = "MOVE"
    SPLIT = "SPLIT"


def print_and_flush(message: str):
    print(message)
    sys.stdout.flush()


def get_beast_strings_from_server_message(
    beast_info_string: str,
) -> tuple[int, float, str]:
    beast_id_str, energy_str, environment_str = beast_info_string.split("#")
    return int(beast_id_str), float(energy_str), str(environment_str)


def get_password_string_from_file(password_file: str) -> str:
    try:
        with open(password_file, "r", encoding="utf-8") as pw_file:
            return pw_file.read().strip("\n").strip()
    except Exception as e:
        raise ValueError(
            f"Error reading Password file: {password_file}"
        ) from e
