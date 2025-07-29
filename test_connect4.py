import unittest
import numpy as np
import torch
from connect4_board import Connect4Board
from dqn_agent import DQNAgent, Connect4Environment, DQN
import os

class TestConnect4Board(unittest.TestCase):
    def setUp(self):
        self.board = Connect4Board()
    
    def test_initialization(self):
        self.assertEqual(self.board.rows, 6)
        self.assertEqual(self.board.cols, 7)
        self.assertEqual(self.board.current_player, 1)
        self.assertTrue(np.array_equal(self.board.board, np.zeros((6, 7))))
    
    def test_valid_actions(self):
        valid_actions = self.board.get_valid_actions()
        self.assertEqual(valid_actions, [0, 1, 2, 3, 4, 5, 6])
    
    def test_make_move(self):
        # Test valid move
        result = self.board.make_move(3)
        self.assertTrue(result)
        self.assertEqual(self.board.board[5][3], 1)
        self.assertEqual(self.board.current_player, 2)
        
        # Test invalid move (out of bounds)
        result = self.board.make_move(-1)
        self.assertFalse(result)
        
        result = self.board.make_move(7)
        self.assertFalse(result)
    
    def test_column_full(self):
        # Fill column 0
        for _ in range(6):
            self.board.make_move(0)
        
        # Try to add another piece
        result = self.board.make_move(0)
        self.assertFalse(result)
        
        # Check that column 0 is not in valid actions
        valid_actions = self.board.get_valid_actions()
        self.assertNotIn(0, valid_actions)
    
    def test_horizontal_win(self):
        # Set up horizontal win for player 1
        for col in range(4):
            self.board.board[5][col] = 1
        
        winner = self.board.check_winner()
        self.assertEqual(winner, 1)
        self.assertTrue(self.board.is_game_over())
    
    def test_vertical_win(self):
        # Set up vertical win for player 2
        for row in range(4):
            self.board.board[row][3] = 2
        
        winner = self.board.check_winner()
        self.assertEqual(winner, 2)
        self.assertTrue(self.board.is_game_over())
    
    def test_diagonal_win(self):
        # Set up diagonal win for player 1 (top-left to bottom-right)
        for i in range(4):
            self.board.board[i][i] = 1
        
        winner = self.board.check_winner()
        self.assertEqual(winner, 1)
        self.assertTrue(self.board.is_game_over())
    
    def test_no_winner(self):
        winner = self.board.check_winner()
        self.assertEqual(winner, 0)
        self.assertFalse(self.board.is_game_over())
    
    def test_reset(self):
        self.board.make_move(3)
        self.board.reset()
        self.assertEqual(self.board.current_player, 1)
        self.assertTrue(np.array_equal(self.board.board, np.zeros((6, 7))))
    
    def test_copy(self):
        self.board.make_move(3)
        copied_board = self.board.copy()
        
        self.assertTrue(np.array_equal(self.board.board, copied_board.board))
        self.assertEqual(self.board.current_player, copied_board.current_player)
        
        # Modify original and ensure copy is unchanged
        self.board.make_move(4)
        self.assertFalse(np.array_equal(self.board.board, copied_board.board))

class TestDQN(unittest.TestCase):
    def setUp(self):
        self.dqn = DQN()
    
    def test_forward_pass(self):
        input_tensor = torch.randn(1, 42)
        output = self.dqn(input_tensor)
        self.assertEqual(output.shape, (1, 7))
    
    def test_output_values(self):
        input_tensor = torch.zeros(1, 42)
        output = self.dqn(input_tensor)
        self.assertEqual(len(output[0]), 7)

class TestDQNAgent(unittest.TestCase):
    def setUp(self):
        self.agent = DQNAgent()
    
    def test_initialization(self):
        self.assertEqual(self.agent.state_size, 42)
        self.assertEqual(self.agent.action_size, 7)
        self.assertEqual(self.agent.epsilon, 1.0)
        self.assertEqual(len(self.agent.memory), 0)
    
    def test_act_with_valid_actions(self):
        state = np.zeros((6, 7))
        valid_actions = [0, 1, 2, 3, 4, 5, 6]
        action = self.agent.act(state, valid_actions)
        self.assertIn(action, valid_actions)
    
    def test_act_with_limited_actions(self):
        state = np.zeros((6, 7))
        valid_actions = [2, 4]
        action = self.agent.act(state, valid_actions)
        self.assertIn(action, valid_actions)
    
    def test_remember(self):
        state = np.zeros((6, 7))
        next_state = np.zeros((6, 7))
        self.agent.remember(state, 3, 1.0, next_state, False)
        self.assertEqual(len(self.agent.memory), 1)
    
    def test_save_and_load(self):
        test_file = "test_agent.pth"
        
        # Modify epsilon to test save/load
        original_epsilon = 0.5
        self.agent.epsilon = original_epsilon
        
        # Save agent
        self.agent.save(test_file)
        self.assertTrue(os.path.exists(test_file))
        
        # Create new agent and load
        new_agent = DQNAgent()
        new_agent.load(test_file)
        
        self.assertEqual(new_agent.epsilon, original_epsilon)
        
        # Clean up
        os.remove(test_file)

class TestConnect4Environment(unittest.TestCase):
    def setUp(self):
        self.env = Connect4Environment()
    
    def test_reset(self):
        state = self.env.reset()
        self.assertEqual(state.shape, (6, 7))
        self.assertTrue(np.array_equal(state, np.zeros((6, 7))))
    
    def test_step_valid_action(self):
        state, reward, done, _ = self.env.step(3, 1)
        self.assertEqual(state.shape, (6, 7))
        self.assertEqual(state[5][3], 1)
        self.assertFalse(done)
    
    def test_step_invalid_action(self):
        state, reward, done, _ = self.env.step(-1, 1)
        self.assertEqual(reward, -10)
        self.assertTrue(done)
    
    def test_get_valid_actions(self):
        valid_actions = self.env.get_valid_actions()
        self.assertEqual(valid_actions, [0, 1, 2, 3, 4, 5, 6])
    
    def test_get_current_player(self):
        self.assertEqual(self.env.get_current_player(), 1)
        self.env.step(3, 1)
        self.assertEqual(self.env.get_current_player(), 2)

class TestGameplay(unittest.TestCase):
    def test_complete_game(self):
        env = Connect4Environment()
        agent = DQNAgent()
        
        state = env.reset()
        moves = 0
        max_moves = 42
        
        while not env.board.is_game_over() and moves < max_moves:
            valid_actions = env.get_valid_actions()
            if not valid_actions:
                break
                
            current_player = env.get_current_player()
            action = agent.act(state, valid_actions)
            state, reward, done, _ = env.step(action, current_player)
            moves += 1
        
        # Game should end within 42 moves
        self.assertLessEqual(moves, max_moves)

def run_tests():
    unittest.main(verbosity=2)

if __name__ == "__main__":
    print("Running Connect 4 DQN Tests...")
    print("=" * 50)
    run_tests()