"""
SECURE MULTIPLAYER GAME (Python)
================================

Architecture:
- Authoritative server
- TCP networking
- Encrypted communication (TLS)
- Login authentication
- Session tokens
- Rate limiting
- Input validation
- Thread-safe state
- Anti-cheat movement validation

Files:
    server.py
    client.py

INSTALL:
---------
pip install bcrypt

GENERATE TLS CERTIFICATE:
-------------------------
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

RUN:
----
python server.py
python client.py

Default users:
---------------
username: player1
password: password123
"""

# ============================================================
# server.py
# ============================================================

import socket
import ssl
import threading
import json
import time
import bcrypt
import secrets

HOST = "0.0.0.0"
PORT = 5555

WORLD_W = 30
WORLD_H = 15

MAX_PACKET_SIZE = 2048
MOVE_COOLDOWN = 0.05

# ============================================================
# USER DATABASE (replace with real DB)
# ============================================================

users = {
    "player1": bcrypt.hashpw(
        b"password123",
        bcrypt.gensalt()
    )
}

# ============================================================
# GAME STATE
# ============================================================

players = {}
clients = {}
sessions = {}

lock = threading.Lock()

# ============================================================
# HELPERS
# ============================================================

def send_json(conn, data):
    payload = json.dumps(data).encode()

    if len(payload) > MAX_PACKET_SIZE:
        return

    conn.sendall(payload + b"\n")


def recv_json(conn):
    data = conn.recv(MAX_PACKET_SIZE)

    if not data:
        return None

    return json.loads(data.decode())


def broadcast_state():
    with lock:
        state = {
            "type": "state",
            "players": players
        }

        dead = []

        for conn in clients.values():
            try:
                send_json(conn, state)
            except:
                dead.append(conn)

        for dc in dead:
            try:
                dc.close()
            except:
                pass


def valid_move(x, y):
    return 0 <= x < WORLD_W and 0 <= y < WORLD_H


# ============================================================
# AUTH
# ============================================================

def authenticate(username, password):
    if username not in users:
        return False

    return bcrypt.checkpw(
        password.encode(),
        users[username]
    )


def create_session(username):
    token = secrets.token_hex(32)

    sessions[token] = {
        "username": username,
        "created": time.time()
    }

    return token


# ============================================================
# CLIENT HANDLER
# ============================================================

def handle_client(conn, addr):
    print(f"[CONNECTED] {addr}")

    username = None

    try:
        # ----------------------------------------------------
        # LOGIN
        # ----------------------------------------------------

        login = recv_json(conn)

        if not login:
            return

        if login.get("type") != "login":
            return

        username = login.get("username", "")
        password = login.get("password", "")

        if not authenticate(username, password):
            send_json(conn, {
                "type": "error",
                "message": "Invalid credentials"
            })
            return

        token = create_session(username)

        send_json(conn, {
            "type": "login_success",
            "token": token
        })

        # ----------------------------------------------------
        # ADD PLAYER
        # ----------------------------------------------------

        with lock:
            players[username] = {
                "x": 5,
                "y": 5,
                "hp": 100
            }

            clients[username] = conn

        broadcast_state()

        last_move = 0

        # ----------------------------------------------------
        # GAME LOOP
        # ----------------------------------------------------

        while True:
            packet = recv_json(conn)

            if not packet:
                break

            # --------------------------------------------
            # RATE LIMITING
            # --------------------------------------------

            now = time.time()

            if now - last_move < MOVE_COOLDOWN:
                continue

            last_move = now

            # --------------------------------------------
            # VALIDATE SESSION
            # --------------------------------------------

            if packet.get("token") != token:
                continue

            action = packet.get("action")

            with lock:
                player = players.get(username)

                if not player:
                    break

                new_x = player["x"]
                new_y = player["y"]

                if action == "UP":
                    new_y -= 1

                elif action == "DOWN":
                    new_y += 1

                elif action == "LEFT":
                    new_x -= 1

                elif action == "RIGHT":
                    new_x += 1

                # ----------------------------------------
                # SERVER-SIDE VALIDATION
                # ----------------------------------------

                if valid_move(new_x, new_y):
                    player["x"] = new_x
                    player["y"] = new_y

            broadcast_state()

    except Exception as e:
        print("[ERROR]", e)

    finally:
        print(f"[DISCONNECTED] {addr}")

        with lock:
            if username in players:
                del players[username]

            if username in clients:
                del clients[username]

        try:
            conn.close()
        except:
            pass

        broadcast_state()


# ============================================================
# SERVER START
# ============================================================

def start_server():
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)

    context.load_cert_chain(
        certfile="cert.pem",
        keyfile="key.pem"
    )

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server.bind((HOST, PORT))
    server.listen(10)

    print(f"[SECURE SERVER RUNNING] {HOST}:{PORT}")

    while True:
        client_socket, addr = server.accept()

        secure_conn = context.wrap_socket(
            client_socket,
            server_side=True
        )

        thread = threading.Thread(
            target=handle_client,
            args=(secure_conn, addr),
            daemon=True
        )

        thread.start()


if __name__ == "__main__":
    start_server()