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

# ✅ Handle bundled vs development paths
def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Load environment variables
load_dotenv(get_resource_path('.env'))

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
            res = requests.post(API_URL, json={"code": code})
            data = res.json()
            explanation_md = data.get("explanation", "No explanation returned.")
            fixes_md = data.get("fixes", "No fixes returned.")

            theme_style = self.window.current_theme_style()
            explanation_html = theme_style + markdown.markdown(explanation_md, extensions=["fenced_code"])
            fixes_html = theme_style + markdown.markdown(fixes_md, extensions=["fenced_code"])

            self.window.update_content(explanation_html, fixes_html)
            self.window.show()

        except Exception as e:
            error_html = f"<b>Error contacting API.</b><br><pre>{str(e)}</pre>"
            self.window.update_content(error_html, "")
            self.window.show()

def start_server():
    """Start the FastAPI server in a separate thread"""
    try:
        import uvicorn
        from api.server import app
        uvicorn.run(app, host="127.0.0.1", port=8000, log_level="error")
    except Exception as e:
        print(f"Server failed to start: {e}")

if __name__ == "__main__":
    # ✅ Start FastAPI server in background thread (PyInstaller compatible)
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Wait a bit to ensure server is ready
    time.sleep(3)
    
    try:
        app = QApplication(sys.argv)
        window = FloatingWindow()
        watcher = ClipboardWatcher(window)
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Application error: {e}")
        # Only show input prompt if running in console mode
        if hasattr(sys, '_getframe'):
            input("Press Enter to exit...")
