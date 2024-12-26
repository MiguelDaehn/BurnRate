import numpy as np

from startup import *
from burnrate import *
from pressure import *

def calculate_thrust(N,motor_data,eta_noz,Ae_At):

    # Calculating Time [s] and Chamber Pressure [MPa]

    # TODO:
    #  Insert multiple operating modes so that you can either insert t, Pc_MPa directly
    #  or have it calculated from motor_data. Only needed in case it begins taking too long
    #  Have a 'lobby function' that checks the format of the input data (is it pressure and time or
    #  motor data?) and then calls the function that calculates thrust
    #  If you're gonna, say, plot 10 thrust curves one atop the other, it's gonna begin to cost time.

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
    CF = lambda P2,Pc:eta_noz*np.sqrt(2*k**2/(k-1)*(2/(k+1))**((k+1)/(k-1))*(1-(P2/Pc)**((k-1)/k)))+(P2-patm_pa)/Pc*(Ae/At)
    IT = lambda F1,F2,T1,T2: (F1+F2)/2*(T2-T1)





    for i in range(Np):
        P2_Pa[i]    = ifxl(P2(Pc_Pa[i])<patm_pa,patm_pa,P2(Pc_Pa[i]))
        cf          = CF(P2_Pa[i],Pc_Pa[i])
        Cf[i]       = np.nan_to_num(cf)
        F[i]        = FT(Cf[i],Pc_Pa[i])
        It_arr[i]   = IT(F[i-1],F[i],t[i-1],t[i])



    F_max           = max(F)
    It              = np.sum(It_arr)
    Isp             = It/(g0*m_grain0)
    id_Pcmax        = where(max(Pc_Pa))
    AeAt_opt_pmax   = AeAt_opt[id_Pcmax]
    AeAt_opt_pavg   = np.average(AeAt_opt)
    Cf_max          = max(Cf)

    ic(F_max,It)

    return F,Pc_MPa,t

def main():

    return 0

if __name__ == '__main__':
    main()