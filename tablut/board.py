import copy
import numpy as np


class WinException(Exception):
    """
    Exception raised when white wins: king escapes
    """
    pass


class LoseException(Exception):
    """
    Exception raised when black loses: king is captured
    """
    pass


class DrawException(Exception):
    """
    Exception raised in case of draw
    """
    pass


class BaseBoard(object):
    """
    Base board implementation
    """

    def __init__(self):
        self.board_history = list()
        self.board = self.unpack(self.BOARD_TEMPLATE)
        # Save initial state to board history
        # (needed as a winning condition is when the same board status appears twice)
        self.board_history.append(self.pack(self.board))

    @property
    def TILE_PIECE_MAP(self):
        raise NotImplementedError

    @property
    def INVERSE_TILE_PIECE_MAP(self):
        raise NotImplementedError

    @property
    def BOARD_TEMPLATE(self):
        raise NotImplementedError

    def infer_move(self, new_board):
        """
        Infer a move from a different board configuration
        """
        raise NotImplementedError

    def pack(self, board):
        """
        Returns the grid with the str rappresentation stated in TILE_PIECE_MAP
        instead of a matrix of objects
        """
        grid = copy.copy(self.BOARD_TEMPLATE)
        for row_i, row in enumerate(grid):
            for col_i, column in enumerate(grid):
                tile = board[row_i][col_i]
                grid[row_i][col_i] = self.INVERSE_TILE_PIECE_MAP[tile]
        return grid

    def unpack(self, template):  # TODO: Remove this, this doesn't actually do shit
        """
        Builds the board using the board template
        """
        grid = np.empty((9, 9))

        for row_i, row in enumerate(grid):
            for col_i, column in enumerate(row):
                tile = self.TILE_PIECE_MAP[template[row_i][col_i]]
                grid[row_i][col_i] = tile
        return grid

    def is_legal(self, player, start, end):
        """
        Return if move from start to end is legal
        """
        raise NotImplementedError

    def step(self, player, start, end, check_legal=True):
        """
        Perform a move and update the board status if a move is legal
        Returns the number of checkers captured
        """
        captures = 0
        #print("STEP {} {}".format(start, end))
        if check_legal:
            legal_move, message = self.is_legal(player, start, end)
        else:
            legal_move = True

        if legal_move:
            # perform move
            # This removes the tile: we just keep the int
            piece = int(self.board[start[0]][start[1]])
            # This removes the piece: we just keep the decimal part
            self.board[start[0]][start[1]] = self.board[start[0]
                                                        ][start[1]] - int(self.board[start[0]][start[1]])  # The modulo %1 doesn't work: Python always returns positives
            self.board[end[0]][end[1]] = self.board[end[0]][end[1]
                                                            ] + piece  # This adds the piece to the new tile

            # remove captured pieces
            captures = self.apply_captures(end)

            # check for winning condition
            if self.winning_condition():
                raise WinException
            elif self.lose_condition():
                raise LoseException
            elif self.draw_condition():
                raise DrawException
            else:
                # store move in board history
                self.board_history.append(self.pack(self.board))
                return captures
        else:
            raise ValueError(message)

    def apply_captures(self, changed_position):
        """
        Apply captures on the board based on the changed position
        Depending on the game rules the neighborhood could be large or small
        Returns the number of captured checkers, if also the king is captured returns -1
        """
        raise NotImplementedError

    def winning_condition(self):
        """
        Return true if the winning condition for white player is reached
        """
        raise NotImplementedError

    def lose_condition(self):
        """
        Return true if the lose condition for white player is reached
        """
        raise NotImplementedError

    def draw_condition(self):
        """
        Return true if the draw condition is met
        """
        raise NotImplementedError
