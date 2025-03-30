
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import json
import uvicorn
from dotenv import load_dotenv

# Import our Python modules
# These imports assume your Python files are in the same directory
# Adjust imports based on your actual file structure
try:
    from text_extractor import extract_text_from_pdf
    from qna_extractor import generate_qna_pairs
    from comparator import compare_answers
except ImportError as e:
    print(f"Error importing Python modules: {e}")
    print("Make sure text_extractor.py, qna_extractor.py, and comparator.py are in the same directory")
    # Create placeholder functions for development if imports fail
    def extract_text_from_pdf(file_path):
        return "Sample extracted text for development"
    
    def generate_qna_pairs(text, teacher_remarks=""):
        return [
            {"question": "Sample Question 1?", "answer": "Sample Answer 1"},
            {"question": "Sample Question 2?", "answer": "Sample Answer 2"}
        ]
    
    def compare_answers(student_answer, ai_answer):
        return {
            "similarity": 85,
            "feedback": "This is sample feedback",
            "suggestedScore": 8.5
        }

# Load environment variables
load_dotenv()

app = FastAPI(title="AI Test System Backend")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class QnAPair(BaseModel):
    question: str
    answer: str

class TestAnalysis(BaseModel):
    studentAnswer: str
    aiAnswer: str
    similarity: float
    feedback: str
    suggestedScore: float

class TestResult(BaseModel):
    questionId: int
    questionText: str
    studentAnswer: str
    analysis: TestAnalysis
    marks: float
    totalMarks: float

class QnARequest(BaseModel):
    text: str
    teacherRemark: Optional[str] = ""

class CompareRequest(BaseModel):
    studentAnswers: List[Dict[str, str]]
    aiAnswers: List[Dict[str, str]]
    testId: str
    studentId: str

@app.get("/")
def read_root():
    return {"message": "AI Test System Backend API"}

@app.post("/api/extract-text")
async def extract_text(file: UploadFile = File(...)):
    """Extract text from an uploaded PDF file"""
    try:
        # Save the uploaded file temporarily
        temp_file_path = f"temp_{file.filename}"
        with open(temp_file_path, "wb") as temp_file:
            content = await file.read()
            temp_file.write(content)
        
        # Extract text from the PDF
        extracted_text = extract_text_from_pdf(temp_file_path)
        
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        
        return {"success": True, "text": extracted_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting text: {str(e)}")

@app.post("/api/generate-qna")
async def generate_qna(request: QnARequest):
    """Generate Q&A pairs from text"""
    try:
        qna_pairs = generate_qna_pairs(request.text, request.teacherRemark)
        return {"success": True, "qnaPairs": qna_pairs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating Q&A pairs: {str(e)}")

@app.post("/api/compare-answers")
async def compare_student_answers(request: CompareRequest):
    """Compare student answers with AI answers"""
    try:
        results = []
        
        for i, (student_item, ai_item) in enumerate(zip(request.studentAnswers, request.aiAnswers)):
            student_answer = student_item.get("answer", "")
            ai_answer = ai_item.get("answer", "")
            question_text = student_item.get("question", "")
            
            # Compare the answers
            analysis = compare_answers(student_answer, ai_answer)
            
            # Create a test result
            result = TestResult(
                questionId=i + 1,
                questionText=question_text,
                studentAnswer=student_answer,
                analysis=TestAnalysis(
                    studentAnswer=student_answer,
                    aiAnswer=ai_answer,
                    similarity=analysis["similarity"],
                    feedback=analysis["feedback"],
                    suggestedScore=analysis["suggestedScore"]
                ),
                marks=analysis["suggestedScore"],
                totalMarks=10  # Assuming total marks is 10 for each question
            )
            results.append(result.dict())
        
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error comparing answers: {str(e)}")

@app.post("/api/save-qna")
async def save_qna(qna_pairs: List[QnAPair], subject_id: str = Form(...)):
    """Save Q&A pairs for a subject"""
    try:
        # In a production environment, you would save to a database
        # For this example, we'll simulate saving to a JSON file
        file_path = f"data/{subject_id}_qna.json"
        
        # Create data directory if it doesn't exist
        os.makedirs("data", exist_ok=True)
        
        with open(file_path, "w") as f:
            json.dump([pair.dict() for pair in qna_pairs], f)
        
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving Q&A pairs: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
