"""
Executa 5 rodadas full do benchmark em sequência.
Após cada rodada, modelos com < 80% de predições válidas são adicionados
ao SKIP_MODELS de run.py e o motivo é registrado no README.
"""
import re
import subprocess
import sys
import time
from pathlib import Path

import pandas as pd

PYTHON      = sys.executable
RUN_PY      = Path("run.py")
README      = Path("README.md")
RESULTS_DIR = Path("results")
ROUNDS      = 5
MIN_VALID   = 0.80   # taxa mínima de predições válidas por rodada


def _get_new_csvs(before: set[Path]) -> dict[str, Path]:
    """Retorna {model_name: csv_path} para CSVs zero_shot criados após 'before'."""
    after = set(RESULTS_DIR.glob("*_zero_shot.csv"))
    new   = after - before
    by_model: dict[str, Path] = {}
    for f in new:
        parts = f.stem.split("_")
        # formato: modelname_YYYYMMDD_HHMMSS_zero_shot → últimos 3 campos são timestamp+sufixo
        model = "_".join(parts[:-3])
        by_model[model] = f
    return by_model


def _update_skip_models(to_skip: list[str]) -> None:
    """Sobrescreve a linha SKIP_MODELS em run.py."""
    content = RUN_PY.read_text(encoding="utf-8")
    quoted  = ", ".join(f'"{m}"' for m in to_skip)
    content = re.sub(
        r"^SKIP_MODELS: list = \[.*?\]",
        f"SKIP_MODELS: list = [{quoted}]",
        content,
        flags=re.MULTILINE,
    )
    RUN_PY.write_text(content, encoding="utf-8")


def _append_readme(round_num: int, exclusions: dict[str, str]) -> None:
    """Adiciona nota de exclusão ao README na seção de achados."""
    content = README.read_text(encoding="utf-8")
    note = (
        f"\n**Rodada {round_num} — modelos excluídos por baixa taxa de válidos "
        f"(< {MIN_VALID:.0%}):**\n"
    )
    for model, reason in exclusions.items():
        note += f"- `{model}`: {reason} — removido das rodadas seguintes\n"
    README.write_text(content + note, encoding="utf-8")


def main() -> None:
    all_excluded: dict[str, str] = {}

    for round_num in range(1, ROUNDS + 1):
        print(f"\n{'='*65}")
        print(f"  RODADA {round_num}/{ROUNDS}  |  {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*65}\n")

        before = set(RESULTS_DIR.glob("*_zero_shot.csv"))
        subprocess.run([PYTHON, str(RUN_PY)], check=False)

        if round_num == ROUNDS:
            break

        new_csvs     = _get_new_csvs(before)
        round_excl   = {}

        for model, csv_path in new_csvs.items():
            df    = pd.read_csv(csv_path)
            valid = int(df["prediction"].isin(["human", "ai"]).sum())
            total = len(df)
            rate  = valid / total if total else 0.0
            status = "OK" if rate >= MIN_VALID else "EXCLUINDO"
            print(f"  {status:<10} {model:<35} {valid}/{total} válidos ({rate:.0%})")

            if rate < MIN_VALID and model not in all_excluded:
                reason = f"rodada {round_num}: {valid}/{total} válidos ({rate:.0%})"
                round_excl[model]    = reason
                all_excluded[model] = reason

        if round_excl:
            _update_skip_models(list(all_excluded.keys()))
            _append_readme(round_num, round_excl)
            print(f"\n  -> SKIP_MODELS atualizado: {list(all_excluded.keys())}")

    print(f"\n{'='*65}")
    print(f"  CONCLUÍDO — {ROUNDS} rodadas  |  {time.strftime('%Y-%m-%d %H:%M:%S')}")
    if all_excluded:
        print(f"  Excluídos ao longo das rodadas:")
        for m, r in all_excluded.items():
            print(f"    - {m}: {r}")
    else:
        print("  Nenhum modelo excluído.")
    print(f"{'='*65}")


if __name__ == "__main__":
    main()
