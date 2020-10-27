import random

from enum import Enum

from collections import defaultdict

from pyglet.image import load, ImageGrid, Animation
from pyglet.window import key

import cocos.layer
import cocos.sprite
import cocos.collision_model as cm
import cocos.euclid as eu


class GameObject(cocos.sprite.Sprite):
    def __init__(self, image, x, y):
        super(GameObject, self).__init__(image)
        self.position = eu.Vector2(x, y)
        self.cshape = cm.AARectShape(self.position,
                                     self.width * 0.5,
                                     self.height * 0.5)

    def update(self, elapsed):
        pass

    def collide(self, other):
        pass


class AbilityBox(GameObject):
    class TYPE(Enum):
        SPEED = 1
        SHOOT_SPEED = 2
        MAX_LIVES = 3
        ADDITIONAL_SHOT = 4
        DAMAGE_UP = 5
        SHOT_LATENCY = 6

    AbilityType = {
        TYPE.SPEED: 'img/speed.png',
        TYPE.SHOOT_SPEED: 'img/shot_speed.png',
        TYPE.MAX_LIVES: 'img/max_lives.png',
        TYPE.ADDITIONAL_SHOT: 'img/additional_shot.png',
        TYPE.DAMAGE_UP: 'img/damage_up.png',
        TYPE.SHOT_LATENCY: 'img/shot_latency.png'
    }

    CHOICE = None

    def __init__(self, abil_type, x, y):
        super(AbilityBox, self).__init__(AbilityBox.AbilityType[abil_type], x, y)
        self.type = abil_type

    def on_exit(self):
        AbilityBox.CHOICE = self.type
        super(AbilityBox, self).on_exit()


class Actor(GameObject):
    def move(self, offset):
        self.position += offset
        self.cshape.center += offset


class PlayerCannon(Actor):
    KEYS_PRESSED = defaultdict(int)
    speed = eu.Vector2(200, 0)
    isValid = False
    number = 1

    def __init__(self, x, y):
        self.sta = ImageGrid(load("img/cannon.png"), 2, 1)
        super(PlayerCannon, self).__init__(Animation.from_image_sequence(self.sta[1:], 0, loop=False), x, y)
        self.shootdelay = 0.0
        self.shootperiod = 1.0
        self.shootpersecond = 1

    def increase_sps(self):
        self.shootpersecond+=1
        self.shootperiod= 1.0/self.shootpersecond

    def validate(self):
        PlayerCannon.isValid = True
        self.image = Animation.from_image_sequence(self.sta[1:], 0, loop=False)
        pass

    def invalidate(self):
        PlayerCannon.isValid = False
        self.image = Animation.from_image_sequence(self.sta[0:], 0, loop=False)

    def update(self, elapsed):
        pressed = PlayerCannon.KEYS_PRESSED
        if self.isValid:
            space_pressed = pressed[key.SPACE] == 1
            self.shootdelay += elapsed
            if self.shootdelay > self.shootperiod and space_pressed:
                self.shootdelay = 0
                for i in range(PlayerCannon.number):
                    self.parent.add(PlayerShoot(self.x-30 + 2*30*(i+1)/(PlayerCannon.number+1), self.y + 50))
        else:
            if PlayerCannon.KEYS_PRESSED[key.SPACE] == 1:
                self.validate()
        movement = pressed[key.RIGHT] - pressed[key.LEFT]
        w = self.width * 0.5
        if movement != 0 and w <= self.x <= self.parent.width - w:
            if self.x + PlayerCannon.speed[0] * movement * elapsed < w:
                self.position = eu.Vector2(w, self.position[1])
            elif self.x + PlayerCannon.speed[0] * movement * elapsed > self.parent.width - w:
                self.position = eu.Vector2(self.parent.width - w, self.position[1])
            else:
                self.move(PlayerCannon.speed * movement * elapsed)

    def collide(self, other):
        other.kill()


