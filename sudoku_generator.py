import pygame, math, random, copy, requests, sys
from io import BytesIO

# CONSTANTS

WIDTH = 594  # 603 is evenly divisible by 9
HEIGHT = WIDTH + 80  # add 95 pixels to the bottom for reset/restart/quit buttons
LINE_WIDTH = 3
LINE_WIDTH_2 = 5
WIN_LINE_WIDTH = 15
BOARD_ROWS = 9
BOARD_COLS = 9
SQUARE_SIZE = 66
CIRCLE_RADIUS = 60
CIRCLE_WIDTH = 15
CROSS_WIDTH = 25
SPACE = 55
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BG_COLOR = (255, 255, 245)
LINE_COLOR = (0, 0, 0)
SKETCH_COLOR = (155, 155, 155)
PLACED_COLOR = (50, 90, 175)
VALUE_COLOR = (50, 50, 50)
BG_IMAGE_REQUEST = requests.get('https://live.staticflickr.com/52/150983118_21b4093a61.jpg')

"""
This was adapted from a GeeksforGeeks article "Program for Sudoku Generator" by Aarti_Rathi and Ankur Trisal
https://www.geeksforgeeks.org/program-sudoku-generator/

REFERENCES
1. ankthon. (2022, September 7). Python: Display images with pygame. GeeksforGeeks. https://www.geeksforgeeks.org/python-display-images-with-pygame/ 
2. Starbuck5. (n.d.). pygame module to transform surfaces. Pygame.transform - pygame v2.6.0 documentation. https://www.pygame.org/docs/ref/transform.html 
3. marios-pz. (n.d.). pygame module for loading and rendering fonts. pygame.font - pygame v2.6.0 documentation. https://www.pygame.org/docs/ref/font.html 
4. pygame.image - pygame v2.6.0 documentation. (n.d.). https://www.pygame.org/docs/ref/image.html 
5. How to load image from web URL in pygame. CodersLegacy. (2023, April 13). https://coderslegacy.com/python/load-image-from-web-url-pygame/ 
6. Purple Slog. (2006, May 22). Sudoku Template. https://www.flickr.com/photos/93453114@N00/150983118. 
"""

