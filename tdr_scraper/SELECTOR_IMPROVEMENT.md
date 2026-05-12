# TDR Wait Time Scraper - Selector Improvement Documentation

## 問題の要約

東京ディズニーランド「モンスターズ・インク『ライド＆ゴーシーク！』」の待ち時間スクレーパーが、以下の不正なデータを取得していました：

**記録されたCSVデータ:**
```
2026-05-12 08:33:34,29,696
2026-05-12 08:38:34,27,648
2026-05-12 08:43:34,25,600
2026-05-12 08:48:34,43,1032
2026-05-12 08:53:34,41,984
...
```

### 問題の原因

- **ディズニーの待ち時間は5分単位のみ:** Disney displays wait times ONLY in 5-minute increments (5, 10, 15, 20, 25, 30, ...)
- **記録された数字がすべて5分単位ではない:** 29, 27, 25, 43, 41, 39, 37, 35, 33, 31...
- **結論:** セレクタが間違った要素を取得していた（実際の待ち時間ではなく、ページ上の別の数字）

---

## 実装された改善内容

### 1. 5分単位の検証機能

**ファイル:** `scraper.py`

```python
def _is_valid_wait_time(self, minutes: int) -> bool:
    """
    Validate that wait time is in valid 5-minute increments.
    Disney displays wait times in 5-minute increments only: 5, 10, 15, 20, ...
    
    Valid: 5, 10, 15, 20, 25, 30, ...
    Invalid: 1, 3, 7, 29, 43, etc.
    """
    return minutes > 0 and minutes % 5 == 0
```

**動作:**
- すべてのセレクタで取得した数字は自動的に検証される
- 5分単位ではない数字は拒否され、次のセレクタが試される
- 5分単位の数字が見つかるまで、複数のセレクタ戦略を試し続ける

### 2. 改善されたセレクタ戦略

**ファイル:** `config.py`

9つのセレクタ戦略を優先度順に実装：

#### **Primary Strategies (最優先)**
1. **TDR Official Detail Page - Info Section**
   - TDRの詳細ページにある「アトラクション情報」セクション
   - パターン: `div[class*='attraction-info'] span[class*='wait']`

2. **Header/Top Section Info Display**
   - ページ上部のヘッダー部分
   - パターン: `header span[class*='wait']`

3. **Semantic HTML Label + Value**
   - 「待ち時間」ラベルの直後の値
   - パターン: `strong:contains('待ち時間') ~ span:first-of-type`

4. **Data Attributes**
   - JavaScript内で使用されるデータ属性
   - パターン: `[data-wait-time]`, `[data-waittime]`, `[data-minutes]`

#### **Secondary Strategies (サブ)**
5. **Japanese Minutes Span**
   - 「分」を含むspan要素
   - パターン: `span:contains('分')`

6. **Info Panel Elements**
   - 情報ボックスやパネル
   - パターン: `div[class*='info-panel'] span`

7. **List Items**
   - リスト形式で表示されている場合
   - パターン: `li span:contains('分')`

8. **Number + Unit Pattern**
   - 数字と単位が別々の要素
   - パターン: `span[class*='number'] ~ span:contains('分')`

#### **Tertiary Strategy (最終手段)**
9. **JavaScript Fallback**
   - ページの全テキストを走査してパターンマッチング
   - 5分単位の有効な数字を優先的に返す

### 3. 拡張されたデバッグ機能

**ファイル:** `scraper.py`, `debug_selectors.py`, `test_selectors_improved.py`

**改善点:**
- どのセレクタがどのような結果を返したかを詳細にログ出力
- 取得した数字が5分単位かどうかを明確に表示
- フォールバック戦略の実行状況を追跡

**ログ出力例:**
```
✓ Successfully fetched wait time via tdr_attraction_info_section: 45 min
✗ Could not find valid wait time using any selector strategy
Debug info: tdr_header_wait_display[0]: invalid time 29min (not 5-minute increment)
```

---

## テスト方法

### オプション1: テストスクリプトの実行（推奨）

```bash
cd /home/user/ZambiniBrothers/tdr_scraper

# 改善されたセレクタをテスト
python test_selectors_improved.py
```

**出力例（成功の場合）:**
```
✓ [tdr_attraction_info_section] Found 1 elements
  Element 0: 45min ✓ VALID - 待ち時間：45分

✓ Found 1 working selector(s):
  - tdr_attraction_info_section

✓ Scraper should be able to fetch wait time
```

### オプション2: スクレーパーの単一実行テスト

```bash
python test_run.py
```

**確認事項:**
- ✓ 実際に待ち時間が取得できたか
- ✓ 取得された数字が5分単位か（5, 10, 15, 20, ...）
- ✓ ログに「Successfully fetched wait time」と出力されているか
- ✓ CSV に正しいデータが記録されているか

