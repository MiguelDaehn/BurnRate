# propellants.py
import numpy as np
import os

# --- 1. ID MAPPINGS ---
# Maps propellant names to their column/index in the CSV files
PROPELLANT_ID_MAP = {
    'kndx': 0,
    'knsb': 1,
    'knsu': 2,
    'kner': 3,
    'knmn': 4,
    'knfr': 5,
    'knpsb': 6
}

# --- 2. MISSION PLANNING ESTIMATES ---
# Used by EzImpulse/Mission Planner (Isp in seconds)
# Density is NOT here anymore; we fetch it from the physics table to ensure consistency.
ISP_ESTIMATES = {
    'kndx': 125,
    'knsb': 120,
    'knsu': 130,
    'kner': 120,
    'knfr': 125,
    'knpsb': 125,
    'knmn': 125  # Added default
}

# --- 3. DATA LOADING ---
# Load the physics tables once
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROP_CSV_PATH = os.path.join(BASE_DIR, 'data', 'csv_files', 'properties.csv')
KN_CSV_PATH = os.path.join(BASE_DIR, 'data', 'csv_files', 'KN_table.csv')

try:
    # Rows: [0]=Rho, [1]=k, [2]=M, [3]=To, etc.
    PROPERTIES_TABLE = np.loadtxt(PROP_CSV_PATH, delimiter=',', skiprows=1, usecols=range(1, 8))

    # KN Max coefficients
    KN_TABLE = np.loadtxt(KN_CSV_PATH, delimiter=',', skiprows=1, usecols=range(0, 7))
except Exception as e:
    print(f"⚠️ Warning: Could not load propellant CSVs: {e}")
    PROPERTIES_TABLE = np.zeros((10, 10))
    KN_TABLE = np.zeros((10, 10))


# --- 4. ACCESSOR FUNCTIONS ---

def get_propellant_id(prop_name: str) -> int:
    """Standardizes name (e.g., 'knsu_geprop' -> 'knsu') and gets ID."""
    key = prop_name.lower().split('_')[0]
    return PROPELLANT_ID_MAP.get(key, 2)  # Default to 2 (knsu) if unknown


def get_density(prop_name: str) -> float:
    """Returns ideal density in g/cm^3"""
    pid = get_propellant_id(prop_name)
    return PROPERTIES_TABLE[0][pid]


def get_k(prop_name: str) -> float:
    """Returns Ratio of Specific Heats (k)"""
    pid = get_propellant_id(prop_name)
    return PROPERTIES_TABLE[1][pid]


def get_molar_mass(prop_name: str) -> float:
    """Returns Molecular Weight (kg/kmol)"""
    pid = get_propellant_id(prop_name)
    return PROPERTIES_TABLE[2][pid]


def get_combustion_temp(prop_name: str) -> float:
    """Returns Chamber Temperature (To) in Kelvin"""
    pid = get_propellant_id(prop_name)
    return PROPERTIES_TABLE[3][pid]


def get_isp_estimate(prop_name: str) -> float:
    """Returns Isp estimate for mission planning"""
    key = prop_name.lower().split('_')[0]
    return ISP_ESTIMATES.get(key, 120)


def find_kn_max(prop_name: str, P_target_mpa: float) -> float:
    """Calculates required Kn for a target pressure."""
    pid = get_propellant_id(prop_name)

    # Special logic for KNDX variants (preserved from original code)
    if pid == 0:  # kndx
        if 2.758 < P_target_mpa <= 5.861:
            pid = 1  # shift logic
        elif P_target_mpa > 5.861:
            pid = 2

    # Polynomial coefficients
    coeffs = KN_TABLE[pid, :]
    a, b, c, d, e, f, g = coeffs

    P = P_target_mpa
    return a + b * P + c * P ** 2 + d * P ** 3 + e * P ** 4 + f * P ** 5 + g * P ** 6