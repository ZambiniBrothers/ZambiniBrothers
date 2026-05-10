import html2canvas from 'html2canvas';

export async function captureScreenshot(element: HTMLElement, pageNumber: number): Promise<void> {
  try {
    const canvas = await html2canvas(element, {
      allowTaint: true,
      useCORS: true,
      backgroundColor: '#ffffff',
      scale: 2, // Higher quality
    });

    // Convert canvas to blob and download
    canvas.toBlob((blob) => {
      if (blob) {
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `book-screenshot-${String(pageNumber).padStart(3, '0')}.png`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
      }
    }, 'image/png');
  } catch (error) {
    console.error('Failed to capture screenshot:', error);
  }
}
