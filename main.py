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
    Prange = np.linspace(0.12,10,10000)
    # Calculate Rd values for each dataset
    Rd1 = [rdp(rd_knsb, p) for p in Prange]
    Rd2 = [rdp(rd_knsu, p) for p in Prange]
    Rd3 = [rdp(rd_kndx, p) for p in Prange]
    Rd4 = [rdp(rd_kner, p) for p in Prange]
    Rd5 = [rdp(rd_knpsb, p) for p in Prange]
    Rd6 = [rdp(rd_knfr, p) for p in Prange]

    # Convert lists to numpy arrays for easier plotting
    Rd1 = np.array(Rd1)
    Rd2 = np.array(Rd2)
    Rd3 = np.array(Rd3)
    Rd4 = np.array(Rd4)
    Rd5 = np.array(Rd5)
    Rd6 = np.array(Rd6)

    # Plot each dataset
    plt.plot(Prange, Rd1, label='Rd Knsb')
    plt.plot(Prange, Rd2, label='Rd Knsu')
    plt.plot(Prange, Rd3, label='Rd Kndx')
    plt.plot(Prange, Rd4, label='Rd Kner')
    plt.plot(Prange, Rd5, label='Rd Knpsb')
    plt.plot(Prange, Rd6, label='Rd Knfr')

    # Add labels and title
    plt.xlabel('Pressure (P)')
    plt.ylabel('Rd Values')
    plt.title('Rd Values vs Pressure')
    plt.legend()  # Show legend
    plt.grid()  # Optional: add a grid for better readability
    plt.show()
    # pl(Pc, BR, 'Pressão na Câmara [MPa]', 'Burn Rate [mm/s]',
    #    'Taxa de regressão em função da pressão',
    #    labelf=f'{pars[1]}·P^{pars[0]}', log=0,
    #    x0f=[0.95 * p_min, 1.0 * p_max],
    #    y0f=[0.95 * min(BR[np.where(BR>0)]), 1.05 * max(BR[np.where(BR<40)])])

    return 0


if __name__ == '__main__':
    main()
