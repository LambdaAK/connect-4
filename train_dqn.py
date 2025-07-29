import os
import numpy as np
import matplotlib.pyplot as plt
from dqn_agent import DQNAgent, Connect4Environment
from connect4 import Connect4, Player, GameResult
import random

def train_dqn(episodes=2000, target_update_freq=100, save_freq=100):
    env = Connect4Environment()
    agent1 = DQNAgent()  # DQN agent (Player 1)
    agent2 = DQNAgent()  # DQN agent (Player 2)
    
    scores = []
    wins_player1 = 0
    wins_player2 = 0
    draws = 0
    
    for episode in range(1, episodes + 1):
        state = env.reset()
        total_reward = 0
        steps = 0
        max_steps = 42  # Maximum possible moves in Connect 4
        
        while env.board.check_winner() == GameResult.ONGOING and steps < max_steps:
            current_player = env.get_current_player()
            valid_actions = env.get_valid_actions()
            
            if len(valid_actions) == 0:
                break
            
            if current_player == Player.HUMAN:
                action = agent1.act(state, valid_actions)
                next_state, reward, done, _ = env.step(action, current_player)
                agent1.remember(state, action, reward, next_state, done)
                total_reward += reward
            else:
                action = agent2.act(state, valid_actions)
                next_state, reward, done, _ = env.step(action, current_player)
                agent2.remember(state, action, -reward, next_state, done)  # Opposite reward for player 2
            
            state = next_state
            steps += 1
        
        # Count wins and draws
        winner = env.board.check_winner()
        if winner == GameResult.PLAYER1_WIN:
            wins_player1 += 1
        elif winner == GameResult.PLAYER2_WIN:
            wins_player2 += 1
        else:
            draws += 1
        
        scores.append(total_reward)
        
        # Train both agents
        agent1.replay()
        agent2.replay()
        
        # Update target networks
        if episode % target_update_freq == 0:
            agent1.update_target_network()
            agent2.update_target_network()
        
        # Save agents every 100 episodes
        if episode % save_freq == 0:
            agent1_path = f"agents/dqn_agent1_episode_{episode}.pth"
            agent2_path = f"agents/dqn_agent2_episode_{episode}.pth"
            agent1.save(agent1_path)
            agent2.save(agent2_path)
            
            print(f"Episode {episode}/{episodes}")
            print(f"Average Score (last 100): {np.mean(scores[-100:]):.2f}")
            print(f"Player 1 Wins: {wins_player1}, Player 2 Wins: {wins_player2}, Draws: {draws}")
            print(f"Epsilon: {agent1.epsilon:.3f}")
            print(f"Agents saved to {agent1_path} and {agent2_path}")
            print("-" * 50)
    
    return agent1, agent2, scores

def play_against_random(agent, num_games=100):
    env = Connect4Environment()
    wins = 0
    losses = 0
    draws = 0
    
    for game in range(num_games):
        state = env.reset()
        
        # Randomly decide if agent goes first or second
        agent_player = random.choice([Player.HUMAN, Player.BOT])
        
        while env.board.check_winner() == GameResult.ONGOING:
            current_player = env.get_current_player()
            valid_actions = env.get_valid_actions()
            
            if len(valid_actions) == 0:
                break
            
            if current_player == agent_player:
                # Agent's turn
                action = agent.act(state, valid_actions)
                next_state, reward, done, _ = env.step(action, current_player)
                state = next_state
            else:
                # Random opponent's turn
                action = random.choice(valid_actions)
                next_state, reward, done, _ = env.step(action, current_player)
                state = next_state
        
        # Determine winner
        winner = env.board.check_winner()
        if winner == GameResult.PLAYER1_WIN and agent_player == Player.HUMAN:
            wins += 1
        elif winner == GameResult.PLAYER2_WIN and agent_player == Player.BOT:
            wins += 1
        elif winner == GameResult.DRAW:
            draws += 1
        else:
            losses += 1
    
    win_rate = wins / num_games
    print(f"Win Rate against Random: {win_rate:.2f}")
    print(f"Wins: {wins}, Losses: {losses}, Draws: {draws}")
    return win_rate

def plot_training_progress(scores):
    plt.figure(figsize=(12, 4))
    
    plt.subplot(1, 2, 1)
    plt.plot(scores)
    plt.title('Training Scores')
    plt.xlabel('Episode')
    plt.ylabel('Score')
    
    plt.subplot(1, 2, 2)
    window_size = 100
    if len(scores) >= window_size:
        moving_avg = [np.mean(scores[i:i+window_size]) for i in range(len(scores)-window_size+1)]
        plt.plot(moving_avg)
        plt.title(f'Moving Average Score (window={window_size})')
        plt.xlabel('Episode')
        plt.ylabel('Average Score')
    
    plt.tight_layout()
    plt.savefig('training_progress.png')
    plt.show()

if __name__ == "__main__":
    print("Starting DQN training for Connect 4...")
    print("This will train two DQN agents to play against each other.")
    print("Agents will be saved every 100 episodes in the 'agents' directory.")
    print("-" * 60)
    
    # Train the agents
    agent1, agent2, scores = train_dqn(episodes=10000)
    
    
    # Plot training progress
    plot_training_progress(scores)
    
    # Test against random player
    print("\nTesting trained agent against random player...")
    agent1.epsilon = 0  # Disable exploration for testing
    play_against_random(agent1, num_games=100)
    
    print("\nTraining completed!")
    print("Final models saved as dqn_agent1_final.pth and dqn_agent2_final.pth")
    agent1.save("agents/dqn_agent1_final.pth")
    agent2.save("agents/dqn_agent2_final.pth")