from math import abs
import board

class BlackSoldier(board.BaseBlackSoldier):
    """
    Black soldier implementation - attacker
    """
    out_of_camp = False
    initial_camp = None

    def __init__(self, initial_camp):
        super().__init__()
        self.initial_camp = initial_camp


    def went_out_of_camp(self):
        """
        Black soldier went out of original camp and cannot go back in another campo
        """
        self.out_of_camp = True


class WhiteSoldier(board.BaseWhiteSoldier):
    """
    White soldier implementation - defender
    """
    pass


class King(board.BaseKing):
    """
    King implementation
    """
    pass


class Castle(board.BaseCastle):
    """
    Castle tile
    """
    def _check_if_can_place(self, piece):
        """
        Castle cannot be occupied by anyone
        """
        raise ValueError("Castle cannot be occupied anymore")


class Camp(board.BaseCamp):
    """
    Camp tile
    """
    def _check_if_can_place(self, piece):
        """
        Only black soldiers can move inside a camp altough only if its their original camp.
        """
        super()._check_if_can_place(piece)
        if not isinstance(piece, BlackSoldier):
            raise ValueError("Can't occupy castle")
        else:
            if piece.initial_camp is not self:
                raise ValueError("Attacker can only move inside his own starting camp")


class Escape(board.BaseEscape):
    """
    Escape tile
    """
    def _check_if_can_place(self, piece):
        """
        Only king can be placed in escape
        """
        super()._check_if_can_place(piece)
        if not isinstance(piece, King):
            raise ValueError("Only king can occupy escape")


class Board(object):
    """
    Tablut board is a grid of 9x9 squares
    Depending on the rules the function of each square changes
    """
    TILE_PIECE_MAP = {
        "te": (board.BaseTile, None),
        "TW": (board.BaseTile, WhiteSoldier),
        "TB": (board.BaseTile, BlackSoldier),
        "TK": (board.BaseTile, King),
        "ce": (Camp, None),
        "CB": (Camp, BlackSoldier),
        "ee": (Escape, None),
        "EK": (Escape, King),
        "ce": (Castle, None),
        "CK": (Castle, King)
    }
    BOARD_TEMPLATE = [
        ["te", "ee", "ee", "CB", "CB", "CB", "ee", "ee", "te"],
        ["ee", "te", "te", "te", "CB", "te", "te", "te", "ee"],
        ["ee", "te", "te", "te", "TW", "te", "te", "te", "ee"],
        ["CB", "te", "te", "te", "TW", "te", "te", "te", "CB"],
        ["CB", "CB", "TW", "TW", "CK", "TW", "TW", "CB", "CB"],
        ["CB", "te", "te", "te", "TW", "te", "te", "te", "CB"],
        ["ee", "te", "te", "te", "TW", "te", "te", "te", "ee"],
        ["ee", "te", "te", "te", "CB", "te", "te", "te", "ee"],
        ["te", "ee", "ee", "CB", "CB", "CB", "ee", "ee", "te"]
    ]

    def is_legal(self, start, end):
        """
        Check if move is legal according to ashton rules
        """
        st = self.board[start[0]][start[1]]
        et = self.board[end[0]][end[1]]

        # start and end cannot be the same
        if start[0] == end[0] and start[1] == end[1]:
            return False, "End needs to be different than start"

        # Move need to be orthogonal
        if start[0] == end[0]:
            mov_direction = 1
        elif start[1] == end[1]:
            mov_direction = 0
        else:
            return False, "Moves need to be orthogonal"

        # End tile cannot be the castle
        if isinstance(et, Castle):
            return False, "Cannot end in the castle"

        # End tile cannot be a camp unless a black soldier is moving inside its starting camp
        # and never left it
        if isinstance(et, Camp) and \
            ((isinstance(st, Camp) and isinstance(et, Camp) and st.piece.initial_camp == et) is False):
            return False, "Cannot end in the castle"

        # Escape tile can be reached only by the king
        if isinstance(et, Escape) and isinstance(st.piece, King) is False:
            return False, "Only king can go in escape"

        # Check for obastacles in movement
        delta = abs(end[mov_direction] - start[mov_direction]) - 1 # final cell already considered
        sign = -1 if start[0] > end[0] else 1
        for i in range(1, delta + 1):
            if mov_direction == 0:
                t = self.board[start[0] + (sign * i)][end[1]]
            else:
                t = self.board[end[0]][start[1] + (sign * i)]

            # check that tile is not an obstacle (occupied, castle or camp)
            if t.occupied() or isinstance(t, Castle) or isinstance(t, Camp):
                return False, f"Cannot pass over obstacle: {et}"

    def apply_captures(self, changed_positions):
        raise NotImplementedError

    def winning_condition(self):
        raise NotImplementedError

    def lose_condition(self):
        raise NotImplementedError
    