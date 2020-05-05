try:
    import os, sys, time, threading
    import tkinter as tk
    from pydub import AudioSegment
    from pydub.playback import play
    from PIL import ImageTk, Image
    import timer
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
audio_lock = threading.Lock()
audio_lock.acquire()
audio_playback_lock = threading.Lock()
audio_playback_lock.acquire()

frames = []
available_frames = []
available_audio = []
audio = []

flag_a_r = False
flag_v_r = False

class myThread(threading.Thread):
   def __init__(self, func, arg=None):
      threading.Thread.__init__(self)
      self.func = func
      self.arg = arg
   def run(self):
      self.func(self.arg)

def get_frame(arg, t):
    global ready_lock
    global frames_lock
    global frames
    global available_frames
    frame = int(t*FRAME_RATE)
    i_frame = max(0, int((frame+1)/60)*60-1)
    with frames_lock:
        if 0 <= i_frame < len(frames) and available_frames[i_frame] is None:
            available_frames[i_frame] = frames[i_frame]
            return
            # Delay here?
        if 0 <= frame < len(frames) and available_frames[frame] is None:
            available_frames[frame] = frames[frame]
            # Delay here?
            return
    return

def play_audio(arg):
    play(AudioSegment.from_file(arg, 'aac'))
    return

def get_audio(arg, t):
    global available_audio
    global audio
    global audio_lock
    t = int(t + 0.5)
    if 0 <= t < len(audio):
        with arg.timer.m_lock:
            arg.timer.set_max_sec(t + 1)
        # Delay here?
        thread2 = myThread(play_audio, audio[int(t)])
        thread2.start()
        with arg.timer.m_lock:
            arg.timer.try_start()
    return True

def scheduler(arg):
    global ready_lock
    global frames_lock
    global audio_lock
    global frames
    global available_frames
    global available_audio
    last_audio = -999
    with ready_lock:
        pass # Wait for ready_lock
    while True:
        if flag_a_r:
            with audio_lock:
                if (len(available_audio)):
                   t = available_audio[-1][0] + 1
                else:
                    t = 0
            paused = arg.paused


        elif flag_v_r:
            pass 
        with arg.timer.m_lock:
            t = arg.timer.get_time()
            paused = arg.paused
        if not paused:
            if 1 <= t - last_audio:
                last_audio = int(t)
                get_audio(arg, t)
            else:
                get_frame(arg, t)
        time.sleep(1/(2*FRAME_RATE))
    return

def start(self):
    global ready_lock
    global frames_lock
    global audio_lock
    global frames
    global available_frames
    global audio
    thread1 = myThread(scheduler, self)
    thread1.start()
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
    audio = sorted([
        'Audio/' + filename
        for filename
        in os.listdir('Audio')
        if os.path.isfile(os.path.join('Audio', filename))
    ])
    with self.timer.m_lock:
       self.timer.set_end_sec(len(frames) * FRAME_RATE)
    available_frames = [None for i in frames]
    ready_lock.release()
    frames_lock.release()
    self.on_loop()
    return

def on_loop(self):
    global ready_lock
    global frames_lock
    global audio_lock
    global frames
    global available_frames
    if 0 < len(available_frames):
        with self.timer.m_lock:
            t = self.timer.get_time()
        frame = int(t*FRAME_RATE)
        i_frame = max(0, int((frame+1)/60)*60-1)
        with frames_lock:
            while True:
                if 0 <= i_frame < len(frames) and \
                    i_frame != self.m_last_i_frame and \
                    available_frames [i_frame] is not None:
                    self.m_canvas_main.delete('all')
                    self.m_canvas_main.create_image(
                        self.m_c_width/2,
                        self.m_c_height/2,
                        image=available_frames[i_frame][1]
                    )
                    self.m_last_i_frame = i_frame
                    break
                if 0 <= frame < len(frames) and \
                    available_frames[frame] is not None:
                    if available_frames[frame][0] == 'i':
                        self.m_canvas_main.delete('all')
                    self.m_canvas_main.create_image(
                        self.m_c_width/2,
                        self.m_c_height/2,
                        image=available_frames[frame][1]
                    )
                    break
                frame -= 1
                if frame < 0:
                    break
    self.m_root.after(UPDATE_RATE, self.on_loop)
    return

