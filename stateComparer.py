from stateSaver import StateSaver
from cv2 import imwrite, TM_SQDIFF, matchTemplate, minMaxLoc, TM_SQDIFF_NORMED, rectangle, cv2

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

        if np.allclose(stateSaver.lastState, stateSaver.currentState, 0, 100, equal_nan=True):
            return False

        last = stateSaver.lastState
        w, h = last.shape[::-1]
        last = stateSaver.lastState[int(h/2):h-1, 1:int(w/2)]
        current = stateSaver.currentState
        # print(last, current, w, h)

        imwrite('tmp_1.jpg', last)
        imwrite('tmp_2.jpg', current)

        img = current.copy()
        method = TM_SQDIFF
        methods = ['cv2.TM_CCOEFF']
        #'cv2.TM_CCOEFF_NORMED', 'cv2.TM_CCORR_NORMED', 'cv2.TM_SQDIFF', 'cv2.TM_SQDIFF_NORMED', 'cv2.TM_CCORR'

        for _method in methods:
            # Apply template Matching
            method = eval(_method)
            res = matchTemplate(img,last,method)
            min_val, max_val, min_loc, max_loc = minMaxLoc(res)

            # If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
            if method in [TM_SQDIFF, TM_SQDIFF_NORMED]:
                top_left = min_loc
            else:
                top_left = max_loc
            bottom_right = (top_left[0] + w, top_left[1] + h)

            rectangle(img,top_left, bottom_right, 255, 2)
            same = top_left[1] == int(h/2)
            print(_method, same, top_left, int(h/2))
            if not same:
                break
        
        return not same
