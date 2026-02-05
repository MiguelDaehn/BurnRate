import os
import platform
import numpy as np

# Imports from your existing library
from motor_library import load_motor
from thrust import calculate_thrust
from plots import save_array_to_eng_file
from reporting import create_pdf_report


def run_motor_analysis(motor_name: str):
    """
    Orchestrates the full simulation pipeline:
    1. Loads motor config
    2. Simulates burn
    3. Exports OpenRocket .eng file (auto-detecting OS path)
    4. Generates PDF Report
    """
    print(f"🚀 Processing: {motor_name}...")

    # 1. Load & Simulate
    try:
        motor = load_motor(motor_name)
        # Using your standard simulation parameters
        F, Pc, t, Cf, It = calculate_thrust(10000, motor, 0.95, 6.278)
    except Exception as e:
        print(f"❌ Failed to load or simulate {motor_name}: {e}")
        return

    # 2. Setup Export Paths
    base_dir = os.path.abspath(os.path.dirname(__file__))
    path_eng_local = os.path.join(base_dir, 'data', 'results', 'eng_files')
    path_pdf_local = os.path.join(base_dir, 'data', 'results', 'reports')

    # OS-Agnostic OpenRocket Path
    if platform.system() == "Windows":
        path_eng_or = os.path.join(os.getenv('APPDATA'), 'OpenRocket', 'ThrustCurves')
    else:
        path_eng_or = os.path.expanduser('~/.openrocket/ThrustCurves')

    # Ensure directories exist
    for p in [path_eng_local, path_pdf_local, path_eng_or]:
        os.makedirs(p, exist_ok=True)

    # 3. Export .eng Files (OpenRocket)
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

    # Save to both locations
    save_array_to_eng_file(data_stack, info_eng, path_eng_local)
    save_array_to_eng_file(data_stack, info_eng, path_eng_or)
    print(f"   Refreshed OpenRocket file at: {path_eng_or}")

    # 4. Export PDF Report
    pdf_path = os.path.join(path_pdf_local, f"{motor.name}_Report.pdf")
    create_pdf_report(motor, t, Pc, F, It, filename=pdf_path)

    print(f"✅ {motor_name} analysis complete.\n")