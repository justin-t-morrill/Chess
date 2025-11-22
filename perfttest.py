def perftest(stockfish, mine):
    stockfishlines = stockfish.split("\n")
    stockfishdict = {}
    for line in stockfishlines:
        square, val = line.split(": ")
        stockfishdict[square] = int(val)
    mylines = mine.split("\n")
    mydict = {}
    for line in mylines:
        square, val = line.split(": ")
        mydict[square] = int(val)
    for square in mydict:
        if square not in stockfishdict.keys():
            print("Anomaly at", square, ". I gave", mydict[square], "should be 0")
        elif mydict[square] != stockfishdict[square]:
            print("Anomaly at", square, ". I gave", mydict[square], "should be", stockfishdict[square])
        else:
            print(square, "correct!")
    for square in stockfishdict:
        if square not in mydict.keys():
            print("Anomaly at", square, ". I gave 0 should be", stockfishdict[square])

perftest("""f3f2: 19
d6d5: 19
c7c6: 20
c7c5: 6
f3e2: 17
f3g2: 17
h5b5: 5
h5c5: 17
h5d5: 19
h5e5: 19
h5f5: 19
h5g5: 19
h5h6: 19
h5h7: 19
h5h8: 19
h4g3: 17
h4g5: 19
h4g4: 18""", """f3f2: 19
f3e2: 17
f3g2: 17
h4g4: 18
h4g5: 19
h4g3: 17
h5h6: 19
h5h7: 19
h5h8: 19
h5g5: 19
h5f5: 19
h5e5: 19
h5d5: 19
h5c5: 17
h5b5: 5
d6d5: 19
c7c6: 20
c7c5: 5""")