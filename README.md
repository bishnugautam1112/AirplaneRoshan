# ✈️ AirplaneRoshan Pro
### The AI-Powered Virtual Flight Controller for Unreal Engine 5

<div align="center">

[![Status](https://img.shields.io/badge/Status-Stable-success?style=for-the-badge)](https://github.com/bishnugautam1112/AirplaneRoshan)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Unreal Engine](https://img.shields.io/badge/Unreal%20Engine-5.x-0E1128?style=for-the-badge&logo=unrealengine&logoColor=white)](https://www.unrealengine.com/)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-Computer%20Vision-00C853?style=for-the-badge&logo=google&logoColor=white)](https://developers.google.com/mediapipe)
[![Protocol](https://img.shields.io/badge/Protocol-UDP%20Socket-FF5722?style=for-the-badge)](https://en.wikipedia.org/wiki/User_Datagram_Protocol)
[![License](https://img.shields.io/badge/License-MIT-purple?style=for-the-badge)](LICENSE)

</div>

<br>

> **"Look , No Hands!"** — *Actually, it's all hands.* 
> 
> **AirplaneRoshan Pro** transforms your standard webcam into a high-precision, zero-latency flight stick. By combining Google's MediaPipe Computer Vision with UDP networking, it allows you to fly 3D jets in Unreal Engine 5 using natural hand gestures.


## 📑 Table of Contents
1. [🌟 Key Features](#-key-features)
2. [🏗️ System Architecture](#%EF%B8%8F-system-architecture)
3. [🧠 How It Works](#-how-it-works-under-the-hood)
4. [🚀 Installation Guide](#-installation-guide)
5. [🔌 Unreal Engine Integration](#-unreal-engine-integration)
6. [⚙️ Configuration](#%EF%B8%8F-configuration)
7. [🎮 Controls](#-flight-controls)
8. [🤝 Contribution](#-contribution)

---

## 🌟 Key Features

*   **⚡ Zero-Latency UDP Bridge:** Uses asynchronous socket communication to blast telemetry data to the game engine in real-time (60+ Hz).
*   **🌊 Liquid Smooth Technology:** Implements **Exponential Moving Average (EMA)** mathematical filters to eliminate webcam jitter, providing AAA-game quality control.
*   **🎮 Virtual Joystick Physics:** Calculates true analog input (0% to 100% intensity) based on hand distance from the center, identical to a physical HOTAS controller.
*   **🛡️ Enterprise-Grade Modularity:** Clean, class-based code structure (`GestureEngine`, `Stabilizer`, `NetworkBridge`) designed for scalability.
*   **🔌 Plug-and-Play:** Auto-detects camera hardware and handles network errors gracefully.

---

## 🏗️ System Architecture

The project operates on a **Client-Server model**. The Python script acts as the Input Controller (Client), and Unreal Engine acts as the Physics Simulation (Server).

```mermaid
graph LR
    subgraph "Python Client (Controller)"
        A[Webcam Feed] -->|Raw Frames| B(GestureEngine)
        B -->|Hand Landmarks| C{Vector Math}
        C -->|Raw Coordinates| D[Stabilizer Filter]
        D -->|Smooth Data| E[NetworkBridge]
    end

    E -->|UDP JSON Packet| F((Unreal Engine 5))

    subgraph "Unreal Server (Game)"
        F -->|Parse JSON| G[Blueprint Logic]
        G -->|Apply Rotation| H[Jet Pawn]
    end
```

### The Data Packet
Every frame, the Python client sends a lightweight JSON packet to `127.0.0.1:5005`:

```json
{
  "roll": 0.542,
  "pitch": -0.123,
  "active": true
}
```

---

## 🧠 How It Works (Under the Hood)

This isn't just "if hand left, go left." We use vector mathematics to create a virtual analog stick.

1.  **Normalization:** MediaPipe normalizes the hand coordinates to `[0.0, 1.0]`. Center is `(0.5, 0.5)`.
2.  **Vector Calculation:** We calculate the deviation ($\Delta$) of the wrist from the center.
3.  **Deadzone:** Small shakes in the center are ignored (clamped to 0).
4.  **Stabilization (EMA):** Raw webcam data is noisy. We use an **Exponential Moving Average** filter to smooth the output:
   ```  $$ S_t = \alpha \cdot X_t + (1 - \alpha) \cdot S_{t-1} $$ ```

---

## 🚀 Installation Guide

### Prerequisites
*   **Python 3.10 or 3.11** (⚠️ Python 3.13 is NOT currently supported by MediaPipe).
*   A Webcam.
*   Unreal Engine 4.27 or 5.x.

### Step 1: Clone the Repository
```bash
git clone https://github.com/R00SHAN/AirplaneRoshan.git
cd AirplaneRoshan
```

### Step 2: Setup Environment
It is highly recommended to use a virtual environment.

```bash
# Windows
python -m venv .venv
.\.venv\Scripts\activate

# Mac/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Dependencies (CRITICAL)
This project requires specific versions of MediaPipe and Protobuf to function correctly on Windows.

```bash
# Run this exact command to avoid version conflicts
pip install mediapipe==0.10.9 protobuf==3.20.3 opencv-python numpy
```

### Step 4: System Check
Run the diagnostic tool to ensure everything is ready.
```bash
python system_check.py
```
If you see **[ OK ]** across the board, you are ready to fly.

---

## 🔌 Unreal Engine Integration

To make your jet respond to Python, you need to set up a UDP Receiver in Unreal Engine.

**👉 [Click Here for the Step-by-Step Connection Guide](HOW_TO_CONNECT.md)**

*Short Version:*
1.  Install the **"UDP Socket Receiver"** plugin in UE5.
2.  Create a Blueprint to listen on IP `127.0.0.1` and Port `5005`.
3.  Parse the incoming JSON string (`{"roll":...}`) into Float variables.
4.  Apply `AddActorLocalRotation` to your Jet Pawn.

---

## ⚙️ Configuration

You can tweak the feel of the flight without touching the code. Open `config.py`:

| Parameter | Default | Description |
| :--- | :--- | :--- |
| `UDP_IP` | "127.0.0.1" | IP Address of the game engine. |
| `UDP_PORT` | 5005 | Port to send data to. |
| `SMOOTHING_FACTOR` | 0.15 | **0.1** = Heavy/Slow, **0.9** = Twitchy/Fast. |
| `DEADZONE` | 0.12 | How much center movement to ignore (0.0 to 0.5). |
| `SENSITIVITY` | 1.6 | Multiplier for hand movement. |
| `INVERT_PITCH` | False | Set `True` for Flight Sim controls (Pull back to climb). |

---

## 🎮 Flight Controls

The system uses a **Virtual Joystick** method. Imagine an invisible stick in the center of your camera frame.

| Gesture | Movement | Data Sent | Effect |
| :--- | :--- | :--- | :--- |
| **Move Hand Right** | Roll Right | `roll > 0` | Plane banks Right |
| **Move Hand Left** | Roll Left | `roll < 0` | Plane banks Left |
| **Move Hand Up** | Pitch Up | `pitch < 0` | Plane Nose Up (Climb) |
| **Move Hand Down** | Pitch Down | `pitch > 0` | Plane Nose Down (Dive) |
| **Remove Hand** | Auto-Level | `roll: 0` | Plane stabilizes automatically |

---

## 🤝 Contribution

This project is open-source and we welcome contributions! 

**Current Contributors:**
*   **R00SHAN** - Original Creator
*   **BishnuGautam1112** - Lead Refactor Engineer & Architecture Design

### How to contribute:
1.  Fork the repo.
2.  Create a feature branch (`git checkout -b feature/AmazingNewFeature`).
3.  Commit your changes.
4.  Push to the branch.
5.  Open a Pull Request.

---

## 📄 License

Distributed under the **MIT License**. See `LICENSE` for more information.

---

<p align="center">
  <b>Built with ❤️ by Developers, for Developers.</b><br>
  <i>Fly safe, Pilot.</i>
</p>
```
