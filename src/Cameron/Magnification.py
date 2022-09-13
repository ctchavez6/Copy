import PIL.Image
from PIL import ImageTk as ImageTk, Image
from tkinter import *
import tkinter as tk


class ExampleApp(Frame):
    def __init__(self,master):
        Frame.__init__(self,master=None)
        self.x = self.y = 0
        self.canvas = Canvas(self,  cursor="cross",height = 500, width = 800)

        self.sbarv=Scrollbar(self,orient=VERTICAL)
        self.sbarh=Scrollbar(self,orient=HORIZONTAL)
        self.sbarv.config(command=self.canvas.yview)
        self.sbarh.config(command=self.canvas.xview)

        self.canvas.config(yscrollcommand=self.sbarv.set)
        self.canvas.config(xscrollcommand=self.sbarh.set)

        self.canvas.grid(row=0,column=0,sticky=N+S+E+W)
        self.sbarv.grid(row=0,column=1,stick=N+S)
        self.sbarh.grid(row=1,column=0,sticky=E+W)

        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

        self.rect = None

        self.start_x = None
        self.start_y = None

        self.im = PIL.Image.open("logo.png")
        self.wazil,self.lard=self.im.size
        self.canvas.config(scrollregion=(0,0,self.wazil,self.lard))
        self.tk_im = ImageTk.PhotoImage(self.im)
        self.canvas.create_image(0,0,anchor="nw",image=self.tk_im)


    def on_button_press(self, event):
        # save mouse drag start position
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)

        # create rectangle if not yet exist
        if not self.rect:
            self.rect = self.canvas.create_rectangle(self.x, self.y, 1, 1, outline='red')

    def on_move_press(self, event):
        curX = self.canvas.canvasx(event.x)
        curY = self.canvas.canvasy(event.y)

        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        if event.x > 0.9*w:
            self.canvas.xview_scroll(1, 'units')
        elif event.x < 0.1*w:
            self.canvas.xview_scroll(-1, 'units')
        if event.y > 0.9*h:
            self.canvas.yview_scroll(1, 'units')
        elif event.y < 0.1*h:
            self.canvas.yview_scroll(-1, 'units')

        # expand rectangle as you drag the mouse
        self.canvas.coords(self.rect, self.start_x, self.start_y, curX, curY)

    def on_button_release(self, event):
        pass

if __name__ == "__main__":
    root= tk.Tk()
    app = ExampleApp(root)
    app.pack()
    root.mainloop()

# import tkinter
#
# # init tk
# root = tkinter.Tk()
#
# # create canvas
# myCanvas = tkinter.Canvas(root, bg="white", height=300, width=300)
#
# # draw arcs
# coord = 10, 10, 300, 300
# arc = myCanvas.create_arc(coord, start=0, extent=150, fill="red")
# arv2 = myCanvas.create_arc(coord, start=150, extent=215, fill="green")
#
# # add to window and show
# myCanvas.pack()
# root.mainloop()
#
#
#
# def get_absolute_position(event):
#     x = event.x
#     y = event.y
#     return x, y