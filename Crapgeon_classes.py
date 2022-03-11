from random import randint
from msvcrt import getch


def count(room, item):
    item_num = 0
    for y in room.grid:
        item_num += y.count(item)  # count monsters in room
    return item_num


def character_exit(character, room):
    if character.position[0] == 0:  # exit north
        return 1
    elif character.position[0] == room.y_axis - 1:  # exit south
        return -1
    elif character.position[1] == 0:  # exit east
        return -2
    elif character.position[1] == room.x_axis - 1:  # exit west
        return 2


def build_map(character, current, follows):
    door = character_exit(character, current)
    if current.id is None:  # player leaves room for 1st time, current room added to database
        Room.database.append(current)
        current.id = len(Room.database) - 1
    follows.boundaries[door * -1] = current.id  # always establish link between next and current room


def generate_doornum():
    die_20 = randint(1, 20)  # change those stats to make dungeon more or less intricate
    print("die20: ", die_20)
    # TODO: implement a max num of open ends. If reached, only dead ends are showed
    if Room.open_ends > 1 and die_20 < 13:  # if open ends more than 1 one door rooms allowed
        return 1
    elif die_20 < 17:
        return 2
    elif die_20 < 20:
        return 3
    else:
        return 4


class Room:
    database = []
    open_ends = 2  # keeps track of open ends of dungeon. DO NOT CHANGE IT

    def __init__(self, y_axis=0, x_axis=0):  # constructor (initializer) function

        self.boundaries = {}  # Key = orientation, value = room_id (index in room database)
        self.monsters = []  # registers monsters present in room
        self.id = None

        if y_axis < 5 or x_axis < 5:  # if invalid or no argument is passed random room is created
            self.y_axis = randint(5, 10)
            self.x_axis = randint(5, 10)
        else:
            self.y_axis = y_axis
            self.x_axis = x_axis

        self.size = (self.y_axis - 2) * (self.x_axis - 2)  # -2 to exclude walls and doors

        self.grid = []  # room grid
        for y in range(self.y_axis):
            self.grid.append([])  # adds one empty nested list (x-axis) to the y-axis
            for x in range(self.x_axis):
                if y == 0 or y == self.y_axis - 1 or x == 0 or x == self.x_axis - 1:  # room edges
                    self.grid[y].append("#")  # print walls on edges
                    continue  # starts iteration all over
                self.grid[y].append(".")

    def print_room(self):
        for y in self.grid:  # iterates through y-axis and prints whole y list on each point
            print(*y)  # asterisk to unpack list (print without square brackets)


    def doors(self, orientations_input=None, autocomplete=True):  # door are passed as a collection, -1 to 2, no 0

        door_orientations = set()  # set to avoid repeated values

        if orientations_input is not None:  # add valid values to door_orientations
            door_orientations = {orientation for orientation in orientations_input if
                                 -3 < orientation < 3 and orientation != 0}

        if autocomplete:
            door_num = generate_doornum()
            while len(door_orientations) < door_num:  # while doors are less than door number
                door_orientation = randint(-2, 2)  # numbers correspond to directions
                if door_orientation == 0:  # zero must be excluded
                    continue
                door_orientations.add(door_orientation)

        for orientation in door_orientations:

            if orientation == -2 or orientation == 2:  # door at east or west (vertical)
                door_middle_point = randint(2, len(self.grid) - 3)  # sets random door middle point in y axis

                for door_point in range(door_middle_point - 1, door_middle_point + 2):  # places rest of door
                    if orientation == 2:  # east
                        self.grid[door_point][len(self.grid[door_point]) - 1] = "+"
                    else:  # west
                        self.grid[door_point][0] = "+"

            elif orientation == -1 or orientation == 1:  # door at south or north (horizontal)
                door_middle_point = randint(2, len(self.grid[0]) - 3)  # sets random door middle point in x axis

                for door_point in range(door_middle_point - 1, door_middle_point + 2):
                    if orientation == -1:  # south
                        self.grid[len(self.grid) - 1][door_point] = "+"
                    else:  # north
                        self.grid[0][door_point] = "+"

        Room.open_ends += len(door_orientations) - 2  # rooms with 2 doors does not increase open ends

    def open_door(self, y_axis=None, x_axis=None):  # one coordinate required as function scans whole axis for doors
        if y_axis == 0 or y_axis == self.y_axis - 1:  # open north or south door
            for x in range(self.x_axis):
                if self.grid[y_axis][x] == "+":
                    # noinspection PyTypeChecker
                    # it gives unexpected type issue for [x]
                    self.grid[y_axis][x] = "."

        elif x_axis == 0 or x_axis == self.x_axis - 1:  # open west or east door
            for y in range(self.y_axis):
                if self.grid[y][x_axis] == "+":
                    self.grid[y][x_axis] = "."

    def populate(self):  # put monsters in room

        monster_num = randint(0, len(Room.database))

        for monster in range(monster_num):
            monster_type = randint(1, 100) + len(Room.database)
            if monster_type < 51:  # rat
                new_monster = Monster(*Monster.database[0])
            elif monster_type < 81:  # zombie
                new_monster = Monster(*Monster.database[1])
            else:  # vampire
                new_monster = Monster(*Monster.database[2])
            new_monster.place(self)


