# 修正レポート（検討・相談の記録）

- **対象**：卒業研究 進捗報告書「Investigating Pneumonia Detection Using Features Outside Physician-Annotated Regions in Chest Radiographs」（2026-11-05 版）
  - 原本：[`docs/reports/2026-11-05_Graduation_Research_Progress_Report_RSNA_Pneumonia_EN.docx`](reports/2026-11-05_Graduation_Research_Progress_Report_RSNA_Pneumonia_EN.docx)
  - Markdown 版：[`docs/reports/2026-11-05_Graduation_Research_Progress_Report_RSNA_Pneumonia_EN.md`](reports/2026-11-05_Graduation_Research_Progress_Report_RSNA_Pneumonia_EN.md)
- **作成日**：2026-11-12

このファイルには、チャットで出た指摘・相談・決定事項を日付ごとに記録します。新しい内容は**末尾に追記**します。

## 記録のルール

- 各エントリは `## YYYY-MM-DD 見出し` で始めます。過去のエントリは書き換えず、状態が変わったときは新しいエントリに書きます。
- 指摘事項には通し番号 `R-xx`、ユーザーへの確認事項には `Q-xx` を付けます。後のエントリでは番号で参照します（例：「R-03：採用」）。
- 状態は次のいずれかです：`未決定`（提案のみ）／`採用`／`不採用`／`対応中`／`対応済`
- 「報告書の該当箇所」は、2026-11-05 版の章・節番号です。

---

## 2026-11-12 進捗報告書（2026-11-05 版）の検討

### 実施したこと

- 報告書の原本（.docx）と Markdown 変換版を `docs/reports/` に追加しました。
- `README.md` と `.gitignore`（データ・学習済み重み・実験出力を除外）を追加しました。
- 報告書の研究設計を検討し、指摘事項 R-01〜R-14 を整理しました。
- この修正レポートを作成しました。今後のチャットの内容は、このファイルの末尾に日付付きで追記していくことに決めました。

### 指摘事項一覧

| 番号 | 区分 | 指摘 | 報告書の該当箇所 | 優先度 | 状態 |
|---|---|---|---|---|---|
| R-01 | データ・設計 | 陰性画像には BBox がないため、Model A/C では「マスクの有無」が正解の手がかりになる | 3.2, 3.4 | 最重要 | 未決定 |
| R-02 | データ | 3クラスのラベル（Lung Opacity / Not Normal / Normal）を活用する | 2.2, 7.2 | 高 | 未決定 |
| R-03 | データ | RSNA の `patientId` は実質的に画像 ID。患者単位の分割には NIH のマッピングが必要 | 2.4, 3.3 | 高 | 未決定 |
| R-04 | データ | NIH ChestX-ray14 で学習した事前学習重みはテスト画像のリークになりうる | 3.3 | 高 | 未決定 |
| R-05 | 仮説 | H1 はほぼ確実に成立してしまう。内訳を調べる形（H1a/b/c）に分け、判定基準を事前に決める | 1.4, 4.4, 6.1 | 最重要 | 未決定 |
| R-06 | 仮説・評価 | 撮影条件（AP/PA など）によるショートカットを、メタデータのみのモデルと層別評価で確かめる | 4.1, 6.1 | 高 | 未決定 |
| R-07 | 仮説 | BBox を付け忘れた陰影が「領域外の情報」に見える可能性がある | 2.1, 6.1 | 中 | 未決定 |
| R-08 | 設計 | Model A/C を画像全体の大きさのまま「対になるマスク」でそろえ、ランダム領域マスク（C-rand）を対照に加える | 3.2 | 高 | 未決定 |
| R-09 | 設計 | マスク方法：ぼかしは陰影が残るので不適。平均値での塗りつぶしを基本にし、BBox 拡張率を変えて調べる | 3.4 | 高 | 未決定 |
| R-10 | 評価 | 「再学習した C」と「B のテスト時だけ BBox を隠す」の2種類で評価し、Grad-CAM との相関を見る | 4.3, 4.4 | 中 | 未決定 |
| R-11 | 評価 | XAI の評価指標を具体化する（Energy-based pointing game、肺野内外、健全性チェックなど） | 4.2, 4.3 | 中 | 未決定 |
| R-12 | 評価 | AUC の差は患者単位ブートストラップか DeLong 検定で評価し、シードは 3〜5 個使う | 4.1 | 中 | 未決定 |
| R-13 | 文献 | ショートカット学習・XAI 評価の関連文献を追加する | References | 低 | 未決定 |
| R-14 | 計画 | 締切に合わせて最小構成から実装する順番を決める | 7.1 | 中 | 未決定 |

