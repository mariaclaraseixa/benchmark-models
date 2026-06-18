"""
Analisa resultados do benchmark — secoes 5.3 a 5.8.

Lê:
  results/*_zero_shot.csv          — predicoes geradas por run.py
  results/complexity_scores.csv    — opcional (copiar do projeto TCC);
                                     se ausente, sec 5.5 e pulada

Gera em results/metrics/:
  5.3_linguagem.{csv,png}
  5.4_linhas.{csv,png}
  5.4_palavras.{csv,png}
  5.5_complexidade.{csv,png}
  5.6a_unanimidade.csv
  5.6b_confianca_heatmap.png
  5.6c_mais_confiante.csv
  5.7_votacao_majoritaria.{csv,png}
  5.8_falsos_negativos.csv

ATENCAO: run.py e analyze.py devem usar as mesmas configuracoes de
LANGUAGES e SAMPLES_PER_CLASS_PER_LANG para que os IDs dos snippets
coincidam com a analise de tamanho e complexidade.
"""

import logging
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    accuracy_score, f1_score, precision_score, recall_score,
    matthews_corrcoef, roc_auc_score, confusion_matrix,
)

warnings.filterwarnings("ignore")

_HERE           = Path(__file__).parent
RESULTS_DIR     = _HERE / "results"
METRICS_DIR     = RESULTS_DIR / "metrics"
COMPLEXITY_FILE = RESULTS_DIR / "complexity_scores.csv"

# Deve ser igual ao run.py
DATASET_NAME            = "isThisYouLLM/H-AIRosettaMP"
LANGUAGES               = ["Python", "C"]
SAMPLES_PER_CLASS_PER_LANG = 50

# Cortes fixos (por especificacao do TCC)
LINE_QUARTILES = [
    ("Q1\n(1–14)",    1,   14),
    ("Q2\n(15–27)",  15,   27),
    ("Q3\n(28–51)",  28,   51),
    ("Q4\n(52+)",    52, None),
]
WORD_QUARTILES = [
    ("Q1\n(≤46)",      0,   46),
    ("Q2\n(47–102)",  47,  102),
    ("Q3\n(103–196)", 103, 196),
    ("Q4\n(197+)",   197, None),
]
COMPLEXITY_BINS = [
    ("Baixa\n(0–2)",      -0.01,  2.99),
    ("Méd-Baixa\n(3–5)",   2.99,  5.99),
    ("Méd-Alta\n(6–7)",    5.99,  7.99),
    ("Alta\n(8–10)",       7.99, 10.01),
]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)
_nan = float("nan")


# ================================================================
# Helpers
# ================================================================

def _metrics(df: pd.DataFrame) -> dict:
    v = df[df["prediction"].isin(["human", "ai"])].copy()
    if len(v) == 0:
        return dict(precision=_nan, recall=_nan, f1=_nan, accuracy=_nan, mcc=_nan, auc=_nan, n=0)
    y_true = (v["true_label"] == "ai").astype(int)
    y_pred = (v["prediction"] == "ai").astype(int)
    v["ai_score"] = v.apply(
        lambda r: r["confidence"] / 10 if r["prediction"] == "ai" else 1.0 - r["confidence"] / 10,
        axis=1,
    )
    try:
        auc = roc_auc_score(y_true, v["ai_score"]) if y_true.nunique() > 1 else _nan
    except Exception:
        auc = _nan
    return dict(
        precision=precision_score(y_true, y_pred, zero_division=0),
        recall=recall_score(y_true, y_pred, zero_division=0),
        f1=f1_score(y_true, y_pred, zero_division=0),
        accuracy=accuracy_score(y_true, y_pred),
        mcc=matthews_corrcoef(y_true, y_pred),
        auc=auc,
        n=int(len(v)),
    )


