import re
from tkinter.ttk import Style

import pyttsx3

from speaker import Speaker
from chatReceiver import ChatReceiver
from stateSaver import StateSaver
from stateComparer import StateComparer
from translateRequester import TranslateRequester
from threading import Thread, Event
from gui import Window
import error as er
from container import Container
from time import sleep
#
# style = Style()
# # ('winnative', 'clam', 'alt', 'default', 'classic', 'vista', 'xpnative')
# style.theme_use('winnative')

class Main:

    translated_sentences = []
    terminate = Event()
    pause = Event()
    refreshing = Event()
    pause.set()
    skip = False
    text = ''
    engine = pyttsx3.init()
    voice_enabled = False
    voice_thread: Thread

    def __init__(self):
        self.container = Container()
        self._chatReceiver = ChatReceiver()
        self._chatReceiver.init(self.container.config)
        self._stateSaver = StateSaver()
        self._stateComparer = StateComparer()
        self._translateRequester = TranslateRequester(self.container)
        self._speaker = Speaker(self.terminate)

    def run(self):
        window = Window(theme="black")
        window.init(self.container, self._chatReceiver.updateCoords, self.pause, self.refreshing, self._speaker)
        screen_reader_thread = Thread(target=self.run_loop, args=(window.refresh,), daemon=True)
        voice_thread = Thread(target=self._speaker.loop, daemon=True)
        voice_thread.start()
        screen_reader_thread.start()
        window.mainloop()
        self.terminate.set()
        screen_reader_thread.join()
        self.container.saveConfig()

    def toggle_voice(self):
        if self.voice_enabled:
            self.voice_thread.join(1)
        else:
            self.voice_thread.start()
        self.voice_enabled = not self.voice_enabled

    def is_handled(self, text: str) -> bool:
        try:
            return self.translated_sentences.index(text) > -1
        except ValueError:
            return False

    def store_as_handled(self, text: str) -> None:
        if len(self.translated_sentences) > 100:
            self.translated_sentences.pop(0)

        self.translated_sentences.append(text)

    def run_loop(self, window_refresh):
        wait_for_same_state = False
        last_sentence = self.text

        while not self.terminate.isSet():

            if self.pause.isSet():
                sleep(0.1)
                continue

            try:
                chat = self._chatReceiver.getChat()
                self._stateSaver.save(chat)

                if not self._stateComparer.stateChanged(self._stateSaver):
                    self.refreshing.clear()
                    if not wait_for_same_state:
                        continue
                else:
                    print('wait for same state')
                    wait_for_same_state = True
                    continue

                wait_for_same_state = False

                self.refreshing.set()
                # text = self._translateRequester.imgToTxt(chat)
                # print(text)
                text = self._translateRequester.translate_image(chat)

                last_row: str = text[-1:][0]
                speaker_search = re.search('(\[\d+:\d+[\s\]}]*([^:]+)):', last_row)
                if speaker_search:
                    speaker = speaker_search.group(2).split(' ')[0] + ' говорит'
                    last_row = last_row.replace(speaker_search.group(1), speaker)

                sentence = re.sub('\[\d+:\d+[^:]+:', '', last_row)

                if last_sentence == sentence:
                    continue

                if self.is_handled(sentence):
                    continue

                self.store_as_handled(sentence)
                self._speaker.queue(sentence)

                self.skip = False
                if not self.terminate.isSet():
                    window_refresh(text)
            except er.RequesterError as e:
                print(str(e))
            except er.NoTextError as e:
                print(str(e))
                window_refresh([str(e)])
                self.skip = True
            except er.BadFile as e:
                print(str(e))
            finally:
                if self.skip:
                    sleep(2)
                else:
                    sleep(.3)


Main().run()
