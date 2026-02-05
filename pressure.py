from startup import *
from burnrate import rdp
from motor_library import MotorConfig, process_motor_specs


def calculate_pressure_parameters(N, motor: MotorConfig, c_star=0):
    """
    Calculates chamber pressure using O-ring spacing and pre-processed specs.
    """
    # 1. Get Pre-processed values (TODO #5)
    specs = process_motor_specs(motor)
    rho_g = specs['rho_g']
    k = specs['k']
    Lc = specs['lc']  # Includes O-ring spacing (TODO #10)

    # Extract motor attributes
    prop = motor.prop
    Dt = motor.Dt
    Ng = motor.Ng
    L0 = motor.L
    De = motor.De
    Di = motor.Di
    csi, esi, osi = motor.core_surface_inhibited, motor.ends_surface_inhibited, motor.outer_surface_inhibited

    # 2. Setup Chamber Geometry
    # Free volume now accounts for the extra space created by O-rings
    Vc = (Lc * (pi / 4) * De ** 2) / 1000 ** 3

    # 3. Thermochemical Properties
    dp = dict_prop.get(prop.lower().split('_')[0], 2)
    rat = Ru / properties_table[2][dp]
    nuc = motor.nuc
    ratto = rat * (nuc * properties_table[3][dp])

    if c_star == 0:
        c_star = np.sqrt(ratto / k * (((k + 1) / 2) ** ((k + 1) / (k - 1))))

    # 4. Nozzle Parameters
    At = (pi / 4) * (Dt ** 2)
    A_star = At / 1e6
    par_AI = np.sqrt(k / ratto) * (2 / (k + 1)) ** ((k + 1) / (2 * (k - 1)))

    # 5. Simulation Initialization
    tw0 = (De - Di) / 2
    s = np.linspace(0, tw0, N)
    incs = s[1] - s[0]

    t = np.zeros(N)
    rdot = np.zeros(N)
    Pc_Mpa = np.ones(N) * patm
    m_grain = np.zeros(N)
    m_sto = np.zeros(N)

    Vg0 = ((pi / 4) * (De ** 2 - Di ** 2) * L0 * Ng) / 1000 ** 3
    m_grain[0] = rho_g * Vg0
    rdot[0] = rdp(prop, patm)

    # 6. Simulation Loop
    for i in range(1, N):
        curr_di = Di + csi * 2 * s[i]
        curr_de = De - osi * 2 * s[i]
        curr_l_individual = L0 - (esi * 2 * s[i])
        curr_l = (curr_l_individual * Ng)

        Ab_mm2 = ((pi / 4) * (curr_de ** 2 - curr_di ** 2) * 2 * Ng * esi) + \
                 (pi * curr_de * curr_l * osi) + \
                 (pi * curr_di * curr_l * csi)

        Vg_m3 = ((pi / 4) * (curr_de ** 2 - curr_di ** 2) * curr_l) / (1000 ** 3)
        V_free = Vc - Vg_m3
        m_grain[i] = rho_g * Vg_m3

        rdot[i] = rdp(prop, Pc_Mpa[i - 1])
        t[i] = t[i - 1] + (incs / rdot[i])

        mdot_gen = (m_grain[i - 1] - m_grain[i]) / (t[i] - t[i - 1])
        mdot_noz = (Pc_Mpa[i - 1] * 1e6) * A_star * par_AI

        m_stodot = mdot_gen - mdot_noz
        m_sto[i] = m_sto[i - 1] + m_stodot * (t[i] - t[i - 1])

        Pc_Mpa[i] = ((m_sto[i] / V_free) * ratto) / 1e6

    # 7. Tail-off
    t_inc, tbout, pbout = 0.001, t[-1], Pc_Mpa[-1]
    while Pc_Mpa[-1] > patm:
        t_next = t[-1] + t_inc
        p_next = pbout * np.exp(-ratto * A_star * (t_next - tbout) / (Vc * c_star))
        t = np.append(t, t_next)
        Pc_Mpa = np.append(Pc_Mpa, p_next)
        if len(t) > N * 2: break

    return t, Pc_Mpa, k, tbout, np.average(rdot), m_grain[0]

if __name__ == '__main__':
    # Test with the new library structure
    from motor_library import load_motor

    test_motor = load_motor("motor_12")
    t, pc, k, tb, ravg, m0 = calculate_pressure_parameters(1000, test_motor)
    print(f"Simulation complete for {test_motor.name}. Peak Pressure: {max(pc):.2f} MPa")