# RSNA Pneumonia Detection Challenge 2018 データセットの特徴

- **作成日**：2026-11-12
- **目的**：卒業研究で使うデータセットの基礎情報を、出典つきでまとめた資料です。プログラムの仕様や報告書の記述の根拠に使います。
- **確認に使った資料**：RSNA 公式配布ページ、Dataset Description（V1 02/07/2022）、Terms of Use and Attribution（いずれも 2026-11-12 に確認）
- **注意**：Shih et al. (2019) の全文は未確認です（Q-06 で保留中）。論文の内容は、検索結果に表示された本文の抜粋に基づいています。

**出典の区分**

| 区分 | 意味 |
|---|---|
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
2. **画像の選定**：NIH の画像から 30,000 枚を選びました。（公式）内訳は、NIH ラベルで肺炎・浸潤・コンソリデーションが陽性の画像が 15,000 枚、No Finding が 7,500 枚、その他の所見が 7,500 枚とされています。（二次）
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
| 枚数 | 30,000 枚（PA 16,248 枚 / AP 13,752 枚。AP は約 46%） | 公式 |
| 形式 | NIH の PNG 画像を DICOM に変換したもの | 公式 |
| 追加された DICOM タグ | 性別・年齢・撮影方向（AP / PA） | 公式 |
| サイズ | 1024×1024 ピクセル | 二次 |
| ビット深度 | 確かめる（元の PNG は 8 ビット相当とされる） | 未確認 |
| 施設 | NIH Clinical Center の1施設 | 公式（Terms の帰属表示から） |
| 画像に写り込んだ個人情報 | Dataset Description では「No / Removed」 | 公式 |
| 画像に写り込んだ文字マーカー（L/R、PORTABLE など） | あるかどうか確かめる | 未確認 |

**本研究への影響**
- 使えるメタデータは性別・年齢・撮影方向の3つだけで、機器や施設の情報はありません（R-19）。
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

### 5.2 件数（Kaggle 版 stage 2 train、二次）

| クラス | 枚数 | 備考 |
|---|---|---|
| Lung Opacity | 6,012 枚 | BBox は計 9,555 個。陽性率 約 22.5% |
| No Lung Opacity / Not Normal | 11,821 枚 | |
| Normal | 8,851 枚 | |
| 合計 | 26,684 枚 | |

6,012 枚は、CSV の行数（Lung Opacity 9,555 行、陰性は1枚1行）から計算した値です。公式配布版の件数はデータを取得して確かめます。

## 6. BBox（バウンディングボックス）

| 項目 | 内容 | 出典 |
|---|---|---|
| 描き方 | 疑わしい陰影全体を含む、できるだけ小さい矩形。離れた陰影には複数の BBox を描く | 論文抜粋 |
| 形式（Kaggle 版） | 1024×1024 画像上の左上の座標 `x, y` と幅・高さ `width, height`（ピクセル単位） | 二次 |
| 形式（公式配布） | JSON（MD.ai の形式と考えられる）。構造はデータを見て確かめる | 未確認 |
| 3人で読んだ画像 | 読影者の BBox の**交差（重なった部分）**を採用。そのため BBox は小さめになる | 論文抜粋 |
| 陰性画像 | BBox なし（R-01 の BBox 移植が必要な理由） | 二次 |

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

**本研究への影響**
- 訓練用と評価用で、ラベルの作り方そのものが違います。BBox の大きさも品質も違うので、1人で読んだか3人で読んだかを記録し、分けて評価します（R-16）。
- 1人で読んだ画像では、BBox を付け忘れた陰影が残っている可能性があります（R-07）。

## 8. 配布形態

### 8.1 RSNA 公式配布（2026-11-12 時点）

配布ページ：https://www.rsna.org/education/ai-resources-and-training/ai-image-challenge/RSNA-Pneumonia-Detection-Challenge-2018

