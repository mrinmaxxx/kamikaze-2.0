import json
import os
import ollama

def read_text_file(file_path):
    """Reads the content of the given text file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return None

def generate_qna(text, teacher_remark="", iteration=1):
    """Generates question-answer pairs using Mistral model."""
    prompt = f"""
    You are an AI that extracts **all possible** question-answer pairs from a given text.
    This is **Iteration {iteration}/3**, ensure that:
    - You focus on missed details from previous runs.
    - Questions cover every key aspect of the text.
    - Answers are **concise yet accurate**.
    - Output must be a **list of dictionaries** with 'question' and 'answer' keys.

    Text: {text}

    Additional Instructions from Teacher: {teacher_remark}

    Provide the output in JSON format like:
    [
        {{"question": "What is ...?", "answer": "It is ..."}},
        {{"question": "How does ... work?", "answer": "It works by ..."}},
        ...
    ]
    """

    try:
        response = ollama.chat(model='mistral', messages=[{"role": "user", "content": prompt}])
        qna_data = json.loads(response['message']['content'])
        return qna_data if isinstance(qna_data, list) else []
    except Exception as e:
        print(f"❌ Error generating Q&A: {e}")
        return []

def remove_duplicates(qna_list):
    """Removes duplicate question-answer pairs."""
    seen = set()
    unique_qna = []
    for entry in qna_list:
        q = entry.get("question", "").strip().lower()
        if q and q not in seen:
            seen.add(q)
            unique_qna.append(entry)
    return unique_qna

def save_qna_to_json(qna_data, file_path):
    """Saves the Q&A pairs to a JSON file (appends data from multiple iterations)."""
    json_file_path = os.path.splitext(file_path)[0] + "_qna.json"

    # Load existing data if the file exists
    if os.path.exists(json_file_path):
        try:
            with open(json_file_path, 'r', encoding='utf-8') as json_file:
                existing_data = json.load(json_file)
        except json.JSONDecodeError:
            existing_data = []
    else:
        existing_data = []

    # Merge and remove duplicates
    combined_qna = remove_duplicates(existing_data + qna_data)

    try:
        with open(json_file_path, 'w', encoding='utf-8') as json_file:
            json.dump(combined_qna, json_file, indent=4, ensure_ascii=False)
        print(f"✅ Q&A saved to: {json_file_path} (Total: {len(combined_qna)} pairs)")
    except Exception as e:
        print(f"❌ Error saving JSON file: {e}")

def main():
    file_path = input("Enter the path to the text file: ").strip()

    if not os.path.exists(file_path):
        print("❌ Error: File does not exist.")
        return
    
    text = read_text_file(file_path)
    if not text:
        print("❌ Error: Unable to read the file.")
        return

    teacher_remark = input("Enter additional instructions for the AI (Teacher Remark): ").strip()
    
    for iteration in range(1, 4):  # Run 3 iterations
        print(f"\n🔄 Running Iteration {iteration}/3...")
        qna_data = generate_qna(text, teacher_remark, iteration)
        if qna_data:
            save_qna_to_json(qna_data, file_path)
        else:
            print(f"⚠️ No new Q&A generated in iteration {iteration}.")

if __name__ == "__main__":
    main()
