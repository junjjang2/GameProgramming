import random

from collections import defaultdict

from pyglet.image import load, ImageGrid, Animation
from pyglet.window import key

import cocos.layer
import cocos.sprite
import cocos.collision_model as cm
import cocos.euclid as eu


class Object(cocos.sprite.Sprite):
    def __init__(self, image, x, y):

        super(Object, self).__init__(image)
        self.position = eu.Vector2(x, y)
        self.cshape = cm.AARectShape(self.position,
                                     self.width * 0.5,
                                     self.height * 0.5)

    def update(self, elapsed):
        pass

    def collide(self, other):
        pass


class AbilityBox(Object):
    #Todo: AbilityType에서 각 keyword를 열거형으로 바꾸기
    #Todo: 5스테이지 당 보스 출현
    #Todo: 레벨당 얻을 수 있는 Ability 수 증가
    #Todo: 적의 패턴 다양화

    AbilityType = {
        'speed': 'img/speed.png',
        'shot_speed': 'img/shot_speed.png',
        'max_lives': 'img/max_lives.png'
    }
    CHOICE = None

    def __init__(self, abil_type, x, y):
        super(AbilityBox, self).__init__(AbilityBox.AbilityType[abil_type], x, y)
        self.type = abil_type

    def on_exit(self):
        AbilityBox.CHOICE = self.type
        super(AbilityBox, self).on_exit()


class Actor(cocos.sprite.Sprite):
    def __init__(self, image, x, y):
        super(Actor, self).__init__(image)
        self.position = eu.Vector2(x, y)
        self.cshape = cm.AARectShape(self.position,
                                     self.width * 0.5,
                                     self.height * 0.5)

    def move(self, offset):
        self.position += offset
        self.cshape.center += offset

    def update(self, elapsed):
        pass

    def collide(self, other):
        pass


class PlayerCannon(Actor):
    KEYS_PRESSED = defaultdict(int)
    speed = eu.Vector2(200, 0)
    shootperiod = 1.0

    def __init__(self, x, y):
        super(PlayerCannon, self).__init__('img/cannon.png', x, y)
        self.shootdelay = 0.0

    def update(self, elapsed):
        pressed = PlayerCannon.KEYS_PRESSED
        space_pressed = pressed[key.SPACE] == 1
        #if PlayerShoot.INSTANCE is None and space_pressed:
        self.shootdelay += elapsed
        #print(self.position)
        if self.shootdelay > PlayerCannon.shootperiod and space_pressed:
            self.shootdelay = 0
            self.parent.add(PlayerShoot(self.x, self.y + 50))
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
        self.kill()


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
        self.level = 1
        self.ability_boxes = []
        self.create_player()
        self.update_level(self.level)
        '''
        self.lives = 3

        self.update_score()
        self.create_alien_group(100, 300)
        cell = 1.25 * 50
        self.collman = cm.CollisionManagerGrid(0, w, 0, h,
                                               cell, cell)
        '''
        cell = 1.25 * 50
        self.collman = cm.CollisionManagerGrid(0, w, 0, h,
                                               cell, cell)
        self.schedule(self.update)

    def update_level(self, level):
        self.lives = self.max_lives
        self.update_score()
        self.hud.update_lives(self.lives)
        self.hud.update_level(self.level)
        self.create_alien_group(100, 300)
        if level > 5:
            self.alien_group.set_period(0.2)
        else:
            self.alien_group.set_period(1.0-(level-1)*0.2)

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
            self.ability_boxes = [AbilityBox('speed', 200, 400), AbilityBox('shot_speed', 400, 400), AbilityBox('max_lives', 600, 400)]
            for i in self.ability_boxes:
                self.add(i)
        else:
            if AbilityBox.CHOICE is not None:
                if AbilityBox.CHOICE is 'speed':
                    PlayerCannon.speed += eu.Vector2(100, 0)
                elif AbilityBox.CHOICE is 'shot_speed':
                    PlayerCannon.shootperiod -= 0.1
                elif AbilityBox.CHOICE is 'max_lives':
                    self.max_lives += 1
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
                node.kill()

    def update(self, dt):
        self.collman.clear()
        for _, node in self.children:
            self.collman.add(node)
            if not self.collman.knows(node):
                self.remove(node)
        for shoot in PlayerShoot.INSTANCES:
            self.collide(shoot)

        if sum(len(column.aliens) for column in self.alien_group.columns) == 0:
            self.select_ability()
            if len(self.ability_boxes) == 0:
                self.hud.disshow_ability()
                self.clear_shoot()
                self.level += 1
                self.update_level(self.level)
        else:
            if self.collide(self.player):
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
            self.hud.show_game_over()
        else:
            self.create_player()


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

    def on_exit(self):
        super(Alien, self).on_exit()
        if self.column:
            self.column.remove(self)


class AlienColumn(object):
    def __init__(self, x, y):
        alien_types = enumerate(['3', '3', '2', '2', '1'])
        self.aliens = [Alien.from_type(x, y+60, '1', self)]
        #self.aliens = [Alien.from_type(x, y+i*60, alien, self)
                       #for i, alien in alien_types]

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


class AlienGroup(object):
    def __init__(self, x, y):
        self.columns = [AlienColumn(x + 1 * 60, y)]
                        #for i in range(10)]
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


class Shoot(Actor):
    def __init__(self, x, y, img='img/shoot.png'):
        super(Shoot, self).__init__(img, x, y)
        self.speed = eu.Vector2(0, -400)

    def update(self, elapsed):
        self.move(self.speed * elapsed)


class PlayerShoot(Shoot):
    INSTANCES = []
    #INSTANCE = None
    def __init__(self, x, y):
        super(PlayerShoot, self).__init__(x, y, 'img/laser.png')
        self.speed *= -1
        #PlayerShoot.INSTANCE = self
        PlayerShoot.INSTANCES.append(self)

    def collide(self, other):
        if isinstance(other, Alien):
            self.parent.update_score(other.score)
            other.kill()
            self.kill()
        if isinstance(other, AbilityBox):
            other.kill()
            self.kill()

    def on_exit(self):
        super(PlayerShoot, self).on_exit()
        #PlayerShoot.INSTANCE = None
        PlayerShoot.INSTANCES.remove(self)


class HUD(cocos.layer.Layer):
    def __init__(self):
        super(HUD, self).__init__()
        w, h = cocos.director.director.get_window_size()
        self.score_text = cocos.text.Label('', font_size=18)
        self.score_text.position = (120, h - 40)
        self.lives_text = cocos.text.Label('', font_size=18)
        self.lives_text.position = (w - 100, h - 40)
        self.level_text = cocos.text.Label('', font_size=18)
        self.level_text.position = (20, h - 40)#Todo: setlocation(w - 100, h - 40)
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

    def disshow_ability(self):
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

#폭탄, 총알 갯수, 레벨,
if __name__ == '__main__':
    cocos.director.director.init(caption='Cocos Invaders',
                                 width=800, height=650)
    main_scene = cocos.scene.Scene()
    hud_layer = HUD()
    main_scene.add(hud_layer, z=1)
    game_layer = GameLayer(hud_layer)
    main_scene.add(game_layer, z=0)
    cocos.director.director.run(main_scene)