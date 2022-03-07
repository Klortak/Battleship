from threading import Thread
import random
import socket
import time
import sys
import os

##################################
host = False

turns = 100

boardSize = 10
# Left justify text to keep aligned

##################################

# Add support for more than 26 rows
if boardSize > 26:
    raise IndexError('Out of bounds')

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

if host: 
    server.bind((socket.gethostname(), 1234))
    server.listen(5)
else:
    server.connect((socket.gethostname(), 1234))

client = None

def connectToClient():
  global client
  while True:
    client, address = server.accept()
    #print(f'Connection with {address[0]} successful')

def send(text):
    if host:
        client.send(text.encode('utf-8'))
    else:
        server.send(text.encode('utf-8'))

def receive():
    if host:
        return client.recv(1024).decode('utf-8')
    else:
        return server.recv(1024).decode('utf-8')

if host:
    t1 = Thread(target = connectToClient)
    t1.start()

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

            if len(self.possibleCoords) == 0: self.destroyed = True

        # If the there was a ship hit at current coord, don't set to miss
        elif grid[coord] != 3:
            grid[coord] = 2

# Returns the state of the selected area on the given board
def stateOfBoard(grid, coord):
    state = 'Error'
    if grid[coord] == 0: state = 'Empty'
    elif grid[coord] == 1: state = 'Ship'
    elif grid[coord] == 2: state = 'Miss'
    elif grid[coord] == 3: state = 'Hit'
    return state

# Converts a number pair into a key for the grid
def numToCoord(x, y):
    return f'{chr(x + 64)}{y}'

# Adds in each key for the grid
userBoard = {}
for x in range(boardSize):
    for y in range(boardSize):
        userBoard[numToCoord(x + 1, y + 1)] = 0

ships = [
    Ship('Carrier', 5, userBoard),
    Ship('Battleship', 4, userBoard),
    Ship('Cruiser', 3, userBoard),
    Ship('Submarine', 3, userBoard),
    Ship('Destroyer', 2, userBoard)
]

winMsg = '''
 __   __         __      ___      
 \ \ / /__ _  _  \ \    / (_)_ _  
  \ V / _ \ || |  \ \/\/ /| | ' \ 
   |_|\___/\_,_|   \_/\_/ |_|_||_| 
    '''

loseMsg = '''
 __   __          _                
 \ \ / /__ _  _  | |   ___ ___ ___ 
  \ V / _ \ || | | |__/ _ (_-</ -_)
   |_|\___/\_,_| |____\___/__/\___|                                
    '''

def drawBoard(grid, showShips):
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
            if not showShips and currentPoint == 'X': currentPoint = 'O'
            print(currentPoint, end='    ')
        print('\n')

attackedCoords = []

playersTurn = host # Host goes first

# Runs as long as there are ships on the board and turns are left
while len(ships) > 0 and turns > 0:
    os.system('cls')
    drawBoard(userBoard, True)
    
    if playersTurn:
        # Send attack coordinates
        send(input('Enter a coordinate >>> '))

        # Recive state of that point on the board
        message = receive()

        # Game is won
        if message == winMsg:
            if host:
                server.close() # Closer server

            os.system('cls') # Clear screen
            print(message) # Display win message
            sys.exit(0) # Stop program
        else:
            # If a valid coordinate, continue
            print(message)
            if '#' not in message:
                playersTurn = False
    else:
        # Get the attack coordinates from the opponent
        print('Opponent\'s turn')
        coord = receive()

        try:
            if coord in attackedCoords:
                raise SyntaxError('Coordinate already attacked')

            if coord not in userBoard.keys():
                raise IndexError('Not valid coordinate')

            shipDestroyed = False
            # Iterate through all ships and check if the coordinates are a viable position
            for ship in ships:
                ship.attack(userBoard, coord)

                # If the ship has been destroyed, remove it from the list to prevent unecessary checks
                if ship.destroyed:
                    ships.remove(ship)

                    # All your ships have been destroyed
                    if len(ships) == 0:
                        os.system('cls')
                        send(winMsg) # Send win message to opponent
                        print(loseMsg) # Display lose message
                        sys.exit(0)

                    send('You sunk my ' + ship.name)
                    shipDestroyed = True

            # Get the state of the chosen point and send it to the opponent
            # If a ship was destroyed, that message has priority
            if not shipDestroyed: send(stateOfBoard(userBoard, coord))
            attackedCoords.append(coord)

            playersTurn = True
        except SyntaxError:
            send('### Coordinate has already been attacked ###')
        except IndexError:
            send('### Please enter a valid coordinate ###')

    turns -= 1
    time.sleep(1)


### TO-DO ###
# Make AI to play against?
# Handle win/lose message over server