class Character:

    # TODO: max_num and aggressivity should be Monster attributes. They are here because otherwise conflict with
    # TODO: move function. Fix.

    def __init__(self, appearance, power=1, health=1, speed=1):

        self.position = [0, 0]
        self.appearance = appearance
        self.power = power
        self.health = health
        self.speed = speed

    def place(self, room, y_axis=-1, x_axis=-1):

        while type(self) is Hero or count(room, self.appearance) < room.size * self.max_num:  # if under max_num

            # if none or invalid position or spot already taken
            if -1 < y_axis < room.y_axis and -1 < x_axis < room.x_axis and room.grid[y_axis][x_axis] == ".":
                room.grid[y_axis][x_axis] = self.appearance
                self.position[0] = y_axis
                self.position[1] = x_axis
                if type(self) is not Hero:
                    room.monsters.append(self)  # if monster, append it to list of rooms monsters
                return  # remove this return to see max num of characters placed

            y_axis = randint(1, room.y_axis - 2)  # random position if none or invalid is passed
            x_axis = randint(1, room.x_axis - 2)  # doors are excluded

    def input_movement(self):

        def manual_move():

            while True:

                # getchar () returns a bite string b'x'
                char = getch()  # 1st call returns generic keycode for function keys
                if char == b'\x00':
                    char = getch()  # 2nd call returns keycode for function keys
                if char in (b'K', b'P', b'H', b'M', b'Q', b'q'):  # if input not allowed, loop keeps running
                    return char

        def passive_move():

            direction = randint(-2, 2)
            if direction == -2:  # west
                return b'K'
            elif direction == -1:  # south
                return b'P'
            elif direction == 0:  # no move
                return direction
            elif direction == 1:  # north
                return b'H'
            elif direction == 2:  # east
                return b'M'

        def aggressive_move(monst):

            second_choice = False

            while True:
                # if y distance is bigger than x distance
                if abs(monst.position[0] - player.position[0]) > \
                        abs(monst.position[1] - player.position[1]) or second_choice:
                    if monst.position[0] > player.position[0]:  # if monster below player
                        if monst.position[0] - 1 > -1 and current_room.grid[monst.position[0] - 1][
                            monst.position[1]] in Monster.allowed:  # if spot is within room and free
                            return b'H'  # go north
                    else:  # if monster above player
                        if monst.position[0] + 1 < current_room.y_axis and current_room.grid[monst.position[0] + 1][
                            monst.position[1]] in Monster.allowed:  # if spot is within room and free
                            return b'P'  # go south

                # if x distance is bigger or equal than y distance
                if abs(monst.position[0] - player.position[0]) <= \
                        abs(monst.position[1] - player.position[1]) or second_choice:
                    if monst.position[1] > player.position[1]:  # if monster east from player
                        if monst.position[1] - 1 > -1 and current_room.grid[monst.position[0]][
                            monst.position[1] - 1] in Monster.allowed:  # if spot is within room and free
                            return b'K'  # go west
                    else:  # if monster west from player
                        if monst.position[1] + 1 < current_room.x_axis and current_room.grid[monst.position[0]][
                            monst.position[1] + 1] in Monster.allowed:  # if spot is within room and free
                            return b'M'  # go east

                if second_choice:  # if monster cannot move will remain quiet
                    return 0
                second_choice = True  # will try to move along opposite axis

        if type(self) is Hero:
            char = manual_move()
        else:
            if self.aggressivity == 1:
                char = passive_move()
            else:  # if aggressivity ==3
                char = aggressive_move(self)

        if char == b'H':  # north
            return self.position[0] - 1, self.position[1]  # returns tuple (y,x), immutable
        elif char == b'P':  # south
            return self.position[0] + 1, self.position[1]
        elif char == b'K':  # west
            return self.position[0], self.position[1] - 1
        elif char == b'M':  # east
            return self.position[0], self.position[1] + 1
        elif char == 0:  # stays in place (monsters only)
            return self.position[0], self.position[1]
        elif char.upper() == b'Q':  # quit game
            return -1, -1

    # TODO:monster movement neutral (random avoids walls and pits)

    def move(self, room, new_position):
        if -1 < new_position[0] < room.y_axis and -1 < new_position[1] < room.x_axis:  # if not out of range

            # NORMAL MOVEMENT
            if room.grid[new_position[0]][new_position[1]] == ".":  # if spot is free
                room.grid[self.position[0]][self.position[1]] = "."  # erase from previous position
                room.grid[new_position[0]][new_position[1]] = self.appearance
                self.position = [new_position[0], new_position[1]]  # position update

            # MONSTER ATTACKS PLAYER
            elif type(self) is Monster:
                if room.grid[new_position[0]][new_position[1]] == player.appearance:  # if monster attacks hero
                    print(f"You are attacked by a {self.name}!")
                    if self.attack(player):  # if player wins
                        # uncomment following to make monster corpse disappear from room grid
                        # room.grid[self.position[0]][self.position[1]] = "."
                        room.monsters.remove(self)
                        del self
                    else:  # if loses
                        print(f"You succumb to the {self.name}...")
                        return False

            elif type(self) is Hero:

                # PLAYER OPENS DOOR
                if room.grid[new_position[0]][new_position[1]] == "+":
                    room.open_door(new_position[0], new_position[1])

                # PLAYER ATTACKS MONSTER
                elif room.grid[new_position[0]][new_position[1]] in Monster.appearances:
                    for monster in room.monsters:
                        if monster.position[0] == new_position[0] and monster.position[1] == new_position[1]:
                            print(f"You fiercely attack the {monster.name}!")
                            if self.attack(monster):  # if player wins
                                # uncomment following to make monster corpse disappear from room grid
                                # room.grid[self.position[0]][self.position[1]] = "."
                                room.monsters.remove(monster)
                                del monster
                            else:  # if loses
                                print(f"Sadly you have underestimated the strength of the {monster.name}...")
                                return False

            return True  # if wall is hit goes directly here

        # PLAYER LEAVES ROOM
        elif type(self) is Hero:  # only player can leave the room
            room.grid[self.position[0]][self.position[1]] = "."
        return False

    def transfer(self, current, follows):

        door = character_exit(self, current)

        if door == -1 or door == 1:  # character exits from south or north
            if door == -1:
                follows.open_door(y_axis=0)
            elif door == 1:
                follows.open_door(y_axis=follows.y_axis - 1)
            for x in range(follows.x_axis):
                if door == 1 and follows.grid[follows.y_axis - 1][x] == ".":  # exits north
                    self.place(follows, follows.y_axis - 1, x)
                    return
                elif door == -1 and follows.grid[0][x] == ".":  # exits south
                    self.place(follows, 0, x)
                    return

        elif door == -2 or door == 2:  # character exits from west or east
            if door == -2:
                follows.open_door(x_axis=follows.x_axis - 1)
            elif door == 2:
                follows.open_door(x_axis=0)
            for y in range(follows.y_axis):
                if door == 2 and follows.grid[y][0] == ".":  # exits west
                    self.place(follows, y, 0)
                    return
                elif door == -2 and follows.grid[y][follows.x_axis - 1] == ".":  # exits east
                    self.place(follows, y, follows.x_axis - 1)
                    return

    def attack(self, opponent):  # returns True if player wins

        start_health = player.health

        opponent.health -= self.power
        if opponent.health > 0:
            self.health -= opponent.power

        if player.health > 0:
            if type(self) is Monster:
                player.gold += self.reward
            elif type(opponent) is Monster:
                player.gold += monster.reward
            print(f"You win the fight losing {abs(player.health - start_health)} health points")
            return True
        else:
            return False


