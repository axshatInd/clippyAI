from PyQt5 import QtWidgets, QtCore
import sys

class OverlayWindow(QtWidgets.QWidget):
    def __init__(self, explanation, fixes):
        super().__init__()
        self.setWindowTitle("Clipboard AI Helper")
        self.setWindowFlags(
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.Tool
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(30, 30, 30, 240);
                color: white;
                font-size: 14px;
                border-radius: 12px;
                padding: 10px;
            }
        """)
        layout = QtWidgets.QVBoxLayout()

        self.expl_label = QtWidgets.QLabel(f"📘 {explanation}")
        self.fix_label = QtWidgets.QLabel(f"🛠 {fixes}")

        layout.addWidget(self.expl_label)
        layout.addWidget(self.fix_label)
        self.setLayout(layout)
        self.resize(300, 120)
        self.show()

    def auto_close(self, seconds=5):
        QtCore.QTimer.singleShot(seconds * 1000, self.close)

# For testing overlay UI independently
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = OverlayWindow("Dummy explanation", "No fix needed.")
    w.auto_close()
    sys.exit(app.exec_())
