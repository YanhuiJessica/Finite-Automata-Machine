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
        self.symbol = symbol    # input symbol 输入符号表
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

    def addTransition(self, fromstate, tostate, inputch):   # add only one 仅添加一条映射关系
        if isinstance(inputch, str):
            inputch = set([inputch])
        self.states.add(fromstate)
        self.states.add(tostate)
        if fromstate in self.transitions and tostate in self.transitions[fromstate]:
            self.transitions[fromstate][tostate] = \
            self.transitions[fromstate][tostate].union(inputch)
        else:
            self.transitions[fromstate][tostate] = inputch

    def addTransition_dict(self, transitions):  # add dict to dict 将一个字典的内容添加到另一个字典
        for fromstate, tostates in transitions.items():
            for state in tostates:
                self.addTransition(fromstate, state, tostates[state])

    def newBuildFromNumber(self, startnum):
    # change the states' representing number to start with the given startnum
    # 改变各状态的表示数字，使之从 startnum 开始
        translations = {}
        for i in self.states:
            translations[i] = startnum
            startnum += 1
        rebuild = FA(self.symbol)
        rebuild.setStart(translations[self.startstate])
        rebuild.addFinal(translations[self.finalstates[0]])
        # 多个终结状态不方便合并操作, 同时提供的合并操作可以保证只产生一个终结状态
        for fromstate, tostates in self.transitions.items():
            for state in tostates:
                rebuild.addTransition(translations[fromstate], translations[state], tostates[state])
        return [rebuild, startnum]

    def newBuildFromEqualStates(self, equivalent, pos):
        # change states' number after merging
        # 在最小化合并状态后修改状态的表示数字
        rebuild = FA(self.symbol)
        for fromstate, tostates in self.transitions.items():
            for state in tostates:
                rebuild.addTransition(pos[fromstate], pos[state], tostates[state])
        rebuild.setStart(pos[self.startstate])
        for s in self.finalstates:
            rebuild.addFinal(pos[s])
        return rebuild

    def getEpsilonClosure(self, findstate):
        allstates = set()
        states = [findstate]
        while len(states):
            state = states.pop()
            allstates.add(state)
            if state in self.transitions:
                for tos in self.transitions[state]:
                    if epsilon in self.transitions[state][tos] and \
                        tos not in allstates:
                        states.append(tos)
        return allstates

    def getMove(self, state, skey):
        if isinstance(state, int):
            state = [state]
        trstates = set()
        for st in state:
            if st in self.transitions:
                for tns in self.transitions[st]:
                    if skey in self.transitions[st][tns]:
                        trstates.add(tns)
        return trstates

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
        else:       # left bracket 左括号
            return 0

    @staticmethod
    def basicstruct(inputch):   # Regex = a -> NFA
        state1 = 1
        state2 = 2
        basic = FA(set([inputch]))
        basic.setStart(state1)
        basic.addFinal(state2)
        basic.addTransition(state1, state2, inputch)
        return basic

    @staticmethod
    def linestruct(a, b):   # Regex = a | b -> NFA
        [a, m1] = a.newBuildFromNumber(2)
        [b, m2] = b.newBuildFromNumber(m1)
        state1 = 1
        state2 = m2
        lineFA = FA(a.symbol.union(b.symbol))
        lineFA.setStart(state1)
        lineFA.addFinal(state2)
        lineFA.addTransition(lineFA.startstate, a.startstate, epsilon)
        lineFA.addTransition(lineFA.startstate, b.startstate, epsilon)
        lineFA.addTransition(a.finalstates[0], lineFA.finalstates[0], epsilon)
        lineFA.addTransition(b.finalstates[0], lineFA.finalstates[0], epsilon)
        lineFA.addTransition_dict(a.transitions)
        lineFA.addTransition_dict(b.transitions)
        return lineFA

    @staticmethod
    def dotstruct(a, b):    # Regex = a · b -> NFA
        [a, m1] = a.newBuildFromNumber(1)
        [b, m2] = b.newBuildFromNumber(m1)
        state1 = 1
        state2 = m2 - 1
        dotFA = FA(a.symbol.union(b.symbol))
        dotFA.setStart(state1)
        dotFA.addFinal(state2)
        dotFA.addTransition(a.finalstates[0], b.startstate, epsilon)
        dotFA.addTransition_dict(a.transitions)
        dotFA.addTransition_dict(b.transitions)
        return dotFA

    @staticmethod
    def starstruct(a):  # Regex = a* -> NFA
        [a, m1] = a.newBuildFromNumber(2)
        state1 = 1
        state2 = m1
        starFA = FA(a.symbol)
        starFA.setStart(state1)
        starFA.addFinal(state2)
        starFA.addTransition(starFA.startstate, a.startstate, epsilon)
        starFA.addTransition(starFA.startstate, starFA.finalstates[0], epsilon)
        starFA.addTransition(a.finalstates[0], starFA.finalstates[0], epsilon)
        starFA.addTransition(a.finalstates[0], a.startstate, epsilon)
        starFA.addTransition_dict(a.transitions)
        return starFA

    def buildNFA(self):
        tword = ''
        pre = ''
        symbol = set()

        # explicitly add dot to the expression 显式地为正则式添加连接符
        for ch in self.regex:
            if ch in alphabet:
                symbol.add(ch)
            if ch in alphabet or ch == leftBracket:
                if pre != dot and (pre in alphabet or pre in [star, rightBracket]):
                    tword += dot
            tword += ch
            pre = ch
        self.regex = tword

        # convert infix expression to postfix expression 将中缀表达式转换为后缀表达式
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
                stack.pop()    # pop left bracket 弹出左括号
            else:
                while(len(stack) and Regex2NFA.getPriority(stack[-1]) >= Regex2NFA.getPriority(ch)):
                    tword += stack[-1]
                    stack.pop()
                stack.append(ch)
        while(len(stack) > 0):
            tword += stack.pop()
        self.regex = tword

        # build ε-NFA from postfix expression 由后缀表达式构建ε-NFA
        self.automata = []
        for ch in self.regex:
            if ch in alphabet:
                self.automata.append(Regex2NFA.basicstruct(ch))
            elif ch == line:
                b = self.automata.pop()
                a = self.automata.pop()
                self.automata.append(Regex2NFA.linestruct(a, b))
            elif ch == dot:
                b = self.automata.pop()
                a = self.automata.pop()
                self.automata.append(Regex2NFA.dotstruct(a, b))
            elif ch == star:
                a = self.automata.pop()
                self.automata.append(Regex2NFA.starstruct(a))
        self.nfa = self.automata.pop()
        self.nfa.symbol = symbol

