# 実行環境の準備と使い方

- **作成日**：2026-11-12
- **対象**：データの取得と構造確認（`scripts/download_data.py`、`scripts/build_tables.py`、`scripts/inspect_dataset.py`）

プログラムは次の2つの環境で同じように動きます。

| 環境 | 使う場面 | 実行方法 | データの保存先（既定） |
|---|---|---|---|
| Google Colab | 自宅での研究 | ノートブック `notebooks/01_data_download_and_inspection.ipynb` | Google Drive の `MyDrive/graduationResearch/data` |
| ローカル GPU PC | 研究室で PC が使えるとき | コマンドライン、または同じノートブック | リポジトリ内の `data/` |

保存先は、環境変数 `GR_DATA_DIR` で変えられます。結果の出力先は `GR_OUTPUT_DIR`（既定はデータフォルダと同じ階層の `outputs/`）で変えられます。

## 必要な容量と時間の目安

| 項目 | 容量 | 時間の目安（2026-11-12 にクラウド環境で計測） |
|---|---|---|
| ダウンロード（JSON 3 種 + 画像 ZIP） | 約 4.1 GB | 約 3 分（毎秒 20 MB 程度の回線の場合） |
| ZIP の検査（全ファイルの CRC） | — | 約 1 分 |
| 表の作成（DICOM ヘッダ 30,000 枚） | 数十 MB | 約 20 秒（2 回目以降は数秒） |

自宅の回線速度によって、ダウンロード時間は大きく変わります。途中で切れても、同じコマンドをもう一度実行すれば続きから再開します。

---

## A. Google Colab（自宅）

1. Colab で「ファイル → ノートブックを開く → GitHub」を選び、`ryu93885/graduationResearch` を入力します。ブランチを選んで `notebooks/01_data_download_and_inspection.ipynb` を開きます。
2. ランタイムは CPU のままで構いません（この段階では GPU は使いません）。
3. 上から順にセルを実行します。
   - 最初のセルで Google Drive のマウントを許可します。
   - リポジトリは `/content/graduationResearch` に取得されます。データは Drive に保存されるので、次回からダウンロードは不要です。
4. Google Drive に **約 4.5 GB の空き**が必要です。

**注意**
- ノートブックの `BRANCH` は、作業中のブランチ名になっています。`main` にマージした後は `"main"` に変えてください。
- Drive 上の ZIP を読むのが遅い場合は、ZIP を `/content` にコピーしてから `GR_DATA_DIR` をそこに向けると速くなります。

## B. ローカル GPU PC（研究室）

Python 3.10 以上と git が必要です。空き容量は 10 GB 以上を目安にしてください。

### 1. 取得とインストール（最初の 1 回だけ）

Linux / macOS：

```bash
git clone -b claude/ecstatic-sagan-459cpd https://github.com/ryu93885/graduationResearch.git
```

```bash
cd graduationResearch
```

```bash
python3 -m venv .venv
```

```bash
source .venv/bin/activate
```

```bash
pip install -e ".[dev]"
```

Windows（PowerShell）では、仮想環境の作成と有効化を次のように行います。その他のコマンドは同じです。

```powershell
py -3 -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2. データの取得と確認

```bash
python scripts/download_data.py
```

```bash
python scripts/build_tables.py
```

```bash
python scripts/inspect_dataset.py
```

データを別のドライブに置く場合は、先に `GR_DATA_DIR` を設定します（PowerShell の場合は `$env:GR_DATA_DIR = "D:\graduationResearch\data"`）。

```bash
export GR_DATA_DIR=/mnt/data/graduationResearch/data
```

### 3. ノートブックを使う場合

```bash
pip install jupyter matplotlib
```

```bash
jupyter notebook notebooks/01_data_download_and_inspection.ipynb
```

ノートブックはローカル環境だと自動で判断し、Drive のマウントとリポジトリの取得を省略します。

### 4. GPU（PyTorch）について

この段階では使いません。モデルの学習に進むときに、PC の CUDA のバージョン（`nvidia-smi` で確認）に合った PyTorch のインストール手順を追加します。

---

## 出力されるファイル

| 場所 | ファイル | 内容 |
|---|---|---|
| `data/raw/` | 公式配布ファイル、`MANIFEST.json` | 取得日・URL・サイズ・SHA-256・ライブラリのバージョン |
| `data/processed/` | `images.csv` | 1 行 1 画像（30,000 行）：ID、NIH 患者 ID、最終ラベル、BBox 数、読影の種類、DICOM ヘッダ、ZIP 内のパス |
| | `boxes.csv` | 最終ラベルの BBox（`x, y` は左上の座標、`w, h` は幅と高さ。単位はピクセル） |
| | `reader_reads.csv` | 読影者ごとの判定 |
| | `reader_boxes.csv` | 読影者ごとの BBox と確率 |
| | `dicom_headers.csv` | DICOM ヘッダのキャッシュ |
| | `splits/folds_k5_seed42.csv` | 交差検証の組（`image_id, nih_patient_id, fold`） |
| `outputs/dataset_inspection/` | `report.md`、`summary.json`、`tables/*.csv` | データ確認レポート |
| `outputs/splits/` | `fold_balance.md`、`fold_balance*.csv` | 交差検証の組の偏りの確認 |

データとその出力は `.gitignore` で除外されており、リポジトリにはコミットされません。

## 動作確認（テスト）

```bash
python -m pytest -q
```

合成データを使うので、ダウンロードは不要です。

## 困ったとき

| 症状 | 対処 |
|---|---|
| ダウンロードが途中で止まった | 同じコマンドをもう一度実行します（続きから再開します） |
| `SHA-256 ... does not match` | ファイルが壊れたか、配布元で更新された可能性があります。`.part` ファイルを消して再実行し、それでも出る場合は相談してください |
| DICOM の画素を読むときにエラー（JPEG） | 画素データは JPEG で圧縮されています。`pip install pillow` を実行します |
| `processed tables not found` | 先に `scripts/build_tables.py` を実行します |
