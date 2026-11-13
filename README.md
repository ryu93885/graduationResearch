# graduationResearch

卒業研究のリポジトリです。RSNA Pneumonia Detection Challenge 2018 の胸部X線画像を使い、画像分類と画像検出のモデルの判断根拠（Grad-CAM で可視化）が、医師のアノテーション（BOX）とどれだけ合っているかを検証します。

| フェーズ | 内容 | モデル・手法 | 状態 |
|---|---|---|---|
| 1 | 画像分類（3クラス：Lung Opacity／No Lung Opacity / Not Normal／Normal） | modelA：ResNet-101 | 未実装 |
| 2 | 画像検出（Lung Opacity の BOX） | modelB：Faster R-CNN（ResNet-101-FPN） | 未実装 |
| 3 | 判断根拠とアノテーションの照合 | Grad-CAM | 未実装 |

現在あるプログラムは、**データの取得（ダウンロード）と解析用の表の作成**だけです。

## 文書

| ファイル | 内容 |
|---|---|
| [`COMMANDS.md`](COMMANDS.md) | 実行コマンドの一覧（ローカル PC） |
| [`docs/setup.md`](docs/setup.md) | 実行環境の準備（Google Colab と研究室のローカル GPU PC） |
| [`docs/procedure.md`](docs/procedure.md) | 実行手順書（実行の順番と、各段階で確かめること） |
| [`docs/final_report_draft.md`](docs/final_report_draft.md) | 最終レポートの草案（上書き形式で更新） |
| [`docs/revision_report.md`](docs/revision_report.md) | 修正レポート（チャットでの指摘・相談・決定事項を日付ごとに記録） |

## 使い方

Google Colab（自宅）と研究室のローカル GPU PC の両方で動きます。準備は [`docs/setup.md`](docs/setup.md)、コマンドは [`COMMANDS.md`](COMMANDS.md) を参照してください。ローカル PC では、仮想環境を有効にしてから次の順に実行します。

```bash
pip install -e ".[dev]"
```

```bash
python scripts/download_data.py
```

```bash
python scripts/build_tables.py
```

## ディレクトリ構成

```
CLAUDE.md              作業ルール
COMMANDS.md            実行コマンドの一覧（ローカル PC）
pyproject.toml         パッケージの設定と依存ライブラリ
scripts/
  download_data.py     公式データのダウンロードと照合
  build_tables.py      解析用の表の作成
src/gradresearch/
  paths.py             データ・出力の保存先（Colab / ローカルを自動判定）
  data/                公式ファイルの一覧・ダウンロード・アノテーションと DICOM ヘッダの読み込み・表の作成
tests/                 テスト（合成データを使用）
docs/                  文書（上の表）
archive/               2026-11-13 の整理で退避したファイル（参照用。元のフォルダ構成のまま）
```

## データについて

画像データ（DICOM など）・アノテーションファイル・学習済みの重みはリポジトリに含めません（`.gitignore` で除外しています）。
データは RSNA の公式配布ページから取得し、RSNA の利用規約と帰属表示の条件に従って扱います。
