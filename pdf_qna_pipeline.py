import streamlit as st
import json
import os
from PyPDF2 import PdfReader
import pytesseract
from pdf2image import convert_from_path
import ollama

def extract_text_from_pdf(pdf_path):
    text = ""
    reader = PdfReader(pdf_path)
    
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    
    if not text:
        images = convert_from_path(pdf_path)
        for img in images:
            text += pytesseract.image_to_string(img) + "\n"
    
    return text

def generate_qna(text, teacher_remark, n_easy, n_medium, n_hard, n_let_ai_decide, iteration):
    prompt = f"""
    You are an AI that extracts **all possible** question-answer pairs from a given text.
    This is **Iteration {iteration}/3**, ensure that:
    - Try to give some creative questions which include practical applications.
    - Make the questions concept based and not directly answerable
    - You focus on missed details from previous runs.
    - Questions cover every key aspect of the text.
    - Answers are **concise yet accurate**.
    - Based on the answers, tag each question as **easy, medium, or hard** in a 'difficulty' field.
    - Output must be a **list of dictionaries** with 'question' and 'answer' keys.
    
    Text: {text}
    
    Additional Instructions from Teacher: {teacher_remark}
    Number of Questions based on difficulty level: Easy: {n_easy}, Medium: {n_medium}, Hard: {n_hard}, AI Decides: {n_let_ai_decide}
    
    Provide the output in JSON format like:
    [
        {{"question": "Q1. What is ...? [difficulty level]", "answer": "It is ..."}},
        {{"question": "Q2. How does ... work? [difficulty level]", "answer": "It works by ..."}}
    ]
    """
    try:
        response = ollama.chat(model='mistral', messages=[{"role": "user", "content": prompt}])
        qna_data = json.loads(response['message']['content'])
        return qna_data if isinstance(qna_data, list) else []
    except Exception as e:
        st.error(f"Error generating Q&A: {e}")
        return []

def remove_duplicates(qna_list):
    seen = set()
    unique_qna = []
    for entry in qna_list:
        q = entry.get("question", "").strip().lower()
        if q and q not in seen:
            seen.add(q)
            unique_qna.append(entry)
    return unique_qna

def save_qna_to_json(qna_data, output_path):
    try:
        with open(output_path, 'w', encoding='utf-8') as json_file:
            json.dump(qna_data, json_file, indent=4, ensure_ascii=False)
    except Exception as e:
        st.error(f"Error saving JSON file: {e}")

def main():
    st.title("📄 PDF to Q&A Generator")
    
    uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])
    teacher_remark = st.text_area("Teacher's Remarks (Optional)")
    
    user_preference = st.radio("Do you want to specify difficulty levels?", ("No", "Yes"))
    
    if user_preference == "Yes":
        n_easy = st.text_area("Number of Easy Questions")
        n_medium = st.text_area("Number of Medium Questions")
        n_hard = st.text_area("Number of Hard Questions")
        n_let_ai_decide = st.text_area("Number of 'Let AI Decide' Questions")
    else:
        n_easy, n_medium, n_hard, n_let_ai_decide = "No Preference", "No Preference", "No Preference", "No Preference"
    
    run_button = st.button("Run")
    
    if uploaded_file and run_button:
        with st.spinner("Processing PDF..."):
            pdf_path = f"temp_{uploaded_file.name}"
            with open(pdf_path, "wb") as f:
                f.write(uploaded_file.read())
            
            text = extract_text_from_pdf(pdf_path)
            if not text.strip():
                st.error("No text could be extracted from the PDF.")
                return
            
            output_file = os.path.splitext(pdf_path)[0] + "_qna.json"
            all_qna = []
            
            for iteration in range(1, 4):
                st.write(f"🔄 Running Iteration {iteration}/3...")
                qna_data = generate_qna(text, teacher_remark, n_easy, n_medium, n_hard, n_let_ai_decide, iteration)
                all_qna.extend(qna_data)
            
            final_qna = remove_duplicates(all_qna)
            save_qna_to_json(final_qna, output_file)
            
            st.success(f"✅ Q&A extraction complete! {len(final_qna)} pairs generated.")
            st.download_button("Download Q&A JSON", data=json.dumps(final_qna, indent=4), file_name="QnA.json", mime="application/json")
            
            os.remove(pdf_path)  

if __name__ == "__main__":
    main()