### 指摘事項の詳細

#### R-01 陰性画像に BBox がない（マスクの有無によるリーク）

- **問題**：RSNA で BBox が付いているのは陽性画像だけです。
  - Model C では、マスクがある画像はすべて陽性になります。モデルは「マスクがあるかどうか」だけで正解できてしまいます。
  - Model A では、陰性画像のどこを切り出すのかが決まっていません。
- **対応案（BBox 移植）**：陰性画像ごとに、ランダムに選んだ陽性画像の BBox 一式（数・大きさ・位置）をそのまま当てはめます。AP 同士・PA 同士で組み合わせます。移植元の陽性画像は同じ分割（train / val / test）の中から選びます。
- **記述上の注意**：A/C は推論時にも正解 BBox を使います。臨床で使うモデルではなく「解析用の設定」であることを報告書に明記します。

#### R-02 3クラスのラベルを活用する

- **問題**：陰性群には、正常画像（Normal）と、肺炎以外の異常がある画像（No Lung Opacity / Not Normal）が混ざっています。
- **対応案**：主タスクは「Lung Opacity か それ以外か」の2値分類のままにします。そのうえで次の比較を追加します。
  - Lung Opacity vs Not Normal：どちらも異常画像なので「何となく病人らしい」という手がかりが使えません。肺炎に固有の領域外情報を調べる、いちばん厳しいテストになります。
  - Lung Opacity vs Normal

#### R-03 患者単位の分割

- **問題**：RSNA の `patientId` は、名前に反して実質的に画像ごとの ID だとされています。このまま分割すると、同じ患者の画像が train と test の両方に入るおそれがあります。
- **対応案**：NIH のマッピング情報で元のファイル名（例：`00000001_000.png`）を引き、先頭 8 桁を患者 ID として使って分割します。データ取得後に実際の構造を確認します。

#### R-04 事前学習重みによるリーク

- **問題**：NIH ChestX-ray14 で学習した重み（例：torchxrayvision の nih / all / rsna 系）は、RSNA のテスト画像を学習中に見ている可能性があります。
- **対応案**：ImageNet で事前学習した重みを使います。肺野セグメンテーションなどに外部モデルを使う場合も、学習データに NIH / RSNA が含まれていないものを選びます。

#### R-05 H1 の分解と判定基準の事前固定

- **問題**：Model C の AUC が 0.5 を大きく超えることはほぼ確実です。ただし、それが肺炎の情報によるものとは限りません。今の H1 のままでは「成立したが、何もわからない」結果になります。
- **対応案**：H1 を次のように分けます。
  - **H1a**：BBox をマスクしても分類に使える信号が残る
  - **H1b**：その信号は、メタデータのみのモデル（R-06）や AP/PA で分けた評価を上回る
  - **H1c**：その信号は肺野の中にある（肺野外ではない）
- それぞれの判定基準（例：「AP・PA の両方の層で C の AUC がメタデータモデルを有意に上回る」）を、実験を始める前に決めて記録します。

#### R-06 撮影条件によるショートカット

