import unittest
import tablut.rules.ashton as ashton
from tablut.board import WinException, LoseException, DrawException
from tablut.game import Player


class AshtonLegalMovesTest(unittest.TestCase):
    def test_to_and_from_same_cell(self):
        board = ashton.Board()
        legal, _ = board.is_legal(Player.WHITE, (2, 4), (2, 4))
        self.assertFalse(legal)

    def test_to_escape_defender(self):
        board = ashton.Board()
        legal, _ = board.is_legal(Player.WHITE, (2, 4), (2, 0))
        self.assertFalse(legal)

    def test_to_escape_attacker(self):
        board = ashton.Board()
        legal, _ = board.is_legal(Player.BLACK, (0, 3), (0, 2))
        self.assertFalse(legal)

    def test_to_camp_not_attacker(self):
        board = ashton.Board()
        legal, _ = board.is_legal(Player.WHITE, (1, 4), (1, 0))
        self.assertFalse(legal)

    def test_not_orthogonal(self):
        board = ashton.Board()
        legal, _ = board.is_legal(Player.BLACK, (0, 3), (1, 1))
        self.assertFalse(legal)

    def test_simple_move(self):
        board = ashton.Board()
        board.step(Player.BLACK, (0, 3), (1, 3))
        self.assertTrue(int(board.board[1][3]) == -2)

    def test_pass_over_checker(self):
        board = ashton.Board()
        board.step(Player.BLACK, (0, 3), (1, 3))
        legal, _ = board.is_legal(Player.BLACK, (1, 3), (1, 5))
        self.assertFalse(legal)

    def test_end_on_checker(self):
        board = ashton.Board()
        board.step(Player.BLACK, (0, 3), (1, 3))
        legal, _ = board.is_legal(Player.BLACK, (1, 3), (1, 4))
        self.assertFalse(legal)

    def test_attacker_moving_on_camp(self):
        board = ashton.Board()
        # make space in camp
        board.step(Player.BLACK, (3, 0), (3, 2))
        # slide checkers in camp
        legal, _ = board.is_legal(Player.BLACK, (4, 0), (3, 0))
        self.assertTrue(legal)

    def test_attacker_returning_on_camp(self):
        board = ashton.Board()
        # make space in camp
        board.step(Player.BLACK, (3, 0), (3, 2))
        # slide checkers in camp
        board.is_legal(Player.BLACK, (4, 1), (3, 1))
        legal, _ = board.is_legal(Player.BLACK, (3, 1), (3, 0))
        self.assertFalse(legal)

    def test_move_backward(self):
        board = ashton.Board()
        legal, _ = board.is_legal(Player.BLACK, (3, 8), (3, 5))
        self.assertTrue(legal)


