from startup import *
# from motor_library import MotorConfig  # Added to support new architecture
from startup import *
import time

def Ab_f(N, De, Di0, L, s):
    A_b = pi * N * (0.5 * (De ** 2 - (Di0 + 2 * s) ** 2) + (L - 2 * s) * (Di0 + 2 * s))
    return A_b


def Delta_s(At, Ab, Pc, rho, cstar, delta_t):
    delta_s = (At * Pc * delta_t) / (Ab * rho * cstar)
    return delta_s


def func_powerlaw(x, a, n):
    return a * (x ** n)


target_func = func_powerlaw


def BR_from_pressure(id, motor: "MotorConfig"):  # Changed to accept MotorConfig object
    T, Pc = LoadData('BR', id.lower(), 'csv')
    if max(Pc > 1e5):
        Pc = Pc / 10 ** 6

    delta_t = np.array([T[i + 1] - T[i] for i in range(len(T) - 1)])
    delta_t = np.append(delta_t, delta_t[-1])
    dt_avg = np.average(delta_t)

    # Use attributes from the motor object instead of array indices
    p_min = motor.p_min
    p_max = motor.p_max
    prop = motor.prop.lower()
    Dt = motor.Dt
    rho_pct = motor.Rho_pct
    Ng = motor.Ng
    L = motor.L
    De = motor.De
    Di = motor.Di

    w0 = (De - Di) / 2
    dp = dict_prop.get(prop.split('_')[0], 2)  # Handle sub-variants like 'knsu_geprop'

    rhoideal = properties_table[0][dp]
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
    return Pc, ds_dt, [pars[0], pars[1], 0]  # Returns a, n, R2 placeholder


def pp(propt):
    # Strip sub-variants (e.g., 'knsu_geprop_02' -> 'knsu') to find the CSV
    base_prop = propt.split('_')[0]
    rddatapath = 'data/BR_dict_' + base_prop + '.csv'

    try:
        rdp_data = np.loadtxt(rddatapath, delimiter=',', skiprows=1, usecols=range(1, 5))
        return rdp_data if rdp_data.ndim > 1 else rdp_data.reshape(1, -1)
    except FileNotFoundError:
        print(f"Warning: Burn rate file for {base_prop} not found.")
        return np.array([])


def get_n(prop, P=1.0):
    """
    Retrieves the burn rate exponent 'n' for a given propellant and pressure.
    Used for the auto-tuning logic to calculate the correct throat resizing factor.
    """
    # 1. Load the REAL data from the CSV
    rd_prop = pp(prop)

    # 2. Safety Clamp
    if P < 0.001: P = 0.001

    # 3. Handle array vs single row
    if rd_prop.ndim == 1:
        rd_prop = rd_prop.reshape(1, -1)

    # 4. Find the correct pressure interval
    # Columns from pp(): [0]=Pmin, [1]=Pmax, [2]=a, [3]=n
    for row in rd_prop:
        if (P >= row[0]) and (P <= row[1]):
            return row[3]  # Return 'n' directly

    # 5. Fallback/Clamping (matches rdp logic)
    if P > rd_prop[-1, 1]:
        return rd_prop[-1, 3]  # Return max pressure 'n'
    if P < rd_prop[0, 0]:
        return rd_prop[0, 3]  # Return min pressure 'n'

    return rd_prop[0, 3]


def rdp(prop, P=1.0):
    # 1. Load the REAL data from the CSV (using your existing pp helper)
    rd_prop = pp(prop)

    # 2. Safety Clamp for the physics engine
    if P < 0.001: P = 0.001

    # 3. Handle array vs single row (in case file has only 1 line)
    if rd_prop.ndim == 1:
        rd_prop = rd_prop.reshape(1, -1)

    # 4. Find the correct pressure interval
    # Columns from pp(): [0]=Pmin, [1]=Pmax, [2]=a, [3]=n
    for row in rd_prop:
        if (P >= row[0]) and (P <= row[1]):
            return row[2] * (P ** row[3])

    # 5. Fallback: If P is outside defined ranges, clamp to nearest edge
    # (Prevents crashing if pressure spikes to 11 MPa when max is 10.6)
    if P > rd_prop[-1, 1]:
        return rd_prop[-1, 2] * (P ** rd_prop[-1, 3])
    if P < rd_prop[0, 0]:
        return rd_prop[0, 2] * (P ** rd_prop[0, 3])

    # If we get here, something is weird, but return a safe default
    return rd_prop[0, 2] * (P ** rd_prop[0, 3])

def test_BR_from_pressure(id_file, motor_id, p_min=3.5, p_max=4.5):
    from motor_library import load_motor
    motor = load_motor(motor_id)
    motor.p_min = p_min
    motor.p_max = p_max
    Pc, BR, [a, n, R2] = BR_from_pressure(id_file, motor)
    plt.plot(Pc, target_func(Pc, *[a,n]), '--')
    pl(Pc, BR, 'Chamber Pressure [MPa]', 'Burn Rate [mm/s]',
       f'Burn Rate as a function of Pressure - R²={round(R2,3)}',
       labelf=f'{round(a,5)}·P^{round(n,5)}', log=0,
       x0f=[0.95 * p_min, 1.0 * p_max],
       y0f=[0.95 * min(BR[np.where(BR > 0)]), 1.05 * max(BR[np.where(BR < 40)])])

def plot_br_multiple(arr_str=ar(['knsb', 'knsu']),p_int=[0.1 , 10.0]):
    p_min = p_int[0]
    p_max = p_int[1]
    Prange = np.linspace(p_min, p_max, 1000)
    arrstr = ar(arr_str)

    for rd in arrstr:
        Rd = ar([rdp(rd, p) for p in Prange])
        plt.plot(Prange, Rd)
        print(f'{rd} at 1 atm: {rdp(rd,0.101)}')

    plt.xlabel('Pressure [MPa]');plt.ylabel('R_dot [mm/s]');plt.title('Rd Values vs Pressure')
    plt.legend();plt.grid()
    plt.show()


def main():
    return 0


if __name__ == '__main__':
    main()
