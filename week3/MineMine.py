import tkinter as tk
from tkinter import messagebox
import random


class GameObject(object):
    def __init__(self, canvas, item):
        self.canvas = canvas
        self.item = item

    def get_postion(self):
        return self.canvas.coords(self.item)

    def delete(self):
        self.canvas.delete(self.item)


class Tile(GameObject):
    def __init__(self, canvas, x, y, number):
        self.number = number
        self.canvas = canvas
        self.size = 10
        self.isOpened = False
        self.isFlagged = False
        item = canvas.create_rectangle(x - self.size, y - self.size, x + self.size, y + self.size, fill='blue',
                                       tag='tile')

        super(Tile, self).__init__(canvas, item)

    def isopen(self):
        return self.isOpened

    def open(self):
        if self.isOpened or self.isFlagged:
            return

        self.isOpened = True
        self.isFlagged = False

        if self.number == 0:
            self.draw(self.number)
        elif self.number > 0:
            self.draw(self.number)
        else:
            self.draw("Bomb")

    def draw(self, symbol):
        if symbol == "Flag":
            self.canvas.itemconfig(self.item, fill='yellow')
        elif symbol == "Bomb":
            self.canvas.itemconfig(self.item, fill='black')
        elif symbol == "Normal":
            self.canvas.itemconfig(self.item, fill='blue')
        else:
            self.canvas.create_text(self.canvas.coords(self.item)[0] + self.size,
                                    self.canvas.coords(self.item)[1] + self.size, text=self.number)
            self.canvas.itemconfig(self.item, fill='white')

    def check(self):
        if not self.isOpened:
            self.isFlagged = not self.isFlagged
            if self.isFlagged:
                self.draw("Flag")
            else:
                self.draw("Normal")

    def add_number(self):
        self.number += 1

    def get_number(self):
        return self.number


