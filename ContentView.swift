import SwiftUI
import Photos

struct ContentView: View {
    @State private var currentPageIndex = 0
    @State private var bookPages = BookContent.samplePages
    @State private var isAutoScreenshooting = false
    @State private var swipeDirection: SwipeDirection = .right
    @State private var showCompletionAlert = false
    @State private var screenshotCount = 0
    @State private var screenshotManager = ScreenshotManager()

    var body: some View {
        ZStack {
            VStack(spacing: 16) {
                // Book content display
                VStack {
                    Text("ページ \(currentPageIndex + 1)/\(bookPages.count)")
                        .font(.caption)
                        .foregroundColor(.gray)

                    ScrollView {
                        Text(bookPages[currentPageIndex].content)
                            .padding()
                            .font(.body)
                            .lineSpacing(6)
                    }
                }
                .frame(maxHeight: .infinity)
                .border(Color.gray.opacity(0.3))
                .padding()

                // Controls
                VStack(spacing: 12) {
                    HStack(spacing: 12) {
                        Button(action: { swipeDirection = .left }) {
                            Label("左へ", systemImage: "arrowshape.left.fill")
                        }
                        .buttonStyle(.bordered)
                        .tint(swipeDirection == .left ? .blue : .gray)

                        Button(action: { swipeDirection = .right }) {
                            Label("右へ", systemImage: "arrowshape.right.fill")
                        }
                        .buttonStyle(.bordered)
                        .tint(swipeDirection == .right ? .blue : .gray)
                    }

                    Button(action: startAutoScreenshot) {
                        HStack {
                            Image(systemName: "camera.fill")
                            Text(isAutoScreenshooting ? "撮影中..." : "自動スクショ開始")
                        }
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(isAutoScreenshooting ? Color.gray : Color.blue)
                        .foregroundColor(.white)
                        .cornerRadius(8)
                    }
                    .disabled(isAutoScreenshooting)
                }
                .padding()
            }
        }
        .alert("完了", isPresented: $showCompletionAlert) {
            Button("OK") {
                resetState()
            }
        } message: {
            Text("\(screenshotCount)枚のスクショを撮影しました")
        }
    }

    private func startAutoScreenshot() {
        isAutoScreenshooting = true
        screenshotCount = 0
        currentPageIndex = 0

        requestPhotoLibraryAccess {
            captureAndSwipe()
        }
    }

    private func captureAndSwipe() {
        let previousContent = bookPages[currentPageIndex].content

        // Screenshot capture
        if let window = UIApplication.shared.connectedScenes.first as? UIWindowScene,
           let screenshot = window.windows.first?.rootViewController?.view.screenshot() {
            screenshotManager.saveScreenshot(screenshot)
            screenshotCount += 1
        }

        // Swipe after short delay
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
            moveToNextPage()
            let newContent = bookPages[currentPageIndex].content

            // Check if content changed or reached the end
            if previousContent == newContent || currentPageIndex >= bookPages.count - 1 {
                isAutoScreenshooting = false
                showCompletionAlert = true
            } else {
                // Continue to next page
                DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
                    captureAndSwipe()
                }
            }
        }
    }

    private func moveToNextPage() {
        if swipeDirection == .right {
            if currentPageIndex < bookPages.count - 1 {
                currentPageIndex += 1
            }
        } else {
            if currentPageIndex > 0 {
                currentPageIndex -= 1
            }
        }
    }

    private func requestPhotoLibraryAccess(completion: @escaping () -> Void) {
        PHPhotoLibrary.requestAuthorization { status in
            DispatchQueue.main.async {
                completion()
            }
        }
    }

    private func resetState() {
        currentPageIndex = 0
        screenshotCount = 0
    }
}

#Preview {
    ContentView()
}
