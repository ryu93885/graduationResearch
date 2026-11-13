# RSNA Pneumonia Detection Challenge 2018 データセットの特徴

- **作成日**：2026-11-12
- **更新日**：2026-11-12（公式配布ファイルを取得し、実データで確認した結果を反映。確認の詳細は [`inspection_report_2026-11-12.md`](inspection_report_2026-11-12.md)）
- **目的**：卒業研究で使うデータセットの基礎情報を、出典つきでまとめた資料です。プログラムの仕様や報告書の記述の根拠に使います。
- **確認に使った資料**：RSNA 公式配布ページ、Dataset Description（V1 02/07/2022）、Terms of Use and Attribution、公式配布ファイル（いずれも 2026-11-12 に確認）
- **注意**：Shih et al. (2019) の全文は未確認です（Q-06 で保留中）。論文の内容は、検索結果に表示された本文の抜粋に基づいています。

**出典の区分**

| 区分 | 意味 |
|---|---|
| 実データ | 公式配布ファイルを取得して、プログラムで確認した（`scripts/inspect_dataset.py`） |
| 公式 | RSNA 公式ページ・Dataset Description・Terms で確認した |
| 論文抜粋 | 検索結果に表示された Shih et al. (2019) 本文の抜粋による（全文で要確認） |
| 二次 | その他の論文・Kaggle の情報による |
| 一般知識 | 胸部 X 線についての一般的な医学知識 |
| 未確認 | データを取得してから確かめる |

---

## 1. 概要

| 項目 | 内容 | 出典 |
|---|---|---|
| 名称 | RSNA Pneumonia Detection Challenge (2018) | 公式 |
| 作成 | RSNA が STR（Society of Thoracic Radiology）と MD.ai と協力して作成 | 公式 |
| 元データ | NIH の胸部 X 線データセット（CXR8 / ChestX-ray14） | 公式 |
| 画像 | 胸部 X 線の正面像 30,000 枚 | 公式 |
| アノテーション | 画像単位のラベルと、肺炎を疑う陰影の BBox（2D ROI） | 公式 |
| コンペ | Kaggle で開催。1,400 チーム以上が参加。課題は肺炎を疑う陰影の検出と位置の特定 | 公式 |
| コンペの評価指標 | IoU のしきい値 0.4〜0.75 での mean Average Precision | 二次 |

## 2. データの成り立ち

1. **NIH ChestX-ray14**：112,120 枚・30,805 人の正面像です。疾患ラベルは読影レポートから自然言語処理で自動抽出したもので、誤りを含みます。（二次）
2. **画像の選定**：NIH の画像から 30,000 枚を選びました。（公式）内訳は、NIH ラベルで肺炎・浸潤・コンソリデーションが陽性の画像が 15,000 枚、No Finding が 7,500 枚、その他の所見が 7,500 枚です。（実データ：対応表の `subset_init_label`）
   - 再読影の結果、NIH で肺炎関連とされた 15,000 枚のうち Lung Opacity になったのは 5,113 枚（34%）でした。NIH で No Finding の 7,500 枚からも 668 枚が Lung Opacity になっています。（実データ）
   - → **肺炎が疑われる例を意図的に多く集めたデータ**です。陽性率は臨床の実態とは違います（R-18）。
3. **再読影**：放射線科医が MD.ai 上で、手作業でラベルと BBox を付け直しました。（公式）
4. **Kaggle のコンペ（2018年）**：stage 1 と stage 2 の2段階で出題されました。（二次）
5. **RSNA 公式配布**：画像・アノテーション・NIH との対応表を配布しています。（公式）

## 3. 前提知識

### 3.1 撮影方向（PA と AP）（一般知識）

| | PA（後前方向） | AP（前後方向） |
|---|---|---|
| X 線の向き | 背中から入り、胸側の検出器へ | 胸側から入り、背中側の検出器へ |
| 撮り方 | 立った状態で、放射線科で撮影 | ポータブル装置で、ベッド上（寝た姿勢や座った姿勢）で撮影 |
| 患者 | 歩ける人が多い | 入院中・重症の人が多い |
| 画像の特徴 | 心臓がほぼ実際の大きさに写る | 心臓が大きく写る。肩甲骨が肺に重なりやすい |

