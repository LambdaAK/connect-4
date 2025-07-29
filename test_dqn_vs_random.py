#!/usr/bin/env python3
"""
Test DQN agent against Random bot
"""

import numpy as np
import time
import os
from connect4 import Connect4, Player, GameResult, RandomBot
from dqn_agent import DQNAgent, DQNBot

def clear_screen():
    """Clear the terminal screen"""
    os.system('clear' if os.name == 'posix' else 'cls')

def test_dqn_vs_random(model_path="dqn_connect4.pth", num_games=1000, watch=False):
    """Test DQN agent against random bot"""
    print(f"Loading model from {model_path}...")
    agent = DQNAgent()
    agent.load(model_path)
    dqn_bot = DQNBot(agent)
    random_bot = RandomBot()
    
    wins = 0
    draws = 0
    losses = 0
    
    print(f"Testing DQN agent vs Random bot for {num_games} games...")
    if watch:
        print("Watch mode enabled - you'll see the games being played!")
        print("DQN Agent: 🔴 (Red) | Random Bot: 🔵 (Blue)")
        input("Press Enter to start...")
    
    for i in range(num_games):
        game = Connect4()
        
        # Randomly decide who goes first
        dqn_goes_first = np.random.random() < 0.5
        
        if watch:
            clear_screen()
            print(f"Game {i+1}/{num_games}")
            if dqn_goes_first:
                print(f"DQN Agent (🔴) goes first | Random Bot (🔵) goes second")
            else:
                print(f"Random Bot (🔵) goes first | DQN Agent (🔴) goes second")
            print("=" * 50)
        
        while True:
            if game.current_player == Player.HUMAN:
                # DQN agent's turn (always red)
                action = dqn_bot.get_move(game)
                if watch:
                    print(f"🧠 🔴 DQN Agent plays column {action + 1}")
            else:
                # Random bot's turn (always blue)
                action = random_bot.get_move(game)
                if watch:
                    print(f"🤖 🔵 Random Bot plays column {action + 1}")
            
            game.make_move(action, game.current_player)
            
            if watch:
                game.display_board()
                time.sleep(0.5)  # Pause to see the move
            
            result = game.check_winner()
            if result != GameResult.ONGOING:
                # Determine result - DQN agent is Player.HUMAN (red), Random bot is Player.BOT (blue)
                if result == GameResult.PLAYER1_WIN:
                    wins += 1
                    if watch:
                        print(f"\n🏆 DQN Agent (🔴) wins!")
                elif result == GameResult.PLAYER2_WIN:
                    losses += 1
                    if watch:
                        print(f"\n💪 Random Bot (🔵) wins!")
                else:  # DRAW
                    draws += 1
                    if watch:
                        print(f"\n🤝 It's a draw!")
                
                if watch:
                    input("Press Enter to continue...")
                break
        
        if not watch and (i + 1) % 100 == 0:
            print(f"Progress: {i+1}/{num_games} games completed")
    
    win_rate = wins / num_games
    draw_rate = draws / num_games
    loss_rate = losses / num_games
    
    print(f"\n=== Test Results ===")
    print(f"Games played: {num_games}")
    print(f"Wins: {wins} ({win_rate:.1%})")
    print(f"Draws: {draws} ({draw_rate:.1%})")
    print(f"Losses: {losses} ({loss_rate:.1%})")
    print(f"Win Rate: {win_rate:.1%}")
    
    return win_rate

def interactive_test(model_path="dqn_connect4.pth"):
    """Interactive test - play against the agent"""
    print(f"Loading model from {model_path}...")
    agent = DQNAgent()
    agent.load(model_path)
    dqn_bot = DQNBot(agent)
    
    print("Interactive test mode!")
    print("You will play as 🔵 (blue pieces) against the DQN agent 🔴 (red pieces)")
    print("Enter column numbers (1-7) to make moves.")
    print("Type 'quit' to exit.\n")
    
    while True:
        game = Connect4()
        game.display_board()
        
        while True:
            if game.current_player == Player.HUMAN:
                # Human's turn
                try:
                    move_input = input(f"\n🔵 Your turn (1-7): ").strip()
                    if move_input.lower() == 'quit':
                        print("Goodbye!")
                        return
                    
                    move = int(move_input) - 1
                    if not game.is_valid_move(move):
                        print("❌ Invalid move! Column is full or out of range.")
                        continue
                    
                    game.make_move(move, Player.HUMAN)
                except ValueError:
                    print("❌ Please enter a valid number (1-7).")
                    continue
            else:
                # DQN agent's turn
                print(f"\n🧠 DQN agent is thinking...")
                move = dqn_bot.get_move(game)
                print(f"🔴 DQN agent plays column {move + 1}")
                game.make_move(move, Player.BOT)
            
            game.display_board()
            
            result = game.check_winner()
            if result != GameResult.ONGOING:
                if result == GameResult.PLAYER1_WIN:
                    print(f"\n🏆 You (🔵) win! 🎉")
                elif result == GameResult.PLAYER2_WIN:
                    print(f"\n🤖 DQN agent (🔴) wins! 💪")
                else:
                    print(f"\n🤝 It's a draw! ⚖️")
                break
        
        play_again = input(f"\nPlay again? (y/n): ").strip().lower()
        if play_again != 'y':
            print("Thanks for playing!")
            break

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test DQN agent against Random bot")
    parser.add_argument("--model", type=str, default="dqn_connect4.pth", help="Model path")
    parser.add_argument("--games", type=int, default=1000, help="Number of games to test")
    parser.add_argument("--watch", action="store_true", help="Watch games being played")
    parser.add_argument("--interactive", action="store_true", help="Play against the agent")
    
    args = parser.parse_args()
    
    if args.interactive:
        interactive_test(args.model)
    else:
        test_dqn_vs_random(args.model, args.games, args.watch) 