import argparse
import asyncio
import ssl
import websockets
from websockets.exceptions import ConnectionClosed

from . import game_state_manager_module

from .utils import Command, get_password_string_from_file, print_and_flush
from .calculate_next_step import (
    handle_beast_command_request,
    handle_beast_gone_INFO,
)

# accept self-signed certificate
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE


async def client_loop(
    username: str, password_file: str, hostname: str, port: int
):
    # store Passowrd in String "password"
    password = get_password_string_from_file(password_file)

    # establish connection
    websocket = await websockets.connect(
        f"wss://{hostname}:{port}/login", ssl=ssl_context
    )

    # send login (username and password)
    await websocket.send(f"{username}:{password}")

    # recieve answer to login and print it
    server_login_message = await websocket.recv()
    print(server_login_message)

    # Erschaffe einen Gamestate-manager
    game_state_manager = game_state_manager_module.Game_state_manager()
    while True:
        try:
            # wait for and recieve serverMessage
            server_message = await websocket.recv()
            server_command = Command(server_message)
            # match serverMessage to command and handle it
            match server_command:
                case Command.BEAST_COMMAND_REQUEST:
                    await handle_beast_command_request(
                        websocket, game_state_manager
                    )
                case Command.BEAST_GONE_INFO:
                    await handle_beast_gone_INFO(websocket, game_state_manager)
                case Command.NO_BEASTS_LEFT_INFO:
                    break
                case Command.SHUTDOWN_INFO:
                    break
        except websockets.ConnectionClosed:
            print("Verbindung wurde geschlossen")
            break
        except ValueError:
            print(f"Unbekannter Server-Befehl: {server_message}")
            continue


def client_main():
    parser = argparse.ArgumentParser()
    parser.add_argument("username", help="User name for authentification")
    parser.add_argument(
        "password_file_name",
        help="Name of File containing Password for authentification.",
    )
    parser.add_argument(
        "-n", "--hostname", type=str, help="Host name", default="localhost"
    )
    parser.add_argument(
        "-p", "--port", type=int, help="Port number", default=9721
    )
    args = parser.parse_args()
    try:
        asyncio.run(
            client_loop(
                args.username,
                args.password_file_name,
                args.hostname,
                args.port,
            )
        )
    except ConnectionClosed:
        print_and_flush("Connection closed by server")


if __name__ == "__main__":
    client_main()
