from random import randint

from constraint import *

import pygame

# Width and Height of Images representing each Square/Tile
IMG_SIZE = 40

pygame.init()

# Number of Rows, Columns and Mines for EASY Difficulty
EASY_ROWS = 8
EASY_COLS = 10
EASY_MINES = 10

# Number of Rows, Columns and Mines for MEDIUM Difficulty
MEDIUM_ROWS = 14
MEDIUM_COLS = 18
MEDIUM_MINES = 40

# Number of Rows, Columns and Mines for HARD Difficulty
HARD_ROWS = 20
HARD_COLS = 24
HARD_MINES = 99


class Button:
    """Class for Button UI"""

    def __init__(self, color, x, y, width, height, text):
        """
        :param color: Color of the button
        :param x: X-coordinate for the button
        :param y: Y-coordinate for the button
        :param width: Width of the button
        :param height: Height of the button
        :param text: Button text
        """
        self.color = color
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text

    def draw(self, win, outline=None):
        """Method to draw the Button
        :param win: Pygame window on which to draw the button
        :param outline: Color value for outline of button, is 2 pixels thick (default: None)
        """
        if outline:
            pygame.draw.rect(win, outline, (self.x - 2, self.y -
                                            2, self.width + 4, self.height + 4), 0)

        pygame.draw.rect(win, self.color, (self.x, self.y,
                                           self.width, self.height), 0)

        font = pygame.font.SysFont('consolas', 14, bold=True)
        text = font.render(self.text, 1, (255, 255, 255))
        win.blit(text,
                 (self.x + int(self.width / 2 - text.get_width() / 2),
                  self.y + int(self.height / 2 - text.get_height() / 2)))

    def isOver(self, pos):
        """Method to check if mouse position or any tuple position is over the button
        :param pos: (x, y) position tuple
        :return: True if pos is over/inside the button area else False
        """
        if self.x < pos[0] < self.x + self.width:
            if self.y < pos[1] < self.y + self.height:
                return True
        return False


class Text:
    """Class for Text UI"""

    def __init__(self, color, x, y, text):
        """
        :param color: Color of the text
        :param x: X-coordinate for the text
        :param y: Y-coordinate for the text
        :param text: String for text
        """
        self.color = color
        self.x = x
        self.y = y
        self.text = text

    def draw(self, win):
        """Method to draw the text object to the window
        :param win: Pygame window on which to draw the text
        """
        font = pygame.font.SysFont('consolas', 20)
        text = font.render(self.text, True, self.color, (0, 0, 0))
        win.blit(text, (self.x, self.y))


class Board:
    """Board class representing the Minefield in an array"""

    def __init__(self, board):
        self.board = board

    def __repr__(self):
        printTable(self.board)
        return "is your table"


class Square:  # Every piece in the board
    """
    Class to represent every tile/square in the game board
    """

    def __init__(self, x, y, w, h, board, ij):
        """
        :param x: X-Coordinate of the pygame window where Square is displayed
        :param y: Y-Coordinate of the pygame window where Square is displayed
        :param w: Width of square
        :param h: Height of square
        :param board: 2D array representing Minesweeper game i.e. Board object
        :param ij: Tuple (i, j) representing index in the board
        """
        self.rect = pygame.rect.Rect(x, y, w, h)
        self.i, self.j = ij
        self.val = board[self.i][self.j]
        self.x = x
        self.y = y
        self.visible: bool = False
        self.flag: bool = False
        self.flagAI: bool = False
        self.safe: bool = False

    def __getitem__(self, arg):
        """
        To get different attributes using Bracket notation
        :param arg: Attribute string
        :return: Attribute value if found
        """
        if arg == 'val':
            return self.val
        elif arg == 'visible':
            return self.visible
        elif arg == 'flagAI':
            return self.flagAI
        elif arg == 'safe':
            return self.safe
        else:
            return 'ERROR: No Items set.'


def mine(rows, cols, bombs):
    """
    Creates a 2D array for mine field
    :param rows: Rows of array/Minefield
    :param cols: Columns of array/Minefield
    :param bombs: Number of bombs/mines to place
    :return: Array of size 'rows' x 'cols' with 'bombs' number of 9's and correct hint number for a minesweeper game
    """
    table = [
        [0] * cols for i in range(rows)]  # Array of size 'rows' x 'cols' with all elements being 0
    table = addBombs(table, bombs)
    table = changeTable(table)
    return table


