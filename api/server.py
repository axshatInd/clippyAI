from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import google.generativeai as genai
from typing import List, Optional, Dict

# ✅ Load environment variables
load_dotenv()

# ✅ Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = FastAPI()

class CodeInput(BaseModel):
    code: str
    session_id: Optional[str] = None
    is_followup: bool = False
    conversation_context: Optional[List[Dict[str, str]]] = None

def is_programming_question(text):
    """Detect if the text is a programming question or code snippet."""
    # Remove "Additional Context:" part for detection
    main_text = text.split("Additional Context:")[0] if "Additional Context:" in text else text
    
    # Keywords that indicate a programming question
    question_keywords = [
        "explain", "how", "what", "why", "solve", "implement", "algorithm", 
        "data structure", "leetcode", "problem", "challenge", "task", 
        "function", "write", "return", "input", "output", "constraints", 
        "example", "given", "find", "determine", "calculate", "optimize",
        "time complexity", "space complexity", "array", "string", "tree",
        "graph", "dynamic programming", "greedy", "binary search", "sort",
        "medium", "hard", "easy", "difficulty", "solution", "approach"
    ]
    
    # Question indicators
    question_indicators = [
        "?", "given:", "input:", "output:", "example:", "constraint", 
        "note:", "follow up:", "can you", "write a", "implement a",
        "design a", "create a", "build a"
    ]
    
    text_lower = main_text.lower()
    
    # Check for question marks or indicators
    for indicator in question_indicators:
        if indicator in text_lower:
            return True
    
    # Check for question keywords
    keyword_count = sum(1 for keyword in question_keywords if keyword in text_lower)
    
    # If multiple keywords found, likely a question
    if keyword_count >= 2:
        return True
    
    # Check if it looks like code (has common code patterns)
    code_patterns = ["def ", "class ", "import ", "from ", "=", "{", "}", ";", "//", "/*"]
    code_pattern_count = sum(1 for pattern in code_patterns if pattern in main_text)
    
    # If has many code patterns and few question keywords, likely code
    if code_pattern_count >= 3 and keyword_count < 2:
        return False
    
    # Default: if has question keywords, treat as question
    return keyword_count > 0

def handle_conversation(model, input: CodeInput):
    """Handle follow-up conversation with context"""
    
    # Build conversation prompt with full context
    conversation_prompt = """
You are ClippyAI, an expert coding assistant. You're having an ongoing conversation about code.

Previous conversation context:
"""
    
    for msg in input.conversation_context:
        conversation_prompt += f"\n{msg['role'].title()}: {msg['content']}"
    
    conversation_prompt += f"\n\nUser: {input.code}"
    conversation_prompt += """

Respond naturally to continue the conversation. If the user is reporting an error:
1. Analyze the error carefully
2. Provide a corrected solution with proper formatting
3. Explain what was wrong and why

If they're asking for improvements or alternatives:
1. Suggest better approaches
2. Explain trade-offs
3. Provide optimized code

If they're asking questions about the code:
1. Provide clear explanations
2. Use examples when helpful
3. Break down complex concepts

Keep your response conversational, helpful, and well-formatted with code blocks when needed.
"""
    
    response = model.generate_content(conversation_prompt)
    result = response.text.strip()
    
    return {
        "explanation": "",  # Empty for chat mode
        "fixes": "",       # Empty for chat mode  
        "chat_response": result,
        "session_id": input.session_id
    }

def handle_initial_analysis(model, input: CodeInput):
    """Handle initial code analysis (existing logic)"""
    
    if is_programming_question(input.code):
        # Handle programming question
        prompt = f"""
        You are a coding assistant helping with programming problems. Analyze this programming question:

        {input.code}

        Provide a comprehensive response with two parts:

        PART 1 - EXPLANATION:
        1. Explain the problem clearly and what it's asking for
        2. Discuss the theory, concepts, and algorithms involved
        3. Mention the optimal approach and time/space complexity
        4. Explain any edge cases to consider

        PART 2 - SOLUTION:
        1. Provide the most optimized solution in Python (or the language specified in the question)
        2. Include proper comments explaining the logic
        3. Handle all edge cases mentioned or implied
        4. Ensure the solution covers all requirements
        5. If multiple approaches exist, provide the most efficient one
        """

        response = model.generate_content(prompt)
        result = response.text.strip()

        # Split response into explanation and solution parts
        if "PART 2" in result:
            parts = result.split("PART 2", 1)
            explanation = parts[0].replace("PART 1 - EXPLANATION:", "").strip()
            solution = "SOLUTION:\n" + parts[1].replace("- SOLUTION:", "").strip()
        else:
            # Fallback splitting method
            lines = result.split('\n')
            mid_point = len(lines) // 2
            explanation = '\n'.join(lines[:mid_point])
            solution = '\n'.join(lines[mid_point:])

        return {
            "explanation": explanation,
            "fixes": solution,
            "session_id": input.session_id
        }

    else:
        # Handle code snippet (original logic)
        prompt = f"""
        You are a coding assistant. Analyze the following code:

        {input.code}

        Provide a comprehensive response with two parts:

        PART 1 - CODE EXPLANATION:
        1. Explain what the code does overall
        2. Describe the purpose and functionality
        3. Mention the programming concepts used

        PART 2 - LINE-BY-LINE ANALYSIS:
        1. Go through the code line by line
        2. For each significant line, mention the line in **bold** followed by explanation
        3. Highlight any syntax or logical errors
        4. Suggest improvements or optimizations if needed
        5. Point out best practices or potential issues
        """

        response = model.generate_content(prompt)
        result = response.text.strip()

        # Split response into explanation and analysis parts
        if "PART 2" in result:
            parts = result.split("PART 2", 1)
            explanation = parts[0].replace("PART 1 - CODE EXPLANATION:", "").strip()
            analysis = "LINE-BY-LINE ANALYSIS:\n" + parts[1].replace("- LINE-BY-LINE ANALYSIS:", "").strip()
        else:
            # Fallback: look for common separators
            if "line by line" in result.lower():
                parts = result.split("line by line", 1)
                explanation = parts[0].strip()
                analysis = "Line by line analysis:\n" + parts[1].strip()
            else:
                # Default split
                lines = result.split('\n')
                mid_point = len(lines) // 2
                explanation = '\n'.join(lines[:mid_point])
                analysis = '\n'.join(lines[mid_point:])

        return {
            "explanation": explanation,
            "fixes": analysis,
            "session_id": input.session_id
        }

@app.post("/analyze")
def analyze_code(input: CodeInput):
    try:
        model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")
        
        if input.is_followup and input.conversation_context:
            # Handle follow-up conversation
            return handle_conversation(model, input)
        else:
            # Handle initial analysis
            return handle_initial_analysis(model, input)
    
    except Exception as e:
        return {
            "explanation": "Failed to get response from Gemini.",
            "fixes": str(e),
            "chat_response": f"Error: {str(e)}"
        }

@app.post("/chat")
def chat_endpoint(input: CodeInput):
    """Dedicated chat endpoint for follow-up conversations"""
    try:
        model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")
        return handle_conversation(model, input)
    except Exception as e:
        return {
            "explanation": "",
            "fixes": "",
            "chat_response": f"Error: {str(e)}"
        }

# ✅ Allow server to run when started directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.server:app", host="127.0.0.1", port=8000, log_level="error")
