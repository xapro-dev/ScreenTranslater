from stateSaver import StateSaver
import numpy as np

class StateComparer:
    def stateChanged(self, stateSaver: StateSaver):
        if stateSaver.lastState is None:
            return True
        
        # _, lastBW = cv2.threshold(stateSaver.lastState,120,255,cv2.THRESH_BINARY)
        # _, curBW = cv2.threshold(stateSaver.currentState,120,255,cv2.THRESH_BINARY)
        # print(lastBW.size, curBW.size)
        if np.size(stateSaver.lastState) != np.size(stateSaver.currentState):
            return True

        same = np.allclose(stateSaver.lastState, stateSaver.currentState, 0, 180, equal_nan=True)
        return not same
