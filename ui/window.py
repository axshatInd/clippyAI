import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QPushButton, QHBoxLayout, QTextEdit, QSizeGrip, QSplitter
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap
from api_key_manager import APIKeyDialog
import resources_rc  # Import the compiled resource file

class FloatingWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.current_theme = "dark"  # Default theme

        self.setWindowTitle("ClippyAI - Code Analyzer")
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.Window |
            Qt.CustomizeWindowHint |
            Qt.WindowTitleHint |
            Qt.WindowMinimizeButtonHint |
            Qt.WindowMaximizeButtonHint |
            Qt.WindowCloseButtonHint
        )

        # Set window icon from embedded resource
        self.set_window_icon()

        self.setGeometry(300, 300, 500, 300)
        self.setMinimumSize(400, 200)

        self.init_ui()

    def set_window_icon(self):
        """Set the window icon from embedded resource"""
        try:
            # Load icon from Qt resource system
            icon = QIcon(":/icon.ico")
            self.setWindowIcon(icon)
            print("✅ Window icon loaded from embedded resource")
        except Exception as e:
            print(f"❌ Error loading embedded window icon: {e}")

    def init_ui(self):
        layout = QVBoxLayout()

        # Top bar
        title_bar = QHBoxLayout()
        
        # Add icon display from embedded resource
        icon_label = QLabel()
        try:
            # Load pixmap from Qt resource system
            pixmap = QPixmap(":/icon.ico")
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                icon_label.setPixmap(scaled_pixmap)
                print("✅ Title icon loaded from embedded resource")
            else:
                raise Exception("Pixmap is null")
        except Exception as e:
            # Fallback to emoji if resource not found
            icon_label.setText("🧠")
            icon_label.setStyleSheet("font-size: 16px;")
            print(f"⚠️ Using fallback emoji for title icon: {e}")
        
        title_bar.addWidget(icon_label)
        
        title = QLabel("ClippyAI")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-left: 8px;")
        title_bar.addWidget(title)
        title_bar.addStretch()

        self.theme_btn = QPushButton("☀️ Light Mode")
        self.theme_btn.setFixedSize(100, 30)
        self.theme_btn.clicked.connect(self.toggle_theme)
        title_bar.addWidget(self.theme_btn)

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
        self.explanation.setPlaceholderText("Code explanation will appear here...")
        self.explanation.setReadOnly(True)
        splitter.addWidget(self.explanation)

        self.fixes = QTextEdit()
        self.fixes.setPlaceholderText("Fixes and suggestions will appear here...")
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
                body {
                    font-size: 16px;
                    line-height: 1.6;
                    font-family: Arial, sans-serif;
                }
                pre {
                    background-color: #2d2d2d; /* Slightly lighter than app background */
                    color: #e6e6e6;           /* Brighter text */
                    padding: 10px;
                    border-radius: 5px;
                    overflow-x: auto;
                    font-family: Consolas, monospace;
                    font-size: 16px; /* Increased font size */
                    line-height: 1.5; /* Improved line height */
                    border: 1px solid #444;  /* Visible border for distinction */
                    box-shadow: 0 0 8px rgba(0, 0, 0, 0.5); /* Optional subtle glow */
                }
                code {
                    font-family: Consolas, monospace;
                    font-size: 16px; /* Increased font size */
                }
                p, li, div, span {
                    font-size: 16px;
                    line-height: 1.6;
                }
                h1, h2, h3, h4, h5, h6 {
                    font-size: 18px;
                    font-weight: bold;
                    margin: 10px 0;
                }
            </style>
            """
        else:
            return """
            <style>
                body {
                    font-size: 16px;
                    line-height: 1.6;
                    font-family: Arial, sans-serif;
                }
                pre {
                    background-color: #f0f0f0;
                    color: #000;
                    padding: 10px;
                    border-radius: 5px;
                    overflow-x: auto;
                    font-family: Consolas, monospace;
                    font-size: 16px; /* Increased font size */
                    line-height: 1.5; /* Improved line height */
                    border: 1px solid #ddd;
                }
                code {
                    font-family: Consolas, monospace;
                    font-size: 16px; /* Increased font size */
                }
                p, li, div, span {
                    font-size: 16px;
                    line-height: 1.6;
                }
                h1, h2, h3, h4, h5, h6 {
                    font-size: 18px;
                    font-weight: bold;
                    margin: 10px 0;
                }
            </style>
            """

    def show_settings(self):
        """Show API key settings dialog"""
        current_key = self.api_key_manager.load_api_key()
        dialog = APIKeyDialog(current_key, is_first_run=False)
        dialog.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FloatingWindow()
    sys.exit(app.exec_())
