"""
AirplaneRoshan: System Diagnostic Tool
======================================
Pre-flight checklist to verify environment integrity.
Checks Python version, MediaPipe installation, Camera access, and Network stack.

Run this command:
    python system_check.py
"""

import sys
import os
import socket
import importlib
import time


# --- ANSI COLORS FOR TERMINAL ---
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_status(step, status, message):
    if status == "OK":
        print(f"[{Colors.OKGREEN} OK {Colors.ENDC}] {step}: {message}")
    elif status == "FAIL":
        print(f"[{Colors.FAIL}FAIL{Colors.ENDC}] {step}: {message}")
    elif status == "WARN":
        print(f"[{Colors.WARNING}WARN{Colors.ENDC}] {step}: {message}")


def check_python_version():
    """Ensures Python is between 3.8 and 3.12 (MP doesn't like 3.13 yet)."""
    major = sys.version_info.major
    minor = sys.version_info.minor

    ver_str = f"{major}.{minor}"
    if major == 3 and (8 <= minor <= 12):
        print_status("Python Version", "OK", f"Detected Python {ver_str}")
        return True
    elif major == 3 and minor >= 13:
        print_status("Python Version", "FAIL", f"Python {ver_str} is too new for MediaPipe. Downgrade to 3.10 or 3.11.")
        return False
    else:
        print_status("Python Version", "WARN", f"Detected Python {ver_str}. MediaPipe might be unstable.")
        return True


def check_dependencies():
    """Checks imports and specifically the MediaPipe 'solutions' bug."""
    required = ['cv2', 'mediapipe', 'numpy']
    all_good = True

    for lib in required:
        try:
            importlib.import_module(lib)
            print_status(f"Library '{lib}'", "OK", "Installed.")
        except ImportError:
            print_status(f"Library '{lib}'", "FAIL", "Not found. Run: pip install -r requirements.txt")
            all_good = False

    # Deep Check for MediaPipe Solutions (The specific error you had)
    if all_good:
        try:
            import mediapipe as mp
            _ = mp.solutions.hands
            print_status("MediaPipe Integrity", "OK", "mp.solutions.hands loaded successfully.")
        except AttributeError:
            print_status("MediaPipe Integrity", "FAIL", "Corrupted Installation detected.")
            print(f"{Colors.WARNING}   👉 FIX: pip install mediapipe==0.10.9 protobuf==3.20.3{Colors.ENDC}")
            all_good = False

    return all_good


def check_camera():
    """Attempts to open the camera briefly."""
    try:
        import cv2
        import config  # Checks if config exists too

        cap = cv2.VideoCapture(config.WEBCAM_ID)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                print_status("Hardware Camera", "OK", f"Camera ID {config.WEBCAM_ID} is working.")
                cap.release()
                return True
            else:
                print_status("Hardware Camera", "WARN", "Camera opened but returned no frame.")
                return False
        else:
            print_status("Hardware Camera", "FAIL", f"Could not open Camera ID {config.WEBCAM_ID}.")
            return False
    except Exception as e:
        print_status("Hardware Camera", "FAIL", f"Crash during check: {e}")
        return False


def check_network():
    """Verifies UDP socket creation."""
    try:
        import config
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setblocking(False)
        # Try to send a dummy packet to check permissions
        sock.sendto(b'ping', (config.UDP_IP, config.UDP_PORT))
        print_status("Network Stack", "OK", f"UDP Socket created. Target: {config.UDP_IP}:{config.UDP_PORT}")
        sock.close()
        return True
    except PermissionError:
        print_status("Network Stack", "FAIL", "Permission Denied. Firewall blocking Python?")
        return False
    except Exception as e:
        print_status("Network Stack", "FAIL", f"Socket error: {e}")
        return False


def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{Colors.BOLD}{Colors.HEADER}=== AIRPLANEROSHAN SYSTEM DIAGNOSTIC TOOL ==={Colors.ENDC}\n")

    score = 0
    checks = 4

    if check_python_version(): score += 1
    if check_dependencies(): score += 1
    if check_network(): score += 1
    if check_camera(): score += 1

    print("\n" + "=" * 50)
    if score == checks:
        print(f"{Colors.OKGREEN}{Colors.BOLD}✅ SYSTEM READY FOR FLIGHT.{Colors.ENDC}")
        print("Run 'python main.py' to start the controller.")
    else:
        print(f"{Colors.FAIL}{Colors.BOLD}❌ SYSTEM CHECKS FAILED.{Colors.ENDC}")
        print("Please resolve the FAIL items above before running main.py.")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    main()