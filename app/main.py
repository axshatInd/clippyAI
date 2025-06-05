import pyperclip
import time
import requests
from PyQt5.QtWidgets import QApplication
from overlay import OverlayWindow
import sys

API_URL = "http://127.0.0.1:8000/analyze"

def fetch_analysis(code):
    try:
        res = requests.post(API_URL, json={"code": code})
        return res.json()
    except Exception as e:
        return {"explanation": "API Error", "fixes": str(e)}

def main_loop():
    last_clip = ""
    app = QApplication(sys.argv)
    while True:
        try:
            text = pyperclip.paste()
            if text != last_clip and len(text.strip()) > 5:
                last_clip = text
                print("[+] Code copied:\n", text)
                result = fetch_analysis(text)
                overlay = OverlayWindow(result['explanation'], result['fixes'])
                overlay.auto_close()
                app.processEvents()
        except KeyboardInterrupt:
            break
        time.sleep(2)

if __name__ == "__main__":
    main_loop()
