from PIL import ImageGrab
from numpy import array as npArray
import cv2
import time as t
from container import Config

class ChatReceiver:

    def getChat(self):
        frame = ImageGrab.grab(self.coords)
        frameGray = cv2.cvtColor(npArray(frame), cv2.COLOR_RGB2GRAY)
        chat = frameGray
        # _, chat = cv2.threshold(frameGray,i*10,255,cv2.THRESH_BINARY)
        # for i in range(25):
        #     _, chat = cv2.threshold(frameGray,i*10,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        #     cv2.imwrite(f'img{i}.jpg', chat)
        # chat = cv2.adaptiveThreshold(frameGray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
        # _, chat = cv2.threshold(frameGray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        return chat

    def init(self, config: Config):
        self.config = config
        self.coords = config['observer']['zone']

    def convertToBytes(self, img):
        _, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        return cv2.imencode('.jpg', img)[1].tostring()

    def updateCoords(self, data):
        self.config['observer']['zone'] = data
        self.coords = data
        print(self.config['observer']['zone'])

if __name__ == "__main__":
    t.sleep(3)
    chat = ChatReceiver().getChat()
    cv2.imwrite('tmp.jpg', chat)