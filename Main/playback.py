try:
    import os, sys, time, threading, random
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
# The frame rate converted to a period in milliseconds
UPDATE_RATE = int(1000/FRAME_RATE + 0.5)
VID_VARIANCE = 30
AUD_VARIANCE = 90

# Locks threads until everything is ready
ready_lock = threading.Lock()   
ready_lock.acquire()
# Locks the frame buffer when accessed
frames_lock = threading.Lock()
frames_lock.acquire()
audio_lock = threading.Lock()
audio_lock.acquire()
audio_pb_lock = threading.Lock()
audio_pb_lock.acquire()

frames = []
available_frames = []
audio = [] # I will be replcing this, check for usage.
available_audio = []
available_frames = [] # Frame buffer
audio = []

# Basic thread class that supports passing an argument
class myThread(threading.Thread):
   def __init__(self, func, arg=None):
      threading.Thread.__init__(self)
      self.func = func
      self.arg = arg
   def run(self):
      self.func(self.arg)

# Adds frame to frame buffer
# arg: VWindow
# t: time in seconds
def get_frame(args):
    arg = args[0]
    t = args[1]
    global ready_lock
    global frames_lock
    global frames
    global available_frames
    frame = int(t*FRAME_RATE)
    # There is always and I-frame at the beginning and every 60 frames
    # Corresponds to indices: 0, 59, 119, ...
    i_frame = max(0, int((frame+1)/60)*60-1)

    waittime = random.randint(arg.m_v_vdelay,
                              arg.m_v_vdelay + VID_VARIANCE)
    
    
    time.sleep(waittime / 1000)

    with frames_lock:
        if 0 <= i_frame < len(frames) and available_frames[i_frame] is None:
            available_frames[i_frame] = frames[i_frame]
            return
        if 0 <= frame < len(frames) and available_frames[frame] is None:
            available_frames[frame] = frames[frame]
            return
    return

def play_audio(arg):
    global audio_lock
    global audio_pb_lock
    global available_audio
    with audio_lock:
        b = AudioSegment.from_file(arg[1], 'aac')
    #with arg.timer.m_lock:
    #    arg.timer.set_max_sec(arg[0] + 1)
    with audio_pb_lock:
        play(b)
    return

# Retrives audio
# arg: VWindow
# t: time in seconds
def get_audio(args):
    global audio
    global available_audio
    global audio_lock
    arg = args[0]
    t_original = args[1]
    # Rounds t
    # Maybe it shouldn't round like this
    t = int(t_original + 0.5)
    if 0 <= t < len(audio):
        with audio_lock: # **
            available_audio[t] = (t, audio[t]) # **
    return True

# arg: VWindow
def scheduler(arg):
    global ready_lock
    global frames_lock
    global audio_lock
    global audio_pb_lock
    global frames
    global available_frames
    global available_audio
    with ready_lock:
        pass # Wait for ready_lock
    while True:
        with arg.timer.m_lock:
            t = arg.timer.get_time()
            paused = arg.paused
        if not paused:
            #print("t - arg.m_last_audio = {}".format(t - arg.m_last_audio))
            if 1 <= abs(t - arg.m_last_audio):
                arg.m_last_audio = int(t)
                print("Called get_audio, t = ", t)
                thread3 = myThread(get_audio, [arg, t])
                thread3.start()
            else:
                thread5 = myThread(get_frame, [arg, t])
                thread5.start()
            with arg.timer.m_lock:
                arg.timer.set_max_sec(t + 1)
                if 0 <= arg.m_last_audio and 1 <= abs(t - arg.m_last_played_audio):
                    arg.m_last_played_audio = int(t)
                    arg.timer.try_start()
                    print("Called play audio, t= ", t)
                    thread4 = myThread(play_audio, available_audio[int(t)])
                    thread4.start()
        # How frequently the scheduler runs
        # This could be messed with but should happen at least as frequently as
        # the frames are needed
    return

