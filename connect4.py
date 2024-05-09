import numpy as np
import pygame
import sys
import math
import random
import copy

# Colors for the board and pieces
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255 ,0)

ROW_COUNT = 6
COLUMN_COUNT = 7

PLAYER = 0
AI = 1

EMPTY = 0
PLAYER_PIECE = 1
AI_PIECE = 2

# Number of spaces AI needs to check
WINNING_LENGTH = 4

# Controlling how deep into the minmax tree the AI checks
# Needs to be > 0
MAX_DEPTH = 1

# Creating the empty board at the start of the game
def create_board():
    board = np.zeros((ROW_COUNT, COLUMN_COUNT))
    return board

# Dropping the piece at the chosen row and column
def drop_piece(board, row, col, piece):
    board[row][col] = piece

def animate_move(board, row, col, piece):
    xposition = int(col*SQUARESIZE + SQUARESIZE/2)
    yposition = int(SQUARESIZE/2)
    COLOR = RED
    if piece == 2:
        COLOR = YELLOW
    yspeed = .2
    while yposition < (HEIGHT-row*SQUARESIZE-SQUARESIZE/2):
        yspeed += .2
        yposition += yspeed
        pygame.draw.rect(screen, BLACK, (0,0, WIDTH, SQUARESIZE))
        draw_board(board)
        pygame.draw.circle(screen, COLOR, (xposition, int(yposition)), RADIUS)
        pygame.display.update()
    return True

# Checking if location is a 0 which means that it is still empty
def is_valid_location(board, col):
    return board[ROW_COUNT-1][col] == 0


def get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == 0:
            return r
        
def print_board(board):
    print(np.flip(board, 0))

def winning_move(board, piece):
    # Check horizontal locations for win
    for c in range(COLUMN_COUNT-3):
        for r in range(ROW_COUNT):
            if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
                return True
            
    # Check vertical locations for win
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT-3):
            if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
                return True
            
    # Check positively sloped diagonals
    for c in range(COLUMN_COUNT-3):
        for r in range(ROW_COUNT-3):
            if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
                return True


    # Check negatively sloper diagonals
    for c in range(COLUMN_COUNT-3):
        for r in range(3, ROW_COUNT):
            if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
                return True

# Point mechanism for the AI to choose the best alternative
# Can be modified to change the way of playing for the AI
def evaluate_window(window, piece):
    score = 0
    opp_piece = PLAYER_PIECE
    if piece == PLAYER_PIECE:
        opp_piece == AI_PIECE

    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 2

    if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
        score -= 4
    return score
            
