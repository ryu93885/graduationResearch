# データ確認レポート（RSNA Pneumonia Detection Challenge 2018）

- 作成日：2026-11-12
- 作成方法：`scripts/inspect_dataset.py`（`src/gradresearch/analysis/dataset_report.py`）
- 最終ラベル：`Calculated` グループ。3人読影（multi_read）：Team 2 と Team 2a の両方が読影した画像
- 割合・陽性率は、最終ラベルのある画像（29,684 枚）で計算しています。

## 1. ファイルと対応関係

| file | size | sha256 | downloaded_at | zip_entries |
|---|---|---|---|---|
| pneumonia-challenge-annotations-adjudicated-kaggle_2018.json | 52,003,071 | f8f5c54bae158fc0… | 2026-11-12T03:04:16+00:00 |  |
| pneumonia-challenge-dataset-mappings_2018.json | 17,587,143 | 803ce79e3bc9c66d… | 2026-11-12T03:04:18+00:00 |  |
| pneumonia-challenge-annotations-original_2018.json | 19,556,559 | 5fbfa5a70c930346… | 2026-11-12T03:04:19+00:00 |  |
| pneumonia-challenge-dataset-adjudicated-kaggle_2018.zip | 3,978,753,654 | 96b97d81eb042c65… | 2026-11-12T03:07:15+00:00 | 30,000 |

| check | value |
|---|---|
| mapping_images | 30,000 |
| unique_image_id | 30,000 |
| images_with_final_label | 29,684 |
| images_without_final_label | 316 |
| dicom_found | 30,000 |
| dicom_uids_match | 30,000 |

## 主な数値

| key | value | 説明 |
|---|---|---|
| multi_read_images_with_3_reads | 4,497 | Team 1 / 2 / 2a の3人の判定がそろう3人読影の画像数 |
| fleiss_kappa_binary | 0.497 | 3人の一致度（陽性かどうか、Fleiss の κ） |
| fleiss_kappa_3class | 0.502 | 3人の一致度（3クラス、Fleiss の κ） |
| unanimous_binary_share | 0.645 | 3人の陽性・陰性の判定が全員一致した割合 |
| single_read_reader_equals_final | 0.935 | 1人読影の画像で、読影者の判定と最終ラベルが一致する割合 |
| patients | 12,274 | NIH の患者 ID の数 |
| max_images_per_patient | 75 | 1人あたりの最大画像枚数 |
| patients_with_both_positive_and_negative_images | 1,946 | 陽性と陰性の両方の画像を持つ患者数 |
| patients_in_both_multi_and_single_read | 2,104 | 3人読影と1人読影の両方に画像がある患者数 |
| multi_read_images_whose_patient_has_single_read_images | 3,273 | 3人読影の画像のうち、同じ患者の1人読影画像がある枚数 |
| patients_in_both_stage1_train_and_rest | 2,009 | Kaggle stage 1 train とそれ以外の両方に画像がある患者数 |
| positive_images | 7,106 | 最終ラベルが Lung Opacity の画像数 |
| positive_rate | 0.239 | 陽性率 |
| final_boxes | 11,390 | 最終ラベルの BBox の総数 |
| multi_read_images | 4,526 | 3人読影の画像数（RSNA の説明では 4,527） |
| adjudicated_images | 1,380 | 調整（Adjudication）の記録がある画像数 |
| ap_share_all | 0.457 | 全体に占める AP の割合 |
| ap_share_positive | 0.773 | 陽性画像に占める AP の割合 |
| auc_view_only | 0.708 | 撮影方向（AP=1）だけで陽性を予測したときの ROC-AUC |
| age_over_100 | 6 | 年齢が 100 を超える画像数 |
| age_max | 412 | 年齢の最大値 |

## 2. ラベル

### final_class

最終ラベル（3クラス）の件数。

| final_class | images | share |
|---|---|---|
| Lung Opacity | 7,106 | 0.239 |
| No Lung Opacity / Not Normal | 12,788 | 0.431 |
| Normal | 9,790 | 0.330 |

### selection_x_class

画像選定時の NIH ラベルによるグループ（行）と最終ラベル（列）。

| selection_group | (no final label) | Lung Opacity | No Lung Opacity / Not Normal | Normal | All |
|---|---|---|---|---|---|
| no_finding | 58 | 668 | 2,139 | 4,635 | 7,500 |
| other_finding | 85 | 1,325 | 4,640 | 1,450 | 7,500 |
| pneumonia_related | 173 | 5,113 | 6,009 | 3,705 | 15,000 |
| All | 316 | 7,106 | 12,788 | 9,790 | 30,000 |

