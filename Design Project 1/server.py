from copyreg import pickle
import socket
import threading

from psutil import users

from classes import user
from operations import Operations

HEADER = 64
PORT = 5050
SERVER = "10.250.35.25"
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
USERS = {}

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

def handle_client(conn, addr):
    print("[NEW CONNECTION] {} connected.".format(addr))

    connected = True
    while connected:
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)
            if msg == DISCONNECT_MESSAGE:
                connected = False

            print("[{}], {}".format(addr, msg))

    conn.close()


def start():
    server.listen(PORT)
    print("[LISTENING] Server is listening on {}".format(SERVER))
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print("[ACTIVE CONNECTIONS] {}".format(threading.activeCount() - 1))
def encode(message, operation):
    pass

def decode(message):
    pass

def login(username):
    if username in USERS:
        return {"status": Operations.SUCCESS}
    return {"status": Operations.ACCOUNT_DOES_NOT_EXIST}

def create_account(username):
    if username in USERS:
        return {"status": Operations.ACCOUNT_ALREADY_EXISTS}
    new_user = user(username)
    USERS[username] = new_user
    return {"status": Operations.SUCCESS}

def delete_account(username):
    if username in USERS:
        USERS.pop(username)
        return {"status": Operations.SUCCESS}
    return {"status": Operations.ACCOUNT_DOES_NOT_EXIST}

def list_accounts():
    user_list = pickle.dumps(list(USERS.keys()))
    return {"status": Operations.LIST_OF_ACCOUNTS, "info": user_list}

def send_message(msg, sender, receiver):
    if receiver in USERS and sender in USERS:
        USERS[receiver].undelivered_messages.append(msg)
        return {"status": Operations.SUCCESS}
    return {"status": Operations.ACCOUNT_DOES_NOT_EXIST}

def view_msgs(username):
    if username in USERS:
        messages = pickle.dumps(USERS[username].undelivered_messages)
        USERS[username].undelivered_messages.clear()
        return {"status": Operations.LIST_OF_MESSAGES, "info": messages}
    return {"status": Operations.ACCOUNT_DOES_NOT_EXIST}



print("[STARTING] server is starting...")
start()

