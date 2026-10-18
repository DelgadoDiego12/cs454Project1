# Check one six-character window.
# Input = a string, such as 'abcdab'
# Output = True if it contains a, b, c, and d
def allLetters(text):
    for letter in 'abcd':
        if letter not in text:
            return False
    return True


# Checks every six-character window in a string.
# Input = a string, such as 'bcaabd'
# Output = True if all its six-character windows are valid
# A string shorter than six characters is automatically valid
def validString(text):
    for position in range(len(text) - 5):
        window = text[position:position + 6]
        if not allLetters(window):
            return False
    return True


class PairedDFA:
    # Creats a second DFA that uses two copies of the original DFA together
    alphabetSize = 16
    start = 0


    def __init__(self, base):
        # saves a reference to the original DFA
        self.base = base


        # original DFA minus the one sink
        self.baseSink = len(base.transitions) - 1
        # numberOfBaseStates is the total number of non sink states
        self.numberOfBaseStates = self.baseSink
        # stores a string for every ordinary state
        self.stateBuffers = base.stateNames[:self.numberOfBaseStates]


        # Each new state represents a pair (leftState, rightState)
        # For every possible pair, we need one numbered state
        self.sink = self.numberOfBaseStates * self.numberOfBaseStates
        # add one rejecting sink state
        self.stateCount = self.sink + 1


        # this bit checks which four-letter endings work around 'aa'.
        # Example if left = 'abcd' and right = 'bcda', we check
        # 'abcd' + 'aa' + reverse('bcda')
        fourLetterWords = []
        # each loop chooses a letter and it goes through every possible combination of abcd and appends it
        for firstLetter in 'abcd':
            for secondLetter in 'abcd':
                for thirdLetter in 'abcd':
                    for fourthLetter in 'abcd':
                        word = firstLetter + secondLetter + thirdLetter + fourthLetter
                        fourLetterWords.append(word)


        self.allowedRights = {}     
        self.goodMiddlePairs = set()  


        # choose one of the left endings
        for LEnding in fourLetterWords:
            validRightEndings = []


            # choose one of the right endings
            for REnding in fourLetterWords:
                # reverse the right ending
                center = LEnding + 'aa' + REnding[::-1]
                # checks if it is valid
                if validString(center):
                    validRightEndings.append(REnding)
                    self.goodMiddlePairs.add((LEnding, REnding))


            # stores the allowed number of right endings that pair with the left ending
            self.allowedRights[LEnding] = validRightEndings


    # creats two DFA states into one pairted state number
    def stateID(self, leftState, rightState):
        if not (0 <= leftState < self.numberOfBaseStates and 0 <= rightState < self.numberOfBaseStates):
            raise ValueError('Invalid original DFA state')
        # example = 2 X 1365 + 4
        return leftState * self.numberOfBaseStates + rightState


    # Does the oposite of state id and finds/returns the stateID
    def statePair(self, state):
        if not 0 <= state < self.sink:
            raise ValueError('The sink has no state pair')
        return state // self.numberOfBaseStates, state % self.numberOfBaseStates


    # creates a pair of letters into a number between 0 and 15 
    @staticmethod
    def pairSymbol(leftLetter, rightLetter):
        # checks if both letters are a b c or d
        if leftLetter not in 'abcd' or rightLetter not in 'abcd':
            raise ValueError('Letters must be a, b, c, or d')
        # gets both the left and right number
        leftNumber = 'abcd'.index(leftLetter)
        rightNumber = 'abcd'.index(rightLetter)
        #makes sure the number is between 0 and 15 and returns that number
        return 4 * leftNumber + rightNumber


    # if the DFA is in a particular state  and reads a particular symbol then it calculates where to move it next
    def transition(self, state, symbol):
        # checks the validity of the state
        if not (0 <= state < self.stateCount and 0 <= symbol < 16):
            raise ValueError('Invalid state or symbol')
        #checks if the state is in the sink state
        if state == self.sink:
            return self.sink


        # combine the two states
        leftState, rightState = self.statePair(state)
        # decode both the left and right state
        leftLetter = symbol // 4    # 0=a, 1=b, 2=c, 3=d
        rightLetter = symbol % 4


        # moves both of the copies to the original DFA
        nextLeft = self.base.transitions[leftState][leftLetter]
        nextRight = self.base.transitions[rightState][rightLetter]


        #  if Either half failing makes the whole string invalid
        if nextLeft == self.baseSink or nextRight == self.baseSink:
            return self.sink


        return self.stateID(nextLeft, nextRight)


    # Decides whether a paired state is accepting
    def isAccepting(self, state):
        # checks if it is valid and also in the sink
        if not 0 <= state < self.stateCount:
            raise ValueError('Invalid state')
        if state == self.sink:
            return False


        # Gets the characters remevered by each state
        leftState, rightState = self.statePair(state)
        LBuffer = self.stateBuffers[leftState]
        RBuffer = self.stateBuffers[rightState]


        # if each buffer is at least 4 characters
        if len(LBuffer) >= 4 and len(RBuffer) >= 4:
            # we only need to get the last 4 characters that are closest to the middle
            LEnding = LBuffer[-4:]
            REnding = RBuffer[-4:]
            # checks if we previously found this valid and returns.
            return (LEnding, REnding) in self.goodMiddlePairs


        # it was a short string so we construct the word and return
        completeString = LBuffer + 'aa' + RBuffer[::-1]
        return validString(completeString)


    # checks a particular sequence of paired strings
    def acceptingPairs(self, symbols):
        state = self.start
        for symbol in symbols:
            state = self.transition(state, symbol)
        return self.isAccepting(state)


