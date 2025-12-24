from dataclasses import dataclass
import numpy as np

@dataclass
class MotorConfig:
    name: str
    prop: str
    Dt: float          # Throat diameter (mm)
    Rho_pct: float     # Density percentage
    Ng: int            # Number of grains
    L: float           # Grain length (mm)
    De: float          # Grain outer diameter (mm)
    Di: float          # Grain inner diameter (mm)
    p_min: float = 0.0
    p_max: float = 10.0
    P_target: float = 0.0
    nuc: float = 0.95  # Combustion efficiency
    csi: int = 1       # Core surface inhibition
    esi: int = 1       # End surface inhibition
    osi: int = 0       # Outer surface inhibition

# Extracted from motor.py
MOTOR_LIBRARY = {
    "motor_1": {"prop": 'knsb', "Dt": 9.659, "Rho_pct": 0.95, "Ng": 4, "L": 50.0, "De": 45.0, "Di": 25.0, "P_target": 4.5, "csi": 1, "esi": 1, "osi": 0},
    "motor_2": {"prop": 'knpsb', "Dt": np.sqrt(81.1 / (np.pi / 4)) * 10, "Rho_pct": 1.912/1.923, "Ng": 2, "L": 65.0, "De": 43.1, "Di": 13.88, "p_min": 3.5, "p_max": 6, "P_target": 4.5, "csi": 1, "esi": 1, "osi": 0},
    "motor_4": {"prop": 'knsu', "Dt": 5.0, "Rho_pct": 0.9, "Ng": 1, "L": 81.14, "De": 24.12, "Di": 5.0, "P_target": 2.0, "csi": 1, "esi": 0, "osi": 0},
    "motor_5": {"prop": 'knsu', "Dt": 11.0, "Rho_pct": 0.85, "Ng": 1, "L": 80.0, "De": 33.0, "Di": 25.5, "P_target": 1.091, "csi": 1, "esi": 1, "osi": 0},
    "motor_7": {"prop": 'knsu', "Dt": 6.0, "Rho_pct": 0.9533, "Ng": 1, "L": 75.0, "De": 25.4, "Di": 15.0, "P_target": 1.091, "csi": 1, "esi": 1, "osi": 0},
    "motor_10": {"prop": 'knsu_geprop_02', "Dt": 12.54, "Rho_pct": 0.89, "Ng": 2, "L": 64.1, "De": 48.34, "Di": 17.44, "p_min": 1.2, "p_max": 2.0, "P_target": 1.091, "csi": 1, "esi": 1, "osi": 0},
    "motor_11": {"prop": 'knsu_geprop_03', "Dt": 12.54, "Rho_pct": 0.885, "Ng": 2, "L": 59.71, "De": 48.22, "Di": 17.88, "p_min": 0.0, "p_max": 1.6, "P_target": 1.091, "csi": 1, "esi": 1, "osi": 0},
    "motor_12": {"prop": 'knsu', "Dt": 12.54, "Rho_pct": 0.9, "Ng": 1, "L": 119.44, "De": 48.22, "Di": 17.88, "p_min": 0.0, "p_max": 1.6, "P_target": 1.091, "csi": 1, "esi": 1, "osi": 0},
}

def load_motor(motor_id: str) -> MotorConfig:
    if motor_id not in MOTOR_LIBRARY:
        raise ValueError(f"Motor '{motor_id}' not found in library.")
    return MotorConfig(name=motor_id, **MOTOR_LIBRARY[motor_id])