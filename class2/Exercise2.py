import tkinter as tk
import random
import math


class GameObject(object):
    def __init__(self, canvas, item):
        self.canvas = canvas
        self.item = item

    def get_position(self):
        return self.canvas.coords(self.item)

    def move(self, x, y):
        self.canvas.move(self.item, x, y)

    def delete(self):
        self.canvas.delete(self.item)


class Ball(GameObject):
    def __init__(self, canvas, x, y):
        self.radius = 10
        self.direction = [1 / math.sqrt(2), -1 / math.sqrt(2)]
        self.speed = 10
        self.dis = 2
        self.ballimage = tk.PhotoImage(file='ball2.png')  # PhotoImage를 멤버변수로 저장하지 않으면 사진이 할당해제되어 이미지가 보이지 않음
        image = canvas.create_image(x, y, anchor=tk.CENTER, image=self.ballimage)
        super(Ball, self).__init__(canvas, image)

    def update(self):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] <= 0 or coords[2] >= width:  # coord[0] : left  , [2] : right
            self.direction[0] *= -1
        if coords[1] <= 0:  # coord[1] : top,  , [4] : bottom
            self.direction[1] *= -1
        x = self.direction[0] * self.speed
        y = self.direction[1] * self.speed
        self.move(x, y)

    def rotate_vector(self, vector, radian):
        cos = 0  # math.cos(radian) math.cos(pi/2)가 0이 안나옴
        sin = math.sin(radian)
        vx = vector[0] * cos - vector[1] * sin
        vy = vector[0] * sin + vector[1] * cos
        return (vx, vy)

    def normalize(self, v):
        magnitude = math.sqrt(v[0] ** 2 + v[1] ** 2)
        return (v[0] / magnitude, v[1] / magnitude)

    def inner_product(self, v1, v2):  # Only two elements
        return v1[0] * v2[0] + v1[1] * v2[1]

    def get_reflection(self, n, v):
        mat = (-2 * (n[0] ** 2 - (1 / 2)), -2 * n[0] * n[1]), (-2 * n[0] * n[1], -2 * (n[1] ** 2 - (1 / 2)))
        result = [mat[0][0] * v[0] + mat[0][1] * v[1], mat[1][0] * v[0] + mat[1][1] * v[1]]
        return result

    def collide(self, game_objects):
        dis = 2
        coords = self.get_position()
        x = (coords[0] + coords[2]) * 0.5  # Ball의 중심x좌표
        y = (coords[1] + coords[3]) * 0.5
        if not len(game_objects)==0:
            if len(game_objects) > 1:  # 수정이 필요함, 가로, 세로로 붙어있는 두개의 블럭인 경우만 생각함
                #self.direction[1] *= -1
                coords=game_objects[0].get_position() # width, height, 0 ,0
                for obj in game_objects:
                    ocrd = obj.get_position()
                    if coords[0] > ocrd[0]:
                        coords[0] = ocrd[0]
                    if coords[1] > ocrd[1]:
                        coords[1] = ocrd[1]
                    if coords[2] < ocrd[2]:
                        coords[2] = ocrd[2]
                    if coords[3] < ocrd[3]:
                        coords[3] = ocrd[3]
            else:
                game_object = game_objects[0]
                coords = game_object.get_position()

            bcenter = (x, y)
            collide_coords = (coords[0] - dis, coords[1] - dis, coords[2] + dis, coords[3] + dis)
            collision_points = []
            for i in range(4):
                d = self.radius ** 2 - (
                            collide_coords[i] - bcenter[i % 2]) ** 2  # bcenter[0] if i%2==0 else bcenter[1]))**2
                if d < 0:
                    continue
                p1 = bcenter[1 - i % 2] - math.sqrt(d)  # (bcenter[1] if i%2==0 else bcenter[0]) - math.sqrt(d)
                p2 = bcenter[1 - i % 2] + math.sqrt(d)  # (bcenter[1] if i%2==0 else bcenter[0]) + math.sqrt(d)
                if i == 0 or i == 2:  # left or right then p are y pos
                    if p1 > collide_coords[1] and p1 < collide_coords[3]:
                        collision_points.append((collide_coords[i], p1))
                    if p2 > collide_coords[1] and p2 < collide_coords[3]:
                        collision_points.append((collide_coords[i], p2))
                else:  # top or bottom then p abre x pos
                    if p1 > collide_coords[0] and p1 < collide_coords[2]:
                        collision_points.append((p1, collide_coords[i]))
                    if p2 > collide_coords[0] and p2 < collide_coords[2]:
                        collision_points.append((p2, collide_coords[i]))

            vector = (collision_points[0][0] - collision_points[1][0], collision_points[0][1] - collision_points[1][1])
            n1 = self.rotate_vector(vector, math.pi / 2)
            n2 = (-n1[0], -n1[1])
            vcenter = ((coords[0] + coords[2]) / 2 - (collision_points[0][0] + collision_points[1][0]) / 2, \
                       (coords[1] + coords[3]) / 2 - (collision_points[0][1] + collision_points[1][1]) / 2)

            if self.inner_product(vcenter, n1) < 0:
                n = n1
            else:
                n = n2
            n = self.normalize(n)
            self.direction = self.get_reflection(n, self.direction)

        for game_object in game_objects:
            if isinstance(game_object, Brick):
                game_object.hit()

    def get_position(self):
        center = self.canvas.coords(self.item)
        left = center[0] - self.radius
        right = center[0] + self.radius
        top = center[1] - self.radius
        bottom = center[1] + self.radius
        return [left, top, right, bottom]


