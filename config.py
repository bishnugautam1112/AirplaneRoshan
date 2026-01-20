"""
AirplaneRoshan: Configuration Settings
======================================
Central repository for all tunable parameters.
Modify these values to change the flight behavior without touching code.
"""

# ==========================================
# 📡 NETWORK CONFIGURATION
# ==========================================
# The IP address of the machine running Unreal Engine.
# Use "127.0.0.1" if Unreal is on the same computer.
UDP_IP = "127.0.0.1"

# The port Unreal Engine is listening on.
# Ensure your UE5 UDP Receiver matches this number.
UDP_PORT = 5005

# ==========================================
# 📷 CAMERA SETTINGS
# ==========================================
# 0 is usually the default webcam. Change to 1 or 2 for external cams.
WEBCAM_ID = 0

# Resolution: 640x480 is the standard sweet spot for low-latency AI.
# Higher resolutions (1280x720) increase CPU load and may cause lag.
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# Target FPS cap to prevent CPU overheating
FPS_LIMIT = 60

# ==========================================
# ✈️ FLIGHT PHYSICS & HANDLING
# ==========================================
# SMOOTHING_FACTOR (0.01 to 1.0)
# Controls the "weight" of the plane.
# 0.1 = Heavy Passenger Jet (Very smooth, slow response)
# 0.9 = F-22 Fighter Jet (Instant response, jittery)
# 0.15 is the "Senior Dev" recommended sweet spot for stability.
SMOOTHING_FACTOR = 0.15

# DEADZONE (0.0 to 0.5)
# Percentage of the screen center that is ignored.
# Prevents the plane from drifting when your hand shakes slightly in the middle.
DEADZONE = 0.12

# SENSITIVITY (1.0 to 3.0)
# Multiplier for hand movement.
# 1.0 = Linear (Move hand to edge for 100% turn)
# 2.0 = Aggressive (Move hand halfway for 100% turn)
SENSITIVITY = 1.6

# INVERT PITCH (True/False)
# True = Pull hand UP to fly DOWN (Like a real joystick/Yoke)
# False = Move hand UP to fly UP (Like a mouse/touchscreen)
INVERT_PITCH = False

# ==========================================
# 🐞 DEBUGGING
# ==========================================
# Set to True to print every packet sent to the console (Spammy!)
DEBUG_PACKETS = False