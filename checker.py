import mediapipe
import os

print("--- DEBUG INFO ---")
print(f"1. MediaPipe File Location: {mediapipe.__file__}")
print(f"2. Current Working Directory: {os.getcwd()}")
print(f"3. Is 'solutions' in dir? {'solutions' in dir(mediapipe)}")
print("------------------")