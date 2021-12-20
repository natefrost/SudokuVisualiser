# -*- coding: utf-8 -*-
"""
An interactive Sudoku visualiser, including a solver using recursion
"""
import pygame
import numpy as np
import random
from random import sample
pygame.font.init()


# Functions that generate a solved sudoku board (9x9), then remove an arbitrary number of values.
# For this specific example, I went with removing 50 values (leaving 31 clues remaining), but 
# anything up to 64 is okay.

def pattern(row, col):
    #sudoku pattern
    return (3*(row%3) + row//3 + col)%9

def shuffle(s):
    return(sample(s, len(s)))
    
def create_board():
    rows = [3*val + row for val in shuffle(range(3)) for row in shuffle(range(3))]
    cols = [3*val + col for val in shuffle(range(3)) for col in shuffle(range(3))]
    nums = shuffle(range(1, 10))
    
    board = np.array([ [nums[pattern(r,c)] for c in cols] for r in rows ])
    return board
    
def remove_numbers(board, remove_amount):
    h, w, r = len(board), len(board[0]), []
    spaces = [[x, y] for x in range(h) for y in range(w)]
    for k in range(remove_amount):
        r = random.choice(spaces)
        board[r[0]][r[1]] = 0
        spaces.remove(r)
    return board

# Functions for Sudoku solving:
    
def find_next(board):
    # Finds the next field to fill in
    for row in range(len(board)):
        for col in range(len(board[0])):
            if board[row][col] == 0:
                return((row, col))
    return None

def possible(board, value, row, col):
    # Given a value and a field on the board, checks whether that value is a possibility on that field.    
    
    # Check for the same number in that column:
    for i in range(len(board)):
        if board[i][col] == value and row != i:
            return False
    # Check for the same number in that row:
    for i in range(len(board[0])):
        if board[row][i] == value and col != i:
            return False
        
    # Check the 3x3 (presumably) box using floor to find out which square to check:
    
    y = row // 3
    x = col // 3
    
    for r in range(y*3, y*3+3):
        for c in range(x*3, x*3+3):
            if board[r][c] == value and (r,c) != (row, col):
                return False
            
    return True
    

def solve(board):
    # Recursively solves a sudoku board.
    
    field = find_next(board)
    
    if not field:
        
        return True
    else:
        row, col = field[0], field[1]
        
    for value in range(1,10):
        if possible(board, value, row, col):
            board[row][col] = value
            # Recursively solve, if the value works, if not, we go back
            
            if solve(board):
                return True
            
            #value doesnt work, set to 0 and go again.
            board[row][col] = 0
            
    return False
            
    
    
# Implementation of classes, which will enable visualisation of Sudoku solving.            
    
class Field:
    
    # Class, which functions as one field of the whole board.
    
    def __init__(self, value, row, col, x, y, selected):
        
        self.value = value
        self.row = row
        self.col = col
        self.x = x
        self.y = y
        self.selected = selected
        
        # Temporary store of value (will display user inserted value) 
        self.temp = 0
        
    def set_value(self, value):
        self.value = value
    def set_temp(self, value):
        self.temp = value
        
    def make(self, game): 
        
        x = self.col * self.x / 9
        y = self.row * self.y / 9
        
        
        # Pick a font (I like corbel a lot)
        font = pygame.font.SysFont('corbel', 35)
        
        # Fill in the value or the temporary value:
        
        if self.value == 0 and self.temp != 0:
            temp = font.render(str(self.temp), 1, (252, 95, 95))
            game.blit(temp, x+5, y+5)
        if self.value != 0:
            value = font.render(str(self.value), 1, (0, 0, 0))
            game.blit(value, (x + (self.x/18 - value.get_width()/2), y + (self.y/18 - value.get_height()/2)))
        
        # Highlight selected rectangle:
        
        if self.selected:
            pygame.draw.rect(game, (248, 88, 48), (x, y, self.x/9, self.y/9), 2)
            
    def update(self, game, valid=True):
        
        x = self.col * self.x / 9
        y = self.row * self.y / 9
            
        
        pygame.draw.rect(game, (173, 216, 230), (x, y, self.x/9, self.y/9))
        
        # Corbel supremacy.
        font = pygame.font.SysFont('corbel', 35)
        value = font.render(str(self.value), 1, (0,0,0))
        game.blit(value, (x + (self.x/18 - value.get_width()/2),y + (self.y/18 - value.get_height()/2)))
        
        
        # green for valid, red for invalid
        if valid:
            pygame.draw.rect(game, (0,255,0), (x, y, self.x/9, self.y/9), 2)
        else:
            pygame.draw.rect(game, (255,0,0), (x, y, self.x/9, self.y/9), 2)
            
            
class Board(): 
    
    # Class, functioning as a board, comprised of 9x9 Fields.
    
    # Every instance generates its new board:
    
    board = remove_numbers(create_board(), 50)
    
    
    def __init__(self, rows, cols, size, game):
        self.fields = [[Field(self.board[row][col], row, col, 540, 540, False) for col in range(cols)] for row in range(rows)]
        self.rows = rows
        self.cols = cols
        self.game = game
        self.curr = None
        self.model = None
        self.size = size
        self.update()
    
    def update(self):
        self.model = [[self.fields[row][col].value for col in range(self.cols)] for row in range(self.rows)]
        
    def delete(self):
        row, col = self.curr
        field = self.fields[row][col]
        if field.value == 0:
            field.set_temp(0)
    
    def current(self, r, c):
        self.curr = (r, c)
        self.fields[r][c].selected = True
        
        for i in range(9):
            for j in range(9):
                if (i, j) != (r, c):
                    self.fields[i][j].selected = False
                
    def select(self, r, c):
        if r>=self.size[0] or c>=self.size[1]:
            return None
        space = self.size[0] / 9
        x = r / space
        y = c / space
        return(int(y), int(x))
        
        
    def solved(self):
        # checks if sudoku is solved
        for row in range(self.rows):
            for col in range(self.cols):
                if self.fields[row][col] == 0:
                    return False
        return True

    def make(self):
        
        # Function which creates the board
        space = self.size[0]/9
        
        # draw squares
        for row in range(self.rows):
            for col in range(self.cols):
                self.fields[row][col].make(self.game)
        # draw lines    
        for i in range(10):
            if i%3 == 0:
                pygame.draw.line(self.game, (248,88,48), (0, i*space), (self.size[0], i*space), 3)
                pygame.draw.line(self.game, (248,88,48), (i*space, 0), (i*space, self.size[1]), 3)
            else:
                pygame.draw.line(self.game, (248,88,48), (0, i*space), (self.size[0], i*space), 1)
                pygame.draw.line(self.game, (248,88,48), (i*space, 0), (i*space, self.size[1]), 1)
    
    def solve_board(self):
        
        # updated version of Solve which also implements visualisation
        
        self.update()
        
        field = find_next(self.model)
        if not field:
            return True
        
        else:
            row, col = field[0], field[1]
        
        for value in range(1 ,10):
            if possible(self.model, value, row, col):
                self.model[row][col] = value
                self.fields[row][col].set_value(value)
                self.fields[row][col].update(self.game)
                self.update()
                pygame.display.update()
                
                pygame.time.delay(5)
                pygame.event.pump()
                
                # Recursively solve, if the value works, if not, we go back
                
                if self.solve_board():
                    return True
            
                #value doesnt work, set to 0 and go again.
                self.model[row][col] = 0
                self.fields[row][col].set_value(0)
                self.fields[row][col].update(self.game, False)
                self.update()
                pygame.display.update()
                
                pygame.time.delay(5)
            
        return False
        
def sudoku():
    
    game = pygame.display.set_mode((540, 620))
    pygame.display.set_caption('Sudoku visualiser')
    
    board = Board(9, 9, (540,540), game)
    
    key = None
    run = True
    
    while run:
        pygame.event.get()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s or event.key == pygame.K_SPACE:
                    board.solve_board()
                    
                if event.key == pygame.K_DELETE:
                    board.delete()
                    key = None
                    
                if event.key == pygame.K_RETURN:
                    row, col = board.curr
                    if board.fields[row][col].temp!= 0:
                        if (board.insert_value(board.fields[row][col].temp)):
                            pass
                        else:
                            print("You can not put this number here!")
                        key = None
                        
                        if board.solved():
                            print("You have solved the Sudoku!")
                            
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    selected = board.select(pos[0], pos[1])
                
                    if selected:
                        board.current(selected[0], selected[1])
                        key = None

            
            game.fill((170, 200, 208))
            font = pygame.font.SysFont("corbel", 30)
            text = font.render("Press Space or S to solve the board!" , 1, (255, 0, 0))
            game.blit(text, (20, 570))
            board.make()
            pygame.display.update()

sudoku()
        
pygame.quit()
        
                
    
    

        
        
        
        
        
        
        
        
        
        
        
        
        

