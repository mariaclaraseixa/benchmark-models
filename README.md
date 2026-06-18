# Benchmark de Detecção de Código AI vs Humano

Projeto de TCC que avalia a capacidade de modelos de linguagem em distinguir código escrito por humanos de código gerado por IA.

---

## Estrutura

```
benchmark-models/
├── run.py                   # coleta predições dos modelos
├── analyze.py               # gera métricas e gráficos (seções 5.3–5.8 do TCC)
├── report.py                # gera PDF completo com relatório e gráficos
├── .env                     # chaves de API (nunca vai ao git)
├── .gitignore               # ignora .env e results/
└── results/
    ├── complexity_scores.csv              # scores de complexidade do TCC original
    ├── run.log                            # log gerado por run.py (com tempos por amostra)
    ├── relatorio_benchmark_{ts}.pdf       # gerado por report.py
    └── metrics/                           # gerado por analyze.py
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
OPENROUTER_API_KEY=...        # fallback genérico
MINIMAX_API_KEY=...           # minimax/minimax-m3
MODEL2_API_KEY=...            # deepseek/deepseek-v4-flash
MODEL3_API_KEY=...            # tencent/hy3-preview
```

---

## Modelos configurados

Todos via OpenRouter com `reasoning: true`:

| Nome | Model ID | Chave |
|---|---|---|
| `minimax-m3` | `minimax/minimax-m3` | `MINIMAX_API_KEY` |
| `deepseek-v4-flash` | `deepseek/deepseek-v4-flash` | `MODEL2_API_KEY` |
| `tencent-hy3-preview` | `tencent/hy3-preview` | `MODEL3_API_KEY` |

---

## run.py — Como funciona

### Dataset
`isThisYouLLM/H-AIRosettaMP` (HuggingFace). Amostragem estratificada: Python e C, 50 snippets por classe por linguagem = **200 snippets por rodada**.

### Prompt (zero-shot)
O modelo recebe um prompt de "analista forense de código" que instrui a buscar **impressões digitais humanas** (comentários pessoais, debug esquecido, estilo inconsistente, etc.). Se não encontrar nenhuma, classifica como `"ai"`. Resposta obrigatória em JSON:

```json
{"prediction": "human", "confidence": 8, "explanation": "..."}
```

### Modos de execução

Controlados pela variável `RUN_MODE` no topo do arquivo:

**`"sanity"`** (padrão):
- 5 snippets, seed fixo (`seed=0`)
- Sempre re-executa (sobrescreve)
- Saída: `results/{modelo}_sanity.csv`
- Use para verificar se as APIs funcionam antes de gastar crédito

**`"full"`**:
- 200 snippets, seed baseado no timestamp atual → snippets diferentes a cada rodada
- Nunca sobrescreve (timestamp no nome do arquivo)
- Saída: `results/{modelo}_20250617_143022_zero_shot.csv`
- Rode 3–5 vezes para acumular dados

### Execução paralela — dois níveis

```
python run.py
  ├── Thread 1 → minimax-m3         ─┐
  ├── Thread 2 → deepseek-v4-flash  ├── 3 modelos em paralelo
  └── Thread 3 → tencent-hy3        ─┘
       └── até 5 workers internos por modelo (snippets em paralelo)
```

### Proteções automáticas
- **Rate limit (429):** backoff exponencial, até 3 retentativas (15s → 30s → 60s)
- **Erro de rede:** até 5 retentativas com 10s de espera
- **Content vazio com reasoning:** retry automático sem `reasoning` (ver seção de problemas)

---

## Como rodar

### Passo 1 — Sanidade
```bash
# RUN_MODE = "sanity"  (já é o padrão)
python run.py
```
Confirma que as 3 APIs respondem. Resultado esperado: `validos=5` para minimax e deepseek, `validos>=4` para tencent.

### Passo 2 — Benchmark completo
Em `run.py`, linha 78, mude:
```python
RUN_MODE = "full"
```
Então:
```bash
python run.py   # rodada 1 → 200 snippets
python run.py   # rodada 2 → 200 snippets diferentes
python run.py   # rodada 3 → 200 snippets diferentes
```

### Passo 3 — Relatório PDF
```bash
python report.py              # lê *_zero_shot.csv (modo full)
python report.py --sanity     # lê *_sanity.csv
python report.py --all        # lê todos os CSVs de resultado
```
Gera `results/relatorio_benchmark_{timestamp}.pdf` com 10 seções (ver abaixo).

### Passo 4 — Análise detalhada (opcional)
```bash
python analyze.py
```
Lê todos os `*_zero_shot.csv` acumulados e gera os gráficos e tabelas em `results/metrics/`.

---

