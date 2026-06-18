# Snippets que Mais Enganaram os Modelos

**Base:** rodada 1 (seed=1781748606) — 5 modelos, 200 snippets
**Critério:** snippets em que todos os 5 modelos erraram (5/5)
**Achado:** todos os 10 são código AI gerado em Python — nenhum humano, nenhum C

---

## Snippet 1 — ID 3 | Python | Verdadeiro: `ai` | Erros: 5/5

```python
# rc_strdup.py
import sys
 
def rc_strdup(str_in):
    """
    Convert Ruby value to C string.  May raise TypeError if the
    value isn't a string, or ArgumentError if it contains '\0'.
    """
    c = str_in.encode('utf-8')
 
    """
    Call strdup() and perhaps raise Errno::ENOMEM.
    """
    d = c.copy()
 
    """
    Convert C string to Python string.
    """
    str_out = d.decode('utf-8')
    return str_out
 
if __name__ == '__main__':
    print(rc_strdup(sys.argv[1]))
```

### Predições e explicações dos modelos

**deepseek** ✗ → prediu `human` (conf 8)
> The code contains unused variables (pi and t) that appear to be leftovers from debugging or early development, a common human fingerprint not typical of AI-generated code.

**llama** ✗ → prediu `human` (conf 7)
> The code contains a simple and somewhat esoteric use of `os.get_terminal_size()` and `chr(219)`, suggesting a specific, possibly experimental or creative goal, and the presence of a bare `input()` at the end is reminiscent of a quick test or debug stub.

**mimo** ✗ → prediu `human` (conf 6)
> Found weak human fingerprints: an unused variable 't = time.time()' suggesting leftover debug or dead code, and the use of magic number 'chr(219)' without explanation.

**minimax** ✗ → prediu `human` (conf 8)
> Unused leftover variables `pi = math.pi` and `t = time.time()` are classic dead-code artifacts from a human's experimental session, and `chr(219)` is a magic number used without explanation. The missing newline between rows (no `print()` per row) is an oversight a human would leave behind.

**qwen** ✗ → prediu `human` (conf 8)
> The snippet contains clear human fingerprints, including completely unused imports and variables (`math`, `pi`, `time`, `t`) that suggest leftover experimentation, the use of the magic number `chr(219)` for an extended ASCII block character, and the classic `input()` call at the end to prevent the console window from closing immediately.

---

## Snippet 2 — ID 4 | Python | Verdadeiro: `ai` | Erros: 5/5

```python
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 27 14:00:00 2020

@author: 
"""

SIZES = [6, 9, 20]
MAX_TOTAL = 100
# Works like Sieve of Eratosthenes
numSizes = len(SIZES)
counts = [0] * numSizes
maxFound = MAX_TOTAL + 1
found = [False] * maxFound
numFound = 0
total = 0
advancedState = False
while numFound < maxFound and advancedState:
    if not found[total]:
        found[total] = True
        numFound += 1
    # Advance state
    advancedState = False
    for i in range(numSizes):
        curSize = SIZES[i]
        if (total + curSize) > MAX_TOTAL:
            # Reset to zero and go to the next box size
            total -= counts[i] * curSize
            counts[i] = 0
        else:
            # Adding a box of this size still keeps the total at or below the maximum
            counts[i] += 1
            total += curSize
            advancedState = True
            break

if numFound < maxFound:
    # Did not find all counts within the search space
    for i in range(MAX_TOTAL, -1, -1):
        if not found[i]:
            print("Largest non-McNugget number in the search space is " + str(i))
            break
else:
    print("All numbers in the search space are McNugget numbers")
```

### Predições e explicações dos modelos

**deepseek** ✗ → prediu `human` (conf 8)
> Uses Python 2 style print statements without parentheses and a non-standard strptime format with %Z (which is not supported by strptime), indicating human experimental or debug code.

**llama** ✗ → prediu `human` (conf 8)
> The presence of commented code and an additional 'another timezone' section with a different library (pytz) suggests a debugging or exploratory process, indicative of human-written code.

