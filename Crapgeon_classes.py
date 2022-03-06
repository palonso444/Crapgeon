from random import randint
from msvcrt import getch


def open_door(room, y_axis=None, x_axis=None):  # only one coordinate required as function scans whole axis for doors
    if y_axis == 0 or y_axis == room.y_axis - 1:  # open north or south door
        for x in range(room.x_axis):
            if room.grid[y_axis][x] == "+":
                room.grid[y_axis][x] = "."
        return

    elif x_axis == 0 or x_axis == room.x_axis - 1:  # open west or east door
        for y in range(room.y_axis):
            if room.grid[y][x_axis] == "+":
                room.grid[y][x_axis] = "."
        return


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
    dice_10 = randint(1, 10)  # change those stats to make dungeon more or less intricate
    print("dice10: ", dice_10)
    if Room.open_ends > 1 and dice_10 < 5:  # if open ends more than 1 one door rooms allowed
        return 1
    elif dice_10 < 8:
        return 2
    elif dice_10 < 10:
        return 3
    else:
        return 4


class Room:
    database = []
    open_ends = 2  # keeps track of open ends of dungeon. DO NOT CHANGE IT
    total_num = len(database)

    def __init__(self, y_axis=0, x_axis=0):  # constructor (initializer) function

        self.boundaries = {}  # Key = orientation, value = index in room database
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

        print("\nUse arrow keys to move, Q to quit")
        # TODO: new function name: print_interface. Prints room plus text below

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

    def check(self, character):
        if character.appearance == "%" and count(self, character.appearance) == 0:
            return True
        elif character.appearance == "M" and count(self, character.appearance) < self.size * 0.15:
            return True
        return False


class Character:

    def __init__(self, speed=1, is_player=False):

        self.is_player = is_player
        self.position = [0, 0]
        self.speed = speed
        if self.is_player:
            self.appearance = "%"
        else:
            self.appearance = "M"

    def place(self, room, y_axis=-1, x_axis=-1):

        while room.check(self):  # if maximum number not reached

            # if none or invalid position or spot already taken
            if -1 < y_axis < room.y_axis and -1 < x_axis < room.x_axis and room.grid[y_axis][x_axis] == ".":
                room.grid[y_axis][x_axis] = self.appearance
                self.position[0] = y_axis
                self.position[1] = x_axis
                return  # remove this return to see max num of characters placed

            y_axis = randint(1, room.y_axis - 2)  # random position if none or invalid is passed
            x_axis = randint(1, room.x_axis - 2)  # doors are excluded

    def input_movement(self):
        while True:

            # getchar () returns a bite string b'x'
            char = getch()  # 1st call returns generic keycode for function keys
            if char == b'\x00':
                char = getch()  # 2nd call returns keycode for function keys

            if char == b'H':  # north
                return self.position[0] - 1, self.position[1]  # returns tuple (x,y), immutable
            elif char == b'P':  # south
                return self.position[0] + 1, self.position[1]
            elif char == b'K':  # west
                return self.position[0], self.position[1] - 1
            elif char == b'M':  # east
                return self.position[0], self.position[1] + 1
            elif char.upper() == b'Q':  # quit game
                return -1, -1

    # TODO:monster movement algorith also goes here. Stupid (random), neutral (random avoids walls and pits) and
    # TODO: aggressive (chases player) profile. Movement loop until "speed" value is achieved.

    def move(self, room, new_position):
        if -1 < new_position[0] < room.y_axis and -1 < new_position[1] < room.x_axis:  # if not out of range

            if room.grid[new_position[0]][new_position[1]] == ".":  # if spot is free
                room.grid[self.position[0]][self.position[1]] = "."  # erase from previous position
                room.grid[new_position[0]][new_position[1]] = self.appearance
                self.position = [new_position[0], new_position[1]]  # position update
            elif room.grid[new_position[0]][new_position[1]] == "M":  # if attack monster
                pass
                # attack function ()
            elif room.grid[new_position[0]][new_position[1]] == "+":  # if door
                open_door(room, new_position[0], new_position[1])
            return True  # if wall # is hit code goes directly here
        room.grid[self.position[0]][self.position[1]] = "."
        return False

    def transfer(self, current, follows):

        door = character_exit(self, current)

        if door == -1 or door == 1:  # character exits from south or north
            if door == -1:
                open_door(follows, y_axis=0)
            elif door == 1:
                open_door(follows, y_axis=follows.y_axis - 1)
            for x in range(follows.x_axis):
                if door == 1 and follows.grid[follows.y_axis - 1][x] == ".":  # exits north
                    self.place(follows, follows.y_axis - 1, x)
                    return
                elif door == -1 and follows.grid[0][x] == ".":  # exits south
                    self.place(follows, 0, x)
                    return

        elif door == -2 or door == 2:  # character exits from west or east
            if door == -2:
                open_door(follows, x_axis=follows.x_axis - 1)
            elif door == 2:
                open_door(follows, x_axis=0)
            for y in range(follows.y_axis):
                if door == 2 and follows.grid[y][0] == ".":  # exits west
                    self.place(follows, y, 0)
                    return
                elif door == -2 and follows.grid[y][follows.x_axis - 1] == ".":  # exits east
                    self.place(follows, y, follows.x_axis - 1)
                    return


#   STARTING ROOM   ######################################

current_room = Room(5, 5)
current_room.doors({1, -1, 2, -2}, False)

player = Character(is_player=True)
monster1 = Character()

player.place(current_room, 2, 2)

monster1.place(current_room)

#   GAME LOOP   ###########################################
end_game = False
while not end_game:
    current_room.print_room()
    print("database:", len(Room.database))
    print("Boundaries: ", current_room.boundaries.values())
    print("Open ends: ", Room.open_ends)
    movement = player.input_movement()
    if movement == (-1, -1):
        end_game = True
        continue

    if not player.move(current_room, movement):  # if after moving player, player does not stay in room

        if character_exit(player, current_room) not in current_room.boundaries.keys():  # goes to unexplored room
            next_room = Room()
            next_room.doors({character_exit(player, current_room) * -1})
        else:  # returns to explored room
            next_room = Room.database[current_room.boundaries[character_exit(player, current_room)]]

        build_map(player, current_room, next_room)  # if needed adds rooms to database and establish boundaries
        player.transfer(current_room, next_room)  # places player to door in new room
        del current_room  # deletes current_room object
        current_room = next_room  # new reference for next room
        del next_room  # delete (now duplicate) next_room

print("Game over")
