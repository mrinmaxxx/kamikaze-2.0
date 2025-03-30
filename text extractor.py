from PyPDF2 import PdfReader
import pytesseract
from pdf2image import convert_from_path

def extract_text_from_pdf(pdf_path):
    text = ""
    reader = PdfReader(pdf_path)  # EnsACure PyPDF2 is properly installed

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    if not text:  # If no text is extracted, use OCR
        images = convert_from_path(pdf_path)
        for img in images:
            text += pytesseract.image_to_string(img) + "\n"
            
    return text

if __name__ == "__main__":
    pdf_path = input("Enter the path of the PDF file: ")
    extracted_text = extract_text_from_pdf(pdf_path)
    with open("notes.txt", "w", encoding="utf-8") as file:
        file.write(extracted_text)
    print("Extracted text saved to notes.txt")
