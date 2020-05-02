import os
from tkinter import *  
from PIL import ImageTk, Image
import time

# --- 80 Columns ------------------------------------------------------------- #

UPDATE_RATE = int(1000/16)

class App():
    def __init__(self):
        self.t = 0
        self.root = Tk()
        self.root.title('Vexing Video')
        return
    def start(self):
        self.on_loop()
        self.root.mainloop()
        return
    def on_cleanup(self):
        return
    def create_canvas(self, width, height):
        self.width1 = width
        self.height1 = height
        self.canvas1 = Canvas(width=self.width1, height=self.height1)
        self.canvas1.pack()
        return
    def set_frames(self, frames):
        self.frames = frames
        return
    def on_loop(self):
        if self.t % len(self.frames) == 0:
            self.canvas1.delete('all')
        self.canvas1.create_image(
            self.width1/2,
            self.height1/2,
            image=self.frames[self.t][1]
        )
        self.t = (self.t + 1) % len(self.frames)
        self.root.after(UPDATE_RATE, self.on_loop)
        return

def main():
    app = App()
    frames = [
        [filename[10], 'Frames/' + filename]
        for filename
        in os.listdir('Frames')
        if os.path.isfile(os.path.join('Frames', filename))
    ]
    frames = sorted(frames, key=lambda x: x[1])
    frames = [
        [i[0], ImageTk.PhotoImage(Image.open(i[1]))]
        for i
        in frames
    ]
    app.create_canvas(frames[0][1].width(), frames[0][1].height())
    app.set_frames(frames)
    app.start()
    return

if __name__ == "__main__" :
    main()

