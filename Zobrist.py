import random

#Zobrist Hashing
#Seed is an array of 781 randomly generated 64-bit ints
def ZobristHash(boardState : list[list[int]], move : int, castlingRights : list[int], passantColumn : int, seed: list[int]):
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