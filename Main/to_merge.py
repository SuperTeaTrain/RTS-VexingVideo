try:
    import os, sys, time, queue, threading
    from tkinter import *  
    from PIL import ImageTk, Image
    from threading import Timer
except ImportError as error:
    print("Couldn't load module {}".format(error))
    sys.exit(2)

# --- 80 Columns ------------------------------------------------------------- #

FRAME_RATE = 29.970030
UPDATE_RATE = int(1000/FRAME_RATE + 0.5)

ready_lock = threading.Lock()
ready_lock.acquire()
frames_lock = threading.Lock()
frames_lock.acquire()

frames = []
available_frames = []

class myThread(threading.Thread):
   def __init__(self, func):
      threading.Thread.__init__(self)
      self.func = func
   def run(self):
      self.func()

def get_frame(t):
    global ready_lock
    global frames_lock
    global frames
    global available_frames
    f = int(t*FRAME_RATE)
    with frames_lock:
        if 0 < len(frames) and f < len(frames):
            available_frames += [frames[f]]
            # Delay here?
        return
    return

def get_audio(t):
    print('Get audio')
    # Delay here?
    return True

def scheduler():
    global ready_lock
    global frames_lock
    global frames
    global available_frames
    last_audio = -1
    with ready_lock:
        pass # Wait for ready_lock
    start_time = time.monotonic()
    while True:
       t = time.monotonic() - start_time
       if 1 <= t - last_audio:
           last_audio = int(t)
           get_audio(t)
       else:
           get_frame(t)
       time.sleep(1/(2*FRAME_RATE))
    return

class App():
    def __init__(self):
        self.t = 0
        self.root = Tk()
        self.root.title('Vexing Video')
        self.root.protocol('WM_DELETE_WINDOW', self.on_cleanup)
        return
    def start(self):
        global ready_lock
        global frames_lock
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
        ready_lock.release()
        frames_lock.release()
        self.on_loop()
        self.root.mainloop()
        return
    def on_cleanup(self):
        self.root.destroy()
        os._exit(1)
        return
    def create_canvas(self, width, height):
        self.width1 = width
        self.height1 = height
        self.canvas1 = Canvas(width=self.width1, height=self.height1)
        self.canvas1.pack()
        return
    def on_loop(self):
        global ready_lock
        global frames_lock
        global frames
        global available_frames
        if 0 < len(available_frames):
            with frames_lock:
                if available_frames[self.t][0] == 'i':
                    self.canvas1.delete('all')
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
    app.start()
    return

if __name__ == '__main__' :
    thread1 = myThread(scheduler)
    thread1.start()
    gui_main()

