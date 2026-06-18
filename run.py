"""
Benchmark de novos modelos — V4 Zero-Shot
Arquivo 100% autocontido. Nao depende de nenhum outro projeto.

COMO USAR:
  1. Edite a secao CONFIGURE AQUI abaixo.
  2. Crie um arquivo .env nesta mesma pasta com suas chaves de API:
       OPENAI_API_KEY=sk-...
       ANTHROPIC_API_KEY=sk-ant-...
       GOOGLE_API_KEY=AIza...
  3. Instale as dependencias:
       pip install openai anthropic google-genai datasets pandas python-dotenv tqdm
  4. Execute:
       python run.py
  Os resultados ficam em results/{modelo}_zero_shot.csv
"""

# ================================================================
#  CONFIGURE AQUI
# ================================================================

MODELS = {
    # --- OpenRouter ---
    # Cada modelo pode ter sua propria chave (api_key_env) ou usar OPENROUTER_API_KEY.
    # Adicione "reasoning": True para modelos que suportam raciocinio estendido.
    "minimax-m3": {
        "provider": "openrouter",
        "model_id": "minimax/minimax-m3",
        "rpm": 60,
        "api_key_env": "MINIMAX_API_KEY",
        "reasoning": True,
    },
    "deepseek-v4-flash": {
        "provider": "openrouter",
        "model_id": "deepseek/deepseek-v4-flash",
        "rpm": 60,
        "api_key_env": "MODEL2_API_KEY",
        "reasoning": True,
    },
    "qwen3.7-max": {
        "provider": "openrouter",
        "model_id": "qwen/qwen3.7-max",
        "rpm": 60,
        "api_key_env": "MODEL4_API_KEY",
        "reasoning": True,
        "workers": 15,
    },
    "llama-4-maverick": {
        "provider": "openrouter",
        "model_id": "meta-llama/llama-4-maverick",
        "rpm": 60,
        "api_key_env": "MODEL6_API_KEY",
        "reasoning": False,
        "workers": 5,
    },
    "nemotron-ultra-550b": {
        "provider": "openrouter",
        "model_id": "nvidia/nemotron-3-ultra-550b-a55b:free",
        "rpm": 20,           # tier :free tem limite menor
        "api_key_env": "MODEL5_API_KEY",
        "reasoning": True,
        "workers": 5,
    },
    # "qwen-2.5-coder-32b": {   # candidato — especializado em código, sem reasoning (ver README — Modelos candidatos)
    #     "provider": "openrouter",
    #     "model_id": "qwen/qwen-2.5-coder-32b-instruct",
    #     "rpm": 60,
    #     "api_key_env": "MODEL7_API_KEY",
    #     "reasoning": False,
    #     "workers": 5,
    # },
    # "tencent-hy3-preview": {  # desabilitado — ConnectionReset + KeyError 'choices' (ver README #4)
    #     "provider": "openrouter",
    #     "model_id": "tencent/hy3-preview",
    #     "rpm": 60,
    #     "api_key_env": "MODEL3_API_KEY",
    #     "reasoning": True,
    # },
    "mimo-v2.5": {
        "provider": "openrouter",
        "model_id": "xiaomi/mimo-v2.5",
        "rpm": 60,
        "api_key_env": "MIMO_API_KEY",
        "reasoning": True,
        "workers": 15,
    },
    #
    # --- OpenAI ---
    # "gpt-4o": {
    #     "provider": "openai",
    #     "model_id": "gpt-4o",
    #     "rpm": 500,
    # },
    #
    # --- Anthropic ---
    # "claude-sonnet": {
    #     "provider": "anthropic",
    #     "model_id": "claude-sonnet-4-5-20251001",
    #     "rpm": 50,
    # },
    #
    # --- Google ---
    # "gemini-2.5-flash": {
    #     "provider": "gemini",
    #     "model_id": "gemini-2.5-flash",
    #     "rpm": 500,
    # },
}

# ----------------------------------------------------------------
# MODO DE EXECUCAO
#   "sanity" — 5 snippets por modelo, seed fixo. Use para verificar
#              se as APIs e o ambiente estao funcionando.
#   "full"   — 200 snippets por modelo, seed aleatorio a cada run.
#              Cada execucao amostra snippets diferentes; rode 3-5x
#              para acumular dados. Resultados em {modelo}_{id}_zero_shot.csv
# ----------------------------------------------------------------
RUN_MODE = "full"

