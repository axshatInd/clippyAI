from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import google.generativeai as genai

# Load API key
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = FastAPI()

class CodeInput(BaseModel):
    code: str

@app.post("/analyze")
def analyze_code(input: CodeInput):
    try:
        model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")

        prompt = f"""
        You are a coding assistant. Analyze the following code:

        {input.code}

        1. Explain what the code does.
        2. Explain the code line by line, mention the line taken from code in bold only for better visibility and understanding, explain the line ahead of it in normal text.
        3. Highlight any syntax or logical errors.
        4. Suggest fixes or improvements only if needed.
        """

        response = model.generate_content(prompt)
        result = response.text.strip()

        # Simple way to split response if it has explanation + fixes
        if "Fix" in result or "fix" in result:
            parts = result.split("\n\n", 1)
            explanation = parts[0]
            fixes = parts[1] if len(parts) > 1 else "No obvious issues."
        else:
            explanation = result
            fixes = "No obvious issues."

        return {
            "explanation": explanation,
            "fixes": fixes
        }

    except Exception as e:
        return {
            "explanation": "Failed to get response from Gemini.",
            "fixes": str(e)
        }
