import line_following

class robot:
    position = [0, 0]
    turn_direction = ['NORTH', 'EAST', 'SOUTH', 'WEST']
    direction = 'NORTH'

    def __init__(self, gX, gY):
        self.gridX = gX
        self.gridY = gY
        self.pos = [0, 0]
    
    def place(self, posX, posY, dir):
        self.pos = [posX, posY]
        self.direction = dir

    def turn_right(self):
        self.direction = self.turn_direction[(self.turn_direction.index(self.direction) + 1) % 4]
        line_following.turn_right_90()

    def turn_left(self):
        self.direction =  self.turn_direction[(self.turn_direction.index(self.direction) - 1) % 4]
        line_following.turn_left_90()

    def move_forward(self):
        if (self.direction == 'NORTH'):
            if ((self.pos[1]) == (self.gridY - 1)):
                print("This move would put the robot out of bounds")
            else:
                self.pos[1] += 1
                line_following.forward_step()
        elif (self.direction == 'SOUTH'):
            if ((self.pos[1]) == 0):
                print("This move would put the robot out of bounds")
            else:
                self.pos[1] -= 1
                line_following.forward_step()
        elif (self.direction == 'EAST'):
            if ((self.pos[0]) == self.gridX - 1):
                print("This move would put the robot out of bounds")
            else:
                self.pos[0] += 1
                line_following.forward_step()
        elif (self.direction == 'WEST'):
            if ((self.pos[0]) == 0):
                print("This move would put the robot out of bounds")
            else:
                self.pos[0] -= 1
                line_following.forward_step()

    def report(self):
        print("Robot position is:\nX: " + str(self.pos[0]) + "\nY: " + str(self.pos[1]) + "\nFacing: " + self.direction + "\n")


    def read_input(self):
        user_input = input("Please enter an instruction (MOVE, LEFT, RIGHT, REPORT, or 'e' to exit): ")
        user_input_str = str(user_input)
        user_input_array = user_input_str.split(",")
        if (len(user_input_array) == 1):
            match((user_input_array[0].strip()).upper()):
                case 'RIGHT':
                    self.turn_right()
                    return 0
                case 'LEFT':
                    self.turn_left()
                    return 0
                case 'MOVE':
                    self.move_forward()
                    return 0
                case 'REPORT':
                    self.report()
                    return 0
                case 'E':
                    return 1
                case _:
                    print("Invalid command")
        elif(len(user_input_array) == 4):
            if((user_input_array[0].strip()).upper() == 'PLACE'):
                if ((user_input_array[3].strip()).upper() in self.turn_direction):
                    if(int(user_input_array[1].strip()) < self.gridX and int(user_input_array[2].strip()) < self.gridY):
                        self.place(int(user_input_array[1].strip()), int(user_input_array[2].strip()), (user_input_array[3].strip()).upper())
                        return 0
        print("invalid input")
        return 0

if __name__ == "__main__":

    while True:
        try:
            gridX = int(input("Enter the size of the grid on the X axis: "))
            break  # Exit the loop if input is valid
        except ValueError:
            print("Invalid input. Please enter a valid integer.")

    while True:
        try:
            gridY = int(input("Enter the size of the grid on the Y axis: "))
            break  # Exit the loop if input is valid
        except ValueError:
            print("Invalid input. Please enter a valid integer.")
    
    line_following.setup_motors()

    r = robot(gridX, gridY)
    print("To place robot, type 'PLACE, <valid X coordinate>, <valid Y coordinate>, <valid direction, in CAPITAL LETTERS>'")
    while(True):
        ret = r.read_input()
        if (ret == 1):
            break
    print("Exiting...")