"""Dataset inspection report (Markdown + CSV + JSON) built from the processed tables.

Covers the post-download checks of the progress report (section 2.4) and the items
listed in ``docs/dataset/rsna_pneumonia_2018.md`` section 11: integrity, image-annotation
correspondence, label distribution, view position / age / sex / pixel spacing, bounding
boxes, readers and patients.
"""

from __future__ import annotations

import datetime as _dt
import json
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

from ..data.annotations import CLASSES, OPACITY, READER_GROUPS

IMG = 1024

CAPTIONS = {
    "final_class": "最終ラベル（3クラス）の件数。",
    "selection_x_class": "画像選定時の NIH ラベルによるグループ（行）と最終ラベル（列）。",
    "stage1_x_multiread": "Kaggle stage 1 train に含まれるか（行）と、3人読影か（列）。",
    "view_x_class": "撮影方向（行）と最終ラベル（列）。positive_rate は Lung Opacity の割合。",
    "sex_x_class": "性別（行）と最終ラベル（列）。",
    "age_by_class": "最終ラベルごとの年齢の分布。100 歳を超える値は入力ミスと考えられる。",
    "pixel_spacing_x_view": "PixelSpacing（mm、小数3桁に丸めた値）と撮影方向の組み合わせごとの枚数と陽性率。撮影機器の違いを反映している可能性がある。",
    "image_format": "画像形式に関する DICOM ヘッダの値（30,000 枚すべて）。",
    "boxes_per_positive_image": "陽性画像1枚あたりの BBox の数。",
    "box_size_by_read": "BBox の幅・高さ（ピクセル）と画像に占める面積の割合。3人読影（交差）と1人読影で比較。",
    "box_center": "BBox の中心座標（ピクセル）の分布。",
    "box_side": "BBox の中心が画像の左右どちらにあるか（画像の左 = 患者の右肺側）。",
    "box_bounds": "画像の外にはみ出した BBox の数。",
    "readers_per_image": "1枚を何人の読影者（Team 1 / 2 / 2a）が読んだか。",
    "reader_box_probability": "読影者が描いた BBox の確率の内訳。",
    "reader_workload": "読影者ごとの担当枚数。",
    "multi_read_positive_votes_x_final": "3人読影の画像で、陽性（BBox あり）と読んだ読影者の数（行）と最終ラベル（列）。",
    "images_per_patient": "NIH の患者 ID ごとの画像枚数の分布。",
}

NUMBER_NOTES = {
    "positive_images": "最終ラベルが Lung Opacity の画像数",
    "positive_rate": "陽性率",
    "final_boxes": "最終ラベルの BBox の総数",
    "multi_read_images": "3人読影の画像数（RSNA の説明では 4,527）",
    "adjudicated_images": "調整（Adjudication）の記録がある画像数",
    "ap_share_all": "全体に占める AP の割合",
    "ap_share_positive": "陽性画像に占める AP の割合",
    "auc_view_only": "撮影方向（AP=1）だけで陽性を予測したときの ROC-AUC",
    "age_over_100": "年齢が 100 を超える画像数",
    "age_max": "年齢の最大値",
    "multi_read_images_with_3_reads": "Team 1 / 2 / 2a の3人の判定がそろう3人読影の画像数",
    "fleiss_kappa_binary": "3人の一致度（陽性かどうか、Fleiss の κ）",
    "fleiss_kappa_3class": "3人の一致度（3クラス、Fleiss の κ）",
    "unanimous_binary_share": "3人の陽性・陰性の判定が全員一致した割合",
    "single_read_reader_equals_final": "1人読影の画像で、読影者の判定と最終ラベルが一致する割合",
    "patients": "NIH の患者 ID の数",
    "max_images_per_patient": "1人あたりの最大画像枚数",
    "patients_with_both_positive_and_negative_images": "陽性と陰性の両方の画像を持つ患者数",
    "patients_in_both_multi_and_single_read": "3人読影と1人読影の両方に画像がある患者数",
    "multi_read_images_whose_patient_has_single_read_images": "3人読影の画像のうち、同じ患者の1人読影画像がある枚数",
    "patients_in_both_stage1_train_and_rest": "Kaggle stage 1 train とそれ以外の両方に画像がある患者数",
}


# ---------------------------------------------------------------- formatting helpers
def md_table(df: pd.DataFrame, index: bool = True, floatfmt: str = "{:.3f}") -> str:
    d = df.reset_index() if index else df

    def fmt(v):
        if isinstance(v, (float, np.floating)):
            if np.isnan(v):
                return ""
            return f"{int(v):,}" if float(v).is_integer() else floatfmt.format(v)
        if isinstance(v, (int, np.integer)):
            return f"{int(v):,}"
        return str(v)

    cols = [str(c) for c in d.columns]
    lines = ["| " + " | ".join(cols) + " |", "|" + "|".join("---" for _ in cols) + "|"]
    for row in d.itertuples(index=False):
        lines.append("| " + " | ".join(fmt(v) for v in row) + " |")
    return "\n".join(lines)


