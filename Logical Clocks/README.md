## Prerequisites
This code requires Python 3.x to run. Additionally, the `multiprocessing`, `queue`, `logging`, `random`, `socket`, `signal`, `threading`, `time`, and `csv` libraries must be installed.

## Description of the Code

This code is a Python program that simulates a distributed system with 3 machines using logical clocks for message ordering. The machines communicate with each other via sockets, sending messages and internal events. The program logs events and messages to a CSV file and a log file.

Each machine is represented by an instance of the Machine class. The Machine class has methods to start a server thread and a client thread, and a run method that runs for a fixed duration of 60 seconds, during which the machine sends messages to other machines or generates internal events. The machine's clock speed is randomly generated between 1 and 6, and the logical clock is used to assign a unique timestamp to each event or message.

The run_tasks method generates a random task (1-10) and sends a message to another machine or generates an internal event, updating the logical clock accordingly. The pop_message method extracts messages from the queue and updates the logical clock. The cleanup method is used to clean up resources when the program is terminated by a KeyboardInterrupt.

## Running the code
Clone this current repository and open a terminal or command prompt and navigate to the directory containing the code file.
Run the command `python machine.py <PORT>` to execute the program.
Note that the PORT variable controls the ports that we connect sockets to (connect to PORT, PORT + 1, PORT + 2). This value is optional though. If `PORT` is not specified, it automatically defaults to `3000`.

## Output
The program logs output to a file located in the logs directory. Each instance of the program running on a machine generates a separate log file with a name formatted as `log_<machine_name>.log`.

Additionally, the program generates a CSV file containing a log of all events in the program. The CSV files are located in the csvs directory and are named `log_<machine_name>_<clock_speed>.csv`. The clock_speed value is randomly generated and determines how often the machine generates messages or performs internal events.

## Stopping the program
The program will exit on its own. To stop the program in the middle, press Ctrl-C in the terminal or command prompt where the program is running. The program will catch the `KeyboardInterrupt` exception and terminate gracefully.