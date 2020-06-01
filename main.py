from chatReceiver import ChatReceiver
from stateSaver import StateSaver
from stateComparer import StateComparer
from translateRequester import TranslateRequester
import time as t
from threading import *
from gui import Window
from error import RequesterError

class Main():

    def __init__(self):
        
        self._chatReceiver = ChatReceiver()
        self._stateSaver = StateSaver()
        self._stateComparer = StateComparer()
        self._translateRequester = TranslateRequester()

    def run(self):
        window = Window()
        window.init()
        window.attributes("-topmost", 1)
        screenReaderThread = Thread(target=self.runLoop, args=(window.refresh,))
        screenReaderThread.setDaemon(True)
        screenReaderThread.start()
        window.mainloop()

    def runLoop(self, callback):

        while True:
            try:
                chat = self._chatReceiver.getChat()
                self._stateSaver.save(chat)
                if (not self._stateComparer.stateChanged(self._stateSaver)):
                    continue
                text = self._translateRequester.translate(self._chatReceiver.convertToBytes(chat))
                callback(text)
            except RequesterError:
                print(RequesterError)
            finally:
                t.sleep(1)

def ok(data):
    print(data)

if __name__ == "__main__":
    Main().run()

