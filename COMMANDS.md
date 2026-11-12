# 実行コマンド一覧（ローカル PC）

- **作成日**：2026-11-12
- **最終更新**：2026-11-12
- このファイルで、プログラムを実行するコマンドを一括管理します。プログラムを追加・変更したら、ここに追記します。
- 対象は**研究室のローカル GPU PC**です。Google Colab ではノートブックを使います（末尾の「Colab の場合」を参照）。
- 特に書いていない限り、コマンドは**リポジトリのフォルダ（`graduationResearch/`）で、仮想環境を有効にしてから**実行します（0-3 を参照）。
- 準備の詳しい説明は [`docs/setup.md`](docs/setup.md) にあります。

## 一覧

| 番号 | 実行するプログラム | 何をするか | 追加日 |
|---|---|---|---|
| 0 | （準備） | リポジトリの取得、仮想環境の作成、インストール | 2026-11-12 |
| 1 | `scripts/download_data.py` | 公式 RSNA データのダウンロードと照合 | 2026-11-12 |
| 2 | `scripts/build_tables.py` | 解析用の表（`images.csv` など）の作成 | 2026-11-12 |
| 3 | `scripts/inspect_dataset.py` | データ確認レポートの作成 | 2026-11-12 |
| 4 | `tests/`（pytest） | プログラムの動作確認（テスト） | 2026-11-12 |
| 5 | `notebooks/01_data_download_and_inspection.ipynb` | 1〜3 をノートブックで実行 | 2026-11-12 |

**初めてデータを用意するときの順番**：0 → 1-2 → 2-1 → 3-1

---

## 0. 準備

### 0-1. リポジトリを取得する（最初の 1 回）

```bash
git clone -b claude/ecstatic-sagan-459cpd https://github.com/ryu93885/graduationResearch.git
```

```bash
cd graduationResearch
```

ブランチを `main` にマージした後は、`-b claude/ecstatic-sagan-459cpd` を `-b main` に変えます。

### 0-2. 仮想環境を作る（最初の 1 回）

Linux / macOS：

```bash
python3 -m venv .venv
```

Windows（PowerShell）：

```powershell
py -3 -m venv .venv
```

### 0-3. 仮想環境を有効にする（ターミナルを開くたび）

Linux / macOS：

```bash
source .venv/bin/activate
```

Windows（PowerShell）：

```powershell
.venv\Scripts\Activate.ps1
```

### 0-4. プログラムをインストールする（最初の 1 回、および依存ライブラリが増えたとき）

```bash
pip install -e ".[dev]"
```

### 0-5. 最新のプログラムに更新する

```bash
git pull
```

### 0-6. データの保存先を変える（任意）

既定の保存先はリポジトリ内の `data/` です。別のドライブに置くときは、1〜3 を実行する前に設定します（ターミナルを開くたびに必要です）。

Linux / macOS：

```bash
export GR_DATA_DIR=/mnt/data/graduationResearch/data
```

Windows（PowerShell）：

```powershell
$env:GR_DATA_DIR = "D:\graduationResearch\data"
```

結果の出力先は `GR_OUTPUT_DIR` で変えられます（既定はデータフォルダと同じ階層の `outputs/`）。

---

## 1. `scripts/download_data.py`：公式データのダウンロード

- **内容**：RSNA の公式配布ファイルを取得します。途中で切れても、同じコマンドを再実行すれば続きから再開します。取得後にサイズと SHA-256 を照合し、ZIP は全ファイルの CRC を検査します。
- **出力**：`data/raw/`（公式ファイルと `MANIFEST.json`）
- **時間の目安**：約 4.1 GB。毎秒 20 MB の回線で約 3 分、ZIP の検査に約 1 分

### 1-1. 取得できるファイルの一覧を表示する

```bash
python scripts/download_data.py --list
```

### 1-2. 標準のファイルをすべて取得する（通常はこれ）

```bash
python scripts/download_data.py
```

### 1-3. 小さい JSON ファイルだけを取得する（約 90 MB、画像は取得しない）

```bash
python scripts/download_data.py --keys annotations_full mapping annotations_stage1
```

### 1-4. 取得済みのファイルが壊れていないか確かめる（SHA-256 の再計算）

```bash
python scripts/download_data.py --verify
```

