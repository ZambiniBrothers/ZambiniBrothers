# Book Auto Screenshot App

iPhone で書籍をスキャンして、自動的にスクリーンショットを撮影し、写真ライブラリに保存するアプリケーションです。

## 機能

- 📱 **自動スクショ**：ボタンをタップするだけで複数ページを自動撮影
- ↔️ **方向選択**：スワイプ方向（左/右）を事前に選択可能
- 🔄 **自動終了判定**：コンテンツの変化を検知して自動終了
- 💾 **写真ライブラリ保存**：撮影したスクショは自動的に iPhone の写真ライブラリに保存
- ✅ **完了通知**：撮影完了時にアラートで通知

## プロジェクト構成

```
BookAutoScreenshot/
├── BookAutoScreenshot.swift          # App entry point
├── ContentView.swift                 # メインビュー
├── Models/
│   └── BookContent.swift            # ページデータとスワイプ方向定義
├── Utilities/
│   └── ScreenshotManager.swift       # スクショ保存機能
├── Extensions/
│   └── UIView+Screenshot.swift       # スクショ撮影拡張
├── Info.plist                        # アプリ設定（フォトライブラリアクセス権限）
└── README.md                         # このファイル
```

## セットアップ方法

### 1. Xcode プロジェクト作成

```bash
cd /path/to/ZambiniBrothers
```

Xcode で新規 iOS App プロジェクトを作成：
- **Product Name**: BookAutoScreenshot
- **Interface**: SwiftUI
- **Language**: Swift
- **Minimum Deployment Target**: iOS 15.0 以上

### 2. ファイルの配置

上記のプロジェクト構成通りに Swift ファイルを Xcode に追加してください。

### 3. Info.plist の設定

Xcode では、`Info.plist` に以下の権限が自動的に設定されます：
```
NSPhotoLibraryAddUsageDescription: "スクリーンショットを写真ライブラリに保存するため、アクセス許可が必要です"
```

### 4. ビルドと実行

```bash
xcodebuild build
# または Xcode で ⌘+B でビルド
```

実行：
```bash
xcodebuild -scheme BookAutoScreenshot -configuration Debug -simulator
# または Xcode で ⌘+R で実行
```

## 使い方

1. **スワイプ方向を選択**
   - 「左へ」ボタン：左方向にスワイプ
   - 「右へ」ボタン：右方向にスワイプ

2. **自動スクショ開始**
   - 「自動スクショ開始」ボタンをタップ
   - アプリが自動的にスクリーンショットを撮影し、次のページにスワイプします

3. **自動終了**
   - コンテンツが変わらなくなると、アプリが自動的に終了
   - 完了アラートが表示され、撮影枚数が表示されます

## 動作フロー

```
1. 「自動スクショ開始」をタップ
   ↓
2. 現在のページをスクショ
   ↓
3. 0.1秒後、指定方向にスワイプ
   ↓
4. 0.5秒後、次のページのスクショを撮影
   ↓
5. コンテンツが前ページと同じ、または最後ページに到達？
   ├─ YES → 「完了」アラート表示
   └─ NO → 手順2に戻る
```

## 技術仕様

- **言語**: Swift 5.9+
- **フレームワーク**: SwiftUI, Photos
- **最小 iOS バージョン**: iOS 15.0
- **対応デバイス**: iPhone (iPad は未テスト)

## 権限設定

このアプリは以下の権限が必要です：
- **NSPhotoLibraryAddUsageDescription**: 写真ライブラリへの追加アクセス

初回起動時にユーザーに許可を求めるアラートが表示されます。

## 今後の拡張予定

- 📸 **OCR 機能**：自動的にテキストを抽出
- 🤖 **NotebookLM 連携**：撮影したスクショから直接 NotebookLM へ送信
- 🌍 **複数言語対応**：日本語以外の言語サポート
- 📄 **PDF 出力**：撮影したスクショから PDF を生成
- ⚙️ **カスタマイズ機能**：撮影間隔やページ判定ロジックの調整

## トラブルシューティング

### スクショが保存されない
- **解決策**: 「写真」アプリへのアクセス許可を確認してください
  - 設定 > 自動スクショ > 写真 > 「追加可能」に設定

### ページが自動で進まない
- **解決策**: ContentView.swift のタイミング値を調整
  - `DispatchQueue.main.asyncAfter(deadline: .now() + 0.5)` の 0.5 を増やす

### コンテンツ変更検知がうまくいかない
- **解決策**: BookContent.swift でサンプルデータを確認
  - 各ページのコンテンツが異なることを確認

## サンプルデータについて

`Models/BookContent.swift` には、テスト用のサンプル本データが含まれています。
実際の本をスキャンするには、BookContent.samplePages を実際のテキストに置き換えてください。

```swift
static let samplePages = [
    BookContent(content: "ページ1のテキスト"),
    BookContent(content: "ページ2のテキスト"),
    // ...
]
```

## ライセンス

MIT License

## サポート

問題が発生した場合は、GitHub Issues で報告してください。
