# 最終レポート草案

> **この文書について**
> - 最終更新日：2026-11-13
> - 卒業研究の最終レポートを執筆するための参考草案である。進捗に合わせて**全体を上書きして更新する**（追記形式ではない）。経緯の記録は `docs/revision_report.md` にある。
> - 2026-11-13 に研究を組み立て直したため、新しく作成した。前回の研究（医師アノテーション領域外の特徴を用いた肺炎検出）の草案は `archive/docs/final_report_draft.md` にある。データセットの事前検証の結果（第3章）は前回の検証を引き継いでいる。
> - 記号の意味：【未実施】＝まだ実験を行っていない、【未確定】＝方針は決まっているが細部が決まっていない、【案】＝提案段階で合意していない、【要確認】＝原典で確認が必要。
> - 文中の R-xx・Q-xx は `docs/revision_report.md` の指摘事項・確認事項の番号である。最終レポートでは削除してよい。

---

# 胸部X線画像の肺炎検出における画像分類・物体検出モデルの判断根拠と医師アノテーションの整合性の検証【案：題名】
## ―ResNet-101 と Faster R-CNN の Grad-CAM による分析―

## 要旨

医療分野では深層学習モデルの性能が専門医に近づきつつある一方、その判断根拠が不明確であることが臨床への導入を妨げている。本研究は、胸部X線画像の公開データセット RSNA Pneumonia Detection Challenge 2018 を用い、画像分類モデル（ResNet-101）と物体検出モデル（Faster R-CNN、ResNet-101-FPN）の判断根拠を Grad-CAM で可視化し、医師が付けた肺炎の陰影の BOX とどれだけ整合するかを定量的に評価する。分類モデルはラベルだけから学習し、検出モデルは BOX から学習する。この違いが判断根拠と医師のアノテーションの整合性にどう表れるかを比較する。整合しない根拠については、ほかの画像と比べて、新たな視点となりうる所見か、撮影条件などの近道（ショートカット）かを検討する。【未実施：結果と結論は実験後に記載する】

---

## 第1章 序論

### 1.1 研究背景

医療分野では AI の活用が進んでおり、まれな症例では専門医の読影に及ばないものの、一般的な症例では専門医と同等以上の性能を示す報告がある【要確認：引用する文献を選ぶ】。しかし、深層学習モデルの判断根拠は人が直接読み取れず、説明可能性が議論され続けている。このことが、医療現場への導入が限られている一因である。

判断根拠を示す方法として、予測に寄与した画像領域をヒートマップで示す XAI の手法がある。その代表が Grad-CAM である [8]。可視化した根拠が医師の注目する領域と一致すれば、モデルが医師と同じ根拠で判断していることの裏付けになる。一致しない場合は、モデルが医師の気づかない所見を捉えている可能性と、病変とは無関係な手がかりに依存している可能性の両方がある。

### 1.2 研究目的

本研究の目的は、胸部X線画像の肺炎検出において、画像分類モデルと物体検出モデルの判断根拠を Grad-CAM で可視化し、医師のアノテーション（BOX）との整合性を定量的に評価することで、AI の判断の信頼性を検証することである。あわせて、医師のアノテーションと異なる判断根拠が、新たな視点での画像検出につながるかどうかを検討する。

### 1.3 研究課題

| 番号 | 研究課題 |
|---|---|
| RQ1 | ラベルだけから学習した画像分類モデル（modelA）の判断根拠は、医師の BOX とどれだけ整合するか |
| RQ2 | BOX から学習した物体検出モデル（modelB）の判断根拠は、医師の BOX とどれだけ整合するか。modelA との違いは何か |
| RQ3 | 医師の BOX と整合しない判断根拠は、ほかの画像と比べたときに、根拠として確からしいか。それとも撮影条件などの近道か |

---

## 第2章 関連研究【要確認：書誌情報と数値は原典で確認する】

### 2.1 胸部X線データセット

