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

        #Stores the best/refutation line
        self.hashMove = None