import os
from tkinter import *  
from PIL import ImageTk, Image
import time

UPDATE_RATE = int(1000/16)

#root = Tk()  
#canvas = Canvas(root, width = 300, height = 300)  
#canvas.pack()  
#img = ImageTk.PhotoImage(Image.open("Frames/ball.png"))  
#canvas.create_image(20, 20, anchor=NW, image=img) 
#root.mainloop()

frames = [[filename[10], 'Frames/' + filename] for filename in os.listdir('Frames') if os.path.isfile(os.path.join('Frames', filename))]
frames = sorted(frames, key=lambda x: x[1])

#root = Tk()  
#canvas = Canvas(root, width = 300, height = 300)  
#canvas.pack()  
#img = ImageTk.PhotoImage(Image.open(frames[0]))  
#canvas.create_image(20, 20, anchor=NW, image=img) 
#root.mainloop()

def place(root, x, i):
    label3 = Label(root, image=x)
    label3.image = x
    label3.place(x=50+i, y=50)
    return

class App(Frame):
    def __init__(self):
        self.t = 0
        self.root = Tk()
        self.root.title('Vexing Video')
        self.imgs = []
        self.array = []
        self.on_init()
        self.on_loop()
        self.root.mainloop()
        return
    def on_init(self):
        self.imgs = [[i[0], ImageTk.PhotoImage(Image.open(i[1]))] for i in frames]
        #for i in range(len(frames)):
        #    self.imgs += [ImageTk.PhotoImage(Image.open(frames[i]))]
        self.canvas1 = Canvas(width=654, height=480)
        self.canvas1.pack()
        self.width1 = self.imgs[self.t][1].width()
        self.height1 = self.imgs[self.t][1].height()
        #for r in range(3):
        #    for c in range(3):
        #        if r == 1 and c == 1:
        #            # 654x480
        #            #self.img = ImageTk.PhotoImage(Image.open(frames[self.t]))
        #            #Label(self.root, image=self.img,
        #            #    borderwidth=1).grid(row=r,column=c)
        #        else:
        #            Label(self.root, text='X',
        #                borderwidth=1).grid(row=r,column=c)
        return
    def on_cleanup(self):
        return
    def on_loop(self):
        #self.img = ImageTk.PhotoImage(Image.open(self[self.t][1]))
        #Label(self.root, image=self.imgs[self.t][1],
        #    borderwidth=1).grid(row=1,column=1)
        if self.t % len(frames) == 0:
            self.canvas1.delete("all")
        self.canvas1.create_image(self.width1/2, self.height1/2, image=self.imgs[self.t][1])
        self.t = (self.t + 1) % len(frames)
        self.root.after(UPDATE_RATE, self.on_loop)
        return

def main():
    app = App()
    return

if __name__ == "__main__" :
    main()
    #print(str(frames))

