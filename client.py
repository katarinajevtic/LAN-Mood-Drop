import socket
import threading
import json
import sys

# ---- Load config ----
with open("config.json") as f:
    config = json.load(f)

SERVER_IP = config["server_ip"]
SERVER_PORT = config["server_port"]

MOODS = {
    "1": "happy",
    "2": "tired",
    "3": "angry",
    "4": "focused"
}

def receive_messages(sock):
    while True:
        try:
            msg = sock.recv(1024).decode()
            if not msg:
                break
            print(msg, end="")
        except:
            break

def choose_mood():
    print("Choose mood:")
    print("1 - 😄 happy")
    print("2 - 😵 tired")
    print("3 - 😡 angry")
    print("4 - 🤖 focused")
    return MOODS.get(input("> ").strip(), "happy")

def start_client():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((SERVER_IP, SERVER_PORT))

    print("Connected to LAN Mood Drop\n")

    mood = choose_mood()
    print(f"\nCurrent mood: {mood}\n")

    print("Command:")
    print("/mood happy|tired|angry|focused")
    print("/users    → who is online")
    print("/stats    → mood statistic")
    print("/history  → message history")
    print("exit      → exit\n")

    threading.Thread(
        target=receive_messages,
        args=(sock,),
        daemon=True
    ).start()

    try:
        while True:
            text = input()
            if text.lower() in ("exit", "quit"):
                break
            sock.sendall(text.encode())
    except KeyboardInterrupt:
        pass
    finally:
        sock.close()
        sys.exit()

if __name__ == "__main__":
    start_client()


