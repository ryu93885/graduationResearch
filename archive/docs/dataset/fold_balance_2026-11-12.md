# 交差検証の分割の確認（患者単位）

- 作成日：2026-11-12
- 作成方法：`scripts/make_splits.py`（`src/gradresearch/data/splits.py`）
- 分割数：5、シード：42、指紋（fingerprint）：`5f2c2423bfaa75b3`
- 同じ患者の画像はすべて同じ組に入ります。集計は解析対象（最終ラベルのある画像）だけです。
- 判定：許容範囲を超えた項目は **0 件**です。

## 各組の内訳

| fold | patients | images | positives | positive_rate | Lung Opacity | No Lung Opacity / Not Normal | Normal | AP_share | multi_difficult | multi_unanimous | single_low_prob | single_other | final_negative_with_positive_read | final_positive_with_negative_read |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 2,447 | 5,937 | 1,421 | 0.239 | 1,421 | 2,558 | 1,958 | 0.457 | 327 | 576 | 339 | 4,695 | 173 | 154 |
| 1 | 2,447 | 5,938 | 1,422 | 0.239 | 1,422 | 2,556 | 1,960 | 0.457 | 328 | 576 | 339 | 4,695 | 173 | 155 |
| 2 | 2,447 | 5,937 | 1,421 | 0.239 | 1,421 | 2,560 | 1,956 | 0.456 | 328 | 575 | 338 | 4,696 | 173 | 155 |
| 3 | 2,446 | 5,936 | 1,421 | 0.239 | 1,421 | 2,557 | 1,958 | 0.457 | 327 | 574 | 338 | 4,697 | 172 | 155 |
| 4 | 2,446 | 5,936 | 1,421 | 0.239 | 1,421 | 2,557 | 1,958 | 0.456 | 326 | 575 | 337 | 4,698 | 171 | 155 |

## 偏りの判定

deviation は、組の平均からの最大のずれです（kind=rel は平均に対する割合、kind=abs は割合の差）。

| column | deviation | kind | tolerance | ok |
|---|---|---|---|---|
| patients | 0.000 | rel | 0.050 | OK |
| images | 0.000 | rel | 0.050 | OK |
| positives | 0.001 | rel | 0.100 | OK |
| positive_rate | 0.000 | abs | 0.010 | OK |
| Lung Opacity | 0.001 | rel | 0.100 | OK |
| No Lung Opacity / Not Normal | 0.001 | rel | 0.100 | OK |
| Normal | 0.001 | rel | 0.100 | OK |
| AP_share | 0.000 | abs | 0.010 | OK |
| multi_difficult | 0.004 | rel | 0.100 | OK |
| multi_unanimous | 0.002 | rel | 0.100 | OK |
| single_low_prob | 0.004 | rel | 0.100 | OK |
| single_other | 0.000 | rel | 0.100 | OK |
| final_negative_with_positive_read | 0.008 | rel | 0.100 | OK |
| final_positive_with_negative_read | 0.005 | rel | 0.100 | OK |

## 各回の役割（ローテーション）

| run | test | val | train |
|---|---|---|---|
| 0 | 0 | 1 | 2, 3, 4 |
| 1 | 1 | 2 | 0, 3, 4 |
| 2 | 2 | 3 | 0, 1, 4 |
| 3 | 3 | 4 | 0, 1, 2 |
| 4 | 4 | 0 | 1, 2, 3 |

## 画像が多い患者（上位 5 人）

| nih_patient_id | images |
|---|---|
| 10007 | 75 |
| 13670 | 75 |
| 12834 | 70 |
| 13993 | 57 |
| 17138 | 52 |
