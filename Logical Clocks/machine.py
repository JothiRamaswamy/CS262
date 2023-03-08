from multiprocessing import Process

import sys

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

    # constructor that initializes an instance of Machine
    def __init__(self, name, port, log_directory="logs") -> None:
        # setting constants
        self.HEADER = 64 
        self.FORMAT = 'utf-8'

        # setting instance variables
        self.name = name # name of the machine instance
        self.clock_speed = random.randint(1, 6) # clock speed of the machine instance, randomly generated between 1 and 6

        self.message_queue = Queue() # creating a Queue instance to store messages received by the machine instance

        # creating directories to store logs and csv files
        os.makedirs(log_directory, exist_ok=True) # creating the top-level directory to store logs and csv files
        os.makedirs(f"{log_directory}/logs", exist_ok=True) # creating a subdirectory to store log files
        os.makedirs(f"{log_directory}/csvs", exist_ok=True) # creating a subdirectory to store csv files

        # creating csv log file to store machine instance data
        self.csv_log = f'{log_directory}/csvs/log_{self.name}_{self.clock_speed}.csv'
        with open(self.csv_log, 'w', newline='') as csvfile: # opening csv file
            writer = csv.writer(csvfile)
            writer.writerow(["timestamp", "logical_clock_time", "queue_length", "event_type"]) # writing headers to csv file

        # configuring logging information to be written to log file
        logging.basicConfig(filename=f'{log_directory}/logs/log_{name}.log', level=logging.INFO, filemode='w') # setting up logging configuration
        logging.info(f"Clock Speed: {self.clock_speed}") # writing clock speed information to log file

        # setting variables that represent the client and server connections
        self.first_other_client_name = (self.name + 1) % 3 # client connection variable that represents the first client connection
        self.second_other_client_name = (self.name - 1) % 3 # client connection variable that represents the second client connection

        self.logical_clock = LogicalClock() # initializing an instance of the LogicalClock class for the machine instance

        # setting up socket configuration for the machine instance's server
        self.SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # creating a socket object to communicate over the network
        self.SERVER_HOST_NAME = socket.gethostname() # getting the host name of the machine instance
        self.SERVER_HOST = socket.gethostbyname(self.SERVER_HOST_NAME) # getting the IP address of the machine instance
        self.PORT = port + name # port that the machine instance's server is listening to
        self.ADDR = (self.SERVER_HOST, self.PORT) # server address that the machine instance is listening to

        self.SERVER_LISTEN = True # boolean variable that is True if the machine instance's server is listening
        self.CLIENT_LISTEN = True # boolean variable that is True if the machine instance's client is listening

        self.cleanup_lock = threading.Lock() # creating a lock to ensure that cleanup tasks are performed correctly
        self.CLEANED_UP = False # boolean variable that is True if we have already closed existing sockets

        # Set up socket connection for the object's client
        self.CLIENT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.CLIENT_PORT = port + self.first_other_client_name
        self.CLIENT_ADDR = (self.SERVER_HOST, self.CLIENT_PORT)
        self.ACTIVE = True
        signal.signal(signal.SIGTERM, self.cleanup)  # Set up signal handler for cleanup

    def run(self, write_data=True):
        """
        Method to run the machine simulator and send/recieve messages while updating the logical clock.

        Args:
            write_data (bool): Flag to specify whether to log data in a log file and write to csv. Default is True.

        Returns:
            None
        """
        # Start the server thread
        server_thread = threading.Thread(target=self.start_server)
        server_thread.start()
        time.sleep(5)

        # Start the client thread
        client_thread = threading.Thread(target=self.start_client)
        client_thread.start()
        time.sleep(5)

        try:
            initial_time = time.time()
            # Run for 60 seconds
            while (time.time() - initial_time < 60):
                start_time = time.time()
                # If there are no messages in the queue, run a task chosen at random
                if self.message_queue.empty():
                    task = random.randint(1, 10)
                    self.run_tasks(task, self.CLIENT, self.CONN)
                # If there are messages in the queue, process them
                else:
                    self.pop_message()
                end_time = time.time()
                # Wait for the next clock tick before starting the next iteration
                time.sleep(max(1/self.clock_speed - (start_time - end_time), 0))
            print("DONE")
        # If the user interrupts the program, exit gracefully
        except KeyboardInterrupt:
            pass

    def run_tasks(self, task, client, conn, write_data=True):
        """
        Sends messages or logs internal events based on the value of `task`.

        Args:
            task (int): The task to be performed.
            client (socket.socket): The client socket object.
            conn (socket.socket): The server socket object.
            write_data (bool, optional): If True, log the message information in a log file and write to csv. Defaults to True.
        """
        if task <= 3:
            message = "[machine {}, task {}] the time is {}".format(
            self.name, task, self.logical_clock.get_time())
            # If task is 1, send the message to client
            if task == 1:
                self.CLIENT_LISTEN = False
                client.send(message.encode())
                self.CLIENT_LISTEN = True
            # If task is 2, send the message to server
            elif task == 2:
                self.SERVER_LISTEN = False
                conn.send(message.encode())
                self.SERVER_LISTEN = True
            # If task is 3, send the message to both client and server
            elif task == 3:
                client.send(message.encode())
                conn.send(message.encode())
            # Increment the logical clock time and get the global time, logical clock time, and queue length
            self.logical_clock.tick()
            global_time, logical_clock_time, queue_length = time.time(), self.logical_clock.get_time(), self.message_queue.qsize()
            # If specified, log the message information in a log file and write to csv
            if write_data:
                logging.info(f"Sent Message: System Time - {global_time}, Logical Clock Time - {logical_clock_time}, Queue Length - {queue_length}, Message - {message}")
                with open(self.csv_log, 'a', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow([global_time, logical_clock_time, queue_length, "Send"])
        # If task is greater than 3, this is an internal event
        else:
            self.logical_clock.tick()
            global_time, logical_clock_time, queue_length = time.time(), self.logical_clock.get_time(), self.message_queue.qsize()
            # If specified, log the message information in a log file and write to csv
            if write_data:
                logging.info(f"Internal Event: System Time - {global_time}, Logical Clock Time - {logical_clock_time}, Queue Length - {queue_length}")
                with open(self.csv_log, 'a', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow([global_time, logical_clock_time, queue_length, "Internal"])

    def pop_message(self, write_data=True):
        """
        Retrieve a message from the message queue, update the logical clock, and log the message data.

        Args:
        - write_data (Optional[bool]): A boolean indicating whether to write the message data to the log file. Default is `True`.

        Returns:
        - None.

        """
        message = self.message_queue.get() #get a message off the queue
        counterparty_clock = int(message.split()[-1]) # get the logical clock time of the sender machine
        self.logical_clock.update(counterparty_clock) #update the logial clock based on its rules

        # Log message data and write to csv if specified
        global_time, logical_clock_time, queue_length = time.time(), self.logical_clock.get_time(), self.message_queue.qsize()
        if write_data:
            logging.info(f"Received Message: System Time - {global_time}, Logical Clock Time - {logical_clock_time}, Queue Length - {queue_length}")
            with open(self.csv_log, 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([global_time, logical_clock_time, queue_length, "Received"])
        print(message)


    def cleanup(self, exitcode=None, exitstack=None):
        """
        Cleanup the machine by setting flags to indicate that the sockets should be closed, and closing the server and client sockets.

        Args:
        - exitcode (Optional[int]): The exit code to return when the program exits. Default is `None`.
        - exitstack (Optional): The exit stack to use for cleanup. Default is `None`.

        Returns:
        - None.
        """
        if not self.CLEANED_UP:
            print("Cleaning up...")
            self.CLEANED_UP = True
            # Set flags to indicate that the sockets should be closed
            self.SERVER_LISTEN = False
            self.CLIENT_LISTEN = False
            self.ACTIVE = False
            time.sleep(2)
            # Close the server and client sockets
            self.SERVER.close()
            self.CLIENT.close()


    def start_server(self):
        """
        Start the server by binding to the server address and listening for incoming connections. 
        Continuously listen for incoming data while the connection is active.

        Args:
        - None.

        Returns:
        - None.
        """
        # Bind to the server address and start listening
        self.SERVER.bind(self.ADDR)
        self.SERVER.listen()
        print("machine {} connected and listening to {}".format(self.name, self.ADDR))
        
        # Accept incoming connections
        self.CONN, addr = self.SERVER.accept()
        print(f"[NEW CONNECTION] {addr} connected.")
        
        # Continue listening for incoming data while the connection is active
        while(self.ACTIVE):
            if self.SERVER_LISTEN:
                try:
                    self.listen_through_socket(self.CONN) # listen for incoming messages
                except socket.timeout:
                    # Ignore timeouts and continue listening
                    pass
                except BlockingIOError:
                    # Ignore blocking I/O errors and continue listening
                    pass
                except (ConnectionResetError, ConnectionAbortedError):
                    # Connection was reset or aborted, break out of the loop
                    print("CONNECTION ABORTED")
                    break



    def start_client(self):
        """
        Start the client machine by connecting to the server and listening for incoming messages.

        Args:
        - None.

        Returns:
        - None.

        """
        client_connected = False # set a flag to track whether the client is connected to the server
        time.sleep(1) # wait for 1 second before attempting to connect to the server
        while(client_connected == False):
            try:
                self.CLIENT.connect(self.CLIENT_ADDR) # connect to the server using the client's socket object and the server address
                client_connected = True # set the flag to indicate that the client is now connected to the server
                print("machine {} connected to server {}".format(self.name, self.CLIENT_ADDR))
                break
            except Exception as e:
                print(e) # if there is an error connecting to the server, print the error message
                time.sleep(1) # wait for 1 second before trying to connect again
                client_connected = False # set the flag to indicate that the client is not yet connected to the server
        while(self.ACTIVE): # continue running the loop as long as the machine is active
            if self.CLIENT_LISTEN: # check if the client is set to listen for incoming messages
                try:
                    self.listen_through_socket(self.CLIENT) # listen for incoming messages
                except socket.timeout:
                    # Ignore timeouts and continue listening
                    pass
                except BlockingIOError:
                    # Ignore blocking I/O errors and continue listening
                    pass
                except (ConnectionResetError, ConnectionAbortedError):
                    # Connection was reset or aborted, break out of the loop
                    print("CONNECTION ABORTED")
                    break# if there is a blocking I/O error, ignore the exception and continue listening for messages


        # refactored out for testing purposes
    def listen_through_socket(self, listener: socket):
        """
        Listen for incoming messages through the provided socket.

        Args:
        - listener: A socket object that is used to listen for incoming messages.

        Returns:
        - The received message if one was received, or None if no message was received.

        Raises:
        - socket.timeout: If no message is received within the timeout period.
        """
        listener.settimeout(1) # set a timeout of 1 second to prevent blocking indefinitely
        message = listener.recv(self.HEADER, socket.MSG_DONTWAIT) # attempt to receive a message without blocking
        if message.decode(self.FORMAT):
            decoded_message = message.decode(self.FORMAT) # decode the message from bytes to string
            self.message_queue.put(decoded_message) # add the decoded message to the message queue for processing
            return message # return the received message



def start_machine(name, port, log_dir):
    """
    Start a machine with the given name, port number, and log directory.

    Args:
    - name: A string representing the name of the machine.
    - port: An integer representing the port number to use for the machine.
    - log_dir: A string representing the path to the directory where log files should be stored.

    Returns:
    - None.
    """
    client = Machine(name, port,log_dir) # create a new Machine object with the specified name, port, and log directory
    client.run() # start the machine by calling its `run()` method
    time.sleep(5) # wait for 5 seconds to give the machine time to start up
    client.cleanup() # clean up the machine by calling its `cleanup()` method, which closes open sockets and logs any remaining messages


if __name__ == '__main__':
    random.seed(262) # set the seed for the random number generator for reproducibility
    try:
        starting_port = int(sys.argv[1]) # get the starting port number from the command line arguments
    except:
        starting_port = 5000 # if no starting port is provided, use a default value of 5000
    # create three separate processes to run the start_machine function
    p = Process(target=start_machine, args=(0, starting_port,"experiment1",))
    p2 = Process(target=start_machine, args=(1, starting_port,"experiment1",))
    p3 = Process(target=start_machine, args=(2, starting_port,"experiment1",))
    try:
        # start the processes
        p.start()
        p2.start()
        p3.start()
        # wait for the processes to finish
        p.join()
        p2.join()
        p3.join()
    except KeyboardInterrupt:
        print("Keyboard interrupt detected. Exiting program...") # if a keyboard interrupt is detected, print a message and exit the program
    finally:
        # terminate the processes
        p.terminate()
        p2.terminate()
        p3.terminate()
