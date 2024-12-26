import numpy as np
import matplotlib.pyplot as plt
from numpy import exp,sin, cos, tan, arcsin, arccos, arctan, pi,where
import pandas as pd
from icecream import ic
import time
from scipy.optimize import curve_fit

Ru = 8314.34 #kg/mol-K
patm = 0.101325 #MPa
patm_pa = patm*1e6
g0 = 9.80665
def main():
    return 0


def ar(lista):
    return np.array(lista)


def LoadData(type, id, format='csv'):
    path_csv = 'data/' + type + '_' + id + '.' + format
    try:
        data = np.loadtxt(path_csv, delimiter='\t', skiprows=1)
    except:
        data = np.loadtxt(path_csv, delimiter=',', skiprows=1)
    T = data[:, 0]
    D1 = data[:, 1]

    return T, D1


def err(x1, x2):
    if x1 == 0:
        return 0
    return abs((x1 - x2) / x1)


def pl(x, y, lx='', ly='', tit='', labelf='', x0f=[0, None], y0f=[0, None], log=0):
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
    plt.show()
    return

def ifxl(cond,v_pos,v_neg):
    if cond:
        return v_pos
    else:
        return v_neg

dict_prop = {'kndx': 0, 'knsb': 1, 'knsu':2,'kner': 3, 'knmn': 4, 'knfr':5,'knpsb': 6}
# rho_prop = {'knsu': 1.889, 'knsb': 1.841, 'kner': 1.820, 'kndx': 1.879, 'knmn': 1.854, 'knpsb': 1.923}

properties_path = 'data/properties.csv'
properties_table = np.loadtxt(properties_path, delimiter=',', skiprows=1, usecols=range(1, 8))
# ic(properties_table)
if __name__ == '__main__':
    main()
