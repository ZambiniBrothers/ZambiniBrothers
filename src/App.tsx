import React, { useState, useRef } from 'react';
import { BookContent, SwipeDirection, bookPages } from './data/bookContent';
import { captureScreenshot } from './utils/screenshotCapture';
import './App.css';

export default function App() {
  const [currentPageIndex, setCurrentPageIndex] = useState(0);
  const [swipeDirection, setSwipeDirection] = useState<SwipeDirection>('right');
  const [isAutoScreenshooting, setIsAutoScreenshooting] = useState(false);
  const [showCompletionAlert, setShowCompletionAlert] = useState(false);
  const [screenshotCount, setScreenshotCount] = useState(0);
  const contentRef = useRef<HTMLDivElement>(null);

  const handleStartAutoScreenshot = async () => {
    setIsAutoScreenshooting(true);
    setScreenshotCount(0);
    setCurrentPageIndex(0);

    await captureAndSwipe(0, bookPages[0].content);
  };

  const captureAndSwipe = async (pageIndex: number, previousContent: string) => {
    await new Promise(resolve => setTimeout(resolve, 100));

    // Capture screenshot
    if (contentRef.current) {
      await captureScreenshot(contentRef.current, pageIndex + 1);
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
    } else {
      // Continue to next page
      await new Promise(resolve => setTimeout(resolve, 500));
      await captureAndSwipe(nextPageIndex, newContent);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold text-center mb-8 text-gray-800">
          📚 Book Auto Screenshot
        </h1>

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
            <div className="bg-white rounded-lg shadow-2xl p-8 max-w-sm w-full">
              <div className="text-center">
                <div className="text-4xl mb-4">✅</div>
                <h2 className="text-2xl font-bold mb-2 text-gray-800">完了</h2>
                <p className="text-gray-600 mb-6 text-lg">
                  {screenshotCount}枚のスクショを撮影しました
                </p>
                <button
                  onClick={() => {
                    setShowCompletionAlert(false);
                    setCurrentPageIndex(0);
                    setScreenshotCount(0);
                  }}
                  className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition-all"
                >
                  OK
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
