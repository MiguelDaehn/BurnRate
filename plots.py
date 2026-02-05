import os
from pathlib import Path
import numpy as np
from thrust import *


def plt_m_parameter(N, param_name, values_to_test, motor: MotorConfig, eta_noz=0.95, Ae_At=6.278):
    """
    Plots and compares multiple configurations of a motor by varying a specific parameter.

    Args:
        N (int): Simulation steps.
        param_name (str): The name of the MotorConfig attribute to vary (e.g., 'Dt', 'L', 'Rho_pct').
        values_to_test (list): A list of values to iterate through for that parameter.
        motor (MotorConfig): The base motor object to use as a template.
    """
    plt.figure(figsize=(12, 5))

    # Create subplots for Pressure and Thrust
    ax1 = plt.subplot(1, 2, 1)
    ax2 = plt.subplot(1, 2, 2)

    for val in values_to_test:
        # 1. Update the specific parameter dynamically
        # This replaces motor[id_prop] = prop with a safe object attribute update
        if hasattr(motor, param_name):
            setattr(motor, param_name, val)
        else:
            print(f"Warning: MotorConfig has no attribute '{param_name}'")
            return

        # 2. Run the simulation
        # Note: calculate_thrust internally calls pressure.py which now uses the
        # pre-processor and Summerfield criterion.
        F, Pc, t, Cf, It = calculate_thrust(N, motor, eta_noz, Ae_At)

        # 3. Plot with descriptive labels
        label_text = f"{param_name}: {val}"
        ax1.plot(t, Pc, label=label_text)
        ax2.plot(t, F, label=label_text)

    # Formatting Pressure Plot
    ax1.set_title("Chamber Pressure Comparison")
    ax1.set_ylabel("Pressure [MPa]")
    ax1.set_xlabel("Time [s]")
    ax1.grid(True)
    ax1.legend()

    # Formatting Thrust Plot
    ax2.set_title("Thrust Comparison")
    ax2.set_ylabel("Thrust [N]")
    ax2.set_xlabel("Time [s]")
    ax2.grid(True)
    ax2.legend()

    plt.tight_layout()
    plt.show()

def plt_AeAt(N,arr_aeat,motor,eta_noz=0.85):
    '''Plots both Thrust (F) and Thrust Coefficient (CF) as a function of time'''
    for aeat in arr_aeat:
        F,Pc,t,Cf,It = calculate_thrust(N,motor,eta_noz,aeat)
        plt.figure(1)
        plt.plot(t,F)
        plt.figure(2)
        plt.plot(t, Cf)
    plt.grid(True)
    plt.show()


def save_array_to_eng_file(data, motor_info, paths):
    """
    Saves the .eng file to multiple destination paths.
    """
    # Extract info
    filename = motor_info['filename']
    name = motor_info['name']
    outer_diameter = motor_info['outer_diameter']
    length = motor_info['length']
    delay_charge_time = motor_info['delay_charge_time']
    propellant_mass = motor_info['propellant_mass']
    total_mass = motor_info['total_mass']
    manufacturer = motor_info['manufacturer']

    if not filename.endswith('.eng'):
        filename += '.eng'

    # Create the standard OpenRocket header
    header = f"{name} {outer_diameter} {length} {delay_charge_time} {propellant_mass} {total_mass} {manufacturer}"

    # Loop through all requested paths (e.g., local results AND OpenRocket folder)
    for p in paths:
        try:
            target_dir = Path(p)

            # Create directory if it doesn't exist
            target_dir.mkdir(parents=True, exist_ok=True)

            full_path = target_dir / filename

            np.savetxt(full_path, data, fmt='%.6f', delimiter='\t', header=header, comments='')
            print(f"✅ Successfully exported to: {full_path}")

        except Exception as e:
            print(f"❌ Error saving to {p}: {e}")


def plot_log_pressure(t, Pc_MPa, motor_name):
    """
    Plots pressure vs time on a log-log scale.
    Resolves TODO #4.
    """
    import matplotlib.pyplot as plt

    # Filter out values <= 0 for log compatibility
    # t[0] is often 0.0, so we start from the second element
    mask = (t > 0) & (Pc_MPa > 0)
    t_log = t[mask]
    P_log = Pc_MPa[mask]

    plt.figure(figsize=(8, 6))
    plt.loglog(t_log, P_log, label='Chamber Pressure', color='blue', linewidth=2)

    # Adding 'minor' grid lines makes log scales readable
    plt.grid(True, which="both", ls="-", alpha=0.5)

    plt.xlabel('Time [s] (Log Scale)')
    plt.ylabel('Pressure [MPa] (Log Scale)')
    plt.title(f'Log-Log Performance: {motor_name}')
    plt.legend()
    plt.show()


def main():

    return 0

if __name__ == '__main__':
    main()