NIH ChestX-ray8/14 は、NIH Clinical Center の正面胸部X線画像 112,120 枚（30,805 人）に、読影レポートから自然言語処理で抽出した 14 種類の所見ラベルを付けたデータセットである [1]。ラベルは自動抽出であるため誤りを含む。RSNA Pneumonia Detection Challenge 2018 のデータセットは、この中から 30,000 枚を選び、放射線科医が肺炎を疑う陰影の有無と位置（BOX）を手作業で付け直したものである [2]。

### 2.2 胸部X線画像の肺炎の分類と検出

RSNA Pneumonia Detection Challenge 2018 は Kaggle で行われ、BOX の検出性能を IoU のしきい値 0.40〜0.75 で平均した mAP で競った。最終順位の上位3チームの mAP は 0.25475、0.24781、0.23908 であった [3, 4]。上位の解法には、複数のモデルや交差検証の各回のモデルを組み合わせたものがある【要確認：1位・3位の解法の詳細】。たとえば2位の解法は、SE-ResNeXt101 を土台とする RetinaNet 型の検出器を4分割の交差検証で学習し、その出力を組み合わせた [3]。Faster R-CNN を改良した手法で mAP 0.3923 を報告した研究もあるが、評価の条件（IoU のしきい値と評価用データ）が異なる【要確認】[5]。

本研究と同じ3クラス（Lung Opacity／No Lung Opacity / Not Normal／Normal）の分類では、ResNet-50 で正解率 0.734 という報告がある【要確認：査読の水準が低い媒体のため、査読付き論文の値を探す】[6]。

### 2.3 判断根拠の可視化と評価

CAM は、全体平均プーリングの直後に全結合層を1つだけ持つ CNN について、最後の畳み込み層の特徴マップと全結合層の重みから、クラスごとの寄与をヒートマップとして示す手法である [7]。Grad-CAM は、これを勾配を用いて一般化し、任意の CNN に適用できるようにした [8]。全体平均プーリングの後に全結合層が1つだけの構造では、Grad-CAM は CAM と定数倍を除いて一致する。

可視化手法には、モデルや学習データに依存しない出力を返すものがあり、健全性の確認が必要であることが指摘されている [9]。胸部X線では、可視化手法による位置の特定は放射線科医の水準に届かないこと [10]、RSNA Pneumonia を含むデータで、Grad-CAM を含む8種類の可視化手法がいずれも、位置を特定するために学習したネットワーク（検出・セグメンテーション）より劣ること [11] が報告されている。後者は、位置の特定が目的なら検出やセグメンテーションのモデルを使うべきだと結論している。ヒートマップと正解領域の整合性の指標には、ヒートマップの最大の点が正解領域に入る割合を測る Pointing game [12] や、ヒートマップの値のうち正解領域の中にある割合を測る方法 [13] がある。

### 2.4 ショートカット学習

Geirhos らは、標準的な評価では高い性能を示すが、意図した特徴とは異なる手がかりに依存する決定規則を「ショートカット学習」として整理した [14]。胸部X線では、Zech らが肺炎検出モデルの性能が施設をまたぐと低下し、モデルが撮影施設そのものを識別できることを示した [15]。DeGrave らは、COVID-19 の検出モデルが病変ではなく画像の文字マーカーや辺縁などに依存していたことを示した [16]。RQ3 では、これらの近道の可能性を区別して検討する必要がある。

---

## 第3章 データセットと事前検証

第3章の数値は、2026-11-12 に公式配布ページから取得したデータで確認したものである。

### 3.1 データの取得

RSNA の公式配布ページ [17] から、アノテーション（全読影医のラベルと最終ラベル）、30,000 枚の DICOM 画像、NIH の元画像との対応表を取得した。各ファイルのサイズと SHA-256 を記録し、画像 ZIP は全 30,000 ファイルの CRC を検査して破損がないことを確認した。データの利用にあたっては RSNA の利用規約 [18] に従い、個人の特定や接触を試みない。共有・再配布の際は NIH と RSNA の帰属表示を行う。

