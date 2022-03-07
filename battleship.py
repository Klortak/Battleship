import random
import time
import os

##################################

turns = 100

boardSize = 10
# Left justify text to keep aligned

##################################

# Add support for more than 26 rows
if boardSize > 26:
    raise IndexError('Out of bounds')

class Ship():
    def __init__(self, name, size, grid):
        self.name = name
        self.size = size
        self.possibleCoords = self.place(grid)
        self.destroyed = False

    def place(self, grid):
        # Set x and y out of bounds
        x, y = -self.size, -self.size
        dir = random.randint(0, 1)

        sizeLeft = self.size
        coords = []

        # Find starting coords that aren't occupied and are within bounds
        while not self.withinBounds(x, y, dir) or self.occupied(grid, x, y):
            x, y = random.randint(1, boardSize), random.randint(1, boardSize)

        # Checks that each coord is not occupied and is within bounds
        while self.withinBounds(x, y, dir) and not self.occupied(grid, x, y):
            sizeLeft -= 1
            # If all coordinates are chosen, return the coordinates
            if sizeLeft < 0:
                # If process finishes, tell the grid that those spots are occupied
                for key in coords:
                    grid[key] = 1
                return coords
            else:
                coords.append(numToCoord(x, y))
                if dir: x += 1
                else: y += 1
        # If coordinates are out of range / occupied, restart the process
        else:
            coords.clear()
            return self.place(grid)
    
    # If coordinate is in grid and isn't occupied return false, if isn't in grid return true
    def occupied(self, grid, x, y):
        return grid[numToCoord(x, y)] if numToCoord(x, y) in grid else True

    # If starting coord + size is withing bounds return true
    def withinBounds(self, x, y, dir):
        return (0 == dir and 1 <= (self.size + x) <= boardSize) or (boardSize >= (y + self.size) >= 1 and dir == 1)

    def attack(self, grid, coord):
        # If coordinate is equal to one of the ships coords, set to hit
        if coord in self.possibleCoords:
            self.possibleCoords.remove(coord)
            grid[coord] = 3

            if len(self.possibleCoords) == 0:
                print('You sunk my ' + self.name)
                self.destroyed = True

        # If the there was a ship hit at current coord, don't set to miss
        elif grid[coord] != 3:
            grid[coord] = 2

# Converts a number pair into a key for the grid
def numToCoord(x, y):
    return f'{chr(x + 64)}{y}'

# Adds in each key for the grid
board = {}
for x in range(boardSize):
    for y in range(boardSize):
        board[numToCoord(x + 1, y + 1)] = 0

ships = [
    Ship('Carrier', 5, board),
    Ship('Battleship', 4, board),
    Ship('Cruiser', 3, board),
    Ship('Submarine', 2, board),
    Ship('Destroyer', 2, board)
]

def drawBoard(grid, usersBoard):
    currentPoint = ''

    for x in range(-1, boardSize):
        for y in range(-1, boardSize):
            # Draw the outer coordinates on the board
            if x == -1:
                currentPoint = y + 1 if y >= 0 else ' '
            elif y == -1:
                currentPoint = chr(x + 65)    
            else: # Get type of point and draw it to the console
                if grid[numToCoord(x + 1, y + 1)] == 0:  currentPoint = 'O'     # Empty
                elif grid[numToCoord(x + 1, y + 1)] == 1: currentPoint = 'X'    # Ship
                elif grid[numToCoord(x + 1, y + 1)] == 2: currentPoint = '^'    # Miss
                elif grid[numToCoord(x + 1, y + 1)] == 3: currentPoint = '*'    # Hit

            # Only display ships if the current board is the user's
            if not usersBoard and currentPoint == 'X': currentPoint = 'O'
            print(currentPoint, end='    ')
        print('\n')

# Runs as long as there are ships on the board and turns are left
while len(ships) > 0 and turns > 0:
    os.system('cls')

    drawBoard(board, True) # Draw enemies board
    coord = input('Enter a coordinate >>> ')

    try:
        for ship in ships:
            ship.attack(board, coord)
            if ship.destroyed:
                ships.remove(ship)

        # Get the state of the chosen point and output it to the console
        if board[coord] == 2:
            print('Miss')
        elif board[coord] == 3:
            print('Hit')
    except:
        print('Please enter a valid coordinate')

    turns -= 1
    time.sleep(1)
else:
    os.system('cls')

    if len(ships) > 0:
        message = '''
        ╭╮╱╱╭╮╱╱╱╱╱╭╮╱╱╱╱╱╱╱╱╭╮
        ┃╰╮╭╯┃╱╱╱╱╱┃┃╱╱╱╱╱╱╱╭╯╰╮
        ╰╮╰╯╭┻━┳╮╭╮┃┃╱╱╭━━┳━┻╮╭╯
        ╱╰╮╭┫╭╮┃┃┃┃┃┃╱╭┫╭╮┃━━┫┃
        ╱╱┃┃┃╰╯┃╰╯┃┃╰━╯┃╰╯┣━━┃╰╮
        ╱╱╰╯╰━━┻━━╯╰━━━┻━━┻━━┻━╯
        '''
    else:
        message = '''
        ╭╮╱╱╭╮╱╱╱╱╱╭╮╭╮╭╮
        ┃╰╮╭╯┃╱╱╱╱╱┃┃┃┃┃┃
        ╰╮╰╯╭┻━┳╮╭╮┃┃┃┃┃┣━━┳━╮
        ╱╰╮╭┫╭╮┃┃┃┃┃╰╯╰╯┃╭╮┃╭╮╮
        ╱╱┃┃┃╰╯┃╰╯┃╰╮╭╮╭┫╰╯┃┃┃┃
        ╱╱╰╯╰━━┻━━╯╱╰╯╰╯╰━━┻╯╰╯
        '''

    print(message)


### TO-DO ###
# Make AI to play against
# Multiplayer?