class Paddle(GameObject):
    def __init__(self, canvas, x, y):
        self.width = 80
        self.height = 10
        self.ball = None
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill='blue')
        super(Paddle, self).__init__(canvas, item)

    def set_ball(self, ball):
        self.ball = ball

    def move(self, offset):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] + offset >= 0 and coords[2] + offset <= width:
            super(Paddle, self).move(offset, 0)
            if self.ball is not None:
                self.ball.move(offset, 0)


class Brick(GameObject):
    COLORS = {1: '#999999', 2: '#555555', 3: '#222222'}

    def __init__(self, canvas, x, y, hits):
        self.width = 75
        self.height = 20
        self.hits = hits
        color = Brick.COLORS[hits]
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill=color, tags='brick')
        super(Brick, self).__init__(canvas, item)

    def hit(self):
        self.hits -= 1
        if self.hits == 0:
            self.delete()
        else:
            self.canvas.itemconfig(self.item,
                                   fill=Brick.COLORS[self.hits])


class Game(tk.Frame):

    def __init__(self, master):
        super(Game, self).__init__(master)
        self.level = 1
        self.lives = 3
        self.width = 610
        self.height = 400
        self.canvas = tk.Canvas(self, bg='#aaaaff',
                                width=self.width,
                                height=self.height, )
        self.canvas.pack()
        self.pack()

        self.hits = ((1, 0, 0), (1, 1, 0), (1, 1, 1), (2, 1, 1), (2, 2, 1), (2, 2, 2))
        self.items = {}
        self.ball = None
        self.paddle = Paddle(self.canvas, self.width / 2, 326)
        self.items[self.paddle.item] = self.paddle
        self.setup_level()

        self.hud = None
        self.setup_game()
        self.canvas.focus_set()
        self.canvas.bind('<Left>',
                         lambda _: self.paddle.move(-10))
        # F4 = lambda _: F(50) _는 매개변수를 받지만 사용하지는 않음
        self.canvas.bind('<Right>',
                         lambda _: self.paddle.move(10))

    def setup_level(self):
        for x in range(5, self.width - 5, 75):
            if random.randint(0, 9) < 2 + self.level:
                self.add_brick(x + 37.5, 50, self.hits[self.level - 1][0])
            if random.randint(0, 9) < 2 + self.level:
                self.add_brick(x + 37.5, 70, self.hits[self.level - 1][1])
            if random.randint(0, 9) < 2 + self.level:
                self.add_brick(x + 37.5, 90, self.hits[self.level - 1][2])

    def setup_game(self):
        self.add_ball()
        self.update_lives_text()
        if self.lives == 3:
            self.setup_level()
        self.text = self.draw_text(300, 200,
                                   'Press Space to start')
        self.canvas.bind('<space>', lambda _: self.start_game())

    def add_ball(self):
        if self.ball is not None:
            self.ball.delete()
        paddle_coords = self.paddle.get_position()
        x = (paddle_coords[0] + paddle_coords[2]) * 0.5
        self.ball = Ball(self.canvas, x, 310)
        self.paddle.set_ball(self.ball)

    def add_brick(self, x, y, hits):
        if hits != 0:
            brick = Brick(self.canvas, x, y, hits)
            self.items[brick.item] = brick

    def draw_text(self, x, y, text, size='40'):
        font = ('Helvetica', size)
        return self.canvas.create_text(x, y, text=text,
                                       font=font)

    def update_lives_text(self):
        text = 'Lives: %s Level: %d Blocks left %d' % (self.lives, self.level, len(self.canvas.find_withtag('brick')))
        if self.hud is None:
            self.hud = self.draw_text(90, 20, text, 15)
        else:
            self.canvas.itemconfig(self.hud, text=text)

    def start_game(self):
        self.canvas.unbind('<space>')
        self.canvas.delete(self.text)
        self.paddle.ball = None
        self.game_loop()

    def game_loop(self):
        self.check_collisions()
        num_bricks = len(self.canvas.find_withtag('brick'))
        self.update_lives_text()
        if num_bricks == 0:
            self.ball.speed = None
            if self.level >= 5:
                self.draw_text(300, 200, 'You win!')
            else:
                self.level += 1
                self.lives = 3
                self.setup_game()

        elif self.ball.get_position()[3] >= self.height:
            self.ball.speed = None
            self.lives -= 1
            if self.lives < 0:
                self.draw_text(300, 200, 'Game Over')
            else:
                self.after(1000, self.setup_game)
        else:
            self.ball.update()
            self.after(50, self.game_loop)

    def check_collisions(self):
        ball_coords = self.ball.get_position()
        items = self.canvas.find_overlapping(*ball_coords)
        objects = [self.items[x] for x in items if x in self.items]
        self.ball.collide(objects)


if __name__ == '__main__':
    root = tk.Tk()
    root.title('Hello, Pong!')
    game = Game(root)
    game.mainloop()
