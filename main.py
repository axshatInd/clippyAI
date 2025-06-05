import sys
import pyperclip
import requests
import markdown
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from ui.window import FloatingWindow
from ui.prompt import PromptWindow

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

            # ✅ Get current HTML style based on theme
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
    app = QApplication(sys.argv)
    window = FloatingWindow()
    watcher = ClipboardWatcher(window)
    sys.exit(app.exec_())
