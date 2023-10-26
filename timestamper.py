class TimeStamper:
    def __init__(self):
        self.time_stamp = 0
        self._observers = []

    @property
    def timestamp(self):
        return self.time_stamp

    @timestamp.setter
    def timestamp(self, value):
        self.timestamp = value
        for callback in self._observers:
            print("announcing change")
            callback(self._global_wealth)

    def bind_to(self, callback):
        print("bound")
        self._observers.append(callback)
