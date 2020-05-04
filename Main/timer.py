try:
    import math, time, threading
except ImportError as error:
    print("Couldn't load module {}".format(error))
    sys.exit(2)

class Timer:
    m_lock = None
    m_running = False
    m_start_sec = None
    m_end_sec = None
    m_ref_time = None
    
    def __init__(self):
        self.m_lock = threading.Lock()
        self.m_running = False
        return
    
    def start(self):
        print('Started')
        self.m_running = True
        self.m_ref_time = time.monotonic()
        return
    
    def try_start(self):
        if self.m_max_sec is not None and self.m_end_sec is not None:
            if not self.m_running and self.m_max_sec < self.m_end_sec:
                self.start()
        return
    
    def pause(self, t=None):
        print('Paused')
        if self.m_running:
            self.m_running = False
            if t is not None:
                self.m_start_sec = t
            else:
                elaspsed = self.m_start_sec + time.monotonic() - self.m_ref_time
                self.m_start_sec = elaspsed
        return
    
    def get_time(self):
        if self.m_running:
            elapsed = self.m_start_sec + time.monotonic() - self.m_ref_time
            x = min(self.m_max_sec, self.m_end_sec)
            if x <= elapsed:
                self.pause(x)
                return x
            return elapsed 
        else:
            return self.m_start_sec
        return self.m_start_sec
     
    def set_end_sec(self, sec):
        self.m_end_sec = sec
        return
    
    def set_start_sec(self, sec):
        self.m_start_sec = sec
        return
    
    def set_max_sec(self, sec):
        if self.m_end_sec is not None:
            self.m_max_sec = max(sec, self.m_end_sec)
        else:
            self.m_max_sec = sec
        return
     
def test():
    timer = Timer()
    timer.set_start_sec(0)
    timer.set_end_sec(10)
    timer.set_max_sec(11)
    timer.start()
    while True:
        print(str(timer.get_time()))
    return

if __name__ == '__main__' :
    test()