class NFA2DFA:

    def __init__(self, nfa):
        self.buildDFA(nfa)

    def buildDFA(self, nfa):    # subset method 子集法
        allstates = dict()  # visited subset
        eclosure = dict()   # every state's ε-closure
        state1 = nfa.getEpsilonClosure(nfa.startstate)
        eclosure[nfa.startstate] = state1
        cnt = 1 # the number of subset, dfa state id
        dfa = FA(nfa.symbol)
        dfa.setStart(cnt)
        states = [[state1, dfa.startstate]] # unvisit
        allstates[cnt] = state1
        cnt += 1
        while len(states):
            [state, fromindex] = states.pop()
            for ch in dfa.symbol:
                trstates = nfa.getMove(state, ch)
                for s in list(trstates):    # 转化为list, 相当于使用了一个临时变量
                    if s not in eclosure:
                        eclosure[s] = nfa.getEpsilonClosure(s)
                    trstates = trstates.union(eclosure[s])
                if len(trstates):
                    if trstates not in allstates.values():
                        states.append([trstates, cnt])
                        allstates[cnt] = trstates
                        toindex = cnt
                        cnt += 1
                    else:
                        toindex = [k for k, v in allstates.items() if v  ==  trstates][0]
                    dfa.addTransition(fromindex, toindex, ch)
            for value, state in allstates.items():
                if nfa.finalstates[0] in state:
                    dfa.addFinal(value)
            self.dfa = dfa

    @staticmethod
    def reNumber(states, pos):  # renumber the sets' number begin from 1
        cnt = 1
        change = dict()
        for st in states:
            if pos[st] not in change:
                change[pos[st]] = cnt
                cnt += 1
            pos[st] = change[pos[st]]

    def minimise(self): # segmentation 分割法, 生成新的状态集合
        states = list(self.dfa.states)
        tostate = dict(set()) # Move(every state, every symbol)

        # initialization 预处理出每个状态经一个输入符号可以到达的下一个状态
        for st in states:
            for sy in self.dfa.symbol:
                if st in tostate:
                    if sy in tostate[st]:
                        tostate[st][sy] = tostate[st][sy].union(self.dfa.getMove(st, sy))
                    else:
                        tostate[st][sy] = self.dfa.getMove(st, sy)
                else:
                    tostate[st] = {sy : self.dfa.getMove(st, sy)}
                if len(tostate[st][sy]):
                    tostate[st][sy] = tostate[st][sy].pop()
                else:
                    tostate[st][sy] = 0

        equal = dict()  # state sets 不同分组的状态集合
        pos = dict()    # record the set which state belongs to 记录状态对应的分组

        # initialization 2 sets, nonterminal states and final states
        equal = {1: set(), 2: set()}
        for st in states:
            if st not in self.dfa.finalstates:
                equal[1] = equal[1].union(set([st]))
                pos[st] = 1
        for fst in self.dfa.finalstates:
            equal[2] = equal[2].union(set([fst]))
            pos[fst] = 2

        unchecked = []
        cnt = 3 # the number of sets
        unchecked.extend([[equal[1], 1], [equal[2], 2]])
        while len(unchecked):
            [equalst, id] = unchecked.pop()
            for sy in self.dfa.symbol:
                diff = dict()
                for st in equalst:
                    if tostate[st][sy] == 0:
                        if 0 in diff:
                            diff[0].add(st)
                        else:
                            diff[0] = set([st])
                    else:
                        if pos[tostate[st][sy]] in diff:
                            diff[pos[tostate[st][sy]]].add(st)
                        else:
                            diff[pos[tostate[st][sy]]] = set([st])
                if len(diff) > 1:
                    for k, v in diff.items():
                        if k:
                            for i in v:
                                equal[id].remove(i)
                                if cnt in equal:
                                    equal[cnt] = equal[cnt].union(set([i]))
                                else:
                                    equal[cnt] = set([i])
                            if len(equal[id]) == 0:
                                equal.pop(id)
                            for i in v:
                                pos[i] = cnt
                            unchecked.append([equal[cnt], cnt])
                            cnt += 1
                    break
        if len(equal) == len(states):
            self.minDFA = self.dfa
        else:
            NFA2DFA.reNumber(states, pos)
            self.minDFA = self.dfa.newBuildFromEqualStates(equal, pos)