def score_position(board, piece):
    score = 0

    # Center score
    # AI prefers the center at the start
    center_array = [int(i) for i in list(board[:, COLUMN_COUNT//2])]
    center_count = center_array.count(piece)
    score += center_count + 3

    # Horizontal score
    for r in range(ROW_COUNT):
        row_array = [int(i) for i in list(board[r,:])]
        for c in range(COLUMN_COUNT-3):
            window = row_array[c:c+WINNING_LENGTH]
            score += evaluate_window(window, piece)

    # Vertical score
    for c in range(COLUMN_COUNT):
        col_array = [int(i) for i in list(board[:,c])]
        for r in range(ROW_COUNT-3):
            window = col_array[r:r+WINNING_LENGTH]
            score += evaluate_window(window, piece)

    # Positive sloped diagonal score
    for r in range(ROW_COUNT-3):
        for c in range(COLUMN_COUNT-3):
            window = [board[r+i][c+i] for i in range(WINNING_LENGTH)]
            score += evaluate_window(window, piece)

    # Negatively sloped diagonal score
    for r in range(ROW_COUNT-3):
        for c in range(COLUMN_COUNT-3):
            window = [board[r+3-i][c+i] for i in range(WINNING_LENGTH)]
            score += evaluate_window(window, piece)

    return score

# Checks if the game is over: player wins or AI wins or tie
def is_terminal_node(board):
    return winning_move(board, PLAYER_PIECE) or winning_move(board, AI_PIECE) or len(get_valid_locations(board)) == 0

# Actual algorithm the AI uses to search for the best possible outcome
# Recursive function switching between min- and max-player
def minimax(board, depth, alpha, beta, maximizing_player):
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)
    # First check if the game is over or if the AI is on the easiest mode
    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, AI_PIECE):
                return (None, 100000)
            elif winning_move(board, PLAYER_PIECE):
                return (None, -100000)
            else: # Game is over
                return (None, 0)
        else: # Depth = 0
            return (None, score_position(board, AI_PIECE))
    if maximizing_player:
        # Value used in the pruning process
        value = -math.inf
        # Setting where the AI starts evaluating
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            # Algorithm needs a copy of the board to work
            b_copy = copy.deepcopy(board)
            drop_piece(b_copy, row, col, AI_PIECE)
            # Calling the function recursively to search deeper
            new_score = minimax(b_copy, depth-1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            # Way for pruning to check if the algorithm can stop there. Better path already found
            if alpha >= beta:
                break
        return column, value
    else:
        value = math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = copy.deepcopy(board)
            drop_piece(b_copy, row, col, PLAYER_PIECE)
            new_score = minimax(b_copy, depth-1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return column, value
    

# Checking all the possible locations that are still unused
def get_valid_locations(board):
    valid_locations = []
    for col in range(COLUMN_COUNT):
        if is_valid_location(board, col):
            valid_locations.append(col)
    return valid_locations

# Drawing the board
def draw_board(board):
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(screen, BLUE, (c*SQUARESIZE, r*SQUARESIZE+SQUARESIZE, SQUARESIZE, SQUARESIZE))
            pygame.draw.circle(screen, BLACK, (int(c*SQUARESIZE+SQUARESIZE/2), int(r*SQUARESIZE+SQUARESIZE+SQUARESIZE/2)), RADIUS)
            
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            if board[r][c] == PLAYER_PIECE:
                pygame.draw.circle(screen, RED, (int(c*SQUARESIZE+SQUARESIZE/2), HEIGHT - int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
            elif board[r][c] == AI_PIECE:
                pygame.draw.circle(screen, YELLOW, (int(c*SQUARESIZE+SQUARESIZE/2), HEIGHT - int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
    pygame.display.update()

    
board = create_board()
game_over = False

pygame.init()

# Pixel sizes for the squares
# Change this to fit for the screen
SQUARESIZE = 90

WIDTH = COLUMN_COUNT * SQUARESIZE
HEIGHT = (ROW_COUNT+1) * SQUARESIZE
RADIUS = int(SQUARESIZE/2 - 5)

size = (WIDTH, HEIGHT)

screen = pygame.display.set_mode(size)
draw_board(board)
pygame.display.update()
myfont = pygame.font.SysFont("monospace", 75)

# Determining if the user or the AI starts
turn = random.randint(PLAYER, AI)

while not game_over:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        # Checking where the players cursor is
        if event.type == pygame.MOUSEMOTION:
            pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, SQUARESIZE))
            posx = event.pos[0]
            if turn == PLAYER:
                pygame.draw.circle(screen, RED, (posx, int(SQUARESIZE/2)), RADIUS)
        pygame.display.update()

        # Used so that the top black bar stays black
        if event.type == pygame.MOUSEBUTTONDOWN:
            pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, SQUARESIZE))

            # Tracking players actions
            if turn == PLAYER:
                posx = event.pos[0]
                col = int(math.floor(posx/SQUARESIZE))

                if is_valid_location(board, col):
                    row = get_next_open_row(board, col)
                    animate_move(board, row, col, 1)
                    drop_piece(board, row, col, PLAYER_PIECE)

                    if winning_move(board, PLAYER_PIECE):
                        label = myfont.render("Player 1 wins!", 1, RED)
                        screen.blit(label, (40, 10))
                        game_over = True

                    turn += 1
                    turn = turn % 2

                    print_board(board)
                    draw_board(board)

    if turn == AI and not game_over:
        # Checking the best possible outcome using the minimax function
        col, minimax_score = minimax(board, MAX_DEPTH, -math.inf, math.inf, True)

        if is_valid_location(board, col):
            pygame.time.wait(500)
            row = get_next_open_row(board, col)
            animate_move(board, row, col, 1)
            drop_piece(board, row, col, AI_PIECE)

            if winning_move(board, AI_PIECE):
                label = myfont.render("Player 2 wins!", 1, YELLOW)
                screen.blit(label, (40, 10))
                game_over = True
            
            print_board(board)
            draw_board(board)

            turn += 1
            turn = turn % 2

    if game_over:
        pygame.time.wait(3000)