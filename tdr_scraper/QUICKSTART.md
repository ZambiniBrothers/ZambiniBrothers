# クイックスタートガイド
## Tokyo Disneyland - Monsters, Inc. Ride & Go Seek!

**対象アトラクション:** 東京ディズニーランド「モンスターズ・インク『ライド＆ゴーシーク！』」

このガイドで5分以内にスクレーパーを起動できます。

---

## 🚀 最速セットアップ（推奨）

### macOS / Linux

```bash
# このコマンド1つですべてセットアップ完了
chmod +x setup.sh && ./setup.sh

# 仮想環境を有効化
source venv/bin/activate

# スクレーパーを実行
python scraper.py
```

### Windows

```bash
# setup.bat をダブルクリックするか、以下を実行
setup.bat

# 仮想環境を有効化（setup.bat内で自動実行される場合があります）
venv\Scripts\activate.bat

# スクレーパーを実行
python scraper.py
```

---

## 📋 手動セットアップ

setup スクリプトが動作しない場合の手動手順です。

### Step 1: Python のインストール確認

```bash
python3 --version
# Python 3.8以上が必要です
```

### Step 2: 仮想環境の作成

```bash
python3 -m venv venv
```

### Step 3: 仮想環境の有効化

**macOS / Linux:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate.bat
```

### Step 4: 依存ライブラリのインストール

```bash
pip install -r requirements.txt
```

### Step 5: Playwright ブラウザのインストール

```bash
playwright install
```

この手順では Chromium ブラウザが自動ダウンロード・インストールされます。

### Step 6: スクレーパーを実行

```bash
python scraper.py
```

---

## ✅ 正常動作の確認

スクレーパーが正常に動作していることを確認してください：

1. **ターミナル出力を確認**
   ```
   2026-05-12 10:00:00 - __main__ - INFO - TDR Wait Time Scraper Started
   2026-05-12 10:00:05 - __main__ - INFO - Browser initialized
   2026-05-12 10:00:15 - __main__ - INFO - Successfully fetched wait time: 45 minutes
   ```

2. **ファイルの生成を確認**
   ```bash
   ls -la
   # 以下のファイルが生成されているか確認:
   # - tdr_scraper.log (ログファイル)
   # - tdr_analysis_log.csv (データファイル)
   ```

3. **CSV ファイルの内容を確認**
   ```bash
   cat tdr_analysis_log.csv
   # 出力例:
   # Timestamp,Wait Time (min),Estimated Queue
   # 2026-05-12 10:00:15,45,1080
   ```

---

## 🛑 停止方法

ターミナルで `Ctrl + C` を押します。

```
^C
2026-05-12 10:05:20 - __main__ - INFO - Scraper interrupted by user
```

---

## 🔧 よくある問題と解決方法

### Q: `command not found: python3`

**対策**: Python 3.8以上をインストール
- [python.org](https://www.python.org/downloads/) からダウンロード

### Q: `ModuleNotFoundError: No module named 'playwright'`

**対策**:
```bash
# 仮想環境が有効化されているか確認
# (コマンドプロンプトの左側に (venv) が表示されている)
pip install -r requirements.txt
playwright install
```

### Q: `Timeout error` が出る

**対策**:
- インターネット接続を確認
- `config.py` の `page_timeout` を増やす
  ```python
  "page_timeout": 30000,  # 30秒に変更
  ```

### Q: 待ち時間が取得できない

**対策**:
1. `config.py` で `headless: False` に変更（ブラウザを表示）
2. ブラウザの画面を確認
3. ログを確認: `cat tdr_scraper.log`
4. セレクタを更新（詳細は README.md 参照）

---

## 📊 例: データを見てみる

### サンプルデータの生成（テスト用）

```bash
python example_usage.py
```

このコマンドで以下の情報が表示されます：
- 待ち時間 → 推定人数の計算例
- 現在の設定値
- セレクタ戦略

### CSV ファイルを開く

生成されたCSVファイルはExcel、Google Sheetsなどで開けます：

```bash
# macOS
open tdr_analysis_log.csv

# Windows
start tdr_analysis_log.csv

# Linux
cat tdr_analysis_log.csv
```

---

## ⚙️ カスタマイズ例

### 実行間隔を10分に変更

`config.py` を編集:
```python
"interval_seconds": 600,  # 10分に変更
```

### ブラウザを表示しながら実行

`config.py` を編集:
```python
"headless": False,  # ブラウザウィンドウが表示されます
```

---

## 📚 次のステップ

- **詳細設定**: [README.md](README.md) を参照
- **トラブルシューティング**: [README.md - トラブルシューティング](README.md#トラブルシューティング) を参照
- **コード理解**: `scraper.py`, `config.py`, `calculator.py` を読む

---

## 💡 Tips

- **バックグラウンド実行**: `python scraper.py > /dev/null 2>&1 &` (Linux/macOS)
- **定期実行**: `cron` や Windows Task Scheduler を使用可能
- **ログ監視**: `tail -f tdr_scraper.log` でリアルタイム確認

---

**何か問題がありましたか？** README.md のトラブルシューティングセクションを確認してください。
