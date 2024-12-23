import numpy as np

from startup import *
from burnrate import *

#TODO:
# 1:
# Correct the error, discontinuity that occurs
# when pressure drops to 0. just set ds/dt = 0.
# 2:
# log scale graph not working. is it because the graph is in MPa? shouldn't be, right?
# 3:
# fit the power law https://www.youtube.com/watch?v=wujirumjHxU



def main():
    testeNakka = True
    testeRand = True
    test_BRfrompressure = False
    test_BRmultiple = False
    id_file = "q2OM"

    testeRand=False
    testeNakka = False

    p_min = 3.85
    p_max = 4.3
    # p_max = 0

    prop = 'knsb'
    Dt = 9.659
    Rho_pct = 0.95
    Ng = 4
    L = 50.0
    De = 45.0
    Di = 25.0


    if testeNakka:
        prop = 'knpsb'
        At = 81.1
        Dt = np.sqrt(At / (pi / 4)) * 10
        Rho_pct = 1.912 / rho_prop[prop]
        Ng = 2
        L = 65.0
        De = 43.1
        Di = 13.88
    elif(testeRand):
        prop = 'knpsb'
        At = 81.1
        Dt = np.sqrt(At / (pi / 4)) * 10
        Rho_pct = 1.912 / rho_prop[prop]
        Ng = 2
        L = 65.0
        De = 50
        Di = 4

    motor = ar([prop, Dt, Rho_pct, Ng, L, De, Di, p_min, p_max])

    if test_BRfrompressure:
        Pc, BR, pars = BR_from_pressure(id_file, motor)
        # plt.plot(Pc, target_func(Pc, *pars), '--')
        # pl(Pc, BR, 'Pressão na Câmara [MPa]', 'Burn Rate [mm/s]',
        #    'Taxa de regressão em função da pressão',
        #    labelf=f'{pars[1]}·P^{pars[0]}', log=0,
        #    x0f=[0.95 * p_min, 1.0 * p_max],
        #    y0f=[0.95 * min(BR[np.where(BR>0)]), 1.05 * max(BR[np.where(BR<40)])])
    if test_BRmultiple:
        Prange = np.linspace(0.12,10,10000)
        # Calculate Rd values for each dataset
        Rd1 = ar([rdp(rd_knsb, p) for p in Prange])
        Rd2 = ar([rdp(rd_knsu, p) for p in Prange])
        Rd3 = ar([rdp(rd_kndx, p) for p in Prange])
        Rd4 = ar([rdp(rd_kner, p) for p in Prange])
        Rd5 = ar([rdp(rd_knpsb, p) for p in Prange])
        Rd6 = ar([rdp(rd_knfr, p) for p in Prange])
        Rd = ar([Rd1,Rd2,Rd3,Rd4,Rd5,Rd6])

        for rd in Rd:
            plt.plot(Prange,rd)


        # Add labels and title
        plt.xlabel('Pressure [MPa]')
        plt.ylabel('R_dot [mm/s]')
        plt.title('Rd Values vs Pressure')
        plt.legend()  # Show legend
        plt.grid()  # Optional: add a grid for better readability
        plt.show()

    return 0


if __name__ == '__main__':
    main()
