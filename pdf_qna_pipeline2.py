import streamlit as st
import PyPDF2
import google.generativeai as genai
from io import BytesIO
from fpdf import FPDF
import re

# Set up Gemini API Key
genai.configure(api_key="AIzaSyAGExpenqm4KlM03dqblF4K0G0eG35ISUg")

def extract_text_from_pdf(pdf_file):
    text = ""
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    for page in pdf_reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += re.sub(r'[^\x00-\x7F]+', ' ', page_text) + "\n"  # Remove non-ASCII characters
    return text

def generate_questions(text, remarks):
    model = genai.GenerativeModel("gemini-1.5-flash")  # Use free-tier compatible model
    prompt = ("Generate a list of questions and answer pairs based on the given content. "
              "Format each question as '_questionnumber. question [level]\n Answer: answer'. "
              "Ensure proper numbering and include difficulty levels like [Easy], [Medium], or [Hard]. "
              f"{remarks}\n{text}")
    response = model.generate_content(prompt, stream=False)  # Ensure compatibility with free-tier
    return response.text if hasattr(response, 'text') else "No response received."

def create_pdf(document_title, content):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Times", style='B', size=16)
    pdf.cell(200, 10, document_title, ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Times", size=12)
    for line in content.split('\n'):
        pdf.multi_cell(0, 10, line)
    
    pdf_output = pdf.output(dest='S').encode('latin1')  # Get PDF output as bytes
    return BytesIO(pdf_output)  # Convert to BytesIO for Streamlit download

def main():
    st.title("PDF-based Question Generator using Gemini API (Free Tier)")
    
    uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])
    document_title = st.text_input("Enter Document Title", "Generated QnA")
    additional_remarks = st.text_area("Additional Remarks (optional)", "")
    
    if uploaded_file is not None:
        with st.spinner("Extracting text from PDF..."):
            text = extract_text_from_pdf(uploaded_file)
        
        # Provide a button to download extracted text
        text_file = BytesIO(text.encode("utf-8"))
        st.download_button(label="Download Extracted Text", 
                           data=text_file, 
                           file_name="extracted_text.txt", 
                           mime="text/plain")
        
        if st.button("Generate Questions"):
            with st.spinner("Generating questions..."):
                questions = generate_questions(text, additional_remarks)
                st.subheader("Generated Questions:")
                st.write(questions)
                
                # Provide a button to download generated QnA pairs as PDF
                pdf_file = create_pdf(document_title, questions)
                st.download_button(label="Download Generated QnA", 
                                   data=pdf_file, 
                                   file_name="generated_qna.pdf", 
                                   mime="application/pdf")

if __name__ == "__main__":
    main()