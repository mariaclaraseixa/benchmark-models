"""
report.py — Gera PDF com relatório completo do benchmark AI vs Humano.

Uso:
    python report.py                # lê *_zero_shot.csv  (modo full)
    python report.py --sanity       # lê *_sanity.csv
    python report.py --all          # lê todos os CSVs de resultado

Gera: results/relatorio_benchmark_{timestamp}.pdf
Dependências: matplotlib seaborn pandas scikit-learn
"""

import argparse
import textwrap
import warnings
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages
from sklearn.metrics import (
    accuracy_score, confusion_matrix, f1_score,
    precision_score, recall_score, matthews_corrcoef, roc_auc_score,
)

warnings.filterwarnings("ignore")
plt.rcParams.update({"font.family": "DejaVu Sans", "figure.dpi": 150})

_HERE = Path(__file__).parent
RESULTS_DIR = _HERE / "results"
PALETTE = ["#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B2", "#937860"]
GOOD  = "#55A868"
BAD   = "#C44E52"
NEUT  = "#4C72B0"


# ================================================================
# Utilitários
# ================================================================

def _load(pattern: str) -> pd.DataFrame:
    frames = [pd.read_csv(p) for p in sorted(RESULTS_DIR.glob(pattern))]
    if not frames:
        raise FileNotFoundError(f"Nenhum '{pattern}' em {RESULTS_DIR}/")
    df = pd.concat(frames, ignore_index=True)
    df["prediction"] = df["prediction"].fillna("unknown")
    return df


def _metrics(df: pd.DataFrame) -> dict:
    """Calcula métricas de classificação binária (ai = positivo)."""
    v = df[df["prediction"].isin(["human", "ai"])].copy()
    n_inv = len(df) - len(v)
    nan = float("nan")
    if len(v) == 0:
        return {k: nan for k in ["acc","prec","rec","f1","mcc","auc","tp","fp","tn","fn","n","n_inv","fpr","fnr"]}
    y_true = (v["true_label"] == "ai").astype(int)
    y_pred = (v["prediction"] == "ai").astype(int)
    v = v.copy()
    if "confidence" in v.columns:
        v = v.copy()
        v["ai_score"] = v.apply(
            lambda r: r["confidence"] / 10 if r["prediction"] == "ai" else 1 - r["confidence"] / 10,
            axis=1,
        )
        try:
            auc = roc_auc_score(y_true, v["ai_score"]) if y_true.nunique() > 1 else nan
        except Exception:
            auc = nan
    else:
        auc = nan
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel()
    fpr = fp / (fp + tn) if (fp + tn) > 0 else nan  # taxa de falsos positivos
    fnr = fn / (fn + tp) if (fn + tp) > 0 else nan  # taxa de falsos negativos
    return {
        "acc":  accuracy_score(y_true, y_pred),
        "prec": precision_score(y_true, y_pred, zero_division=0),
        "rec":  recall_score(y_true, y_pred, zero_division=0),
        "f1":   f1_score(y_true, y_pred, zero_division=0),
        "mcc":  matthews_corrcoef(y_true, y_pred),
        "auc":  auc,
        "tp": int(tp), "fp": int(fp), "tn": int(tn), "fn": int(fn),
        "fpr": fpr, "fnr": fnr,
        "n": int(len(v)), "n_inv": int(n_inv),
    }


def _fmt(v, decimals=3):
    return f"{v:.{decimals}f}" if isinstance(v, float) and not np.isnan(v) else "—"


def _wrap(text: str, width: int = 90) -> str:
    return "\n".join(textwrap.wrap(str(text), width=width))


# ================================================================
# Páginas do PDF
# ================================================================

