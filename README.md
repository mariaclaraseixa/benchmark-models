# Benchmark de Detecção de Código AI vs Humano

Projeto de TCC que avalia a capacidade de modelos de linguagem em distinguir código escrito por humanos de código gerado por IA.

---

## Estrutura

```
benchmark-models/
├── run.py                   # coleta predições dos modelos
├── runner.py                # orquestra N rodadas full com exclusão automática de modelos
├── analyze.py               # gera métricas e gráficos (seções 5.3–5.8 do TCC)
├── report.py                # gera PDF completo com relatório e gráficos
├── ANALISE_RESULTADOS.md    # interpretação dos resultados finais
├── SNIPPETS_CONFUSOS.md     # top 10 snippets que enganaram 100% dos modelos
├── top10_snippets.json      # dados brutos dos snippets confusos (código + explicações)
├── .env                     # chaves de API (nunca vai ao git)
├── .gitignore               # ignora .env, PDFs e backups
└── results/
    ├── complexity_scores.csv              # scores de complexidade do TCC original
    ├── run.log                            # log gerado por run.py
    ├── runner.log                         # log gerado por runner.py
    ├── *_zero_shot.csv                    # predições por modelo e rodada
    ├── *_sanity.csv                       # predições do sanity check
    ├── relatorio_benchmark_{ts}.pdf       # gerado por report.py (ignorado no git)
    └── metrics/                           # gerado por analyze.py
        ├── 5.3_linguagem.{csv,png}
        ├── 5.4_linhas.{csv,png}
        ├── 5.4_palavras.{csv,png}
        ├── 5.5_complexidade.{csv,png}
        ├── 5.6a_unanimidade.csv
        ├── 5.6b_confianca_heatmap.png
        ├── 5.6c_mais_confiante.csv
        ├── 5.7_votacao_majoritaria.{csv,png}
        └── 5.8_falsos_negativos.csv
```

---

## Dependências

```bash
pip install openai anthropic google-genai datasets pandas python-dotenv tqdm requests scikit-learn matplotlib seaborn fpdf2
```

---

## Configuração

Crie um arquivo `.env` na raiz do projeto com as chaves:

```
OPENROUTER_API_KEY=...   # fallback genérico
MINIMAX_API_KEY=...      # minimax/minimax-m3
MODEL2_API_KEY=...       # deepseek/deepseek-v4-flash
MIMO_API_KEY=...         # xiaomi/mimo-v2.5
MODEL4_API_KEY=...       # qwen/qwen3.7-max
MODEL5_API_KEY=...       # nvidia/nemotron (descartado — manter para histórico)
MODEL6_API_KEY=...       # meta-llama/llama-4-maverick
MODEL7_API_KEY=...       # qwen/qwen-2.5-coder-32b-instruct (comentado em run.py)
```

---

## Modelos ativos no benchmark

Todos via OpenRouter. Workers = número de snippets processados em paralelo por modelo.

| Nome | Model ID | Chave | Workers | Reasoning |
|---|---|---|---|---|
| `minimax-m3` | `minimax/minimax-m3` | `MINIMAX_API_KEY` | 5 | Sim |
| `deepseek-v4-flash` | `deepseek/deepseek-v4-flash` | `MODEL2_API_KEY` | 5 | Sim |
| `mimo-v2.5` | `xiaomi/mimo-v2.5` | `MIMO_API_KEY` | 15 | Sim |
| `qwen3.7-max` | `qwen/qwen3.7-max` | `MODEL4_API_KEY` | 15 | Sim |
| `llama-4-maverick` | `meta-llama/llama-4-maverick` | `MODEL6_API_KEY` | 5 | Não |
| ~~`nemotron-ultra-550b`~~ | ~~`nvidia/nemotron-3-ultra-550b-a55b:free`~~ | descartado | — | — |
| ~~`tencent-hy3-preview`~~ | ~~`tencent/hy3-preview`~~ | descartado | — | — |

**Candidato comentado (pronto para ativar):**
- `qwen/qwen-2.5-coder-32b-instruct` — chave `MODEL7_API_KEY`, descomentar bloco em `run.py`

---

## Modelos avaliados e descartados

| Modelo | ID | Motivo |
|---|---|---|
| **Llama Nemotron Rerank VL 1B V2** | `nvidia/llama-nemotron-rerank-vl-1b-v2` | Tipo errado: reranker para RAG, não modelo de chat/instrução. |
| **Qwen3 235B** | `qwen/qwen3-235b-a22b` | Substituído pelo Qwen3.7-Max (mais focado em coding, mais popular no OpenRouter). |
| **GLM 5.2** | `z-ai/glm-5.2` | 5º modelo chinês com reasoning — perfil redundante com os existentes. |
| **Nemotron Ultra 550B** | `nvidia/nemotron-3-ultra-550b-a55b:free` | Tier `:free` instável: ConnectionReset em série, não concluiu 200 snippets em 6h. Mesmo padrão do tencent. |
| **tencent/hy3-preview** | `tencent/hy3-preview` | ConnectionResetError + KeyError 'choices' (HTTP 200 com corpo de erro). Ver problema #4. |

