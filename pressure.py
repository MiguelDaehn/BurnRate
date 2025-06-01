from startup import *
from burnrate import *

def calculate_pressure_parameters(N, motor_data):
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

    # TODO:
    #  Add functionality to check if the user is separating KNSB grains with o-rings

    # L_oring = motor_data[x]
    # Lc = Ng*(L0+L_oring)
    Lc = (Ng * L0) * 1.2
    Vc = (Lc * (pi / 4) * De ** 2) / 1000 ** 3
    dp = dict_prop[prop]
    rat = Ru / properties_table[2][dp]
    # Manipulate 'nuc' to reach the calculated value of c*
    # if calculating from experimental pressure values
    nuc = 0.95
    to = nuc * properties_table[3][dp]
    ratto = rat * to
    # ic(ratto)
    k = properties_table[1][dp]
    c_star = np.sqrt(ratto/k*(((k+1)/2)**((k+1)/(k-1))))
    # ic(c_star)
    pbd = 0

    tw0 = (De - Di) / 2
    dp = dict_prop[prop]
    rhoideal = properties_table[0][dp]

    rho_g = 1000 * rhoideal * Rho_pct
    At = pi * (Dt / 2) ** 2

    # Assuming At is in mm² units, A_star is At in m²
    A_star = At / (1e6)
    Vg0 = ((pi / 4) * (De ** 2 - Di ** 2) * L0 * Ng) / 1000 ** 3
    mp0 = Ng * Vg0 * rho_g
    par_AI = np.sqrt(k / ratto) * (2 / (k + 1)) ** ((k + 1) / 2 / (k - 1))
    # ic(par_AI)

    s = np.linspace(0, tw0, N)
    incs = s[1] - s[0]

    t           = np.zeros_like(s)
    DI          = np.zeros_like(s)
    DE          = np.zeros_like(s)
    L           = np.zeros_like(s)
    TW          = np.zeros_like(s)
    A_duct      = np.zeros_like(s)
    A_duct_t    = np.zeros_like(s)
    AI          = np.zeros_like(s)
    rho_prod    = np.zeros_like(s)
    m_sto       = np.zeros_like(s)
    m_stodot    = np.zeros_like(s)
    V_g         = np.zeros_like(s)
    Pc_Mpa2     = np.zeros_like(s)
    mdot_nozzle = np.zeros_like(s)
    mdot_ger    = np.zeros_like(s)
    m_grain     = np.zeros_like(s)
    rdot        = np.zeros_like(s)
    A_burn      = np.zeros_like(s)

    Pc_pa       = np.ones_like(s) * patm * 1e6
    V_free      = np.ones_like(s) * Vc
    Pc_Mpa      = np.ones_like(s) * patm

    DI[0]   = Di
    DE[0]   = De
    L[0]    = L0 * Ng
    TW[0]   = tw0

    A_burn[0] = ((pi/4)*(DE[0]**2-DI[0]**2)*2*Ng*esi) + (pi*DE[0]*L[0]*Ng*osi) + (pi*DI[0]*L[0]*Ng*csi)
    # Note:
    # Here I'm assuming that the grain outer diameter is the case inner diameter
    # Of course there is thermal protection too, but the area we're gonna use (A_duct) is the
    # area through which the gasses can flow so I'll take the initial grain outer diameter as the maximum
    # flowing internal d1iameter.

    A_duct[0]   = (pi / 4) * (Di ** 2)
    A_duct_t[0] = A_duct[0] / At
    # Ignore: Pc_pa[0] += rho_prod[i]*ratto

    V_g[0]      = Vg0
    V_free[0]   = Vc - Vg0
    m_grain[0]  = rho_g * Vg0
    rdot[0]     = rdp(prop, patm)
    Pc_Mpa2[0]  = patm

    # ic(incs)
    for i in range(1, N):
        Pc_Mpa2[i] = Pc_Mpa[i - 1]
        DI[i] = DI[i - 1] + csi * 2 * incs
        DE[i] = DE[i - 1] - osi * 2 * incs
        L[i] = L[i - 1] - Ng * esi * 2 * incs
        TW[i] = (DE[i] - DI[i]) / 2
        A_duct[i] = (pi / 4) * De ** 2 - (pi / 4) * (DE[i] ** 2 - DI[i] ** 2)
        A_duct_t[i] = A_duct[i] / At
        V_g[i] = ((pi / 4) * (DE[i] ** 2 - DI[i] ** 2) * L[i]) / (1000 ** 3)
        V_free[i] -= V_g[i]
        m_grain[i] = rho_g * (V_g[i])

        # Above this line, all are functional --/---/--/---/--/---/--/---/--/---/--/---/
        # ic(Pc_pa,Pc_Mpa,Pc_Mpa2)
        rdot[i] = rdp(prop, Pc_Mpa2[i])


        t[i] = incs / rdot[i] + t[i - 1]

        AI[i] = (Pc_Mpa2[i] - patm) * 1e6 * A_star * par_AI
        A_burn[i] = ((pi / 4) * (DE[i] ** 2 - DI[i] ** 2) * 2 * Ng * esi) + (pi * DE[i] * L[i] * Ng * osi) + (pi * DI[i] * L[i] * Ng * csi)

        #TODO: Change this implementation to the ifxl() function for readability. Or don't.
        if (mdot_ger[i] < AI[i]):
            if Pc_Mpa[i - 1] > pbd:
                mdot_nozzle[i] = AI[i]
            else:
                mdot_nozzle[i] = 0
        else:
            mdot_nozzle[i] = AI[i]

        mdot_ger[i] = (m_grain[i - 1] - m_grain[i]) / (t[i] - t[i - 1])
        m_stodot[i] = mdot_ger[i] - mdot_nozzle[i]
        m_sto[i] = m_stodot[i] * (t[i] - t[i - 1]) + m_sto[i - 1]

        rho_prod[i] = m_sto[i] / V_free[i]
        Pc_pa[i] += rho_prod[i] * ratto
        Pc_Mpa[i] = Pc_pa[i] / 1e6

        # ic(i,Pc_Mpa2[i],rdot[i])
        # ic(i,Pc_pa[i])
        # ic(i,mdot_nozzle[i],mdot_ger[i],AI[i])
        # ic(i,Pc_Mpa[i])
        # ic(i,t[i])
        # ic(i,rdot[i])
        # ic(i,m_sto[i])

    A_burn_max = max(A_burn)
    # ic(A_burn_max)
    t_inc = 0.00001
    tbout = t[-1]
    pbout = Pc_Mpa[-1]
    # ic(tbout,pbout,ratto,A_star,Vc,c_star)
    # breakpoint()

    err_MPa = 1.0
    n = 10000


    # ic(Pc_Mpa[-1])

    start = time.time()
    while Pc_Mpa[-1]>=patm:

        t = np.append(t, t[-1]+t_inc)
        Pc_pos = pbout*np.exp(-ratto*A_star*(t[-1]-tbout)/(Vc*c_star))
        Pc_Mpa = np.append(Pc_Mpa,Pc_pos)

        # finish = time.time()
        # if finish - start>1:
        #     break

    r_avg = np.average(rdot)



    arr_m = ar([s, TW, DI, DE, L, A_duct, A_duct_t, rdot,
                V_g, V_free, m_grain, mdot_ger,
                # 13
                mdot_nozzle, m_stodot, m_sto, rho_prod, Pc_pa, AI])


    # TODO: fix the following:
    #  rho_prod, Pc_pa,AI,rdot,m_sto,m_stodot,t,mdot_ger,mdot_nozzle,rho_prod
    #  I think they're fixed, but please doublecheck


    # Debugging

    na = 19

    for aa in arr_m[na:]:
        # ic(aa[0])
        pass
    # ic(rdot)
    # ic(arr_m[na:])
    # ic(rdot)
    # ic(Pc_Mpa2)
    # Pc_Mpa2[-1] = patm

    # Plotting pressure x time

    
    return t,Pc_Mpa,k,tbout,r_avg,m_grain[0],








def main():

    return 0

if __name__ == '__main__':
    main()