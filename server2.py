"""
Simple Multiplayer Chat + Movement Game (Server + Client)
=========================================================
A minimal real-time multiplayer game using Python sockets.

Features:
- Multiple players connect to a server
- Players move on a 2D grid
- Server broadcasts player positions
- Text-based rendering

Run:
1. Start server:
   python server.py

2. Start clients in separate terminals:
   python client.py

Controls:
- W = up
- S = down
- A = left
- D = right
- Q = quit
"""

# =========================
# server.py
# =========================

import socket
import threading
import json

HOST = "0.0.0.0"
PORT = 5555

players = {}
clients = []

lock = threading.Lock()

def broadcast_game_state():
    state = json.dumps(players).encode()

    disconnected = []

    for client in clients:
        try:
            client.sendall(state)
        except:
            disconnected.append(client)

    for dc in disconnected:
        clients.remove(dc)

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr}")

    with lock:
        player_id = str(addr[1])
        players[player_id] = {"x": 5, "y": 5}
        clients.append(conn)

    broadcast_game_state()

    try:
        while True:
            data = conn.recv(1024).decode()

            if not data:
                break

            move = data.strip().upper()

            with lock:
                player = players[player_id]

                if move == "W":
                    player["y"] -= 1
                elif move == "S":
                    player["y"] += 1
                elif move == "A":
                    player["x"] -= 1
                elif move == "D":
                    player["x"] += 1

            broadcast_game_state()

    except Exception as e:
        print(f"[ERROR] {e}")

    finally:
        with lock:
            if player_id in players:
                del players[player_id]

            if conn in clients:
                clients.remove(conn)

        conn.close()
        broadcast_game_state()
        print(f"[DISCONNECTED] {addr}")

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    print(f"[SERVER STARTED] {HOST}:{PORT}")

    while True:
        conn, addr = server.accept()

        thread = threading.Thread(
            target=handle_client,
            args=(conn, addr),
            daemon=True
        )
        thread.start()

if __name__ == "__main__":
    start_server()