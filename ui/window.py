import sys
import os
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QPushButton, QHBoxLayout, QTextEdit, QSizeGrip, QSplitter, QLineEdit
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap
from api_key_manager import APIKeyDialog
from chat_history import ConversationManager
import resources_rc  # Import the compiled resource file

class FloatingWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.current_theme = "dark"  # Default theme
        self.conversation_manager = ConversationManager()

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

        self.setGeometry(300, 300, 900, 500)  # Increased width for chat panel
        self.setMinimumSize(600, 300)  # Increased minimum size

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

        # Main content area with horizontal split
        main_splitter = QSplitter(Qt.Horizontal)

        # Left panel: Original analysis (vertical split)
        analysis_widget = QWidget()
        analysis_layout = QVBoxLayout()
        analysis_layout.setContentsMargins(0, 0, 0, 0)

        analysis_splitter = QSplitter(Qt.Vertical)

        self.explanation = QTextEdit()
        self.explanation.setPlaceholderText("Code explanation will appear here...")
        self.explanation.setReadOnly(True)
        analysis_splitter.addWidget(self.explanation)

        self.fixes = QTextEdit()
        self.fixes.setPlaceholderText("Fixes and suggestions will appear here...")
        self.fixes.setReadOnly(True)
        analysis_splitter.addWidget(self.fixes)

        analysis_splitter.setSizes([120, 180])  # Maintain your preferred ratio
        analysis_layout.addWidget(analysis_splitter)
        analysis_widget.setLayout(analysis_layout)

        # Right panel: Chat interface
        chat_widget = self.create_chat_interface()

        # Add both panels to main splitter
        main_splitter.addWidget(analysis_widget)
        main_splitter.addWidget(chat_widget)
        main_splitter.setSizes([500, 300])  # 60-40 split

        layout.addWidget(main_splitter)

        # Resize grip
        grip = QSizeGrip(self)
        layout.addWidget(grip, 0, Qt.AlignRight)

        self.setLayout(layout)
        self.apply_theme()
        self.show()

    def create_chat_interface(self):
        """Create the chat interface panel"""
        chat_widget = QWidget()
        chat_layout = QVBoxLayout()
        chat_layout.setContentsMargins(5, 0, 5, 0)

        # Chat header
        chat_header = QLabel("💬 Interactive Chat")
        chat_header.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px;")
        chat_layout.addWidget(chat_header)

        # Chat history display
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_history.setPlaceholderText("Continue the conversation here...\n\nAfter initial analysis, you can:\n• Report errors\n• Ask for improvements\n• Request explanations\n• Debug issues")
        chat_layout.addWidget(self.chat_history)

        # Chat input area
        input_layout = QVBoxLayout()
        input_layout.setContentsMargins(0, 5, 0, 0)

        # Input field
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Ask about the code, report errors, or request improvements...")
        self.chat_input.returnPressed.connect(self.send_chat_message)
        input_layout.addWidget(self.chat_input)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 5, 0, 0)

        clear_chat_btn = QPushButton("🗑️ Clear Chat")
        clear_chat_btn.setFixedSize(80, 25)
        clear_chat_btn.clicked.connect(self.clear_chat)
        button_layout.addWidget(clear_chat_btn)

        button_layout.addStretch()

        send_btn = QPushButton("Send")
        send_btn.setFixedSize(60, 25)
        send_btn.clicked.connect(self.send_chat_message)
        button_layout.addWidget(send_btn)

        input_layout.addLayout(button_layout)
        chat_layout.addLayout(input_layout)

        chat_widget.setLayout(chat_layout)
        return chat_widget

    def send_chat_message(self):
        """Send a chat message to the AI"""
        user_message = self.chat_input.text().strip()
        if not user_message:
            return

        # Add to chat history display
        self.add_chat_message("You", user_message, "#4CAF50")
        self.chat_input.clear()

        # Add to conversation manager
        self.conversation_manager.add_message("user", user_message)

        # Send to AI for response (this will be called from main.py)
        if hasattr(self, 'get_chat_response_callback'):
            self.get_chat_response_callback()

    def add_chat_message(self, sender: str, message: str, color: str):
        """Add a message to the chat history display"""
        timestamp = datetime.now().strftime("%H:%M")
        
        # Apply theme-appropriate styling
        if self.current_theme == "dark":
            bg_color = "#2d2d2d"
            text_color = "#dcdcdc"
            time_color = "#888"
        else:
            bg_color = "#f5f5f5"
            text_color = "#333"
            time_color = "#666"

        # Use .format() method instead of f-string to avoid backslash issues
        formatted_message = """
        <div style="margin: 8px 0; padding: 10px; background-color: {bg_color}; border-left: 3px solid {color}; border-radius: 5px;">
            <div style="margin-bottom: 5px;">
                <strong style="color: {color};">{sender}</strong> 
                <span style="color: {time_color}; font-size: 11px; float: right;">{timestamp}</span>
            </div>
            <div style="color: {text_color}; line-height: 1.4;">
                {message}
            </div>
        </div>
        """.format(
            bg_color=bg_color, 
            color=color, 
            sender=sender, 
            time_color=time_color, 
            timestamp=timestamp, 
            text_color=text_color,
            message=message.replace('\n', '<br>')
        )
        
        self.chat_history.append(formatted_message)
        
        # Auto-scroll to bottom
        scrollbar = self.chat_history.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def clear_chat(self):
        """Clear the chat history"""
        self.chat_history.clear()
        self.conversation_manager.clear_current_session()
        self.add_chat_message("System", "Chat cleared. Start a new conversation by copying code or asking questions.", "#FF9800")

    def toggle_theme(self):
        """Toggle between dark and light themes"""
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
                    border: 1px solid #444;
                }
                QLineEdit {
                    background-color: #2d2d2d;
                    color: #dcdcdc;
                    border: 1px solid #444;
                    padding: 5px;
                    border-radius: 3px;
                }
                QPushButton {
                    background-color: #2e2e2e;
                    color: #ffffff;
                    border: 1px solid #555;
                    padding: 4px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #3e3e3e;
                }
                QSplitter::handle {
                    background-color: #444;
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
                    border: 1px solid #ccc;
                }
                QLineEdit {
                    background-color: #ffffff;
                    color: #000000;
                    border: 1px solid #ccc;
                    padding: 5px;
                    border-radius: 3px;
                }
                QPushButton {
                    background-color: #f0f0f0;
                    color: #000000;
                    border: 1px solid #aaa;
                    padding: 4px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                }
                QSplitter::handle {
                    background-color: #ccc;
                }
            """
        self.setStyleSheet(style)

    def update_content(self, explanation_text, fixes_text):
        self.explanation.setHtml(explanation_text)
        self.fixes.setHtml(fixes_text)

    def clear_content(self):
        self.explanation.clear()
        self.fixes.clear()
        self.clear_chat()

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