# Modelos a excluir de rodadas subsequentes — atualizado automaticamente pelo runner.py
SKIP_MODELS: list = ["nemotron-ultra-550b"]

# Dataset (mesmo do experimento original)
DATASET_NAME        = "isThisYouLLM/H-AIRosettaMP"
LANGUAGES           = ["Python", "C"]
SAMPLES_PER_CLASS_PER_LANG = 50   # 50 por classe x 2 linguagens x 2 classes = 200 snippets
MAX_CODE_CHARS      = 3000
MAX_TOKENS          = 8000   # tencent/hy3 usa ate ~4000+ tokens de reasoning; e um limite, nao alocacao fixa
MAX_WORKERS         = 5

# ================================================================
#  PROMPT V4 ZERO-SHOT
# ================================================================

PROMPT_TEMPLATE = """You are a forensic code analyst. Classify the following code snippet as "human" (human-written) or "ai" (AI-generated).

DOMAIN PRINCIPLE
Human-authored code carries the fingerprints of lived experience: debugging sessions, evolving understanding, personal habits, shortcuts, idiosyncrasies accumulated over time. AI-generated code lacks these fingerprints — it is structurally clean, stylistically uniform, and free of the residue of authorship.

Your task is therefore asymmetric: look for human fingerprints. If you find them, classify as human. If you cannot find them, classify as ai — because human code is distinguishable by what it carries, and AI code is the featureless default.

HUMAN FINGERPRINTS (any one is sufficient evidence)
- REPL/interactive artifacts: ">>>", "In [1]:", IPython prompts, traceback fragments mixed with code
- Version, authorship, or dated annotations: "# v0.3 - fixed bug", "# author: jdoe", "// 2019-04-12"
- Idiosyncratic or inconsistent style within the same file: mixed camelCase/snake_case, irregular indentation, inconsistent quote style
- Commented-out experimental code, dead branches, leftover debug prints, hardcoded local paths
- Personal, colloquial, or non-English comments; informal TODO/FIXME/HACK; typos
- Distinctive language idioms: Haskell-style type signatures in comments, Perl one-liner condensation, C macro tricks, pointer-arithmetic offsets
- Stack-Overflow-style fragments, magic numbers used without explanation, "it works but I don't know why" patterns

AI FINGERPRINTS (reinforce the default; not required to classify as ai)
- Pedagogical comments restating what the immediately following line does
- Uniform docstrings or type hints applied identically to every function including trivial ones
- Defensive structure beyond what the task requires: broad try/except, redundant null checks, exhaustive input validation
- Demonstration scaffolding: "Example usage:" blocks, boilerplate `if __name__ == "__main__":` around trivial code
- Consistently placeholder-flavored names throughout: "data", "result", "value", "process_data", "helper"
- Exhaustive edge-case coverage for a task that does not require it
- Residual chat framing in comments or strings: "Here is the solution:", "Sure!", "Note that...", "This function..."

DECISION LOGIC
1. Scan for human fingerprints. Found at least one?
   -> Evaluate its strength.
   -> Strong, distinctive fingerprint: predict "human", confidence 8-9.
   -> Weak or ambiguous fingerprint: predict "human", confidence 6-7.
2. No human fingerprints found?
   -> Predict "ai". Human code is distinguishable; absence of fingerprints is meaningful.
   -> Also found AI fingerprints: confidence 7-8.
   -> No AI fingerprints either (clean but anonymous code): confidence 6-7.
3. Fingerprints AND strong AI markers both present?
   -> Weigh specificity and quantity. Pick the stronger side.
   -> If truly tied: predict "ai", confidence 6.

CONFIDENCE CALIBRATION
- 9-10: multiple clear fingerprints or AI markers on the chosen side
- 7-8:  one clear fingerprint or AI marker
- 6-7:  weak or ambiguous evidence
- <6:   do not use

Return ONLY this JSON object, with no surrounding text:
{"prediction": "human" or "ai", "confidence": <integer 0-10>, "explanation": "<1-2 sentences citing the specific fingerprint(s) observed, or stating that no human fingerprints were found>"}

CODE SNIPPET:
{code}
"""

