from enum import Enum


class Player(Enum):
    WHITE = "W"
    BLACK = "B"


class TurnException(Exception):
    pass


class Game(object):
    """
    Create a tablut board and lets the user play
    """

    def __init__(self, board):
        self.board = board
        self.turn = Player.WHITE

    def white_move(self, start, end):
        """
        Make the white move
        """
        if self.turn == Player.WHITE:
            try:
                self.board.step(Player.WHITE, start, end)
                self.turn = Player.BLACK
            except Exception as e:
                raise ValueError("White move illegal: %s" % str(e))
        else:
            raise TurnException("Its black player turn")

    def black_move(self, start, end):
        """
        Make the black move
        """
        if self.turn == Player.BLACK:
            try:
                self.board.step(Player.BLACK, start, end)
                self.turn = Player.WHITE
            except Exception as e:
                raise ValueError("Black move illegal:%s " % str(e))
        else:
            raise TurnException("Its white player turn")