class Game(tk.Frame):
    def __init__(self, master):
        super(Game, self).__init__(master)
        self.level = 0
        self.levelsetting = [(9, 9, 10), (16, 16, 40), (16, 30, 99)]
        self.size = 10

        menubar = tk.Menu(master)
        filemenu = tk.Menu(menubar, tearoff=0)
        for i in range(3):
            filemenu.add_command(label="%d*%d" % (self.levelsetting[i][0], self.levelsetting[i][1]), \
                                 command=lambda i=i: self.begin(i))

        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=master.destroy)
        menubar.add_cascade(label="File", menu=filemenu)
        master.config(menu=menubar)

        self.hud = None

        self.width = self.levelsetting[self.level][1] * self.size * 2
        self.height = self.levelsetting[self.level][0] * self.size * 2
        self.canvas = tk.Canvas(self, bg='#aaaaff', width=self.width, height=self.height, )

        self.items = {}
        self.canvas.pack()
        self.pack()

        self.canvas.focus_set()

        self.setup_level()
        self.set_number()

        self.canvas.bind('<Button-1>', self.left_button)
        self.canvas.bind('<Button-3>', self.right_button)

    def begin(self, level):
        self.level = level
        self.items = {}
        self.canvas.destroy()

        self.width = self.levelsetting[self.level][1] * self.size * 2
        self.height = self.levelsetting[self.level][0] * self.size * 2
        self.canvas = tk.Canvas(self, bg='#aaaaff', width=self.width, height=self.height, )
        self.canvas.pack()
        self.pack()
        self.canvas.focus_set()

        self.setup_level()
        self.set_number()
        self.game_loop()

    def left_button(self, event):
        x = event.x
        y = event.y
        tile = self.canvas.find_overlapping(x, y, x, y)
        objects = [self.items[x] for x in tile if x in self.items]
        if len(objects) == 1:
            if objects[0].get_number() == 0:
                self.find_zero(tile[0])
            if objects[0].get_number() == -1:
                for i in range(1, self.levelsetting[self.level][0] * self.levelsetting[self.level][1] + 1):
                    self.items[i].open()
                self.draw_text('Game Over', 'Bomb!')
                return
            objects[0].open()
        self.game_loop()

    def right_button(self, event):
        x = event.x
        y = event.y
        tile = self.canvas.find_overlapping(x, y, x, y)
        objects = [self.items[x] for x in tile if x in self.items]
        if len(objects) == 1:
            objects[0].check()
        self.game_loop()

    def setup_level(self):
        setting = self.levelsetting[self.level]
        bomb = setting[2]
        tot = setting[0] * setting[1]
        for x in range(self.size, self.width, self.size * 2):
            for y in range(self.size, self.height, self.size * 2):
                number = random.random()
                if number > (tot - bomb) / tot:
                    self.add_tile(x, y, -1)
                    bomb -= 1
                else:
                    self.add_tile(x, y, 0)
                tot -= 1

    def add_tile(self, x, y, number):
        tile = Tile(self.canvas, x, y, number)
        self.items[tile.item] = tile

    def game_loop(self):
        left_tiles = len([x for x in self.canvas.find_withtag('tile') if not self.items[x].isopen()])
        if left_tiles == self.levelsetting[self.level][2] - \
                len([x for x in self.canvas.find_withtag('tile') if self.items[x].isopen() if
                     self.items[x].get_number() is -1]):
            for i in range(1, self.levelsetting[self.level][0] * self.levelsetting[self.level][1] + 1):
                self.items[i].open()
            self.draw_text('Win', 'You Win!')

    def draw_text(self, label, text):
        tk.messagebox.showinfo(label, text)

    def find_zero(self, idx):
        if self.items[idx].get_number() is not 0 or self.items[idx].isOpened:
            self.items[idx].open()
            return
        else:
            self.items[idx].open()
        height = self.levelsetting[self.level][0]
        width = self.levelsetting[self.level][1]

        if idx > height:
            if idx - height - 1 > 0 and idx % height is not 1:
                self.find_zero(idx - height - 1)
            self.find_zero(idx - height)
            if idx - height + 1 > 0 and idx % height is not 0:
                self.find_zero(idx - height + 1)

        if idx % height is not 1:
            self.find_zero(idx - 1)

        if idx % height is not 0:
            self.find_zero(idx + 1)

        if idx < height * (width - 1) + 1:
            if idx % height is not 1:
                self.find_zero(idx + height - 1)
            self.find_zero(idx + height)
            if idx % height is not 0:
                self.find_zero(idx + height + 1)

    def set_number(self):
        height = self.levelsetting[self.level][0]
        width = self.levelsetting[self.level][1]

        for idx in range(1, height * width + 1):
            if self.items[idx].get_number() is -1:
                continue
            if idx > height:
                if idx - height - 1 > 0 and idx % height is not 1:
                    if self.items[idx - height - 1].get_number() is -1:
                        self.items[idx].add_number()
                if self.items[idx - height].get_number() is -1:
                    self.items[idx].add_number()
                if idx - height + 1 > 0 and idx % height is not 0:
                    if self.items[idx - height + 1].get_number() is -1:
                        self.items[idx].add_number()

            if idx % height is not 1:
                if self.items[idx - 1].get_number() is -1:
                    self.items[idx].add_number()

            if idx % height is not 0:
                if self.items[idx + 1].get_number() is -1:
                    self.items[idx].add_number()

            if idx < height * (width - 1) + 1:
                if idx % height is not 1:
                    if self.items[idx + height - 1].get_number() is -1:
                        self.items[idx].add_number()
                if self.items[idx + height].get_number() is -1:
                    self.items[idx].add_number()
                if idx % height is not 0:
                    if self.items[idx + height + 1].get_number() is -1:
                        self.items[idx].add_number()


if __name__ == '__main__':
    root = tk.Tk()
    root.title('MineMine')
    game = Game(root)
    game.mainloop()
