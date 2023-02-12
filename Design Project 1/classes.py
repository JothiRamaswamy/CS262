import hashlib

from dataclasses import dataclass

class user:
    def __init__(self, username):
        self.username = username
        self.undelivered_msgs = []