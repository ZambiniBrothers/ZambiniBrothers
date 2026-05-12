# TDR Wait Time Scraper
## モンスターズ・インク「ライド＆ゴーシーク！」待ち時間自動取得エージェント

自動的に東京ディズニーランドの「モンスターズ・インク『ライド＆ゴーシーク！』」の待ち時間を取得し、推定Qライン人数を計算・記録するPythonエージェントです。

---

## 機能

✅ **自動待ち時間取得**
- Playwrightを使用したブラウザ自動操作
- 複数のセレクタ戦略で堅牢な抽出
- サイト構造変更に強い設計

✅ **推定人数計算**
- 30秒ディスパッチ × 12名/回 = 24名/分
- 計算式: 待ち時間（分） × 24 = 推定Qライン人数

✅ **定期実行**
- 5分ごとに自動実行（カスタマイズ可能）
- ログ記録機能付き

✅ **CSVエクスポート**
- `tdr_analysis_log.csv` に日時・待ち時間・推定人数を記録

---

## セットアップ手順

### 前提条件

- **Python 3.8以上**がインストールされていること
- **pip**がインストールされていること
- インターネット接続が必要

### Step 1: リポジトリをクローン/移動

```bash
cd tdr_scraper
```

### Step 2: 仮想環境の作成（推奨）

```bash
# 仮想環境を作成
python -m venv venv

# 仮想環境を有効化
# Windows の場合:
venv\Scripts\activate
# macOS / Linux の場合:
source venv/bin/activate
```

### Step 3: 依存ライブラリのインストール

```bash
pip install -r requirements.txt
```

### Step 4: Playwrightブラウザのインストール

```bash
playwright install
```

このコマンドはChromiumブラウザをダウンロード・インストールします。

---

## 使用方法

### 基本的な実行

```bash
python scraper.py
```

このコマンドで、5分ごとに待ち時間を自動取得し続けます。

### 停止方法

ターミナルで `Ctrl + C` を押して停止します。

### ログ出力

- **コンソール**: リアルタイム実行状況の表示
- **ファイル**: `tdr_scraper.log` に詳細ログを記録
- **CSV**: `tdr_analysis_log.csv` に集計データを記録

---

## 設定のカスタマイズ

### `config.py` で調整可能な設定

```python
CONFIG = {
    "interval_seconds": 300,      # 実行間隔（秒）。デフォルト: 5分
    "page_timeout": 15000,         # ページ読み込みタイムアウト（ミリ秒）
    "output_csv": "tdr_analysis_log.csv",  # 出力CSV名
    "headless": True,              # True: ブラウザを表示しない, False: 表示
}
```

### セレクタの更新（サイト構造変更時）

TDRの公式サイトのHTML構造が変わった場合、`config.py` の `wait_time_selectors` を更新します。

**複数のセレクタ戦略が実装されているため、1つのセレクタが動作しなくても他の戦略が自動的に試されます。**

```python
# 新しいセレクタを追加する場合
from config import update_selectors

update_selectors({
    "new_strategy_name": "新しいCSSセレクタ",
})
```

---

## 出力ファイル形式

### `tdr_analysis_log.csv`

```csv
Timestamp,Wait Time (min),Estimated Queue
2026-05-12 10:00:15,45,1080
2026-05-12 10:05:30,48,1152
2026-05-12 10:10:45,50,1200
```

### `tdr_scraper.log`

```
2026-05-12 10:00:00 - __main__ - INFO - TDR Wait Time Scraper Started
2026-05-12 10:00:05 - __main__ - INFO - Browser initialized
2026-05-12 10:00:15 - __main__ - INFO - Successfully fetched wait time: 45 minutes
2026-05-12 10:00:16 - __main__ - INFO - Logged: 2026-05-12 10:00:15, Wait: 45min, Queue: 1080 people
```

---

## トラブルシューティング

### Q1: `ModuleNotFoundError: No module named 'playwright'`

**対策**: 以下のコマンドを実行

```bash
pip install -r requirements.txt
playwright install
```

### Q2: `Timeout error` が繰り返される

**対策**: 
- インターネット接続を確認
- `config.py` の `page_timeout` を大きくする（例: 30000）
- 別の時間帯で試す（TDRサイトの負荷が低い時間）

### Q3: 待ち時間が取得できない

**対策**:
1. ブラウザを表示して確認：`config.py` で `headless: False` に変更
2. ログを確認：`tdr_scraper.log` でどのセレクタで失敗したか確認
3. TDRサイトのHTML構造を調査し、セレクタを更新

### Q4: メモリ使用量が多い

**対策**:
- 実行間隔を広げる（例: 600秒に変更）
- ブラウザを複数立ち上げないようにする（既にシングルインスタンス設計）

---

## コード構成

```
tdr_scraper/
├── scraper.py          # メインスクレーパーロジック
├── config.py           # 設定・セレクタ管理
├── calculator.py       # 推定人数計算
├── utils.py            # ユーティリティ関数
├── requirements.txt    # Python依存ライブラリ
├── README.md           # このファイル
├── tdr_analysis_log.csv    # 出力データ（実行後に生成）
└── tdr_scraper.log     # 実行ログ（実行後に生成）
```

---

## 計算ロジックの詳細

### 基本パラメータ

| 項目 | 値 |
|------|-----|
| 1回のディスパッチ（発車）時間 | 30秒 |
| 1回あたりの乗車人数 | 12名（6人乗り × 2台連結） |
| 1分間のディスパッチ回数 | 2回（60秒 ÷ 30秒） |
| 1分間のキャリー人数 | 24名（12名 × 2回） |

### 計算式

```
推定Qライン人数 = 待ち時間（分） × 24
```

**例**:
- 待ち時間が45分の場合
- 推定Qライン人数 = 45 × 24 = **1,080人**

---

## パフォーマンス考慮事項

### メモリ使用量の最適化

- Playwrightページは各実行後に確実にクローズ
- 最大リトライ回数: 3回（無限ループ防止）
- 各リトライ間に遅延を挿入

### 通信最適化

- User-Agentを設定（ブロック防止）
- `domcontentloaded` まで待機（全読み込み待機ではない）
- HTTPヘッダーを最小限に

---

## セキュリティノート

- 本スクリプトはTDR公式サイトからデータを取得します
- サイトの `robots.txt` とサービス規約を尊重してください
- 過度な頻度でのアクセスはご控えください
- 個人用途での利用を想定しています

---

## ライセンス

このプロジェクトはMITライセンスの下で提供されています。

---

## 技術サポート

セレクタが動作しなくなった場合は、`config.py` を確認し、新しいセレクタを追加してください。複数のセレクタ戦略を持つことで、頑健性を確保しています。
