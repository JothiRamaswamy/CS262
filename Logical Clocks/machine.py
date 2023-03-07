from multiprocessing import Process
from logical_clock import LogicalClock
from queue import Queue
import logging
import random
import socket
import signal
import threading
import time
import csv
import os


class Machine:

    def __init__(self, name, port, log_directory="logs") -> None:
        self.HEADER = 64
        self.FORMAT = 'utf-8'

        self.name = name
        self.clock_speed = random.randint(1,6)

        self.message_queue = Queue()

        os.makedirs(log_directory, exist_ok=True)
        os.makedirs(f"{log_directory}/logs", exist_ok=True)
        os.makedirs(f"{log_directory}/csvs", exist_ok=True)

        self.csv_log = f'{log_directory}/csvs/log_{self.name}_{self.clock_speed}.csv'
        with open(self.csv_log, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["timestamp", "logical_clock_time", "queue_length", "event_type"])
        logging.basicConfig(filename=f'{log_directory}/logs/log_{name}.log', level=logging.INFO, filemode='w')
        logging.info(f"Clock Speed: {self.clock_speed}")

        self.first_other_client_name = (self.name + 1) % 3 #our client connects to their server
        self.second_other_client_name = (self.name - 1) % 3 #their client connects to our server

        self.logical_clock = LogicalClock()

        self.SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create socket
        self.SERVER_HOST_NAME = socket.gethostname() # gets name representing computer on the network
        self.SERVER_HOST = socket.gethostbyname(self.SERVER_HOST_NAME) # gets host IPv4 address
        self.PORT = port + name # port to connect to the server with
        self.ADDR = (self.SERVER_HOST, self.PORT) # address that the server is listening into

        self.SERVER_LISTEN = True
        self.CLIENT_LISTEN = True

        self.cleanup_lock = threading.Lock()
        self.CLEANED_UP = False

        self.CLIENT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.CLIENT_PORT = port + self.first_other_client_name
        self.CLIENT_ADDR = (self.SERVER_HOST, self.CLIENT_PORT)

        self.ACTIVE = True
        signal.signal(signal.SIGTERM, self.cleanup)

        


    def run(self):
        server_thread = threading.Thread(target=self.start_server)
        server_thread.start()
        time.sleep(5)

        client_thread = threading.Thread(target=self.start_client)
        client_thread.start()
        time.sleep(5)

        try:
            curr_time = time.time()
            while(time.time() - curr_time < 60):
                start_time = time.time()
                if self.message_queue.empty():
                    task = random.randint(1,10)
                    if task <= 3:
                        message = "[machine {}, task {}] the time is {}".format(self.name, task, self.logical_clock.get_time())
                        if task == 1:
                            self.CLIENT_LISTEN = False
                            self.CLIENT.send(message.encode())
                            self.CLIENT_LISTEN = True
                        elif task == 2:
                            self.SERVER_LISTEN = False
                            self.CONN.send(message.encode())
                            self.SERVER_LISTEN = True
                        elif task == 3:
                            self.CLIENT.send(message.encode())
                            self.CONN.send(message.encode())
                        self.logical_clock.tick()
                        global_time, logical_clock_time, queue_length = time.time(), self.logical_clock.get_time(), self.message_queue.qsize()
                        logging.info(f"Sent Message: System Time - {global_time}, Logical Clock Time - {logical_clock_time}, Queue Length - {queue_length}, Message - {message}")
                        with open(self.csv_log, 'a', newline='') as csvfile:
                            writer = csv.writer(csvfile)
                            writer.writerow([global_time, logical_clock_time, queue_length, "Send"])
                    else:
                        self.logical_clock.tick()
                        global_time, logical_clock_time, queue_length = time.time(), self.logical_clock.get_time(), self.message_queue.qsize()
                        logging.info(f"Internal Event: System Time - {global_time}, Logical Clock Time - {logical_clock_time}, Queue Length - {queue_length}")
                        with open(self.csv_log, 'a', newline='') as csvfile:
                            writer = csv.writer(csvfile)
                            writer.writerow([global_time, logical_clock_time, queue_length, "Internal"])                    
                else:
                    message = self.message_queue.get()
                    counterparty_clock = int(message.split()[-1])
                    self.logical_clock.update(counterparty_clock)

                    global_time, logical_clock_time, queue_length = time.time(), self.logical_clock.get_time(), self.message_queue.qsize()
                    logging.info(f"Received Message: System Time - {global_time}, Logical Clock Time - {logical_clock_time}, Queue Length - {queue_length}")
                    with open(self.csv_log, 'a', newline='') as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerow([global_time, logical_clock_time, queue_length, "Received"]) 
                    print(message)
                end_time = time.time()
                time.sleep(max(1/self.clock_speed - (start_time - end_time), 0))
            print("DONE")
        except KeyboardInterrupt:
            pass

    def cleanup(self, exitcode=None, exitstack=None):
        if not self.CLEANED_UP:
            print("Cleaning up...")
            self.CLEANED_UP = True
            # close the sockets
            self.SERVER_LISTEN = False
            self.CLIENT_LISTEN = False
            self.ACTIVE = False
            time.sleep(2)
            self.SERVER.close()
            self.CLIENT.close()


    def start_server(self):
        self.SERVER.bind(self.ADDR)
        self.SERVER.listen()
        print("machine {} connected and listening to {}".format(self.name, self.ADDR))
        self.CONN, addr = self.SERVER.accept()
        print(f"[NEW CONNECTION] {addr} connected.")
        
        while(self.ACTIVE):
            if self.SERVER_LISTEN:
                try:
                    self.CONN.settimeout(1)
                    message = self.CONN.recv(self.HEADER)
                    if message.decode(self.FORMAT):
                        decoded_message = message.decode(self.FORMAT)
                        self.message_queue.put(decoded_message)
                except socket.timeout:
                    pass
                except BlockingIOError:
                    pass
                except (ConnectionResetError, ConnectionAbortedError):
                    print("CONNECTION ABORTED")
                    break


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
        while(self.ACTIVE):
            if self.CLIENT_LISTEN:
                try:
                    self.CLIENT.settimeout(1) # set a timeout of 1 second
                    message = self.CLIENT.recv(self.HEADER, socket.MSG_DONTWAIT)
                    if message.decode(self.FORMAT):
                        decoded_message = message.decode(self.FORMAT)
                        self.message_queue.put(decoded_message)
                except socket.timeout:
                    pass
                except BlockingIOError:
                    pass
                except ConnectionResetError:
                    print("CONNECTION ABORTED")
                    break



def start_machine(name, port, log_dir):
    client = Machine(name, port,log_dir)
    client.run()
    time.sleep(5)
    client.cleanup()

if __name__ == '__main__':
    random.seed(262)
    starting_port = 3000
    p = Process(target=start_machine, args=(0, starting_port,"experiment1",))
    p2 = Process(target=start_machine, args=(1, starting_port,"experiment1",))
    p3 = Process(target=start_machine, args=(2, starting_port,"experiment1",))
    try:
        p.start()
        p2.start()
        p3.start()
        p.join()
        p2.join()
        p3.join()
    except KeyboardInterrupt:
        print("Keyboard interrupt detected. Exiting program...")
    finally:
        p.terminate()
        p2.terminate()
        p3.terminate()