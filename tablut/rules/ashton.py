from math import abs
import board

class Tile(board.BaseTile):
    pass


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


# TODO: How do we implement when a user is stuck?
class Board(board.BaseBoard):
    """
    Tablut board is a grid of 9x9 squares
    Depending on the rules the function of each square changes
    """
    TILE_PIECE_MAP = {
        "te": (Tile, None),
        "TW": (Tile, WhiteSoldier),
        "TB": (Tile, BlackSoldier),
        "TK": (Tile, King),
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

    def apply_captures(self, changed_position):
        """
        Apply orthogonal captures for soldiers and 
        """
        changed_tile = self.board[changed_position[0]][changed_position[1]]
        piece_class = [type(changed_tile.piece)]
        enemy_class = [BlackSoldier] if piece_class == WhiteSoldier else [WhiteSoldier, King]

        self._orthogonal_capture(changed_position, enemy_class, piece_class)
        self._king_in_castle_capture()
        self._king_adjacent_castle_capture()

    def _king_in_castle_capture(self):
        """
        If king is still in castle its captured only when its surrounded
        """
        castle = self.board[4][4]
        if castle.occupied() and \
            self._has_neighbour((4, 4), BlackSoldier, "up") and
            self._has_neighbour((4, 4), BlackSoldier, "right") and
            self._has_neighbour((4, 4), BlackSoldier, "down") and
            self._has_neighbour((4, 4), BlackSoldier, "left"):
            self.board[4][4].empty() 

    def _king_adjacent_castle_capture(self):
        """
        When king is adjacent to castle its captured only if its surrounded in all the other sides
        """
        directions = ["up", "right", "down", "left"]
        
        # check if king is in castle neighborhood
        king_around_castle = directions.map(lambda d: self._has_neighbour((4, 4), [King], d), directions)
        if True in king_around_castle:
            king_direction = directions[king_around_castle.index(True)]
            king_position = self._neighbour_position((4, 4), king_direction)

            # Already know that king is adjacent to castle, just check that is adjacent to 3 black soldiers
            neighbours = directions.map(
                lambda d: self._has_neighbour(king_position, [BlackSoldier], d), directions)
            
            if neighbours.count(True) == 3:
                # King surrounded by soldiers and castle, remove it
                self.board[king_position[0]][king_position[1]].empty()

    def _orthogonal_capture(self, changed_position, enemy_class, piece_class):
        """
        A soldier is captured if its surrounded by two other soldiers, note that the capture needs to be
        active: if a soldier places himself between two enemies its not captured.
        We just need to check the piece orthogonal neighborhood: if an enemy is present then we need to
        wether in the same axis there is another soldier and just in that case capture.

        e.g. (S is newly moved soldier, s is for soldier, e for enemy)
        
        ... | S | e | s | ...
        => enemy is captured as there was already a soldier on his side on same the same axis  

        ... | s | S | e | ...
        => enemy isnt captured as there isnt a soldier on his side on same the same axis  

        ... | s | E | s | ...
        => enemy isnt captured as the capture is not active.

        The castle acts as an enemy.
        e.g. (S is newly moved soldier, c for castle, e for enemy)
        ... | c | e | S | ...
        => enemy is captured  
        """
        # Check in all directions
        directions = ["up", "right", "down", "left"]
        for d in directions:
            # Check that adjacent to current tile has an enemy in direction d
            if self._has_neighbour(changed_position, enemy_class, d):
                neighbour_pos = self._neighbour_position(changed_position, d)
                
                # TODO: Break into smaller chunks? Or build a bigger boolean clause?
                # If neighbour is king and is adjacent to castle skip control
                if (isinstance(self.board[neighbour_pos[0]][neighbour_pos[1]], King) and
                    self._adjacent_to(neighbour_pos, [Castle])) is False:
                    # Check that enemy is surrounded on the other side (castle is an enemy)
                    if self._has_neighbour(neighbour_pos, piece_class, d) or \
                    self._has_neighbour(neighbour_pos, [Castle], d) :
                        # element in neighbour_pos has been captured
                        self.board[neighbour_pos[0]][neighbour_pos[1]].empty()

    def _adjacent_to(self, position, cell, is_piece=False):
        """
        Check if tile in position is adjacent to a particular tile is is_piece is False or
        adjacent to a particular checker if is_piece is True.

        cell is a list.
        """
        return self._has_neighbour(position, cell, "right", check_piece=is_piece) or \
            self._has_neighbour(position, cell, "down", check_piece=is_piece) or \
            self._has_neighbour(position, cell, "left", check_piece=is_piece) or \
            self._has_neighbour(position, cell, "up", check_piece=is_piece)
            
    def _has_neighbour(self, position, enemy, direction, check_piece=True):
        """
        Returns if tile in specified position has a specified neighbour in the specified direction.
        Axis can be 'left', 'right', 'up', 'down'.

        if check piece is True the enemy is searched inside the neighbour tile, 
        if false the neighbour tile type (e.g. Castle) is considered as enemy
        """ 
        try:
            position = self._neighbour_position(position, direction)
            neighbour = self.board[position[0]][position[1]]

            if check_piece:
                return neighbour.piece is not None and type(neighbour) in enemy
            else:
                return type(neighbour) in enemy
        except ValueError:
            return False
        
    def _neighbour_position(self, position, direction):
        """
        Return the neighbour coords in the specified position
        """
        pos = position
        if direction.lower() == "left":
            pos[1] -= 1
        elif direction.lower() == "right"
            pos[1] += 1
        elif direction.lower() == "up"
            pos[0] -= 1
        elif direction.lower() == "down"
            pos[0] += 1

        # check that new position is in the board bound
        if pos[0] > len(self.board) or pos[1] > len(self.board[0]):
            raise ValueError("position out of board bound")
        else:
            return pos

    def winning_condition(self):
        """
        Check if escape tiles are occupied by a king
        """
        escape_tiles_pos = ((1, 1), (1, 2), (1, 6), (1, 7), (2, 0), (2, 8), (3, 0), (3, 8),
            (8, 1), (8, 2), (8, 6), (8, 7), (7, 0), (7, 8), (6, 0), (6, 8))

        # Escapes can be occupied only by king
        for pos in escape_tiles_pos:
            if self.board[pos[0]][pos[1]].occupied():
                return True

    def lose_condition(self):
        """
        Check in all board if king is present
        FIXME: Too ineficient?
        """
        for row in self.board:
            for column in row:
                if self.board[row][column].occupied() and isinstance(self.board[row][column].piece, King):
                    return False
        return True 
        
    def draw_condition(self):
        """
        Twice the same state
        """
        packed = self.pack(self.board)
        if packed in self.board_history:
            return True
    