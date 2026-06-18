# Análise de Resultados — Benchmark de Detecção de Código AI vs Humano

**Data:** 2026-06-18
**Base:** 4 rodadas full, ~800–990 amostras por modelo, seed diferente a cada rodada
**Modelos:** minimax-m3, deepseek-v4-flash, mimo-v2.5, qwen3.7-max, llama-4-maverick
**Dataset:** `isThisYouLLM/H-AIRosettaMP` — Python e C, balanceado 50% AI / 50% humano

---

## 1. Acurácia e métricas gerais

| Modelo | Acc | Precisão | Recall | F1 | n válidas |
|---|---|---|---|---|---|
| **qwen3.7-max** | **0.562** | 0.645 | 0.244 | 0.354 | 983 |
| llama-4-maverick | 0.533 | **0.642** | 0.141 | 0.232 | 994 |
| deepseek-v4-flash | 0.528 | 0.530 | 0.501 | 0.515 | 990 |
| mimo-v2.5 | 0.527 | 0.530 | **0.570** | **0.549** | 979 |
| minimax-m3 | 0.522 | 0.561 | 0.235 | 0.331 | 779 |

> Todos os modelos ficam entre 52–56% em uma tarefa binária onde o acaso daria 50%. A tarefa de detecção de autoria de código zero-shot está no limiar do acaso para todos os modelos testados.

---

## 2. Viés sistemático de predição

O dataset é balanceado (~50% AI, ~50% humano), mas a distribuição de predições revela viés forte:

| Modelo | Prediz AI | Prediz Human |
|---|---|---|
| llama-4-maverick | **11.0%** | 89.0% |
| qwen3.7-max | 18.6% | 81.4% |
| minimax-m3 | 21.1% | 78.9% |
| deepseek-v4-flash | 47.3% | 52.7% |
| mimo-v2.5 | **54.3%** | 45.7% |

**Interpretação:** O prompt instrui os modelos a buscar *fingerprints humanos* e só classificar como AI na ausência deles. Isso cria um viés de confirmação: ao não encontrar evidências humanas claras, a maioria dos modelos ainda opta por `human` em vez de `ai`. Mimo é o único que vai na direção oposta — ligeiramente mais desconfiado.

---

## 3. Acurácia por classe — quem detecta AI vs quem reconhece humanos

| Modelo | Acerto em código AI | Acerto em código humano |
|---|---|---|
| mimo-v2.5 | **57.0%** | 48.3% |
| deepseek-v4-flash | 50.1% | 55.6% |
| qwen3.7-max | 24.4% | **87.0%** |
| minimax-m3 | 23.5% | 81.4% |
| llama-4-maverick | **14.1%** | **92.2%** |

**Padrão emergente — dois perfis opostos:**

- **Perfil "conservador" (llama, qwen, minimax):** excelentes em reconhecer código humano (81–92%), mas quase cegos para código AI (14–24%). Raramente acusam código humano, mas deixam a maioria do código AI passar.
- **Perfil "agressivo" (mimo, deepseek):** mais equilibrados entre as classes, mas erram mais em código humano. Mimo é o único com recall superior a 50% em código AI.

---

## 4. Falsos positivos e falsos negativos

| Modelo | TP | FP | TN | FN | FPR | FNR |
|---|---|---|---|---|---|---|
| mimo-v2.5 | 282 | 250 | 234 | 213 | **51.7%** | 43.0% |
| deepseek-v4-flash | 248 | 220 | 275 | 247 | 44.4% | 49.9% |
| minimax-m3 | 92 | 72 | 315 | 300 | 18.6% | **76.5%** |
| qwen3.7-max | 118 | 65 | 434 | 366 | 13.0% | 75.6% |
| llama-4-maverick | 70 | 39 | 460 | 425 | **7.8%** | **85.9%** |

> **FPR** = taxa de código humano classificado erroneamente como AI ("acusação indevida")
> **FNR** = taxa de código AI classificado erroneamente como humano ("AI que passa despercebido")

**Quem mais acusa humanos indevidamente:** mimo (51.7%) e deepseek (44.4%)

**Quem mais deixa AI passar:** llama (85.9%), minimax (76.5%), qwen (75.6%)

**Implicação prática:** em um cenário real de detecção de plágio ou autoria, llama e qwen teriam altíssima taxa de falsos negativos — a maioria do código AI passaria como humano. Mimo e deepseek são mais "paranóicos" mas também acusam mais código legítimo.

---

## 5. Calibração de confiança

