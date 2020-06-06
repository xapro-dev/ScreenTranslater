from chatReceiver import ChatReceiver
from stateSaver import StateSaver
from stateComparer import StateComparer
from translateRequester import TranslateRequester
from threading import Thread, Event
from gui import Window
from error import RequesterError
from container import Container
from time import sleep


class Main():

    terminate = Event()
    pause = Event()
    refreshing = Event()
    pause.set()

    def __init__(self):
        self.container = Container()
        self._chatReceiver = ChatReceiver()
        self._chatReceiver.init(self.container.config)
        self._stateSaver = StateSaver()
        self._stateComparer = StateComparer()
        self._translateRequester = TranslateRequester()

    def run(self):
        window = Window()
        window.init(self.container, self._chatReceiver.updateCoords, self.pause, self.refreshing)
        screenReaderThread = Thread(target=self.runLoop, args=(window.refresh,), daemon=True)
        screenReaderThread.start()
        window.mainloop()
        self.terminate.set()
        screenReaderThread.join()
        self.container.saveConfig()

    def runLoop(self, windowRefresh):

        while not self.terminate.isSet():

            if self.pause.isSet():
                sleep(0.1)
                continue

            try:
                chat = self._chatReceiver.getChat()
                self._stateSaver.save(chat)
                if (not self._stateComparer.stateChanged(self._stateSaver)):
                    self.refreshing.clear()
                    continue
                self.refreshing.set()
                text = self._translateRequester.translate(self._chatReceiver.convertToBytes(chat))
                if not self.terminate.isSet():
                    windowRefresh(text)
            except RequesterError:
                print(RequesterError)
            finally:
                sleep(1)


Main().run()