# Create the second DFA using the original one
# Input = base DFA and the Output = PairedDFA with every state
def buildMiddleAADFA(base):
    # creates the dfa
    return PairedDFA(base)


# Count using the two-array method
# Input = paired DFA and a nonnegative number of pairs
# Output = exact count Example = pair_length=0 -> 1 ('aa')
def pairedCountDP(paired, pair_length):
    if pair_length < 0:
        raise ValueError('Length cannot be negative')


    # creates an array for the states
    previous = [0] * paired.stateCount
    # we store 1 for the accepting state
    for state in range(paired.stateCount):
        if paired.isAccepting(state):
            previous[state] = 1
    # repeats once for each paured symbol in the DFA
    # calculates the next length to use
    for step in range(pair_length):
        next_counts = [0] * paired.stateCount


        # fort every state, it will try each of the 16 possible symbols
        for state in range(paired.stateCount):


            for symbol in range(16):
                next_state = paired.transition(state, symbol)
                next_counts[state] += previous[next_state]


        # updates the array
        previous = next_counts


    # returns the count
    return previous[paired.start]


# Count the same accepted strings using smaller arrays
# Input = paired DFA and a nonnegative number of PAIRS
# Output = exact count and an Example = pair_length=2 -> 60 (length-6 words)
# this is what is used for option 2 of the DFA
def fasterPairedCount(paired, pair_length):
    if pair_length < 0:
        raise ValueError('Length cannot be negative')


    # The right half has the same possible states and counts, because
    # it uses a second, identical copy of that DFA
    ways_to_state = [0] * paired.numberOfBaseStates
    ways_to_state[0] = 1


    # this loop will run 4 times
    for step in range(pair_length): 
        # creates a new array for the next string lenth
        next_counts = [0] * paired.numberOfBaseStates


        # goes through every nonsink state in the DFA
        for state in range(paired.numberOfBaseStates):
            #find out how many string reach this state  and skip if none
            ways = ways_to_state[state]
            if ways == 0:
                continue


            #use the originals DFA's transistion table to find the state reached
            for letter in range(4):
                next_state = paired.base.transitions[state][letter]
                # checks it doesnt lead to the sink
                if next_state != paired.baseSink:
                    # adds the current number of ways to reach our state
                    next_counts[next_state] += ways


        ways_to_state = next_counts


    # for short strings
    if pair_length < 4:
        reachable = []
        # examine each original DFA state
        for state in range(paired.numberOfBaseStates):
            # only includes states reached by at least 1 string
            if ways_to_state[state] > 0:
                reachable.append(state)


        total = 0
        # try for both left and right if reachable
        for leftState in reachable:
            for rightState in reachable:
                # pair the DFA states
                pair_state = paired.stateID(leftState, rightState)
                # if the combines state is accepting
                if paired.isAccepting(pair_state):
                    left_ways = ways_to_state[leftState]
                    right_ways = ways_to_state[rightState]
                    # multiply the two possible accepting states together
                    total += left_ways * right_ways
        return total


    ways_by_ending = {}
    # go through every non sink state in the dfa
    for state in range(paired.numberOfBaseStates):
        # get the number of strings to reach this state
        ways = ways_to_state[state]
        if ways > 0:
            #get the string stored in the buffer
            ending = paired.stateBuffers[state][-4:]
            # add it to the dictionary if its not already there
            if ending not in ways_by_ending:
                ways_by_ending[ending] = 0
                #add the number of strings that reached this state
            ways_by_ending[ending] += ways


    total = 0
    # go through every four character ending that exists
    for LEnding in ways_by_ending:
        left_ways = ways_by_ending[LEnding]
        # go through every four character ending that exists and is compatible with the right
        for REnding in paired.allowedRights[LEnding]:
            right_ways = ways_by_ending.get(REnding, 0)
            # multiply the endings together to get the complete total
            total += left_ways * right_ways


    # return the total number of combinations
    return total
