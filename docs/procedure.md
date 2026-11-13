# 実行手順書

- **作成日**：2026-11-13（2026-11-12 までの版は `archive/docs/procedure.md`）
- **最終更新**：2026-11-13（新規作成）
- 現在あるプログラムを、**どの順番で実行し、何を確かめればよいか**をまとめた手順書です。今後追加する手順の予定も末尾に示します。
- 各コマンドの詳細とオプションは [`COMMANDS.md`](../COMMANDS.md) にあります。手順の中の「（COMMANDS 1-2）」のような表記は、`COMMANDS.md` の番号です。
- 環境の準備と困ったときの対処は [`docs/setup.md`](setup.md) にあります。
- プログラムを追加・変更したら、この手順書も更新します。

## 全体の流れ

| 手順 | 内容 | 実行するプログラム | 主な出力 | 状態 |
|---|---|---|---|---|
| 1 | 準備（最初の 1 回） | — | 仮想環境、パッケージのインストール | 作成済み |
| 2 | 公式データの取得と照合 | `scripts/download_data.py` | `data/raw/`（約 4.1 GB） | 作成済み |
| 3 | 解析用の表の作成 | `scripts/build_tables.py` | `data/processed/*.csv` | 作成済み |
| 4 | 動作確認（テスト） | `pytest` | 画面に結果を表示 | 作成済み |
| 5〜10 | 画像の縮小、データの分割、modelA・modelB の学習と評価、判断根拠の照合 | 未作成 | — | 予定（末尾の D） |

手順 2・3 は、この順番でしか実行できません（前の手順の出力を使うため）。手順 4 はいつ実行しても構いません。

---

## A. 研究室のローカル PC で実行する

### 手順 1：準備（最初の 1 回）

1. リポジトリを取得し、フォルダに移動します（COMMANDS 0-1）。
2. 仮想環境を作ります（COMMANDS 0-2）。研究室の PC に PyTorch などがすでに入っている場合は、`--system-site-packages` を付けて作ります。
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

### 手順 3：解析用の表の作成（COMMANDS 2-1、2-5）

```bash
python scripts/build_tables.py
```

**確認 1**：最後に次の行数が表示されること。

| 表 | 行数 |
|---|---|
| `images` | 30,000 |
| `boxes` | 11,390 |
| `reader_reads` | 39,966 |
| `reader_boxes` | 19,635 |

**確認 2**：COMMANDS 2-5 のコマンドで、最終ラベルの枚数と患者数が次の値になること（2026-11-12 に取得した公式データの場合）。

| `final_class` | 枚数 | 本研究での扱い |
|---|---|---|
| No Lung Opacity / Not Normal | 12,788 | modelA の1クラス。modelB では BOX なしの画像 |
| Normal | 9,790 | modelA の1クラス。modelB では BOX なしの画像 |
| Lung Opacity | 7,106 | modelA の1クラス。modelB では BOX ありの画像（BOX 11,390 個） |
| 空欄（NaN） | 316 | 最終ラベルがないので使わない（R-23） |
| `patients` | 12,274 | 患者単位の分割の単位 |

### 手順 4：動作確認（COMMANDS 3-1）

```bash
python -m pytest -q
```

**確認**：`14 passed` と表示されること（2026-11-13 時点のテスト数）。

---

## B. 自宅の Google Colab で実行する

`docs/setup.md` の「A. Google Colab」のセル 1〜4 を順に実行します。セルと上の手順の対応は次のとおりです。

| セル | 対応する手順 | 確認すること |
|---|---|---|
| 1. Drive のマウント | 手順 1 | 許可した後に `Mounted at /content/drive` と表示されること |
| 2. 取得とインストール | 手順 1 | エラーが出ないこと |
| 3. データの取得と表の作成 | 手順 2・3 | 最初の行が `environment=Colab data_dir=/content/drive/MyDrive/graduationResearch/data` であること。それ以外は A の手順 2・3 と同じ |
| 4. テスト | 手順 4 | `14 passed` |

- データは Google Drive に保存されるので、2 回目以降はダウンロードが省略されます（`[skip] ... already present` と表示されます）。
- 手順 3 の確認 2 は、セルで `!python -c "..."`（COMMANDS 2-5 のコマンドの `data/processed/images.csv` を `/content/drive/MyDrive/graduationResearch/data/processed/images.csv` に変えたもの）を実行して確かめます。

---

## C. プログラムを更新したとき（`git pull` の後）

1. 最新のプログラムを取得します（COMMANDS 0-5）。Colab では、セル 2 を実行し直します。
2. 依存ライブラリが増えた場合は、インストールし直します（COMMANDS 0-4）。
3. テストを実行します（手順 4）。
4. 表を作り直します（手順 3）。表に列が増えることがあるためです。ダウンロード（手順 2）はやり直す必要はありません。

---

## D. 今後追加する手順（予定）

方針は [`docs/final_report_draft.md`](final_report_draft.md) の第4章、経緯は [`docs/revision_report.md`](revision_report.md) にあります。まず交差検証の1回分（fold 0）で手順 5〜10 を通し、その後に 5 回すべてを行います（Q-22）。

| 手順 | 内容 | 確かめること（予定） | 状態 |
|---|---|---|---|
| 5 | 画像を 512×512 に縮小して PNG で保存（2×2 画素の平均） | 30,000 枚がすべて 512×512 であること。BOX（座標 ÷2）を重ねた画像で、ずれがないこと（各クラス数枚を目で確認）。32 px 未満になる BOX の数と割合 | 未作成 |
| 6 | 患者単位の5分割の作成（`archive/` の `make_splits.py` を戻す） | 指紋が `5f2c2423bfaa75b3` であること（2026-11-12 と同じ分割） | 未作成 |
| 7 | modelA（ResNet-101、3クラス）の学習 | 検証用データのマクロ平均 ROC-AUC が改善しなくなった時点で止まること | 未作成 |
| 8 | modelB（Faster R-CNN、ResNet-101-FPN）の学習 | 検証用データの mAP が改善しなくなった時点で止まること | 未作成 |
| 9 | modelA・modelB の評価 | 検証用データで目標値（Q-27）に届いているか。届いてから評価用データで 1 回だけ評価する（R-29） | 未作成 |
| 10 | Grad-CAM による判断根拠とアノテーションの照合 | Pointing game・BOX 内の割合・IoU の集計 | 未作成 |