### 3.2 画像の性質

30,000 枚はすべて 1024×1024 画素、8 ビット、MONOCHROME2 であり、画素データは JPEG Baseline（非可逆）で圧縮されている。撮影方向は PA が 16,248 枚、AP が 13,752 枚である。1画素の実寸（PixelSpacing）は画像によって異なり、主に 0.139〜0.194 mm である。

### 3.3 ラベルと BOX

最終ラベルの内訳は、Lung Opacity 7,106 枚、No Lung Opacity / Not Normal 12,788 枚、Normal 9,790 枚であり、316 枚には最終ラベルがない。最終ラベルのない画像は使わず、解析対象は 29,684 枚とする（R-23）。BOX は Lung Opacity の画像にだけ付いており、総数は 11,390 個である。陽性画像 1 枚あたりの BOX は 1 個が 3,030 枚、2 個が 3,892 枚、3 個が 160 枚、4 個が 24 枚である。

BOX の大きさ（中央値）は、1人読影の画像で幅 221 × 高さ 308 ピクセル（画像の 6.5%）、3人読影の画像で 178 × 224 ピクセル（3.8%）である。3人読影では読影医の BOX の交差が最終 BOX とされているため [2]、BOX が小さい。最小の BOX は幅・高さとも約 40 ピクセルである。

### 3.4 データの特性

- **撮影方向による偏り**：陽性率は AP で 40.5%、PA で 10.0% であり、陽性画像の 77.3% が AP であった。撮影方向だけを予測値としたときの ROC-AUC は 0.708 である。AP 撮影はベッド上の重症患者に多く用いられるため、撮影方向はモデルの近道となりうる（R-06）。一部の画像には文字マーカーの写り込みも確認した。
- **画像の選定による偏り**：30,000 枚は、NIH のラベルで肺炎関連 15,000 枚、No Finding 7,500 枚、その他の所見 7,500 枚となるように選ばれている。肺炎疑い例を意図的に多く含むため、陽性率や適合率を臨床の集団にそのまま一般化することはできない（R-18）。
- **患者**：30,000 枚は NIH の患者 12,274 人に由来し、1 人あたり最大 75 枚の画像がある。同じ患者の画像が学習用と評価用の両方に入ると性能を過大に評価するため、患者単位で分割する（R-03）。

### 3.5 512×512 への縮小の検証

計算量を抑えるため、入力画像は 1024×1024 から 512×512 に縮小する（Q-18）。その妥当性を次のとおり確認した。

| 確認項目 | 結果 |
|---|---|
| 縮小の方法 | 全画像が 1024×1024 であるため、ちょうど 1/2 になる。2×2 画素の平均で縮小すれば、縦横比が変わらず余白も不要であり、BOX の座標は 2 で割るだけでよい |
| 1画素の実寸 | 0.28〜0.39 mm となる。BOX の中央値は実寸で約 3〜5 cm であり、肺炎の陰影を写すには十分である |
| BOX の大きさ | 中央値は約 110×154 ピクセル、最小は約 20×19 ピクセルとなる。Faster R-CNN の最小のアンカー（32 ピクセル）より小さい BOX はごく一部と見込まれる【未実施：件数を数える】 |
| Grad-CAM の細かさ | ResNet-101 の最後の層（layer4）の出力は 16×16 となる（1マスは元の画像の 64 ピクセル）。中央値の BOX は約 3×5 マスに当たり、比較できる。最小の BOX は1マスより小さいため、32×32 の layer3 も補助として用いる |

ただし、No Lung Opacity / Not Normal には結節など小さい所見も含まれるため、縮小の影響が Lung Opacity より出やすい可能性がある。所見によって必要な解像度が異なることが報告されている [19]。縮小画像に BOX を重ねてずれがないことは、前処理の実装時に確認する【未実施】。

---

## 第4章 方法

### 4.1 全体の流れ

