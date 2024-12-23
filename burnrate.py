import numpy as np

from startup import *


def Ab_f(N, De, Di0, L, s):
    A_b = pi * N * (0.5 * (De ** 2 - (Di0 + 2 * s) ** 2) + (L - 2 * s) * (Di0 + 2 * s))
    return A_b


def Delta_s(At, Ab, Pc, rho, cstar, delta_t):
    delta_s = (At * Pc * delta_t) / (Ab * rho * cstar)
    return delta_s


def func_powerlaw(x, n, a):
    return x ** n * a


target_func = func_powerlaw


def BR_from_pressure(id, motor_data):
    T, Pc = LoadData('BR', id.lower(), 'csv')
    if max(Pc > 1e5):
        Pc = Pc / 10 ** 6
    delta_t = np.array([T[i + 1] - T[i] for i in range(len(T) - 1)])
    delta_t = np.append(delta_t, delta_t[-1])
    dt_avg = np.average(delta_t)

    p_min = motor_data[7].astype(float)
    p_max = motor_data[8].astype(float)
    # p_min *= 1e6
    # p_max *= 1e6

    prop = motor_data[0].lower()
    Dt = motor_data[1].astype(float)
    rho_pct = motor_data[2].astype(float)
    Ng = motor_data[3].astype(int)
    L = motor_data[4].astype(float)
    De = motor_data[5].astype(float)
    Di = motor_data[6].astype(float)
    w0 = (De - Di) / 2
    rho_g = rho_pct * rho_prop[prop]

    At = pi * (Dt / 2) ** 2
    Vg = pi * ((De / 2 / 10) ** 2 - (Di / 2 / 10) ** 2) * (L / 10)
    mp = Ng * Vg * rho_g
    Psum = np.sum(Pc)
    cstar = ((At / mp) * Psum * dt_avg) / 1000
    err_w0 = 1.0

    Ab = np.zeros_like(T)
    s = np.zeros_like(T)
    delta_s = np.zeros_like(T)
    ds_dt = np.zeros_like(T)

    # delta_s[1] = 0.0
    ss = np.array([0, 5, 100]) / 100
    start = time.time()
    while err_w0 > 1e-15:
        s[1] = ss[1]
        for i, t in enumerate(T):

            Ab[i] = Ab_f(Ng, De, Di, L, s[i - 1])
            # ic(Ab[i])
            if i > 1:
                s[i] = s[i - 1] + delta_s[i - 1]
            if i > 0:
                delta_s[i] = Delta_s(At, Ab[i], Pc[i], rho_g, cstar, delta_t[i])
                if delta_t[i] != 0:
                    ds_dt[i] = delta_s[i] / delta_t[i]
                else:
                    ds_dt[i] = 0
                # ic(delta_t[i])

        err_w0 = err(w0, s[-1])
        # ic(err_w0)

        if s[-1] >= w0:
            ss[2] = ss[1]
            ss[1] = (ss[0] + ss[1]) / 2
        else:
            ss[0] = ss[1]
            ss[1] = (ss[1] + ss[2]) / 2
        finish = time.time()
        if finish - start > 10:
            break

    if p_max == 0:
        pass
    else:
        j = np.where(Pc > p_min)
        k = np.where(Pc < p_max)
        z = np.intersect1d(j, k)
        Pc = Pc[z]
        ds_dt = ds_dt[z]



    target_func = func_powerlaw

    pars, sol0 = curve_fit(func_powerlaw, Pc, ds_dt, p0=np.asarray([4, 0.5]),maxfev=4000)
    n, a = pars
    print(f'a: {a}, \nn: {n}')
    plt.scatter(Pc, ds_dt, marker='*', color='red')
    plt.plot(Pc, target_func(Pc, *pars), '--',label=f'{pars[1]}·P^{pars[0]}')
    return Pc, ds_dt,pars

def pp(propt):
    rddatapath = 'data/BR_dict_'+propt+'.csv'
    rdp = np.loadtxt(rddatapath, delimiter=',', skiprows=1, usecols=range(1, 5))
    ic(np.size(rdp))
    if np.size(rdp) == 0:
        pass
    ic(rdp)
    return rdp

rd_knsu = pp('knsu')
rd_knsb = pp('knsb')
rd_kndx = pp('kndx')
rd_knfr = pp('knfr')
rd_kner = pp('kner')
rd_knpsb = pp('knpsb')


def rdp(rd_prop, P):
    if P > 1e5:
        P = P * 1e-6

    result = None  # Initialize result variable
    for i, row in enumerate(rd_prop):
        # Check if row is a scalar or an array
        if isinstance(row, np.ndarray):
            if len(row) < 4:
                raise ValueError("Row does not have enough columns.")
        else:
            raise ValueError("Row is not an array.")

        if (P >= row[0]) and (P <= row[1]):  # Use 'and' for logical comparison
            result = row[2] * P ** row[3]  # Use row[2] instead of rd[2]
            break  # Exit the loop once the condition is met

    if result is None:
        raise ValueError('ERROR: no adequate pressure interval found!')

    return result


def rdot_br():
    rdot = 0
    return rdot

def main():
    return 0


if __name__ == '__main__':
    main()
