from startup import *
from motor_library import MotorConfig
import propellants as prop_db  # <--- NEW


def Ab_f(N, De, Di0, L, s):
    A_b = pi * N * (0.5 * (De ** 2 - (Di0 + 2 * s) ** 2) + (L - 2 * s) * (Di0 + 2 * s))
    return A_b


def Delta_s(At, Ab, Pc, rho, cstar, delta_t):
    delta_s = (At * Pc * delta_t) / (Ab * rho * cstar)
    return delta_s


def func_powerlaw(x, a, n):
    return a * (x ** n)


target_func = func_powerlaw


def BR_from_pressure(id, motor: MotorConfig):
    T, Pc = LoadData('BR', id.lower(), 'csv')
    if max(Pc > 1e5):
        Pc = Pc / 10 ** 6

    delta_t = np.array([T[i + 1] - T[i] for i in range(len(T) - 1)])
    delta_t = np.append(delta_t, delta_t[-1])
    dt_avg = np.average(delta_t)

    # Use attributes from the motor object
    p_min = motor.p_min
    p_max = motor.p_max
    prop = motor.prop
    Dt = motor.Dt
    rho_pct = motor.Rho_pct
    Ng = motor.Ng
    L = motor.L
    De = motor.De
    Di = motor.Di

    w0 = (De - Di) / 2

    # NEW: Get density from propellants.py instead of dict_prop
    rhoideal = prop_db.get_density(prop)
    rho_g = rho_pct * rhoideal

    At = pi * (Dt / 2) ** 2
    # Geometry calculation for mass propellant
    Vg = pi * ((De / 2 / 10) ** 2 - (Di / 2 / 10) ** 2) * (L / 10)
    mp = Ng * Vg * rho_g
    Psum = np.sum(Pc)
    cstar = ((At / mp) * Psum * dt_avg) / 1000
    err_w0 = 1.0

    Ab = np.zeros_like(T)
    s = np.zeros_like(T)
    delta_s = np.zeros_like(T)
    ds_dt = np.zeros_like(T)

    ss = np.array([0, 5, 100]) / 100
    start = time.time()

    while err_w0 > 1e-15:
        s[1] = ss[1]
        for i, t in enumerate(T):
            Ab[i] = Ab_f(Ng, De, Di, L, s[i - 1])
            if i > 1:
                s[i] = s[i - 1] + delta_s[i - 1]
            if i > 0:
                delta_s[i] = Delta_s(At, Ab[i], Pc[i], rho_g, cstar, delta_t[i])
                ds_dt[i] = delta_s[i] / delta_t[i] if delta_t[i] != 0 else 0

        err_w0 = err(w0, s[-1])

        if s[-1] >= w0:
            ss[2] = ss[1]
            ss[1] = (ss[0] + ss[1]) / 2
        else:
            ss[0] = ss[1]
            ss[1] = (ss[1] + ss[2]) / 2

        if time.time() - start > 10:
            break

    if p_max != 0:
        z = np.intersect1d(np.where(Pc > p_min), np.where(Pc < p_max))
        Pc = Pc[z]
        ds_dt = ds_dt[z]

    pars, _ = curve_fit(func_powerlaw, Pc, ds_dt, p0=np.asarray([5, 0.5]), maxfev=10000)
    return Pc, ds_dt, [pars[0], pars[1], 0]


def pp(propt):
    # Strip sub-variants (e.g., 'knsu_geprop_02' -> 'knsu')
    base_prop = propt.split('_')[0]
    rddatapath = f'data/propellants/BR_dict_{base_prop}.csv'

    try:
        rdp_data = np.loadtxt(rddatapath, delimiter=',', skiprows=1, usecols=range(1, 5))
        return rdp_data if rdp_data.ndim > 1 else rdp_data.reshape(1, -1)
    except FileNotFoundError:
        print(f"Warning: Burn rate file for {base_prop} not found at {rddatapath}")
        return np.array([])


def rdp(prop, P=1.0):
    rd_prop = pp(prop)
    if P > 1e5:
        P = P * 1e-6

    # Logic to find the correct pressure interval
    if len(rd_prop) == 0: return 0

    for row in rd_prop:
        if (P >= row[0]) and (P <= row[1]):
            return row[2] * P ** row[3]

    # raise ValueError(f'ERROR: no adequate pressure interval found for {prop} at {P} MPa!')
    # Fallback to last known row (extrapolation) instead of crash
    last_row = rd_prop[-1]
    return last_row[2] * P ** last_row[3]


def main():
    return 0


if __name__ == '__main__':
    main()