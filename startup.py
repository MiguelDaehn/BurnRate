import numpy as np
from numpy import exp,sin, cos, tan, arcsin, arccos, arctan, pi,where
from scipy.optimize import curve_fit

import matplotlib.pyplot as plt
import pandas as pd

from icecream import ic
import time
import warnings

# Suppress RuntimeWarnings
# Debugging: turn this off
warnings.filterwarnings("ignore", category=RuntimeWarning)




Ru = 8314.34 #kg/mol-K
patm = 0.101325 #MPa
patm_pa = patm*1e6
g0 = 9.80665

def ar(lista):
    return np.array(lista)


def err(x1, x2):
    if x1 == 0:
        return 0
    return abs((x1 - x2) / x1)


def err_arr(value,array):
    er = ar([err(value,i) for i in array])
    return er

def where_interval(Array, min_val, max_val):
    Array = ar(Array)

    A = np.where(Array >= min_val)[0]
    B = np.where(Array <= max_val)[0]

    C = np.intersect1d(A, B)

    return C

def find_er(value,array):
    '''Finds the id of the value with the mininum relative error to the desired value.'''
    er = err_arr(value,array)
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

def pl_m(x,y_arr):
    for row in y_arr:
        pl(x,row,x0f=[None, None], y0f=[None, None])
    return 0


def ifxl(cond,v_pos,v_neg):
    if cond:
        return v_pos
    else:
        return v_neg

def find_M2(AeAt,k):
    AeAt = float(AeAt)
    ME = lambda Me: AeAt - 1 / Me * ((1 + (k - 1) / 2 * Me ** 2) / (1 + (k - 1) / 2)) ** ((k + 1) / (2 * (k - 1)))

    M2 = np.linspace(0.001, 10, 1000)
    Mea = ar([abs(ME(i)) for i in M2])
    ID = np.argmin(Mea)
    val = M2[ID]

    M2 = np.linspace(val-1,val+1,10000)
    Mea = ar([abs(ME(i)) for i in M2])
    ID = np.argmin(Mea)
    val = M2[ID]

    return val




dict_prop = {'kndx': 0, 'knsb': 1, 'knsu':2,'kner': 3, 'knmn': 4, 'knfr':5,'knpsb': 6}



# DEPRECATED: now using properties_table
# rho_prop = {'knsu': 1.889, 'knsb': 1.841, 'kner': 1.820, 'kndx': 1.879, 'knmn': 1.854, 'knpsb': 1.923}
properties_path = 'data/properties.csv'
properties_table = np.loadtxt(properties_path, delimiter=',', skiprows=1, usecols=range(1, 8))

KN_table_path = 'data/KN_table.csv'
KN_table = np.loadtxt(KN_table_path, delimiter=',', skiprows=1, usecols=range(0, 7))

# ic(KN_table)

def find_kn_max(prop_type,P_target):
    '''PROP_TYPE: "KNSU", "KNSB", "KNDX",...'''
    '''P_TARGET: UNITS IN MPa'''

    prop = dict_prop[prop_type.lower()]

    if prop>=1:
        prop+=2

    if prop == 0:
        if (P_target>2.758) and (P_target<=5.861):
            prop = 1
        if P_target>5.861:
            prop = 2
    ic(prop)
    kn_f = lambda P,a,b,c,d,e,f,g: a + b*P**1+ c*P**2 + d*P**3 + e*P**4 + f*P**5 + g*P**6

    a,b,c,d,e,f,g = KN_table[prop,:]
    kn_max = kn_f(P_target,a,b,c,d,e,f,g)

    return kn_max

def main():
    # ic(find_M2(6.278, 1.137))

    ic(find_kn_max('kn'+'dx',1.0))

    return 0



if __name__ == '__main__':
    main()
