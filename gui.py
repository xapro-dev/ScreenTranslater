from __future__ import annotations
import re
import container as cnt
from threading import Thread
from PIL import ImageGrab, ImageTk
import time as t
from tkinter import Tk, Frame, StringVar, Text, Toplevel, Canvas, Label, Button
from tkinter.constants import BOTH, E, LEFT, Y, NORMAL, END, INSERT, DISABLED,\
    WORD, NW


class Window(Tk):

    def init(self, container: cnt.Container, zoneUpdater, pauseEvent, refreshing):
        self.refreshing = refreshing
        self.pauseEvent = pauseEvent
        self.zoneUpdater = zoneUpdater
        self.config = container.config
        coords = self.config['gui']['window']['pos']
        self.attributes("-topmost", 1)
        self.attributes("-alpha", "0.7")
        self.overrideredirect(1)
        self.geometry(f'500x300+{coords[0]}+{coords[1]}')
        Drag(self)

        self._frame = Frame(self, bg='#222')
        self._frame.pack(fill=BOTH, expand=1)

        buttonFrame = Frame(self._frame, bg='#222')
        buttonFrame.pack(anchor=E)

        self.refreshingTextVar = StringVar()
        Label(buttonFrame, textvariable=self.refreshingTextVar, bg='#222', fg='#fff', bd=0).pack(side=LEFT, fill=Y)
        Thread(target=self.watchRefreshingState, daemon=True).start()

        self._selectBtn = Button(buttonFrame, text='pause', command=self.pause, bg='#222', fg='#fff')
        self._selectBtn.pack(side=LEFT)

        self._selectBtn = Button(buttonFrame, text='select', command=self.runSelect, bg='#222', fg='#fff')
        self._selectBtn.pack(side=LEFT)

        self._closeBtn = Button(buttonFrame, text='close', command=self.destroy, bg='#222', fg='#fff')
        self._closeBtn.pack(side=LEFT)

        self._listbox = Text(self._frame, width=100, height=100, wrap=WORD, spacing1=5, font="Helvetica 12", bg="black", fg="white")
        self._listbox.tag_configure("bold", font="Helvetica 12 bold")
        self._listbox.pack()

    def watchRefreshingState(self):
        while True:
            if self.pauseEvent.isSet():
                text = 'paused...'
            elif self.refreshing.isSet():
                text = 'translating...'
            else:
                text = ''
            self.refreshingTextVar.set(text)
            t.sleep(0.1)


    def pause(self):
        if not self.pauseEvent.isSet():
            self.pauseEvent.set()
        else:
            self.pauseEvent.clear()
        

    def refresh(self, data: list):
        self._listbox.configure(state=NORMAL)
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
        self.geometry(f'1920x1080')

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
