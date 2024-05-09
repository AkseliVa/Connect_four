import unittest
import numpy as np
from connect4 import create_board, drop_piece, is_valid_location, winning_move, get_next_open_row

class TestConnectFour(unittest.TestCase):
    def setUp(self):
        self.board = create_board()

    def test_create_board(self):
        self.assertIsInstance(self.board, np.ndarray)
        self.assertEqual(self.board.shape, (6, 7))
        self.assertTrue(np.all(self.board == 0))

    def test_drop_piece(self):
        drop_piece(self.board, 0, 3, 1)
        self.assertEqual(self.board[0][3], 1)

    def test_is_valid_location(self):
        self.assertTrue(is_valid_location(self.board, 0))
        drop_piece(self.board, 5, 0, 1)
        self.assertFalse(is_valid_location(self.board, 0))

    def test_winning_move(self):
        drop_piece(self.board, 5, 0, 1)
        drop_piece(self.board, 5, 1, 1)
        drop_piece(self.board, 5, 2, 1)
        drop_piece(self.board, 5, 3, 1)
        self.assertTrue(winning_move(self.board, 1))

    def test_get_next_open_row(self):
        drop_piece(self.board, 5, 0, 1)  # Fill row 5 (bottom row)
        drop_piece(self.board, 4, 0, 1)  # Fill row 4
        self.assertEqual(get_next_open_row(self.board, 0), 3)

if __name__ == '__main__':
    unittest.main()
