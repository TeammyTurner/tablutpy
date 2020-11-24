import copy


class BasePiece(object):
    """
    Base piece implementation
    """
    pass


class BaseSoldier(BasePiece):
    """
    BaseSoldier piece
    """
    pass


class BaseBlackSoldier(BaseSoldier):
    """
    Black soldier implementation - attacker
    """
    pass


class BaseWhiteSoldier(BaseSoldier):
    """
    White soldier implementation - defender
    """
    pass


class BaseKing(BaseSoldier):
    """
    King implementation
    """
    pass


class EmptyTile(object):
    pass


class BaseTile(object):
    """
    Tile of the board
    """
    piece = EmptyTile()

    def occupied(self):
        """
        Check if tile is occupied
        """
        return not isinstance(self.piece, EmptyTile)

    def _check_if_can_place(self, piece):
        """
        Raise proper exception if piece cannot be placed
        """
        if not isinstance(self.piece, EmptyTile):
            raise ValueError("Tile already occupied")

    def place(self, piece):
        """
        Place a piece if can be placed
        """
        try:
            self._check_if_can_place(piece)
            self.piece = piece
        except Exception:
            raise

    def empty(self):
        """
        Remove a piece if can be removed. 
        Return True if a piece was removed, False if was already empty
        """
        already_empty = isinstance(self.piece, EmptyTile)
        self.piece = EmptyTile()
        return already_empty


class BaseCastle(BaseTile):
    """
    Castle tile
    """
    pass


class BaseCamp(BaseTile):
    """
    Camp tile
    """
    pass


class BaseCampSet(list):
    """
    Camps are related by being in one camp set
    """
    pass


class BaseEscape(BaseTile):
    """
    Escape tile
    """

    def _check_if_can_place(self, piece):
        """
        Only king can be placed in escape
        """
        super()._check_if_can_place(piece)
        if piece is not BaseKing:
            raise ValueError("Only king can occupy escape")


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
    BOARD_TEMPLATE = None

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
    def BOARD_TEMPLATE(self):
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
                # FIXME: really sorry for this :'(((
                for k, v in self.TILE_PIECE_MAP.items():
                    # check if the tile correspond to this symbol
                    if isinstance(tile, v[0]) and isinstance(tile.piece, v[1]):
                        grid[row_i][col_i] = k
                        break
        return grid

    def unpack(self, template):
        """
        Builds the board using the board template
        """
        grid = copy.copy(self.BOARD_TEMPLATE)

        for row_i, row in enumerate(grid):
            for col_i, column in enumerate(row):
                tile, piece = self.TILE_PIECE_MAP[template[row_i][col_i]]
                grid[row_i][col_i] = tile()
                if piece is not None:
                    grid[row_i][col_i].piece = piece()
        return grid

    def is_legal(self, start, end):
        """
        Return if move from start to end is legal
        """
        raise NotImplementedError

    def step(self, start, end):
        """
        Perform a move and update the board status if a move is legal
        """
        previous_board = self.board

        legal_move, message = self.is_legal(start, end)
        if legal_move:
            # perform move
            piece = self.board[start[0]][start[1]].piece
            self.board[start[0]][start[1]].empty()
            self.board[end[0]][end[1]].place(piece)

            # remove captured pieces
            reward = self.apply_captures(end)
            done = False
            obs = None  # TODO: make this something real
            # check for winning condition
            if self.winning_condition():
                reward = reward+20
                done = True
                #raise WinException
            elif self.lose_condition():
                reward = reward-20
                done = True
                #raise LoseException
            elif self.draw_condition():
                reward = reward-1
                done = True
                #raise DrawException

            # store move in board history
            self.board_history.append(self.pack(self.board))
            return obs, reward, done
        else:
            raise ValueError(message)

    def apply_captures(self, changed_position):
        """
        Apply captures on the board based on the changed position
        Depending on the game rules the neighborhood could be large or small 
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
