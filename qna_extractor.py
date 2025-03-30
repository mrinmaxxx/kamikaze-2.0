
"""
Q&A extraction module for the AI Test System.
This module handles generating questions and answers from extracted text.
"""

import os
from typing import List, Dict, Any
from dotenv import load_dotenv
import openai
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Load environment variables
load_dotenv()

# Initialize OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY")

def split_text(text: str, chunk_size: int = 2000) -> List[str]:
    """
    Split text into smaller chunks for processing.
    
    Args:
        text: Text to split
        chunk_size: Maximum size of each chunk
        
    Returns:
        List of text chunks
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=200,
        length_function=len,
    )
    
    return text_splitter.split_text(text)

def generate_qna_pairs(text: str, teacher_remarks: str = "", num_questions: int = 10) -> List[Dict[str, str]]:
    """
    Generate question-answer pairs from the provided text.
    
    Args:
        text: Text to generate questions and answers from
        teacher_remarks: Additional guidance from the teacher
        num_questions: Number of questions to generate
        
    Returns:
        List of dictionaries containing questions and answers
    """
    if not text:
        return []
    
    if not os.getenv("OPENAI_API_KEY"):
        # Return sample data if no API key is available
        return [
            {"question": "What is the law of conservation of energy?", 
             "answer": "The law of conservation of energy states that energy cannot be created or destroyed, only transformed from one form to another."},
            {"question": "Define Newton's First Law of Motion.", 
             "answer": "Newton's First Law of Motion states that an object at rest stays at rest and an object in motion stays in motion with the same speed and direction unless acted upon by an unbalanced force."}
        ]
    
    try:
        # Split text into chunks if it's too long
        chunks = split_text(text) if len(text) > 4000 else [text]
        
        all_qna_pairs = []
        questions_per_chunk = max(1, num_questions // len(chunks))
        
        for chunk in chunks:
            # Prepare the prompt
            prompt = f"""
            Based on the following text, generate {questions_per_chunk} question-answer pairs that would be suitable for a test.
            
            TEXT:
            {chunk}
            
            TEACHER REMARKS:
            {teacher_remarks}
            
            Each question should test understanding of key concepts. Provide detailed answers.
            Format your response as a JSON array with 'question' and 'answer' fields for each pair.
            Example: [{{"question": "What is X?", "answer": "X is Y."}}]
            """
            
            # Call OpenAI API
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an AI assistant that generates educational test questions and answers."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            # Parse the response
            response_text = response.choices[0].message.content.strip()
            
            # Extract the JSON part (assuming the AI might add extra text)
            import json
            import re
            
            # Find anything that looks like a JSON array
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            
            if json_match:
                try:
                    qna_pairs = json.loads(json_match.group())
                    all_qna_pairs.extend(qna_pairs)
                except json.JSONDecodeError:
                    # If JSON parsing fails, use a basic fallback
                    all_qna_pairs.append({
                        "question": "Error parsing generated questions. How would you improve this system?",
                        "answer": "The system could be improved by enhancing the Q&A generation algorithm and implementing better error handling."
                    })
            else:
                # Fallback if no JSON-like structure is found
                all_qna_pairs.append({
                    "question": "No structured Q&A could be generated. What might be a key concept from the text?",
                    "answer": "Please review the text manually to identify key concepts as the automated extraction was unsuccessful."
                })
                
        return all_qna_pairs[:num_questions]  # Limit to requested number of questions
        
    except Exception as e:
        print(f"Error generating Q&A pairs: {e}")
        # Return a fallback Q&A pair in case of error
        return [
            {"question": f"Error occurred while generating questions. What could be improved?",
             "answer": f"The system encountered an error: {str(e)}. It could be improved with better error handling and fallback mechanisms."}
        ]
