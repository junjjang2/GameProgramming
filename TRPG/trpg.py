import random


class Object:
    pass


class Character(Object):
    def __init__(self, name, alignment, species, level, exp, hp, mhp, stat, chr_class, appearance, background, *props):
        self.name = name
        self.alignment = alignment
        self.species = species
        self.level = level
        self.exp = exp
        self.mhp = mhp
        self.hp = hp
        self.armour = 0
        self.dmg = 0
        self.stat = stat  # [strength, dexility, health, intellect, insight, charisma]
        self.char_class = chr_class
        self.appearance = appearance
        self.background = background
        self.properties = list(props)
        self.items = list()
        self.equipments = list()

    def get_prop(self):
        pass

    def __str__(self):
        result = f"""
        -----------------------------------
        {self.__class__} 
         {self.name} | {self.species} | {self.char_class} | {self.alignment}
         str | dex | hth | int | ins | chr
        {self.stat[0]:^5}|{self.stat[1]:^5}|{self.stat[2]:^5}|{self.stat[3]:^5}|{self.stat[4]:^5}|{self.stat[5]:^5}
        dmg: {self.dmg} | armour: {self.armour} | HP: {self.hp}/{self.mhp}
        level: {self.level} | exp: {self.exp}
        props
        -----------------------------------
        """
        return result


class Player(Character):
    def __init__(self, name, alignment, species, level, exp, stat, chr_class, appearance, background, *props):
        self.mhp = self.stat[2] + 6
        self.hp = self.mhp
        self.level = level
        self.exp = exp

        super(Player, self).__init__(self, name, alignment, species, level, exp, self.hp, self.mhp, stat, chr_class,
                                     appearance, background, *props)


class NPC(Character):
    pass


class Enemy(NPC):
    pass


class Property:
    pass


class HUD:
    liner = '-'
    bar = '|'
    mainpage = '''
    %s %s %d | %s |  
    %s
    
    
    '''

    def printDice(self, args):
        diceline = "dice |"
        l = self.liner * (len(args) * 5)  # " n |" + " sum |"
        numline = "num  |"
        for case in args:
            diceline += " %d |" % case[0]
            numline += " %d |" % case[1]
        diceline += " sum |"
        numline += " %d |" % sum([case[1] for case in args])
        print(diceline, l, numline, sep="\n")

    def printObject(self):
        pass

    def clearScreen(self):
        print("\n" * 20)

    def showDefineHUD(self):
        definehud = """
        -----------------------------------
        Character 
         {self.name} | {self.species} | {self.char_class} | {self.alignment}
         str | dex | hth | int | ins | chr
        {self.stat[0]:^5}|{self.stat[1]:^5}|{self.stat[2]:^5}|{self.stat[3]:^5}|{self.stat[4]:^5}|{self.stat[5]:^5}
        dmg: {self.dmg} | armour: {self.armour} | HP: {self.hp}/{self.mhp}
        level: {self.level} | exp: {self.exp}
        props
        -----------------------------------
        """
        print(definehud)


class TimeLine:
    pass


