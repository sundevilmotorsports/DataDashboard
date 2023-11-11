import time


class TimeStamper:
    def __init__(self, init_time=0, max_time=1200):
        # Initialize the TimeStamper with an initial timestamp of 630.
        self.time_stamp = init_time
        self.max_time = max_time
        # Create a list to store callback functions that observe changes to the timestamp.
        self._observers = []

    def set_init_time(self, init):
        self.time_stamp = init

    def self_max_time(self, max_time):
        self.max_time = max_time

    def time_generator(self):
        for i in range(int(self.time_stamp), int(self.max_time)):
            yield i
