import random
import os
from typing import List, Optional, Tuple
from enum import Enum

class Colors:
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    BACKGROUND_BLUE = '\033[44m'
    BACKGROUND_WHITE = '\033[47m'
    DARK_GRAY = '\033[90m'
    BRIGHT_WHITE = '\033[97m'

class Player(Enum):
    EMPTY = 0
    HUMAN = 1
    BOT = 2

class GameResult(Enum):
    ONGOING = 0
    PLAYER1_WIN = 1
    PLAYER2_WIN = 2
    DRAW = 3

class Connect4:
    def __init__(self, rows: int = 6, cols: int = 7):
        self.rows = rows
        self.cols = cols
        self.board = [[Player.EMPTY for _ in range(cols)] for _ in range(rows)]
        self.current_player = Player.HUMAN
        
    def display_board(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        
        print(f"\n{Colors.CYAN}{Colors.BOLD}┌{'─' * (self.cols * 4 - 1)}┐{Colors.END}")
        print(f"{Colors.CYAN}│{Colors.END}", end="")
        for i in range(1, self.cols + 1):
            print(f"{Colors.WHITE}{Colors.BOLD} {i} {Colors.END}", end="")
        print(f"{Colors.CYAN}│{Colors.END}")
        print(f"{Colors.CYAN}├{'─' * (self.cols * 4 - 1)}┤{Colors.END}")
        
        for row in self.board:
            print(f"{Colors.CYAN}│{Colors.END}", end="")
            for cell in row:
                if cell == Player.EMPTY:
                    print(f"{Colors.BACKGROUND_BLUE} ⚪ {Colors.END}", end="")
                elif cell == Player.HUMAN:
                    print(f"{Colors.BACKGROUND_BLUE}{Colors.RED}{Colors.BOLD} 🔴 {Colors.END}", end="")
                else:
                    print(f"{Colors.BACKGROUND_BLUE}{Colors.YELLOW}{Colors.BOLD} 🟡 {Colors.END}", end="")
            print(f"{Colors.CYAN}│{Colors.END}")
        print(f"{Colors.CYAN}└{'─' * (self.cols * 4 - 1)}┘{Colors.END}")
    
    def is_valid_move(self, col: int) -> bool:
        return 0 <= col < self.cols and self.board[0][col] == Player.EMPTY
    
    def make_move(self, col: int, player: Player) -> bool:
        if not self.is_valid_move(col):
            return False
        
        for row in range(self.rows - 1, -1, -1):
            if self.board[row][col] == Player.EMPTY:
                self.board[row][col] = player
                return True
        return False
    
    def check_winner(self) -> GameResult:
        for row in range(self.rows):
            for col in range(self.cols):
                if self.board[row][col] != Player.EMPTY:
                    if self._check_direction(row, col, 1, 0) or \
                       self._check_direction(row, col, 0, 1) or \
                       self._check_direction(row, col, 1, 1) or \
                       self._check_direction(row, col, 1, -1):
                        return GameResult.PLAYER1_WIN if self.board[row][col] == Player.HUMAN else GameResult.PLAYER2_WIN
        
        if all(self.board[0][col] != Player.EMPTY for col in range(self.cols)):
            return GameResult.DRAW
        
        return GameResult.ONGOING
    
    def _check_direction(self, row: int, col: int, delta_row: int, delta_col: int) -> bool:
        player = self.board[row][col]
        count = 1
        
        r, c = row + delta_row, col + delta_col
        while 0 <= r < self.rows and 0 <= c < self.cols and self.board[r][c] == player:
            count += 1
            r += delta_row
            c += delta_col
        
        r, c = row - delta_row, col - delta_col
        while 0 <= r < self.rows and 0 <= c < self.cols and self.board[r][c] == player:
            count += 1
            r -= delta_row
            c -= delta_col
        
        return count >= 4
    
    def get_valid_moves(self) -> List[int]:
        return [col for col in range(self.cols) if self.is_valid_move(col)]
    
    def reset(self):
        self.board = [[Player.EMPTY for _ in range(self.cols)] for _ in range(self.rows)]
        self.current_player = Player.HUMAN

class RandomBot:
    def get_move(self, game: Connect4) -> int:
        valid_moves = game.get_valid_moves()
        return random.choice(valid_moves) if valid_moves else 0

def get_human_move(game: Connect4) -> int:
    while True:
        try:
            player_color = Colors.RED if game.current_player == Player.HUMAN else Colors.YELLOW
            player_symbol = "🔴" if game.current_player == Player.HUMAN else "🟡"
            player_num = 1 if game.current_player == Player.HUMAN else 2
            
            move = int(input(f"\n{player_color}{Colors.BOLD}{player_symbol} Player {player_num}{Colors.END}, enter column {Colors.CYAN}(1-{game.cols}){Colors.END}: ")) - 1
            if game.is_valid_move(move):
                return move
            else:
                print(f"{Colors.RED}❌ Invalid move! Column is full or out of range.{Colors.END}")
        except ValueError:
            print(f"{Colors.RED}❌ Please enter a valid number.{Colors.END}")

def play_game(mode: str = "pvp"):
    game = Connect4()
    bot = RandomBot() if mode == "pvb" else None
    
    print(f"\n{Colors.PURPLE}{Colors.BOLD}{'═'*60}{Colors.END}")
    print(f"{Colors.PURPLE}{Colors.BOLD}║{' '*22}🔴 CONNECT 4 🟡{' '*22}║{Colors.END}")
    print(f"{Colors.PURPLE}{Colors.BOLD}║{' '*20}Get 4 in a row to win!{' '*19}║{Colors.END}")
    if mode == "pvp":
        print(f"{Colors.PURPLE}{Colors.BOLD}║{' '*15}{Colors.RED}Player 1: 🔴{Colors.PURPLE}  vs  {Colors.YELLOW}Player 2: 🟡{Colors.PURPLE}{' '*14}║{Colors.END}")
    else:
        print(f"{Colors.PURPLE}{Colors.BOLD}║{' '*17}{Colors.RED}Player: 🔴{Colors.PURPLE}  vs  {Colors.YELLOW}Bot: 🟡{Colors.PURPLE}{' '*17}║{Colors.END}")
    print(f"{Colors.PURPLE}{Colors.BOLD}{'═'*60}{Colors.END}")
    
    game.display_board()
    
    while True:
        if game.current_player == Player.HUMAN:
            move = get_human_move(game)
            game.make_move(move, Player.HUMAN)
        else:
            if mode == "pvb":
                print(f"\n{Colors.YELLOW}{Colors.BOLD}🤖 Bot is thinking...{Colors.END}")
                move = bot.get_move(game)
                print(f"{Colors.YELLOW}{Colors.BOLD}🟡 Bot plays column {move + 1}{Colors.END}")
                game.make_move(move, Player.BOT)
            else:
                move = get_human_move(game)
                game.make_move(move, Player.BOT)
        
        game.display_board()
        
        result = game.check_winner()
        if result != GameResult.ONGOING:
            print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
            if result == GameResult.PLAYER1_WIN:
                print(f"{Colors.GREEN}{Colors.BOLD}🏆 VICTORY! Player 1 🔴 wins! 🎉{Colors.END}")
            elif result == GameResult.PLAYER2_WIN:
                if mode == "pvb":
                    print(f"{Colors.YELLOW}{Colors.BOLD}🤖 Bot 🟡 wins! Better luck next time! 💪{Colors.END}")
                else:
                    print(f"{Colors.GREEN}{Colors.BOLD}🏆 VICTORY! Player 2 🟡 wins! 🎉{Colors.END}")
            else:
                print(f"{Colors.CYAN}{Colors.BOLD}🤝 It's a draw! Well played! ⚖️{Colors.END}")
            print(f"{Colors.BOLD}{'='*60}{Colors.END}")
            break
        
        game.current_player = Player.BOT if game.current_player == Player.HUMAN else Player.HUMAN

def main():
    while True:
        os.system('clear' if os.name == 'posix' else 'cls')
        print(f"\n{Colors.PURPLE}{Colors.BOLD}{'╔'+'═'*58+'╗'}{Colors.END}")
        print(f"{Colors.PURPLE}{Colors.BOLD}║{' '*18}🔴 CONNECT 4 GAME 🟡{' '*18}║{Colors.END}")
        print(f"{Colors.PURPLE}{Colors.BOLD}{'╠'+'═'*58+'╣'}{Colors.END}")
        print(f"{Colors.PURPLE}{Colors.BOLD}║{Colors.END} {Colors.CYAN}1.{Colors.END} {Colors.WHITE}Player vs Player{Colors.END}{' '*38}{Colors.PURPLE}{Colors.BOLD}║{Colors.END}")
        print(f"{Colors.PURPLE}{Colors.BOLD}║{Colors.END} {Colors.CYAN}2.{Colors.END} {Colors.WHITE}Player vs Random Bot{Colors.END}{' '*33}{Colors.PURPLE}{Colors.BOLD}║{Colors.END}")
        print(f"{Colors.PURPLE}{Colors.BOLD}║{Colors.END} {Colors.CYAN}3.{Colors.END} {Colors.WHITE}Quit{Colors.END}{' '*48}{Colors.PURPLE}{Colors.BOLD}║{Colors.END}")
        print(f"{Colors.PURPLE}{Colors.BOLD}{'╚'+'═'*58+'╝'}{Colors.END}")
        
        choice = input(f"\n{Colors.BOLD}Select game mode {Colors.CYAN}(1-3){Colors.END}: ").strip()
        
        if choice == "1":
            play_game("pvp")
        elif choice == "2":
            play_game("pvb")
        elif choice == "3":
            print(f"\n{Colors.GREEN}{Colors.BOLD}🎮 Thanks for playing Connect 4! Goodbye! 👋{Colors.END}")
            break
        else:
            print(f"{Colors.RED}{Colors.BOLD}❌ Invalid choice. Please enter 1, 2, or 3.{Colors.END}")
            input(f"{Colors.WHITE}Press Enter to continue...{Colors.END}")
        
        if choice in ["1", "2"]:
            play_again = input(f"\n{Colors.BOLD}🎮 Play again? {Colors.CYAN}(y/n){Colors.END}: ").strip().lower()
            if play_again != 'y':
                print(f"\n{Colors.GREEN}{Colors.BOLD}🎮 Thanks for playing Connect 4! Goodbye! 👋{Colors.END}")
                break

if __name__ == "__main__":
    main()