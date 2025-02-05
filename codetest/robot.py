import sys
sys.path.append('../')


class robot:
    position = [0, 0]
    direction = 'NORTH'

    def __init__(gX, gY):
        self.gridX = gX
        self.gridY = gY
    
    def place(posX, posY):
        position = [posX, posY]

    def turn(dir)
    turn = True
        if (dir == 'RIGHT'):
            match direction:
                case 'NORTH':
                    direction = 'EAST'
                    break
                case 'EAST':
                    direction = 'SOUTH'
                    break
                case 'SOUTH':
                    direction = 'WEST'
                    break
                case 'WEST'
                    direction = 'NORTH'
                    break
                case _:
                    print("Invalid input, please try again")
                    turn = False
                    break
            if turn:
                turn_right_90()
        else if (dir == 'LEFT'):
            match direction:
                case 'NORTH':
                    direction = 'WEST'
                    break
                case 'WEST':
                    direction = 'SOUTH'
                    break
                case 'SOUTH':
                    direction = 'EAST'
                    break
                case 'EAST'
                    direction = 'NORTH'
                    break
                case _:
                    print("Invalid input, please try again")
                    turn = False
                    break
            if turn:
                turn_right_90()
        else:
            print("The robot seems not to have a direction")
    
    def move():
        move = True
        match direction:
            case 'NORTH':
                if (position[1] < gridY - 1):
                    position[1] = position[1] + 1
                else:
                    print("This move would send the robot over the edge")
                break
            case 'WEST':
                if (position[0] < gridX - 1):
                    position[0] = position[0] + 1
                else:
                    print("This move would send the robot over the edge")
                break
            case 'SOUTH':
                if (position[1] > 0):
                    position[1] = position[1] - 1
                else:
                    print("This move would send the robot over the edge")
                break
            case 'EAST'
                if (position[0] > 0):
                    position[0] = position[0] - 1
                else:
                    print("This move would send the robot over the edge")
                break
            case _:
                print("Invalid input, please try again")
                move = False
                break
        if move:
            move_forward()

    def report_virtual():
        print("Currently at position x:" + position[0] + "\ny: " + position[1] + "\nFacing: " + direction)