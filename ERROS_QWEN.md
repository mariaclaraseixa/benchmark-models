# Erros do Melhor Modelo (qwen3.7-max) -- Analise com Codigo Real

**Modelo analisado:** `qwen3.7-max` (melhor acuracia geral: 0.558)
**Erros totais:** 523 em 6 rodadas (448 FN + 75 FP)
**Base:** codigo real recuperado via seed de cada rodada

---

## Visao Geral dos Erros

| Tipo | Total | 4/4 outros acertaram | 3/4 acertaram | Ninguem acertou |
|---|---|---|---|---|
| FN -- AI classificado como `human` | 448 | 4 (0.9%) | 38 (8.5%) | 185 (41.3%) |
| FP -- Humano classificado como `ai` | 75 | 1 (1.3%) | 3 (4.0%) | 30 (40.0%) |

> Em ~40% dos erros de ambos os tipos, nenhum outro modelo acertou. Os erros sao amplamente compartilhados. Os casos onde so o qwen errou sao raros e revelam pontos especificos de fraqueza.

---

## Parte 1 -- Falsos Positivos: Humano classificado como `ai`

### FP 1 | C | Rodada 20260618_174314 | Outros corretos: 4/4

```c
if (condition)
{
   // Some Task
}
 
if (condition)
{
  // Some Task
}
else if (condition2)
{
  // Some Task
}
else
{
  // Some Task
}
```

**qwen3.7-max** ERROU -> prediu `ai` (conf 7)
> The snippet consists entirely of generic structural placeholders ('// Some Task') without any functional code, which is characteristic of AI-generated pedagogical examples or syntax demonstrations. No distinct human fingerprints are present.

**Outros modelos nesta rodada:**
  - `deepseek-v4-flash` -> `human` (CERTO, conf 6): Minor inconsistent indentation (3 spaces vs 2 spaces in the comment) and a stray non-breaking space line after the first block suggest human typing quirks rather than AI-generated uniformity.
  - `llama-4-maverick` -> `human` (CERTO, conf 7): The code snippet exhibits inconsistent indentation within the same file, which is a human fingerprint indicating idiosyncratic or inconsistent style.
  - `mimo-v2.5` -> `human` (CERTO, conf 6): Inconsistent indentation is observed, which is a weak human fingerprint indicating style variation typical of human authorship.
  - `minimax-m3` -> `human` (CERTO, conf 7): Inconsistent indentation within the same file (first if-block uses 3-space indentation, second uses 2-space), a classic human fingerprint of code copy-pasted or merged from different sources over time

**Causa do erro:** Codigo humano minimalista -- ausencia de fingerprints fez o qwen aplicar a regra default (sem fingerprint = AI).

---

### FP 2 | C | Rodada 20260618_081133 | Outros corretos: 3/4

```c
#include <stdio.h>
#include <stdbool.h>
 
int proper_divisors(const int n, bool print_flag)
{
    int count = 0;
 
    for (int i = 1; i < n; ++i) {
        if (n % i == 0) {
            count++;
            if (print_flag)
                printf("%d ", i);
        }
    }
 
    if (print_flag)
        printf("\n");
 
    return count;
}
 
int main(void)
{
    for (int i = 1; i <= 10; ++i) {
        printf("%d: ", i);
        proper_divisors(i, true);
    }
 
    int max = 0;
    int max_i = 1;
 
    for (int i = 1; i <= 20000; ++i) {
        int v = proper_divisors(i, false);
        if (v >= max) {
            max = v;
            max_i = i;
        }
    }
 
    printf("%d with %d divisors\n", max_i, max);
    return 0;
}
```

**qwen3.7-max** ERROU -> prediu `ai` (conf 7)
> No human fingerprints were found; the code is structurally clean, stylistically uniform, and lacks the idiosyncrasies, informal comments, or residue of authorship typical of human-written code.

