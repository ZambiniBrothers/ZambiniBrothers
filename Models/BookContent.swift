import Foundation

struct BookContent {
    let content: String

    static let samplePages = [
        BookContent(content: "第1章 はじめに\n\nこの本は、自動スクショ機能の使い方について説明しています。ページを左右にスワイプして、各ページの内容を撮影することができます。"),
        BookContent(content: "第1章 続き\n\nこのアプリケーションは、書籍をデジタル化するために設計されました。スクリーンショットを自動的に撮影し、写真ライブラリに保存します。"),
        BookContent(content: "第2章 機能説明\n\n・自動スクショ機能：ボタンを押すだけで複数ページの撮影ができます\n・方向選択：左右どちらへスワイプするかを事前に選択できます\n・自動終了：コンテンツの変化を検知して自動的に終了します"),
        BookContent(content: "第2章 続き\n\n撮影されたスクリーンショットは、自動的にiPhoneの写真ライブラリに保存されます。後でNotebookLMなどのツールでテキスト抽出や分析ができます。"),
        BookContent(content: "第3章 今後の展開\n\nこのアプリは今後以下の機能が追加される予定です：\n・OCR機能による自動テキスト抽出\n・NotebookLM連携\n・複数言語対応\n・PDF出力"),
    ]
}

enum SwipeDirection {
    case left
    case right
}
