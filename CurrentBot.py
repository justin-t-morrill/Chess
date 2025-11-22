#Features added:
#Negamax w alpha beta
#PeSTO tables
#Quiescience search
#Transposition tables
#Hash move/MVVLVA ordering
#Iterative deepening
#Opening book
#Aspiration windows
#Known drawn endgames
#Doubled pawn evaluation
#Killer moves
#King safety (did not see real improvement, parameters still must be tuned)

#Features tested (with no real improvement)
#PV extensions
#Check extensions

#Features to implement
#More pawn evaluation (passed, isolated)
#LMR


from ChessBoard import ChessBoard
from HelperFunctions import *
from Move import Move
from State import State
from TTEntry import TTEntry
import time, math
import OpeningBookDeep

#Defines which opening book to use
myBook = OpeningBookDeep.myBook

#Uses negamax to get the eval
def negaMax(board : ChessBoard, alpha : int, beta : int, depth : float, tt : list[TTEntry], endTime : float, killerMoves : dict[int, list[Move]]):
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
    if depth <= 0:
        return quiesce(board, alpha, beta, tt)
    
    moves = board.getMoves()

    #If in checkmate or stalemate, return the correct value
    if not moves:
        if board.inCheck():
            return -100000
        return 0
    
    value = -1000000
    orderedMoves = sortMoves(board, moves, tt, killerMoves.get(depth, None))
    bestMove = None
    moveIndex = 0
    for move in orderedMoves:
        #Searches next move with one less depth
        board.makeMove(move)
        if moveIndex < 2 or depth < 3:
            invScore = negaMax(board, -beta, -alpha, depth - 1, tt, endTime, killerMoves)
        
        #LMR (Late Move Reduction) searches later moves at lower depth
        else:
            reduction = int(0.3 + 0.7 * math.log(depth) + 0.5 * math.log(moveIndex))
            invScore = negaMax(board, -beta, -alpha, depth - 1 - reduction, tt, endTime, killerMoves)

            #If it fails high, we still fully search
            if invScore != None and -1 * invScore >= beta:
                invScore = negaMax(board, -beta, -alpha, depth - 1, tt, endTime, killerMoves)


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
            bestMove = move
            value = score
            if score > alpha:
                alpha = score
        
        #Prunes if appropriate
        if score >= beta:

            #Adds move to killer moves if it is quiet
            if (not bestMove.isCapture) and (not bestMove.isPromotion):
                if depth not in killerMoves.keys():
                    killerMoves[depth] = [None, bestMove]
                elif bestMove not in killerMoves[depth]:
                    killerMoves[depth] = [killerMoves[depth][1], bestMove]

            break

        moveIndex += 1
    
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
    ttEntry.hashMove = bestMove
    tt[board.state_stack[-1].zobrist] = ttEntry

    return value

#Root of negamax to also get the best move
#Uses iterative deepening for better move ordering
def rootNegaMax(board, depth, tt, startTime, timeLeft, increment, verbose):
    #Makes move from opening book if still in book moves
    if board.inOpening or True:
        currentFEN = board.getFEN()
        if currentFEN in myBook:
            if verbose:
                print("Eval: book")
                print("Best depth: book")
            randomMove = random.choice(myBook[currentFEN])
            return strToMove(board, randomMove)
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
    moves = board.getMoves()
    if not moves:
        if board.inCheck():
            return -100000
        return 0
    if board.state_stack[-1].lastIrreversible == 100 or board.seenPositions[board.state_stack[-1].zobrist] >= 3:
        return 0
    
    killerMoves = {}
    oldBest = None
    #bestDepth keeps track of the best depth we could achieve before time ran out
    bestMove = None
    bestVal = -1000000
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
            pv_move = oldBest
            other_moves = moves.copy()
            if pv_move != None:
                other_moves.remove(pv_move)
            orderedMoves = mvv_lva(board, other_moves)
            if pv_move != None:
                orderedMoves.insert(0, pv_move)

            movesChecked = 0

            for move in orderedMoves:
                #Makes and tests each move
                board.makeMove(move)
                invScore = negaMax(board, -beta, -alpha, depth - 1, tt, endTime, killerMoves)

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
                    bestVal = score
                    if score > alpha:
                        alpha = score

                movesChecked += 1

            #Removes aspirational window if search fails
            if depth >= 4 and value <= alphaOrig:
                alphaOrig = -1000000
                betaOrig = 1000000
                bestMove = oldBest
            elif depth >= 4 and value >= betaOrig:
                alphaOrig = -1000000
                betaOrig = 1000000
                bestMove = oldBest
            else:
                aspirationalRepeat = False

            #Breaks if we are out of time
            if timeOut == True:
                break

        #Breaks if we are out of time
        if timeOut == True:
            break


        bestDepth += 1
        oldValue = value
        oldBest = bestMove

    if verbose:
        if abs(bestVal * board.move) >= 99000:
            print("Eval: Mate in", 100000 - abs(bestVal * board.move))
        else:
            print("Eval:", bestVal * board.move / 100)
            print("Best depth:", bestDepth)
        if oldBest != bestMove:
            print("Better move found with search!")
            print("\"Better\" move:", moveToStr(bestMove), "Old move:", moveToStr(oldBest))
            print("Old Line: " + printLine(board, oldBest, tt, 15))
        print("Extra moves searched:", movesChecked)

        print("Line: " + printLine(board, bestMove, tt, 15))

    return bestMove
    
