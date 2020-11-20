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


class BaseTile(object):
    """
    Tile of the board
    """
    piece = None

    def occupied(self):
        """
        Check if tile is occupied
        """
        return self.piece is not None


    def _check_if_can_place(self, piece):
        """
        Raise proper exception if piece cannot be placed
        """
        if self.piece is not None:
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
        already_empty = self.piece is None
        self.piece = None
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


class BaseEscape(BaseTile):
    """
    Escape tile
    """
    def _check_if_can_place(self, piece):
        """
        Only king can be placed in escape
        """
        super()._check_if_can_place(piece)
        if not issubclass(piece, King):
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


class BaseBoard(object):
    """
    Base board implementation
    """
    TILE_PIECE_MAP = {
        "te": (BaseTile, None),
        "TW": (BaseTile, BaseWhiteSoldier),
        "TB": (BaseTile, BaseBlackSoldier),
        "TK": (BaseTile, BaseKing),
        "ce": (BaseCamp, None),
        "CB": (BaseCamp, BaseBlackSoldier),
        "ee": (BaseEscape, None),
        "EK": (BaseEscape, BaseKing),
        "ce": (BaseCastle, None),
        "CK": (BaseCastle, BaseKing)
    }
    BOARD_TEMPLATE = None

    def __init__(self):
        self.board_history = list()
        self.board = self.unpack(self.BOARD_TEMPLATE)
        # Save initial state to board history 
        # (needed as a winning condition is when the same board status appears twice)
        self.board_history.append(self.pack(self.board))

    def pack(self, board):
        """
        Returns the grid with the str rappresentation stated in TILE_PIECE_MAP
        instead of a matrix of objects
        """
        grid = self.BOARD_TEMPLATE

        for row in grid:
            for column in grid:
                tile = grid[row][column]
                # FIXME: really sorry for this :'(((
                for k, v in self.TILE_PIECE_MAP.items():
                    if issubclass(tile, v[0]) and \
                       ((tile.piece is None and v is None) or issubclass(tile.piece, v)):
                       grid[row][column] = k
                       break

        return grid

    def unpack(self, template):
        """
        Builds the board using the board template
        """
        grid = self.BOARD_TEMPLATE

        for row in grid:
            for column in row:
                tile, piece = self.TILE_PIECE_MAP[template[row][column]]
                grid[row][column] = tile()
                if piece is not None:
                    grid[row][column].place(piece())
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
            piece = start.piece
            self.board[start[0]][start[1]].empty()
            self.board[end[0]][end[1]].place(piece)
    
            # remove captured pieces
            self.apply_captures(end)
            
            # store move in board history
            self.board_history.append(self.pack(self.board))

        else:
            raise ValueError(message)

        # check for winning condition
        if self.winning_condition():
            raise WinException
        else:
            raise LoseException

    def apply_captures(self, changed_positions):
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