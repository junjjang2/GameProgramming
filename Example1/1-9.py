class Object:
    color = "white"

    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color

    def printlocation(self):
        print("x = %d, y = %d" % (self.x, self.y))


class Ball(Object):

    def __init__(self, x, y, color, radius):
        super(Ball, self).__init__(x, y, color)
        self.radius = radius

    def print(self):
        print(self.x, self.y, self.color, self. radius)

    def move(self, x, y):
        self.x += x
        self.y += y


b = Ball(10, 20, "Black", 25)
b.print()
b.printlocation()
b.move(5, 2)
b.print()