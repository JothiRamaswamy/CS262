import socket

from operations import Operations

HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = "10.250.35.25"
ADDR = (SERVER, PORT)
VERSION = 1

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

def send(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)
    return client.recv(1024).decode(FORMAT)

def serialize(data):
    return data

def unserialize(data):
    return data

def login(username):
    data = {"operation": Operations.LOGIN, "info": username}
    new_data = serialize(data)
    received_info = send(new_data)
    status = unserialize(received_info)["operation"]
    if status == "0":
        return 0
    print("Account information does not exist")
    return 1



def create_account(username):
    data = {"operation": Operations.CREATE_ACCOUNT, "info": username}
    new_data = serialize(data)
    received_info = send(new_data)
    status = unserialize(received_info)["operation"]
    if status == "0":
        return 0
    print("Account information already exists")
    return 1

def delete_account(username):
    data = {"operation": Operations.DELETE_ACCOUNT, "info": username}
    new_data = serialize(data)
    received_info = send(new_data)
    status = unserialize(received_info)["operation"]
    if status == "0":
        return 0
    print("Deletion Unsuccessful")
    return 1

def list_accounts():
    data = {"operation": Operations.LIST_ACCOUNT, "info": ""}
    new_data = serialize(data)
    received_info = send(new_data)
    status = unserialize(received_info)["operation"]
    if status == "3":
        return unserialize(received_info)["info"]
    print("Account information does not exist")
    return 1

def send_message(msg, sender, receiver):
    total_info = sender + "\n" + receiver + "\n" + msg
    data = {"operation": Operations.SEND_MESSAGE, "info": total_info}
    new_data = serialize(data)
    received_info = send(new_data)
    status = unserialize(received_info)["operation"]
    if status == "0":
        return 0
    print("Message send failure")
    return 1

def view_msgs(username):
    data = {"operation": Operations.VIEW_UNDELIVERED_MESSAGES, "info": username}
    new_data = serialize(data)
    received_info = send(new_data)
    status = unserialize(received_info)["operation"]
    if status == "4":
        return unserialize(received_info)["info"]
    print("Cannot retrieve messages")
    return 1

send("Hello World!")
