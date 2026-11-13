# 実行環境の準備と使い方

- **作成日**：2026-11-13（2026-11-12 までの版は `archive/docs/setup.md`）
- **最終更新**：2026-11-13（新規作成）
- **対象**：データの取得と表の作成（`scripts/download_data.py`、`scripts/build_tables.py`）。モデルの学習のプログラムを追加したら、この文書に GPU（PyTorch）の準備を追記する。

プログラムは次の2つの環境で同じように動きます。

| 環境 | 使う場面 | 実行方法 | データの保存先（既定） |
|---|---|---|---|
| Google Colab | 自宅での研究 | ノートブックのセルで `!` を付けてコマンドを実行 | Google Drive の `MyDrive/graduationResearch/data` |
| ローカル GPU PC | 研究室で PC が使えるとき | コマンドライン | リポジトリ内の `data/` |

保存先は環境変数 `GR_DATA_DIR` で変えられます。結果の出力先は `GR_OUTPUT_DIR`（既定はデータフォルダと同じ階層の `outputs/`）で変えられます。

## 必要な容量と時間の目安

| 項目 | 容量 | 時間の目安（2026-11-12 にクラウド環境で計測） |
|---|---|---|
| ダウンロード（JSON 3 種 + 画像 ZIP） | 約 4.1 GB | 約 3 分（毎秒 20 MB 程度の回線の場合） |
| ZIP の検査（全ファイルの CRC） | — | 約 1 分 |
| 表の作成（DICOM ヘッダ 30,000 枚） | 数十 MB | 約 20 秒（2 回目以降は数秒） |

自宅の回線速度によって、ダウンロード時間は大きく変わります。途中で切れても、同じコマンドをもう一度実行すれば続きから再開します。

---

## A. Google Colab（自宅）

2026-11-13 の整理でノートブックを `archive/` に移したため、新しいノートブックを作るまでは、空のノートブックに次のセルを入力して実行します。ランタイムは CPU のままで構いません（この段階では GPU は使いません）。Google Drive に**約 4.5 GB の空き**が必要です。

**セル 1：Google Drive をマウントする**（許可を求められたら許可します）

```python
from google.colab import drive
drive.mount("/content/drive")
```

**セル 2：リポジトリを取得してインストールする**（Colab を開くたびに必要です）

```python
!git clone -q -b claude/practical-cray-sgayfw https://github.com/ryu93885/graduationResearch.git /content/graduationResearch
%cd /content/graduationResearch
!pip install -q -e ".[dev]"
```

同じセッションの中で 2 回目に実行するときは、`git clone` の代わりに `!git -C /content/graduationResearch pull -q` を実行します。`main` にマージした後は、`-b claude/practical-cray-sgayfw` を `-b main` に変えます。

**セル 3：データを取得して表を作る**

```python
!python scripts/download_data.py
!python scripts/build_tables.py
```

- 最初の行に `environment=Colab data_dir=/content/drive/MyDrive/graduationResearch/data` と表示されることを確かめます。
- `environment=local` と表示された場合は、セル 3 の前に `%env GR_DATA_DIR=/content/drive/MyDrive/graduationResearch/data` を実行します。
- データは Drive に保存されるので、2 回目以降はダウンロードが省略されます（`[skip] ... already present` と表示されます）。
- Drive 上の ZIP を読むのが遅い場合は、ZIP を `/content` にコピーしてから `GR_DATA_DIR` をそこに向けると速くなります。

**セル 4（任意）：テストを実行する**

```python
!python -m pytest -q
```

## B. ローカル GPU PC（研究室）

Python 3.10 以上と git が必要です。空き容量は 10 GB 以上を目安にしてください（縮小画像の保存やモデルの重みを含めると、今後さらに必要になります）。

### 1. 取得とインストール（最初の 1 回だけ）

Linux / macOS：

```bash
git clone -b claude/practical-cray-sgayfw https://github.com/ryu93885/graduationResearch.git
```

```bash
cd graduationResearch
```

```bash
python3 -m venv --system-site-packages .venv
```

```bash
source .venv/bin/activate
```

```bash
pip install -e ".[dev]"
```

Windows（PowerShell）では、仮想環境の作成と有効化を次のように行います。その他のコマンドは同じです。

```powershell
py -3 -m venv --system-site-packages .venv
```

```powershell
.venv\Scripts\Activate.ps1
```

`--system-site-packages` を付けると、研究室の PC にすでに入っている PyTorch などをそのまま使えます（共用の環境は書き換えません）。付けずに作る方法は [`COMMANDS.md`](../COMMANDS.md) の 0-2 にあります。

### 2. データの取得と表の作成

```bash
python scripts/download_data.py
```

```bash
python scripts/build_tables.py
```

データを別のドライブに置く場合は、先に `GR_DATA_DIR` を設定します（PowerShell の場合は `$env:GR_DATA_DIR = "D:\graduationResearch\data"`）。

```bash
export GR_DATA_DIR=/mnt/data/graduationResearch/data
```

### 3. GPU（PyTorch）について

データの取得と表の作成では使いません。modelA・modelB の学習のプログラムを追加するときに、次を確かめて、PC の CUDA のバージョンに合った PyTorch の準備をこの文書に追記します（Q-11）。

```bash
nvidia-smi
```

```bash
python -c "import torch, torchvision; print(torch.__version__, torchvision.__version__, torch.cuda.is_available())"
```

---

## 出力されるファイル

| 場所 | ファイル | 内容 |
|---|---|---|
| `data/raw/` | 公式配布ファイル、`MANIFEST.json` | 取得日・URL・サイズ・SHA-256・ライブラリのバージョン |
| `data/processed/` | `images.csv` | 1 行 1 画像（30,000 行）：ID、NIH 患者 ID、最終ラベル、BOX の数、読影の種類、DICOM ヘッダ、ZIP 内のパス |
| | `boxes.csv` | 最終ラベルの BOX（`x, y` は左上の座標、`w, h` は幅と高さ。単位は 1024×1024 の画像上のピクセル） |
| | `reader_reads.csv` | 読影医ごとの判定 |
| | `reader_boxes.csv` | 読影医ごとの BOX と確率 |
| | `dicom_headers.csv` | DICOM ヘッダのキャッシュ |

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
| `ModuleNotFoundError: No module named 'gradresearch'` | 仮想環境が有効になっているか確かめ、`pip install -e ".[dev]"` を実行します |
| `... not found; run scripts/download_data.py first` | 先に `scripts/download_data.py` を実行します |
| Colab で `environment=local` と表示される | `%env GR_DATA_DIR=/content/drive/MyDrive/graduationResearch/data` を実行してから、もう一度実行します |
