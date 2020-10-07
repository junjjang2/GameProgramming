import cocos
import cocos.collision_model as cm
import cocos.euclid as eu
import random
import math

from collections import defaultdict
from pyglet.window import key


class Actor(cocos.sprite.Sprite):
    def __init__(self, x, y, color):
        super(Actor, self).__init__('ball.png', color=color)
        self.position = pos = eu.Vector2(x, y)
        self.cshape = cm.CircleShape(pos, self.width/2)
        self.velocity = self.normalization((random.uniform(-1, 1), random.uniform(-1, 1)))
        self.speed = 300.0

    def change_speed(self, s):
        self.speed = s

    def change_velocity(self, v):
        v = self.normalization(v)
        self.velocity = v

    def normalization(self, v):
        if v[0] is not 0 or v[1] is not 0:
            magnitude = math.sqrt(v[0]**2 + v[1]**2)
            v = (v[0]/magnitude, v[1]/magnitude)
            return v
        return (0, 0)

    def move(self, dt):
        pos = self.position
        new_x = pos[0] + self.speed * self.velocity[0] * dt
        new_y = pos[1] + self.speed * self.velocity[1] * dt
        self.position = (new_x, new_y)
        self.cshape.center = eu.Vector2(self.position[0], self.position[1])


class MainLayer(cocos.layer.Layer):
    is_event_handler = True

    def __init__(self):
        super(MainLayer, self).__init__()
        self.player = Actor(320, 240, (0, 0, 255))
        self.player.change_velocity((0, 0))
        self.add(self.player)
        for pos in [(100, 100), (540, 380), (540, 100), (100, 380)]:
            self.add(Actor(pos[0], pos[1], (255, 0, 0)))

        cell = self.player.width * 1.25
        self.collman = cm.CollisionManagerGrid(0, 640, 0, 480,
                                               cell, cell)
        self.pressed = defaultdict(int)
        self.schedule(self.update)

    def on_key_press(self, k, m):
        self.pressed[k] = 1

    def on_key_release(self, k, m):
        self.pressed[k] = 0

    def update(self, dt):
        self.collman.clear()
        for _, node in self.children:
            self.collman.add(node)
        for other in self.collman.iter_colliding(self.player):
            self.remove(other)
            pos = random.choice([(320, 0), (320, 480), (0, 240), (680, 240)])
            npc = Actor(pos[0], pos[1], (255, 0, 0))
            npc.change_speed(random.randint(200, 300))
            self.add(npc)

        x = self.pressed[key.RIGHT] - self.pressed[key.LEFT]
        y = self.pressed[key.UP] - self.pressed[key.DOWN]
        self.player.change_velocity((x, y))

        for _, node in self.children:
            node.move(dt)
            node.change_velocity((node.velocity[0]+random.uniform(-0.1, 0.1), node.velocity[1]+random.uniform(-0.1, 0.1)))
            if node.position[0] < 0:
                node.position = (640, node.position[1])
            if node.position[0] > 640:
                node.position = (0, node.position[1])
            if node.position[1] < 0:
                node.position = (node.position[0], 480)
            if node.position[1] > 480:
                node.position = (node.position[0], 0)


if __name__ == '__main__':
    cocos.director.director.init(caption='Hello, Cocos')
    layer = MainLayer()
    scene = cocos.scene.Scene(layer)
    cocos.director.director.run(scene)
