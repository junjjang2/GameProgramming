# tkinter Python interface to Tcl/Tk
# Tk : widget toolkit
# Tcl : script language
# tkinter.Tk() : toplevel widget
# Tk().mainloop() : starting the event loop

import tkinter as tk
nW = 600
nH = 400
# Tk setup
root = tk.Tk()
frame = tk.Frame(root)
canvas = tk.Canvas(frame, width=nW, height=nH, bg='#aaaaff')
# Canvas (master, option = value, ...)
# #ff0000 -> red
root.title('Hello, Pong!')

#Implement of yk canvas
coord = (10, 50, nW-10, nH-50)
arc = canvas.create_arc(coord, start=0, extent=270, fill='red')
#Bounding Box : 아크를 포함하는 직사각형 left-top, right-bottom 방식으로 표현
filename = tk.PhotoImage(file='ball.png')
Image = canvas.create_image(97, 97, anchor=tk.CENTER, image=filename)
# anchor : NW, N ,NE, W, CENTER, E, SW, S, SE
text = canvas.create_text(0, 0, text='Ball', anchor=tk.NW, font=('Arial', '32'))
frame.pack()
canvas.pack()
#

root.mainloop()

# Frame : container widget to organize other widgets
# Canvas : widget for drawing shapes
# Color : RGB (2byte(16bit) per each color
#         (0, 0, 0) = BLACK
#         (255,255,255) = WHITE