class GameLayer(cocos.layer.Layer):
    is_event_handler = True

    def on_key_press(self, k, _):
        PlayerCannon.KEYS_PRESSED[k] = 1

    def on_key_release(self, k, _):
        PlayerCannon.KEYS_PRESSED[k] = 0

    def __init__(self, hud):
        super(GameLayer, self).__init__()
        w, h = cocos.director.director.get_window_size()
        self.hud = hud
        self.width = w
        self.height = h
        self.max_lives = 3
        self.score = 0
        self.level = 5
        self.ability_boxes = []
        self.create_player()
        self.player.validate()
        self.update_level(self.level)
        cell = 1.25 * 50
        self.collman = cm.CollisionManagerGrid(0, w, 0, h,
                                               cell, cell)
        self.schedule(self.update)

    def update_level(self, level):
        self.lives = self.max_lives
        self.update_score()
        self.hud.update_lives(self.lives)
        self.hud.update_level(self.level)
        if level % 5 == 0:
            self.create_boss(level)
        else:
            self.create_alien_group(100, 300)
            if level > 5:
                self.alien_group.set_period(0.2)
            else:
                self.alien_group.set_period(1.2 - level * 0.2) # 1 - (level -1) * 0.2

    def create_boss(self, level):
        self.boss = AlienBoss(level, 400, 500)
        self.add(self.boss)

    def create_player(self):
        self.player = PlayerCannon(self.width * 0.5, 50)
        self.add(self.player)

    def update_score(self, score=0):
        self.score += score
        self.hud.update_score(self.score)

    def select_ability(self):
        if len(self.ability_boxes) == 0:
            self.hud.show_ability()
            self.clear_shoot()
            if self.level % 5 == 0:
                self.ability_boxes = [AbilityBox(AbilityBox.TYPE.ADDITIONAL_SHOT, 300, 400),
                                      AbilityBox(AbilityBox.TYPE.SHOT_LATENCY, 500, 400)]
            else:
                self.ability_boxes = [AbilityBox(AbilityBox.TYPE.SPEED, 200, 400), AbilityBox(AbilityBox.TYPE.SHOOT_SPEED, 400, 400),
                                  AbilityBox(AbilityBox.TYPE.MAX_LIVES, 600, 400)]

            for i in self.ability_boxes:
                self.add(i)
        else:
            if AbilityBox.CHOICE is not None:
                if AbilityBox.CHOICE is AbilityBox.TYPE.SPEED:
                    PlayerCannon.speed += eu.Vector2(100, 0)
                elif AbilityBox.CHOICE is AbilityBox.TYPE.SHOOT_SPEED:
                    PlayerShoot.speed += 50
                elif AbilityBox.CHOICE is AbilityBox.TYPE.MAX_LIVES:
                    self.max_lives += 1
                elif AbilityBox.CHOICE is AbilityBox.TYPE.ADDITIONAL_SHOT:
                    PlayerCannon.number += 1
                elif AbilityBox.CHOICE is AbilityBox.TYPE.DAMAGE_UP:
                    PlayerCannon.damage += 1
                elif AbilityBox.CHOICE is AbilityBox.TYPE.SHOT_LATENCY:
                    self.player.increase_sps()

                for i in self.ability_boxes:
                    for _, node in self.children:
                        if i is node:
                            i.kill()
                self.ability_boxes = []
                AbilityBox.CHOICE = None

    def create_alien_group(self, x, y):
        self.alien_group = AlienGroup(x, y)
        for alien in self.alien_group:
            self.add(alien)

    def clear_shoot(self):
        for _, node in self.children:
            if isinstance(node, Shoot):
                self.remove(node)

    def update(self, dt):
        # collision check
        self.collman.clear()
        for _, node in self.children:
            self.collman.add(node)
            if not self.collman.knows(node):
                self.remove(node)
        for shoot in PlayerShoot.INSTANCES:
            self.collide(shoot)

        def new_stage():
            if len(self.ability_boxes) == 0:
                self.hud.close_ability()
                self.clear_shoot()
                self.level += 1
                self.update_level(self.level)
        # when stage ended
        if self.level % 5 == 0:
            if self.boss.lives == 0:
                self.select_ability()
                new_stage()
            #when boss stage is on
            else:
                if self.player.isValid and self.collide(self.player):
                    self.respawn_player()
                for shoot in self.boss.shoot(dt):
                    self.add(shoot)
                self.boss.update(dt)
        else:
            if len(self.alien_group) == 0:  # if sum(len(column.aliens) for column in self.alien_group.columns) == 0:
                self.select_ability()
                new_stage()
            # when normal stage is on
            else:
                if self.player.isValid and self.collide(self.player):
                    self.respawn_player()
                for column in self.alien_group.columns:
                    shoot = column.shoot()
                    if shoot is not None:
                        self.add(shoot)
                self.alien_group.update(dt)
                if random.random() < 0.001:
                    self.add(MysteryShip(50, self.height - 50))

        for _, node in self.children:
            node.update(dt)

    def collide(self, node):
        if node is not None:
            for other in self.collman.iter_colliding(node):
                node.collide(other)
                return True
        return False

    def respawn_player(self):
        self.lives -= 1
        if self.lives < 0:
            self.unschedule(self.update)
            self.remove(self.player)
            self.hud.show_game_over()
        else:
            self.hud.update_lives(self.lives)
            self.player.invalidate()


