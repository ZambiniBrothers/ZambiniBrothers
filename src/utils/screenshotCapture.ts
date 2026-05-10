import html2canvas from 'html2canvas';
import { jsPDF } from 'jspdf';
import Tesseract from 'tesseract.js';

export async function captureScreenshotAsBlob(element: HTMLElement): Promise<Blob> {
  return new Promise((resolve, reject) => {
    html2canvas(element, {
      allowTaint: true,
      useCORS: true,
      backgroundColor: '#ffffff',
      scale: 2,
    })
      .then((canvas) => {
        canvas.toBlob((blob) => {
          if (blob) {
            resolve(blob);
          } else {
            reject(new Error('Failed to create blob from canvas'));
          }
        }, 'image/png');
      })
      .catch(reject);
  });
}

export async function extractTextFromImage(imageBlob: Blob): Promise<string> {
  try {
    const reader = new FileReader();
    return new Promise((resolve, reject) => {
      reader.onload = async (e) => {
        const imageData = e.target?.result as string;
        try {
          const result = await Tesseract.recognize(imageData, 'jpn+eng', {
            logger: (m) => {
              console.log('OCR Progress:', m);
            },
          });
          resolve(result.data.text);
        } catch (error) {
          reject(error);
        }
      };
      reader.onerror = () => reject(new Error('Failed to read file'));
      reader.readAsDataURL(imageBlob);
    });
  } catch (error) {
    console.error('OCR Error:', error);
    throw error;
  }
}

export async function generatePDF(
  texts: string[],
  filename: string
): Promise<void> {
  try {
    const pdf = new jsPDF({
      orientation: 'portrait',
      unit: 'mm',
      format: 'a4',
    });

    const pageWidth = pdf.internal.pageSize.getWidth();
    const pageHeight = pdf.internal.pageSize.getHeight();
    const margin = 10;
    const maxWidth = pageWidth - 2 * margin;

    // Set font
    pdf.setFont('NotoSerifJP', 'normal');
    pdf.setFontSize(11);

    texts.forEach((text, pageIndex) => {
      if (pageIndex > 0) {
        pdf.addPage();
      }

      const lines = pdf.splitTextToSize(text, maxWidth);
      let yPosition = margin;
      const lineHeight = 6;

      lines.forEach((line: string) => {
        if (yPosition > pageHeight - margin) {
          pdf.addPage();
          yPosition = margin;
        }
        pdf.text(line, margin, yPosition);
        yPosition += lineHeight;
      });
    });

    pdf.save(filename);
  } catch (error) {
    console.error('PDF Generation Error:', error);
    throw error;
  }
}
