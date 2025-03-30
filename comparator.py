
"""
Answer comparison module for the AI Test System.
This module handles comparing student answers with AI answers.
"""

import os
from typing import Dict, Any
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI API if available
openai.api_key = os.getenv("OPENAI_API_KEY")

def compare_answers(student_answer: str, ai_answer: str) -> Dict[str, Any]:
    """
    Compare a student's answer with the AI-generated answer.
    
    Args:
        student_answer: The student's answer
        ai_answer: The AI-generated correct answer
        
    Returns:
        Dictionary containing similarity score, feedback, and suggested score
    """
    if not student_answer or not ai_answer:
        return {
            "similarity": 0,
            "feedback": "No answer provided.",
            "suggestedScore": 0
        }
    
    # Check if OpenAI API key is available
    if not os.getenv("OPENAI_API_KEY"):
        # Return mock data if no API key is available
        import random
        similarity = round(random.uniform(60, 95), 1)
        return {
            "similarity": similarity,
            "feedback": f"This is sample feedback for development purposes. Similarity score: {similarity}%",
            "suggestedScore": round(similarity / 10, 1)
        }
    
    try:
        # Prepare the prompt for comparison
        prompt = f"""
        I need to compare a student's answer with a correct answer and evaluate it.
        
        Correct answer: "{ai_answer}"
        
        Student answer: "{student_answer}"
        
        Please analyze how accurate the student's answer is compared to the correct answer.
        Consider key concepts, factual accuracy, completeness, and clarity.
        
        Provide:
        1. A similarity percentage (0-100)
        2. Constructive feedback explaining what was good and what could be improved
        3. A suggested score out of 10
        
        Format your response as a JSON object with keys: "similarity", "feedback", and "suggestedScore".
        """
        
        # Call OpenAI API
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an educational assessment AI that evaluates student answers."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        # Parse the response
        response_text = response.choices[0].message.content.strip()
        
        # Extract the JSON part
        import json
        import re
        
        # Find anything that looks like a JSON object
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        
        if json_match:
            try:
                result = json.loads(json_match.group())
                # Ensure all required fields are present
                if "similarity" not in result:
                    result["similarity"] = 70.0
                if "feedback" not in result:
                    result["feedback"] = "The answer covers some key points but could be more detailed."
                if "suggestedScore" not in result:
                    result["suggestedScore"] = 7.0
                
                return result
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return {
                    "similarity": 50.0,
                    "feedback": "Unable to precisely evaluate the answer. The response contains relevant information but a detailed assessment couldn't be generated.",
                    "suggestedScore": 5.0
                }
        else:
            # Fallback if no JSON-like structure is found
            return {
                "similarity": 60.0,
                "feedback": "The system was unable to generate a structured evaluation. Consider manual review.",
                "suggestedScore": 6.0
            }
            
    except Exception as e:
        print(f"Error comparing answers: {e}")
        # Return a default response in case of error
        return {
            "similarity": 0.0,
            "feedback": f"Error occurred during evaluation: {str(e)}",
            "suggestedScore": 0.0
        }

def batch_compare_answers(student_answers, ai_answers):
    """
    Compare multiple student answers with AI answers in batch.
    
    Args:
        student_answers: List of student answers
        ai_answers: List of AI-generated correct answers
        
    Returns:
        List of comparison results
    """
    results = []
    
    for student_answer, ai_answer in zip(student_answers, ai_answers):
        result = compare_answers(student_answer, ai_answer)
        results.append(result)
        
    return results
