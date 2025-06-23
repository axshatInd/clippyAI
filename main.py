import sys
import os

# ✅ Fix for PyInstaller console=False with FastAPI/Uvicorn
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    import io
    
    # Redirect stdout and stderr to prevent Uvicorn logging errors
    sys.stdout = io.StringIO()
    sys.stderr = io.StringIO()
    
    # Alternative: Redirect to a log file if you want to keep logs
    # log_file = os.path.join(os.path.dirname(sys.executable), 'app.log')
    # sys.stdout = open(log_file, 'w')
    # sys.stderr = sys.stdout
    
import pyperclip
import requests
import markdown
import threading
import time
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon
from ui.window import FloatingWindow
from ui.prompt import PromptWindow, AdditionalInfoPromptWindow
from api_key_manager import APIKeyManager, APIKeyDialog
from chat_history import ConversationManager
import resources_rc  # Import the compiled resource file

API_URL = "http://127.0.0.1:8000/analyze"
CHAT_URL = "http://127.0.0.1:8000/chat"

# ✅ Updated theme-specific HTML styling with larger fonts
LIGHT_MODE_STYLE = """
<style>
body {
    font-size: 16px;
    line-height: 1.5;
    font-family: Arial, sans-serif;
}
pre {
    background-color: #f0f0f0;
    color: #000;
    padding: 10px;
    border-radius: 5px;
    overflow-x: auto;
    font-family: Consolas, monospace;
    font-size: 14px;
    line-height: 1.4;
}
code {
    font-family: Consolas, monospace;
    font-size: 14px;
}
p, li, div {
    font-size: 16px;
    line-height: 1.5;
}
</style>
"""

DARK_MODE_STYLE = """
<style>
body {
    font-size: 16px;
    line-height: 1.5;
    font-family: Arial, sans-serif;
}
pre {
    background-color: #1e1e1e;
    color: #dcdcdc;
    padding: 10px;
    border-radius: 5px;
    overflow-x: auto;
    font-family: Consolas, monospace;
    font-size: 14px;
    line-height: 1.4;
}
code {
    font-family: Consolas, monospace;
    font-size: 14px;
}
p, li, div {
    font-size: 16px;
    line-height: 1.5;
}
</style>
"""

class ClipboardWatcher:
    def __init__(self, window):
        self.window = window
        self.last_clipboard = ""
        self.current_copied_text = ""
        self.current_session_id = None

        # Set up the callback for chat responses
        self.window.get_chat_response_callback = self.get_chat_response

        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.check_clipboard)
        self.timer.start()

    def check_clipboard(self):
        current = pyperclip.paste()
        if current != self.last_clipboard and current.strip():
            self.last_clipboard = current
            self.current_copied_text = current
            self.ask_permission(current)

    def ask_permission(self, copied_text):
        self.prompt = PromptWindow(
            on_yes=lambda: self.show_additional_info_prompt(),
            on_no=lambda: None
        )
        self.prompt.show()

    def show_additional_info_prompt(self):
        """Show the additional information prompt window"""
        self.additional_prompt = AdditionalInfoPromptWindow(
            on_proceed=lambda additional_info: self.analyze_code_with_additional_info(additional_info)
        )
        self.additional_prompt.show()

    def analyze_code_with_additional_info(self, additional_info):
        """Enhanced to start a conversation session"""
        try:
            print(f"📡 Sending request to: {API_URL}")
            
            # Start new conversation session
            self.current_session_id = self.window.conversation_manager.start_new_session(
                self.current_copied_text + (f"\n\nAdditional Context: {additional_info}" if additional_info else "")
            )
            
            # Combine original text with additional info
            combined_input = self.current_copied_text
            if additional_info:
                combined_input += f"\n\nAdditional Context: {additional_info}"
            
            # Send initial analysis request
            res = requests.post(API_URL, json={
                "code": combined_input,
                "session_id": self.current_session_id,
                "is_followup": False
            }, timeout=30)
            
            print(f"✅ API Response status: {res.status_code}")
            data = res.json()
            explanation_md = data.get("explanation", "No explanation returned.")
            fixes_md = data.get("fixes", "No fixes returned.")
            
            # Add AI response to conversation
            self.window.conversation_manager.add_message("assistant", explanation_md + "\n\n" + fixes_md)
            
            # Display results
            theme_style = self.window.current_theme_style()
            explanation_html = theme_style + markdown.markdown(explanation_md, extensions=["fenced_code"])
            fixes_html = theme_style + markdown.markdown(fixes_md, extensions=["fenced_code"])
            
            self.window.update_content(explanation_html, fixes_html)
            
            # Initialize chat with welcome message
            self.window.add_chat_message("ClippyAI", "Analysis complete! 🎉\n\nFeel free to:\n• Report any LeetCode errors\n• Ask for improvements\n• Request explanations\n• Debug issues", "#2196F3")
            
            self.window.show()
            
        except Exception as e:
            print(f"❌ API Error: {e}")
            error_html = f"<b>Error contacting API.</b><br><pre>{str(e)}</pre>"
            self.window.update_content(error_html, "")
            self.window.show()

    def get_chat_response(self):
        """Get AI response for chat message"""
        if not self.current_session_id:
            self.window.add_chat_message("ClippyAI", "Please start by copying some code first!", "#f44336")
            return
            
        try:
            # Get conversation context
            context = self.window.conversation_manager.get_conversation_context()
            
            # Get the last user message
            last_message = context[-1]["content"] if context else ""
            
            print(f"💬 Sending chat request to: {CHAT_URL}")
            
            res = requests.post(CHAT_URL, json={
                "code": last_message,
                "session_id": self.current_session_id,
                "is_followup": True,
                "conversation_context": context
            }, timeout=30)
            
            print(f"✅ Chat Response status: {res.status_code}")
            data = res.json()
            ai_response = data.get("chat_response", "Sorry, I couldn't process that.")
            
            # Add AI response to conversation manager
            self.window.conversation_manager.add_message("assistant", ai_response)
            
            # Display in chat with markdown formatting
            formatted_response = markdown.markdown(ai_response, extensions=["fenced_code"])
            self.window.add_chat_message("ClippyAI", formatted_response, "#2196F3")
            
        except Exception as e:
            print(f"❌ Chat Error: {e}")
            self.window.add_chat_message("ClippyAI", f"Error: {str(e)}", "#f44336")

    # Keep the original analyze_code method as backup (not used now)
    def analyze_code(self, code):
        """Original analyze_code method - now replaced by analyze_code_with_additional_info"""
        # This method is now replaced by analyze_code_with_additional_info
        # Keeping it for backward compatibility
        self.analyze_code_with_additional_info("")

