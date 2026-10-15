class DFA:
    def __init__(self,alphabet_size):
        self.alphabet_size = alphabet_size
        self.transitions = []
        self.accepting = []


# Input: a string over a,b,c,d.
# Output: whether all four letters occur.
# Example: "aabbcd" -> True.
def has_all_letters(s):
    return ('a' in s and
            'b' in s and
            'c' in s and
            'd' in s)


# Input: a state description.
# Output: its numeric state ID.
# Example: requesting "ab" twice gives the same ID.
def add_state(key, ids, names, dfa):
    if key in ids:
        return ids[key]

    state_id = len(names)
    ids[key] = state_id
    names.append(key)

    dfa.transitions.append([-1] * dfa.alphabet_size)
    dfa.accepting.append(True)

    return state_id


# Input: a DFA with -1 transitions for failure.
# Output: the same DFA with a rejecting sink state.
def add_sink(dfa):
    sink = len(dfa.transitions)

    dfa.transitions.append([sink] * dfa.alphabet_size)
    dfa.accepting.append(False)

    for q in range(sink):
        for c in range(dfa.alphabet_size):
            if dfa.transitions[q][c] == -1:
                dfa.transitions[q][c] = sink


# Input: none.
# Output: DFA for strings whose every 6-window
# contains a,b,c,d.
# Example: "abcdab" is accepted.
def build_base_dfa():
    dfa = DFA(4)

    ids = {}
    names = []

    add_state("", ids, names, dfa)

    q = 0
    while q < len(names):
        current = names[q]

        for c in range(4):
            next_state = current + chr(ord('a') + c)

            if len(next_state) == 6:
                if not has_all_letters(next_state):
                    continue

                next_state = next_state[1:]

            dfa.transitions[q][c] = add_state(
                next_state, ids, names, dfa
            )

        q += 1

    add_sink(dfa)
    return dfa


# Input: DFA and length n >= 0.
# Output: exact accepted count.
# Example: base DFA with n=1 returns 4.
# Uses two arrays.
def count_accepted(dfa, n):
    states = len(dfa.transitions)

    prev = [0] * states

    for q in range(states):
        if dfa.accepting[q]:
            prev[q] = 1

    for k in range(n):
        next_counts = [0] * states

        for q in range(states):
            for c in range(4):
                next_state = dfa.transitions[q][c]
                next_counts[q] += prev[next_state]

        prev = next_counts

    return prev[0]


# Input: base DFA and even n.
# Output: exact count with middle aa.
# Example: n=2 returns 1.
# Precondition: n is even and >= 2.
def count_middle_aa(dfa, n):
    half = n // 2 - 1
    states = len(dfa.transitions)

    forward = [0] * states
    forward[0] = 1

    for k in range(half):
        temp = [0] * states

        for q in range(states):
            for c in range(4):
                next_state = dfa.transitions[q][c]
                temp[next_state] += forward[q]

        forward = temp

    backward = [0] * states

    for q in range(states):
        if dfa.accepting[q]:
            backward[q] = 1

    for k in range(half):
        next_counts = [0] * states

        for q in range(states):
            total = 0

            for c in range(4):
                next_state = dfa.transitions[q][c]
                total += backward[next_state]
            next_counts[q] = total

        backward = next_counts

    answer = 0

    for q in range(states):
        after_first_a = dfa.transitions[q][0]
        after_second_a = dfa.transitions[after_first_a][0]

        answer += forward[q] * backward[after_second_a]

    return answer


# Input: decimal text and bounds.
# Output: integer or -1.
# Example: parse_integer("62", 1, 300) returns 62.
def parse_integer(s, low, high):
    if not s or not s.isascii() or not s.isdecimal():
        return -1

    n = int(s)

    if low <= n <= high:
        return n

    return -1


# Input: menu choices and n in [1,300].
# Output: exact counts.
# Example: choice 1 and n=1 prints 4.
def main():
    base = build_base_dfa()

    while True:
        print("\n1. Count strings in L")
        print("2. Count even-length strings with middle aa")
        print("3. Quit")

        try:
            line = input("Choice: ")
        except EOFError:
            break

        choice = parse_integer(line, 1, 3)

        if choice == 3:
            break

        if choice not in (1, 2):
            print("Invalid choice.")
            continue

        try:
            line = input("Enter n (1-300): ")
        except EOFError:
            break

        n = parse_integer(line, 1, 300)

        if n == -1:
            print("Invalid length.")
            continue

        if choice == 1:
            print("Answer:", count_accepted(base, n))

        elif n % 2 != 0:
            print("Answer: 0")

        else:
            print("Answer:", count_middle_aa(base, n))


if __name__ == "__main__":
    main()
