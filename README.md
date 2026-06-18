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
# MODEL3_API_KEY=...          # tencent/hy3-preview — desabilitado (ver problema #4)
MIMO_API_KEY=...              # xiaomi/mimo-v2.5
```

---

## Modelos configurados

Todos via OpenRouter. Workers = número de snippets em paralelo por modelo.

| Nome | Model ID | Chave | Workers |
|---|---|---|---|
| `minimax-m3` | `minimax/minimax-m3` | `MINIMAX_API_KEY` | 5 |
| `deepseek-v4-flash` | `deepseek/deepseek-v4-flash` | `MODEL2_API_KEY` | 5 |
| `mimo-v2.5` | `xiaomi/mimo-v2.5` | `MIMO_API_KEY` | 15 |
| `qwen3.7-max` | `qwen/qwen3.7-max` | `MODEL4_API_KEY` | 15 |
| `llama-4-maverick` | `meta-llama/llama-4-maverick` | `MODEL6_API_KEY` | 5 |
| `nemotron-ultra-550b` | `nvidia/nemotron-3-ultra-550b-a55b:free` | `MODEL5_API_KEY` | 5 |
| ~~`tencent-hy3-preview`~~ | ~~`tencent/hy3-preview`~~ | desabilitado — ver problema #4 | — |

---

## Modelos candidatos para próximas execuções

Três candidatos recomendados para expandir o benchmark, cobrindo hipóteses distintas:

| Modelo | Empresa | ID OpenRouter | Reasoning | Workers | Status |
|---|---|---|---|---|---|
| **Qwen3.7-Max** | Alibaba | `qwen/qwen3.7-max` | Sim | 15 | Adicionado ao `run.py` — aguarda chave `MODEL4_API_KEY` |
| **Qwen2.5-Coder 32B** | Alibaba | `qwen/qwen-2.5-coder-32b-instruct` | Não | 5 | Comentado em `run.py` — chave `MODEL7_API_KEY` pronta, habilitar quando necessário |
| **Llama 4 Maverick** | Meta | `meta-llama/llama-4-maverick` | Não | 5 | Adicionado ao `run.py` — chave `MODEL6_API_KEY` |

**Critério de seleção:** Qwen3.7-Max e Qwen2.5-Coder 32B estão no topo da lista de modelos open source por popularidade no OpenRouter e são especializados em código — diretamente relevante para análise forense de autoria.

**Por que esses três:**

- **Qwen3.7-Max** — flagship da série Qwen3.7, otimizado para coding e workloads agentic. Selecionado por popularidade no OpenRouter (open models) e especialização em código. `workers=15` pelo perfil de latência esperado similar ao mimo.

- **Qwen2.5-Coder 32B** — modelo de código da geração anterior, sem reasoning. Testa se especialização em código supera modelos gerais nesta tarefa, e serve como controle para a hipótese de reasoning.

- **Llama 4 Maverick** — Meta, empresa ocidental, sem reasoning. Diversifica a origem dos modelos (os 4 ativos são todos chineses) e serve como controle: se Maverick sem reasoning performa próximo de modelos com reasoning, o overhead de latência não se justifica.

**Comparações que o conjunto completo permite:**

| Comparação | Modelos |
|---|---|
| Reasoning vs sem reasoning | minimax / deepseek / mimo / qwen3.7 / nemotron vs **Maverick** / Qwen2.5-Coder |
| Especializado em código vs generalista | minimax / deepseek / mimo / **Maverick** vs Qwen3.7-Max / Qwen2.5-Coder / Nemotron |
| Escala (params ativos) | deepseek (~7B) → **Maverick** (17B) → Qwen2.5-Coder (32B) → Nemotron (55B / 550B total) |
| Origem geográfica | modelos chineses vs **Maverick** (Meta/US) / Nemotron (NVIDIA/US) |
| Arquitetura | Transformer denso vs MoE: **Maverick** (128 experts) / Nemotron (Transformer-Mamba) |

---

## Modelos avaliados e descartados

Modelos considerados durante a seleção mas não adicionados ao benchmark, com justificativa.

| Modelo | ID | Motivo da rejeição |
|---|---|---|
| **Llama Nemotron Rerank VL 1B V2** | `nvidia/llama-nemotron-rerank-vl-1b-v2` | Tipo errado: é um *reranker* para pipelines RAG (scores de relevância query↔documento), não um modelo de chat/instrução. Não gera JSON de classificação nem explicações. 1.7B params — insuficiente para raciocínio forense. |
| **Qwen3 235B** | `qwen/qwen3-235b-a22b` | Substituído pelo Qwen3.7-Max: mesma família Alibaba, mas o 3.7-Max é otimizado especificamente para coding e workloads agentic, além de estar mais alto na lista de popularidade open do OpenRouter. Manter os dois seria redundante. |
| **GLM 5.2** | `z-ai/glm-5.2` | Perfil redundante com os modelos já configurados: seria o 5º modelo chinês com reasoning focado em código. Os slots restantes foram priorizados para hipóteses diferentes (Maverick sem reasoning, Qwen2.5-Coder sem reasoning). |
| **Nemotron Ultra 550B** | `nvidia/nemotron-3-ultra-550b-a55b:free` | Instabilidade grave na rodada 1 (2026-06-18): ConnectionResetError em série após 6h de execução sem concluir os 200 snippets. Os 5 outros modelos já haviam finalizado. Comportamento idêntico ao tencent/hy3-preview (ver problema #4). Tier `:free` parece ser o fator determinante — endpoints gratuitos do OpenRouter derrubam conexões longas com reasoning. Dados de comparação: latências de 400–600s/snippet nos outros modelos na mesma rodada (instabilidade de rede geral) vs 2.4s do llama-4-maverick sem reasoning — reforça que o tier free + reasoning é inviável para benchmarks longos. Adicionado a `SKIP_MODELS` em run.py. |

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
  ├── Thread 1 → minimax-m3              ─┐
  ├── Thread 2 → deepseek-v4-flash       │
  ├── Thread 3 → mimo-v2.5               ├── 6 modelos em paralelo
  ├── Thread 4 → qwen3.7-max             │
  ├── Thread 5 → llama-4-maverick        │
  └── Thread 6 → nemotron-ultra-550b     ─┘
       └── workers internos por modelo (snippets em paralelo):
             minimax-m3, deepseek-v4-flash  → 5 (MAX_WORKERS global)
             mimo-v2.5, qwen3.7-max         → 15 (override — reasoning lento)
             llama-4-maverick               → 5 (sem reasoning, rápido)
             nemotron-ultra-550b            → 5 (tier :free, rpm=20)
```

