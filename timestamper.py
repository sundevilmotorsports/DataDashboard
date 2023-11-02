import time


class TimeStamper:
    def __init__(self):
        self.time_stamp = 630
        self._observers = []

    @property
    def timestamp(self):
        return self.time_stamp

    @timestamp.setter
    def timestamp(self, value):
        self.time_stamp = value
        for callback in self._observers:
            callback(timestamp=self.time_stamp)
            print("announcing change")

    def bind_to(self, callback):
        print("bound")
        self._observers.append(callback)