def _bar_group(ax, group_labels, series: dict, title, ylabel="Accuracy", ylim=(0, 1.15)):
    x = np.arange(len(group_labels))
    n = len(series)
    w = min(0.7 / max(n, 1), 0.28)
    colors = list(plt.cm.Set2.colors)
    for i, (name, vals) in enumerate(series.items()):
        offset = (i - (n - 1) / 2) * w
        bars = ax.bar(x + offset, vals, w, label=name, color=colors[i % len(colors)], edgecolor="white")
        for bar, v in zip(bars, vals):
            if not np.isnan(v):
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                        f"{v:.2f}", ha="center", va="bottom", fontsize=7)
    ax.set_title(title, fontsize=10, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(group_labels, fontsize=8)
    ax.set_ylabel(ylabel, fontsize=9)
    ax.set_ylim(*ylim)
    ax.legend(fontsize=7, ncol=min(n, 3))
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def _clean(label: str) -> str:
    return label.replace("\n", " ")


# ================================================================
# Carregamento de dados
# ================================================================

def _load_predictions() -> pd.DataFrame:
    frames = []
    for p in sorted(RESULTS_DIR.glob("*_zero_shot.csv")):
        frames.append(pd.read_csv(p))
    if not frames:
        raise FileNotFoundError(f"Nenhum '*_zero_shot.csv' encontrado em {RESULTS_DIR}/")
    preds = pd.concat(frames, ignore_index=True)
    logger.info("Modelos carregados: %s", sorted(preds["model"].unique()))
    logger.info("Predicoes totais: %d", len(preds))
    return preds


def _load_dataset_info() -> pd.DataFrame:
    """Carrega dataset e calcula n_lines e n_words com a mesma amostragem do run.py."""
    from datasets import load_dataset
    logger.info("Carregando dataset para calcular linhas/palavras...")
    ds = load_dataset(DATASET_NAME, split="train")
    df = ds.to_pandas()
    df = df[df["language_name"].isin(LANGUAGES)].copy()
    df["label"] = df["target"].apply(lambda x: "ai" if x == "Ai_generated" else "human")
    df = df.dropna(subset=["code"])
    df = df[df["code"].str.strip() != ""]
    sampled = []
    for lang in LANGUAGES:
        for label in ["ai", "human"]:
            sub = df[(df["language_name"] == lang) & (df["label"] == label)]
            sampled.append(sub.sample(n=min(SAMPLES_PER_CLASS_PER_LANG, len(sub)), random_state=42))
    df = pd.concat(sampled).reset_index(drop=True)
    df["id"]      = df.index
    df["n_lines"] = df["code"].apply(lambda c: len(c.strip().splitlines()))
    df["n_words"] = df["code"].apply(lambda c: len(c.split()))
    logger.info("Dataset info pronto: %d snippets", len(df))
    return df[["id", "language_name", "label", "n_lines", "n_words"]]


# ================================================================
# 5.3 — Por linguagem
# ================================================================

def section_53(preds: pd.DataFrame, out: Path):
    logger.info("=== 5.3 Por linguagem ===")
    models = sorted(preds["model"].unique())
    rows = []
    for model in models:
        sub = preds[preds["model"] == model]
        for lang in LANGUAGES:
            m = _metrics(sub[sub["language"] == lang])
            rows.append({"model": model, "language": lang, **m})
    df = pd.DataFrame(rows)
    df.to_csv(out / "5.3_linguagem.csv", index=False)

    fig, ax = plt.subplots(figsize=(7, 4.5))
    _bar_group(
        ax, LANGUAGES,
        {m: [df[(df["model"] == m) & (df["language"] == l)]["accuracy"].values[0] for l in LANGUAGES] for m in models},
        "5.3 — Acurácia por Linguagem (zero-shot)",
    )
    fig.tight_layout()
    fig.savefig(out / "5.3_linguagem.png", dpi=150)
    plt.close(fig)

    print("\n5.3 — Por linguagem")
    print(df[["model", "language", "accuracy", "precision", "recall", "f1", "mcc", "auc", "n"]].to_string(
        index=False, float_format=lambda x: f"{x:.3f}"))


# ================================================================
# 5.4 — Por tamanho (linhas e palavras)
# ================================================================

def _quartile_df(preds, info, col, quartiles) -> pd.DataFrame:
    merged = preds.merge(info[["id", col]], on="id", how="left")
    models = sorted(preds["model"].unique())
    rows = []
    for model in models:
        sub = merged[merged["model"] == model]
        for label, lo, hi in quartiles:
            grp = sub[sub[col] >= lo] if hi is None else sub[(sub[col] >= lo) & (sub[col] <= hi)]
            m = _metrics(grp)
            rows.append({"model": model, "quartile": _clean(label), **m})
    return pd.DataFrame(rows)


def section_54(preds: pd.DataFrame, info: pd.DataFrame, out: Path):
    logger.info("=== 5.4 Por tamanho ===")
    for col, quartiles, fname, title in [
        ("n_lines", LINE_QUARTILES,  "5.4_linhas",   "5.4 — Acurácia por Nº de Linhas (zero-shot)"),
        ("n_words", WORD_QUARTILES,  "5.4_palavras",  "5.4 — Acurácia por Nº de Palavras (zero-shot)"),
    ]:
        df = _quartile_df(preds, info, col, quartiles)
        df.to_csv(out / f"{fname}.csv", index=False)
        models = sorted(preds["model"].unique())
        qlabels_clean = [_clean(q[0]) for q in quartiles]

        fig, ax = plt.subplots(figsize=(9, 4.5))
        _bar_group(
            ax,
            [q[0] for q in quartiles],
            {m: [df[(df["model"] == m) & (df["quartile"] == q)]["accuracy"].values[0] for q in qlabels_clean] for m in models},
            title,
        )
        fig.tight_layout()
        fig.savefig(out / f"{fname}.png", dpi=150)
        plt.close(fig)

        print(f"\n{title}")
        print(df[["model", "quartile", "accuracy", "f1", "mcc", "n"]].to_string(
            index=False, float_format=lambda x: f"{x:.3f}"))


# ================================================================
# 5.5 — Por complexidade
# ================================================================

def section_55(preds: pd.DataFrame, out: Path):
    if not COMPLEXITY_FILE.exists():
        logger.warning("5.5 — %s nao encontrado. Coloque o arquivo e re-execute.", COMPLEXITY_FILE)
        print("\n5.5 — PULADO (complexity_scores.csv ausente)")
        return
    logger.info("=== 5.5 Por complexidade ===")

    comp = pd.read_csv(COMPLEXITY_FILE)
    comp = comp[comp["language"].isin(LANGUAGES)]
    comp_mean = comp.groupby("id")["complexity_score"].mean().reset_index()
    comp_mean.columns = ["id", "avg_complexity"]

    merged = preds.merge(comp_mean, on="id", how="left").dropna(subset=["avg_complexity"])
    models = sorted(merged["model"].unique())

    rows = []
    for model in models:
        sub = merged[merged["model"] == model]
        for blabel, lo, hi in COMPLEXITY_BINS:
            grp = sub[(sub["avg_complexity"] > lo) & (sub["avg_complexity"] <= hi)]
            m = _metrics(grp)
            rows.append({"model": model, "complexity": _clean(blabel), **m})
    df = pd.DataFrame(rows)
    df.to_csv(out / "5.5_complexidade.csv", index=False)

    bin_clean = [_clean(b[0]) for b in COMPLEXITY_BINS]
    fig, ax = plt.subplots(figsize=(9, 4.5))
    _bar_group(
        ax,
        [b[0] for b in COMPLEXITY_BINS],
        {m: [df[(df["model"] == m) & (df["complexity"] == b)]["accuracy"].values[0] for b in bin_clean] for m in models},
        "5.5 — Acurácia por Complexidade (zero-shot)",
    )
    fig.tight_layout()
    fig.savefig(out / "5.5_complexidade.png", dpi=150)
    plt.close(fig)

    print("\n5.5 — Por complexidade")
    print(df[["model", "complexity", "accuracy", "f1", "mcc", "n"]].to_string(
        index=False, float_format=lambda x: f"{x:.3f}"))


# ================================================================
# 5.6 — Confiança
# ================================================================

def section_56(preds: pd.DataFrame, out: Path):
    logger.info("=== 5.6 Confianca ===")
    valid = preds[preds["prediction"].isin(["human", "ai"])].copy()
    models = sorted(valid["model"].unique())

    # Determina unanimidade por snippet (todos os modelos concordam?)
    agree = valid.groupby("id")["prediction"].agg(lambda x: x.nunique() == 1)
    valid["unanimous"] = valid["id"].map(agree)

    # --- 5.6a: Unanimidade vs Divergencia ---
    rows_a = []
    for model in models:
        sub = valid[valid["model"] == model]
        for state_label, flag in [("unanime", True), ("divergente", False)]:
            m = _metrics(sub[sub["unanimous"] == flag])
            rows_a.append({"model": model, "estado": state_label, **m})
    df_a = pd.DataFrame(rows_a)
    df_a.to_csv(out / "5.6a_unanimidade.csv", index=False)
    print("\n5.6a — Unanimidade vs Divergencia")
    print(df_a[["model", "estado", "accuracy", "f1", "n"]].to_string(
        index=False, float_format=lambda x: f"{x:.3f}"))

    # --- 5.6b: Heatmaps de confianca media (true × pred), por estado ---
    n_m = len(models)
    fig, axes = plt.subplots(2, n_m, figsize=(4 * n_m, 7))
    if n_m == 1:
        axes = np.array(axes).reshape(2, 1)

    for col, model in enumerate(models):
        sub = valid[valid["model"] == model]
        for row, (state_label, flag) in enumerate([("Unânime", True), ("Divergente", False)]):
            ax = axes[row][col]
            grp = sub[sub["unanimous"] == flag]
            if len(grp) == 0:
                ax.text(0.5, 0.5, "sem dados", ha="center", va="center", transform=ax.transAxes, fontsize=9)
                ax.set_title(f"{model}\n{state_label}", fontsize=8)
                ax.axis("off")
                continue
            matrix = grp.groupby(["true_label", "prediction"])["confidence"].mean().unstack(fill_value=0)
            for c in ["human", "ai"]:
                if c not in matrix.columns:
                    matrix[c] = 0.0
            for r in ["human", "ai"]:
                if r not in matrix.index:
                    matrix.loc[r] = 0.0
            matrix = matrix.loc[["human", "ai"], ["human", "ai"]]
            sns.heatmap(matrix, ax=ax, annot=True, fmt=".1f", cmap="Blues",
                        vmin=0, vmax=10, cbar=False,
                        xticklabels=["pred:human", "pred:ai"],
                        yticklabels=["true:human", "true:ai"])
            ax.set_title(f"{model}\n{state_label} (n={len(grp)})", fontsize=8)
            if col > 0:
                ax.set_ylabel("")

    fig.suptitle("5.6b — Confiança Média por (true_label × prediction)", fontsize=11, fontweight="bold")
    fig.tight_layout()
    fig.savefig(out / "5.6b_confianca_heatmap.png", dpi=150)
    plt.close(fig)
    logger.info("5.6b salvo.")

    # --- 5.6c: Ensemble "modelo mais confiante por amostra" ---
    most_conf = (
        valid.loc[valid.groupby("id")["confidence"].idxmax()]
        [["id", "model", "prediction", "true_label", "confidence"]]
        .copy()
    )
    m_c = _metrics(most_conf)
    pd.DataFrame([{"ensemble": "mais_confiante", **m_c}]).to_csv(out / "5.6c_mais_confiante.csv", index=False)
    print(f"\n5.6c — Ensemble mais confiante:  acc={m_c['accuracy']:.3f}  f1={m_c['f1']:.3f}  n={m_c['n']}")


# ================================================================
# 5.7 — Votacao majoritaria (hard voting, zero-shot)
# ================================================================

def section_57(preds: pd.DataFrame, out: Path):
    logger.info("=== 5.7 Votacao majoritaria ===")
    valid = preds[preds["prediction"].isin(["human", "ai"])].copy()
    models = sorted(valid["model"].unique())
    n_models = len(models)

    if n_models < 2:
        logger.warning("5.7 — Votacao majoritaria requer >= 2 modelos. Pulando.")
        print("\n5.7 — PULADO (menos de 2 modelos)")
        return

    all_ids = valid["id"].unique()
    ai_votes    = (valid[valid["prediction"] == "ai"]
                   .groupby("id")["model"].count()
                   .reindex(all_ids, fill_value=0)
                   .rename("ai_votes"))
    total_votes = valid.groupby("id")["model"].count().rename("total_votes")
    true_labels = valid.groupby("id")["true_label"].first()

    ensemble = pd.concat([ai_votes, total_votes, true_labels], axis=1).dropna().reset_index()
    # Maioria estrita: AI se ai_votes > total_votes/2; empate -> human
    ensemble["prediction"] = (ensemble["ai_votes"] * 2 > ensemble["total_votes"]).map({True: "ai", False: "human"})

    m = _metrics(ensemble)
    threshold = f">={n_models // 2 + 1}/{n_models}"
    pd.DataFrame([{"ensemble": f"hard_voting ({threshold})", **m}]).to_csv(
        out / "5.7_votacao_majoritaria.csv", index=False)

    # Confusion matrix
    v = ensemble[ensemble["prediction"].isin(["human", "ai"])]
    y_true = (v["true_label"] == "ai").astype(int)
    y_pred = (v["prediction"] == "ai").astype(int)
    cm = confusion_matrix(y_true, y_pred)

    fig, ax = plt.subplots(figsize=(4.5, 3.8))
    sns.heatmap(
        pd.DataFrame(cm, index=["true: human", "true: ai"], columns=["pred: human", "pred: ai"]),
        annot=True, fmt="d", cmap="Blues", ax=ax, cbar=False,
    )
    ax.set_title(
        f"5.7 — Votação Majoritária ({threshold})\n"
        f"acc={m['accuracy']:.3f}  f1={m['f1']:.3f}  mcc={m['mcc']:.3f}",
        fontsize=9,
    )
    fig.tight_layout()
    fig.savefig(out / "5.7_votacao_majoritaria.png", dpi=150)
    plt.close(fig)

    print(f"\n5.7 — Votacao majoritaria ({threshold} modelos = ai)")
    print(f"  acc={m['accuracy']:.3f}  prec={m['precision']:.3f}  rec={m['recall']:.3f}"
          f"  f1={m['f1']:.3f}  mcc={m['mcc']:.3f}  n={m['n']}")


# ================================================================
# 5.8 — Analise de erros: falsos negativos
# ================================================================

def section_58(preds: pd.DataFrame, out: Path):
    logger.info("=== 5.8 Analise de erros ===")
    fn = preds[(preds["true_label"] == "ai") & (preds["prediction"] == "human")].copy()
    fn.to_csv(out / "5.8_falsos_negativos.csv", index=False)

    print(f"\n5.8 — Falsos negativos (AI classificado como 'human')")
    for model in sorted(preds["model"].unique()):
        sub = fn[fn["model"] == model]
        total_ai = len(preds[
            (preds["model"] == model) &
            (preds["true_label"] == "ai") &
            (preds["prediction"].isin(["human", "ai"]))
        ])
        print(f"\n  {model}: {len(sub)} / {total_ai} amostras AI classificadas como human")
        if "explanation" in sub.columns:
            for i, (_, row) in enumerate(sub.head(5).iterrows()):
                expl = str(row.get("explanation", "")).strip()[:130]
                lang = row.get("language", "?")
                print(f"    [{i+1}] ({lang}) {expl}")
    print(f"\n  Arquivo completo: {out / '5.8_falsos_negativos.csv'}")


# ================================================================
# Main
# ================================================================

def main():
    METRICS_DIR.mkdir(parents=True, exist_ok=True)

    preds = _load_predictions()
    info  = _load_dataset_info()

    section_53(preds, METRICS_DIR)
    section_54(preds, info, METRICS_DIR)
    section_55(preds, METRICS_DIR)
    section_56(preds, METRICS_DIR)
    section_57(preds, METRICS_DIR)
    section_58(preds, METRICS_DIR)

    print(f"\n{'='*60}")
    print(f"  Arquivos em: {METRICS_DIR}/")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
