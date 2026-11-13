# 実行コマンド一覧（ローカル PC）

- **作成日**：2026-11-13（2026-11-12 までの版は `archive/COMMANDS.md`）
- **最終更新**：2026-11-13（新規作成。1. `scripts/download_data.py`、2. `scripts/build_tables.py`、3. テスト）
- このファイルで、プログラムを実行するコマンドを一括管理します。プログラムを追加・変更したら、ここに追記します。
- 対象は**研究室のローカル GPU PC**です。Google Colab での実行方法は [`docs/setup.md`](docs/setup.md) の「A. Google Colab」にあります。
- 特に書いていない限り、コマンドは**リポジトリのフォルダ（`graduationResearch/`）で、仮想環境を有効にしてから**実行します（0-3 を参照）。
- 実行の順番と各段階で確かめることは [`docs/procedure.md`](docs/procedure.md) にあります。

## 一覧

| 番号 | 実行するプログラム | 何をするか | 追加日 |
|---|---|---|---|
| 0 | （準備） | リポジトリの取得、仮想環境の作成、インストール | 2026-11-13 |
| 1 | `scripts/download_data.py` | 公式 RSNA データのダウンロードと照合 | 2026-11-13 |
| 2 | `scripts/build_tables.py` | 解析用の表（`images.csv`、`boxes.csv` など）の作成 | 2026-11-13 |
| 3 | `tests/`（pytest） | プログラムの動作確認（テスト） | 2026-11-13 |

**初めてデータを用意するときの順番**：0 → 1-2 → 2-1 → 3-1

**プログラムを更新した後（`git pull` の後）**：3-1 → 2-1 を実行し直します（表に列が増えることがあるため）。

---

## 0. 準備

### 0-1. リポジトリを取得する（最初の 1 回）

```bash
git clone -b claude/practical-cray-sgayfw https://github.com/ryu93885/graduationResearch.git
```

```bash
cd graduationResearch
```

ブランチを `main` にマージした後は、`-b claude/practical-cray-sgayfw` を `-b main` に変えます。

### 0-2. 仮想環境を作る（最初の 1 回）

Linux / macOS：

```bash
python3 -m venv .venv
```

Windows（PowerShell）：

```powershell
py -3 -m venv .venv
```

**既存のライブラリを使う場合**：研究室の PC に PyTorch などがすでに入っているときは、上の代わりに次のコマンドで作ります。PC に入っているライブラリをそのまま使い、足りないものだけを仮想環境に追加します（共用の環境は書き換えません）。conda を使っている場合は、先にその環境を有効にしてから実行します。モデルの学習（今後追加）では PyTorch を使うので、研究室の PC ではこちらを勧めます。

Linux / macOS：

```bash
python3 -m venv --system-site-packages .venv
```

Windows（PowerShell）：

```powershell
py -3 -m venv --system-site-packages .venv
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

既定の保存先はリポジトリ内の `data/` です。別のドライブに置くときは、1・2 を実行する前に設定します（ターミナルを開くたびに必要です）。

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
  - `images.csv`：1 行 1 画像（30,000 行）。画像 ID、NIH の患者 ID、最終ラベル（`final_class`：3クラス）、BOX の数、撮影方向・年齢・性別などの DICOM ヘッダ、ZIP 内のパス
  - `boxes.csv`：最終ラベルの BOX（`x, y` は左上の座標、`w, h` は幅と高さ。1024×1024 の画像上のピクセル）
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

### 2-5. 最終ラベルの枚数と患者数を確かめる

```bash
python -c "import pandas as pd; d = pd.read_csv('data/processed/images.csv'); print(d['final_class'].value_counts(dropna=False)); print('patients', d['nih_patient_id'].nunique())"
```

0-6 で保存先を変えた場合は、`data/processed/images.csv` をその場所に読み替えます。期待される値は [`docs/procedure.md`](docs/procedure.md) の手順 3 にあります。

| オプション | 意味 |
|---|---|
| `--no-dicom` | DICOM ヘッダの読み込みを省略 |
| `--rescan` | キャッシュ（`dicom_headers.csv`）を使わずに読み直す |
| `--dicom-limit N` | 最初の N 枚だけ読む（動作確認用） |
| `--data-dir パス` | データの保存先を指定 |

---

## 3. `tests/`：テスト（pytest）

- **内容**：プログラムが正しく動くかを、合成データで確かめます。ダウンロードしたデータは使いません。
- **使う場面**：`git pull` でプログラムを更新した後や、プログラムを変更した後

### 3-1. すべてのテストを実行する

```bash
python -m pytest -q
```

### 3-2. 1 つのファイルのテストだけを実行する（例：ダウンロード）

```bash
python -m pytest -q tests/test_download.py
```

---

## Colab の場合

Colab では、ノートブックのセルに `!` を付けてコマンドを実行します。手順は [`docs/setup.md`](docs/setup.md) の「A. Google Colab」を参照してください。