**mimo** ✗ → prediu `human` (conf 7)
> The informal comment '# another timezone' is a colloquial, personal annotation that serves as a weak human fingerprint, indicating authorship by a human rather than AI.

**minimax** ✗ → prediu `human` (conf 8)
> Python 2 print-statement syntax, magic number 12*3600 without explanation, informal '# another timezone' comment, and a hardcoded specific date ('March 7 2009 7:30pm EST') all point to human-authored exploratory code; absence of docstrings, type hints, or defensive scaffolding further contradicts AI generation.

**qwen** ✗ → prediu `human` (conf 9)
> The snippet uses Python 2 `print` statements and contains a highly specific hardcoded date from 2009, alongside magic numbers (`12*3600`) and short variable names typical of a quick scratchpad script or forum post from that era. AI models almost universally default to Python 3 syntax and avoid such specific, dated hardcoded strings unless explicitly prompted.

---

## Snippet 3 — ID 6 | Python | Verdadeiro: `ai` | Erros: 5/5

```python
def egyptian_divmod(dividend, divisor):
    table = [[1, divisor]]
    while table[-1][0] * 2 <= dividend:
        table.append(list(map(lambda x: x*2, table[-1])))
    answer, accumulator = 0, 0
    for pow, double in reversed(table):
        if accumulator + double <= dividend:
            accumulator += double
            answer += pow
    return [answer, dividend - accumulator]
 
print("Quotient = %s Remainder = %s" % egyptian_divmod(580, 34))
```

### Predições e explicações dos modelos

**deepseek** ✗ → prediu `human` (conf 8)
> The code contains human fingerprints such as unused imports (sqrt, itemgetter), use of Python 2's cmp function, and a quirky string construction for 'Ascending'/'Descending', indicating idiosyncratic style and lived experience.

**llama** ✗ → prediu `human` (conf 8)
> The code contains idiosyncratic or inconsistent style, such as the use of 'cmp' which is a Python 2 function, and the format specifier '{0:n0}' which is not a standard format specifier, indicating a human fingerprint.

**mimo** ✗ → prediu `human` (conf 8)
> The code contains unused imports (sqrt and itemgetter) and uses the deprecated cmp function, which are common human-written artifacts reflecting oversight or legacy practices.

**minimax** ✗ → prediu `human` (conf 9)
> Multiple strong human fingerprints: unused imports (sqrt, itemgetter) left over from experimentation; Python 2 `cmp()` builtin dates the code to pre-2020; cryptic, terse variable names (mil, lmt, lg, ng, mx, bi) with no comments on non-trivial logic; manual micro-optimizations (j << 1 bit shift, 8-step loop) typical of competitive programming; and a redundant islice over an already-bounded generator.

**qwen** ✗ → prediu `human` (conf 9)
> The code contains strong human fingerprints, including the use of the Python 2-only `cmp()` function, highly cryptic variable names (`lg`, `ng`, `mx`, `bi`), unused imports (`sqrt`, `itemgetter`), and an idiosyncratic indexing trick (`cmp(ng, lg) + 1`) to map comparison results to array indices for ascending/descending strings.

---

## Snippet 4 — ID 11 | Python | Verdadeiro: `ai` | Erros: 5/5

```python
javascript
<!DOCTYPE html><html><head><meta charset="UTF-8">
<title>Wireworld</title>
<script src="wireworld.js"></script></head><body>
<input type='file' accept='text/plain' onchange='openFile( event )' />
<br /></body></html>
```

### Predições e explicações dos modelos

**deepseek** ✗ → prediu `human` (conf 9)
> The code contains human fingerprints such as a likely bug (infinite loop due to `if quiet and kind!= "": continue` skipping increment logic), idiosyncratic style (using a comma-split trick with leading empty string, missing space in print formatting), and old-style % formatting, indicating a real programmer's quick script.

**llama** ✗ → prediu `human` (conf 7)
> The code contains idiosyncratic style, such as inconsistent spacing and an informal variable name 'big_lim', and has a specific task implementation that suggests human authorship.

