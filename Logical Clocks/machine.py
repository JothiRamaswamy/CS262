from multiprocessing import Process
import os
import random
import socket
import threading
import time

class Machine:

    def __init__(self, name, port) -> None:
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

        self.CLIENT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.CLIENT_PORT = 5050 + self.first_other_client_name
        self.CLIENT_ADDR = (self.SERVER_HOST, self.CLIENT_PORT)
        


    def run(self):
        server_thread = threading.Thread(target=self.start_server)
        client_thread = threading.Thread(target=self.start_client)
        server_thread.start()
        client_thread.start()
        # for i in range(10):
        #     start_time = time.time()
        #     print("hi", self.name)
        #     end_time = time.time()
        #     time.sleep(1/self.clock_speed - (start_time - end_time))


    def start_client(self):
        self.SERVER.bind(self.ADDR)
        self.SERVER.listen()
        print("machine {} connected and listening to {}".format(self.name, self.ADDR))

    def start_server(self):
        client_connected = False
        time.sleep(1)
        while(client_connected == False):
            try:
                self.CLIENT.connect(self.CLIENT_ADDR)
                client_connected = True
                print("machine {} connected to server {}".format(self.name, self.CLIENT_ADDR))
                break
            except Exception as e:
                client_connected = False

    def export_log():
        pass

def start_machine(name, port):
    client = Machine(name, port)
    client.run()

if __name__ == '__main__':
    p = Process(target=start_machine, args=(0, 5050,))
    p2 = Process(target=start_machine, args=(1, 5051,))
    p3 = Process(target=start_machine, args=(2, 5052,))
    p.start()
    p2.start()
    p3.start()
    p.join()
    p2.join()
    p3.join()