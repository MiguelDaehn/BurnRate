from dataclasses import dataclass, asdict
import numpy as np
from startup import dict_prop, properties_table, Ru, pi


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
    o_ring_thickness: float = 0.0
    empty_mass: float = 0.0  # Default 0.0 as requested
    manufacturer: str = "TauRocketTeam"  # Default manufacturer


MOTOR_LIBRARY = {
    "motor_1": {"prop": 'knsb', "Dt": 9.659, "Rho_pct": 0.95, "Ng": 4, "L": 50.0, "De": 45.0, "Di": 25.0,
                "P_target": 4.5},
    "motor_2": {"prop": 'knpsb', "Dt": np.sqrt(81.1 / (np.pi / 4)), "Rho_pct": 1.912 / 1.923, "Ng": 2, "L": 65.0,
                "De": 43.1, "Di": 13.88, "p_min": 3.5, "p_max": 6, "P_target": 4.5},
    "motor_4": {"prop": 'knsu', "Dt": 5.0, "Rho_pct": 0.9, "Ng": 1, "L": 81.14, "De": 24.12, "Di": 5.0, "P_target": 2.0,
                "ends_surface_inhibited": 0},
    "motor_5": {"prop": 'knsu', "Dt": 11.0, "Rho_pct": 0.85, "Ng": 1, "L": 80.0, "De": 33.0, "Di": 25.5,
                "P_target": 1.091},
    "motor_7": {"prop": 'knsu', "Dt": 6.0, "Rho_pct": 0.9533, "Ng": 1, "L": 75.0, "De": 25.4, "Di": 15.0,
                "P_target": 1.091},
    "motor_10": {"prop": 'knsu_geprop_02', "Dt": 12.54, "Rho_pct": 0.89, "Ng": 2, "L": 64.1, "De": 48.34, "Di": 17.44,
                 "p_min": 1.2, "p_max": 2.0, "P_target": 1.091},
    "motor_11": {"prop": 'knsu_geprop_03', "Dt": 12.54, "Rho_pct": 0.885, "Ng": 2, "L": 59.71, "De": 48.22, "Di": 17.88,
                 "p_min": 0.0, "p_max": 1.6, "P_target": 1.091},
    "motor_12": {"prop": 'knsu', "Dt": 12.54, "Rho_pct": 0.9, "Ng": 1, "L": 119.44, "De": 48.22, "Di": 17.88,
                 "p_min": 0.0, "p_max": 1.6, "P_target": 1.091},
    "motor_tauzinha": {"prop": 'knsu', "Dt": 12, "Rho_pct": 0.95, "Ng": 2, "L": 70, "De": 48, "Di": 20, "p_min": 0.0,
                       "p_max": 1.6, "P_target": 1.091},
    "Hadron": {"prop": 'knsb', "Dt": 10.3, "Rho_pct": 0.95, "Ng": 3, "L": 60.0, "De": 56.0, "Di": 25.0,
                        "P_target": 4.0},
    "Quark3": {"prop": 'knsb', "Dt": 8.0, "Rho_pct": 0.95, "Ng": 2, "L": 60.0, "De": 56.0, "Di": 25.0,
                        "P_target": 4.0, "o_ring_thickness": 3.3}
}


def load_motor(motor_id: str) -> MotorConfig:
    if motor_id not in MOTOR_LIBRARY:
        raise ValueError(f"Motor '{motor_id}' not found in library.")
    return MotorConfig(name=motor_id, **MOTOR_LIBRARY[motor_id])


def process_motor_specs(motor: MotorConfig):
    from startup import find_kn_max

    base_prop = motor.prop.split('_')[0]
    dp = dict_prop.get(base_prop, 2)
    rho_ideal = properties_table[0][dp]
    rho_g = 1000 * rho_ideal * motor.Rho_pct
    k = properties_table[1][dp]

    total_grain_l = motor.L * motor.Ng
    lc_with_rings = (total_grain_l + (motor.Ng * motor.o_ring_thickness)) * 1.2

    kn_required = find_kn_max(base_prop, motor.P_target)

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