本研究は3つのフェーズで行う。フェーズ1では modelA（ResNet-101）で画像を3クラスに分類する。フェーズ2では modelB（Faster R-CNN、ResNet-101-FPN）で Lung Opacity の BOX を検出する。フェーズ3では、両モデルの判断根拠を Grad-CAM で可視化し、医師の BOX と照合する。

検出モデルには当初 MedSAM [20] を検討した。しかし MedSAM は、画像と BOX のプロンプトを入力として領域のマスクを出力するモデルであり、単独では BOX を検出しない。また、本データセットにはマスクの正解がない。そこで、modelA と同じ ResNet-101 を土台に使え、ResNet の論文 [21] でも ResNet-101 と組み合わせて検出の結果が報告されている Faster R-CNN [22] を採用した（Q-16、Q-20）。両モデルの土台を同じにすることで、Grad-CAM を同じ構造の層にかけて判断根拠を比べられる。

### 4.2 データの分割

患者単位の5分割交差検証を用いる。同じ患者の画像はすべて同じ組に入れ、最終ラベル・読影の種類と判断の難しさ（3人読影で意見が割れた画像など、R-25）・撮影方向の内訳がそろうように分ける（シード 42、指紋 `5f2c2423bfaa75b3`。2026-11-12 に作成した分割）。各組は約 5,937 枚・約 2,447 人であり、陽性率はすべての組で 0.239 である。第 k 回では、組 k を評価用、組 k+1 を検証用、残りの 3 組を学習用とする（学習 60%・検証 20%・評価 20%）。まず第 0 回で全フェーズを通し、その後に 5 回すべてを行う（Q-22）。結果は 5 回の平均と標準偏差で示す。

### 4.3 前処理

DICOM の画素を読み込み、2×2 画素の平均で 512×512 に縮小し、PNG（可逆圧縮）で保存する。グレースケールの画像を 3 チャンネルに複製して入力する。BOX の座標は 1/2 にする。データ拡張は最初は行わず、目標値に届かないときの見直しの候補とする【案】。

### 4.4 modelA：画像分類（ResNet-101）

torchvision の ResNet-101 [21] を用い、ImageNet で学習済みの重み（`IMAGENET1K_V1`）から学習を始める。本体の構造は変えず、最後の全結合層（2048→1000）を 2048→3 の線形層に置き換える。残差接続は全 33 ブロックにすでにあるため、追加しない。中間の層を追加しないことで、Grad-CAM が CAM と一致し、判断根拠の解釈が単純になる。パラメータ数は 42,506,307 である。入力は ImageNet の平均と標準偏差で正規化し、出力は softmax による3クラスの確率とする。損失関数は交差エントロピーとする。全層を学習する。

### 4.5 modelB：物体検出（Faster R-CNN、ResNet-101-FPN）

torchvision の Faster R-CNN [22] に、ResNet-101 と FPN [23] からなる土台を組み合わせる。土台は modelA と同じ ImageNet の重みから始め、FPN・RPN・検出ヘッドは新しく学習する。torchvision には ResNet-101 版の COCO で学習済みの重みがないためである。検出するクラスは Lung Opacity の1つ（背景を含めて2クラス）とし、ほかの2クラスの画像は BOX のない画像として学習に用いる。

構造は、ResNet-101（全結合層を除く）→ FPN（5段階：128²〜8²、各 256 チャンネル）→ RPN → RoIAlign（7×7）→ 全結合 2 層（12,544→1,024→1,024）→ 予測層（分類 1,024→2、BOX の回帰 1,024→8）である。パラメータ数は 60,239,065 である。torchvision は既定で画像の短辺を 800 に拡大するため、入力の大きさを 512 に固定する。アンカーは既定の 32〜512 ピクセル、縦横比 0.5・1・2 とする。conv1・layer1 とバッチ正規化の統計は固定する（torchvision の既定）。

### 4.6 学習の条件

