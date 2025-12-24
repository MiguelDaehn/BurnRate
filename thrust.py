import numpy as np
from startup import *
from pressure import calculate_pressure_parameters
from motor_library import MotorConfig


def thrust_coefficient(P2: float,
                       Pc: float,
                       k: float,
                       eta_noz: float,
                       Ae_At: float,
                       patm_pa: float = 101325.0) -> float:
    """
    Calculates the thrust coefficient (CF) for a rocket nozzle.
    Includes safety checks to prevent numerical instability.
    """
    if Pc <= patm_pa or Pc <= 0:
        return 0.0

    # Prevent division by zero and invalid exponents
    if np.isclose(k, 1.0, atol=1e-5):
        k = 1.0001

    # Isentropic term calculation
    try:
        isentropic_term = (2 * k ** 2 / (k - 1)) * (2 / (k + 1)) ** ((k + 1) / (k - 1))
        pressure_ratio = P2 / Pc

        # Ensure pressure_term isn't negative due to rounding
        pressure_term = max(0.0, 1 - pressure_ratio ** ((k - 1) / k))

        cf_isentropic = eta_noz * np.sqrt(isentropic_term * pressure_term)

        # Pressure thrust term
        pressure_thrust = (P2 - patm_pa) / Pc * Ae_At

        # Total CF
        CF = cf_isentropic + pressure_thrust

        # Physical bounds check to prevent "surges"
        return float(np.clip(CF, 0, 2.5))

    except (ValueError, ZeroDivisionError):
        return 0.0


def calculate_thrust(N, motor: MotorConfig, eta_noz, Ae_At):
    """
    Calculates Thrust and Impulse parameters using the MotorConfig object.

    Args:
        N: Discretization steps
        motor: MotorConfig object from motor_library
        eta_noz: Nozzle efficiency (e.g., 0.85)
        Ae_At: Expansion ratio
    """
    # 1. Get pressure data using the refactored MotorConfig-based function
    t, Pc_MPa, k, tbout, r_avg, m_grain0 = calculate_pressure_parameters(int(N), motor)

    Pc_Pa = Pc_MPa * 1e6
    Np = len(t)

    # 2. Initializing empty arrays
    P2_Pa = np.zeros_like(t)
    Cf = np.zeros_like(t)
    F = np.zeros_like(t)
    It_arr = np.zeros_like(t)

    # 3. Setup Nozzle Constants
    # Using the robust Mach solver
    Me = find_M2(Ae_At, k)

    # Throat area in m^2
    At_m2 = (np.pi / 4) * (motor.Dt ** 2) / 1e6

    # Lambda for Exit Pressure (P2) based on Isentropic Flow
    calc_P2 = lambda pc: pc / (1 + (k - 1) / 2 * Me ** 2) ** (k / (k - 1))

    # 4. Main Thrust Loop
    for i in range(Np):
        if Pc_Pa[i] < patm_pa:
            # Below atmospheric pressure, the motor isn't producing usable thrust
            continue

        # STABILITY FIX: Summerfield Criterion / Flow Separation
        # If exit pressure drops too low, the flow separates from the nozzle walls.
        # We clip P2 to 0.35 * Patm to prevent the negative pressure 'surge'.
        raw_P2 = calc_P2(Pc_Pa[i])
        P2_Pa[i] = max(raw_P2, 0.35 * patm_pa)

        # Calculate CF
        cf = thrust_coefficient(
            P2=P2_Pa[i],
            Pc=Pc_Pa[i],
            k=k,
            eta_noz=eta_noz,
            Ae_At=Ae_At,
            patm_pa=patm_pa
        )
        Cf[i] = cf

        # Calculate Instantaneous Thrust (F = At * Cf * Pc)
        F[i] = At_m2 * Cf[i] * Pc_Pa[i]

        # Calculate Incremental Total Impulse (Integral of F dt)
        if i > 0:
            dt = t[i] - t[i - 1]
            It_arr[i] = (F[i] + F[i - 1]) / 2 * dt

    # 5. Performance Metrics
    total_impulse = np.sum(It_arr)
    # Isp = Total Impulse / (Weight of propellant)
    isp = total_impulse / (g0 * m_grain0) if m_grain0 > 0 else 0

    return F, Pc_MPa, t, Cf, total_impulse


def thrust_pressure_plot(N, motor: MotorConfig, Ae_At):
    """
    Helper function to simulate and plot results.
    """
    F, Pc, t, Cf, It = calculate_thrust(N, motor, 0.85, Ae_At)

    plt.figure(figsize=(10, 8))

    plt.subplot(2, 1, 1)
    plt.plot(t, Pc, color='blue')
    plt.title(f'Simulation: {motor.name}')
    plt.ylabel('Chamber Pressure [MPa]')
    plt.grid(True)

    plt.subplot(2, 1, 2)
    plt.plot(t, F, color='red')
    plt.ylabel('Thrust [N]')
    plt.xlabel('Time [s]')
    plt.grid(True)

    plt.tight_layout()
    plt.show()

    return F, Pc, t


if __name__ == '__main__':
    from motor_library import load_motor

    # Test with a known motor
    motor = load_motor("motor_12")
    thrust_pressure_plot(1000, motor, Ae_At=6.278)