### difficulty_x_class

評価用の層（行、`src/gradresearch/data/strata.py`）と最終ラベル（列）。multi_difficult は3人読影で意見が割れた、または全員一致の判定が最終ラベルで覆された画像。single_low_prob は低確率の BBox しか描かれなかった画像。

| difficulty_group | Lung Opacity | No Lung Opacity / Not Normal | Normal | All |
|---|---|---|---|---|
| multi_difficult | 774 | 772 | 90 | 1,636 |
| multi_unanimous | 865 | 662 | 1,349 | 2,876 |
| single_low_prob | 2 | 1,687 | 2 | 1,691 |
| single_other | 5,465 | 9,667 | 8,349 | 23,481 |
| All | 7,106 | 12,788 | 9,790 | 29,684 |

### difficult_direction

multi_difficult の内訳（最終ラベルが陰性で陽性と読んだ読影者がいる / 最終ラベルが陽性で陰性と読んだ読影者がいる）。

| difficult_direction | images |
|---|---|
| final_negative_with_positive_read | 862 |
| final_positive_with_negative_read | 774 |

### stage1_x_multiread

Kaggle stage 1 train に含まれるか（行）と、3人読影か（列）。

| kaggle_stage1_train | multi_read | single_read | All |
|---|---|---|---|
| not_stage1 | 3,928 | 388 | 4,316 |
| stage1_train | 598 | 25,086 | 25,684 |
| All | 4,526 | 25,474 | 30,000 |

## 3. 撮影条件と画像形式（DICOM ヘッダ）

### view_x_class

撮影方向（行）と最終ラベル（列）。positive_rate は Lung Opacity の割合。

| view | Lung Opacity | No Lung Opacity / Not Normal | Normal | positive_rate |
|---|---|---|---|---|
| AP | 5,492 | 6,268 | 1,795 | 0.405 |
| PA | 1,614 | 6,520 | 7,995 | 0.100 |

### sex_x_class

性別（行）と最終ラベル（列）。

| sex | Lung Opacity | No Lung Opacity / Not Normal | Normal | positive_rate |
|---|---|---|---|---|
| F | 2,948 | 5,562 | 4,294 | 0.230 |
| M | 4,158 | 7,226 | 5,496 | 0.246 |

### age_by_class

最終ラベルごとの年齢の分布。100 歳を超える値は入力ミスと考えられる。

| final_class | count | mean | std | min | 25% | 50% | 75% | max |
|---|---|---|---|---|---|---|---|---|
| Lung Opacity | 7,106 | 45.636 | 18.066 | 1 | 32 | 48 | 58 | 412 |
| No Lung Opacity / Not Normal | 12,788 | 49.368 | 16.450 | 1 | 38 | 52 | 61 | 153 |
| Normal | 9,790 | 44.995 | 16.379 | 2 | 33 | 46 | 57 | 155 |

### pixel_spacing_x_view

PixelSpacing（mm、小数3桁に丸めた値）と撮影方向の組み合わせごとの枚数と陽性率。撮影機器の違いを反映している可能性がある。

| pixel_spacing_mm | view | images | positive_rate |
|---|---|---|---|
| 0.143 | PA | 9,978 | 0.091 |
| 0.168 | AP | 7,430 | 0.408 |
| 0.139 | AP | 4,910 | 0.400 |
| 0.168 | PA | 2,399 | 0.134 |
| 0.194 | PA | 1,520 | 0.082 |
| 0.139 | PA | 1,208 | 0.092 |
| 0.171 | AP | 1,200 | 0.407 |
| 0.171 | PA | 1,021 | 0.143 |
| 0.115 | AP | 7 | 0.571 |
| 0.194 | AP | 4 | 0 |
| 0.115 | PA | 3 | 0 |
| 0.199 | AP | 3 | 0.667 |
| 0.143 | AP | 1 | 0 |

### image_format

画像形式に関する DICOM ヘッダの値（30,000 枚すべて）。

| field | values |
|---|---|
| rows | 1024 (30,000) |
| cols | 1024 (30,000) |
| bits_stored | 8 (30,000) |
| photometric | MONOCHROME2 (30,000) |
| transfer_syntax | JPEG Baseline (Process 1) (30,000) |
| modality | CR (30,000) |
| body_part | CHEST (30,000) |

## 4. BBox（最終ラベル）

### boxes_per_positive_image

陽性画像1枚あたりの BBox の数。

| n_boxes | images |
|---|---|
| 1 | 3,030 |
| 2 | 3,892 |
| 3 | 160 |
| 4 | 24 |

### box_size_by_read

