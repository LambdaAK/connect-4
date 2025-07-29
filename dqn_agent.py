import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import numpy as np
import random
from collections import deque
from connect4 import Connect4, Player, GameResult

class DQN(nn.Module):
    def __init__(self, input_size=42, hidden_size=512, output_size=7):
        super(DQN, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, hidden_size)
        self.fc4 = nn.Linear(hidden_size, output_size)
        
    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = F.relu(self.fc3(x))
        return self.fc4(x)

class DQNAgent:
    def __init__(self, state_size=42, action_size=7, lr=0.001, gamma=0.95, 
                 epsilon=1.0, epsilon_min=0.01, epsilon_decay=0.995, 
                 memory_size=10000, batch_size=32):
        self.state_size = state_size
        self.action_size = action_size
        self.lr = lr
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.memory_size = memory_size
        self.batch_size = batch_size
        
        self.memory = deque(maxlen=memory_size)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        self.q_network = DQN(state_size, 512, action_size).to(self.device)
        self.target_network = DQN(state_size, 512, action_size).to(self.device)
        self.optimizer = optim.Adam(self.q_network.parameters(), lr=lr)
        
        self.update_target_network()
        
    def update_target_network(self):
        self.target_network.load_state_dict(self.q_network.state_dict())
    
    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))
    
    def act(self, state, valid_actions):
        if np.random.random() <= self.epsilon:
            return random.choice(valid_actions)
        
        state_tensor = torch.FloatTensor(state.flatten()).unsqueeze(0).to(self.device)
        q_values = self.q_network(state_tensor)
        
        # Mask invalid actions
        masked_q_values = q_values.clone()
        for i in range(self.action_size):
            if i not in valid_actions:
                masked_q_values[0][i] = float('-inf')
        
        return masked_q_values.argmax().item()
    
    def replay(self):
        if len(self.memory) < self.batch_size:
            return
        
        batch = random.sample(self.memory, self.batch_size)
        states = torch.FloatTensor([e[0].flatten() for e in batch]).to(self.device)
        actions = torch.LongTensor([e[1] for e in batch]).to(self.device)
        rewards = torch.FloatTensor([e[2] for e in batch]).to(self.device)
        next_states = torch.FloatTensor([e[3].flatten() for e in batch]).to(self.device)
        dones = torch.BoolTensor([e[4] for e in batch]).to(self.device)
        
        current_q_values = self.q_network(states).gather(1, actions.unsqueeze(1))
        next_q_values = self.target_network(next_states).max(1)[0].detach()
        target_q_values = rewards + (self.gamma * next_q_values * ~dones)
        
        loss = F.mse_loss(current_q_values.squeeze(), target_q_values)
        
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
    
    def save(self, filepath):
        torch.save({
            'model_state_dict': self.q_network.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'epsilon': self.epsilon
        }, filepath)
    
    def load(self, filepath):
        checkpoint = torch.load(filepath, map_location=self.device)
        self.q_network.load_state_dict(checkpoint['model_state_dict'])
        self.target_network.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.epsilon = checkpoint['epsilon']

class DQNBot:
    """Bot wrapper for DQN agent"""
    
    def __init__(self, agent: DQNAgent):
        self.agent = agent
    
    def get_move(self, game: Connect4) -> int:
        """Get move from DQN agent"""
        # Convert game state to tensor format
        state = self._game_to_state(game)
        valid_actions = game.get_valid_moves()
        
        # Use greedy action (no exploration during testing)
        state_tensor = torch.FloatTensor(state.flatten()).unsqueeze(0).to(self.agent.device)
        q_values = self.agent.q_network(state_tensor)
        
        # Mask invalid actions
        masked_q_values = q_values.clone()
        for i in range(self.agent.action_size):
            if i not in valid_actions:
                masked_q_values[0][i] = float('-inf')
        
        return masked_q_values.argmax().item()
    
    def _game_to_state(self, game: Connect4) -> np.ndarray:
        """Convert Connect4 game to state array"""
        state = np.zeros((6, 7), dtype=np.float32)
        for row in range(6):
            for col in range(7):
                if game.board[row][col] == Player.HUMAN:
                    state[row][col] = 1.0
                elif game.board[row][col] == Player.BOT:
                    state[row][col] = -1.0
        return state

class Connect4Environment:
    def __init__(self):
        self.board = Connect4()
        self.reset()
    
    def reset(self):
        self.board.reset()
        return self._game_to_state(self.board)
    
    def step(self, action, player):
        if not self.board.is_valid_move(action):
            return self._game_to_state(self.board), -10, True, {}
        
        self.board.make_move(action, player)
        state = self._game_to_state(self.board)
        reward = self._get_reward(self.board, player)
        done = self.board.check_winner() != GameResult.ONGOING
        
        return state, reward, done, {}
    
    def get_valid_actions(self):
        return self.board.get_valid_moves()
    
    def get_current_player(self):
        return self.board.current_player
    
    def _game_to_state(self, game: Connect4) -> np.ndarray:
        """Convert Connect4 game to state array"""
        state = np.zeros((6, 7), dtype=np.float32)
        for row in range(6):
            for col in range(7):
                if game.board[row][col] == Player.HUMAN:
                    state[row][col] = 1.0
                elif game.board[row][col] == Player.BOT:
                    state[row][col] = -1.0
        return state
    
    def _get_reward(self, game: Connect4, player: Player) -> float:
        """Calculate reward based on game result"""
        result = game.check_winner()
        if result == GameResult.ONGOING:
            return 0.0
        elif result == GameResult.DRAW:
            return 0.1
        elif (result == GameResult.PLAYER1_WIN and player == Player.HUMAN) or \
             (result == GameResult.PLAYER2_WIN and player == Player.BOT):
            return 1.0
        else:
            return -1.0