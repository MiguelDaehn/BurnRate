import os
import platform
import numpy as np
from scipy.optimize import brentq

# Imports from all layers
from motor_library import load_motor, process_motor_specs
from thrust import calculate_thrust
from plots import save_array_to_eng_file
from reporting import create_pdf_report


def find_optimal_throat(motor, target_p_mpa, tol=1e-3):
    """
    Iteratively solves for the Throat Diameter (Dt) that results
    in exactly the target Peak Pressure.
    """
    print(f"   ⚙️ Auto-Sizing Enabled. Target: {target_p_mpa} MPa")
    print(f"      Iterating to find precise Dt...")

    original_dt = motor.Dt

    # Define the "Error Function" we want to find the root of
    # f(dt) = Peak_Pressure(dt) - Target_Pressure
    def objective(dt_guess):
        motor.Dt = dt_guess
        # Run a faster, lower-res simulation for the optimizer (N=2000)
        # We don't need the full 10,000 steps just to find the peak
        _, Pc, _, _, _ = calculate_thrust(2000, motor, 0.95, 6.278)
        peak_p = np.max(Pc)
        error = peak_p - target_p_mpa
        return error

    # 1. Establish Brackets (Bounds) for the solver
    # Pressure is inversely proportional to Dt.
    # We search +/- 20% of the current Dt.
    dt_min = original_dt * 0.8
    dt_max = original_dt * 1.2

    try:
        # brentq is a robust root-finding algorithm
        dt_opt = brentq(objective, dt_min, dt_max, xtol=tol)

        # Feedback
        diff = dt_opt - original_dt
        print(f"   ✅ Converged! Dt adjusted: {original_dt:.3f} -> {dt_opt:.3f} mm ({diff:+.3f} mm)")
        return dt_opt

    except ValueError:
        print("   ⚠️ Optimization Warning: Target pressure is outside the +/- 20% search range.")
        print("      Reverting to original Dt.")
        return original_dt
    except Exception as e:
        print(f"   ⚠️ Optimization Failed: {e}")
        return original_dt


def run_motor_analysis(motor_name: str, auto_size: bool = False):
    """
    Orchestrates the full simulation pipeline.

    Args:
        motor_name: The ID of the motor in MOTOR_LIBRARY.
        auto_size: If True, iteratively calculates the exact Throat Diameter (Dt)
                   to match the motor's P_target.
    """
    print(f"🚀 Processing: {motor_name}...")

    # 1. Load Motor
    try:
        motor = load_motor(motor_name)
    except Exception as e:
        print(f"❌ Failed to load {motor_name}: {e}")
        return

    # 2. Precise Auto-Sizing
    if auto_size:
        # We assume the target is the one defined in the motor config
        optimal_dt = find_optimal_throat(motor, motor.P_target)
        motor.Dt = optimal_dt

    # 3. Run Final High-Res Simulation
    # Now using the optimized Dt with full resolution (N=10000)
    try:
        F, Pc, t, Cf, It = calculate_thrust(10000, motor, 0.95, 6.278)
    except Exception as e:
        print(f"❌ Simulation failed for {motor_name}: {e}")
        return

    # 4. Setup Export Paths
    base_dir = os.path.abspath(os.path.dirname(__file__))
    path_eng_local = os.path.join(base_dir, 'data/results', 'eng_files')
    path_pdf_local = os.path.join(base_dir, 'data/results', 'reports')

    if platform.system() == "Windows":
        path_eng_or = os.path.join(os.getenv('APPDATA'), 'OpenRocket', 'ThrustCurves')
    else:
        path_eng_or = os.path.expanduser('~/.openrocket/ThrustCurves')

    for p in [path_eng_local, path_pdf_local, path_eng_or]:
        os.makedirs(p, exist_ok=True)

    # 5. Export Data
    info_eng = {
        'filename': f"{motor.name}_sim",
        'name': f"{motor.name} (Simulated)",
        'outer_diameter': f"{motor.De:.1f}",
        'length': f"{motor.L * motor.Ng:.1f}",
        'delay_charge_time': '0',
        'propellant_mass': f"{(It / 1200):.3f}",
        'total_mass': f"{(It / 1000):.3f}",
        'manufacturer': 'TauRocketTeam'
    }

    data_stack = np.column_stack((t, F))

    save_array_to_eng_file(data_stack, info_eng, path_eng_local)
    save_array_to_eng_file(data_stack, info_eng, path_eng_or)
    # print(f"   Refreshed OpenRocket file at: {path_eng_or}")

    # 6. Generate Report
    pdf_path = os.path.join(path_pdf_local, f"{motor.name}_Report.pdf")
    create_pdf_report(motor, t, Pc, F, It, filename=pdf_path)

    print(f"✅ {motor_name} analysis complete.\n")