- **問題**：陽性画像は AP（ポータブル撮影）に大きく偏っていることが知られています。画像内のマーカー文字やチューブ類も手がかりになりえます。
- **対応案**：
  - 年齢・性別・View Position（AP/PA）だけを使うメタデータモデル（ロジスティック回帰）を作り、「画像を見なくても出せる性能」の基準にします。
  - AP・PA それぞれの中で AUC を評価します。

#### R-07 BBox を付け忘れた陰影

- **問題**：多くの症例は読影医 1 人で読まれています。BBox が付いていない陰影が残っていると、Grad-CAM が「領域外」に反応しても、実は付け忘れの陰影かもしれません。
- **対応案**：読影医 3 人で読まれた 4,527 例で別途評価します。領域外への反応が強い症例は、指導教員や専門医の意見を聞いて定性的に確認します。

#### R-08 Model A/C を対になるマスクでそろえる

- **問題**：Model A を切り出し画像にすると、拡大率が変わります。Grad-CAM も同じ座標で比べられなくなり、B・C との比較が不公平になります。
- **対応案**：どのモデルも画像全体の大きさのまま入力し、次のようにします。
  - A：BBox の中だけ残す（外を塗りつぶす）
  - C：BBox の中だけ塗りつぶす
  - C-rand（対照）：BBox と同じ面積のランダム領域を塗りつぶす。「マスクをすること自体」の影響を測ります。

#### R-09 マスク方法

- **問題**：肺炎の陰影は低周波の濃度上昇なので、ぼかしでは陰影の情報が残ってしまいます。また BBox は病変をぴったり囲んでいないため、陰影が BBox の外にはみ出していることがあります。
- **対応案**：
  - 平均値での塗りつぶしを基本にし、周囲からの補間（inpainting）は比較用にします。ぼかしは「リークの例」として示す程度にとどめます。
  - BBox を 0 / 10 / 25 / 50% 広げてマスクし、Model C の AUC がどう変わるかを曲線で示します。広げるほど AUC が下がるなら、残っていた信号ははみ出した陰影だった可能性が高くなります。

#### R-10 2種類の評価と Grad-CAM との対応

- **対応案**：
  - **再学習した C**：BBox 外の情報がそもそも存在するかを調べます（ROAR と同じ考え方）。
  - **B のテスト時だけ BBox を隠す**：B がその領域にどれだけ頼っているかを調べます。
  - 画像ごとに「B のスコアがどれだけ下がったか」と「Grad-CAM の値が BBox 内にどれだけ集まっているか」の相関をとります。これは RQ1 と RQ3 をつなぐ忠実性の指標になります。

#### R-11 XAI 評価の具体化

- **対応案**：
  - 領域との一致：Energy-based pointing game（BBox 内の CAM の割合）。BBox の面積で補正します。
  - 領域外の反応を「肺野内の BBox 外」と「肺野外」に分けます。肺野外への強い反応はショートカットの疑いが濃くなります（肺野セグメンテーションが必要）。
  - 健全性チェック：モデルの重みをランダムにしたとき、説明マップが変わるかを確認します。
  - Grad-CAM 以外の手法を 1 つ加え、結論が手法によらないかを確かめます。
  - 入力解像度は 512px 程度にします。224px では CAM が 7×7 の粗さにしかなりません。

#### R-12 統計的な評価

- **対応案**：同じテストセットでの AUC の差は、患者単位のブートストラップか DeLong 検定で評価します。乱数シードは 3〜5 個使い、平均と標準偏差を報告します。

#### R-13 追加すると説得力が増す文献

報告書に入れる前に、書誌情報は原典で確認します。

