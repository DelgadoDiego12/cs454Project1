from L_double_dfa import buildMiddleAADFA, pairedCountDP

# This is our DFA class
# alphabetSize is the number of possible characters
# transistions is where the DFA goes after reading a character
# accepting is whether each state is accepting or rejecting
class DFA:
    def __init__(self,alphabetSize):
        self.alphabetSize = alphabetSize
        self.transitions = []
        self.accepting = []

# Input = a string over a,b,c,d
# Output = whether all four letters occur
#  An example of this would be "aabbcd" equals true
def hadAllLetters(x):
    return ('a' in x and
            'b' in x and
            'c' in x and
            'd' in x)

# The function creates a state and asignes it a number
# Input = The description of a state
# Output = its state ID
# Example "ab" will have the same ID
def addState(key, ids, names, dfa):
    # Checks if the state exists already to prevent duplication
    if key in ids:
        return ids[key]

    # creates a new ID for this current state and updates ids and names
    stateID = len(names)
    ids[key] = stateID
    names.append(key)

    # This creates four transitions for the state (because we have four charcters) and make it accepting
    dfa.transitions.append([-1] * dfa.alphabetSize)
    dfa.accepting.append(True)

    # returns the new state ID
    return stateID


#This creates our fail state
# Input = a DFA with one less transitions for failure
# Output = the same DFA with a rejecting fail state
def addSink(dfa):
    sink = len(dfa.transitions)


    # Creates the sink transistions like the previous block execpt make it a fail state
    dfa.transitions.append([sink] * dfa.alphabetSize)
    dfa.accepting.append(False)
    # Goes through every state and its transistions
    for currentState in range(sink):
        for letterIndex in range(dfa.alphabetSize):
            # if the transistion is -1 then it becomes a sink state that lead to this sink state
            if dfa.transitions[currentState][letterIndex] == -1:
                dfa.transitions[currentState][letterIndex] = sink


# This is what builds our DFA
# Input = none
# Output = DFA for strings whose every 6-window
# contains a,b,c,d
# Example = "abcdab" is accepted
def originalDFA():
    # DFA with four character alphabet
    dfa = DFA(4)
    # Creates an empty dictionary and list for tracking the states
    ids = {}
    names = []


    # calls our add state function
    addState("", ids, names, dfa)


    currentState = 0
    # Processes every stae
    while currentState < len(names):
        current = names[currentState]

        # Creates 1,2,3,4 and convertes into letters
        for letterIndex in range(4):
            nextState = current + chr(ord('a') + letterIndex)

            # First checks if it has all letters at length 6
            if len(nextState) == 6:
                if not hadAllLetters(nextState):
                    continue

                #Drops the first charcter
                nextState = nextState[1:]

            # Finds/creates the new state representing the current buffer
            # Savesthe states number as the transistion from state currentState on the character C
            dfa.transitions[currentState][letterIndex] = addState(
                nextState, ids, names, dfa
            )
        # moves to the next state to process
        currentState += 1

    # after every state is delt with it calls the addSink function
    addSink(dfa)
    # creates the rejecting state and fills in the invalid transistions
    dfa.stateNames = names + [None]  # State labels for product DFA construction.
    return dfa
# Finds the # of accepting states
# Input = DFA and length n >= 0
# Output = exact accepted count
# Example is the base DFA with n=1 returns 4
def acceptedCount(dfa, n):
    # saves the number of states in states
    states = len(dfa.transitions)

    # creates an array of 0's in the # of states
    prev = [0] * states

    # Initializes the states for a string of length 0
    for currentState in range(states):
        if dfa.accepting[currentState]:
            prev[currentState] = 1

    # increases the string length
    for k in range(n):
        nextCounts = [0] * states
        # uses the formula preszented in our project pdf starting at state 0
        for currentState in range(states):
            for letterIndex in range(dfa.alphabetSize):
                nextState = dfa.transitions[currentState][letterIndex]
                nextCounts[currentState] += prev[nextState]
        prev = nextCounts
    # returns the count
    return prev[0]

# makes sure the user enters a valid input
# Input = decimal text and bounds
# Output = integer or -1
# Example = parseInteger("62", 1, 300) returns 62
def parseInteger(userInput, low, high):
    # rejects non ASCII characters, rejects if its not a decimal, rejects if the input is empty
    if not userInput or not userInput.isascii() or not userInput.isdecimal():
        return -1


    # converts text to an integer
    n = int(userInput)

    # makes sure its between 1 and 300
    if low <= n <= high:
        return n

    return -1


# Input = menu choices and n in [1,300]
# Output = exact counts
def main():
    # Creates two different DFAs (One for L and the other for L")
    base = originalDFA()
    middleDFA = buildMiddleAADFA(base)

    # repeats until they type 3
    while True:
        print("\n1. Count strings in L")
        print("2. Count even-length strings with middle aa")
        print("3. Quit")

        # Input reads what the user chose
        try:
            line = input("Choice: ")
        # prevents an error if the user input stream closes
        except EOFError:
            break


        # makes sure the user inputs 1 2 or 3
        choice = parseInteger(line, 1, 3)

        # stops the code if input is 3
        if choice == 3:
            break

        # outputs "invalid choice" if it was not 1 or 2
        if choice not in (1, 2):
            print("Invalid choice.")
            continue

        # Asks for the strinbg lenth
        try:
            line = input("Enter n (1-300): ")
        except EOFError:
            break

        n = parseInteger(line, 1, 300)

        if n == -1:
            print("Invalid length.")
            continue


        # if the choice is 1 then it calls acceptedCount with the base DFA and n
        if choice == 1:
            print("Answer:", acceptedCount(base, n))

        # Handles off things for option 2
        elif n % 2 != 0:
            print("Answer: 0")

        # Count strings accepted by the paired DFA M''.
        # The paired DFA represents strings of the form x + aa + reverse(y),
        # where x and y each have length n // 2 - 1.
        else:
            # A pair-word has n/2 - 1 symbols; each symbol is in 0..15.
            print("Answer:", pairedCountDP(middleDFA, n // 2 - 1))


if __name__ == "__main__":
    main()