class GameManager:
    def __init__(self, filename):
        self.filename = filename

        self.properties = list()
        self.characters = list()
        self.NPCs = list()
        self.enemies = list()
        self.otherObjects = list()
        self.timeline = TimeLine()
        self.hud = HUD()

    def __del__(self):
        self.saveData()
        self.saveGame(self.filename)

    def saveData(self):
        pass

    def loadData(self):
        gamefile = open(self.filename, 'r')
        self.readGameFromFile(gamefile)

    def saveGame(self, filename):
        file = open("%s.txt" % filename, 'r')
        file.write(
            "character name alignment species level exp hp mhp str dex hel int ins cha class \'appearence\' \'background\' *prop1* *prop2* ...")
        for chr in self.characters:
            file.write(chr)
            file.write(chr.get_prop())

        file.write(
            "character name alignment species level exp hp mhp str dex hel int ins cha class \'appearence\' \'background\' *prop1* *prop2* ...")
        for npc in self.NPCs:
            file.write(npc)
        for enemy in self.enemies:
            file.write(enemy)
        for obj in self.otherObjects:
            file.write(obj)

    def readGameFromFile(self, gamefile):
        for line in gamefile:
            keywords = line.split(" ")
            if keywords[0] == 'c':
                pass

    def giveItem(self, chr, args):
        if not isinstance(chr, Character):
            print("Wrong instance")
            return False
        Character.give(args)

    def giveProperty(self, obj, args):
        if not isinstance(obj, Object):
            print("Wrong instance")
            return False

    def createObject(self):
        self.hud.showDefineHUD()

    def defineObject(self):
        self.hud.showDefineHUD()

    def createCharacter(self):
        self.hud.showDefineHUD()
        name = input("name : ")
        alignment = input("alignment : ")
        species = input("species : ")
        char_class = input("class : ")
        stat = list()
        stat.append(int(input("strength : ")))
        stat.append(int(input("dexility : ")))
        stat.append(int(input("health : ")))
        stat.append(int(input("intellect : ")))
        stat.append(int(input("insight : ")))
        stat.append(int(input("charisma : ")))
        level = input("level : ")
        exp = input("exp : ")
        appearance = list()
        background = list()
        prop = list()

        cnt = 0
        while True:
            cnt += 1
            line = input("appearance %d: " % cnt)
            if line == 'EOL':
                break
            appearance.append(line)
        cnt = 0

        while True:
            cnt += 1
            line = input("background %d: " % cnt)
            if line == 'EOL':
                break
            background.append(line)
        self.defineCharacter(name, alignment, species, level, exp, stat[2] + 6, stat[2] + 6, stat, char_class,
                             appearance, background, prop)

    def defineCharacter(self, name, alignment, species, level, exp, hp, mhp, stat, chr_class, appearence, background,
                        *props):
        c = Character(name, alignment, species, level, exp, hp, mhp, stat, chr_class, appearence, background, *props)
        print(c)  # test code
        self.characters.append(c)

    def roll(self, args):
        d = self.dice(args)
        if d is not None:
            self.hud.printDice(d)

    def dice(self, dices):
        result = list()
        try:
            for command in dices:
                dices = list(map(int, command.split("d")))
                for i in range(dices[0]):
                    num = random.randint(1, dices[1] + 1)
                    result.append((dices[1], num))
        except:
            print("Wrong Input")
            return None
        return result

    def PrintAll(self):
        for c in self.characters:
            print(c)
        for npc in self.NPCs:
            print(npc)
        for enemy in self.enemies:
            print(enemy)

    def nextTimeline(self):
        pass


def help_command(command):
    str = \
        '''
    dice *number*d*type*                        number: 1~, type:1~
    define *object_type* *object_name*
    print *object_type* *object_name*
    show *type*                                 type:characters, NPCs, enemies, objects
    del *object_type* *object_name*
    give *character* *type* *object_name*
    get *character* *type* *object_name*
    put *character* *affection_type* *number*
    damage *character* *number*
    heal *character* *number*
    
    save
    load
    help 
    exit
    '''
    command_helps = ['''dice *number*d*type*                        number: 1~, type:1~
-print results of given dices
-input:dice 2d6 1d2
-output:
                    ''',
                     '''define *object_type* *object_name*''',
                     '''print *object_type* *object_name*''',
                     '''show *type*                                 type:characters, NPCs, enemies, objects''',
                     '''del *object_type* *object_name*''',
                     '''save''',
                     '''load''',
                     '''help''',
                     '''exit''']
    print(str)


def set_up():
    filelist = open('recentGame.txt', 'r')
    while True:
        file = input("Enter Filename")
        print(file)

        if file == 'Recent Files':
            print("-------START---------")
            for line in filelist:
                print(line)
            print("--------END---------")
        else:
            for line in filelist:
                if file == line:
                    gm = GameManager(file)
                    gm.loadData()
                    return gm
            gm = GameManager(file)
            return gm


if __name__ == '__main__':
    gm = set_up()
    while True:
        command = input("Enter Command").strip()
        ctype = command.split(" ")[0]
        args = command.split(" ")[1:]
        # print(ctype, args)
        if ctype == "dice":
            gm.roll(args)
        elif ctype == 'define':
            if args[0] == 'character':
                gm.createCharacter()
            elif args[0] == 'object':
                gm.createObject()
        elif ctype == 'print':
            gm.printObject(args)
        elif ctype == 'show':
            gm.showLists(args[0], args[1:])
            '''if args[0] == 'characters':
                pass
            elif args[0] == 'items':
                pass
            elif args[0] == 'enemies':
                pass
            elif args[0] == 'NPCs':
                pass
            elif args[0] == 'all':
                gm.PrintAll()
            '''
        elif ctype == 'del':
            gm.deleteObject()
        elif ctype == 'give':
            if args[0] == 'item':
                gm.giveItem(args[1], args[2:])
            elif args[0] == 'prop':
                gm.giveProperty(args[1], args[2:])
        elif ctype == 'timeline':
            if args[0] == 'current':
                gm.currentTimeline()
            elif args[0] == "next":
                gm.nextTimeline()
        elif ctype == 'save':
            gm.saveData()
        elif ctype == 'load':
            gm.loadData()
        elif ctype == 'help':
            help_command(None)
        elif ctype == 'exit':
            del GameManager
            break
        else:
            print("wrong command")
