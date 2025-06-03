import numpy as np

from startup import *
from burnrate import *
from pressure import *

import numpy as np


def thrust_coefficient(P2: float,
                       Pc: float,
                       k: float,
                       eta_noz: float,
                       Ae_At: float,
                       patm_pa: float = 101325.0) -> float:
    """
    Calculates the thrust coefficient (CF) for a rocket nozzle.

    Args:
        P2: Nozzle exit pressure (Pa)
        Pc: Chamber pressure (Pa)
        k: Specific heat ratio (γ)
        eta_noz: Nozzle efficiency (0-1)
        Ae_At: Nozzle expansion ratio (Ae/At)
        patm_pa: Ambient pressure (Pa, default=101325)

    Returns:
        CF: Thrust coefficient (dimensionless)
    """
    # Input validation
    if Pc <= 0 or P2 <= 0:
        return 0.0

    # Prevent division by zero and invalid exponents
    if np.isclose(k, 1.0, atol=1e-5):
        k = 1.0001  # Avoid singularity

    # Critical pressure ratio check
    P_ratio = P2 / Pc
    P_crit = (2 / (k + 1)) ** (k / (k - 1))

    if P_ratio >= P_crit:  # Flow not choked
        return 0.0

    # Isentropic term calculation
    try:
        isentropic_term = 2 * k ** 2 / (k - 1) * (2 / (k + 1)) ** ((k + 1) / (k - 1))
        pressure_term = 1 - P_ratio ** ((k - 1) / k)

        if pressure_term <= 1e-10:  # Handle numerical underflow
            pressure_term = 0.0

        cf_isentropic = eta_noz * np.sqrt(isentropic_term * pressure_term)

        # Pressure thrust term
        pressure_thrust = (P2 - patm_pa) / Pc * Ae_At

        # Total CF
        CF = cf_isentropic + pressure_thrust

        # Physical bounds check
        CF = np.clip(CF, 0, 2.5)  # Practical upper limit for CF

        return float(CF)

    except (ValueError, ZeroDivisionError):
        return 0.0


def calculate_thrust(N,motor_data,eta_noz,Ae_At):

    # Calculating Time [s] and Chamber Pressure [MPa]

    # TODO:
    #  1:
    #  Insert multiple operating modes so that you can either insert t, Pc_MPa directly
    #  or have it calculated from motor_data. Only needed in case it begins taking too long
    #  Have a 'lobby function' that checks the format of the input data (is it pressure and time or
    #  motor data?) and then calls the function that calculates thrust
    #  If you're gonna, say, plot 10 thrust curves one atop the other, it's gonna begin to cost time.
    #  2:
    #  For some reason, some values of epsilon (Ae/At) lead to surges in the value of CF, that
    #  leads to a surge in the value of thrust. Possibly linked to the calculation of P2, I think that's
    #  what's causing P2 then Cf then Thrust to boom


    t,Pc_MPa,k,tbout,r_avg,m_grain0 = calculate_pressure_parameters(N, motor_data)
    Pc_Pa = Pc_MPa*1e6
    Np = len(t)

    # Importing motor data

    prop    = motor_data[0].astype(str)

    Dt      = motor_data[1].astype(float)
    Rho_pct = motor_data[2].astype(float)
    Ng      = motor_data[3].astype(float)
    L0      = motor_data[4].astype(float)
    De      = motor_data[5].astype(float)
    Di      = motor_data[6].astype(float)

    p_min   = motor_data[7].astype(float)
    p_max   = motor_data[8].astype(float)

    csi     = motor_data[9].astype(int)
    esi     = motor_data[10].astype(int)
    osi     = motor_data[11].astype(int)


    # Initializing empty arrays

    P2_Pa       = np.zeros_like(t)
    Cf          = np.zeros_like(t)
    F           = np.zeros_like(t)
    It_arr      = np.zeros_like(t)
    AeAt_opt    = np.zeros_like(t)


    #Initializing other variables

    Me          = find_M2(Ae_At,k)
    P2_Pa[0]    = patm_pa
    AeAt_opt[0] = 1
    Cf[0]       = eta_noz

    At = (pi/4)*Dt**2/1000**2
    Ae = At*Ae_At
    De = np.sqrt(Ae/(pi/4))

    wf = 2*r_avg*tbout/De


    # Lambda functions for the loops
    P2 = lambda Pc: Pc/(1+(k-1)/2*Me**2)**(k/(k-1))
    FT = lambda Cf,Pc: At*Cf*Pc
    # CF = lambda P2,Pc:eta_noz*np.sqrt(2*k**2/(k-1)*(2/(k+1))**((k+1)/(k-1))*(1-(P2/Pc)**((k-1)/k)))+(P2-patm_pa)/Pc*(Ae/At)
    IT = lambda F1,F2,T1,T2: (F1+F2)/2*(T2-T1)





    for i in range(Np):
        P2_Pa[i]    = ifxl(P2(Pc_Pa[i])<patm_pa,patm_pa,P2(Pc_Pa[i]))
        cf = thrust_coefficient(
            P2=P2_Pa[i],
            Pc=Pc_Pa[i],
            k=k,
            eta_noz=eta_noz,    # From function args (0.85 default)
            Ae_At=Ae_At,        # (Ae/At ratio)
            patm_pa=patm_pa     # From startup.py (101325 Pa)
        )
        Cf[i] = cf

        F[i]        = FT(Cf[i],Pc_Pa[i])
        It_arr[i]   = IT(F[i-1],F[i],t[i-1],t[i])



    F_max           = max(F)
    It              = np.sum(It_arr)
    Isp             = It/(g0*m_grain0)
    id_Pcmax        = where(max(Pc_Pa))[0]
    AeAt_opt_pmax   = AeAt_opt[id_Pcmax]
    AeAt_opt_pavg   = np.average(AeAt_opt)
    Cf_max          = max(Cf)

    # TODO: remember to use ic() to figure out what causes the surge in CF in certain Ae/At values.
    # ic(F_max,It,AeAt_opt_pmax)

    return F,Pc_MPa,t,Cf

def thrust_pressure(N,motor,Ae_At):
    # motor = mot(id_motor)
    F, Pc, t,Cf = calculate_thrust(N, motor, 0.85, Ae_At)
    # ic(F, Pc, t)
    pl(t, Pc, 'Tempo [s]', 'Pressão na Câmara [MPa]',
       'Pressão na câmara em função do tempo', 'Pressão', [-0.05, None], [0, None])

    pl(t, F, 'Tempo [s]', 'Empuxo [N]',
       'Empuxo em função do tempo', 'F', [-0.05, None], [0, None])
    return F, Pc, t


def main():

    return 0

if __name__ == '__main__':
    main()