# 実行手順書

- **作成日**：2026-11-12
- **最終更新**：2026-11-12
- これまでに作成したプログラムを、**どの順番で実行し、何を確かめればよいか**をまとめた手順書です。
- 各コマンドの詳細とオプションは [`COMMANDS.md`](../COMMANDS.md) にあります。手順の中の「（COMMANDS 1-2）」のような表記は、`COMMANDS.md` の番号です。
- 環境の準備と困ったときの対処は [`docs/setup.md`](setup.md) にあります。
- プログラムを追加・変更したら、この手順書も更新します。

## 全体の流れ

| 手順 | 内容 | 実行するプログラム | 主な出力 |
|---|---|---|---|
| 1 | 準備（最初の 1 回） | — | 仮想環境、パッケージのインストール |
| 2 | 公式データの取得と照合 | `scripts/download_data.py` | `data/raw/`（約 4.1 GB） |
| 3 | 解析用の表の作成 | `scripts/build_tables.py` | `data/processed/*.csv` |
| 4 | データ確認レポートの作成 | `scripts/inspect_dataset.py` | `outputs/dataset_inspection/` |
| 5 | 交差検証の分割の作成と確認 | `scripts/make_splits.py` | `data/processed/splits/`、`outputs/splits/` |
| 6 | 動作確認（テスト） | `pytest` | 画面に結果を表示 |

手順 2〜5 は、この順番でしか実行できません（前の手順の出力を使うため）。手順 6 はいつ実行しても構いません。

---

## A. 研究室のローカル PC で実行する

### 手順 1：準備（最初の 1 回）

1. リポジトリを取得し、フォルダに移動します（COMMANDS 0-1）。
2. 仮想環境を作ります（COMMANDS 0-2）。
   - 研究室の PC に PyTorch などがすでに入っている場合は、それを使えるように `--system-site-packages` を付けて作ります（COMMANDS 0-2 の「既存のライブラリを使う場合」）。共用の環境を書き換えずに済みます。
3. 仮想環境を有効にします（COMMANDS 0-3）。ターミナルを開くたびに必要です。
4. パッケージをインストールします（COMMANDS 0-4）。
5. データを別のドライブに置く場合は、保存先を設定します（COMMANDS 0-6）。

**確認**：`python -c "import gradresearch, pydicom, pandas; print('ok')"` で `ok` と表示されること。

### 手順 2：公式データの取得と照合（COMMANDS 1-2）

```bash
python scripts/download_data.py
```

- 約 4.1 GB を取得します。途中で止まった場合は、同じコマンドをもう一度実行すれば続きから再開します。
- 取得後に、サイズ・SHA-256・ZIP 内の全ファイルの CRC を自動で照合します。

**確認**
- 最後に `done: annotations_full, mapping, annotations_stage1, images_full -> ...` と表示されること。
- `data/raw/MANIFEST.json` に 4 つのファイルが記録され、画像 ZIP の `zip_entries` が `30000` であること。
- エラーで `SHA-256 ... does not match` と出た場合は、`docs/setup.md` の「困ったとき」を参照します。

### 手順 3：解析用の表の作成（COMMANDS 2-1）

```bash
python scripts/build_tables.py
```

**確認**：最後に次の行数が表示されること。

| 表 | 行数 |
|---|---|
| `images` | 30,000 |
| `boxes` | 11,390 |
| `reader_reads` | 39,966 |
| `reader_boxes` | 19,635 |

### 手順 4：データ確認レポートの作成（COMMANDS 3-1）

```bash
python scripts/inspect_dataset.py
```

**確認**：`outputs/dataset_inspection/report.md` の「主な数値」が次の値になっていること（2026-11-12 に取得した公式データの場合）。

| 項目 | 値 |
|---|---|
| `positive_images` | 7,106 |
| `multi_read_images` | 4,526 |
| `patients` | 12,274 |
| `ap_share_positive` | 0.773 |
| `dicom_uids_match`（「1. ファイルと対応関係」の表） | 30,000 |

### 手順 5：交差検証の分割の作成と確認（COMMANDS 6-1）

```bash
python scripts/make_splits.py
```

**確認**
- 画面に `fingerprint 5f2c2423bfaa75b3` と表示されること。これは 2026-11-12 に作った分割と同じであることを示します。
- `outputs/splits/fold_balance.md` の冒頭に「許容範囲を超えた項目は **0 件**」と書かれていること。

### 手順 6：動作確認（COMMANDS 4-1）

```bash
python -m pytest -q
```

**確認**：`21 passed` と表示されること（2026-11-12 時点のテスト数）。

---

## B. 自宅の Google Colab で実行する

1. Colab で `notebooks/01_data_download_and_inspection.ipynb` を開きます（開き方は `docs/setup.md` の「A. Google Colab」）。
2. ランタイムは CPU のままで構いません。
3. 上から順にセルを実行します。ノートブックの節と、上の手順の対応は次のとおりです。

| ノートブックの節 | 対応する手順 | 確認すること |
|---|---|---|
| 1. 環境の準備 | 手順 1 | Google Drive のマウントを許可し、最後に `environment=Colab` と表示されること |
| 2. ダウンロード | 手順 2 | A の手順 2 と同じ |
| 3. 表の作成 | 手順 3 | A の手順 3 と同じ |
| 4. データ確認レポート | 手順 4 | A の手順 4 と同じ |
| 5. 交差検証の分割 | 手順 5 | 指紋が `5f2c2423bfaa75b3` であること |
| 6. BBox を重ねた画像の確認 | — | 赤い枠が肺の陰影の上に表示されること |
| 7. テストの実行 | 手順 6 | `21 passed` |

- データは Google Drive に保存されるので、2 回目以降はダウンロードが省略されます（`[skip] ... already present` と表示されます）。
- Drive に約 4.5 GB の空きが必要です。

---

## C. プログラムを更新したとき（`git pull` の後）

1. 最新のプログラムを取得します（COMMANDS 0-5）。Colab では、ノートブックの「1. 環境の準備」を実行すれば自動で取得します。
2. 依存ライブラリが増えた場合は、インストールし直します（COMMANDS 0-4）。
3. テストを実行します（手順 6）。
4. 表と分割を作り直します（手順 3 → 手順 5）。表に列が増えることがあるためです。ダウンロード（手順 2）はやり直す必要はありません。

---

## D. 今後追加する手順（予定）

| 手順 | 内容 | 状態 |
|---|---|---|
| 7 | 画像の前処理と保存（512px への縮小など、R-24） | 未作成 |
| 8 | メタデータモデル（年齢・性別・撮影方向・PixelSpacing、R-06） | 未作成 |
| 9 | Model B / C / C-rand / A の学習と評価 | 未作成（Q-11 の回答後に学習設定を決める） |
| 10 | Grad-CAM などによる判断根拠の評価 | 未作成 |