# ================================================================
#  CODIGO — nao e necessario editar abaixo
# ================================================================

import json
import logging
import os
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from tqdm import tqdm

_HERE = Path(__file__).parent
RESULTS_DIR = _HERE / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

load_dotenv(_HERE / ".env")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(RESULTS_DIR / "run.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)


# ----------------------------------------------------------------
# Rate limiter
# ----------------------------------------------------------------

class _RateLimiter:
    def __init__(self, rpm: int):
        self._interval = 60.0 / max(rpm, 1)
        self._lock = threading.Lock()
        self._last_ts = 0.0

    def acquire(self):
        with self._lock:
            now = time.monotonic()
            wait = self._interval - (now - self._last_ts)
            if wait > 0:
                time.sleep(wait)
            self._last_ts = time.monotonic()


# ----------------------------------------------------------------
# Provider factory
# ----------------------------------------------------------------

def _make_call_fn(cfg: dict):
    ptype = cfg["provider"]
    model_id = cfg["model_id"]

    if ptype == "openai":
        from openai import OpenAI
        key = os.getenv("OPENAI_API_KEY") or ""
        if not key:
            raise ValueError("OPENAI_API_KEY nao encontrada no .env")
        client = OpenAI(api_key=key)

        def _call(prompt):
            r = client.chat.completions.create(
                model=model_id,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=MAX_TOKENS,
            )
            return r.choices[0].message.content.strip()

    elif ptype == "anthropic":
        import anthropic as _ant
        key = os.getenv("ANTHROPIC_API_KEY") or ""
        if not key:
            raise ValueError("ANTHROPIC_API_KEY nao encontrada no .env")
        client = _ant.Anthropic(api_key=key)

        def _call(prompt):
            r = client.messages.create(
                model=model_id,
                max_tokens=MAX_TOKENS,
                messages=[{"role": "user", "content": prompt}],
            )
            return r.content[0].text.strip()

    elif ptype == "gemini":
        from google import genai as _gen
        key = os.getenv("GOOGLE_API_KEY") or ""
        if not key:
            raise ValueError("GOOGLE_API_KEY nao encontrada no .env")
        client = _gen.Client(api_key=key)

        def _call(prompt):
            r = client.models.generate_content(model=model_id, contents=prompt)
            return r.text.strip()

    elif ptype == "openrouter":
        import requests as _req
        key_env = cfg.get("api_key_env", "OPENROUTER_API_KEY")
        key = os.getenv(key_env) or ""
        if not key:
            raise ValueError(f"{key_env} nao encontrada no .env")
        use_reasoning = cfg.get("reasoning", False)

        def _call(prompt):
            payload = {
                "model": model_id,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": MAX_TOKENS,
            }
            if use_reasoning:
                payload["reasoning"] = {"enabled": True}
            r = _req.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=120,
            )
            r.raise_for_status()
            msg = r.json()["choices"][0]["message"]
            content = msg.get("content") or msg.get("reasoning_content") or ""
            if not content.strip() and use_reasoning:
                # reasoning esgotou o budget sem produzir content; retenta sem reasoning
                logger.debug("[%s] content vazio com reasoning; retentando sem reasoning...", model_id)
                payload2 = {k: v for k, v in payload.items() if k != "reasoning"}
                r2 = _req.post(
                    url="https://openrouter.ai/api/v1/chat/completions",
                    headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                    json=payload2,
                    timeout=120,
                )
                r2.raise_for_status()
                msg2 = r2.json()["choices"][0]["message"]
                content = msg2.get("content") or msg2.get("reasoning_content") or ""
            return content.strip()

    else:
        raise ValueError(f"Provider desconhecido: '{ptype}'. Use openai, anthropic ou gemini.")

    return _call


def _is_rate_limit(e: Exception) -> bool:
    msg = str(e).lower()
    return "429" in msg or "quota" in msg or "resource exhausted" in msg or "rate limit" in msg


