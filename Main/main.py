#!/usr/bin/env python
# Programmer: Miles Brandt
# File: VVDummy.py
# Description: This is the Vexing Video GUI's main GUI window. It is intended
# to accept input for the canvas on the left side of the screen, so that images
# may be displayed.

# --- 80 Columns ------------------------------------------------------------- #

try:
    import os, time, sys
    import tkinter as tk
    from PIL import ImageTk, Image
    import pydub as pdb
    import tkinter.filedialog
    import playback, timer
except ImportError as error:
    print("Couldn't load module {}".format(error))
    sys.exit(2)

# Class: VVWindow
# Description: This is the class for the tkinter main window for Vexing Video.
# it is class, so that it, and all of its modules, may be passed as a whole to 
# a separate main function.

class VVWindow:
    m_root = None # TCL is used in lieu of Tk for ease of use on Linux.
    m_q = None # Picture to be displayed on the canvas ASAP.
    m_base_frame = None # To be placed in the root.
    m_button_frame = None # Buttons to interact with the canvas.
    m_ctrl_frame = None # Control panel, pack to the right. 
    m_canvas_frame = None # Contains the canvas and the button frame.
    m_button_play = None # Play button, pack it first.
    m_button_pause = None # Pause button, pack it after the play button
    m_canvas_main = None
    m_label_dt = None
    m_label_vdelay = None
    m_label_adelay = None
    m_v_is_dt = None # this is to be tied to the radio button.
    m_radio_tol = None # Delay Tolerant user selection.
    m_radio_intol = None # Delay Intolerant user selection.
    m_scale_vdelay = None # Delay for video random seed, in ms
    m_v_vdelay = None # The actual value for this
    m_c_width = 800
    m_c_height = 600
    m_menubar = None # Helps to open files and close.
    m_menu_file = None
    m_video_dir = None


    # Description: Initializer of the VVWindow class. Intended to set it 
    # up with all buttons and their handlers ready.
    # Precondition: None
    # Postcondition: A new window appears.

    def __init__(self):
        self.m_root = tk.Tk()
        
        self.m_last_i_frame = -999
        self.m_last_audio = -999
        self.m_last_played_audio = -999
        self.m_v_vdelay = tk.IntVar()
        self.paused = True
        self.timer = timer.Timer()
        with self.timer.m_lock:
            self.timer.set_start_sec(0)
            self.timer.set_max_sec(1)
        
        # Get size from frame image
        try:
            temp = ImageTk.PhotoImage(Image.open('Frames/0000000001i.png'))
            m_c_width, m_c_height = temp.width(), temp.height()
        except:
            m_c_width, m_c_height = 800, 600
        
        self.m_v_is_dt = True
        self.m_root.title = "Vexing Video"
        self.m_root.protocol('WM_DELETE_WINDOW', self.on_cleanup)
        self.m_base_frame = tk.Frame(self.m_root, borderwidth=10)
        self.m_base_frame.pack()
        self.m_canvas_frame = tk.Frame(self.m_base_frame, background='RED')
        self.m_canvas_frame.pack(side=tk.LEFT, expand=tk.YES)
        self.m_canvas_main = tk.Canvas(self.m_canvas_frame,
                                       width=self.m_c_width, height=self.m_c_height)
        self.m_canvas_main.pack(side=tk.TOP)
        self.m_button_frame = tk.Frame(self.m_canvas_frame, background='BLUE')
        self.m_button_frame.pack(side=tk.TOP, expand=tk.YES)
        self.m_button_play = tk.Button(self.m_button_frame, text="Play",
                                       padx=10, pady=10,
                                       command=self._play)
        self.m_button_play.pack(side=tk.LEFT)
        self.m_button_pause = tk.Button(self.m_button_frame, text="Pause",
                                        padx=10, pady=10,
                                        command=self._pause)
        self.m_button_pause.pack(side=tk.LEFT)
        self.m_ctrl_frame = tk.Frame(self.m_base_frame, borderwidth=10,
                                     relief=tk.RIDGE)
        self.m_ctrl_frame.pack(side=tk.LEFT, expand=tk.YES)
        self.m_label_dt = tk.Label(self.m_ctrl_frame, text="Delay Tolerance")
        self.m_label_dt.pack(side=tk.TOP)
        self.m_radio_tol = tk.Radiobutton(self.m_ctrl_frame,
                                          text="Tolerant (Videos)",
                                          variable=self.m_v_is_dt, pady = 10,
                                          value=True).pack(side=tk.TOP)
        self.m_radio_intol = tk.Radiobutton(self.m_ctrl_frame,
                                            text="Intolerant (Calls)",
                                            variable=self.m_v_is_dt, pady = 10,
                                            value=False).pack(side=tk.TOP)
        self.m_label_vdelay = tk.Label(self.m_ctrl_frame, 
                                       text="Preferred Video Delay", 
                                       pady=10).pack(side=tk.TOP)
        self.m_scale_vdelay = tk.Scale(self.m_ctrl_frame, orient=tk.HORIZONTAL,
                                       variable=self.m_v_vdelay, from_ = 0, 
                                       to = 100).pack(side=tk.TOP)
        self.m_menubar = tk.Menu(self.m_root)
        self.m_menu_file = tk.Menu(self.m_menubar, tearoff=0)
        self.m_menu_file.add_command(label = "Open",
                                     command = self._trigger_open)
        self.m_menu_file.add_command(label = "Help",
                                     command = self._trigger_help)
        self.m_menu_file.add_separator()
        self.m_menu_file.add_command(label = "Exit", command = lambda : exit(0))
        self.m_menubar.add_cascade(label = 'File', menu = self.m_menu_file)
        self.m_root.config(menu=self.m_menubar)
        return

    def on_cleanup(self):
        self.m_root.destroy()
        os._exit(1)
        return

    def start(self):
        playback.start(self)
        self.m_root.mainloop()
        return
    
    def on_loop(self):
        playback.on_loop(self)
        return
    
    def _trigger_open(self):
        self.video_dir = tk.filedialog.askdirectory()
        return

    def _trigger_help(self):
        pass

    def _pause(self):
        with self.timer.m_lock:
            self.paused = True
            self.timer.pause()
        return
    
    def _play(self):
        with self.timer.m_lock:
            self.paused = False
            self.timer.try_start()
        return

def __main__():
    a = VVWindow()
    a.start()
    return

__main__()