- Geirhos R, et al. "Shortcut learning in deep neural networks." *Nature Machine Intelligence*, 2020.
- DeGrave AJ, Janizek JD, Lee SI. "AI for radiographic COVID-19 detection selects shortcuts over signal." *Nature Machine Intelligence*, 2021.
- Zech JR, et al. "Variable generalization performance of a deep learning model to detect pneumonia in chest radiographs: A cross-sectional study." *PLOS Medicine*, 2018.
- Hooker S, et al. "A Benchmark for Interpretability Methods in Deep Neural Networks." *NeurIPS*, 2019.（ROAR）
- Adebayo J, et al. "Sanity Checks for Saliency Maps." *NeurIPS*, 2018.
- Petsiuk V, Das A, Saenko K. "RISE: Randomized Input Sampling for Explanation of Black-box Models." *BMVC*, 2018.（Deletion / Insertion）
- Wang H, et al. "Score-CAM: Score-Weighted Visual Explanations for Convolutional Neural Networks." *CVPR Workshops*, 2020.（Energy-based pointing game）
- Saporta A, et al. "Benchmarking saliency methods for chest X-ray interpretation." *Nature Machine Intelligence*, 2022.
- DeLong ER, DeLong DM, Clarke-Pearson DL. "Comparing the areas under two or more correlated receiver operating characteristic curves: a nonparametric approach." *Biometrics*, 1988.

#### R-14 実装の順番

- **対応案**：残り期間が短い場合は、次の最小構成を先に完成させます。
  1. B・C・C-rand・メタデータモデル・Grad-CAM（BBox 移植つき）
  2. そのあとに A、マスク方法の比較、BBox 拡張率のスイープ、Deletion / Insertion、複数シード

### 提案中の実験条件（R-01, R-06, R-08 のまとめ）

陰性画像には、すべての条件で R-01 の移植 BBox を使います。

| 条件 | 入力 | 目的 |
|---|---|---|
| B | 画像全体 | 基準 |
| A | BBox の中だけ残す（外を塗りつぶす） | 領域内の情報量 |
| C | BBox の中を塗りつぶす | 領域外の情報量（H1） |
| C-rand | BBox と同面積のランダム領域を塗りつぶす | マスク操作そのものの影響（対照） |
| Meta | 年齢・性別・AP/PA のみ（ロジスティック回帰） | 撮影条件だけで出せる性能の基準 |

### データ取得後に確認する値

以下は Kaggle 版（stage 2 train）で知られている値です。公式配布版でも同じかを確認します。

- 画像数：約 26,700 枚
- Lung Opacity：約 6,000 枚（陽性率 約 22.5%）、BBox 数：約 9,600 個
- No Lung Opacity / Not Normal：約 11,800 枚
- Normal：約 8,900 枚
- 陽性画像の AP/PA の偏り、年齢の外れ値の有無

### ユーザーへの確認事項（未回答）

| 番号 | 内容 | 決まると何が決まるか |
|---|---|---|
| Q-01 | 計算環境（Colab / 大学の GPU サーバ / 自宅の PC） | コードをノートブックで書くかスクリプトで書くか |
| Q-02 | 卒論の提出・発表の締切 | R-14 の実装の順番 |
| Q-03 | R-01, R-06, R-08 などの設計変更を採用するか、先に指導教員と相談するか | 実験条件の確定 |
| Q-04 | 報告書 7.1 のタスク 1（指導教員とのデータ利用の確認）が済んでいるか | データ取得を始めてよいか |

### 次のアクション（案）

1. Q-01〜Q-04 の回答を受けて方針を決める。
2. データ構造を確認するスクリプトを作る（ラベル件数、AP/PA とラベルのクロス集計、BBox の統計、患者マッピング）。データ取得は Q-04 の確認後に行う。
3. 採用した指摘を反映して、進捗報告書の改訂版を作る。

---

## 2026-11-12 データセット（RSNA Pneumonia Detection Challenge 2018）の基礎の確認

### 実施したこと

- データセットの基礎を一次資料で確認しました。読めたのは、RSNA 公式配布ページ、Dataset Description（V1 02/07/2022）、Terms of Use の3つです。
- Shih et al. (2019) の全文は、配布元の自動アクセス防止に止められて取得できませんでした。論文の内容は、検索結果に出た本文の抜粋（二次情報）で補っています。下の表の「出典」列で区別しています。
- このセッション用に個人用クラウド環境「graduationResearch」を作り、www.rsna.org と escholarship.org への接続を許可しました（escholarship.org は自動アクセス防止のため実際には読めませんでした）。