def _is_network_error(e: Exception) -> bool:
    msg = str(e).lower()
    return any(x in msg for x in [
        "getaddrinfo failed", "connect error", "read error", "write error",
        "connection reset", "connection aborted", "connection refused",
        "network unreachable", "eof occurred", "ssl", "timed out", "timeout",
    ])


# ----------------------------------------------------------------
# Parse da resposta
# ----------------------------------------------------------------

def _parse(text: str):
    try:
        cleaned = text.replace("```json", "").replace("```", "").strip()
        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError:
            idx = cleaned.rfind('"prediction"')
            if idx == -1:
                raise ValueError("sem chave prediction")
            start = cleaned.rfind('{', 0, idx)
            depth = end = 0
            for i, ch in enumerate(cleaned[start:], start):
                if ch == '{':
                    depth += 1
                elif ch == '}':
                    depth -= 1
                    if depth == 0:
                        end = i + 1
                        break
            data = json.loads(cleaned[start:end])
        pred = str(data.get("prediction", "")).lower().strip()
        try:
            conf = int(data.get("confidence", 50))
        except Exception:
            conf = 50
        if pred not in ["human", "ai"]:
            pred = "unknown"
        return pred, conf, str(data.get("explanation", ""))
    except Exception as e:
        logger.debug("Parse error: %s", e)
        return "unknown", 50, "parse_error"


# ----------------------------------------------------------------
# Dataset
# ----------------------------------------------------------------

def _load_data(n_per_class: int = SAMPLES_PER_CLASS_PER_LANG, seed: int = 42, cap: int | None = None) -> pd.DataFrame:
    from datasets import load_dataset
    logger.info("Carregando dataset %s...", DATASET_NAME)
    ds = load_dataset(DATASET_NAME, split="train")
    df = ds.to_pandas()
    df = df[df["language_name"].isin(LANGUAGES)].copy()
    df["label"] = df["target"].apply(lambda x: "ai" if x == "Ai_generated" else "human")
    df = df.dropna(subset=["code"])
    df = df[df["code"].str.strip() != ""]
    sampled = []
    for lang in LANGUAGES:
        for label in ["ai", "human"]:
            subset = df[(df["language_name"] == lang) & (df["label"] == label)]
            n = min(n_per_class, len(subset))
            sampled.append(subset.sample(n=n, random_state=seed))
    df = pd.concat(sampled).reset_index(drop=True)
    if cap:
        df = df.sample(n=min(cap, len(df)), random_state=seed).reset_index(drop=True)
    logger.info("Pronto: %d snippets (seed=%d)", len(df), seed)
    return df


# ----------------------------------------------------------------
# Runner
# ----------------------------------------------------------------

def _run_model(df: pd.DataFrame, model_name: str, cfg: dict) -> list:
    call_fn = _make_call_fn(cfg)
    limiter = _RateLimiter(cfg["rpm"])
    rows = list(df.itertuples())
    results = [None] * len(rows)
    model_start = time.monotonic()

    def process(i, row):
        prompt = PROMPT_TEMPLATE.replace("{code}", str(row.code)[:MAX_CODE_CHARS])
        limiter.acquire()
        t0 = time.monotonic()
        rate_r = net_r = 0
        while True:
            try:
                raw = call_fn(prompt)
                pred, conf, expl = _parse(raw) if raw and raw.strip() else ("unknown", 50, "empty_response")
                break
            except Exception as e:
                if _is_rate_limit(e) and rate_r < 3:
                    wait = 15 * (2 ** rate_r)
                    logger.warning("[%s] Rate limit — aguardando %ds...", model_name, wait)
                    time.sleep(wait)
                    rate_r += 1
                    continue
                if _is_network_error(e) and net_r < 5:
                    logger.warning("[%s] Erro de rede — aguardando 10s...", model_name)
                    time.sleep(10)
                    net_r += 1
                    continue
                logger.error("[%s] id=%s: %s", model_name, row.Index, e)
                pred, conf, expl = "unknown", 50, f"api_error: {e}"
                break
        elapsed = time.monotonic() - t0
        logger.debug("[%s] id=%-4s  %.1fs  pred=%-6s  conf=%s  lang=%s",
                     model_name, row.Index, elapsed, pred, conf, row.language_name)
        return i, {
            "id": row.Index,
            "language": row.language_name,
            "true_label": row.label,
            "model": model_name,
            "strategy": "zero_shot",
            "prediction": pred,
            "confidence": conf,
            "explanation": expl,
            "elapsed_s": round(elapsed, 2),
        }

    with ThreadPoolExecutor(max_workers=cfg.get("workers", MAX_WORKERS)) as ex:
        futures = {ex.submit(process, i, row): i for i, row in enumerate(rows)}
        with tqdm(total=len(rows), desc=model_name, unit="snippet") as pbar:
            for future in as_completed(futures):
                i, res = future.result()
                results[i] = res
                pbar.update(1)

    return results