#Uses quiescience to calculate all captures
def quiesce(board : ChessBoard, alpha : int, beta : int, tt : list[TTEntry]):
    #Looks if in check
    inCheck = board.inCheck()

    #Gets the current eval if not in check. If in check, postion could be bad, so set minimum current eval
    if inCheck:
        currentEval = -1000000
    else:
        currentEval = eval(board) * board.move

    maxEval = currentEval

    #Checks for pruning
    if maxEval >= beta:
        return maxEval
    if maxEval > alpha:
        alpha = maxEval

    #Checks for checkmate or stalemate
    moves = board.getMoves()
    if not moves:
        if board.inCheck():
            return -100000
        return 0
    
    #Searches each capture or each legal move if in check
    orderedMoves = sortMoves(board, moves, tt, None)
    for move in orderedMoves:
        if move.isCapture or inCheck:
            board.makeMove(move)
            score = -quiesce(board, -beta, -alpha, tt)
            board.unmakeMove(move)

            #Decreases mate scores by one centipawn for each move until mate (prioritizes mate in fewer moves)
            if score >= 99000:
                score -= 1

            #Prunes and updates values if nescessary
            if score >= beta:
                return score
            if score > maxEval:
                maxEval = score
            if score > alpha:
                alpha = score

    return maxEval


