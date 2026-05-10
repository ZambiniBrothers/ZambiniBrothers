import React, { useState, useRef } from 'react';
import { BookContent, SwipeDirection, bookPages } from './data/bookContent';
import { captureScreenshotAsBlob, extractTextFromImage, generatePDF } from './utils/screenshotCapture';
import './App.css';

export default function App() {
  const [currentPageIndex, setCurrentPageIndex] = useState(0);
  const [swipeDirection, setSwipeDirection] = useState<SwipeDirection>('right');
  const [isAutoScreenshooting, setIsAutoScreenshooting] = useState(false);
  const [showCompletionAlert, setShowCompletionAlert] = useState(false);
  const [screenshotCount, setScreenshotCount] = useState(0);
  const [capturedImages, setCapturedImages] = useState<Blob[]>([]);
  const [extractedTexts, setExtractedTexts] = useState<string[]>([]);
  const [isExtracting, setIsExtracting] = useState(false);
  const [extractionProgress, setExtractionProgress] = useState(0);
  const [pdfMode, setPdfMode] = useState<'single' | 'multiple'>('single');
  const [showPdfOptions, setShowPdfOptions] = useState(false);
  const contentRef = useRef<HTMLDivElement>(null);

  const handleStartAutoScreenshot = async () => {
    setIsAutoScreenshooting(true);
    setScreenshotCount(0);
    setCurrentPageIndex(0);
    setCapturedImages([]);
    setExtractedTexts([]);

    await captureAndSwipe(0, bookPages[0].content);
  };

  const captureAndSwipe = async (pageIndex: number, previousContent: string) => {
    await new Promise(resolve => setTimeout(resolve, 100));

    // Capture screenshot
    if (contentRef.current) {
      const blob = await captureScreenshotAsBlob(contentRef.current);
      setCapturedImages(prev => [...prev, blob]);
      setScreenshotCount(prev => prev + 1);
    }

    // Wait and then swipe
    await new Promise(resolve => setTimeout(resolve, 100));

    let nextPageIndex = pageIndex;
    if (swipeDirection === 'right') {
      nextPageIndex = Math.min(pageIndex + 1, bookPages.length - 1);
    } else {
      nextPageIndex = Math.max(pageIndex - 1, 0);
    }

    setCurrentPageIndex(nextPageIndex);

    const newContent = bookPages[nextPageIndex].content;

    // Check if content changed or reached the end
    if (previousContent === newContent || nextPageIndex >= bookPages.length - 1) {
      setIsAutoScreenshooting(false);
      setShowCompletionAlert(true);
      setShowPdfOptions(true);
    } else {
      // Continue to next page
      await new Promise(resolve => setTimeout(resolve, 500));
      await captureAndSwipe(nextPageIndex, newContent);
    }
  };

  const handleExtractText = async () => {
    setIsExtracting(true);
    setExtractionProgress(0);
    const texts: string[] = [];

    for (let i = 0; i < capturedImages.length; i++) {
      try {
        const text = await extractTextFromImage(capturedImages[i]);
        texts.push(text);
        setExtractionProgress(Math.round(((i + 1) / capturedImages.length) * 100));
      } catch (error) {
        console.error(`Failed to extract text from image ${i}:`, error);
        texts.push(`[テキスト抽出失敗]`);
      }
    }

    setExtractedTexts(texts);
    setIsExtracting(false);
  };

  const handleGeneratePDF = async () => {
    let textsToUse = extractedTexts;

    // If single page mode and not extracted yet, extract first
    if (pdfMode === 'single' && extractedTexts.length === 0) {
      await handleExtractText();
      textsToUse = extractedTexts;
    }

    if (pdfMode === 'single') {
      // Generate PDF with all text combined
      const combinedText = textsToUse.join('\n\n---\n\n');
      await generatePDF([combinedText], 'book-combined.pdf');
    } else {
      // Generate PDF with one page per image
      await generatePDF(textsToUse, 'book-pages.pdf');
    }

    setShowPdfOptions(false);
  };

  const handleReset = () => {
    setShowCompletionAlert(false);
    setShowPdfOptions(false);
    setCurrentPageIndex(0);
    setScreenshotCount(0);
    setCapturedImages([]);
    setExtractedTexts([]);
    setExtractionProgress(0);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold text-center mb-2 text-gray-800">
          📚 Book Scanner Pro
        </h1>
        <p className="text-center text-gray-600 mb-8">
          スクショ → OCR → PDF 変換
        </p>

        {/* Book Content Display */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6 min-h-96">
          <div className="text-sm text-gray-500 mb-3">
            ページ {currentPageIndex + 1}/{bookPages.length}
          </div>
          <div
            ref={contentRef}
            className="prose prose-sm max-w-none text-gray-700 whitespace-pre-wrap leading-relaxed"
            id="content-to-capture"
          >
            {bookPages[currentPageIndex].content}
          </div>
        </div>

        {/* Controls */}
        <div className="bg-white rounded-lg shadow-lg p-6 space-y-4">
          {/* Direction Selection */}
          <div className="grid grid-cols-2 gap-3">
            <button
              onClick={() => setSwipeDirection('left')}
              className={`py-3 px-4 rounded-lg font-semibold transition-all flex items-center justify-center gap-2 ${
                swipeDirection === 'left'
                  ? 'bg-blue-500 text-white shadow-md'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
              disabled={isAutoScreenshooting}
            >
              <span>⬅️</span>
              左へ
            </button>
            <button
              onClick={() => setSwipeDirection('right')}
              className={`py-3 px-4 rounded-lg font-semibold transition-all flex items-center justify-center gap-2 ${
                swipeDirection === 'right'
                  ? 'bg-blue-500 text-white shadow-md'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
              disabled={isAutoScreenshooting}
            >
              右へ
              <span>➡️</span>
            </button>
          </div>

          {/* Start Button */}
          <button
            onClick={handleStartAutoScreenshot}
            disabled={isAutoScreenshooting}
            className={`w-full py-4 px-6 rounded-lg font-bold text-white transition-all flex items-center justify-center gap-2 text-lg ${
              isAutoScreenshooting
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700 active:scale-95 shadow-lg'
            }`}
          >
            <span>📷</span>
            {isAutoScreenshooting ? '撮影中...' : '自動スクショ開始'}
          </button>

          {/* Status */}
          {isAutoScreenshooting && (
            <div className="text-center text-sm text-gray-600">
              進捗: {screenshotCount}枚 撮影完了
            </div>
          )}
        </div>

        {/* Completion Alert */}
        {showCompletionAlert && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg shadow-2xl p-8 max-w-sm w-full max-h-96 overflow-y-auto">
              <div className="text-center">
                <div className="text-4xl mb-4">✅</div>
                <h2 className="text-2xl font-bold mb-2 text-gray-800">スクショ撮影完了！</h2>
                <p className="text-gray-600 mb-6">
                  {screenshotCount}枚のスクショを撮影しました
                </p>

                {showPdfOptions && (
                  <div className="space-y-4">
                    <div>
                      <p className="text-sm text-gray-600 mb-3">PDF形式を選択してください</p>
                      <div className="space-y-2">
                        <button
                          onClick={() => setPdfMode('single')}
                          className={`w-full py-2 px-3 rounded text-sm font-semibold transition-all ${
                            pdfMode === 'single'
                              ? 'bg-green-500 text-white'
                              : 'bg-gray-200 text-gray-700'
                          }`}
                        >
                          📄 1枚のPDF (全テキスト結合)
                        </button>
                        <button
                          onClick={() => setPdfMode('multiple')}
                          className={`w-full py-2 px-3 rounded text-sm font-semibold transition-all ${
                            pdfMode === 'multiple'
                              ? 'bg-green-500 text-white'
                              : 'bg-gray-200 text-gray-700'
                          }`}
                        >
                          📚 複数ページのPDF (1ページ/画像)
                        </button>
                      </div>
                    </div>

                    {!isExtracting && extractedTexts.length === 0 && (
                      <button
                        onClick={handleExtractText}
                        className="w-full bg-purple-600 text-white py-2 px-4 rounded-lg font-semibold hover:bg-purple-700 transition-all text-sm"
                      >
                        🔍 OCRで文字認識
                      </button>
                    )}

                    {isExtracting && (
                      <div className="space-y-2">
                        <div className="text-sm text-gray-600">文字認識中... {extractionProgress}%</div>
                        <div className="w-full bg-gray-300 rounded-full h-2">
                          <div
                            className="bg-purple-600 h-2 rounded-full transition-all duration-300"
                            style={{ width: `${extractionProgress}%` }}
                          />
                        </div>
                      </div>
                    )}

                    {extractedTexts.length > 0 && (
                      <button
                        onClick={handleGeneratePDF}
                        className="w-full bg-red-600 text-white py-3 px-4 rounded-lg font-bold hover:bg-red-700 transition-all"
                      >
                        💾 PDFを作成・ダウンロード
                      </button>
                    )}

                    <button
                      onClick={handleReset}
                      className="w-full bg-gray-600 text-white py-2 px-4 rounded-lg font-semibold hover:bg-gray-700 transition-all text-sm"
                    >
                      🔄 やり直す
                    </button>
                  </div>
                )}

                {!showPdfOptions && (
                  <button
                    onClick={handleReset}
                    className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition-all"
                  >
                    OK
                  </button>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
