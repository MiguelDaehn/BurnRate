import numpy as np
from numba import jit
from startup import *
import burnrate  # To load the burn rate table
from motor_library import MotorConfig, process_motor_specs
import propellants as prop_db


# ==========================================
# 1. THE JIT KERNEL (Machine Code Speed)
# ==========================================
@jit(nopython=True)
def _get_burn_rate(P_val, table):
    """
    Fast lookup for a * P^n.
    Assumes P_val is in MPa and table columns are [min, max, a, n].
    """
    rows = table.shape[0]
    # Default to last row if out of bounds (extrapolation)
    a = table[rows - 1, 2]
    n = table[rows - 1, 3]

    for i in range(rows):
        if table[i, 0] <= P_val <= table[i, 1]:
            a = table[i, 2]
            n = table[i, 3]
            break

    return a * (P_val ** n)


@jit(nopython=True)
def _simulation_kernel(N, rho_g, k, ratto, c_star, A_star, par_AI, Vc,
                       De, Di, L0, Ng,
                       csi, esi, osi,
                       br_table, patm_val):
    """
    The heavy calculation loop compiled to machine code.
    No classes, no dictionaries—only raw numbers and arrays.
    """
    # Initialization
    tw0 = (De - Di) / 2
    s = np.linspace(0, tw0, N)
    incs = s[1] - s[0]

    t = np.zeros(N)
    rdot = np.zeros(N)
    Pc_Mpa = np.ones(N) * patm_val
    m_grain = np.zeros(N)
    m_sto = np.zeros(N)

    # Initial State
    Vg0 = ((np.pi / 4) * (De ** 2 - Di ** 2) * L0 * Ng) / 1000 ** 3
    m_grain[0] = rho_g * Vg0
    rdot[0] = _get_burn_rate(patm_val, br_table)

    # The Loop (This runs 50-100x faster now)
    for i in range(1, N):
        curr_di = Di + csi * 2 * s[i]
        curr_de = De - osi * 2 * s[i]
        curr_l_individual = L0 - (esi * 2 * s[i])
        curr_l = (curr_l_individual * Ng)

        # Ab calculation (mm^2)
        Ab_mm2 = ((np.pi / 4) * (curr_de ** 2 - curr_di ** 2) * 2 * Ng * esi) + \
                 (np.pi * curr_de * curr_l * osi) + \
                 (np.pi * curr_di * curr_l * csi)

        Vg_m3 = ((np.pi / 4) * (curr_de ** 2 - curr_di ** 2) * curr_l) / (1000 ** 3)
        V_free = Vc - Vg_m3
        m_grain[i] = rho_g * Vg_m3

        # Burn Rate Lookup
        rdot[i] = _get_burn_rate(Pc_Mpa[i - 1], br_table)

        # Safety for very small rdot to prevent div/0
        if rdot[i] < 1e-9: rdot[i] = 1e-9

        # Time Step
        t[i] = t[i - 1] + (incs / rdot[i])

        # Mass Balance
        mdot_gen = (m_grain[i - 1] - m_grain[i]) / (t[i] - t[i - 1])
        mdot_noz = (Pc_Mpa[i - 1] * 1e6) * A_star * par_AI

        m_stodot = mdot_gen - mdot_noz
        m_sto[i] = m_sto[i - 1] + m_stodot * (t[i] - t[i - 1])

        # Pressure Update
        Pc_Mpa[i] = ((m_sto[i] / V_free) * ratto) / 1e6

    return t, Pc_Mpa, rdot, m_grain[0]


# ==========================================
# 2. THE PYTHON WRAPPER (User-Friendly)
# ==========================================
def calculate_pressure_parameters(N, motor: MotorConfig, c_star=0):
    """
    Prepares data from the MotorConfig object and calls the JIT kernel.
    """
    # 1. Get Pre-processed values (Python Logic)
    specs = process_motor_specs(motor)
    rho_g = specs['rho_g']
    k = specs['k']
    Lc = specs['lc']

    # Extract motor attributes
    prop = motor.prop
    Dt = motor.Dt
    Ng = motor.Ng
    L0 = motor.L
    De = motor.De
    Di = motor.Di
    csi, esi, osi = motor.core_surface_inhibited, motor.ends_surface_inhibited, motor.outer_surface_inhibited

    # 2. Setup Chamber Geometry
    Vc = (Lc * (np.pi / 4) * De ** 2) / 1000 ** 3

    # 3. Thermochemical Properties
    M_val = prop_db.get_molar_mass(prop)
    rat = Ru / M_val
    nuc = motor.nuc
    T0_val = prop_db.get_combustion_temp(prop)
    ratto = rat * (nuc * T0_val)

    if c_star == 0:
        c_star = np.sqrt(ratto / k * (((k + 1) / 2) ** ((k + 1) / (k - 1))))

    # 4. Nozzle Parameters
    At = (np.pi / 4) * (Dt ** 2)
    A_star = At / 1e6
    par_AI = np.sqrt(k / ratto) * (2 / (k + 1)) ** ((k + 1) / (2 * (k - 1)))

    # 5. Get Burn Rate Table
    # JIT needs a numpy array, not a function lookup
    br_table = burnrate.pp(prop)
    if br_table.ndim == 1:
        br_table = br_table.reshape(1, -1)

    # 6. RUN KERNEL (This calls the compiled code)
    # We pass 'int(N)' to ensure it's not a float
    t, Pc_Mpa, rdot, m_initial = _simulation_kernel(
        int(N), rho_g, k, ratto, c_star, A_star, par_AI, Vc,
        De, Di, L0, Ng,
        csi, esi, osi,
        br_table, patm
    )

    # 7. Tail-off (Keep this in Python, it's short and complex to JIT)
    t_inc, tbout, pbout = 0.001, t[-1], Pc_Mpa[-1]

    # Simple Python loop for tail-off (negligible performance impact)
    tail_t = []
    tail_p = []

    curr_t, curr_p = tbout, pbout
    while curr_p > patm:
        curr_t += t_inc
        curr_p = pbout * np.exp(-ratto * A_star * (curr_t - tbout) / (Vc * c_star))
        tail_t.append(curr_t)
        tail_p.append(curr_p)
        if len(tail_t) > N: break  # Safety break

    if tail_t:
        t = np.append(t, tail_t)
        Pc_Mpa = np.append(Pc_Mpa, tail_p)

    return t, Pc_Mpa, k, tbout, np.average(rdot), m_initial