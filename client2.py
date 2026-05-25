# ============================================================
# client.py
# ============================================================

import socket
import ssl
import json
import threading
import os

SERVER_IP = "127.0.0.1"
PORT = 5555

game_state = {}
token = None

# ============================================================
# NETWORK HELPERS
# ============================================================

def send_json(sock, data):
    sock.sendall(
        (json.dumps(data) + "\n").encode()
    )


def recv_json(sock):
    data = sock.recv(4096)

    if not data:
        return None

    return json.loads(data.decode())


# ============================================================
# RENDER
# ============================================================

def clear():
    os.system("cls" if os.name == "nt" else "clear")


def render():
    clear()

    width = 30
    height = 15

    grid = [
        ["." for _ in range(width)]
        for _ in range(height)
    ]

    for name, p in game_state.items():
        x = p["x"]
        y = p["y"]

        if 0 <= x < width and 0 <= y < height:
            grid[y][x] = name[0].upper()

    print("=== SECURE MULTIPLAYER GAME ===")
    print("Controls: W A S D")
    print()

    for row in grid:
        print(" ".join(row))


# ============================================================
# RECEIVE THREAD
# ============================================================

def receive_loop(sock):
    global game_state

    while True:
        try:
            packet = recv_json(sock)

            if not packet:
                break

            if packet["type"] == "state":
                game_state = packet["players"]
                render()

        except:
            break


# ============================================================
# MAIN
# ============================================================

def main():
    global token

    context = ssl.create_default_context()

    # Self-signed cert support
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    raw_sock = socket.socket(socket.AF_INET)

    secure_sock = context.wrap_socket(
        raw_sock,
        server_hostname=SERVER_IP
    )

    secure_sock.connect((SERVER_IP, PORT))

    username = input("Username: ")
    password = input("Password: ")

    # --------------------------------------------------------
    # LOGIN
    # --------------------------------------------------------

    send_json(secure_sock, {
        "type": "login",
        "username": username,
        "password": password
    })

    response = recv_json(secure_sock)

    if response["type"] != "login_success":
        print("Login failed")
        return

    token = response["token"]

    print("Authenticated!")

    threading.Thread(
        target=receive_loop,
        args=(secure_sock,),
        daemon=True
    ).start()

    # --------------------------------------------------------
    # INPUT LOOP
    # --------------------------------------------------------

    while True:
        key = input("> ").strip().upper()

        action = None

        if key == "W":
            action = "UP"

        elif key == "S":
            action = "DOWN"

        elif key == "A":
            action = "LEFT"

        elif key == "D":
            action = "RIGHT"

        if action:
            send_json(secure_sock, {
                "token": token,
                "action": action
            })


if __name__ == "__main__":
    main()