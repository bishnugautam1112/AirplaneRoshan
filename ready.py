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
last_center = None
movement_threshold = 0.015  # More sensitive

def get_hand_center(lm):
    xs = [p.x for p in lm]
    ys = [p.y for p in lm]
    return (np.mean(xs), np.mean(ys))

def is_thumbs_up(lm):
    return lm[4].y < lm[3].y and all(lm[i].y > lm[i - 2].y for i in [8, 12, 16, 20])

def detect_motion(prev, curr):
    dx = curr[0] - prev[0]
    dy = curr[1] - prev[1]

    if abs(dx) < movement_threshold and abs(dy) < movement_threshold:
        return "FORWARD"

    if abs(dx) > abs(dy):
        return "RIGHT" if dx > 0 else "LEFT"
    else:
        return "DOWN" if dy > 0 else "UP"

# === Main Loop ===
running = True
while running:
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    hands_data = []
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            hands_data.append(hand_landmarks.landmark)
            draw.draw_landmarks(frame, hand_landmarks, mp.solutions.hands.HAND_CONNECTIONS)

    if not started:
        for lm in hands_data:
            if is_thumbs_up(lm):
                started = True
                gesture = "STARTED"
                last_center = None
    else:
        if len(hands_data) >= 1:
            centers = [get_hand_center(lm) for lm in hands_data]
            avg_center = np.mean(centers, axis=0)

            if last_center is not None:
                gesture = detect_motion(last_center, avg_center)
            else:
                gesture = "FORWARD"

            last_center = avg_center
        else:
            gesture = "NONE"
            last_center = None

    # === Pygame Drawing ===
    win.fill(bg_color)

    # Move plane (2D only)
    if gesture == "LEFT":
        plane.x -= 5
    elif gesture == "RIGHT":
        plane.x += 5
    elif gesture == "UP":
        plane.y -= 5
    elif gesture == "DOWN":
        plane.y += 5
    # FORWARD = no movement, just label

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