| 配布ページでの名称 | ファイル名 | 本研究での使い方（Q-05 で決定） |
|---|---|---|
| Download images from NIH chest x-ray dataset used in initial annotation（3.3 GB） | `pneumonia-challenge-dataset-original_2018.zip` | 初期アノテーション用の画像 |
| Download initial annotations | `pneumonia-challenge-annotations-original_2018.json` | 読影者ごとの分析・確率ラベルの分析（中身を確認してから確定） |
| Download images from NIH chest x-ray dataset used in the Pneumonia Challenge | `pneumonia-challenge-dataset-adjudicated-kaggle_2018.zip` | **主解析**の画像 |
| Download annotations used in the Pneumonia Challenge | `pneumonia-challenge-annotations-adjudicated-kaggle_2018.json` | **主解析**のアノテーション（調整済み） |
| Download mapping of RSNA image dataset to original NIH dataset | `pneumonia-challenge-dataset-mappings_2018.json` | NIH の元画像との対応。患者単位の分割に使う（R-03） |

ファイルは `https://s3.amazonaws.com/east1.public.rsna.org/AI/2018/` 以下で配布されています。容量が書かれているのは 3.3 GB の1つだけです。

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
- `patientId` の種類数は画像の枚数と同じです。つまり **`patientId` は実質的に画像ごとの ID** です。患者単位で分割するには、NIH の対応表が必要です（R-03）。
- Kaggle 版の合計は 26,684 + 3,000 = 29,684 枚で、公式の 30,000 枚との差の理由は未確認です。

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
| 元データは NIH ChestX-ray14 | NIH で学習した事前学習重みはリークになりうる | R-04 |
| AP は重症患者に多い | 撮影方向によるショートカット | R-06 |
| ほとんどの画像は1人で読影 | BBox の付け忘れ・ラベルのばらつき | R-07, R-17 |
| 3人読影の BBox は交差で小さい | 陰影が BBox の外にはみ出しやすい。読影の種類で分けて評価する | R-09, R-16 |
| 肺炎疑い例を多く集めた選び方 | 陽性率・Precision を臨床にそのまま一般化できない | R-18 |
| メタデータは3項目だけ | 画像に写り込んだ文字マーカーは目視で確認する | R-19 |

## 11. データ取得後に確認すること

- [ ] 公式配布の JSON の構造（画像 ID、ラベル、BBox の表し方、読影者 ID、確率のラベル、3人で読んだかどうかの情報）
- [ ] 総枚数（30,000 枚）とクラスごとの件数。Kaggle 版の合計 29,684 枚との差の理由
- [ ] 陽性・陰性それぞれの AP / PA の比率
- [ ] 1枚あたりの BBox の数と大きさの分布。1人で読んだ画像と3人で読んだ画像での違い
- [ ] NIH 対応表で得られる患者 ID と、1人あたりの画像枚数（報告書 2.1 の「12,274 人」の確認、R-21）
- [ ] 画像のサイズとビット深度、DICOM タグの中身
- [ ] 年齢の外れ値の有無
- [ ] 画像に写り込んだ文字マーカー（L/R、PORTABLE など）の有無

## 12. 出典

- RSNA. RSNA Pneumonia Detection Challenge (2018). https://www.rsna.org/education/ai-resources-and-training/ai-image-challenge/RSNA-Pneumonia-Detection-Challenge-2018
- RSNA. 2018 RSNA Pneumonia Detection Challenge Dataset Description, V1 02/07/2022.（上記ページの「Dataset description」）
- RSNA. Pneumonia Detection Challenge Terms of Use and Attribution.（上記ページの「Terms of use and acknowledgments」）
- Shih G, et al. Augmenting the National Institutes of Health Chest Radiograph Dataset with Expert Annotations of Possible Pneumonia. *Radiology: Artificial Intelligence*, 2019. https://doi.org/10.1148/ryai.2019180041（全文は未確認。検索結果の抜粋のみ）
- Wang X, et al. ChestX-ray8: Hospital-scale Chest X-ray Database and Benchmarks on Weakly-Supervised Classification and Localization of Common Thorax Diseases. *IEEE CVPR*, pp. 3462-3471, 2017.
- Gabruseva T, et al. Deep Learning for Automatic Pneumonia Detection. *CVPR Workshops*, 2020.（Kaggle 版の件数）
- Pneumonia Detection in Chest Radiographs. arXiv:1811.08939.（画像の選び方の内訳）
- Kaggle. RSNA Pneumonia Detection Challenge, Discussion 64723. https://www.kaggle.com/c/rsna-pneumonia-detection-challenge/discussion/64723（3人読影の分け方と調整の手順）
