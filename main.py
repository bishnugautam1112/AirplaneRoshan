
import cv2
import mediapipe as mp
import pygame
import numpy as np
import time

# === Pygame Setup ===
pygame.init()
WIDTH, HEIGHT = 800, 600
win = pygame.display.set_mode((WIDTH + 320, HEIGHT))  # Extra space for webcam
pygame.display.set_caption("Gesture-Controlled Plane + Camera")
clock = pygame.time.Clock()

plane = pygame.Rect(WIDTH//2 - 25, HEIGHT - 100, 50, 50)
plane_color = (0, 200, 255)
bg_color = (30, 30, 30)
font = pygame.font.SysFont(None, 48)

# === MediaPipe Setup ===
cap = cv2.VideoCapture(0)
hands = mp.solutions.hands.Hands(max_num_hands=2, min_detection_confidence=0.7)
draw = mp.solutions.drawing_utils

started = False
gesture = ""
last_gesture_time = 0

def fingers_up(lm):
    tips = [8, 12, 16, 20]
    return [lm[i].y < lm[i - 2].y for i in tips]

def is_thumbs_up(lm):
    return lm[4].y < lm[3].y and all(lm[i].y > lm[i - 2].y for i in [8, 12, 16, 20])

def is_index_pointing_right(lm): return lm[8].x > lm[5].x
def is_index_pointing_left(lm): return lm[8].x < lm[5].x

def detect_gesture(hands_data, hand_types):
    global started
    if not started:
        for lm in hands_data:
            if is_thumbs_up(lm):
                started = True
                return "START"
        return ""

    if len(hands_data) == 2:
        left_lm = hands_data[hand_types.index("Left")] if "Left" in hand_types else None
        right_lm = hands_data[hand_types.index("Right")] if "Right" in hand_types else None

        if left_lm and right_lm:
            f1 = fingers_up(left_lm)
            f2 = fingers_up(right_lm)

            if f1 == [1, 0, 0, 0] and f2 == [1, 0, 0, 0]:
                return "FORWARD"
            elif f1 == [1, 0, 0, 0] and f2 == [0, 0, 0, 0] and is_index_pointing_right(left_lm):
                return "RIGHT"
            elif f2 == [1, 0, 0, 0] and f1 == [0, 0, 0, 0] and is_index_pointing_left(right_lm):
                return "LEFT"
            elif f1 == [0, 0, 0, 0] and f2 == [0, 0, 0, 0]:
                return "DOWN"
    return ""

# === Main Loop ===
running = True
while running:
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    hands_data = []
    hand_types = []
    if results.multi_hand_landmarks and results.multi_handedness:
        for i, hand_landmarks in enumerate(results.multi_hand_landmarks):
            hands_data.append(hand_landmarks.landmark)
            hand_types.append(results.multi_handedness[i].classification[0].label)
            draw.draw_landmarks(frame, hand_landmarks, mp.solutions.hands.HAND_CONNECTIONS)

    new_gesture = detect_gesture(hands_data, hand_types)
    gesture = new_gesture if new_gesture else ""

    # === Pygame Drawing ===
    win.fill(bg_color)

    # Move plane
    if gesture == "LEFT":
        plane.x -= 5
    elif gesture == "RIGHT":
        plane.x += 5
    elif gesture == "FORWARD":
        plane.y -= 5
    elif gesture == "DOWN":
        plane.y += 5

    # Clamp to screen
    plane.x = max(0, min(WIDTH - plane.width, plane.x))
    plane.y = max(0, min(HEIGHT - plane.height, plane.y))

    pygame.draw.rect(win, plane_color, plane)

    # Show gesture text
    label = f"Gesture: {gesture if gesture else 'NONE'}"
    text = font.render(label, True, (255, 255, 255))
    win.blit(text, (50, 50))

    # === Show webcam feed ===
    frame = cv2.resize(frame, (320, 240))
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    cam_surface = pygame.surfarray.make_surface(np.rot90(frame_rgb))
    win.blit(cam_surface, (WIDTH, HEIGHT - 240))

    pygame.display.update()
    clock.tick(30)

    # Quit on ESC or window close
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

cap.release()
pygame.quit()