| 項目 | modelA | modelB |
|---|---|---|
| 最適化アルゴリズム | SGD（momentum 0.9、weight decay 1e-4。文献 [21] と同じ） | SGD（momentum 0.9、weight decay 5e-4。文献 [22] と同じ） |
| 学習率【案】 | 0.001〜0.01 の中から検証用データで決める | 画像 1 枚あたり 0.001（バッチの枚数倍） |
| 学習率の調整【案】 | 検証用データの指標が改善しなくなったら 1/10 にする | 同じ |
| バッチサイズ【未確定】 | 16〜32（GPU による。Q-11） | 4〜8（同） |
| 学習の終了 | 検証用データの指標が一定の epoch 数（【案】5）改善しなければ終了し、最も良かった epoch の重みを用いる（Q-21） | 同じ |
| 終了の判断に使う指標【案】 | マクロ平均 ROC-AUC | mAP（IoU 0.5） |

文献 [21] の学習率 0.1 は ImageNet をゼロから学習するときの設定であり、学習済みの重みから始める本研究では小さくする。検証用データで目標値（4.8 節）に届かない場合は、モデルの構造、損失関数、最適化アルゴリズム、スケジューラを見直す（Q-21）。

### 4.7 評価指標

- **modelA**：正解率、クラスごとの適合率・再現率・F値、マクロ平均 F値、クラスごとの ROC-AUC（そのクラスか否か）、混同行列。
- **modelB**（R-28）：BOX 単位では、予測 BOX と正解 BOX の IoU が 0.5 以上なら正解として、適合率・再現率・F値・mAP を求める。画像単位では、BOX の最大の確信度を陽性の度合いとみなし、Lung Opacity かどうかの正解率・F値・ROC-AUC を求める。先行研究と比べるため、Kaggle と同じ方法（IoU 0.40〜0.75 の平均）でも求める【要確認：BOX のない画像の扱いなど、Kaggle の計算方法の細部】。

### 4.8 目標値【案】

目標値は先行研究の値を参考に、学習を始める前に決める（Q-24）。目標値に届いたかどうかは検証用データで判断し、評価用データは最後に1回だけ用いる（R-29）。

| モデル | 指標 | 参考にする値 | 目標値【案】 |
|---|---|---|---|
| modelA | 3クラスの正解率 | ResNet-50 で 0.734 [6]【要確認】 | 0.70 以上 |
| modelA | Lung Opacity の ROC-AUC | 撮影方向だけで予測した値 0.708（本データ、3.4 節） | 0.708 を明確に上回る。具体的な値は査読付き論文の値を確認して決める【要確認】 |
| modelB | Kaggle 方式の mAP | コンペ上位3チーム 0.239〜0.255（2位は複数モデルの組み合わせ。評価用データは Kaggle のもの）[3, 4] | 0.20 以上（単一モデルのため、1位の約 8 割を目安とする） |

先行研究の値は評価用データや条件が本研究と異なるため、目標値は性能が妥当な水準にあることを確かめる目安とし、厳密な比較には用いない。

### 4.9 判断根拠の評価（フェーズ3）

| 項目 | modelA | modelB |
|---|---|---|
| Grad-CAM の対象の層 | layer4 の出力（2048 チャンネル × 16×16）。補助として layer3（1024 チャンネル × 32×32） | 土台の layer4 の出力（【案】FPN の出力も候補） |
| 何に対する根拠か | Lung Opacity のスコア（softmax の前の値） | 予測した各 BOX の確信度 |
| 対象の画像 | 評価用データの Lung Opacity の画像 | 同じ |

整合性は次の3つの指標で測る【案】。

- **Pointing game** [12]：Grad-CAM の最大の点が正解 BOX の中に入る割合
- **BOX 内の割合** [13]：Grad-CAM の値の合計のうち、正解 BOX の中にある割合
- **IoU**：Grad-CAM の上位 20% の領域と正解 BOX の和集合との IoU

