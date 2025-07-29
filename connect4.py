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
                    print(f"{Colors.BACKGROUND_BLUE}{Colors.BLUE}{Colors.BOLD} 🔵 {Colors.END}", end="")
                else:
                    print(f"{Colors.BACKGROUND_BLUE}{Colors.RED}{Colors.BOLD} 🔴 {Colors.END}", end="")
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
        if not valid_moves:
            return 0
        return random.choice(valid_moves)

def get_human_move(game: Connect4) -> int:
    while True:
        try:
            move = int(input(f"Enter column (1-{game.cols}): ")) - 1
            if game.is_valid_move(move):
                return move
            else:
                print("Invalid move! Column is full or out of range.")
        except ValueError:
            print("Please enter a valid number.")

def play_game(mode: str = "pvp", dqn_bot=None):
    """Play a game of Connect 4"""
    game = Connect4()
    
    if mode == "pvp":
        print("Player 1: 🔵 (Blue) | Player 2: 🔴 (Red)")
    elif mode == "pve":
        print("You: 🔵 (Blue) | DQN Agent: 🔴 (Red)")
    elif mode == "eve":
        print("DQN Agent 1: 🔵 (Blue) | DQN Agent 2: 🔴 (Red)")
    
    while True:
        game.display_board()
        
        if game.current_player == Player.HUMAN:
            if mode == "pvp":
                print(f"\n🔵 Player 1's turn")
                move = get_human_move(game)
            elif mode == "pve":
                print(f"\n🔵 Your turn")
                move = get_human_move(game)
            else:  # eve
                move = dqn_bot.get_move(game)
                print(f"\n🧠 🔵 DQN Agent 1 plays column {move + 1}")
        else:
            if mode == "pvp":
                print(f"\n🔴 Player 2's turn")
                move = get_human_move(game)
            elif mode == "pve":
                move = dqn_bot.get_move(game)
                print(f"\n🧠 🔴 DQN Agent plays column {move + 1}")
            else:  # eve
                move = dqn_bot.get_move(game)
                print(f"\n🧠 🔴 DQN Agent 2 plays column {move + 1}")
        
        game.make_move(move, game.current_player)
        
        result = game.check_winner()
        if result != GameResult.ONGOING:
            game.display_board()
            if result == GameResult.PLAYER1_WIN:
                if mode == "pvp":
                    print(f"\n🏆 Player 1 (🔵) wins!")
                elif mode == "pve":
                    print(f"\n🏆 You (🔵) win!")
                else:
                    print(f"\n🏆 DQN Agent 1 (🔵) wins!")
            elif result == GameResult.PLAYER2_WIN:
                if mode == "pvp":
                    print(f"\n🏆 Player 2 (🔴) wins!")
                elif mode == "pve":
                    print(f"\n🤖 DQN Agent (🔴) wins!")
                else:
                    print(f"\n🏆 DQN Agent 2 (🔴) wins!")
            else:
                print(f"\n🤝 It's a draw!")
            break

def main():
    # Try to load DQN bot if available
    dqn_bot = None
    try:
        from dqn_agent import DQNBot, DQNAgent
        agent = DQNAgent()
        agent.load_model("dqn_connect4.pth")
        dqn_bot = DQNBot(agent)
        print("✅ DQN agent loaded successfully!")
    except:
        print("⚠️  DQN agent not available, some modes may not work.")
    
    print("\n=== Connect 4 Game ===")
    print("1. Player vs Player")
    print("2. Player vs DQN Agent")
    print("3. DQN Agent vs DQN Agent")
    print("4. Exit")
    
    while True:
        try:
            choice = input("\nSelect mode (1-4): ").strip()
            
            if choice == "1":
                play_game("pvp")
            elif choice == "2":
                if dqn_bot:
                    play_game("pve", dqn_bot)
                else:
                    print("❌ DQN agent not available!")
            elif choice == "3":
                if dqn_bot:
                    play_game("eve", dqn_bot)
                else:
                    print("❌ DQN agent not available!")
            elif choice == "4":
                print("Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")
                
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 