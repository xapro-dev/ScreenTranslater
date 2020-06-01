import numpy as np

class StateSaver:

    lastState: np.array = None
    currentState: np.array = None
    
    def save(self, data):
        self.lastState = self.currentState
        self.currentState = data