AP であること自体が「重症らしさ」と結びつくので、モデルのショートカットの候補になります（R-06）。

### 3.2 陰影（opacity）

- X 線を通しにくく、周りより白く写る部分です。（一般知識）
- 肺炎は浸潤影（コンソリデーション）やすりガラス影として写ります。ただし、無気肺・胸水・肺水腫・腫瘤なども白く写ります。（一般知識）
- このデータセットでは、Fleischner Society の定義に基づき「周りより不透明な領域で、**咳と発熱のある患者なら**肺炎の可能性が低〜高のもの」を BBox の対象にしています。（論文抜粋）
- 読影医は臨床情報なしで画像だけを見て判断しているので、**ラベルは診断ではなく、画像所見の分類**です。

## 4. 画像

| 項目 | 内容 | 出典 |
|---|---|---|
| 枚数 | 30,000 枚（PA 16,248 枚 / AP 13,752 枚。AP は約 46%） | 公式・実データ |
| 形式 | NIH の PNG 画像を DICOM に変換したもの | 公式 |
| 追加された DICOM タグ | 性別・年齢・撮影方向（AP / PA） | 公式 |
| サイズ | 1024×1024 ピクセル（30,000 枚すべて） | 実データ |
| ビット深度・色 | 8 ビット、MONOCHROME2（0 = 黒） | 実データ |
| 画素の圧縮 | **JPEG Baseline（非可逆圧縮）**。読み込みには Pillow などの JPEG デコーダが必要 | 実データ |
| PixelSpacing（1画素の実寸） | 画像によって違う（主に 0.139 / 0.143 / 0.168 / 0.171 / 0.194 mm）。撮影機器の違いを反映している可能性がある | 実データ |
| 年齢 | 文字列（例：`46`）。100 を超える値が 6 枚あり、最大は 412（入力ミスと考えられる） | 実データ |
| 施設 | NIH Clinical Center の1施設 | 公式（Terms の帰属表示から） |
| 画像に写り込んだ個人情報 | Dataset Description では「No / Removed」 | 公式 |
| 画像に写り込んだ文字マーカー | 一部の画像で確認（目視）。どのくらいの割合かは未確認 | 実データ |

**撮影方向と陽性率（実データ）**

| 撮影方向 | 陽性率 | 陽性画像に占める割合 |
|---|---|---|
| AP | 40.5% | 77.3% |
| PA | 10.0% | 22.7% |

撮影方向だけで陽性を予測しても ROC-AUC は 0.708 になります。PA の中でも、PixelSpacing によって陽性率が 8.2%〜14.3% と違います（1,000 枚以上ある組み合わせで比較）。

**本研究への影響**
- DICOM から使えるメタデータは、性別・年齢・撮影方向に加えて PixelSpacing です。機器や施設の名前はありません（R-19）。
- 撮影方向は強いショートカットになりえます（R-06）。
- 施設が1つなので、施設差による交絡はありません。その代わり、他の施設でも同じ結果になるかはわかりません。

## 5. ラベル

### 5.1 元のラベルと配布用のクラス

| 読影医が付けた元のラベル（論文抜粋） | 配布用のクラス | Target |
|---|---|---|
| Opacity（High / Medium / Low Probability） | Lung Opacity（BBox あり） | 1 |
| No Opacity / Not Normal | No Lung Opacity / Not Normal | 0 |
| Normal | Normal | 0 |

- 胸部専門医に確認を回すための「Question」フラグもありました。（論文抜粋）
- **Lung Opacity** には「低確率」の陰影も含まれます（R-17）。高確率と中確率の判断は、読影医によってばらつきがありました。（論文抜粋）
- **No Lung Opacity / Not Normal** は「肺に陰影があっても、肺炎を疑う陰影ではないもの」です。陰影がないという意味ではありません。（論文抜粋）

