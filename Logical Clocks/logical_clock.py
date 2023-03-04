import threading

class LogicalClock:
    def __init__(self, initial_time=0):
        self.time = initial_time
        self.lock = threading.Lock()
        
    def tick(self):
        with self.lock:
            self.time += 1
        
    def update(self, other):
        with self.lock:
            self.time = max(self.time, other.time) + 1
        
    def get_time(self):
        with self.lock:
            return self.time
