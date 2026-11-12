# graduationResearch

卒業研究「胸部X線画像における医師アノテーション領域外の特徴を用いた肺炎検出の検討」のリポジトリです。

RSNA Pneumonia Detection Challenge 2018 のデータを使い、次の3モデルを比較します。

- **Model A**: 医師アノテーション領域（Bounding Box）を中心に入力するモデル
- **Model B**: 画像全体を入力するモデル（基準）
- **Model C**: アノテーション領域をマスクした画像を入力するモデル

あわせて Grad-CAM などの XAI で判断根拠を可視化し、その妥当性・忠実性・安定性を評価します。

## 使い方

Google Colab（自宅）と研究室のローカル GPU PC の両方で動きます。詳しくは [`docs/setup.md`](docs/setup.md) を参照してください。

**実行コマンドの一覧は [`COMMANDS.md`](COMMANDS.md) にまとめています。**

- **Colab**：`notebooks/01_data_download_and_inspection.ipynb` を開いて、上から順に実行します。
- **ローカル**：次の順に実行します。

```bash
pip install -e ".[dev]"
```

```bash
python scripts/download_data.py
```

```bash
python scripts/build_tables.py
```

```bash
python scripts/inspect_dataset.py
```

## ディレクトリ構成

```
COMMANDS.md            実行コマンドの一覧（ローカル PC）
src/gradresearch/      Python パッケージ
  paths.py             データ・出力の保存先（Colab / ローカルを自動判定）
  data/                公式ファイルの一覧・ダウンロード・JSON と DICOM の読み込み・表の作成
  analysis/            データ確認レポート
scripts/               コマンドラインから実行するスクリプト
notebooks/             Colab / ローカル共通のノートブック
tests/                 テスト（合成データを使用）
docs/
  setup.md             実行環境の準備と使い方
  procedure.md         実行手順書（実行の順番と、各段階で確かめること）
  final_report_draft.md 最終レポートの草案（上書き形式で更新）
  reports/             進捗報告書（.docx の原本と、GitHub 上で読める .md 版）
  dataset/             データセットの資料（特徴・配布形態・利用条件・確認結果）
  revision_report.md   修正レポート（チャットでの指摘・相談・決定事項を日付ごとに記録）
```

## データについて

画像データ（DICOM など）やアノテーションファイルはリポジトリに含めません（`.gitignore` で除外しています）。
データは RSNA 公式配布ページから取得し、RSNA の利用規約と帰属表示の条件に従って扱います。