def pct(n: float, d: float) -> str:
    return f"{100 * n / d:.1f}%" if d else "-"


def auc(score: pd.Series, target: pd.Series) -> float:
    """ROC-AUC via the Mann-Whitney statistic (ties count one half)."""
    s, t = pd.Series(score).reset_index(drop=True), pd.Series(target).astype(int).reset_index(drop=True)
    n_pos, n_neg = int(t.sum()), int((1 - t).sum())
    if n_pos == 0 or n_neg == 0:
        return float("nan")
    ranks = s.rank(method="average")
    return float((ranks[t == 1].sum() - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg))


def fleiss_kappa(counts: np.ndarray) -> float:
    """Fleiss' kappa for an (items x categories) matrix of rating counts (same raters per item)."""
    counts = np.asarray(counts, dtype=float)
    n = counts.sum(axis=1)
    if len(counts) == 0 or not np.all(n == n[0]) or n[0] < 2:
        return float("nan")
    n = n[0]
    p_j = counts.sum(axis=0) / counts.sum()
    p_i = ((counts**2).sum(axis=1) - n) / (n * (n - 1))
    p_bar, p_e = p_i.mean(), (p_j**2).sum()
    return float((p_bar - p_e) / (1 - p_e)) if p_e < 1 else float("nan")


# ---------------------------------------------------------------- analyses
def label_tables(images: pd.DataFrame) -> dict[str, pd.DataFrame]:
    lab = images[images["has_final_label"]]
    out = {}
    cls = lab["final_class"].value_counts().reindex(CLASSES)
    out["final_class"] = pd.DataFrame({"images": cls, "share": cls / cls.sum()})
    out["selection_x_class"] = pd.crosstab(images["selection_group"], images["final_class"].fillna("(no final label)"), margins=True)
    if "kaggle_stage1_train" in images:
        out["stage1_x_multiread"] = pd.crosstab(
            images["kaggle_stage1_train"].map({True: "stage1_train", False: "not_stage1"}),
            images["multi_read"].map({True: "multi_read", False: "single_read"}),
            margins=True,
        )
    return out


def metadata_tables(images: pd.DataFrame) -> dict[str, pd.DataFrame]:
    lab = images[images["has_final_label"]].copy()
    out = {}
    ct = pd.crosstab(lab["view"], lab["final_class"]).reindex(columns=CLASSES)
    ct["positive_rate"] = lab.groupby("view")["target"].mean()
    out["view_x_class"] = ct
    ct = pd.crosstab(lab["sex"], lab["final_class"]).reindex(columns=CLASSES)
    ct["positive_rate"] = lab.groupby("sex")["target"].mean()
    out["sex_x_class"] = ct
    out["age_by_class"] = lab.groupby("final_class")["age"].describe(percentiles=[0.25, 0.5, 0.75]).reindex(CLASSES)
    lab["pixel_spacing_mm"] = lab["pixel_spacing"].round(3)
    sp = lab.groupby(["pixel_spacing_mm", "view"]).agg(images=("image_id", "size"), positive_rate=("target", "mean")).reset_index()
    out["pixel_spacing_x_view"] = sp.sort_values("images", ascending=False).set_index(["pixel_spacing_mm", "view"])
    fmt = {}
    for col in ("rows", "cols", "bits_stored", "photometric", "transfer_syntax", "modality", "body_part"):
        fmt[col] = images[col].astype(str).value_counts().to_dict()
    out["image_format"] = pd.DataFrame(
        [{"field": k, "values": ", ".join(f"{v} ({n:,})" for v, n in d.items())} for k, d in fmt.items()]
    ).set_index("field")
    return out