## report.py — Páginas do PDF

| Página | Conteúdo |
|---|---|
| Capa | Resumo geral: modelos, modo, total de predições |
| Métricas | Tabela: Acc, Precisão, Recall, F1, MCC, AUC, TP, FP, TN, FN por modelo |
| Matrizes de Confusão | Heatmap por modelo com TP/FP/TN/FN |
| Precisão / Recall / F1 | Gráfico de barras comparativo com fórmulas |
| Falsos Positivos / Negativos | Contagem absoluta e taxa (FPR/FNR) por modelo |
| Confiança | Boxplot acertos vs erros + histograma por modelo |
| Por Linguagem | Acurácia, F1, Precisão, Recall separados por Python / C |
| Ensemble | Matriz de confusão do voto majoritário + comparativo individual vs ensemble |
| Erros Detalhados | FP e FN com id, linguagem, confiança e explicação do modelo |
| Predições Completas | Tabela com todas as predições por modelo (verde=acerto, vermelho=erro) |

---

## run.py — Log de execução

O arquivo `results/run.log` registra:
- Tempo total por modelo
- Tempo médio, mínimo e máximo por amostra
- Contagem de válidos/inválidos por modelo
- Erros de API, rate limits e retentativas

Os CSVs de resultado incluem a coluna `elapsed_s` (tempo de resposta da API por amostra), útil para análises de latência no TCC.

---

## analyze.py — Seções geradas

| Seção | Análise | Arquivos |
|---|---|---|
| 5.3 | Acurácia por linguagem (Python vs C) | `5.3_linguagem.csv/png` |
| 5.4 | Acurácia por tamanho (quartis de linhas e palavras) | `5.4_linhas.*`, `5.4_palavras.*` |
| 5.5 | Acurácia por complexidade ciclomática | `5.5_complexidade.*` |
| 5.6 | Confiança: unanimidade, heatmaps, ensemble mais confiante | `5.6a/b/c.*` |
| 5.7 | Votação majoritária entre os 3 modelos | `5.7_votacao_majoritaria.*` |
| 5.8 | Falsos negativos (código AI classificado como humano) | `5.8_falsos_negativos.csv` |

---

## Problemas encontrados e soluções

### 1. `content: null` nas respostas da API

**Problema:** Modelos de reasoning (minimax, tencent) retornavam `content: null` no JSON da resposta, causando `AttributeError: 'NoneType' object has no attribute 'strip'`.

**Causa:** O campo `content` da API pode ser `None` quando o modelo ainda não produziu saída de texto.

**Solução:** Substituído acesso direto por `.get()` com fallback para `reasoning_content`:
```python
content = msg.get("content") or msg.get("reasoning_content") or ""
```

---

### 2. `MAX_TOKENS` insuficiente para modelos de reasoning

**Problema:** Com `MAX_TOKENS = 300`, os modelos esgotavam o orçamento de tokens inteiramente com reasoning (pensamento interno), sem tokens restantes para produzir o JSON de resposta. Resultado: `content: None` em quase todas as chamadas.

**Diagnóstico:** Inspecionando `usage.completion_tokens_details.reasoning_tokens` nas respostas:
- minimax: ~300–500 tokens de reasoning
- tencent: ~1000–4000+ tokens de reasoning por snippet

**Evolução do ajuste:**
| MAX_TOKENS | minimax | deepseek | tencent |
|---|---|---|---|
| 300 | 0/5 válidos | 1/5 válidos | 0/5 válidos |
| 1500 | 5/5 ✓ | 4/5 | 0/5 |
| 4000 | 5/5 ✓ | 5/5 ✓ | 2/5 |
| 8000 | 5/5 ✓ | 5/5 ✓ | 3/5 |

**Solução final:** `MAX_TOKENS = 8000` + retry sem reasoning quando content ainda vem vazio.

> **Nota:** `max_tokens` é um limite máximo, não alocação fixa. Cada modelo cobra apenas pelos tokens efetivamente usados.

---

### 3. Tencent usa reasoning excessivo em snippets complexos

**Problema:** Mesmo com 8000 tokens, alguns snippets C complexos faziam o tencent usar todo o orçamento em reasoning sem produzir content.

**Solução:** Retry automático sem o parâmetro `reasoning` quando o content vem vazio na primeira tentativa:
```python
if not content.strip() and use_reasoning:
    payload2 = {k: v for k, v in payload.items() if k != "reasoning"}
    r2 = requests.post(...)  # segunda chamada sem reasoning
    content = r2.json()["choices"][0]["message"].get("content") or ""
```

**Resultado final (sanity):** minimax 5/5, deepseek 5/5, tencent 5/5 (com retry).
