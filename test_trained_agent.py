#!/usr/bin/env python3
"""
Test trained DQN agents against random bot
"""

import os
import glob
import numpy as np
import time
from connect4 import Connect4, Player, GameResult, RandomBot
from dqn_agent import DQNAgent, DQNBot

def clear_screen():
    """Clear the terminal screen"""
    os.system('clear' if os.name == 'posix' else 'cls')

def scan_agents_directory():
    """Scan the agents directory and return available models"""
    agents_dir = "agents"
    if not os.path.exists(agents_dir):
        print(f"❌ Agents directory '{agents_dir}' not found!")
        return []
    
    # Find all .pth files
    pattern = os.path.join(agents_dir, "*.pth")
    model_files = glob.glob(pattern)
    
    if not model_files:
        print(f"❌ No model files found in '{agents_dir}' directory!")
        return []
    
    # Sort by episode number
    def extract_episode(filename):
        try:
            # Extract episode number from filename like "dqn_agent1_episode_100.pth"
            parts = filename.split('_')
            episode_part = parts[-1].replace('.pth', '')
            return int(episode_part)
        except:
            return 0
    
    model_files.sort(key=extract_episode)
    return model_files

def select_agent(model_files):
    """Let user select an agent from the available models"""
    print("🤖 Available Trained Agents:")
    print("=" * 50)
    
    for i, model_file in enumerate(model_files, 1):
        filename = os.path.basename(model_file)
        # Extract episode number
        try:
            episode = filename.split('_')[-1].replace('.pth', '')
            agent_num = filename.split('_')[1]
            print(f"{i:2d}. {filename} (Episode {episode})")
        except:
            print(f"{i:2d}. {filename}")
    
    print("=" * 50)
    
    while True:
        try:
            choice = input(f"Select an agent (1-{len(model_files)}): ").strip()
            choice_idx = int(choice) - 1
            
            if 0 <= choice_idx < len(model_files):
                selected_model = model_files[choice_idx]
                print(f"✅ Selected: {os.path.basename(selected_model)}")
                return selected_model
            else:
                print(f"❌ Please enter a number between 1 and {len(model_files)}")
        except ValueError:
            print("❌ Please enter a valid number")
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            return None

def test_agent_vs_random(model_path, num_games=100, watch=False):
    """Test selected agent against random bot"""
    print(f"Loading model from {model_path}...")
    agent = DQNAgent()
    agent.load(model_path)
    dqn_bot = DQNBot(agent)
    random_bot = RandomBot()
    
    wins = 0
    draws = 0
    losses = 0
    
    print(f"Testing trained agent vs Random bot for {num_games} games...")
    if watch:
        print("Watch mode enabled - you'll see the games being played!")
        print("Trained Agent: 🔴 (Red) | Random Bot: 🔵 (Blue)")
        input("Press Enter to start...")
    
    for i in range(num_games):
        game = Connect4()
        
        # Randomly decide who goes first
        agent_goes_first = np.random.random() < 0.5
        
        if watch:
            clear_screen()
            print(f"Game {i+1}/{num_games}")
            if agent_goes_first:
                print(f"Trained Agent (🔴) goes first | Random Bot (🔵) goes second")
            else:
                print(f"Random Bot (🔵) goes first | Trained Agent (🔴) goes second")
            print("=" * 50)
        
        while True:
            if game.current_player == Player.HUMAN:
                # Trained agent's turn (always red)
                action = dqn_bot.get_move(game)
                if watch:
                    print(f"🧠 🔴 Trained Agent plays column {action + 1}")
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
                # Determine result - Trained agent is Player.HUMAN (red), Random bot is Player.BOT (blue)
                if result == GameResult.PLAYER1_WIN:
                    wins += 1
                    if watch:
                        print(f"\n🏆 Trained Agent (🔴) wins!")
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
        
        if not watch and (i + 1) % 20 == 0:
            print(f"Progress: {i+1}/{num_games} games completed")
    
    win_rate = wins / num_games
    draw_rate = draws / num_games
    loss_rate = losses / num_games
    
    print(f"\n=== Test Results ===")
    print(f"Model: {os.path.basename(model_path)}")
    print(f"Games played: {num_games}")
    print(f"Wins: {wins} ({win_rate:.1%})")
    print(f"Draws: {draws} ({draw_rate:.1%})")
    print(f"Losses: {losses} ({loss_rate:.1%})")
    print(f"Win Rate: {win_rate:.1%}")
    
    return win_rate

def interactive_test(model_path):
    """Interactive test - play against the trained agent"""
    print(f"Loading model from {model_path}...")
    agent = DQNAgent()
    agent.load(model_path)
    dqn_bot = DQNBot(agent)
    
    print("Interactive test mode!")
    print("You will play as 🔵 (blue pieces) against the trained agent 🔴 (red pieces)")
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
                # Trained agent's turn
                print(f"\n🧠 Trained agent is thinking...")
                move = dqn_bot.get_move(game)
                print(f"🔴 Trained agent plays column {move + 1}")
                game.make_move(move, Player.BOT)
            
            game.display_board()
            
            result = game.check_winner()
            if result != GameResult.ONGOING:
                if result == GameResult.PLAYER1_WIN:
                    print(f"\n🏆 You (🔵) win! 🎉")
                elif result == GameResult.PLAYER2_WIN:
                    print(f"\n🤖 Trained agent (🔴) wins! 💪")
                else:
                    print(f"\n🤝 It's a draw! ⚖️")
                break
        
        play_again = input(f"\nPlay again? (y/n): ").strip().lower()
        if play_again != 'y':
            print("Thanks for playing!")
            break

def main():
    print("🤖 Trained Agent Tester")
    print("=" * 30)
    
    # Scan for available agents
    model_files = scan_agents_directory()
    if not model_files:
        return
    
    # Let user select an agent
    selected_model = select_agent(model_files)
    if selected_model is None:
        return
    
    print("\n" + "=" * 50)
    print("Testing Options:")
    print("1. Quick Test (100 games, no watching)")
    print("2. Watch Games (10 games with visual)")
    print("3. Interactive Test (play against agent)")
    print("4. Exit")
    
    while True:
        try:
            choice = input("\nSelect option (1-4): ").strip()
            
            if choice == "1":
                test_agent_vs_random(selected_model, num_games=100, watch=False)
            elif choice == "2":
                test_agent_vs_random(selected_model, num_games=10, watch=True)
            elif choice == "3":
                interactive_test(selected_model)
            elif choice == "4":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 