---

## Resultados finais (2026-06-18)

**6 rodadas × 200 snippets × 5 modelos = 6.000 amostras, 5.919 predições válidas.**

| Modelo | Rodadas | Amostras | Acc | Prec | Recall | F1 | FPR | FNR |
|---|---|---|---|---|---|---|---|---|
| `qwen3.7-max` | 6 | 1.200 | **0.558** | 0.645 | 0.233 | 0.342 | 0.125 | 0.767 |
| `deepseek-v4-flash` | 6 | 1.200 | 0.534 | 0.536 | 0.501 | **0.518** | 0.434 | 0.499 |
| `llama-4-maverick` | 6 | 1.200 | 0.529 | 0.623 | 0.136 | 0.224 | **0.082** | **0.864** |
| `minimax-m3` | 6 | 1.200 | 0.526 | 0.566 | 0.232 | 0.329 | 0.179 | 0.768 |
| `mimo-v2.5` | 6 | 1.200 | 0.525 | 0.528 | **0.561** | **0.544** | **0.511** | 0.439 |

Análise interpretada: [ANALISE_RESULTADOS.md](ANALISE_RESULTADOS.md)
Snippets mais confusos: [SNIPPETS_CONFUSOS.md](SNIPPETS_CONFUSOS.md)

---

## run.py — Como funciona

### Dataset
`isThisYouLLM/H-AIRosettaMP` (HuggingFace). Amostragem estratificada: Python e C, 50 snippets por classe por linguagem = **200 snippets por rodada**, seed aleatório a cada run.

### Prompt (zero-shot)
O modelo recebe um prompt de "analista forense de código" que instrui a buscar **impressões digitais humanas**. Se não encontrar nenhuma, classifica como `"ai"`. Resposta obrigatória em JSON:

```json
{"prediction": "human", "confidence": 8, "explanation": "..."}
```

### Modos de execução

**`"sanity"`**: 5 snippets, seed fixo (`seed=0`). Sempre re-executa. Use para verificar APIs.

**`"full"`**: 200 snippets, seed baseado em timestamp. Nunca sobrescreve (nome com timestamp).

### Execução paralela — dois níveis

```
python run.py
  ├── Thread 1 → minimax-m3         ─┐
  ├── Thread 2 → deepseek-v4-flash  │
  ├── Thread 3 → mimo-v2.5          ├── 5 modelos em paralelo
  ├── Thread 4 → qwen3.7-max        │
  └── Thread 5 → llama-4-maverick   ─┘
       └── workers internos por modelo:
             minimax-m3, deepseek, llama  → 5 (MAX_WORKERS global)
             mimo-v2.5, qwen3.7-max       → 15 (override — reasoning lento)
```

### SKIP_MODELS

Modelos em `SKIP_MODELS` são ignorados no modo full. Atualizado automaticamente pelo `runner.py` quando um modelo cai abaixo de 80% de predições válidas.

### Proteções automáticas
- **Rate limit (429):** backoff exponencial, até 3 retentativas (15s → 30s → 60s)
- **Erro de rede:** até 5 retentativas com 10s de espera
- **Content vazio com reasoning:** retry automático sem `reasoning`

---

## Como rodar

### Passo 1 — Sanidade
```python
# run.py linha ~85
RUN_MODE = "sanity"
```
```bash
python run.py
```
Resultado esperado: `validos=5` para todos os modelos.

### Passo 2 — Benchmark completo (5 rodadas automáticas)
```python
RUN_MODE = "full"
```
```bash
python runner.py   # roda 5 rodadas, exclui automaticamente modelos instáveis
```
Ou manualmente:
```bash
python run.py   # rodada 1 → 200 snippets
python run.py   # rodada 2 → 200 snippets diferentes
```

### Passo 3 — Análise detalhada
```bash
python analyze.py
```
Gera CSVs e gráficos em `results/metrics/` (seções 5.3–5.8).

### Passo 4 — Relatório PDF
```bash
python report.py        # lê *_zero_shot.csv
python report.py --sanity   # lê *_sanity.csv
python report.py --all      # lê todos os CSVs
```

---

## report.py — Páginas do PDF

| Página | Conteúdo |
|---|---|
| Capa | Resumo geral: modelos, modo, total de predições |
| Métricas | Tabela: Acc, Precisão, Recall, F1, MCC, AUC, TP, FP, TN, FN por modelo |
| Matrizes de Confusão | Heatmap por modelo |
| Precisão / Recall / F1 | Gráfico de barras comparativo |
| Falsos Positivos / Negativos | Contagem e taxa por modelo |
| Confiança | Boxplot acertos vs erros + histograma |
| Por Linguagem | Acurácia, F1, Precisão, Recall por Python / C |
| Ensemble | Voto majoritário + comparativo individual vs ensemble |
| Erros Detalhados | FP e FN com id, linguagem, confiança e explicação |
| Predições Completas | Tabela completa (verde=acerto, vermelho=erro) |

