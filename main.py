import sys
import os
import pyperclip
import requests
import markdown
import subprocess
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

if __name__ == "__main__":
    # ✅ Updated for PyInstaller
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        server_script = get_resource_path(os.path.join("api", "server.py"))
        server_process = subprocess.Popen(
            [sys.executable, server_script],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    else:
        # Running in development
        server_process = subprocess.Popen(
            [sys.executable, os.path.join("api", "server.py")],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    # Wait a bit to ensure server is ready
    time.sleep(2)

    try:
        app = QApplication(sys.argv)
        window = FloatingWindow()
        watcher = ClipboardWatcher(window)
        sys.exit(app.exec_())
    finally:
        # ✅ Kill server on exit
        server_process.terminate()