def addBombs(table, bombs, safe_indices=None):
    """
    Adds bombs represented by 9 to the table
    safe_indices is provided so that the index of user's first clicked tile and its surrounding don't contain a mine
    :param table: 2D array
    :param bombs: Number of bombs to add to the table
    :param safe_indices: Indices where bombs shouldn't be placed (default: None)
    :return: 2D array with correct number of new bombs(9) added to the argument array
    """
    for _ in range(bombs):
        is_bomb = False
        while not is_bomb:
            x = randint(0, len(table) - 1)
            y = randint(0, len(table[0]) - 1)

            if safe_indices is not None:
                if table[x][y] != 9 and [x, y] not in safe_indices:
                    table[x][y] = 9
                    is_bomb = True
            else:
                if table[x][y] != 9:
                    table[x][y] = 9
                    is_bomb = True
    return table


def changeTable(table):
    """
    Changes table values which are not bomb/mine to show correct number of bombs around that place
    :param table: 2D array with bombs represented by 9 and all other elements 0
    :return: 2D array with correct hint numbers based on how many bombs are around
    """
    for i in range(len(table)):
        for j in range(len(table[0])):
            if table[i][j] == 9:
                for index in getSurroundingIndices(table, i, j):
                    if table[index[0]][index[1]] != 9:
                        table[index[0]][index[1]] += 1
    return table


def printTable(table):
    """Prints the minefield table in somewhat formatted way"""
    for i in table:
        print(i)


def resetHintsValue(table):
    """
    Corrects the hints value of the game
    Is called only if the initialized mine should be changed if user's first click is not a zero(0) tile
    :param table: 2D array representing Minefield
    :return: 2D array with correct hint numbers based on how many bombs are around
    """
    for i in range(len(table)):
        for j in range(len(table[0])):
            if table[i][j] != 9:
                table[i][j] = 0
    return changeTable(table)


def getSurroundingIndices(table, row, col):
    """
    Helper function to find valid indices around an index
    :param table: 2D array
    :param row: Row index
    :param col: Column index
    :return: List of indices available in the 'table' around the 'row' and 'column' element
    """
    SURROUNDING = ((-1, -1), (-1, 0), (-1, 1),
                   (0, -1), (0, 1),
                   (1, -1), (1, 0), (1, 1))

    possibleIndices = []
    for pos in SURROUNDING:
        temp_row = row + pos[0]
        temp_col = col + pos[1]
        if 0 <= temp_row < len(table) and 0 <= temp_col < len(table[0]):
            possibleIndices.append([temp_row, temp_col])

    return possibleIndices


def getHowManyAndWhereAround(listOfSquares, row, col, checkAttribute, checkValue):
    """
    Helper function to obtain which Squares around a square have their checkAttribute value equal to checkValue
    :param listOfSquares: List of all Square Objects in the current game
    :param row: Row index of the square whose surroundings are to be checked
    :param col: Column index of the square whose surroundings are to be checked
    :param checkAttribute: List of attributes of Square object to be checked in surrounding Square objects
    :param checkValue: List of values the attribute of Square object should have in surrounding Square objects
    :return: Count of Square objects around the Square that have checkAttribute value = checkValue and their Indices
    """
    count = 0
    valueLoc = []
    for index in getSurroundingIndices(listOfSquares, row, col):
        ti = index[0]
        tj = index[1]
        actualValues = []
        for attribute in checkAttribute:
            actualValues.append(listOfSquares[ti][tj][attribute])
        if actualValues == checkValue:
            count += 1
            valueLoc.append([ti, tj])
    return count, valueLoc


def restart(rows, cols, bombs):
    """
    Function to restart the game
    :param rows: Rows of new Minesweeper game
    :param cols: Columns of new Minesweeper game
    :param bombs: Number of bombs in new game
    """
    game(rows, cols, bombs)


def openGame(listOfSquares, square):
    """
    Function to open up the Squares in the game when the player clicks on a zero(0) tile/square
    Recursively checks the surrounding indices until a square with value other than 0 is found.
    :param listOfSquares: List of all Square Objects in the current game
    :param square: the Square object with val attribute equal to zero
    """
    square.visible = True
    j, i = square.x // IMG_SIZE, square.y // IMG_SIZE

    for index in getSurroundingIndices(listOfSquares, i, j):
        ti = index[0]
        tj = index[1]
        if not listOfSquares[ti][tj].visible and not listOfSquares[ti][tj].flag:
            listOfSquares[ti][tj].visible = True
            if listOfSquares[ti][tj].val == 0:
                openGame(listOfSquares, listOfSquares[ti][tj])


