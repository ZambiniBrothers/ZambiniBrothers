import React, { useState, useRef } from 'react';
import { extractTextFromImage, generatePDF } from './utils/screenshotCapture';
import './App.css';

type AppMode = 'upload' | 'processing';

export default function App() {
  const [mode, setMode] = useState<AppMode>('upload');
  const [uploadedImages, setUploadedImages] = useState<File[]>([]);
  const [previewUrls, setPreviewUrls] = useState<string[]>([]);
  const [extractedTexts, setExtractedTexts] = useState<string[]>([]);
  const [isExtracting, setIsExtracting] = useState(false);
  const [extractionProgress, setExtractionProgress] = useState(0);
  const [pdfMode, setPdfMode] = useState<'single' | 'multiple'>('single');
  const [showPdfOptions, setShowPdfOptions] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const dragOverRef = useRef(false);

  const handleFileSelect = (files: FileList) => {
    const newFiles = Array.from(files).filter(file =>
      file.type.startsWith('image/')
    );

    if (newFiles.length === 0) {
      alert('画像ファイルを選択してください（PNG、JPG等）');
      return;
    }

    setUploadedImages(prev => [...prev, ...newFiles]);

    // Create preview URLs
    newFiles.forEach(file => {
      const reader = new FileReader();
      reader.onload = (e) => {
        setPreviewUrls(prev => [...prev, e.target?.result as string]);
      };
      reader.readAsDataURL(file);
    });
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    dragOverRef.current = true;
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    dragOverRef.current = false;
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    dragOverRef.current = false;
    handleFileSelect(e.dataTransfer.files);
  };

  const handleRemoveImage = (index: number) => {
    setUploadedImages(prev => prev.filter((_, i) => i !== index));
    setPreviewUrls(prev => prev.filter((_, i) => i !== index));
    setExtractedTexts(prev => prev.filter((_, i) => i !== index));
  };

  const handleExtractText = async () => {
    if (uploadedImages.length === 0) {
      alert('画像をアップロードしてください');
      return;
    }

    setMode('processing');
    setIsExtracting(true);
    setExtractionProgress(0);
    const texts: string[] = [];

    for (let i = 0; i < uploadedImages.length; i++) {
      try {
        const text = await extractTextFromImage(uploadedImages[i]);
        texts.push(text);
        setExtractionProgress(Math.round(((i + 1) / uploadedImages.length) * 100));
      } catch (error) {
        console.error(`Failed to extract text from image ${i}:`, error);
        texts.push(`[ページ ${i + 1}: テキスト抽出失敗]`);
      }
    }

    setExtractedTexts(texts);
    setIsExtracting(false);
    setShowPdfOptions(true);
  };

  const handleGeneratePDF = async () => {
    if (extractedTexts.length === 0) {
      alert('先にOCRで文字認識してください');
      return;
    }

    if (pdfMode === 'single') {
      // Generate PDF with all text combined
      const combinedText = extractedTexts.join('\n\n---ページ区切り---\n\n');
      await generatePDF([combinedText], 'book-scanned.pdf');
    } else {
      // Generate PDF with one page per image
      await generatePDF(extractedTexts, 'book-scanned.pdf');
    }

    alert('PDFを作成しました！ダウンロードフォルダを確認してください。');
    handleReset();
  };

  const handleReset = () => {
    setUploadedImages([]);
    setPreviewUrls([]);
    setExtractedTexts([]);
    setExtractionProgress(0);
    setShowPdfOptions(false);
    setMode('upload');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-center mb-2 text-gray-800">
          📚 Book Scanner Pro
        </h1>
        <p className="text-center text-gray-600 mb-8">
          書籍のスクショ → OCR → PDF 変換
        </p>

        {mode === 'upload' && (
          <div className="space-y-6">
            {/* Upload Area */}
            <div
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              className={`border-3 border-dashed rounded-lg p-12 text-center transition-all cursor-pointer ${
                dragOverRef.current
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-300 bg-white hover:border-blue-400'
              }`}
              onClick={() => fileInputRef.current?.click()}
            >
              <div className="text-5xl mb-3">📸</div>
              <h3 className="text-xl font-bold text-gray-800 mb-2">
                スクショをドラッグ&ドロップ
              </h3>
              <p className="text-gray-600 mb-4">
                または、ここをクリックして画像を選択
              </p>
              <p className="text-sm text-gray-500">
                Kindle、PDF リーダー、ブラウザなど、<br />
                どのアプリのスクショでも対応
              </p>
              <input
                ref={fileInputRef}
                type="file"
                multiple
                accept="image/*"
                onChange={(e) => {
                  if (e.target.files) {
                    handleFileSelect(e.target.files);
                  }
                }}
                className="hidden"
              />
            </div>

            {/* Image Preview */}
            {previewUrls.length > 0 && (
              <div className="bg-white rounded-lg shadow-lg p-6">
                <h2 className="text-xl font-bold mb-4 text-gray-800">
                  アップロード済み画像 ({previewUrls.length}枚)
                </h2>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  {previewUrls.map((url, index) => (
                    <div
                      key={index}
                      className="relative group rounded-lg overflow-hidden border-2 border-gray-200 hover:border-red-500 transition-all"
                    >
                      <img
                        src={url}
                        alt={`Preview ${index + 1}`}
                        className="w-full h-40 object-cover"
                      />
                      <button
                        onClick={() => handleRemoveImage(index)}
                        className="absolute inset-0 bg-red-500 bg-opacity-0 group-hover:bg-opacity-75 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all"
                      >
                        <span className="text-white font-bold text-2xl">✕</span>
                      </button>
                      <div className="absolute bottom-0 left-0 right-0 bg-black bg-opacity-50 text-white text-xs py-1 px-2">
                        {index + 1}
                      </div>
                    </div>
                  ))}
                </div>
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="mt-4 w-full bg-gray-600 text-white py-2 px-4 rounded-lg font-semibold hover:bg-gray-700 transition-all"
                >
                  ➕ さらに画像を追加
                </button>
              </div>
            )}

            {/* Controls */}
            {previewUrls.length > 0 && (
              <div className="space-y-3">
                <button
                  onClick={handleExtractText}
                  className="w-full bg-purple-600 text-white py-4 px-6 rounded-lg font-bold text-lg hover:bg-purple-700 active:scale-95 shadow-lg transition-all flex items-center justify-center gap-2"
                >
                  <span>🔍</span>
                  OCRで文字認識を開始
                </button>
                <button
                  onClick={handleReset}
                  className="w-full bg-gray-400 text-white py-2 px-4 rounded-lg font-semibold hover:bg-gray-500 transition-all"
                >
                  🗑️ リセット
                </button>
              </div>
            )}
          </div>
        )}

        {mode === 'processing' && (
          <div className="bg-white rounded-lg shadow-2xl p-8 max-w-2xl mx-auto">
            <div className="text-center space-y-6">
              {isExtracting ? (
                <>
                  <div className="text-5xl animate-spin">⚙️</div>
                  <h2 className="text-2xl font-bold text-gray-800">
                    文字認識中...
                  </h2>
                  <div className="space-y-2">
                    <div className="text-lg font-semibold text-purple-600">
                      {extractionProgress}%
                    </div>
                    <div className="w-full bg-gray-300 rounded-full h-3">
                      <div
                        className="bg-purple-600 h-3 rounded-full transition-all duration-300"
                        style={{ width: `${extractionProgress}%` }}
                      />
                    </div>
                    <p className="text-sm text-gray-600">
                      {uploadedImages.length}枚の画像を処理中...
                    </p>
                  </div>
                </>
              ) : (
                <>
                  <div className="text-5xl">✅</div>
                  <h2 className="text-2xl font-bold text-gray-800">
                    文字認識完了！
                  </h2>
                  <p className="text-gray-600">
                    {uploadedImages.length}枚の画像から<br />
                    テキストを抽出しました
                  </p>

                  {/* PDF Mode Selection */}
                  <div className="bg-gray-50 rounded-lg p-4 space-y-3 my-6">
                    <p className="text-sm font-semibold text-gray-700">
                      PDF形式を選択してください
                    </p>
                    <button
                      onClick={() => setPdfMode('single')}
                      className={`w-full py-3 px-4 rounded-lg font-semibold transition-all ${
                        pdfMode === 'single'
                          ? 'bg-blue-600 text-white'
                          : 'bg-white text-gray-700 border-2 border-gray-300'
                      }`}
                    >
                      📄 1枚のPDF
                      <div className="text-xs mt-1">
                        全ページのテキストを1つのPDFに結合
                      </div>
                    </button>
                    <button
                      onClick={() => setPdfMode('multiple')}
                      className={`w-full py-3 px-4 rounded-lg font-semibold transition-all ${
                        pdfMode === 'multiple'
                          ? 'bg-blue-600 text-white'
                          : 'bg-white text-gray-700 border-2 border-gray-300'
                      }`}
                    >
                      📚 複数ページのPDF
                      <div className="text-xs mt-1">
                        各画像が1ページになるPDF
                      </div>
                    </button>
                  </div>

                  {/* Action Buttons */}
                  <div className="space-y-2">
                    <button
                      onClick={handleGeneratePDF}
                      className="w-full bg-red-600 text-white py-4 px-6 rounded-lg font-bold text-lg hover:bg-red-700 active:scale-95 shadow-lg transition-all"
                    >
                      💾 PDFを作成・ダウンロード
                    </button>
                    <button
                      onClick={handleReset}
                      className="w-full bg-gray-600 text-white py-2 px-4 rounded-lg font-semibold hover:bg-gray-700 transition-all"
                    >
                      🔄 やり直す
                    </button>
                  </div>
                </>
              )}
            </div>
          </div>
        )}

        {/* Instructions */}
        <div className="mt-12 bg-blue-50 rounded-lg p-6 border-l-4 border-blue-500">
          <h3 className="text-lg font-bold text-gray-800 mb-3">📖 使い方</h3>
          <ol className="space-y-2 text-gray-700">
            <li><strong>1.</strong> Kindle、PDF リーダー、ブラウザなど、任意のアプリで書籍を開く</li>
            <li><strong>2.</strong> Mac のスクショツール（Cmd+Shift+5）でページをスクショ</li>
            <li><strong>3.</strong> このアプリにスクショをドラッグ&ドロップ</li>
            <li><strong>4.</strong> 「OCRで文字認識を開始」をクリック</li>
            <li><strong>5.</strong> PDF形式を選択して「PDFを作成・ダウンロード」</li>
            <li><strong>6.</strong> ダウンロードフォルダで PDF を確認</li>
          </ol>
        </div>

        {/* Features */}
        <div className="mt-8 grid md:grid-cols-3 gap-4">
          <div className="bg-white rounded-lg p-4 shadow">
            <div className="text-3xl mb-2">🎯</div>
            <h4 className="font-bold text-gray-800">複数アプリ対応</h4>
            <p className="text-sm text-gray-600 mt-2">
              Kindle、PDF、ブラウザ、雑誌アプリなど、あらゆるアプリに対応
            </p>
          </div>
          <div className="bg-white rounded-lg p-4 shadow">
            <div className="text-3xl mb-2">⚡</div>
            <h4 className="font-bold text-gray-800">高速処理</h4>
            <p className="text-sm text-gray-600 mt-2">
              複数ページを一度にアップロードして一括処理
            </p>
          </div>
          <div className="bg-white rounded-lg p-4 shadow">
            <div className="text-3xl mb-2">🔒</div>
            <h4 className="font-bold text-gray-800">プライベート</h4>
            <p className="text-sm text-gray-600 mt-2">
              全処理がローカル実行、サーバーに送信なし
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
