"""
AirplaneRoshan: Professional Flight Controller
==============================================
Main Entry Point.
Coordinates Vision AI, Network Telemetry, and User Interface.

Author: BishnuGautam1112 (Refactored)
"""

import cv2
import time
import logging
import sys

# Import Configuration
try:
    import config
except ImportError:
    print("❌ FATAL: config.py not found. Please restore the file.")
    sys.exit(1)

# Import Local Modules
from modules.gesture_engine import GestureEngine
from modules.network_manager import NetworkBridge

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("Main")


def render_hud(frame, roll, pitch, is_tracking, fps):
    """
    Draws the Premium Heads-Up Display (HUD) overlay.
    Keeps the main loop clean by isolating UI logic.
    """
    h, w, _ = frame.shape
    cx, cy = w // 2, h // 2

    # --- STYLE CONFIG ---
    COLOR_ACTIVE = (0, 255, 0)  # Neon Green
    COLOR_IDLE = (0, 0, 255)  # Red
    COLOR_UI = (200, 200, 200)  # Light Gray
    COLOR_TEXT = (255, 255, 255)  # White

    status_color = COLOR_ACTIVE if is_tracking else COLOR_IDLE

    # 1. Center Crosshair (Static Reference)
    # Horizontal & Vertical lines
    cv2.line(frame, (cx - 20, cy), (cx + 20, cy), COLOR_UI, 1)
    cv2.line(frame, (cx, cy - 20), (cx, cy + 20), COLOR_UI, 1)
    # Central Box
    cv2.rectangle(frame, (cx - 5, cy - 5), (cx + 5, cy + 5), COLOR_UI, 1)

    # 2. Virtual Joystick (Dynamic Indicator)
    # Map float values (-1.0 to 1.0) to screen pixels relative to center
    # Multiplier 0.3 means the dot moves 30% of screen width max
    joy_x = int(cx + (roll * (w * 0.3)))
    joy_y = int(cy + (pitch * (h * 0.3)))

    # Draw Tether Line (Visualizes the 'pull')
    if is_tracking:
        cv2.line(frame, (cx, cy), (joy_x, joy_y), status_color, 2)

    # Draw Joystick Knob
    cv2.circle(frame, (joy_x, joy_y), 15, status_color, -1)  # Filled
    cv2.circle(frame, (joy_x, joy_y), 18, COLOR_TEXT, 2)  # Outline

    # 3. Telemetry Panel (Bottom Left)
    # Background Box for readability
    panel_h = 90
    cv2.rectangle(frame, (10, h - panel_h), (220, h - 10), (0, 0, 0), -1)

    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(frame, f"FPS  : {int(fps)}", (25, h - 65), font, 0.6, COLOR_TEXT, 1)

    # Roll/Pitch Text (Color changes based on intensity)
    # If banking hard (>0.8), text turns Yellow
    rp_color = (0, 255, 255) if abs(roll) > 0.8 or abs(pitch) > 0.8 else COLOR_ACTIVE

    cv2.putText(frame, f"ROLL : {roll:+.2f}", (25, h - 40), font, 0.6, rp_color, 1)
    cv2.putText(frame, f"PITCH: {pitch:+.2f}", (25, h - 15), font, 0.6, rp_color, 1)


def main():
    """Main Execution Loop."""

    logger.info("--- ✈️ AirplaneRoshan Pro Launching ---")
    logger.info(f"Targeting Unreal Engine at {config.UDP_IP}:{config.UDP_PORT}")

    # 1. Initialize Modules
    try:
        engine = GestureEngine()
        # NetworkBridge is used as a Context Manager (with statement)
        # This ensures the socket closes safely when we exit
        network_ctx = NetworkBridge(config.UDP_IP, config.UDP_PORT)
    except Exception as e:
        logger.critical(f"Initialization Failed: {e}")
        return

    # 2. Setup Camera
    logger.info(f"Opening Camera ID {config.WEBCAM_ID}...")
    cap = cv2.VideoCapture(config.WEBCAM_ID)

    # Force Camera Resolution (Optimization)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)
    cap.set(cv2.CAP_PROP_FPS, config.FPS_LIMIT)

    if not cap.isOpened():
        logger.critical("❌ Error: Could not open webcam. Check connection.")
        return

    logger.info("✅ System Online. Press 'Q' to Exit.")

    # Timing variables
    prev_frame_time = 0
    new_frame_time = 0

    # 3. The Loop
    # We use a context manager for the network to ensure cleanup
    with network_ctx as network:
        try:
            while True:
                # A. Capture
                success, frame = cap.read()
                if not success:
                    logger.warning("Frame dropped or camera disconnected.")
                    break

                # B. Process (Vision & Math)
                # 'frame' is updated with skeleton drawing inside engine.process
                processed_frame, roll, pitch, is_tracking = engine.process(frame)

                # C. Transmit (Networking)
                network.send_telemetry({
                    "roll": roll,
                    "pitch": pitch,
                    "active": is_tracking
                })

                # D. Render (UI)
                # Calculate FPS using High-Res Timer
                new_frame_time = time.perf_counter()
                fps = 1 / (new_frame_time - prev_frame_time) if prev_frame_time > 0 else 0
                prev_frame_time = new_frame_time

                render_hud(processed_frame, roll, pitch, is_tracking, fps)

                # E. Display
                cv2.imshow("AirplaneRoshan Controller", processed_frame)

                # F. Exit Condition
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    logger.info("Shutdown signal received.")
                    break

        except KeyboardInterrupt:
            logger.info("User forced exit (Ctrl+C).")
        except Exception as e:
            logger.error(f"Unexpected runtime error: {e}")
        finally:
            # G. Cleanup
            logger.info("Releasing resources...")
            cap.release()
            cv2.destroyAllWindows()
            logger.info("--- Session Ended ---")


if __name__ == "__main__":
    main()