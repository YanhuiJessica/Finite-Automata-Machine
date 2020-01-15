from collections import defaultdict
from graphviz import Digraph

star = '*'
line = '|'
dot = '·'
leftBracket, rightBracket = '(', ')'
alphabet = [chr(i) for i in range(ord('A'), ord('Z') + 1)] + \
    [chr(i) for i in range(ord('a'), ord('z') + 1)] + \
    [chr(i) for i in range(ord('0'), ord('9') + 1)]
epsilon = 'ε'

class FA:

    def __init__(self, symbol = set([])):
        self.states = set()
        self.symbol = symbol    # input symbol
        self.transitions = defaultdict(defaultdict)
        self.startstate = None
        self.finalstates = []

    def setStart(self, state):
        self.startstate = state
        self.states.add(state)

    def addFinal(self, state):
        if isinstance(state, int):
            state = [state]
        for s in state:
            if s not in self.finalstates:
                self.finalstates.append(s)

    def addTransition(self, fromstate, tostate, inputch):   # add only one
        if isinstance(inputch, str):
            inputch = set([inputch])
        self.states.add(fromstate)
        self.states.add(tostate)
        if fromstate in self.transitions and tostate in self.transitions[fromstate]:
            self.transitions[fromstate][tostate] = \
            self.transitions[fromstate][tostate].union(inputch)
        else:
            self.transitions[fromstate][tostate] = inputch

    def addTransition_dict(self, transitions):  # add dict to dict
        for fromstate, tostates in transitions.items():
            for state in tostates:
                self.addTransition(fromstate, state, tostates[state])

class Regex2NFA:

    def __init__(self, regex):
        self.regex = regex
        self.buildNFA()

    @staticmethod
    def getPriority(op):
        if op == line:
            return 1
        elif op == dot:
            return 2
        elif op == star:
            return 3
        else:       # leftBracket
            return 0

    def buildNFA(self):
        tword = ''
        pre = ''
        symbol = set()

        # explicitly add dot to the expression
        for ch in self.regex:
            if ch in alphabet:
                symbol.add(ch)
            if ch in alphabet or ch == leftBracket:
                if pre != dot and (pre in alphabet or pre in [star, rightBracket]):
                    tword += dot
            tword += ch
            pre = ch
        self.regex = tword

        # convert infix expression to postfix expression
        tword = ''
        stack = []
        for ch in self.regex:
            if ch in alphabet:
                tword += ch
            elif ch == leftBracket:
                stack.append(ch)
            elif ch == rightBracket:
                while(stack[-1] != leftBracket):
                    tword += stack[-1]
                    stack.pop()
                stack.pop()    # pop left bracket
            else:
                while(len(stack) and Regex2NFA.getPriority(stack[-1]) >= Regex2NFA.getPriority(ch)):
                    tword += stack[-1]
                    stack.pop()
                stack.append(ch)
        while(len(stack) > 0):
            tword += stack.pop()
        self.regex = tword
