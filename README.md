## Finite-Automata-Machine

### Overview

This is a python program to construct ε-NFA, DFA, and minimised DFA from a given regex. After constructing DFA, it can judge a given word whether it matches the regex.

### Requirements

- Python 3
- python-graphviz
  - Users can install it by running `pip install graphviz`

### Regex -> NFA

- `Regex2NFA.basicstruct`<br>
![basic struct](img/basic.jpg)
- `Regex2NFA.linestruct`<br>
![line struct](img/line.jpg)
- `Regex2NFA.dotstruct`<br>
![dot struct](img/dot.jpg)
- `Regex2NFA.starstruct`<br>
![star struct](img/star.jpg)

### Sample Generation

- Sample regex: `1*0(0|1)*`
- Sample-generated NFA: <br>
![Sample-generated NFA](img/sample-nfa.png)
- Sample-generated DFA: <br>
![Sample-generated DFA](img/sample-dfa.png)
- Sample-generated minDFA: <br>
![Sample-generated minDFA](img/sample-mindfa.png)