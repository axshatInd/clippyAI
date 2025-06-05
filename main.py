# main.py
import sys
import pyperclip
import requests
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from ui.window import FloatingWindow

API_URL = "http://127.0.0.1:8000/analyze"

class ClipboardWatcher:
    def __init__(self, window):
        self.window = window
        self.last_clipboard = ""

        self.timer = QTimer()
        self.timer.setInterval(1000)  # check every 1 second
        self.timer.timeout.connect(self.check_clipboard)
        self.timer.start()

    def check_clipboard(self):
        current = pyperclip.paste()
        if current != self.last_clipboard and current.strip():
            self.last_clipboard = current
            self.analyze_code(current)

    def analyze_code(self, code):
        try:
            res = requests.post(API_URL, json={"code": code})
            data = res.json()
            explanation = data.get("explanation", "No explanation returned.")
            fixes = data.get("fixes", "No fixes returned.")
            self.window.update_content(explanation, fixes)
        except Exception as e:
            self.window.update_content("Error contacting API.", str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FloatingWindow()
    watcher = ClipboardWatcher(window)
    sys.exit(app.exec_())
