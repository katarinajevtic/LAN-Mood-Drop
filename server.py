import socket
import threading
import json
from datetime import datetime
from collections import Counter

# ---- Load config ----
with open("config.json") as f:
    config = json.load(f)

HOST = "0.0.0.0"
PORT = config["server_port"]
SUMMARY_INTERVAL = config.get("summary_interval", 10)

clients = []
clients_lock = threading.Lock()

client_moods = {}          # socket -> mood
message_history = []
MAX_HISTORY = 20

mood_counter = Counter()
message_count = 0

VALID_MOODS = {
    "happy": "😄",
    "tired": "😵",
    "angry": "😡",
    "focused": "🤖"
}

# ---- Helpers ----
def broadcast(message, sender=None):
    with clients_lock:
        for c in clients:
            if c != sender:
                try:
                    c.sendall(message.encode())
                except:
                    clients.remove(c)

def send_stats(to_socket):
    response = "\n📊 Mood statistic:\n"
    for mood, emoji in VALID_MOODS.items():
        response += f"{emoji} {mood}: {mood_counter[mood]}\n"
    response += "\n"
    to_socket.sendall(response.encode())

def send_users(to_socket):
    with clients_lock:
        users = [
            f"{c.getpeername()[0]}:{c.getpeername()[1]} ({client_moods.get(c)})"
            for c in clients
        ]

    response = "\n👥 Online users:\n"
    response += "\n".join(users) if users else "No online users"
    response += "\n\n"

    to_socket.sendall(response.encode())

def send_history(to_socket):
    if not message_history:
        to_socket.sendall("📭 No message history.\n\n".encode())
        return

    response = "\n📜 History (last messages):\n"
    for msg in message_history:
        response += msg
    response += "\n"

    to_socket.sendall(response.encode())

# ---- Client handler ----
def handle_client(client_socket, address):
    global message_count

    client_moods[client_socket] = "happy"
    print(f"[CONNECTED] {address[0]}:{address[1]}")

    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break

            raw = data.decode().strip()
            timestamp = datetime.now().strftime("%H:%M:%S")

            # ---- COMMANDS ----
            if raw.startswith("/mood"):
                parts = raw.split()
                if len(parts) == 2 and parts[1] in VALID_MOODS:
                    client_moods[client_socket] = parts[1]
                    client_socket.sendall(
                        f"✅ Mood changed to {parts[1]}\n".encode()
                    )
                else:
                    client_socket.sendall(
                        "❌ Use: /mood happy|tired|angry|focused\n".encode()
                    )
                continue

            if raw == "/users":
                send_users(client_socket)
                continue

            if raw == "/stats":
                send_stats(client_socket)
                continue

            if raw == "/history":
                send_history(client_socket)
                continue


            mood = client_moods.get(client_socket, "unknown")
            emoji = VALID_MOODS.get(mood, "❓")

            mood_counter[mood] += 1
            message_count += 1

            formatted = (
                f"[{timestamp}] "
                f"{address[0]}:{address[1]} "
                f"{emoji} → {raw}\n"
            )

            print(formatted.strip())

            message_history.append(formatted)
            if len(message_history) > MAX_HISTORY:
                message_history.pop(0)

            broadcast(formatted, client_socket)

            if message_count % SUMMARY_INTERVAL == 0:
                for c in clients:
                    send_stats(c)

    except Exception as e:
        print(f"[ERROR] {address}: {e}")

    finally:
        print(f"[DISCONNECTED] {address[0]}:{address[1]}")
        client_moods.pop(client_socket, None)
        with clients_lock:
            if client_socket in clients:
                clients.remove(client_socket)
        client_socket.close()

# ---- Server loop ----
def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()

    print(f"[SERVER STARTED] Listening on port {PORT}")

    while True:
        client_socket, address = server_socket.accept()
        with clients_lock:
            clients.append(client_socket)

        threading.Thread(
            target=handle_client,
            args=(client_socket, address),
            daemon=True
        ).start()

if __name__ == "__main__":
    start_server()


