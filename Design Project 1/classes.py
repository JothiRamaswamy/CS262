import hashlib

from dataclasses import dataclass

class user:
    def __init__(self, username, pwd):
        self.username = username
        self.undelivered_msgs = []

class message:
    version: int
    size: int
    text: str
    sender_addr: str
    receiver_addr: str
    def __init__(self, text):
        self.version = None
        self.size = None
        self.text = text
        self.sender_addr = None
        self.receiver_addr = None
    def serialize(self):
        return str(self.version) + str(self.size) + self.sender_addr + self.receiver_addr + self.text