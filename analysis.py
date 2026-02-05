import os
import platform
import numpy as np

# Imports from all layers
from motor_library import load_motor, process_motor_specs
from thrust import calculate_thrust
from plots import save_array_to_eng_file
from reporting import create_pdf_report


def run_motor_analysis(motor_name: str, auto_size: bool = False):
    """
    Orchestrates the full simulation pipeline.

    Args:
        motor_name: The ID of the motor in MOTOR_LIBRARY.
        auto_size: If True, calculates and applies the optimal Throat Diameter (Dt)
                   to match the motor's P_target before simulating.
    """
    print(f"🚀 Processing: {motor_name}...")

    # 1. Load Motor
    try:
        motor = load_motor(motor_name)
    except Exception as e:
        print(f"❌ Failed to load {motor_name}: {e}")
        return

    # 2. Auto-Sizing Logic (Nakka's Feature)
    if auto_size:
        print(f"   ⚙️ Optimization enabled. Target Pressure: {motor.P_target} MPa")

        # Get the ideal geometry based on P_target
        specs = process_motor_specs(motor)
        dt_ideal = specs['dt_ideal']

        # Feedback to user
        diff = dt_ideal - motor.Dt
        print(f"   🔧 Adjusting Throat Diameter (Dt):")
        print(f"      Old: {motor.Dt:.3f} mm")
        print(f"      New: {dt_ideal:.3f} mm (Delta: {diff:+.3f} mm)")

        # APPLY THE CHANGE
        motor.Dt = dt_ideal

    # 3. Run Simulation
    # Now using the potentially modified motor.Dt
    try:
        F, Pc, t, Cf, It = calculate_thrust(10000, motor, 0.95, 6.278)
    except Exception as e:
        print(f"❌ Simulation failed for {motor_name}: {e}")
        return

    # 4. Setup Export Paths
    base_dir = os.path.abspath(os.path.dirname(__file__))
    path_eng_local = os.path.join(base_dir, 'data', 'results', 'eng_files')
    path_pdf_local = os.path.join(base_dir, 'data','results', 'reports')

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
    print(f"   Refreshed OpenRocket file at: {path_eng_or}")

    # 6. Generate Report
    pdf_path = os.path.join(path_pdf_local, f"{motor.name}_Report.pdf")
    create_pdf_report(motor, t, Pc, F, It, filename=pdf_path)

    print(f"✅ {motor_name} analysis complete.\n")