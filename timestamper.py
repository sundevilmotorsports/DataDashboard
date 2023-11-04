import time

class TimeStamper:
    def __init__(self):
        # Initialize the TimeStamper with an initial timestamp of 630.
        self.time_stamp = 630
        # Create a list to store callback functions that observe changes to the timestamp.
        self._observers = []

    @property
    def timestamp(self):
        """Getter for the timestamp property. Returns the current timestamp value"""
        return self.time_stamp

    @timestamp.setter
    def timestamp(self, value):
        """Setter for the timestamp property. Updates the timestamp value and notifies observers"""
        self.time_stamp = value
        # Notify all registered observers with the updated timestamp value.
        for callback in self._observers:
            callback(timestamp=self.time_stamp)
        # Print a message to indicate that a change has been announced.

    def bind_to(self, callback):
        """Register a callback function to observe changes in the timestamp"""
        print("Bound observer to TimeStamper.")
        self._observers.append(callback)

