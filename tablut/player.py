from tablut.game import Player
from tablut.board import WinException, LoseException, DrawException
import threading
from time import sleep
from random import randint


class RandomPlayer(object):
    """
    Really naive implementation of a random playey
    """

    def __init__(self, game, player):
        self.game = game
        self.player = player

    def _random_move(self):
        start = (randint(0, 8), randint(0, 8))
        end = (randint(0, 8), randint(0, 8))
        return start, end

    def play(self):
        # Find a random move
        start, end = self._random_move()
        legal, _ = self.game.board.is_legal(self.player, start, end)
        while not legal:
            start, end = self._random_move()
            legal, _ = self.game.board.is_legal(self.player, start, end)

        try:
            if self.player is Player.WHITE:
                self.game.white_move(start, end)
            elif self.player is Player.BLACK:
                self.game.black_move(start, end)
        except (ValueError, WinException, LoseException, DrawException):
            # illegal move... shouldnt happen
            pass
