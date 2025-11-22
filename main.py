
import random, time, pygame
from ChessBoard import ChessBoard
from CurrentBot import rootNegaMax
from HelperFunctions import *

def playChess(totalTime = 60, increment = 0.5, whitecomputer = True, blackcomputer = True, maxDepth = 100, whiteInfiniteTime = False, blackInfiniteTime = False):
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
    if not whiteInfiniteTime:
        whiteTime = totalTime
    else:
        whiteTime = 1000000000
    if not blackInfiniteTime:
        blackTime = totalTime
    else:
        blackTime = 1000000000

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
    pgnStr = ''

    sideSwap = random.randint(0, 1)
    if sideSwap == 1:
        whiteBot = bot2
        blackBot = bot1
        sideMult = -1
        print("Sides swapped!")
        pgnStr += '[White "Engine B"]\n'
        pgnStr += '[Black "Engine A"]\n'
    else:
        whiteBot = bot1
        blackBot = bot2
        sideMult = 1
        print("Sides not swapped!")
        pgnStr += '[White "Engine A"]\n'
        pgnStr += '[Black "Engine B"]\n'

    board = ChessBoard()
    if openings != None:
        opening = random.choice(openings)
        board.loadFEN(opening)
        pgnStr += '[FEN "' + opening[:-2] + '"]\n'

    pgnStr += '\n'
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
    turn = 1
    whiteTime = totalTime
    blackTime = totalTime

    whiteTt = {}
    blackTt = {}

    while running:
        whitemoves = board.getMoves()
        moveStartTime = time.time()

        #Checks for timeout
        if blackTime <= 0:
            print("Black ran out of time! White wins!")
            return sideMult, pgnStr

        #Checks for checkmate and stalemate
        if not whitemoves:
            if board.inCheck():
                print("Checkmate! Black wins!")
                return -sideMult, pgnStr
            else:
                print("Draw by stalemate! No legal moves available!")
                return 0, pgnStr

        #Checks for 50-move rule and threefold repition
        if board.state_stack[-1].lastIrreversible == 100:
            print("Draw by 50-move rule!")
            return 0, pgnStr
        if board.seenPositions[board.state_stack[-1].zobrist] >= 3:
            print("Draw by threefold repetition!")
            return 0, pgnStr

        board.render(pngs, screen)
        startTime = time.time()
        print("Start of white's Move")
        print("FEN:", board.getFEN())
        bestMove = whiteBot(board, maxDepth, whiteTt, startTime, whiteTime, increment, True)
        moveTime = time.time() - moveStartTime
        whiteTime = whiteTime - moveTime + increment
        print("Move:", moveToStr(bestMove))
        print(f"Time left for white: {whiteTime:.2f}")
        moves.append(bestMove)
        board.makeMove(bestMove)
        print("End of white's move")
        pgnStr += str(board.moveCounter) + '. '
        pgnStr += moveToStr(bestMove)

        blackmoves = board.getMoves()
        moveStartTime = time.time()

        #Checks for timeout
        if whiteTime <= 0:
            print("White ran out of time! Black wins!")
            return -sideMult, pgnStr

        #Checks for checkmate and stalemate
        if not blackmoves:
            if board.inCheck():
                print("Checkmate! White wins!")
                return sideMult, pgnStr
            else:
                print("Draw by stalemate! No legal moves available!")
                return 0, pgnStr

        #Checks for 50-move rule and threefold repition
        if board.state_stack[-1].lastIrreversible == 100:
            print("Draw by 50-move rule!")
            return 0, pgnStr
        if board.seenPositions[board.state_stack[-1].zobrist] >= 3:
            print("Draw by threefold repetition!")
            return 0, pgnStr

        board.render(pngs, screen)
        startTime = time.time()
        print("Start of black's Move")
        print("FEN:", board.getFEN())
        bestMove = blackBot(board, maxDepth, blackTt, startTime, blackTime, increment, True)
        moveTime = time.time() - moveStartTime
        blackTime = blackTime - moveTime + increment
        print("Move:", moveToStr(bestMove))
        print(f"Time left for black: {blackTime:.2f}")
        moves.append(bestMove)
        board.makeMove(bestMove)
        print("End of black's move")
        pgnStr += ' ' + moveToStr(bestMove) + ' '

def RepeatTest(bot1, bot2, timePerMove, maxDepth = 100, openingFile = None, count = 100):

    if openingFile != None:
        openings = []
        with open(openingFile) as file:
            for line in file:
                openings.append(line)
    else:
        openings = ["rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"]

    games = []
    pgns = []
    for i in range(count):
        result, pgn = GameTest(bot1, bot2, timePerMove * 10, timePerMove, openings=openings)
        games.append(result)
        pgns.append(pgn)
        print(pgn)
        print(games)

    print(pgns)
    print(games)
    bot1wins = 0
    draws = 0
    bot2wins = 0
    for game in games:
        if game == 1:
            bot1wins += 1
        elif game == 0:
            draws += 1
        else:
            bot2wins += 1

    print("bot1wins:", bot1wins, "bot2wins:",bot2wins, "draws:",draws)

def MakeBook():
    myBook = {}

    with open("OpeningBookDeepBase.txt", "r") as file:
        for line in file:
            if len(line) > 1 and line[0] != "/":
                board = ChessBoard()
                for moveStr in line.split(" ")[:-1]:
                    oldfen = board.getFEN()
                    move = HelperFunctions.strToMove(board, moveStr)
                    if move != None:
                        board.makeMove(move)
                        if oldfen not in myBook:
                            myBook[oldfen] = [moveStr]
                        else:
                            oldList = myBook[oldfen]
                            oldList.append(moveStr)
                            myBook[oldfen] = oldList

    print(myBook)

if __name__ == "__main__":
    import CurrentBot
    import oldmain
    import OldBot
    import HelperFunctions
    #RepeatTest(CurrentBot.rootNegaMax, oldmain.rootNegaMax, openingFile="8mvs_+90_+99.epd", totalTime = 10, increment= 1, count = 1)
    RepeatTest(CurrentBot.rootNegaMax, OldBot.rootNegaMax, 0.25, openingFile="8mvs_+90_+99.epd", count=100)


    #playChess(2.5, 0.25, False, True, whiteInfiniteTime=True)

    # pygame.init()
    # screen = pygame.display.set_mode((512, 512))
    # running = True
    # pngs = [
    #     pygame.image.load('images/black_king_64x64.png'),
    #     pygame.image.load('images/black_queen_64x64.png'),
    #     pygame.image.load('images/black_bishop_64x64.png'),
    #     pygame.image.load('images/black_knight_64x64.png'),
    #     pygame.image.load('images/black_rook_64x64.png'),
    #     pygame.image.load('images/black_pawn_64x64.png'),
    #     pygame.image.load('images/board.png'),
    #     pygame.image.load('images/white_pawn_64x64.png'),
    #     pygame.image.load('images/white_rook_64x64.png'),
    #     pygame.image.load('images/white_knight_64x64.png'),
    #     pygame.image.load('images/white_bishop_64x64.png'),
    #     pygame.image.load('images/white_queen_64x64.png'),
    #     pygame.image.load('images/white_king_64x64.png')]

    # tt = {}

    # board = ChessBoard()
    # board.loadFEN("4r1k1/p3P2p/8/1p1p1R2/8/8/1r5P/4R1K1 w - - 0 28")
    # move = CurrentBot.rootNegaMax(board, 100, tt, time.time(), 200, 20, True)
    