from PIL import ImageGrab
import numpy as np
import cv2
import time as t

class ChatReceiver:
    
    coords = (20,777,550,1028)

    def getChat(self):
        frame = ImageGrab.grab(self.coords)
        frameGray = cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2GRAY)
        chat = frameGray
        # _, chat = cv2.threshold(frameGray,120,255,cv2.THRESH_BINARY)
        # chat = cv2.adaptiveThreshold(frameGray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
        # _, chat = cv2.threshold(frameGray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        return chat

    def convertToBytes(self, img):
        return cv2.imencode('.jpg', img)[1].tostring()

if __name__ == "__main__":
    t.sleep(3)
    chat = ChatReceiver().getChat()
    cv2.imwrite('tmp.jpg', chat)