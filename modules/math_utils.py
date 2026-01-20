"""
Math Utilities Module
=====================
Provides high-performance mathematical filtering and coordinate mapping
functions for the flight control system.

Logic:
    - Exponential Moving Average (EMA) for jitter reduction.
    - Linear interpolation (Lerp) and remapping for coordinate systems.
    - Deadzone calculations to prevent drift.
"""

from typing import Union


class Stabilizer:
    """
    A stateful filter using Exponential Moving Average (EMA).

    This acts as a 'Virtual Shock Absorber'. It takes noisy input (hand shaking)
    and returns smooth output based on the 'alpha' factor.
    """

    # Optimization: Reduces memory footprint for high-frequency objects
    __slots__ = ('_alpha', '_state')

    def __init__(self, alpha: float = 0.5, initial_value: float = 0.0):
        """
        Initialize the stabilizer.

        :param alpha: Smoothing factor between 0.0 (Frozen) and 1.0 (No smoothing).
                      - 0.1: Very Slow/Smooth (Cinematic)
                      - 0.9: Very Fast/Twitchy (Combat)
        :param initial_value: Starting value for the filter.
        :raises ValueError: If alpha is not between 0 and 1.
        """
        if not (0.0 <= alpha <= 1.0):
            raise ValueError(f"Alpha must be between 0.0 and 1.0. Got: {alpha}")

        self._alpha = alpha
        self._state = initial_value

    def update(self, measurement: float) -> float:
        """
        Update the filter with a new raw measurement.

        Formula: Output = (Input * alpha) + (Previous_Output * (1 - alpha))

        :param measurement: The raw, noisy value from the sensor/camera.
        :return: The smoothed value.
        """
        self._state = (measurement * self._alpha) + (self._state * (1.0 - self._alpha))
        return self._state

    def reset(self, value: float = 0.0) -> None:
        """Hard reset the internal state (useful when hand is lost/regained)."""
        self._state = value


# ==========================================
# 🛠️ Static Utility Functions
# ==========================================

def map_range_clamped(
        value: float,
        in_min: float,
        in_max: float,
        out_min: float,
        out_max: float
) -> float:
    """
    Re-maps a number from one range to another and clamps the result.
    Equivalent to Arduino's map() but with safety checks.

    Example: Converting 0.0-1.0 (Screen) to -45 to 45 (Degrees).

    :return: Float mapped to the output range.
    """
    # 1. Safety Check: Prevent division by zero
    if abs(in_max - in_min) < 1e-9:
        return out_min

    # 2. Linear Interpolation
    slope = (out_max - out_min) / (in_max - in_min)
    result = out_min + slope * (value - in_min)

    # 3. Clamping (Ensure we don't exceed physical limits)
    if out_min < out_max:
        return max(out_min, min(out_max, result))
    else:
        return max(out_max, min(out_min, result))


def apply_deadzone(value: float, threshold: float) -> float:
    """
    Applies a deadzone to the input.
    If value is within [-threshold, threshold], returns 0.0.

    This prevents the plane from drifting when the user thinks
    their hand is centered but is slightly off.

    :param value: The input value (centered at 0).
    :param threshold: The absolute limit to ignore.
    :return: Processed float.
    """
    if abs(value) < threshold:
        return 0.0
    return value


# ==========================================
# 🧪 Unit Test Block
# ==========================================
if __name__ == "__main__":
    # This block allows you to run this file specifically to test if the math works.
    # Run: python modules/math_utils.py

    print("--- Running Math Diagnostics ---")

    # Test 1: Smoothing
    stab = Stabilizer(alpha=0.1)  # Heavy smoothing
    inputs = [0.0, 1.0, 1.0, 1.0, 0.0]  # Sudden spike
    print(f"Smoothing Input {inputs}:")
    for x in inputs:
        print(f" -> In: {x} | Out: {stab.update(x):.4f}")

    # Test 2: Deadzone
    val = 0.05
    dz = 0.1
    print(f"\nDeadzone Check (Val: {val}, Threshold: {dz}):")
    print(f" -> Result: {apply_deadzone(val, dz)} (Expected: 0.0)")

    # Test 3: Mapping
    mapped = map_range_clamped(0.5, 0.0, 1.0, -100, 100)
    print(f"\nMapping Check (0.5 in 0..1 to -100..100):")
    print(f" -> Result: {mapped} (Expected: 0.0)")

    print("\n--- Diagnostics Complete ---")