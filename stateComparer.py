from stateSaver import StateSaver
import cv2
import numpy as np

class StateComparer:
    def stateChanged(self, stateSaver: StateSaver):
        if stateSaver.lastState is None:
            return True
        
        # _, lastBW = cv2.threshold(stateSaver.lastState,120,255,cv2.THRESH_BINARY)
        # _, curBW = cv2.threshold(stateSaver.currentState,120,255,cv2.THRESH_BINARY)
        # print(lastBW.size, curBW.size)
        same = np.allclose(stateSaver.lastState, stateSaver.currentState, 0, 80, equal_nan=True)
        print(same)
        return not same