modelB は BOX から学習するため、判断根拠が BOX と整合するのはある程度当然である。ラベルだけから学習した modelA の判断根拠が BOX とどれだけ整合するかが、本研究の中心的な結果となる。1人読影と3人読影では BOX の決め方が異なる（3.3 節）ため、読影の種類ごとにも集計する【案】。

BOX と整合しない判断根拠（RQ3）は、ヒートマップの最大の点の位置で分類する【案】。肺野の中で BOX の外にあるものは、ほかの読影医が陰影と判断した領域（読影医ごとの BOX）と重なるかを確かめる。肺野の外（文字マーカー、チューブ類、画像の端など）にあるものは近道の候補として、撮影方向（AP／PA）ごとの頻度をほかの画像と比べる。

### 4.10 評価用データの扱い

再学習や設定の調整はすべて検証用データで判断し、評価用データは最後に1回だけ用いる（R-29）。これにより、評価用データに合わせた調整による性能の過大評価を防ぐ。

---

## 第5章 結果

### 5.1 modelA の分類性能【未実施】

### 5.2 modelB の検出性能【未実施】

### 5.3 modelA の判断根拠と BOX の整合性【未実施】

### 5.4 modelB の判断根拠と BOX の整合性【未実施】

### 5.5 BOX と整合しない判断根拠の分析【未実施】

---

## 第6章 考察

### 6.1 結果に関する考察【未実施】

### 6.2 限界

- BOX は陰影を囲む矩形であり、病変の輪郭ではない。BOX の中にも病変でない部分が含まれる。
- 3人読影の画像の BOX は読影医の BOX の交差であり、1人読影の画像の BOX より小さい。整合性の値は BOX の決め方の影響を受ける。
- ラベルは肺炎を疑う画像所見の分類であり、臨床的な診断ではない。
- データは単一施設（NIH Clinical Center）の画像であり、ほかの施設での一般化は検証できない。
- 画像は 8 ビットに変換され、JPEG で非可逆圧縮されている。本研究ではさらに 512×512 に縮小する。
- データセットは肺炎疑い例を多く含むように選ばれており、陽性率は臨床の集団とは異なる。
- Grad-CAM の細かさは最後の層の大きさ（16×16）で決まり、小さい BOX との整合性は粗くしか測れない。
- ヒートマップはモデルの内部の判断過程を完全には説明しない。本研究では可視化だけから因果的な主張は行わない。

---

## 第7章 結論と今後の計画

### 7.1 現時点の結論【未実施】

### 7.2 今後の計画（締切 2026-12-31）【案】

| 期間 | 内容 |
|---|---|
| 11/14〜11/20 | 画像の縮小と保存、分割の準備、modelA の実装と第 0 回の学習 |
| 11/21〜11/30 | modelB の実装と第 0 回の学習、Grad-CAM の実装 |
| 12/01〜12/10 | 第 0 回でのフェーズ3、目標値に届かない場合の見直し |
| 12/11〜12/24 | 残りの 4 回の学習と評価、フェーズ3 の集計 |
| 12/25〜12/31 | 結果の整理と執筆 |

---

## 付録 A：実装と再現性

- プログラムは Python で実装し、リポジトリ（`ryu93885/graduationResearch`）で管理している。Google Colab と研究室のローカル GPU PC の両方で同じ結果が得られるように作成する。
- データの取得では、公式ファイルのサイズと SHA-256 を照合し、取得日・URL・ライブラリのバージョンを `MANIFEST.json` に記録する。
- 交差検証の分割は指紋で同一性を確認する。
- 2つのモデルの構造（パラメータ数・特徴マップの大きさ）は、torchvision 0.29.2（torch 2.15.0、CPU）で組み立てて確認した（2026-11-13）。
- 実行手順は `docs/procedure.md`、実行コマンドは `COMMANDS.md` にある。

## 参考文献【要確認：最終レポートに載せる前に原典で確認する】

