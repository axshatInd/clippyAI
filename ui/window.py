import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QPushButton, QHBoxLayout, QTextEdit, QSizeGrip
)
from PyQt5.QtCore import Qt

class FloatingWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Modern Window Features
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

        self.setGeometry(300, 300, 500, 300)  # Initial size
        self.setMinimumSize(400, 200)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Title area with close button
        title_bar = QHBoxLayout()
        title = QLabel("🧠 Clipboard AI Helper")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        title_bar.addWidget(title)
        title_bar.addStretch()

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(30, 30)
        close_btn.clicked.connect(self.close)
        title_bar.addWidget(close_btn)

        layout.addLayout(title_bar)

        # Explanation area
        self.explanation = QTextEdit()
        self.explanation.setPlaceholderText("Explanation will appear here...")
        layout.addWidget(self.explanation)

        # Fix suggestions area
        self.fixes = QTextEdit()
        self.fixes.setPlaceholderText("Fixes/suggestions...")
        layout.addWidget(self.fixes)

        # Resizing handle
        grip = QSizeGrip(self)
        layout.addWidget(grip, 0, Qt.AlignRight)

        self.setLayout(layout)
        self.show()

    def update_content(self, explanation_text, fixes_text):
        self.explanation.setText(explanation_text)
        self.fixes.setText(fixes_text)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FloatingWindow()
    sys.exit(app.exec_())
