import numpy as np
from typing import List, Tuple, Optional

class Connect4Board:
    def __init__(self, rows: int = 6, cols: int = 7):
        self.rows = rows
        self.cols = cols
        self.board = np.zeros((rows, cols), dtype=int)
        self.current_player = 1
        
    def reset(self):
        self.board = np.zeros((self.rows, self.cols), dtype=int)
        self.current_player = 1
        
    def get_valid_actions(self) -> List[int]:
        return [col for col in range(self.cols) if self.board[0][col] == 0]
    
    def make_move(self, col: int) -> bool:
        if col < 0 or col >= self.cols or self.board[0][col] != 0:
            return False
            
        for row in range(self.rows - 1, -1, -1):
            if self.board[row][col] == 0:
                self.board[row][col] = self.current_player
                break
                
        self.current_player = 3 - self.current_player
        return True
    
    def check_winner(self) -> int:
        # Check horizontal
        for row in range(self.rows):
            for col in range(self.cols - 3):
                if (self.board[row][col] != 0 and
                    self.board[row][col] == self.board[row][col+1] == 
                    self.board[row][col+2] == self.board[row][col+3]):
                    return self.board[row][col]
        
        # Check vertical
        for row in range(self.rows - 3):
            for col in range(self.cols):
                if (self.board[row][col] != 0 and
                    self.board[row][col] == self.board[row+1][col] == 
                    self.board[row+2][col] == self.board[row+3][col]):
                    return self.board[row][col]
        
        # Check diagonal (top-left to bottom-right)
        for row in range(self.rows - 3):
            for col in range(self.cols - 3):
                if (self.board[row][col] != 0 and
                    self.board[row][col] == self.board[row+1][col+1] == 
                    self.board[row+2][col+2] == self.board[row+3][col+3]):
                    return self.board[row][col]
        
        # Check diagonal (top-right to bottom-left)
        for row in range(self.rows - 3):
            for col in range(3, self.cols):
                if (self.board[row][col] != 0 and
                    self.board[row][col] == self.board[row+1][col-1] == 
                    self.board[row+2][col-2] == self.board[row+3][col-3]):
                    return self.board[row][col]
        
        return 0
    
    def is_game_over(self) -> bool:
        return self.check_winner() != 0 or len(self.get_valid_actions()) == 0
    
    def get_state(self) -> np.ndarray:
        return self.board.copy()
    
    def get_reward(self, player: int) -> float:
        winner = self.check_winner()
        if winner == player:
            return 1.0
        elif winner != 0:
            return -1.0
        elif len(self.get_valid_actions()) == 0:
            return 0.0
        else:
            return 0.0
    
    def copy(self):
        new_board = Connect4Board(self.rows, self.cols)
        new_board.board = self.board.copy()
        new_board.current_player = self.current_player
        return new_board
    
    def __str__(self):
        display = ""
        for row in self.board:
            display += "|" + "|".join([" " if cell == 0 else "X" if cell == 1 else "O" for cell in row]) + "|\n"
        display += "|" + "|".join([str(i) for i in range(self.cols)]) + "|\n"
        return display