### 確認できた事実

出典の略号：**公式**＝RSNA 公式ページ／Dataset Description／Terms、**論文抜粋**＝検索結果に表示された Shih et al. 本文の抜粋、**二次**＝その他の論文・Kaggle の議論、**未確認**＝実データで確かめる必要があるもの

| 項目 | 内容 | 出典 |
|---|---|---|
| 元データ | NIH ChestX-ray（CXR8 / ChestX-ray14）。112,120 枚・30,805 人の正面像。疾患ラベルは読影レポートから自然言語処理で自動抽出したもの | 二次 |
| 枚数 | NIH から選んだ正面像 30,000 枚（PA 16,248 枚、AP 13,752 枚）。複数読影は 4,527 枚 | 公式 |
| 選び方 | NIH ラベルで肺炎・浸潤・コンソリデーション陽性 15,000 枚、No Finding 7,500 枚、その他の所見 7,500 枚 | 二次 |
| 画像形式 | PNG を DICOM に変換し、性別・年齢・撮影方向（AP/PA）のタグを追加。1024×1024 | 公式（サイズは二次） |
| 読影者 | 18 人・16 施設（うち STR の胸部放射線科医 12 人）、平均経験 10.6 年。MD.ai で手作業の BBox | 公式 |
| 読影の分担 | RSNA の読影者 6 人が 5,000 枚ずつ単独で読影。4,527 枚は 3 人（STR 2 人＋RSNA 1 人）が読影し、不一致は胸部専門医が調整 | 論文抜粋・二次 |
| 元のラベル | Opacity（高 / 中 / 低確率）、No Opacity / Not Normal、Normal の5種類。胸部専門医に回す「Question」フラグもあった | 論文抜粋 |
| 陰影の定義 | Fleischner Society の定義に基づき「周囲より不透明な領域」で、咳と発熱のある患者なら肺炎の可能性が低〜高のもの | 論文抜粋 |
| BBox の描き方 | 疑わしい陰影全体を含む最小の矩形。離れた陰影には複数の BBox | 論文抜粋 |
| 複数読影の BBox | 読影者の BBox の交差（重なり部分）を採用。そのため評価用データの BBox は小さめになる | 論文抜粋 |
| 訓練用と評価用の違い | 訓練画像は胸部専門ではない RSNA の読影者、評価画像は STR の胸部専門医のパネルがラベル付け | 論文抜粋 |
| Not Normal の意味 | 肺に陰影があっても、肺炎を疑う陰影ではないもの | 論文抜粋 |
| Kaggle 版の分割 | stage 1：train 25,684 / test 1,000。stage 2：train 26,684 / test 3,000。3人読影のうち約 1,500 枚が train、3,000 枚が test | 二次 |
| Kaggle 版 stage 2 train の内訳 | Lung Opacity 6,012 枚（BBox 9,555 個、陽性率 約 22.5%）、Not Normal 11,821 枚、Normal 8,851 枚 | 二次（6,012 は行数からの計算） |
| 公式配布の中身 | ①初期アノテーションに使った画像（3.3 GB）と初期アノテーション（JSON）、②チャレンジで使った画像とアノテーション（JSON）、③RSNA 画像と NIH 元画像の対応表（JSON） | 公式 |
| 利用条件 | 学術・教育・商用・非商用で利用可。個人の特定や接触の禁止。共有・再配布時は NIH と RSNA の両方の帰属表示が必要 | 公式 |

### 新しい指摘事項