def get_motor_signature(motor: MotorConfig):
    """
    Generates a unique string representing the motor's physical configuration.
    Used to detect if the motor geometry has changed.
    """
    d = asdict(motor)
    # Exclude fields that don't affect physics/naming
    exclude_keys = ['name', 'manufacturer', 'empty_mass']
    signature_dict = {k: v for k, v in d.items() if k not in exclude_keys}
    return f"; {signature_dict}"


def resolve_filename(base_name, signature, paths):
    """
    Checks if a file exists.
    - If YES and signature MATCHES: Overwrite it (keep same name).
    - If YES and signature DIFFERS: Increment name (Name_02, Name_03).
    - If NO: Use Name.
    Returns (final_name, final_filename)
    """
    from pathlib import Path

    # We use the first path (local results) as the reference
    check_dir = Path(paths[0])

    # Try the base name first
    candidate_name = base_name
    candidate_file = f"{candidate_name}_sim.eng"

    target = check_dir / candidate_file

    if not target.exists():
        return candidate_name, candidate_file

    # File exists, check signature
    try:
        with open(target, 'r') as f:
            first_line = f.readline().strip()
            # If the file doesn't have a comment line (old version), we assume mismatch
            if first_line.startswith(';') and first_line == signature.strip():
                return candidate_name, candidate_file
    except:
        pass

        # Signature mismatch or old file: Start versioning
    counter = 2
    while True:
        candidate_name = f"{base_name}_{counter:02d}"
        candidate_file = f"{candidate_name}_sim.eng"
        target = check_dir / candidate_file

        if not target.exists():
            return candidate_name, candidate_file

        # If version exists, check if THAT one matches our current data
        try:
            with open(target, 'r') as f:
                first_line = f.readline().strip()
                if first_line == signature.strip():
                    return candidate_name, candidate_file
        except:
            pass

        counter += 1


def run_full_simulation(motor_name, N=10000, eta_noz=0.95, Ae_At=6.278, export_eng=True):
    from thrust import calculate_thrust
    from reporting import create_pdf_report
    from plots import save_array_to_eng_file
    from startup import path_thrustcurves
    import os
    from pathlib import Path

    motor = load_motor(motor_name)
    F, Pc_MPa, t, Cf, It = calculate_thrust(N, motor, eta_noz, Ae_At)

    if export_eng:
        # 1. Physics Calc (Fixed length logic: one o-ring PER grain)
        total_len = (motor.L * motor.Ng) + (motor.Ng * motor.o_ring_thickness)

        specs = process_motor_specs(motor)
        rho_g = specs['rho_g']

        # Volume in m^3
        vol_grain = (pi / 4) * (motor.De ** 2 - motor.Di ** 2) * motor.L * motor.Ng * 1e-9
        prop_mass = vol_grain * rho_g
        total_mass = prop_mass + motor.empty_mass

        # 2. Paths
        # Create a "results/eng_files" folder if it doesn't exist
        project_results = Path("results/eng_files")

        # Save to Local AND OpenRocket
        export_paths = [project_results, path_thrustcurves]

        # 3. Smart Naming & Signature
        signature = get_motor_signature(motor)

        # Resolve smart name
        final_name, final_filename = resolve_filename(motor.name, signature, export_paths)

        # Internal name in OpenRocket
        or_internal_name = f"{final_name}_Simulated"

        info_eng = {
            'filename': final_filename,
            'name': or_internal_name,
            'outer_diameter': str(motor.De),
            'length': f"{total_len:.2f}",
            'delay_charge_time': 'P',
            'propellant_mass': f"{prop_mass:.4f}",
            'total_mass': f"{total_mass:.4f}",
            'manufacturer': motor.manufacturer
        }

        save_array_to_eng_file(np.column_stack((t, F)), info_eng, export_paths, header_comment=signature)
        print(f"saved as {final_filename}")

    # 4. Report
    report_path = os.path.join("results", "reports", f"{motor.name}_Report.pdf")
    create_pdf_report(motor, t, Pc_MPa, F, It, filename=report_path)

    return It