def box_tables(images: pd.DataFrame, boxes: pd.DataFrame) -> dict[str, pd.DataFrame]:
    b = boxes.merge(images[["image_id", "multi_read", "view"]], on="image_id", how="left")
    b["area_frac"] = b["w"] * b["h"] / (IMG * IMG)
    b["cx"] = b["x"] + b["w"] / 2
    b["cy"] = b["y"] + b["h"] / 2
    b["read"] = b["multi_read"].map({True: "multi_read", False: "single_read"})
    out = {}
    pos = images[images["has_final_label"] & (images["target"] == 1)]
    out["boxes_per_positive_image"] = pos["n_boxes"].value_counts().sort_index().rename("images").to_frame()
    desc = b.groupby("read")[["w", "h", "area_frac"]].describe(percentiles=[0.5]).T
    desc = desc.loc[(slice(None), ["mean", "50%", "min", "max"]), :]
    desc.index = desc.index.set_names(["measure", "stat"])
    out["box_size_by_read"] = desc
    out["box_center"] = b[["cx", "cy"]].describe(percentiles=[0.1, 0.5, 0.9]).T.rename_axis("coordinate")
    side = np.where(b["cx"] < IMG / 2, "image left (patient's right)", "image right (patient's left)")
    out["box_side"] = pd.Series(side).value_counts().rename("boxes").rename_axis("side").to_frame()
    outside = ((b["x"] < 0) | (b["y"] < 0) | (b["x"] + b["w"] > IMG) | (b["y"] + b["h"] > IMG)).sum()
    out["box_bounds"] = pd.DataFrame({"boxes": [len(b)], "outside_image": [int(outside)]}).rename_axis("row")
    return out


def reader_tables(images: pd.DataFrame, reads: pd.DataFrame, reader_boxes: pd.DataFrame) -> tuple[dict, dict]:
    out, numbers = {}, {}
    out["readers_per_image"] = images["n_readers"].value_counts().sort_index().rename("images").to_frame()
    rb = reader_boxes.copy()
    out["reader_box_probability"] = pd.crosstab(rb["group"], rb["probability"]).reindex(columns=["high", "medium", "low"])
    r = reads[reads["reader_class"].notna()]
    workload = r.groupby(["group", "reader_id"]).size().rename("images").reset_index()
    out["reader_workload"] = workload.sort_values(["group", "images"], ascending=[True, False]).set_index(["group", "reader_id"])

    multi = images.loc[images["multi_read"], "image_id"]
    mr = r[r["image_id"].isin(multi) & r["group"].isin(READER_GROUPS)]
    first = mr.drop_duplicates(["image_id", "group"])  # one read per group
    wide = first.pivot(index="image_id", columns="group", values="reader_class").dropna()
    if len(wide):
        cat = np.stack([(wide == c).sum(axis=1).to_numpy() for c in CLASSES], axis=1)
        binary = np.stack([cat[:, 0], cat[:, 1] + cat[:, 2]], axis=1)
        numbers["multi_read_images_with_3_reads"] = int(len(wide))
        numbers["fleiss_kappa_binary"] = round(fleiss_kappa(binary), 3)
        numbers["fleiss_kappa_3class"] = round(fleiss_kappa(cat), 3)
        numbers["unanimous_binary_share"] = round(float(((binary == 3).any(axis=1)).mean()), 3)
    fin = images.set_index("image_id")
    m = images[images["multi_read"] & images["has_final_label"]]
    out["multi_read_positive_votes_x_final"] = pd.crosstab(m["n_positive_reads"], m["final_class"]).reindex(columns=CLASSES)

    single = images[~images["multi_read"] & images["has_final_label"] & (images["n_readers"] == 1)]
    sr = r[r["image_id"].isin(single["image_id"])].drop_duplicates("image_id").set_index("image_id")
    agree = (sr["reader_class"] == fin.loc[sr.index, "final_class"]).mean() if len(sr) else float("nan")
    numbers["single_read_reader_equals_final"] = round(float(agree), 4)
    return out, numbers


def patient_tables(images: pd.DataFrame) -> tuple[dict, dict]:
    out, numbers = {}, {}
    per = images.groupby("nih_patient_id")
    n_img = per.size()
    bins = pd.cut(n_img, [0, 1, 2, 5, 10, 20, np.inf], labels=["1", "2", "3-5", "6-10", "11-20", "21+"])
    out["images_per_patient"] = pd.DataFrame(
        {"patients": bins.value_counts().sort_index(), "images": n_img.groupby(bins, observed=False).sum()}
    ).rename_axis("images_per_patient")
    numbers["patients"] = int(n_img.size)
    numbers["max_images_per_patient"] = int(n_img.max())
    lab = images[images["has_final_label"]]
    t = lab.groupby("nih_patient_id")["target"].agg(["min", "max"])
    numbers["patients_with_both_positive_and_negative_images"] = int(((t["min"] == 0) & (t["max"] == 1)).sum())
    pm = images.groupby("nih_patient_id")["multi_read"].agg(["any", "all"])
    mixed = pm[pm["any"] & ~pm["all"]].index
    numbers["patients_in_both_multi_and_single_read"] = int(len(mixed))
    numbers["multi_read_images_whose_patient_has_single_read_images"] = int(
        images[images["multi_read"] & images["nih_patient_id"].isin(mixed)].shape[0]
    )
    if "kaggle_stage1_train" in images:
        ps = images.groupby("nih_patient_id")["kaggle_stage1_train"].agg(["any", "all"])
        numbers["patients_in_both_stage1_train_and_rest"] = int((ps["any"] & ~ps["all"]).sum())
    return out, numbers