# ----------------------------------------------------------------
# Main
# ----------------------------------------------------------------

def _run_and_save(df: pd.DataFrame, model_name: str, cfg: dict, suffix: str):
    safe = model_name.replace("/", "_")
    out = RESULTS_DIR / f"{safe}_{suffix}.csv"
    logger.info("Iniciando: %s  [%s / %s]", model_name, cfg["provider"], cfg["model_id"])
    t0 = time.monotonic()
    rows = _run_model(df, model_name, cfg)
    total_s = time.monotonic() - t0
    result_df = pd.DataFrame(rows)
    result_df.to_csv(out, index=False)

    # resumo de tempo
    n = len(result_df)
    n_valid = result_df["prediction"].isin(["human", "ai"]).sum()
    avg_s = result_df["elapsed_s"].mean() if "elapsed_s" in result_df.columns else 0
    min_s = result_df["elapsed_s"].min() if "elapsed_s" in result_df.columns else 0
    max_s = result_df["elapsed_s"].max() if "elapsed_s" in result_df.columns else 0
    logger.info(
        "Salvo: %s  |  total=%.1fs  media/amostra=%.1fs  min=%.1fs  max=%.1fs  validos=%d/%d",
        out.name, total_s, avg_s, min_s, max_s, n_valid, n,
    )


def main():
    if not MODELS:
        print("\nMODELS esta vazio. Edite a secao CONFIGURE AQUI no topo do arquivo.")
        return

    if RUN_MODE == "sanity":
        seed   = 0
        suffix = "sanity"
        df     = _load_data(cap=5, seed=seed)
        logger.info("=== MODO SANITY — %d snippets por modelo ===", len(df))
        pending = dict(MODELS)

    elif RUN_MODE == "full":
        seed    = int(time.time())
        run_id  = time.strftime("%Y%m%d_%H%M%S")
        suffix  = f"{run_id}_zero_shot"
        df      = _load_data(seed=seed)
        logger.info("=== MODO FULL — %d snippets, seed=%d, run_id=%s ===", len(df), seed, run_id)
        pending = {k: v for k, v in MODELS.items() if k not in SKIP_MODELS}
        if SKIP_MODELS:
            logger.info("Modelos ignorados (SKIP_MODELS): %s", SKIP_MODELS)

    else:
        print(f"\nRUN_MODE invalido: '{RUN_MODE}'. Use 'sanity' ou 'full'.")
        return

    logger.info("Rodando %d modelo(s) em paralelo...", len(pending))
    with ThreadPoolExecutor(max_workers=len(pending)) as ex:
        futures = {ex.submit(_run_and_save, df, name, cfg, suffix): name for name, cfg in pending.items()}
        for future in as_completed(futures):
            name = futures[future]
            try:
                future.result()
            except Exception as e:
                logger.error("Modelo %s falhou: %s", name, e)

    print("\n" + "=" * 65)
    print(f"  RESUMO  [{RUN_MODE.upper()}]  suffix={suffix}")
    print("=" * 65)
    for model_name in MODELS:
        safe = model_name.replace("/", "_")
        out  = RESULTS_DIR / f"{safe}_{suffix}.csv"
        if out.exists():
            r = pd.read_csv(out)
            v = r[r["prediction"].isin(["human", "ai"])]
            acc = (v["prediction"] == v["true_label"]).mean() if len(v) else float("nan")
            print(f"  {model_name:<35}  total={len(r)}  validos={len(v)}  acc={acc:.3f}")
        else:
            print(f"  {model_name:<35}  (nao gerado)")
    print("=" * 65)


if __name__ == "__main__":
    main()