class Hero(Character):

    # TODO: overwrite __new__ so if player_created is True no more players can be created

    def __init__(self, appearance="%", power=1, health=1, speed=1, max_health=10, gold = 0):
        super().__init__(appearance, power, health, speed)
        self.max_health = max_health
        self.gold = gold
        Monster.allowed.add(appearance)


class Monster(Character):
    database = (
        ("rat", "r", 1, 1, 1, 5, 0.5, 1),  # to pass as unpacked to create monsters by generator
        ("zombie", "Z", 3, 2, 1, 10, 0.25, 1),
        ("vampire", "V", 6, 5, 3, 50, 0.1, 3))

    appearances = set()  # keep track of appearances to detect collision with monster in move

    allowed = {"."}  # allowed places to move. Free spots and player.appearance (added once created)

    def __init__(self, name, appearance, power=1, health=1, speed=1, reward=1, max_num=0.15, aggressivity=1):
        super().__init__(appearance, power, health, speed)
        self.name = name
        self.reward = reward
        self.aggressivity = aggressivity
        self.max_num = max_num
        Monster.appearances.add(appearance)


#   STARTING ROOM   ######################################

current_room = Room(12, 5)
current_room.doors({1}, False)

player = Hero(speed=3, power=4, health=10)

player.place(current_room, 10, 2)