def integrity(images: pd.DataFrame, manifest: dict) -> tuple[pd.DataFrame, dict]:
    files = pd.DataFrame(
        [
            {
                "file": k,
                "size": v.get("size"),
                "sha256": (v.get("sha256") or "")[:16] + "…" if v.get("sha256") else "",
                "downloaded_at": v.get("downloaded_at", ""),
                "zip_entries": v.get("zip_entries", ""),
            }
            for k, v in manifest.items()
        ]
    )
    n = {
        "mapping_images": int(len(images)),
        "unique_image_id": int(images["image_id"].nunique()),
        "images_with_final_label": int(images["has_final_label"].sum()),
        "images_without_final_label": int((~images["has_final_label"]).sum()),
    }
    if "dicom_found" in images:
        n["dicom_found"] = int(images["dicom_found"].sum())
        n["dicom_uids_match"] = int(images["dicom_uids_match"].sum())
    return files, n


# ---------------------------------------------------------------- report
def build_report(tables: dict[str, pd.DataFrame], manifest: dict, out_dir: Path, title_date: Optional[str] = None) -> Path:
    out_dir = Path(out_dir)
    (out_dir / "tables").mkdir(parents=True, exist_ok=True)
    images, boxes = tables["images"], tables["boxes"]
    reads, reader_boxes = tables["reader_reads"], tables["reader_boxes"]
    has_dicom = "view" in images.columns

    files, checks = integrity(images, manifest)
    numbers: dict = {}
    sections: list[tuple[str, dict[str, pd.DataFrame]]] = []
    sections.append(("2. ラベル", label_tables(images)))
    if has_dicom:
        sections.append(("3. 撮影条件と画像形式（DICOM ヘッダ）", metadata_tables(images)))
    sections.append(("4. BBox（最終ラベル）", box_tables(images, boxes)))
    rt, rn = reader_tables(images, reads, reader_boxes)
    sections.append(("5. 読影者", rt))
    pt, pn = patient_tables(images)
    sections.append(("6. 患者（NIH の患者 ID）", pt))
    numbers.update(rn)
    numbers.update(pn)

    lab = images[images["has_final_label"]]
    numbers["positive_images"] = int((lab["target"] == 1).sum())
    numbers["positive_rate"] = round(float(lab["target"].mean()), 4)
    numbers["final_boxes"] = int(len(boxes))
    numbers["multi_read_images"] = int(images["multi_read"].sum())
    numbers["adjudicated_images"] = int(images["adjudicated"].sum())
    if has_dicom:
        pos = lab[lab["target"] == 1]
        numbers["ap_share_all"] = round(float((lab["view"] == "AP").mean()), 4)
        numbers["ap_share_positive"] = round(float((pos["view"] == "AP").mean()), 4)
        numbers["auc_view_only"] = round(auc(lab["view"].eq("AP").astype(int), lab["target"]), 3)
        numbers["age_over_100"] = int((images["age"] > 100).sum())
        numbers["age_max"] = int(images["age"].max())

    date = title_date or _dt.date.today().isoformat()
    md = [
        "# データ確認レポート（RSNA Pneumonia Detection Challenge 2018）",
        "",
        f"- 作成日：{date}",
        "- 作成方法：`scripts/inspect_dataset.py`（`src/gradresearch/analysis/dataset_report.py`）",
        "- 最終ラベル：`Calculated` グループ。3人読影（multi_read）：Team 2 と Team 2a の両方が読影した画像",
        "- 割合・陽性率は、最終ラベルのある画像（29,684 枚）で計算しています。",
        "",
        "## 1. ファイルと対応関係",
        "",
        md_table(files, index=False),
        "",
        md_table(pd.DataFrame({"value": checks}).rename_axis("check")),
        "",
        "## 主な数値",
        "",
        md_table(pd.DataFrame({"value": numbers, "説明": {k: NUMBER_NOTES.get(k, "") for k in numbers}}).rename_axis("key")),
        "",
    ]
    for title, tbls in sections:
        md += [f"## {title}", ""]
        for name, df in tbls.items():
            md += [f"### {name}", ""]
            if name in CAPTIONS:
                md += [CAPTIONS[name], ""]
            md += [md_table(df), ""]
            df.to_csv(out_dir / "tables" / f"{name}.csv")
    (out_dir / "summary.json").write_text(json.dumps({**checks, **numbers}, indent=2, ensure_ascii=False), encoding="utf-8")
    report = out_dir / "report.md"
    report.write_text("\n".join(md), encoding="utf-8")
    return report
