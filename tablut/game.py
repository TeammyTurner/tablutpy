from enum import Enum
from copy import deepcopy
from tablut.board import WinException, DrawException, LoseException

class Player(Enum):
    WHITE = "W"
    BLACK = "B"

    def next(self):
        if self is self.WHITE:
            return self.BLACK
        else:
            return self.WHITE


class TurnException(Exception):
    pass


class Game(object):
    """
    Create a tablut board and lets the user play
    """

    def __init__(self, board):
        self.board = board
        self.turn = Player.WHITE
        self.ended = False
        self.winner = None

    def white_move(self, start, end, known_legal=False):
        """
        Make the white move
        """
        if self.turn == Player.WHITE and not self.ended:
            try:
                self.board.step(Player.WHITE, start, end, check_legal=known_legal)
                self.turn = Player.BLACK
            except WinException:
                # white winned
                self.ended = True
                self.winner = Player.WHITE
            except LoseException:
                # white losed (shouldn't happen after a white move right now)
                # FIXME: Stuck player? 
                self.ended = True
                self.winner = Player.BLACK
            except DrawException:
                self.ended = True
            except Exception as e:
                raise ValueError("White move illegal: %s" % str(e))
        else:
            raise TurnException("Its black player turn")

    def black_move(self, start, end, known_legal=False):
        """
        Make the black move
        """
        if self.turn == Player.BLACK:
            try:
                self.board.step(Player.BLACK, start, end, check_legal=known_legal)
                self.turn = Player.WHITE
            except WinException:
                # white winned (shouldn't happen here...)
                # FIXME: Implement stuck player?
                self.ended = True
                self.winner = Player.WHITE
            except LoseException:
                # white losed
                self.ended = True
                self.winner = Player.BLACK
            except DrawException:
                self.ended = True
            except Exception as e:
                raise ValueError("Black move illegal:%s " % str(e))
        else:
            raise TurnException("Its white player turn")

    def what_if(self, start, end, player=None):
        """
        Return the game instance if a particular move is made but doesnt modify the actual instance. 
        The right player is automatically used if not provided
        """
        if player is None:
            player = self.turn

        cpy = deepcopy(self)
        if cpy.turn is Player.WHITE:
            cpy.white_move(start, end)
        else:
            cpy.black_move(start, end)

        return cpy        
