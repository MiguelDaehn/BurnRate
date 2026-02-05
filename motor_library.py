from dataclasses import dataclass
import numpy as np
from startup import dict_prop, properties_table, Ru, pi  # Add this line

@dataclass
class MotorConfig:
    name: str
    prop: str
    Dt: float
    Rho_pct: float
    Ng: int
    L: float
    De: float
    Di: float
    p_min: float = 0.0
    p_max: float = 10.0
    P_target: float = 0.0
    nuc: float = 0.95
    core_surface_inhibited: int = 1
    ends_surface_inhibited: int = 1
    outer_surface_inhibited: int = 0
    o_ring_thickness: float = 0.0 # Added for TODO #10

MOTOR_LIBRARY = {
    "motor_1": {"prop": 'knsb', "Dt": 9.659, "Rho_pct": 0.95, "Ng": 4, "L": 50.0, "De": 45.0, "Di": 25.0, "P_target": 4.5, "core_surface_inhibited": 1, "ends_surface_inhibited": 1, "outer_surface_inhibited": 0},
    "motor_2": {"prop": 'knpsb', "Dt": np.sqrt(81.1 / (np.pi / 4)) , "Rho_pct": 1.912/1.923, "Ng": 2, "L": 65.0, "De": 43.1, "Di": 13.88, "p_min": 3.5, "p_max": 6, "P_target": 4.5, "core_surface_inhibited": 1, "ends_surface_inhibited": 1, "outer_surface_inhibited": 0},
    "motor_4": {"prop": 'knsu', "Dt": 5.0, "Rho_pct": 0.9, "Ng": 1, "L": 81.14, "De": 24.12, "Di": 5.0, "P_target": 2.0, "core_surface_inhibited": 1, "ends_surface_inhibited": 0, "outer_surface_inhibited": 0},
    "motor_5": {"prop": 'knsu', "Dt": 11.0, "Rho_pct": 0.85, "Ng": 1, "L": 80.0, "De": 33.0, "Di": 25.5, "P_target": 1.091, "core_surface_inhibited": 1, "ends_surface_inhibited": 1, "outer_surface_inhibited": 0},
    "motor_7": {"prop": 'knsu', "Dt": 6.0, "Rho_pct": 0.9533, "Ng": 1, "L": 75.0, "De": 25.4, "Di": 15.0, "P_target": 1.091, "core_surface_inhibited": 1, "ends_surface_inhibited": 1, "outer_surface_inhibited": 0},
    "motor_10": {"prop": 'knsu_geprop_02', "Dt": 12.54, "Rho_pct": 0.89, "Ng": 2, "L": 64.1, "De": 48.34, "Di": 17.44, "p_min": 1.2, "p_max": 2.0, "P_target": 1.091, "core_surface_inhibited": 1, "ends_surface_inhibited": 1, "outer_surface_inhibited": 0},
    "motor_11": {"prop": 'knsu_geprop_03', "Dt": 12.54, "Rho_pct": 0.885, "Ng": 2, "L": 59.71, "De": 48.22, "Di": 17.88, "p_min": 0.0, "p_max": 1.6, "P_target": 1.091, "core_surface_inhibited": 1, "ends_surface_inhibited": 1, "outer_surface_inhibited": 0},
    "motor_12": {"prop": 'knsu', "Dt": 12.54, "Rho_pct": 0.9, "Ng": 1, "L": 119.44, "De": 48.22, "Di": 17.88, "p_min": 0.0, "p_max": 1.6, "P_target": 1.091, "core_surface_inhibited": 1, "ends_surface_inhibited": 1, "outer_surface_inhibited": 0},
    "motor_tauzinha": {"prop": 'knsu', "Dt": 12, "Rho_pct": 0.95, "Ng": 2, "L": 70, "De": 48, "Di": 20,
                 "p_min": 0.0, "p_max": 1.6, "P_target": 1.091, "core_surface_inhibited": 1,
                 "ends_surface_inhibited": 1, "outer_surface_inhibited": 0},
    "motor_hadron_04": {"prop": 'knsb', "Dt": 10.3, "Rho_pct": 0.95, "Ng": 3, "L": 60.0, "De": 56.0, "Di": 25.0, "P_target": 4.0, "core_surface_inhibited": 1, "ends_surface_inhibited": 1, "outer_surface_inhibited": 0},
    "motor_quark3_04": {"prop": 'knsb', "Dt": 8.0, "Rho_pct": 0.95, "Ng": 2, "L": 60.0, "De": 56.0, "Di": 25.0, "P_target": 4.0, "core_surface_inhibited": 1, "ends_surface_inhibited": 1, "outer_surface_inhibited": 0}

}

import os
import platform
import numpy as np
from motor_library import load_motor
from thrust import calculate_thrust
from plots import save_array_to_eng_file
from reporting import create_pdf_report


def run_motor_analysis(motor_name: str):
    """
    One-stop function to load a motor, run the simulation, and export all
    required data (OpenRocket .eng and PDF reports) to the correct system paths.

    Usage:
        run_motor_analysis("motor_hadron_04")
    """
    print(f"🚀 Processing: {motor_name}...")

    # 1. Load & Simulate
    # Defaulting to N=10000, eta=0.95, Ae/At=6.278 based on your previous settings
    try:
        motor = load_motor(motor_name)
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

    # Save to Local and OpenRocket folders
    save_array_to_eng_file(data_stack, info_eng, path_eng_local)
    save_array_to_eng_file(data_stack, info_eng, path_eng_or)
    print(f"   Refreshed OpenRocket file at: {path_eng_or}")

    # 4. Export PDF Report
    pdf_path = os.path.join(path_pdf_local, f"{motor.name}_Report.pdf")
    create_pdf_report(motor, t, Pc, F, It, filename=pdf_path)

    print(f"✅ {motor_name} analysis complete.\n")





def load_motor(motor_id: str) -> MotorConfig:
    if motor_id not in MOTOR_LIBRARY:
        raise ValueError(f"Motor '{motor_id}' not found in library.")
    return MotorConfig(name=motor_id, **MOTOR_LIBRARY[motor_id])


def process_motor_specs(motor: MotorConfig):
    from startup import find_kn_max  # Local import to avoid circular dependencies

    #this
    base_prop = motor.prop.split('_')[0]
    dp = dict_prop.get(base_prop, 2)

    # 1. Thermochemicals
    rho_ideal = properties_table[0][dp]
    rho_g = 1000 * rho_ideal * motor.Rho_pct
    k = properties_table[1][dp]

    # 2. Geometry (TODO #10: Accounting for O-rings)
    total_grain_l = motor.L * motor.Ng
    lc_with_rings = (total_grain_l + (motor.Ng - 1) * motor.o_ring_thickness) * 1.2

    # 3. Nozzle Sizing (TODO #7)
    kn_required = find_kn_max(base_prop, motor.P_target)

    # Simplified Ab_max for sizing check
    Ab_max = ((pi / 4) * (motor.De ** 2 - motor.Di ** 2) * 2 * motor.Ng * motor.ends_surface_inhibited) + \
             (pi * motor.De * total_grain_l * motor.outer_surface_inhibited) + \
             (pi * motor.Di * total_grain_l * motor.core_surface_inhibited)

    at_ideal = Ab_max / kn_required
    dt_ideal = np.sqrt(at_ideal / (pi / 4))

    return {
        "rho_g": rho_g,
        "k": k,
        "lc": lc_with_rings,
        "dt_ideal": dt_ideal,
        "kn_required": kn_required
    }