
"""
Text extraction module for the AI Test System.
This module handles extracting text from PDF documents.
"""

import os
from typing import Optional, List
import PyPDF2
from docx import Document

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from a PDF file.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        Extracted text from the PDF
    """
    extracted_text = ""
    
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Extract text from each page
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                extracted_text += page.extract_text() + "\n\n"
                
        return extracted_text.strip()
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return f"Error extracting text: {str(e)}"

def extract_text_from_docx(file_path: str) -> str:
    """
    Extract text from a DOCX file.
    
    Args:
        file_path: Path to the DOCX file
        
    Returns:
        Extracted text from the DOCX
    """
    try:
        doc = Document(file_path)
        full_text = []
        
        for para in doc.paragraphs:
            full_text.append(para.text)
            
        return '\n'.join(full_text)
    except Exception as e:
        print(f"Error extracting text from DOCX: {e}")
        return f"Error extracting text: {str(e)}"

def extract_text(file_path: str) -> str:
    """
    Extract text from a document (PDF or DOCX).
    
    Args:
        file_path: Path to the document file
        
    Returns:
        Extracted text from the document
    """
    file_extension = os.path.splitext(file_path)[1].lower()
    
    if file_extension == '.pdf':
        return extract_text_from_pdf(file_path)
    elif file_extension == '.docx':
        return extract_text_from_docx(file_path)
    else:
        return f"Unsupported file format: {file_extension}"