class Alien(Actor):
    def load_animation(image):
        seq = ImageGrid(load(image), 2, 1)
        return Animation.from_image_sequence(seq, 0.5)

    TYPES = {
        '1': (load_animation('img/alien1.png'), 40),
        '2': (load_animation('img/alien2.png'), 20),
        '3': (load_animation('img/alien3.png'), 10)
    }

    @staticmethod
    def from_type(x, y, alien_type, column):
        animation, score = Alien.TYPES[alien_type]
        return Alien(animation, x, y, score, column)

    def __init__(self, img, x, y, score, column=None):
        super(Alien, self).__init__(img, x, y)
        self.score = score
        self.column = column

    def collide(self):
        self.kill()

    def on_exit(self):
        super(Alien, self).on_exit()
        if self.column:
            self.column.remove(self)


class AlienBoss(Actor):
    class Direction:
        def __init__(self, x, y):
            self.x = x
            self.y = y

        def __add__(self, other):
            result = AlienBoss.Direction(self.x + other.x, self.y + other.y)
            return result

        def __sub__(self, other):
            result = AlienBoss.Direction(self.x - other.x, self.y - other.y)
            return result

        def __mul__(self, other):
            if isinstance(other, int) or isinstance(other, float):
                result = AlienBoss.Direction(self.x * other, self.y * other)
                return result
            elif isinstance(other, AlienBoss.Direction):
                result = AlienBoss.Direction(self.x * other.x, self.y * other.y)
                return result

        def __radd__(self, other):
            result = AlienBoss.Direction(self.x + other.x, self.y + other.y)
            return result

        def __rsub__(self, other):
            result = AlienBoss.Direction(self.x - other.x, self.y - other.y)
            return result

        def __rmul__(self, other):
            if isinstance(other, int) or isinstance(other, float):
                result = AlienBoss.Direction(self.x * other, self.y * other)
                return result
            elif isinstance(other, AlienBoss.Direction):
                result = AlienBoss.Direction(self.x * other.x, self.y * other.y)
                return result

        def __str__(self):
            return "%d %d" % (self.x, self.y)

        def get_x(self):
            return self.x

        def get_y(self):
            return self.y


    def load_animation(image):
        seq = ImageGrid(load(image), 2, 1)
        return Animation.from_image_sequence(seq, 0.5)

    TYPES = {
        1: (load_animation('img/alien_boss1.png'), 100),
        2: (load_animation('img/alien_boss2.png'), 200),
        3: (load_animation('img/alien_boss3.png'), 400)
    }

    def __init__(self, level, x, y):
        super(AlienBoss, self).__init__(AlienBoss.TYPES[(level // 5 - 1) % 3 + 1][0], x, y)
        self.score = AlienBoss.TYPES[level % 3 + 1][1] * level // 5
        self.time = 0
        self.phase = 0
        self.max_lives = 3 * (level // 5)
        self.lives = self.max_lives

    def on_hit(self):
        self.lives -= 1
        if self.lives == 0:
            self.parent.update_score(self.score)
            self.kill()

    def shoot(self, elapsed):
        l = AlienBoss.Direction(-1, 0)
        r = AlienBoss.Direction(1, 0)
        d = AlienBoss.Direction(0, -1)
        u = AlienBoss.Direction(0, 1)
        #print(l + 2*d)
        self.time += elapsed
                    # phase 1
        patterns = [((1.0, (d, )),
                     (0.3, (l, l + 2*d, d, r + 2*d, r)),
                     (0.3, (l, l + 2*d, d, r + 2*d, r)),
                     (0.3, (l, l + 2*d, d, r + 2*d, r))),
                    # phase 2
                    ((1.0, (d, )),
                     (0.2, (l, l + 2*d, d, r + 2*d, r)),
                     (0.1, (l + 2*d, r + 2*d)),
                     (0.2, (l, l + 2*d, d, r + 2*d, r)),
                     (0.1, (l + 2*d, r + 2*d)),
                     (0.2, (l, l + 2*d, d, r + 2*d, r)),
                     (0.1, (l + 2*d, r + 2*d))),
                    # phase 3
                    ((1.0, (d, )),
                     (0.2, (l, l + 2*d, d, r + 2*d, r)),
                     (0.1, (l + 2*d, l + 3*d, d, r + 3*d, r + 2*d)),
                     (0.2, (l, l + 2*d, d, r + 2*d, r)),
                     (0.1, (l + 2*d, l + 3*d, d, r + 3*d, r + 2*d)),
                     (0.2, (l, l + 2*d, d, r + 2*d, r)),
                     (0.1, (l + 2*d, l + 3*d, d, r + 3*d, r + 2*d)))]

        shoot_list = []
        delay, shoot_dir = patterns[3 - int(3*self.lives/self.max_lives)][self.phase]
        #print(self.max_lives, self.lives, 3 - int(3*self.lives/self.max_lives))
        if self.time > delay:
            self.time -= delay
            for dir in shoot_dir:
                shoot_list.append(Shoot(self.x, self.y, velocity=eu.Vector2(dir.get_x(), dir.get_y())))
            self.phase = (self.phase+1) % 4
        return shoot_list


class AlienColumn(object):
    def __init__(self, x, y):
        alien_types = enumerate(['3', '3', '2', '2', '1'])
        self.aliens = [Alien.from_type(x, y + i * 60, alien, self)
                       for i, alien in alien_types]

    def should_turn(self, d):
        if len(self.aliens) == 0:
            return False
        alien = self.aliens[0]
        x, width = alien.x, alien.parent.width
        return x >= width - 50 and d == 1 or x <= 50 and d == -1

    def remove(self, alien):
        self.aliens.remove(alien)

    def shoot(self):
        if random.random() < 0.001 and len(self.aliens) > 0:
            pos = self.aliens[0].position
            return Shoot(pos[0], pos[1] - 50)
        return None

    def __len__(self):
        return len(self.aliens)


class AlienGroup(object):
    def __init__(self, x, y):
        self.columns = [AlienColumn(x + i * 60, y) for i in range(10)]
        self.speed = eu.Vector2(10, 0)
        self.direction = 1
        self.elapsed = 0.0
        self.period = 1.0

    def update(self, elapsed):
        self.elapsed += elapsed
        while self.elapsed >= self.period:
            self.elapsed -= self.period
            offset = self.direction * self.speed
            if self.side_reached():
                self.direction *= -1
                offset = eu.Vector2(0, -10)
            for alien in self:
                alien.move(offset)

    def set_period(self, period):
        self.period = period

    def side_reached(self):
        return any(map(lambda c: c.should_turn(self.direction),
                       self.columns))

    def __iter__(self):
        for column in self.columns:
            for alien in column.aliens:
                yield alien

    def __len__(self):
        return sum(len(column) for column in self.columns)


class Shoot(Actor):
    def __init__(self, x, y, img='img/shoot.png', velocity=eu.Vector2(0, -1)):
        super(Shoot, self).__init__(img, x, y)
        self.speed = 400
        self.velocity = velocity
        self.movement = self.speed * self.velocity

    def set_velocity(self, v):
        self.velocity = v
        self.movement = self.speed * self.velocity

    def set_speed(self, speed):
        self.speed = speed
        self.movement = self.speed * self.velocity

    def update(self, elapsed):
        self.move(self.movement * elapsed)


class PlayerShoot(Shoot):
    INSTANCES = []
    damage = 1
    speed = 400

    def __init__(self, x, y):
        super(PlayerShoot, self).__init__(x, y, 'img/laser.png')
        self.set_speed(PlayerShoot.speed)
        self.set_speed(self.speed * -1)
        PlayerShoot.INSTANCES.append(self)

    def collide(self, other):
        try:
            if isinstance(other, Alien):
                self.parent.update_score(other.score)
                other.kill()
                self.kill()
            if isinstance(other, AbilityBox):
                other.kill()
                self.kill()
            if isinstance(other, AlienBoss):
                other.on_hit()
                self.kill()
        except:
            pass

    def on_exit(self):
        super(PlayerShoot, self).on_exit()
        PlayerShoot.INSTANCES.remove(self)

class HUD(cocos.layer.Layer):
    def __init__(self):
        super(HUD, self).__init__()
        w, h = cocos.director.director.get_window_size()
        self.score_text = cocos.text.Label('', font_size=18)
        self.score_text.position = (140, h - 40)
        self.lives_text = cocos.text.Label('', font_size=18)
        self.lives_text.position = (w - 100, h - 40)
        self.level_text = cocos.text.Label('', font_size=18)
        self.level_text.position = (20, h - 40)
        self.add(self.score_text)
        self.add(self.lives_text)
        self.add(self.level_text)

    def update_score(self, score):
        self.score_text.element.text = 'Score: %s' % score

    def update_lives(self, lives):
        self.lives_text.element.text = 'Lives: %s' % lives

    def update_level(self, level):
        self.level_text.element.text = 'Level: %s' % level

    def show_ability(self):
        self.abil_text = cocos.text.Label('Shoot one of Abilities to Take', font_size=18)
        self.abil_text.position = (230, 500)
        self.add(self.abil_text)

    def close_ability(self):
        self.remove(self.abil_text)

    def show_game_over(self):
        w, h = cocos.director.director.get_window_size()
        game_over = cocos.text.Label('Game Over', font_size=50,
                                     anchor_x='center',
                                     anchor_y='center')
        game_over.position = w * 0.5, h * 0.5
        self.add(game_over)


class MysteryShip(Alien):
    SCORES = [10, 50, 100, 200]

    def __init__(self, x, y):
        score = random.choice(MysteryShip.SCORES)
        super(MysteryShip, self).__init__('img/alien4.png', x, y,
                                          score)
        self.speed = eu.Vector2(150, 0)

    def update(self, elapsed):
        self.move(self.speed * elapsed)


if __name__ == '__main__':
    cocos.director.director.init(caption='Cocos Invaders',
                                 width=800, height=650)
    main_scene = cocos.scene.Scene()
    hud_layer = HUD()
    main_scene.add(hud_layer, z=1)
    game_layer = GameLayer(hud_layer)
    main_scene.add(game_layer, z=0)
    cocos.director.director.run(main_scene)
