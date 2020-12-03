import tablut.board as board
from tablut.game import Player
import numpy as np


class Board(board.BaseBoard):
    """
    Tablut board is a grid of 9x9 squares
    Depending on the rules the function of each square changes
    """

    def __init__(self):
        super().__init__()

    @property
    def TILE_PIECE_MAP(self):
        return {
            "te": 0,
            "TW": 2,
            "TB": -2,
            "TK": 1,
            "ce": -0.5,
            "CB": -2.5,
            "Se": 0.7,
            "SK": 1.7
        }

    @property
    # We know we could inverse the other one, but we're tryna be fast, man!
    def INVERSE_TILE_PIECE_MAP(self):
        return {
            0: "te",
            2: "TW",
            -2: "TB",
            1: "TK",
            -0.5: "ce",
            -2.5: "CB",
            0.7: "Se",
            1.7: "SK"
        }

    @property
    def BOARD_TEMPLATE(self):
        return [
            ["te", "te", "te", "CB", "CB", "CB", "te", "te", "te"],
            ["te", "te", "te", "te", "CB", "te", "te", "te", "te"],
            ["te", "te", "te", "te", "TW", "te", "te", "te", "te"],
            ["CB", "te", "te", "te", "TW", "te", "te", "te", "CB"],
            ["CB", "CB", "TW", "TW", "SK", "TW", "TW", "CB", "CB"],
            ["CB", "te", "te", "te", "TW", "te", "te", "te", "CB"],
            ["te", "te", "te", "te", "TW", "te", "te", "te", "te"],
            ["te", "te", "te", "te", "CB", "te", "te", "te", "te"],
            ["te", "te", "te", "CB", "CB", "CB", "te", "te", "te"]
        ]

    def infer_move(self, new_board):
        # get the different tiles from my board configuration
        changed_idxs = np.where(np.abs(new_board - self.board) != 0)
        changed_idxs = list(zip(changed_idxs[0], changed_idxs[1]))

        if self.board[changed_idxs[0]] in [-0.5, 0.0, 0.7]:
            # 0th index is a tile where a piece can be plced so must be the end coord
            end = changed_idxs[0]
            start = changed_idxs[1]
        else:
            # 0th index must be the start
            start = changed_idxs[0]
            end = changed_idxs[1]

        return start, end

    def is_legal(self, player, start, end):
        """
        Check if move is legal according to ashton rules
        """
        st = self.board[start[0]][start[1]]
        et = self.board[end[0]][end[1]]

        # cant land on corners
        # if end in [(0, 0), (0, 8), (8, 0), (8, 8)]:
        #    return False, "Cant end on tile corners"

        # start tile cant be empty
        if -1 < st < 1:
            return False, "Start tile is empty"

        # start tile must contain my pieces
        if (player is Player.BLACK and st > 0 or
                (player is Player.WHITE and st < 0)):
            return False, "Cant move other player pieces"

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
        if not -1 < et < 1:
            return False, "Cannot go into already occupied tile"

        # End tile cannot be the castle
        if et == 0.7:
            return False, "Cannot end in the castle"

        # End tile cannot be a camp unless a black soldier is moving inside its starting camp
        # and never left it
        if et == -0.5 and not (st - int(st)) == -0.5:
            return False, "Cannot end in camp"

        # Escape tile can be reached only by the king
        # if et == 0.3 and not int(st) == 1:
        #    return False, "Only king can go in escape"

        # Check for obastacles in movement.
        # final cell already considered
        delta = end[mov_direction] - start[mov_direction]
        if abs(delta)-1 > 0:
            sum = 0
            i = start[mov_direction]
            while i != end[mov_direction]:
                # This is firstly needed to skip the first cell (containing our piece), then to loop
                if delta < 0:
                    i = i-1
                else:
                    i = i+1
                if mov_direction == 0:
                    sum = sum + abs(self.board[i][start[1]])
                else:
                    sum = sum + abs(self.board[start[0]][i])
            if not sum == 0:
                return False, "Cannot pass over obstacle: %s" % sum

        return True, ""

    def apply_captures(self, changed_position):
        """
        Apply orthogonal captures for soldiers and
        """
        changed_tile = self.board[changed_position[0]][changed_position[1]]
        enemy_class = [-2] if changed_tile > 0 else [
            1, 2]

        captures = self._orthogonal_capture(
            changed_position, enemy_class)
        king_captured = self._king_in_castle_capture()
        king_captured = self._king_adjacent_castle_capture()

        if king_captured:
            captures = -1

        return captures

    def _king_in_castle_capture(self):
        """
        If king is still in castle its captured only when its surrounded
        """
        castle = self.board[4][4]
        if castle == 1.7 and \
                self.get_neighbourhood_sum((4, 4)) == -8:
            self.board[4][4] = 0.7
            return True

        return False

    def _king_adjacent_castle_capture(self):
        """
        When king is adjacent to castle its captured only if its surrounded in all the other sides
        """
        king_i, king_j = np.where(self.board == 1)
        if len(king_i) > 0:  # Numpy returns an array instead of the single value, so we have to get its one and only element
            king_i = king_i[0]
            king_j = king_j[0]

            # check if king is in castle neighborhood
            # If the module is 1, it means that there's a king
            if self.get_neighbourhood_sum(
                    (king_i, king_j)) == -5.3:
                self.board[king_i][king_j] = self.board[king_i][king_j] - \
                    int(self.board[king_i][king_j])
                return True

        return False

    def get_neighbourhood_sum(self, position):
        """
        Method that returns the + (up, down, right, left) neighbourhood sum of a position
        """
        directions = ["up", "right", "down", "left"]
        sum = 0
        for d in directions:
            try:
                neighbour_pos = self._neighbour_position(position, d)
                sum += self.board[neighbour_pos[0]][neighbour_pos[1]]
            except (ValueError, IndexError):
                pass  # If the position doesn't exist, let's skip it!
        return sum

    def _orthogonal_capture(self, changed_position, enemy_class):
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
        FIXME: I don't really like this, there has to be a better way using sums
        """
        captured = 0

        # Check in all directions
        directions = ["up", "right", "down", "left"]
        for d in directions:
            # Check that adjacent to current tile has an enemy in direction d
            if self._has_neighbour(changed_position, enemy_class, d):
                neighbour_pos = self._neighbour_position(changed_position, d)
                neighbour = self.board[neighbour_pos[0]][neighbour_pos[1]]

                neighbour_is_king = int(neighbour) == 1
                king_in_castle = neighbour == 1.7
                king_adjacent_to_castle = self.get_neighbourhood_sum(
                    neighbour_pos) % 1 == 0.7
                if (neighbour_is_king and not (king_in_castle or king_adjacent_to_castle)) or not neighbour_is_king:
                    # Check that enemy is surrounded on the other side
                    # castle and camp are counted as enemies
                    try:
                        other_side_pos = self._neighbour_position(
                            neighbour_pos, d)
                        other_side = self.board[other_side_pos[0]
                                                ][other_side_pos[1]]
                        if (other_side*neighbour < 0) or other_side % 1 == 0.7 or (other_side - int(other_side)) == -0.5:
                            # element in neighbour_pos has been captured
                            self.board[neighbour_pos[0]][neighbour_pos[1]
                                                         ] = self.board[neighbour_pos[0]][neighbour_pos[1]] - int(self.board[neighbour_pos[0]][neighbour_pos[1]])
                            captured += 1
                    except ValueError:
                        pass
        return captured

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
            neighbour_position = self._neighbour_position(position, direction)
            neighbour = self.board[neighbour_position[0]
                                   ][neighbour_position[1]]

            if check_piece:
                # If they're from different "teams", the product has to be <0
                return (self.board[position[0]][position[1]]*neighbour) < 0
            else:
                return neighbour in enemy
        except (ValueError, IndexError):
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
        if pos[0] > len(self.board)-1 or pos[1] > len(self.board[0])-1:
            raise ValueError("position out of board bound")
        else:
            return pos

    def winning_condition(self):
        """
        Check if escape tiles are occupied by a king
        TODO: Make this check the single tiles since now escapes are just normal tiles
        """
        escape_tiles = [(0, 1), (0, 2), (0, 6), (0, 7),
                        (1, 0), (1, 8),
                        (2, 0), (2, 8),
                        (6, 0), (6, 8),
                        (7, 0), (7, 8),
                        (8, 1), (8, 2), (8, 6), (8, 7)]
        winning = False
        for tile in escape_tiles:
            winning = self.board[tile[0]][tile[1]] == 1 or winning
        return winning

    def lose_condition(self):
        """
        Check in all board if king is present
        """
        king_present = len(
            np.where(self.board.flatten().astype(int) == 1)[0]) > 0
        return not king_present

    def draw_condition(self):
        """
        Twice the same state
        """
        packed = self.pack(self.board)
        if packed in self.board_history[:-1]:
            return True
        else:
            return False