# self: VWindow
def start(self):
    global ready_lock
    global frames_lock
    global audio_lock
    global audio_pb_lock
    global frames
    global available_frames
    global audio
    global available_audio
    thread1 = myThread(scheduler, self)
    thread1 = myThread(scheduler, self) # Spawn scheduler
    thread1.start()
    frames = [
        [filename[10], 'Frames/' + filename]
        for filename
        in os.listdir('Frames')
        if os.path.isfile(os.path.join('Frames', filename))
    ]
    frames = sorted(frames, key=lambda x: x[1]) # Sort by filename
    # Open images and store them
    # This is where the preprocessing happens
    frames = [
        [i[0], ImageTk.PhotoImage(Image.open(i[1]))]
        for i
        in frames
    ]
    # Just a list of file paths
    audio = sorted([
        'Audio/' + filename
        for filename
        in os.listdir('Audio')
        if os.path.isfile(os.path.join('Audio', filename))
    ])
    available_audio = [None for i in audio]
    with self.timer.m_lock:
       self.timer.set_end_sec(len(frames) / FRAME_RATE)
    available_frames = [None for i in frames]
    ready_lock.release()
    frames_lock.release()
    audio_lock.release()
    audio_pb_lock.release()
    self.on_loop()
    return

# self: VWindow
def reset(self):
    global ready_lock
    global frames_lock
    global audio_lock
    global available_frames
    global available_audio
    with self.timer.m_lock:
        self.paused = True
        self.timer.pause()
        self.timer.set_start_sec(0)
        self.timer.set_end_sec(len(frames) / FRAME_RATE)
        self.timer.set_max_sec(1)
        self.m_last_i_frame = -999
        self.m_last_audio = -999
    with frames_lock:
        available_frames = [None for i in frames] # Clear frame buffer
    with audio_lock:
        available_audio = [None for i in audio]
    return

# self: VWindow
def on_loop(self):
    global ready_lock
    global frames_lock
    global frames
    global available_frames
    if 0 < len(available_frames):
        with self.timer.m_lock:
            t = self.timer.get_time()
        frame = int(t*FRAME_RATE)
        # There is always and I-frame at the beginning and every 60 frames
        # Corresponds to indices: 0, 59, 119, ...
        i_frame = max(0, int((frame+1)/60)*60-1)
        with frames_lock:
            while True: # Loop is always broken out of eventually
                # Displays the last I-frame if needed
                if 0 <= i_frame < len(frames) and \
                    i_frame != self.m_last_i_frame and \
                    available_frames [i_frame] is not None:
                    self.m_canvas_main.delete('all') # Clear canvas
                    self.m_canvas_main.create_image(
                        self.m_c_width/2,
                        self.m_c_height/2,
                        image=available_frames[i_frame][1]
                    )
                    self.m_last_i_frame = i_frame
                    break
                # Displays frame closest to current time but not after
                if 0 <= frame < len(frames) and \
                    available_frames[frame] is not None:
                    if available_frames[frame][0] == 'i':
                        self.m_canvas_main.delete('all') # Clear canvas
                    self.m_canvas_main.create_image(
                        self.m_c_width/2,
                        self.m_c_height/2,
                        image=available_frames[frame][1]
                    )
                    break
                # If this is reached, then there are frames missing
                # So it will look for previous frames
                frame -= 1
                if frame < 0:
                    break # Here, the beginning is reached
        with self.timer.m_lock:
            end_sec = self.timer.m_end_sec
        if abs(end_sec - t) <= 0.05:
            reset(self) # Reached the end of the video
    self.m_root.after(UPDATE_RATE, self.on_loop) # Calls itself to forever
    return

# Description: Non-blocking "with" for locks. This is so that the timer
# can be lined up with the play_audio stuff, and it doesn't constantly
# try to get audio.
# Precondition: None.
# Postcondition: True is returned if the acquire is available, otherwise
# false.

def locket(lock):
    locked = lock.acquire(False)
    try:
        yield locked
    finally:
        if locked:
            lock.release()