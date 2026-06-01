# v0_1/network/protocol.py

import json

def encode(msg: dict) -> bytes:
    return (json.dumps(msg) + "\n").encode()

def decode(raw: bytes):
    try:
        return json.loads(raw.decode())
    except:
        return None