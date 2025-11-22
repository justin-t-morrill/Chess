#State tracks the irreversible parts of the board state
class State:
    def __init__(self, castlingRights : list[bool], passantColumn : int, lastIrreversible : int, zobrist : int, capturedPiece : int):
        #castling lists the castling rights of each player. The first entry is white's kingside castling, then white's queenside castling, then black's kingside castling, and lastly black's queenside castling
        self.castlingRights : list[bool] = castlingRights
        
        #If en passant is possible, passantColumn is the column that the pawn is at. Otherwise, passantColumn is -1
        self.passantColumn : int = passantColumn

        #lastIrreversible tracks the plies since the last irreversible move (capture or pawn move) when lastIrreversible is 100, the game is a draw by the 50 move rule.
        #It is also helpful for decreasing engine search times
        self.lastIrreversible : int = lastIrreversible

        #zobrist tracks the zobrist hash of the board state. It is useful for storing the board state as a single 64-bit integer
        self.zobrist : int = zobrist

        #capturedPiece tracks whether the last move captured a piece. Since we know which side made the last move, this is a positive integer corresponding to the piece, or 0 if no piece was captured
        #This allows the undoMove function to replace captured pieces
        self.capturedPiece : int = capturedPiece