### 5.2 件数

**公式配布の最終ラベル（`Calculated` グループ、実データ）**

| クラス | 枚数 | 備考 |
|---|---|---|
| Lung Opacity | 7,106 枚 | BBox は計 11,390 個。陽性率 23.9% |
| No Lung Opacity / Not Normal | 12,788 枚 | |
| Normal | 9,790 枚 | |
| 合計 | 29,684 枚 | Kaggle 版の train + test（26,684 + 3,000）と同じ数 |
| 最終ラベルなし | 316 枚 | 除外された画像と考えられる（R-23） |

**参考：Kaggle 版 stage 2 train（二次）**：Lung Opacity 6,012 枚（BBox 9,555 個）、Not Normal 11,821 枚、Normal 8,851 枚、合計 26,684 枚。

### 5.3 読影者の確率ラベル（実データ）

読影者が描いた BBox の確率の内訳です。1人読影（Team 1）では「中」が大半で、「低」も約 22% あります（R-17）。

| グループ | 高 | 中 | 低 |
|---|---|---|---|
| Team 1（1人読影） | 1,437 | 8,837 | 2,891 |
| Team 2 | 856 | 1,721 | 957 |
| Team 2a | 669 | 1,334 | 913 |

**確率ラベルと最終ラベルの関係（1人読影の画像、実データ、2026-11-12 に集計）**

| 読影者が描いた BBox の最高確率 | 最終 Lung Opacity | 最終 Not Normal | 最終 Normal | 最終ラベルなし |
|---|---|---|---|---|
| 高 | 844 | 8 | 1 | 25 |
| 中 | 4,492 | 19 | 0 | 143 |
| 低 | 23 | **1,620** | 2 | 44 |

低確率の BBox しか描かれなかった画像は、ほぼすべて最終ラベルが **Not Normal** になっています。つまり、最終ラベルの Lung Opacity は実質「中・高確率」の陰影です。低確率の陰影がある画像は陰性側（Not Normal）に入っています。公式資料には書かれておらず、データから推定したことです。

## 6. BBox（バウンディングボックス）

| 項目 | 内容 | 出典 |
|---|---|---|
| 描き方 | 疑わしい陰影全体を含む、できるだけ小さい矩形。離れた陰影には複数の BBox を描く | 論文抜粋 |
| 形式（Kaggle 版） | 1024×1024 画像上の左上の座標 `x, y` と幅・高さ `width, height`（ピクセル単位） | 二次 |
| 形式（公式配布） | MD.ai の JSON。各アノテーションの `data` に `{x, y, width, height}`（小数を含む）。`x, y` が左上であることを、画像に重ねて目視で確認した | 実データ |
| 1枚あたりの数 | 1個：3,030 枚、2個：3,892 枚、3個：160 枚、4個：24 枚 | 実データ |
| 3人で読んだ画像 | 読影者の BBox の**交差（重なった部分）**を採用。そのため BBox は小さめになる（論文抜粋）。実際に、面積の中央値は3人読影で画像の 3.8%、1人読影で 6.5% だった（実データ） | 論文抜粋・実データ |
| 位置 | 画像の左半分（患者の右肺側）に 6,025 個、右半分に 5,365 個。画像の外にはみ出した BBox はない | 実データ |
| 陰性画像 | BBox なし（R-01 の BBox 移植が必要な理由） | 実データ |

BBox は病変の輪郭そのものではなく、陰影を囲む矩形です。中に正常な組織が入ることも、陰影が外にはみ出すこともあります。

## 7. アノテーションの手順と品質

