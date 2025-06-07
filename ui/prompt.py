from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QTextEdit
from PyQt5.QtCore import Qt

class PromptWindow(QWidget):
    def __init__(self, on_yes, on_no):
        super().__init__()
        self.setWindowTitle("Confirm")
        self.setFixedSize(300, 100)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        label = QLabel("Explain with ClippyAI?")
        label.setStyleSheet("font-size: 14px;")

        yes_button = QPushButton("Yes")
        no_button = QPushButton("No")

        yes_button.clicked.connect(self.handle_yes)
        no_button.clicked.connect(self.handle_no)

        self.on_yes = on_yes
        self.on_no = on_no

        button_layout = QHBoxLayout()
        button_layout.addWidget(yes_button)
        button_layout.addWidget(no_button)

        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def handle_yes(self):
        self.close()
        self.on_yes()

    def handle_no(self):
        self.close()
        self.on_no()

# ✅ New Additional Info Prompt Window
class AdditionalInfoPromptWindow(QWidget):
    def __init__(self, on_proceed):
        super().__init__()
        self.setWindowTitle("Additional Information")
        self.setFixedSize(450, 250)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        # Instructions
        label = QLabel("Any additional information you want to specify? (Optional)")
        label.setStyleSheet("font-size: 14px; font-weight: bold;")

        # Additional info text box with fixed background and color
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Enter additional context, requirements, or specific questions here...")
        self.text_edit.setStyleSheet("""
            QTextEdit {
                font-size: 12px; 
                padding: 5px;
                background-color: white;
                color: black;
                border: 1px solid #ccc;
                border-radius: 3px;
            }
        """)

        # Buttons
        proceed_button = QPushButton("✅ Proceed")
        proceed_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 5px;")
        proceed_button.clicked.connect(self.handle_proceed)

        skip_button = QPushButton("⏭️ Skip")
        skip_button.setStyleSheet("background-color: #f0f0f0; color: #333; padding: 5px;")
        skip_button.clicked.connect(self.handle_skip)

        self.on_proceed = on_proceed

        # Layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(skip_button)
        button_layout.addWidget(proceed_button)

        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(self.text_edit)
        layout.addLayout(button_layout)
        self.setLayout(layout)

        # Focus on text box
        self.text_edit.setFocus()

    def handle_proceed(self):
        additional_text = self.text_edit.toPlainText().strip()
        self.close()
        self.on_proceed(additional_text)

    def handle_skip(self):
        self.close()
        self.on_proceed("")  # Empty string for no additional info
