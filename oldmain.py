import copy, random, time, pygame
import OpeningBook

#Class to represent a board state. Board is a 2D array of integers
#Pawn : 1, Rook : 2, Knight : 3, Bishop : 4, Queen : 5, King : 6
#White is positive, black is negative, blank squares are 0
class ChessBoard:
    #Initializes board to default state
    def __init__(self):
        #myState is the board state
        self.myState : list[list[int]] = [[2, 3, 4, 5, 6, 4, 3, 2], [1, 1, 1, 1, 1, 1, 1, 1], [0] * 8, [0] * 8, [0] * 8, [0] * 8, [-1, -1, -1, -1, -1, -1, -1, -1], [-2, -3, -4, -5, -6, -4, -3, -2]]
        
        #move is a bit storing whose move it is. 1 for white, -1 for black
        self.move : int = 1

        #state_stack is a stack consisting of the irreversible aspects of a board position: en passant state, castling rights, captures, and the time since the last irreversible move
        #It also contains the current zobrist hash
        self.state_stack : list[State] = []

        #seenPositions is a dictionary of all seen board positions. It is used to detect repearted positions and theefold repetitions
        self.seenPositions : dict = {}

        #zobristKey is the key needed to perform zobrist hashing
        self.zobristKey : list[int] = ZobristInit()

        #moveCounter is the number of total moves (starts at 1, increases after black moves)
        self.moveCounter = 1

        #Shows whether the bot is still in it's opening book or not
        self.inOpening = True

        #Stores the opening book
        self.openingBook = OpeningBook.myBook

        #Sets up PeSTO tables
        mg_pawn_table = [
            [0,   0,   0,   0,   0,   0,  0,   0],
            [-35,  -1, -20, -23, -15,  24, 38, -22],
            [-26,  -4,  -4, -10,   3,   3, 33, -12],
            [-27,  -2,  -5,  12,  17,   6, 10, -25],
            [-14,  13,   6,  21,  23,  12, 17, -23],
            [-6,   7,  26,  31,  65,  56, 25, -20],
            [98, 134,  61,  95,  68, 126, 34, -11],
            [0,   0,   0,   0,   0,   0,  0,   0]
        ]

        eg_pawn_table = [
            [0,   0,   0,   0,   0,   0,   0,   0],
            [13,   8,   8,  10,  13,   0,   2,  -7],
            [4,   7,  -6,   1,   0,  -5,  -1,  -8],
            [13,   9,  -3,  -7,  -7,  -8,   3,  -1],
            [32,  24,  13,   5,  -2,   4,  17,  17],
            [94, 100,  85,  67,  56,  53,  82,  84],
            [178, 173, 158, 134, 147, 132, 165, 187],
            [0,   0,   0,   0,   0,   0,   0,   0]
        ]

        mg_knight_table = [
            [-73, -41,  72,  36,  23,  62,   7,  -17],
            [-105, -21, -58, -33, -17, -28, -19,  -23],
            [-29, -53, -12,  -3,  -1,  18, -14,  -19],
            [-23,  -9,  12,  10,  19,  17,  25,  -16],
            [-13,   4,  16,  13,  28,  19,  21,   -8],
            [-9,  17,  19,  53,  37,  69,  18,   22],
            [-47,  60,  37,  65,  84, 129,  73,   44],
            [-167, -89, -34, -49,  61, -97, -15, -107]
        ]

        eg_knight_table = [
            [-29, -51, -23, -15, -22, -18, -50, -64],
            [-42, -20, -10,  -5,  -2, -20, -23, -44],
            [-23,  -3,  -1,  15,  10,  -3, -20, -22],
            [-18,  -6,  16,  25,  16,  17,   4, -18],
            [-17,   3,  22,  22,  22,  11,   8, -18],
            [-24, -20,  10,   9,  -1,  -9, -19, -41],
            [-25,  -8, -25,  -2,  -9, -25, -24, -52],
            [-58, -38, -13, -28, -31, -27, -63, -99]
        ]

        mg_bishop_table = [
            [-33,  -3, -14, -21, -13, -12, -39, -21],
            [4,  15,  16,   0,   7,  21,  33,   1],
            [0,  15,  15,  15,  14,  27,  18,  10],
            [-6,  13,  13,  26,  34,  12,  10,   4],
            [-4,   5,  19,  50,  37,  37,   7,  -2],
            [-16,  37,  43,  40,  35,  50,  37,  -2],
            [-26,  16, -18, -13,  30,  59,  18, -47],
            [-29,   4, -82, -37, -25, -42,   7,  -8]
        ]

        eg_bishop_table = [
            [-23,  -9, -23,  -5, -9, -16,  -5, -17],
            [-14, -18,  -7,  -1,  4,  -9, -15, -27],
            [-12,  -3,   8,  10, 13,   3,  -7, -15],
            [-6,   3,  13,  19,  7,  10,  -3,  -9],
            [-3,   9,  12,   9, 14,  10,   3,   2],
            [2,  -8,   0,  -1, -2,   6,   0,   4],
            [-8,  -4,   7, -12, -3, -13,  -4, -14],
            [-14, -21, -11,  -8, -7,  -9, -17, -24]
        ]

        mg_rook_table = [
            [-19, -13,   1,  17, 16,  7, -37, -26],
            [-44, -16, -20,  -9, -1, 11,  -6, -71],
            [-45, -25, -16, -17,  3,  0,  -5, -33],
            [-36, -26, -12,  -1,  9, -7,   6, -23],
            [-24, -11,   7,  26, 24, 35,  -8, -20],
            [-5,  19,  26,  36, 17, 45,  61,  16],
            [27,  32,  58,  62, 80, 67,  26,  44],
            [32,  42,  32,  51, 63,  9,  31,  43]
        ]

        eg_rook_table = [
            [-9,  2,  3, -1, -5, -13,   4, -20],
            [-6, -6,  0,  2, -9,  -9, -11,  -3],
            [-4,  0, -5, -1, -7, -12,  -8, -16],
            [3,  5,  8,  4, -5,  -6,  -8, -11],
            [4,  3, 13,  1,  2,   1,  -1,   2],
            [7,  7,  7,  5,  4,  -3,  -5,  -3],
            [11, 13, 13, 11, -3,   3,   8,   3],
            [13, 10, 18, 15, 12,  12,   8,   5]
        ]

        mg_queen_table = [
            [ -1, -18,  -9,  10, -15, -25, -31, -50],
            [-35,  -8,  11,   2,   8,  15,  -3,   1],
            [-14,   2, -11,  -2,  -5,   2,  14,   5],
            [ -9, -26,  -9, -10,  -2,  -4,   3,  -3],
            [-27, -27, -16, -16,  -1,  17,  -2,   1],
            [-13, -17,   7,   8,  29,  56,  47,  57],
            [-24, -39,  -5,   1, -16,  57,  28,  54],
            [-28,   0,  29,  12,  59,  44,  43,  45]
        ]

        eg_queen_table = [
            [-33, -28, -22, -43,  -5, -32, -20, -41],
            [-22, -23, -30, -16, -16, -23, -36, -32],
            [-16, -27,  15,   6,   9,  17,  10,   5],
            [-18,  28,  19,  47,  31,  34,  39,  23],
            [  3,  22,  24,  45,  57,  40,  57,  36],
            [-20,   6,   9,  49,  47,  35,  19,   9],
            [-17,  20,  32,  41,  58,  25,  30,   0],
            [ -9,  22,  22,  27,  27,  19,  10,  20]
        ]

        mg_king_table = [
            [-15,  36,  12, -54,   8, -28,  24,  14],
            [  1,   7,  -8, -64, -43, -16,   9,   8],
            [-14, -14, -22, -46, -44, -30, -15, -27],
            [-49,  -1, -27, -39, -46, -44, -33, -51],
            [-17, -20, -12, -27, -30, -25, -14, -36],
            [ -9,  24,   2, -16, -20,   6,  22, -22],
            [ 29,  -1, -20,  -7,  -8,  -4, -38, -29],
            [-65,  23,  16, -15, -56, -34,   2,  13]
        ]

        eg_king_table = [
            [-53, -34, -21, -11, -28, -14, -24, -43],
            [-27, -11,   4,  13,  14,   4,  -5, -17],
            [-19,  -3,  11,  21,  23,  16,   7,  -9],
            [-18,  -4,  21,  24,  27,  23,   9, -11],
            [ -8,  22,  24,  27,  26,  33,  26,   3],
            [ 10,  17,  23,  15,  20,  45,  44,  13],
            [-12,  17,  14,  17,  17,  38,  23,  11],
            [-74, -35, -18, -18, -11,  15,   4, -17]
        ]

        self.mg_value = [82, 477, 337, 365, 1025,  0]
        self.eg_value = [94, 512, 281, 297,  936,  0]

        self.gamephaseInc = [0,2,1,1,4,0]

        self.mg_pesto_table = [
            mg_pawn_table,
            mg_rook_table,
            mg_knight_table,
            mg_bishop_table,
            mg_queen_table,
            mg_king_table
        ]

        self.eg_pesto_table = [
            eg_pawn_table,
            eg_rook_table,
            eg_knight_table,
            eg_bishop_table,
            eg_queen_table,
            eg_king_table
        ]

        #Sets up the current states and zobrist key
        castlingRights = [True, True, True, True]
        passantColumn = -1
        lastIrreversible = 0
        zobrist = ZobristHash(self.myState, self.move, castlingRights, passantColumn, self.zobristKey)
        capturedPiece = 0
        currentState = State(castlingRights, passantColumn, lastIrreversible, zobrist, capturedPiece)
        self.state_stack.append(currentState)
        self.seenPositions[zobrist] = 1

    #Checks if the player to move is in check
    def inCheck(self):
        #Skips move, then checks each opponent move to see if the opponent can take the king
        self.move = -1 * self.move
        opponentMoves = self.getPseudoLegalMoves(True)
        for move in opponentMoves:
            if self.myState[move.toSq[0]][move.toSq[1]] * self.move == -6:
                self.move = -1 * self.move
                return True
        self.move = -1 * self.move
        return False

    #Makes the move on the board, updating all variables accordingly
    def makeMove(self, move):
        if move is not None:
            #Gets simple info and sets the square the piece moved from to be empty
            pieceMoved = self.myState[move.fromSq[0]][move.fromSq[1]]
            oldState = self.state_stack[-1]
            zobrist = oldState.zobrist
            self.myState[move.fromSq[0]][move.fromSq[1]] = 0
            castlingRights = copy.copy(self.state_stack[-1].castlingRights)
            lastIrreversible = self.state_stack[-1].lastIrreversible
            passantColumn = self.state_stack[-1].passantColumn
            capturedPiece = 0

            #Update zobrist hash
            if pieceMoved > 0:
                zobristPiece = pieceMoved + 5
            else:
                zobristPiece = pieceMoved + 6
            zobrist = zobrist ^ self.zobristKey[(8 * move.fromSq[0] + move.fromSq[1]) * 12 + zobristPiece]

            #Castling rights and corresponding zobrist hash updates
            if self.move == 1:
                if pieceMoved == 6:
                    if castlingRights[0] == True:
                        castlingRights[0] = False
                        zobrist = zobrist ^ self.zobristKey[769]
                    if castlingRights[1] == True:
                        castlingRights[1] = False
                        zobrist = zobrist ^ self.zobristKey[770]
                elif pieceMoved == 2:
                    if move.fromSq == (0, 7) and castlingRights[0] == True:
                        castlingRights[0] = False
                        zobrist = zobrist ^ self.zobristKey[769]
                    elif move.fromSq == (0, 0) and castlingRights[1] == True:
                        castlingRights[1] = False
                        zobrist = zobrist ^ self.zobristKey[770]
            elif self.move == -1:
                if pieceMoved == -6:
                    if castlingRights[2] == True:
                        castlingRights[2] = False
                        zobrist = zobrist ^ self.zobristKey[771]
                    if castlingRights[3] == True:
                        castlingRights[3] = False
                        zobrist = zobrist ^ self.zobristKey[772]
                elif pieceMoved == -2:
                    if move.fromSq == (7, 7) and castlingRights[2] == True:
                        castlingRights[2] = False
                        zobrist = zobrist ^ self.zobristKey[771]
                    elif move.fromSq == (7, 0) and castlingRights[3] == True:
                        castlingRights[3] = False
                        zobrist = zobrist ^ self.zobristKey[772]

            #Makes the move, and updates corresponding values
            if move.isPromotion == False:
                if move.isCapture == False:
                    #Non capture, non-promotion moves we can simply move the piece to the correct square
                    self.myState[move.toSq[0]][move.toSq[1]] = pieceMoved
                    zobrist = zobrist ^ self.zobristKey[(8 * move.toSq[0] + move.toSq[1]) * 12 + zobristPiece]

                    if move.sp1 == False:
                        #Quiet moves
                        if move.sp2 == False:
                            if passantColumn != -1:
                                zobrist = zobrist ^ self.zobristKey[773 + passantColumn]
                            passantColumn = -1
                            if pieceMoved * self.move == 1:
                                lastIrreversible = 0
                            else:
                                lastIrreversible += 1

                        #Double pawn pushes
                        else:
                            if passantColumn != -1:
                                zobrist = zobrist ^ self.zobristKey[773 + passantColumn]
                            zobrist = zobrist ^ self.zobristKey[773 + move.toSq[1]]
                            passantColumn = move.toSq[1]
                            lastIrreversible = 0
                    
                    else:
                        #Castling (don't have to worry about castling rights since they were dealt with before)
                        if self.move == 1:
                            row = 0
                            rookZobrist = 7
                        else:
                            row = 7
                            rookZobrist = 4

                        #King side castling
                        if move.sp2 == False:
                            self.myState[row][7] = 0
                            zobrist = zobrist ^ self.zobristKey[(8 * row + 7) * 12 + rookZobrist]
                            self.myState[row][5] = 2 * self.move
                            zobrist = zobrist ^ self.zobristKey[(8 * row + 5) * 12 + rookZobrist]
                            if passantColumn != -1:
                                zobrist = zobrist ^ self.zobristKey[773 + passantColumn]
                            passantColumn = -1
                            lastIrreversible += 1

                        #Queen side castling
                        else:
                            self.myState[row][0] = 0
                            zobrist = zobrist ^ self.zobristKey[(8 * row) * 12 + rookZobrist]
                            self.myState[row][3] = 2 * self.move
                            zobrist = zobrist ^ self.zobristKey[(8 * row + 3) * 12 + rookZobrist]
                            if passantColumn != -1:
                                zobrist = zobrist ^ self.zobristKey[773 + passantColumn]
                            passantColumn = -1
                            lastIrreversible += 1

                else:
                    #Normal captures
                    if move.sp2 == False:
                        capturedPiece = self.myState[move.toSq[0]][move.toSq[1]]
                        if capturedPiece > 0:
                            capturedZobrist = capturedPiece + 5
                        else:
                            capturedZobrist = capturedPiece + 6
                        zobrist = zobrist ^ self.zobristKey[(8 * move.toSq[0] + move.toSq[1]) * 12 + capturedZobrist]
                        self.myState[move.toSq[0]][move.toSq[1]] = pieceMoved
                        zobrist = zobrist ^ self.zobristKey[(8 * move.toSq[0] + move.toSq[1]) * 12 + zobristPiece]
                        if passantColumn != -1:
                            zobrist = zobrist ^ self.zobristKey[773 + passantColumn]
                        passantColumn = -1
                        lastIrreversible = 0

                        #If capturing an unmoved rook, need to remove castling rights
                        if capturedPiece == -2 * self.move:
                            if (self.move == -1) and (move.toSq[0] == 0) and (move.toSq[1] == 7):
                                if castlingRights[0] == True:
                                    castlingRights[0] = False
                                    zobrist = zobrist ^ self.zobristKey[769]
                            
                            if (self.move == -1) and (move.toSq[0] == 0) and (move.toSq[1] == 0):
                                if castlingRights[1] == True:
                                    castlingRights[1] = False
                                    zobrist = zobrist ^ self.zobristKey[770]
                            
                            if (self.move == 1) and (move.toSq[0] == 7) and (move.toSq[1] == 7):
                                if castlingRights[2] == True:
                                    castlingRights[2] = False
                                    zobrist = zobrist ^ self.zobristKey[771]
                            
                            if (self.move == 1) and (move.toSq[0] == 7) and (move.toSq[1] == 0):
                                if castlingRights[3] == True:
                                    castlingRights[3] = False
                                    zobrist = zobrist ^ self.zobristKey[772]
                    
                    #En passant
                    else:
                        capturedPiece = -1 * self.move
                        if capturedPiece > 0:
                            capturedZobrist = capturedPiece + 5
                        else:
                            capturedZobrist = capturedPiece + 6
                        self.myState[move.toSq[0] - self.move][move.toSq[1]] = 0
                        zobrist = zobrist ^ self.zobristKey[(8 * (move.toSq[0] - self.move) + move.toSq[1]) * 12 + capturedZobrist]
                        self.myState[move.toSq[0]][move.toSq[1]] = pieceMoved
                        zobrist = zobrist ^ self.zobristKey[(8 * move.toSq[0] + move.toSq[1]) * 12 + zobristPiece]
                        if passantColumn != -1:
                            zobrist = zobrist ^ self.zobristKey[773 + passantColumn]
                        passantColumn = -1
                        lastIrreversible = 0

            #Promotions
            else:
                #Gets promoted piece and zobrist info
                if move.sp1 == False:
                    if move.sp2 == False:
                        promotedPiece = 3 * self.move
                    else:
                        promotedPiece = 4 * self.move
                else:
                    if move.sp2 == False:
                        promotedPiece = 2 * self.move
                    else:
                        promotedPiece = 5 * self.move
                if promotedPiece > 0:
                    promotedZobrist = promotedPiece + 5
                else:
                    promotedZobrist = promotedPiece + 6
                
                #En passant and irreversible move changes
                if passantColumn != -1:
                    zobrist = zobrist ^ self.zobristKey[773 + passantColumn]
                passantColumn = -1
                lastIrreversible = 0

                #Changes the state and zobrist hash
                if move.isCapture == False:
                    self.myState[move.toSq[0]][move.toSq[1]] = promotedPiece
                    zobrist = zobrist ^ self.zobristKey[(8 * move.toSq[0] + move.toSq[1]) * 12 + promotedZobrist]
                else:
                    capturedPiece = self.myState[move.toSq[0]][move.toSq[1]]
                    if capturedPiece > 0:
                        capturedZobrist = capturedPiece + 5
                    else:
                        capturedZobrist = capturedPiece + 6
                    zobrist = zobrist ^ self.zobristKey[(8 * move.toSq[0] + move.toSq[1]) * 12 + capturedZobrist]
                    self.myState[move.toSq[0]][move.toSq[1]] = promotedPiece
                    zobrist = zobrist ^ self.zobristKey[(8 * move.toSq[0] + move.toSq[1]) * 12 + promotedZobrist]

                    #Captured rooks update castling rights
                    if capturedPiece == -2 * self.move:
                        if (self.move == -1) and (move.toSq[0] == 0) and (move.toSq[1] == 7):
                            if castlingRights[0] == True:
                                castlingRights[0] = False
                                zobrist = zobrist ^ self.zobristKey[769]
                        
                        if (self.move == -1) and (move.toSq[0] == 0) and (move.toSq[1] == 0):
                            if castlingRights[1] == True:
                                castlingRights[1] = False
                                zobrist = zobrist ^ self.zobristKey[770]
                        
                        if (self.move == 1) and (move.toSq[0] == 7) and (move.toSq[1] == 7):
                            if castlingRights[2] == True:
                                castlingRights[2] = False
                                zobrist = zobrist ^ self.zobristKey[771]
                        
                        if (self.move == 1) and (move.toSq[0] == 7) and (move.toSq[1] == 0):
                            if castlingRights[3] == True:
                                castlingRights[3] = False
                                zobrist = zobrist ^ self.zobristKey[772]

            #Updates whose turn it is and zobrist hash accordingly
            self.move = -1 * self.move
            zobrist = zobrist ^ self.zobristKey[768]

            #Updates move counter
            if (self.move == 1):
                self.moveCounter += 1

            #Updates seen positions
            if zobrist in self.seenPositions.keys():
                self.seenPositions[zobrist] += 1
            else:
                self.seenPositions[zobrist] = 1

            #Updates state stack
            newState = State(castlingRights, passantColumn, lastIrreversible, zobrist, capturedPiece)
            self.state_stack.append(newState)
                
    def unmakeMove(self, move):
        if move is not None:
            #Pops the last state off the state stack
            poppedState = self.state_stack.pop()

            #Removes the state from seenPositions
            if self.seenPositions[poppedState.zobrist] > 1:
                self.seenPositions[poppedState.zobrist] -= 1
            else:
                del self.seenPositions[poppedState.zobrist]

            #Changes the board state back
            #Non-promotions
            if move.isPromotion == False:
                #For non-promotions, the moved piece is the piece on the "to square"
                movedPiece = self.myState[move.toSq[0]][move.toSq[1]]

                #Non-captures
                if move.isCapture == False:
                    #Moves the piece back to the starting square
                    self.myState[move.toSq[0]][move.toSq[1]] = 0
                    self.myState[move.fromSq[0]][move.fromSq[1]] = movedPiece

                    #Undoes the rook move for castling
                    if move.sp1 == True:
                        if self.move == -1:
                            row = 0
                        else:
                            row = 7
                        if move.sp2 == False:
                            self.myState[row][5] = 0
                            self.myState[row][7] = -2 * self.move
                        else:
                            self.myState[row][3] = 0
                            self.myState[row][0] = -2 * self.move
                            
                #Non-promotion captures
                else:
                    #Normal captures, just move moved piece back and replace square with the captured piece
                    if move.sp2 == False:
                        self.myState[move.toSq[0]][move.toSq[1]] = poppedState.capturedPiece
                        self.myState[move.fromSq[0]][move.fromSq[1]] = movedPiece

                    #En passant, also need to replace captured pawn
                    else:
                        self.myState[move.toSq[0]][move.toSq[1]] = 0
                        self.myState[move.fromSq[0]][move.fromSq[1]] = movedPiece
                        self.myState[move.toSq[0] + self.move][move.toSq[1]] = self.move

            #Promotions
            else:
                #Moved piece is a pawn
                movedPiece = -1 * self.move

                #Non-captures, just need to move the pawn back
                if move.isCapture == False:
                    self.myState[move.toSq[0]][move.toSq[1]] = 0
                    self.myState[move.fromSq[0]][move.fromSq[1]] = movedPiece
                
                #Captured, just need to move the pawn back and replace the captured piece
                else:
                    self.myState[move.toSq[0]][move.toSq[1]] = poppedState.capturedPiece
                    self.myState[move.fromSq[0]][move.fromSq[1]] = movedPiece

            #Change whose turn it is
            self.move = -1 * self.move

            #Update move counter
            if self.move == -1:
                self.moveCounter -= 1

    #Gets all pseudo legal moves possible from one piece. Pseudo legal moves are moves that pieces can make, but may leave the king in check
    def getPseudoLegalPieceMoves(self, row, column, capFriendly):
        #moves is a list of the possible moves
        moves = []

        #If piece is not the right color or the square is blank, no moves can be made
        if self.myState[row][column] * self.move < 0:
            return moves
        
        #Switch statement to determine which piece is being moves
        match (self.myState[row][column] * self.move):
            #Pawns
            case 1:
                #If it is on the 2nd to last row, the only moves available are promotions
                if (row == 6 and self.move == 1) or (row == 1 and self.move == -1):
                    #Non-capture promotion
                    if self.myState[row + self.move][column] == 0:
                        #Loops over all four possible promotion pieces (the sp1 and sp2 flags) and adds each move
                        for piece in [[0, 0], [0, 1], [1, 0], [1, 1]]:
                            moves.append(Move((row, column), (row + self.move, column), True, False, piece[0], piece[1]))
                    
                    #Left capture promotion
                    if (column > 0) and ((self.myState[row + self.move][column - 1] * self.move < 0) or (capFriendly and (self.myState[row + self.move][column - 1] * self.move > 0))):
                        for piece in [[0, 0], [0, 1], [1, 0], [1, 1]]:
                            moves.append(Move((row, column), (row + self.move, column - 1), True, True, piece[0], piece[1]))
                    
                    #Right capture promotion
                    if (column < 7) and ((self.myState[row + self.move][column + 1] * self.move < 0) or (capFriendly and (self.myState[row + self.move][column + 1] * self.move > 0))):
                        for piece in [[0, 0], [0, 1], [1, 0], [1, 1]]:
                            moves.append(Move((row, column), (row + self.move, column + 1), True, True, piece[0], piece[1]))
                
                else:
                    #Single/double pawn moves
                    if self.myState[row + self.move][column] == 0:
                        moves.append(Move((row, column), (row + self.move, column), False, False, False, False))

                        #Double pawn move
                        if ((row == 1 and self.move == 1) or (row == 6 and self.move == -1)) and (self.myState[row + (2 * self.move)][column] == 0):
                            moves.append(Move((row, column), (row + (2 * self.move), column), False, False, False, True))
                    
                    #Left capture
                    if (column > 0) and ((self.myState[row + self.move][column - 1] * self.move < 0) or (capFriendly and (self.myState[row + self.move][column - 1] * self.move > 0))):
                        moves.append(Move((row, column), (row + self.move, column - 1), False, True, False, False))
                    
                    #Right capture
                    if (column < 7) and ((self.myState[row + self.move][column + 1] * self.move < 0) or (capFriendly and (self.myState[row + self.move][column + 1] * self.move > 0))):
                        moves.append(Move((row, column), (row + self.move, column + 1), False, True, False, False))

                    #En passant
                    if (row == 4 and self.move == 1) or (row == 3 and self.move == -1):
                        #Left en passant
                        if (column > 0) and (self.state_stack[-1].passantColumn == column - 1):
                            moves.append(Move((row, column), (row + self.move, column - 1), False, True, False, True))

                        #Right en passant
                        if (column < 7) and (self.state_stack[-1].passantColumn == column + 1):
                            moves.append(Move((row, column), (row + self.move, column + 1), False, True, False, True))

            #Rooks
            case 2:
                #Loops over all 4 directions the rook can move in
                for direction in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                    currRow = row + direction[0]
                    currCol = column + direction[1]

                    #While the square we are looking at is blank (and still on the board), add a move to that square and move on to the next square
                    while (0 <= currRow <= 7) and (0 <= currCol <= 7) and self.myState[currRow][currCol] == 0:
                        moves.append(Move((row, column), (currRow, currCol), False, False, False, False))
                        currRow += direction[0]
                        currCol += direction[1]

                    #If the last square has an enemy piece on it, we can take that piece
                    if (0 <= currRow <= 7) and (0 <= currCol <= 7) and (capFriendly or self.myState[currRow][currCol] * self.move < 0):
                        moves.append(Move((row, column), (currRow, currCol), False, True, False, False))

            #Knights
            case 3:
                #Loops over all 8 possible knight moves
                for direction in [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (-1, 2), (1, -2), (-1, -2)]:
                    #Checks if the move is in bounds
                    if (0 <= row + direction[0] <= 7) and (0 <= column + direction[1] <= 7):
                        #Non-captures
                        if self.myState[row + direction[0]][column + direction[1]] == 0:
                            moves.append(Move((row, column), (row + direction[0], column + direction[1]), False, False, False, False))

                        #Captures
                        elif self.myState[row + direction[0]][column + direction[1]] * self.move < 0 or (capFriendly and self.myState[row + direction[0]][column + direction[1]] * self.move > 0):
                            moves.append(Move((row, column), (row + direction[0], column + direction[1]), False, True, False, False))

            #Bishops
            case 4:
                #Loops over all 4 directions the bishop can move in
                for direction in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
                    currRow = row + direction[0]
                    currCol = column + direction[1]

                    #While the square we are looking at is blank (and still on the board), add a move to that square and move on to the next square
                    while (0 <= currRow <= 7) and (0 <= currCol <= 7) and self.myState[currRow][currCol] == 0:
                        moves.append(Move((row, column), (currRow, currCol), False, False, False, False))
                        currRow += direction[0]
                        currCol += direction[1]

                    #If the last square has an enemy piece on it, we can take that piece
                    if (0 <= currRow <= 7) and (0 <= currCol <= 7) and (capFriendly or self.myState[currRow][currCol] * self.move < 0):
                        moves.append(Move((row, column), (currRow, currCol), False, True, False, False))

            #Queens
            case 5:
                #Loops over all 8 directions the queen can move in
                for direction in [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
                    currRow = row + direction[0]
                    currCol = column + direction[1]

                    #While the square we are looking at is blank (and still on the board), add a move to that square and move on to the next square
                    while (0 <= currRow <= 7) and (0 <= currCol <= 7) and self.myState[currRow][currCol] == 0:
                        moves.append(Move((row, column), (currRow, currCol), False, False, False, False))
                        currRow += direction[0]
                        currCol += direction[1]

                    #If the last square has an enemy piece on it, we can take that piece
                    if (0 <= currRow <= 7) and (0 <= currCol <= 7) and (capFriendly or self.myState[currRow][currCol] * self.move < 0):
                        moves.append(Move((row, column), (currRow, currCol), False, True, False, False))

            #Kings
            case 6:
                #Loops over all 8 possible king moves
                for direction in [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
                    #Checks if the move is in bounds
                    if (0 <= row + direction[0] <= 7) and (0 <= column + direction[1] <= 7):
                        #Non-captures
                        if self.myState[row + direction[0]][column + direction[1]] == 0:
                            moves.append(Move((row, column), (row + direction[0], column + direction[1]), False, False, False, False))

                        #Captures
                        elif self.myState[row + direction[0]][column + direction[1]] * self.move < 0 or (capFriendly and self.myState[row + direction[0]][column + direction[1]] * self.move > 0):
                            moves.append(Move((row, column), (row + direction[0], column + direction[1]), False, True, False, False))
                
                #King side castling
                if self.state_stack[-1].castlingRights[1 - self.move] == True:
                    if (self.myState[row][column + 1] == 0) and (self.myState[row][column + 2] == 0):
                        moves.append(Move((row, column), (row, column + 2), False, False, True, False))

                #Queen side castling
                if self.state_stack[-1].castlingRights[2 - self.move] == True:
                    if (self.myState[row][column - 1] == 0) and (self.myState[row][column - 2] == 0) and (self.myState[row][column - 3] == 0):
                        moves.append(Move((row, column), (row, column - 2), False, False, True, True))

        return moves

                        
    #Gets all pseudo legal moves possible from the current state
    def getPseudoLegalMoves(self, capFriendly):
        #moves is a list of all pseudo legal moves, stored as Move objects
        moves = []

        #Loops over all squares and gets the pseudo legal moves for each square
        for row in range(8):
            for column in range(8):
                squareMoves = self.getPseudoLegalPieceMoves(row, column, capFriendly)
                for move in squareMoves:
                    moves.append(move)
        return moves
    
    #Gets all legal moves (need to worry about checks)
    def getMoves(self):
        moves = []

        #Gets king position
        kingRow = -1
        kingColumn = -1
        for row in range(8):
            for column in range(8):
                if self.myState[row][column] * self.move == 6:
                    kingRow = row
                    kingColumn = column

        #Gets squares controlled by the opponent
        opponentControlled = set()
        self.move = -1 * self.move
        opponentMoves = self.getPseudoLegalMoves(True)
        for move in opponentMoves:
            if self.myState[move.fromSq[0]][move.fromSq[1]] * self.move != 1:
                opponentControlled.add(move.toSq)
        for row in range(8):
            for column in range(8):
                if self.myState[row][column] * self.move == 1:
                    opponentControlled.add((row + self.move, column + 1))
                    opponentControlled.add((row + self.move, column - 1))
        self.move = -1 * self.move

        #Gets pinned pieces (and rooks/bishops/queens attacking the king)
        pinnedSquares = []
        pinnedAxes = []
        attackers = []
        attackerDirs = []
        rookMoves = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        bishopMoves = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        #Searches each direction a piece can pin the king
        for direction in [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
            currentRow = kingRow + direction[0]
            currentCol = kingColumn + direction[1]
            pieceBlock = False
            pinnedSquare = (-1, -1)
            #Looks for the first piece in the direction
            #Friendly pieces can be pinned, enemy pieces can be attackers
            while (0 <= currentRow <= 7) and (0 <= currentCol <= 7):
                currentPiece = self.myState[currentRow][currentCol] * self.move
                if currentPiece > 0:
                    pieceBlock = True
                    pinnedSquare = currentRow, currentCol
                    break
                elif currentPiece < 0:
                    if ((currentPiece == -2) and (direction in rookMoves)) or ((currentPiece == -4) and (direction in bishopMoves)) or (currentPiece == -5):
                        attackers.append((currentRow, currentCol))
                        attackerDirs.append(direction)
                    break
                currentRow += direction[0]
                currentCol += direction[1]

            #If there is a friendly piece that can be pinned, keep looking for an enemy piece pinning it
            if pieceBlock == True:
                currentRow += direction[0]
                currentCol += direction[1]
                while (0 <= currentRow <= 7) and (0 <= currentCol <= 7):
                    currentPiece = self.myState[currentRow][currentCol] * self.move
                    if currentPiece > 0:
                        break
                    elif currentPiece < 0:
                        if ((currentPiece == -2) and (direction in rookMoves)) or ((currentPiece == -4) and (direction in bishopMoves)) or (currentPiece == -5):
                            pinnedSquares.append(pinnedSquare)
                            pinnedAxes.append(direction)
                        break
                    currentRow += direction[0]
                    currentCol += direction[1]

        pseudoLegalMoves = self.getPseudoLegalMoves(False)
        #Not in check
        if (kingRow, kingColumn) not in opponentControlled:
            for move in pseudoLegalMoves:

                #King moves cannot move into check or castle through check
                if (move.fromSq[0] == kingRow) and (move.fromSq[1] == kingColumn):
                    if move.toSq not in opponentControlled:
                        #Castling
                        if move.sp1 == True:
                            if move.sp2 == False:
                                if (move.toSq[0], move.toSq[1] - 1) not in opponentControlled:
                                    moves.append(move)
                            else:
                                if (move.toSq[0], move.toSq[1] + 1) not in opponentControlled:
                                    moves.append(move)

                        else:
                            moves.append(move)

                #Pinned pieces can only move along the axis that they are pinned on
                elif move.fromSq in pinnedSquares:
                    axis = pinnedAxes[pinnedSquares.index(move.fromSq)]
                    validRow = kingRow + axis[0]
                    validCol = kingColumn + axis[1]
                    while (0 <= validRow <= 7) and (0 <= validCol <= 7):
                        if move.toSq == (validRow, validCol):
                            moves.append(move)
                            break
                        validRow += axis[0]
                        validCol += axis[1]

                #Nonpinned pieces can move freely
                else:
                    #With en passant we will look to see if the opponent can take our king after making the move
                    #This isn't super slow since en passant is rare
                    if (move.sp2 == True) and (move.isPromotion == False) and (move.isCapture == True):
                        self.makeMove(move)
                        newOpponentControlled = set()
                        newOpponentMoves = self.getPseudoLegalMoves(False)
                        for newMove in newOpponentMoves:
                            newOpponentControlled.add(newMove.toSq)
                        if (kingRow, kingColumn) not in newOpponentControlled:
                            moves.append(move)
                        self.unmakeMove(move)

                    #Nonpinned pieces can move freely
                    else:
                        moves.append(move)

        #In check
        else:
            sliderAttacker = False
            if len(attackers) != 0:
                sliderAttacker = True
                
            #If a slider attacker (rook, bishop, queen), can block the attack
            #This gets the squares to block the attack
            if sliderAttacker and (len(attackers) == 1):
                blockable = set()
                currentRow = kingRow + attackerDirs[0][0]
                currentCol = kingColumn + attackerDirs[0][1]
                while (currentRow, currentCol) != attackers[0]:
                    blockable.add((currentRow, currentCol))
                    currentRow += attackerDirs[0][0]
                    currentCol += attackerDirs[0][1]

            #First, find all attacking pieces
            #Attacking pawns
            for direction in ((self.move, 1), (self.move, -1)):
                if (0 <= kingRow + direction[0] <= 7) and (0 <= kingColumn + direction[1] <= 7):
                    if self.myState[kingRow + direction[0]][kingColumn + direction[1]] * self.move == -1:
                        attackers.append((kingRow + direction[0], kingColumn + direction[1]))

            #Attacking knights
            for direction in ((2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (-1, 2), (1, -2), (-1, -2)):
                if (0 <= kingRow + direction[0] <= 7) and (0 <= kingColumn + direction[1] <= 7):
                    if self.myState[kingRow + direction[0]][kingColumn + direction[1]] * self.move == -3:
                        attackers.append((kingRow + direction[0], kingColumn + direction[1]))

            for move in pseudoLegalMoves:
                #King can move into any safe square (besides castling)
                if (move.fromSq[0] == kingRow) and (move.fromSq[1] == kingColumn):
                    if move.sp1 == False:
                        if move.toSq not in opponentControlled:
                            valid = True
                            for sliderDir in attackerDirs:
                                if move.toSq == (kingRow - sliderDir[0], kingColumn - sliderDir[1]):
                                    valid = False
                            if valid:
                                moves.append(move)


                #If one attacker, can also capture or block the attack (as long as piece is not pinned)
                elif len(attackers) == 1:
                    #Checks if the move captures or blocks the attack, can check for pins at the same time
                    isSafe = False

                    #Blocking attacks
                    if (sliderAttacker) and (move.toSq in blockable):
                        isSafe = True
                        
                    #Capturing the attacker
                    if move.toSq == attackers[0]:
                        isSafe = True

                    #If the attacker is a pawn, you can capture it with en passant
                    if (move.sp2 == True) and (move.isPromotion == False) and (move.isCapture == True):
                        if (move.toSq[0] - self.move, move.toSq[1]) == attackers[0]:
                            isSafe = True
                    
                    #If the piece is pinned, can only move along the pin. Otherwise, the piece is free to move
                    if isSafe:
                        if move.fromSq in pinnedSquares:
                            axis = pinnedAxes[pinnedSquares.index(move.fromSq)]
                            validRow = kingRow + axis[0]
                            validCol = kingColumn + axis[1]
                            while (0 <= validRow <= 7) and (0 <= validCol <= 7):
                                if move.toSq == (validRow, validCol):
                                    moves.append(move)
                                    break
                                validRow += axis[0]
                                validCol += axis[1]
                        else:
                            moves.append(move)

        return moves
    
    #Runs the Perft test (prints number of legal moves for a certain depth)
    def perft(self, depth, verbose, divide):
        if depth == 0:
            return 1
        total = 0
        #Loops over each move, makes the move, calls Perft with one less depth, then undoes the move
        moves = self.getMoves()
        for move in moves:
            self.makeMove(move)

            #Verbose prints the board state of every state it computes
            if verbose:
                print(self)

            part = self.perft(depth - 1, verbose, False)

            #Divide prints the perft value after each move
            if divide:
                if move.isPromotion:
                    promPiece = ".prnbqk"[abs(self.myState[move.toSq[0]][move.toSq[1]])]
                else:
                    promPiece = ""
                print(intsToSquare(move.fromSq[0], move.fromSq[1]) + intsToSquare(move.toSq[0], move.toSq[1]) + promPiece + ":", part)
            
            total += part
            self.unmakeMove(move)

        return total
    
    #Loads a FEN string into the board state
    def loadFEN(self, FEN):
        splitFEN = FEN.split(" ")
        if len(splitFEN) == 6:
            state, move, castling, passant, irreversible, counter = splitFEN
        elif len(splitFEN) == 5:
            state, move, castling, passant, irreversible = splitFEN
            counter = "1"
        elif len(splitFEN) == 4:
            state, move, castling, passant = splitFEN
            counter = "1"
            irreversible = "0"
        
        #Deals with the board state
        self.myState = []
        rows = state.split("/")
        for row in rows:
            newRow = []
            for piece in row:
                if piece in "12345678":
                    for _ in range(int(piece)):
                        newRow.append(0)
                elif piece in "kqbnrp.PRNBQK":
                    newRow.append("kqbnrp.PRNBQK".find(piece) - 6)
            self.myState.append(newRow)
        self.myState.reverse()

        #Deals with whose move it is
        if move == 'w':
            self.move = 1
        else:
            self.move = -1

        #Deals with castling state
        castlingRights = [False, False, False, False]
        for right in castling:
            if right == "K":
                castlingRights[0] = True
            elif right == "Q":
                castlingRights[1] = True
            elif right == "k":
                castlingRights[2] = True
            elif right == "q":
                castlingRights[3] = True

        #Deals with en passant target square
        if passant in "abcdefgh":
            passantColumn = "abcdefgh".find(passant)
        else:
            passantColumn = -1

        #Deals with the half-move counter
        lastIrreversible = int(irreversible)

        #Deals with move counter
        self.moveCounter = int(counter)

        #Gets Zobrist hash
        zobrist = ZobristHash(self.myState, self.move, castlingRights, passantColumn, self.zobristKey)

        #Default values
        capturedPiece = 0
        self.seenPositions = {}
        self.seenPositions[zobrist] = 1

        #Updates state stack
        self.state_stack = []
        self.state_stack.append(State(castlingRights, passantColumn, lastIrreversible, zobrist, capturedPiece))
    
    #Gets the FEN string for the board state
    def getFEN(self):
        FENstring = ""

        #Loops over each square and adds the corresponding value to the string
        for row in self.myState:
            rowStr = "" 
            blanks = 0
            for piece in row:
                if piece == 0:
                    blanks += 1
                else:
                    if blanks != 0:
                        rowStr += str(blanks)
                        blanks = 0
                    rowStr += "kqbnrp.PRNBQK"[piece + 6]
            if blanks != 0:
                rowStr += str(blanks)
            rowStr += "/"
            FENstring = rowStr + FENstring
        FENstring = FENstring[:-1]

        FENstring += " "
        FENstring += "b.w"[self.move + 1]
        FENstring += " "
        if self.state_stack[-1].castlingRights[0]:
            FENstring += "K"
        if self.state_stack[-1].castlingRights[1]:
            FENstring += "Q"
        if self.state_stack[-1].castlingRights[2]:
            FENstring += "k"
        if self.state_stack[-1].castlingRights[3]:
            FENstring += "q"
        FENstring += " "

        if self.state_stack[-1].passantColumn == -1:
            FENstring += "-"
        else:
            FENstring += "abcdefgh"[self.state_stack[-1].passantColumn]
            FENstring += "3.6"[self.move + 1]

        FENstring += " "
        FENstring += str(self.state_stack[-1].lastIrreversible)
        FENstring += " "
        FENstring += str(self.moveCounter)

        return FENstring
                


    #Renders the board using pygame
    def render(self, pngs, screen):
        #Displays the blank board
        screen.fill("white")
        screen.blit(pngs[6], (0,0))

        #Loops over each square, drawing the poiece on that square
        rowIndex = 0
        for row in self.myState:
            columnIndex = 0
            for piece in row:
                if piece != 0:
                    screen.blit(pngs[piece + 6], (64 * columnIndex, 64 * (7 - rowIndex)))
                columnIndex += 1
            rowIndex += 1
        pygame.display.flip()
        
    #Gets a basic material evaluation of the board state
    def eval(self):
        points = [-100000, -900, -300, -300, -500, -100, 0, 100, 500, 300, 300, 900, 100000]
        eval = 0
        for row in self.myState:
            for piece in row:
                eval += points[piece + 6]

        return eval
    
    #String representation of a board
    def __str__(self):
        #Loops over each square, and prints the piece in that square
        myString = " _________________\n"
        for row in range(7, -1, -1):
            myString += str(row + 1) + "|"
            for column in range(8):
                if (self.myState[row][column] > 0):
                    myString += (["", "P", "R", "N", "B", "Q", "K"][abs(self.myState[row][column])])
                elif (self.myState[row][column] < 0):
                    myString += (["", "p", "r", "n", "b", "q", "k"][abs(self.myState[row][column])])
                else:
                    myString += "."
                myString += "|"
            myString += "\n"
        myString += " _________________\n  a b c d e f g h"
        return myString
    
#Uses negamax to get the eval
def negaMax(board, alpha, beta, depth, tt, endTime):
    #Makes sure the screen doesn't freeze
    #pygame.event.pump()

    #Breaks if we run out of time
    if time.time() >= endTime:
        return None

    #Original alpha value to check for fail-low nodes
    alphaOrig = alpha

    #Checks for 50-move rule and three-fold repitition before transposition table entries
    #This is because the half move clock and seen moves are not included in the zobrist hash
    #Also note that this is checking for 2-fold repitition. This is because the position is identical, so it should be a draw
    if board.state_stack[-1].lastIrreversible == 100 or board.seenPositions[board.state_stack[-1].zobrist] >= 2:
        return 0

    #Looks if the transposition table entry gives any helpful info
    if board.state_stack[-1].zobrist in tt.keys():
        ttEntry = tt[board.state_stack[-1].zobrist]
        if ttEntry.valid and ttEntry.depth >= depth:
            #Decreases mate scores by one centipawn for each move until mate (prioritizes mate in fewer moves)
            if ttEntry.value >= 99000:
                trueValue = ttEntry.value - 1
            else:
                trueValue = ttEntry.value

            if ttEntry.flag == "EXACT":
                return trueValue
            elif ttEntry.flag == "LOWERBOUND":
                alpha = max(alpha, trueValue)
            elif ttEntry.flag == "UPPERBOUND":
                beta = min(beta, trueValue)

            if alpha >= beta:
                return ttEntry.value

    #If depth is 0, search for tactical capture sequences and evaluate the position
    if depth == 0:
        return quiesce(board, alpha, beta, tt)
    
    moves = board.getMoves()

    #If in checkmate or stalemate, return the correct value
    if not moves:
        if board.inCheck():
            return -100000
        return 0
    
    value = -1000000
    orderedMoves = sortMoves(board, moves, tt)
    for move in orderedMoves:
        #Searches next move with one less depth
        board.makeMove(move)
        invScore = negaMax(board, -beta, -alpha, depth - 1, tt, endTime)

        #If the return value is None, we have ran out of time and must return the best move for the deepest depth we have calculates so far
        if invScore == None:
            board.unmakeMove(move)
            return None

        score = -1 * invScore
        
        #Decreases mate scores by one centipawn for each move until mate (prioritizes mate in fewer moves)
        if score >= 99000:
            score -= 1

        board.unmakeMove(move)

        #Updates alpha
        if score > value:
            value = score
            if score > alpha:
                alpha = score
        
        #Prunes if appropriate
        if score >= beta:
            break
    
    #Stores transposition table value
    ttEntry = TTEntry()
    ttEntry.value = value
    if value <= alphaOrig:
        ttEntry.flag = "UPPERBOUND"
    elif value >= beta:
        ttEntry.flag = "LOWERBOUND"
    else:
        ttEntry.flag = "EXACT"
    ttEntry.depth = depth
    ttEntry.valid = True
    tt[board.state_stack[-1].zobrist] = ttEntry

    return value

#Root of negamax to also get the best move
#Uses iterative deepening for better move ordering
def rootNegaMax(board, depth, tt, startTime, timeLeft, increment, verbose):
    #Makes move from opening book if still in book moves
    if board.inOpening:
        currentFEN = board.getFEN()
        if currentFEN in board.openingBook:
            if verbose:
                print("Eval: book")
                print("Best depth: book")
            randomMove = random.random()
            for move in board.openingBook[currentFEN]:
                randomMove -= move[0]
                if randomMove <= 0:
                    return strToMove(board, move[1])
            return ((board.openingBook[currentFEN])[0])[1]
        else:
            board.inOpening = False

    if depth < 1:
        print("Depth too low, could not search for any moves")
        return None

    #Calculates how much time it can spend on this move
    endTime = startTime + max((timeLeft / 20 + increment / 2), timeLeft / 40)
                                
    #Calculates if the game is over, returns appropriate value
    bestMove = None
    moves = board.getMoves()
    if not moves:
        if board.inCheck():
            return -100000
        return 0
    if board.state_stack[-1].lastIrreversible == 100 or board.seenPositions[board.state_stack[-1].zobrist] >= 3:
        return 0
    
    #oldBest keeps track of the best move from the previous depth to return if we run out of time
    oldBest = None
    #bestDepth keeps track of the best depth we could achieve before time ran out
    bestDepth = 0
    oldValue = -1000000
    timeOut = False
    for depth in range(1, depth + 1):
        #Makes a move quicker if we found mate
        if oldValue >= 99000:
            break

        #Sets up aspirational window
        if depth >= 4:
            alphaOrig = oldValue - 50
            betaOrig = oldValue + 50
        else:
            alphaOrig = -1000000
            betaOrig = 1000000
        aspirationalRepeat = True

        while aspirationalRepeat == True:
            #Sets values and loops over each move
            alpha = alphaOrig
            beta = betaOrig
            value = -1000000
            orderedMoves = sortMoves(board, moves, tt)
            for move in orderedMoves:
                #Makes and tests each move
                board.makeMove(move)
                invScore = negaMax(board, -beta, -alpha, depth - 1, tt, endTime)

                #If the return value is None, we have ran out of time and must return the best move for the deepest depth we have calculates so far
                if invScore == None:
                    board.unmakeMove(move)
                    timeOut = True
                    break

                score = -1 * invScore
                board.unmakeMove(move)
        
                #Decreases mate scores by one centipawn for each move until mate (prioritizes mate in fewer moves)
                if score >= 99000:
                    score -= 1

                #Updates alpha value (no need to prune since beta will not change)
                if score > value:
                    bestMove = move
                    value = score
                    if score > alpha:
                        alpha = score

            #Breaks if we are out of time
            if timeOut == True:
                break

            #Removes aspirational window if search fails
            if depth >= 4 and value <= alphaOrig:
                alphaOrig = -1000000
                betaOrig = 1000000
            elif depth >= 4 and value >= betaOrig:
                alphaOrig = -1000000
                betaOrig = 1000000
            else:
                aspirationalRepeat = False

        #Breaks if we are out of time
        if timeOut == True:
            break


        bestDepth += 1
        oldBest = bestMove
        oldValue = value

    if verbose:
        if abs(oldValue * board.move) >= 99000:
            print("Eval: Mate in", 100000 - abs(oldValue * board.move))
        else:
            print("Eval:", oldValue * board.move / 100)
        print("Best depth:", bestDepth)
    return oldBest
    
#Uses quiescience to calculate all captures
def quiesce(board, alpha, beta, tt):
    currentEval = eval(board) * board.move
    maxEval = currentEval

    #Checks for pruning
    if maxEval >= beta:
        return maxEval
    if maxEval > alpha:
        alpha = maxEval

    #Searches each capture
    moves = board.getMoves()
    orderedMoves = sortMoves(board, moves, tt)
    for move in orderedMoves:
        if move.isCapture:
            board.makeMove(move)
            score = -quiesce(board, -beta, -alpha, tt)
            board.unmakeMove(move)

            #Prunes and updates values if nescessary
            if score >= beta:
                return score
            if score > maxEval:
                maxEval = score
            if score > alpha:
                alpha = score

    return maxEval

#Basic PeSTO evaluation. Uses piece tables and piece values for middle and end games
def eval(board : ChessBoard):
    #Stores king locations
    whiteKingPos = (-1, -1)
    blackKingPos = (-1, -1)


    #Seperate evals for middle and end game and both players
    middleGameEval = [0, 0]
    endGameEval = [0, 0]

    #Quantifies how close to the end game the board is
    gamePhase = 0

    #Stores whether there are any pawns on the board
    whiteHasPawns = False
    blackHasPawns = False

    #Stores pieces each side has
    whitePieces = {}
    blackPieces = {}

    #Gets the columns each side has pawns in (used to determine doubled pawns)
    whitePawns = []
    blackPawns = []

    #Loops over each piece and updates the values
    rowIndex = 0
    for row in board.myState:
        columnIndex = 0
        for piece in row:
            if piece != 0:
                if piece == 1:
                    #Checks for doubled pawns
                    if columnIndex in whitePawns:
                        middleGameEval[0] -= (2 * board.mg_pesto_table[piece - 1][rowIndex][columnIndex] + board.mg_value[piece - 1]) // 5
                        endGameEval[0] -= (2 * board.eg_pesto_table[piece - 1][rowIndex][columnIndex] + board.eg_value[piece - 1]) // 5
                    else:
                        whitePawns.append(columnIndex)

                    whiteHasPawns = True
                
                if piece == -1:
                    #Checks for doubled pawns
                    if columnIndex in blackPawns:
                        middleGameEval[1] -= (2 * board.mg_pesto_table[-piece - 1][7 - rowIndex][columnIndex] + board.mg_value[-piece - 1]) // 5
                        endGameEval[1] -= (2 * board.eg_pesto_table[-piece - 1][7 - rowIndex][columnIndex] + board.eg_value[-piece - 1]) // 5
                    else:
                        blackPawns.append(columnIndex)

                    blackHasPawns = True

                if piece == 6:
                    whiteKingPos = (rowIndex, columnIndex)
                
                if piece == -6:
                    blackKingPos = (rowIndex, columnIndex)

                if piece > 0:
                    middleGameEval[0] += board.mg_pesto_table[piece - 1][rowIndex][columnIndex] + board.mg_value[piece - 1]
                    endGameEval[0] += board.eg_pesto_table[piece - 1][rowIndex][columnIndex] + board.eg_value[piece - 1]
                    whitePieces[piece] = whitePieces.get(piece, 0) + 1

                elif piece < 0:
                    middleGameEval[1] += board.mg_pesto_table[-piece - 1][7 - rowIndex][columnIndex] + board.mg_value[-piece - 1]
                    endGameEval[1] += board.eg_pesto_table[-piece - 1][7 - rowIndex][columnIndex] + board.eg_value[-piece - 1]
                    blackPieces[-piece] = blackPieces.get(-piece, 0) + 1

                gamePhase += board.gamephaseInc[abs(piece) - 1]
            columnIndex += 1
        rowIndex += 1

    evalAdjustments = 0

    #Looks for known endgames  without pawns
    if whiteHasPawns == False and blackHasPawns == False:
        #Counts how many pieces each side has
        whitePiecesSum = -1
        blackPiecesSum = -1
        for piece in whitePieces:
            whitePiecesSum += whitePieces[piece]
        for piece in blackPieces:
            blackPiecesSum += blackPieces[piece]

        #Checks for known drawn endgames (if there are rooks queens or pawns on the board, not certain draw)
        if 5 not in whitePieces and 2 not in whitePieces and 5 not in blackPieces and 2 not in blackPieces:

            #Both sides have at most king + minor piece
            #In some cases this can be a win, but that would be found by the search before evaluation
            if whitePiecesSum <= 1 and blackPiecesSum <= 2:
                    return 0
            
            #King vs two knights
            if whitePiecesSum == 0 and blackPiecesSum == 2 and 4 not in blackPieces:
                return 0
            if blackPiecesSum == 0 and whitePiecesSum == 2 and 4 not in whitePieces:
                return 0
            
            #Two minors vs one is a draw unless it is two bishops vs one knight
            if whitePiecesSum == 2 and blackPiecesSum == 1:
                if whitePieces.get(4, 0) == 2:
                    if blackPieces.get(4, 0) == 1:
                        return 0
                else:
                    return 0
            if blackPiecesSum == 2 and whitePiecesSum == 1:
                if blackPieces.get(4, 0) == 2:
                    if whitePieces.get(4, 0) == 1:
                        return 0
                else:
                    return 0
                
        #Mop-up eval (looks to bring enemy king to edge and king to enemy king if in completely winning endgame)
        if whitePiecesSum == 0 and (endGameEval[1] - endGameEval[0]) >= 400:
            whiteKingCenterDist = abs(whiteKingPos[0] - 3.5) + abs(whiteKingPos[1] - 3.5) - 1
            kingDist = abs(whiteKingPos[0] - blackKingPos[0]) + abs(whiteKingPos[1] - blackKingPos[1])
            evalAdjustments -= 50 * whiteKingCenterDist + 2 * (140 - kingDist)
        if blackPiecesSum == 0 and (endGameEval[0] - endGameEval[1]) >= 400:
            blackKingCenterDist = abs(blackKingPos[0] - 3.5) + abs(blackKingPos[1] - 3.5) - 1
            kingDist = abs(whiteKingPos[0] - blackKingPos[0]) + abs(whiteKingPos[1] - blackKingPos[1])
            evalAdjustments += 50 * blackKingCenterDist + 2 * (140 - kingDist)


    #Finishes calculations
    mgScore = middleGameEval[0] - middleGameEval[1]
    egScore = endGameEval[0] - endGameEval[1]
    mgPhase = gamePhase
    if mgPhase > 24:
        mgPhase = 24
    egPhase = 24 - mgPhase
    return (mgScore * mgPhase + egScore * egPhase) // 24 + evalAdjustments


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

#Transposition table entry
class TTEntry:
    def __init__(self):
        #Starts as invalid if values are not set appropriately
        self.valid = False

        #Value is the evaluation of the position
        self.value = 0

        #Flags inclue exact, lowerbound, and upperbound
        self.flag = "EXACT"

        #Depth is the depth that the value was gotten
        self.depth = -1

#Converts coordinates to a chess square
def intsToSquare(row, column):
    return ["a", "b", "c", "d", "e", "f", "g", "h"][column] + str(row + 1)

#Zobrist Hashing
#Seed is an array of 781 randomly generated 64-bit ints
def ZobristHash(boardState, move, castlingRights, passantColumn, seed: list[int]):
    retVal = 0
    seedIndex = 0

    #Loops through each square and xors in the corresponding value if a piece is there
    for row in boardState:
        for piece in row:
            if piece != 0:
                if piece > 0:
                    piece -= 1
                retVal = retVal ^ seed[seedIndex + piece + 6]
            seedIndex += 12

    #xors in a value if it is black's move
    if move == -1:
        retVal = retVal ^ seed[seedIndex]
    seedIndex += 1

    #xors in a value for each of the 4 castling rights
    for right in castlingRights:
        if right:
            retVal = retVal ^ seed[seedIndex]
        seedIndex += 1
    
    #xors in a value for whether en passant is possible
    if passantColumn != -1:
        retVal = retVal ^ seed[seedIndex + passantColumn]
    
    return retVal

#Creates and returns a list of 781 random 64-bit ints
def ZobristInit():
    random.seed(1234)
    seed = []
    max = (2 ** 64) - 1
    for _ in range(781):
        seed.append(random.randint(0, max))
    random.seed()
    return seed

#Orders a list of moves according to MVV-LVA (most valuable victim - least valuable aggressor), returns ordered list
def mvv_lva(board, moves):
    def key(move):
        if move.isCapture:
            victim = 0
            if (not move.isPromotion) and move.sp2:
                victim = 1
            else:
                victim = abs(board.myState[move.toSq[0]][move.toSq[1]])
            victimVal = [0, 1, 4, 2, 3, 5, 6][victim]
            aggressor = abs(board.myState[move.fromSq[0]][move.fromSq[1]])
            aggressorVal = [0, 1, 4, 2, 3, 5, 6][aggressor]
            return 10 * victimVal + aggressorVal
        return 0

    new_moves = sorted(moves, key=key, reverse=True)
    return new_moves

#Sorts the moves by transposition table value first, then by MMV-LVA
def sortMoves(board, moves, tt):
    ttMoves = []
    otherMoves = []
    for move in moves:
        board.makeMove(move)
        if board.state_stack[-1].zobrist in tt.keys():
            ttMoves.append((tt[board.state_stack[-1].zobrist].value, move))
        else:
            otherMoves.append(move)
        board.unmakeMove(move)
    
    ttMoves.sort(key = lambda x: x[0])
    otherSorted = mvv_lva(board, otherMoves)

    sortedMoves = []
    for move in ttMoves:
        sortedMoves.append(move[1])
    for move in otherSorted:
        sortedMoves.append(move)

    return sortedMoves

#Turns a move object into long algebraic format i.e. e2e4, a7a8q
def moveToStr(move : Move):
    promPiece = ""
    if move.isPromotion:
        if move.sp1:
            if move.sp2:
                promPiece = "q"
            else:
                promPiece = "r"
        else:
            if move.sp2:
                promPiece = "b"
            else:
                promPiece = "n"
    
    fromSq = intsToSquare(move.fromSq[0], move.fromSq[1])
    toSq = intsToSquare(move.toSq[0], move.toSq[1])
    return fromSq + toSq + promPiece

#Turns a move in long algebraic format to a move object (needs a board object to get captures/special info)
def strToMove(board : ChessBoard, moveStr):
    for move in board.getMoves():
        if moveToStr(move) == moveStr:
            return move
    return None

def playChess(totalTime = 60, increment = 0.5, whitecomputer = True, blackcomputer = True, maxDepth = 100):
    #Basic pygame setup, setting the screen and loading the images
    
    pygame.init()
    screen = pygame.display.set_mode((512, 512))
    running = True
    pngs = [
        pygame.image.load('images/black_king_64x64.png'),
        pygame.image.load('images/black_queen_64x64.png'),
        pygame.image.load('images/black_bishop_64x64.png'),
        pygame.image.load('images/black_knight_64x64.png'),
        pygame.image.load('images/black_rook_64x64.png'),
        pygame.image.load('images/black_pawn_64x64.png'),
        pygame.image.load('images/board.png'),
        pygame.image.load('images/white_pawn_64x64.png'),
        pygame.image.load('images/white_rook_64x64.png'),
        pygame.image.load('images/white_knight_64x64.png'),
        pygame.image.load('images/white_bishop_64x64.png'),
        pygame.image.load('images/white_queen_64x64.png'),
        pygame.image.load('images/white_king_64x64.png')]

    whitePromotionBoard = ChessBoard()
    blackPromotionBoard = ChessBoard()
    whitePromotionBoard.myState = [[0] * 8, [0] * 8, [0] * 8, [0, 0, 0, 2, 4, 0, 0, 0], [0, 0, 0, 5, 3, 0, 0, 0], [0] * 8, [0] * 8, [0] * 8]
    blackPromotionBoard.myState = [[0] * 8, [0] * 8, [0] * 8, [0, 0, 0, -2, -4, 0, 0, 0], [0, 0, 0, -5, -3, 0, 0, 0], [0] * 8, [0] * 8, [0] * 8]

    board = ChessBoard()

    moves = []
    turn = 1
    whiteTime = totalTime
    blackTime = totalTime

    tt = {}

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        board.render(pngs, screen)

        whitemoves = board.getMoves()
        moveStartTime = time.time()

        #Checks for timeout
        if blackTime <= 0:
            print("Black ran out of time! White wins!")
            break

        #Checks for checkmate and stalemate
        if not whitemoves:
            if board.inCheck():
                print("Checkmate! Black wins!")
            else:
                print("Draw by stalemate! No legal moves available!")
            break

        #Checks for 50-move rule and threefold repition
        if board.state_stack[-1].lastIrreversible == 100:
            print("Draw by 50-move rule!")
            break
        if board.seenPositions[board.state_stack[-1].zobrist] >= 3:
            print("Draw by threefold repetition!")
            break

        #Gets player input to make a move
        if not whitecomputer:
            while board.move == 1:
                board.render(pngs, screen)
                fromSq = (-1, -1)
                toSq = (-1, -1)

                #Looks for the first click and gets the square
                while fromSq == (-1, -1):
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            running = False
                        
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            fromSq = (7 - (event.pos[1] // 64), event.pos[0] // 64)

                #Looks for the second click and gets the square
                while toSq == (-1, -1):
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            running = False
                        
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            toSq = (7 - (event.pos[1] // 64), event.pos[0] // 64)

                #Loops over each legal move and checks if it is the move selected
                promotionPiece = 0
                for move in whitemoves:
                    if (move.fromSq == fromSq) and (move.toSq == toSq):
                        #Non promotions can be defined by the from and to squares
                        if not move.isPromotion:
                            moveTime = time.time() - moveStartTime
                            whiteTime = whiteTime - moveTime + increment
                            print(f"Time left for white: {whiteTime:.2f}")
                            moves.append(move)
                            board.makeMove(move)
                            
                        
                        #Promotions need to do more work
                        else:
                            #promotionpiece is the piece the user is promoting to. If it is 0, we need to prompt the user to pick a piece
                            if promotionPiece == 0:
                                whitePromotionBoard.render(pngs, screen)
                                promotionclick = False
                                while not promotionclick:
                                    for event in pygame.event.get():
                                        if event.type == pygame.QUIT:
                                            running = False
                                        
                                        if event.type == pygame.MOUSEBUTTONDOWN:
                                            promotionPiece = whitePromotionBoard.myState[7 - (event.pos[1] // 64)][event.pos[0] // 64]
                                            promotionclick = True

                            #Gets the piece the move is promoting to
                            if move.sp1:
                                if move.sp2:
                                    movePiece = 5 * board.move
                                else:
                                    movePiece = 2 * board.move
                            else:
                                if move.sp2:
                                    movePiece = 4 * board.move
                                else:
                                    movePiece = 3 * board.move
                            
                            #If the move is the correct promotion, make the move
                            if promotionPiece == movePiece:
                                moveTime = time.time() - moveStartTime
                                whiteTime = whiteTime - moveTime + increment
                                print(f"Time left for white: {whiteTime:.2f}")
                                moves.append(move)
                                board.makeMove(move)
        
        #Gets the engine's move
        else:
            board.render(pngs, screen)
            startTime = time.time()
            bestMove = rootNegaMax(board, maxDepth, tt, startTime, whiteTime, increment, True)
            moveTime = time.time() - moveStartTime
            whiteTime = whiteTime - moveTime + increment
            print(f"Time left for white: {whiteTime:.2f}")
            moves.append(bestMove)
            board.makeMove(bestMove)

        board.render(pngs, screen)

        blackmoves = board.getMoves()
        moveStartTime = time.time()

        #Checks for timeout
        if whiteTime <= 0:
            print("White ran out of time! Black wins!")
            break

        #Checks for checkmate and stalemate
        if not blackmoves:
            if board.inCheck():
                print("Checkmate! White wins!")
            else:
                print("Draw by stalemate! No legal moves available!")
            break

        #Checks for 50-move rule and threefold repition
        if board.state_stack[-1].lastIrreversible == 100:
            print("Draw by 50-move rule!")
            break
        if board.seenPositions[board.state_stack[-1].zobrist] >= 3:
            print("Draw by threefold repetition!")
            break

        #Gets player input to make a move
        if not blackcomputer:
            while board.move == -1:
                board.render(pngs, screen)
                fromSq = (-1, -1)
                toSq = (-1, -1)

                #Looks for the first click and gets the square
                while fromSq == (-1, -1):
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            running = False
                        
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            fromSq = (7 - (event.pos[1] // 64), event.pos[0] // 64)

                #Looks for the second click and gets the square
                while toSq == (-1, -1):
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            running = False
                        
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            toSq = (7 - (event.pos[1] // 64), event.pos[0] // 64)

                #Loops over each legal move and checks if it is the move selected
                promotionPiece = 0
                for move in blackmoves:
                    if (move.fromSq == fromSq) and (move.toSq == toSq):
                        #Non promotions can be defined by the from and to squares
                        if not move.isPromotion:
                            moveTime = time.time() - moveStartTime
                            blackTime = blackTime - moveTime + increment
                            print(f"Time left for black: {blackTime:.2f}")
                            moves.append(move)
                            board.makeMove(move)
                        
                        #Promotions need to do more work
                        else:
                            #promotionpiece is the piece the user is promoting to. If it is 0, we need to prompt the user to pick a piece
                            if promotionPiece == 0:
                                blackPromotionBoard.render(pngs, screen)
                                promotionclick = False
                                while not promotionclick:
                                    for event in pygame.event.get():
                                        if event.type == pygame.QUIT:
                                            running = False
                                        
                                        if event.type == pygame.MOUSEBUTTONDOWN:
                                            promotionPiece = blackPromotionBoard.myState[7 - (event.pos[1] // 64)][event.pos[0] // 64]
                                            promotionclick = True

                            #Gets the piece the move is promoting to
                            if move.sp1:
                                if move.sp2:
                                    movePiece = 5 * board.move
                                else:
                                    movePiece = 2 * board.move
                            else:
                                if move.sp2:
                                    movePiece = 4 * board.move
                                else:
                                    movePiece = 3 * board.move
                            
                            #If the move is the correct promotion, make the move
                            if promotionPiece == movePiece:
                                moveTime = time.time() - moveStartTime
                                blackTime = blackTime - moveTime + increment
                                print(f"Time left for black: {blackTime:.2f}")
                                moves.append(move)
                                board.makeMove(move)
        
        #Gets the engine's move
        else:
            startTime = time.time()
            bestMove = rootNegaMax(board, maxDepth, tt, startTime, blackTime, increment, True)
            moveTime = time.time() - moveStartTime
            blackTime = blackTime - moveTime + increment
            print(f"Time left for black: {blackTime:.2f}")
            moves.append(bestMove)
            board.makeMove(bestMove)

    moveList = ""
    for move in moves:
        moveList += intsToSquare(move.fromSq[0], move.fromSq[1]) + intsToSquare(move.toSq[0], move.toSq[1]) + ", "
    print(moveList)
    return moveList

def GameTest(bot1, bot2, totalTime, increment, maxDepth = 100, openings = None):
    board = ChessBoard()
    pygame.init()
    screen = pygame.display.set_mode((512, 512))
    running = True
    pngs = [
        pygame.image.load('images/black_king_64x64.png'),
        pygame.image.load('images/black_queen_64x64.png'),
        pygame.image.load('images/black_bishop_64x64.png'),
        pygame.image.load('images/black_knight_64x64.png'),
        pygame.image.load('images/black_rook_64x64.png'),
        pygame.image.load('images/black_pawn_64x64.png'),
        pygame.image.load('images/board.png'),
        pygame.image.load('images/white_pawn_64x64.png'),
        pygame.image.load('images/white_rook_64x64.png'),
        pygame.image.load('images/white_knight_64x64.png'),
        pygame.image.load('images/white_bishop_64x64.png'),
        pygame.image.load('images/white_queen_64x64.png'),
        pygame.image.load('images/white_king_64x64.png')]

    moves = []
    whiteTime = totalTime
    blackTime = totalTime

    whiteTt = {}
    blackTt = {}

    if not openings == None:
        opening  = random.choice(openings)
        board.loadFEN(opening)
        print("FEN:", opening)

    while running:
        whitemoves = board.getMoves()
        moveStartTime = time.time()

        #Checks for timeout
        if blackTime <= 0:
            print("Black ran out of time! White wins!")
            return 1

        #Checks for checkmate and stalemate
        if not whitemoves:
            if board.inCheck():
                print("Checkmate! Black wins!")
                return -1
            else:
                print("Draw by stalemate! No legal moves available!")
                return 0

        #Checks for 50-move rule and threefold repition
        if board.state_stack[-1].lastIrreversible == 100:
            print("Draw by 50-move rule!")
            return 0
        if board.seenPositions[board.state_stack[-1].zobrist] >= 3:
            print("Draw by threefold repetition!")
            return 0

        board.render(pngs, screen)
        startTime = time.time()
        bestMove = bot1(board, maxDepth, whiteTt, startTime, whiteTime, increment, True)
        moveTime = time.time() - moveStartTime
        whiteTime = whiteTime - moveTime + increment
        print("Move:", moveToStr(bestMove))
        print("FEN:", board.getFEN())
        print(f"Time left for white: {whiteTime:.2f}")
        moves.append(bestMove)
        board.makeMove(bestMove)

        blackmoves = board.getMoves()
        moveStartTime = time.time()

        #Checks for timeout
        if whiteTime <= 0:
            print("White ran out of time! Black wins!")
            return -1

        #Checks for checkmate and stalemate
        if not blackmoves:
            if board.inCheck():
                print("Checkmate! White wins!")
                return 1
            else:
                print("Draw by stalemate! No legal moves available!")
                return 0

        #Checks for 50-move rule and threefold repition
        if board.state_stack[-1].lastIrreversible == 100:
            print("Draw by 50-move rule!")
            return 0
        if board.seenPositions[board.state_stack[-1].zobrist] >= 3:
            print("Draw by threefold repetition!")
            return 0

        board.render(pngs, screen)
        startTime = time.time()
        bestMove = bot2(board, maxDepth, blackTt, startTime, blackTime, increment, True)
        moveTime = time.time() - moveStartTime
        blackTime = blackTime - moveTime + increment
        print("Move:", moveToStr(bestMove))
        print(f"Time left for black: {blackTime:.2f}")
        moves.append(bestMove)
        board.makeMove(bestMove)


if __name__ == "__main__":
    playChess(180, 1, False, True)