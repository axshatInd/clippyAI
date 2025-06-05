import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QPushButton, QHBoxLayout, QTextEdit, QSizeGrip
)
from PyQt5.QtCore import Qt

class FloatingWindow(QWidget):
    def __init__(self):
        super().__init__()

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

        # Title bar with close and clear buttons
        title_bar = QHBoxLayout()
        title = QLabel("🧠 Clipboard AI Helper")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        title_bar.addWidget(title)
        title_bar.addStretch()

        clear_btn = QPushButton("🧹 Clear")
        clear_btn.setFixedSize(60, 30)
        clear_btn.clicked.connect(self.clear_content)
        title_bar.addWidget(clear_btn)

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(30, 30)
        close_btn.clicked.connect(self.close)
        title_bar.addWidget(close_btn)

        layout.addLayout(title_bar)

        # ✅ Create a QSplitter for resizable vertical areas
        from PyQt5.QtWidgets import QSplitter
        splitter = QSplitter(Qt.Vertical)

        self.explanation = QTextEdit()
        self.explanation.setPlaceholderText("Explanation will appear here...")
        splitter.addWidget(self.explanation)

        self.fixes = QTextEdit()
        self.fixes.setPlaceholderText("Fixes/suggestions...")
        splitter.addWidget(self.fixes)

        # Optionally set initial splitter ratio
        splitter.setSizes([200, 100])  # [top, bottom]

        layout.addWidget(splitter)

        # Resizing handle at bottom-right
        grip = QSizeGrip(self)
        layout.addWidget(grip, 0, Qt.AlignRight)

        self.setLayout(layout)
        self.show()

    def update_content(self, explanation_text, fixes_text):
        self.explanation.setHtml(explanation_text)
        self.fixes.setHtml(fixes_text)

    def clear_content(self):
        self.explanation.clear()
        self.fixes.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FloatingWindow()
    sys.exit(app.exec_())
