import numpy as np
from numpy import exp, sin, cos, tan, arcsin, arccos, arctan, pi, where
from scipy.optimize import curve_fit
from scipy.optimize import brentq


import matplotlib.pyplot as plt
import pandas as pd

from icecream import ic
import time
import warnings

# Suppress RuntimeWarnings
# Debugging: turn this off
warnings.filterwarnings("ignore", category=RuntimeWarning)

path_thrustcurves = '/home/kanamori/.openrocket/ThrustCurves/'

Ru = 8314.34  # kg/mol-K
patm = 0.101325  # MPa
patm_pa = patm * 1e6
g0 = 9.80665

dict_prop = {'kndx': 0, 'knsb': 1, 'knsu': 2, 'kner': 3, 'knmn': 4, 'knfr': 5, 'knpsb': 6}

# DEPRECATED: now using properties_table
# rho_prop = {'knsu': 1.889, 'knsb': 1.841, 'kner': 1.820, 'kndx': 1.879, 'knmn': 1.854, 'knpsb': 1.923}
properties_path = 'data/properties.csv'
properties_table = np.loadtxt(properties_path, delimiter=',', skiprows=1, usecols=range(1, 8))

KN_table_path = 'data/KN_table.csv'
KN_table = np.loadtxt(KN_table_path, delimiter=',', skiprows=1, usecols=range(0, 7))


def ar(lista):
    return np.array(lista)


def err(x1, x2):
    if x1 == 0:
        return 0
    return abs((x1 - x2) / x1)


def err_arr(value, array):
    er = ar([err(value, i) for i in array])
    return er


def where_interval(Array, min_val, max_val):
    Array = ar(Array)

    A = np.where(Array >= min_val)[0]
    B = np.where(Array <= max_val)[0]

    C = np.intersect1d(A, B)

    return C


def find_er(value, array):
    '''Finds the id of the value with the mininum relative error to the desired value.'''
    er = err_arr(value, array)
    K = where(min(er))[0]
    return K


def LoadData(type, id, format='csv'):
    path_csv = 'data/' + type + '_' + id + '.' + format
    try:
        data = np.loadtxt(path_csv, delimiter='\t', skiprows=1)
    except:
        data = np.loadtxt(path_csv, delimiter=',', skiprows=1)
    T = data[:, 0]
    D1 = data[:, 1]

    return T, D1


def pl(x, y, lx='', ly='', tit='', labelf='', x0f=[0, None], y0f=[0, None], log=0, show=1):
    if log == 0:
        plt.plot(x, y, label=labelf)
        pass
    else:
        plt.loglog(x, y, label=labelf)
    plt.grid(True)
    plt.ylabel(ly)
    plt.xlabel(lx)
    plt.title(tit)
    plt.ylim(y0f[0], y0f[1])
    plt.xlim(x0f[0], x0f[1])
    plt.legend()
    if show == 1:
        plt.show()
    return


def pl_m(x, y_arr):
    for row in y_arr:
        pl(x, row, x0f=[None, None], y0f=[None, None], show=0)
    plt.show()
    return 0


# t = np.linspace(0,10,100)
# v1 = 5
# v2 = 4
# d1 = v1*t
# d2 = v2*t
# pl_m(t,ar([d1,d2]))

def ifxl(cond, v_pos, v_neg):
    if cond:
        return v_pos
    else:
        return v_neg



def find_M2(Ae_At, k):
    """
    Finds the supersonic Mach number (Me) for a given area ratio.
    Replaces the np.linspace search for better stability and speed.
    """
    # Define the area-ratio function (Isentropic flow equation)
    def area_ratio_func(M):
        # term = ((k+1)/2)**(-(k+1)/(2*(k-1)))
        # return (1/M) * ((1 + (k-1)/2 * M**2)**((k+1)/(2*(k-1)))) * term - Ae_At
        # Simplified version for stability:
        exponent = (k + 1) / (2 * (k - 1))
        return (1/M) * ((1 + (k-1)/2 * M**2) / ((k+1)/2))**exponent - Ae_At

    try:
        # Supersonic roots are always > 1.0.
        # We search between 1.0001 and 10.0 (covering almost all SRM cases).
        return brentq(area_ratio_func, 1.0001, 10.0)
    except ValueError:
        # If no supersonic solution exists (Ae_At < 1), return 1.0 (choked at exit)
        return 1.0


def find_kn_max(prop_type, P_target):
    '''PROP_TYPE: "KNSU", "KNSB", etc. P_TARGET: MPa'''
    prop_key = prop_type.lower().split('_')[0]  # Handle sub-variants
    prop = dict_prop.get(prop_key, 2)

    if prop >= 1:
        prop += 2

    # Logic for KNDX variants as per your original code
    if prop == 0:
        if (P_target > 2.758) and (P_target <= 5.861):
            prop = 1
        if P_target > 5.861:
            prop = 2

    kn_f = lambda P, a, b, c, d, e, f, g: a + b * P ** 1 + c * P ** 2 + d * P ** 3 + e * P ** 4 + f * P ** 5 + g * P ** 6

    a, b, c, d, e, f, g = KN_table[prop, :]
    return kn_f(P_target, a, b, c, d, e, f, g)

def main():

    ic(find_kn_max('kn' + 'dx', 2.0))

    return 0


if __name__ == '__main__':
    main()