| 番号 | 区分 | 指摘 | 報告書の該当箇所 | 優先度 | 状態 |
|---|---|---|---|---|---|
| R-15 | データ | 公式配布には「初期アノテーション」と「チャレンジ用（調整済み）」の2系統がある。どちらを主に使うかを決める（Q-05） | 2.4 | 高 | 未決定 |
| R-16 | データ | 単独読影と3人読影（BBox の交差）では BBox の大きさや品質が違う。3人読影かどうかを記録し、層別に評価する（R-07, R-09 と関連） | 2.1, 3.3, 6.1 | 高 | 未決定 |
| R-17 | データ | 陽性ラベルは確率（低・中・高）をまとめたもので、ノイズを含む。初期アノテーションから確率が取れれば「高確率のみ」で感度分析する | 2.2, 6.1 | 中 | 未決定 |
| R-18 | 解釈 | 肺炎疑い例を多く含むように選ばれたデータなので、陽性率は臨床と違う。Precision などはそのまま一般化できないと明記する | 2.1, 4.1, 6.1 | 中 | 未決定 |
| R-19 | データ | DICOM タグは性別・年齢・撮影方向だけで、機器や施設の情報はない。メタデータの交絡はこの3項目に限られるが、画像に写り込んだ文字マーカーなどは残りうるので目視で確認する（R-06 と関連） | 2.1, 3.3 | 中 | 未決定 |
| R-20 | 記述 | Dataset Description には「Non-commercial purpose」、Terms と配布ページには「商用・非商用で利用可」とあり、記載が食い違う。学術利用はどちらでも問題ないが、報告書 2.3 に一言書く | 2.3 | 低 | 未決定 |
| R-21 | 記述 | 報告書 2.1 の「12,274 individuals」は、今回の一次資料では確認できなかった。論文本文か対応表で確かめる | 2.1 | 中 | 未決定 |

### ユーザーへの確認事項（追加）

| 番号 | 内容 | 決まると何が決まるか |
|---|---|---|
| Q-05 | 主解析に使うアノテーション系統（提案：主解析は「チャレンジ用（調整済み）」、読影者ごとの解析や確率の解析には「初期アノテーション」を使う。中身を見てから確定する） | データ読み込みプログラムの仕様 |
| Q-06 | Shih et al. (2019) の PDF を大学経由で入手してアップロードできるか | R-16, R-17, R-21 の確認 |

### データ取得後に確認すること（追加）

- 公式配布の JSON の構造（読影者 ID、確率のラベル、3人読影かどうかの情報が含まれているか）
- 公式配布の総枚数（30,000 枚）と Kaggle 版の合計（26,684 + 3,000 = 29,684 枚）の差の理由
- 陽性・陰性それぞれの AP/PA の比率（全体では AP が約 46%）
- 年齢の外れ値の有無、画像に写り込んだ文字マーカーの有無

### 参考にした資料

- RSNA. RSNA Pneumonia Detection Challenge (2018). https://www.rsna.org/education/ai-resources-and-training/ai-image-challenge/RSNA-Pneumonia-Detection-Challenge-2018
- RSNA. 2018 RSNA Pneumonia Detection Challenge Dataset Description (V1 02/07/2022). 上記ページの「Dataset description」
- RSNA. Pneumonia Detection Challenge Terms of Use and Attribution. 上記ページの「Terms of use and acknowledgments」
- Shih G, et al. Augmenting the NIH Chest Radiograph Dataset with Expert Annotations of Possible Pneumonia. *Radiology: AI*, 2019. https://doi.org/10.1148/ryai.2019180041（全文は未取得。検索結果の抜粋のみ）
- Wang X, et al. ChestX-ray8: Hospital-scale Chest X-ray Database and Benchmarks on Weakly-Supervised Classification and Localization of Common Thorax Diseases. *IEEE CVPR*, pp. 3462-3471, 2017.
- Gabruseva T, et al. Deep Learning for Automatic Pneumonia Detection. *CVPR Workshops*, 2020.（Kaggle 版の内訳）
- Kaggle. RSNA Pneumonia Detection Challenge, Discussion 64723.（3人読影の分割と調整の手順）