### オプション3: 詳細な診断（Playwrightが必要）

```bash
python debug_selectors.py
```

---

## 使用例

### スクレーパーの実行

```bash
# 5分ごとにループ実行
python scraper.py

# Ctrl+C で停止
```

### CSVデータの確認

```bash
cat tdr_analysis_log.csv

# 出力例:
Timestamp,Wait Time (min),Estimated Queue
2026-05-12 13:00:00,45,1080
2026-05-12 13:05:00,50,1200
2026-05-12 13:10:00,45,1080
```

**重要:** すべての「Wait Time (min)」が5の倍数であることを確認してください。

---

## 技術詳細

### Disney Wait Time Rules (ディズニー待ち時間規則)

ディズニーテーマパークは以下のルールで待ち時間を表示：

1. **5分単位のみ表示**
   - 表示値: 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, ...

2. **端数は切り捨て（切り上げではない）**
   - 8分 → 5分表示（3分切り捨て）
   - 14分 → 10分表示（4分切り捨て）
   - 47分 → 45分表示（2分切り捨て）

3. **予測値と実績値**
   - 表示される待ち時間は「現在の待ち時間」（キュー内で待機する実測時間）
   - アトラクション側の処理時間を含まない

### セレクタ選択ロジック

```python
# Pseudo-code
for selector in config.wait_time_selectors:
    elements = page.query_selector_all(selector)
    for element in elements:
        text = element.text_content()
        minutes = parse_wait_time(text)
        
        # 重要: 5分単位の検証
        if minutes % 5 == 0 and minutes > 0:
            return minutes  # ✓ 有効
        else:
            continue  # ✗ 無効、次の要素を試す

# すべてのセレクタが失敗した場合
return None
```

---

## トラブルシューティング

### 問題1: 「Could not find valid wait time」

**原因:**
- セレクタが実際のページ構造と一致していない
- ページ構造が変更された
- ネットワーク接続の問題

**解決方法:**
```bash
# 1. テストを実行してどのセレクタが機能しているか確認
python test_selectors_improved.py

# 2. ブラウザ表示での動作確認（headless=False）
# config.py で "headless": False に変更
# python test_selectors.py

# 3. TDR公式ページを手動で確認して、HTMLを調査
# https://www.tokyodisneyresort.jp/tdl/attraction/detail/189/
```

### 問題2: 「invalid time XX min (not 5-minute increment)」

**原因:**
- セレクタが待ち時間ではなく、別の数字（ゲストレビュー、混雑スコア、年齢指定など）を取得している

**解決方法:**
```bash
# セレクタの順序を変更するか、より具体的なセレクタに変更
# config.py の wait_time_selectors を編集
```

---

## ファイル変更履歴

### config.py
- ✓ 9つのセレクタ戦略を追加（3→9に拡充）
- ✓ ディズニー待ち時間ルールのドキュメント追加
- ✓ 各セレクタに詳細なコメント追加

### scraper.py
- ✓ `_extract_wait_time()` メソッドを改善
- ✓ 複数要素の処理ロジックを追加
- ✓ デバッグログの詳細化
- ✓ `_extract_via_fallback()` メソッドを実装
- ✓ `_is_valid_wait_time()` メソッドの検証ロジック

### 新規ファイル
- ✓ `debug_selectors.py` - 詳細なセレクタ診断ツール
- ✓ `test_selectors_improved.py` - 改善されたテストスクリプト
- ✓ `SELECTOR_IMPROVEMENT.md` - このドキュメント

---

## 今後の改善提案

1. **自動セレクタ検出**
   - ページを読み込み、すべての「XX分」パターンを自動検出
   - 5分単位のパターンを自動的に使用

2. **セレクタの学習機能**
   - 複数のパターンを試して、成功したセレクタの優先度を上げる
   - 失敗したセレクタの優先度を下げる

3. **エラー通知機能**
   - セレクタが失敗した場合、通知を送信
   - GitHub Issues を自動作成してアラート

4. **複数アトラクション対応**
   - 現在はモンスターズ・インク専用だが、他のアトラクションにも対応
   - アトラクション ID をパラメータ化

---

## 参考情報

- **TDR公式ページ:** https://www.tokyodisneyresort.jp/tdl/attraction/detail/189/
- **Playwright ドキュメント:** https://playwright.dev/python/
- **CSS セレクタ リファレンス:** https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Selectors

---

**作成日:** 2026-05-12  
**バージョン:** 2.0 (Selector Improvement Update)  
**ステータス:** テスト待機中 (Awaiting Playwright Browser Installation)
