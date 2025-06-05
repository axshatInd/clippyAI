from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt  # ✅ Add this line

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