**mimo** ✗ → prediu `human` (conf 7)
> nan

**minimax** ✗ → prediu `human` (conf 8)
> Human fingerprints include: the `',odd,prime'.split(',')` trick to sneak an empty string into the iteration list (with the matching trailing space in `kind == 'odd '`), inconsistent operator spacing (`b!= f`, `kind!= ''`), the cryptic single-letter variable `f`, and notably the absence of `if __name__ == '__main__':` boilerplate around `main()` — all hallmarks of a personal, pragmatic coding style rather than AI-generated scaffolding.

**qwen** ✗ → prediu `human` (conf 9)
> The code contains distinct human typos and bugs, such as the trailing space in the string literal `"odd "` (which causes an infinite loop since it won't match the split result), the invalid `%,d` format specifier (confusing `%` formatting with f-string thousands separators), and inconsistent spacing around the `!=` operator.

---

## Snippet 5 — ID 13 | Python | Verdadeiro: `ai` | Erros: 5/5

```python
import ldap
import logging
import sys
 
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
 
class LDAPClient(object):
    def __init__(self, host, port, base, group_filter):
        self.host = host
        self.port = port
        self.base = base
        self.group_filter = group_filter
        self.connection = None
 
    def connect(self):
        self.connection = ldap.initialize('ldap://%s:%s' % (self.host, self.port))
        self.connection.protocol_version = ldap.VERSION3
 
    def get_groups_of_user(self, username):
        search_filter = self.group_filter % username
        logging.debug('Searching for groups with filter: %s' % search_filter)
        result = self.connection.search_s(self.base, ldap.SCOPE_SUBTREE, search_filter)
        logging.debug('Result: %s' % result)
        return [entry[0] for entry in result]
 
    def close(self):
        self.connection.unbind_s()
 
if __name__ == '__main__':
    client = LDAPClient(
        host='ldap.example.com',
        port=389,
        base='dc=example,dc=com',
        group_filter='(memberUid=%s)',
    )
    client.connect()
    groups = client.get_groups_of_user('username')
    print 'Groups: %s' % groups
```

### Predições e explicações dos modelos

**deepseek** ✗ → prediu `human` (conf 8)
> The code includes a version annotation ('# version 1.0.6'), which is a human fingerprint indicating iterative development and authorship.

**llama** ✗ → prediu `human` (conf 8)
> The code contains version annotation ('# version 1.0.6') and task-specific comments ('# Chaotic Building Society task', '# Siegfried Rump task'), indicating human fingerprints.

**mimo** ✗ → prediu `human` (conf 9)
> The code includes a clear version annotation '# version 1.0.6', which is a distinctive human fingerprint indicating authorship and development history.

**minimax** ✗ → prediu `human` (conf 9)
> Multiple human fingerprints: explicit version annotation '# version 1.0.6', informal task-referencing comments ('# Chaotic Building Society task', '# Siegfried Rump task') pointing to specific numerical-analysis benchmarks, irregular spacing in assignments ('a  =', 'b  =' with double spaces vs single elsewhere), and variable naming that accreted over time (c1-c3 used early, c4-c8 appended later in the Rump section).

**qwen** ✗ → prediu `human` (conf 9)
> The code includes a clear version annotation (`# version 1.0.6`), which is a strong human fingerprint. Additionally, the manual alignment spacing (e.g., `a  = Decimal(77617)`) and the implementation of specific, niche numerical analysis benchmark tasks (Muller's sequence, Siegfried Rump task) reflect human authorship and domain-specific scripting habits.

---

## Snippet 6 — ID 15 | Python | Verdadeiro: `ai` | Erros: 5/5

```python
original = "hello"
reference = original          # copies reference
copy1 = original.dup          # instance of original.class
copy2 = String.new(original)  # instance of String
 
original << " world!"         # append
p reference                   #=> "hello world!"
p copy1                       #=> "hello"
p copy2                       #=> "hello"
```

### Predições e explicações dos modelos

**deepseek** ✗ → prediu `human` (conf 8)
> The code includes a version annotation '# version 1.0.6', a clear human fingerprint indicating version tracking. Additionally, the class definition 'class FloatRange(start, endInclusive):' contains a syntax error typical of human oversight.

**llama** ✗ → prediu `human` (conf 7)
> The code contains a version annotation ('# version 1.0.6') and a simple main function with example usage, indicating human fingerprints, although the overall style is fairly clean and consistent.

**mimo** ✗ → prediu `human` (conf 8)
> The code contains a clear human fingerprint with the version annotation '# version 1.0.6', indicating development history and tracking.

**minimax** ✗ → prediu `human` (conf 8)
> Clear human fingerprints: version annotation '# version 1.0.6', inconsistent naming style mixing PascalCase (FloatRange), camelCase (endInclusive, mappedValue), and snake_case (mapRange), plus non-standard class declaration syntax (class FloatRange(start, endInclusive) without proper inheritance) and a main(args) function that accepts args but is called with None and never uses them.

**qwen** ✗ → prediu `human` (conf 8)
> The code includes a clear version annotation ("# version 1.0.6") and exhibits idiosyncratic style choices such as camelCase naming ("mappedValue", "endInclusive") and a syntactically confused class definition (`class FloatRange(start, endInclusive):`), which are strong human fingerprints.

---

## Snippet 7 — ID 18 | Python | Verdadeiro: `ai` | Erros: 5/5

```python
import os
os.mkdir(path)
```

### Predições e explicações dos modelos

**deepseek** ✗ → prediu `human` (conf 6)
> The code includes a missing 'self' parameter in the method definition and no import for sys, both common human oversights that deviate from typical AI-generated correctness.

**llama** ✗ → prediu `human` (conf 7)
> The code contains a hardcoded local example in the main function and lacks uniform docstrings or type hints, indicating human fingerprints.

**mimo** ✗ → prediu `human` (conf 8)
> The code shows human fingerprints with incorrect Python method definitions (missing self parameter) and a missing import for sys, indicating debugging artifacts or evolving understanding typical of human authorship.

**minimax** ✗ → prediu `human` (conf 9)
> Strong human fingerprints: methods lack the required `self` parameter (a classic mistake by developers coming from Java/C#), method names use camelCase (`stripChars`, `inString`) which violates Python conventions, and the playful example sentence ('She was a soul stripper') suggests a human author. These are not patterns an AI would produce.

**qwen** ✗ → prediu `human` (conf 9)
> The code contains multiple structural errors typical of a human beginner or a direct translation from a language like Java (e.g., missing `self` parameters, calling class methods as globals, and missing `import sys`), which AI models rarely produce. Additionally, the presence of non-breaking space artifacts suggests it was copy-pasted from a web source like Rosetta Code.

---

## Snippet 8 — ID 19 | Python | Verdadeiro: `ai` | Erros: 5/5

```python
from collections import defaultdict
 
class Hffs:
    def __init__(self):
        self.sequence_r = defaultdict(int)
        self.sequence_s = defaultdict(int)
 
    def ffr(self, n):
        if n in self.sequence_r:
            return self.sequence_r[n]
        elif n == 0:
            return 1
        else:
            new_r = self.ffr(n - 1) + self.ffs(n - 1)
            self.sequence_r[n] = new_r
            return new_r
 
    def ffs(self, n):
        if n in self.sequence_s:
            return self.sequence_s[n]
        elif n == 0:
            return 2
        else:
            lower = self.ffs(n - 1) + 1
            upper = self.ffr(n) + 1
            min_s = 0
            for i in range(lower, upper + 1):
                if i not in self.sequence_r.values():
                    min_s = i
                    break
            self.sequence_s[n] = min_s
            return min_s
 
if __name__ == "__main__":
    hof = Hffs()
 
    for i in range(10):
        print(f"H:{i} -> R: {hof.ffr(i)}, S: {hof.ffs(i)}")
 
    r40 = [hof.ffr(i) for i in range(40)]
    s960 = [hof.ffs(i) for i in range(960)]
 
    s960.extend(r40)
    s960.sort()
    f1000 = list(range(1, 1001))
 
    assert f1000 == s960, "Does NOT match"
```

### Predições e explicações dos modelos

**deepseek** ✗ → prediu `human` (conf 8)
> The code shadows the built-in 'len' with a variable and then attempts to call len(t) as a function, which will cause a TypeError—a classic human debugging oversight. Also includes an unused import sys, common in human code.

**llama** ✗ → prediu `human` (conf 7)
> The code exhibits idiosyncratic style, such as reusing the built-in 'len' as a variable name, and contains a straightforward, uncommented implementation that suggests a personal or experimental approach.

**mimo** ✗ → prediu `human` (conf 8)
> The code uses `len` as a variable name, overriding the built-in function, which is a human fingerprint indicating idiosyncratic or non-standard practice commonly seen in human-written code.

**minimax** ✗ → prediu `human` (conf 8)
> Strong human fingerprints: `len` is shadowed as a variable name (clobbering the built-in), `import sys` is unused (forgotten import), and output is inconsistent (prints a single element then switches to printing the whole list) — all hallmarks of exploratory, unpolished human code.

**qwen** ✗ → prediu `human` (conf 9)
> The code shadows the built-in `len` function with an integer (`len = 1`) and subsequently attempts to call it as a function (`len = len(t)`), which will cause a TypeError. This classic beginner mistake, combined with the unused `import sys` and non-descriptive variable names, strongly indicates human authorship.

---

## Snippet 9 — ID 23 | Python | Verdadeiro: `ai` | Erros: 5/5

```python
# version 1.1.2
 
maxPathLength = 0
maxPathLengthCount = 0
maxPathExample = ""
 
names = [
    "audino", "bagon", "baltoy", "banette", "bidoof", 
    "braviary", "bronzor", "carracosta", "charmeleon", "cresselia", 
    "croagunk", "darmanitan", "deino", "emboar", "emolga", 
    "exeggcute", "gabite", "girafarig", "gulpin", "haxorus", 
    "heatmor", "heatran", "ivysaur", "jellicent", "jumpluff", 
    "kangaskhan", "kricketune", "landorus", "ledyba", "loudred", 
    "lumineon", "lunatone", "machamp", "magnezone", "mamoswine", 
    "nosepass", "petilil", "pidgeotto", "pikachu", "pinsir", 
    "poliwrath", "poochyena", "porygon2", "porygonz", "registeel", 
    "relicanth", "remoraid", "rufflet", "sableye", "scolipede", 
    "scrafty", "seaking", "sealeo", "silcoon", "simisear", 
    "snivy", "snorlax", "spoink", "starly", "tirtouga",
    "trapinch", "treecko", "tyrogue", "vigoroth", "vulpix",
    "wailord", "wartortle", "whismur", "wingull", "yamask"
]
 
def search(part, offset):
    global maxPathLength, maxPathLengthCount, maxPathExample
    if offset > maxPathLength:
        maxPathLength = offset
        maxPathLengthCount = 1
    elif offset == maxPathLength:
        maxPathLengthCount += 1
        maxPathExample = ""
        for i in range(offset):
            if i % 5 == 0:
                maxPathExample += "\n  "
            else:
                maxPathExample += " "
            maxPathExample += part[i]
    lastChar = part[offset - 1][-1]
    for i in range(offset, len
```

### Predições e explicações dos modelos

**deepseek** ✗ → prediu `human` (conf 8)
> The code contains a common human mistake: using integer division `/` instead of floor division `//`, causing a TypeError at runtime, and shadows the built-in `len` as a parameter name.

**llama** ✗ → prediu `human` (conf 7)
> The code contains a simple and typical implementation of the Cantor set, but the variable 'lines' is initialized with a list comprehension that uses 'i' and 'j' as dummy variables, and later 'i' and 'j' are reused as loop variables, which is not a typical practice in AI-generated code and indicates a human fingerprint.

**mimo** ✗ → prediu `human` (conf 6)
> Magic numbers (81, 5) used without explanation are a weak human fingerprint, indicating possible human authorship.

**minimax** ✗ → prediu `human` (conf 6)
> Weak human fingerprints: `len` is used as a parameter name, shadowing the Python built-in (a common beginner mistake AI would avoid); the 2D list is initialized with integers (0) but later assigned empty strings, mixing types in an unprincipled way; the recursive function lacks any docstring or explanatory comments despite the non-trivial Cantor-set logic, suggesting an informal human draft.

**qwen** ✗ → prediu `human` (conf 8)
> The code exhibits strong human beginner fingerprints, including shadowing the built-in `len` function as a parameter, using Python 2-style integer division (`/` instead of `//`), and a logical bug where it uses an empty string `''` instead of a space `' '` to erase characters in a grid. The unused `import sys` is also a common human leftover.

---

## Snippet 10 — ID 27 | Python | Verdadeiro: `ai` | Erros: 5/5

```python
import sys
 
with open("file.txt") as f:
    for line in f:
        print(line)
```

### Predições e explicações dos modelos

**deepseek** ✗ → prediu `human` (conf 8)
> The code contains a clear human fingerprint: the `import math` statement is unused, a common leftover from debugging or iterative development. Additionally, the hardcoded magic number 27720 is used without explanation, suggesting a human approach over a more general computed solution.

**llama** ✗ → prediu `human` (conf 7)
> The code contains a distinctive calculation pattern and manually computed probability values, suggesting human authorship, as well as a specific large fraction (1759/27720.0) that is not obviously simplified.

**mimo** ✗ → prediu `human` (conf 8)
> The code uses a magic number (27720) without explanation, which is a human fingerprint as it indicates an unannotated shortcut or domain-specific knowledge.

**minimax** ✗ → prediu `human` (conf 8)
> Idiosyncratic spacing inside parentheses (e.g., `( "aleph", 1/5.0 )`, `probabilities[ i ]`), the unexplained magic number 27720 (LCM of 5-11), the informal variable name 'decider', and the manual nested-loop cumulative distribution computation instead of using numpy or accumulating incrementally all point to human authorship, likely a statistics homework or learning exercise.

**qwen** ✗ → prediu `human` (conf 9)
> The code features highly idiosyncratic spacing (e.g., `( ( "aleph", 1/5.0 ) )`, `[ i ]`) and an inefficient, un-Pythonic O(N^2) nested loop to calculate cumulative sums instead of using a running total, which are strong indicators of a human beginner's thought process rather than AI generation.

---

## Padrões identificados

Os 10 snippets revelam um padrão sistemático: **código AI gerado em Python que imita fingerprints humanos**.
Os modelos foram enganados pelas seguintes características presentes nesses snippets:

| Padrão de engano | Exemplos encontrados |
|---|---|
| **Anotação de autoria/data** | `@author:`, `Created on Tue Oct 27 2020`, cabeçalhos de IDE |
| **Imports não utilizados** | `import sys`, `from functools import reduce` — sem uso no código |
| **Variáveis mortas** | Variáveis declaradas e nunca usadas, típico de debugging |
| **Docstrings em posições incomuns** | Strings de documentação dentro de funções, não no início |
| **Comentários de arquivo** | `# rc_strdup.py`, `# Query.py` — nomes de arquivo como comentário |
| **Bugs reais** | Lógica que causa loop infinito, erros de índice — interpretados como "humano errou" |
| **Estilo misto** | Mistura de convenções em um mesmo arquivo |
| **Números mágicos** | Constantes sem nome ou explicação |

**Conclusão:** O gerador de AI do dataset H-AIRosettaMP reproduz deliberadamente artefatos de código humano — imports esquecidos, variáveis mortas, cabeçalhos de IDE. Isso cria um ponto cego sistemático em todos os modelos testados: **a presença de fingerprints humanos artificiais é suficiente para enganar o classificador**, independente do modelo ou da capacidade de reasoning.