| 項目 | 内容 | 出典 |
|---|---|---|
| 読影者 | 18 人・16 施設。うち 12 人は STR の胸部放射線科医。平均経験 10.6 年（3〜35 年） | 公式 |
| 事前の練習 | 全員が同じ 50 枚で練習した（ほかの読影者の結果は見ない） | 論文抜粋 |
| 1人で読んだ画像 | RSNA の読影者 6 人が 5,000 枚ずつ担当した | 論文抜粋 |
| 3人で読んだ画像 | 4,527 枚（STR 2 人＋RSNA 1 人）。意見が分かれた画像は、経験 10 年以上の胸部専門医 2 人のどちらかが調整した | 公式（枚数）・論文抜粋・二次（調整） |
| 訓練用と評価用の違い | 訓練画像は胸部専門ではない RSNA の読影者、評価画像は STR の胸部専門医パネルがラベル付けした | 論文抜粋 |
| Kaggle での分け方 | 3人で読んだ画像のうち 3,000 枚が test、約 1,500 枚が train に入った | 二次 |
| 公式配布での読影グループ | `Team 1`（1人読影。6人が約 5,000 枚ずつ）、`Team 2` と `Team 2a`（追加の読影者）、`Adjudication`（調整）、`Calculated`（最終ラベル） | 実データ |
| 3人読影の枚数 | Team 2 と Team 2a の両方が読影した画像は 4,526 枚（RSNA の説明の 4,527 枚とほぼ一致） | 実データ |
| 調整の記録がある画像 | 1,380 枚 | 実データ |
| 3人の一致度 | Fleiss の κ = 0.50（陽性かどうか）。3人の判定が全員一致したのは 64.5% | 実データ |
| 多数決との関係 | 3人読影で陽性と読んだのが1人だけでも最終ラベルが陽性の画像が 158 枚、2人以上が陽性と読んでも最終ラベルが陰性の画像が 241 枚ある | 実データ |

**本研究への影響**
- 訓練用と評価用で、ラベルの作り方そのものが違います。BBox の大きさも品質も違うので、1人で読んだか3人で読んだかを記録し、分けて評価します（R-16）。
- 1人で読んだ画像では、BBox を付け忘れた陰影が残っている可能性があります（R-07）。

## 8. 配布形態

### 8.1 RSNA 公式配布（2026-11-12 時点）

配布ページ：https://www.rsna.org/education/ai-resources-and-training/ai-image-challenge/RSNA-Pneumonia-Detection-Challenge-2018

中身は実際にファイルを取得して確認しました（2026-11-12、実データ）。

| 配布ページでの名称 | ファイル名・容量 | 中身 | 本研究での使い方 |
|---|---|---|---|
| Download images ... used in initial annotation | `pneumonia-challenge-dataset-original_2018.zip`（3.41 GB） | Kaggle stage 1 train の画像 25,684 枚（下の 30,000 枚に含まれる） | 使わない |
| Download initial annotations | `pneumonia-challenge-annotations-original_2018.json`（19.6 MB） | Kaggle stage 1 train のラベル（25,684 枚、陽性 5,659 枚）。2値のラベルだけで、読影者の情報はない | Kaggle stage 1 train に含まれていたかの印付けだけに使う |
| Download images ... used in the Pneumonia Challenge | `pneumonia-challenge-dataset-adjudicated-kaggle_2018.zip`（3.98 GB） | 30,000 枚の DICOM | **すべての解析**の画像 |
| Download annotations used in the Pneumonia Challenge | `pneumonia-challenge-annotations-adjudicated-kaggle_2018.json`（52.0 MB） | 30,000 枚分。**全読影者のラベル（確率つき）、調整の記録、最終ラベル（`Calculated`）がすべて入っている** | **主解析**には最終ラベル、**読影者ごとの分析・確率の分析**には Team 1 / 2 / 2a のラベルを使う |
| Download mapping of RSNA image dataset to original NIH dataset | `pneumonia-challenge-dataset-mappings_2018.json`（17.6 MB） | 30,000 枚の RSNA 画像 ID・DICOM の UID・NIH のファイル名・NIH ラベル・選定グループ | 患者単位の分割（R-03）と、選定グループの分析に使う |

