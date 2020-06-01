from tkinter import *
import re

class Window(Tk):

    def init(self):
        self._listbox = Text(self, wrap=WORD, spacing1=5, font="Helvetica 12")
        self._listbox.tag_configure("bold", font="Helvetica 12 bold")
        self._listbox.pack()

    def refresh(self, data: list):
        self._listbox.delete("1.0", END)
        for row in data:
            match = re.search('([^:]+:)(.+)', row)
            speaker = ''
            sentence = row
            if match:
                speaker = match.groups()[0]
                sentence = match.groups()[1]
            self._listbox.insert(INSERT, speaker, 'bold')
            self._listbox.insert(INSERT, sentence + "\n")
        