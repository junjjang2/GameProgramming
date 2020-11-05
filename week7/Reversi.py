import cocos
from cocos.menu import *
import numpy as np
import cocos.euclid as eu


class HUD(cocos.layer.Layer):
    def __init__(self):
        super(HUD, self).__init__()
        w, h = cocos.director.director.get_window_size()
        self.score_text = cocos.text.Label('', font_size=18, color=(50, 50, 255, 255))
        self.score_text.position = (20, h - 40)
        self.add(self.score_text)

    def update_score(self, person, computer):
        self.score_text.element.text = 'You: %s, Computer: %s' % (person, computer)

    def show_game_over(self, winner):
        w, h = cocos.director.director.get_window_size()
        game_over = cocos.text.Label(winner, font_size=50, anchor_x='center', anchor_y='center',
                                     color=(50, 50, 255, 255))
        game_over.position = w * 0.5, h * 0.5
        self.add(game_over)


class GameLayer(cocos.layer.Layer):
    is_event_handler = True
    PERSON = -1
    COMPUTER = 1

    def __init__(self, difficulty, hud_layer):
        super(GameLayer, self).__init__()
        self.difficulty = difficulty
        self.levelDepth = self.difficulty * 2 + 2
        self.hud = hud_layer
        self.square = 75
        self.row = 8  # 4
        self.column = 8  # 4
        self.height = self.row * self.square
        self.width = self.column * self.square
        self.table = np.arange(self.row * self.column).reshape(self.row, self.column)
        self.weight = np.array([[50, -10, 15, 15, 15, 15, -10, 50],
                                [-10, -20, -10, -10, -10, -10, -20, -10],
                                [-15, -10, 1, 1, 1, 1, -10, 15],
                                [-15, -10, 1, 1, 1, 1, -10, 15],
                                [-15, -10, 1, 1, 1, 1, -10, 15],
                                [-15, -10, 1, 1, 1, 1, -10, 15],
                                [-10, -20, -10, -10, -10, -10, -20, -10],
                                [50, -10, 15, 15, 15, 15, -10, 50]])
        for x in range(0, self.column + 1):
            line = cocos.draw.Line((x * self.square, 0), (x * self.square, self.height), (255, 0, 255, 255))
            self.add(line)

        for y in range(0, self.row + 1):
            line = cocos.draw.Line((0, y * self.square), (self.width, y * self.square), (255, 0, 255, 255))
            self.add(line)

        self.disk = [[None for i in range(self.column)] for j in range(self.row)]

        for y in range(0, self.row):
            for x in range(0, self.column):
                centerPt = eu.Vector2(x * self.square + self.square / 2, y * self.square + self.square / 2)
                self.disk[y][x] = cocos.sprite.Sprite('ball.png', position=centerPt, color=(255, 255, 255))
                self.add(self.disk[y][x])

        self.setup()
        self.turn = GameLayer.PERSON
        self.count = 0
        self.schedule(self.update)

    def setup(self):
        for y in range(0, self.row):
            for x in range(0, self.column):
                self.table[y][x] = 0

        self.table[3][3] = GameLayer.PERSON
        self.table[3][4] = GameLayer.COMPUTER
        self.table[4][3] = GameLayer.COMPUTER
        self.table[4][4] = GameLayer.PERSON

    def update(self, dt):
        computer = 0
        person = 0
        self.count += 1
        for y in range(0, self.row):
            for x in range(0, self.column):
                if self.table[y][x] == GameLayer.COMPUTER:
                    self.disk[y][x].color = (255, 255, 255)
                    self.disk[y][x].visible = True
                    computer += 1
                elif self.table[y][x] == GameLayer.PERSON:
                    self.disk[y][x].color = (0, 0, 0)
                    self.disk[y][x].visible = True
                    person += 1
                else:
                    self.disk[y][x].visible = False

        self.hud.update_score(person, computer)
        moves1 = self.getMoves(GameLayer.PERSON, self.table)
        moves2 = self.getMoves(GameLayer.COMPUTER, self.table)

        if self.turn == GameLayer.PERSON and len(moves1) == 0:
            self.turn *= -1
        if computer + person == self.row * self.column or (len(moves1) == 0 and len(moves2) == 0):
            if computer > person:
                self.hud.show_game_over('Computer win')
            elif computer < person:
                self.hud.show_game_over('You win')
            else:
                self.hud.show_game_over('Draw')
        if self.turn == GameLayer.COMPUTER and self.count > 100:  # 100번 update가 실행된 후 (임의의 delay임)
            self.computer()

    def isPossible(self, x, y, turn, board):
        rtnList = list()

        if board[y][x] != 0: return rtnList

        for dirX in range(-1, 2):
            for dirY in range(-1, 2):
                if dirX == 0 and dirY == 0: continue
                if x + dirX < 0 or x + dirX >= self.column: continue
                if y + dirY < 0 or y + dirY >= self.row: continue
                xList = list()
                yList = list()

                if dirX == 0:
                    for yy in range(y + dirY * 2, self.row * dirY, dirY):
                        if yy < 0 or yy >= self.row: break
                        xList.append(x)
                        yList.append(yy)
                elif dirY == 0:
                    for xx in range(x + dirX * 2, self.column * dirX, dirX):
                        if xx < 0 or xx >= self.column: break
                        xList.append(xx)
                        yList.append(y)

                else:
                    for xx, yy in zip(range(x + dirX * 2, self.column * dirX, dirX),
                                      range(y + dirY * 2, self.row * dirY, dirY)):
                        if xx < 0 or xx >= self.column: break
                        if yy < 0 or yy >= self.row: break
                        xList.append(xx)
                        yList.append(yy)
                bDetected = False
                revList = []
                if board[y + dirY][x + dirX] == turn * -1:
                    revList.append((x + dirX, y + dirY))
                    for xx, yy in zip(xList, yList):
                        if xx >= self.column or xx < 0 or yy >= self.row or yy < 0:
                            break
                        if board[yy][xx] == turn * -1:
                            revList.append((xx, yy))
                        if board[yy][xx] == turn:
                            bDetected = True
                            break
                        if board[yy][xx] == 0:
                            break
                    if bDetected == False:
                        revList = []
                rtnList += revList
        return rtnList

    def getMoves(self, turn, board):
        moves = []
        for y in range(0, self.row):
            for x in range(0, self.column):
                if board[y][x] != 0: continue

                revList = self.isPossible(x, y, turn, board)
                if len(revList) > 0:
                    moves.append((x, y, revList))

        return moves

    def on_mouse_press(self, x, y, buttons, mod):
        if self.turn != GameLayer.PERSON:
            return

        moves = self.getMoves(GameLayer.PERSON, self.table)

        if len(moves) > 0:
            xx = x // self.square  # x번째 칸
            yy = y // self.square  # y번째 칸
            revList = self.isPossible(xx, yy, GameLayer.PERSON, self.table)

            if len(revList) == 0: return

            self.table[yy][xx] = GameLayer.PERSON
            for revX, revY in revList:
                self.table[revY][revX] = GameLayer.PERSON
        self.turn *= -1  # switch turn to computer
        self.count = 0

    def computer(self):
        move = self.minimax(GameLayer.COMPUTER)

        if len(move) > 0:
            self.table[move[1]][move[0]] = GameLayer.COMPUTER
            for revX, revY in move[2]:  # move[2]는 isPossible()에서 얻은 rtnList(revList)
                self.table[revY][revX] = GameLayer.COMPUTER

        self.turn *= -1  # switch turn to player

    def minimax(self, player):
        moves = self.getMoves(player, self.table)
        if len(moves) == 0:
            return moves
        scores = np.zeros(len(moves))
        alpha = float("-inf")
        beta = float("inf")

        maxscore = self.maxMove(np.copy(self.table), 1, alpha, beta)
        for i, move in enumerate(moves):
            boardCopy = self.getNewBoard(move[0], move[1], move[2], GameLayer.COMPUTER, np.copy(self.table))
            #boardCopy = np.copy(self.table)
            scores[i] = self.minMove(boardCopy, 1, alpha, beta)

        maxIndex = np.argmax(scores)
        return moves[maxIndex]

    def getNewBoard(self, x, y, revList, player, table):
        table[y][x] = player
        for (x, y) in revList:
            table[y][x] = player
        return table

    def maxMove(self, board, depth, alpha, beta):
        moves = self.getMoves(GameLayer.COMPUTER, board)
        scores = np.zeros(len(moves))

        if len(moves) == 0:
            if depth <= self.levelDepth:
                return self.minMove(board, depth + 1, alpha, beta)
            else:
                return self.boardScore(board)
        for i, move in enumerate(moves):
            boardCopy = self.getNewBoard(move[0], move[1], move[2], GameLayer.COMPUTER, np.copy(board))
            if depth >= self.levelDepth:
                scores[i] = self.boardScore(boardCopy)
            else:
                scores[i] = self.minMove(boardCopy, depth + 1, alpha, beta)
                if scores[i] > alpha:
                    alpha = scores[i]
                if beta <= alpha:
                    return scores[i]

        return max(scores)

    def minMove(self, board, depth, alpha, beta):
        moves = self.getMoves(GameLayer.PERSON, board)
        scores = np.zeros(len(moves))

        if len(moves) == 0:
            if depth <= self.levelDepth:
                return self.maxMove(board, depth + 1, alpha, beta)
            else:
                return self.boardScore(board)
        for i, move in enumerate(moves):
            boardCopy = self.getNewBoard(move[0], move[1], move[2], GameLayer.COMPUTER, np.copy(board))
            if depth >= self.levelDepth:
                scores[i] = self.boardScore(boardCopy)
            else:
                scores[i] = self.maxMove(boardCopy, depth + 1, alpha, beta)
                if scores[i] > alpha:
                    alpha = scores[i]
                if beta <= alpha:
                    return scores[i]
        return min(scores)

    def boardScore(self, board):
        computerWieghtSum = 0
        personWeightSum = 0

        for y in range(0, self.row):
            for x in range(0, self.column):
                if board[y][x] == GameLayer.COMPUTER:
                    computerWieghtSum += self.weight[y][x]

                if board[y][x] == GameLayer.PERSON:
                    personWeightSum += self.weight[y][x]

        return computerWieghtSum - personWeightSum