### 1-5. 保存先を指定して取得する

```bash
python scripts/download_data.py --data-dir /mnt/data/graduationResearch/data
```

| オプション | 意味 |
|---|---|
| `--list` | 取得できるファイルの一覧を表示して終了 |
| `--keys キー ...` | 取得するファイルを指定（`annotations_full` `mapping` `annotations_stage1` `images_full` `images_stage1`） |
| `--verify` | 取得済みのファイルの SHA-256 を計算し直して照合 |
| `--no-zip-test` | ZIP の CRC 検査を省略 |
| `--data-dir パス` | データの保存先を指定（`GR_DATA_DIR` より優先） |

---

## 2. `scripts/build_tables.py`：解析用の表の作成

- **内容**：アノテーション・NIH 対応表・DICOM ヘッダから、解析に使う表を作ります。ZIP を展開せずに DICOM ヘッダを読みます。
- **前提**：1-2 が終わっていること
- **出力**：`data/processed/`（`images.csv`、`boxes.csv`、`reader_reads.csv`、`reader_boxes.csv`、`dicom_headers.csv`）
- **時間の目安**：初回約 20 秒（DICOM ヘッダ 30,000 枚）、2 回目以降は数秒

### 2-1. 表をすべて作る（通常はこれ）

```bash
python scripts/build_tables.py
```

### 2-2. DICOM ヘッダを使わずに作る（画像 ZIP がなくても動く）

```bash
python scripts/build_tables.py --no-dicom
```

### 2-3. DICOM ヘッダを読み直す（キャッシュを使わない）

```bash
python scripts/build_tables.py --rescan
```

### 2-4. 動作確認用に、最初の 300 枚だけ DICOM ヘッダを読む

```bash
python scripts/build_tables.py --dicom-limit 300
```

この場合 `images.csv` の DICOM の列はほとんど空になります。確認が終わったら 2-1 を実行し直してください。

| オプション | 意味 |
|---|---|
| `--no-dicom` | DICOM ヘッダの読み込みを省略 |
| `--rescan` | キャッシュ（`dicom_headers.csv`）を使わずに読み直す |
| `--dicom-limit N` | 最初の N 枚だけ読む（動作確認用） |
| `--data-dir パス` | データの保存先を指定 |

---

## 3. `scripts/inspect_dataset.py`：データ確認レポートの作成

- **内容**：ラベルの分布、撮影方向・年齢・性別・PixelSpacing、BBox、読影者の一致度、患者ごとの画像枚数をまとめます。
- **前提**：2-1 が終わっていること
- **出力**：`outputs/dataset_inspection/`（`report.md`、`summary.json`、`tables/*.csv`）

### 3-1. レポートを作る

```bash
python scripts/inspect_dataset.py
```

### 3-2. 出力先を指定してレポートを作る

```bash
python scripts/inspect_dataset.py --out outputs/dataset_inspection_test
```

| オプション | 意味 |
|---|---|
| `--out パス` | 出力先を指定 |
| `--data-dir パス` | データの保存先を指定 |

---

## 4. `tests/`：テスト（pytest）

- **内容**：プログラムが正しく動くかを、合成データで確かめます。ダウンロードしたデータは使いません。
- **使う場面**：`git pull` でプログラムを更新した後や、プログラムを変更した後

### 4-1. すべてのテストを実行する

```bash
python -m pytest -q
```

### 4-2. 1 つのファイルのテストだけを実行する（例：ダウンロード）

```bash
python -m pytest -q tests/test_download.py
```

---

## 5. `notebooks/01_data_download_and_inspection.ipynb`：ノートブック（ローカル）

- **内容**：1〜3 と、BBox を重ねた画像の表示を、ノートブックで順に実行します。ローカル環境だと自動で判断し、Google Drive のマウントは行いません。

### 5-1. Jupyter をインストールする（最初の 1 回）

```bash
pip install jupyter matplotlib
```

### 5-2. ノートブックを開く

```bash
jupyter notebook notebooks/01_data_download_and_inspection.ipynb
```

---

## Colab の場合

Colab ではコマンドを直接入力する必要はありません。`notebooks/01_data_download_and_inspection.ipynb` を開いて、上から順にセルを実行します。手順は [`docs/setup.md`](docs/setup.md) の「A. Google Colab」を参照してください。
