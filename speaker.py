from threading import Event
from time import sleep

import pyttsx3


class Speaker:

    txt_queue = []
    stop: Event
    enabled: bool = True

    def __init__(self, terminate_event: Event):
        self.stop = terminate_event
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", 300)

    def toggle(self):
        self.enabled = not self.enabled

    def queue(self, text: str):
        self.txt_queue.append(text)
        # last_sentence = ''
        # if not self.enabled:
        #     self.txt_queue.clear()
        #     return
        #
        # sentence = self.txt_queue.pop(0)
        # if last_sentence == sentence:
        #     return
        #
        # last_sentence = sentence
        # self.engine.say(sentence)

    def loop(self):
        last_sentence = ''
        while not self.stop.isSet():
            sleep(.1)

            if not self.enabled:
                self.txt_queue.clear()
                continue

            if not self.txt_queue:
                continue

            sentence = self.txt_queue.pop(0)
            if last_sentence == sentence:
                continue

            last_sentence = sentence
            self.engine.say(sentence)
            self.engine.runAndWait()


if __name__ == '__main__':
    e = Event()
    speaker = Speaker(e)
    speaker.queue('hi hi hi')
    speaker.loop()
