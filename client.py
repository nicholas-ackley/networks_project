""" Termninal Chat LAN Client with File Transfer """

import socket
import threading
import sys
import os
from datetime import datetime
from colorama import Fore, Style, init

init(autoreset=True)

HOST = "10.169.160.142"   # Change server’s LAN IP
PORT = 5000

LOG_FILE = 'chat_history.txt'
SHOW_TIMESTAMPS = True
USERNAME = ""
RECEIVED_DIR = "received_files"
os.makedirs(RECEIVED_DIR, exist_ok=True)

# Returns in the format HH:MM:SS
def timestamp():
    return datetime.now().strftime('%H:%M:%S')

# Appends each message to add to the history
def log_message(msg):
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(msg + "\n")

# If timestamps are on, add to the timestamp prefix, if OFF return the msg unchanged
def format_message(msg):
    if SHOW_TIMESTAMPS:
        return f"[{timestamp()}] {msg}"
    return msg


def print_prompt():
    print(Fore.CYAN + f"{USERNAME}> ", end="", flush=True)

# Sends a file to the server for forwarding
def send_file(sock, sender, target, filepath):
    if not os.path.isfile(filepath):
        print(Fore.RED + f"[ERROR] File not found: {filepath}")
        return

    filename = os.path.basename(filepath)
    filesize = os.path.getsize(filepath)

    header = f"FILE_HEADER {sender} {target} {filename} {filesize} "
    sock.sendall(header.encode())

    print(Fore.YELLOW + f"[SENDING FILE] {filename} → {target} ({filesize} bytes)")

    with open(filepath, "rb") as f:
        while True:
            chunk = f.read(4096)
            if not chunk:
                break
            sock.sendall(chunk)

    print(Fore.GREEN + f"[FILE SENT] {filename} sent to {target}")

# Constantly listens for messages from the server and runs in its own seperate thread.
def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')

            # Disconnected
            if not message:
                print(Fore.RED + "\n[DISCONNECTED] Connection lost.")
                break

            # FILE HEADER
            if message.startswith("FILE_HEADER"):
                _, sender, target, filename, filesize = message.split(" ", 4)
                filesize = int(filesize)

                save_path = os.path.join(RECEIVED_DIR, filename)
                print(f"\n[FILE RECEIVING] {filename} from {sender}")

                remaining = filesize
                with open(save_path, "wb") as f:
                    while remaining > 0:
                        chunk = client_socket.recv(min(4096, remaining))
                        if not chunk:
                            break
                        f.write(chunk)
                        remaining -= len(chunk)

                print(Fore.GREEN + f"[FILE RECEIVED] Saved → {save_path}")
                print_prompt()
                continue

            #If message arrives, then it while format with the timestamp, print in white, save to the chat log, and display the prompt
            formatted = format_message(message)
            print("\n" + Fore.WHITE + formatted)
            log_message(formatted)
            print_prompt()
        # Error 10038 means the socket closed prematurely on Windows
        except OSError as e:
            if getattr(e, "winerror", None) == 10038:
                break
            break
        except:
            break

#For interpreting any messages that start with the '/' character
def handle_command(cmd, client_socket):
    global SHOW_TIMESTAMPS, USERNAME

    if cmd == "/help":
        print(Fore.YELLOW + """
Commands:
/help       Shows help
/clear      Clears history
/time       Timestamps
/nick NAME  change name
/sendfile <user> <path>
/pm <user> <message>
/quit       Quit
""")

    elif cmd == "/clear":
        os.system("cls" if os.name == "nt" else "clear")

    elif cmd == "/time":
        SHOW_TIMESTAMPS = not SHOW_TIMESTAMPS
        print(f"Timestamps {'ON' if SHOW_TIMESTAMPS else 'OFF'}")

    elif cmd.startswith("/nick "):
        new = cmd.split(" ", 1)[1]
        USERNAME = new
        client_socket.sendall(cmd.encode())

    elif cmd.startswith("/sendfile "):
        try:
            _, target, path = cmd.split(" ", 2)
            send_file(client_socket, USERNAME, target, path)
        except:
            print(Fore.RED + "Usage: /sendfile <user> <filepath>")

    elif cmd == "/list":
        client_socket.sendall(cmd.encode())

    elif cmd.startswith("/pm "):
        client_socket.sendall(cmd.encode())

    elif cmd == "/quit":
        client_socket.sendall(cmd.encode())
        print(Fore.RED + "[INFO] Disconnecting...")

        try:
            client_socket.shutdown(socket.SHUT_RDWR)
        except:
            pass
        client_socket.close()
        sys.exit(0)

    else:
        print(Fore.RED + "Unknown command. Try /help")


def send_messages(client_socket):
    try:
        while True:
            print_prompt()
            msg = input()

            if not msg:
                continue

            if msg.startswith("/"):
                handle_command(msg, client_socket)
            else:
                client_socket.sendall(msg.encode())

    except KeyboardInterrupt:
        print(Fore.RED + "\n[INFO] Disconnecting...")
        try:
            client_socket.sendall("/quit".encode())
        except:
            pass

    finally:
        try:
            client_socket.shutdown(socket.SHUT_RDWR)
        except:
            pass
        client_socket.close()


def start_client():
    global USERNAME

    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST, PORT))

        print(Fore.GREEN + f"[CONNECTED] Connected to {HOST}:{PORT}\n")

        prompt = client.recv(1024).decode()
        print(prompt, end="")
        USERNAME = input()
        client.sendall(USERNAME.encode())

        response = client.recv(1024).decode()
        print(response)

        if "Disconnecting" in response:
            client.close()
            return

        recv_thread = threading.Thread(target=receive_messages, args=(client,))
        recv_thread.start()

        send_messages(client)

        recv_thread.join()

    except Exception as e:
        print(Fore.RED + f"[ERROR] {e}")


if __name__ == "__main__":
    print(Fore.MAGENTA + "=" * 55)
    print(Fore.MAGENTA + "      TERMINAL CHAT CLIENT")
    print(Fore.MAGENTA + "=" * 55)
    start_client()
    print("[GOODBYE]")