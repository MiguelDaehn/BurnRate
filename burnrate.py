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
    T, Pc = LoadData('BR_', id.lower(), 'csv')
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

    if np.size(rdp) == 0:
        pass
    # ic(rdp)
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

def pl_m(x,y_arr):
    for row in y_arr:
        pl(x,row,x0f=[None, None], y0f=[None, None])
    return 0

def rdot_br(n,motor_data):
    prop = motor_data[0].astype(str)
    Dt = motor_data[1].astype(float)
    Rho_pct = motor_data[2].astype(float)
    Ng = motor_data[3].astype(float)
    L0 = motor_data[4].astype(float)
    De = motor_data[5].astype(float)
    Di = motor_data[6].astype(float)
    p_min = motor_data[7].astype(float)
    p_max = motor_data[8].astype(float)

    csi = motor_data[9].astype(int)
    esi = motor_data[10].astype(int)
    osi = motor_data[11].astype(int)

    #TODO:
    #Add functionality to check if the user is
    #separating KNSB grains with o-rings
    # L_oring = motor_data[x]
    #Lc = Ng*(L0+L_oring)
    Lc= (Ng*L0)*1.2
    Vc = (Lc*(pi/4)*De**2)/1000**3
    dp = dict_prop[prop]
    rat = Ru/properties_table[2][dp]
    # Manipulate 'nuc' to reach the calculated value of c*
    #if calculating from experimental pressure values
    nuc = 0.95
    to = nuc*properties_table[4][dp]
    ratto = rat*to

    tw0 = (De-Di) / 2
    rho_g = rho_prop[prop]
    At = pi * (Dt / 2) ** 2

    #Assuming At is in mm² units, A_star is At in m²
    A_star = At/(1e6)
    Vg0 = pi * ((Dt / 2) / 10) ** 2
    mp0 = Ng * Vg0 * rho_g

    s = np.linspace(0,tw0,n)
    incs = s[1]-s[0]

    DI = np.zeros_like(s)
    DE = np.zeros_like(s)
    L = np.zeros_like(s)
    TW = np.zeros_like(s)
    A_duct = np.zeros_like(s)
    A_duct_t = np.zeros_like(s)
    AI = np.zeros_like(s)
    Pc_pa = np.ones_like(s)*patm*1e6
    rho_prod = np.zeros_like(s)
    m_sto = np.zeros_like(s)
    V_g = np.zeros_like(s)
    V_free = np.ones_like(s)*Vc


    DI[0] = Di
    DE[0] = De
    L[0] = L0*Ng
    TW[0] = tw0

    #Note:
    #Here I'm assuming that the grain outer diameter is the case inner diameter
    #Of course there is thermal protection too, but the area we're gonna use (A_duct) is the
    #area through which the gasses can flow so I'll take the initial grain outer diameter as the maximum
    #flowing internal d1iameter.

    A_duct[0] = (pi/4)*(Di**2)
    A_duct_t[0] = A_duct[0]/At
    # Ignore: Pc_pa[0] += rho_prod[i]*ratto
    V_g[0] = Vg0

    for i in range(1,n):
        DI[i] = DI[i-1]+csi*2*incs
        DE[i] = DE[i-1]-osi*2*incs
        L[i] = L[i-1]-Ng*esi*2*incs
        TW[i] = (DE[i]-DI[i])/2
        A_duct[i] = (pi/4)*De**2 - (pi/4)*(DE[i]**2-DI[i]**2)
        A_duct_t[i] = A_duct[i]/At
        # AI[i] = =($M29-patm)*1000000*$I29/SQRT(rat*to)*SQRT(k)*(2/(k+1))^((k+1)/2/(k-1))
        rho_prod[i] = rho_prod[i-1]
        Pc_pa[i] += rho_prod[i]*ratto
        V_g[i] = ((pi/4)*(DE[i]**2-DI[i]**2)*L[i])/(1000**3)
        V_free[i] -= V_g[i]
        

    arr_plot = ar([DI,DE,L,TW,A_duct,A_duct_t])
    # pl_m(s,arr_plot)
    ic(arr_plot)



    rdot = 0
    return rdot

def main():
    return 0


if __name__ == '__main__':
    main()
