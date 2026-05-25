# =========================
# client.py
# =========================

import socket
import threading
import json
import os

SERVER_IP = "127.0.0.1"
PORT = 5555

game_state = {}

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def render():
    clear_screen()

    width = 20
    height = 10

    grid = [["." for _ in range(width)] for _ in range(height)]

    for pid, pos in game_state.items():
        x = max(0, min(width - 1, pos["x"]))
        y = max(0, min(height - 1, pos["y"]))

        grid[y][x] = "P"

    print("=== Multiplayer Grid Game ===")
    print("Controls: W A S D | Q to quit\n")

    for row in grid:
        print(" ".join(row))

def receive_updates(sock):
    global game_state

    while True:
        try:
            data = sock.recv(4096)

            if not data:
                break

            game_state = json.loads(data.decode())
            render()

        except:
            break

def start_client():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((SERVER_IP, PORT))

    threading.Thread(
        target=receive_updates,
        args=(sock,),
        daemon=True
    ).start()

    while True:
        move = input("> ").strip().upper()

        if move == "Q":
            break

        if move in ["W", "A", "S", "D"]:
            sock.sendall(move.encode())

    sock.close()

if __name__ == "__main__":
    start_client()