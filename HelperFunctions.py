import random
from ChessBoard import ChessBoard
from Move import Move
from TTEntry import TTEntry

#Rerturns the hash move from the transposition table recursively to get a string of the engine's expected line
def printLine(board : ChessBoard, move : Move, tt : dict[int, TTEntry], maxDepth : int):
    line = ""

    if move == None or maxDepth <= 0:
        return line
    
    line += moveToStr(move)
    board.makeMove(move)
    if board.state_stack[-1].zobrist not in tt.keys():
        board.unmakeMove(move)
        return line
    
    else:
        nextMove = tt[board.state_stack[-1].zobrist].hashMove
        line += " " + printLine(board, nextMove, tt, maxDepth - 1)
        board.unmakeMove(move)
        return line

#Converts coordinates to a chess square
def intsToSquare(row : int, column : int):
    return ["a", "b", "c", "d", "e", "f", "g", "h"][column] + str(row + 1)

#Turns a move object into long algebraic format i.e. e2e4, a7a8q
def moveToStr(move : Move):
    if move == None:
        return "Null"

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
def strToMove(board : ChessBoard, moveStr : str):
    for move in board.getMoves():
        if moveToStr(move) == moveStr:
            return move
    print("MOVE NOT FOUND:", moveStr)
    return None


    
#Runs the Perft test (prints number of legal moves for a certain depth)
def perft(board : ChessBoard, depth : int, verbose : bool, divide : bool):
    if depth == 0:
        return 1
    total = 0
    #Loops over each move, makes the move, calls Perft with one less depth, then undoes the move
    moves = board.getMoves()
    for move in moves:
        board.makeMove(move)

        #Verbose prints the board state of every state it computes
        if verbose:
            print(board)

        part = board.perft(depth - 1, verbose, False)

        #Divide prints the perft value after each move
        if divide:
            if move.isPromotion:
                promPiece = ".prnbqk"[abs(board.myState[move.toSq[0]][move.toSq[1]])]
            else:
                promPiece = ""
            print(intsToSquare(move.fromSq[0], move.fromSq[1]) + intsToSquare(move.toSq[0], move.toSq[1]) + promPiece + ":", part)
        
        total += part
        board.unmakeMove(move)

    return total