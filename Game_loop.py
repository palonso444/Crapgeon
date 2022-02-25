import random

from msvcrt import getch


def count(room, item):
    item_num = 0
    for y in range(room.y_axis):
        item_num += room.grid[y].count(item)  # count monsters in room
    return item_num


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

        self.size = self.y_axis * self.x_axis

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

    def place_doors(self, door_num=0):  # takes room object and list of door orientations as argument

        if door_num < 1 or door_num > 4:  # if invalid or no argument is passed generates random num of doors
            door_num = random.randint(2, 4)

        door_orientations = set()  # set not list to avoid repeated values

        while len(door_orientations) < door_num:  # while doors are less than door number
            door_orientation = random.randint(-2, 2)  # numbers correspond to directions
            if door_orientation == 0:  # zero must be excluded
                continue
            door_orientations.add(door_orientation)

        for orientation in door_orientations:

            if orientation == -2 or orientation == 2:  # door at east or west (vertical)

                door_middle_point = random.randint(2, len(self.grid) - 3)  # sets random door middle point in y axis

                for door_point in range(door_middle_point - 1, door_middle_point + 2):  # places rest of door
                    if orientation == -2:  # east
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

    def __init__(self, speed=1, player=False):

        self.player = player
        self.position_y = 0
        self.position_x = 0
        self.speed = speed

        if self.player:
            self.appearance = "%"
        else:
            self.appearance = "M"

    def place(self, room, y_axis=None, x_axis=None):

        while room.check(self):  # if maximmum number not reached
            if y_axis != None and x_axis != None:
                # if none or invalid position or spot already taken
                if y_axis < room.y_axis - 1 and x_axis < room.x_axis - 1 and room.grid[y_axis][x_axis] == ".":
                    room.grid[y_axis][x_axis] = self.appearance
                    self.position_y = y_axis
                    self.position_x = x_axis
                    break  # remove this break to see max num of characters placed

            y_axis = random.randint(0, room.y_axis - 1)  # random position if none or invalid is passed
            x_axis = random.randint(0, room.x_axis - 1)

    def input_movement(self):

        while True:

            # getchar () returns a bite string b'x'
            char = getch()  # 1st call returns generic keycode for function keys
            if char == b'\x00':
                char = getch()  # 2nd call returns keycode for function keys

            if char == b'H':  # north
                return [self.position_y - 1, self.position_x]
            elif char == b'P':  # south
                return [self.position_y + 1, self.position_x]
            elif char == b'K':  # west
                return [self.position_y, self.position_x - 1]
            elif char == b'M':  # east
                return [self.position_y, self.position_x + 1]
            elif char.upper() == b'Q':  # quit game
                return [-1, -1]

    # TODO:monster movement algorith also goes here

    def move(self, room, new_position):

        if -1 < new_position[0] < room.y_axis and -1 < new_position[1] < room.x_axis:  # if not out of range

            if room.grid[new_position[0]][new_position[1]] == ".":  # if spot is free
                room.grid[self.position_y][self.position_x] = "."  # erase from previous position
                room.grid[new_position[0]][new_position[1]] = self.appearance
                self.position_y = new_position[0]  # position update
                self.position_x = new_position[1]
                return True  # 2 is player still in room
            elif room.grid[new_position[0]][new_position[1]] == "#":  # if wall is hit
                return True
            elif room.grid[new_position[0]][new_position[1]] == "M":  # if attack monster
                # attack function ()
                return True
        # place_player_new room
        return False


#   STARTING ROOM   ######################################

current_room = Room(10,5)
current_room.place_doors(1)

player = Character(player=True)
monster1 = Character()

player.place(current_room)
monster1.place(current_room)

current_room.print_room()


#   GAME LOOP   ###########################################
end_game = False
while not end_game:
    movement = player.input_movement()
    if movement == [-1, -1]:
        end_game = True
        continue
    if player.move(current_room, movement):
        current_room.print_room()
    else:
        print ("Next room")
        break

print("Game over")


# DRAFT OF ENTERING NEXT ROOM SCRIPT
# next_room = Room()
# Room.database.append(current_room) # this must be done when player leaves room.
# player.place(next_room, position_y, position_x)
# current_room = next_room
# del next_room
