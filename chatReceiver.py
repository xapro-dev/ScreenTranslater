import sys
from PIL import ImageGrab
import numpy as np
from numpy import array as npArray
from cv2 import imwrite, cv2, bitwise_not, copyMakeBorder, BORDER_REPLICATE, imencode, cvtColor, COLOR_RGB2GRAY
import time as t
from container import Config


def increase_brightness(np_el):
    # if isinstance(np_el, np.ndarray):
    #     map(increase_brightness, np_el)
    #     return np_el
    return np_el * 2


class ChatReceiver:

    def getChat(self):
        frame = ImageGrab.grab(self.coords)
        frame.convert()

        frame_gray: cv2 = cvtColor(npArray(frame), COLOR_RGB2GRAY)
        imwrite(f'img_fgr.jpg', frame_gray)
        # chat = frame_gray
        # _, chat = cv2.threshold(frame_gray,i*10,255,cv2.THRESH_BINARY)
        # _, chat = cv2.threshold(frame_gray,i*10,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        # chat = cv2.adaptiveThreshold(frame_gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
        # for i in range(25):
        #     _, chat = cv2.threshold(frame_gray,i*10,255,cv2.THRESH_BINARY)
        #     chat = cv2.bitwise_not(chat)
        #     cv2.imwrite(f'img{i}.jpg', chat)
        if np.mean(frame_gray[:10, :10]) < 122:
            frame_gray = bitwise_not(frame_gray)
        padding = 20
        frame_gray = copyMakeBorder(frame_gray, padding, padding, padding, padding, BORDER_REPLICATE)
        imwrite(f'img_fgr2.jpg', frame_gray)
        # _, chat = cv2.threshold(frame_gray, 80, 255, cv2.THRESH_BINARY)
        # chat = cv2.ximgproc.niBlackThreshold(frame_gray, 255, cv2.THRESH_BINARY, 9, 0, cv2.ximgproc.BINARIZATION_SAUVOLA)
        # _, chat = cv2.threshold(frame_gray, 50, 255, 0)
        # cv2.imwrite(f'imgx1.jpg', chat)
        # chat = cv2.ximgproc.thinning(chat, thinningType=cv2.ximgproc.THINNING_GUOHALL)
        # cv2.imwrite(f'imgx2.jpg', chat)
        return frame_gray

    def init(self, config: Config):
        self.config = config
        self.updateCoords(config['observer']['zone'])

    def convertToBytes(self, img):
        # _, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        return imencode('.jpg', img)[1].tostring()

    def updateCoords(self, data):
        self.config['observer']['zone'] = data
        self.coords = data
        print(self.config['observer']['zone'])


if __name__ == "__main__":
    t.sleep(3)
    chat = ChatReceiver().getChat()
    imwrite('tmp.jpg', chat)
