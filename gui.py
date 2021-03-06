from __future__ import annotations
import re
from tkinter.ttk import Style

import container as cnt
from threading import Thread
from PIL import ImageGrab, ImageTk
import time as t
from tkinter import Tk, Frame, StringVar, Text, Toplevel, Canvas, Label, Button, Widget, EventType
from tkinter.constants import BOTH, E, LEFT, Y, NORMAL, END, INSERT, DISABLED,\
    WORD, NW
from ttkthemes import ThemedTk

from speaker import Speaker



class Window(ThemedTk):
    voice_api = refreshing = pauseEvent = zoneUpdater = _frame = refreshingTextVar = _voice_btn = _selectBtn = \
        _closeBtn = _listbox = _pause_btn = _autohide_btn = None
    visible = True
    visible_till = None
    ahide = False
    top = None

    def toggle(self, event):
        if event.type == EventType.Map:
            self.deiconify()
        else:
            self.withdraw()

    def init(self, container: cnt.Container, zoneUpdater, pauseEvent, refreshing, voice_api: Speaker):
        # create the "invisible" toplevel
        self.top = Toplevel(self)
        self.top.geometry('0x0+10000+10000')  # make it not visible
        self.top.protocol('WM_DELETE_WINDOW', self.destroy)  # close root window if toplevel is closed
        self.top.bind("<Map>", self.toggle)
        self.top.bind("<Unmap>", self.toggle)

        self.voice_api = voice_api
        self.visible = True
        self.reset_visibility()
        self.refreshing = refreshing
        self.pauseEvent = pauseEvent
        self.zoneUpdater = zoneUpdater
        self.config = container.config
        coords = self.config['gui']['window']['pos']
        self.attributes("-topmost", 1)
        self.attributes("-alpha", "0.7")
        # self.wm_attributes('-type', 'dock')
        self.overrideredirect(1)
        width = int(self.winfo_screenwidth() / 3.84)
        height = int(self.winfo_screenheight() / 3.6)
        self.geometry(f'{width}x{height}+{coords[0]}+{coords[1]}')
        Drag(self)

        style = Style()
        # ('winnative', 'clam', 'alt', 'default', 'classic', 'vista', 'xpnative')
        style.theme_use('clam')

        self._frame = Frame(self, bg='#222')
        self._frame.pack(fill=BOTH, expand=1)

        button_frame = Frame(self._frame, bg='#222')
        button_frame.pack(anchor=E)

        self.refreshingTextVar = StringVar()
        Label(button_frame, textvariable=self.refreshingTextVar, bg='#222', fg='#fff', bd=0).pack(side=LEFT, fill=Y)
        Thread(target=self.watchRefreshingState, daemon=True).start()

        self._autohide_btn = Button(button_frame, text='ahide', command=self.toggle_autohide, bg='#222', fg='#fff')
        self._autohide_btn.pack(side=LEFT)

        self._voice_btn = Button(button_frame, text='mute', command=self.toggle_voice, bg='#222', fg='#fff')
        self._voice_btn.pack(side=LEFT)

        self._pause_btn = Button(button_frame, text='run', command=self.pause, bg='#222', fg='#fff')
        self._pause_btn.pack(side=LEFT)

        self._selectBtn = Button(button_frame, text='select', command=self.runSelect, bg='#222', fg='#fff')
        self._selectBtn.pack(side=LEFT)

        self._closeBtn = Button(button_frame, text='close', command=self.destroy, bg='#222', fg='#fff')
        self._closeBtn.pack(side=LEFT)

        self._listbox = Text(self._frame, width=100, height=100, wrap=WORD, spacing1=5, font="Helvetica 12", bg="black", fg="white")
        self._listbox.tag_configure("bold", font="Helvetica 12 bold")
        self._listbox.pack()

    def toggle_autohide(self):
        self.ahide = not self.ahide
        if self.ahide:
            self._autohide_btn.config(bg='#fff', fg='#222')
        else:
            self._autohide_btn.config(bg='#222', fg='#fff')

    def reset_visibility(self):
        self.visible_till = t.time() + 20

    def watchRefreshingState(self):
        while True:
            if self.pauseEvent.isSet():
                text = 'paused...'
            elif self.refreshing.isSet():
                self.reset_visibility()
                text = 'translating...'
            else:
                text = ''
            self.refreshingTextVar.set(text)
            
            if self.visible_till < t.time() and self.visible and text != 'paused...' and self.ahide:
                self.visible = False
                self.top.iconify()
            
            if self.visible_till >= t.time() and not self.visible:
                self.visible = True
                self.top.deiconify()

            t.sleep(0.2)

    def toggle_voice(self):
        if self.voice_api.enabled:
            self._voice_btn.config(text='speak')
        else:
            self._voice_btn.config(text='mute')

        self.voice_api.toggle()

    def pause(self):
        if not self.pauseEvent.isSet():
            self._pause_btn.config(text='resume')
            self.pauseEvent.set()
        else:
            self._pause_btn.config(text='pause')
            self.pauseEvent.clear()

    def refresh(self, data: list):
        self._listbox.configure(state=NORMAL)
        self._listbox.delete("1.0", END)
        for row in data:
            match = re.search('\d+:\d+[]\s}]*([^:]+:)(.+)', row)
            speaker = ''
            sentence = row
            if match:
                speaker = match.groups()[0]
                sentence = match.groups()[1]
            self._listbox.insert(INSERT, speaker, 'bold')
            self._listbox.insert(INSERT, sentence + "\n")
        self._listbox.see(END)
        self._listbox.configure(state=DISABLED)

    def destroy(self, *args):
        self.config['gui']['window']['pos'] = [self.winfo_x(), self.winfo_y()]
        return super().destroy()

    def runSelect(self):
        rectangler = Rectangler()
        rectangler.init(self.zoneUpdater)
        Thread(target=rectangler.mainloop)


