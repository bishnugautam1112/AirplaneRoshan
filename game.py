import cv2
import mediapipe as mp
import pygame
import threading

# Initialize MediaPipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Shared direction variable
plane_direction = None

# Fist detection logic
def is_fist(hand_landmarks):
    tips = [8, 12, 16, 20]  # Fingertips
    mcps = [5, 9, 13, 17]   # MCP joints
    for tip, mcp in zip(tips, mcps):
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[mcp].y:
            return False
    return True

# Pygame plane window
def run_game():
    global plane_direction
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Gesture-Controlled Plane")
    clock = pygame.time.Clock()

    # Load and resize plane image
    plane_img = pygame.image.load("image.png").convert_alpha()
    plane_img = pygame.transform.scale(plane_img, (300, 200))
    plane_rect = plane_img.get_rect(center=(400, 500))

    running = True
    while running:
        screen.fill((135, 206, 235))  # Sky blue background

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Move plane based on gesture
        if plane_direction == "left" and plane_rect.left > 0:
            plane_rect.x -= 5
        elif plane_direction == "right" and plane_rect.right < 800:
            plane_rect.x += 5
        elif plane_direction == "up" and plane_rect.top > 0:
            plane_rect.y -= 5

        screen.blit(plane_img, plane_rect)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

# Start game in a separate thread
threading.Thread(target=run_game, daemon=True).start()

# MediaPipe gesture detection
cap = cv2.VideoCapture(0)
with mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.8, min_tracking_confidence=0.8) as hands:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb)

        fists = []
        open_hand_y = None

        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                cx = int(hand_landmarks.landmark[0].x * w)
                cy = int(hand_landmarks.landmark[0].y * h)

                if is_fist(hand_landmarks):
                    fists.append(hand_landmarks.landmark[0].x)
                    cv2.circle(frame, (cx, cy), 10, (0, 255, 0), -1)  # Green dot for fist
                else:
                    open_hand_y = hand_landmarks.landmark[0].y
                    cv2.circle(frame, (cx, cy), 10, (0, 255, 255), -1)  # Yellow dot for open hand

        # Gesture logic
        if len(fists) == 2:
            avg_x = sum(fists) / 2
            if avg_x < 0.4:
                plane_direction = "left"
            elif avg_x > 0.6:
                plane_direction = "right"
            else:
                plane_direction = None
        elif open_hand_y is not None and open_hand_y < 0.3:
            plane_direction = "up"
        else:
            plane_direction = None

        cv2.imshow("Gesture Detection", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break

cap.release()
cv2.destroyAllWindows()