class SudokuGenerator:

    '''
	create a sudoku board - initialize class variables and set up the 2D board
	This should initialize:
	self.row_length		- the length of each row
	self.removed_cells	- the total number of cells to be removed
	self.board			- a 2D list of ints to represent the board
	self.box_length		- the square root of row_length

	Parameters:
    row_length is the number of rows/columns of the board (always 9 for this project)
    removed_cells is an integer value - the number of cells to be removed

	Return:
	None
    '''
    def __init__(self, row_length, removed_cells):
        self.row_length = row_length
        self.removed_cells = removed_cells
        self.board = []  # creates a square 2D array of 0's
        for i in range(0, row_length):
            self.board.append([])
            for j in range(0, row_length):
                self.board[i].append(0)
        self.box_length = math.floor(math.sqrt(row_length))

    '''
	Returns a 2D python list of numbers which represents the board

	Parameters: None
	Return: list[list]
    '''
    def get_board(self):
        return self.board

    '''
	Displays the board to the console
    This is not strictly required, but it may be useful for debugging purposes

	Parameters: None
	Return: None
    '''
    def print_board(self):
        print("___" * self.row_length)
        for row in self.board:
            for cell in row:
                print(cell, end="  ")
            print("|")
        print("___" * self.row_length, end="|\n")

    '''
	Determines if num is contained in the specified row (horizontal) of the board
    If num is already in the specified row, return False. Otherwise, return True

	Parameters:
	row is the index of the row we are checking
	num is the value we are looking for in the row
	
	Return: boolean
    '''
    def valid_in_row(self, row, num):
        for value in self.board[row]:  # check each value in given board
            if value == num:
                return False
        return True  # if it gets through entire row

    '''
	Determines if num is contained in the specified column (vertical) of the board
    If num is already in the specified col, return False. Otherwise, return True

	Parameters:
	col is the index of the column we are checking
	num is the value we are looking for in the column
	
	Return: boolean
    '''
    def valid_in_col(self, col, num):
        for row in self.board:
            if row[col] == num:  # checks given column value in each row
                return False
        return True  # if it gets through entire column

    '''
	Determines if num is contained in the 3x3 box specified on the board
    If num is in the specified box starting at (row_start, col_start), return False.
    Otherwise, return True

	Parameters:
	row_start and col_start are the starting indices of the box to check
	i.e. the box is from (row_start, col_start) to (row_start+2, col_start+2)
	num is the value we are looking for in the box

	Return: boolean
    '''
    def valid_in_box(self, row_start, col_start, num):
        for i in range(row_start, row_start + 2 + 1):
            for j in range(col_start, col_start + 2 + 1):  # '+ 1' is to offset the range excluding last number
                if self.board[i][j] == num:  # compare each value in box to given num
                    return False
        return True  # if it gets through the 3x3 box
    
    '''
    Determines if it is valid to enter num at (row, col) in the board
    This is done by checking that num is unused in the appropriate, row, column, and box

	Parameters:
	row and col are the row index and col index of the cell to check in the board
	num is the value to test if it is safe to enter in this cell

	Return: boolean
    '''
    def is_valid(self, row, col, num):
        if (self.valid_in_row(row, num)
                and self.valid_in_col(col, num)
                and self.valid_in_box((row // 3) * 3,(col // 3) * 3, num)):
            return True
        return False

    '''
    Fills the specified 3x3 box with values
    For each position, generates a random digit which has not yet been used in the box

	Parameters:
	row_start and col_start are the starting indices of the box to check
	i.e. the box is from (row_start, col_start) to (row_start+2, col_start+2)

	Return: None
    '''
    def fill_box(self, row_start, col_start):
        box_dict = {}
        for i in range(row_start, (row_start + 2 + 1)):
            for j in range(col_start, (col_start + 2 + 1)):  # '+ 1' is to offset the range excluding last number
                while self.board[i][j] == 0:  # keep retrying until cell successfully filled
                    num = random.randint(1, 9)  # random number 1 - 9
                    if num in box_dict.values():  # skip lengthy checks if value already used
                        continue
                    if self.is_valid(i, j, num):  # check if valid
                        self.board[i][j] = num  # if valid, set & end while loop
                        box_dict[num] = num  # save used values

    '''
    Fills the three boxes along the main diagonal of the board
    These are the boxes which start at (0,0), (3,3), and (6,6)

	Parameters: None
	Return: None
    '''
    def fill_diagonal(self):
        self.fill_box(0, 0)
        self.fill_box(3, 3)
        self.fill_box(6, 6)

    '''
    DO NOT CHANGE
    Provided for students
    Fills the remaining cells of the board
    Should be called after the diagonal boxes have been filled
	
	Parameters:
	row, col specify the coordinates of the first empty (0) cell

	Return:
	boolean (whether or not we could solve the board)
    '''
    def fill_remaining(self, row, col):
        if (col >= self.row_length and row < self.row_length - 1):
            row += 1
            col = 0
        if row >= self.row_length and col >= self.row_length:
            return True
        if row < self.box_length:
            if col < self.box_length:
                col = self.box_length
        elif row < self.row_length - self.box_length:
            if col == int(row // self.box_length * self.box_length):
                col += self.box_length
        else:
            if col == self.row_length - self.box_length:
                row += 1
                col = 0
                if row >= self.row_length:
                    return True
        
        for num in range(1, self.row_length + 1):
            if self.is_valid(row, col, num):
                self.board[row][col] = num
                if self.fill_remaining(row, col + 1):
                    return True
                self.board[row][col] = 0
        return False

    '''
    DO NOT CHANGE
    Provided for students
    Constructs a solution by calling fill_diagonal and fill_remaining

	Parameters: None
	Return: None
    '''
    def fill_values(self):
        self.fill_diagonal()
        self.fill_remaining(0, self.box_length)

    '''
    Removes the appropriate number of cells from the board
    This is done by setting some values to 0
    Should be called after the entire solution has been constructed
    i.e. after fill_values has been called
    
    NOTE: Be careful not to 'remove' the same cell multiple times
    i.e. if a cell is already 0, it cannot be removed again

	Parameters: None
	Return: None
    '''
    def remove_cells(self):
        removed = 0  # counter variable
        while removed < self.removed_cells:  # run until correct number removed
            row = random.randint(0, 8)  # offset by 1 because indexes
            col = random.randint(0, 8)
            if self.board[row][col] != 0:  # check cell isn't already removed
                self.board[row][col] = 0
                removed += 1


class Cell:

    def __init__(self, value, row, col, dimensions, screen):
        self.value = value
        self.sketched_value = 0
        self.user_placed = False
        self.row = row
        self.col = col
        self.width, self.height = dimensions  # dimensions is a tuple (width, height)
        self.screen = screen

    # value = locked-in guess/unchangeable numbers
    def set_cell_value(self, value):
        self.value = value

    # sketched value = user guess
    def set_sketched_value(self, value):
        self.sketched_value = value

    # user placed means it's a solidified sketch value -- info not given to user initially
    def set_user_placed(self):
        self.user_placed = True

    def draw(self):  # value --> cell.value, sketch --> cell.sketched_value
        cell_font = pygame.font.Font(None, 60)
        sketch_font = pygame.font.Font(None, 40)
        cell_value_surface = cell_font.render(str(self.value), 0, VALUE_COLOR)
        cell_placed_surface = cell_font.render(str(self.value), 0, PLACED_COLOR)
        cell_sketch_surface = sketch_font.render(str(self.sketched_value), 0, SKETCH_COLOR)

        # un-editable values -- black
        if self.value != 0 and not self.user_placed:
            cell_value_rectangle = cell_value_surface.get_rect(
                center=(self.width // 18 + self.width * self.col // 9, self.width // 18 + self.width * self.row // 9))
            screen.blit(cell_value_surface, cell_value_rectangle)

        # user-placed values -- blue
        elif self.value != 0 and self.user_placed:
            cell_placed_rectangle = cell_placed_surface.get_rect(
                center=(self.width // 18 + self.width * self.col // 9, self.width // 18 + self.width * self.row // 9))
            screen.blit(cell_placed_surface, cell_placed_rectangle)

        # sketched values -- gray & top left
        elif self.sketched_value != 0:
            cell_sketch_rectangle = cell_sketch_surface.get_rect(
                center=(self.width // 36 + self.width * self.col // 9, self.width // 36 + self.width * self.row // 9))
            screen.blit(cell_sketch_surface, cell_sketch_rectangle)


class Board:

    def __init__(self, width, height, screen, unsolved_board, solved_board):
        self.width = width  # screen width
        self.height = height  # screen height
        self.screen = screen  # window from PyGame
        self.selected_cell = None  # cell object of currently selected cell
        self.unsolved_board = unsolved_board  # 2d array of integers, unsolved board    -- (used for resetting)
        self.solved_board = solved_board  # 2d array of integers, solved board          -- (used to check win)
        self.cell_array = []  # 2d array of cell objects, unsolved board                -- (used for actual game loop)
        for row in range(0, len(unsolved_board)):  # generate 2d array of cells
            self.cell_array.append([])
            for col in range(0, len(unsolved_board)):
                self.cell_array[row].append(Cell(
                    unsolved_board[row][col],  # gets cell value from board
                    row,
                    col,
                    (width, height),  # info for cell.draw()
                    screen  # info for cell.draw()
                ))

    # draw all board components in order
    def refresh_board(self):

        # refresh game window info
        pygame.draw.rect(self.screen, WHITE, (0, 0, WIDTH, WIDTH))
        self.draw_selected()
        self.draw()

        # print info to console for debug purposes
        print("\n" * 10)
        print("GAME BOARD:")
        print_array(current_game.get_integer_array())  # print current board to console -- debug
        if current_game.selected_cell is not None:
            print(f'Selected Cell: ({current_game.selected_cell.col}, {current_game.selected_cell.row})')
        if current_game.selected_cell is None:
            print("Selected Cell: (None)")

    # draws board and all selected cells
    def draw(self):
        # draw horizontal lines
        for i in range(1, BOARD_ROWS):
            pygame.draw.line(self.screen, LINE_COLOR, (0, SQUARE_SIZE * i),
                             (WIDTH, SQUARE_SIZE * i), LINE_WIDTH)
        # draw vertical lines
        for i in range(1, BOARD_COLS):
            pygame.draw.line(self.screen, LINE_COLOR, (SQUARE_SIZE * i, 0),
                             (SQUARE_SIZE * i, WIDTH), LINE_WIDTH)

        # draw thicker horizontal lines
        for i in range(0, BOARD_ROWS + 6, 3):
            pygame.draw.line(self.screen, LINE_COLOR, (0, SQUARE_SIZE * i),
                             (WIDTH, SQUARE_SIZE * i), LINE_WIDTH_2)


        # draw thicker vertical lines
        for i in range(0, BOARD_COLS + 3, 3):
            pygame.draw.line(self.screen, LINE_COLOR, (SQUARE_SIZE * i, 0),
                             (SQUARE_SIZE * i, WIDTH), LINE_WIDTH_2)

        # draw cells
        for i in range(BOARD_ROWS):
            for j in range(BOARD_COLS):
                self.cell_array[i][j].draw()

    def draw_selected(self):
        if self.selected_cell is not None:
            # center the rectangles based on position (to account for line offset)
            rect_center = (self.selected_cell.col * 67 - 2 - (self.selected_cell.col - 4),
                           self.selected_cell.row * 67 - 2 - (self.selected_cell.row - 4))

            # create more offsets to account for line cutting it off
            # "up offset" means giving it one pixel of breathing room on top
            top_offset = 0
            bottom_offset = 0
            left_offset = 0
            right_offset = 0
            if (self.selected_cell.row % 3)     == 0:  # cells on the top of boxes
                top_offset = 1
            if (self.selected_cell.row - 2) % 3 == 0:  # cells on the bottom of boxes
                bottom_offset = 1
            if (self.selected_cell.col) % 3     == 0:  # cells on the left of boxes
                left_offset = 1
                right_offset = 1
            if (self.selected_cell.col - 2) % 3 == 0:  # cells on the right of boxes
                right_offset = 1

            # red background
            pygame.draw.rect(self.screen, RED, (
                rect_center[0], rect_center[1], 63, 63))

            # white inner (to make it look like a border)
            pygame.draw.rect(self.screen, WHITE, (
                rect_center[0] + 3 + left_offset, rect_center[1] + 3 + top_offset,
                56 - right_offset, 56 - bottom_offset))

    # change currently selected cell
    def select(self, row, col):
        if (not (0 <= row <= 8)) or (not (0 <= col <= 8)):  # clear selected if invalid coords
            self.selected_cell = None
        else:
            self.selected_cell = self.cell_array[row][col]
            self.draw_selected()

    # turn click coordinates into tuple of sudoku cell coordinates (either (row, col) or None)
    def click(self, x, y):
        if y <= WIDTH:
            return y // (WIDTH // 9), x // (WIDTH // 9)
        return None

    # clear currently selected cell's values (if values entered by user)
    def clear(self):  # clear selected
        if self.selected_cell is not None:
            if self.selected_cell.value == 0 or self.selected_cell.user_placed:
                self.selected_cell.set_cell_value(0)
                self.selected_cell.set_sketched_value(0)

    # place a sketched value onto selected cell
    def sketch(self, value):
        if self.selected_cell is not None:
            self.selected_cell.set_sketched_value(value)
            self.selected_cell.set_user_placed()

    # turn selected sketch into placed value
    def place_number(self):
        if self.selected_cell is not None:
            if (self.selected_cell.sketched_value != 0) and (self.selected_cell.value == 0):  # check it can be placed
                self.selected_cell.set_cell_value(self.selected_cell.sketched_value)
                self.selected_cell.set_user_placed()

    # takes keyboard intput of a number 1 - 9 and sketches it
    def number_input(self, number):
        if self.selected_cell.value == 0:  # check there's no value in cell already
            self.sketch(number)

    # reset board to initial (removed) puzzle state
    def reset_to_original(self):
        self.cell_array = []  # reset cell array
        for row in range(0, 9):  # generate 2d array of cells using original board
            self.cell_array.append([])
            for col in range(0, 9):
                self.cell_array[row].append(Cell(
                    self.unsolved_board[row][col],  # gets cell value from board
                    row,
                    col,
                    (self.width, self.height),  # info for cell.draw()
                    self.screen  # info for cell.draw()
                ))

    # check if board is full or not
    def is_full(self):  # returns boolean
        for row in self.get_integer_array():
            if 0 in row:
                return False
        return True

    # check if board is solved
    def check_board(self):
        if self.get_integer_array() == self.solved_board:
            return True
        return False

    # takes 2d cell array & returns values in integer array
    def get_integer_array(self):
        integer_array = []
        for row in range(0, len(self.cell_array)):
            integer_array.append([])
            for col in range(0, len(self.cell_array[row])):
                integer_array[row].append(self.cell_array[row][col].value)
        return integer_array


'''
DO NOT CHANGE
Provided for students
Given a number of rows and number of cells to remove, this function:
1. creates a SudokuGenerator
2. fills its values and saves this as the solved state
3. removes the appropriate number of cells
4. returns the representative 2D Python Lists of the board and solution

Parameters:
size is the number of rows/columns of the board (9 for this project)
removed is the number of cells to clear (set to 0)

Return: list[list] (a 2D Python list to represent the board)
'''
# changed this function to return a tuple of removed board and solved board
# original code didn't seem to have any way to access the original solved board (for checking wins)
def generate_sudoku(size, removed):
    sudoku = SudokuGenerator(size, removed)

    sudoku.fill_values()
    solved_board = copy.deepcopy(sudoku.get_board())
    sudoku.remove_cells()
    board = sudoku.get_board()
    return board, solved_board  # use tuple unpacking, i.e.:  board, solved_board = generate_sudoku(size, removed)

def generate_game(width, height, screen, size, removed):
    unsolved_board, solved_board = generate_sudoku(size, removed)
    return Board(width, height, screen, unsolved_board, solved_board)

def print_array(array):  # debug, prints 2d array
    print("___" * len(array))
    for row in array:
        for cell in row:
            print(cell, end="  ")
        print("|")
    print("___" * len(array), end="|\n")

def init():
    pygame.init()
    pygame.display.set_caption("Sudoku")

def welcome():
    screen.fill(BG_COLOR)

def draw_game_start(screen):
    # initialize font
    start_title_font = pygame.font.SysFont("Times New Roman", 60) # [3]
    button_font = pygame.font.SysFont("Times New Roman", 40) # [3]
    game_mode_font = pygame.font.SysFont("Times New Roman", 50) # [3]

    # color background image
    screen_display = pygame.display.set_mode((WIDTH, HEIGHT)) # [1]
    image = pygame.image.load(BytesIO(BG_IMAGE_REQUEST.content)).convert() # [4]
    image = pygame.transform.smoothscale(image, (WIDTH, HEIGHT)) # [2]
    screen_display.blit(image, (0,0))
    pygame.display.flip()

    # initialize & draw title
    title_surface = start_title_font.render("Welcome to Sudoku", 0, (0, 0, 0))
    title_rectangle = title_surface.get_rect(
        center=(WIDTH // 2, HEIGHT // 2 - 150))
    screen.blit(title_surface, title_rectangle)

    # initialize & draw game mode text
    game_mode_surface = game_mode_font.render("Select Game Mode:", 0, (0, 0, 0))
    game_mode_rectangle = title_surface.get_rect(
        center=(WIDTH // 2 + 50, HEIGHT // 2 + 50))
    screen.blit(game_mode_surface, game_mode_rectangle)

    # initialize buttons ---
    # initialize button text
    easy_mode = button_font.render("Easy", 0, (255, 255, 255))
    medium_mode = button_font.render("Medium", 0, (255, 255, 255))
    hard_mode = button_font.render("Hard", 0, (255, 255, 255))

    # initialize button background color and text
    # easy mode
    easy_surface = pygame.Surface((easy_mode.get_size()[0] + 20, easy_mode.get_size()[1] + 20))
    easy_surface.fill((0, 204, 0))
    easy_surface.blit(easy_mode, (10, 10))
    # easy mode border
    easy_surface_border = pygame.Surface((easy_mode.get_size()[0] + 30, easy_mode.get_size()[1] + 30))
    easy_surface_border.fill((0, 102, 0))
    easy_surface_border.blit(easy_mode, (10, 10))
    # medium mode
    medium_surface = pygame.Surface((medium_mode.get_size()[0] + 20, medium_mode.get_size()[1] + 20))
    medium_surface.fill((229, 202, 33))
    medium_surface.blit(medium_mode, (10, 10))
    # medium mode border
    medium_surface_border = pygame.Surface((easy_mode.get_size()[0] + 90, easy_mode.get_size()[1] + 30))
    medium_surface_border.fill((210, 156, 30))
    medium_surface_border.blit(medium_mode, (10, 10))
    # hard mode
    hard_surface = pygame.Surface((hard_mode.get_size()[0] + 20, hard_mode.get_size()[1] + 20))
    hard_surface.fill((204, 0, 0))
    hard_surface.blit(hard_mode, (10, 10))
    # hard mode border
    hard_surface_border = pygame.Surface((easy_mode.get_size()[0] + 32, easy_mode.get_size()[1] + 30))
    hard_surface_border.fill((120, 0, 0))
    hard_surface_border.blit(hard_mode, (10, 10))

    # initialize button rectangle
    easy_rectangle = easy_surface.get_rect(
        center=(WIDTH // 2 - 150, HEIGHT // 2 + 150))
    easy_rectangle_border = easy_surface.get_rect(
        center=(WIDTH // 2 - 155, HEIGHT // 2 + 145))
    medium_rectangle = medium_surface.get_rect(
        center=(WIDTH // 2, HEIGHT // 2 + 150))
    medium_rectangle_border = easy_surface.get_rect(
        center=(WIDTH // 2 - 35, HEIGHT // 2 + 145))
    hard_rectangle = hard_surface.get_rect(
        center=(WIDTH // 2 + 150, HEIGHT // 2 + 150))
    hard_rectangle_border = easy_surface.get_rect(
        center=(WIDTH // 2 + 144, HEIGHT // 2 + 145))

    # draw buttons
    screen.blit(easy_surface_border, easy_rectangle_border)
    screen.blit(easy_surface, easy_rectangle)
    screen.blit(medium_surface_border, medium_rectangle_border)
    screen.blit(medium_surface, medium_rectangle)
    screen.blit(hard_surface_border, hard_rectangle_border)
    screen.blit(hard_surface, hard_rectangle)

    # action loop
    while True:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if easy_rectangle.collidepoint(event.pos):  # check if mouse on easy button
                    init()  # reinitialize start screen
                    welcome()
                    return generate_game(WIDTH, HEIGHT, screen, 9, 30)  # generate new easy board
                elif medium_rectangle.collidepoint(event.pos):  # check if mouse on medium button
                    init()  # reinitialize start screen
                    welcome()
                    return generate_game(WIDTH, HEIGHT, screen, 9, 40)  # generate new medium board
                elif hard_rectangle.collidepoint(event.pos):  # check if mouse on hard button
                    init()  # reinitialize start screen
                    welcome()
                    return generate_game(WIDTH, HEIGHT, screen, 9, 50)  # generate new hard board

        pygame.display.update()

def draw_sudoku_buttons(screen):
    # draws button games during sudoku

    # initialize font
    exit_font = pygame.font.SysFont("Times New Roman", 40) # [3]
    restart_font = pygame.font.SysFont("Times New Roman", 40) # [3]
    reset_font = pygame.font.SysFont("Times New Roman", 40) # [3]

    # initialize & draw exit button
    exit_surface = exit_font.render("Exit", 0, (0, 0, 0))
    exit_rectangle = exit_surface.get_rect(
        center=(WIDTH // 2, HEIGHT // 2 - 1000))
    screen.blit(exit_surface, exit_rectangle)

    # initialize & draw restart button
    restart_surface = restart_font.render("Restart", 0, (0, 0, 0))
    restart_rectangle = restart_surface.get_rect(
        center=(WIDTH // 2, HEIGHT // 2 - 1000))
    screen.blit(restart_surface, restart_rectangle)

    # initialize & draw reset button
    reset_surface = reset_font.render("Reset", 0, (0, 0, 0))
    reset_rectangle = reset_surface.get_rect(
        center=(WIDTH // 2, HEIGHT // 2 - 1000))
    screen.blit(reset_surface, reset_rectangle)

    # initialize text first
    exit_mode = exit_font.render("Exit", 0, (255, 255, 255))
    restart_mode = restart_font.render("Restart", 0, (255, 255, 255))
    reset_mode = restart_font.render("Reset", 0, (255, 255, 255))

    # initialize button background color and text
    # exit
    exit_surface = pygame.Surface((exit_mode.get_size()[0] + 20, exit_mode.get_size()[1] + 20))
    exit_surface.fill((0, 0, 0))
    exit_surface.blit(exit_mode, (10, 10))
    # restart
    restart_surface = pygame.Surface((restart_mode.get_size()[0] + 20, restart_mode.get_size()[1] + 20))
    restart_surface.fill((0, 0, 0))
    restart_surface.blit(restart_mode, (10, 10))
    # reset
    reset_surface = pygame.Surface((reset_mode.get_size()[0] + 20, reset_mode.get_size()[1] + 20))
    reset_surface.fill((0, 0, 0))
    reset_surface.blit(reset_mode, (10, 10))

    # initialize button rectangle
    exit_rectangle = exit_surface.get_rect(
        center=(WIDTH // 2 + 150, HEIGHT // 2 + 300))
    restart_rectangle = restart_surface.get_rect(
        center=(WIDTH // 2, HEIGHT // 2 + 300))
    reset_rectangle = reset_surface.get_rect(
        center=(WIDTH // 2 - 150, HEIGHT // 2 + 300))

    # draw buttons
    screen.blit(exit_surface, exit_rectangle)
    screen.blit(restart_surface, restart_rectangle)
    screen.blit(reset_surface, reset_rectangle)

    # check for button presses
    try:
        if restart_rectangle.collidepoint(event.pos):  # check if mouse is on restart button
            #return draw_game_start(screen)
            return "restart"
        elif reset_rectangle.collidepoint(event.pos):  # check if mouse is on reset button
            #return board, solved_board
            return "reset"
        elif exit_rectangle.collidepoint(event.pos):
            return "exit"
        pygame.display.update()
    except:
        return None

def draw_game_over(screen):

    # initialize font & background color
    game_over_font = pygame.font.SysFont("Times New Roman", 50) # [3]
    screen.fill(BG_COLOR)

    # color background image
    screen_display = pygame.display.set_mode((WIDTH, HEIGHT)) # [1]
    image = pygame.image.load(BytesIO(BG_IMAGE_REQUEST.content)).convert() # [4]
    image = pygame.transform.smoothscale(image, (WIDTH, HEIGHT)) # [2]
    screen_display.blit(image, (0,0))
    pygame.display.flip()

    if game_won:
        # game won

        # initialize & draw win text
        game_won_surf = game_over_font.render("Game Won!", 0, (0, 0, 0))
        game_won_rect = game_won_surf.get_rect(
            center=(WIDTH // 2, HEIGHT // 2 - 100))
        screen.blit(game_won_surf, game_won_rect)

        # initialize & draw exit button
        exit_surface = game_over_font.render("Exit", 0, (0, 0, 0))
        exit_rectangle = exit_surface.get_rect(
            center=(WIDTH // 2, HEIGHT // 2 - 500))
        screen.blit(exit_surface, exit_rectangle)

        # initialize buttons ---
        # initialize button text
        exit_mode = game_over_font.render("Exit", 0, (255, 255, 255))

        # initialize exit button color & text
        exit_surface = pygame.Surface((exit_mode.get_size()[0] + 20, exit_mode.get_size()[1] + 20))
        exit_surface.fill((0, 0, 0))
        exit_surface.blit(exit_mode, (10, 10))

        # initialize button rectangle
        exit_rectangle = exit_surface.get_rect(
            center=(WIDTH // 2, HEIGHT // 2 + 100))

        # draw button
        screen.blit(exit_surface, exit_rectangle)

        # action loop
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if exit_rectangle.collidepoint(event.pos):
                        # Checks if mouse is on exit button
                        sys.exit()

            pygame.display.update()

    else:
        # game over

        game_over_surf = game_over_font.render("Game Over :(", 0, (0, 0, 0))
        game_over_rect = game_over_surf.get_rect(
            center=(WIDTH // 2, HEIGHT // 2 - 100))
        screen.blit(game_over_surf, game_over_rect)

        # initialize & draw restart button
        restart_surface = game_over_font.render("Restart", 0, (0, 0, 0))
        restart_rectangle = restart_surface.get_rect(
            center=(WIDTH // 2, HEIGHT // 2 - 500))
        screen.blit(restart_surface, restart_rectangle)

        # initialize button ---
        # initialize button text
        restart_mode = game_over_font.render("Restart", 0, (255, 255, 255))

        # initialize button background color & text
        restart_surface = pygame.Surface((restart_mode.get_size()[0] + 20, restart_mode.get_size()[1] + 20))
        restart_surface.fill((0, 0, 0))
        restart_surface.blit(restart_mode, (10, 10))

        # initialize button rectangle
        restart_rectangle = restart_surface.get_rect(
            center=(WIDTH // 2, HEIGHT // 2 + 100))

        # draw button
        screen.blit(restart_surface, restart_rectangle)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if restart_rectangle.collidepoint(event.pos):  # checks if mouse is on restart button
                        draw_game_start(screen)  # reload game
                        return
            pygame.display.update()

# main
if __name__ == '__main__':
    game_over = False
    game_won = False
    menu_button_press = None
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    # initialize welcome screen
    init()
    welcome()

    # generate first game instance based on start screen (easy/med/hard)
    current_game = draw_game_start(screen)
    current_game.refresh_board()  # draw sudoku values initially

    # core gameplay loop
    while True:

        # execute each user input (clicking, keystrokes, etc.)
        for event in pygame.event.get():

            # draw menu buttons
            draw_sudoku_buttons(screen)

            # exiting game using X
            if event.type == pygame.QUIT:
                sys.exit()

            # click actions
            if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                # select clicked cell
                if current_game.click(event.pos[0], event.pos[1]) is not None:  # if clicked cell, set as selected
                    selected_row, selected_col = current_game.click(event.pos[0], event.pos[1])
                    current_game.select(selected_row, selected_col)

                elif current_game.click(event.pos[0], event.pos[1]) is None:  # if not, clear selected
                    current_game.select(-1, -1)

                current_game.refresh_board()

                # check if clicked menu buttons
                menu_button_press = draw_sudoku_buttons(screen)
                if menu_button_press == "restart":
                    current_game = draw_game_start(screen)  # generate fresh game instance (restart)
                    current_game.refresh_board()
                elif menu_button_press == "reset":
                    current_game.reset_to_original()  # reset board to unsolved state
                    current_game.refresh_board()
                elif menu_button_press == "exit":
                    sys.exit()



            # keyboard actions
            if event.type == pygame.KEYDOWN:
                if current_game.selected_cell is not None:  # check a cell is selected

                    # clearing cells
                    if event.key == pygame.K_BACKSPACE and current_game.selected_cell.user_placed:
                        current_game.clear()

                    # solidfying sketched guesses
                    elif event.key == pygame.K_RETURN:
                        current_game.place_number()

                    # sketching selected cell
                    match event.key:  # check if button is keys 1 - 9 -- sketch value
                        case pygame.K_1:
                            current_game.number_input(1)
                        case pygame.K_2:
                            current_game.number_input(2)
                        case pygame.K_3:
                            current_game.number_input(3)
                        case pygame.K_4:
                            current_game.number_input(4)
                        case pygame.K_5:
                            current_game.number_input(5)
                        case pygame.K_6:
                            current_game.number_input(6)
                        case pygame.K_7:
                            current_game.number_input(7)
                        case pygame.K_8:
                            current_game.number_input(8)
                        case pygame.K_9:
                            current_game.number_input(9)

                    # arrow key movements
                    match event.key:
                        case pygame.K_UP:
                            if current_game.selected_cell.row > 0:
                                current_game.select(current_game.selected_cell.row - 1, current_game.selected_cell.col)
                        case pygame.K_DOWN:
                            if current_game.selected_cell.row < 8:
                                current_game.select(current_game.selected_cell.row + 1, current_game.selected_cell.col)
                        case pygame.K_LEFT:
                            if current_game.selected_cell.col > 0:
                                current_game.select(current_game.selected_cell.row, current_game.selected_cell.col - 1)
                        case pygame.K_RIGHT:
                            if current_game.selected_cell.col < 8:
                                current_game.select(current_game.selected_cell.row, current_game.selected_cell.col + 1)

                current_game.refresh_board()  # update sudoku values on screen
                if current_game.is_full():  # check if board is full (game over)
                    game_over = True
                    game_won = current_game.check_board()  # boolean

        # game is over
        if game_over:
            draw_game_over(screen)
            pygame.display.update()
            current_game = draw_game_start(screen)
            current_game.refresh_board()
            game_over = False

        pygame.display.update()
