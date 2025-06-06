import sys
import os
import pyperclip
import requests
import markdown
import threading
import time
from dotenv import load_dotenv
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from ui.window import FloatingWindow
from ui.prompt import PromptWindow

# ✅ Enhanced environment loading with debugging
def load_env_file():
    """Load .env file from the correct location"""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable - look next to .exe file
        exe_dir = os.path.dirname(sys.executable)
        env_path = os.path.join(exe_dir, '.env')
    else:
        # Running in development
        env_path = '.env'
    
    print(f"🔍 Looking for .env at: {env_path}")
    print(f"🔍 .env file exists: {os.path.exists(env_path)}")
    
    if os.path.exists(env_path):
        try:
            with open(env_path, 'r') as f:
                content = f.read()
                print(f"🔍 .env content preview: {content[:50]}...")
        except Exception as e:
            print(f"❌ Error reading .env file: {e}")
    
    load_dotenv(env_path)

# Load environment variables
load_env_file()

API_URL = "http://127.0.0.1:8000/analyze"

# ✅ Theme-specific HTML styling for code blocks
LIGHT_MODE_STYLE = """
<style>
pre {
    background-color: #f0f0f0;
    color: #000;
    padding: 10px;
    border-radius: 5px;
    overflow-x: auto;
    font-family: Consolas, monospace;
}
code {
    font-family: Consolas, monospace;
}
</style>
"""

DARK_MODE_STYLE = """
<style>
pre {
    background-color: #1e1e1e;
    color: #dcdcdc;
    padding: 10px;
    border-radius: 5px;
    overflow-x: auto;
    font-family: Consolas, monospace;
}
code {
    font-family: Consolas, monospace;
}
</style>
"""

class ClipboardWatcher:
    def __init__(self, window):
        self.window = window
        self.last_clipboard = ""

        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.check_clipboard)
        self.timer.start()

    def check_clipboard(self):
        current = pyperclip.paste()
        if current != self.last_clipboard and current.strip():
            self.last_clipboard = current
            self.ask_permission(current)

    def ask_permission(self, copied_text):
        self.prompt = PromptWindow(
            on_yes=lambda: self.analyze_code(copied_text),
            on_no=lambda: None
        )
        self.prompt.show()

    def analyze_code(self, code):
        try:
            print(f"📡 Sending request to: {API_URL}")
            res = requests.post(API_URL, json={"code": code}, timeout=30)
            print(f"✅ API Response status: {res.status_code}")
            data = res.json()
            explanation_md = data.get("explanation", "No explanation returned.")
            fixes_md = data.get("fixes", "No fixes returned.")

            theme_style = self.window.current_theme_style()
            explanation_html = theme_style + markdown.markdown(explanation_md, extensions=["fenced_code"])
            fixes_html = theme_style + markdown.markdown(fixes_md, extensions=["fenced_code"])

            self.window.update_content(explanation_html, fixes_html)
            self.window.show()

        except Exception as e:
            print(f"❌ API Error: {e}")
            error_html = f"<b>Error contacting API.</b><br><pre>{str(e)}</pre>"
            self.window.update_content(error_html, "")
            self.window.show()

def start_server():
    """Start the FastAPI server in a separate thread"""
    print("🚀 Attempting to start FastAPI server...")
    
    try:
        # Test environment variables first
        gemini_key = os.getenv("GEMINI_API_KEY")
        if not gemini_key:
            print("❌ GEMINI_API_KEY not found in environment variables!")
            print("🔍 Available environment variables:")
            for key in os.environ.keys():
                if 'GEMINI' in key.upper():
                    print(f"   {key}")
            return
        else:
            print(f"✅ GEMINI_API_KEY loaded: {gemini_key[:10]}...")
        
        # Try importing modules with detailed error reporting
        print("📦 Importing uvicorn...")
        import uvicorn
        print("✅ uvicorn imported successfully")
        
        print("📦 Importing FastAPI app...")
        
        # Add path for PyInstaller
        if getattr(sys, 'frozen', False):
            current_dir = os.path.dirname(sys.executable)
        else:
            current_dir = os.path.dirname(os.path.abspath(__file__))
        
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
            print(f"📁 Added to sys.path: {current_dir}")
        
        from api.server import app
        print("✅ FastAPI app imported successfully")
        
        print("🌐 Starting uvicorn server on 127.0.0.1:8000...")
        uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("🔍 Current sys.path:")
        for path in sys.path:
            print(f"   {path}")
    except Exception as e:
        print(f"❌ Server failed to start: {e}")
        import traceback
        traceback.print_exc()

def test_server_connection():
    """Test if server is responding"""
    max_attempts = 15
    for i in range(max_attempts):
        try:
            response = requests.get("http://127.0.0.1:8000", timeout=2)
            print("✅ Server is responding!")
            return True
        except requests.exceptions.RequestException:
            print(f"⏳ Server not ready yet... ({i+1}/{max_attempts})")
            time.sleep(1)
    
    print("❌ Server failed to start after 15 seconds")
    return False

if __name__ == "__main__":
    print("🎯 Starting ClippyAI application...")
    print(f"🐍 Python executable: {sys.executable}")
    print(f"📁 Current working directory: {os.getcwd()}")
    print(f"🔧 Running as frozen: {getattr(sys, 'frozen', False)}")
    
    # Start server thread
    print("🧵 Creating server thread...")
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Wait for server with better testing
    print("⏳ Waiting for server to start...")
    server_ready = test_server_connection()
    
    if not server_ready:
        print("⚠️ Server may not be ready, but continuing with GUI...")
    
    try:
        print("🖥️ Starting PyQt5 application...")
        app = QApplication(sys.argv)
        window = FloatingWindow()
        watcher = ClipboardWatcher(window)
        print("✅ GUI started successfully")
        sys.exit(app.exec_())
    except Exception as e:
        print(f"❌ Application error: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