Cada modelo pode sobrescrever o padrão global com o campo `"workers"` na sua config. Modelos com alta latência de reasoning se beneficiam de mais workers já que a taxa real de requisições fica bem abaixo do limite de RPM (mimo: ~0.06 req/s com 5 workers, limite é 60 RPM = 1 req/s).

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

---

### 4. `tencent/hy3-preview` instável na execução full (200 snippets)

**Problema:** Na primeira execução full (2026-06-17), o tencent apresentou duas falhas distintas:

**4a. `ConnectionResetError(10054)`**

O servidor do endpoint derrubava a conexão no meio da requisição, provavelmente porque respostas longas com reasoning (até 4000+ tokens) excediam o timeout ou a estabilidade do endpoint. Resultado: rajadas de `connection reset` simultâneas em múltiplos workers.

```
[tencent-hy3-preview] Erro de rede — aguardando 10s...
[tencent-hy3-preview] id=63: ("Connection broken: ConnectionResetError(10054...)")
[tencent-hy3-preview] id=62: ("Connection broken: ConnectionResetError(10054...)")
```

O retry automático de rede (até 5x, 10s de espera) absorveu parte dos erros, mas alguns snippets foram registrados como `api_error`.

**4b. `KeyError: 'choices'`**

Em alguns snippets, a API retornou HTTP 200 com corpo de erro (`{"error": {...}}`), em vez da estrutura padrão `{"choices": [...]}`. O `raise_for_status()` não detecta esse caso — o código travava com `KeyError: 'choices'` e o snippet era perdido.

```
[tencent-hy3-preview] id=92: 'choices'
```

**Resultado da execução full:** tencent ainda em andamento / degradado; minimax `194/200 válidos`, deepseek `198/200 válidos`.

**Alternativas testadas/consideradas:**

| Modelo | ID OpenRouter | Reasoning | Observação |
|---|---|---|---|
| `qwen/qwen3-235b-a22b` | `qwen/qwen3-235b-a22b` | Sim | Substituto direto; endpoint estável |
| `moonshotai/kimi-k2` | `moonshotai/kimi-k2` | Sim | Forte em análise de código |
| `meta-llama/llama-4-maverick` | `meta-llama/llama-4-maverick` | Não | Alta velocidade e confiabilidade |
| `mistralai/mistral-large` | `mistralai/mistral-large` | Não | Estável, sem surpresas de formato |

**Recomendação:** substituir `tencent/hy3-preview` por `qwen/qwen3-235b-a22b` na próxima execução — mesma chave `MODEL3_API_KEY`, suporta `reasoning: true`, e o endpoint do OpenRouter se mostrou consistente em testes.

---

### 5. `mimo-v2.5` — latência alta por reasoning extenso

**Contexto:** `xiaomi/mimo-v2.5` foi adicionado como substituto do tencent (2026-06-18). No sanity de 5 snippets, a API funcionou sem erros (5/5 válidos), mas a latência foi ~84s/snippet em média (mín 12s, máx 158s), contra ~14s dos outros modelos. O reasoning estendido consome o orçamento de tokens antes de produzir a resposta.

