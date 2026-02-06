import os
import sys
import time
import warnings
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit, brentq
from math import pi, sqrt, exp, log

# Suppress RuntimeWarnings
warnings.filterwarnings("ignore", category=RuntimeWarning)

# --- GLOBAL CONSTANTS ---
Ru = 8314.34  # Universal Gas Constant (J/kmol-K)
patm = 0.101325  # Standard Atmospheric Pressure (MPa)
patm_pa = patm * 1e6
g0 = 9.80665  # Standard Gravity (m/s^2)


# --- HELPER FUNCTIONS ---

def ar(lista):
    """Converts a list to a numpy array."""
    return np.array(lista)


def err(x1, x2):
    """Calculates relative error between x1 and x2."""
    if x1 == 0:
        return 0
    return abs((x1 - x2) / x1)


def err_arr(value, array):
    """Returns an array of relative errors for a target value."""
    er = ar([err(value, i) for i in array])
    return er


def where_interval(Array, min_val, max_val):
    """Returns indices where Array values are within [min_val, max_val]."""
    Array = ar(Array)

    A = np.where(Array >= min_val)[0]
    B = np.where(Array <= max_val)[0]

    C = np.intersect1d(A, B)

    return C


def find_er(value, array):
    """Finds the index of the value with the minimum relative error to the target."""
    er = err_arr(value, array)
    # Fixed: Added 'np.' prefix to where()
    K = np.where(er == min(er))[0]
    return K


def LoadData(type, id, format='csv'):
    """
    Loads raw experimental data from the 'data/' directory.
    Usage: LoadData('BR', 'teste_30_05', 'csv')
    """
    path_csv = 'data/' + type + '_' + id + '.' + format
    try:
        data = np.loadtxt(path_csv, delimiter='\t', skiprows=1)
    except:
        try:
            data = np.loadtxt(path_csv, delimiter=',', skiprows=1)
        except Exception as e:
            print(f"Error loading {path_csv}: {e}")
            return np.array([]), np.array([])

    T = data[:, 0]
    D1 = data[:, 1]

    return T, D1


def pl(x, y, lx='', ly='', tit='', labelf='', x0f=[0, None], y0f=[0, None], log=0, show=1):
    """Quick plotting helper."""
    if log == 0:
        plt.plot(x, y, label=labelf)
    else:
        plt.loglog(x, y, label=labelf)

    plt.grid(True)
    plt.ylabel(ly)
    plt.xlabel(lx)
    plt.title(tit)

    # Handle auto-scaling if None is passed
    if y0f[1] is not None:
        plt.ylim(y0f[0], y0f[1])
    if x0f[1] is not None:
        plt.xlim(x0f[0], x0f[1])

    if labelf:
        plt.legend()

    if show == 1:
        plt.show()
    return


def pl_m(x, y_arr):
    """Plots multiple arrays against a single x-axis."""
    for row in y_arr:
        pl(x, row, x0f=[None, None], y0f=[None, None], show=0)
    plt.show()
    return 0


def ifxl(cond, v_pos, v_neg):
    """Excel-like IF function."""
    if cond:
        return v_pos
    else:
        return v_neg


def find_M2(Ae_At, k):
    """
    Finds the supersonic Mach number (Me) for a given area ratio.
    Uses Brent's method for stability.
    """

    # Define the area-ratio function (Isentropic flow equation)
    def area_ratio_func(M):
        exponent = (k + 1) / (2 * (k - 1))
        # Eq: (1/M) * [ (1 + (k-1)/2 * M^2) / ((k+1)/2) ] ^ exponent - AreaRatio
        return (1 / M) * ((1 + (k - 1) / 2 * M ** 2) / ((k + 1) / 2)) ** exponent - Ae_At

    try:
        # Supersonic roots are always > 1.0.
        # We search between 1.0001 and 10.0 (covering almost all SRM cases).
        return brentq(area_ratio_func, 1.0001, 10.0)
    except ValueError:
        # If no supersonic solution exists (Ae_At < 1), return 1.0 (choked at exit)
        return 1.0


if __name__ == '__main__':
    print("Startup module loaded.")