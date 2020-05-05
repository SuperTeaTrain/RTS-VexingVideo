# Programmer: Miles Brandt
# File: FrameDelayer.py
# Description: This file is intended to serve as a location to hold the pseudo
# delay functions for the audio and video. These must occur at the highest 
# priority, since the audio being passed will go through here.

# Class: UserDelay
# Description: A class is necessary because there will be variables passed to
# this, for the managing of the queues (arrays) of files.

import random
import sys
import threading

class FrameDelayer:
    
    m_v_index = 0
    m_a_index = 0
    m_vlist_files = None
    m_alist_files = None
    m_ds_audio = -1
    m_ds_video = -1
    _vid_variance = 30
    _aud_variance = 90
    m_v_buffer = None
    m_a_buffer = None
    m_v_flag = False
    m_a_flag = False
    
    # Description: Default constructor for the Frame Delayer. It does NOT
    # contain initial values for the delay, because this will always start at 0
    # for the GUI, and will be updated at user's discretion. 

    def __init__(self, v_file_array, a_file_array):
        self.m_alist_files = a_file_array
        self.m_vlist_files = v_file_array

    # Description: This is intended to be called each time the console is ready
    # for an additional frame, i.e. after it confirms having received the
    # previous one, and sends a new frame to the GUI after a constrained random
    # amount of time dependent on the seed value for the previous one. Also,
    # an additional argument may be passed for a user-updated value for the 
    # delay by the slider.
    # Precondition: The GUI is in "play" mode.
    # Postcondition: The m_ds_video is reset, if passed to this, and the next
    # frame is updated, i.e. m_v_index is incremented.

    def get_frame(self, new_seed=None):
        if self.m_v_index < len(m_vlist_files):
            self.m_v_buffer = self.m_vlist_files[self.m_v_index]
            self.m_v_index += 1
            if new_seed is not None:
                if new_seed > 0:
                    self.m_ds_video = new_seed # Update the seed.
                elif new_seed == 0:
                    self.m_ds_video = -1
            if self.m_ds_video == -1:
                self.send_video()
                return
            else:
                waittime = random.randint(self.m_ds_video - self._vid_variance,
                                          self.m_ds_video + self._vid_variance)
                threading.timer(waittime/1000, self.send_video())
                return
        else:
            return None # The video is over.
        

    def get_audio_snippet(self, new_seed=None):
        if self.m_a_index < len(m_alist_files):
            buffer = self.m_alist_files[self.m_a_index]
            self.m_a_index += 1
            if new_seed is not None:
                if new_seed > 0:
                    self.m_ds_audio = new_seed
                elif new_seed == 0:
                    self.m_ds_audio = -1
            if self.m_ds_audio == -1:
                return buffer
            else:
                waittime = random.randint(self.m_ds_audio - self._aud_variance,
                                          self.m_ds_audio + self._aud_variance)
                sys.sleep(waittime)
                return buffer
        else:
            return None # The video is over.
