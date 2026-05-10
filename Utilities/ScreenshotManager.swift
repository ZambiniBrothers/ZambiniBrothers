import UIKit
import Photos

struct ScreenshotManager {
    func saveScreenshot(_ image: UIImage) {
        PHPhotoLibrary.shared().performChanges({
            PHAssetChangeRequest.creationRequestForAsset(from: image)
        }) { success, error in
            if !success {
                print("Failed to save screenshot: \(error?.localizedDescription ?? "Unknown error")")
            }
        }
    }
}
