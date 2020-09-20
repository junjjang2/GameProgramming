import tkinter as tk

class Game(tk.Frame):
    def __init__(self, master):
        # Frame(Master, option, ...) if need
        super(Game, self).__init__(master)
        self.lives = 3
        self.width = 610
        self.heigh = 400
        self.canvas = tk.Canvas(self, bg='#aaaaff', width=self.width, height=self.height)

        self.canvas.pack()
        self.pack()

        
