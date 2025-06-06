import winreg
import os
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QLineEdit, QMessageBox, QTextEdit)
from PyQt5.QtCore import Qt

class APIKeyManager:
    """Manages API key storage in Windows Registry"""
    
    REGISTRY_KEY = r"SOFTWARE\ClippyAI"
    VALUE_NAME = "GeminiAPIKey"
    
    @staticmethod
    def save_api_key(api_key):
        """Save API key to Windows Registry"""
        try:
            # Create or open the registry key
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, APIKeyManager.REGISTRY_KEY)
            winreg.SetValueEx(key, APIKeyManager.VALUE_NAME, 0, winreg.REG_SZ, api_key)
            winreg.CloseKey(key)
            return True
        except Exception as e:
            print(f"Error saving API key: {e}")
            return False
    
    @staticmethod
    def load_api_key():
        """Load API key from Windows Registry"""
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, APIKeyManager.REGISTRY_KEY)
            api_key, _ = winreg.QueryValueEx(key, APIKeyManager.VALUE_NAME)
            winreg.CloseKey(key)
            return api_key
        except FileNotFoundError:
            return None
        except Exception as e:
            print(f"Error loading API key: {e}")
            return None
    
    @staticmethod
    def delete_api_key():
        """Delete API key from Windows Registry"""
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, APIKeyManager.REGISTRY_KEY, 0, winreg.KEY_SET_VALUE)
            winreg.DeleteValue(key, APIKeyManager.VALUE_NAME)
            winreg.CloseKey(key)
            return True
        except Exception as e:
            print(f"Error deleting API key: {e}")
            return False

class APIKeyDialog(QDialog):
    """Dialog for entering/editing API key"""
    
    def __init__(self, current_key=None, is_first_run=False):
        super().__init__()
        self.api_key = current_key
        self.is_first_run = is_first_run
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("ClippyAI - API Key Setup")
        self.setFixedSize(500, 400)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        
        layout = QVBoxLayout()
        
        # Title
        if self.is_first_run:
            title = QLabel("🎉 Welcome to ClippyAI!")
            title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2196F3;")
        else:
            title = QLabel("🔧 API Key Settings")
            title.setStyleSheet("font-size: 16px; font-weight: bold;")
        
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Instructions
        instructions = QTextEdit()
        instructions.setReadOnly(True)
        instructions.setMaximumHeight(150)
        instructions.setHtml("""
        <div style="font-family: Arial; font-size: 12px; line-height: 1.4;">
        <p><b>To use ClippyAI, you need a Google Gemini API key:</b></p>
        <ol>
        <li>Go to <a href="https://aistudio.google.com/app/apikey">Google AI Studio</a></li>
        <li>Sign in with your Google account</li>
        <li>Click "Create API Key"</li>
        <li>Copy the generated key and paste it below</li>
        </ol>
        <p><b>Your API key will be stored securely on your computer.</b></p>
        </div>
        """)
        layout.addWidget(instructions)
        
        # API Key input
        key_label = QLabel("Enter your Gemini API Key:")
        key_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(key_label)
        
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("AIzaSy...")
        self.key_input.setEchoMode(QLineEdit.Password)
        if self.api_key:
            self.key_input.setText(self.api_key)
        layout.addWidget(self.key_input)
        
        # Show/Hide key button
        show_key_btn = QPushButton("👁️ Show Key")
        show_key_btn.setFixedSize(100, 30)
        show_key_btn.clicked.connect(self.toggle_key_visibility)
        layout.addWidget(show_key_btn)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        if not self.is_first_run:
            delete_btn = QPushButton("🗑️ Delete Key")
            delete_btn.clicked.connect(self.delete_key)
            button_layout.addWidget(delete_btn)
        
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        save_btn = QPushButton("💾 Save & Continue")
        save_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        
        cancel_btn.clicked.connect(self.reject)
        save_btn.clicked.connect(self.save_key)
        
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def toggle_key_visibility(self):
        if self.key_input.echoMode() == QLineEdit.Password:
            self.key_input.setEchoMode(QLineEdit.Normal)
            self.sender().setText("🙈 Hide Key")
        else:
            self.key_input.setEchoMode(QLineEdit.Password)
            self.sender().setText("👁️ Show Key")
    
    def save_key(self):
        key = self.key_input.text().strip()
        if not key:
            QMessageBox.warning(self, "Error", "Please enter an API key!")
            return
        
        if not key.startswith("AIzaSy"):
            reply = QMessageBox.question(
                self, "Confirm", 
                "The API key doesn't look like a typical Gemini key. Continue anyway?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        
        if APIKeyManager.save_api_key(key):
            self.api_key = key
            QMessageBox.information(self, "Success", "API key saved successfully!")
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "Failed to save API key!")
    
    def delete_key(self):
        reply = QMessageBox.question(
            self, "Confirm Delete", 
            "Are you sure you want to delete the stored API key?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            if APIKeyManager.delete_api_key():
                QMessageBox.information(self, "Success", "API key deleted!")
                self.api_key = None
                self.accept()
            else:
                QMessageBox.critical(self, "Error", "Failed to delete API key!")