**Outros modelos nesta rodada:**
  - `deepseek-v4-flash` -> `human` (CERTO, conf 6): The code contains a non-ASCII non-breaking space character in the printf string ("with %d"), a typographical irregularity that serves as a weak human fingerprint.
  - `llama-4-maverick` -> `human` (CERTO, conf 7): The code contains a non-English character in the output string (' %d with %d divisors
'), which is a personal or colloquial fingerprint, and the code structure is simple and clean, but not overly defe
  - `mimo-v2.5` -> `human` (CERTO, conf 7): The code contains a magic number (20000) used in a loop without explanation, which is a weak human fingerprint as it reflects a personal shortcut or idiosyncrasy.
  - `minimax-m3` -> `ai` (ERROU, conf 6): No human fingerprints were found: the code has no version annotations, commented-out experiments, debug prints, inconsistent style, or personal comments. The clean structure, consistent snake_case nam

**Causa do erro:** Codigo humano minimalista -- ausencia de fingerprints fez o qwen aplicar a regra default (sem fingerprint = AI).

---

### FP 3 | Python | Rodada 20260618_150629 | Outros corretos: 3/4

```python
w = "print('w = ' + chr(34) + w + chr(34) + chr(10) + w)"
print('w = ' + chr(34) + w + chr(34) + chr(10) + w)
```

**qwen3.7-max** ERROU -> prediu `ai` (conf 7)
> No human fingerprints were found; the snippet is a perfectly clean, minimal, and anonymous Python quine lacking any idiosyncratic style, comments, debugging artifacts, or structural irregularities.

**Outros modelos nesta rodada:**
  - `deepseek-v4-flash` -> `ai` (ERROU, conf 6): The code is a concise quine with no human fingerprints—no comments, style variations, debugging artifacts, or personal idioms—making it indistinguishable from the featureless default of AI-generated c
  - `llama-4-maverick` -> `human` (CERTO, conf 8): The code snippet is a self-replicating quine, a type of code often used as a programming puzzle or intellectual curiosity, indicating a human author's creativity and playfulness.
  - `mimo-v2.5` -> `human` (CERTO, conf 7): The code uses a magic number with chr(34) and a self-referential trick, which suggests experimental coding and familiarity with low-level details, a weak but distinctive human fingerprint.
  - `minimax-m3` -> `human` (CERTO, conf 6): This is a compact quine using the chr(34)/chr(10) trick to avoid quote escaping — a clever, puzzle-solving idiom typical of human-crafted quines. No comments, scaffolding, or pedagogical framing; the 

**Causa do erro:** Codigo humano minimalista -- ausencia de fingerprints fez o qwen aplicar a regra default (sem fingerprint = AI).

---

### FP 4 | Python | Rodada 20260618_150629 | Outros corretos: 3/4

```python
import random
 
s = ('It is certain', 'It is decidedly so', 'Without a doubt', 'Yes, definitely',
 'You may rely on it', 'As I see it, yes', 'Most likely', 'Outlook good',
 'Signs point to yes', 'Yes', 'Reply hazy, try again', 'Ask again later',
 'Better not tell you now', 'Cannot predict now', 'Concentrate and ask again',
 "Don't bet on it", 'My reply is no', 'My sources say no', 'Outlook not so good',
 'Very doubtful')
 
q_and_a = {}
 
while True:
    question = input('Ask your question:')
    if len(question) == 0: break
 
    if question in q_and_a:
        print('Your question has already been answered')
    else:
        answer = random.choice(s)
        q_and_a[question] = answer
        print(answer)
```

**qwen3.7-max** ERROU -> prediu `ai` (conf 7)
> No human fingerprints were found; the code is structurally clean, stylistically uniform, and lacks the idiosyncrasies, comments, or debugging residue typical of human authorship.

**Outros modelos nesta rodada:**
  - `deepseek-v4-flash` -> `ai` (ERROU, conf 6): No human fingerprints such as idiosyncratic style, personal comments, or debugging artifacts were found; the code is clean and featureless, consistent with AI generation.
  - `llama-4-maverick` -> `human` (CERTO, conf 7): The code contains a simple, informal implementation with a 'while True' loop and a straightforward input handling, which is a common human coding idiom, and it lacks uniform docstrings or excessive de
  - `mimo-v2.5` -> `human` (CERTO, conf 8): Inconsistent quote style in the response tuple, with most entries using single quotes and 'Don't bet on it' using double quotes to handle the apostrophe, a common human idiosyncrasy reflecting practic
  - `minimax-m3` -> `human` (CERTO, conf 7): The terse, single-letter variable name 's' for a 20-element tuple of magic 8-ball answers is a lazy human shortcut unlikely to be chosen by an AI, and the complete absence of docstrings, type hints, d

**Causa do erro:** Codigo humano minimalista -- ausencia de fingerprints fez o qwen aplicar a regra default (sem fingerprint = AI).

---

### FP 5 | Python | Rodada 20260618_081133 | Outros corretos: 0/4

```python
"""Langton's ant implementation."""
from enum import Enum, IntEnum
 
 
class Dir(IntEnum):
    """Possible directions."""
 
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3
 
 
class Color(Enum):
    """Possible colors."""
 
    WHITE = " "
    BLACK = "#"
 
 
def invert_color(grid, x, y):
    """Invert the color of grid at x, y coordinate."""
    if grid[y][x] == Color.BLACK:
        grid[y][x] = Color.WHITE
    else:
        grid[y][x] = Color.BLACK
 
 
def next_direction(grid, x, y, direction):
    """Compute next direction according to current position and direction."""
    if grid[y][x] == Color.BLACK:
        turn_right = False
    else:
        turn_right = True
    direction_index = direction.value
    if turn_right:
        direction_index = (direction_index + 1) % 4
    else:
        direction_index = (direction_index - 1) % 4
    directions = [Dir.UP, Dir.RIGHT, Dir.DOWN, Dir.LEFT]
    direction = directions[direction_index]
    return direction
 
 
def next_position(x, y, direction):
    """Compute next position according to direction."""
    if direction == Dir.UP:
        y -= 1
    elif direction == Dir.RIGHT:
        x -= 1
    elif direction == Dir.DOWN:
        y += 1
    elif direction == Dir.LEFT:
        x += 1
    return x, y
 
 
def print_grid(grid):
    """Display grid."""
    print(80 * "#")
    print("\n".join("".join(v.value for v in row) for row in grid))
 
 
def ant(width, height, max_nb_steps):
    """Langton's ant."""
    grid = [[Color.WHITE] * width for _ in range(height)]
    x = width // 2
    y = height // 2
    direction = Dir.UP
 
    i = 0
    while i < max_nb_steps and 0 <= x < width and 0 <= y < height:
        invert_color(grid, x, y)
        direction = next_direction(grid, x, y, direction)
        x, y = next_position(x, y, direction)
        print_grid(grid)
        i += 1
 
 
if __name__ == "__main__":
    ant(width=75, height=52, max_nb_steps=12000)
```

**qwen3.7-max** ERROU -> prediu `ai` (conf 8)
> No human fingerprints are present; instead, the code displays clear AI markers including uniformly applied, brief docstrings for every class and function, and a standard `if __name__ == '__main__':` demonstration scaffold.

**Outros modelos nesta rodada:**
  - `deepseek-v4-flash` -> `ai` (ERROU, conf 8): No human fingerprints (e.g., idiosyncratic style, personal comments, debug artifacts) are present; the code instead shows AI-like uniformity with pedagogical docstrings on every function and a clean, 
  - `llama-4-maverick` -> `ai` (ERROU, conf 7): No human fingerprints were found; the code has a clean and uniform structure, with some AI fingerprints such as the 'Example usage:' equivalent in the `if __name__ == "__main__":` block.
  - `mimo-v2.5` -> `ai` (ERROU, conf 7): nan
  - `minimax-m3` -> `ai` (ERROU, conf 7): Every function has a uniform docstring that restates what the code does (e.g., 'Invert the color of grid at x, y coordinate.', 'Display grid.', 'Langton's ant.'), including trivial ones—a classic AI p

**Causa do erro:** Codigo humano minimalista -- ausencia de fingerprints fez o qwen aplicar a regra default (sem fingerprint = AI).

---

### FP 6 | Python | Rodada 20260618_081133 | Outros corretos: 0/4

```python
def addsub(x, y):
  return x + y, x - y
```

**qwen3.7-max** ERROU -> prediu `ai` (conf 6)
> No human fingerprints were found in this extremely brief and featureless snippet; it lacks the idiosyncrasies, comments, or structural residue typical of human-authored code, defaulting to the clean, anonymous style of AI generation.

**Outros modelos nesta rodada:**
  - `deepseek-v4-flash` -> `ai` (ERROU, conf 6): No human fingerprints found; the code is clean and minimal with no authorial residue.
  - `llama-4-maverick` -> `ai` (ERROU, conf 6): No human fingerprints were found in the code snippet.
  - `mimo-v2.5` -> `ai` (ERROU, conf 6): No human fingerprints were observed; the code is structurally clean, minimal, and lacks any comments, annotations, or idiosyncratic styles that indicate personal authorship.
  - `minimax-m3` -> `ai` (ERROU, conf 6): No human fingerprints found in this extremely minimal snippet; the code is clean and anonymous with no annotations, comments, or stylistic irregularities. The function name 'addsub' is a generic conca

**Causa do erro:** Codigo humano minimalista -- ausencia de fingerprints fez o qwen aplicar a regra default (sem fingerprint = AI).

---

## Parte 2 -- Falsos Negativos: AI classificado como `human`

### FN 1 | Python | Rodada 20260618_150629 | Outros corretos: 4/4

```python
print("Enter a string: ")
s = input()
print("Enter an integer: ")
i = int(input())
print("Enter a real number: ")
f = float(input())
print("String  = ", s)
print("Integer = ", i)
print("Float   = ", f)
```

**qwen3.7-max** ERROU -> prediu `human` (conf 7)
> The manual padding of spaces within the string literals to perfectly align the equals signs in the console output is a classic human workaround, whereas AI typically relies on f-string formatting or ignores alignment entirely.

**Outros modelos nesta rodada:**
  - `deepseek-v4-flash` -> `ai` (CERTO, conf 6): No human fingerprints found; the code is structurally clean, stylistically uniform, and lacks any debugging residues, idiosyncrasies, or annotations.
  - `llama-4-maverick` -> `ai` (CERTO, conf 7): No human fingerprints were found; the code has a clean and uniform structure.
  - `mimo-v2.5` -> `ai` (CERTO, conf 6): No human fingerprints such as comments, idiosyncratic style, or annotations were observed; the code is structurally clean and anonymous.
  - `minimax-m3` -> `ai` (CERTO, conf 6): No human fingerprints found; the code is clean, stylistically uniform, and free of any authorship traces, debugging artifacts, or idiosyncratic comments. The minimal, boilerplate-like structure (promp

**Causa do erro:** Padrao tecnico especifico interpretado como workaround humano -- AI pode reproduzir idiomas tecnicos sofisticados.

---

### FN 2 | Python | Rodada 20260618_170235 | Outros corretos: 4/4

```python
import java.util.Arrays;

public class CompareListOfStrings {

    public static void main(String[] args) {
        String[][] arr = {{"AA", "AA", "AA", "AA"}, {"AA", "ACB", "BB", "CC"}};
        for (String[] a : arr) {
            System.out.println(Arrays.toString(a));
            System.out.println(Arrays.stream(a).distinct().count() < 2);
            System.out.println(Arrays.equals(Arrays.stream(a).distinct().sorted().toArray(), a));
        }
    }
}
```

**qwen3.7-max** ERROU -> prediu `human` (conf 7)
> The snippet exhibits strong characteristics of a human-written scratchpad or StackOverflow test case, featuring highly specific hardcoded test arrays and raw, unextracted stream operations in the main method without any explanatory comments or method encapsulation.

**Outros modelos nesta rodada:**
  - `deepseek-v4-flash` -> `ai` (CERTO, conf 6): No human fingerprints detected; the code is clean, simple, and lacks any idiosyncratic or personal markers, consistent with AI-generated code.
  - `llama-4-maverick` -> `ai` (CERTO, conf 7): No human fingerprints were found; the code is clean and lacks idiosyncrasies, but it contains a simple and somewhat generic example usage.
  - `mimo-v2.5` -> `ai` (CERTO, conf 7): No human fingerprints such as comments, inconsistencies, or debug artifacts were found; the code exhibits AI markers like demonstration scaffolding with hardcoded test arrays and pedagogical structure
  - `minimax-m3` -> `ai` (CERTO, conf 6): No human fingerprints found: no version/author annotations, no commented-out code, no debug prints, no inconsistent style, no colloquial comments, and no idiosyncratic idioms. The code is clean, minim

**Causa do erro:** Valor hardcoded ou nome especifico interpretado como evidencia de sessao humana -- AI pode gerar constantes especificas contextualmente.

---

### FN 3 | Python | Rodada 20260618_174314 | Outros corretos: 4/4

```python
def fib(n):
    if n<2:
        return n
    else:
        return fib(n-1)+fib(n-2)
```

**qwen3.7-max** ERROU -> prediu `human` (conf 6)
> The lack of PEP 8 spacing around operators (e.g., `n<2`, `fib(n-1)+fib(n-2)`) is a common human typing artifact in quick scripts or competitive programming, whereas AI models typically default to properly spaced, auto-formatted code.

**Outros modelos nesta rodada:**
  - `deepseek-v4-flash` -> `ai` (CERTO, conf 6): The code is a minimal, clean recursive Fibonacci function with no comments, idiosyncrasies, or any human fingerprints such as debugging artifacts, style inconsistencies, or personal annotations.
  - `llama-4-maverick` -> `ai` (CERTO, conf 6): No human fingerprints were found in the code snippet; it is a clean and straightforward implementation of the Fibonacci function.
  - `mimo-v2.5` -> `ai` (CERTO, conf 7): No human fingerprints were found; the code is structurally clean, minimal, and anonymous, lacking any personal or idiosyncratic elements.
  - `minimax-m3` -> `ai` (CERTO, conf 6): The code is a textbook-clean recursive Fibonacci with no human fingerprints: no comments, no debugging artifacts, no annotations, no version markers, and no stylistic idiosyncrasies. The minimal, feat

**Causa do erro:** Estilo nao-padrao interpretado como fingerprint humano -- AI pode gerar codigo que viola PEP 8 ou usa estilo misto.

---

### FN 4 | Python | Rodada 20260618_174314 | Outros corretos: 4/4

```python
2.3         # Normal floating point literal
3.          # Equivalent to 3.0 (3 would be interpreted as an integer)
2f64        # The type (in this case f64, a 64-bit floating point number) may be appended to the value
1_000.2_f32 # Underscores may appear anywhere in the number for clarity.
```

**qwen3.7-max** ERROU -> prediu `human` (conf 7)
> The snippet uses '#' for comments alongside Rust-style floating-point literals (which natively use '//'), a common idiosyncratic fingerprint of a human taking personal notes or writing a cheat sheet and mixing comment conventions from other languages like Python or shell scripts.

**Outros modelos nesta rodada:**
  - `deepseek-v4-flash` -> `ai` (CERTO, conf 7): No human fingerprints found; the snippet is a clean, pedagogical example with explanatory comments, typical of AI-generated instructional content.
  - `llama-4-maverick` -> `ai` (CERTO, conf 7): No human fingerprints were found; the code appears to be a clean, pedagogical explanation of floating point literals.
  - `mimo-v2.5` -> `ai` (CERTO, conf 7): No human fingerprints found; the code contains pedagogical comments that uniformly explain each literal, characteristic of AI-generated documentation or demonstration scaffolding.
  - `minimax-m3` -> `ai` (CERTO, conf 8): Strong AI fingerprints present: uniformly pedagogical comments that restate what each floating-point literal does (e.g., 'Equivalent to 3.0', 'may be appended to the value'), forming a clean example-d

**Causa do erro:** Estilo nao-padrao interpretado como fingerprint humano -- AI pode gerar codigo que viola PEP 8 ou usa estilo misto.

---

### FN 5 | Python | Rodada 20260618_081133 | Outros corretos: 3/4

```python
from typing import List
import re
 
def ms(txt: str, sep: List[str]) -> List[str]:
    ans = []
    while txt:
        sep_match = ""
        pos_match = len(txt)
        for s in sep:
            p = txt.find(s)
            if p >= 0 and p < pos_match:
                sep_match = s
                pos_match = p
        ans.append(txt[:pos_match])
        txt = txt[pos_match + len(sep_match):]
    return ans
 
if __name__ == "__main__":
    print(ms("a!===b=!=c", ["==", "!=", "="]))
```

**qwen3.7-max** ERROU -> prediu `human` (conf 8)
> The presence of an unused `import re` alongside a manually implemented string splitting algorithm strongly suggests a human author who initially considered using regex but switched to a manual loop without cleaning up the imports. Terse, non-descriptive variable and function names like `ans`, `txt`, and `ms` also point away from AI generation.

**Outros modelos nesta rodada:**
  - `deepseek-v4-flash` -> `ai` (CERTO, conf 6): No human fingerprints such as idiosyncratic style, personal comments, or debugging artifacts were found; the code is structurally clean and uses a standard pattern.
  - `llama-4-maverick` -> `ai` (CERTO, conf 7): The code contains 'if __name__ == "__main__":' around non-trivial code, which is a demonstration scaffolding characteristic of AI fingerprints, and lacks distinct human fingerprints.
  - `mimo-v2.5` -> `ai` (CERTO, conf 7): No human fingerprints such as comments, idiosyncrasies, or debug artifacts were found; the code is structurally clean with a demonstration scaffolding via the 'if __name__ == "__main__":' block.
  - `minimax-m3` -> `human` (ERROU, conf 7): Cryptic function name 'ms' and competitive-programming-style variable name 'ans' suggest informal human authorship; the complete absence of docstrings or comments (which AI almost always adds) combine

**Causa do erro:** Import nao utilizado interpretado como fingerprint humano -- o dataset H-AIRosettaMP inclui AI que deliberadamente imita codigo com imports mortos.

---

### FN 6 | Python | Rodada 20260618_081133 | Outros corretos: 3/4

```python
from math import sqrt
 
def is_prime(n):
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return n == 2
    if n % 3 == 0:
        return n == 3
    d = 5
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
        if n % d == 0:
            return False
        d += 4
    return True
 
def count_prime_factors(n):
    count = 0
    f = 2
    if n == 1:
        return 0
    if is_prime(n):
        return 1
    while True:
        if n % f == 0:
            count += 1
            n //= f
            if n == 1:
                return count
            if is_prime(n):
                f = n
        elif f >= 3:
            f += 2
        else:
            f = 3
 
MAX = 120
print("The attractive numbers up to and including", MAX, "are:")
count = 0
for i in range(1, MAX + 1):
    n = count_prime_factors(i)
    if is_prime(n):
        print(i, end=" ")
        count += 1
        if count % 20 == 0:
            print()
print()
```

**qwen3.7-max** ERROU -> prediu `human` (conf 8)
> The code contains an unused import (`from math import sqrt`), which is a classic artifact of refactoring the prime-checking loop to use `d * d <= n` without removing the original import. Additionally, the `is_prime` function contains slightly redundant logic (`return n == 2` immediately after an explicit `n == 2` check), and the script features idiosyncratic row-formatting logic typical of human s

**Outros modelos nesta rodada:**
  - `deepseek-v4-flash` -> `ai` (CERTO, conf 7): No human fingerprints such as personal comments, inconsistent style, or debug artifacts; the code is clean, consistent, and lacks distinctive residues of human authorship.
  - `llama-4-maverick` -> `human` (ERROU, conf 8): The code contains distinctive algorithmic choices and optimizations, such as the incrementing pattern in the `is_prime` function and the handling of factors in `count_prime_factors`, which suggest a h
  - `mimo-v2.5` -> `ai` (CERTO, conf 6): No human fingerprints such as comments, inconsistent style, or idiosyncratic elements were found; the code is structurally clean and anonymous.
  - `minimax-m3` -> `ai` (CERTO, conf 7): No human fingerprints found: no comments, no personal annotations, no debug artifacts, no style inconsistencies. The code is clean and anonymous, following a textbook/Rosetta Code pattern for the 'att

**Causa do erro:** Import nao utilizado interpretado como fingerprint humano -- o dataset H-AIRosettaMP inclui AI que deliberadamente imita codigo com imports mortos.

---

### FN 7 | Python | Rodada 20260618_081133 | Outros corretos: 3/4

```python
import re
import operator

def wc(filename):
    with open(filename) as f:
        text = f.read()
        words = re.findall(r'[A-Za-zÀ-ÿ]+', text.lower())
        word_count = {}
        for word in words:
            if word in word_count:
                word_count[word] += 1
            else:
                word_count[word] = 1
        sorted_word_count = sorted(word_count.items(), key=operator.itemgetter(1))
        return sorted_word_count[-10:]

if __name__ == '__main__':
    print(wc('135-0.txt'))
```

**qwen3.7-max** ERROU -> prediu `human` (conf 8)
> The hardcoded, highly specific filename '135-0.txt' (characteristic of a Project Gutenberg download) combined with the French-accent-inclusive regex '[A-Za-zÀ-ÿ]+' strongly indicates a human author testing the script on a specific local file, rather than an AI using generic placeholder names.

**Outros modelos nesta rodada:**
  - `deepseek-v4-flash` -> `ai` (CERTO, conf 6): No human fingerprints such as idiosyncratic style, personal comments, or debugging artifacts are present; the code is clean, uniform, and lacks the residue of authorship, consistent with AI generation
  - `llama-4-maverick` -> `ai` (CERTO, conf 7): The presence of a boilerplate `if __name__ == '__main__':` block around a simple example usage is a characteristic AI fingerprint, and no strong human fingerprints were found.
  - `mimo-v2.5` -> `ai` (CERTO, conf 7): No human fingerprints were found; the code includes boilerplate demonstration scaffolding with an if __name__ == '__main__': block, typical of AI-generated examples.
  - `minimax-m3` -> `human` (ERROU, conf 8): Strong human fingerprints: hardcoded local file '135-0.txt' (a Project Gutenberg text ID), manual dictionary counting loop instead of using the more idiomatic `collections.Counter`, and a terse, comme

**Causa do erro:** Valor hardcoded ou nome especifico interpretado como evidencia de sessao humana -- AI pode gerar constantes especificas contextualmente.

---

### FN 8 | C | Rodada 20260618_081133 | Outros corretos: 3/4

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <gmp.h>
 
int main(void)
{
    mpz_t n, e, d, pt, ct, dc;
    mpz_init_set_str(n, "9516311845790656153499716760847001433441357", 10);
    mpz_init_set_str(e, "65537", 10);
    mpz_init_set_str(d, "5617843187844953170308463622230283376298685", 10);
 
    const char *plaintextstring = "Hello, Rosetta!";
    mpz_init_set_str(pt, plaintextstring, 10);
    if (mpz_cmp(pt, n) > 0)
        return 1;
 
    mpz_init(ct);
    mpz_powm(ct, pt, e, n);
    gmp_printf("Encoded:  %Zd\n", ct);
 
    mpz_init(dc);
    mpz_powm(dc, ct, d, n);
    gmp_printf("Decoded:  %Zd\n", dc);
 
    char *decoded;
    size_t decoded_len;
    decoded = mpz_get_str(NULL, 10, dc);
    decoded_len = strlen(decoded);
    printf("As ASCII: %s\n", decoded);
    free(decoded);
 
    mpz_clear(n);
    mpz_clear(e);
    mpz_clear(d);
    mpz_clear(pt);
    mpz_clear(ct);
    mpz_clear(dc);
 
    return 0;
}
```

**qwen3.7-max** ERROU -> prediu `human` (conf 9)
> The code contains the specific string "Hello, Rosetta!", a hallmark of Rosetta Code contributions, and exhibits a classic human conceptual error by attempting to parse and format an ASCII string as a base-10 integer using GMP, a mistake AI models typically avoid.

**Outros modelos nesta rodada:**
  - `deepseek-v4-flash` -> `ai` (CERTO, conf 6): No human fingerprints found; the code is clean, stylistically uniform, and lacks any idiosyncrasies, comments, or debugging artifacts.
  - `llama-4-maverick` -> `human` (ERROU, conf 7): The code contains a hardcoded plaintext string 'Hello, Rosetta!' and uses a specific value for 'e' (65537), which are common practices in example or test code written by humans.
  - `mimo-v2.5` -> `ai` (CERTO, conf 7): No human fingerprints were found; the code is structurally clean, uniform, and lacks personal comments or idiosyncrasies, aligning with typical AI-generated patterns.
  - `minimax-m3` -> `ai` (CERTO, conf 6): No human fingerprints found: no comments, no TODOs, no debugging artifacts, no version annotations, no inconsistent style. The code exhibits AI-like characteristics: clean pedagogical output formattin

**Causa do erro:** Valor hardcoded ou nome especifico interpretado como evidencia de sessao humana -- AI pode gerar constantes especificas contextualmente.

---

### FN 9 | Python | Rodada 20260618_081133 | Outros corretos: 0/4

```python
import os
import time
import math
 
pi = math.pi
 
cols = os.get_terminal_size().columns
rows = os.get_terminal_size().lines
 
t = time.time()
 
for i in range(rows):
	for j in range(cols):
		print(chr(219), end='')
 
input()
```

**qwen3.7-max** ERROU -> prediu `human` (conf 8)
> The snippet contains clear human fingerprints, including completely unused imports and variables (`math`, `pi`, `time`, `t`) that suggest leftover experimentation, the use of the magic number `chr(219)` for an extended ASCII block character, and the classic `input()` call at the end to prevent the console window from closing immediately.

**Outros modelos nesta rodada:**
  - `deepseek-v4-flash` -> `human` (ERROU, conf 8): The code contains unused variables (pi and t) that appear to be leftovers from debugging or early development, a common human fingerprint not typical of AI-generated code.
  - `llama-4-maverick` -> `human` (ERROU, conf 7): The code contains a simple and somewhat esoteric use of `os.get_terminal_size()` and `chr(219)`, suggesting a specific, possibly experimental or creative goal, and the presence of a bare `input()` at 
  - `mimo-v2.5` -> `human` (ERROU, conf 6): Found weak human fingerprints: an unused variable 't = time.time()' suggesting leftover debug or dead code, and the use of magic number 'chr(219)' without explanation.
  - `minimax-m3` -> `human` (ERROU, conf 8): Unused leftover variables `pi = math.pi` and `t = time.time()` are classic dead-code artifacts from a human's experimental session, and `chr(219)` is a magic number used without explanation. The missi

**Causa do erro:** Import nao utilizado interpretado como fingerprint humano -- o dataset H-AIRosettaMP inclui AI que deliberadamente imita codigo com imports mortos.

---

### FN 10 | Python | Rodada 20260618_081133 | Outros corretos: 0/4

```python
import time
d = "March 7 2009 7:30pm EST"
t = time.strptime(d, "%B %d %Y %I:%M%p %Z")
print time.strftime("%a, %d %b %Y %H:%M:%S +0000", t)
print time.strftime("%Z", t)
 
new = time.mktime(t) + 12*3600
print time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.localtime(new))
print time.strftime("%Z", time.localtime(new))
 
# another timezone
import pytz
zone = pytz.timezone('Asia/Shanghai')
remote = zone.fromutc(time.localtime(new))
print time.strftime("%a, %d %b %Y %H:%M:%S +0000", remote)
print remote.tzname()
```

**qwen3.7-max** ERROU -> prediu `human` (conf 9)
> The snippet uses Python 2 `print` statements and contains a highly specific hardcoded date from 2009, alongside magic numbers (`12*3600`) and short variable names typical of a quick scratchpad script or forum post from that era. AI models almost universally default to Python 3 syntax and avoid such specific, dated hardcoded strings unless explicitly prompted.

**Outros modelos nesta rodada:**
  - `deepseek-v4-flash` -> `human` (ERROU, conf 8): Uses Python 2 style print statements without parentheses and a non-standard strptime format with %Z (which is not supported by strptime), indicating human experimental or debug code.
  - `llama-4-maverick` -> `human` (ERROU, conf 8): The presence of commented code and an additional 'another timezone' section with a different library (pytz) suggests a debugging or exploratory process, indicative of human-written code.
  - `mimo-v2.5` -> `human` (ERROU, conf 7): The informal comment '# another timezone' is a colloquial, personal annotation that serves as a weak human fingerprint, indicating authorship by a human rather than AI.
  - `minimax-m3` -> `human` (ERROU, conf 8): Python 2 print-statement syntax, magic number 12*3600 without explanation, informal '# another timezone' comment, and a hardcoded specific date ('March 7 2009 7:30pm EST') all point to human-authored 

**Causa do erro:** Valor hardcoded ou nome especifico interpretado como evidencia de sessao humana -- AI pode gerar constantes especificas contextualmente.

---

## Parte 3 -- Sintese dos Padroes de Erro

### Falsos Positivos (humano -> AI)

| Padrao | Descricao | Freq. estimada |
|---|---|---|
| Codigo minimalista | Sem marcas de autoria -- qwen aplica default (sem fingerprint = AI) | ~60% |
| Comentarios didaticos | Comentarios inline interpretados como AI pedagogico | ~25% |
| Codigo funcional compacto | Implementacoes curtas e elegantes sem idiossincrasias | ~15% |

### Falsos Negativos (AI -> humano)

| Padrao | Descricao | Freq. estimada |
|---|---|---|
| Import nao utilizado | AI com import morto -- fingerprint falso mais comum | ~35% |
| Valor hardcoded especifico | AI usa nomes/numeros especificos que parecem contexto humano | ~20% |
| Estilo inconsistente | AI viola PEP 8 ou usa estilo misto | ~15% |
| Comentario informal | AI gera comentarios coloquiais ou em primeira pessoa | ~15% |
| Bug ou falha logica | AI comete erros que parecem humanos | ~15% |

### Quando os outros modelos acertam e o qwen erra

- **FN exclusivos do qwen (4/4 outros acertaram):** apenas 4 casos em 448 FN -- qwen e facilmente enganado por AI que usa padroes especificos (spacing, alinhamento, nomes contextuais)
- **FP exclusivo do qwen (4/4 outros acertaram):** 1 caso em 75 FP -- codigo C com comentarios placeholder que qwen interpretou como AI
- **Conclusao:** qwen erra principalmente junto com os outros modelos. Seus erros unicos revelam que ele interpreta os fingerprints do prompt com mais literalidade -- qualquer ausencia de marca humana vira AI, e qualquer marca humana vira human, mesmo quando sao artificiais.