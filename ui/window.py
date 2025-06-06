import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QPushButton, QHBoxLayout, QTextEdit, QSizeGrip, QSplitter
)
from PyQt5.QtCore import Qt
# Add this import at the top
from api_key_manager import APIKeyDialog

class FloatingWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.current_theme = "dark"  # Default theme

        self.setWindowTitle("Clipboard AI Helper")
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.Window |
            Qt.CustomizeWindowHint |
            Qt.WindowTitleHint |
            Qt.WindowMinimizeButtonHint |
            Qt.WindowMaximizeButtonHint |
            Qt.WindowCloseButtonHint
        )

        self.setGeometry(300, 300, 500, 300)
        self.setMinimumSize(400, 200)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Top bar
        title_bar = QHBoxLayout()
        title = QLabel("🧠 Clipboard AI Helper")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        title_bar.addWidget(title)
        title_bar.addStretch()

        self.theme_btn = QPushButton("☀️ Light Mode")
        self.theme_btn.setFixedSize(100, 30)
        self.theme_btn.clicked.connect(self.toggle_theme)
        title_bar.addWidget(self.theme_btn)

        # In the init_ui method, add this button after the theme button:
        settings_btn = QPushButton("⚙️ Settings")
        settings_btn.setFixedSize(80, 30)
        settings_btn.clicked.connect(self.show_settings)
        title_bar.addWidget(settings_btn)

        clear_btn = QPushButton("🧹 Clear")
        clear_btn.setFixedSize(60, 30)
        clear_btn.clicked.connect(self.clear_content)
        title_bar.addWidget(clear_btn)

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(30, 30)
        close_btn.clicked.connect(self.close)
        title_bar.addWidget(close_btn)

        layout.addLayout(title_bar)

        # Split text areas
        splitter = QSplitter(Qt.Vertical)

        self.explanation = QTextEdit()
        self.explanation.setPlaceholderText("Explanation will appear here...")
        self.explanation.setReadOnly(True)
        splitter.addWidget(self.explanation)

        self.fixes = QTextEdit()
        self.fixes.setPlaceholderText("Fixes/suggestions...")
        self.fixes.setReadOnly(True)
        splitter.addWidget(self.fixes)

        splitter.setSizes([200, 100])
        layout.addWidget(splitter)

        # Resize grip
        grip = QSizeGrip(self)
        layout.addWidget(grip, 0, Qt.AlignRight)

        self.setLayout(layout)
        self.apply_theme()
        self.show()

    def toggle_theme(self):
        if self.current_theme == "dark":
            self.current_theme = "light"
            self.theme_btn.setText("🌙 Dark Mode")
        else:
            self.current_theme = "dark"
            self.theme_btn.setText("☀️ Light Mode")
        self.apply_theme()

    def apply_theme(self):
        if self.current_theme == "dark":
            style = """
                QWidget {
                    background-color: #1e1e1e;
                    color: #dcdcdc;
                }
                QTextEdit {
                    background-color: #1e1e1e;
                    color: #dcdcdc;
                    font-family: Consolas, monospace;
                }
                QPushButton {
                    background-color: #2e2e2e;
                    color: #ffffff;
                    border: 1px solid #555;
                    padding: 4px;
                }
                QPushButton:hover {
                    background-color: #3e3e3e;
                }
            """
        else:
            style = """
                QWidget {
                    background-color: #ffffff;
                    color: #000000;
                }
                QTextEdit {
                    background-color: #ffffff;
                    color: #000000;
                    font-family: Consolas, monospace;
                }
                QPushButton {
                    background-color: #f0f0f0;
                    color: #000000;
                    border: 1px solid #aaa;
                    padding: 4px;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                }
            """
        self.setStyleSheet(style)

    def update_content(self, explanation_text, fixes_text):
        self.explanation.setHtml(explanation_text)
        self.fixes.setHtml(fixes_text)

    def clear_content(self):
        self.explanation.clear()
        self.fixes.clear()

    def current_theme_style(self):
        # Called by main.py to apply correct HTML styling
        if self.current_theme == "dark":
            return """
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
        else:
            return """
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

    # Add this method to the FloatingWindow class:
    def show_settings(self):
        """Show API key settings dialog"""
        current_key = self.api_key_manager.load_api_key()
        dialog = APIKeyDialog(current_key, is_first_run=False)
        dialog.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FloatingWindow()
    sys.exit(app.exec_())