BBox の幅・高さ（ピクセル）と画像に占める面積の割合。3人読影（交差）と1人読影で比較。

| measure | stat | multi_read | single_read |
|---|---|---|---|
| w | mean | 183.038 | 222.488 |
| h | mean | 255.101 | 337.325 |
| area_frac | mean | 0.048 | 0.077 |
| w | 50% | 178.445 | 220.961 |
| h | 50% | 224 | 308.024 |
| area_frac | 50% | 0.038 | 0.065 |
| w | min | 56 | 39.864 |
| h | min | 38 | 44.573 |
| area_frac | min | 0.003 | 0.002 |
| w | max | 415 | 528.072 |
| h | max | 785.920 | 942.493 |
| area_frac | max | 0.262 | 0.354 |

### box_center

BBox の中心座標（ピクセル）の分布。

| coordinate | count | mean | std | min | 10% | 50% | 90% | max |
|---|---|---|---|---|---|---|---|---|
| cx | 11,390 | 505.814 | 205.251 | 87.500 | 268.686 | 420.690 | 761.305 | 899.981 |
| cy | 11,390 | 534.914 | 115.607 | 129.722 | 386.950 | 535.077 | 681.839 | 944.676 |

### box_side

BBox の中心が画像の左右どちらにあるか（画像の左 = 患者の右肺側）。

| side | boxes |
|---|---|
| image left (patient's right) | 6,025 |
| image right (patient's left) | 5,365 |

### box_bounds

画像の外にはみ出した BBox の数。

| row | boxes | outside_image |
|---|---|---|
| 0 | 11,390 | 0 |

## 5. 読影者

### readers_per_image

1枚を何人の読影者（Team 1 / 2 / 2a）が読んだか。

| n_readers | images |
|---|---|
| 1 | 24,687 |
| 2 | 679 |
| 3 | 4,619 |
| 4 | 15 |

### reader_box_probability

読影者が描いた BBox の確率の内訳。

| group | high | medium | low |
|---|---|---|---|
| Team 1 | 1,437 | 8,837 | 2,891 |
| Team 2 | 856 | 1,721 | 957 |
| Team 2a | 669 | 1,334 | 913 |

### reader_workload

読影者ごとの担当枚数。

| group | reader_id | images |
|---|---|---|
| Team 1 | U_mve | 4,996 |
| Team 1 | U_1d2 | 4,990 |
| Team 1 | U_1n5 | 4,984 |
| Team 1 | U_1x0 | 4,984 |
| Team 1 | U_rk3 | 4,981 |
| Team 1 | U_mej | 4,958 |
| Team 1 | U_136 | 13 |
| Team 1 | U_rld | 7 |
| Team 1 | U_e8j | 2 |
| Team 2 | U_136 | 700 |
| Team 2 | U_rw0 | 500 |
| Team 2 | U_d92 | 499 |
| Team 2 | U_r6p | 499 |
| Team 2 | U_x90 | 499 |
| Team 2 | U_r43 | 498 |
| Team 2 | U_r9e | 498 |
| Team 2 | U_z66 | 498 |
| Team 2 | U_mj4 | 490 |
| Team 2 | U_yyj | 400 |
| Team 2 | U_r29 | 204 |
| Team 2a | U_yyj | 586 |
| Team 2a | U_r43 | 500 |
| Team 2a | U_r9e | 499 |
| Team 2a | U_rw0 | 499 |
| Team 2a | U_z66 | 498 |
| Team 2a | U_d92 | 496 |
| Team 2a | U_r6p | 492 |
| Team 2a | U_mj4 | 475 |
| Team 2a | U_x90 | 250 |
| Team 2a | U_rp8 | 248 |
| Team 2a | U_e8j | 19 |

### multi_read_positive_votes_x_final

3人読影の画像で、陽性（BBox あり）と読んだ読影者の数（行）と最終ラベル（列）。

| n_positive_reads | Lung Opacity | No Lung Opacity / Not Normal | Normal |
|---|---|---|---|
| 0 | 0 | 662 | 1,349 |
| 1 | 158 | 534 | 87 |
| 2 | 616 | 202 | 3 |
| 3 | 865 | 35 | 0 |
| 4 | 0 | 1 | 0 |

## 6. 患者（NIH の患者 ID）

### images_per_patient

NIH の患者 ID ごとの画像枚数の分布。

| images_per_patient | patients | images |
|---|---|---|
| 1 | 7,464 | 7,464 |
| 2 | 1,970 | 3,940 |
| 3-5 | 1,810 | 6,552 |
| 6-10 | 639 | 4,784 |
| 11-20 | 291 | 4,185 |
| 21+ | 100 | 3,075 |
