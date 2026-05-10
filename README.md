# Book Auto Screenshot - Web Version

書籍をスキャンして、自動的にスクリーンショットを撮影し、ダウンロードするウェブアプリケーションです。iPhone のブラウザで **今すぐ動きます**！

## 機能

- 📱 **iPhone で動作**：ブラウザで開くだけで使用可能
- 📷 **自動スクショ**：ボタンをタップするだけで複数ページを自動撮影
- ↔️ **方向選択**：スワイプ方向（左/右）を事前に選択可能
- 🔄 **自動終了判定**：コンテンツの変化を検知して自動終了
- 💾 **自動ダウンロード**：撮影したスクショは自動的にダウンロード
- ✅ **完了通知**：撮影完了時にアラートで通知

## プロジェクト構成

```
BookAutoScreenshot/
├── src/
│   ├── App.tsx                       # メインアプリケーション
│   ├── App.css                       # スタイル
│   ├── main.tsx                      # エントリーポイント
│   ├── data/
│   │   └── bookContent.ts           # ページデータ定義
│   └── utils/
│       └── screenshotCapture.ts     # スクショ撮影機能
├── index.html                        # HTML テンプレート
├── package.json                      # 依存パッケージ
├── vite.config.ts                    # Vite 設定
├── tsconfig.json                     # TypeScript 設定
├── tailwind.config.js                # Tailwind CSS 設定
├── postcss.config.js                 # PostCSS 設定
└── README.md                         # このファイル
```

## セットアップ方法

### 必須環境

- Node.js 16 以上
- npm または yarn

### インストール

```bash
# 依存パッケージをインストール
npm install
```

### 開発サーバー起動

```bash
npm run dev
```

ブラウザで `http://localhost:5173` を開いてください。

### ビルド

```bash
npm run build
```

ビルド結果は `dist/` ディレクトリに出力されます。

### プレビュー

```bash
npm run preview
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

4. **ダウンロード確認**
   - 撮影したスクショは `book-screenshot-001.png` 形式で自動ダウンロード
   - iPhone では「ファイル」アプリまたは「写真」アプリで確認できます

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

## 技術スタック

- **フロントエンド**: React 18 + TypeScript
- **ビルドツール**: Vite
- **スタイリング**: Tailwind CSS
- **スクショライブラリ**: html2canvas
- **ランタイム**: Node.js 16+

## iPhone で使用する

### 1. ローカルネットワークでアクセス

開発マシンの IP アドレスを取得：

```bash
# Mac/Linux
ifconfig | grep inet

# Windows
ipconfig
```

iPhone の Safari で `http://<your-ip>:5173` にアクセス。

### 2. 本番環境にデプロイ

```bash
npm run build
```

`dist/` フォルダを Vercel、Netlify などでデプロイして、iPhone からアクセスできます。

## サンプルデータについて

`src/data/bookContent.ts` には、テスト用のサンプル本データが含まれています。
実際の本をスキャンするには、`bookPages` 配列を実際のテキストに置き換えてください。

```typescript
export const bookPages: BookContent[] = [
  {
    content: "ページ1のテキスト",
  },
  {
    content: "ページ2のテキスト",
  },
  // ...
];
```

## 今後の拡張予定

- 📸 **OCR 機能**：自動的にテキストを抽出
- 🤖 **NotebookLM 連携**：撮影したスクショから直接 NotebookLM へ送信
- 🌍 **複数言語対応**：日本語以外の言語サポート
- 📄 **PDF 出力**：撮影したスクショから PDF を生成
- ⚙️ **カスタマイズ機能**：撮影間隔やページ判定ロジックの調整
- 📤 **クラウド保存**：Google Drive, Dropbox などとの連携

## トラブルシューティング

### スクショが保存されない

- ブラウザのコンソール（F12）でエラーを確認
- html2canvas の CORS エラーが出ている場合は、要素の書き込みを確認

### ページが自動で進まない

- `src/App.tsx` のタイミング値を調整
- `setTimeout` の値を増やしてみてください

### iPhone で表示がおかしい

- ブラウザをリロード（Ctrl+R または Cmd+R）
- キャッシュをクリア

## ライセンス

MIT License

## サポート

問題が発生した場合は、GitHub Issues で報告してください。
