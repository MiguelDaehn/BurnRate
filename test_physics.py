import numpy as np
from motor_library import load_motor
from thrust import calculate_thrust


def test_motor_12_consistency():
    """
    Verifies that the simulation of Motor 12 produces expected physical results.
    Resolves TODO #14.
    """
    # 1. Setup baseline values (These are the "correct" values from your previous runs)
    EXPECTED_PEAK_P = 1.345  # MPa
    EXPECTED_IMPULSE = 398.5  # Ns
    TOLERANCE = 0.02  # 2% allowable deviation

    # 2. Run current simulation
    motor = load_motor("motor_12")
    F, Pc_MPa, t, Cf, It = calculate_thrust(10000, motor, 0.95, 6.278)

    current_peak_p = max(Pc_MPa)
    current_impulse = It

    # 3. Validation Logic
    p_error = abs(current_peak_p - EXPECTED_PEAK_P) / EXPECTED_PEAK_P
    it_error = abs(current_impulse - EXPECTED_IMPULSE) / EXPECTED_IMPULSE

    print(f"--- Physics Validation: {motor.name} ---")

    if p_error < TOLERANCE and it_error < TOLERANCE:
        print("✅ PASS: Physics engine is consistent.")
    else:
        print("❌ FAIL: Significant drift detected!")
        if p_error >= TOLERANCE:
            print(f"   Pressure Error: {p_error:.2%} (Target: {EXPECTED_PEAK_P})")
        if it_error >= TOLERANCE:
            print(f"   Impulse Error: {it_error:.2%} (Target: {EXPECTED_IMPULSE})")


if __name__ == "__main__":
    test_motor_12_consistency()