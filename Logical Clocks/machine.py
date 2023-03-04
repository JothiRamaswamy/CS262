from multiprocessing import Process
import os
import random
import socket
import threading
import time

class Machine:

    def __init__(self, name, port) -> None:
        self.HEADER = 64
        self.FORMAT = 'utf-8'

        self.name = name
        self.clock_speed = random.randint(1,6)
        self.log = []

        self.first_other_client_name = (self.name + 1) % 3 #our client connects to their server
        self.second_other_client_name = (self.name - 1) % 3 #their client connects to our server

        self.SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create socket
        self.SERVER_HOST_NAME = socket.gethostname() # gets name representing computer on the network
        self.SERVER_HOST = socket.gethostbyname(self.SERVER_HOST_NAME) # gets host IPv4 address
        self.PORT = port # port to connect to the server with
        self.ADDR = (self.SERVER_HOST, self.PORT) # address that the server is listening into

        self.SERVER_LISTEN = True
        self.CLIENT_LISTEN = True

        self.CLIENT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.CLIENT_PORT = 5050 + self.first_other_client_name
        self.CLIENT_ADDR = (self.SERVER_HOST, self.CLIENT_PORT)
        


    def run(self):
        server_thread = threading.Thread(target=self.start_server)
        client_thread = threading.Thread(target=self.start_client)
        server_thread.start()
        client_thread.start()
        time.sleep(1)
        for i in range(20):
            start_time = time.time()
            task = random.randint(1,10)
            if task <= 3:
                message = "[{}, task {}] the time is {}".format(self.name, task, i)
                if task != 2:
                    print(task)
                    self.CLIENT_LISTEN = False
                    self.CLIENT.send(message.encode())
                    self.CLIENT_LISTEN = True
                if task != 1:
                    print(task)
                    self.SERVER_LISTEN = False
                    self.CONN.send(message.encode())
                    self.SERVER_LISTEN = True

            end_time = time.time()
            time.sleep(max(1/self.clock_speed - (start_time - end_time), 0))
        print("DONE")


    def start_server(self):
        self.SERVER.bind(self.ADDR)
        self.SERVER.listen()
        print("machine {} connected and listening to {}".format(self.name, self.ADDR))
        self.CONN, addr = self.SERVER.accept()
        print(f"[NEW CONNECTION] {addr} connected.")
        
        connected = True
        while(connected):
            if self.SERVER_LISTEN:
                try:
                    message = self.CONN.recv(self.HEADER, socket.MSG_DONTWAIT)
                    if message.decode(self.FORMAT):
                        decoded_message = message.decode(self.FORMAT)
                        print(decoded_message)
                except BlockingIOError:
                    pass


    def start_client(self):
        client_connected = False
        time.sleep(1)
        while(client_connected == False):
            try:
                self.CLIENT.connect(self.CLIENT_ADDR)
                client_connected = True
                print("machine {} connected to server {}".format(self.name, self.CLIENT_ADDR))
                break
            except Exception as e:
                print(e)
                time.sleep(1)
                client_connected = False
        while(True):
            if self.CLIENT_LISTEN:
                try:
                    message = self.CLIENT.recv(self.HEADER, socket.MSG_DONTWAIT)
                    if message.decode(self.FORMAT):
                        decoded_message = message.decode(self.FORMAT)
                        print(decoded_message)
                except BlockingIOError:
                    pass


    def export_log():
        pass

def start_machine(name, port):
    client = Machine(name, port)
    client.run()

if __name__ == '__main__':
    p = Process(target=start_machine, args=(0, 5050,))
    p2 = Process(target=start_machine, args=(1, 5051,))
    p3 = Process(target=start_machine, args=(2, 5052,))
    try:
        p.start()
        p2.start()
        p3.start()
        p.join()
        p2.join()
        p3.join()
    except KeyboardInterrupt:
        pass