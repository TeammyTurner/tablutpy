from enum import Enum

class Turn(Enum):
    WHITE = "W"
    BLACK = "B"

class TurnException(Exception):
    pass

class Game(object):
    """
    Create a tablut board and lets the user play
    """
    def __init__(self, board):
        self.board = board()
        self.turn = Turn.WHITE 
    
    def white_move(self, start, end):
        """
        Make the white move
        """
        if self.turn == Turn.WHITE:
            try:
                self.step(start, end)
                self.turn = Turn.BLACK
            except Exception as e:
                raise ValueError("White move illegal: " % str(e))
        else:
            raise TurnException("Its black player turn")

    def black_move(self, start, end):
        """
        Make the black move
        """
        if self.turn == Turn.BLACK:
            try:
                self.step(start, end)
                self.turn = Turn.WHITE
            except Exception as e:
                raise ValueError("Black move illegal: " % str(e))
        else:
            raise TurnException("Its white player turn")