---

## analyze.py — Seções geradas

| Seção | Análise | Arquivos |
|---|---|---|
| 5.3 | Acurácia por linguagem (Python vs C) | `5.3_linguagem.csv/png` |
| 5.4 | Acurácia por tamanho (quartis de linhas e palavras) | `5.4_linhas.*`, `5.4_palavras.*` |
| 5.5 | Acurácia por complexidade ciclomática | `5.5_complexidade.*` |
| 5.6 | Confiança: unanimidade, heatmaps, ensemble mais confiante | `5.6a/b/c.*` |
| 5.7 | Votação majoritária entre os 5 modelos | `5.7_votacao_majoritaria.*` |
| 5.8 | Falsos negativos (código AI classificado como humano) | `5.8_falsos_negativos.csv` |

---

## Estimativa de custo e tempo — 1000 snippets × 3 modelos (2026-06-18 07h)

*(Estimativa feita antes da adição do Llama e Nemotron, com 3 modelos originais)*

**Custo realizado:** ~$0.60 para as primeiras execuções (sanity + rodada 1 parcial).
**Custo total estimado da execução completa (6 rodadas × 5 modelos × 200):** ~$15–25, dominado pelo reasoning extenso do mimo e qwen3.7.

---

## Problemas encontrados e soluções

### 1. `content: null` nas respostas da API

**Causa:** Campo `content` pode ser `None` quando o modelo ainda não produziu saída de texto.

**Solução:**
```python
content = msg.get("content") or msg.get("reasoning_content") or ""
```

---

### 2. `MAX_TOKENS` insuficiente para modelos de reasoning

**Problema:** Com `MAX_TOKENS = 300`, modelos esgotavam o orçamento inteiro com reasoning.

**Solução final:** `MAX_TOKENS = 8000` + retry sem reasoning quando content vem vazio.

| MAX_TOKENS | minimax | deepseek | tencent |
|---|---|---|---|
| 300 | 0/5 válidos | 1/5 válidos | 0/5 válidos |
| 8000 | 5/5 ✓ | 5/5 ✓ | 3/5 |

---

### 3. Reasoning excessivo em snippets complexos

**Solução:** Retry automático sem `reasoning` quando content vem vazio:
```python
if not content.strip() and use_reasoning:
    payload2 = {k: v for k, v in payload.items() if k != "reasoning"}
    r2 = requests.post(...)
    content = r2.json()["choices"][0]["message"].get("content") or ""
```

---

### 4. `tencent/hy3-preview` e `nemotron-ultra-550b` — endpoints instáveis

Ambos apresentaram `ConnectionResetError(10054)` em série durante execuções longas com reasoning. O nemotron (tier `:free`) não concluiu 200 snippets em 6h na rodada 1. Ambos adicionados a `SKIP_MODELS` e documentados na seção de descartados.

---

### 5. `mimo-v2.5` — latência alta por reasoning extenso

Sanity: ~84s/snippet (vs ~14s dos outros). Solução: `workers=15` por modelo, reduz tempo de ~56 min para ~18 min para 200 snippets.

---

### 6. Instabilidade de rede na rodada 1 (2026-06-18 08h–15h)

Latências anormais: deepseek 334s/snippet, qwen3.7 448s/snippet, minimax 588s/snippet. Rodadas 2–6 voltaram ao normal. Predições não foram afetadas — apenas `elapsed_s` está inflado na rodada 1.

---

### 7. Bugs em `analyze.py` (corrigidos em 2026-06-18)

- `UnicodeEncodeError`: caractere `≤` não suportado no terminal Windows (cp1252) — substituído por `<=` e adicionado `sys.stdout.reconfigure(encoding='utf-8')`.
- `KeyError: 'confidence'`: ensemble na seção 5.7 não possui coluna `confidence` — `_metrics()` atualizado para tratá-la como opcional.

---

## Achados do sanity inicial (minimax + deepseek + mimo, 2026-06-18)

| Modelo | Acc | Conf. média | FP | FN | Latência média |
|---|---|---|---|---|---|
| `minimax-m3` | 0.60 | 7.8 | 0 | 2 | 13.9s |
| `deepseek-v4-flash` | 0.20 | 7.4 | 2 | 2 | 14.2s |
| `mimo-v2.5` | 0.40 | 7.6 | 1 | 2 | 84.0s |

Dois snippets enganaram todos os modelos: AI com `# version 1.2.0` e AI com bug de sintaxe real — ambos interpretados como fingerprints humanos. Ver [SNIPPETS_CONFUSOS.md](SNIPPETS_CONFUSOS.md).