- ファイルは `https://s3.amazonaws.com/east1.public.rsna.org/AI/2018/` 以下で配布されています。
- 当初は「initial annotations」に読影者ごとの情報が入っていると考えていました（Q-05）。実際には、読影者ごとの情報も「annotations used in the Pneumonia Challenge」のほうに入っていました（R-15 の修正）。
- 取得には `scripts/download_data.py` を使います。サイズと SHA-256 を照合します。

### 8.2 Kaggle 版（参考）

本研究では公式配布を使います。Kaggle 版は先行研究と比べるときの参考にします。（いずれも二次）

| 段階 | train | test |
|---|---|---|
| stage 1 | 25,684 枚 | 1,000 枚 |
| stage 2 | 26,684 枚（stage 1 の train と test を合わせたもの） | 3,000 枚 |

- 主なファイルは次のとおりです。
  - `stage_2_train_labels.csv`（`patientId, x, y, width, height, Target`）
  - `stage_2_detailed_class_info.csv`（`patientId, class`）
  - DICOM 画像
- `patientId` の種類数は画像の枚数と同じです。つまり **`patientId` は実質的に画像ごとの ID** です（実データ：対応表の `subset_img_id` と DICOM の PatientID が一致し、30,000 枚すべて異なる）。患者単位で分割するには、NIH の対応表が必要です（R-03）。
- Kaggle 版の合計 29,684 枚は、公式配布で最終ラベルのある画像の数と一致します。30,000 枚との差の 316 枚は、最終ラベルのない画像です（実データ）。
- **Kaggle の分割は患者単位ではありません**。stage 1 train とそれ以外の両方に画像がある患者が 2,009 人います（実データ）。

## 9. 利用条件と帰属表示（公式）

- 学術研究・教育、商用・非商用の目的で利用できます。
  - ただし Dataset Description には「Non-commercial purpose」とあり、記載が食い違っています（R-20）。学術利用はどちらでも問題ありません。
- データに写っている個人を特定しようとしたり、連絡を取ろうとしたりしてはいけません。
- データを共有・再配布するときは、次の帰属表示が必要です。
  - **NIH データについて**
    - ダウンロードサイトへのリンク：https://nihcc.app.box.com/v/ChestXray-NIHCC
    - 論文の引用：Xiaosong Wang, Yifan Peng, Le Lu, Zhiyong Lu, Mohammadhadi Bagheri, Ronald Summers. ChestX-ray8: Hospital-scale Chest X-ray Database and Benchmarks on Weakly-Supervised Classification and Localization of Common Thorax Diseases. IEEE CVPR, pp. 3462-3471, 2017.
    - NIH Clinical Center がデータ提供者であることの明記
  - **RSNA-STR のデータとアノテーションについて**
    - 配布ページへのリンク：https://www.rsna.org/education/ai-resources-and-training/ai-image-challenge/RSNA-Pneumonia-Detection-Challenge-2018
    - 論文の引用：George Shih, Carol C. Wu, Safwan S. Halabi, Marc D. Kohli, Luciano M. Prevedello, Tessa S. Cook, Arjun Sharma, Judith K. Amorosa, Veronica Arteaga, Maya Galperin-Aizenberg, Ritu R. Gill, Myrna C.B. Godoy, Stephen Hobbs, Jean Jeudy, Archana Laroia, Palmi N. Shah, Dharshan Vummidi, Kavitha Yaddanapudi, Anouk Stein. Augmenting the National Institutes of Health Chest Radiograph Dataset with Expert Annotations of Possible Pneumonia. Radiology: Artificial Intelligence, 2019. https://doi.org/10.1148/ryai.2019180041

## 10. 本研究で特に注意する点

詳しくは `docs/revision_report.md` の各番号を参照してください。