def _page_cover(pdf: PdfPages, preds: pd.DataFrame, mode: str):
    fig = plt.figure(figsize=(8.27, 11.69))
    fig.patch.set_facecolor("#F7F9FC")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_axis_off()

    models = sorted(preds["model"].unique())
    n_total = len(preds)
    n_valid = len(preds[preds["prediction"].isin(["human", "ai"])])
    langs   = sorted(preds["language"].unique())

    ax.text(0.5, 0.88, "Benchmark de Detecção", ha="center", va="center",
            fontsize=26, fontweight="bold", color="#1A2A44", transform=ax.transAxes)
    ax.text(0.5, 0.82, "Código AI vs Humano — Relatório Completo", ha="center",
            fontsize=17, color="#3A5070", transform=ax.transAxes)
    ax.plot([0.1, 0.9], [0.78, 0.78], color="#4C72B0", linewidth=2, transform=ax.transAxes)

    lines = [
        ("Data / hora",     datetime.now().strftime("%d/%m/%Y  %H:%M")),
        ("Modo",            mode.upper()),
        ("Modelos",         ", ".join(models)),
        ("Linguagens",      ", ".join(langs)),
        ("Predições totais", str(n_total)),
        ("Predições válidas", f"{n_valid}  ({n_valid/n_total*100:.0f}%)"),
    ]
    for i, (k, v) in enumerate(lines):
        y = 0.70 - i * 0.06
        ax.text(0.22, y, k + ":", ha="right", fontsize=12, color="#555", transform=ax.transAxes)
        ax.text(0.25, y, v,          ha="left",  fontsize=12, color="#1A2A44", fontweight="bold", transform=ax.transAxes)

    ax.text(0.5, 0.12, "Gerado automaticamente por report.py", ha="center",
            fontsize=9, color="#aaa", transform=ax.transAxes)
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


def _page_metrics_table(pdf: PdfPages, preds: pd.DataFrame):
    models = sorted(preds["model"].unique())
    rows, cols_hdr = [], ["Modelo", "N", "Inválidos", "Acc", "Precisão", "Recall", "F1", "MCC", "AUC-ROC", "TP", "FP", "TN", "FN"]
    for m in models:
        mt = _metrics(preds[preds["model"] == m])
        rows.append([
            m,
            mt["n"] + mt["n_inv"],
            mt["n_inv"],
            _fmt(mt["acc"]),
            _fmt(mt["prec"]),
            _fmt(mt["rec"]),
            _fmt(mt["f1"]),
            _fmt(mt["mcc"]),
            _fmt(mt["auc"]),
            mt["tp"], mt["fp"], mt["tn"], mt["fn"],
        ])

    fig, ax = plt.subplots(figsize=(14, max(3, len(models) * 1.2 + 2)))
    ax.set_axis_off()
    ax.set_title("Métricas por Modelo (ai = classe positiva)", fontsize=13, fontweight="bold", pad=14)
    t = ax.table(cellText=rows, colLabels=cols_hdr, loc="center", cellLoc="center")
    t.auto_set_font_size(False)
    t.set_fontsize(9)
    t.scale(1, 1.8)
    for j in range(len(cols_hdr)):
        t[0, j].set_facecolor("#4C72B0")
        t[0, j].set_text_props(color="white", fontweight="bold")
    for i in range(1, len(rows) + 1):
        clr = "#EAF0FB" if i % 2 == 0 else "white"
        for j in range(len(cols_hdr)):
            t[i, j].set_facecolor(clr)
    fig.tight_layout()
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


def _page_confusion_matrices(pdf: PdfPages, preds: pd.DataFrame):
    models = sorted(preds["model"].unique())
    n = len(models)
    fig, axes = plt.subplots(1, n, figsize=(5 * n, 4.5))
    if n == 1:
        axes = [axes]
    fig.suptitle("Matrizes de Confusão por Modelo  (ai = positivo)", fontsize=13, fontweight="bold")

    for ax, m in zip(axes, models):
        v = preds[(preds["model"] == m) & preds["prediction"].isin(["human", "ai"])]
        if len(v) == 0:
            ax.text(0.5, 0.5, "sem dados", ha="center", va="center")
            ax.set_title(m)
            continue
        y_true = (v["true_label"] == "ai").astype(int)
        y_pred = (v["prediction"] == "ai").astype(int)
        cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
        labels = ["Human", "AI"]
        cdf = pd.DataFrame(cm, index=[f"Real: {l}" for l in labels],
                              columns=[f"Pred: {l}" for l in labels])
        sns.heatmap(cdf, annot=True, fmt="d", cmap="Blues", ax=ax,
                    linewidths=0.5, cbar=False, annot_kws={"size": 13, "weight": "bold"})
        mt = _metrics(v)
        ax.set_title(f"{m}\nAcc={_fmt(mt['acc'])}  F1={_fmt(mt['f1'])}  MCC={_fmt(mt['mcc'])}", fontsize=9)

    # legenda
    fig.text(0.5, 0.01,
             "TN=Humano corretamente previsto | FP=Humano previsto como AI  |  FN=AI previsto como Humano  |  TP=AI corretamente previsto",
             ha="center", fontsize=7.5, color="#555")
    fig.tight_layout(rect=[0, 0.04, 1, 1])
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


