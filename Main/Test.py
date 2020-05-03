try:
    import os
    from tkinter import *  
    from PIL import ImageTk, Image
    import time
    from threading import Timer
    import queue
    import threading
except ImportError as error:
    print("Couldn't load module {}".format(error))
    sys.exit(2)

# --- 80 Columns ------------------------------------------------------------- #

UPDATE_RATE = int(1000/16)

readyLock = threading.Lock()
readyLock.acquire()
framesLock = threading.Lock()
framesLock.acquire()

frames = []
available_frames = []

class myThread(threading.Thread):
   def __init__(self, threadID, func):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.func = func
   def run(self):
      self.func()

def scheduler():
    global readyLock
    global framesLock
    global frames
    global available_frames
    t = 0
    with readyLock:
        pass
    while True:
       with framesLock:
           if 0 < len(frames) and t < len(frames):
               available_frames += [frames[t]]
           t = t + 1
       time.sleep(0.2)
    return

class App():
    def __init__(self):
        self.t = 0
        self.root = Tk()
        self.root.title('Vexing Video')
        return
    def start(self):
        global readyLock
        global framesLock
        global frames
        global available_frames
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
        print('len(frames) = ' + str(len(frames)))
        readyLock.release()
        framesLock.release()
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
    #def set_frames(self, frames):
    #    self.frames = frames
    #    return
    def on_loop(self):
        global readyLock
        global framesLock
        global frames
        global available_frames
        if 0 < len(frames) and self.t % len(frames) == 0:
            self.canvas1.delete('all')
        with framesLock:
            if 0 < len(available_frames):
                self.canvas1.create_image(
                    self.width1/2,
                    self.height1/2,
                    image=available_frames[self.t][1]
            )
            if 0 < len(available_frames):
                self.t = (self.t + 1) % len(available_frames)
        self.root.after(UPDATE_RATE, self.on_loop)
        return

def gui_main():
    app = App()
    temp = ImageTk.PhotoImage(Image.open('Frames/0000000001i.png'))
    app.create_canvas(temp.width(), temp.height())
    #app.set_frames(frames)
    app.start()
    return

if __name__ == '__main__' :
    thread1 = myThread('2', scheduler)
    thread1.start()
    gui_main()