class MainMenu(Menu):
    def __init__(self):
        super(MainMenu, self).__init__('Menu')
        self.font_title['font_name'] = 'Times New Roman'
        self.font_title['font_size'] = 60
        self.font_title['bold'] = True
        self.font_item['font_name'] = 'Times New Roman'
        self.font_item_selected['font_name'] = 'Times New Roman'

        self.selDifficulty = 0
        self.difficulty = ['Easy', 'Normal', 'Hard']

        items = list()
        items.append(MenuItem('New Game', self.start_game))
        items.append(MultipleMenuItem('Difficulty: ', self.set_difficulty, self.difficulty, 0))
        items.append(MenuItem('Quit', exit))
        self.create_menu(items, shake(), shake_back())

    def start_game(self):
        scene = cocos.scene.Scene()
        color_layer = cocos.layer.ColorLayer(0, 100, 0, 255)
        hud_layer = HUD()
        scene.add(hud_layer, z=2)
        scene.add(GameLayer(self.selDifficulty, hud_layer), z=1)
        scene.add(color_layer, z=0)
        cocos.director.director.push(scene)

    def set_difficulty(self, index):
        self.difficulty = index


if __name__ == '__main__':
    cocos.director.director.init(caption='Othello', width=75 * 8, height=75 * 8)

    scene = cocos.scene.Scene()
    scene.add(MainMenu())

    cocos.director.director.run(scene)