def updateListOfSquares(rows, cols, board):
    """
    Function to create a new List of Squares
    :param rows: Number of rows in the board
    :param cols: Number of columns in the board
    :param board: 2D Array representing the game i.e. Board object
    :return: New correct List of all Squares in the game
    """
    listOfSquares = [[] for i in range(rows)]
    for i in range(0, rows * IMG_SIZE, IMG_SIZE):
        for j in range(0, cols * IMG_SIZE, IMG_SIZE):
            listOfSquares[i // IMG_SIZE] += [Square(j, i, IMG_SIZE, IMG_SIZE, board, (i // IMG_SIZE, j // IMG_SIZE))]
    return listOfSquares


""" The helper AI part begins from here."""


def getAllMineNeighbours(listOfSquares):
    """
    Shows All Mine Neighbours (AMNs). Straight-forward Logic.
    AMNs are tiles that certainly contain a mine because the number of covered tiles around a
    Square/tile is equal to its value(hint).
    Called by Show All Mine Neighbours Button i.e. AMN_Button
    :param listOfSquares: List of all Square Objects in the current game
    :return: True if new AMNs found else False
    """
    foundAMN = False
    for i in listOfSquares:
        for j in i:
            if j.visible and (j.val != 0):
                if j.val == getHowManyAndWhereAround(listOfSquares, j.i, j.j, ['visible'], [False])[0]:
                    for index in getHowManyAndWhereAround(listOfSquares, j.i, j.j, ['visible'], [False])[1]:
                        if not listOfSquares[index[0]][index[1]].flagAI:
                            listOfSquares[index[0]][index[1]].flagAI = True
                            foundAMN = True
                        # print("Mine at Index:", index)
    return foundAMN


def getAllFreeNeighbours(listOfSquares):
    """
    Shows All Free Neighbours (AFNs). Straight-forward Logic.
    AFNs are tiles that certainly do NOT contain a mine because the number of correctly flagged tiles around a
    Square/tile is equal to its value(hint) and some other tiles are still present around the square/tile.
    Called by Show All Free Neighbours Button i.e. AFN_Button
    :param listOfSquares: List of all Square Objects in the current game
    :return: True if new AFNs found else False
    """
    foundAFN = False
    getAllMineNeighbours(listOfSquares)
    for i in listOfSquares:
        for j in i:
            if j.visible and (j.val != 0):
                if j.val == getHowManyAndWhereAround(listOfSquares, j.i, j.j, ['flagAI'], [True])[0]:
                    mineIndices = getHowManyAndWhereAround(
                        listOfSquares, j.i, j.j, ['flagAI'], [True])[1]
                    for index in getSurroundingIndices(listOfSquares, j.i, j.j):
                        if index not in mineIndices:
                            ti, tj = index
                            if not (listOfSquares[ti][tj].visible or listOfSquares[ti][tj].flagAI or
                                    listOfSquares[ti][tj].safe):
                                listOfSquares[ti][tj].safe = True
                                listOfSquares[ti][tj].flag = False
                                foundAFN = True
                                # print("Safe tile at index:", index)
    return foundAFN


def createConstraintEquation(listOfSquares, square):
    """
    Helper Function to get constraint parameters required for equation
    This returns None if the constraint is trivial or if square is not visible
    :param listOfSquares: List of Square objects in the game
    :param square: A Square object
    :return: Tuple representing square index, ExactSumConstraint value and Variables List
    """
    if not square.visible or square.val == 0:
        return None
    tileValue = square.val  # This gives number of mines around the square
    variablesList = []
    mineOccurrences, mineCoordinates = getHowManyAndWhereAround(
        listOfSquares, square.i, square.j, ['flagAI'], [True])
    unknownOccurrences, unknownCoordinates = getHowManyAndWhereAround(listOfSquares, square.i, square.j,
                                                                      ['visible', 'flagAI', 'safe'],
                                                                      [False, False, False])
    if unknownOccurrences == 0:
        return None
    # Since the variables should add up to number of mines - number of known mines
    tileValue -= mineOccurrences
    for unknownCoordinate in unknownCoordinates:
        # Variables for Square[i][j] is named as a string 'i_j'
        variablesList.append(
            str(unknownCoordinate[0]) + "_" + str(unknownCoordinate[1]))
    return (square.i, square.j), tileValue, variablesList


def getConstraints(listOfSquares):
    """
    Calls the createConstraintEquation function to get all possible constraints for the current game state
    :param listOfSquares: List of all Square Objects in the current game
    :return: List of all possible constraint equation parameters
    """
    constraintList = []
    for row in listOfSquares:
        for square in row:
            constraintEq = createConstraintEquation(listOfSquares, square)
            if constraintEq is not None:
                constraintList.append(constraintEq)
    # printTable(constraintList)
    return constraintList


def takeActions(listOfSquares):
    """
    Function to explore tiles/squares marked safe and flag squares found to be mines by the AI
    This is called when the Take AI Actions button is pressed
    :param listOfSquares: List of Squares objects in the game
    :return: True if it took some actions(explore/flag) else False
    """
    tookActions = False
    for row in listOfSquares:
        for square in row:
            if not square.visible:
                if square.safe:
                    square.visible = True
                    if square.val == 0:
                        openGame(listOfSquares, square)
                    tookActions = True
                elif square.flagAI and not square.flag:
                    square.flag = True
                    tookActions = True
    return tookActions


def cspSolver(listOfSquares):
    """
    Function to find safe and mine tiles by formulating current game state as a Constraint Satisfaction Problem and
    generating necessary solutions.
    Called by Solve using CSP Button press i.e. CSP_Button
    If the generated solutions are consistent then and only then it shows hints for safe and mine tiles.
    CSP is modelled as follows:
        Variable: String 'i_j' where i and j are row-index and column index of hidden cell that is not known to be mine.
                This is to ensure a single hidden cell always gets the same Variable name for all constraints
        Domain: [0, 1] where 0 represents safe tile and 1 represents mine
        Constraint: Variable around a visible square with value 'n' should sum to 'n'
                    If 'm' hidden tiles are known to be mines then
                        Variable around a visible square with value 'n' should sum to 'n-m'
    This particular function initially checks two constraints with at least a common variable. Also known as
        "Coupled Subsets CSP"
    If it fails to find new safe/mine tiles, then it calls cspSolver3D() which may then call globalCSP().
    :param listOfSquares: List of all Square Objects in the current game
    :return: True if finds new safe and/or mine tiles using CSP else False
    """
    foundConsistentSolution = False
    print("Trying Straight-Forward Logic.")
    foundConsistentSolution = getAllFreeNeighbours(listOfSquares)
    print("Trying Coupled Subsets CSP.")
    constraintProblem = Problem()
    constraintList = getConstraints(listOfSquares)
    printTable(constraintList)

    for x in range(0, len(constraintList) - 1):
        for y in range(x + 1, len(constraintList)):
            constraintProblem.reset()
            constraint1 = constraintList[x]
            constraint2 = constraintList[y]
            c1_Index, c1_Value, c1_Variables = constraint1
            c2_Index, c2_Value, c2_Variables = constraint2
            uniqueVariables = list(set(c1_Variables + c2_Variables))
            if len(uniqueVariables) == len(c1_Variables + c2_Variables):
                break  # If there are no common variables, the CSP will never give consistent solution
            constraintProblem.addVariables(uniqueVariables, [0, 1])
            constraintProblem.addConstraint(
                ExactSumConstraint(c1_Value), c1_Variables)
            constraintProblem.addConstraint(
                ExactSumConstraint(c2_Value), c2_Variables)
            solutions = constraintProblem.getSolutions()
            # printTable(solutions)
            # print("X:", x, "Y:", y)
            if len(solutions) != 0:
                for variable in uniqueVariables:
                    firstVal = solutions[0][variable]
                    print("\nValue in first found solution is",
                          firstVal, "of variable", variable)
                    isConsistent = True
                    for solution in solutions[1:]:
                        print("Value in another instance:", solution[variable])
                        if solution[variable] != firstVal:
                            isConsistent = False
                            break
                    if isConsistent:
                        foundConsistentSolution = True
                        print("Found consistent", variable,
                              "with value", firstVal)
                        decodedX = int(variable.split('_')[0])
                        decodedY = int(variable.split('_')[1])
                        if firstVal == 0:
                            listOfSquares[decodedX][decodedY].safe = True
                        if firstVal == 1:
                            listOfSquares[decodedX][decodedY].flagAI = True
    if not foundConsistentSolution:
        return cspSolver3D(listOfSquares)
    else:
        return True


def cspSolver3D(listOfSquares):
    """
    Additional Function to find safe and mine tiles by formulating current game state as
    a Constraint Satisfaction Problem and
    generating necessary solutions similar to cspSolver.
    If the generated solutions are consistent then and only then it shows hints for safe and mine tiles.
    CSP is modelled as follows:
        Variable: String 'i_j' where i and j are row-index and column index of hidden cell that is not known to be mine.
                This is to ensure a single hidden cell always gets the same Variable name for all constraints
        Domain: [0, 1] where 0 represents safe tile and 1 represents mine
        Constraint: Variable around a visible square with value 'n' should sum to 'n'
                    If 'm' hidden tiles are known to be mines then
                        Variable around a visible square with value 'n' should sum to 'n-m'
    This particular function checks three (3) constraints say C1, C2 and C3
        if C1 and C2 share a common variable and C1 or C2 share a common variable with C3.
    Also, this function is ONLY called if cspSolver() fails to find any safe and/or mine tiles
    If this function fails to find any new safe/mine tiles, it calls globalCSP() as a last ditch effort.
    :param listOfSquares: List of all Square Objects in the current game
    :return: True if finds new safe and/or mine tiles using CSP else False
    """
    print("\nTrying 3 subsets CSP.")
    constraintProblem = Problem()
    constraintList = getConstraints(listOfSquares)
    printTable(constraintList)
    foundConsistentSolution = False
    for x in range(0, len(constraintList) - 2):
        for y in range(x + 1, len(constraintList) - 1):
            for z in range(y + 1, len(constraintList)):
                constraintProblem.reset()
                constraint1 = constraintList[x]
                constraint2 = constraintList[y]
                c1_Index, c1_Value, c1_Variables = constraint1
                c2_Index, c2_Value, c2_Variables = constraint2
                uniqueVariables = list(set(c1_Variables + c2_Variables))
                commonVariablesCount = len(
                    c1_Variables + c2_Variables) - len(uniqueVariables)
                if commonVariablesCount == 0:
                    break  # If there are no common variables, the CSP will never give consistent solution
                else:
                    constraint3 = constraintList[z]
                    c3_Index, c3_Value, c3_Variables = constraint3
                    length = len(uniqueVariables + c3_Variables)
                    uniqueVariables = list(set(uniqueVariables + c3_Variables))
                    if len(uniqueVariables) == length:
                        break

                constraintProblem.addVariables(uniqueVariables, [0, 1])
                constraintProblem.addConstraint(
                    ExactSumConstraint(c1_Value), c1_Variables)
                constraintProblem.addConstraint(
                    ExactSumConstraint(c2_Value), c2_Variables)
                constraintProblem.addConstraint(
                    ExactSumConstraint(c3_Value), c3_Variables)
                solutions = constraintProblem.getSolutions()

                if len(solutions) != 0:
                    for variable in uniqueVariables:
                        firstVal = solutions[0][variable]
                        print("\nValue in first found solution is",
                              firstVal, "of variable", variable)
                        isConsistent = True
                        for solution in solutions[1:]:
                            print("Value in another instance:",
                                  solution[variable])
                            if solution[variable] != firstVal:
                                isConsistent = False
                                break
                        if isConsistent:
                            foundConsistentSolution = True
                            print("Found consistent", variable,
                                  "with value", firstVal)
                            decodedX = int(variable.split('_')[0])
                            decodedY = int(variable.split('_')[1])
                            if firstVal == 0:
                                listOfSquares[decodedX][decodedY].safe = True
                            if firstVal == 1:
                                listOfSquares[decodedX][decodedY].flagAI = True
    if not foundConsistentSolution:
        return globalCSP(listOfSquares)
    else:
        return True


def globalCSP(listOfSquares):
    """
    Additional Function to find safe and mine tiles by formulating current game state as
    a Constraint Satisfaction Problem and
    generating necessary solutions similar to cspSolver and cspSolver3D.
    If the generated solutions are consistent then and only then it shows hints for safe and mine tiles.
    CSP is modelled as follows:
        Variable: String 'i_j' where i and j are row-index and column index of hidden cell that is not known to be mine.
                This is to ensure a single hidden cell always gets the same Variable name for all constraints
        Domain: [0, 1] where 0 represents safe tile and 1 represents mine
        Constraint: Variable around a visible square with value 'n' should sum to 'n'
                    If 'm' hidden tiles are known to be mines then
                        Variable around a visible square with value 'n' should sum to 'n-m'
    Additionally, this function also adds the constraint that
        all hidden unknown cells must sum up to number of mines remaining to be flagged
        if the number of flags to be placed is considered small enough. Currently it is less than or equal to 5.
        This constraint is a popular EndGame tactic in Minesweeper.
    This particular function tries to find solution/s satisfying all the constraints.
    Also, this function is ONLY called if both cspSolver() and cspSolver3D fails to find any safe and/or mine tiles.
    NOTE: This is a final desperate attempt to find a consistent solution.
    :param listOfSquares: List of all Square Objects in the current game
    :return: True if finds new safe and/or mine tiles using CSP else False
    """
    print("I'm using Global Solver now.")
    constraintProblem = Problem()
    constraintList = getConstraints(listOfSquares)
    printTable(constraintList)
    foundConsistentSolution = False
    allVariables = []
    for constraint in constraintList:
        c_Index, c_Value, c_Variables = constraint
        allVariables += c_Variables
        constraintProblem.addConstraint(
            ExactSumConstraint(c_Value), c_Variables)

    nMines = 0
    nFlagged = 0
    for sRows in listOfSquares:
        for sq in sRows:
            if sq.val == 9:
                nMines += 1
            if sq.flagAI:
                nFlagged += 1
    if nMines - nFlagged <= 5:
        for sRows in listOfSquares:
            for sq in sRows:
                if not sq.visible and not sq.flagAI and not sq.safe:
                    allVariables.append(str(sq.i) + '_' + str(sq.j))

    uniqueVariables = list(set(allVariables))
    if nMines - nFlagged <= 5:
        constraintProblem.addConstraint(
            ExactSumConstraint(nMines - nFlagged), uniqueVariables)
    constraintProblem.addVariables(uniqueVariables, [0, 1])

    solutions = constraintProblem.getSolutions()
    if len(solutions) != 0:

        for variable in uniqueVariables:
            firstVal = solutions[0][variable]
            print("\nValue in first found solution is",
                  firstVal, "of variable", variable)
            isConsistent = True
            for solution in solutions[1:]:
                print("Value in another instance:", solution[variable])
                if solution[variable] != firstVal:
                    isConsistent = False
                    break
            if isConsistent:
                foundConsistentSolution = True
                print("Found consistent", variable, "with value", firstVal)
                decodedX = int(variable.split('_')[0])
                decodedY = int(variable.split('_')[1])
                if firstVal == 0:
                    listOfSquares[decodedX][decodedY].safe = True
                if firstVal == 1:
                    listOfSquares[decodedX][decodedY].flagAI = True
    if not foundConsistentSolution:
        return False
    else:
        return True


def game(rows, cols, bombs):
    """
    Main Function for the game logic and initializations
    :param rows: Number of Rows for the game
    :param cols: Number of Columns for the game
    :param bombs: Number of Bombs in the game
    """
    noOfFlags = 0  # Variable to count how many flags the user has placed

    """Initialize/Load all the images"""
    grey = pygame.image.load("Images/grey.png")  # Hidden Squares
    safe = pygame.image.load("Images/safe.png")  # Hidden Squares marked safe by the AI

    AMN_Tip = pygame.image.load("Images/Hints LOL/AMN.png")  # AMN Tooltip
    AFN_Tip = pygame.image.load("Images/Hints LOL/AFN.png")  # AFN Tooltip
    CSP_Tip = pygame.image.load("Images/Hints LOL/CSP.png")  # CSP Tooltip
    AIMove_Tip = pygame.image.load("Images/Hints LOL/Take.png")  # AI Move Actions Tooltip
    Reset_Tip = pygame.image.load("Images/Hints LOL/black.png")  # Reset Tooltip area

    zero = pygame.image.load("Images/zero.png")
    one = pygame.image.load("Images/one.png")
    two = pygame.image.load("Images/two.png")
    three = pygame.image.load("Images/three.png")
    four = pygame.image.load("Images/four.png")
    five = pygame.image.load("Images/five.png")
    six = pygame.image.load("Images/six.png")
    seven = pygame.image.load("Images/seven.png")
    eight = pygame.image.load("Images/eight.png")
    nine = pygame.image.load("Images/nine.png")

    flag = pygame.image.load("Images/flag.png")  # Flagged by user
    flagAI = pygame.image.load("Images/flagAI.png")  # Flagged by AI

    # Array of images to show correct image based on the Square.val
    numbers = [zero, one, two, three, four, five, six, seven, eight, nine]

    c = Board(mine(rows, cols, bombs))
    W = len(c.board[0]) * IMG_SIZE  # Width occupied by game Squares
    H = len(c.board) * IMG_SIZE  # Height occupied by game Squares
    print(c)
    screen = pygame.display.set_mode((W + 250, H + 120))

    """Initializing the UI objects"""
    AMN_Button = Button((0, 0, 200), W + 25, 10, 200,
                        60, "Show All MINE Neighbours")
    AFN_Button = Button((0, 0, 200), W + 25, 80, 200,
                        60, "Show All FREE Neighbours")
    CSP_Button = Button((0, 0, 200), W + 25, 150, 200, 60, "Solve using CSP")
    AIMove_Button = Button((0, 0, 200), W + 25, 220,
                           200, 60, "Take AI actions")
    CheatToClearAIText = Button((0, 0, 0), 10, H + 45, W + 240, IMG_SIZE, "")
    Mines_Text = Text((255, 255, 255), 10, H + 5, "Mines: " + str(bombs))
    Flags_Text = Text((255, 255, 255), 150, H + 5, "Flags: " + str(noOfFlags))
    AI_Text = Text((255, 255, 255), 10, H + 45, "")
    EndGame_Text = Text((255, 255, 255), 10, H + 85, "")
    Tooltip_Pos = (W, 290)

    listOfSquares = updateListOfSquares(rows, cols, c.board)
    run = True
    hasNotClickedTile = True  # Boolean to check if a tile exploration is user's first click
    while run:
        noOfFlags = 0
        AMN_Button.draw(screen, (255, 255, 255))
        AFN_Button.draw(screen, (255, 255, 255))
        CSP_Button.draw(screen, (255, 255, 255))
        AIMove_Button.draw(screen, (255, 255, 255))
        Mines_Text.draw(screen)

        for event in pygame.event.get():
            mousePos = pygame.mouse.get_pos()
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    run = False
                    restart(rows, cols, bombs)
            # Left Click Event
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                """Call necessary function on each button press"""
                if AMN_Button.isOver(mousePos):
                    print("I'll now show you all MINE neighbours.")
                    if getAllMineNeighbours(listOfSquares):
                        AI_Text.text = "AI: I found some Mine neighbours"
                    else:
                        AI_Text.text = "AI: Couldn't find any mine neighbours. Try CSP or open more tiles."
                    CheatToClearAIText.draw(screen)
                    AI_Text.draw(screen)

                if AFN_Button.isOver(mousePos):
                    print("I'll now show you all FREE neighbours.")
                    if getAllFreeNeighbours(listOfSquares):
                        AI_Text.text = "AI: I found some Free neighbours"
                    else:
                        AI_Text.text = "AI: Couldn't find any safe neighbours. Try CSP or open more tiles."
                    CheatToClearAIText.draw(screen)
                    AI_Text.draw(screen)

                if CSP_Button.isOver(mousePos):
                    print("I'll now show you all solutions I found using CSP.")
                    if cspSolver(listOfSquares):
                        AI_Text.text = "AI: Hey, Look I found some certain safe and mine tiles using Facts and Logic."
                    else:
                        AI_Text.text = "AI: This is so Sad. I couldn't find any consistent solution."
                    CheatToClearAIText.draw(screen)
                    AI_Text.draw(screen)

                if AIMove_Button.isOver(mousePos):
                    print("I'll now show you all solutions I found using CSP.")
                    if takeActions(listOfSquares):
                        AI_Text.text = "AI: I flagged the found mines and opened found safe tiles."
                    else:
                        AI_Text.text = "AI: No mines to flag or tiles to open. Try solving first."
                    CheatToClearAIText.draw(screen)
                    AI_Text.draw(screen)

                """Perform necessary Actions based on the tile/Square clicked"""
                for i in listOfSquares:
                    for j in i:
                        r = pygame.rect.Rect(mousePos, (1, 1))
                        if j.rect.colliderect(r):
                            if j.flag == False and j.visible == False and j.flagAI == False:
                                if hasNotClickedTile:
                                    # This is what ensures the first clicked tile and its surrounding is never a mine
                                    hasNotClickedTile = False
                                    if j.val != 0:
                                        safeIndices = getSurroundingIndices(
                                            c.board, j.i, j.j)
                                        safeIndices.append([j.i, j.j])
                                        # print(safeIndices)
                                        # Number of mines around the first clicked tile which is to be moved elsewhere
                                        noOfBombs = getHowManyAndWhereAround(
                                            listOfSquares, j.i, j.j, ['val'], [9])[0]
                                        # print("i:", j.i, "j:", j.j)
                                        if j.val == 9:
                                            # If the users' first click was a mine, it should also be moved elsewhere
                                            noOfBombs += 1
                                            c.board[j.i][j.j] = 0
                                        j.val = 0
                                        c.board = addBombs(
                                            c.board, noOfBombs, safeIndices)
                                        for index in getHowManyAndWhereAround(listOfSquares, j.i, j.j, ['val'], [9])[1]:
                                            # Diffuse all mines around the first clicked tile
                                            c.board[index[0]][index[1]] = 0
                                        c.board = resetHintsValue(c.board)
                                        listOfSquares = updateListOfSquares(
                                            rows, cols, c.board)
                                        print(c)
                                        listOfSquares[j.i][j.j].visible = True
                                        openGame(listOfSquares, j)
                                    print(
                                        "I changed the board for you. Your new board is:")
                                    print(c)

                                if j.val == 9:
                                    AI_Text.text = "AI: You clicked a mine. Now start a new game by pressing 'r'."
                                    EndGame_Text.text = "GAME OVER :("
                                    CheatToClearAIText.draw(screen)
                                    AI_Text.draw(screen)
                                    EndGame_Text.draw(screen)
                                    print("Game Over")
                                    run = False
                                j.visible = True
                                if j.val == 0:
                                    openGame(listOfSquares, j)
                                    j.visible = True
                                # printTable(currentPlayState(listOfSquares, bombs))

            # Right Click Event: To flag tiles as mines
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                for i in listOfSquares:
                    for j in i:
                        r = pygame.rect.Rect(mousePos, (1, 1))
                        if j.rect.colliderect(r):
                            if not j.visible:
                                j.flag = not j.flag

            # Mouse motion event, Change button color and show tooltip
            elif event.type == pygame.MOUSEMOTION:
                screen.blit(Reset_Tip, Tooltip_Pos)
                if AMN_Button.isOver(mousePos):
                    AMN_Button.color = (0, 0, 255)
                    screen.blit(AMN_Tip, Tooltip_Pos)
                else:
                    AMN_Button.color = (0, 0, 200)
                if AFN_Button.isOver(mousePos):
                    AFN_Button.color = (0, 0, 255)
                    screen.blit(AFN_Tip, Tooltip_Pos)
                else:
                    AFN_Button.color = (0, 0, 200)
                if CSP_Button.isOver(mousePos):
                    CSP_Button.color = (0, 0, 255)
                    screen.blit(CSP_Tip, Tooltip_Pos)
                else:
                    CSP_Button.color = (0, 0, 200)
                if AIMove_Button.isOver(mousePos):
                    AIMove_Button.color = (0, 0, 255)
                    screen.blit(AIMove_Tip, Tooltip_Pos)
                else:
                    AIMove_Button.color = (0, 0, 200)

        """Display correct image for the Square based on its attributes"""
        for i in listOfSquares:
            for j in i:
                if j.visible:
                    screen.blit(numbers[j.val], (j.x, j.y))
                if j.flag:
                    noOfFlags += 1
                    screen.blit(flag, (j.x, j.y))
                if not j.flag and not j.visible:
                    screen.blit(grey, (j.x, j.y))
                if j.flagAI and not j.flag:
                    screen.blit(flagAI, (j.x, j.y))
                if j.safe and not j.visible:
                    screen.blit(safe, (j.x, j.y))
        Flags_Text.text = "Flags: " + str(noOfFlags)
        Flags_Text.draw(screen)

        countOfVisibleTiles = 0  # To check if the game is WON
        for i in listOfSquares:
            for j in i:
                if j.visible and j.val != 9:
                    countOfVisibleTiles += 1
            if countOfVisibleTiles == rows * cols - bombs:
                run = False
                AI_Text.text = "AI: Congratulations. You can press 'r' to start a new game"
                CheatToClearAIText.draw(screen)
                AI_Text.draw(screen)
                EndGame_Text.text = "You Won :)"
                EndGame_Text.draw(screen)
                print("You Won")

        pygame.display.update()

    for i in listOfSquares:
        for j in i:
            if j.val == 9:
                screen.blit(nine, (j.x, j.y))

    pygame.display.update()

    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    run = False
                    restart(rows, cols, bombs)


if __name__ == '__main__':
    print("This is a Minesweeper game with Helper AI.\nWhen prompted please choose your desired difficulty.")
    print("EASY:\t8x10 grid with 10 mines")
    print("MEDIUM:\t14x18 grid with 40 mines")
    print("HARD:\t20x24 grid with 99 mines")
    takingInput = True
    while takingInput:
        difficulty = input(
            "Enter 'E' for Easy, 'M' for Medium, 'H' for Hard and 'C' for custom: ")
        if difficulty in ['E', 'e']:
            takingInput = False
            game(EASY_ROWS, EASY_COLS, EASY_MINES)
        elif difficulty in ['M', 'm']:
            takingInput = False
            game(MEDIUM_ROWS, MEDIUM_COLS, MEDIUM_MINES)
        elif difficulty in ['H', 'h']:
            takingInput = False
            game(HARD_ROWS, HARD_COLS, HARD_MINES)
        elif difficulty in ['C', 'c']:
            rows = int(input("Enter Number of rows: "))
            cols = int(input("Enter number of columns: "))
            mines = int(input(
                "Enter number of mines to place (Should be less than 25% of the board size): "))
            if mines < (rows * cols) / 4:
                takingInput = False
                game(rows, cols, mines)
            else:
                print("Number of mines cannot be more than 25% of the board size.")
