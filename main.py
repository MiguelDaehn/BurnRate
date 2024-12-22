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
    id_file = "nakka"

    testeRand=False
    # testeNakka = False

    p_min = 3.5
    p_max = 6
    # p_max = 0

    # prop = 'knsb'
    # Dt = 9.659
    # Rho_pct = 0.95
    # Ng = 4
    # L = 50.0
    # De = 45.0
    # Di = 25.0


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

    Pc, BR, pars = BR_from_pressure(id_file, motor)
    # plt.plot(Pc, target_func(Pc, *pars), '--')

    pl(Pc, BR, 'Pressão na Câmara [MPa]', 'Burn Rate [mm/s]',
       'Taxa de regressão em função da pressão',
       labelf=f'{pars[1]}·P^{pars[0]}', log=0,
       x0f=[0.9 * p_min, 1.0 * p_max],
       y0f=[0.9 * min(BR[np.where(BR>0)]), 1.1 * max(BR[np.where(BR<40)])])

    return 0


if __name__ == '__main__':
    main()
