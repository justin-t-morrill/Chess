#The Move object contains all the needed information about a move.
class Move:#
    def __init__(self, fromSq : tuple[int, int], toSq : tuple[int, int], isPromotion : bool, isCapture : bool, sp1 : bool, sp2 : bool):
        #fromSq is the square the piece moves from
        self.fromSq : tuple[int, int] = fromSq

        #toSq is the suqare the piece moves to
        self.toSq : tuple[int, int] = toSq

        #isPromotion tracks if the move is a pawn promotion
        self.isPromotion : bool = isPromotion

        #isCapture tracks if the move was a capture
        self.isCapture : bool = isCapture

        #sp1 and sp2 track special information about the move: whether it was en passant, castling, and which piece a pawn was promoted into
        #For non promotions or captures, 00 means a quite move, 01 means a double pawn push, 10 means a kingside castle, and 11 means a queenside castle
        #For captures, 00 is a normal capture, and 01 is en passant
        #For promotions, 00 is a knight promotion, 01 is a bishop, 10 is a rook, and 11 is a queen
        self.sp1 : bool = sp1
        self.sp2 : bool = sp2  