def start_server():
    """Start the FastAPI server in a separate thread"""
    print("🚀 Starting FastAPI server...")
    
    try:
        # Get API key from registry
        gemini_key = APIKeyManager.load_api_key()
        if not gemini_key:
            print("❌ No API key found!")
            return
        
        # Set environment variable for the server
        os.environ["GEMINI_API_KEY"] = gemini_key
        print(f"✅ GEMINI_API_KEY loaded from registry: {gemini_key[:10]}...")
        
        import uvicorn
        from api.server import app
        
        print("🌐 Starting uvicorn server on 127.0.0.1:8000...")
        uvicorn.run(app, host="127.0.0.1", port=8000, log_level="error")
        
    except Exception as e:
        print(f"❌ Server failed to start: {e}")
        import traceback
        traceback.print_exc()

def setup_api_key():
    """Handle API key setup on first run or when missing"""
    api_key = APIKeyManager.load_api_key()
    
    if not api_key:
        print("🔑 No API key found - showing setup dialog...")
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        dialog = APIKeyDialog(is_first_run=True)
        if dialog.exec_() == dialog.Accepted:
            return dialog.api_key
        else:
            QMessageBox.critical(None, "Error", "API key is required to run ClippyAI!")
            return None
    
    return api_key

def test_server_connection():
    """Test if server is responding"""
    max_attempts = 15
    for i in range(max_attempts):
        try:
            response = requests.get("http://127.0.0.1:8000", timeout=2)
            print("✅ Server is responding!")
            return True
        except requests.exceptions.RequestException:
            print(f"⏳ Server not ready yet... ({i+1}/{max_attempts})")
            time.sleep(1)
    
    print("❌ Server failed to start after 15 seconds")
    return False

def set_application_icon(app):
    """Set the application icon globally from embedded resource"""
    try:
        # Try to load icon from Qt resource system first
        icon = QIcon(":/icon.ico")
        if not icon.isNull():
            app.setWindowIcon(icon)
            print("✅ Application icon set from embedded resource")
            return
        
        # Fallback to external file if resource not available
        if getattr(sys, 'frozen', False):
            icon_path = os.path.join(os.path.dirname(sys.executable), 'icon.ico')
        else:
            icon_path = 'icon.ico'
        
        if os.path.exists(icon_path):
            app.setWindowIcon(QIcon(icon_path))
            print(f"✅ Application icon set from file: {icon_path}")
        else:
            print(f"⚠️ Icon not found at: {icon_path}")
            
    except Exception as e:
        print(f"❌ Error setting application icon: {e}")

if __name__ == "__main__":
    print("🎯 Starting ClippyAI application...")
    
    # Setup API key first
    api_key = setup_api_key()
    if not api_key:
        sys.exit(1)
    
    # Start server thread
    print("🧵 Creating server thread...")
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Wait for server
    print("⏳ Waiting for server to start...")
    server_ready = test_server_connection()
    
    if not server_ready:
        print("⚠️ Server may not be ready, but continuing with GUI...")
    
    try:
        print("🖥️ Starting PyQt5 application...")
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # Set application icon globally
        set_application_icon(app)
        
        # Set application properties
        app.setApplicationName("ClippyAI")
        app.setApplicationDisplayName("ClippyAI - Code Analyzer")
        app.setApplicationVersion("2.0.0")  # Updated to v2.0.0 for chat feature
        app.setOrganizationName("ClippyAI")
        
        window = FloatingWindow()
        
        # Add API key settings to window
        window.api_key_manager = APIKeyManager
        
        watcher = ClipboardWatcher(window)
        print("✅ GUI started successfully")
        sys.exit(app.exec_())
    except Exception as e:
        print(f"❌ Application error: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
