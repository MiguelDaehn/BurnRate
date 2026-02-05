import os
import numpy as np
import scipy.constants as const
from pathlib import Path
from numpy import exp, sin, cos, tan, arcsin, arccos, arctan, pi, where
from scipy.optimize import brentq
import matplotlib.pyplot as plt
import warnings

# Suppress RuntimeWarnings
warnings.filterwarnings("ignore", category=RuntimeWarning)

# ==========================================
#        SIMULATION CONSTANTS & PATHS
# ==========================================

Ru = const.R  # 8.314 J/mol·K
g0 = const.g  # 9.80665 m/s²
patm = 0.101325  # MPa
patm_pa = patm * 1e6

def get_openrocket_path():
    if os.name == 'nt':  # Windows
        base = Path(os.path.expandvars(r'%APPDATA%'))
        return base / "OpenRocket" / "ThrustCurves"
    else:  # Linux/Unix
        return Path("~/.openrocket/ThrustCurves").expanduser()

path_thrustcurves = get_openrocket_path()
try:
    path_thrustcurves.mkdir(parents=True, exist_ok=True)
except:
    pass

dict_prop = {
    'kndx': 0, 'knsb': 1, 'knsu': 2, 'kner': 3,
    'knmn': 4, 'knfr': 5, 'knpsb': 6,
    'knsu_geprop_01': 2, 'knsu_geprop_02': 2, 'knsu_geprop_03': 2
}

# --- LOAD PROPERTIES & FIX TABLE ---
# 1. Load Thermo properties from CSV (Rows 0-3: rho, k, M, To)
properties_path = 'data/properties.csv'
base_properties = np.loadtxt(properties_path, delimiter=',', skiprows=1, usecols=range(1, 8))

# 2. Define Burn Rate parameters (Rows 4-5: a, n)
# Standard Nakka values: [KNDX, KNSB, KNSU, KNER, KNMN, KNFR, KNPSB]
burn_rate_a = [4.64, 4.20, 8.26, 6.70, 8.26, 8.26, 8.26]
burn_rate_n = [0.38, 0.44, 0.319, 0.49, 0.319, 0.319, 0.319]

# 3. Stack to create full properties_table (6 rows)
properties_table = np.vstack([base_properties, burn_rate_a, burn_rate_n])

# Load KN table
KN_table_path = 'data/KN_table.csv'
KN_table = np.loadtxt(KN_table_path, delimiter=',', skiprows=1, usecols=range(0, 7))

# --- HELPER FUNCTIONS ---
def ar(lista): return np.array(lista)
def err(x1, x2): return abs((x1 - x2) / x1) if x1 != 0 else 0
def pl(x, y, lx='', ly='', tit='', labelf='', x0f=[0, None], y0f=[0, None], log=0, show=1):
    if log == 0: plt.plot(x, y, label=labelf)
    else: plt.loglog(x, y, label=labelf)
    plt.grid(True); plt.ylabel(ly); plt.xlabel(lx); plt.title(tit)
    plt.ylim(y0f[0], y0f[1]); plt.xlim(x0f[0], x0f[1]); plt.legend()
    if show == 1: plt.show()

def find_M2(Ae_At, k):
    def area_ratio_func(M):
        exponent = (k + 1) / (2 * (k - 1))
        return (1/M) * ((1 + (k-1)/2 * M**2) / ((k+1)/2))**exponent - Ae_At
    try: return brentq(area_ratio_func, 1.0001, 10.0)
    except: return 1.0

def find_kn_max(prop_type, P_target, efficiency=0.95):
    prop_key = prop_type.lower().split('_')[0]
    prop = dict_prop.get(prop_key, 2)
    if prop == 0:
        if (P_target > 2.758) and (P_target <= 5.861): prop = 1
        if P_target > 5.861: prop = 2
    elif prop >= 1: prop += 2
    if prop >= len(KN_table): prop = 4

    kn_f = lambda P, a, b, c, d, e, f, g: a + b * P ** 1 + c * P ** 2 + d * P ** 3 + e * P ** 4 + f * P ** 5 + g * P ** 6
    a, b, c, d, e, f, g = KN_table[prop, :]
    return kn_f(P_target, a, b, c, d, e, f, g) / efficiency


def main():
    ic(find_kn_max('kn' + 'dx', 2.0))
    return 0


if __name__ == '__main__':
    main()