end_game = False

#   GAME LOOP   ###########################################

while not end_game:

    current_room.print_room()  # has to be on top so all function output will be printed below room

    if player.health < 1:  # played is killed
        end_game = True
        continue

    print("\nUse arrow keys to move, Q to quit")
    print(f"Power: {player.power}")
    print(f"Health: {player.health}")
    print(f"Gold: {player.gold}")

    monsters_move = True

    for move in range(player.speed):
        movement = player.input_movement()
        if movement == (-1, -1):
            end_game = True
            break

        if not player.move(current_room, movement) and player.health > 0:  # if player leaves room alive

            if character_exit(player, current_room) not in current_room.boundaries:  # goes to unexplored room
                next_room = Room()
                next_room.doors({character_exit(player, current_room) * -1})
                next_room.populate()  # places monsters in room
            else:  # returns to explored room
                next_room = Room.database[current_room.boundaries[character_exit(player, current_room)]]

            build_map(player, current_room, next_room)  # if needed adds rooms to database and establish boundaries
            player.transfer(current_room, next_room)  # places player to door in new room
            del current_room  # deletes current_room object
            current_room = next_room  # new reference for next room
            del next_room  # delete (now duplicate) next_room
            monsters_move = False
            break

        elif player.health > 0:  # if player stays alive in room
            if move == player.speed - 1:
                break  # so in the last move room wont be printed twice
            current_room.print_room()  # print room to show player move
            print("\nUse arrow keys to move, Q to quit") # TODO: make this interface a function
            print(f"Power: {player.power}")
            print(f"Health: {player.health}")
            print(f"Gold: {player.gold}")

    if player.health > 0 and monsters_move:  # monsters do not move if player is dead or player left room
        for monster in current_room.monsters:  # move each monster in room
            for move in range(monster.speed):  # the faster it is, the more it moves each turn
                m_movement = monster.input_movement() # TODO: monsters with speed > 1 can attack two times. Fix
                if not monster.move(current_room, m_movement):
                    break

print("Game over")