class AshtonCaptureTest(unittest.TestCase):
    def test_simple_active_capture(self):
        board = ashton.Board()

        board.step(Player.BLACK, (3, 0), (3, 2))
        board.step(Player.BLACK, (5, 0), (5, 2))
        self.assertTrue(board.board[4][2] == 0)

    def test_simple_non_active_capture(self):
        board = ashton.Board()

        board.step(Player.BLACK, (1, 4), (1, 1))
        board.step(Player.BLACK, (4, 1), (3, 1))
        board.step(Player.WHITE, (2, 4), (2, 1))

        self.assertFalse(board.board[2][1] == 0)

    def test_multiple_capture(self):
        board = ashton.Board()

        board.step(Player.BLACK, (5, 0), (5, 2))
        board.step(Player.WHITE, (2, 4), (2, 2))
        board.step(Player.BLACK, (1, 4), (1, 2))
        board.step(Player.BLACK, (3, 0), (3, 2))

        self.assertTrue(board.board[4][2] == 0)
        self.assertTrue(board.board[2][2] == 0)

    def test_passive_capture_consistency(self):
        # In this test we force a passive capture situation and then
        # do an active capture which could potentially be multiple, it shouldnt tho
        board = ashton.Board()

        # passive capture
        board.step(Player.WHITE, (6, 4), (6, 2))
        board.step(Player.BLACK, (5, 0), (5, 2))
        self.assertFalse(board.board[5][2] == 0)

        # active capture
        board.step(Player.BLACK, (3, 0), (3, 2))
        self.assertTrue(board.board[4][2] == 0)

    def test_king_in_castle_capture(self):
        board = ashton.Board()
        board.board[4][2] = board.board[4][2] - int(board.board[4][2])
        board.board[4][3] = board.board[4][3] - int(board.board[4][3])
        board.board[4][5] = board.board[4][5] - int(board.board[4][5])
        board.board[4][6] = board.board[4][6] - int(board.board[4][6])
        board.board[2][4] = board.board[2][4] - int(board.board[2][4])
        board.board[3][4] = board.board[3][4] - int(board.board[3][4])
        board.board[5][4] = board.board[5][4] - int(board.board[5][4])
        board.board[6][4] = board.board[6][4] - int(board.board[6][4])

        with self.assertRaises(LoseException):
            board.step(Player.BLACK, (4, 1), (4, 3))
            board.step(Player.BLACK, (4, 7), (4, 5))
            self.assertTrue(board.board[4][4] == 1.7)
            board.step(Player.BLACK, (1, 4), (3, 4))
            board.step(Player.BLACK, (7, 4), (5, 4))

    def test_king_adjacent_castle_capture(self):
        board = ashton.Board()
        board.board[4][2] = board.board[4][2] - int(board.board[4][2])
        board.board[4][3] = board.board[4][3] - int(board.board[4][3])
        board.board[4][5] = board.board[4][5] - int(board.board[4][5])
        board.board[4][6] = board.board[4][6] - int(board.board[4][6])
        board.board[2][4] = board.board[2][4] - int(board.board[2][4])
        board.board[3][4] = board.board[3][4] - int(board.board[3][4])
        board.board[5][4] = board.board[5][4] - int(board.board[5][4])
        board.board[6][4] = board.board[6][4] - int(board.board[6][4])
        board.step(Player.WHITE, (4, 4), (3, 4))
        with self.assertRaises(LoseException):
            board.step(Player.BLACK, (1, 4), (2, 4))
            board.step(Player.BLACK, (3, 0), (3, 3))
            board.step(Player.BLACK, (3, 8), (3, 5))

    def test_king_simple_capture(self):
        board = ashton.Board()
        board.board[4][2] = board.board[4][2] - int(board.board[4][2])
        board.board[4][3] = board.board[4][3] - int(board.board[4][3])
        board.board[4][5] = board.board[4][5] - int(board.board[4][5])
        board.board[4][6] = board.board[4][6] - int(board.board[4][6])
        board.board[2][4] = board.board[2][4] - int(board.board[2][4])
        board.board[3][4] = board.board[3][4] - int(board.board[3][4])
        board.board[5][4] = board.board[5][4] - int(board.board[5][4])
        board.board[6][4] = board.board[6][4] - int(board.board[6][4])

        board.step(Player.WHITE, (4, 4), (2, 4))
        with self.assertRaises(LoseException):
            board.step(Player.BLACK, (0, 3), (2, 3))
            board.step(Player.BLACK, (0, 5), (2, 5))

    def test_camp_side_simple_capture(self):
        board = ashton.Board()

        board.board[3][0] = board.board[3][0] - int(board.board[3][0])

        board.step(Player.BLACK, (4, 1), (3, 1))
        board.step(Player.WHITE, (4, 2), (3, 2))
        self.assertTrue(board.board[3][1] == 0)

    def test_castle_side_with_king_capture(self):
        board = ashton.Board()

        board.board[4][2] = board.board[4][2] - int(board.board[4][2])

        board.step(Player.BLACK, (4, 1), (4, 2))
        self.assertTrue(board.board[4][3] == 0)

    def test_castle_side_without_king_capture(self):
        board = ashton.Board()

        board.board[4][2] = board.board[4][2] - int(board.board[4][2])

        board.board[3][4] = board.board[3][4] - int(board.board[3][4])
        board.step(Player.WHITE, (4, 4), (3, 4))

        board.step(Player.BLACK, (4, 1), (4, 2))
        self.assertTrue(board.board[4][3] == 0)


class AshtonEndConditionTest(unittest.TestCase):
    def test_white_win(self):
        board = ashton.Board()
        board.board[3][4] = board.board[3][4] - int(board.board[3][4])
        board.board[2][4] = board.board[2][4] - int(board.board[2][4])

        board.step(Player.WHITE, (4, 4), (2, 4))

        with self.assertRaises(WinException):
            board.step(Player.WHITE, (2, 4), (2, 8))

    def test_black_win(self):
        board = ashton.Board()
        board.board[4][2] = board.board[4][2] - int(board.board[4][2])
        board.board[4][3] = board.board[4][3] - int(board.board[4][3])
        board.board[4][5] = board.board[4][5] - int(board.board[4][5])
        board.board[4][6] = board.board[4][6] - int(board.board[4][6])
        board.board[2][4] = board.board[2][4] - int(board.board[2][4])
        board.board[3][4] = board.board[3][4] - int(board.board[3][4])
        board.board[5][4] = board.board[5][4] - int(board.board[5][4])
        board.board[6][4] = board.board[6][4] - int(board.board[6][4])

        board.step(Player.BLACK, (4, 1), (4, 3))
        board.step(Player.BLACK, (4, 7), (4, 5))
        board.step(Player.BLACK, (1, 4), (3, 4))
        with self.assertRaises(LoseException):
            board.step(Player.BLACK, (7, 4), (5, 4))


class AshtonUtils(unittest.TestCase):
    def test_infer_move(self):
        board1 = ashton.Board()
        board1.step(Player.WHITE, (2, 4), (2, 3))
        
        board2 = ashton.Board()
        
        start, end = board2.infer_move(board1.board)
        self.assertEqual(start, (2, 4))
        self.assertEqual(end, (2, 3))

if __name__ == '__main__':
    unittest.main()
