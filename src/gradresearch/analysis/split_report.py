"""Markdown report on how balanced the cross-validation folds are."""

from __future__ import annotations

import datetime as _dt
from pathlib import Path
from typing import Optional

import pandas as pd

from ..data.splits import balance_summary, balance_table, fingerprint, fold_roles
from .dataset_report import md_table

# Pre-set tolerances for calling the folds "balanced" (relative deviation from the fold mean,
# except positive_rate and AP_share, which use absolute differences in proportion).
TOLERANCE = {"images": 0.05, "patients": 0.05, "positive_rate": 0.01, "AP_share": 0.01, "strata": 0.10}


def judge(summary: pd.DataFrame, table: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for col, s in summary.iterrows():
        if col in ("positive_rate", "AP_share"):
            dev = float((table[col] - table[col].mean()).abs().max())
            tol = TOLERANCE[col]
            kind = "abs"
        elif col in ("images", "patients"):
            dev, tol, kind = s["max_rel_dev"], TOLERANCE[col], "rel"
        else:
            dev, tol, kind = s["max_rel_dev"], TOLERANCE["strata"], "rel"
        rows.append({"column": col, "deviation": dev, "kind": kind, "tolerance": tol, "ok": "OK" if dev <= tol else "偏りあり"})
    return pd.DataFrame(rows).set_index("column")


def build_split_report(images: pd.DataFrame, folds: pd.DataFrame, n_folds: int, seed: int, out: Path, date: Optional[str] = None) -> Path:
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    table = balance_table(images, folds)
    summary = balance_summary(table)
    verdict = judge(summary, table)
    roles = pd.DataFrame(
        [{"run": k, **{r: ", ".join(map(str, v)) for r, v in fold_roles(k, n_folds).items()}} for k in range(n_folds)]
    ).set_index("run")
    largest = images.groupby("nih_patient_id").size().nlargest(5).rename("images").to_frame()
    largest.index = largest.index.astype(str)  # an ID, not a quantity
    n_bad = int((verdict["ok"] != "OK").sum())
    md = [
        "# 交差検証の分割の確認（患者単位）",
        "",
        f"- 作成日：{date or _dt.date.today().isoformat()}",
        "- 作成方法：`scripts/make_splits.py`（`src/gradresearch/data/splits.py`）",
        f"- 分割数：{n_folds}、シード：{seed}、指紋（fingerprint）：`{fingerprint(folds)}`",
        "- 同じ患者の画像はすべて同じ組に入ります。集計は解析対象（最終ラベルのある画像）だけです。",
        f"- 判定：許容範囲を超えた項目は **{n_bad} 件**です。",
        "",
        "## 各組の内訳",
        "",
        md_table(table),
        "",
        "## 偏りの判定",
        "",
        "deviation は、組の平均からの最大のずれです（kind=rel は平均に対する割合、kind=abs は割合の差）。",
        "",
        md_table(verdict),
        "",
        "## 各回の役割（ローテーション）",
        "",
        md_table(roles),
        "",
        "## 画像が多い患者（上位 5 人）",
        "",
        md_table(largest),
        "",
    ]
    table.to_csv(out / "fold_balance.csv")
    verdict.to_csv(out / "fold_balance_verdict.csv")
    path = out / "fold_balance.md"
    path.write_text("\n".join(md), encoding="utf-8")
    return path
