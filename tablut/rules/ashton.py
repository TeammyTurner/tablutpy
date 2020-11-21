import copy
import tablut.board as board

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
            # TODO: handle piece not belonging to this camp set
            pass
            

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

    def __init__(self):
        # create camp sets
        # 0 -> upper camp set
        # 1 -> right camp set
        # 2 -> lower camp set
        # 3 -> left camp set
        self.camp_sets = [
            board.BaseCampSet(),
            board.BaseCampSet(),
            board.BaseCampSet(),
            board.BaseCampSet()
        ]
        super().__init__()

    @property
    def TILE_PIECE_MAP(self):
        return {
            "te": (Tile, board.EmptyTile),
            "TW": (Tile, WhiteSoldier),
            "TB": (Tile, BlackSoldier),
            "TK": (Tile, King),
            "ce": (Camp, board.EmptyTile),
            "CB": (Camp, BlackSoldier),
            "ee": (Escape, board.EmptyTile),
            "EK": (Escape, King),
            "Se": (Castle, board.EmptyTile),
            "SK": (Castle, King)
        }

    @property
    def BOARD_TEMPLATE(self):
        return [
            ["te", "ee", "ee", "CB", "CB", "CB", "ee", "ee", "te"],
            ["ee", "te", "te", "te", "CB", "te", "te", "te", "ee"],
            ["ee", "te", "te", "te", "TW", "te", "te", "te", "ee"],
            ["CB", "te", "te", "te", "TW", "te", "te", "te", "CB"],
            ["CB", "CB", "TW", "TW", "SK", "TW", "TW", "CB", "CB"],
            ["CB", "te", "te", "te", "TW", "te", "te", "te", "CB"],
            ["ee", "te", "te", "te", "TW", "te", "te", "te", "ee"],
            ["ee", "te", "te", "te", "CB", "te", "te", "te", "ee"],
            ["te", "ee", "ee", "CB", "CB", "CB", "ee", "ee", "te"]
        ]

    def unpack(self, template):
        """
        Builds the board using the board template
        """
        grid = copy.copy(self.BOARD_TEMPLATE)

        for row_i, row in enumerate(grid):
            for col_i, column in enumerate(row):
                tile, piece = self.TILE_PIECE_MAP[template[row_i][col_i]]
                grid[row_i][col_i] = tile()
                
                if tile is Camp:
                    # Add the camp to the belonging camp set
                    if row_i < 2:
                        # upper camp set
                        self.camp_sets[0].append(grid[row_i][col_i])
                    elif row_i > 6:
                        # lower camp set
                        self.camp_sets[2].append(grid[row_i][col_i])
                    elif col_i < 2:
                        # lower camp set
                        self.camp_sets[3].append(grid[row_i][col_i])
                    elif col_i > 6:
                        # lower camp set
                        self.camp_sets[1].append(grid[row_i][col_i])

                if piece is BlackSoldier:
                    # create black soldier with initial camp set
                    piece = piece(tile)
                else:
                    piece = piece()
                
                grid[row_i][col_i].piece = piece

        return grid

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

        # End tile cannot be already occupied
        if not isinstance(et.piece, board.EmptyTile):
            return False, "Cannot go into already occupied tile"

        # End tile cannot be the castle
        if isinstance(et, Castle):
            return False, "Cannot end in the castle"

        # End tile cannot be a camp unless a black soldier is moving inside its starting camp
        # and never left it
        if isinstance(et, Camp):
            # Check that both camps belong to same camp set
            belonging_campset = [st in cs and et in cs for cs in self.camp_sets]
            if True not in belonging_campset:
                return False, "Cannot end in camp"

        # Escape tile can be reached only by the king
        if isinstance(et, Escape) and isinstance(st.piece, King) is False:
            return False, "Only king can go in escape"

        # Check for obastacles in movement
        delta = abs(end[mov_direction] - start[mov_direction]) - 1 # final cell already considered
        if delta > 0:
            sign = -1 if start[0] > end[0] or start[1] > end[1] else 1
            for i in range(1, delta + 1):
                if mov_direction == 0:
                    t = self.board[start[0] + (sign * i)][end[1]]
                else:
                    t = self.board[end[0]][start[1] + (sign * i)]

                # check that tile is not an obstacle (occupied, castle or camp)
                if t.occupied() or isinstance(t, Castle) or isinstance(t, Camp):
                    return False, f"Cannot pass over obstacle: {et}"
        
        return True, ""

    def apply_captures(self, changed_position):
        """
        Apply orthogonal captures for soldiers and 
        """
        changed_tile = self.board[changed_position[0]][changed_position[1]]
        piece_class = [type(changed_tile.piece)]
        enemy_class = [BlackSoldier] if piece_class[0] == WhiteSoldier else [WhiteSoldier, King]

        self._orthogonal_capture(changed_position, enemy_class, piece_class)
        self._king_in_castle_capture()
        self._king_adjacent_castle_capture()

    def _king_in_castle_capture(self):
        """
        If king is still in castle its captured only when its surrounded
        """
        castle = self.board[4][4]
        if castle.occupied() and \
            self._has_neighbour((4, 4), [BlackSoldier], "up") and \
            self._has_neighbour((4, 4), [BlackSoldier], "right") and \
            self._has_neighbour((4, 4), [BlackSoldier], "down") and \
            self._has_neighbour((4, 4), [BlackSoldier], "left"):
            self.board[4][4].empty() 

    def _king_adjacent_castle_capture(self):
        """
        When king is adjacent to castle its captured only if its surrounded in all the other sides
        """
        directions = ["up", "right", "down", "left"]
        
        # check if king is in castle neighborhood
        king_around_castle = list(map(lambda d: self._has_neighbour((4, 4), [King], d), directions))
        if True in king_around_castle:
            king_direction = directions[king_around_castle.index(True)]
            king_position = self._neighbour_position((4, 4), king_direction)

            # Already know that king is adjacent to castle, just check that is adjacent to 3 black soldiers
            neighbours = list(map(
                lambda d: self._has_neighbour(king_position, [BlackSoldier], d), directions))
            
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
                
                neighbour_is_king = isinstance(self.board[neighbour_pos[0]][neighbour_pos[1]].piece, King)
                king_in_castle = isinstance(self.board[4][4].piece, King)
                king_adjacent_to_castle = self._adjacent_to(neighbour_pos, [Castle])
                if (neighbour_is_king and (king_in_castle or king_adjacent_to_castle)) is False:
                    # Check that enemy is surrounded on the other side 
                    # castle and camp are counted as enemies
                    side_border = neighbour_pos[0] in [1, 7] or \
                        neighbour_pos[1] in [1, 7]
                    side_castle = neighbour_pos in [[4, 3], [3, 4], [4, 5], [5, 4]]

                    if self._has_neighbour(neighbour_pos, 
                        piece_class + [Castle, Camp], 
                        d,
                        check_piece=not(side_border or side_castle)):
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
                return not isinstance(neighbour.piece, board.EmptyTile) and \
                       type(neighbour.piece) in enemy
            else:
                return type(neighbour) in enemy
        except ValueError:
            return False
        
    def _neighbour_position(self, position, direction):
        """
        Return the neighbour coords in the specified position
        """
        pos = list(position)
        if direction.lower() == "left":
            pos[1] -= 1
        elif direction.lower() == "right":
            pos[1] += 1
        elif direction.lower() == "up":
            pos[0] -= 1
        elif direction.lower() == "down":
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
        escape_tiles_pos = [
            (0, 1), (0, 2), (0, 6), (0, 7), 
            (1, 0), (1, 8), (2, 0), (2, 8),
            (8, 1), (8, 2), (8, 6), (8, 7), 
            (7, 0), (7, 8), (6, 0), (6, 8)
        ]

        # Escapes can be occupied only by king
        for pos in escape_tiles_pos:
            if self.board[pos[0]][pos[1]].occupied():
                return True

    def lose_condition(self):
        """
        Check in all board if king is present
        FIXME: Too ineficient?
        """
        for row_i, row in enumerate(self.board):
            for col_i, column in enumerate(row):
                if self.board[row_i][col_i].occupied() and isinstance(self.board[row_i][col_i].piece, King):
                    return False
        return True 
        
    def draw_condition(self):
        """
        Twice the same state
        """
        packed = self.pack(self.board)
        if packed in self.board_history:
            return True
    