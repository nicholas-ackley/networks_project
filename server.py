"""Terminal Chat LAN Server with File Transfer"""

import socket
import threading

HOST = "0.0.0.0"  # Listen on LAN
PORT = 5000

clients = {}
clients_lock = threading.Lock()


def parse_command(message):
    message = message.strip()

    # Private messages
    if message.startswith('/pm '):
        parts = message[4:].split(' ', 1)
        if len(parts) == 2:
            target, msg = parts
            return 'pm', {'target': target, 'message': msg}
        return 'invalid', {'error': 'Usage: /pm <user> <message>'}

    # File transfer header
    if message.startswith("FILE_HEADER"):
        _, sender, target, filename, filesize = message.split(" ", 4)
        return 'file_header', {
            'sender': sender,
            'target': target,
            'filename': filename,
            'filesize': int(filesize)
        }

    if message.startswith('/quit'):
        return 'quit', {}

    if message.startswith('/list'):
        return 'list', {}

    return 'broadcast', {'message': message}


def send_private(sender, target, msg):
    with clients_lock:
        if target not in clients:
            clients[sender].sendall(f"[ERROR] User '{target}' not found.".encode())
            return
        clients[target].sendall(f"[PM from {sender}] {msg}".encode())
        clients[sender].sendall(f"[PM to {target}] {msg}".encode())


def broadcast(msg, sender=None):
    formatted = f"[{sender}] {msg}" if sender else msg
    dead = []

    with clients_lock:
        for user, conn in clients.items():
            if user != sender:
                try:
                    conn.sendall(formatted.encode())
                except:
                    dead.append(user)
        # Cleanup dropped clients
        for user in dead:
            clients[user].close()
            del clients[user]


def list_users(requester):
    with clients_lock:
        users = ", ".join(clients.keys())
        clients[requester].sendall(f"[USERS ONLINE] {users}".encode())


def forward_file(sender, target, header_data, conn, filesize):
    with clients_lock:
        if target not in clients:
            clients[sender].sendall(f"[ERROR] User '{target}' not found.".encode())
            return
        receiver = clients[target]

    # Forward header data
    receiver.sendall(header_data)

    remaining = filesize
    while remaining > 0:
        chunk = conn.recv(min(4096, remaining))
        if not chunk:
            break
        receiver.sendall(chunk)
        remaining -= len(chunk)

    clients[sender].sendall(f"[INFO] File sent to {target}".encode())


def route_message(username, raw_msg, conn):
    cmd, data = parse_command(raw_msg)

    if cmd == 'pm':
        send_private(username, data['target'], data['message'])

    elif cmd == 'broadcast':
        broadcast(data['message'], username)

    elif cmd == 'list':
        list_users(username)

    elif cmd == 'quit':
        return 'quit'

    elif cmd == 'invalid':
        clients[username].sendall(f"[ERROR] {data['error']}".encode())

    elif cmd == 'file_header':
        header = raw_msg.encode()
        forward_file(
            username,
            data['target'],
            header,
            conn,
            data['filesize']
        )

    return cmd

# Main server code
def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    conn.sendall("Enter your username: ".encode())

    try:
        username = conn.recv(1024).decode().strip()

        with clients_lock:
            if username in clients:
                conn.sendall("Username already taken. Disconnecting.\n".encode())
                conn.close()
                return
            clients[username] = conn

        broadcast(f"{username} has joined the chat.")

        conn.sendall("Welcome! Commands: /pm, /list, /quit, /sendfile.\n".encode())

        while True:
            msg = conn.recv(1024).decode()
            if not msg:
                break

            if route_message(username, msg, conn) == "quit":
                conn.sendall("[SERVER] Goodbye!\n".encode())
                break

    except:
        pass

    print(f"[DISCONNECT] {username}")

    with clients_lock:
        if username in clients:
            del clients[username]

    broadcast(f"{username} has left the chat.")
    conn.close()


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()

    print(f"[STARTED] Chat server running on {HOST}:{PORT}")

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()


if __name__ == "__main__":
    start_server()
