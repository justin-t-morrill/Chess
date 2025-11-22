import random, time
import main

random.seed(1234)
version = "TheCarrotGodBOT 2025"
moves = []
tt = {}
depth = 100

board = main.ChessBoard()
while True:
    args = input().split()
    if args[0] == "uci":
        print("id name", version)
        print("option name Move Overhead type spin default 10 min 0 max 5000")
        print("uciok")

    elif args[0] == "isready":
        print("readyok")

    elif args[0] == "quit":
        break
    
    elif args[0] == "ucinewgame":
        tt = {}
    
    elif args[:2] == ["position", "startpos"]:

        if len(args) == 2:
            board = main.ChessBoard()
            moves = []

        else:
            newMoves = args[3:]
            ply = 0
            for move in newMoves:
                if len(moves) <= ply or move != moves[ply]:
                    board.makeMove(main.strToMove(board, move))
                ply += 1
            moves = newMoves

    elif args[0] == "setoption":
        if args[2:5] == ["Move" ,"Overhead", "value"]:
            overhead = int(args[5]) / 1000

    elif args[0] == "go":
        if args[1] == "movetime":
            startTime = time.time()
            bestMove = board.rootNegaMax(depth, tt, startTime, 200, 0, False)

        else:
            wtime, btime, winc, binc = [int(a) / 1000 for a in args[2::2]]
            if board.move == 1:
                timeLeft = wtime - overhead
                increment = winc - overhead
            else:
                timeLeft = btime - overhead
                increment = binc - overhead

            startTime = time.time()
            bestMove = board.rootNegaMax(depth, tt, startTime, timeLeft, increment, False)

        print("bestmove " + main.moveToStr(bestMove))
