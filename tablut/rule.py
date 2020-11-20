import board

TILE_PIECE_MAP = {
    "te": (board.Tile, None),
    "TW": (board.Tile, board.WhiteSoldier),
    "TB": (board.Tile, board.BlackSoldier),
    "TK": (board.Tile, board.King),
    "ce": (board.Camp, None),
    "CB": (board.Camp, board.BlackSoldier),
    "ee": (board.Escape, None),
    "EK": (board.Escape, board.King),
    "ce": (board.Castle, None),
    "CK": (board.Castle, board.King)
}

class GameRule(object):
    """
    Base class for game rules
    """

    @staticmethod
    def board():
        """
        Builds the board by
        """
        grid = self.BOARD_TEMPLATE

        for row in grid:
            for column in row:
                
                tile, piece = TILE_PIECE_MAP[self.BOARD_TEMPLATE[row][column]]

                grid[row][column] = tile()
                if piece is not None

                grid[row][column]


class AshtonRules(GameRule):
    """
    Ashton rules implementation
    """
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

    def board():
        # Create a 9x9 grid
        grid = [
            [board.Tile()] * 9 for _ in range(9)
        ]

        # Place castle and king
        grid[4][4] = board.Castle()
        grid[4][4].place(board.King())

        # Place white soldiers
        grid[4][2:4] = list(map()

        grid[4][2:4].place(board.WhiteSoldier())
        grid[4][5:7].place(board.WhiteSoldier())
        grid[2:4][4].place(board.WhiteSoldier())
        grid[5:7][4].place(board.WhiteSoldier())

        # Place camps
        grid[3:6][0] = board.Camp()
        grid[3:6]