| Modelo | Conf. média | Conf. acertos | Conf. erros | Diferença |
|---|---|---|---|---|
| qwen3.7-max | **8.13** | 8.2 | 8.1 | 0.1 |
| minimax-m3 | 7.35 | 7.4 | 7.3 | 0.1 |
| llama-4-maverick | 7.32 | 7.4 | 7.2 | 0.2 |
| deepseek-v4-flash | 7.13 | 7.1 | 7.1 | 0.0 |
| mimo-v2.5 | 7.08 | 7.1 | 7.1 | 0.0 |

**Achado crítico: a confiança não está calibrada em nenhum modelo.** A diferença de confiança entre acertos e erros é de 0.0 a 0.2 pontos — estatisticamente insignificante. Os modelos erram com a mesma certeza com que acertam.

Consequência: o campo `confidence` do JSON de resposta **não pode ser usado como indicador de confiabilidade** da predição. Um modelo com confidence=9 pode estar tão errado quanto um com confidence=6.

**qwen3.7-max é o mais confiante (média 8.13) mas não é o mais preciso** — padrão de overconfidence: alta segurança nas respostas independente de estar certo ou errado.

---

## 6. Desempenho por linguagem

| Modelo | Acc Python | Acc C | Diferença (C - Python) |
|---|---|---|---|
| qwen3.7-max | 0.526 | **0.598** | +0.072 |
| deepseek-v4-flash | 0.497 | 0.560 | +0.063 |
| mimo-v2.5 | 0.509 | 0.545 | +0.036 |
| minimax-m3 | 0.508 | 0.538 | +0.030 |
| llama-4-maverick | **0.553** | 0.514 | −0.039 |

4 de 5 modelos performam melhor em C do que Python. Apenas llama tem resultado invertido.

**Hipótese:** código C humano carrega fingerprints mais distintivos — aritmética de ponteiros, macros, nomes crípticos, estilo variável entre programadores. Código Python humano e AI convergem mais em estilo (PEP 8, docstrings), dificultando a distinção. Llama foge ao padrão: sua estratégia ultra-conservadora (sempre human) pode ter resultado estatístico diferente por acidente de amostragem.

---

## 7. Síntese comparativa

### Qual modelo traz mais acertos?
**qwen3.7-max** tem a maior acurácia geral (56.2%), mas seus acertos concentram-se em código humano. Em termos de F1, **mimo-v2.5** (0.549) e **deepseek-v4-flash** (0.515) são os mais equilibrados.

### Quem erra mais?
**minimax-m3** tem a menor acurácia geral (52.2%) e o segundo maior FNR (76.5%).

### Quem acusa humanos indevidamente?
**mimo-v2.5** é o campeão de falsos positivos (FPR 51.7%) — classifica código humano como AI em mais da metade dos casos. **deepseek** vem em segundo (44.4%).

### Quem deixa AI passar?
**llama-4-maverick** detecta apenas 14.1% do código AI — passa 85.9% sem detectar. É o modelo mais "confiante" em humanos.

### Quem tem melhor equilíbrio?
**deepseek-v4-flash** tem a distribuição de predições mais próxima do 50/50 real do dataset (47.3% AI vs 52.7% human) e desempenho similar entre as classes.

---

## 8. Observações para o TCC

1. **Desempenho próximo ao acaso** em todos os modelos indica que a tarefa de detecção de autoria de código via zero-shot é um problema aberto e genuinamente difícil.

2. **O design do prompt influencia o viés de predição.** A instrução "procure fingerprints humanos; ausência = AI" funciona melhor no papel do que na prática — a maioria dos modelos ainda prefere `human` mesmo sem encontrar fingerprints.

3. **Código AI é eficiente em imitar código humano.** FNR altos em todos os modelos (43–86%) sugerem que o código do dataset H-AIRosettaMP não possui fingerprints de AI suficientemente distintivos para o método zero-shot detectar.

4. **A confiança declarada pelos modelos é irrelevante** para distinguir acertos de erros — não deve ser usada como critério de filtragem ou ponderação.

5. **C é mais distinguível que Python** para 4 dos 5 modelos — pode ser um fator de análise por linguagem relevante para as seções 5.3 e 5.4 do TCC.

6. **Dois perfis claros de comportamento:** conservadores (llama, qwen, minimax) que preservam humanos e agressivos (mimo, deepseek) que detectam mais AI a custo de mais falsos positivos. Esta divisão pode ser explorada na discussão de trade-offs de precisão × recall.
