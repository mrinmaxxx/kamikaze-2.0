import streamlit as st
import json
import ollama
import tempfile

def load_qna(file, key):
    try:
        content = file.getvalue().decode("utf-8")  # Convert bytes to string
        data = json.loads(content)  # Parse JSON
        if isinstance(data, list) and all(isinstance(entry, dict) for entry in data):
            return data
        else:
            st.error(f"Invalid JSON format in {key}. Expected a list of dictionaries.")
            return None
    except (json.JSONDecodeError, UnicodeDecodeError):
        st.error(f"Invalid JSON file format in {key}.")
        return None

def evaluate_answer(question, ai_answer, student_answer, key):
    prompt = f"""
    Evaluate the student's answer compared to the AI-provided answer.
    Provide:
    1. Accuracy (0-10)
    2. Context Understanding (0-10)
    3. Relevance (0-10)
    4. Completeness (0-10)
    5. Coherence & Grammar (0-10)
    6. Overall Score (0-10)
    7. Whether Rote Learning is being practiced or not.
    7. How the student can improve.
    If **all the scores are 10/10** then also warn that **the student might be practicing route learning**.

    Question: {question}
    AI Answer: {ai_answer}
    Student Answer: {student_answer}

    Response format:
    {{
        "accuracy": <value>,
        "context": <value>,
        "relevance": <value>,
        "completeness": <value>,
        "coherence": <value>,
        "overall_score": <value>,
        "rote_learning": "<text>",
        "improvement_suggestions": "<text>"
    }}
    """
    response = ollama.chat(model="mistral", messages=[{"role": "user", "content": prompt}])
    
    try:
        result = json.loads(response['message']['content'])
    except (json.JSONDecodeError, KeyError):
        result = {
            "accuracy": 0,
            "context": 0,
            "relevance": 0,
            "completeness": 0,
            "coherence": 0,
            "overall_score": 0,
            "rote_learning": "none",
            "improvement_suggestions": "Could not process response."
        }
    return result

def evaluate_qna(ai_qna, student_qna):
    evaluation_results = []
    for index, (ai_entry, student_entry) in enumerate(zip(ai_qna, student_qna)):
        if ai_entry.get("question") != student_entry.get("question"):
            st.warning(f"Mismatched question detected: {ai_entry.get('question')}")
            continue
        
        question = ai_entry["question"]
        ai_answer = ai_entry["answer"]
        student_answer = student_entry["answer"]
        evaluation = evaluate_answer(question, ai_answer, student_answer, key=f"evaluation_{index}")
        evaluation["question"] = question
        evaluation["student_answer"] = student_answer
        evaluation["ai_answer"] = ai_answer
        evaluation_results.append(evaluation)
    return evaluation_results


st.title("QnA Answer Evaluator")
st.write("Upload two JSON files: One with AI-generated answers and another with student answers.")


ai_file = st.file_uploader("Upload AI-generated QnA JSON", type=["json"], key="ai_file")
student_file = st.file_uploader("Upload Student QnA JSON", type=["json"], key="student_file")

if ai_file and student_file:
    ai_qna = load_qna(ai_file, "AI QnA File")
    student_qna = load_qna(student_file, "Student QnA File")
    
    if ai_qna and student_qna:
        if st.button("Run Evaluation", key="run_evaluation"):
            with st.spinner("Evaluating answers..."):
                results = evaluate_qna(ai_qna, student_qna)

               
                with tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w", encoding="utf-8") as temp_file:
                    json.dump(results, temp_file, indent=4)  # Write as string
                    temp_filename = temp_file.name
                
                st.success("Evaluation completed!")

               
                for i, result in enumerate(results):
                    with st.expander(f"Question {i+1}: {result['question']}"):
                        st.write(f"**AI Answer:** {result['ai_answer']}")
                        st.write(f"**Student Answer:** {result['student_answer']}")
                        st.write(f"**Accuracy:** {result['accuracy']}/10")
                        st.write(f"**Context Understanding:** {result['context']}/10")
                        st.write(f"**Relevance:** {result['relevance']}/10")
                        st.write(f"**Completeness:** {result['completeness']}/10")
                        st.write(f"**Coherence & Grammar:** {result['coherence']}/10")
                        st.write(f"**Overall Score:** {result['overall_score']}/10")
                        st.write(f"**Rote Learning:** {result['rote_learning']}")
                        st.write(f"**Improvement Suggestions:** {result['improvement_suggestions']}")


                st.download_button(
                    label="Download Evaluation JSON",
                    data=json.dumps(results, indent=4).encode("utf-8"),  # Encode before download
                    file_name="evaluation_results.json",
                    mime="application/json",
                    key="download_button"
                )
