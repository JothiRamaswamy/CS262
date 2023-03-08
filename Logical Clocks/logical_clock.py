import threading

class LogicalClock:
    def __init__(self, initial_time=0):
        """
        A class to represent a logical clock.

        Args:
            initial_time (int): The initial value of the logical clock. Defaults to 0.
        """
        self.time = initial_time
        self.lock = threading.Lock()
        
    def tick(self):
        """
        Increments the logical clock by 1.
        """
        with self.lock:
            self.time += 1
        
    def update(self, other):
        """
        Updates the logical clock based on the value of another logical clock.

        Args:
            other (int): The value of the other logical clock.
        """
        with self.lock:
            self.time = max(self.time, other) + 1
        
    def get_time(self):
        """
        Returns the current value of the logical clock.

        Returns:
            int: The current value of the logical clock.
        """
        with self.lock:
            return self.time