| 特徴 | 注意点 | 関連 |
|---|---|---|
| 陰性画像には BBox がない | Model A/C で「マスクの有無」が正解の手がかりになる | R-01 |
| ラベルは3クラス | Not Normal には肺炎以外の陰影がありうる | R-02 |
| `patientId` は画像ごとの ID | 患者単位の分割には NIH の対応表が必要 | R-03 |
| 同じ患者の画像が複数ある（最大 75 枚）。Kaggle の分割は患者単位ではない | 患者単位で自分たちで分割し直す必要がある | R-03 |
| 元データは NIH ChestX-ray14 | NIH で学習した事前学習重みはリークになりうる | R-04 |
| AP は重症患者に多い（陽性の 77% が AP） | 撮影方向によるショートカット。撮影方向だけで AUC 0.71 | R-06 |
| PixelSpacing が画像によって違う | 撮影機器の違いによるショートカットの可能性 | R-19 |
| 年齢に外れ値がある（最大 412） | 前処理で欠損として扱う | R-22 |
| ほとんどの画像は1人で読影 | BBox の付け忘れ・ラベルのばらつき | R-07, R-17 |
| 3人読影の BBox は交差で小さい | 陰影が BBox の外にはみ出しやすい。読影の種類で分けて評価する | R-09, R-16 |
| 肺炎疑い例を多く集めた選び方 | 陽性率・Precision を臨床にそのまま一般化できない | R-18 |
| メタデータは3項目だけ | 画像に写り込んだ文字マーカーは目視で確認する | R-19 |

## 11. データ取得後に確認すること

2026-11-12 に確認しました。詳しい数値は [`inspection_report_2026-11-12.md`](inspection_report_2026-11-12.md) にあります。

- [x] 公式配布の JSON の構造：MD.ai の形式。読影者 ID、確率のラベル、読影グループ（3人読影の判定に使える）、最終ラベルがある（8.1 節）
- [x] 総枚数とクラスごとの件数：30,000 枚のうち最終ラベルのある画像は 29,684 枚（5.2 節）
- [x] 陽性・陰性それぞれの AP / PA の比率：陽性の 77.3% が AP（4 節）
- [x] 1枚あたりの BBox の数と大きさ：3人読影の BBox のほうが小さい（6 節）
- [x] NIH の患者 ID：**12,274 人**（報告書 2.1 の値と一致、R-21）。1 人で最大 75 枚。画像が 1 枚だけの患者は 7,464 人
- [x] 画像のサイズとビット深度：1024×1024、8 ビット、JPEG Baseline（4 節）
- [x] 年齢の外れ値：100 を超える値が 6 枚（最大 412）
- [ ] 画像に写り込んだ文字マーカー：一部の画像で目視で確認した。割合は未確認

## 12. 出典

- RSNA. RSNA Pneumonia Detection Challenge (2018). https://www.rsna.org/education/ai-resources-and-training/ai-image-challenge/RSNA-Pneumonia-Detection-Challenge-2018
- RSNA. 2018 RSNA Pneumonia Detection Challenge Dataset Description, V1 02/07/2022.（上記ページの「Dataset description」）
- RSNA. Pneumonia Detection Challenge Terms of Use and Attribution.（上記ページの「Terms of use and acknowledgments」）
- Shih G, et al. Augmenting the National Institutes of Health Chest Radiograph Dataset with Expert Annotations of Possible Pneumonia. *Radiology: Artificial Intelligence*, 2019. https://doi.org/10.1148/ryai.2019180041（全文は未確認。検索結果の抜粋のみ）
- Wang X, et al. ChestX-ray8: Hospital-scale Chest X-ray Database and Benchmarks on Weakly-Supervised Classification and Localization of Common Thorax Diseases. *IEEE CVPR*, pp. 3462-3471, 2017.
- Gabruseva T, et al. Deep Learning for Automatic Pneumonia Detection. *CVPR Workshops*, 2020.（Kaggle 版の件数）
- Pneumonia Detection in Chest Radiographs. arXiv:1811.08939.（画像の選び方の内訳）
- Kaggle. RSNA Pneumonia Detection Challenge, Discussion 64723. https://www.kaggle.com/c/rsna-pneumonia-detection-challenge/discussion/64723（3人読影の分け方と調整の手順）