#Basic PeSTO evaluation. Uses piece tables and piece values for middle and end games
def eval(board : ChessBoard, moves = None):
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
                if piece == 1: #White pawn
                    #Checks for doubled pawns
                    if columnIndex in whitePawns:
                        middleGameEval[0] -= (2 * board.mg_pesto_table[piece - 1][rowIndex][columnIndex] + board.mg_value[piece - 1]) // 5
                        endGameEval[0] -= (2 * board.eg_pesto_table[piece - 1][rowIndex][columnIndex] + board.eg_value[piece - 1]) // 5
                    else:
                        whitePawns.append(columnIndex)

                    whiteHasPawns = True
                
                if piece == -1: #Black pawn
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
                    #Adds piece value and square value
                    middleGameEval[0] += board.mg_pesto_table[piece - 1][rowIndex][columnIndex] + board.mg_value[piece - 1]
                    endGameEval[0] += board.eg_pesto_table[piece - 1][rowIndex][columnIndex] + board.eg_value[piece - 1]
                    whitePieces[piece] = whitePieces.get(piece, 0) + 1

                elif piece < 0:
                    #Adds piece value and square value
                    middleGameEval[1] += board.mg_pesto_table[-piece - 1][7 - rowIndex][columnIndex] + board.mg_value[-piece - 1]
                    endGameEval[1] += board.eg_pesto_table[-piece - 1][7 - rowIndex][columnIndex] + board.eg_value[-piece - 1]
                    blackPieces[-piece] = blackPieces.get(-piece, 0) + 1

                gamePhase += board.gamephaseInc[abs(piece) - 1]
            columnIndex += 1
        rowIndex += 1

    evalAdjustments = 0

    #If castled, looks for pawn shield protecting the king
    if whiteKingPos[1] > 4:
        middleGameEval[0] -= 25
        if board.myState[1][5] == 1:
            middleGameEval[0] += 10
        elif board.myState[2][5] == 1:
            middleGameEval[0] += 5
        elif 5 not in whitePawns:
            middleGameEval[0] -= 10
            
        if board.myState[1][6] == 1:
            middleGameEval[0] += 10
        elif board.myState[2][6] == 1:
            middleGameEval[0] += 5
        elif 6 not in whitePawns:
            middleGameEval[0] -= 10
            
        if board.myState[1][7] == 1:
            middleGameEval[0] += 10
        elif board.myState[2][7] == 1:
            middleGameEval[0] += 5
        elif 7 not in whitePawns:
            middleGameEval[0] -= 10

    elif whiteKingPos[1] < 3:
        middleGameEval[0] -= 25
        if board.myState[1][0] == 1:
            middleGameEval[0] += 10
        elif board.myState[2][0] == 1:
            middleGameEval[0] += 5
        elif 0 not in whitePawns:
            middleGameEval[0] -= 10
            
        if board.myState[1][1] == 1:
            middleGameEval[0] += 10
        elif board.myState[2][1] == 1:
            middleGameEval[0] += 5
        elif 1 not in whitePawns:
            middleGameEval[0] -= 10
            
        if board.myState[1][2] == 1:
            middleGameEval[0] += 10
        elif board.myState[2][2] == 1:
            middleGameEval[0] += 5
        elif 2 not in whitePawns:
            middleGameEval[0] -= 10

    if blackKingPos[1] > 4:
        middleGameEval[1] -= 25
        if board.myState[6][5] == -1:
            middleGameEval[1] += 10
        elif board.myState[5][5] == -1:
            middleGameEval[1] += 5
        elif 5 not in blackPawns:
            middleGameEval[1] -= 10
            
        if board.myState[6][6] == -1:
            middleGameEval[1] += 10
        elif board.myState[5][6] == -1:
            middleGameEval[1] += 5
        elif 6 not in blackPawns:
            middleGameEval[1] -= 10
            
        if board.myState[6][7] == -1:
            middleGameEval[1] += 10
        elif board.myState[5][7] == -1:
            middleGameEval[1] += 5
        elif 7 not in blackPawns:
            middleGameEval[1] -= 10

    elif blackKingPos[1] < 3:
        middleGameEval[1] -= 25
        if board.myState[6][0] == -1:
            middleGameEval[1] += 10
        elif board.myState[5][0] == -1:
            middleGameEval[1] += 5
        elif 0 not in blackPawns:
            middleGameEval[1] -= 10
            
        if board.myState[6][1] == -1:
            middleGameEval[1] += 10
        elif board.myState[5][1] == -1:
            middleGameEval[1] += 5
        elif 1 not in blackPawns:
            middleGameEval[1] -= 10
            
        if board.myState[6][2] == -1:
            middleGameEval[1] += 10
        elif board.myState[5][2] == -1:
            middleGameEval[1] += 5
        elif 2 not in blackPawns:
            middleGameEval[1] -= 10
        
    #Calculates king tropism
    # tropVals = [0, 0]
    # tropWeights = [0, 1, 1, 1, 2, 0]
    # rowIndex = 0
    # for row in board.myState:
    #     columnIndex = 0
    #     for piece in row:
    #         if piece < 0:
    #             dist = max(abs(rowIndex-whiteKingPos[0]), abs(columnIndex-whiteKingPos[1]))
    #             s = max(0, 7 - dist)
    #             tropVals[0] -= s * tropWeights[piece]

    #         elif piece > 0:
    #             dist = max(abs(rowIndex-blackKingPos[0]), abs(columnIndex-blackKingPos[1]))
    #             s = max(0, 7 - dist)
    #             tropVals[0] -= s * tropWeights[-piece]

    #         columnIndex += 1
    #     rowIndex += 1
    # tropVals[0] = min(40, tropVals[0]) * 2
    # tropVals[1] = min(40, tropVals[1]) * 2

    # middleGameEval[0] -= tropVals[0]
    # middleGameEval[1] -= tropVals[1]
    # endGameEval[0] -= int(0.2 * tropVals[0])
    # endGameEval[1] -= int(0.2 * tropVals[1])

    #Looks for known endgames without pawns
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
                if 4 in whitePieces.keys() and whitePieces[4] == 2:
                    if 4 in blackPieces.keys() and blackPieces[4] == 1:
                        return 0
                else:
                    return 0
            if blackPiecesSum == 2 and whitePiecesSum == 1:
                if 4 in blackPieces.keys() and blackPieces[4] == 2:
                    if 4 in whitePieces.keys() and whitePieces[4] == 1:
                        return 0
                else:
                    return 0
                
        #Mop-up eval (looks to bring enemy king to edge and king to enemy king if in completely winning endgame)
        if whitePiecesSum == 0 and (endGameEval[1] - endGameEval[0]) >= 400:
            whiteKingCenterDist = int(abs(whiteKingPos[0] - 3.5) + abs(whiteKingPos[1] - 3.5) - 1)
            kingDist = abs(whiteKingPos[0] - blackKingPos[0]) + abs(whiteKingPos[1] - blackKingPos[1])
            evalAdjustments -= 50 * whiteKingCenterDist + 2 * (140 - kingDist)
        if blackPiecesSum == 0 and (endGameEval[0] - endGameEval[1]) >= 400:
            blackKingCenterDist = int(abs(blackKingPos[0] - 3.5) + abs(blackKingPos[1] - 3.5) - 1)
            kingDist = abs(whiteKingPos[0] - blackKingPos[0]) + abs(whiteKingPos[1] - blackKingPos[1])
            evalAdjustments += 50 * blackKingCenterDist + 2 * (140 - kingDist)

    #Calculates legal moves in the position (for mobility and king safety)
    moveList = [None, None]
    if board.move == 1:
        if moves == None:
            moveList[0] = board.getPseudoLegalMoves(True)
        else:
            moveList[0] = moves
    else:
        if moves == None:
            moveList[1] = board.getPseudoLegalMoves(True)
        else:
            moveList[1] = moves

    board.move *= -1
    if board.move == -1:
        moveList[1] = board.getPseudoLegalMoves(True)
    else:
        moveList[0] = board.getPseudoLegalMoves(True)
    board.move *= -1

    #Calculates mobility
    middleGameEval[0] += 1 * len(moveList[0])
    middleGameEval[1] += 1 * len(moveList[1])
    endGameEval[0] += int(len(moveList[0]) * 0.5)
    endGameEval[1] += int(len(moveList[1]) * 0.5)

    #Calculates king safety (using attacking king zone)
    whiteKingZone = []
    for dist in [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1), (2, -1), (2, 0), (2, 1)]:
        whiteKingZone.append((whiteKingPos[0] + dist[0], whiteKingPos[1] + dist[1]))
    blackKingZone = []
    for dist in [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1), (-2, -1), (-2, 0), (-2, 1)]:
        blackKingZone.append((blackKingPos[0] + dist[0], blackKingPos[1] + dist[1]))
    attackWeights = [0, 0, 50, 75, 88, 94, 97, 99]
    whiteAttackVal = 0
    whiteAttackingPieces = []
    for move in moveList[0]:
        if move.toSq in blackKingZone:
            attackPiece = board.myState[move.fromSq[0]][move.fromSq[1]]
            whiteAttackVal += [0, 0, 40, 20, 20, 80, 0][attackPiece]
            if attackPiece > 1 and attackPiece != 6 and move.fromSq not in whiteAttackingPieces:
                whiteAttackingPieces.append(move.fromSq)
    whiteAttackingPiecesCount = min(7, len(whiteAttackingPieces))
    whiteAttackScore = whiteAttackVal * attackWeights[whiteAttackingPiecesCount]
    blackAttackVal = 0
    blackAttackingPieces = []
    for move in moveList[1]:
        if move.toSq in whiteKingZone:
            attackPiece = -1 * board.myState[move.fromSq[0]][move.fromSq[1]]
            blackAttackVal += [0, 0, 40, 20, 20, 80, 0][attackPiece]
            if attackPiece > 1 and attackPiece != 6 and move.fromSq not in blackAttackingPieces:
                blackAttackingPieces.append(move.fromSq)
    blackAttackingPiecesCount = min(7, len(blackAttackingPieces))
    blackAttackScore = blackAttackVal * attackWeights[blackAttackingPiecesCount]
    const = 0.25
    middleGameEval[0] += int(whiteAttackScore * 0.01 * const)
    middleGameEval[1] += int(blackAttackScore * 0.01 * const)
    endGameEval[0] += int(whiteAttackScore * 0.003 * const)
    endGameEval[1] += int(blackAttackScore * 0.003 * const)

            

    #Finishes calculations
    mgScore = middleGameEval[0] - middleGameEval[1]
    egScore = endGameEval[0] - endGameEval[1]
    mgPhase = gamePhase
    if mgPhase > 24:
        mgPhase = 24
    egPhase = 24 - mgPhase
    return (mgScore * mgPhase + egScore * egPhase) // 24 + evalAdjustments

#Orders a list of moves according to MVV-LVA (most valuable victim - least valuable aggressor), returns ordered list
def mvv_lva(board : ChessBoard, moves : list[Move]):
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

#Sorts the moves by hash move first, then by MVV-LVA
def sortMoves(board : ChessBoard, moves : list[Move], tt : dict[int, TTEntry], killerMovesAtDepth):
    sortedMoves = []
    if board.state_stack[-1].zobrist in tt.keys():
        possibleHashMove = tt[board.state_stack[-1].zobrist].hashMove
        if possibleHashMove in moves:
            sortedMoves.append(possibleHashMove)
            moves.remove(possibleHashMove)

    if killerMovesAtDepth != None:
        for killerMove in killerMovesAtDepth:
            if killerMove != None and killerMove in moves:
                sortedMoves.append(killerMove)
                moves.remove(killerMove)

    sortedMoves.extend(mvv_lva(board, moves))
    return sortedMoves