class Rectangler(Toplevel):
    xScreenShot = None
    def init(self, zoneUpdater):
        self.zoneUpdater = zoneUpdater
        self.attributes("-topmost", 1)
        self.overrideredirect(1)
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(str(screen_width) + 'x' + str(screen_height))

        self.canvas = Canvas(self, bg='#111')
        screenshot = ImageGrab.grab()
        self.xScreenShot = ImageTk.PhotoImage(screenshot, master=self)
        self.canvas.create_image(0,0,image=self.xScreenShot, anchor=NW)
        self.canvas.pack(fill=BOTH, expand=1)
        self.bind('<ButtonPress-1>', self.startSelect)
    
    def startSelect(self, event):
        self.zone = []
        self.zone.append(event.x)
        self.zone.append(event.y)
        self.rectangle = self.canvas.create_rectangle(self.zone[0], self.zone[1], self.zone[0], self.zone[1])
        self.bind('<ButtonRelease-1>', self.stopSelect)
        self.bind('<Motion>', self.onMouseMove)
        print(self.rectangle)

    def onMouseMove(self, event):
        self.canvas.delete(self.rectangle)
        self.rectangle = self.canvas.create_rectangle(self.zone[0], self.zone[1], event.x, event.y, width=2, outline='red')

    def stopSelect(self, event):
        self.zone.append(self.winfo_pointerx())
        self.zone.append(self.winfo_pointery())
        self.unbind('<ButtonRelease-1>')
        self.unbind('<Motion>')
        self.zoneUpdater(self.canonicalRect())
        self.destroy()

    def canonicalRect(self):
        return [
            min(self.zone[0], self.zone[2]),
            min(self.zone[1], self.zone[3]),
            max(self.zone[0], self.zone[2]),
            max(self.zone[1], self.zone[3]),
        ]


class Drag:
    ''' Makes a window dragable. '''
    Par: Tk

    def __init__(self, par, dissable=None, releasecmd=None):

        self.Par = par
        self.Dissable = dissable

        self.ReleaseCMD = releasecmd

        self.Par.bind('<Button-1>', self.relative_position)

    def relative_position(self, event):

        self.Par.bind('<ButtonRelease-1>', self.drag_unbind)

        cx, cy = self.Par.winfo_pointerxy()
        x = self.Par.winfo_x()
        y = self.Par.winfo_y()

        self.OriX = x
        self.OriY = y

        self.RelX = cx - x
        self.RelY = cy - y

        self.Par.bind('<Motion>', self.drag_wid)

    def drag_wid(self, event):

        cx, cy = self.Par.winfo_pointerxy()

        d = self.Dissable

        if d == 'x':
            x = self.OriX
            y = cy - self.RelY
        elif d == 'y':
            x = cx - self.RelX
            y = self.OriY
        else:
            x = cx - self.RelX
            y = cy - self.RelY

        if x < 0:
            x = 0

        if y < 0:
            y = 0

        self.Par.wm_geometry('+' + str(x) + '+' + str(y))

    def drag_unbind(self, event):

        self.Par.unbind('<ButtonRelease-1>')
        self.Par.unbind('<Motion>')

        if self.ReleaseCMD is not None:
            self.ReleaseCMD()

    def dissable(self):

        self.Par.unbind('<Button-1>')
        self.Par.unbind('<ButtonRelease-1>')
        self.Par.unbind('<Motion>')


class CanvasMover():
    canvas: Canvas = None
    mouseTarget: Widget = None
    movable = None

    def __init__(self, canvas, mouseTarget, movable):

        self.canvas = canvas
        self.mouseTarget = mouseTarget
        self.movable = movable

        self.mouseTarget.bind('<Button-1>', self.relative_position)

    def relative_position(self, event):

        self.mouseTarget.bind('<ButtonRelease-1>', self.drag_unbind)
        self.mouseTarget.bind('<Motion>', self.drag_wid)

        self.OriX, self.OriY = self.canvas.winfo_pointerxy()

    def drag_wid(self, event):

        cx, cy = self.canvas.winfo_pointerxy()

        offsetX = cx - self.OriX
        offsetY = cy - self.OriY

        self.OriX = cx
        self.OriY = cy

        self.canvas.move(self.movable, offsetX, offsetY)

    def drag_unbind(self, event):

        self.mouseTarget.unbind('<ButtonRelease-1>')
        self.mouseTarget.unbind('<Motion>')