**Impacto no full (200 snippets):** com o padrão de 5 workers, o mimo levaria ~56 min — 4–5x mais que os outros modelos.

**Solução:** override de workers por modelo. O campo `"workers"` na config do modelo sobrescreve `MAX_WORKERS`:

```python
"mimo-v2.5": {
    ...
    "workers": 15,
}
```

Com 15 workers e ~84s/request, a taxa efetiva é ~0.18 req/s (10.7 RPM) — dentro do limite de 60 RPM. Tempo estimado para 200 snippets cai de ~56 min para **~18 min**.

**Cálculo:** `200 snippets × 84s ÷ 15 workers ≈ 1120s ≈ 18 min`

---

## Execução full — estado atual (2026-06-18)

### Rodadas concluídas

| Modelo | Rodadas | Amostras acumuladas | Válidas | Taxa válidas |
|---|---|---|---|---|
| `llama-4-maverick` | 2 | 400 | 398 | 99.5% |
| `deepseek-v4-flash` | 2 | 400 | 391 | 97.8% |
| `qwen3.7-max` | 2 | 400 | 384 | 96.0% |
| `minimax-m3` | 2 | 400 | 381 | 95.3% |
| `mimo-v2.5` | 2 | 400 | 381 | 95.3% |
| `nemotron-ultra-550b` | 0 | — | — | descartado (ver seção de modelos descartados) |

**Última atualização: 2026-06-18 ~17h**

| Modelo | Rodadas concluídas | Amostras | Válidas | Taxa |
|---|---|---|---|---|
| `llama-4-maverick` | 3/5 | 600 | 597 | 99.5% |
| `deepseek-v4-flash` | 3/5 | 600 | 590 | 98.3% |
| `qwen3.7-max` | 3/5 | 600 | 584 | 97.3% |
| `mimo-v2.5` | 3/5 | 600 | 581 | 96.8% |
| `minimax-m3` | 2/5 + R3 em andamento | 400 | 381 | 95.2% |
| `nemotron-ultra-550b` | 0 | — | — | descartado |

Runner ativo, rodadas 4 e 5 pendentes. Nenhum modelo excluído (todos acima de 80% de válidos).

**Nota sobre a rodada 1:** latências anormalmente altas (deepseek 334s/snippet, qwen3.7 448s/snippet, minimax 588s/snippet) indicam instabilidade de rede geral no período 08h–15h. As rodadas 2 e 3 voltaram ao normal (deepseek ~8-9s, qwen3.7 ~24s, mimo ~22s), confirmando que os dados da rodada 1 são válidos mas ruidosos em `elapsed_s` — predições e conteúdo não foram afetados. Minimax apresenta erros de rede recorrentes mesmo nas rodadas normais, mas o retry automático absorve e completa os 200 snippets.

---

## Achados do primeiro sanity com minimax + deepseek + mimo (2026-06-18)

Sanity de 5 snippets (seed fixo), gerado por `report.py --sanity`.

### Métricas

| Modelo | Acc | Conf. média | TP | FP | TN | FN | Latência média |
|---|---|---|---|---|---|---|---|
| `minimax-m3` | 0.60 | 7.8 | 0 | 0 | 3 | 2 | 13.9s |
| `deepseek-v4-flash` | 0.20 | 7.4 | 0 | 2 | 1 | 2 | 14.2s |
| `mimo-v2.5` | 0.40 | 7.6 | 0 | 1 | 2 | 2 | 84.0s |

> Acc em 5 amostras não é estatisticamente significativa — serve apenas para verificar funcionamento e identificar padrões de erro.

### Padrão de erro comum — dois snippets enganaram os 3 modelos

**Snippet #0 (AI, Python) — falso negativo universal:**
O código contém `# version 1.2.0` no topo. Os 3 modelos classificaram como `human` com confiança 8, citando a anotação de versão como fingerprint humano. O snippet é AI-gerado com uma anotação típica de projeto — ponto cego compartilhado.

**Snippet #2 (AI, C) — falso negativo universal:**
O código tem um bug de sintaxe real (parêntese desbalanceado no operador ternário) e nomes de variáveis crípticos. Os 3 modelos interpretaram o bug como evidência de autoria humana. Código AI pode conter bugs; a presença de erro sintático não é fingerprint humano confiável.

### Diferenças entre modelos

- **minimax-m3** — mais conservador: não gerou nenhum falso positivo, errou apenas os 2 snippets AI difíceis. Explicações mais detalhadas e contextualmente ricas.
- **deepseek-v4-flash** — mais agressivo ao classificar como AI: 2 falsos positivos (snippets humanos classificados como AI). Explicações mais rasas, menor qualidade de raciocínio visível.
- **mimo-v2.5** — comportamento intermediário: 1 falso positivo, explicações comparáveis ao minimax em profundidade, mas latência ~6x maior por reasoning extenso.
