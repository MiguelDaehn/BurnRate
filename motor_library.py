from dataclasses import dataclass
import numpy as np
from startup import pi
import propellants as prop_db  # <--- NEW: Uses the new database

@dataclass
class MotorConfig:
    name: str
    Dt: float
    Ng: int
    L: float
    De: float
    Di: float
    prop: str = 'knsb'
    Rho_pct: float = 0.95
    p_min: float = 0.01
    p_max: float = 10.0
    P_target: float = 3.0
    nuc: float = 0.95
    core_surface_inhibited: int = 1
    ends_surface_inhibited: int = 1
    outer_surface_inhibited: int = 0
    o_ring_thickness: float = 0.0

L_a = 36.5; De_a = 56.0; Di_a = 25.0;oring_a=3.3

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
    "Hadron_09": {"Dt": 13.0, "Ng": 5, "L": L_a, "De": De_a, "Di": Di_a, "P_target": 4.0, "o_ring_thickness": oring_a},
    "Quark3_09": {"Dt": 10.00, "Ng": 3, "L": L_a, "De": De_a, "Di": Di_a, "P_target": 4.0, "o_ring_thickness": oring_a}
}


def load_motor(motor_id: str) -> MotorConfig:
    if motor_id not in MOTOR_LIBRARY:
        # Fallback for dynamic motor creation if needed, or error
        raise ValueError(f"Motor '{motor_id}' not found in library.")
    return MotorConfig(name=motor_id, **MOTOR_LIBRARY[motor_id])


def get_grain_mass(motor: MotorConfig) -> float:
    """Calculates geometric mass."""
    specs = process_motor_specs(motor)
    rho_g = specs['rho_g']
    volume_mm3 = (np.pi / 4) * (motor.De**2 - motor.Di**2) * motor.L * motor.Ng
    volume_m3 = volume_mm3 / 1e9
    return volume_m3 * rho_g


def get_config_table_data(motor: MotorConfig):
    """Helper for reporting."""
    return [
        ["Motor ID", motor.name, "-"],
        ["Propellant", motor.prop, "-"],
        ["Grain Length", f"{motor.L:.1f}", "mm"],
        ["Grain OD", f"{motor.De:.1f}", "mm"],
        ["Grain ID", f"{motor.Di:.1f}", "mm"],
        ["No. of Grains", str(motor.Ng), "-"],
        ["Throat Dia", f"{motor.Dt:.2f}", "mm"],
        ["Target Pressure", f"{motor.P_target:.1f}", "MPa"],
    ]


def process_motor_specs(motor: MotorConfig):
    # 1. Thermochemicals (FETCHED FROM PROPELLANTS.PY)
    rho_ideal = prop_db.get_density(motor.prop)
    rho_g = 1000 * rho_ideal * motor.Rho_pct
    k = prop_db.get_k(motor.prop)

    # 2. Geometry
    total_grain_l = motor.L * motor.Ng
    lc_with_rings = (total_grain_l + (motor.Ng - 1) * motor.o_ring_thickness) * 1.2

    # 3. Nozzle Sizing (FETCHED FROM PROPELLANTS.PY)
    # This replaces the old "from startup import find_kn_max"
    kn_required = prop_db.find_kn_max(motor.prop, motor.P_target)

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