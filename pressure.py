from startup import *
from burnrate import rdp
from motor_library import MotorConfig, process_motor_specs


from startup import *
from burnrate import rdp
from motor_library import MotorConfig, process_motor_specs


def calculate_pressure_parameters(N, motor: MotorConfig, c_star=0):
    specs = process_motor_specs(motor)
    rho_g = specs['rho_g']
    k = specs['k']
    Lc = specs['lc']

    prop, Dt, Ng, L0, De, Di = motor.prop, motor.Dt, motor.Ng, motor.L, motor.De, motor.Di
    csi, esi, osi = motor.core_surface_inhibited, motor.ends_surface_inhibited, motor.outer_surface_inhibited

    Vc = (Lc * (pi / 4) * De ** 2) / 1000 ** 3
    dp = dict_prop.get(prop.lower().split('_')[0], 2)
    nuc = motor.nuc
    rat = Ru / properties_table[dp][2]
    ratto = rat * (nuc * properties_table[dp][3])

    if c_star == 0:
        c_star = np.sqrt(ratto / k * (((k + 1) / 2) ** ((k + 1) / (k - 1))))

    At = (pi / 4) * (Dt ** 2)
    A_star = At / 1e6
    par_AI = np.sqrt(k / ratto) * (2 / (k + 1)) ** ((k + 1) / (2 * (k - 1)))

    tw0 = (De - Di) / 2
    s = np.linspace(0, tw0, N)
    incs = s[1] - s[0] if N > 1 else 0

    t = np.zeros(N)
    rdot = np.zeros(N)
    Pc_Mpa = np.ones(N) * patm
    m_grain = np.zeros(N)
    # CURRENT (BROKEN):
    m_sto = np.zeros(N)

    # FIX:
    V_free_0 = Vc - (m_grain[0] / rho_g)
    m_sto[0] = (patm * 1e6 * V_free_0) / ratto  # Ideal Gas Law: m = PV/RT

    Vg0 = ((pi / 4) * (De ** 2 - Di ** 2) * L0 * Ng) / 1000 ** 3
    m_grain[0] = rho_g * Vg0
    rdot[0] = rdp(prop, patm)

    # =========================================================
    # [CRITICAL] IGNITER KICK
    # Force the chamber to start at 0.5 MPa (70 psi).
    # This prevents the "Fizzle" where flow drains too fast.
    # =========================================================
    P_start = 0.5
    Pc_Mpa[0] = P_start
    m_sto[0] = (P_start * 1e6 * Vc) / ratto
    # =========================================================

    for i in range(1, N):
        curr_di = Di + csi * 2 * s[i]
        curr_de = De - osi * 2 * s[i]
        curr_l = (L0 * Ng) - esi * 2 * s[i]

        Vg_m3 = ((pi / 4) * (curr_de ** 2 - curr_di ** 2) * curr_l) / (1000 ** 3)
        Vg_m3 = max(Vg_m3, 1e-9)
        V_free = Vc - Vg_m3
        m_grain[i] = rho_g * Vg_m3

        # Safety: Use previous pressure, clamped to 1 atm
        safe_P = max(Pc_Mpa[i - 1], patm)
        rdot[i] = rdp(prop, safe_P)

        t[i] = t[i - 1] + (incs / rdot[i] if rdot[i] > 0 else 0.001)
        dt = t[i] - t[i - 1]

        mdot_gen = (m_grain[i - 1] - m_grain[i]) / dt
        mdot_noz = (safe_P * 1e6) * A_star * par_AI

        m_stodot = mdot_gen - mdot_noz
        m_sto[i] = m_sto[i - 1] + m_stodot * dt

        # [CRITICAL] Mass Floor: Cannot have less mass than air at 1 atm
        min_mass = (patm * 1e6 * V_free) / ratto
        if m_sto[i] < min_mass:
            m_sto[i] = min_mass

        Pc_Mpa[i] = ((m_sto[i] / V_free) * ratto) / 1e6

    # Tail-off logic
    t_inc, tbout, pbout = 0.001, t[-1], Pc_Mpa[-1]
    if pbout > patm * 1.05:
        while Pc_Mpa[-1] > patm * 1.01:
            t_next = t[-1] + t_inc
            p_next = pbout * np.exp(-ratto * A_star * (t_next - tbout) / (Vc * c_star))
            if p_next < patm:
                p_next = patm
                break
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