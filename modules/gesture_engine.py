"""
Gesture Engine Module
=====================
The core vision processing unit.
It wraps Google MediaPipe to detect hands and converts raw wrist coordinates
into normalized Virtual Joystick values (-1.0 to 1.0).
"""

import cv2
import sys
import logging
from typing import Tuple, Optional, Any

# Internal Project Imports
try:
    import config
    from modules.math_utils import Stabilizer, apply_deadzone, map_range_clamped
except ImportError:
    # Fallback to allow running this file directly for testing
    sys.path.append("..")
    import config
    from modules.math_utils import Stabilizer, apply_deadzone, map_range_clamped

# Setup Logger
logger = logging.getLogger(__name__)


class GestureEngine:
    """
    Analyzes webcam frames to extract flight control telemetry.
    """

    def __init__(self):
        logger.info("Initializing Gesture Engine...")

        # 1. Initialize MediaPipe (With Crash Protection)
        self._init_mediapipe()

        # 2. Initialize Physics Stabilizers
        # We create separate filters for Roll (X) and Pitch (Y)
        self.roll_filter = Stabilizer(alpha=config.SMOOTHING_FACTOR)
        self.pitch_filter = Stabilizer(alpha=config.SMOOTHING_FACTOR)

        logger.info("Gesture Engine Ready.")

    def _init_mediapipe(self) -> None:
        """
        Safely loads MediaPipe. If Protobuf is incompatible, it warns the user.
        """
        try:
            import mediapipe as mp
            self.mp_hands = mp.solutions.hands
            self.mp_draw = mp.solutions.drawing_utils
            self.mp_styles = mp.solutions.drawing_styles

            self.hands = self.mp_hands.Hands(
                max_num_hands=1,  # Single hand control is more precise
                model_complexity=0,  # 0 = Fastest, 1 = Accurate
                min_detection_confidence=0.7,
                min_tracking_confidence=0.7
            )
        except (ImportError, AttributeError) as e:
            logger.critical("MediaPipe installation is corrupted!")
            logger.critical("Run: pip install mediapipe==0.10.9 protobuf==3.20.3")
            raise RuntimeError("Critical dependency failure.") from e

    def process(self, frame: Any) -> Tuple[Any, float, float, bool]:
        """
        The main pipeline function.

        :param frame: Raw BGR image from OpenCV.
        :return: Tuple(processed_frame, roll, pitch, is_tracking)
        """
        # 1. Image Pre-processing
        # Flip horizontally for mirror effect (intuitive for users)
        frame = cv2.flip(frame, 1)

        # Convert to RGB (MediaPipe requires RGB)
        # Note: We pass by reference to save memory, but MP needs read-only
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_rgb.flags.writeable = False

        # 2. Inference (The heavy AI lifting)
        results = self.hands.process(frame_rgb)

        # 3. Data Extraction
        raw_roll = 0.0
        raw_pitch = 0.0
        is_tracking = False

        if results.multi_hand_landmarks:
            is_tracking = True
            # Get the first hand found
            hand_landmarks = results.multi_hand_landmarks[0]

            # Visualize the skeleton
            self._draw_skeleton(frame, hand_landmarks)

            # Calculate physics
            raw_roll, raw_pitch = self._compute_vectors(hand_landmarks)

        # 4. Physics Smoothing
        # We run this EVERY frame. If tracking is lost, raw values are 0.0,
        # so the plane will smoothly return to center (auto-leveling).
        smooth_roll = self.roll_filter.update(raw_roll)
        smooth_pitch = self.pitch_filter.update(raw_pitch)

        return frame, smooth_roll, smooth_pitch, is_tracking

    def _compute_vectors(self, landmarks) -> Tuple[float, float]:
        """
        Converts wrist position into normalized joystick coordinates.
        """
        # Landmark 0 is the Wrist.
        # Coordinates are normalized [0.0, 1.0] by MediaPipe.
        wrist = landmarks.landmark[0]

        # 1. Center Offset Calculation
        # Center of screen is (0.5, 0.5).
        dx = wrist.x - 0.5
        dy = wrist.y - 0.5

        # 2. Apply Deadzone
        # If the hand is very close to center, ignore small jitters.
        dx = apply_deadzone(dx, config.DEADZONE)
        dy = apply_deadzone(dy, config.DEADZONE)

        # 3. Sensitivity Scaling & Clamping
        # Example: If Sensitivity is 2.0, moving halfway to edge counts as full turn.
        roll = map_range_clamped(dx * config.SENSITIVITY, -0.5, 0.5, -1.0, 1.0)
        pitch = map_range_clamped(dy * config.SENSITIVITY, -0.5, 0.5, -1.0, 1.0)

        # 4. Invert Pitch (Optional Flight Sim Style)
        if config.INVERT_PITCH:
            pitch = -pitch

        return roll, pitch

    def _draw_skeleton(self, frame, landmarks):
        """Helper to draw high-quality hand connections."""
        self.mp_draw.draw_landmarks(
            frame,
            landmarks,
            self.mp_hands.HAND_CONNECTIONS,
            self.mp_styles.get_default_hand_landmarks_style(),
            self.mp_styles.get_default_hand_connections_style()
        )