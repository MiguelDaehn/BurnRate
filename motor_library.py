from dataclasses import dataclass, asdict
import numpy as np
from startup import dict_prop, properties_table, Ru, pi
from burnrate import get_n
from icecream import ic

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
    empty_mass: float = 0.0
    manufacturer: str = "TauRocketTeam"


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
    "Quark3": {"prop": 'knsb', "Dt": 8.0, "Rho_pct": 0.95, "Ng": 2, "L": 60.0, "De": 56.0, "Di": 25.0, "P_target": 4.0,
               "o_ring_thickness": 3.3}
}


def load_motor(motor_id: str) -> MotorConfig:
    if motor_id not in MOTOR_LIBRARY:
        raise ValueError(f"Motor '{motor_id}' not found in library.")
    return MotorConfig(name=motor_id, **MOTOR_LIBRARY[motor_id])


def process_motor_specs(motor: MotorConfig):
    from startup import find_kn_max

    base_prop = motor.prop.split('_')[0]
    dp = dict_prop.get(base_prop, 2)
    rho_ideal = properties_table[dp][0]  # [Propellant][Param_Index]
    k = properties_table[dp][1]
    rho_g = 1000 * rho_ideal * motor.Rho_pct

    # Extract 'n' (burn rate exponent) for the iterative solver
    n_exponent = get_n(base_prop,1)

    total_grain_l = motor.L * motor.Ng
    lc_with_rings = (total_grain_l + (motor.Ng * motor.o_ring_thickness))

    # Initial guess using efficiency correction
    kn_required = find_kn_max(base_prop, motor.P_target, efficiency=motor.nuc)

    Ab_max = ((pi / 4) * (motor.De ** 2 - motor.Di ** 2) * 2 * motor.Ng * motor.ends_surface_inhibited) + \
             (pi * motor.De * total_grain_l * motor.outer_surface_inhibited) + \
             (pi * motor.Di * total_grain_l * motor.core_surface_inhibited)

    at_ideal = Ab_max / kn_required
    dt_ideal = np.sqrt(at_ideal / (pi / 4))

    return {
        "prop": motor.prop,
        "base_prop": base_prop,
        "rho_g": rho_g,
        "k": k,
        "n": n_exponent,  # Return 'n' for the solver
        "lc": lc_with_rings,
        "dt_ideal": dt_ideal,
        "kn_required": kn_required
    }


def get_motor_signature(motor: MotorConfig):
    d = asdict(motor)
    exclude_keys = ['name', 'manufacturer', 'empty_mass', 'filename']
    signature_dict = {k: v for k, v in d.items() if k not in exclude_keys}
    return f"; {signature_dict}"


def resolve_filename(base_name, signature, paths):
    from pathlib import Path
    check_dir = Path(paths[0])
    candidate_name = base_name
    candidate_file = f"{candidate_name}_sim.eng"
    target = check_dir / candidate_file

    if not target.exists():
        return candidate_name, candidate_file

    try:
        with open(target, 'r') as f:
            first_line = f.readline().strip()
            if first_line.startswith(';') and first_line == signature.strip():
                return candidate_name, candidate_file
    except:
        pass

    counter = 2
    while True:
        candidate_name = f"{base_name}_{counter:02d}"
        candidate_file = f"{candidate_name}_sim.eng"
        target = check_dir / candidate_file
        if not target.exists():
            return candidate_name, candidate_file
        try:
            with open(target, 'r') as f:
                first_line = f.readline().strip()
                if first_line == signature.strip():
                    return candidate_name, candidate_file
        except:
            pass
        counter += 1


def run_full_simulation(motor_name, N=30_000, eta_noz=0.95, Ae_At=6.278, export_eng=True, auto_size_throat=False):
    from thrust import calculate_thrust
    from reporting import create_pdf_report
    from plots import save_array_to_eng_file
    from startup import path_thrustcurves
    import os
    from pathlib import Path

    motor = load_motor(motor_name)
    specs = process_motor_specs(motor)

    # --- AUTO-SIZING LOOP ---
    if auto_size_throat:
        # 1. Initial Guess
        motor.Dt = specs['dt_ideal']
        #TODO: tem um problema aqui: tu tá pegando apenas o base_prop, não pega a diferença entre diferentes versoes do KNSU por exemplo
        prop = specs['prop']
        target_p = motor.P_target
        n_exp = ic(get_n(prop,target_p))

        print(f"🔧 TUNING: Initial Guess Dt={motor.Dt:.3f}mm for Target {target_p} MPa...")

        # Iteration Loop (Max 3 passes)
        for i in range(5):
            F_check, Pc_check, _, _, _ = calculate_thrust(1000, motor, eta_noz, Ae_At)
            p_peak = np.max(Pc_check)

            error = (p_peak - target_p) / target_p

            if abs(error) < 0.01:  # Within 1%
                print(f"✅ CONVERGED: Dt={motor.Dt:.3f}mm -> P_peak={p_peak:.3f} MPa")
                break

            # Physics-based Correction: D_new = D_old * (P_current / P_target) ^ ((1-n)/2)
            # This derivation comes from P ~ Kn^(1/(1-n)) ~ Dt^(-2/(1-n))

            correction_factor = (p_peak / target_p) ** ((1 - n_exp) / 2)

            print(f"   Pass {i + 1}: Peak {p_peak:.3f} MPa. Adjusting Dt by factor {correction_factor:.4f}...")
            motor.Dt = motor.Dt * correction_factor

    # --- FINAL SIMULATION ---
    # Run with high resolution (N)
    F, Pc_MPa, t, Cf, It = calculate_thrust(N, motor, eta_noz, Ae_At)

    if export_eng:
        total_len = (motor.L * motor.Ng) + (motor.Ng * motor.o_ring_thickness)
        rho_g = specs['rho_g']
        vol_grain = (pi / 4) * (motor.De ** 2 - motor.Di ** 2) * motor.L * motor.Ng * 1e-9
        prop_mass = vol_grain * rho_g
        total_mass = prop_mass + motor.empty_mass

        project_results = Path("results/eng_files")
        export_paths = [project_results, path_thrustcurves]

        signature = get_motor_signature(motor)
        final_name, final_filename = resolve_filename(motor.name, signature, export_paths)
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
        print(f"💾 Saved as {final_filename} (10k points)")

    report_path = os.path.join("results", "reports", f"{motor.name}_Report.pdf")
    create_pdf_report(motor, t, Pc_MPa, F, It, filename=report_path)

    return It