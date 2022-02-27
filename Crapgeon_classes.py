import random

from msvcrt import getch


def count(room, item):
    item_num = 0
    for y in range(room.y_axis):
        item_num += room.grid[y].count(item)  # count monsters in room
    return item_num


def invert(character, room):
    if character.position[0] == 0:  # exit north
        return -1
    elif character.position[0] == len(room.grid) - 1:  # exit south
        return 1
    elif character.position[1] == 0:  # exit east
        return 2
    elif character.position[1] == len(room.grid[character.position[0]]) - 1:  # exit west
        return -2


class Room:
    database = []

    def __init__(self, y_axis=0, x_axis=0):  # constructor (initializer) function

        self.grid = []  # room grid

        if y_axis < 5 or x_axis < 5:  # if invalid or no argument is passed random room is created
            self.y_axis = random.randint(5, 15)
            self.x_axis = random.randint(5, 15)
        else:
            self.y_axis = y_axis
            self.x_axis = x_axis

        self.size = (self.y_axis - 2) * (self.x_axis - 2)  # -2 to exclude walls and doors

        for y in range(self.y_axis):
            self.grid.append([])  # adds one empty nested list (x-axis) to the y-axis
            for x in range(self.x_axis):
                if y == 0 or y == self.y_axis - 1 or x == 0 or x == self.x_axis - 1:  # room edges
                    self.grid[y].append("#")  # print walls on edges
                    continue  # starts iteration all over
                self.grid[y].append(".")

    def print_room(self):
        for y in range(self.y_axis):  # iterates through y-axis and prints whole x-axis list on each y point
            print(*self.grid[y])  # asterisk to unpack list (print without square brackets)

        print("\nUse arrow keys to move, Q to quit")

    def place_doors(self, orientations_input=None, autocomplete=True):  # door are passed as a collection, -1 to 2, no 0

        door_orientations = set()  # set to avoid repeated values

        if orientations_input is not None:  # add valid values to door_orientations
            for orientation in orientations_input:
                if -3 < orientation < 3 and orientation != 0:
                    door_orientations.add(orientation)

        if autocomplete:
            door_num = random.randint(2, 4)
            while len(door_orientations) < door_num:  # while doors are less than door number
                door_orientation = random.randint(-2, 2)  # numbers correspond to directions
                if door_orientation == 0:  # zero must be excluded
                    continue
                door_orientations.add(door_orientation)

        for orientation in door_orientations:

            if orientation == -2 or orientation == 2:  # door at east or west (vertical)
                door_middle_point = random.randint(2, len(self.grid) - 3)  # sets random door middle point in y axis

                for door_point in range(door_middle_point - 1, door_middle_point + 2):  # places rest of door
                    if orientation == 2:  # east
                        self.grid[door_point][len(self.grid[door_point]) - 1] = "."
                    else:  # west
                        self.grid[door_point][0] = "."

            elif orientation == -1 or orientation == 1:  # door at south or north (horizontal)
                door_middle_point = random.randint(2, len(self.grid[0]) - 3)  # sets random door middle point in x axis

                for door_point in range(door_middle_point - 1, door_middle_point + 2):
                    if orientation == -1:  # south
                        self.grid[len(self.grid) - 1][door_point] = "."
                    else:  # north
                        self.grid[0][door_point] = "."

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

            y_axis = random.randint(1, room.y_axis - 2)  # random position if none or invalid is passed
            x_axis = random.randint(1, room.x_axis - 2)  # doors are excluded

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

    # TODO:monster movement algorith also goes here

    def move(self, room, new_position):
        if -1 < new_position[0] < room.y_axis and -1 < new_position[1] < room.x_axis:  # if not out of range

            if room.grid[new_position[0]][new_position[1]] == ".":  # if spot is free
                room.grid[self.position[0]][self.position[1]] = "."  # erase from previous position
                room.grid[new_position[0]][new_position[1]] = self.appearance
                self.position = [new_position[0], new_position[1]]  # position update
            elif room.grid[new_position[0]][new_position[1]] == "M":  # if attack monster
                pass
                # attack function ()
            return True  # if wall # is hit code goes directly here
        room.grid[self.position[0]][self.position[1]] = "."
        return False

    def transfer(self, current, follows):

        entrance = invert(self, current)

        if entrance == -1 or entrance == 1:  # character enters from south or north
            for x in range(len(follows.grid[0])):  # valid is index 0 or any other
                if entrance == -1 and follows.grid[len(follows.grid) - 1][x] == ".":  # south
                    self.place(follows, len(follows.grid) - 1, x)
                    return
                elif entrance == 1 and follows.grid[0][x] == ".":  # north
                    self.place(follows, 0, x)
                    return

        elif entrance == -2 or entrance == 2:  # character enters from west or east
            for y in range(len(follows.grid)):
                if entrance == -2 and follows.grid[y][0] == ".":  # west
                    self.place(follows, y, 0)
                    return
                elif entrance == 2 and follows.grid[y][len(follows.grid[0]) - 1] == ".":  # east
                    self.place(follows, y, len(follows.grid[0]) - 1)
                    return


#   STARTING ROOM   ######################################

current_room = Room(5, 5)
current_room.place_doors({1, -1, 2, -2})

player = Character(is_player=True)
monster1 = Character()

player.place(current_room, 2, 2)
# monster1.place(current_room)

current_room.print_room()

#   GAME LOOP   ###########################################
end_game = False
while not end_game:
    movement = player.input_movement()
    if movement == (-1, -1):
        end_game = True
        continue
    if player.move(current_room, movement):
        current_room.print_room()
    else:
        next_room = Room()
        print(invert(player, current_room))
        next_room.place_doors({invert(player, current_room)})
        # Room.database.append(current_room) # this must be done when player leaves room.
        player.transfer(current_room, next_room)
        current_room = next_room
        del next_room
        current_room.print_room()

print("Game over")
