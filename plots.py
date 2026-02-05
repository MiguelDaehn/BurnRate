import os
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from scipy.interpolate import interp1d
from thrust import *


def plt_m_parameter(N, param_name, values_to_test, motor, eta_noz=0.95, Ae_At=6.278):
    plt.figure(figsize=(12, 5))
    ax1 = plt.subplot(1, 2, 1)
    ax2 = plt.subplot(1, 2, 2)

    for val in values_to_test:
        if hasattr(motor, param_name):
            setattr(motor, param_name, val)
        else:
            print(f"Warning: MotorConfig has no attribute '{param_name}'")
            return

        F, Pc, t, Cf, It = calculate_thrust(N, motor, eta_noz, Ae_At)
        label_text = f"{param_name}: {val}"
        ax1.plot(t, Pc, label=label_text)
        ax2.plot(t, F, label=label_text)

    ax1.set_title("Chamber Pressure Comparison");
    ax1.grid(True);
    ax1.legend()
    ax2.set_title("Thrust Comparison");
    ax2.grid(True);
    ax2.legend()
    plt.tight_layout();
    plt.show()


def plot_log_pressure(t, Pc_MPa, motor_name):
    mask = (t > 0) & (Pc_MPa > 0)
    plt.figure(figsize=(8, 6))
    plt.loglog(t[mask], Pc_MPa[mask], label='Chamber Pressure', color='blue', linewidth=2)
    plt.grid(True, which="both", ls="-", alpha=0.5)
    plt.title(f'Log-Log Performance: {motor_name}')
    plt.legend();
    plt.show()


def resample_data(data, num_points=10000):
    """
    Resamples the Time vs Thrust data to a fixed number of points (default 10k).
    Ensures homogeneity across all exported .eng files.
    """
    t = data[:, 0]
    F = data[:, 1]

    # Create a uniform time grid from start to finish
    t_uniform = np.linspace(t[0], t[-1], num_points)

    # Interpolate Thrust onto the new grid
    # 'linear' is safe; 'fill_value' handles floating point edges
    interpolator = interp1d(t, F, kind='linear', fill_value="extrapolate")
    F_uniform = interpolator(t_uniform)

    return np.column_stack((t_uniform, F_uniform))


def save_array_to_eng_file(data, motor_info, paths, header_comment=None):
    """
    Saves the .eng file to multiple destination paths.
    Automatically resamples data to 10,000 points for consistency.
    """
    # 1. Resample to ensure 10k points
    data_resampled = resample_data(data, num_points=10000)

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

    # Standard OpenRocket format line
    eng_format_line = f"{name} {outer_diameter} {length} {delay_charge_time} {propellant_mass} {total_mass} {manufacturer}"

    if header_comment:
        full_header = f"{header_comment}\n{eng_format_line}"
    else:
        full_header = eng_format_line

    if not isinstance(paths, list):
        paths = [paths]

    for p in paths:
        try:
            target_dir = Path(p)
            target_dir.mkdir(parents=True, exist_ok=True)
            full_path = target_dir / filename

            np.savetxt(full_path, data_resampled, fmt='%.6f', delimiter='\t', header=full_header, comments='')
            print(f"✅ Exported (10k pts): {full_path}")

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