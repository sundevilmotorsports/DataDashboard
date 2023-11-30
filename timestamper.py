import time


class TimeStamper:
    def __init__(self, init_time=0, max_time=1200, slider=None):
        # Initialize the TimeStamper with an initial timestamp of 630.
        self.time_stamp = init_time
        self.max_time = max_time
        # Create a list to store callback functions that observe changes to the timestamp.
        self._observers = []
        self.slider = slider

    def set_init_time(self, init):
        self.time_stamp = init

    def self_max_time(self, max_time):
        self.max_time = max_time

    def time_generator(self):
        while self.time_stamp < int(self.max_time):
            self.time_stamp += 1
            if self.time_stamp > self.max_time:
                self.time_stamp = 0
                yield self.time_stamp
                break
            if self.slider is not None:
                self.slider.setValue(self.time_stamp / (self.max_time / 100))
            yield self.time_stamp