def _page_f1_breakdown(pdf: PdfPages, preds: pd.DataFrame):
    models = sorted(preds["model"].unique())
    metrics_list = ["Precisão", "Recall", "F1-Score"]
    keys = ["prec", "rec", "f1"]
    x = np.arange(len(models))
    width = 0.22

    fig, ax = plt.subplots(figsize=(10, 5))
    for i, (metric, key) in enumerate(zip(metrics_list, keys)):
        vals = [_metrics(preds[preds["model"] == m])[key] for m in models]
        bars = ax.bar(x + i * width, vals, width, label=metric,
                      color=PALETTE[i], edgecolor="white")
        for bar, v in zip(bars, vals):
            if not np.isnan(v):
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                        f"{v:.2f}", ha="center", va="bottom", fontsize=8)

    ax.set_xticks(x + width)
    ax.set_xticklabels(models, fontsize=9)
    ax.set_ylim(0, 1.18)
    ax.set_ylabel("Score")
    ax.set_title("Precisão / Recall / F1-Score por Modelo  (ai = classe positiva)", fontsize=12, fontweight="bold")
    ax.legend(fontsize=9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    fig.text(0.5, 0.01,
             "Precisão = TP/(TP+FP) — penaliza falsos positivos  |  "
             "Recall = TP/(TP+FN) — penaliza falsos negativos  |  "
             "F1 = média harmônica entre precisão e recall",
             ha="center", fontsize=8, color="#555")
    fig.tight_layout(rect=[0, 0.06, 1, 1])
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


def _page_fp_fn_analysis(pdf: PdfPages, preds: pd.DataFrame):
    models = sorted(preds["model"].unique())
    x = np.arange(len(models))
    width = 0.32

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle("Análise de Erros: Falsos Positivos e Falsos Negativos", fontsize=13, fontweight="bold")

    # Contagens absolutas
    ax = axes[0]
    fp_counts = [_metrics(preds[preds["model"] == m])["fp"] for m in models]
    fn_counts = [_metrics(preds[preds["model"] == m])["fn"] for m in models]
    b1 = ax.bar(x - width / 2, fp_counts, width, label="FP (Humano → AI)", color=BAD, edgecolor="white")
    b2 = ax.bar(x + width / 2, fn_counts, width, label="FN (AI → Humano)", color="#E69000", edgecolor="white")
    for bar in list(b1) + list(b2):
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, h + 0.1, str(int(h)),
                ha="center", va="bottom", fontsize=10, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(models, fontsize=9)
    ax.set_title("Contagem absoluta de erros")
    ax.set_ylabel("Quantidade")
    ax.legend(fontsize=9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Taxas
    ax = axes[1]
    fpr_vals = [_metrics(preds[preds["model"] == m])["fpr"] for m in models]
    fnr_vals = [_metrics(preds[preds["model"] == m])["fnr"] for m in models]
    b1 = ax.bar(x - width / 2, fpr_vals, width, label="FPR — Taxa de Falsos Positivos", color=BAD, edgecolor="white")
    b2 = ax.bar(x + width / 2, fnr_vals, width, label="FNR — Taxa de Falsos Negativos", color="#E69000", edgecolor="white")
    for bar in list(b1) + list(b2):
        v = bar.get_height()
        if not np.isnan(v):
            ax.text(bar.get_x() + bar.get_width() / 2, v + 0.01,
                    f"{v:.2f}", ha="center", va="bottom", fontsize=9)
    ax.set_xticks(x)
    ax.set_xticklabels(models, fontsize=9)
    ax.set_title("Taxas de erro")
    ax.set_ylim(0, 1.15)
    ax.set_ylabel("Taxa (0–1)")
    ax.legend(fontsize=9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    fig.text(0.5, 0.01,
             "FP: código humano classificado como AI  |  FN: código AI classificado como humano\n"
             "FPR = FP/(FP+TN)  |  FNR = FN/(FN+TP)",
             ha="center", fontsize=8, color="#555")
    fig.tight_layout(rect=[0, 0.07, 1, 1])
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


def _page_confidence(pdf: PdfPages, preds: pd.DataFrame):
    valid = preds[preds["prediction"].isin(["human", "ai"])].copy()
    valid["correto"] = valid["prediction"] == valid["true_label"]
    models = sorted(valid["model"].unique())

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle("Distribuição de Confiança dos Modelos", fontsize=13, fontweight="bold")

    # Boxplot por modelo separado por correto/errado
    ax = axes[0]
    data_plot, labels_plot, colors_plot = [], [], []
    for m in models:
        sub = valid[valid["model"] == m]
        data_plot.append(sub[sub["correto"]]["confidence"].values)
        data_plot.append(sub[~sub["correto"]]["confidence"].values)
        labels_plot += [f"{m}\nCerto", f"{m}\nErrado"]
        colors_plot += [GOOD, BAD]

    bps = ax.boxplot(data_plot, labels=labels_plot, patch_artist=True,
                     medianprops={"color": "black", "linewidth": 2})
    for patch, color in zip(bps["boxes"], colors_plot):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    ax.set_ylabel("Confiança (0–10)")
    ax.set_title("Confiança: acertos vs erros")
    ax.tick_params(axis="x", labelsize=7)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Histograma acumulado por modelo
    ax = axes[1]
    for i, m in enumerate(models):
        sub = valid[valid["model"] == m]
        ax.hist(sub["confidence"], bins=10, range=(0, 10), alpha=0.6,
                label=m, color=PALETTE[i], edgecolor="white", density=True)
    ax.set_xlabel("Confiança (0–10)")
    ax.set_ylabel("Densidade")
    ax.set_title("Histograma de confiança por modelo")
    ax.legend(fontsize=8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    fig.tight_layout()
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


def _page_by_language(pdf: PdfPages, preds: pd.DataFrame):
    valid  = preds[preds["prediction"].isin(["human", "ai"])].copy()
    models = sorted(valid["model"].unique())
    langs  = sorted(valid["language"].unique())

    metrics_to_show = [("Acurácia", "acc"), ("F1-Score", "f1"), ("Precisão", "prec"), ("Recall", "rec")]
    fig, axes = plt.subplots(1, len(metrics_to_show), figsize=(14, 5))
    fig.suptitle("Métricas por Linguagem", fontsize=13, fontweight="bold")
    x = np.arange(len(langs))
    width = 0.6 / max(len(models), 1)

    for ax, (label, key) in zip(axes, metrics_to_show):
        for i, m in enumerate(models):
            vals = []
            for lang in langs:
                sub = valid[(valid["model"] == m) & (valid["language"] == lang)]
                v = _metrics(sub)[key]
                vals.append(v if not np.isnan(v) else 0)
            bars = ax.bar(x + i * width - (len(models) - 1) * width / 2, vals, width,
                          label=m, color=PALETTE[i], edgecolor="white")
            for bar, v in zip(bars, vals):
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                        f"{v:.2f}", ha="center", va="bottom", fontsize=7)
        ax.set_xticks(x)
        ax.set_xticklabels(langs, fontsize=10)
        ax.set_ylim(0, 1.2)
        ax.set_title(label)
        ax.set_ylabel(label if ax == axes[0] else "")
        if ax == axes[-1]:
            ax.legend(fontsize=7, loc="upper right")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    fig.tight_layout()
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


def _page_ensemble(pdf: PdfPages, preds: pd.DataFrame):
    valid  = preds[preds["prediction"].isin(["human", "ai"])].copy()
    models = sorted(valid["model"].unique())

    if len(models) < 2:
        return

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle("Análise de Ensemble — Votação Majoritária", fontsize=13, fontweight="bold")

    # Votação majoritária
    ai_votes    = valid[valid["prediction"] == "ai"].groupby("id")["model"].count().rename("ai_votes")
    total_votes = valid.groupby("id")["model"].count().rename("total_votes")
    true_labels = valid.groupby("id")["true_label"].first()
    ens = pd.concat([ai_votes, total_votes, true_labels], axis=1).dropna().reset_index()
    ens["ai_votes"] = ens["ai_votes"].fillna(0)
    ens["prediction"] = (ens["ai_votes"] * 2 > ens["total_votes"]).map({True: "ai", False: "human"})

    mt_ens = _metrics(ens)

    # Confusion matrix do ensemble
    ax = axes[0]
    y_true = (ens["true_label"] == "ai").astype(int)
    y_pred = (ens["prediction"] == "ai").astype(int)
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    cdf = pd.DataFrame(cm, index=["Real: Human", "Real: AI"], columns=["Pred: Human", "Pred: AI"])
    sns.heatmap(cdf, annot=True, fmt="d", cmap="Blues", ax=ax, cbar=False,
                annot_kws={"size": 14, "weight": "bold"})
    threshold = f">={len(models)//2+1}/{len(models)}"
    ax.set_title(f"Ensemble Majoritário ({threshold} votos = AI)\n"
                 f"Acc={_fmt(mt_ens['acc'])}  F1={_fmt(mt_ens['f1'])}  MCC={_fmt(mt_ens['mcc'])}")

    # Comparativo: ensemble vs modelos individuais
    ax = axes[1]
    all_models = models + ["Ensemble"]
    all_f1  = [_metrics(valid[valid["model"] == m])["f1"]  for m in models] + [mt_ens["f1"]]
    all_acc = [_metrics(valid[valid["model"] == m])["acc"] for m in models] + [mt_ens["acc"]]
    x = np.arange(len(all_models))
    width = 0.35
    b1 = ax.bar(x - width / 2, all_acc, width, label="Acurácia", color=NEUT, edgecolor="white")
    b2 = ax.bar(x + width / 2, all_f1,  width, label="F1-Score", color=GOOD, edgecolor="white")
    for bar in list(b1) + list(b2):
        v = bar.get_height()
        if not np.isnan(v):
            ax.text(bar.get_x() + bar.get_width() / 2, v + 0.01,
                    f"{v:.2f}", ha="center", va="bottom", fontsize=8)
    ax.set_xticks(x)
    ax.set_xticklabels(all_models, fontsize=9)
    ax.set_ylim(0, 1.2)
    ax.set_title("Ensemble vs Modelos Individuais")
    ax.legend(fontsize=9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    fig.tight_layout()
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


def _page_errors_detail(pdf: PdfPages, preds: pd.DataFrame):
    models = sorted(preds["model"].unique())

    for m in models:
        sub = preds[preds["model"] == m].copy()
        fp_rows = sub[(sub["true_label"] == "human") & (sub["prediction"] == "ai")]
        fn_rows = sub[(sub["true_label"] == "ai")    & (sub["prediction"] == "human")]

        if len(fp_rows) == 0 and len(fn_rows) == 0:
            continue

        fig = plt.figure(figsize=(8.27, 11.69))
        fig.patch.set_facecolor("#FAFAFA")
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_axis_off()

        ax.text(0.5, 0.97, f"Análise de Erros — {m}", ha="center", fontsize=13,
                fontweight="bold", color="#1A2A44", transform=ax.transAxes)
        ax.plot([0.05, 0.95], [0.95, 0.95], color="#4C72B0", linewidth=1, transform=ax.transAxes)

        y = 0.92
        for title, rows, color in [
            (f"Falsos Positivos — Humano classificado como AI  ({len(fp_rows)} casos)", fp_rows, BAD),
            (f"Falsos Negativos — AI classificado como Humano  ({len(fn_rows)} casos)", fn_rows, "#E69000"),
        ]:
            ax.text(0.05, y, title, ha="left", fontsize=10, fontweight="bold",
                    color=color, transform=ax.transAxes)
            y -= 0.03
            for _, row in rows.iterrows():
                if y < 0.05:
                    break
                expl = _wrap(row.get("explanation", ""), 100)
                snippet = f"  [id={row['id']} | {row['language']} | conf={row['confidence']}]  {expl}"
                for line in snippet.split("\n"):
                    ax.text(0.05, y, line, ha="left", fontsize=7.5, color="#333",
                            transform=ax.transAxes, family="monospace")
                    y -= 0.025
                    if y < 0.05:
                        break
                y -= 0.01
            y -= 0.02

        pdf.savefig(fig, bbox_inches="tight")
        plt.close(fig)


def _page_predictions_table(pdf: PdfPages, preds: pd.DataFrame):
    models = sorted(preds["model"].unique())
    for m in models:
        sub = preds[preds["model"] == m][["id", "language", "true_label", "prediction", "confidence"]].copy()
        sub["ok"] = sub["prediction"] == sub["true_label"]
        sub["prediction"] = sub.apply(
            lambda r: r["prediction"] if r["prediction"] in ("human", "ai") else "—", axis=1)

        n_rows = len(sub)
        fig, ax = plt.subplots(figsize=(10, max(3, n_rows * 0.35 + 2)))
        ax.set_axis_off()
        ax.set_title(f"Predições completas — {m}", fontsize=11, fontweight="bold", pad=12)

        cell_data = sub[["id", "language", "true_label", "prediction", "confidence"]].values.tolist()
        t = ax.table(
            cellText=cell_data,
            colLabels=["ID", "Linguagem", "Rótulo Real", "Predição", "Confiança"],
            loc="center", cellLoc="center",
        )
        t.auto_set_font_size(False)
        t.set_fontsize(9)
        t.scale(1, 1.6)

        for j in range(5):
            t[0, j].set_facecolor("#4C72B0")
            t[0, j].set_text_props(color="white", fontweight="bold")

        for i, (_, row) in enumerate(sub.iterrows(), start=1):
            ok = row["prediction"] == row["true_label"]
            base = "#E8F5E9" if ok else "#FFEBEE"
            for j in range(5):
                t[i, j].set_facecolor(base)

        fig.tight_layout()
        pdf.savefig(fig, bbox_inches="tight")
        plt.close(fig)


# ================================================================
# Main
# ================================================================

def main():
    parser = argparse.ArgumentParser(description="Gera PDF do benchmark AI vs Humano")
    grp = parser.add_mutually_exclusive_group()
    grp.add_argument("--sanity", action="store_true", help="Lê *_sanity.csv")
    grp.add_argument("--all",    action="store_true", help="Lê todos os CSVs de resultado")
    args = parser.parse_args()

    if args.sanity:
        pattern, mode = "*_sanity.csv", "sanity"
    elif args.all:
        pattern, mode = "*.csv", "all"
    else:
        pattern, mode = "*_zero_shot.csv", "full"

    print(f"Carregando arquivos: results/{pattern}")
    preds = _load(pattern)
    # remove complexity_scores.csv se lido acidentalmente
    if "complexity_score" in preds.columns or "avg_complexity" in preds.columns:
        preds = preds[preds["prediction"].notna() & preds.get("model", pd.Series()).notna()]
    preds = preds[preds["model"].notna()].copy()

    ts  = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = RESULTS_DIR / f"relatorio_benchmark_{ts}.pdf"

    print(f"Gerando PDF: {out.name}")
    with PdfPages(out) as pdf:
        _page_cover(pdf, preds, mode)
        _page_metrics_table(pdf, preds)
        _page_confusion_matrices(pdf, preds)
        _page_f1_breakdown(pdf, preds)
        _page_fp_fn_analysis(pdf, preds)
        _page_confidence(pdf, preds)
        _page_by_language(pdf, preds)
        _page_ensemble(pdf, preds)
        _page_errors_detail(pdf, preds)
        _page_predictions_table(pdf, preds)

        info = pdf.infodict()
        info["Title"]   = "Benchmark Detecção AI vs Humano"
        info["Author"]  = "report.py — gerado automaticamente"
        info["Subject"] = "TCC — Detecção de Código Gerado por IA"

    print(f"\nPDF salvo em: {out}")
    print(f"  Páginas: capas + métricas + matrizes + F1 + FP/FN + confiança + linguagem + ensemble + erros + tabelas")


if __name__ == "__main__":
    main()