1. Wang X, Peng Y, Lu L, Lu Z, Bagheri M, Summers RM. ChestX-ray8: Hospital-scale Chest X-ray Database and Benchmarks on Weakly-Supervised Classification and Localization of Common Thorax Diseases. *IEEE CVPR*, pp. 3462-3471, 2017.
2. Shih G, Wu CC, Halabi SS, et al. Augmenting the National Institutes of Health Chest Radiograph Dataset with Expert Annotations of Possible Pneumonia. *Radiology: Artificial Intelligence*, 2019. https://doi.org/10.1148/ryai.2019180041（全文は未確認、Q-06）
3. Gabruseva T, Poplavskiy D, Kalinin AA. Deep Learning for Automatic Pneumonia Detection. *CVPR Workshops*, 2020. https://arxiv.org/abs/2005.13899（Table 4 にコンペの最終順位）
4. RSNA. プレスリリース（RSNA Pneumonia Detection Challenge の結果の発表, 2018。題名は未確認）. https://www.rsna.org/media/press/i/2059
5. Pneumonia Detection Using an Improved Algorithm Based on Faster R-CNN. 2021. https://pmc.ncbi.nlm.nih.gov/articles/PMC8081632/（著者名・掲載誌・評価条件は未確認）
6. Pneumonia Detection in Chest X-Rays Using Deep Learning. *Young Scientist Journal*（Vanderbilt University）. https://www.vanderbilt.edu/youngscientistjournal/article/5769/（著者名・年は未確認）
7. Zhou B, Khosla A, Lapedriza A, Oliva A, Torralba A. Learning Deep Features for Discriminative Localization. *IEEE CVPR*, 2016.
8. Selvaraju RR, et al. Grad-CAM: Visual Explanations from Deep Networks via Gradient-based Localization. *ICCV*, 2017.
9. Adebayo J, et al. Sanity Checks for Saliency Maps. *NeurIPS*, 2018.
10. Saporta A, et al. Benchmarking saliency methods for chest X-ray interpretation. *Nature Machine Intelligence*, 2022.
11. Arun N, et al. Assessing the Trustworthiness of Saliency Maps for Localizing Abnormalities in Medical Imaging. *Radiology: Artificial Intelligence*, 3(6): e200267, 2021.
12. Zhang J, et al. Top-down Neural Attention by Excitation Backprop. *ECCV*, 2016.
13. Wang H, et al. Score-CAM: Score-Weighted Visual Explanations for Convolutional Neural Networks. *CVPR Workshops*, 2020.
14. Geirhos R, et al. Shortcut learning in deep neural networks. *Nature Machine Intelligence*, 2020.
15. Zech JR, et al. Variable generalization performance of a deep learning model to detect pneumonia in chest radiographs: A cross-sectional study. *PLOS Medicine*, 2018.
16. DeGrave AJ, Janizek JD, Lee SI. AI for radiographic COVID-19 detection selects shortcuts over signal. *Nature Machine Intelligence*, 2021.
17. RSNA. RSNA Pneumonia Detection Challenge (2018). https://www.rsna.org/education/ai-resources-and-training/ai-image-challenge/RSNA-Pneumonia-Detection-Challenge-2018
18. RSNA. Pneumonia Detection Challenge Terms of Use and Attribution.
19. Sabottke CF, Spieler BM. The Effect of Image Resolution on Deep Learning in Radiography. *Radiology: Artificial Intelligence*, 2020.
20. Ma J, He Y, Li F, Han L, You C, Wang B. Segment anything in medical images. *Nature Communications*, 15: 654, 2024.
21. He K, Zhang X, Ren S, Sun J. Deep Residual Learning for Image Recognition. *IEEE CVPR*, 2016.
22. Ren S, He K, Girshick R, Sun J. Faster R-CNN: Towards Real-Time Object Detection with Region Proposal Networks. *NeurIPS*, 2015.
23. Lin TY, Dollár P, Girshick R, He K, Hariharan B, Belongie S. Feature Pyramid Networks for Object Detection. *IEEE CVPR*, 2017.
